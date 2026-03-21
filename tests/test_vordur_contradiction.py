"""
test_vordur_contradiction.py — E-36: Contradiction Analyzer
============================================================

Tests for ContradictionType enum, ContradictionRecord dataclass,
ContradictionAnalyzer.analyze(), TRADITION_DIVERGENCE handling,
and TruthProfile.contradictions field.
"""

import sys
import uuid
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "viking_girlfriend_skill"))

from scripts.vordur import (
    Claim,
    ClaimType,
    ClaimVerification,
    ContradictionAnalyzer,
    ContradictionRecord,
    ContradictionType,
    EvidenceBundler,
    SupportVerdict,
    TruthProfile,
    VerificationRecord,
    VerdictLabel,
    VordurChecker,
)
from scripts.mimir_well import KnowledgeChunk, DataRealm, TruthTier


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _chunk(text: str, *, source_file: str = "test.md") -> KnowledgeChunk:
    return KnowledgeChunk(
        chunk_id=str(uuid.uuid4()),
        text=text,
        source_file=source_file,
        domain="norse_culture",
        realm=DataRealm.MIDGARD,
        tier=TruthTier.TRUNK,
        level=1,
        metadata={},
    )


def _claim(text: str, claim_type: str = ClaimType.FACTUAL.value) -> Claim:
    c = Claim(text=text, source_sentence=text, claim_index=0)
    c.claim_type = claim_type
    return c


def _record(claim_id: str, verdict: SupportVerdict, *, chunk_id: str = "e1") -> VerificationRecord:
    return VerificationRecord(
        claim_id=claim_id,
        evidence_ids=[chunk_id],
        verdict=verdict,
        entailment_score=1.0 if verdict == SupportVerdict.SUPPORTED else 0.0,
        contradiction_score=1.0 if verdict == SupportVerdict.CONTRADICTED else 0.0,
        citation_coverage=0.33,
        ambiguity_score=0.0,
    )


def _analyzer() -> ContradictionAnalyzer:
    return ContradictionAnalyzer()


# ─── Tests: ContradictionType enum ───────────────────────────────────────────


def test_contradiction_type_has_all_5_values():
    """ContradictionType enum exposes all 5 classification values."""
    expected = {
        "CLAIM_VS_SOURCE", "INTER_SOURCE", "INTRA_RESPONSE",
        "TRADITION_DIVERGENCE", "NONE",
    }
    actual = {m.name for m in ContradictionType}
    assert expected == actual


def test_contradiction_type_values_are_strings():
    """ContradictionType values are lowercase strings (str Enum)."""
    for ct in ContradictionType:
        assert isinstance(ct.value, str)


# ─── Tests: ContradictionRecord dataclass ────────────────────────────────────


def test_contradiction_record_defaults():
    """ContradictionRecord has safe defaults."""
    rec = ContradictionRecord()
    assert rec.claim_ids == []
    assert rec.chunk_ids == []
    assert rec.contradiction_type == ContradictionType.NONE
    assert rec.severity == 0.0
    assert rec.description == ""


def test_contradiction_record_to_dict():
    """ContradictionRecord.to_dict() returns dict with all expected keys."""
    rec = ContradictionRecord(
        claim_ids=["c1"],
        chunk_ids=["k1", "k2"],
        contradiction_type=ContradictionType.CLAIM_VS_SOURCE,
        severity=0.8,
        description="test contradiction",
    )
    d = rec.to_dict()
    assert d["claim_ids"] == ["c1"]
    assert d["chunk_ids"] == ["k1", "k2"]
    assert d["contradiction_type"] == "claim_vs_source"
    assert d["severity"] == 0.8
    assert d["description"] == "test contradiction"


# ─── Tests: ContradictionAnalyzer.analyze() — CLAIM_VS_SOURCE ────────────────


def test_analyze_empty_inputs_returns_empty():
    """analyze() on empty claims/records/chunks returns []."""
    ana = _analyzer()
    result = ana.analyze([], [], [])
    assert result == []


def test_analyze_contradicted_record_produces_claim_vs_source():
    """CONTRADICTED VerificationRecord → ContradictionType.CLAIM_VS_SOURCE."""
    ana = _analyzer()
    c = _claim("Loki is a frost giant.", claim_type=ClaimType.FACTUAL.value)
    rec = _record(c.id, SupportVerdict.CONTRADICTED)
    result = ana.analyze([c], [rec], [])
    assert len(result) >= 1
    types = [r.contradiction_type for r in result]
    assert ContradictionType.CLAIM_VS_SOURCE in types


def test_analyze_supported_record_no_contradiction():
    """SUPPORTED VerificationRecord → no ContradictionRecord."""
    ana = _analyzer()
    c = _claim("Odin is the Allfather.")
    rec = _record(c.id, SupportVerdict.SUPPORTED)
    result = ana.analyze([c], [rec], [])
    claim_vs_source = [r for r in result if r.contradiction_type == ContradictionType.CLAIM_VS_SOURCE]
    assert claim_vs_source == []


def test_analyze_contradiction_record_includes_claim_id():
    """ContradictionRecord for CLAIM_VS_SOURCE includes the claim's id."""
    ana = _analyzer()
    c = _claim("Loki created Midgard.", claim_type=ClaimType.FACTUAL.value)
    rec = _record(c.id, SupportVerdict.CONTRADICTED)
    results = ana.analyze([c], [rec], [])
    claim_vs = [r for r in results if r.contradiction_type == ContradictionType.CLAIM_VS_SOURCE]
    assert any(c.id in r.claim_ids for r in claim_vs)


# ─── Tests: TRADITION_DIVERGENCE (symbolic/historical) ───────────────────────


def test_analyze_symbolic_claim_contradicted_gives_tradition_divergence():
    """CONTRADICTED verdict on SYMBOLIC claim → TRADITION_DIVERGENCE (not CLAIM_VS_SOURCE)."""
    ana = _analyzer()
    c = _claim("Yggdrasil symbolizes the cycle of life.", claim_type=ClaimType.SYMBOLIC.value)
    rec = _record(c.id, SupportVerdict.CONTRADICTED)
    results = ana.analyze([c], [rec], [])
    types = [r.contradiction_type for r in results]
    assert ContradictionType.TRADITION_DIVERGENCE in types
    assert ContradictionType.CLAIM_VS_SOURCE not in types


def test_analyze_historical_claim_contradicted_gives_tradition_divergence():
    """CONTRADICTED verdict on HISTORICAL claim → TRADITION_DIVERGENCE."""
    ana = _analyzer()
    c = _claim("Vikings arrived in Vinland during the 10th century.",
               claim_type=ClaimType.HISTORICAL.value)
    rec = _record(c.id, SupportVerdict.CONTRADICTED)
    results = ana.analyze([c], [rec], [])
    types = [r.contradiction_type for r in results]
    assert ContradictionType.TRADITION_DIVERGENCE in types


def test_analyze_interpretive_claim_contradicted_gives_tradition_divergence():
    """CONTRADICTED verdict on INTERPRETIVE claim → TRADITION_DIVERGENCE."""
    ana = _analyzer()
    c = _claim("The serpent Jörmungandr can be interpreted as entropy.",
               claim_type=ClaimType.INTERPRETIVE.value)
    rec = _record(c.id, SupportVerdict.CONTRADICTED)
    results = ana.analyze([c], [rec], [])
    types = [r.contradiction_type for r in results]
    assert ContradictionType.TRADITION_DIVERGENCE in types


# ─── Tests: INTER_SOURCE ─────────────────────────────────────────────────────


def test_analyze_inter_source_detected_with_negation_asymmetry():
    """Two chunks with shared topic overlap + one negating → INTER_SOURCE."""
    ana = _analyzer()
    c1 = _chunk("Odin is the Allfather of all Norse gods.")
    c2 = _chunk("Odin is not the creator but the ruler of Norse gods.")
    result = ana.analyze([], [], [c1, c2])
    inter = [r for r in result if r.contradiction_type == ContradictionType.INTER_SOURCE]
    assert len(inter) >= 1
    assert all(len(r.chunk_ids) == 2 for r in inter)


# ─── Tests: INTRA_RESPONSE ───────────────────────────────────────────────────


def test_analyze_intra_response_detected():
    """Two claims of same type with overlap + negation → INTRA_RESPONSE."""
    ana = _analyzer()
    c1 = _claim("Thor is always victorious in battle.", claim_type=ClaimType.FACTUAL.value)
    c2 = _claim("Thor is not always victorious in battle.", claim_type=ClaimType.FACTUAL.value)
    result = ana.analyze([c1, c2], [], [])
    intra = [r for r in result if r.contradiction_type == ContradictionType.INTRA_RESPONSE]
    assert len(intra) >= 1


# ─── Tests: TruthProfile.contradictions ──────────────────────────────────────


def test_truth_profile_has_contradictions_field():
    """TruthProfile has contradictions field defaulting to []."""
    tp = TruthProfile()
    assert hasattr(tp, "contradictions")
    assert tp.contradictions == []


def test_truth_profile_contradictions_in_to_dict():
    """TruthProfile.to_dict() includes contradictions list."""
    rec = ContradictionRecord(
        contradiction_type=ContradictionType.CLAIM_VS_SOURCE,
        severity=0.5,
        description="test",
    )
    tp = TruthProfile(contradictions=[rec])
    d = tp.to_dict()
    assert "contradictions" in d
    assert len(d["contradictions"]) == 1
    assert d["contradictions"][0]["contradiction_type"] == "claim_vs_source"


def test_score_and_repair_truth_profile_has_contradictions():
    """score_and_repair() truth_profile.contradictions is populated."""
    checker = VordurChecker(router=None, verdict_cache_enabled=False)
    chunks = [_chunk("Norse mythology has many gods.")]
    fs, tp, text = checker.score_and_repair(
        "Odin is the Allfather. He always wins every battle.", chunks
    )
    assert hasattr(tp, "contradictions")
    assert isinstance(tp.contradictions, list)
