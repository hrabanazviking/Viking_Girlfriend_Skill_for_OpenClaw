"""
tests/test_scheduler_heartbeat.py -- E-13: Heartbeat Sentinel
8 tests covering heartbeat file creation, get_heartbeat_age_s(),
SchedulerState.heartbeat_age_s, and _heartbeat_tick().
"""
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "viking_girlfriend_skill"))

import pytest
from scripts.scheduler import SchedulerService, get_heartbeat_age_s

class TestHeartbeatFile:

    def test_heartbeat_tick_creates_file(self, tmp_path):
        svc = SchedulerService(session_dir=str(tmp_path))
        svc._heartbeat_tick()
        hb_path = tmp_path / "heartbeat.json"
        assert hb_path.exists()

    def test_heartbeat_file_contains_ts_and_pid(self, tmp_path):
        svc = SchedulerService(session_dir=str(tmp_path))
        svc._heartbeat_tick()
        payload = json.loads((tmp_path / "heartbeat.json").read_text())
        assert "ts" in payload
        assert "pid" in payload

    def test_heartbeat_ts_is_iso_format(self, tmp_path):
        svc = SchedulerService(session_dir=str(tmp_path))
        svc._heartbeat_tick()
        payload = json.loads((tmp_path / "heartbeat.json").read_text())
        # Should parse without error
        datetime.fromisoformat(payload["ts"])

    def test_heartbeat_pid_is_integer(self, tmp_path):
        svc = SchedulerService(session_dir=str(tmp_path))
        svc._heartbeat_tick()
        payload = json.loads((tmp_path / "heartbeat.json").read_text())
        assert isinstance(payload["pid"], int)


class TestGetHeartbeatAge:

    def test_age_returns_none_when_no_file(self, tmp_path):
        age = get_heartbeat_age_s(str(tmp_path))
        assert age is None

    def test_age_returns_float_after_tick(self, tmp_path):
        svc = SchedulerService(session_dir=str(tmp_path))
        svc._heartbeat_tick()
        age = get_heartbeat_age_s(str(tmp_path))
        assert isinstance(age, float)
        assert age >= 0.0

    def test_age_is_small_immediately_after_tick(self, tmp_path):
        svc = SchedulerService(session_dir=str(tmp_path))
        svc._heartbeat_tick()
        age = get_heartbeat_age_s(str(tmp_path))
        assert age < 5.0  # written moments ago

    def test_heartbeat_age_in_scheduler_state(self, tmp_path):
        svc = SchedulerService(session_dir=str(tmp_path))
        svc._heartbeat_tick()
        state = svc.get_state()
        assert state.heartbeat_age_s is not None
        assert isinstance(state.heartbeat_age_s, float)
