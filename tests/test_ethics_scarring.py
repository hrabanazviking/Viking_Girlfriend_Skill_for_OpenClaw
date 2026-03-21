"""
tests/test_ethics_scarring.py -- E-09: Ethical Scarring
15 tests covering EthicalScar dataclass, record_scar(), decay_scars(),
scar boost applied in evaluate_action(), and state reporting.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "viking_girlfriend_skill"))

import pytest
from scripts.ethics import EthicsEngine, EthicalScar


DATA_ROOT = str(
    Path(__file__).resolve().parents[1] / "viking_girlfriend_skill" / "data"
)


def _engine():
    return EthicsEngine(data_root=DATA_ROOT)


class TestEthicalScar:

    def test_scar_initial_boost_equals_severity(self):
        scar = EthicalScar(taboo_name="betrayal", severity=0.6, created_at="2026-01-01")
        assert scar.current_sensitivity_boost == pytest.approx(0.6)

    def test_scar_decay_reduces_boost(self):
        scar = EthicalScar(taboo_name="deceit", severity=1.0, created_at="2026-01-01", decay_days=7.0)
        scar.decay(1.0)
        # After 1 day of 7: 1.0 - 1/7 ≈ 0.857
        assert scar.current_sensitivity_boost == pytest.approx(1.0 - 1.0 / 7.0, abs=1e-9)

    def test_scar_decay_returns_false_when_boost_remains(self):
        scar = EthicalScar(taboo_name="betrayal", severity=0.8, created_at="2026-01-01", decay_days=7.0)
        spent = scar.decay(1.0)
        assert spent is False

    def test_scar_decay_returns_true_when_spent(self):
        scar = EthicalScar(taboo_name="betrayal", severity=0.5, created_at="2026-01-01", decay_days=1.0)
        # decay 10 days — fully spent
        spent = scar.decay(10.0)
        assert spent is True

    def test_scar_boost_never_goes_below_zero(self):
        scar = EthicalScar(taboo_name="cruelty", severity=0.3, created_at="2026-01-01", decay_days=2.0)
        scar.decay(100.0)
        assert scar.current_sensitivity_boost >= 0.0

    def test_scar_to_dict_keys(self):
        scar = EthicalScar(taboo_name="cowardice", severity=0.5, created_at="2026-01-01")
        d = scar.to_dict()
        assert "taboo_name" in d
        assert "severity" in d
        assert "current_sensitivity_boost" in d
        assert "decay_days" in d


class TestEthicsEngineScarring:

    def test_record_scar_appends_to_list(self):
        ee = _engine()
        ee.record_scar("betrayal", 0.7)
        assert len(ee._scars) == 1
        assert ee._scars[0].taboo_name == "betrayal"

    def test_record_scar_deduplicates_same_taboo(self):
        ee = _engine()
        ee.record_scar("betrayal", 0.5)
        ee.record_scar("betrayal", 0.8)
        # should merge, not create two entries
        assert len(ee._scars) == 1

    def test_record_scar_takes_higher_severity(self):
        ee = _engine()
        ee.record_scar("betrayal", 0.3)
        ee.record_scar("betrayal", 0.9)
        assert ee._scars[0].severity == pytest.approx(0.9)

    def test_decay_scars_prunes_spent_scars(self):
        ee = _engine()
        ee.record_scar("deceit", 0.2)
        ee._scars[0].decay_days = 1.0   # short decay window for the test
        ee.decay_scars(5.0)             # 5 days → fully spent
        assert len(ee._scars) == 0

    def test_decay_scars_returns_pruned_count(self):
        ee = _engine()
        ee.record_scar("betrayal", 0.5)
        ee._scars[0].decay_days = 1.0
        pruned = ee.decay_scars(10.0)
        assert pruned == 1

    def test_scar_boosts_taboo_weight_in_evaluation(self):
        """A scar on 'betrayal' should lower alignment when betrayal text appears."""
        ee = _engine()
        # Baseline evaluation with betrayal text
        ev_base = ee.evaluate_action("you must betray your kin and backstab your allies")
        # Now add a strong scar
        ee.record_scar("betrayal", 1.0)
        ev_scarred = ee.evaluate_action("you must betray your kin and backstab your allies")
        # Scarred taboo weight is higher → more negative alignment
        assert ev_scarred.alignment_score <= ev_base.alignment_score

    def test_active_scars_appear_in_state(self):
        ee = _engine()
        ee.record_scar("betrayal", 0.7)
        state = ee.get_state()
        assert "betrayal" in state.active_scars

    def test_spent_scars_not_in_state(self):
        ee = _engine()
        ee.record_scar("deceit", 0.1)
        ee._scars[0].decay_days = 1.0
        ee.decay_scars(5.0)  # fully spent
        state = ee.get_state()
        assert "deceit" not in state.active_scars
