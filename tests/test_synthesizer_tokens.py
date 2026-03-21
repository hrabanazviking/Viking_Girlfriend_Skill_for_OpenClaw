"""
test_synthesizer_tokens.py — E-30: Actual Token Counting
=========================================================

Tests for PromptSynthesizer._count_tokens(). Covers:
- Fallback mode (litellm absent / raises → len//4)
- Fallback mode flag tracks state
- litellm path (mocked) returns int
- Token estimate logged during build_messages()
"""

import sys
import os
import importlib
from pathlib import Path
from unittest import mock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "viking_girlfriend_skill"))

from scripts.prompt_synthesizer import PromptSynthesizer


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _synth(tmp_path) -> PromptSynthesizer:
    return PromptSynthesizer(
        data_root=str(tmp_path),
        skaldic_injection=False,
    )


# ─── Tests: fallback path ────────────────────────────────────────────────────


def test_count_tokens_fallback_returns_len_over_four(tmp_path):
    """When litellm is unavailable, _count_tokens returns len(text)//4."""
    synth = _synth(tmp_path)
    text = "a" * 400  # 400 chars → 100 tokens in fallback mode
    with mock.patch.dict("sys.modules", {"litellm": None}):
        count = synth._count_tokens(text)
    assert count == 100


def test_count_tokens_fallback_for_short_string(tmp_path):
    """Fallback handles short strings correctly."""
    synth = _synth(tmp_path)
    with mock.patch.dict("sys.modules", {"litellm": None}):
        count = synth._count_tokens("Hi!")
    assert count == len("Hi!") // 4  # 0


def test_count_tokens_fallback_sets_flag(tmp_path):
    """First fallback call sets _token_count_fallback = True."""
    synth = _synth(tmp_path)
    assert synth._token_count_fallback is False
    with mock.patch.dict("sys.modules", {"litellm": None}):
        synth._count_tokens("test text here")
    assert synth._token_count_fallback is True


def test_count_tokens_litellm_available_returns_int(tmp_path):
    """When litellm.token_counter is available, its int result is returned."""
    synth = _synth(tmp_path)
    mock_litellm = mock.MagicMock()
    mock_litellm.token_counter.return_value = 42
    with mock.patch.dict("sys.modules", {"litellm": mock_litellm}):
        count = synth._count_tokens("Some text of moderate length here.")
    assert count == 42


def test_count_tokens_litellm_raises_falls_back(tmp_path):
    """If litellm.token_counter raises, falls back to len//4."""
    synth = _synth(tmp_path)
    mock_litellm = mock.MagicMock()
    mock_litellm.token_counter.side_effect = RuntimeError("model not found")
    text = "x" * 80  # 80 chars → 20 tokens fallback
    with mock.patch.dict("sys.modules", {"litellm": mock_litellm}):
        count = synth._count_tokens(text)
    assert count == 20


def test_count_tokens_returns_int_not_float(tmp_path):
    """Return type is always int."""
    synth = _synth(tmp_path)
    with mock.patch.dict("sys.modules", {"litellm": None}):
        result = synth._count_tokens("hello world")
    assert isinstance(result, int)


def test_build_messages_logs_token_estimate(tmp_path, caplog):
    """build_messages() logs a DEBUG message containing token estimate."""
    import logging
    synth = _synth(tmp_path)
    with caplog.at_level(logging.DEBUG, logger="scripts.prompt_synthesizer"):
        synth.build_messages(user_text="Hello Sigrid!")
    # Check that at least one log record mentions "tokens" or "chars"
    messages_text = " ".join(r.message for r in caplog.records)
    assert "token" in messages_text.lower() or "chars" in messages_text.lower()


def test_fallback_flag_cleared_when_litellm_recovers(tmp_path):
    """If litellm fails then succeeds, _token_count_fallback resets to False."""
    synth = _synth(tmp_path)
    # First: force fallback
    with mock.patch.dict("sys.modules", {"litellm": None}):
        synth._count_tokens("trigger fallback mode")
    assert synth._token_count_fallback is True

    # Now: litellm available
    mock_litellm = mock.MagicMock()
    mock_litellm.token_counter.return_value = 10
    with mock.patch.dict("sys.modules", {"litellm": mock_litellm}):
        synth._count_tokens("now litellm works")
    assert synth._token_count_fallback is False
