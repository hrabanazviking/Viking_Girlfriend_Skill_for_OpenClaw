"""
tests/test_wyrd_vitality_modulation.py -- E-07: Vitality-driven emotional inertia
6 tests covering the metabolism_vitality parameter in WyrdMatrix.tick().
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "viking_girlfriend_skill"))

from scripts.wyrd_matrix import WyrdMatrix


class TestVitalityModulation:

    def _make_matrix(self):
        return WyrdMatrix()

    def test_tick_no_vitality_flag_false(self):
        """tick() without metabolism_vitality leaves vitality_modulated_decay False."""
        wm = self._make_matrix()
        state = wm.tick()
        assert state.vitality_modulated_decay is False

    def test_tick_with_vitality_flag_true(self):
        """tick(metabolism_vitality=0.5) sets vitality_modulated_decay True."""
        wm = self._make_matrix()
        state = wm.tick(metabolism_vitality=0.5)
        assert state.vitality_modulated_decay is True

    def test_full_vitality_decay_unchanged(self):
        """At vitality=1.0 the effective decay rate equals the base rate."""
        wm = self._make_matrix()
        base_decay = wm.profile.decay_rate
        wm.tick(metabolism_vitality=1.0)
        # effective_decay = base / (1 + (1-1)*0.5) = base / 1.0
        assert abs(wm.soul.hugr.decay_rate - base_decay) < 1e-9

    def test_zero_vitality_slows_decay_by_50_percent(self):
        """At vitality=0.0 the Hugr decay rate should be ≈ base / 1.5."""
        wm = self._make_matrix()
        base_decay = wm.profile.decay_rate
        wm.tick(metabolism_vitality=0.0)
        expected = base_decay / 1.5
        assert abs(wm.soul.hugr.decay_rate - expected) < 1e-9

    def test_midpoint_vitality_modulates_proportionally(self):
        """At vitality=0.5 the decay divisor is 1.25 (halfway between 1.0 and 1.5)."""
        wm = self._make_matrix()
        base_decay = wm.profile.decay_rate
        wm.tick(metabolism_vitality=0.5)
        expected = base_decay / 1.25
        assert abs(wm.soul.hugr.decay_rate - expected) < 1e-9

    def test_flag_resets_when_vitality_omitted_next_turn(self):
        """After a vitality-modulated tick, a plain tick() clears the flag."""
        wm = self._make_matrix()
        wm.tick(metabolism_vitality=0.3)
        assert wm.tick().vitality_modulated_decay is False

    def test_decay_rate_restores_to_base_when_vitality_omitted(self):
        """Plain tick() after a modulated tick restores hugr.decay_rate to base."""
        wm = self._make_matrix()
        base_decay = wm.profile.decay_rate
        wm.tick(metabolism_vitality=0.2)
        wm.tick()  # no vitality
        assert abs(wm.soul.hugr.decay_rate - base_decay) < 1e-9
