"""
tests/test_memory_synonyms.py — E-18: Synonym Expansion in Relevance Scoring
12 tests covering synonym loading, _expand_query, keyword_search hits,
no-synonym fallback, hot-reload, and case-insensitive matching.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "viking_girlfriend_skill"))

import pytest
from scripts.memory_store import EpisodicStore, MemoryEntry, MemoryStore


def _make_store_with_synonyms(tmp_path, synonyms: dict) -> EpisodicStore:
    syn_file = tmp_path / "synonym_map.json"
    syn_file.write_text(json.dumps(synonyms), encoding="utf-8")
    return EpisodicStore(data_root=str(tmp_path))


# ─── Synonym loading ──────────────────────────────────────────────────────────

class TestSynonymLoading:

    def test_load_synonyms_from_file(self, tmp_path):
        store = _make_store_with_synonyms(tmp_path, {"Odin": ["Allfather", "Grimnir"]})
        assert "odin" in store._synonym_map

    def test_no_synonym_file_gives_empty_map(self, tmp_path):
        store = EpisodicStore(data_root=str(tmp_path))
        assert store._synonym_map == {}

    def test_hot_reload_picks_up_changes(self, tmp_path):
        store = _make_store_with_synonyms(tmp_path, {"Odin": ["Allfather"]})
        assert "odin" in store._synonym_map
        # Overwrite file with different content
        syn_file = tmp_path / "synonym_map.json"
        syn_file.write_text(json.dumps({"Thor": ["Thunderer"]}), encoding="utf-8")
        store.reload_synonyms()
        assert "odin" not in store._synonym_map
        assert "thor" in store._synonym_map


# ─── _expand_query ─────────────────────────────────────────────────────────────

class TestExpandQuery:

    def test_expand_adds_synonyms(self, tmp_path):
        store = _make_store_with_synonyms(tmp_path, {"Allfather": ["Odin", "Grimnir"]})
        expanded = store._expand_query("Allfather")
        assert "odin" in expanded
        assert "grimnir" in expanded

    def test_expand_keeps_original_word(self, tmp_path):
        store = _make_store_with_synonyms(tmp_path, {"Allfather": ["Odin"]})
        expanded = store._expand_query("Allfather")
        assert "allfather" in expanded

    def test_expand_empty_query_returns_empty(self, tmp_path):
        store = EpisodicStore(data_root=str(tmp_path))
        expanded = store._expand_query("")
        assert expanded == set()

    def test_expand_unknown_word_returns_original_only(self, tmp_path):
        store = EpisodicStore(data_root=str(tmp_path))
        expanded = store._expand_query("unknownterm")
        assert expanded == {"unknownterm"}


# ─── keyword_search with synonyms ─────────────────────────────────────────────

class TestKeywordSearchWithSynonyms:

    def _seed_entry(self, store: EpisodicStore, content: str, eid: str) -> MemoryEntry:
        e = MemoryEntry(entry_id=eid, session_id="s", timestamp="t",
                        memory_type="fact", content=content)
        store.add(e)
        return e

    def test_synonym_query_finds_entry_with_synonym_term(self, tmp_path):
        # Entry contains "Odin"; query uses "Allfather" — should still match
        store = _make_store_with_synonyms(tmp_path, {"Allfather": ["Odin"]})
        self._seed_entry(store, "Odin walks the halls of Asgard", "e1")
        results = store.keyword_search("Allfather")
        assert any(e.entry_id == "e1" for e in results)

    def test_no_synonym_match_falls_through_to_keyword(self, tmp_path):
        store = EpisodicStore(data_root=str(tmp_path))
        self._seed_entry(store, "mead hall drinking ritual", "e1")
        results = store.keyword_search("mead")
        assert any(e.entry_id == "e1" for e in results)

    def test_query_with_no_synonyms_still_works(self, tmp_path):
        store = EpisodicStore(data_root=str(tmp_path))
        self._seed_entry(store, "dragon ship sailing", "e1")
        results = store.keyword_search("dragon")
        assert any(e.entry_id == "e1" for e in results)

    def test_synonym_case_insensitive(self, tmp_path):
        # synonym_map key "Allfather" — query "allfather" should expand
        store = _make_store_with_synonyms(tmp_path, {"Allfather": ["Odin"]})
        self._seed_entry(store, "Odin sees all", "e1")
        results = store.keyword_search("allfather")
        assert any(e.entry_id == "e1" for e in results)
