from __future__ import annotations

from typing import Any


def memory_analysis_snapshot(memory_store: Any) -> dict[str, Any]:
    analysis_payload: dict[str, Any] = {}
    analysis_stats = getattr(memory_store, "analysis_stats", None)
    if callable(analysis_stats):
        try:
            raw_analysis = analysis_stats()
        except Exception:
            raw_analysis = {}
        if isinstance(raw_analysis, dict):
            analysis_payload = raw_analysis
    return analysis_payload


def memory_quality_snapshot(memory_store: Any) -> dict[str, Any]:
    quality_payload: dict[str, Any] = {}
    quality_state_snapshot = getattr(memory_store, "quality_state_snapshot", None)
    if callable(quality_state_snapshot):
        try:
            raw_quality = quality_state_snapshot()
        except Exception:
            raw_quality = {}
        if isinstance(raw_quality, dict):
            quality_payload = raw_quality
    return quality_payload


def dashboard_memory_summary(
    *,
    memory_monitor: Any,
    memory_store: Any,
    config: Any,
    memory_profile_snapshot_fn,
    memory_suggest_snapshot_fn,
    memory_version_snapshot_fn,
) -> dict[str, Any]:
    monitor_payload: dict[str, Any]
    if memory_monitor is None:
        monitor_payload = {"enabled": False}
    else:
        try:
            monitor_payload = dict(memory_monitor.telemetry())
        except Exception:
            monitor_payload = {"enabled": False, "error": "memory_monitor_unavailable"}
        monitor_payload["enabled"] = True

    return {
        "monitor": monitor_payload,
        "analysis": memory_analysis_snapshot(memory_store),
        "profile": memory_profile_snapshot_fn(config),
        "suggestions": memory_suggest_snapshot_fn(config, refresh=False),
        "versions": memory_version_snapshot_fn(config),
        "quality": memory_quality_snapshot(memory_store),
    }
