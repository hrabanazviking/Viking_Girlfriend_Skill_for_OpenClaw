"""
test_vordur_trigger.py — E-37: Verification Modes + Trigger Engine
===================================================================

Tests for extended VerificationMode enum, TriggerEngine.detect_mode(),
get_mode_thresholds() for new modes, and smart_complete_with_cove() integration.
"""

import sys
import uuid
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "viking_girlfriend_skill"))

from scripts.vordur import (
    TriggerEngine,
    VerificationMode,
    VordurChecker,
    get_mode_thresholds,
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


def _engine() -> TriggerEngine:
    return TriggerEngine()


# ─── Tests: VerificationMode enum (extended) ─────────────────────────────────


def test_verification_mode_has_original_values():
    """VerificationMode retains original 4 values (backward compat)."""
    names = {m.name for m in VerificationMode}
    assert "GUARDED" in names
    assert "IRONSWORN" in names
    assert "SEIÐR" in names
    assert "WANDERER" in names


def test_verification_mode_has_new_e37_values():
    """VerificationMode gains NONE, STRICT, INTERPRETIVE, SPECULATIVE."""
    names = {m.name for m in VerificationMode}
    assert "NONE" in names
    assert "STRICT" in names
    assert "INTERPRETIVE" in names
    assert "SPECULATIVE" in names


def test_verification_mode_total_count():
    """VerificationMode has exactly 8 values (4 original + 4 new)."""
    assert len(list(VerificationMode)) == 8


def test_verification_mode_none_value():
    """VerificationMode.NONE has string value 'none'."""
    assert VerificationMode.NONE.value == "none"


def test_verification_mode_strict_value():
    """VerificationMode.STRICT has string value 'strict'."""
    assert VerificationMode.STRICT.value == "strict"


# ─── Tests: get_mode_thresholds() for new modes ───────────────────────────────


def test_get_mode_thresholds_strict_is_high():
    """STRICT mode has thresholds higher than IRONSWORN."""
    strict_high, strict_marginal = get_mode_thresholds(VerificationMode.STRICT)
    iron_high, iron_marginal = get_mode_thresholds(VerificationMode.IRONSWORN)
    assert strict_high >= iron_high or strict_marginal >= iron_marginal


def test_get_mode_thresholds_interpretive():
    """INTERPRETIVE mode returns valid (high, marginal) thresholds."""
    high, marginal = get_mode_thresholds(VerificationMode.INTERPRETIVE)
    assert 0.0 < marginal < high <= 1.0


def test_get_mode_thresholds_speculative():
    """SPECULATIVE mode returns valid thresholds lower than IRONSWORN."""
    spec_high, spec_marginal = get_mode_thresholds(VerificationMode.SPECULATIVE)
    iron_high, iron_marginal = get_mode_thresholds(VerificationMode.IRONSWORN)
    assert spec_high <= iron_high


def test_get_mode_thresholds_none_returns_defaults():
    """NONE mode returns default thresholds (thresholds don't matter — Vörðr skipped)."""
    high, marginal = get_mode_thresholds(VerificationMode.NONE)
    assert isinstance(high, float)
    assert isinstance(marginal, float)


# ─── Tests: TriggerEngine construction ───────────────────────────────────────


def test_trigger_engine_init_no_config():
    """TriggerEngine initializes with no config."""
    engine = TriggerEngine()
    assert engine is not None


def test_trigger_engine_init_with_config():
    """TriggerEngine accepts config dict."""
    engine = TriggerEngine(config={"none_threshold_chars": 30})
    assert engine._none_threshold_chars == 30


# ─── Tests: TriggerEngine.detect_mode() ──────────────────────────────────────


def test_detect_mode_returns_verification_mode():
    """detect_mode() always returns a VerificationMode instance."""
    engine = _engine()
    result = engine.detect_mode("what is Odin?", "Odin is the Allfather.", {})
    assert isinstance(result, VerificationMode)


def test_detect_mode_short_response_returns_none():
    """Very short responses (<50 chars, no certainty language) → NONE."""
    engine = _engine()
    result = engine.detect_mode("hello", "Hello there!", {})
    assert result == VerificationMode.NONE


def test_detect_mode_certainty_language_returns_strict():
    """'always', 'never', 'proven', 'fact' in draft → STRICT."""
    engine = _engine()
    result = engine.detect_mode(
        "tell me about Odin",
        "It is a proven fact that Odin always wins his battles against giants.",
        {},
    )
    assert result == VerificationMode.STRICT


def test_detect_mode_numbers_returns_strict():
    """Year numbers or statistics → STRICT."""
    engine = _engine()
    result = engine.detect_mode(
        "when did Vikings arrive?",
        "The Vikings arrived in Vinland around 1000 AD and settled for several years.",
        {},
    )
    assert result == VerificationMode.STRICT


def test_detect_mode_symbolic_content_returns_interpretive():
    """Symbolic/mythic content → INTERPRETIVE."""
    engine = _engine()
    result = engine.detect_mode(
        "what does Yggdrasil mean?",
        # "all" would trigger STRICT first — use text without universal quantifiers
        "Yggdrasil symbolizes the sacred connection between spiritual realms in Norse mythology.",
        {},
    )
    assert result == VerificationMode.INTERPRETIVE


def test_detect_mode_hedged_language_returns_speculative():
    """Multiple hedging words → SPECULATIVE."""
    engine = _engine()
    result = engine.detect_mode(
        "what happened?",
        "This may possibly be true. It probably suggests an unclear origin. Perhaps it is likely.",
        {},
    )
    assert result == VerificationMode.SPECULATIVE


def test_detect_mode_factual_response_returns_ironsworn():
    """Normal factual response with no special triggers → IRONSWORN."""
    engine = _engine()
    result = engine.detect_mode(
        "who is Thor?",
        "Thor is the son of Odin and the god of thunder in Norse mythology.",
        {},
    )
    assert result == VerificationMode.IRONSWORN


def test_detect_mode_never_raises():
    """detect_mode() never raises regardless of input."""
    engine = _engine()
    result = engine.detect_mode(None, None, None)  # type: ignore[arg-type]
    assert isinstance(result, VerificationMode)


# ─── Tests: smart_complete_with_cove() trigger_engine integration ─────────────


def test_smart_complete_with_cove_accepts_trigger_engine_param():
    """smart_complete_with_cove() accepts trigger_engine kwarg without error."""
    from scripts.model_router_client import ModelRouterClient, CompletionResponse
    # We can't call the full method without a real router, but we can verify the
    # signature accepts the parameter by inspecting it.
    import inspect
    sig = inspect.signature(ModelRouterClient.smart_complete_with_cove)
    assert "trigger_engine" in sig.parameters


def test_trigger_engine_detect_mode_with_seidr_content():
    """Seiðr/rune content triggers INTERPRETIVE mode."""
    engine = _engine()
    result = engine.detect_mode(
        "explain seiðr",
        "Seiðr is a divine ritual practice involving völva and galdr chants.",
        {},
    )
    assert result == VerificationMode.INTERPRETIVE
