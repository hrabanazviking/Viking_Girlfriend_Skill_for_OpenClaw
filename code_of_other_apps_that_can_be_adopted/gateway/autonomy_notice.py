from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from typing import Any

from clawlite.core.memory_monitor import MemoryMonitor
from clawlite.utils.logging import bind_event


LATEST_MEMORY_ROUTE_CACHE_TTL_S = 5.0


def default_heartbeat_route() -> tuple[str, str]:
    return ("cli", "profile")


def _record_autonomy_event(
    autonomy_log: Any | None,
    source: str,
    action: str,
    status: str,
    *,
    summary: str = "",
    metadata: dict[str, Any] | None = None,
    event_at: str = "",
) -> None:
    if autonomy_log is None:
        return
    try:
        autonomy_log.record(
            source=source,
            action=action,
            status=status,
            summary=summary,
            metadata=metadata,
            event_at=event_at,
        )
    except Exception as exc:
        bind_event("autonomy.log", source=source, action=action).warning("autonomy log record failed error={}", exc)


def latest_route_from_history_tail(
    memory_store: Any,
    *,
    preferred_channel: str = "",
    tail_bytes: int = 16 * 1024,
) -> tuple[str, str]:
    history_path = getattr(memory_store, "history_path", None)
    if history_path is None:
        return default_heartbeat_route()
    try:
        path = Path(history_path)
    except Exception:
        return default_heartbeat_route()
    if not path.exists() or not path.is_file():
        return default_heartbeat_route()

    try:
        with path.open("rb") as fh:
            fh.seek(0, 2)
            size = fh.tell()
            start = max(0, size - max(512, int(tail_bytes)))
            fh.seek(start)
            chunk = fh.read()
    except Exception:
        return default_heartbeat_route()

    if not chunk:
        return default_heartbeat_route()
    raw_text = chunk.decode("utf-8", errors="ignore")
    lines = raw_text.splitlines()
    latest_route: tuple[str, str] | None = None
    preferred = str(preferred_channel or "").strip().lower()
    for raw_line in reversed(lines):
        line = str(raw_line or "").strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except Exception:
            continue
        if not isinstance(payload, dict):
            continue
        source = str(payload.get("source", "") or "").strip()
        if not source:
            continue
        route = MemoryMonitor._delivery_route_from_source(source)
        if latest_route is None:
            latest_route = route
        if preferred and route[0] == preferred:
            return route
    return latest_route or default_heartbeat_route()


async def latest_memory_route(
    memory_store: Any,
    *,
    preferred_channel: str = "",
    cache: dict[tuple[int, str], tuple[float, tuple[str, str]]] | None = None,
    cache_ttl_s: float = LATEST_MEMORY_ROUTE_CACHE_TTL_S,
) -> tuple[str, str]:
    channel, target = default_heartbeat_route()
    if memory_store is None:
        return channel, target

    normalized_preference = str(preferred_channel or "").strip().lower()
    cache_key = (id(memory_store), normalized_preference)
    now = time.monotonic()
    if cache is not None:
        cached = cache.get(cache_key)
        if cached is not None:
            cached_at, cached_route = cached
            if (now - cached_at) <= float(cache_ttl_s):
                return cached_route

    try:
        resolved_route = await asyncio.to_thread(
            latest_route_from_history_tail,
            memory_store,
            preferred_channel=normalized_preference,
        )
    except Exception:
        return channel, target

    if not isinstance(resolved_route, tuple) or len(resolved_route) != 2:
        resolved_route = (channel, target)
    if cache is not None:
        cache[cache_key] = (now, resolved_route)
    return resolved_route


async def send_autonomy_notice(
    *,
    source: str,
    action: str,
    status: str,
    text: str,
    memory_store: Any,
    channels: Any,
    autonomy_log: Any | None = None,
    metadata: dict[str, Any] | None = None,
    summary: str = "",
    event_at: str = "",
    preferred_channel: str = "telegram",
    cache: dict[tuple[int, str], tuple[float, tuple[str, str]]] | None = None,
    cache_ttl_s: float = LATEST_MEMORY_ROUTE_CACHE_TTL_S,
) -> bool:
    notice_text = str(text or "").strip()
    if not notice_text:
        return False

    channel_name, target = await latest_memory_route(
        memory_store,
        preferred_channel=preferred_channel,
        cache=cache,
        cache_ttl_s=cache_ttl_s,
    )
    if not channel_name or not target:
        return False

    payload_metadata = dict(metadata or {})
    payload_metadata.setdefault("source", source)
    payload_metadata["autonomy_notice"] = True
    payload_metadata.setdefault("autonomy_action", action)
    payload_metadata.setdefault("autonomy_status", status)

    event_metadata = {
        "channel": channel_name,
        "target": target,
        "notice_status": status,
        **payload_metadata,
    }
    try:
        await channels.send(
            channel=channel_name,
            target=target,
            text=notice_text,
            metadata=payload_metadata,
        )
    except Exception as exc:
        event_metadata["error"] = str(exc)
        _record_autonomy_event(
            autonomy_log,
            source,
            f"{action}_notice",
            "failed",
            summary=summary or f"notice failed for {action}",
            metadata=event_metadata,
            event_at=event_at,
        )
        bind_event("autonomy.notice", source=source, action=action).warning(
            "autonomy notice failed channel={} target={} error={}",
            channel_name,
            target,
            exc,
        )
        return False

    _record_autonomy_event(
        autonomy_log,
        source,
        f"{action}_notice",
        "sent",
        summary=summary or f"notice sent for {action}",
        metadata=event_metadata,
        event_at=event_at,
    )
    return True


__all__ = [
    "LATEST_MEMORY_ROUTE_CACHE_TTL_S",
    "default_heartbeat_route",
    "latest_memory_route",
    "latest_route_from_history_tail",
    "send_autonomy_notice",
]
