"""
Norns — The Three Fates
~~~~~~~~~~~~~~~~~~~~~~~~
The Norns (Old Norse: nornir) are the weavers of fate in Norse cosmology.
They sit at the foot of Yggdrasil beside the well Urðarbrunnr and weave
the threads of destiny for gods and mortals alike.

  URÐ  (That Which Was) — the past; what has been decided and done
  VERÐANDI  (That Which Is Becoming) — the present; the living moment
  SKULD  (That Which Shall Be) — the future; obligation and necessity

  *"There dwelt two in the dwelling; Urð was one called,
   Verðandi the other — on a tablet they carved —
   Skuld the third; laws they established,
   life allotted to the children of man."*
      — Völuspá, stanza 20

In ClawLite, the Norns shape how the autonomy agent reasons over each tick.
Instead of a flat snapshot dump, the prompt is structured into three phases:

  PHASE 1 — URÐ: "What has been"
    Recent session history, last autonomy results, resolved incidents,
    Huginn's historical patterns. The agent sees what was decided before.

  PHASE 2 — VERÐANDI: "What is becoming"
    Live system state: current health, running jobs, active sessions,
    Huginn & Muninn's fresh analysis. The agent sees what is true now.

  PHASE 3 — SKULD: "What must be"
    Pending tasks, open incidents, memory maintenance backlog from Völva,
    Gjallarhorn's active alert state. The agent sees what demands action.

Architecture:
  NornsFrame — dataclass holding the three sections
  weave(snapshot) → NornsFrame — structures a snapshot into three phases
  norns_prompt(frame) → str — renders the frame as a structured prompt string
  norns_autonomy_prompt(snapshot) → str — convenience: weave + render
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


# ── NornsFrame ─────────────────────────────────────────────────────────────────

@dataclass(slots=True)
class NornsFrame:
    """
    The three phases of fate, structured for the autonomy agent.

    Each phase is a dict of key → value pairs that will be rendered
    as a JSON block in the prompt. Keys are concise labels.
    """
    urd: dict[str, Any] = field(default_factory=dict)        # Past
    verdandi: dict[str, Any] = field(default_factory=dict)   # Present
    skuld: dict[str, Any] = field(default_factory=dict)      # Future/obligations

    def to_dict(self) -> dict[str, Any]:
        return {
            "urd": self.urd,
            "verdandi": self.verdandi,
            "skuld": self.skuld,
        }


# ── Weaving ────────────────────────────────────────────────────────────────────

def weave(snapshot: dict[str, Any]) -> NornsFrame:
    """
    Weave a raw autonomy snapshot into a structured NornsFrame.

    Extracts relevant fields into three temporal phases so the LLM
    sees the snapshot in a causally ordered, purposeful structure
    rather than a flat JSON dump.
    """
    s = snapshot or {}
    counsel = s.get("ravens_counsel") or {}
    huginn = counsel.get("huginn") or {} if isinstance(counsel, dict) else {}
    muninn = counsel.get("muninn") or {} if isinstance(counsel, dict) else {}

    # ── URÐ: What has been ────────────────────────────────────────────────────
    urd: dict[str, Any] = {}
    auto = s.get("autonomy") or {}
    if isinstance(auto, dict):
        if auto.get("last_run_at"):
            urd["last_autonomy_run"] = auto["last_run_at"]
        if auto.get("last_result_excerpt"):
            urd["last_result"] = str(auto["last_result_excerpt"])[:200]
        urd["total_ticks"] = auto.get("ticks", 0)
        urd["run_success"] = auto.get("run_success", 0)
        urd["run_failures"] = auto.get("run_failures", 0)

    history = s.get("history") or s.get("recent_history") or []
    if isinstance(history, list) and history:
        urd["recent_history_count"] = len(history)
        # Keep last 3 summaries only
        urd["last_messages"] = [
            {"role": str(m.get("role", "")), "preview": str(m.get("content", ""))[:100]}
            for m in history[-3:]
            if isinstance(m, dict)
        ]

    if huginn.get("error_trend") not in (None, "", "unknown"):
        urd["error_trend"] = huginn["error_trend"]

    # ── VERÐANDI: What is becoming ────────────────────────────────────────────
    verdandi: dict[str, Any] = {}
    health = s.get("health") or {}
    if isinstance(health, dict):
        verdandi["component_health"] = {
            k: (v.get("running", True) if isinstance(v, dict) else bool(v))
            for k, v in health.items()
        }

    workers = s.get("workers") or s.get("queue") or {}
    if isinstance(workers, dict):
        verdandi["jobs"] = {
            "pending": workers.get("pending_jobs", 0),
            "running": workers.get("running_jobs", 0),
            "failed": workers.get("failed", 0),
        }

    sessions = s.get("sessions") or {}
    if isinstance(sessions, dict):
        verdandi["active_sessions"] = len(sessions)

    # Include Huginn's live analysis
    if huginn:
        verdandi["huginn"] = {
            "priority": huginn.get("priority", "unknown"),
            "attention": huginn.get("attention_items", [])[:3],
            "warnings": huginn.get("health_warnings", [])[:3],
        }

    # Provider state
    provider = s.get("provider") or {}
    if isinstance(provider, dict):
        verdandi["provider"] = {
            "name": provider.get("provider", "unknown"),
            "suppressed": bool(provider.get("suppression_reason")),
        }

    # ── SKULD: What must be ───────────────────────────────────────────────────
    skuld: dict[str, Any] = {}

    # Muninn's memory obligations
    if muninn:
        stale = muninn.get("stale_categories") or []
        if stale:
            skuld["stale_memory_realms"] = stale[:5]
        if muninn.get("consolidation_needed"):
            skuld["memory_consolidation_needed"] = True

    # Huginn's suggested action
    if huginn.get("suggested_action"):
        skuld["huginn_action"] = huginn["suggested_action"]

    # Stalled sessions
    stalled = huginn.get("stalled_sessions") or []
    if stalled:
        skuld["stalled_sessions"] = stalled[:5]

    # Consecutive errors require action
    if isinstance(auto, dict) and int(auto.get("consecutive_error_count", 0) or 0) >= 2:
        skuld["consecutive_errors"] = auto["consecutive_error_count"]
        skuld["last_error"] = str(auto.get("last_error", ""))[:120]

    # Völva / memory maintenance backlog
    volva = s.get("volva") or {}
    if isinstance(volva, dict) and int(volva.get("consecutive_errors", 0) or 0) >= 2:
        skuld["memory_maintenance_failing"] = True
        skuld["volva_error"] = str(volva.get("last_error", ""))[:120]

    return NornsFrame(urd=urd, verdandi=verdandi, skuld=skuld)


# ── Rendering ──────────────────────────────────────────────────────────────────

def norns_prompt(frame: NornsFrame) -> str:
    """
    Render a NornsFrame as a structured prompt string.

    The three phases are presented in causal order with clear Norse labels
    so the LLM understands the temporal structure of the analysis.
    """
    def _block(d: dict[str, Any]) -> str:
        return json.dumps(d, ensure_ascii=False, indent=2, sort_keys=False) if d else "{}"

    return (
        "=== URÐ — What Has Been (past context) ===\n"
        f"{_block(frame.urd)}\n\n"
        "=== VERÐANDI — What Is Becoming (present state) ===\n"
        f"{_block(frame.verdandi)}\n\n"
        "=== SKULD — What Must Be (obligations & actions needed) ===\n"
        f"{_block(frame.skuld)}\n"
    )


def norns_autonomy_prompt(snapshot: dict[str, Any]) -> str:
    """
    Convenience: weave a snapshot and render the full Norns prompt.

    Used in place of raw json.dumps(snapshot) for autonomy tick prompts.
    The structured three-phase format guides the LLM toward causal,
    purposeful reasoning rather than pattern-matching over a flat dump.
    """
    return norns_prompt(weave(snapshot))


__all__ = [
    "NornsFrame",
    "norns_autonomy_prompt",
    "norns_prompt",
    "weave",
]
