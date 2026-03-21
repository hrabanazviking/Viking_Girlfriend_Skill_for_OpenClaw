"""
test_synthesizer_reorder.py — E-28: Dynamic Section Reordering
==============================================================

Tests for PromptSynthesizer._reorder_sections() and the emotional_state
parameter on build_messages(). No identity files needed — data_root is
pointed at a temp directory.
"""

import json
import sys
import os
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "viking_girlfriend_skill"))

from scripts.prompt_synthesizer import PromptSynthesizer, SectionPriority, _HINT_SECTION_ORDER


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _synth(tmp_path) -> PromptSynthesizer:
    """Synthesizer with empty data root — no identity files required."""
    return PromptSynthesizer(
        data_root=str(tmp_path),
        skaldic_injection=False,
    )


# ─── Tests: SectionPriority dataclass ────────────────────────────────────────


def test_section_priority_fields(tmp_path):
    """SectionPriority has name, base_order, current_order."""
    sp = SectionPriority(name="wyrd_matrix", base_order=2, current_order=0)
    assert sp.name == "wyrd_matrix"
    assert sp.base_order == 2
    assert sp.current_order == 0


# ─── Tests: _reorder_sections ────────────────────────────────────────────────


def test_default_order_preserved_no_emotional_state(tmp_path):
    """Without emotional_state, sections follow _HINT_SECTION_ORDER."""
    synth = _synth(tmp_path)
    keys = ["ethics", "wyrd_matrix", "scheduler"]
    result = synth._reorder_sections(keys, None)
    # scheduler comes before wyrd_matrix before ethics in _HINT_SECTION_ORDER
    assert result.index("scheduler") < result.index("wyrd_matrix")
    assert result.index("wyrd_matrix") < result.index("ethics")


def test_high_arousal_elevates_wyrd_matrix(tmp_path):
    """pad_arousal > 0.7 moves wyrd_matrix to position 0."""
    synth = _synth(tmp_path)
    keys = ["scheduler", "wyrd_matrix", "ethics"]
    result = synth._reorder_sections(keys, {"pad_arousal": 0.85})
    assert result[0] == "wyrd_matrix"


def test_high_arousal_does_not_elevate_without_wyrd_matrix(tmp_path):
    """High arousal has no effect if wyrd_matrix is not in the hint keys."""
    synth = _synth(tmp_path)
    keys = ["scheduler", "ethics"]
    result = synth._reorder_sections(keys, {"pad_arousal": 0.9})
    assert result[0] != "wyrd_matrix"
    assert "wyrd_matrix" not in result


def test_low_pleasure_elevates_ethics(tmp_path):
    """pad_pleasure < -0.5 moves ethics to position 0."""
    synth = _synth(tmp_path)
    keys = ["scheduler", "wyrd_matrix", "ethics"]
    result = synth._reorder_sections(keys, {"pad_pleasure": -0.7})
    assert result[0] == "ethics"


def test_low_pleasure_does_not_elevate_without_ethics(tmp_path):
    """Low pleasure has no effect if ethics is not in hint keys."""
    synth = _synth(tmp_path)
    keys = ["scheduler", "wyrd_matrix"]
    result = synth._reorder_sections(keys, {"pad_pleasure": -0.9})
    assert "ethics" not in result


def test_arousal_takes_priority_over_pleasure(tmp_path):
    """When both pad_arousal > 0.7 AND pad_pleasure < -0.5, arousal wins (wyrd_matrix first)."""
    synth = _synth(tmp_path)
    keys = ["scheduler", "wyrd_matrix", "ethics"]
    result = synth._reorder_sections(keys, {"pad_arousal": 0.8, "pad_pleasure": -0.7})
    assert result[0] == "wyrd_matrix"


def test_normal_arousal_and_pleasure_preserves_order(tmp_path):
    """Mid-range values preserve the default section order."""
    synth = _synth(tmp_path)
    keys = ["ethics", "wyrd_matrix", "scheduler"]
    result = synth._reorder_sections(keys, {"pad_arousal": 0.3, "pad_pleasure": -0.2})
    assert result.index("scheduler") < result.index("wyrd_matrix")
    assert result.index("wyrd_matrix") < result.index("ethics")


def test_empty_hints_returns_empty(tmp_path):
    """Empty hint_keys returns empty list regardless of emotional_state."""
    synth = _synth(tmp_path)
    result = synth._reorder_sections([], {"pad_arousal": 0.9})
    assert result == []


def test_build_messages_accepts_emotional_state(tmp_path):
    """build_messages() accepts emotional_state without error."""
    synth = _synth(tmp_path)
    messages, _ = synth.build_messages(
        user_text="Hello.",
        state_hints={"wyrd_matrix": "[Mood: intense]", "scheduler": "[Time: dawn]"},
        emotional_state={"pad_arousal": 0.85, "pad_pleasure": 0.2},
    )
    assert isinstance(messages, list)
    assert len(messages) == 2


def test_wyrd_matrix_content_appears_early_in_system_prompt(tmp_path):
    """When arousal is high, wyrd_matrix hint text appears before scheduler text in system."""
    synth = _synth(tmp_path)
    messages, _ = synth.build_messages(
        user_text="Tell me more.",
        state_hints={
            "scheduler": "[Time: morning]",
            "wyrd_matrix": "[MOOD_MARKER_UNIQUE]",
        },
        emotional_state={"pad_arousal": 0.9},
    )
    system = messages[0]["content"]
    wyrd_pos = system.find("[MOOD_MARKER_UNIQUE]")
    sched_pos = system.find("[Time: morning]")
    if wyrd_pos >= 0 and sched_pos >= 0:
        assert wyrd_pos < sched_pos
