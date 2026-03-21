# TASK_wave6_trust.md — Wave 6: Relational Intelligence
**Created**: 2026-03-21
**Branch**: development
**Module**: `viking_girlfriend_skill/scripts/trust_engine.py`

---

## Scope
Wave 6 (E-23, E-24, E-25) — three enhancements to TrustEngine deepening
Sigrid's relational modeling. All in `trust_engine.py`.

---

## Inventory

### E-23 — TrustFacets: Multidimensional Trust ⏳
**What**:
- `TrustFacets` dataclass: `competence`, `benevolence`, `integrity` (each 0–1)
- `trust_score` becomes computed property: `competence*0.3 + benevolence*0.4 + integrity*0.3`
- `_EVENT_IMPACTS` updated from 4-tuple to 6-tuple (+ competence, benevolence, integrity deltas)
- New `competence_shown` event type + keywords
- `TrustState` gains `facets: TrustFacets`; `to_dict()` includes facets
- `_build_prompt_hint()` extended with dominant facet info
- `_ensure_ledger()` initialises all facets to `initial_trust`

### E-24 — Relational Milestones ⏳
**What**:
- `Milestone` dataclass: `milestone_id`, `name`, `description`, `occurred_at`, `trust_anchor`, `contact_id`
- `TrustEngine` gains `session_dir` param; loads/saves `session/milestones.json` (append-only)
- `_MILESTONE_DEFS` dict: 8 milestone types mapped to triggering events + anchor values
- `_detect_milestones(cid, inferred_events, bus)` — checks firsts, creates and saves
- `TrustLedger.anchor_floor: float` — kept in sync by TrustEngine; applied in `trust_score` property
- Publishes `trust.milestone_reached` StateEvent to StateBus
- `from_config()` reads `session_dir` from `trust_engine` config block

### E-25 — Diminishing Returns on Repeated Signals ⏳
**What**:
- `_signal_counts: Dict[str, int]` on TrustEngine (session-only, not persisted)
- Applied in `process_turn()` before each `apply_event()` call
- Formula: `effective_mag = max(0.1, 1.0 / (1.0 + log(1.0 + count)))`
- `reset_signal_counts()` public method (call at session end)
- DEBUG log when count > 3 for any signal type
- Only applies to keyword-inferred events (not to explicit `record_event()` calls)

---

## Test Files to Create

| File | Tests | Status |
|------|-------|--------|
| `tests/test_trust_facets.py` | 15 | ⏳ |
| `tests/test_trust_milestones.py` | 15 | ⏳ |
| `tests/test_trust_diminishing.py` | 8 | ⏳ |

---

## Progress Tracker

- [ ] TASK file committed (this file)
- [ ] E-23 TrustFacets implemented
- [ ] E-24 Milestones implemented
- [ ] E-25 Diminishing Returns implemented
- [ ] test_trust_facets.py written
- [ ] test_trust_milestones.py written
- [ ] test_trust_diminishing.py written
- [ ] Tests passing (full suite)
- [ ] STATUS file updated
- [ ] Memory updated
- [ ] Committed and pushed

---

## File Paths
- `viking_girlfriend_skill/scripts/trust_engine.py` — sole Python target
- `tests/test_trust_facets.py` — new
- `tests/test_trust_milestones.py` — new
- `tests/test_trust_diminishing.py` — new
- `STATUS_2026-03-21.md` — update Wave 6 status
