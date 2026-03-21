"""
tests/test_memory_consolidation.py — E-19: Nightly Memory Consolidation
15 tests covering MemoryConsolidator.run(), raw fallback, buffer clearing,
StateBus event, SchedulerService.register_cron_job(), and register_consolidation_job().
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "viking_girlfriend_skill"))

import pytest
from scripts.memory_store import (
    ConversationBuffer,
    EpisodicStore,
    MemoryConsolidator,
    MemoryStore,
)
from scripts.scheduler import SchedulerService


# ─── MemoryConsolidator helpers ───────────────────────────────────────────────

def _make_consolidator(tmp_path, medium_entries=None):
    buf = ConversationBuffer()
    episodic = EpisodicStore(data_root=str(tmp_path))
    if medium_entries:
        buf._medium_term.extend(medium_entries)
    return MemoryConsolidator(buffer=buf, episodic=episodic, session_id="test_session")


# ─── MemoryConsolidator.run() ────────────────────────────────────────────────

class TestMemoryConsolidatorRun:

    def test_run_returns_true_on_empty_buffer(self, tmp_path):
        consolidator = _make_consolidator(tmp_path)
        assert consolidator.run() is True

    def test_run_clears_medium_term_buffer(self, tmp_path):
        entries = ["T1: hello world", "T2: discuss runes", "T3: farewell"]
        consolidator = _make_consolidator(tmp_path, medium_entries=entries)
        # Patch _summarize to avoid model calls
        consolidator._summarize = lambda e: "Sigrid and Volmarr discussed runes."
        consolidator.run()
        assert consolidator._buffer._medium_term == []

    def test_run_stores_episodic_entry(self, tmp_path):
        entries = ["T1: discussed Odin lore", "T2: brewed mead"]
        consolidator = _make_consolidator(tmp_path, medium_entries=entries)
        consolidator._summarize = lambda e: "Discussed Odin and mead."
        before_count = consolidator._episodic.count
        consolidator.run()
        assert consolidator._episodic.count == before_count + 1

    def test_run_stores_entry_with_consolidation_tag(self, tmp_path):
        entries = ["T1: rune work"]
        consolidator = _make_consolidator(tmp_path, medium_entries=entries)
        consolidator._summarize = lambda e: "Rune work done."
        consolidator.run()
        recent = consolidator._episodic.get_recent(n=1)
        assert "consolidation" in recent[0].tags

    def test_run_entry_memory_type_is_conversation(self, tmp_path):
        entries = ["T1: general chat"]
        consolidator = _make_consolidator(tmp_path, medium_entries=entries)
        consolidator._summarize = lambda e: "General chat."
        consolidator.run()
        recent = consolidator._episodic.get_recent(n=1)
        assert recent[0].memory_type == "conversation"

    def test_run_empty_buffer_adds_no_entry(self, tmp_path):
        consolidator = _make_consolidator(tmp_path)
        before_count = consolidator._episodic.count
        consolidator.run()
        assert consolidator._episodic.count == before_count


# ─── Graceful fallback (model unavailable) ───────────────────────────────────

class TestConsolidationFallback:

    def test_raw_fallback_when_summarize_returns_empty(self, tmp_path):
        entries = ["T1: raw entry one", "T2: raw entry two"]
        consolidator = _make_consolidator(tmp_path, medium_entries=entries)
        consolidator._summarize = lambda e: ""  # simulate model failure
        consolidator.run()
        recent = consolidator._episodic.get_recent(n=1)
        assert "raw" in recent[0].tags

    def test_fallback_still_clears_buffer(self, tmp_path):
        entries = ["T1: entry"]
        consolidator = _make_consolidator(tmp_path, medium_entries=entries)
        consolidator._summarize = lambda e: ""
        consolidator.run()
        assert consolidator._buffer._medium_term == []

    def test_fallback_still_returns_true(self, tmp_path):
        entries = ["T1: entry"]
        consolidator = _make_consolidator(tmp_path, medium_entries=entries)
        consolidator._summarize = lambda e: ""
        assert consolidator.run() is True


# ─── StateBus event ───────────────────────────────────────────────────────────

class TestConsolidationBusEvent:

    def test_run_publishes_event_when_bus_provided(self, tmp_path):
        entries = ["T1: something"]
        consolidator = _make_consolidator(tmp_path, medium_entries=entries)
        consolidator._summarize = lambda e: "Summary."
        mock_bus = MagicMock()
        mock_bus.publish_state = MagicMock(return_value=None)
        consolidator.run(bus=mock_bus)
        mock_bus.publish_state.assert_called_once()

    def test_run_does_not_crash_when_bus_publish_fails(self, tmp_path):
        entries = ["T1: something"]
        consolidator = _make_consolidator(tmp_path, medium_entries=entries)
        consolidator._summarize = lambda e: "Summary."
        mock_bus = MagicMock()
        mock_bus.publish_state.side_effect = RuntimeError("bus failure")
        # Should not raise
        consolidator.run(bus=mock_bus)


# ─── SchedulerService cron job (E-19) ────────────────────────────────────────

class TestSchedulerCronJob:

    def test_register_cron_job_returns_true(self):
        svc = SchedulerService()
        result = svc.register_cron_job("test_cron", lambda: None, hour=3, minute=30)
        assert result is True

    def test_register_cron_job_stored_in_jobs(self):
        svc = SchedulerService()
        svc.register_cron_job("daily_job", lambda: None, hour=6, minute=0)
        assert "daily_job" in svc._jobs
        assert svc._jobs["daily_job"]["trigger"] == "cron"
        assert svc._jobs["daily_job"]["hour"] == 6
        assert svc._jobs["daily_job"]["minute"] == 0

    def test_register_consolidation_job(self, tmp_path):
        svc = SchedulerService()
        consolidator = _make_consolidator(tmp_path)
        mock_bus = MagicMock()
        result = svc.register_consolidation_job(consolidator, mock_bus)
        assert result is True
        assert "memory_consolidation" in svc._jobs
        assert svc._jobs["memory_consolidation"]["hour"] == 3
        assert svc._jobs["memory_consolidation"]["minute"] == 30

    def test_register_cron_job_replace_existing_false(self):
        svc = SchedulerService()
        svc.register_cron_job("once", lambda: None, hour=1, minute=0)
        result = svc.register_cron_job("once", lambda: None, hour=2, minute=0,
                                       replace_existing=False)
        assert result is False
        # Original hour preserved
        assert svc._jobs["once"]["hour"] == 1
