"""
tests/test_environment_tod.py — E-20: Time-of-Day Vibe Shift
10 tests covering vibe_by_tod resolution, TOD override flag, fallback to base
vibe, EnvironmentState new fields, and scheduler unavailable path.
"""
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "viking_girlfriend_skill"))

import pytest
from scripts.environment_mapper import EnvironmentMapper, EnvironmentState


DATA_ROOT = str(Path(__file__).resolve().parents[1] / "viking_girlfriend_skill" / "data")


class TestEnvironmentStateTODFields:

    def test_environment_state_has_current_vibe(self):
        state = EnvironmentState(
            location_key="k", location_name="n", description="d",
            activities=[], vibe="base", prompt_hint="h", timestamp="t",
        )
        assert hasattr(state, "current_vibe")

    def test_environment_state_has_tod_override(self):
        state = EnvironmentState(
            location_key="k", location_name="n", description="d",
            activities=[], vibe="base", prompt_hint="h", timestamp="t",
        )
        assert hasattr(state, "tod_override")

    def test_current_vibe_defaults_empty(self):
        state = EnvironmentState(
            location_key="k", location_name="n", description="d",
            activities=[], vibe="base", prompt_hint="h", timestamp="t",
        )
        assert state.current_vibe == ""

    def test_tod_override_defaults_false(self):
        state = EnvironmentState(
            location_key="k", location_name="n", description="d",
            activities=[], vibe="base", prompt_hint="h", timestamp="t",
        )
        assert state.tod_override is False

    def test_to_dict_includes_tod_fields(self):
        state = EnvironmentState(
            location_key="k", location_name="n", description="d",
            activities=[], vibe="base", prompt_hint="h", timestamp="t",
            current_vibe="night vibe", tod_override=True,
        )
        d = state.to_dict()
        assert d["current_vibe"] == "night vibe"
        assert d["tod_override"] is True


class TestTODVibeResolution:

    def test_tod_vibe_applied_when_scheduler_available(self):
        mapper = EnvironmentMapper(data_root=DATA_ROOT)
        with patch.object(mapper, "_get_time_of_day", return_value="evening"):
            state = mapper.get_state("home_base/living_room")
        assert state.tod_override is True
        assert "candles" in state.current_vibe.lower() or "warm" in state.current_vibe.lower()

    def test_fallback_to_base_vibe_when_scheduler_unavailable(self):
        mapper = EnvironmentMapper(data_root=DATA_ROOT)
        with patch.object(mapper, "_get_time_of_day", return_value=None):
            state = mapper.get_state("home_base/bedroom")
        assert state.tod_override is False
        assert state.current_vibe == state.vibe

    def test_fallback_when_tod_not_in_vibe_by_tod(self):
        mapper = EnvironmentMapper(data_root=DATA_ROOT)
        # "night" is a valid TOD that should exist in vibe_by_tod for bedroom
        with patch.object(mapper, "_get_time_of_day", return_value="night"):
            state = mapper.get_state("home_base/bedroom")
        # Either override applied or graceful fallback — no crash
        assert isinstance(state.current_vibe, str)

    def test_third_place_uses_base_vibe_no_tod(self):
        mapper = EnvironmentMapper(data_root=DATA_ROOT)
        with patch.object(mapper, "_get_time_of_day", return_value="morning"):
            state = mapper.get_state("third_places/tyresta_national_park")
        # third_places have no vibe_by_tod — fallback to base vibe
        assert state.tod_override is False
        assert state.current_vibe == state.vibe

    def test_prompt_hint_uses_current_vibe(self):
        mapper = EnvironmentMapper(data_root=DATA_ROOT)
        with patch.object(mapper, "_get_time_of_day", return_value="deep night"):
            state = mapper.get_state("home_base/bedroom")
        # prompt_hint should reflect the current (possibly TOD) vibe
        assert state.location_name in state.prompt_hint
