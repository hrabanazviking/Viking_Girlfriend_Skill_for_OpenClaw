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

### Phase 1 — Foundation (Tracks A) — ✅ COMPLETE (2026-03-20)
| Step | Module | Status | Notes |
|------|--------|--------|-------|
| 01 | System Prep / Dependencies | ✅ DONE | Windows 11 env fully set up |
| 02 | Container Deploy | ⏸ DEFERRED | No Podman on Win; deploy on Linux laptop later |
| 03 | Local Model Provision | ⏸ DEFERRED | Ollama app installed; pull llama3 when on Linux |
| 04 | Skill Manifest (SKILL.md) | ✅ DONE | viking_girlfriend_skill/SKILL.md created |
| 05 | Core Python Scaffolding | ✅ DONE | scripts/ dir, main.py, requirements.txt all created |
| — | `crash_reporting.py` | ✅ DONE | Adopted + adapted from borrowed code |
| — | `comprehensive_logging.py` | ✅ DONE | Adopted + adapted (InteractionLog replaces TurnLog) |
| — | `config_loader.py` | ✅ DONE | New — JSON/JSONL/YAML/MD/TXT/CSV/PDF loader |
| — | `state_bus.py` | ✅ DONE | Adopted from bus/ — InboundEvent, OutboundEvent, StateEvent |
| — | `runtime_kernel.py` | ✅ DONE | New — lifecycle, heartbeat, module registry |
| — | `main.py` | ✅ DONE | Entry point, async runtime loop |

### Phase 2 — State Machines (Track B)
| Step | Module | Status | Notes |
|------|--------|--------|-------|
| 06 | `wyrd_matrix.py` | ✅ DONE | PAD vector + SoulLayer + StressAccumulator + bio integration |
| 07 | `bio_engine.py` | ✅ DONE | Module 04, adopts menstrual_cycle.py — real-date cycle + biorhythms |
| 08 | `oracle.py` | ✅ DONE | Rune + Tarot (Book T/GD 78-card) + I Ching + Norn atmosphere |
| 09 | `metabolism.py` | ✅ DONE | psutil → somatic descriptors (mental_load, body_warmth, memory_pressure, weariness, vitality) |

### Phase 3 — Mind & Shield (Track C)
| Step | Module | Status | Notes |
|------|--------|--------|-------|
| 10 | `security.py` | ✅ DONE | Circuit-breaker + sanitize + path guard + secret compare; adopts thor_guardian.py |
| 11 | `trust_engine.py` | ✅ DONE | Gebo ledger: trust/intimacy/reliability/friction scores, text inference, friction decay |
| 12 | `ethics.py` | ✅ DONE | Loads values.json + SOUL.md; value/taboo eval, context detection, rolling alignment score |
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

## Immediate Next Steps — Phase 2: State Machines

1. ~~**Read** `menstrual_cycle.py` → **Write** `bio_engine.py`~~ ✅ DONE (2026-03-20)
2. ~~**Read** source files → **Write** `wyrd_matrix.py`~~ ✅ DONE (2026-03-20)
7. **Write** `scripts/oracle.py` — daily deterministic Rune/Tarot/I Ching seed
8. ~~**Write** `scripts/metabolism.py` — psutil hardware → somatic sensations~~ ✅ DONE (2026-03-20)

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
