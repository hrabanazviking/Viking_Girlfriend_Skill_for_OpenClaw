"""
test_synthesizer_skaldic.py — E-29: Skaldic Vocabulary Injection
================================================================

Tests for PromptSynthesizer._inject_skaldic_flavor(), _load_skaldic_vocab(),
and the skaldic_injection flag. Uses a minimal synthetic vocabulary JSON.
"""

import json
import sys
import os
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "viking_girlfriend_skill"))

from scripts.prompt_synthesizer import PromptSynthesizer


# ─── Helpers ──────────────────────────────────────────────────────────────────


_SMALL_VOCAB = [
    {"word": "wyrd", "meaning": "fate", "context_tags": ["fate", "spirit"], "usage_example": "Her wyrd was written."},
    {"word": "skald", "meaning": "Norse poet", "context_tags": ["general", "honor"], "usage_example": "The skald sang."},
    {"word": "hamingja", "meaning": "luck-spirit", "context_tags": ["spirit", "emotion"], "usage_example": "Her hamingja shone."},
    {"word": "frith", "meaning": "sacred peace", "context_tags": ["honor", "duty"], "usage_example": "Frith binds the kin."},
    {"word": "seiðr", "meaning": "Norse magic", "context_tags": ["mystery", "spirit"], "usage_example": "She wove seiðr."},
    {"word": "galdr", "meaning": "runic chant", "context_tags": ["mystery", "fate"], "usage_example": "Galdr rose at dawn."},
    {"word": "hugr", "meaning": "mind-spirit", "context_tags": ["thought", "spirit"], "usage_example": "Her hugr wandered far."},
    {"word": "Yggdrasil", "meaning": "world-tree", "context_tags": ["nature", "spirit"], "usage_example": "Yggdrasil holds all realms."},
    {"word": "völva", "meaning": "seeress", "context_tags": ["mystery", "spirit"], "usage_example": "The völva spoke true."},
    {"word": "mjolnir", "meaning": "Thor's hammer", "context_tags": ["honor", "general"], "usage_example": "By Mjolnir, we swore."},
]


def _synth_with_vocab(tmp_path, injection: bool = True) -> PromptSynthesizer:
    """Synthesizer with small test vocabulary written to tmp_path."""
    vocab_file = tmp_path / "skaldic_vocabulary.json"
    vocab_file.write_text(json.dumps(_SMALL_VOCAB), encoding="utf-8")
    return PromptSynthesizer(
        data_root=str(tmp_path),
        skaldic_injection=injection,
        skaldic_vocab_file="skaldic_vocabulary.json",
    )


# ─── Tests: vocab loading ─────────────────────────────────────────────────────


def test_load_skaldic_vocab_reads_entries(tmp_path):
    """_load_skaldic_vocab loads all entries from the JSON file."""
    synth = _synth_with_vocab(tmp_path)
    assert len(synth._skaldic_vocab) == len(_SMALL_VOCAB)


def test_load_skaldic_vocab_missing_file_returns_empty(tmp_path):
    """Missing vocab file → _skaldic_vocab is empty list, no crash."""
    synth = PromptSynthesizer(
        data_root=str(tmp_path),
        skaldic_injection=True,
        skaldic_vocab_file="nonexistent.json",
    )
    assert synth._skaldic_vocab == []


# ─── Tests: injection logic ──────────────────────────────────────────────────


def test_inject_skaldic_flavor_returns_string(tmp_path):
    """_inject_skaldic_flavor returns a non-empty string with vocab loaded."""
    synth = _synth_with_vocab(tmp_path)
    line = synth._inject_skaldic_flavor(1, {"wyrd_matrix": "[Mood]"})
    assert isinstance(line, str)
    assert len(line) > 0


def test_inject_skaldic_flavor_contains_prefix(tmp_path):
    """Injected line starts with the '[Skaldic Voice]' prefix."""
    synth = _synth_with_vocab(tmp_path)
    line = synth._inject_skaldic_flavor(3, {})
    assert line.startswith("[Skaldic Voice] Weave these into your voice today:")


def test_inject_skaldic_deterministic_per_turn(tmp_path):
    """Same turn_id and same hints always produce the same line."""
    synth = _synth_with_vocab(tmp_path)
    line1 = synth._inject_skaldic_flavor(5, {"oracle": "[Mystery]"})
    line2 = synth._inject_skaldic_flavor(5, {"oracle": "[Mystery]"})
    assert line1 == line2


def test_inject_skaldic_different_turns_differ(tmp_path):
    """Different turn IDs produce different lines when the pool is large enough."""
    synth = _synth_with_vocab(tmp_path)
    # Use wyrd_matrix hint to get spirit/emotion/fate tags → 7-entry pool
    hints = {"wyrd_matrix": "[Mood]"}
    line1 = synth._inject_skaldic_flavor(1, hints)
    line2 = synth._inject_skaldic_flavor(7, hints)
    # With 7-entry pool: turn 1 → idx1=0 (wyrd), idx2=4 (hugr)
    #                    turn 7 → idx1=0 (wyrd), idx2=5 (Yggdrasil) — idx2 differs
    assert line1 != line2


def test_injection_disabled_flag(tmp_path):
    """skaldic_injection=False → _inject_skaldic_flavor not called / no line in prompt."""
    synth = _synth_with_vocab(tmp_path, injection=False)
    messages, _ = synth.build_messages(
        user_text="Hello.",
        state_hints={"wyrd_matrix": "[Mood]"},
    )
    system = messages[0]["content"]
    assert "[Skaldic Voice]" not in system


def test_injection_appears_in_system_prompt(tmp_path):
    """With injection enabled, system prompt contains '[Skaldic Voice]' line."""
    synth = _synth_with_vocab(tmp_path, injection=True)
    messages, _ = synth.build_messages(user_text="Hello.")
    system = messages[0]["content"]
    assert "[Skaldic Voice]" in system


def test_turn_counter_increments_each_build(tmp_path):
    """_turn_counter increments on every build_messages() call."""
    synth = _synth_with_vocab(tmp_path)
    assert synth._turn_counter == 0
    synth.build_messages(user_text="first")
    assert synth._turn_counter == 1
    synth.build_messages(user_text="second")
    assert synth._turn_counter == 2


def test_context_tags_influence_selection(tmp_path):
    """wyrd_matrix hint triggers emotion/spirit/fate tags → matched entries preferred."""
    synth = _synth_with_vocab(tmp_path)
    # spirit/fate-tagged words: wyrd, hamingja, seiðr, galdr, hugr, Yggdrasil, völva
    line = synth._inject_skaldic_flavor(0, {"wyrd_matrix": "[Mood: intense]"})
    spirit_words = {e["word"] for e in _SMALL_VOCAB if {"emotion", "spirit", "fate"} & set(e["context_tags"])}
    # At least one selected word should be from the spirit/emotion/fate set
    assert any(w in line for w in spirit_words)
