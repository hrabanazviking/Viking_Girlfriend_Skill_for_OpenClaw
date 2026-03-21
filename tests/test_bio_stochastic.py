"""
tests/test_bio_stochastic.py -- E-11: BioEngine Stochastic Daily Variance
8 tests covering _apply_jitter(), determinism, seeding, clamping, and
variance_applied field surfacing in BioState.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "viking_girlfriend_skill"))

import pytest
from datetime import date
from scripts.bio_engine import BioEngine

# Real dates so the engine is NOT in degraded mode
_BIRTH = date(2004, 11, 3)
_CYCLE_START = date(2026, 3, 8)


def _engine(chaos: float = 0.10, seed: int = 42) -> BioEngine:
    return BioEngine(
        birth_date=_BIRTH,
        cycle_start_date=_CYCLE_START,
        chaos_factor=chaos,
        session_seed=seed,
    )


class TestBioStochastic:

    def test_zero_chaos_produces_zero_variance(self):
        eng = _engine(chaos=0.0)
        state = eng.get_state()
        assert state.variance_applied == pytest.approx(0.0)

    def test_nonzero_chaos_produces_nonzero_variance(self):
        eng = _engine(chaos=0.10)
        state = eng.get_state()
        # variance_applied should be > 0 when chaos is on
        assert state.variance_applied > 0.0

    def test_same_cycle_day_same_seed_deterministic(self):
        """Two engines with identical seed should produce identical variance."""
        eng1 = _engine(chaos=0.10, seed=7)
        eng2 = _engine(chaos=0.10, seed=7)
        s1 = eng1.get_state()
        s2 = eng2.get_state()
        assert s1.variance_applied == pytest.approx(s2.variance_applied)

    def test_different_seeds_produce_different_variance(self):
        """Different session seeds should produce different variance (with high probability)."""
        eng1 = _engine(chaos=0.10, seed=1)
        eng2 = _engine(chaos=0.10, seed=999)
        s1 = eng1.get_state()
        s2 = eng2.get_state()
        # With chaos=0.10, two different seeds almost certainly differ
        assert s1.variance_applied != pytest.approx(s2.variance_applied)

    def test_multipliers_clamped_non_negative(self):
        """Even with large chaos, no multiplier should go below 0."""
        eng = _engine(chaos=2.0, seed=1)  # extreme chaos
        state = eng.get_state()
        for mult in state.emotion_multipliers.values():
            assert mult >= 0.0

    def test_multipliers_clamped_at_two(self):
        """Even with large chaos, no multiplier should exceed 2.0."""
        eng = _engine(chaos=2.0, seed=1)  # extreme chaos
        state = eng.get_state()
        for mult in state.emotion_multipliers.values():
            assert mult <= 2.0

    def test_variance_applied_in_state_dict(self):
        eng = _engine(chaos=0.10)
        d = eng.get_state().to_dict()
        assert "variance_applied" in d

    def test_variance_applied_non_negative(self):
        eng = _engine(chaos=0.10)
        state = eng.get_state()
        assert state.variance_applied >= 0.0
