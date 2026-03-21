# TASK_security_context_resilience.md — Security: Context Resilience Hardening
**Created**: 2026-03-21
**Branch**: development
**Modules**: `security.py`, `mimir_well.py`, `model_router_client.py`, `memory_store.py`, `prompt_synthesizer.py`, `runtime_kernel.py`

---

## Scope

Implement the 6 security/context-resilience improvements designed in
`data/SECURITY_CODE_IDEAS_context_resilience.md`, ordered by effort (lowest first):

| # | Priority | Gap | Module | Effort |
|---|----------|-----|--------|--------|
| S-01 | P-3 | RAG chunk injection scan | `mimir_well.py` + `security.py` | Low |
| S-02 | P-4 | Response size capping per mode | `model_router_client.py` | Low |
| S-03 | P-6 | Precise token budget (litellm counter) | `memory_store.py` | Very Low |
| S-04 | P-2 | Hard token cap + dialogue truncation | `prompt_synthesizer.py` | Medium |
| S-05 | P-1 | ContextGuard + soul re-injection | `prompt_synthesizer.py` + `security_config.json` | Medium-High |
| S-06 | P-5 | Session file integrity verification | `security.py` + `runtime_kernel.py` | Medium |

Total expected new tests: ~53 across 4 new test files + extensions.

---

## File Inventory

### Modified files
- `viking_girlfriend_skill/scripts/mimir_well.py` — add RAG chunk injection scan in `retrieve()`
- `viking_girlfriend_skill/scripts/security.py` — add `SessionFileGuard`, extend `SecurityState`
- `viking_girlfriend_skill/scripts/model_router_client.py` — add `_get_response_cap()`, use in routing
- `viking_girlfriend_skill/scripts/memory_store.py` — replace len//4 estimate with litellm counter
- `viking_girlfriend_skill/scripts/prompt_synthesizer.py` — add `ContextGuard`, `_build_soul_anchor_block()`, `_compact_dialogue_history()`, hard cap enforcement in `build_prompt()`
- `viking_girlfriend_skill/scripts/runtime_kernel.py` — call `SessionFileGuard.init_session()` at startup
- `viking_girlfriend_skill/data/security_config.json` — add new config keys

### New test files
- `tests/test_security_rag_scan.py` (~10 tests, S-01)
- `tests/test_response_caps.py` (~10 tests, S-02)
- `tests/test_context_guard.py` (~15 tests, S-04 + S-05)
- `tests/test_session_integrity.py` (~8 tests, S-06)

---

## Progress Tracker

- [x] TASK file committed
- [x] S-01: RAG chunk injection scan
- [x] S-02: Response size capping
- [x] S-03: Precise token budget
- [x] S-04: Hard token cap + auto-truncation
- [x] S-05: ContextGuard + soul re-injection
- [x] S-06: Session file integrity
- [x] All test files written (48 new tests)
- [x] Tests passing (491 total, 5 pre-existing backpressure failures only)
- [x] STATUS + memory updated
- [x] Committed and pushed

---

## Notes

- All changes additive — no existing tests should break
- `security_config.json` keys added with safe defaults (booleans default true, thresholds default conservative)
- OpenClaw Node.js layer not in scope here — separate research/proposal document
