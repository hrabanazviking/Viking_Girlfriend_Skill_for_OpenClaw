"""
Völva — The Oracle / Proactive Memory Guardian
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In Norse tradition, the Völva (Old Norse: vǫlva, 'wand-carrier') was a
seeress who could perceive the threads of fate woven by the Norns and
advise chieftains before great undertakings.

  *"I remember giants born at the dawn of time,
   who long ago nourished me. Nine worlds I know,
   the nine abodes of the glorious world-tree."*
      — Völuspá, stanza 2

In ClawLite, the Völva is a background async daemon that:

  1. Reads Muninn's staleness report from the ravens_counsel (when available)
     or runs its own lightweight memory audit if no counsel is present.

  2. Identifies memory categories that are stale (not updated in > STALE_H
     hours) or oversize (> CONSOLIDATION_THRESHOLD items).

  3. Triggers memory maintenance (consolidation / decay pruning) on the
     identified categories so that Sigrid's next conversation opens with
     fresh, relevant context.

  4. Writes audit records to the Runestone log for all maintenance actions.

  5. Backs off exponentially on provider errors to avoid hammering the LLM
     during outages.

Architecture:
  VolvaOracle — daemon class
    start(memory, consolidator, *, runestone=None) → background asyncio.Task
    stop()
    status() → dict
    _tick(snapshot) → coroutine — one maintenance cycle

Integration:
  Called by the gateway at startup alongside other background tasks.
  Optionally receives ravens_counsel via the autonomy snapshot callback.

The Völva acts alone, in the background, without disturbing the living.
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any

from clawlite.utils.logging import bind_event

# ── Constants ──────────────────────────────────────────────────────────────────

_VOLVA_RUNE = "ᚹ"          # Wunjo — joy in harmony; the reward of care
_DEFAULT_INTERVAL_S = 1800  # run every 30 minutes
_STALE_H = 48.0             # category untouched 48h → stale
_CONSOLIDATION_THRESHOLD = 50  # > 50 items → trigger consolidation
_MAX_CATEGORIES_PER_TICK = 3   # limit LLM calls per tick
_BACKOFF_BASE_S = 60.0
_BACKOFF_MAX_S = 3600.0


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hours_since(iso_str: str) -> float:
    if not iso_str:
        return 0.0
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return max(0.0, (now - dt).total_seconds() / 3600.0)
    except Exception:
        return 0.0


# ── VolvaOracle ────────────────────────────────────────────────────────────────

class VolvaOracle:
    """
    Background memory maintenance daemon.

    The Völva wakes periodically, reads the memory landscape, and tends
    whatever has grown stale or oversize — so Sigrid always works with
    well-tended, current knowledge.
    """

    def __init__(
        self,
        *,
        interval_s: float = _DEFAULT_INTERVAL_S,
        stale_hours: float = _STALE_H,
        consolidation_threshold: int = _CONSOLIDATION_THRESHOLD,
        max_categories_per_tick: int = _MAX_CATEGORIES_PER_TICK,
    ) -> None:
        self.interval_s = max(60.0, float(interval_s))
        self.stale_hours = max(1.0, float(stale_hours))
        self.consolidation_threshold = max(10, int(consolidation_threshold))
        self.max_categories_per_tick = max(1, int(max_categories_per_tick))

        self._memory: Any = None
        self._consolidator: Any = None
        self._runestone: Any = None
        self._task: asyncio.Task | None = None
        self._running = False

        # Stats
        self._ticks = 0
        self._categories_consolidated = 0
        self._categories_pruned = 0
        self._last_tick_at = ""
        self._last_error = ""
        self._consecutive_errors = 0
        self._backoff_until = 0.0

        self._log = bind_event("volva")

    # ── Lifecycle ──────────────────────────────────────────────────────────────

    def start(
        self,
        memory: Any,
        consolidator: Any,
        *,
        runestone: Any = None,
    ) -> asyncio.Task:
        """
        Start the Völva daemon as a background asyncio Task.

        Args:
            memory:       MemoryEngine or equivalent — must expose
                          list_categories() → list[dict] and/or
                          category_item_count(category) → int
            consolidator: LLMConsolidator — must expose
                          consolidate(records, category=...) coroutine
            runestone:    Optional RunestoneLog for audit trail
        """
        self._memory = memory
        self._consolidator = consolidator
        self._runestone = runestone
        self._running = True
        self._task = asyncio.ensure_future(self._loop())
        self._log.info("{} Völva oracle started (interval={}s)", _VOLVA_RUNE, self.interval_s)
        return self._task

    async def stop(self) -> None:
        """Gracefully stop the daemon."""
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self._log.info("{} Völva oracle stopped", _VOLVA_RUNE)

    def status(self) -> dict[str, Any]:
        return {
            "running": self._running and (self._task is not None and not self._task.done()),
            "interval_s": self.interval_s,
            "ticks": self._ticks,
            "categories_consolidated": self._categories_consolidated,
            "categories_pruned": self._categories_pruned,
            "last_tick_at": self._last_tick_at,
            "last_error": self._last_error,
            "consecutive_errors": self._consecutive_errors,
        }

    # ── Snapshot-driven tick (called by autonomy with ravens counsel) ──────────

    async def tick_from_snapshot(self, snapshot: dict[str, Any]) -> None:
        """
        Run one maintenance cycle informed by the autonomy snapshot.

        This is called by the autonomy service's run_callback when the
        ravens_counsel includes Muninn's stale category report. It is
        also safe to call without ravens_counsel — the Völva will run
        her own audit in that case.
        """
        await self._tick(snapshot)

    # ── Internal loop ──────────────────────────────────────────────────────────

    async def _loop(self) -> None:
        while self._running:
            now = asyncio.get_event_loop().time()
            if now < self._backoff_until:
                await asyncio.sleep(min(self._backoff_until - now, 30.0))
                continue
            try:
                await self._tick({})
                self._consecutive_errors = 0
                self._last_error = ""
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                self._consecutive_errors += 1
                self._last_error = str(exc)[:200]
                backoff = min(
                    _BACKOFF_BASE_S * (2 ** min(self._consecutive_errors - 1, 6)),
                    _BACKOFF_MAX_S,
                )
                self._backoff_until = asyncio.get_event_loop().time() + backoff
                self._log.warning(
                    "{} Völva error (attempt {}): {} — backing off {}s",
                    _VOLVA_RUNE, self._consecutive_errors, exc, round(backoff),
                )
            await asyncio.sleep(self.interval_s)

    async def _tick(self, snapshot: dict[str, Any]) -> None:
        self._ticks += 1
        self._last_tick_at = _utc_now()

        stale, oversize = self._identify_targets(snapshot)
        if not stale and not oversize:
            self._log.info("{} Völva tick #{} — all memory realms healthy", _VOLVA_RUNE, self._ticks)
            return

        total = len(stale) + len(oversize)
        self._log.info(
            "{} Völva tick #{} — {} stale, {} oversize categories to tend",
            _VOLVA_RUNE, self._ticks, len(stale), len(oversize),
        )

        # Work through highest-priority categories up to the per-tick cap
        candidates = list(dict.fromkeys([*oversize, *stale]))[:self.max_categories_per_tick]

        for category in candidates:
            await self._tend_category(category, is_oversize=(category in oversize))

    def _identify_targets(self, snapshot: dict[str, Any]) -> tuple[list[str], list[str]]:
        """
        Return (stale_categories, oversize_categories) to tend this tick.

        Prefers Muninn's staleness data from ravens_counsel in the snapshot,
        falls back to querying the memory engine directly.
        """
        stale: list[str] = []
        oversize: list[str] = []

        # ── Prefer Muninn's pre-computed analysis ─────────────────────────────
        counsel = (snapshot or {}).get("ravens_counsel") or {}
        if isinstance(counsel, dict):
            muninn = counsel.get("muninn") or {}
            if isinstance(muninn, dict):
                stale = list(muninn.get("stale_categories") or [])
                if muninn.get("consolidation_needed"):
                    # Derive oversize from memory meta if available
                    mem_meta = snapshot.get("memory") or snapshot.get("memory_meta") or {}
                    if isinstance(mem_meta, dict):
                        for cat, cat_data in mem_meta.items():
                            if not isinstance(cat_data, dict):
                                continue
                            count = int(cat_data.get("count", 0) or cat_data.get("items", 0) or 0)
                            if count > self.consolidation_threshold:
                                oversize.append(str(cat))
                if stale or oversize:
                    return stale, oversize

        # ── Fallback: query memory engine directly ────────────────────────────
        if self._memory is None:
            return [], []

        try:
            list_fn = getattr(self._memory, "list_categories", None)
            if not callable(list_fn):
                return [], []
            categories = list_fn() or []
            for cat_info in categories:
                if not isinstance(cat_info, dict):
                    continue
                cat = str(cat_info.get("category", "") or "")
                if not cat:
                    continue
                count = int(cat_info.get("count", 0) or 0)
                updated = str(cat_info.get("updated_at", "") or "")
                if count > self.consolidation_threshold:
                    oversize.append(cat)
                elif _hours_since(updated) > self.stale_hours and count > 0:
                    stale.append(cat)
        except Exception as exc:
            self._log.warning("{} Völva memory audit failed: {}", _VOLVA_RUNE, exc)

        return stale, oversize

    async def _tend_category(self, category: str, *, is_oversize: bool) -> None:
        """Run consolidation or pruning on a single memory category."""
        action = "consolidate" if is_oversize else "refresh"
        self._log.info("{} Völva tending '{}' ({})", _VOLVA_RUNE, category, action)

        try:
            if is_oversize and self._consolidator is not None:
                # Fetch records and consolidate
                records = self._fetch_category_records(category)
                if records:
                    await self._consolidator.consolidate(records, category=category)
                    self._categories_consolidated += 1
                    self._audit("volva_consolidate", category=category, count=len(records))
            else:
                # For stale categories, trigger a decay prune if available
                prune_fn = getattr(self._memory, "purge_decayed", None)
                if callable(prune_fn):
                    pruned = await prune_fn(category=category)
                    self._categories_pruned += 1
                    self._audit("volva_prune", category=category, pruned=pruned or 0)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            self._log.warning(
                "{} Völva failed tending '{}': {}", _VOLVA_RUNE, category, exc
            )

    def _fetch_category_records(self, category: str) -> list[Any]:
        """Retrieve records for a category from the memory engine."""
        try:
            recall_fn = getattr(self._memory, "recall_category", None) or \
                        getattr(self._memory, "recall", None)
            if not callable(recall_fn):
                return []
            return list(recall_fn(category, limit=100) or [])
        except Exception:
            return []

    def _audit(self, kind: str, **details: Any) -> None:
        """Write to Runestone if registered."""
        if self._runestone is not None:
            try:
                self._runestone.append(kind=kind, source="volva", details=dict(details))
            except Exception:
                pass


__all__ = ["VolvaOracle"]
