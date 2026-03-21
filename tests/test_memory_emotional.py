"""
tests/test_memory_emotional.py — E-17: Emotional Significance Weighting
10 tests covering pad_arousal/pad_pleasure storage, relevance score boost,
fallback when WyrdMatrix unavailable, and emotional_weight_applied flag.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "viking_girlfriend_skill"))

import pytest
from scripts.memory_store import MemoryEntry, MemoryStore


# ─── MemoryEntry emotional fields ────────────────────────────────────────────

class TestMemoryEntryEmotionalFields:

    def test_default_pad_arousal_is_zero(self):
        e = MemoryEntry(entry_id="x", session_id="s", timestamp="t",
                        memory_type="fact", content="test")
        assert e.pad_arousal == 0.0

    def test_default_pad_pleasure_is_zero(self):
        e = MemoryEntry(entry_id="x", session_id="s", timestamp="t",
                        memory_type="fact", content="test")
        assert e.pad_pleasure == 0.0

    def test_default_emotional_weight_applied_false(self):
        e = MemoryEntry(entry_id="x", session_id="s", timestamp="t",
                        memory_type="fact", content="test")
        assert e.emotional_weight_applied is False

    def test_from_dict_preserves_emotional_fields(self):
        d = {
            "entry_id": "x", "session_id": "s", "timestamp": "t",
            "memory_type": "fact", "content": "test",
            "pad_arousal": 0.8, "pad_pleasure": 0.3, "emotional_weight_applied": True,
        }
        e = MemoryEntry.from_dict(d)
        assert e.pad_arousal == 0.8
        assert e.pad_pleasure == 0.3
        assert e.emotional_weight_applied is True

    def test_from_dict_defaults_missing_emotional_fields(self):
        d = {"entry_id": "x", "session_id": "s", "timestamp": "t",
             "memory_type": "fact", "content": "test"}
        e = MemoryEntry.from_dict(d)
        assert e.pad_arousal == 0.0
        assert e.emotional_weight_applied is False


# ─── relevance_score emotional boost ─────────────────────────────────────────

class TestRelevanceScoreBoost:

    def _entry_with_arousal(self, arousal: float) -> MemoryEntry:
        return MemoryEntry(
            entry_id="x", session_id="s", timestamp="t",
            memory_type="fact", content="rune Odin magic",
            pad_arousal=arousal,
        )

    def test_high_arousal_scores_higher_than_low(self):
        high = self._entry_with_arousal(1.0)
        low = self._entry_with_arousal(0.0)
        words = {"rune", "Odin"}
        assert high.relevance_score(words) > low.relevance_score(words)

    def test_zero_arousal_no_boost(self):
        e = self._entry_with_arousal(0.0)
        words = {"rune"}
        score_zero = e.relevance_score(words)
        # High arousal should score higher for the same content and query
        e_high = self._entry_with_arousal(1.0)
        score_high = e_high.relevance_score(words)
        # Zero arousal multiplier is 1.0, high arousal is 1.3 — ratio must hold
        assert abs(score_high / score_zero - 1.3) < 0.001

    def test_max_arousal_boost_30_percent(self):
        low = self._entry_with_arousal(0.0)
        high = self._entry_with_arousal(1.0)
        words = {"rune"}
        ratio = high.relevance_score(words) / low.relevance_score(words)
        assert abs(ratio - 1.3) < 0.001


# ─── MemoryStore.add_memory fallback ─────────────────────────────────────────

class TestAddMemoryEmotionalFallback:

    def test_add_memory_without_wyrd_uses_fallback(self, tmp_path):
        # WyrdMatrix not initialised — should use fallback 0.5
        store = MemoryStore(data_root=str(tmp_path), semantic_enabled=False)
        entry = store.add_memory("some memory", memory_type="fact")
        # Fallback arousal is 0.5; emotional_weight_applied stays False
        assert entry.pad_arousal == 0.5
        assert entry.emotional_weight_applied is False

    def test_add_memory_persists_emotional_fields(self, tmp_path):
        store = MemoryStore(data_root=str(tmp_path), semantic_enabled=False)
        entry = store.add_memory("another memory", memory_type="fact")
        # Reload store and check the entry was persisted with arousal
        store2 = MemoryStore(data_root=str(tmp_path), semantic_enabled=False)
        loaded = store2._episodic.get_recent(n=1)
        assert len(loaded) == 1
        assert loaded[0].pad_arousal == 0.5
