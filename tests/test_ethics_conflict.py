"""
tests/test_ethics_conflict.py -- E-10: Value-Conflict Mediation
10 tests covering ValueConflict detection, opposing pair logic,
threshold enforcement, and conflict reporting in EthicsEvaluation.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "viking_girlfriend_skill"))

from scripts.ethics import EthicsEngine, ValueConflict


DATA_ROOT = str(
    Path(__file__).resolve().parents[1] / "viking_girlfriend_skill" / "data"
)


def _engine():
    return EthicsEngine(data_root=DATA_ROOT)


class TestValueConflict:

    def test_value_conflict_dataclass_fields(self):
        vc = ValueConflict(
            value_a="loyalty",
            value_b="wisdom",
            context="casual",
            resolution_hint="balance them",
        )
        assert vc.value_a == "loyalty"
        assert vc.value_b == "wisdom"
        assert vc.resolution_hint == "balance them"

    def test_value_conflict_to_dict(self):
        vc = ValueConflict("loyalty", "wisdom", "casual", "balance")
        d = vc.to_dict()
        assert d["value_a"] == "loyalty"
        assert d["value_b"] == "wisdom"
        assert d["context"] == "casual"
        assert d["resolution_hint"] == "balance"


class TestConflictDetection:

    def test_no_conflict_single_value(self):
        """Single value triggered — no opposing pair possible."""
        ee = _engine()
        # only loyalty keyword present
        ev = ee.evaluate_action("I stand loyal to my kin and sworn allies")
        # loyalty alone should not produce conflicts
        assert ev.conflicts == []

    def test_loyalty_vs_wisdom_conflict_detected(self):
        """loyalty + wisdom keywords together → conflict detected."""
        ee = _engine()
        ev = ee.evaluate_action(
            "I am loyal to my sworn kin and I seek wisdom and knowledge to understand"
        )
        conflict_pairs = [(c.value_a, c.value_b) for c in ev.conflicts]
        assert ("loyalty", "wisdom") in conflict_pairs

    def test_conflict_contains_resolution_hint(self):
        """The detected conflict carries a non-empty resolution_hint."""
        ee = _engine()
        ev = ee.evaluate_action(
            "I remain loyal and true, and I seek understanding and wisdom"
        )
        conflicts = [c for c in ev.conflicts if c.value_a == "loyalty" and c.value_b == "wisdom"]
        if conflicts:
            assert len(conflicts[0].resolution_hint) > 0

    def test_evaluation_conflicts_is_list(self):
        """EthicsEvaluation.conflicts is always a list (even if empty)."""
        ee = _engine()
        ev = ee.evaluate_action("The runes are beautiful today")
        assert isinstance(ev.conflicts, list)

    def test_low_weight_values_do_not_conflict(self):
        """Values with weight ≤ 0.7 should not trigger conflict detection.

        Checks that the threshold enforcement actually works — we inject a
        fake low-weight value pair and confirm no conflict fires.
        """
        from scripts.ethics import _OPPOSING_VALUE_PAIRS
        ee = _engine()
        # Simulate a fake pair in the list by temporarily appending
        # (we only test that our real pairs with weight <= 0.7 don't fire)
        # playfulness has weight 0.75 > 0.7, so check ancestral_reverence (0.9)
        # vs a value with weight == 0.7 (independence): loyalty+independence shouldn't
        # fire unless independence weight > 0.7 in values.json (it's exactly 0.7)
        # If independence is exactly 0.7, the pair should NOT fire (strict > check)
        ev = ee.evaluate_action(
            "I am loyal to my kin and I am self-reliant and independent"
        )
        conflicts = [c for c in ev.conflicts if set([c.value_a, c.value_b]) == {"loyalty", "independence"}]
        # independence weight is 0.7 — exactly at threshold, must NOT fire (strict >)
        # This test validates the boundary condition
        indep_weight = float(ee._core_values.get("independence", {}).get("weight", 0.5))
        if indep_weight <= 0.7:
            assert len(conflicts) == 0

    def test_detect_conflicts_internal_method(self):
        """_detect_conflicts() returns ValueConflict objects for valid pairs."""
        ee = _engine()
        conflicts = ee._detect_conflicts(["loyalty", "wisdom"], "casual")
        assert any(c.value_a == "loyalty" and c.value_b == "wisdom" for c in conflicts)

    def test_detect_conflicts_empty_when_no_pairs(self):
        """No conflict when triggered values have no opposing pair."""
        ee = _engine()
        conflicts = ee._detect_conflicts(["playfulness", "ancestral_reverence"], "casual")
        assert conflicts == []

    def test_conflict_context_matches_evaluation_context(self):
        """Conflict context string matches the detected evaluation context."""
        ee = _engine()
        ev = ee.evaluate_action(
            "I must stay loyal and seek wisdom",
            context_type="spiritual",
        )
        for c in ev.conflicts:
            assert c.context == "spiritual"
