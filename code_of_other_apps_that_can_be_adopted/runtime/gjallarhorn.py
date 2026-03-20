"""
Gjallarhorn — The Warning Horn
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Gjallarhorn (Old Norse: 'yelling horn') is Heimdall's horn, kept at the
roots of Yggdrasil. When sounded, it is heard across all nine worlds and
signals that something demands immediate attention.

  *"Louder than all horns resounds Gjallarhorn."*
      — Gylfaginning, Prose Edda

In ClawLite, Gjallarhorn is the critical alert broadcaster. It watches for
threshold-crossing events and sends a notice to a configured channel when:

  - The Runestone log accumulates N BLOCK events within a time window
    (sustained injection attack in progress)
  - Huginn reports 'high' priority for K consecutive autonomy ticks
    (persistent system degradation)
  - The Völva fails repeatedly (memory maintenance broken)
  - Consecutive autonomy errors exceed a threshold

Architecture:
  GjallarhornWatch — async watcher class
    start(send_fn) → asyncio.Task
    stop()
    ring(reason, details) → send alert via send_fn
    observe_runestone(record) → feed a RunestoneRecord for threshold tracking
    observe_ravens(counsel_dict) → feed ravens_counsel for high-priority tracking
    observe_volva(status_dict) → feed Völva status for failure tracking
    status() → dict

Usage:
  horn = GjallarhornWatch(channel_target="admin:123456")
  horn.start(send_fn=runtime.channels.send)

  # Feed events from the Runestone audit callback:
  horn.observe_runestone(record)
  # Feed ravens counsel from wrap_with_ravens:
  horn.observe_ravens(snapshot.get("ravens_counsel", {}))
"""
from __future__ import annotations

import asyncio
import collections
import time
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable

from clawlite.utils.logging import bind_event

# ── Constants ──────────────────────────────────────────────────────────────────

_GJALLARHORN_RUNE = "ᚷ"     # Gebo — gift, reciprocity; the alarm is a gift
_BLOCK_WINDOW_S = 300.0      # 5-minute sliding window for block counting
_BLOCK_THRESHOLD = 5         # 5+ blocks in window → sound horn
_HIGH_TICK_THRESHOLD = 3     # 3 consecutive high-priority Huginn reports
_VOLVA_FAIL_THRESHOLD = 3    # 3 consecutive Völva failures
_AUTONOMY_ERR_THRESHOLD = 5  # 5 consecutive autonomy errors
_COOLDOWN_S = 600.0          # 10 minutes between alerts for the same reason


SendFn = Callable[[str, str], Awaitable[None]]   # (target, message) → None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── GjallarhornWatch ───────────────────────────────────────────────────────────

class GjallarhornWatch:
    """
    Threshold-based critical alert broadcaster.

    Feed it events from Runestone, ravens, and Völva; it decides when to sound.
    When the horn sounds, it calls `send_fn(target, message)` — typically
    routed through the active channel to the operator's chat.
    """

    def __init__(
        self,
        *,
        channel_target: str = "",
        block_threshold: int = _BLOCK_THRESHOLD,
        block_window_s: float = _BLOCK_WINDOW_S,
        high_tick_threshold: int = _HIGH_TICK_THRESHOLD,
        volva_fail_threshold: int = _VOLVA_FAIL_THRESHOLD,
        autonomy_err_threshold: int = _AUTONOMY_ERR_THRESHOLD,
        cooldown_s: float = _COOLDOWN_S,
    ) -> None:
        self.channel_target = str(channel_target or "").strip()
        self.block_threshold = max(1, int(block_threshold))
        self.block_window_s = max(10.0, float(block_window_s))
        self.high_tick_threshold = max(1, int(high_tick_threshold))
        self.volva_fail_threshold = max(1, int(volva_fail_threshold))
        self.autonomy_err_threshold = max(1, int(autonomy_err_threshold))
        self.cooldown_s = max(0.0, float(cooldown_s))

        self._send_fn: SendFn | None = None
        self._task: asyncio.Task | None = None
        self._running = False
        self._log = bind_event("gjallarhorn")

        # Sliding window of BLOCK timestamps (deque for O(1) rotation)
        self._block_times: collections.deque[float] = collections.deque()
        # Consecutive high-priority Huginn ticks
        self._consecutive_high = 0
        # Consecutive Völva errors
        self._consecutive_volva_fail = 0
        # Consecutive autonomy errors (fed via observe_autonomy)
        self._consecutive_auto_err = 0

        # Cooldown tracking per alert kind
        self._last_ring: dict[str, float] = {}

        # Stats
        self._alerts_sent = 0
        self._last_alert_at = ""
        self._last_alert_reason = ""

    # ── Lifecycle ──────────────────────────────────────────────────────────────

    def start(self, send_fn: SendFn) -> asyncio.Task:
        """Start the watcher. send_fn(target, message) is called on alerts."""
        self._send_fn = send_fn
        self._running = True
        self._task = asyncio.ensure_future(self._idle_loop())
        self._log.info("{} Gjallarhorn watching (target={})", _GJALLARHORN_RUNE, self.channel_target or "unset")
        return self._task

    async def stop(self) -> None:
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    def status(self) -> dict[str, Any]:
        now = time.monotonic()
        return {
            "running": self._running,
            "target": self.channel_target,
            "alerts_sent": self._alerts_sent,
            "last_alert_at": self._last_alert_at,
            "last_alert_reason": self._last_alert_reason,
            "recent_blocks": self._count_recent_blocks(now),
            "consecutive_high_huginn": self._consecutive_high,
            "consecutive_volva_failures": self._consecutive_volva_fail,
            "consecutive_autonomy_errors": self._consecutive_auto_err,
        }

    # ── Event observers ────────────────────────────────────────────────────────

    def observe_runestone(self, record: Any) -> None:
        """
        Feed a RunestoneRecord (or dict) to track injection BLOCK events.
        Call this from the Runestone audit callback when kind starts with
        'injection_block'.
        """
        kind = str(getattr(record, "kind", "") or record.get("kind", "") if isinstance(record, dict) else "")
        if "block" not in kind.lower():
            return
        now = time.monotonic()
        self._block_times.append(now)
        count = self._count_recent_blocks(now)
        if count >= self.block_threshold:
            asyncio.ensure_future(self._maybe_ring(
                "injection_storm",
                f"{_GJALLARHORN_RUNE} INJECTION STORM DETECTED\n"
                f"{count} blocked messages in {self.block_window_s/60:.0f}min window.\n"
                "Sigrid's Ægishjálmr is holding — but someone is probing hard.",
            ))

    def observe_ravens(self, counsel: dict[str, Any]) -> None:
        """
        Feed ravens_counsel dict. Tracks consecutive Huginn 'high' priority.
        """
        if not isinstance(counsel, dict):
            return
        huginn = counsel.get("huginn") or {}
        if not isinstance(huginn, dict):
            return
        priority = str(huginn.get("priority", "") or "")
        if priority == "high":
            self._consecutive_high += 1
            if self._consecutive_high >= self.high_tick_threshold:
                suggestion = str(huginn.get("suggested_action", "") or "")[:200]
                asyncio.ensure_future(self._maybe_ring(
                    "huginn_high",
                    f"{_GJALLARHORN_RUNE} SYSTEM ALERT — HUGINN URGENT\n"
                    f"High priority for {self._consecutive_high} consecutive ticks.\n"
                    f"Huginn says: {suggestion}",
                ))
        else:
            self._consecutive_high = 0

    def observe_volva(self, volva_status: dict[str, Any]) -> None:
        """Feed Völva status dict. Rings on repeated maintenance failures."""
        if not isinstance(volva_status, dict):
            return
        errs = int(volva_status.get("consecutive_errors", 0) or 0)
        self._consecutive_volva_fail = errs
        if errs >= self.volva_fail_threshold:
            last_err = str(volva_status.get("last_error", "") or "")[:160]
            asyncio.ensure_future(self._maybe_ring(
                "volva_failing",
                f"{_GJALLARHORN_RUNE} VÖLVA FAILING\n"
                f"Memory maintenance broken ({errs} consecutive errors).\n"
                f"Last error: {last_err}",
            ))

    def observe_autonomy(self, consecutive_errors: int, last_error: str = "") -> None:
        """Feed autonomy error count. Rings when threshold exceeded."""
        self._consecutive_auto_err = consecutive_errors
        if consecutive_errors >= self.autonomy_err_threshold:
            asyncio.ensure_future(self._maybe_ring(
                "autonomy_down",
                f"{_GJALLARHORN_RUNE} AUTONOMY FAILING\n"
                f"{consecutive_errors} consecutive autonomy errors.\n"
                f"Last: {str(last_error)[:160]}",
            ))

    # ── Ringing ────────────────────────────────────────────────────────────────

    async def ring(self, reason: str, message: str) -> None:
        """Sound the horn — send an alert regardless of cooldown."""
        if not self.channel_target or self._send_fn is None:
            self._log.warning("{} Gjallarhorn: no target/send_fn configured — alert suppressed", _GJALLARHORN_RUNE)
            return
        try:
            await self._send_fn(self.channel_target, message)
            self._alerts_sent += 1
            self._last_alert_at = _utc_now()
            self._last_alert_reason = reason
            self._log.info("{} Gjallarhorn sounded: {} → {}", _GJALLARHORN_RUNE, reason, self.channel_target)
        except Exception as exc:
            self._log.warning("{} Gjallarhorn failed to send alert: {}", _GJALLARHORN_RUNE, exc)

    async def _maybe_ring(self, reason: str, message: str) -> None:
        """Sound the horn only if not in cooldown for this reason."""
        now = time.monotonic()
        last = self._last_ring.get(reason, 0.0)
        if now - last < self.cooldown_s:
            return
        self._last_ring[reason] = now
        await self.ring(reason, message)

    # ── Internals ──────────────────────────────────────────────────────────────

    def _count_recent_blocks(self, now: float) -> int:
        cutoff = now - self.block_window_s
        while self._block_times and self._block_times[0] < cutoff:
            self._block_times.popleft()
        return len(self._block_times)

    async def _idle_loop(self) -> None:
        """Keep the task alive — observations drive the logic, not polling."""
        while self._running:
            await asyncio.sleep(30)


__all__ = ["GjallarhornWatch"]
