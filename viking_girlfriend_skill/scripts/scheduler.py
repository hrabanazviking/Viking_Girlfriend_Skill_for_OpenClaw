"""
scheduler.py — Sigrid's Time & Background Task Scheduler
=========================================================

Adapted from timeline_service.py. Drops the game simulation clock
(turn-minutes, seasons, travel tables) and replaces it with real
wall-clock time awareness plus APScheduler for background periodic tasks.

Two responsibilities:

  1. Time-of-day awareness — maps the real current hour to a named
     segment (dawn / morning / midday / afternoon / evening / night).
     Sigrid's mood, tone, and energy shift across the day; prompt_synthesizer
     reads this to tune her voice.

  2. Background job scheduler — APScheduler BackgroundScheduler manages
     periodic callbacks (heartbeat ticks, memory consolidation, dream
     ticks, oracle refresh, etc.). Jobs are registered by name and can
     be started, paused, and removed at runtime.

Norse framing: Dagr (the god of Day) drives his horse Skinfaxi across
the sky. The light he casts changes everything beneath it — Sigrid is
alive to the time of day in ways that matter.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from scripts.state_bus import StateBus, StateEvent

logger = logging.getLogger(__name__)

# ─── Time segments ────────────────────────────────────────────────────────────
# Maps real wall-clock hour (0-23) to a named time-of-day segment.
# Each segment carries a mood hint for prompt_synthesizer.

_TIME_SEGMENTS: tuple = (
    (5,  "deep night"),     # 00:00–04:59
    (8,  "dawn"),           # 05:00–07:59
    (12, "morning"),        # 08:00–11:59
    (14, "midday"),         # 12:00–13:59
    (18, "afternoon"),      # 14:00–17:59
    (21, "evening"),        # 18:00–20:59
    (24, "night"),          # 21:00–23:59
)

_SEGMENT_HINTS: Dict[str, str] = {
    "deep night": "quiet and introspective; the veil is thin",
    "dawn":       "liminal and gentle; the world waking",
    "morning":    "alert and purposeful; fresh energy",
    "midday":     "clear and direct; full presence",
    "afternoon":  "warm and steady; flowing forward",
    "evening":    "reflective and warm; candle-light mind",
    "night":      "soft and inward; the day settling",
}


def _current_time_of_day() -> str:
    """Map the current local hour to a named time-of-day segment."""
    hour = datetime.now().hour
    for threshold, label in _TIME_SEGMENTS:
        if hour < threshold:
            return label
    return "night"


# ─── SchedulerState ───────────────────────────────────────────────────────────


@dataclass(slots=True)
class SchedulerState:
    """Typed snapshot of scheduler health and current time awareness."""

    time_of_day: str
    time_hint: str              # mood/tone hint for this segment
    active_job_count: int
    job_names: List[str]
    running: bool
    prompt_hint: str
    timestamp: str
    degraded: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "time": {
                "segment": self.time_of_day,
                "hint": self.time_hint,
            },
            "jobs": {
                "active": self.active_job_count,
                "names": self.job_names,
                "running": self.running,
            },
            "prompt_hint": self.prompt_hint,
            "timestamp": self.timestamp,
            "degraded": self.degraded,
        }


# ─── SchedulerService ─────────────────────────────────────────────────────────


class SchedulerService:
    """Real-time scheduler — time-of-day awareness + APScheduler background jobs.

    Call ``start()`` to begin background processing. Register periodic
    callbacks with ``register_job()``. The scheduler degrades gracefully
    if APScheduler is not available — time-of-day awareness still works.
    """

    def __init__(self, timezone_str: str = "local") -> None:
        self._timezone_str = timezone_str
        self._jobs: Dict[str, Dict[str, Any]] = {}   # name → {func, interval_s, job_id}
        self._scheduler = None
        self._running: bool = False
        self._degraded: bool = False

        self._init_apscheduler()

    # ── Public API ────────────────────────────────────────────────────────────

    def register_job(
        self,
        name: str,
        func: Callable[[], None],
        interval_s: float,
        replace_existing: bool = True,
    ) -> bool:
        """Register a named periodic job.

        Returns True if the job was registered (and scheduled if running).
        ``func`` must be a zero-argument callable.
        """
        if name in self._jobs and not replace_existing:
            logger.debug("SchedulerService: job '%s' already registered.", name)
            return False

        self._jobs[name] = {
            "func": func,
            "interval_s": interval_s,
            "job_id": f"sigrid_{name}",
        }

        if self._running and self._scheduler is not None:
            self._add_apscheduler_job(name)

        logger.info("SchedulerService: job '%s' registered (interval=%.1fs).", name, interval_s)
        return True

    def remove_job(self, name: str) -> bool:
        """Remove a named job. Returns True if it existed."""
        if name not in self._jobs:
            return False
        if self._scheduler is not None:
            try:
                self._scheduler.remove_job(f"sigrid_{name}")
            except Exception:
                pass
        del self._jobs[name]
        logger.info("SchedulerService: job '%s' removed.", name)
        return True

    def start(self) -> None:
        """Start the background scheduler and all registered jobs."""
        if self._running:
            return
        if self._scheduler is None:
            logger.warning("SchedulerService: APScheduler unavailable — background jobs disabled.")
            self._degraded = True
            return
        try:
            for name in self._jobs:
                self._add_apscheduler_job(name)
            self._scheduler.start()
            self._running = True
            logger.info("SchedulerService started (%d jobs).", len(self._jobs))
        except Exception as exc:
            logger.warning("SchedulerService.start() failed: %s", exc)
            self._degraded = True

    def stop(self) -> None:
        """Stop the background scheduler gracefully."""
        if not self._running or self._scheduler is None:
            return
        try:
            self._scheduler.shutdown(wait=False)
            self._running = False
            logger.info("SchedulerService stopped.")
        except Exception as exc:
            logger.warning("SchedulerService.stop() failed: %s", exc)

    def time_of_day(self) -> str:
        """Return the current named time-of-day segment."""
        return _current_time_of_day()

    def time_hint(self) -> str:
        """Return the mood/tone hint for the current time segment."""
        return _SEGMENT_HINTS.get(self.time_of_day(), "present and aware")

    # ── State bus integration ─────────────────────────────────────────────────

    def get_state(self) -> SchedulerState:
        """Build a typed SchedulerState snapshot."""
        tod = self.time_of_day()
        hint = _SEGMENT_HINTS.get(tod, "")
        names = list(self._jobs.keys())
        prompt_hint = f"[Time: {tod} — {hint}]"
        return SchedulerState(
            time_of_day=tod,
            time_hint=hint,
            active_job_count=len(names),
            job_names=names,
            running=self._running,
            prompt_hint=prompt_hint,
            timestamp=datetime.now(timezone.utc).isoformat(),
            degraded=self._degraded,
        )

    def publish(self, bus: StateBus) -> None:
        """Emit a ``scheduler_tick`` StateEvent to the state bus."""
        try:
            state = self.get_state()
            event = StateEvent(
                source_module="scheduler",
                event_type="scheduler_tick",
                payload=state.to_dict(),
            )
            bus.publish_state(event, nowait=True)
        except Exception as exc:
            logger.warning("SchedulerService.publish failed: %s", exc)

    # ── Internals ─────────────────────────────────────────────────────────────

    def _init_apscheduler(self) -> None:
        try:
            from apscheduler.schedulers.background import BackgroundScheduler
            self._scheduler = BackgroundScheduler(
                job_defaults={"coalesce": True, "max_instances": 1},
            )
            logger.info("SchedulerService: APScheduler ready.")
        except ImportError:
            logger.warning("SchedulerService: APScheduler not installed — background jobs disabled.")
            self._scheduler = None
            self._degraded = True

    def _add_apscheduler_job(self, name: str) -> None:
        if self._scheduler is None:
            return
        job_cfg = self._jobs[name]
        try:
            self._scheduler.add_job(
                func=job_cfg["func"],
                trigger="interval",
                seconds=job_cfg["interval_s"],
                id=job_cfg["job_id"],
                replace_existing=True,
            )
        except Exception as exc:
            logger.warning("SchedulerService: failed to add job '%s': %s", name, exc)

    # ── Factory ───────────────────────────────────────────────────────────────

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "SchedulerService":
        """Construct from a config dict.

        Reads keys under ``scheduler``:
          timezone  (str, default "local")
        """
        cfg: Dict[str, Any] = config.get("scheduler", {})
        return cls(timezone_str=str(cfg.get("timezone", "local")))


# ─── Singleton ────────────────────────────────────────────────────────────────

_SCHEDULER: Optional[SchedulerService] = None


def init_scheduler_from_config(config: Dict[str, Any]) -> SchedulerService:
    """Initialise the global SchedulerService from a config dict. Idempotent."""
    global _SCHEDULER
    if _SCHEDULER is None:
        _SCHEDULER = SchedulerService.from_config(config)
        logger.info("SchedulerService initialised (degraded=%s).", _SCHEDULER._degraded)
    return _SCHEDULER


def get_scheduler() -> SchedulerService:
    """Return the global SchedulerService.

    Raises RuntimeError if not yet initialised.
    """
    if _SCHEDULER is None:
        raise RuntimeError(
            "SchedulerService not initialised — call init_scheduler_from_config() first."
        )
    return _SCHEDULER
