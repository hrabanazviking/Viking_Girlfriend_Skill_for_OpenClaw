# TASK: Sigrid — Ørlög Architecture Implementation
# Created: 2026-03-20
# Branch: development

## Scope
Full Python implementation of the Ørlög Architecture skill for OpenClaw.
18 Python modules, built in dependency order, adopting code from
`code_of_other_apps_that_can_be_adopted/`.

---

## Environment (Windows 11)
- Python 3.10.11 ✅
- Node.js 22.14.0 ✅
- OpenClaw 2026.3.11 ✅ (global npm install)
- Ollama 0.12.0 ✅ (desktop app — start manually when needed)
- psutil 7.0.0 ✅
- APScheduler 3.11.2 ✅
- numpy 2.1.2 ✅
- chromadb 1.5.5 ✅
- litellm 1.82.4 ✅
- ollama (Python client) 0.6.1 ✅

---

## Implementation Progress Tracker

### Phase 1 — Foundation (Tracks A)
| Step | Module | Status | Notes |
|------|--------|--------|-------|
| 01 | System Prep / Dependencies | ✅ DONE | Windows 11 env fully set up |
| 02 | Container Deploy | ⏳ PENDING | Need Docker Desktop or direct run (no Podman on Win) |
| 03 | Local Model Provision | ⏳ PENDING | Ollama installed; need to pull llama3 8B |
| 04 | Skill Manifest (SKILL.md) | ⏳ PENDING | OpenClaw skill registration |
| 05 | Core Python Scaffolding | ⏳ PENDING | `scripts/` dir, `main.py`, `requirements.txt` |
| — | `runtime_kernel.py` | ⏳ PENDING | Module 01 |
| — | `state_bus.py` | ⏳ PENDING | Module 02, adopts bus/ |
| — | `config_loader.py` | ⏳ PENDING | Module 03 |
| — | `comprehensive_logging.py` | ⏳ PENDING | Module 04, direct adopt |

### Phase 2 — State Machines (Track B)
| Step | Module | Status | Notes |
|------|--------|--------|-------|
| 06 | `wyrd_matrix.py` | ⏳ PENDING | Module 05/06, adopts wyrd_system.py + emotional_engine.py |
| 07 | `bio_engine.py` | ⏳ PENDING | Module 04, adopts menstrual_cycle.py |
| 08 | `oracle.py` | ⏳ PENDING | Module 06, adopts Norn logic from wyrd_system.py |
| 09 | `metabolism.py` | ⏳ PENDING | Module 07, psutil direct |

### Phase 3 — Mind & Shield (Track C)
| Step | Module | Status | Notes |
|------|--------|--------|-------|
| 10 | `security.py` | ⏳ PENDING | Module 08, adopts thor_guardian.py |
| 11 | `trust_engine.py` | ⏳ PENDING | Module 09, adopts social_ledger.py |
| 12 | `ethics.py` | ⏳ PENDING | Module 10, loads values.json + SOUL.md |
| 13 | `memory_store.py` | ⏳ PENDING | Module 11, adopts memory_system + enhanced_memory + RAG |
| 14 | `dream_engine.py` | ⏳ PENDING | Module 12, adopts world_dreams.py |

### Phase 4 — Agency & Context (Track D)
| Step | Module | Status | Notes |
|------|--------|--------|-------|
| 15 | `scheduler.py` | ⏳ PENDING | Module 13, adopts timeline_service.py + APScheduler |
| 16 | `project_generator.py` | ⏳ PENDING | Module 14 |
| 17 | `environment_mapper.py` | ⏳ PENDING | Module 15, loads environment.json |
| 18 | `prompt_synthesizer.py` | ⏳ PENDING | Module 16, loads prompt_templates/ |
| — | `model_router_client.py` | ⏳ PENDING | Module 17, adopts local_providers.py + openrouter.py |

### Phase 5 — Launch (Track E)
| Step | Module | Status | Notes |
|------|--------|--------|-------|
| — | `main.py` (full integration) | ⏳ PENDING | Module 18, wires everything |
| 19 | E2E Validation Suite | ⏳ PENDING | |
| 20 | Launch Calibration & Autostart | ⏳ PENDING | |

---

## Immediate Next Steps

1. **Read** `implementation_blueprints/module_specs/module_01_runtime_kernel.md`
2. **Read** `implementation_blueprints/module_specs/module_02_state_bus.md`
3. **Read** `implementation_blueprints/module_specs/module_03_config_loader.md`
4. **Read** `code_of_other_apps_that_can_be_adopted/comprehensive_logging.py` (full)
5. **Write** planning report for Phase 1 scaffolding
6. **Create** `viking_girlfriend_skill/scripts/` directory structure
7. **Create** `viking_girlfriend_skill/SKILL.md` for OpenClaw registration
8. **Write** `requirements.txt`

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `RULES.AI.md` | Immutable coding laws |
| `CLAUDE.md` | My working config for this project |
| `ROADMAP.md` | 20-step plan |
| `ARCHITECTURE.md` | System diagram |
| `implementation_blueprints/adoption_from_other_apps/00_ADOPTION_MASTER_PLAN.md` | Adoption strategy |
| `viking_girlfriend_skill/data/core_identity.md` | Sigrid's full personality system |
| `viking_girlfriend_skill/data/values.json` | Machine-readable values |
| `infrastructure/litellm_config.yaml` | 3-tier model routing config |

---

## Adoption Source Map (Key Files)

| Adopt From | Into Module |
|-----------|-------------|
| `bus/events.py`, `bus/queue.py`, `bus/journal.py` | `state_bus.py` |
| `menstrual_cycle.py` | `bio_engine.py` |
| `wyrd_system.py` + `emotional_engine.py` + `soul_mechanics.py` + `stress_system.py` | `wyrd_matrix.py` |
| `thor_guardian.py` + `crash_reporting.py` | `security.py` |
| `social_ledger.py` | `trust_engine.py` |
| `memory_system.py` + `enhanced_memory.py` + `character_memory_rag.py` + `rag_system.py` | `memory_store.py` |
| `world_dreams.py` | `dream_engine.py` |
| `timeline_service.py` | `scheduler.py` |
| `local_providers.py` + `openrouter.py` | `model_router_client.py` |
| `comprehensive_logging.py` | direct copy + adapt |
| `personality_engine.py` | `prompt_synthesizer.py` |

---

## Session Resume Instructions

On session start: read this file → check status tracker → pick next ⏳ PENDING item →
read its blueprint doc → read its adoption source → plan → report → code.
