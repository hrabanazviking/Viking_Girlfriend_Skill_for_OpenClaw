"""
tests/test_environment_sensory.py — E-21: Sensory Hint Layer
8 tests covering get_sensory_hints(), stochastic selection bounds,
no-sensory fallback, and PromptSynthesizer._build_environment_block().
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "viking_girlfriend_skill"))

import pytest
from scripts.environment_mapper import EnvironmentMapper
from scripts.prompt_synthesizer import PromptSynthesizer


DATA_ROOT = str(Path(__file__).resolve().parents[1] / "viking_girlfriend_skill" / "data")


class TestGetSensoryHints:

    def test_returns_dict_for_known_room(self):
        mapper = EnvironmentMapper(data_root=DATA_ROOT)
        hints = mapper.get_sensory_hints("home_base/bedroom")
        assert isinstance(hints, dict)
        assert len(hints) >= 1

    def test_selects_at_most_two_channels(self):
        mapper = EnvironmentMapper(data_root=DATA_ROOT)
        for _ in range(20):
            hints = mapper.get_sensory_hints("home_base/living_room")
            assert len(hints) <= 2

    def test_selects_at_least_one_channel(self):
        mapper = EnvironmentMapper(data_root=DATA_ROOT)
        for _ in range(10):
            hints = mapper.get_sensory_hints("home_base/kitchen")
            assert len(hints) >= 1

    def test_channels_are_valid_sensory_keys(self):
        mapper = EnvironmentMapper(data_root=DATA_ROOT)
        valid_channels = {"smell", "sound", "texture"}
        hints = mapper.get_sensory_hints("home_base/balcony")
        assert all(k in valid_channels for k in hints)

    def test_unknown_location_returns_empty(self):
        mapper = EnvironmentMapper(data_root=DATA_ROOT)
        hints = mapper.get_sensory_hints("nowhere/void")
        assert hints == {}

    def test_third_place_has_sensory_data(self):
        mapper = EnvironmentMapper(data_root=DATA_ROOT)
        hints = mapper.get_sensory_hints("third_places/tyresta_national_park")
        assert len(hints) >= 1


class TestBuildEnvironmentBlock:

    def _synth(self, include_sensory=True):
        return PromptSynthesizer(data_root=DATA_ROOT, include_sensory=include_sensory)

    def test_block_includes_sensory_layer_header(self):
        synth = self._synth()
        block = synth._build_environment_block({"smell": "pine resin"})
        assert "[Sensory Layer]" in block

    def test_block_includes_channel_content(self):
        synth = self._synth()
        block = synth._build_environment_block({"sound": "wind through pines"})
        assert "wind through pines" in block

    def test_empty_when_include_sensory_false(self):
        synth = self._synth(include_sensory=False)
        block = synth._build_environment_block({"smell": "coffee"})
        assert block == ""

    def test_empty_when_no_hints(self):
        synth = self._synth()
        block = synth._build_environment_block({})
        assert block == ""

    def test_injected_into_build_messages(self):
        synth = self._synth()
        messages, _ = synth.build_messages(
            user_text="hello",
            sensory_hints={"smell": "beeswax candles"},
        )
        system = messages[0]["content"]
        assert "beeswax candles" in system
