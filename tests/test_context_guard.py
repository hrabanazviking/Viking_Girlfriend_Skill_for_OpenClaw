"""
test_context_guard.py — S-04 + S-05: Hard token cap and soul anchor re-injection
==================================================================================

Tests for:
  - _truncate_to_token_cap()  (S-04)
  - _build_soul_anchor_block() (S-05)
  - overflow detection and soul re-injection in build_messages() (S-05)
  - new constructor params
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "viking_girlfriend_skill"))

from scripts.prompt_synthesizer import (
    PromptSynthesizer,
    _DEFAULT_MAX_CONTEXT_TOKENS,
    _DEFAULT_OVERFLOW_THRESHOLD_RATIO,
    _SOUL_ANCHOR_IDENTITY_CHARS,
    _SOUL_ANCHOR_SOUL_CHARS,
)


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _synth(**kwargs) -> PromptSynthesizer:
    """Build a minimal PromptSynthesizer with test data root."""
    defaults = dict(
        data_root=str(Path(__file__).resolve().parents[1] / "viking_girlfriend_skill" / "data"),
    )
    defaults.update(kwargs)
    return PromptSynthesizer(**defaults)


# ─── Tests: new constructor params ───────────────────────────────────────────


def test_default_max_context_tokens():
    """Default max_context_tokens is _DEFAULT_MAX_CONTEXT_TOKENS."""
    synth = _synth()
    assert synth._max_context_tokens == _DEFAULT_MAX_CONTEXT_TOKENS


def test_custom_max_context_tokens():
    """Custom max_context_tokens stored correctly."""
    synth = _synth(max_context_tokens=50000)
    assert synth._max_context_tokens == 50000


def test_default_overflow_threshold_ratio():
    """Default overflow_threshold_ratio is _DEFAULT_OVERFLOW_THRESHOLD_RATIO."""
    synth = _synth()
    assert synth._overflow_threshold_ratio == _DEFAULT_OVERFLOW_THRESHOLD_RATIO


def test_soul_anchor_enabled_default_true():
    """soul_anchor_enabled defaults to True."""
    synth = _synth()
    assert synth._soul_anchor_enabled is True


def test_soul_anchor_enabled_can_be_disabled():
    """soul_anchor_enabled can be set to False."""
    synth = _synth(soul_anchor_enabled=False)
    assert synth._soul_anchor_enabled is False


# ─── Tests: _truncate_to_token_cap() ──────────────────────────────────────────


def test_truncate_returns_text_when_under_cap():
    """_truncate_to_token_cap() returns unchanged text when already under budget."""
    synth = _synth()
    short = "Short text."
    result = synth._truncate_to_token_cap(short, max_tokens=1000)
    assert result == short


def test_truncate_reduces_long_text():
    """_truncate_to_token_cap() reduces text that exceeds the cap."""
    synth = _synth()
    long_text = "word " * 5000  # ~5000 tokens worth of words
    result = synth._truncate_to_token_cap(long_text, max_tokens=100)
    assert len(result) < len(long_text)


def test_truncated_text_is_under_cap():
    """After _truncate_to_token_cap(), token count is at or under max_tokens."""
    synth = _synth()
    long_text = "word " * 3000
    max_toks = 200
    result = synth._truncate_to_token_cap(long_text, max_tokens=max_toks)
    actual_tokens = synth._count_tokens(result)
    assert actual_tokens <= max_toks


def test_truncate_never_raises():
    """_truncate_to_token_cap() never raises even on edge cases."""
    synth = _synth()
    assert synth._truncate_to_token_cap("", 0) == ""
    assert isinstance(synth._truncate_to_token_cap("x" * 10000, 1), str)


# ─── Tests: _build_soul_anchor_block() ────────────────────────────────────────


def test_soul_anchor_block_returns_non_empty_when_identity_loaded():
    """_build_soul_anchor_block() returns non-empty string if identity text is loaded."""
    synth = _synth()
    if not synth._identity_text:
        pytest.skip("Identity text not loaded — no test data available")
    anchor = synth._build_soul_anchor_block()
    assert isinstance(anchor, str)
    assert len(anchor) > 0


def test_soul_anchor_block_under_size_limit():
    """Soul anchor block is under the sum of the two char limits plus markup."""
    synth = _synth()
    synth._identity_text = "A" * 2000
    synth._soul_text = "B" * 1000
    anchor = synth._build_soul_anchor_block()
    # Should only take first _SOUL_ANCHOR_IDENTITY_CHARS + _SOUL_ANCHOR_SOUL_CHARS chars
    expected_max = _SOUL_ANCHOR_IDENTITY_CHARS + _SOUL_ANCHOR_SOUL_CHARS + 200  # +200 for labels
    assert len(anchor) <= expected_max


def test_soul_anchor_block_contains_identity_content():
    """Soul anchor block contains content from identity text."""
    synth = _synth()
    synth._identity_text = "IDENTITY_MARKER_UNIQUE_STRING " * 10
    anchor = synth._build_soul_anchor_block()
    assert "IDENTITY_MARKER_UNIQUE_STRING" in anchor


def test_soul_anchor_block_never_raises():
    """_build_soul_anchor_block() never raises even with empty texts."""
    synth = _synth()
    synth._identity_text = ""
    synth._soul_text = ""
    result = synth._build_soul_anchor_block()
    assert isinstance(result, str)


# ─── Tests: build_messages() context guard integration ────────────────────────


def test_build_messages_normal_prompt_unchanged():
    """Normal-sized prompts are returned unchanged (no overflow action)."""
    synth = _synth()
    messages, mode = synth.build_messages("Hello Sigrid!")
    assert len(messages) == 2
    assert messages[0]["role"] == "system"


def test_build_messages_overflow_triggers_truncation():
    """When system content exceeds max_context_tokens, it is truncated."""
    synth = _synth(max_context_tokens=10)  # tiny cap to force truncation
    # With max=10 tokens and actual content being much larger, truncation fires
    messages, mode = synth.build_messages("Hi!")
    # The system content should have been truncated — just verify no crash
    assert messages[0]["role"] == "system"
    assert isinstance(messages[0]["content"], str)


def test_build_messages_never_raises_at_tiny_cap():
    """build_messages() never raises even with a tiny max_context_tokens."""
    synth = _synth(max_context_tokens=1)
    try:
        messages, mode = synth.build_messages("Test")
    except Exception as exc:
        pytest.fail(f"build_messages raised: {exc}")
