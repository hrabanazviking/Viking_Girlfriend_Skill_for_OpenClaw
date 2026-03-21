"""
test_vordur_domain_validators.py — E-38: Domain-Specific Validators
====================================================================

Tests for DomainValidator ABC, CodeValidator, HistoricalValidator,
SymbolicValidator, ProceduralValidator, _DOMAIN_VALIDATORS registry,
get_domain_validator(), and VordurChecker.verify_claim() domain shortcircuit.
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
    CodeValidator,
    DomainValidator,
    HistoricalValidator,
    ProceduralValidator,
    SymbolicValidator,
    VerdictLabel,
    VordurChecker,
    _DOMAIN_VALIDATORS,
    get_domain_validator,
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


def _claim(text: str, claim_type: str = ClaimType.FACTUAL.value) -> Claim:
    c = Claim(text=text, source_sentence=text, claim_index=0)
    c.claim_type = claim_type
    return c


# ─── Tests: DomainValidator ABC ──────────────────────────────────────────────


def test_domain_validator_base_returns_uncertain():
    """Base DomainValidator.validate() returns (UNCERTAIN, 0.5, reason)."""
    dv = DomainValidator()
    verdict, confidence, reason = dv.validate(_claim("test"), [])
    assert verdict == VerdictLabel.UNCERTAIN
    assert confidence == 0.5
    assert isinstance(reason, str)


def test_domain_validator_has_domain_attribute():
    """DomainValidator subclasses set a domain class attribute."""
    assert CodeValidator.domain == "code"
    assert HistoricalValidator.domain == "historical"
    assert SymbolicValidator.domain == "symbolic"
    assert ProceduralValidator.domain == "procedural"


# ─── Tests: _DOMAIN_VALIDATORS registry ──────────────────────────────────────


def test_domain_validators_registry_has_expected_keys():
    """_DOMAIN_VALIDATORS contains entries for code, historical, symbolic, procedural."""
    assert ClaimType.CODE_BEHAVIOR.value in _DOMAIN_VALIDATORS
    assert ClaimType.HISTORICAL.value in _DOMAIN_VALIDATORS
    assert ClaimType.SYMBOLIC.value in _DOMAIN_VALIDATORS
    assert ClaimType.PROCEDURAL.value in _DOMAIN_VALIDATORS


def test_get_domain_validator_returns_correct_instance():
    """get_domain_validator() returns the right DomainValidator type."""
    assert isinstance(get_domain_validator(ClaimType.CODE_BEHAVIOR.value), CodeValidator)
    assert isinstance(get_domain_validator(ClaimType.HISTORICAL.value), HistoricalValidator)
    assert isinstance(get_domain_validator(ClaimType.SYMBOLIC.value), SymbolicValidator)
    assert isinstance(get_domain_validator(ClaimType.PROCEDURAL.value), ProceduralValidator)


def test_get_domain_validator_returns_none_for_factual():
    """get_domain_validator() returns None for FACTUAL claim type (no special validator)."""
    assert get_domain_validator(ClaimType.FACTUAL.value) is None


def test_get_domain_validator_returns_none_for_unknown():
    """get_domain_validator() returns None for unknown claim types."""
    assert get_domain_validator("totally_unknown_type") is None


# ─── Tests: CodeValidator ─────────────────────────────────────────────────────


def test_code_validator_syntax_error_returns_contradicted():
    """CodeValidator.validate() returns CONTRADICTED on SyntaxError."""
    cv = CodeValidator()
    c = _claim("def foo(: invalid python syntax here")
    verdict, confidence, reason = cv.validate(c, [])
    assert verdict == VerdictLabel.CONTRADICTED
    assert confidence > 0.5
    assert "syntax" in reason.lower()


def test_code_validator_valid_code_returns_entailed():
    """CodeValidator.validate() returns ENTAILED for parseable Python code."""
    cv = CodeValidator()
    c = _claim("def greet(): return 'hello'")
    verdict, confidence, reason = cv.validate(c, [])
    assert verdict == VerdictLabel.ENTAILED
    assert confidence > 0.5


def test_code_validator_no_code_returns_uncertain():
    """CodeValidator.validate() returns UNCERTAIN for non-code text."""
    cv = CodeValidator()
    c = _claim("Odin is the Allfather of the Norse gods.")
    verdict, confidence, reason = cv.validate(c, [])
    assert verdict == VerdictLabel.UNCERTAIN


def test_code_validator_never_raises():
    """CodeValidator.validate() never raises regardless of input."""
    cv = CodeValidator()
    c = _claim("")
    verdict, confidence, reason = cv.validate(c, [])
    assert isinstance(verdict, VerdictLabel)


# ─── Tests: HistoricalValidator ───────────────────────────────────────────────


def test_historical_validator_universal_quantifier_returns_neutral():
    """HistoricalValidator.validate() returns NEUTRAL for universal claims."""
    hv = HistoricalValidator()
    c = _claim("All Vikings always raided coastal settlements every summer.")
    verdict, confidence, reason = hv.validate(c, [])
    assert verdict == VerdictLabel.NEUTRAL
    assert "universal" in reason.lower()


def test_historical_validator_primary_source_returns_entailed():
    """HistoricalValidator.validate() returns ENTAILED when primary source referenced."""
    hv = HistoricalValidator()
    c = _claim("According to the Prose Edda, Odin hung on Yggdrasil for nine days.")
    verdict, confidence, reason = hv.validate(c, [])
    assert verdict == VerdictLabel.ENTAILED
    assert confidence >= 0.8


def test_historical_validator_primary_source_in_chunk_returns_entailed():
    """HistoricalValidator boosts confidence when primary source found in chunks."""
    hv = HistoricalValidator()
    c = _claim("Odin hanged on Yggdrasil for nine days.")
    chunk = _chunk("The Hávamál saga records Odin's ordeal on Yggdrasil.")
    verdict, confidence, reason = hv.validate(c, [chunk])
    assert verdict == VerdictLabel.ENTAILED


def test_historical_validator_generic_returns_neutral():
    """HistoricalValidator.validate() returns NEUTRAL for unconfirmed historical claims."""
    hv = HistoricalValidator()
    c = _claim("Norse explorers visited North America around 1000 CE.")
    verdict, confidence, reason = hv.validate(c, [])
    assert verdict == VerdictLabel.NEUTRAL


def test_historical_validator_never_raises():
    """HistoricalValidator.validate() never raises."""
    hv = HistoricalValidator()
    verdict, confidence, reason = hv.validate(_claim(""), [])
    assert isinstance(verdict, VerdictLabel)


# ─── Tests: SymbolicValidator ─────────────────────────────────────────────────


def test_symbolic_validator_returns_neutral_not_contradicted():
    """SymbolicValidator.validate() always returns NEUTRAL — never CONTRADICTED."""
    sv = SymbolicValidator()
    c = _claim("The raven symbolizes wisdom in Norse tradition.")
    verdict, confidence, reason = sv.validate(c, [])
    assert verdict == VerdictLabel.NEUTRAL
    assert verdict != VerdictLabel.CONTRADICTED


def test_symbolic_validator_confidence_is_reasonable():
    """SymbolicValidator.validate() returns confidence >= 0.5."""
    sv = SymbolicValidator()
    c = _claim("Yggdrasil embodies the cosmos.")
    verdict, confidence, reason = sv.validate(c, [])
    assert confidence >= 0.5


def test_symbolic_validator_reason_mentions_symbolic():
    """SymbolicValidator.validate() reason mentions symbolic/tradition."""
    sv = SymbolicValidator()
    c = _claim("The wolf Fenrir represents chaos.")
    verdict, confidence, reason = sv.validate(c, [])
    assert "symbolic" in reason.lower() or "tradition" in reason.lower()


def test_symbolic_validator_never_raises():
    """SymbolicValidator.validate() never raises."""
    sv = SymbolicValidator()
    verdict, confidence, reason = sv.validate(_claim(""), [])
    assert isinstance(verdict, VerdictLabel)


# ─── Tests: ProceduralValidator ───────────────────────────────────────────────


def test_procedural_validator_step_words_in_claim_and_chunk_returns_entailed():
    """ProceduralValidator returns ENTAILED when step order found in claim and chunk."""
    pv = ProceduralValidator()
    c = _claim("First prepare the offering, then light the fire, finally speak the runes.")
    chunk = _chunk("Begin with an offering, then proceed to the fire ritual, next speak aloud.")
    verdict, confidence, reason = pv.validate(c, [chunk])
    assert verdict == VerdictLabel.ENTAILED


def test_procedural_validator_no_step_words_returns_neutral():
    """ProceduralValidator returns NEUTRAL when no step order words in claim."""
    pv = ProceduralValidator()
    c = _claim("Odin is the Allfather and ruler of Asgard.")
    verdict, confidence, reason = pv.validate(c, [])
    assert verdict == VerdictLabel.NEUTRAL


def test_procedural_validator_step_in_claim_no_chunk_returns_neutral():
    """ProceduralValidator returns NEUTRAL when step words in claim but not confirmed by chunk."""
    pv = ProceduralValidator()
    c = _claim("First invoke the rune, then wait three days.")
    chunk = _chunk("Runes are powerful symbols of the Norse cosmos.")
    verdict, confidence, reason = pv.validate(c, [chunk])
    assert verdict == VerdictLabel.NEUTRAL


def test_procedural_validator_never_raises():
    """ProceduralValidator.validate() never raises."""
    pv = ProceduralValidator()
    verdict, confidence, reason = pv.validate(_claim(""), [])
    assert isinstance(verdict, VerdictLabel)


# ─── Tests: VordurChecker domain validator integration ───────────────────────


def test_verify_claim_uses_domain_validator_for_code_claim():
    """verify_claim() uses CodeValidator for CODE_BEHAVIOR claims (tier = domain:code)."""
    checker = VordurChecker(router=None, verdict_cache_enabled=False)
    c = _claim("def greet(): return 'hello'", claim_type=ClaimType.CODE_BEHAVIOR.value)
    chunks = [_chunk("Python functions return values.")]
    result = checker.verify_claim(c, chunks)
    assert isinstance(result, ClaimVerification)
    assert result.judge_tier_used.startswith("domain:")


def test_verify_claim_uses_domain_validator_for_symbolic_claim():
    """verify_claim() uses SymbolicValidator for SYMBOLIC claims."""
    checker = VordurChecker(router=None, verdict_cache_enabled=False)
    c = _claim("Yggdrasil symbolizes cosmic unity.", claim_type=ClaimType.SYMBOLIC.value)
    chunks = [_chunk("Yggdrasil is the world tree in Norse mythology.")]
    result = checker.verify_claim(c, chunks)
    assert isinstance(result, ClaimVerification)
    assert result.judge_tier_used.startswith("domain:")


def test_verify_claim_factual_skips_domain_validator():
    """verify_claim() does not use domain validator for FACTUAL claims."""
    checker = VordurChecker(router=None, verdict_cache_enabled=False)
    c = _claim("Odin is the Allfather.", claim_type=ClaimType.FACTUAL.value)
    chunks = [_chunk("Odin rules Asgard.")]
    result = checker.verify_claim(c, chunks)
    assert isinstance(result, ClaimVerification)
    # FACTUAL → no domain validator → uses regex tier
    assert not result.judge_tier_used.startswith("domain:")
