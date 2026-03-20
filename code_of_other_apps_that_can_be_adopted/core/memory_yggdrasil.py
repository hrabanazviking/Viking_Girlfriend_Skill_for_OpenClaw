"""
Yggdrasil Memory Layer Mapping
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Yggdrasil — the World Tree — holds nine realms across three levels.
ClawLite's memory tiers mirror this structure:

  ROOTS  (Mímisbrunnr — Well of Wisdom)
         Deep, persistent, slow-changing core knowledge.
         The Norns weave fate here. These memories last.

  TRUNK  (Miðgarðr — the living world)
         Active working context: current session, preferences,
         recent decisions. The present moment of memory.

  BRANCHES (Ásgarðr — realm of higher awareness)
         Episodic and recent memories: what just happened,
         what was just said, the working set of a task.

This module provides:
  - Category → realm mapping
  - Realm metadata (Norse name, description, rune, retrieval weight)
  - A helper to annotate memory summaries with their realm
"""
from __future__ import annotations

from typing import Any

# ── Realm definitions ─────────────────────────────────────────────────────────

REALMS: dict[str, dict[str, Any]] = {
    "roots": {
        "norse_name": "Mímisbrunnr",
        "english": "Well of Wisdom / Roots",
        "rune": "ᛟ",          # Othala — heritage, inheritance, what endures
        "description": "Deep persistent knowledge. Slow to change, long to last.",
        "retrieval_weight": 1.0,
        "decay_multiplier": 0.1,   # very slow decay
    },
    "trunk": {
        "norse_name": "Miðgarðr",
        "english": "Middle World / Trunk",
        "rune": "ᚱ",          # Raidho — the present journey
        "description": "Active working context. The living present of memory.",
        "retrieval_weight": 1.5,
        "decay_multiplier": 1.0,   # normal decay
    },
    "branches": {
        "norse_name": "Ásgarðr",
        "english": "High Realm / Branches",
        "rune": "ᚨ",          # Ansuz — signals, messages, the recent word
        "description": "Recent and episodic memory. What just happened.",
        "retrieval_weight": 2.0,   # highest retrieval boost — recency matters
        "decay_multiplier": 3.0,   # faster decay — branches are pruned
    },
}

# ── Category → realm mapping ──────────────────────────────────────────────────
# Any category not listed here defaults to "trunk".

_CATEGORY_REALM: dict[str, str] = {
    # ROOTS — deep, persistent, identity-level
    "identity":     "roots",
    "user":         "roots",
    "facts":        "roots",
    "knowledge":    "roots",
    "beliefs":      "roots",
    "skills":       "roots",
    "goals":        "roots",
    "relationships":"roots",
    "core":         "roots",
    "persona":      "roots",

    # TRUNK — working context, preferences, decisions
    "context":      "trunk",
    "preferences":  "trunk",
    "decisions":    "trunk",
    "projects":     "trunk",
    "tasks":        "trunk",
    "session":      "trunk",
    "config":       "trunk",
    "state":        "trunk",

    # BRANCHES — recent, episodic, working set
    "recent":       "branches",
    "episodic":     "branches",
    "working":      "branches",
    "events":       "branches",
    "messages":     "branches",
    "logs":         "branches",
    "observations": "branches",
}


def realm_for_category(category: str) -> str:
    """Return the Yggdrasil realm name for a memory category."""
    return _CATEGORY_REALM.get(str(category or "").strip().lower(), "trunk")


def realm_meta(category: str) -> dict[str, Any]:
    """Return full realm metadata dict for a memory category."""
    return dict(REALMS[realm_for_category(category)])


def realm_header(category: str) -> str:
    """Return a single-line Norse realm header for use in memory summaries."""
    realm = realm_for_category(category)
    meta = REALMS[realm]
    return (
        f"{meta['rune']} {meta['norse_name']} ({meta['english']}) — {meta['description']}"
    )


def retrieval_weight(category: str) -> float:
    """Return the retrieval score multiplier for a category's realm."""
    return float(realm_meta(category).get("retrieval_weight", 1.0))


def decay_multiplier(category: str) -> float:
    """Return the decay rate multiplier for a category's realm."""
    return float(realm_meta(category).get("decay_multiplier", 1.0))


__all__ = [
    "REALMS",
    "decay_multiplier",
    "realm_for_category",
    "realm_header",
    "realm_meta",
    "retrieval_weight",
]
