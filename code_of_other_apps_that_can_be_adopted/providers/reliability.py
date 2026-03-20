from __future__ import annotations

from datetime import datetime, timezone
from dataclasses import dataclass
from email.utils import parsedate_to_datetime


QUOTA_429_SIGNALS = (
    "insufficient_quota",
    "quota exceeded",
    "quota_exceeded",
    "exceeded your current quota",
    "billing hard limit",
    "billing_hard_limit",
    "credit balance is too low",
    "out of credits",
    "payment required",
    "billing exhausted",
)


@dataclass(slots=True, frozen=True)
class ReliabilitySettings:
    retry_max_attempts: int = 3
    retry_initial_backoff_s: float = 0.5
    retry_max_backoff_s: float = 8.0
    retry_jitter_s: float = 0.2
    circuit_failure_threshold: int = 3
    circuit_cooldown_s: float = 30.0


def parse_retry_after_seconds(header_value: str | None) -> float | None:
    raw = str(header_value or "").strip()
    if not raw:
        return None
    try:
        value = float(raw)
    except ValueError:
        try:
            parsed = parsedate_to_datetime(raw)
        except (TypeError, ValueError):
            return None
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        delay = (parsed - datetime.now(timezone.utc)).total_seconds()
        if delay < 0:
            return 0.0
        return delay
    if value < 0:
        return None
    return value


def parse_http_status(error_message: str, *, prefixes: tuple[str, ...] = ("provider_http_error:", "codex_http_error:")) -> int | None:
    text = str(error_message or "")
    for prefix in prefixes:
        if text.startswith(prefix):
            suffix = text[len(prefix) :]
            code_raw = suffix.split(":", 1)[0].strip()
            try:
                return int(code_raw)
            except ValueError:
                return None
    return None


def is_quota_429_error(error_message: str) -> bool:
    lowered = str(error_message or "").lower()
    if not lowered:
        return False
    return any(token in lowered for token in QUOTA_429_SIGNALS)


def is_retryable_error(error_message: str) -> bool:
    text = str(error_message or "").strip()
    if not text:
        return False
    if text.startswith("provider_circuit_open:"):
        return True
    if text.startswith("provider_network_error:") or text.startswith("codex_network_error:"):
        return True
    status = parse_http_status(text)
    if status is None:
        return False
    if status == 429:
        return not is_quota_429_error(text)
    return 500 <= status <= 599


def classify_provider_error(error_message: str) -> str:
    text = str(error_message or "").strip()
    lowered = text.lower()
    if not lowered:
        return "unknown"

    if lowered.startswith("provider_circuit_open:"):
        return "circuit_open"

    if lowered.startswith("provider_config_error:") or lowered.startswith("codex_config_error:"):
        return "config"

    if lowered.startswith("provider_auth_error:") or lowered.startswith("codex_auth_error:"):
        return "auth"

    if lowered.startswith("provider_network_error:") or lowered.startswith("codex_network_error:"):
        return "network"

    if lowered.endswith("_exhausted") or "retry_exhausted" in lowered:
        return "retry_exhausted"

    status = parse_http_status(text)
    if status in {401, 403}:
        return "auth"
    if status == 429:
        if is_quota_429_error(text):
            return "quota"
        return "rate_limit"
    if status is not None and (status == 408 or 500 <= status <= 599):
        return "http_transient"

    if any(token in lowered for token in ("quota", "billing", "insufficient_quota", "out of credits", "payment required")):
        return "quota"
    if any(token in lowered for token in ("rate limit", "too many requests", "throttl")):
        return "rate_limit"
    if any(token in lowered for token in ("timeout", "timed out", "connection", "dns", "socket", "refused", "unreachable")):
        return "network"

    return "unknown"
