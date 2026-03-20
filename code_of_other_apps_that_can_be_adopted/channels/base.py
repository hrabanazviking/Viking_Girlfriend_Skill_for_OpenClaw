from __future__ import annotations

import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Awaitable, Callable

from clawlite.channels.inbound_text import sanitize_inbound_system_tags

InboundHandler = Callable[[str, str, str, dict[str, Any]], Awaitable[None]]


class _TokenBucketRateLimiter:
    def __init__(self, *, rate: float, per_s: float) -> None:
        self._rate = max(1.0, float(rate or 1.0))
        self._per_s = max(0.001, float(per_s or 0.001))
        self._buckets: dict[str, tuple[float, float]] = {}

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        tokens, last_ts = self._buckets.get(key, (self._rate, now))
        elapsed = max(0.0, now - last_ts)
        refill = elapsed * (self._rate / self._per_s)
        tokens = min(self._rate, tokens + refill)
        if tokens < 1.0:
            self._buckets[key] = (tokens, now)
            return False
        self._buckets[key] = (tokens - 1.0, now)
        return True

    def reset(self, key: str) -> None:
        self._buckets.pop(key, None)


@dataclass(slots=True)
class ChannelHealth:
    running: bool
    last_error: str


@dataclass(slots=True, frozen=True)
class ChannelCapabilities:
    supports_progress: bool = True
    supports_tool_hints: bool = True
    supports_metadata: bool = True
    supports_retry: bool = True


class BaseChannel(ABC):
    def __init__(
        self,
        *,
        name: str,
        config: dict[str, Any],
        on_message: InboundHandler | None = None,
        capabilities: ChannelCapabilities | None = None,
    ) -> None:
        self.name = name
        self.config = config
        self.on_message = on_message
        self._capabilities = capabilities or ChannelCapabilities()
        self._running = False
        self._last_error = ""
        self._rate_limiter = _TokenBucketRateLimiter(rate=10.0, per_s=60.0)

    @property
    def running(self) -> bool:
        return self._running

    def health(self) -> ChannelHealth:
        return ChannelHealth(running=self._running, last_error=self._last_error)

    @property
    def capabilities(self) -> ChannelCapabilities:
        return self._capabilities

    async def emit(self, *, session_id: str, user_id: str, text: str, metadata: dict[str, Any] | None = None) -> None:
        if self.on_message is None:
            return
        limiter_key = f"{self.name}:{session_id}"
        if not self._rate_limiter.allow(limiter_key):
            return
        await self.on_message(
            session_id,
            user_id,
            sanitize_inbound_system_tags(text),
            metadata or {},
        )

    @abstractmethod
    async def start(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def stop(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def send(self, *, target: str, text: str, metadata: dict[str, Any] | None = None) -> str:
        raise NotImplementedError


class PassiveChannel(BaseChannel):
    """Base channel for integrations not implemented yet in v2."""

    async def start(self) -> None:
        self._running = True

    async def stop(self) -> None:
        self._running = False

    async def send(self, *, target: str, text: str, metadata: dict[str, Any] | None = None) -> str:
        del target, text, metadata
        raise RuntimeError(f"{self.name}_not_implemented")


async def cancel_task(task: asyncio.Task[Any] | None) -> None:
    if task is None:
        return
    if task.done():
        return
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        return
