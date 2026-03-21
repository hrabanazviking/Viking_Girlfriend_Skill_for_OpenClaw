"""
test_vordur_claims.py — E-33: Claim Extraction + Typing
========================================================

Tests for ClaimType enum, extended Claim dataclass, ClaimExtractor.extract(),
ClaimExtractor.classify(), and FaithfulnessScore.claims / claim_types_found.
"""

import sys
import uuid
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "viking_girlfriend_skill"))

from scripts.vordur import (
    Claim,
    ClaimExtractor,
    ClaimType,
    FaithfulnessScore,
    VordurChecker,
    VerdictLabel,
    ClaimVerification,
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


def _extractor() -> ClaimExtractor:
    return ClaimExtractor(router=None)


# ─── Tests: ClaimType enum ───────────────────────────────────────────────────


def test_claim_type_enum_has_all_12_values():
    """ClaimType enum exposes all 12 semantic categories."""
    expected = {
        "DEFINITIONAL", "FACTUAL", "HISTORICAL", "RELATIONAL", "CAUSAL",
        "PROCEDURAL", "INTERPRETIVE", "SYMBOLIC", "CODE_BEHAVIOR",
        "MATHEMATICAL", "SPECULATIVE", "SOURCE_ATTRIBUTION",
    }
    actual = {m.name for m in ClaimType}
    assert expected == actual


def test_claim_type_values_are_lowercase_strings():
    """ClaimType values are lowercase kebab/underscore strings (str enum)."""
    for ct in ClaimType:
        assert ct.value == ct.value.lower()
        assert isinstance(ct.value, str)


# ─── Tests: Claim dataclass (E-33 extensions) ────────────────────────────────


def test_claim_has_auto_uuid_id():
    """Claim.id is auto-generated and looks like a UUID."""
    c = _claim("Odin is the Allfather.")
    assert c.id
    # Should be parseable as a UUID
    parsed = uuid.UUID(c.id)
    assert str(parsed) == c.id


def test_claim_two_instances_have_different_ids():
    """Each Claim gets its own unique id."""
    c1 = _claim("Odin is the Allfather.")
    c2 = _claim("Odin is the Allfather.")
    assert c1.id != c2.id


def test_claim_default_claim_type_is_factual():
    """Claim.claim_type defaults to 'factual'."""
    c = _claim("Thor is the son of Odin.")
    assert c.claim_type == ClaimType.FACTUAL.value


def test_claim_default_sentence_index_is_zero():
    """Claim.sentence_index defaults to 0."""
    c = _claim("Mjolnir is Thor's hammer.")
    assert c.sentence_index == 0


def test_claim_default_certainty_level():
    """Claim.certainty_level defaults to 0.8."""
    c = _claim("Valhalla is Odin's hall.")
    assert c.certainty_level == 0.8


def test_claim_default_source_draft_section_empty():
    """Claim.source_draft_section defaults to empty string."""
    c = _claim("Freyja is a Vanir goddess.")
    assert c.source_draft_section == ""


def test_claim_backward_compatible_no_new_required_fields():
    """Claim can be constructed with only the original 3 positional args."""
    c = Claim(text="Odin has two ravens.", source_sentence="Odin has two ravens.", claim_index=0)
    assert c.text == "Odin has two ravens."
    assert c.id  # auto-generated


# ─── Tests: ClaimExtractor.extract() ─────────────────────────────────────────


def test_extract_empty_string_returns_empty():
    """extract() on empty string returns []."""
    ex = _extractor()
    assert ex.extract("") == []


def test_extract_whitespace_only_returns_empty():
    """extract() on whitespace-only returns []."""
    ex = _extractor()
    assert ex.extract("   \n\t  ") == []


def test_extract_returns_list_of_claims():
    """extract() on real text returns a non-empty List[Claim]."""
    ex = _extractor()
    text = "Odin is the Allfather. He sacrificed his eye at Mimir's well."
    result = ex.extract(text)
    assert isinstance(result, list)
    assert len(result) >= 1
    assert all(isinstance(c, Claim) for c in result)


def test_extract_assigns_claim_type_to_each_claim():
    """Each Claim returned by extract() has claim_type set."""
    ex = _extractor()
    text = "Thor wields Mjolnir. Historically this hammer is from Norse mythology."
    for claim in ex.extract(text):
        assert claim.claim_type in {ct.value for ct in ClaimType}


# ─── Tests: ClaimExtractor.classify() ────────────────────────────────────────


def test_classify_generic_text_is_factual():
    """Generic declarative text classifies as FACTUAL."""
    ex = _extractor()
    c = _claim("Odin rules Asgard.")
    result = ex.classify(c)
    assert result == ClaimType.FACTUAL


def test_classify_historical_keyword():
    """Text with 'century' or 'historically' classifies as HISTORICAL."""
    ex = _extractor()
    c = _claim("Viking raids occurred during the 9th century across Europe.")
    result = ex.classify(c)
    assert result == ClaimType.HISTORICAL


def test_classify_causal_keyword():
    """Text with 'because' or 'therefore' classifies as CAUSAL."""
    ex = _extractor()
    c = _claim("The raven is sacred to Odin because it carries wisdom from Midgard.")
    result = ex.classify(c)
    assert result == ClaimType.CAUSAL


def test_classify_procedural_keyword():
    """Text with 'first' / 'then' / 'step' classifies as PROCEDURAL."""
    ex = _extractor()
    c = _claim("First sacrifice an offering, then speak the runes aloud.")
    result = ex.classify(c)
    assert result == ClaimType.PROCEDURAL


def test_classify_speculative_keyword():
    """Text with 'may' or 'possibly' classifies as SPECULATIVE."""
    ex = _extractor()
    c = _claim("The serpent may represent chaos in Norse cosmology.")
    result = ex.classify(c)
    assert result == ClaimType.SPECULATIVE


def test_classify_code_keyword():
    """Text with 'function' or 'returns' classifies as CODE_BEHAVIOR."""
    ex = _extractor()
    c = _claim("The function returns a list of tokens after parsing the input.")
    result = ex.classify(c)
    assert result == ClaimType.CODE_BEHAVIOR


def test_classify_source_attribution_phrase():
    """Text with 'according to' classifies as SOURCE_ATTRIBUTION (phrase check)."""
    ex = _extractor()
    c = _claim("According to the Prose Edda, Yggdrasil has three roots.")
    result = ex.classify(c)
    assert result == ClaimType.SOURCE_ATTRIBUTION


def test_classify_definitional_phrase():
    """Text with 'is a' classifies as DEFINITIONAL."""
    ex = _extractor()
    c = _claim("A völva is a seeress in Norse Pagan tradition.")
    result = ex.classify(c)
    assert result == ClaimType.DEFINITIONAL


# ─── Tests: score() populates claims and claim_types_found ───────────────────


def test_score_populates_claims_list():
    """score() sets FaithfulnessScore.claims to extracted claims."""
    checker = VordurChecker(router=None, verdict_cache_enabled=False)
    chunks = [_chunk("Odin is the Allfather and ruler of Asgard in Norse mythology.")]
    fs = checker.score("Odin is the Allfather.", chunks)
    assert isinstance(fs.claims, list)


def test_score_claim_types_found_is_list_of_strings():
    """score() sets claim_types_found as a list of strings."""
    checker = VordurChecker(router=None, verdict_cache_enabled=False)
    chunks = [_chunk("Odin is the Allfather and ruler of Asgard in Norse mythology.")]
    fs = checker.score("Odin is the Allfather. He watches from Asgard.", chunks)
    assert isinstance(fs.claim_types_found, list)
    for ct in fs.claim_types_found:
        assert isinstance(ct, str)
        assert ct in {c.value for c in ClaimType}
