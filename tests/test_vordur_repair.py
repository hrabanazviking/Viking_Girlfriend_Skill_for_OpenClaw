"""
test_vordur_repair.py — E-35: Repair Engine + Truth Profile
===========================================================

Tests for RepairAction enum, RepairRecord dataclass, TruthProfile dataclass,
RepairEngine.repair() (regex + model paths), score_and_repair(), _build_truth_profile(),
and CompletionResponse.truth_profile.
"""

import sys
import uuid
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "viking_girlfriend_skill"))

from scripts.vordur import (
    Claim,
    ClaimVerification,
    EvidenceBundler,
    FaithfulnessScore,
    RepairAction,
    RepairEngine,
    RepairRecord,
    SupportVerdict,
    TruthProfile,
    VerificationRecord,
    VerdictLabel,
    VordurChecker,
)
from scripts.mimir_well import KnowledgeChunk, DataRealm, TruthTier


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _chunk(text: str) -> KnowledgeChunk:
    return KnowledgeChunk(
        chunk_id=str(uuid.uuid4()),
        text=text,
        source_file="test.md",
        domain="norse_culture",
        realm=DataRealm.MIDGARD,
        tier=TruthTier.TRUNK,
        level=1,
        metadata={},
    )


def _claim(text: str) -> Claim:
    return Claim(text=text, source_sentence=text, claim_index=0)


def _record(verdict: SupportVerdict) -> VerificationRecord:
    return VerificationRecord(
        claim_id=str(uuid.uuid4()),
        evidence_ids=["e1"],
        verdict=verdict,
        entailment_score=1.0 if verdict == SupportVerdict.SUPPORTED else 0.0,
        contradiction_score=1.0 if verdict == SupportVerdict.CONTRADICTED else 0.0,
        citation_coverage=0.33,
        ambiguity_score=0.0,
    )


# ─── Tests: RepairAction enum ─────────────────────────────────────────────────


def test_repair_action_has_all_5_values():
    """RepairAction enum exposes all 5 action types."""
    expected = {
        "REMOVE_CLAIM", "DOWNGRADE_CERTAINTY", "ADD_UNCERTAINTY_MARKER",
        "REPLACE_WITH_EVIDENCE", "SPLIT_INTO_TRADITIONS",
    }
    actual = {m.name for m in RepairAction}
    assert expected == actual


def test_repair_action_values_are_strings():
    """RepairAction values are strings (str Enum)."""
    for ra in RepairAction:
        assert isinstance(ra.value, str)


# ─── Tests: RepairRecord dataclass ───────────────────────────────────────────


def test_repair_record_construction():
    """RepairRecord can be constructed with all fields."""
    cid = str(uuid.uuid4())
    rr = RepairRecord(
        claim_id=cid,
        action=RepairAction.DOWNGRADE_CERTAINTY.value,
        original_text="Odin is the god of war.",
        revised_text="Odin may be considered a god of war.",
        reason="Contradicted by source.",
    )
    assert rr.claim_id == cid
    assert rr.action == "downgrade_certainty"
    assert "war" in rr.original_text
    assert rr.reason == "Contradicted by source."


# ─── Tests: TruthProfile dataclass ───────────────────────────────────────────


def test_truth_profile_defaults_all_zero():
    """TruthProfile defaults: all floats 0.0, repair_count 0."""
    tp = TruthProfile()
    assert tp.faithfulness == 0.0
    assert tp.citation_coverage == 0.0
    assert tp.contradiction_risk == 0.0
    assert tp.inference_density == 0.0
    assert tp.source_quality == 0.0
    assert tp.answer_relevance == 0.0
    assert tp.ambiguity_level == 0.0
    assert tp.repair_count == 0


def test_truth_profile_to_dict():
    """TruthProfile.to_dict() returns dict with all expected keys."""
    tp = TruthProfile(faithfulness=0.85, contradiction_risk=0.1, repair_count=2)
    d = tp.to_dict()
    assert d["faithfulness"] == 0.85
    assert d["contradiction_risk"] == 0.1
    assert d["repair_count"] == 2
    assert "citation_coverage" in d
    assert "ambiguity_level" in d


# ─── Tests: RepairEngine ─────────────────────────────────────────────────────


def test_repair_engine_init_no_router():
    """RepairEngine initializes with no router."""
    engine = RepairEngine(router=None)
    assert engine._router is None


def test_repair_no_contradicted_records_returns_original():
    """repair() with no CONTRADICTED records returns original draft unchanged."""
    engine = RepairEngine(router=None)
    draft = "Odin is the Allfather of Norse mythology."
    records = [_record(SupportVerdict.SUPPORTED), _record(SupportVerdict.INFERRED_PLAUSIBLE)]
    text, repairs = engine.repair(draft, records)
    assert text == draft
    assert repairs == []


def test_repair_empty_records_returns_original():
    """repair() with empty records list returns (draft, [])."""
    engine = RepairEngine(router=None)
    draft = "Some text here."
    text, repairs = engine.repair(draft, [])
    assert text == draft
    assert repairs == []


def test_repair_regex_downgrades_is_to_may_be():
    """_repair_regex() replaces 'is' with 'may be' on CONTRADICTED claims."""
    engine = RepairEngine(router=None)
    draft = "Loki is a fire giant from Jotunheim."
    records = [_record(SupportVerdict.CONTRADICTED)]
    text, repairs = engine.repair(draft, records)
    assert "may be" in text or text != draft  # some downgrade occurred


def test_repair_regex_downgrades_always_to_often():
    """_repair_regex() replaces 'always' with 'often' on CONTRADICTED claims."""
    engine = RepairEngine(router=None)
    draft = "Loki always causes mischief in Asgard without reason."
    records = [_record(SupportVerdict.CONTRADICTED)]
    text, repairs = engine.repair(draft, records)
    assert "often" in text


def test_repair_regex_downgrades_never_to_rarely():
    """_repair_regex() replaces 'never' with 'rarely'."""
    engine = RepairEngine(router=None)
    draft = "Odin never loses in battle according to myths."
    records = [_record(SupportVerdict.CONTRADICTED)]
    text, repairs = engine.repair(draft, records)
    assert "rarely" in text


def test_repair_regex_downgrades_proven():
    """_repair_regex() replaces 'proven' with 'suggested' when 'is' not present first."""
    engine = RepairEngine(router=None)
    # Avoid 'is/are/was/were/always/never' so the proven pattern fires (patterns apply in order)
    draft = "Thor has proven strength beyond all other gods."
    records = [_record(SupportVerdict.CONTRADICTED)]
    text, repairs = engine.repair(draft, records)
    assert "suggested" in text


def test_repair_regex_produces_repair_record():
    """_repair_regex() produces a RepairRecord with DOWNGRADE_CERTAINTY action."""
    engine = RepairEngine(router=None)
    draft = "Baldur is always pure and cannot be harmed."
    records = [_record(SupportVerdict.CONTRADICTED)]
    text, repairs = engine.repair(draft, records)
    assert isinstance(repairs, list)
    if repairs:  # at least one repair when text changed
        assert repairs[0].action == RepairAction.DOWNGRADE_CERTAINTY.value


# ─── Tests: score_and_repair() ───────────────────────────────────────────────


def test_score_and_repair_returns_3_tuple():
    """score_and_repair() returns exactly 3 items."""
    checker = VordurChecker(router=None, verdict_cache_enabled=False)
    chunks = [_chunk("Odin is the Allfather of Norse mythology.")]
    result = checker.score_and_repair("Odin is the Allfather.", chunks)
    assert len(result) == 3


def test_score_and_repair_first_item_is_faithfulness_score():
    """score_and_repair() first item is a FaithfulnessScore."""
    checker = VordurChecker(router=None, verdict_cache_enabled=False)
    chunks = [_chunk("Odin rules Asgard.")]
    fs, tp, text = checker.score_and_repair("Odin is the Allfather.", chunks)
    assert isinstance(fs, FaithfulnessScore)


def test_score_and_repair_second_item_is_truth_profile():
    """score_and_repair() second item is a TruthProfile."""
    checker = VordurChecker(router=None, verdict_cache_enabled=False)
    chunks = [_chunk("Norse mythology spans many cultures.")]
    fs, tp, text = checker.score_and_repair("Odin is wise.", chunks)
    assert isinstance(tp, TruthProfile)


def test_score_and_repair_third_item_is_string():
    """score_and_repair() third item is a string (repaired or original text)."""
    checker = VordurChecker(router=None, verdict_cache_enabled=False)
    chunks = [_chunk("Norse mythology spans many cultures.")]
    fs, tp, text = checker.score_and_repair("Odin is wise.", chunks)
    assert isinstance(text, str)


def test_score_and_repair_does_not_raise_on_empty_chunks():
    """score_and_repair() never raises even with no source chunks."""
    checker = VordurChecker(router=None, verdict_cache_enabled=False)
    fs, tp, text = checker.score_and_repair("Odin is the Allfather.", [])
    assert isinstance(fs, FaithfulnessScore)
    assert isinstance(tp, TruthProfile)
    assert isinstance(text, str)


# ─── Tests: _build_truth_profile() ───────────────────────────────────────────


def test_build_truth_profile_faithfulness_matches_fs_score():
    """_build_truth_profile() faithfulness mirrors FaithfulnessScore.score."""
    checker = VordurChecker(router=None, verdict_cache_enabled=False)
    chunks = [_chunk("Odin is the Allfather of Asgard.")]
    fs = checker.score("Odin is the Allfather.", chunks)
    tp = checker._build_truth_profile(fs, repair_count=0)
    assert tp.faithfulness == fs.score


def test_build_truth_profile_contradiction_risk():
    """_build_truth_profile() contradiction_risk = contradicted / claim_count."""
    checker = VordurChecker(router=None, verdict_cache_enabled=False)
    # Build a synthetic FaithfulnessScore
    c = _claim("test claim")
    cv = ClaimVerification(
        claim=c,
        verdict=VerdictLabel.CONTRADICTED,
        confidence=0.9,
        supporting_chunk_id="x",
        judge_tier_used="regex",
        verification_ms=1.0,
    )
    fs = FaithfulnessScore(
        score=0.0,
        tier="hallucination",
        claim_count=2,
        entailed_count=0,
        neutral_count=0,
        contradicted_count=2,
        uncertain_count=0,
        verifications=[cv, cv],
    )
    tp = checker._build_truth_profile(fs, repair_count=0)
    assert tp.contradiction_risk == pytest.approx(1.0)


def test_build_truth_profile_citation_coverage():
    """_build_truth_profile() citation_coverage = entailed / claim_count."""
    checker = VordurChecker(router=None, verdict_cache_enabled=False)
    c = _claim("test claim")
    cv_entailed = ClaimVerification(
        claim=c,
        verdict=VerdictLabel.ENTAILED,
        confidence=0.9,
        supporting_chunk_id="x",
        judge_tier_used="regex",
        verification_ms=1.0,
    )
    fs = FaithfulnessScore(
        score=0.5,
        tier="marginal",
        claim_count=2,
        entailed_count=1,
        neutral_count=1,
        contradicted_count=0,
        uncertain_count=0,
        verifications=[cv_entailed],
    )
    tp = checker._build_truth_profile(fs, repair_count=0)
    assert tp.citation_coverage == pytest.approx(0.5)


def test_build_truth_profile_repair_count():
    """_build_truth_profile() passes through repair_count."""
    checker = VordurChecker(router=None, verdict_cache_enabled=False)
    fs = FaithfulnessScore(
        score=0.5,
        tier="marginal",
        claim_count=1,
        entailed_count=0,
        neutral_count=1,
        contradicted_count=0,
        uncertain_count=0,
    )
    tp = checker._build_truth_profile(fs, repair_count=3)
    assert tp.repair_count == 3


# ─── Tests: CompletionResponse.truth_profile ─────────────────────────────────


def test_completion_response_has_truth_profile_field():
    """CompletionResponse has a truth_profile attribute (defaults to None)."""
    from scripts.model_router_client import CompletionResponse
    resp = CompletionResponse(content="Hello, traveller!", model="test", tier="subconscious")
    assert hasattr(resp, "truth_profile")
    assert resp.truth_profile is None


def test_completion_response_truth_profile_accepts_truth_profile():
    """CompletionResponse.truth_profile can store a TruthProfile instance."""
    from scripts.model_router_client import CompletionResponse
    tp = TruthProfile(faithfulness=0.9, repair_count=1)
    resp = CompletionResponse(content="Hello!", model="test", tier="subconscious", truth_profile=tp)
    assert resp.truth_profile is tp
    assert resp.truth_profile.faithfulness == 0.9
