# Ørlög Architecture — Session Status
**Date:** 2026-03-22
**Branch:** development
**Operator:** Runa Gridweaver Freyjasdottir

---

## Session Summary

Post-enhancement-plan hardening and infrastructure work. No new enhancement waves — all work below is maintenance, quality, and portability.

---

## Completed This Session

### S-06b — Full Soul Anchor (Conflict / Injection Defence Mode)
- Created `data/soul_anchor_full_version.md` — 6,400-char detailed anchor with:
  - Anti-manipulation protocol section (7 named patterns)
  - Override hierarchy (5-level priority list)
  - Absolute hard limits
- `prompt_synthesizer.py`: `activate_full_anchor(turns)` method + `_full_anchor_turns_remaining` countdown counter
- `main.py`: SecurityViolation handler now calls `activate_full_anchor(turns=3)` so the next 3 turns get the full anchor

### Wave TG-1 — TrustGraph Optional Client
- Created `scripts/trustgraph_client.py` — thin wrapper with three-state circuit breaker (CLOSED/OPEN/HALF_OPEN)
- Created `data/trustgraph_settings.md` — markdown feature toggle; set `enabled: true` to activate
- Created `requirements-optional.txt` — `trustgraph-api` as optional dep
- `main.py`: wired via `_safe_init("trustgraph", ...)` — graceful no-op when disabled
- ChromaDB + BM25 remain primary systems; TrustGraph is an enhancement layer
- Waves TG-2/3/4 (MimirWell GraphRAG, memory mirroring, infra docs) deferred until live deployment

### De-personalisation (Public Release Prep)
- Removed all hardcoded `"Volmarr"` / `"volmarr"` references from production files
- `trust_engine.py`: `_DEFAULT_PRIMARY_CONTACT = "user"`
- `main.py`: default `user_id="user"`, farewell message, injection penalty uses runtime `._primary_contact_id` lookup
- `memory_store.py`, `wyrd_matrix.py`, `environment_mapper.py`, `ops/launch_calibration.py`: comments/strings updated
- All tests: `"volmarr"` contact IDs → `"test_user"`
- `data/synonym_map.json`: removed `"Volmarr"` entry (was a personalized runtime query expansion entry)
- **Rule**: Dev planning files (TODO.md, PLAN_*.md, STATUS_*.md, ENHANCEMENT_PLAN.md, blueprints) may retain personal references — they are not part of the working release

### Portable Paths (All Scripts Fixed)
- 120 `scripts/write_*.py` and `scripts/gen_*.py` files: all replaced `C:\Users\volma\...` absolute paths with `Path(__file__).resolve().parent.parent / ...` portable pattern
- `data/knowledge_reference/populate.py`: same fix
- All code is now cross-platform with no hardcoded absolute paths

### Production Stub Fixes (from PLACEHOLDER_INVENTORY.md)
- `state_bus.py:close()` — was empty `pass`. Now signals all session stop events, clears subscriber topic registrations, logs shutdown
- `vordur.py:answer_relevance` — was always `0.0`. Added `_jaccard_relevance()` (Jaccard token overlap using existing `_tokenize()`) and threaded `query` + `response` through `score_and_repair()` → `_build_truth_profile()`

### Data Size Limits Audit
**Data loss fixed:**
- `memory_store.py:add_turn()` — removed `[:1000]` truncation. Full user/sigrid text now stored; no data silently dropped

**Processing limits raised:**
- `vordur.py`: `_MAX_RESPONSE_CHARS_FOR_EXTRACTION` 1200 → 4000; `_MAX_CHUNK_CHARS_FOR_NLI` 500 → 1200
- `huginn.py`: `_MAX_EPISODIC_CHARS` 1200 → 3000; `_MAX_KNOWLEDGE_CHARS` 3000 → 6000; per-chunk display cap 1000 → 2500
- `cove_pipeline.py`: `context[:1500]` → `context[:3000]` in all three CoVe stage prompts

**System prompt expanded:**
- `prompt_synthesizer.py`: identity_chars 2000→4000, soul_chars 400→800, memory_chars 800→1600, max_system_chars 6000→12000, max_hint_chars 200→400
- Added soft response length guidance to system prompt (section 4b)

**Response caps raised (S-02 tiers now safety rails, not editorial limits):**
- 512/1024/1500/2048 → 1024/2048/4096/8192 tokens per tier

### Cross-Platform / Hardware-Adaptive
- `main.py`: `_detect_hardware_profile()` — detects CPU count + RAM, classifies as `low_power` / `standard` / `high_end`, logs at startup
- Adaptive config via `_hw()` helper in `_build_config()`:
  - `low_power` (< 2 cores or < 2 GB RAM): timeout 90s, max_tokens 512, poll 60s, vordur timeout 20s, CoVe step 40s
  - `high_end` (> 8 cores + > 16 GB RAM): timeout 20s, max_tokens 2048, poll 15s, tighter verification
  - `standard`: defaults unchanged
- `scheduler.py`: APScheduler thread pool now `min(cpu_count, 4)` instead of unlimited

### Task 3: Placeholder Inventory
- Created `PLACEHOLDER_INVENTORY.md` — full scan of all placeholders, stubs, incomplete content
- Both production stubs (state_bus.close, vordur answer_relevance) now resolved and marked ✅

---

## Test Suite Status
- **490 tests passing** in `tests/` (run with `python -m pytest tests/ --ignore=tests/test_e2e_system.py`)
- 5 pre-existing backpressure ordering failures (pass in isolation, test ordering issue in full suite)
- 1 pre-existing floating-point equality failure in `test_trust_diminishing`
- `test_e2e_system.py` excluded (pre-existing event loop pollution)

---

## Pending / Deferred

| Item | Status |
|---|---|
| TrustGraph TG-2: MimirWell GraphRAG tier | Deferred — needs live TrustGraph deployment |
| TrustGraph TG-3: Memory store mirroring | Deferred |
| TrustGraph TG-4: Infrastructure docs | Deferred |
| Knowledge build (72-domain misconception watchlists, batch ledgers) | Future sprint — planning scaffolding in `implementation_blueprints/sigrid_knowledge_build/` |

---

## Notes

- `soul_anchor.md` restructured with 13 markdown headings (all original content preserved)
- `SECURITY_RESEARCH_context_resilience.md` and `SECURITY_CODE_IDEAS_context_resilience.md` remain in `data/` as research reference
- `PLAN_trustgraph_integration.md` documents all 4 TrustGraph waves for future reference
- `PLACEHOLDER_INVENTORY.md` is the living placeholder tracker — update when items resolve
