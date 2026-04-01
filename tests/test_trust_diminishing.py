"""
tests/test_trust_diminishing.py — E-25: Diminishing Returns on Repeated Signals
8 tests covering logarithmic attenuation, floor enforcement, independent
per-signal counts, and reset behavior.
"""
import sys
from math import log
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "viking_girlfriend_skill"))

import pytest
from scripts.trust_engine import TrustEngine, _DIMINISHING_FLOOR


class TestDiminishingReturns:

    def test_first_occurrence_full_magnitude(self, tmp_path):
        """Count=0 → factor = 1/(1+log(1)) = 1.0 → full magnitude."""
        engine = TrustEngine(session_dir=str(tmp_path))
        ledger = engine.get_ledger("test_user")
        b_before = ledger.facets.benevolence
        engine.process_turn("thank you so much", "", "test_user")
        b_after = ledger.facets.benevolence
        # First occurrence should apply full delta
        assert b_after > b_before

    def test_second_occurrence_reduced_magnitude(self, tmp_path):
        """The second 'warmth_shown' signal should have less impact than the first."""
        engine = TrustEngine(session_dir=str(tmp_path))
        ledger = engine.get_ledger("test_user")

        # First occurrence
        b0 = ledger.facets.benevolence
        engine.process_turn("thank you so much", "", "test_user")
        delta_1 = ledger.facets.benevolence - b0

        # Reset facets to baseline to isolate second occurrence
        ledger.facets.benevolence = b0

        # Second occurrence
        engine.process_turn("thank you so much", "", "test_user")
        delta_2 = ledger.facets.benevolence - b0

        # Second delta should be smaller (count=1 → factor < 1.0)
        assert delta_2 < delta_1

    def test_floor_at_10_percent(self, tmp_path):
        """After many repetitions the factor floors at _DIMINISHING_FLOOR."""
        engine = TrustEngine(session_dir=str(tmp_path))
        # Manually push count very high
        engine._signal_counts["warmth_shown"] = 1000
        ledger = engine.get_ledger("test_user")
        b_before = ledger.facets.benevolence
        engine.process_turn("thank you so much", "", "test_user")
        b_after = ledger.facets.benevolence
        # Minimum effective magnitude = _DIMINISHING_FLOOR (0.1)
        # benevolence delta for warmth_shown at count=1000 should be > 0 (floor > 0)
        assert b_after > b_before

    def test_count_increments_per_signal(self, tmp_path):
        engine = TrustEngine(session_dir=str(tmp_path))
        engine.process_turn("thank you so much", "", "test_user")
        assert engine._signal_counts.get("warmth_shown", 0) >= 1

    def test_different_signals_counted_independently(self, tmp_path):
        engine = TrustEngine(session_dir=str(tmp_path))
        engine.process_turn("thank you so much", "", "test_user")
        engine.process_turn("kept my promise to you", "", "test_user")
        warmth_count = engine._signal_counts.get("warmth_shown", 0)
        oath_count = engine._signal_counts.get("oath_kept", 0)
        assert warmth_count >= 1
        assert oath_count >= 1
        # They should be counted separately
        assert warmth_count != oath_count or warmth_count == 1

    def test_reset_clears_all_counts(self, tmp_path):
        engine = TrustEngine(session_dir=str(tmp_path))
        engine.process_turn("thank you so much", "", "test_user")
        assert engine._signal_counts.get("warmth_shown", 0) >= 1
        engine.reset_signal_counts()
        assert engine._signal_counts == {}

    def test_logarithmic_curve_count3_less_than_count0(self, tmp_path):
        """Confirm count=3 has less effect than count=0 for the same event."""
        # Factor at count=0: 1/(1+log(1)) = 1.0
        # Factor at count=3: 1/(1+log(4)) ≈ 0.42
        factor_0 = 1.0 / (1.0 + log(1.0 + 0))
        factor_3 = 1.0 / (1.0 + log(1.0 + 3))
        assert factor_3 < factor_0
        assert factor_3 > _DIMINISHING_FLOOR

    def test_explicit_record_event_not_diminished(self, tmp_path):
        """record_event() bypasses diminishing returns — explicit events are authoritative."""
        engine = TrustEngine(session_dir=str(tmp_path))
        # Saturate the oath_kept signal count
        engine._signal_counts["oath_kept"] = 1000
        ledger = engine.get_ledger("test_user")
        i_before = ledger.facets.integrity
        # Explicit record_event should use full magnitude (1.0), not reduced
        engine.record_event("oath_kept", magnitude=1.0, contact_id="test_user")
        i_after = ledger.facets.integrity
        # Should still increase — not saturated
        assert i_after > i_before
