# TASK: Wave 4 — Memory Depth (E-16–E-19)
**Created:** 2026-03-21
**Branch:** development
**Status:** IN PROGRESS

## Scope
Implement Wave 4 of the Ørlög Enhancement Plan: four enhancements to memory_store.py
and scheduler.py that give Sigrid richer, emotionally-weighted, associatively-linked,
and automatically consolidated memories.

## Enhancements

| ID   | Title                        | Module(s)                        | Status   |
|------|------------------------------|----------------------------------|----------|
| E-16 | Associative Memory Hooks     | memory_store.py                  | DONE     |
| E-17 | Emotional Significance Weight| memory_store.py                  | DONE     |
| E-18 | Synonym Expansion            | memory_store.py, data/synonym_map.json | DONE |
| E-19 | Nightly Memory Consolidation | memory_store.py, scheduler.py    | DONE     |

## File Changes

### memory_store.py
- `MemoryLink` dataclass: source_id, target_id, similarity, created_at
- `MemoryEntry` gains: pad_arousal, pad_pleasure, emotional_weight_applied fields
- `MemoryEntry.relevance_score()`: emotional weight multiplier (1.0 + arousal * 0.3)
- `SemanticLayer.search_with_scores()`: returns (id, similarity) pairs
- `EpisodicStore`: synonym loading from data_root/synonym_map.json, link file at data_root/session/memory_links.json
- `EpisodicStore._expand_query()`: synonym expansion for keyword search
- `EpisodicStore.keyword_search()`: uses expanded query
- `MemoryStore._find_related()`: finds 3 related memories after store, saves MemoryLink records
- `MemoryStore.add_memory()`: reads WyrdState for emotional weighting, calls _find_related
- `MemoryStore._retrieve_episodic()`: includes linked memories in results
- `MemoryConsolidator` class: batches medium_term buffer → subconscious model → EpisodicEntry

### scheduler.py
- `SchedulerService.register_cron_job()`: register daily HH:MM jobs via CronTrigger
- `SchedulerService._add_apscheduler_job()`: dispatches to interval or cron trigger
- `SchedulerService.register_consolidation_job(consolidator, bus)`: sets up 03:30 nightly job

### data/synonym_map.json (new)
- Initial Norse deity synonyms, concept aliases, name variants

## Test Files
- tests/test_memory_associative.py (E-16) — 15 tests
- tests/test_memory_emotional.py (E-17) — 10 tests
- tests/test_memory_synonyms.py (E-18) — 12 tests
- tests/test_memory_consolidation.py (E-19) — 15 tests

## Next Steps After Wave 4
Wave 5 (E-20–E-24) — Environment & Situational Presence
