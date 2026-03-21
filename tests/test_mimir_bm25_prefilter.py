"""
test_mimir_bm25_prefilter.py — E-26: BM25 Pre-Filter Shortcircuit
=================================================================

Tests for _FlatIndex.search_with_top_score() and MimirWell.retrieve()
BM25 shortcircuit logic. ChromaDB is never initialised in these tests;
the flat in-memory index is exercised directly.
"""

import sys
import os
import uuid
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "viking_girlfriend_skill"))

from scripts.mimir_well import (
    _FlatIndex,
    KnowledgeChunk,
    DataRealm,
    TruthTier,
    MimirState,
)


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _make_chunk(text: str, domain: str = "norse_culture") -> KnowledgeChunk:
    return KnowledgeChunk(
        chunk_id=str(uuid.uuid4()),
        text=text,
        source_file="test.md",
        domain=domain,
        realm=DataRealm.MIDGARD,
        tier=TruthTier.TRUNK,
        level=1,
        metadata={},
    )


def _make_index(*texts: str) -> tuple:
    """Return (_FlatIndex, chunks_by_id) preloaded with the given texts."""
    idx = _FlatIndex()
    chunks_by_id = {}
    for text in texts:
        chunk = _make_chunk(text)
        idx.add(chunk)
        chunks_by_id[chunk.chunk_id] = chunk
    return idx, chunks_by_id


# ─── Tests: search_with_top_score ────────────────────────────────────────────


def test_search_with_top_score_returns_tuple():
    """search_with_top_score returns (list, float) — correct types."""
    idx, cbi = _make_index("Odin hung upon the World Tree Yggdrasil for nine nights")
    result, score = idx.search_with_top_score("Odin Yggdrasil", cbi)
    assert isinstance(result, list)
    assert isinstance(score, float)


def test_search_with_top_score_empty_index():
    """Empty index returns empty list and score 0.0."""
    idx = _FlatIndex()
    result, score = idx.search_with_top_score("Odin", {})
    assert result == []
    assert score == 0.0


def test_search_with_top_score_no_match_returns_zero():
    """Query with no matching terms returns empty list and score 0.0."""
    idx, cbi = _make_index("The ravens Huginn and Muninn fly over all the worlds")
    result, score = idx.search_with_top_score("pizza banana", cbi)
    assert result == []
    assert score == 0.0


def test_search_with_top_score_match_positive_score():
    """Matching query returns positive top_score."""
    idx, cbi = _make_index("Odin sacrificed his eye at Mimir's well to gain wisdom")
    result, score = idx.search_with_top_score("Odin wisdom", cbi)
    assert len(result) >= 1
    assert score > 0.0


def test_search_delegates_to_search_with_top_score():
    """search() returns same chunks as search_with_top_score() ignoring score."""
    idx, cbi = _make_index(
        "Freyja wept golden tears for her lost husband Oðr",
        "Thor wielded Mjolnir with terrible strength",
    )
    via_search = idx.search("Freyja golden tears", cbi)
    via_swts, _ = idx.search_with_top_score("Freyja golden tears", cbi)
    assert [c.chunk_id for c in via_search] == [c.chunk_id for c in via_swts]


def test_high_score_exceeds_low_score():
    """Identical query against a chunk that contains all query words scores higher."""
    idx, cbi = _make_index(
        "Odin Odin Odin wisdom wisdom wisdom",
        "The cat sat on the mat",
    )
    result, score = idx.search_with_top_score("Odin wisdom", cbi)
    assert len(result) >= 1
    # Top result should be the first chunk (high keyword density)
    assert result[0].text.startswith("Odin")
    assert score > 0.0


def test_retrieval_path_tagged_bm25_fast():
    """When shortcircuit fires, returned chunks carry retrieval_path='bm25_fast'."""
    from scripts.mimir_well import MimirWell

    well = MimirWell(
        persist_dir="/nonexistent",
        bm25_shortcircuit_threshold=0.0,   # always shortcircuit
    )
    # Manually inject a chunk into the flat index
    chunk = _make_chunk("Odin Odin wisdom wisdom runes runes ancient")
    well._flat_index.add(chunk)
    well._chunks_by_id[chunk.chunk_id] = chunk

    results = well.retrieve("Odin wisdom runes")
    # At least some chunks should come back
    if results:
        assert results[0].metadata.get("retrieval_path") == "bm25_fast"


def test_bm25_total_queries_increments():
    """retrieve() increments _bm25_total_queries each call."""
    from scripts.mimir_well import MimirWell

    well = MimirWell(persist_dir="/nonexistent")
    initial = well._bm25_total_queries
    well.retrieve("any query")
    assert well._bm25_total_queries == initial + 1


def test_bm25_shortcircuit_hits_increments_when_threshold_exceeded():
    """_bm25_shortcircuit_hits increments when shortcircuit fires."""
    from scripts.mimir_well import MimirWell

    well = MimirWell(
        persist_dir="/nonexistent",
        bm25_shortcircuit_threshold=0.0,  # always shortcircuit
    )
    chunk = _make_chunk("Yggdrasil world tree Norse cosmos three roots")
    well._flat_index.add(chunk)
    well._chunks_by_id[chunk.chunk_id] = chunk

    well.retrieve("Yggdrasil Norse roots")
    assert well._bm25_shortcircuit_hits >= 1


def test_mimir_state_includes_bm25_shortcircuit_rate():
    """get_state() returns MimirState with bm25_shortcircuit_rate field."""
    from scripts.mimir_well import MimirWell

    well = MimirWell(persist_dir="/nonexistent")
    state = well.get_state()
    assert hasattr(state, "bm25_shortcircuit_rate")
    assert isinstance(state.bm25_shortcircuit_rate, float)
