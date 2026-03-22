# Placeholder & Incomplete Content Inventory

**Project**: Viking Girlfriend Skill for OpenClaw (Sigrid / Ørlög Architecture)
**Last Scanned**: 2026-03-22
**Maintained by**: Runa — update whenever a placeholder is resolved or a new one is introduced.

---

## Summary

| Category | Count | Priority |
|---|---|---|
| Production code — genuine stubs | 2 | High |
| Knowledge data — upstream TODO content | 1 | Low (third-party) |
| Knowledge build planning scaffold | ~360 files | Future work |
| Data generation scripts (non-production) | 1 | Low |
| Deferred integration waves | 3 waves | Future work |

---

## Section 1 — Production Code Stubs (Must Fix Before Release)

### 1.1 `viking_girlfriend_skill/scripts/state_bus.py` — Line 344

```python
async def close(self) -> None:
    """Gracefully shut down the bus — Bifröst retracts."""
    pass
```

**Issue**: `close()` is an empty method body. A graceful shutdown should cancel any running subscriber tasks, drain pending queues, and signal completion.
**Impact**: The skill has no bus teardown path. Resources may leak on shutdown.
**Status**: Incomplete — needs implementation.
**Suggested work**: Cancel all subscriber queue tasks, drain `_inbound_topics` and `_state_topics`, log shutdown.

---

### 1.2 `viking_girlfriend_skill/scripts/vordur.py` — Line 1801

```python
answer_relevance=0.0,   # placeholder — requires query context
```

**Issue**: `answer_relevance` field in `TruthProfile` is always set to `0.0` in `_compute_truth_profile()`. The actual score requires the original user query to be passed into this method, which currently only receives the generated answer.
**Impact**: VordurChecker truth profiles always report zero answer relevance — one of the 6 scored dimensions is permanently silent.
**Status**: Known limitation, intentionally deferred. Query context wiring is a non-trivial refactor of the Vordur → CovePipeline → MimirWell call chain.
**Suggested work**: Thread the original query string through to `_compute_truth_profile()` and implement semantic similarity scoring against the answer.

---

## Section 2 — Knowledge Reference — Upstream Content

### 2.1 `viking_girlfriend_skill/data/knowledge_reference/guide_science_communication.md` — Lines 39, 47, 51, 64

```markdown
## Scope

TODO

### Collections of useful phrases

TODO
```

**Issue**: Several sections in this file contain literal `TODO` markers. This is upstream content from an "Awesome Lists" repository — the original author left sections unfilled.
**Impact**: Minimal. This file is read-only reference data from an external source. Sigrid's RAG pipeline will simply return no content for those sections, which is harmless.
**Status**: Third-party content. No action required unless sections are needed for specific use cases.
**Suggested work** (optional): Remove the empty `TODO` sections or replace with a note marking them as "not available in this source."

---

## Section 3 — Knowledge Build Planning Scaffold (Future Work)

All files under `implementation_blueprints/sigrid_knowledge_build/` are planning infrastructure for a future large-scale knowledge ingestion project. They are **not production code** and are **not loaded at runtime**. None affect Sigrid's operation today.

### 3.1 Misconception Watchlists — All 72 files empty

**Path**: `implementation_blueprints/sigrid_knowledge_build/misconception_watchlists/`
**Files**: `01_software_engineering_misconception_watchlist.md` through `72_trauma-informed_approaches_misconception_watchlist.md`
**Issue**: All 72 files contain only the template headers:
```
- Misconception:
- Why it is wrong or incomplete:
- Safer corrected framing:
- Whether a dedicated archival entry is warranted:
```
No actual misconceptions have been entered.
**Status**: Template scaffolding — awaiting knowledge build sprint.

---

### 3.2 Batch Ledgers, Rollback Logs, Citation Tracking (~360 files with "not started" status)

**Affected subdirectories**:

| Subdirectory | Files | Status |
|---|---|---|
| `batch_ledgers/` | 72 | All "not started" |
| `batch_rollback_logs/` | 72 | All empty template |
| `batch_audit_templates/` | varies | All empty template |
| `batch_execution_worksheets/` | varies | All empty template |
| `batch_milestone_ledgers/` | varies | All empty template |
| `citation_tracking_sheets/` | 72 | All empty template |
| `claim_validation_logs/` | 72 | All empty template |
| `contradiction_check_sheets/` | 72 | All empty template |
| `coverage_review_dashboards/` | varies | All empty template |
| `deduplication_ledgers/` | 72 | All empty template |
| `dispute_registers/` | 72 | All empty template |
| `entry_merge_decision_logs/` | 72 | All empty template |
| `entry_status_boards/` | 72 | All empty template |
| `exclusion_ledgers/` | 72 | All empty template |
| `progress_narrative_logs/` | 72 | All empty template |
| `research_queue_sheets/` | 72 | All empty template |
| `review_cadence_sheets/` | 72 | All empty template |
| `source_gap_trackers/` | 72 | All empty template |
| `source_provenance_logs/` | 72 | All empty template |
| `unresolved_question_registers/` | 72 | All empty template |
| `verification_plans/` | 72 | Populated (meaningful) |
| `subject_scope_dossiers/` | 72 | Populated (meaningful) |
| `misconception_watchlists/` | 72 | Empty (see 3.1) |
| `subject_taxonomy_plans/` | 145 | Populated (meaningful) |
| `source_reliability_rubrics/` | 72 | Populated (meaningful) |

**Status**: Normal state for planning infrastructure. These are filled in during knowledge build sprints, not before.

---

## Section 4 — Data Generation Scripts (Non-Production)

### 4.1 `scripts/knowledge_generator.py`

```python
"""
This is a placeholder for actual knowledge generation.
In a real scenario, this would be populated with high-quality data.
"""
```

**Issue**: This script generates dummy "Concept {n}" placeholder entries. Its own docstring explicitly identifies itself as a placeholder.
**Impact**: Zero — it is not imported by any production module and not called by the skill.
**Status**: Can be deleted. It was the root cause of the placeholder contamination documented in `AUDIT_REPORT_PLACEHOLDERS.md`.
**Suggested work**: Delete `scripts/knowledge_generator.py` and all `scripts/write_ai_*.py`, `scripts/gen_old_norse.py`, `scripts/gen_warfare.py` — these are the scripts that generated bad data. Verify knowledge files are clean before deleting.

---

## Section 5 — Deferred Integration Waves

### 5.1 TrustGraph Waves TG-2, TG-3, TG-4

**Plan document**: `PLAN_trustgraph_integration.md`

Wave TG-1 (client wrapper + feature toggle) is complete and merged. Three further waves are deferred:

| Wave | Description | Status |
|---|---|---|
| TG-2 | MimirWell GraphRAG Enhancement — wire `get_trustgraph_client()` into `mimir_well.py` search path as a third retrieval tier | Deferred |
| TG-3 | Memory Store Mirroring — optionally mirror memory store writes to TrustGraph triples | Deferred |
| TG-4 | Infrastructure Docs — RPi deployment notes, production config template | Deferred |

**Trigger to resume**: TrustGraph feature toggle is set to `enabled: true` in `data/trustgraph_settings.md` and the deployment is stable.

---

## Resolved Placeholders (Historical Record)

| Item | Resolution | Commit |
|---|---|---|
| Hardcoded `C:\Users\volma\...` absolute paths in 120 `scripts/write_*.py` / `scripts/gen_*.py` | Replaced with `Path(__file__).resolve().parent.parent / ...` portable pattern | Multiple commits |
| Personal name "Volmarr" hardcoded in production defaults (`trust_engine.py`, `main.py`, etc.) | Replaced with generic "user" / runtime lookup | Multiple commits |
| `ARTIFICIAL_INTELLIGENCE.md`, `OLD_NORSE.md`, `SOFTWARE_ENGINEERING.md`, `ANCIENT_WARFARE.md` — "Concept {n}" placeholder contamination | Re-forged with Wikipedia DB import or hand-crafted content | Per `AUDIT_REPORT_PLACEHOLDERS.md` |
| `soul_anchor.md` — missing headings / disorganised | Restructured with 13 markdown headings, all original content preserved | commit `67861de` |
| `soul_anchor_full_version.md` — conflict/injection defence anchor missing | Created with anti-manipulation protocols and override hierarchy | commit `8fa953d` |
| `prompt_synthesizer.py` — no full anchor activation mechanism | Added `activate_full_anchor()` / `_full_anchor_turns_remaining` counter | commit `8fa953d` |

---

*This file is a living document. Cross-reference with `TODO.md` for the broader project backlog.*
