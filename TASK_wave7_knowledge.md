# TASK_wave7_knowledge.md — Wave 7: Knowledge & Synthesis Quality
**Created**: 2026-03-21
**Branch**: development
**Modules**: `mimir_well.py` (E-26, E-27), `prompt_synthesizer.py` (E-28–E-31)

---

## Scope
Wave 7 (E-26–E-31) — 6 enhancements improving retrieval speed, integrity, voice
quality, token accuracy, and hot-reload capability. Two modules, 56 tests.

---

## Inventory

### mimir_well.py

#### E-26 — BM25 Pre-Filter (Layer 0)
- `_FlatIndex.search_with_top_score(query, chunks_by_id, n)` → `(List[KnowledgeChunk], float)`
- `_FlatIndex.search()` refactored to delegate to `search_with_top_score()`
- `MimirWell._bm25_shortcircuit_threshold: float = 0.75` (constructor + config)
- Counters: `_bm25_shortcircuit_hits: int`, `_bm25_total_queries: int`
- `_tag_retrieval_path(chunks, path) -> List[KnowledgeChunk]` — copies with metadata tag
- `retrieve()` runs BM25 first; shortcircuit if `top_score > threshold`
- retrieval_path values: `"bm25_fast"` | `"chromadb"` | `"bm25_fallback"`
- `MimirState` gains `bm25_shortcircuit_rate: float`

#### E-27 — Axiom Integrity Sentinel
- `MimirWell` gains `session_dir: str = "session"` param → `_axiom_hashes_file`
- `_compute_axiom_hashes() -> Dict[str, str]` — sha256 of all DEEP_ROOT/ASGARD chunks
- `_save_axiom_hashes()`, `_load_axiom_hashes()` — session/axiom_hashes.json
- In `ingest_all()`: compute + save hashes after ingesting axiom chunks
- `check_axiom_integrity() -> bool` — re-hashes and compares; logs CRITICAL on mismatch
- `MimirHealthState` gains `axiom_integrity: bool = True`
- `MimirHealthMonitor._health_check()` calls `check_axiom_integrity()` + triggers reindex on failure

### prompt_synthesizer.py

#### E-28 — Dynamic Section Reordering
- `SectionPriority` dataclass: `name: str`, `base_order: int`, `current_order: int`
- `build_messages()` gains `emotional_state: Optional[Dict[str, float]] = None` param
- `_reorder_sections(hint_keys, emotional_state) -> List[str]`:
  - `pad_arousal > 0.7` → wyrd_matrix moves to position 0
  - `pad_pleasure < -0.5` → ethics moves to position 0
  - Normal → default `_HINT_SECTION_ORDER` preserved
- Section ordering logged at DEBUG level each turn

#### E-29 — Skaldic Vocabulary Injection
- `data/skaldic_vocabulary.json` — 200+ entries: `word`, `meaning`, `context_tags`, `usage_example`
- `PromptSynthesizer` gains `skaldic_injection: bool = True` + `_skaldic_vocab`
- `_load_skaldic_vocab(filename)` loads from data root
- `_turn_counter: int = 0` increments each `build_messages()` call
- `_inject_skaldic_flavor(turn_id, context_tags) -> str` — seeded from `turn_id % len(vocab)`,
  picks 2 contextually matching entries
- Injected as a single system line: "Weave these into your voice today: ..."
- Disabled if `skaldic_injection=False`

#### E-30 — Actual Token Counting
- `_count_tokens(text: str) -> int` — uses `litellm.token_counter()`, fallback `len(text)//4`
- Used in `_build_system()` logging to report token estimate alongside char count
- Fallback mode logged at DEBUG when litellm unavailable

#### E-31 — Hot-Reload Identity
- `_reload_lock: threading.Lock` added at `__init__`
- `reload_identity() -> None` — thread-safe reload of core_identity.md + SOUL.md
- `_IdentityFileWatcher` class: polling-based (Windows-compatible), interval=5s
- `start_watcher(bus=None)`, `stop_watcher()` on PromptSynthesizer
- On change: calls `reload_identity()`, publishes `persona.identity_reloaded` StateEvent
- `_degraded` flag stays False if reload succeeds; True if both files missing

---

## Test Files to Create

| File | Tests | Status |
|------|-------|--------|
| `tests/test_mimir_bm25_prefilter.py` | 10 | ⏳ |
| `tests/test_mimir_axiom_integrity.py` | 8 | ⏳ |
| `tests/test_synthesizer_reorder.py` | 10 | ⏳ |
| `tests/test_synthesizer_skaldic.py` | 10 | ⏳ |
| `tests/test_synthesizer_tokens.py` | 8 | ⏳ |
| `tests/test_synthesizer_hotreload.py` | 10 | ⏳ |

---

## Progress Tracker

- [ ] TASK file committed
- [ ] E-26 BM25 pre-filter implemented
- [ ] E-27 Axiom integrity implemented
- [ ] E-28 Dynamic reordering implemented
- [ ] E-29 Skaldic vocabulary implemented (data file + injection)
- [ ] E-30 Token counting implemented
- [ ] E-31 Hot-reload implemented
- [ ] All 6 test files written
- [ ] Tests passing (full suite)
- [ ] STATUS + memory updated
- [ ] Committed and pushed

---

## File Paths
- `viking_girlfriend_skill/scripts/mimir_well.py`
- `viking_girlfriend_skill/scripts/prompt_synthesizer.py`
- `viking_girlfriend_skill/data/skaldic_vocabulary.json` *(new)*
- `tests/test_mimir_bm25_prefilter.py` *(new)*
- `tests/test_mimir_axiom_integrity.py` *(new)*
- `tests/test_synthesizer_reorder.py` *(new)*
- `tests/test_synthesizer_skaldic.py` *(new)*
- `tests/test_synthesizer_tokens.py` *(new)*
- `tests/test_synthesizer_hotreload.py` *(new)*
