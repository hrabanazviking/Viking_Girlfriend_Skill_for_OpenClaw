"""
tests/test_trust_facets.py — E-23: TrustFacets Multidimensional Trust
15 tests covering TrustFacets dataclass, trust_score computed property,
facet-mapped events, TrustState inclusion, and initial state.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "viking_girlfriend_skill"))

import pytest
from scripts.trust_engine import (
    TrustEngine,
    TrustFacets,
    TrustLedger,
    _FACET_WEIGHTS,
)


DATA_ROOT = str(Path(__file__).resolve().parents[1] / "viking_girlfriend_skill" / "data")


# ── TrustFacets dataclass ─────────────────────────────────────────────────────

class TestTrustFacetsDataclass:

    def test_has_competence_field(self):
        f = TrustFacets()
        assert hasattr(f, "competence")

    def test_has_benevolence_field(self):
        f = TrustFacets()
        assert hasattr(f, "benevolence")

    def test_has_integrity_field(self):
        f = TrustFacets()
        assert hasattr(f, "integrity")

    def test_defaults_are_0_5(self):
        f = TrustFacets()
        assert f.competence == 0.5
        assert f.benevolence == 0.5
        assert f.integrity == 0.5

    def test_to_dict_returns_rounded(self):
        f = TrustFacets(competence=0.333333, benevolence=0.666667, integrity=0.5)
        d = f.to_dict()
        assert d["competence"] == round(0.333333, 3)
        assert d["benevolence"] == round(0.666667, 3)
        assert d["integrity"] == 0.5

    def test_dominant_returns_highest(self):
        f = TrustFacets(competence=0.9, benevolence=0.5, integrity=0.4)
        assert f.dominant() == "competence"

    def test_dominant_benevolence(self):
        f = TrustFacets(competence=0.3, benevolence=0.8, integrity=0.3)
        assert f.dominant() == "benevolence"


# ── trust_score computed property ─────────────────────────────────────────────

class TestTrustScoreProperty:

    def test_default_facets_give_0_5_score(self):
        ledger = TrustLedger(contact_id="test")
        cw, bw, iw = _FACET_WEIGHTS
        expected = 0.5 * cw + 0.5 * bw + 0.5 * iw
        assert abs(ledger.trust_score - expected) < 1e-9

    def test_weighted_average_computed_correctly(self):
        ledger = TrustLedger(
            contact_id="test",
            facets=TrustFacets(competence=0.6, benevolence=0.8, integrity=0.4),
        )
        cw, bw, iw = _FACET_WEIGHTS
        expected = 0.6 * cw + 0.8 * bw + 0.4 * iw
        assert abs(ledger.trust_score - expected) < 1e-9

    def test_trust_score_clamped_to_1(self):
        ledger = TrustLedger(
            contact_id="test",
            facets=TrustFacets(competence=1.0, benevolence=1.0, integrity=1.0),
        )
        assert ledger.trust_score <= 1.0

    def test_trust_score_clamped_to_0(self):
        ledger = TrustLedger(
            contact_id="test",
            facets=TrustFacets(competence=0.0, benevolence=0.0, integrity=0.0),
        )
        assert ledger.trust_score >= 0.0


# ── Event impact on facets ─────────────────────────────────────────────────────

class TestFacetEventMapping:

    def test_warmth_shown_raises_benevolence(self, tmp_path):
        engine = TrustEngine(session_dir=str(tmp_path))
        ledger = engine.get_ledger("test")
        b_before = ledger.facets.benevolence
        ledger.apply_event("warmth_shown")
        assert ledger.facets.benevolence > b_before

    def test_oath_kept_raises_integrity(self, tmp_path):
        engine = TrustEngine(session_dir=str(tmp_path))
        ledger = engine.get_ledger("test")
        i_before = ledger.facets.integrity
        ledger.apply_event("oath_kept")
        assert ledger.facets.integrity > i_before

    def test_competence_shown_raises_competence(self, tmp_path):
        engine = TrustEngine(session_dir=str(tmp_path))
        ledger = engine.get_ledger("test")
        c_before = ledger.facets.competence
        ledger.apply_event("competence_shown")
        assert ledger.facets.competence > c_before

    def test_boundary_violated_lowers_integrity(self, tmp_path):
        engine = TrustEngine(session_dir=str(tmp_path))
        ledger = engine.get_ledger("test")
        i_before = ledger.facets.integrity
        ledger.apply_event("boundary_violated")
        assert ledger.facets.integrity < i_before


# ── TrustState includes facets ─────────────────────────────────────────────────

class TestTrustStateFacets:

    def test_get_state_includes_facets(self, tmp_path):
        engine = TrustEngine(session_dir=str(tmp_path))
        state = engine.get_state()
        assert hasattr(state, "facets")
        assert isinstance(state.facets, TrustFacets)

    def test_to_dict_includes_facets(self, tmp_path):
        engine = TrustEngine(session_dir=str(tmp_path))
        d = engine.get_state().to_dict()
        assert "facets" in d
        assert "competence" in d["facets"]
        assert "benevolence" in d["facets"]
        assert "integrity" in d["facets"]

    def test_initial_facets_equal_initial_trust(self, tmp_path):
        engine = TrustEngine(
            primary_contact_initial_trust=0.75,
            session_dir=str(tmp_path),
        )
        state = engine.get_state()
        assert abs(state.facets.competence - 0.75) < 1e-9
        assert abs(state.facets.benevolence - 0.75) < 1e-9
        assert abs(state.facets.integrity - 0.75) < 1e-9

    def test_stranger_facets_equal_stranger_trust(self, tmp_path):
        engine = TrustEngine(
            stranger_initial_trust=0.30,
            session_dir=str(tmp_path),
        )
        state = engine.get_state("stranger_01")
        assert abs(state.facets.competence - 0.30) < 1e-9
