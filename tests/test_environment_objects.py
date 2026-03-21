"""
tests/test_environment_objects.py — E-22: Object State Tracking
12 tests covering ObjectState dataclass, set_object_state(), get_active_object_states(),
auto-expiry, persistence, and get_state() integration.
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "viking_girlfriend_skill"))

import pytest
from scripts.environment_mapper import EnvironmentMapper, ObjectState


DATA_ROOT = str(Path(__file__).resolve().parents[1] / "viking_girlfriend_skill" / "data")


class TestObjectStateDataclass:

    def test_objectstate_fields(self):
        obj = ObjectState(
            object_id="hearth", room_id="living_room",
            state="lit", changed_at="ts", expires_at=""
        )
        assert obj.object_id == "hearth"
        assert obj.state == "lit"

    def test_objectstate_not_expired_when_no_expiry(self):
        obj = ObjectState(
            object_id="candle", room_id="bedroom",
            state="burning", changed_at="ts", expires_at=""
        )
        assert obj.is_expired() is False

    def test_objectstate_expired_in_past(self):
        obj = ObjectState(
            object_id="tea", room_id="kitchen",
            state="warm", changed_at="ts",
            expires_at="2000-01-01T00:00:00+00:00"
        )
        assert obj.is_expired() is True

    def test_objectstate_to_prompt_line(self):
        obj = ObjectState(
            object_id="hearth", room_id="living_room",
            state="lit", changed_at="ts", expires_at=""
        )
        line = obj.to_prompt_line()
        assert "hearth" in line
        assert "lit" in line

    def test_objectstate_underscore_replaced_in_prompt_line(self):
        obj = ObjectState(
            object_id="oil_lamp", room_id="bedroom",
            state="burning", changed_at="ts", expires_at=""
        )
        line = obj.to_prompt_line()
        assert "oil lamp" in line


class TestSetAndGetObjectState:

    def test_set_object_state_creates_state(self, tmp_path):
        mapper = EnvironmentMapper(data_root=DATA_ROOT)
        mapper._object_states_file = tmp_path / "object_states.json"
        mapper.set_object_state("living_room", "hearth", "lit", 60)
        active = mapper.get_active_object_states("living_room")
        assert len(active) == 1
        assert active[0].state == "lit"

    def test_set_object_state_overwrites_existing(self, tmp_path):
        mapper = EnvironmentMapper(data_root=DATA_ROOT)
        mapper._object_states_file = tmp_path / "object_states.json"
        mapper.set_object_state("living_room", "hearth", "lit", 60)
        mapper.set_object_state("living_room", "hearth", "embers", 30)
        active = mapper.get_active_object_states("living_room")
        assert len(active) == 1
        assert active[0].state == "embers"

    def test_no_duration_means_no_expiry(self, tmp_path):
        mapper = EnvironmentMapper(data_root=DATA_ROOT)
        mapper._object_states_file = tmp_path / "object_states.json"
        mapper.set_object_state("bedroom", "candle", "burning")
        active = mapper.get_active_object_states("bedroom")
        assert len(active) == 1
        assert active[0].expires_at == ""

    def test_get_active_filters_by_room(self, tmp_path):
        mapper = EnvironmentMapper(data_root=DATA_ROOT)
        mapper._object_states_file = tmp_path / "object_states.json"
        mapper.set_object_state("living_room", "hearth", "lit", 60)
        mapper.set_object_state("kitchen", "kettle", "hot", 30)
        living = mapper.get_active_object_states("living_room")
        kitchen = mapper.get_active_object_states("kitchen")
        assert len(living) == 1
        assert len(kitchen) == 1
        assert living[0].object_id == "hearth"

    def test_expired_state_not_returned(self, tmp_path):
        mapper = EnvironmentMapper(data_root=DATA_ROOT)
        mapper._object_states_file = tmp_path / "object_states.json"
        # Set a state that expires in the past by directly inserting
        from datetime import datetime, timezone, timedelta
        obj = ObjectState(
            object_id="tea", room_id="kitchen",
            state="warm", changed_at="ts",
            expires_at="2000-01-01T00:00:00+00:00",
        )
        mapper._object_states["kitchen:tea"] = obj
        active = mapper.get_active_object_states("kitchen")
        assert len(active) == 0


class TestObjectStatePersistence:

    def test_object_states_persisted_to_file(self, tmp_path):
        mapper = EnvironmentMapper(data_root=DATA_ROOT)
        mapper._object_states_file = tmp_path / "session" / "object_states.json"
        mapper._object_states_file.parent.mkdir(parents=True, exist_ok=True)
        mapper.set_object_state("living_room", "hearth", "lit", 60)
        assert mapper._object_states_file.exists()

    def test_object_states_loaded_on_init(self, tmp_path):
        # Save a state via one mapper instance
        mapper1 = EnvironmentMapper(data_root=DATA_ROOT)
        mapper1._object_states_file = tmp_path / "session" / "object_states.json"
        mapper1._object_states_file.parent.mkdir(parents=True, exist_ok=True)
        mapper1.set_object_state("bedroom", "candle", "burning")
        # Create new instance pointing at same file
        mapper2 = EnvironmentMapper(data_root=DATA_ROOT)
        mapper2._object_states_file = tmp_path / "session" / "object_states.json"
        mapper2._object_states = {}
        mapper2._load_object_states()
        assert len(mapper2._object_states) == 1


class TestGetStateObjectIntegration:

    def test_get_state_includes_active_object_states(self, tmp_path):
        mapper = EnvironmentMapper(data_root=DATA_ROOT)
        mapper._object_states_file = tmp_path / "object_states.json"
        mapper.set_location("home_base/living_room")
        mapper.set_object_state("living_room", "hearth", "lit", 60)
        state = mapper.get_state()
        assert len(state.object_states) == 1
        assert "hearth" in state.object_states[0]
        assert "lit" in state.object_states[0]
