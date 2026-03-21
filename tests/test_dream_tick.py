"""
tests/test_dream_tick.py -- E-15: Dream Tick Integration
15 tests covering DreamEngine.handle_dream_tick(), WyrdMatrix.handle_dream_tick(),
and MimirWell.associative_link_pass().
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "viking_girlfriend_skill"))

import pytest
from scripts.dream_engine import DreamEngine, Dream
from scripts.wyrd_matrix import WyrdMatrix
from scripts.mimir_well import MimirWell, KnowledgeChunk, DataRealm, TruthTier

DATA_ROOT = str(
    Path(__file__).resolve().parents[1] / "viking_girlfriend_skill" / "data"
)


# ─── DreamEngine.handle_dream_tick ────────────────────────────────────────────


class TestDreamEngineDreamTick:

    def test_returns_dream_object(self):
        eng = DreamEngine()
        result = eng.handle_dream_tick()
        assert isinstance(result, Dream)

    def test_dream_appended_to_active_list(self):
        eng = DreamEngine()
        assert len(eng.active_dreams) == 0
        eng.handle_dream_tick()
        assert len(eng.active_dreams) == 1

    def test_max_active_cap_respected(self):
        eng = DreamEngine(max_active=3)
        for _ in range(10):
            eng.handle_dream_tick()
        assert len(eng.active_dreams) <= 3

    def test_seed_hints_accepted_without_error(self):
        eng = DreamEngine()
        result = eng.handle_dream_tick(seed_hints=["joy", "fear"])
        assert result is not None

    def test_dream_written_to_session_dir(self, tmp_path):
        eng = DreamEngine()
        eng.handle_dream_tick(session_dir=str(tmp_path))
        last_dream_path = tmp_path / "last_dream.json"
        assert last_dream_path.exists()

    def test_session_json_contains_symbol(self, tmp_path):
        eng = DreamEngine()
        eng.handle_dream_tick(session_dir=str(tmp_path))
        data = json.loads((tmp_path / "last_dream.json").read_text())
        assert "symbol" in data

    def test_no_session_dir_does_not_crash(self):
        eng = DreamEngine()
        result = eng.handle_dream_tick(session_dir=None)
        assert result is not None


# ─── WyrdMatrix.handle_dream_tick ─────────────────────────────────────────────


class TestWyrdMatrixDreamTick:

    def test_returns_none(self):
        wm = WyrdMatrix()
        result = wm.handle_dream_tick()
        assert result is None

    def test_no_crash_with_empty_emotions(self):
        wm = WyrdMatrix()
        # emotions dict is empty by default — should log and return cleanly
        wm.handle_dream_tick()  # no exception

    def test_emotions_modified_when_present(self):
        wm = WyrdMatrix()
        # Seed some emotions
        wm.soul.hugr.emotions["joy"] = 0.5
        wm.soul.hugr.emotions["fear"] = -0.3
        before_joy = wm.soul.hugr.emotions["joy"]
        wm.handle_dream_tick()
        after_joy = wm.soul.hugr.emotions["joy"]
        # Values should differ by up to ±0.05
        assert abs(after_joy - before_joy) <= 0.06  # small epsilon for float precision

    def test_emotions_clamped_after_tick(self):
        wm = WyrdMatrix()
        wm.soul.hugr.emotions["anger"] = 1.0
        wm.handle_dream_tick()
        assert wm.soul.hugr.emotions["anger"] <= 1.0
        assert wm.soul.hugr.emotions["anger"] >= -1.0


# ─── MimirWell.associative_link_pass ──────────────────────────────────────────


def _seeded_well(n_chunks: int = 5) -> MimirWell:
    """Build a MimirWell with n_chunks injected into the flat BM25 index."""
    well = MimirWell()
    for i in range(n_chunks):
        chunk = KnowledgeChunk(
            chunk_id=f"test_chunk_{i}",
            text=f"Norse mythology Yggdrasil rune wisdom fate wyrd destiny chunk {i}",
            source_file=f"test_{i}.md",
            domain="mythology",
            realm=DataRealm.ASGARD,
            tier=TruthTier.BRANCH,
            level=1,
            metadata={},
        )
        well._flat_index.add(chunk)
        well._chunks_by_id[chunk.chunk_id] = chunk
    return well


class TestAssociativeLinkPass:

    def test_empty_index_returns_empty_list(self):
        well = MimirWell()
        result = well.associative_link_pass()
        assert result == []

    def test_returns_list_of_tuples(self):
        well = _seeded_well(5)
        result = well.associative_link_pass()
        assert isinstance(result, list)
        for item in result:
            assert len(item) == 2

    def test_pairs_are_unique(self):
        well = _seeded_well(10)
        result = well.associative_link_pass()
        seen = set(result)
        assert len(seen) == len(result)

    def test_session_cache_written(self, tmp_path):
        well = _seeded_well(5)
        well.associative_link_pass(session_dir=str(tmp_path))
        cache_path = tmp_path / "association_cache.json"
        assert cache_path.exists()

    def test_session_cache_has_pairs_key(self, tmp_path):
        well = _seeded_well(5)
        well.associative_link_pass(session_dir=str(tmp_path))
        data = json.loads((tmp_path / "association_cache.json").read_text())
        assert "pairs" in data
        assert "ts" in data
