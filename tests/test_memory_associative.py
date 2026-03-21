"""
tests/test_memory_associative.py — E-16: Associative Memory Hooks
15 tests covering MemoryLink creation, link storage, retrieval expansion,
keyword-overlap fallback, deduplication, and persistence.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "viking_girlfriend_skill"))

import pytest
from scripts.memory_store import (
    ConversationBuffer,
    EpisodicStore,
    MemoryEntry,
    MemoryLink,
    MemoryStore,
)


# ─── MemoryLink dataclass ─────────────────────────────────────────────────────

class TestMemoryLinkDataclass:

    def test_memorylink_fields(self):
        link = MemoryLink(source_id="a", target_id="b", similarity=0.85, created_at="now")
        assert link.source_id == "a"
        assert link.target_id == "b"
        assert link.similarity == 0.85
        assert link.created_at == "now"

    def test_memorylink_to_dict(self):
        link = MemoryLink(source_id="a", target_id="b", similarity=0.5, created_at="ts")
        d = link.to_dict()
        assert d["source_id"] == "a"
        assert d["target_id"] == "b"
        assert d["similarity"] == 0.5


# ─── EpisodicStore link I/O ────────────────────────────────────────────────────

class TestEpisodicStoreLinks:

    def test_append_link_creates_file(self, tmp_path):
        store = EpisodicStore(data_root=str(tmp_path))
        link = MemoryLink(source_id="s1", target_id="t1", similarity=0.9, created_at="ts")
        store.append_link(link)
        links_file = tmp_path / "session" / "memory_links.json"
        assert links_file.exists()

    def test_append_link_persists_data(self, tmp_path):
        store = EpisodicStore(data_root=str(tmp_path))
        link = MemoryLink(source_id="s1", target_id="t1", similarity=0.75, created_at="ts")
        store.append_link(link)
        raw = json.loads((tmp_path / "session" / "memory_links.json").read_text())
        assert len(raw["links"]) == 1
        assert raw["links"][0]["source_id"] == "s1"

    def test_links_loaded_on_init(self, tmp_path):
        store1 = EpisodicStore(data_root=str(tmp_path))
        link = MemoryLink(source_id="s1", target_id="t1", similarity=0.6, created_at="ts")
        store1.append_link(link)
        store2 = EpisodicStore(data_root=str(tmp_path))
        assert len(store2._links) == 1

    def test_get_links_for_returns_correct_links(self, tmp_path):
        store = EpisodicStore(data_root=str(tmp_path))
        store.append_link(MemoryLink("src", "tgt1", 0.8, "ts"))
        store.append_link(MemoryLink("src", "tgt2", 0.7, "ts"))
        store.append_link(MemoryLink("other", "tgt3", 0.6, "ts"))
        links = store.get_links_for("src")
        assert len(links) == 2
        target_ids = {lk.target_id for lk in links}
        assert target_ids == {"tgt1", "tgt2"}

    def test_get_links_for_unknown_id_returns_empty(self, tmp_path):
        store = EpisodicStore(data_root=str(tmp_path))
        assert store.get_links_for("nobody") == []

    def test_get_entries_by_ids(self, tmp_path):
        store = EpisodicStore(data_root=str(tmp_path))
        e1 = MemoryEntry(entry_id="id1", session_id="s", timestamp="t",
                         memory_type="fact", content="alpha fact")
        e2 = MemoryEntry(entry_id="id2", session_id="s", timestamp="t",
                         memory_type="fact", content="beta fact")
        store.add(e1)
        store.add(e2)
        result = store.get_entries_by_ids(["id2", "id1"])
        assert [e.entry_id for e in result] == ["id2", "id1"]


# ─── MemoryStore._find_related ────────────────────────────────────────────────

class TestFindRelated:

    def _make_store(self, tmp_path, n_seed: int = 5) -> MemoryStore:
        store = MemoryStore(data_root=str(tmp_path), semantic_enabled=False)
        # Seed with memories containing overlapping keywords
        topics = ["Odin rune wisdom", "rune magic stave", "Odin Allfather hall",
                  "mead hall drinking blót", "Freyja seiðr magic"]
        for i, t in enumerate(topics[:n_seed]):
            entry = MemoryEntry(
                entry_id=f"seed{i}", session_id="s", timestamp="t",
                memory_type="fact", content=t,
            )
            store._episodic.add(entry)
        return store

    def test_find_related_creates_links(self, tmp_path):
        store = self._make_store(tmp_path)
        new_entry = MemoryEntry(
            entry_id="new1", session_id="s", timestamp="t",
            memory_type="fact", content="Odin rune hall magic",
        )
        store._episodic.add(new_entry)
        store._find_related(new_entry)
        links = store._episodic.get_links_for("new1")
        assert len(links) >= 1

    def test_find_related_max_3_links(self, tmp_path):
        store = self._make_store(tmp_path, n_seed=5)
        new_entry = MemoryEntry(
            entry_id="new1", session_id="s", timestamp="t",
            memory_type="fact", content="rune Odin magic mead hall blót seiðr",
        )
        store._episodic.add(new_entry)
        store._find_related(new_entry)
        links = store._episodic.get_links_for("new1")
        assert len(links) <= 3

    def test_find_related_no_self_link(self, tmp_path):
        store = self._make_store(tmp_path)
        new_entry = MemoryEntry(
            entry_id="new1", session_id="s", timestamp="t",
            memory_type="fact", content="Odin rune hall magic",
        )
        store._episodic.add(new_entry)
        store._find_related(new_entry)
        links = store._episodic.get_links_for("new1")
        assert all(lk.target_id != "new1" for lk in links)

    def test_find_related_no_links_for_empty_store(self, tmp_path):
        store = MemoryStore(data_root=str(tmp_path), semantic_enabled=False)
        new_entry = MemoryEntry(
            entry_id="lone", session_id="s", timestamp="t",
            memory_type="fact", content="isolated memory",
        )
        store._episodic.add(new_entry)
        store._find_related(new_entry)
        assert store._episodic.get_links_for("lone") == []


# ─── Retrieval expansion ───────────────────────────────────────────────────────

class TestRetrievalExpansion:

    def test_retrieve_includes_linked_entry(self, tmp_path):
        store = MemoryStore(data_root=str(tmp_path), semantic_enabled=False)
        related = MemoryEntry(
            entry_id="rel1", session_id="s", timestamp="t",
            memory_type="fact", content="related lore memory",
        )
        store._episodic.add(related)
        primary = MemoryEntry(
            entry_id="pri1", session_id="s", timestamp="t",
            memory_type="fact", content="rune magic Odin",
        )
        store._episodic.add(primary)
        # Manually link pri1 → rel1
        store._episodic.append_link(
            MemoryLink(source_id="pri1", target_id="rel1", similarity=0.8, created_at="ts")
        )
        # Query that hits primary but not related by keyword
        results = store._retrieve_episodic("rune Odin")
        result_ids = {e.entry_id for e in results}
        assert "rel1" in result_ids

    def test_retrieve_deduplicates_linked_entries(self, tmp_path):
        store = MemoryStore(data_root=str(tmp_path), semantic_enabled=False)
        e1 = MemoryEntry(entry_id="e1", session_id="s", timestamp="t",
                         memory_type="fact", content="rune Odin")
        store._episodic.add(e1)
        # Link to itself (edge case — should not cause duplicates)
        store._episodic.append_link(
            MemoryLink(source_id="e1", target_id="e1", similarity=1.0, created_at="ts")
        )
        results = store._retrieve_episodic("rune Odin")
        ids = [e.entry_id for e in results]
        assert len(ids) == len(set(ids))
