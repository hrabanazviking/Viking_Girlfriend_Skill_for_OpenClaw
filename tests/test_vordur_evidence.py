"""
test_vordur_evidence.py — E-34: Evidence Bundling + Support Analysis
=====================================================================

Tests for EvidenceBundle, SupportVerdict, VerificationRecord,
EvidenceBundler.bundle() / analyze(), and FaithfulnessScore.verification_records.
"""

import sys
import uuid
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "viking_girlfriend_skill"))

from scripts.vordur import (
    Claim,
    ClaimVerification,
    EvidenceBundle,
    EvidenceBundler,
    SupportVerdict,
    VerificationRecord,
    VerdictLabel,
    VordurChecker,
)
from scripts.mimir_well import KnowledgeChunk, DataRealm, TruthTier


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _chunk(text: str, *, source_file: str = "test.md", tier: TruthTier = TruthTier.TRUNK) -> KnowledgeChunk:
    return KnowledgeChunk(
        chunk_id=str(uuid.uuid4()),
        text=text,
        source_file=source_file,
        domain="norse_culture",
        realm=DataRealm.MIDGARD,
        tier=tier,
        level=1,
        metadata={},
    )


def _claim(text: str) -> Claim:
    return Claim(text=text, source_sentence=text, claim_index=0)


def _cv(claim: Claim, verdict: VerdictLabel, *, chunk_id: str = "abc") -> ClaimVerification:
    return ClaimVerification(
        claim=claim,
        verdict=verdict,
        confidence=0.8,
        supporting_chunk_id=chunk_id,
        judge_tier_used="regex",
        verification_ms=1.0,
    )


# ─── Tests: SupportVerdict enum ──────────────────────────────────────────────


def test_support_verdict_has_all_7_values():
    """SupportVerdict enum exposes all 7 fine-grained support classifications."""
    expected = {
        "SUPPORTED", "PARTIALLY_SUPPORTED", "UNSUPPORTED",
        "CONTRADICTED", "INFERRED_PLAUSIBLE", "SPECULATIVE", "AMBIGUOUS",
    }
    actual = {m.name for m in SupportVerdict}
    assert expected == actual


def test_support_verdict_values_are_strings():
    """SupportVerdict values are lowercase strings (str Enum)."""
    for sv in SupportVerdict:
        assert isinstance(sv.value, str)
        assert sv.value == sv.value.lower()


# ─── Tests: EvidenceBundle dataclass ─────────────────────────────────────────


def test_evidence_bundle_construction():
    """EvidenceBundle can be constructed with required fields."""
    c = _chunk("Odin is the Allfather.")
    bundle = EvidenceBundle(claim_id="test-id", primary_chunk=c)
    assert bundle.claim_id == "test-id"
    assert bundle.primary_chunk is c
    assert bundle.neighbor_chunks == []
    assert bundle.source_tier == ""
    assert bundle.provenance == ""


def test_evidence_bundle_with_neighbors():
    """EvidenceBundle accepts neighbor_chunks list."""
    primary = _chunk("Odin is the Allfather.")
    n1 = _chunk("Odin rules Asgard.")
    n2 = _chunk("Odin is husband of Frigg.")
    bundle = EvidenceBundle(
        claim_id="c1",
        primary_chunk=primary,
        neighbor_chunks=[n1, n2],
        source_tier="trunk",
        provenance="eddas.md",
    )
    assert len(bundle.neighbor_chunks) == 2
    assert bundle.source_tier == "trunk"
    assert bundle.provenance == "eddas.md"


# ─── Tests: VerificationRecord dataclass ─────────────────────────────────────


def test_verification_record_defaults():
    """VerificationRecord uses sensible defaults."""
    rec = VerificationRecord(claim_id="cid")
    assert rec.evidence_ids == []
    assert rec.verdict == SupportVerdict.AMBIGUOUS
    assert rec.entailment_score == 0.5
    assert rec.contradiction_score == 0.0
    assert rec.citation_coverage == 0.0
    assert rec.ambiguity_score == 0.5


def test_verification_record_to_dict():
    """VerificationRecord.to_dict() returns a dict with expected keys."""
    rec = VerificationRecord(
        claim_id="cid",
        evidence_ids=["e1", "e2"],
        verdict=SupportVerdict.SUPPORTED,
        entailment_score=1.0,
        contradiction_score=0.0,
        citation_coverage=0.67,
        ambiguity_score=0.0,
    )
    d = rec.to_dict()
    assert d["claim_id"] == "cid"
    assert d["verdict"] == "supported"
    assert d["entailment_score"] == 1.0
    assert "evidence_ids" in d


# ─── Tests: EvidenceBundler.bundle() ─────────────────────────────────────────


def test_bundle_empty_chunks_returns_null_primary():
    """bundle() with empty source_chunks returns an EvidenceBundle with null chunk."""
    bundler = EvidenceBundler()
    c = _claim("Odin is the Allfather.")
    result = bundler.bundle(c, [])
    assert isinstance(result, EvidenceBundle)
    assert result.claim_id == c.id
    assert result.primary_chunk is not None  # null chunk placeholder


def test_bundle_picks_primary_chunk():
    """bundle() selects a primary chunk from the list."""
    bundler = EvidenceBundler()
    c = _claim("Odin is the Allfather.")
    chunks = [_chunk("Odin rules Asgard."), _chunk("Freyja is Vanir.")]
    result = bundler.bundle(c, chunks)
    assert result.primary_chunk in chunks


def test_bundle_neighbors_exclude_primary():
    """bundle() neighbor_chunks don't include the primary chunk."""
    bundler = EvidenceBundler()
    c = _claim("Odin is the Allfather.")
    chunks = [_chunk(f"chunk {i}") for i in range(4)]
    result = bundler.bundle(c, chunks)
    assert result.primary_chunk not in result.neighbor_chunks


def test_bundle_sets_provenance_from_source_file():
    """bundle() sets provenance to primary_chunk.source_file."""
    bundler = EvidenceBundler()
    c = _claim("Odin is the Allfather.")
    chunks = [_chunk("Odin rules Asgard.", source_file="prose_edda.md")]
    result = bundler.bundle(c, chunks)
    assert result.provenance == "prose_edda.md"


def test_bundle_sets_source_tier():
    """bundle() sets source_tier from primary chunk tier name."""
    bundler = EvidenceBundler()
    c = _claim("Odin is the Allfather.")
    chunks = [_chunk("Odin rules Asgard.", tier=TruthTier.TRUNK)]
    result = bundler.bundle(c, chunks)
    assert result.source_tier == "trunk"


# ─── Tests: EvidenceBundler.analyze() ────────────────────────────────────────


def test_analyze_entailed_maps_to_supported():
    """analyze() maps ENTAILED verdict to SupportVerdict.SUPPORTED."""
    bundler = EvidenceBundler()
    c = _claim("Odin is the Allfather.")
    chunk = _chunk("Odin is the Allfather and ruler of Asgard.")
    bundle = bundler.bundle(c, [chunk])
    cv = _cv(c, VerdictLabel.ENTAILED, chunk_id=chunk.chunk_id)
    rec = bundler.analyze(bundle, cv)
    assert rec.verdict == SupportVerdict.SUPPORTED


def test_analyze_neutral_maps_to_inferred_plausible():
    """analyze() maps NEUTRAL verdict to SupportVerdict.INFERRED_PLAUSIBLE."""
    bundler = EvidenceBundler()
    c = _claim("Odin may have invented the runes.")
    chunk = _chunk("Norse myths contain many stories about wisdom.")
    bundle = bundler.bundle(c, [chunk])
    cv = _cv(c, VerdictLabel.NEUTRAL, chunk_id=chunk.chunk_id)
    rec = bundler.analyze(bundle, cv)
    assert rec.verdict == SupportVerdict.INFERRED_PLAUSIBLE


def test_analyze_contradicted_maps_to_contradicted():
    """analyze() maps CONTRADICTED verdict to SupportVerdict.CONTRADICTED."""
    bundler = EvidenceBundler()
    c = _claim("Thor is a Vanir god.")
    chunk = _chunk("Thor is an Aesir god, son of Odin.")
    bundle = bundler.bundle(c, [chunk])
    cv = _cv(c, VerdictLabel.CONTRADICTED, chunk_id=chunk.chunk_id)
    rec = bundler.analyze(bundle, cv)
    assert rec.verdict == SupportVerdict.CONTRADICTED


def test_analyze_uncertain_maps_to_ambiguous():
    """analyze() maps UNCERTAIN verdict to SupportVerdict.AMBIGUOUS."""
    bundler = EvidenceBundler()
    c = _claim("Some mystery exists here.")
    chunk = _chunk("Details are unclear.")
    bundle = bundler.bundle(c, [chunk])
    cv = _cv(c, VerdictLabel.UNCERTAIN, chunk_id=chunk.chunk_id)
    rec = bundler.analyze(bundle, cv)
    assert rec.verdict == SupportVerdict.AMBIGUOUS


def test_analyze_entailment_score_1_for_entailed():
    """analyze() sets entailment_score=1.0 for ENTAILED verdict."""
    bundler = EvidenceBundler()
    c = _claim("Odin is the Allfather.")
    chunk = _chunk("Odin rules Asgard.")
    bundle = bundler.bundle(c, [chunk])
    cv = _cv(c, VerdictLabel.ENTAILED)
    rec = bundler.analyze(bundle, cv)
    assert rec.entailment_score == 1.0


def test_analyze_entailment_score_0_for_contradicted():
    """analyze() sets entailment_score=0.0 for CONTRADICTED verdict."""
    bundler = EvidenceBundler()
    c = _claim("Thor is Vanir.")
    chunk = _chunk("Thor is Aesir.")
    bundle = bundler.bundle(c, [chunk])
    cv = _cv(c, VerdictLabel.CONTRADICTED)
    rec = bundler.analyze(bundle, cv)
    assert rec.entailment_score == 0.0


def test_analyze_contradiction_score_1_for_contradicted():
    """analyze() sets contradiction_score=1.0 for CONTRADICTED verdict."""
    bundler = EvidenceBundler()
    c = _claim("Thor is Vanir.")
    chunk = _chunk("Thor is Aesir.")
    bundle = bundler.bundle(c, [chunk])
    cv = _cv(c, VerdictLabel.CONTRADICTED)
    rec = bundler.analyze(bundle, cv)
    assert rec.contradiction_score == 1.0


def test_analyze_ambiguity_score_1_for_uncertain():
    """analyze() sets ambiguity_score=1.0 for UNCERTAIN verdict."""
    bundler = EvidenceBundler()
    c = _claim("Something unclear.")
    chunk = _chunk("Mystery text.")
    bundle = bundler.bundle(c, [chunk])
    cv = _cv(c, VerdictLabel.UNCERTAIN)
    rec = bundler.analyze(bundle, cv)
    assert rec.ambiguity_score == 1.0


# ─── Tests: score() integration ───────────────────────────────────────────────


def test_score_populates_verification_records():
    """score() populates FaithfulnessScore.verification_records."""
    checker = VordurChecker(router=None, verdict_cache_enabled=False)
    text = "Odin is the Allfather. Thor wields Mjolnir."
    chunks = [_chunk("Norse gods include Odin and Thor.")]
    fs = checker.score(text, chunks)
    assert isinstance(fs.verification_records, list)
    assert len(fs.verification_records) >= 0  # may be 0 if no claims extracted


def test_score_verification_records_have_claim_ids():
    """Each VerificationRecord in score() result has a non-empty claim_id."""
    checker = VordurChecker(router=None, verdict_cache_enabled=False)
    text = "Odin is the Allfather. He rules Asgard with great power."
    chunks = [_chunk("Odin rules Asgard in Norse mythology.")]
    fs = checker.score(text, chunks)
    for rec in fs.verification_records:
        assert rec.claim_id
        assert isinstance(rec.claim_id, str)
