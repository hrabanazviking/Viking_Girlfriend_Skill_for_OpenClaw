from __future__ import annotations

import asyncio
import math
import random
import time
from dataclasses import dataclass
from email.utils import parsedate_to_datetime
from typing import Any


@dataclass(slots=True)
class TelegramRetryPolicy:
    max_attempts: int = 3
    base_backoff_s: float = 0.35
    max_backoff_s: float = 8.0
    jitter_ratio: float = 0.2

    def normalized(self) -> "TelegramRetryPolicy":
        max_attempts = max(1, int(self.max_attempts))
        base_backoff_s = max(0.0, float(self.base_backoff_s))
        max_backoff_s = max(base_backoff_s, float(self.max_backoff_s))
        jitter_ratio = min(0.9, max(0.0, float(self.jitter_ratio)))
        return TelegramRetryPolicy(
            max_attempts=max_attempts,
            base_backoff_s=base_backoff_s,
            max_backoff_s=max_backoff_s,
            jitter_ratio=jitter_ratio,
        )


class TelegramCircuitOpenError(RuntimeError):
    pass


class TelegramAuthCircuitBreaker:
    def __init__(self, *, failure_threshold: int = 1, cooldown_s: float = 60.0) -> None:
        self.failure_threshold = max(1, int(failure_threshold))
        self.cooldown_s = max(1.0, float(cooldown_s))
        self._consecutive_failures = 0
        self._open_until_monotonic: float | None = None

    @property
    def is_open(self) -> bool:
        if self._open_until_monotonic is None:
            return False
        return time.monotonic() < self._open_until_monotonic

    def on_success(self) -> None:
        self._consecutive_failures = 0
        self._open_until_monotonic = None

    def on_auth_failure(self) -> None:
        self._consecutive_failures += 1
        if self._consecutive_failures >= self.failure_threshold:
            self._open_until_monotonic = time.monotonic() + self.cooldown_s


def status_code_from_exc(exc: Exception) -> int | None:
    for attr in ("status_code", "error_code"):
        value = getattr(exc, attr, None)
        try:
            if value is not None:
                return int(value)
        except (TypeError, ValueError):
            pass

    response = getattr(exc, "response", None)
    if response is not None:
        value = getattr(response, "status_code", None)
        try:
            if value is not None:
                return int(value)
        except (TypeError, ValueError):
            pass
    return None


def exception_text(exc: Exception) -> str:
    return str(exc or "").strip().lower()


def is_auth_failure(exc: Exception) -> bool:
    status_code = status_code_from_exc(exc)
    if status_code in {401, 403}:
        return True
    name = exc.__class__.__name__.lower()
    return "unauthorized" in name or "forbidden" in name


def is_transient_failure(exc: Exception) -> bool:
    if isinstance(exc, (asyncio.TimeoutError, TimeoutError, ConnectionError, OSError)):
        return True

    status_code = status_code_from_exc(exc)
    if status_code == 429:
        return True

    name = exc.__class__.__name__.lower()
    if any(part in name for part in ("timeout", "network", "retryafter")):
        return True

    text = exception_text(exc)
    return any(
        snippet in text
        for snippet in (
            "timed out",
            "timeout",
            "temporary failure",
            "connection reset",
            "too many requests",
            "retry after",
            "network",
        )
    )


def is_formatting_error(exc: Exception) -> bool:
    if status_code_from_exc(exc) != 400:
        return False
    text = exception_text(exc)
    return "can't parse entities" in text or "parse entities" in text


def is_thread_not_found_error(exc: Exception) -> bool:
    status_code = status_code_from_exc(exc)
    if status_code not in {None, 400}:
        return False
    return "message thread not found" in exception_text(exc)


def retry_delay_s(policy: TelegramRetryPolicy, attempt: int) -> float:
    normalized = policy.normalized()
    base = normalized.base_backoff_s * (2 ** max(0, int(attempt) - 1))
    capped = min(base, normalized.max_backoff_s)
    if capped <= 0:
        return 0.0
    jitter_span = capped * normalized.jitter_ratio
    jitter = (random.random() * 2.0 - 1.0) * jitter_span
    return max(0.0, capped + jitter)


def coerce_retry_after_seconds(value: Any) -> float | None:
    if value is None:
        return None
    if hasattr(value, "total_seconds"):
        try:
            seconds = float(value.total_seconds())
            if math.isfinite(seconds) and seconds > 0:
                return seconds
        except (TypeError, ValueError):
            pass
    try:
        seconds = float(value)
        if math.isfinite(seconds) and seconds > 0:
            return seconds
    except (TypeError, ValueError):
        pass
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            seconds = float(text)
            if math.isfinite(seconds) and seconds > 0:
                return seconds
        except ValueError:
            pass
        try:
            when = parsedate_to_datetime(text)
            if when.tzinfo is None:
                return None
            seconds = when.timestamp() - time.time()
            if math.isfinite(seconds) and seconds > 0:
                return seconds
        except (TypeError, ValueError, IndexError):
            return None
    return None


def retry_after_delay_s(exc: Exception) -> float | None:
    direct = coerce_retry_after_seconds(getattr(exc, "retry_after", None))
    if direct is not None:
        return direct

    parameters = getattr(exc, "parameters", None)
    from_parameters = coerce_retry_after_seconds(getattr(parameters, "retry_after", None))
    if from_parameters is not None:
        return from_parameters

    response = getattr(exc, "response", None)
    if response is None:
        return None

    headers = getattr(response, "headers", None)
    if headers is None and isinstance(response, dict):
        headers = response.get("headers")
    if headers is None:
        return None

    if hasattr(headers, "get"):
        for key in ("retry-after", "Retry-After", "RETRY-AFTER"):
            value = headers.get(key)
            delay = coerce_retry_after_seconds(value)
            if delay is not None:
                return delay
    return None


def sync_auth_breaker_signal_transition(
    *,
    signals: dict[str, int],
    breaker: TelegramAuthCircuitBreaker,
    key_prefix: str,
    seen_open: bool,
) -> bool:
    is_open = breaker.is_open
    if is_open:
        return True
    if seen_open:
        signals[f"{key_prefix}_auth_breaker_close_count"] += 1
    return False


def coerce_thread_id(value: Any) -> int | None:
    if value is None:
        return None
    try:
        thread_id = int(value)
    except (TypeError, ValueError):
        return None
    return thread_id if thread_id > 0 else None


def parse_target(target: str) -> tuple[str, int | None]:
    raw_target = str(target).strip()
    if not raw_target:
        return "", None
    if raw_target.startswith("telegram:"):
        payload = raw_target.split(":", 1)[1].strip()
        if ":topic:" in payload:
            chat_id, _, maybe_thread = payload.partition(":topic:")
            return chat_id.strip(), coerce_thread_id(maybe_thread.strip())
        if ":thread:" in payload:
            chat_id, _, maybe_thread = payload.partition(":thread:")
            return chat_id.strip(), coerce_thread_id(maybe_thread.strip())
        raw_target = payload
    elif raw_target.startswith("tg_"):
        payload = raw_target[3:].strip()
        if ":topic:" in payload:
            chat_id, _, maybe_thread = payload.partition(":topic:")
            return chat_id.strip(), coerce_thread_id(maybe_thread.strip())
        if ":thread:" in payload:
            chat_id, _, maybe_thread = payload.partition(":thread:")
            return chat_id.strip(), coerce_thread_id(maybe_thread.strip())
        raw_target = payload
    chat_id, sep, maybe_thread = raw_target.partition(":")
    if not sep:
        return chat_id.strip(), None
    return chat_id.strip(), coerce_thread_id(maybe_thread.strip())


def typing_key(*, chat_id: str, message_thread_id: int | None) -> str:
    if message_thread_id is None:
        return chat_id
    return f"{chat_id}:{message_thread_id}"


def threadless_retry_allowed(*, chat_id: str) -> bool:
    return not str(chat_id or "").strip().startswith("-")


def normalize_api_message_thread_id(*, chat_id: str, message_thread_id: Any) -> int | None:
    thread_id = coerce_thread_id(message_thread_id)
    if thread_id is None:
        return None
    if str(chat_id or "").strip().startswith("-") and thread_id == 1:
        return None
    return thread_id


def typing_task_is_active(task: asyncio.Task[Any] | None) -> bool:
    if task is None:
        return False
    cancelling = getattr(task, "cancelling", None)
    if callable(cancelling) and cancelling() > 0:
        return True
    return not task.done()
