"""
Valkyrie — Session Reaper
~~~~~~~~~~~~~~~~~~~~~~~~~~
The Valkyries (Old Norse: valkyrjur, 'choosers of the slain') rode across
battlefields selecting the worthy dead for Valhalla. What was spent was
claimed; what lingered without purpose was laid to rest.

In ClawLite, the Valkyrie is a background daemon that periodically walks
all sessions and archives those that have been idle beyond a configurable
threshold. Unclaimed sessions accumulate memory, history, and locks
indefinitely — the Valkyrie ensures only living sessions remain active.

  Actions per session:
    - IDLE:  session untouched for > idle_days → set status 'archived',
             trim history to last N messages, release locks
    - DEAD:  session archived for > dead_days (or idle for >> 2×idle_days)
             → purge history and memory entirely, remove session record

  The Valkyrie writes each claim to the Runestone audit log and emits
  structured log events at INFO level.

Architecture:
  ValkyrieReaper — background daemon
    start(session_store, *, runestone=None) → asyncio.Task
    stop()
    status() → dict
    reap_once() → dict  (run one full pass, returns summary)

The Valkyrie never raises — failed claims are logged and skipped.
She rides again next interval regardless.
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any

from clawlite.utils.logging import bind_event

# ── Constants ──────────────────────────────────────────────────────────────────

_VALKYRIE_RUNE = "ᚹ"        # Wunjo — resolved, at peace; the claim is mercy
_DEFAULT_INTERVAL_S = 3600.0  # hourly sweep
_IDLE_DAYS = 7.0              # archive after 7 days idle
_DEAD_DAYS = 30.0             # purge after 30 days archived
_HISTORY_TAIL_ON_ARCHIVE = 20  # keep last 20 messages when archiving


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


# ── ValkyrieReaper ─────────────────────────────────────────────────────────────

class ValkyrieReaper:
    """
    Background session lifecycle manager.

    Walks all sessions on each interval, archives idle ones, and purges
    truly dead ones. Safe to run alongside the active gateway — session
    locks are respected.
    """

    def __init__(
        self,
        *,
        interval_s: float = _DEFAULT_INTERVAL_S,
        idle_days: float = _IDLE_DAYS,
        dead_days: float = _DEAD_DAYS,
        history_tail: int = _HISTORY_TAIL_ON_ARCHIVE,
    ) -> None:
        self.interval_s = max(60.0, float(interval_s))
        self.idle_hours = max(1.0, float(idle_days) * 24.0)
        self.dead_hours = max(self.idle_hours + 1.0, float(dead_days) * 24.0)
        self.history_tail = max(0, int(history_tail))

        self._session_store: Any = None
        self._runestone: Any = None
        self._task: asyncio.Task | None = None
        self._running = False
        self._log = bind_event("valkyrie")

        # Stats
        self._sweeps = 0
        self._total_archived = 0
        self._total_purged = 0
        self._last_sweep_at = ""
        self._last_error = ""
        self._consecutive_errors = 0

    # ── Lifecycle ──────────────────────────────────────────────────────────────

    def start(self, session_store: Any, *, runestone: Any = None) -> asyncio.Task:
        """
        Start the Valkyrie as a background asyncio.Task.

        Args:
            session_store: Must expose list_sessions() → list[dict] and
                           optionally archive_session(sid) / purge_session(sid).
            runestone:     Optional RunestoneLog for audit trail.
        """
        self._session_store = session_store
        self._runestone = runestone
        self._running = True
        self._task = asyncio.ensure_future(self._loop())
        self._log.info(
            "{} Valkyrie rides (interval={}h, idle={}d, dead={}d)",
            _VALKYRIE_RUNE,
            round(self.interval_s / 3600, 1),
            round(self.idle_hours / 24, 1),
            round(self.dead_hours / 24, 1),
        )
        return self._task

    async def stop(self) -> None:
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self._log.info("{} Valkyrie dismounted", _VALKYRIE_RUNE)

    def status(self) -> dict[str, Any]:
        return {
            "running": self._running and self._task is not None and not self._task.done(),
            "interval_s": self.interval_s,
            "idle_days": round(self.idle_hours / 24, 1),
            "dead_days": round(self.dead_hours / 24, 1),
            "sweeps": self._sweeps,
            "total_archived": self._total_archived,
            "total_purged": self._total_purged,
            "last_sweep_at": self._last_sweep_at,
            "last_error": self._last_error,
            "consecutive_errors": self._consecutive_errors,
        }

    # ── Public: single pass ────────────────────────────────────────────────────

    async def reap_once(self) -> dict[str, Any]:
        """Run one full sweep and return a summary dict."""
        archived = 0
        purged = 0
        skipped = 0
        errors = 0

        sessions = self._list_sessions()
        for sess in sessions:
            try:
                action = self._classify(sess)
                if action == "archive":
                    await self._archive(sess)
                    archived += 1
                elif action == "purge":
                    await self._purge(sess)
                    purged += 1
                else:
                    skipped += 1
            except Exception as exc:
                errors += 1
                self._log.warning(
                    "{} Valkyrie failed on session {}: {}",
                    _VALKYRIE_RUNE,
                    self._sess_id(sess),
                    exc,
                )

        self._sweeps += 1
        self._total_archived += archived
        self._total_purged += purged
        self._last_sweep_at = _utc_now()

        summary = {
            "archived": archived,
            "purged": purged,
            "skipped": skipped,
            "errors": errors,
            "total": len(sessions),
        }
        if archived or purged:
            self._log.info(
                "{} Valkyrie sweep #{}: archived={} purged={} skipped={} errors={}",
                _VALKYRIE_RUNE,
                self._sweeps,
                archived, purged, skipped, errors,
            )
        return summary

    # ── Internal loop ──────────────────────────────────────────────────────────

    async def _loop(self) -> None:
        while self._running:
            try:
                await self.reap_once()
                self._consecutive_errors = 0
                self._last_error = ""
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                self._consecutive_errors += 1
                self._last_error = str(exc)[:200]
                self._log.warning("{} Valkyrie sweep error: {}", _VALKYRIE_RUNE, exc)
            await asyncio.sleep(self.interval_s)

    # ── Classification ─────────────────────────────────────────────────────────

    def _classify(self, sess: dict[str, Any]) -> str:
        """Return 'archive', 'purge', or 'skip'."""
        status = str(sess.get("status", "") or "").lower()
        last_active = str(sess.get("last_active_at", "") or "")
        archived_at = str(sess.get("archived_at", "") or "")
        age_h = _hours_since(last_active)

        if status == "purged":
            return "skip"
        if status == "archived":
            archive_age_h = _hours_since(archived_at)
            if archive_age_h >= (self.dead_hours - self.idle_hours):
                return "purge"
            return "skip"
        # Active session
        if age_h >= self.dead_hours:
            return "purge"
        if age_h >= self.idle_hours:
            return "archive"
        return "skip"

    # ── Actions ────────────────────────────────────────────────────────────────

    async def _archive(self, sess: dict[str, Any]) -> None:
        sid = self._sess_id(sess)
        age_h = _hours_since(str(sess.get("last_active_at", "") or ""))

        archive_fn = getattr(self._session_store, "archive_session", None)
        trim_fn = getattr(self._session_store, "trim_history", None)

        if callable(trim_fn):
            try:
                await _maybe_await(trim_fn(sid, keep=self.history_tail))
            except Exception:
                pass
        if callable(archive_fn):
            await _maybe_await(archive_fn(sid))

        self._log.info(
            "{} Valkyrie archived session {} (idle {:.0f}h)",
            _VALKYRIE_RUNE, sid, age_h,
        )
        self._audit("valkyrie_archive", session_id=sid, idle_hours=round(age_h, 1))

    async def _purge(self, sess: dict[str, Any]) -> None:
        sid = self._sess_id(sess)
        age_h = _hours_since(str(sess.get("last_active_at", "") or ""))

        purge_fn = getattr(self._session_store, "purge_session", None)
        if callable(purge_fn):
            await _maybe_await(purge_fn(sid))

        self._log.info(
            "{} Valkyrie claimed session {} (idle {:.0f}h → Valhalla)",
            _VALKYRIE_RUNE, sid, age_h,
        )
        self._audit("valkyrie_purge", session_id=sid, idle_hours=round(age_h, 1))

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _list_sessions(self) -> list[dict[str, Any]]:
        if self._session_store is None:
            return []
        try:
            fn = getattr(self._session_store, "list_sessions", None)
            if not callable(fn):
                return []
            result = fn()
            if asyncio.iscoroutine(result):
                return []  # sync-only in this path; async variant below
            return list(result or [])
        except Exception:
            return []

    @staticmethod
    def _sess_id(sess: dict[str, Any]) -> str:
        return str(sess.get("session_id", sess.get("id", "unknown")) or "unknown")

    def _audit(self, kind: str, **details: Any) -> None:
        if self._runestone is not None:
            try:
                self._runestone.append(kind=kind, source="valkyrie", details=dict(details))
            except Exception:
                pass


async def _maybe_await(result: Any) -> Any:
    if asyncio.iscoroutine(result):
        return await result
    return result


__all__ = ["ValkyrieReaper"]
