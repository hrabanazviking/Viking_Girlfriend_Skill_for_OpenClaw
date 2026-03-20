from __future__ import annotations

import json
from typing import Any, Awaitable, Callable


def _memory_method_payload(
    *,
    memory_store: Any,
    method_name: str,
    invalid_error: str,
    session_id: str | None = None,
) -> dict[str, Any]:
    method = getattr(memory_store, method_name, None)
    if not callable(method):
        return {"available": False}
    try:
        if session_id is None:
            raw_payload = method()
        else:
            try:
                raw_payload = method(session_id=session_id)
            except TypeError:
                raw_payload = method()
    except Exception as exc:
        return {
            "available": True,
            "error": str(exc),
        }
    if isinstance(raw_payload, dict):
        payload = dict(raw_payload)
    else:
        payload = {
            "available": True,
            "error": invalid_error,
        }
    payload.setdefault("available", True)
    return payload


def engine_memory_payloads(*, memory_store: Any) -> dict[str, Any]:
    return {
        "memory": _memory_method_payload(
            memory_store=memory_store,
            method_name="diagnostics",
            invalid_error="invalid_memory_diagnostics_payload",
        ),
        "memory_analysis": _memory_method_payload(
            memory_store=memory_store,
            method_name="analysis_stats",
            invalid_error="invalid_memory_analysis_payload",
        ),
        "memory_integration": engine_memory_integration_payload(memory_store=memory_store),
    }


def engine_memory_integration_payload(*, memory_store: Any) -> dict[str, Any]:
    return _memory_method_payload(
        memory_store=memory_store,
        method_name="integration_policies_snapshot",
        invalid_error="invalid_memory_integration_payload",
        session_id="",
    )


def _memory_quality_default_payload() -> dict[str, Any]:
    return {
        "available": False,
        "updated": False,
        "report": {},
        "state": {},
        "tuning": {},
        "error": {
            "type": "not_supported",
            "message": "memory_quality_methods_unavailable",
        },
    }


def _memory_quality_cache_fingerprint(
    *,
    retrieval_metrics: dict[str, Any],
    turn_metrics: dict[str, Any],
    semantic_metrics: dict[str, Any],
    reasoning_layer_metrics: dict[str, Any],
) -> str:
    fingerprint_payload = {
        "retrieval": retrieval_metrics,
        "turn": turn_metrics,
        "semantic": semantic_metrics,
        "reasoning_layers": reasoning_layer_metrics,
    }
    try:
        return json.dumps(fingerprint_payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    except Exception:
        return repr(fingerprint_payload)


def _refresh_memory_quality_tuning_from_state(
    *,
    cached_payload: dict[str, Any],
    snapshot: Any,
) -> dict[str, Any]:
    refreshed = dict(cached_payload)
    if not isinstance(snapshot, dict):
        return refreshed

    tuning_snapshot = snapshot.get("tuning", {})
    tuning_payload = dict(tuning_snapshot) if isinstance(tuning_snapshot, dict) else {}

    state_payload = refreshed.get("state", {})
    if isinstance(state_payload, dict):
        state_payload = dict(state_payload)
    else:
        state_payload = {}
    state_payload["tuning"] = tuning_payload
    refreshed["state"] = state_payload
    refreshed["tuning"] = tuning_payload

    report_payload = refreshed.get("report", {})
    if isinstance(report_payload, dict):
        report_payload = dict(report_payload)
        report_payload["tuning"] = dict(tuning_payload)
        refreshed["report"] = report_payload
    return refreshed


def _call_quality_update(
    quality_update,
    *,
    retrieval_metrics: dict[str, Any],
    turn_metrics: dict[str, Any],
    semantic_metrics: dict[str, Any],
    generated_at: str,
    reasoning_layer_metrics: dict[str, Any],
) -> Any:
    kwargs = {
        "retrieval_metrics": retrieval_metrics,
        "turn_stability_metrics": turn_metrics,
        "semantic_metrics": semantic_metrics,
        "sampled_at": generated_at,
    }
    if reasoning_layer_metrics:
        try:
            return quality_update(
                **kwargs,
                reasoning_layer_metrics=reasoning_layer_metrics,
            )
        except TypeError:
            return quality_update(**kwargs)
    return quality_update(**kwargs)


async def engine_memory_quality_payload(
    *,
    memory_store: Any,
    retrieval_metrics_snapshot: dict[str, Any],
    turn_metrics_snapshot: dict[str, Any],
    generated_at: str,
    memory_quality_cache: dict[str, Any],
    collect_memory_analysis_metrics: Callable[[], Awaitable[tuple[dict[str, Any], dict[str, Any]]]],
) -> dict[str, Any]:
    payload = _memory_quality_default_payload()
    quality_update = getattr(memory_store, "update_quality_state", None)
    quality_snapshot = getattr(memory_store, "quality_state_snapshot", None)
    if not callable(quality_update) or not callable(quality_snapshot):
        return payload

    retrieval_metrics = {
        "attempts": int(retrieval_metrics_snapshot.get("retrieval_attempts", 0) or 0),
        "hits": int(retrieval_metrics_snapshot.get("retrieval_hits", 0) or 0),
        "rewrites": int(retrieval_metrics_snapshot.get("retrieval_rewrites", 0) or 0),
    }
    turn_metrics = {
        "successes": int(turn_metrics_snapshot.get("turns_success", 0) or 0),
        "errors": int(turn_metrics_snapshot.get("turns_provider_errors", 0) or 0)
        + int(turn_metrics_snapshot.get("turns_cancelled", 0) or 0),
    }
    semantic_raw, reasoning_layer_metrics = await collect_memory_analysis_metrics()
    semantic_metrics = {
        "enabled": bool(semantic_raw.get("enabled", False)),
        "coverage_ratio": float(semantic_raw.get("coverage_ratio", 0.0) or 0.0),
    }

    fingerprint = _memory_quality_cache_fingerprint(
        retrieval_metrics=retrieval_metrics,
        turn_metrics=turn_metrics,
        semantic_metrics=semantic_metrics,
        reasoning_layer_metrics=reasoning_layer_metrics,
    )

    cached_payload = memory_quality_cache.get("payload")
    if memory_quality_cache.get("fingerprint") == fingerprint and isinstance(cached_payload, dict):
        try:
            snapshot = quality_snapshot()
        except Exception:
            snapshot = {}
        return _refresh_memory_quality_tuning_from_state(
            cached_payload=cached_payload,
            snapshot=snapshot,
        )

    try:
        report = _call_quality_update(
            quality_update,
            retrieval_metrics=retrieval_metrics,
            turn_metrics=turn_metrics,
            semantic_metrics=semantic_metrics,
            generated_at=generated_at,
            reasoning_layer_metrics=reasoning_layer_metrics,
        )
        snapshot = quality_snapshot()
        payload = {
            "available": True,
            "updated": True,
            "report": dict(report) if isinstance(report, dict) else {},
            "state": dict(snapshot) if isinstance(snapshot, dict) else {},
            "tuning": (snapshot.get("tuning", {}) if isinstance(snapshot, dict) else {}),
            "error": None,
        }
        if isinstance(payload["report"], dict):
            payload["report"].setdefault("tuning", dict(payload.get("tuning", {})))
    except Exception as exc:
        state_payload: dict[str, Any] = {}
        try:
            snapshot = quality_snapshot()
            if isinstance(snapshot, dict):
                state_payload = dict(snapshot)
        except Exception:
            state_payload = {}
        payload = {
            "available": True,
            "updated": False,
            "report": {},
            "state": state_payload,
            "tuning": (state_payload.get("tuning", {}) if isinstance(state_payload, dict) else {}),
            "error": {
                "type": exc.__class__.__name__,
                "message": str(exc),
            },
        }

    memory_quality_cache["fingerprint"] = fingerprint
    memory_quality_cache["payload"] = dict(payload)
    return payload


def memory_monitor_payload(*, memory_monitor: Any, proactive_runner_state: dict[str, Any]) -> dict[str, Any]:
    if memory_monitor is None:
        return {"enabled": False, "runner": dict(proactive_runner_state)}
    try:
        payload = dict(memory_monitor.telemetry())
    except Exception:
        payload = {}
    payload["enabled"] = True
    payload["runner"] = dict(proactive_runner_state)
    return payload
