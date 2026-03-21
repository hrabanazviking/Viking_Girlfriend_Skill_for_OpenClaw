"""
tests/test_metabolism_hamingja.py -- E-08: Honor-driven energy reserve
5 tests covering the hamingja vitality boost in MetabolismAdapter.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "viking_girlfriend_skill"))

from scripts.metabolism import MetabolismAdapter


class TestHamingjaBoost:

    def _make_adapter(self):
        return MetabolismAdapter()

    def test_no_hamingja_boost_is_zero(self):
        """Without hamingja param the boost field is 0.0."""
        adapter = self._make_adapter()
        state = adapter.get_state(force=True)
        assert state.hamingja_boost_applied == 0.0

    def test_neutral_hamingja_no_boost(self):
        """hamingja=0.5 produces zero boost (midpoint of the range)."""
        adapter = self._make_adapter()
        state = adapter.get_state(force=True, hamingja=0.5)
        assert abs(state.hamingja_boost_applied) < 1e-9

    def test_high_hamingja_positive_boost(self):
        """hamingja=1.0 → boost = (1.0-0.5)*0.15 = +0.075."""
        adapter = self._make_adapter()
        state = adapter.get_state(force=True, hamingja=1.0)
        assert abs(state.hamingja_boost_applied - 0.075) < 1e-9

    def test_low_hamingja_negative_boost(self):
        """hamingja=0.0 → boost = (0.0-0.5)*0.15 = -0.075."""
        adapter = self._make_adapter()
        state = adapter.get_state(force=True, hamingja=0.0)
        assert abs(state.hamingja_boost_applied - (-0.075)) < 1e-9

    def test_vitality_capped_at_one(self):
        """High hamingja cannot push vitality above 1.0."""
        adapter = self._make_adapter()
        # Force vitality baseline to something high + large hamingja
        state = adapter.get_state(force=True, hamingja=1.0)
        assert state.vitality_score <= 1.0
