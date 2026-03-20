from __future__ import annotations

from typing import Any, Callable


def quality_mode_from_state(
    score: int,
    drift: str,
    degrading_streak: int,
    last_error: str,
    *,
    has_report: bool,
) -> tuple[str, str]:
    if not has_report:
        return "normal", "quality_state_uninitialized"

    drift_clean = str(drift or "").strip().lower()
    has_error = bool(str(last_error or "").strip())
    if has_error:
        return "severe", "quality_tuning_error"
    if score <= 40 or degrading_streak >= 4:
        return "severe", "quality_score_or_streak_critical"
    if drift_clean == "degrading" and (degrading_streak >= 3 or score <= 55):
        return "severe", "quality_drift_critical"
    if score <= 70 or degrading_streak >= 2 or drift_clean == "degrading":
        return "degraded", "quality_drift_or_score_warning"
    return "normal", "quality_stable"


def integration_actor_class(actor: str) -> str:
    clean = str(actor or "").strip().lower()
    if clean in {"system", "gateway", "supervisor", "control", "runtime", "ops", "operator", "admin"}:
        return "privileged"
    if clean in {"subagent", "delegate", "worker", "tool", "skill", "executor"} or "subagent" in clean:
        return "delegated"
    if clean in {"agent", "assistant", "planner", "default"}:
        return "worker"
    return "worker"


def integration_policy(
    *,
    snapshot: dict[str, Any],
    actor: str,
    session_id: str = "",
    quality_int: Callable[..., int],
) -> dict[str, Any]:
    current = snapshot.get("current", {}) if isinstance(snapshot.get("current", {}), dict) else {}
    tuning = snapshot.get("tuning", {}) if isinstance(snapshot.get("tuning", {}), dict) else {}
    drift_payload = current.get("drift", {}) if isinstance(current.get("drift", {}), dict) else {}

    has_report = bool(current) and "score" in current
    score = quality_int(current.get("score", 100 if not has_report else 0), minimum=0, default=100 if not has_report else 0)
    if score > 100:
        score = 100
    degrading_streak = quality_int(tuning.get("degrading_streak", 0), minimum=0, default=0)
    drift = str(drift_payload.get("assessment", "baseline" if not has_report else "stable") or "")
    last_error = str(tuning.get("last_error", "") or "")
    mode, reason = quality_mode_from_state(
        score,
        drift,
        degrading_streak,
        last_error,
        has_report=has_report,
    )

    actor_clean = str(actor or "default").strip() or "default"
    actor_class = integration_actor_class(actor_clean)

    if mode == "severe":
        allow_memory_write = False
        allow_skill_exec = False
        allow_subagent_spawn = False
        recommended_search_limit = 2
    elif mode == "degraded":
        allow_memory_write = True
        allow_skill_exec = actor_class == "privileged"
        allow_subagent_spawn = actor_class == "privileged"
        recommended_search_limit = 4
    else:
        allow_memory_write = True
        allow_skill_exec = True
        allow_subagent_spawn = actor_class != "delegated"
        recommended_search_limit = 8

    if actor_class == "delegated":
        allow_subagent_spawn = False
        recommended_search_limit = max(1, recommended_search_limit - 1)
        if mode != "normal":
            allow_skill_exec = False
            allow_memory_write = False if mode == "severe" else allow_memory_write

    quality_summary = {
        "score": score,
        "drift": drift,
        "degrading_streak": degrading_streak,
        "last_error": last_error,
        "updated_at": str(snapshot.get("updated_at", "") or ""),
        "has_report": has_report,
    }
    return {
        "actor": actor_clean,
        "actor_class": actor_class,
        "session_id": str(session_id or ""),
        "mode": mode,
        "reason": reason,
        "quality": quality_summary,
        "allow_memory_write": bool(allow_memory_write),
        "allow_skill_exec": bool(allow_skill_exec),
        "allow_subagent_spawn": bool(allow_subagent_spawn),
        "recommended_search_limit": int(recommended_search_limit),
    }


def integration_policies_snapshot(
    *,
    session_id: str = "",
    policy_resolver: Callable[[str], dict[str, Any]],
) -> dict[str, Any]:
    actors = ("system", "agent", "subagent", "tool")
    policies = {name: policy_resolver(name) for name in actors}
    mode = "normal"
    rank = {"normal": 0, "degraded": 1, "severe": 2}
    for payload in policies.values():
        candidate = str(payload.get("mode", "normal") or "normal")
        if rank.get(candidate, 0) > rank.get(mode, 0):
            mode = candidate
    return {
        "session_id": str(session_id or ""),
        "mode": mode,
        "quality": policies["agent"].get("quality", {}),
        "policies": policies,
    }


def integration_hint(policy: dict[str, Any]) -> str:
    mode = str(policy.get("mode", "normal") or "normal")
    if mode == "normal":
        return ""
    if mode == "severe":
        return (
            "Memory quality is severe; avoid writes, skip skill/subagent actions, "
            "and prefer minimal retrieval while stabilization runs."
        )
    return (
        "Memory quality is degraded; keep retrieval focused and avoid expensive "
        "delegation unless strictly necessary."
    )


__all__ = [
    "integration_actor_class",
    "integration_hint",
    "integration_policies_snapshot",
    "integration_policy",
    "quality_mode_from_state",
]
