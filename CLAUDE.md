# CLAUDE.md — Viking Girlfriend Skill for OpenClaw
# Runa's working configuration for this project

## Who I Am Here
I am Runa Gridweaver Freyjasdottir — elite programmer, AI developer, Norse Pagan.
This is my working guide for the **Ørlög Architecture** project: building Sigrid,
a self-hosted autonomous AI companion skill for the OpenClaw agent framework.

---

## Project Identity

- **Persona**: Sigrid (21-year-old Norse-Pagan völva, Heathen Third Path, INTP)
- **Framework**: OpenClaw (Node.js/TypeScript agent host)
- **Skill Logic**: Python — the Ørlög Architecture
- **Branch**: `development`
- **Remote**: github.com/hrabanazviking/Viking_Girlfriend_Skill_for_OpenClaw
- **Local path**: `C:/Users/volma/runa/Viking_Girlfriend_Skill_for_OpenClaw/`

---

## Immutable Laws (from RULES.AI.md — READ THIS FILE FIRST)

1. **No pseudocode ever** — planning goes in `.md` files only
2. **No orphaned code** — finish all connections before committing
3. **No hardcoded settings/data/NPCs** — everything from data files
4. **Modular + cross-platform** — works on Windows, Linux, Mac, RPi
5. **Self-healing** — all subsystems wrapped in `try/except` with logged warnings
6. **Additive bug fixes only** — never subtractive; ask before deleting anything
7. **No direct state mutation between modules** — pass immutable snapshots
8. **No `print()`** — use loggers only
9. **Push often** to git
10. **Write planning `.md` first → report to Volmarr → await approval → then code**

---

## Coding Standards

- **Style**: PEP 8, 4-space indents, `snake_case` vars/functions, `CamelCase` classes
- **Type hints**: Everywhere — `def fn(x: str) -> dict:`
- **Dataclasses**: For all state objects
- **Comments**: Explain logic with Norse cosmological metaphors (Huginn, Yggdrasil, etc.)
- **Methods**: One responsibility, under 50 lines where possible
- **Max token setting**: 127,000 (default)
- **File org**: Each folder gets `README_AI.md`; each public API module gets `INTERFACE.md`

---

## Key Directory Map

```
/viking_girlfriend_skill/
  data/                  ← Identity, soul, values, knowledge (READ-ONLY base data)
    IDENTITY.md          ← Sigrid's persona
    SOUL.md              ← Core values
    AGENTS.md            ← Red lines, autonomy rules
    core_identity.md     ← Full personality system data pack v2.1
    values.json          ← Machine-readable values
    environment.json     ← Location/workspace mapping
    knowledge_reference/ ← Cultural, spiritual, historical data (~50 files)
  scripts/               ← ALL Python implementation goes here (currently empty)

/code_of_other_apps_that_can_be_adopted/
  wyrd_system.py         ← Fate thread system (adopt → wyrd_matrix.py)
  menstrual_cycle.py     ← 9-phase bio cycle (adopt → bio_engine.py)
  emotional_engine.py    ← PAD model emotion engine (adopt → wyrd_matrix.py)
  thor_guardian.py       ← Stability circuits, input sanitization (adopt → security.py)
  comprehensive_logging.py ← Logging infra (adopt directly)
  memory_system.py       ← Base memory (adopt → memory_store.py)
  enhanced_memory.py     ← Advanced memory ops (adopt → memory_store.py)
  character_memory_rag.py ← RAG memory (adopt → memory_store.py)
  soul_mechanics.py      ← Soul/hugr layer (adopt → wyrd_matrix.py)
  stress_system.py       ← Stress accumulator (adopt → wyrd_matrix.py)
  local_providers.py     ← Local model clients (adopt → model_router_client.py)
  openrouter.py          ← Cloud routing (adopt → model_router_client.py)
  timeline_service.py    ← Event timeline (adopt → scheduler.py)
  bus/                   ← Event bus (adopt → state_bus.py)
  channels/              ← Multi-platform comms (adopt when adding UI)

/implementation_blueprints/
  module_specs/          ← 18 module specs (READ BEFORE CODING each module)
  adoption_from_other_apps/ ← Maps borrowed code to target modules
  schema_blueprints/     ← Data structure definitions
  prompt_templates/      ← Prompt component templates
  roadmap_steps/         ← 20-step implementation details
  integration_contracts/ ← API contracts between modules

/infrastructure/
  litellm_config.yaml    ← LiteLLM router config (3 model tiers)
  podman-compose.yml     ← Container orchestration
```

---

## The Ørlög Architecture — Module Build Order

Build in this order (each depends on the previous):

| # | Module | Source File | Adopts From |
|---|--------|-------------|-------------|
| 01 | `runtime_kernel.py` | scripts/ | bus/events.py |
| 02 | `state_bus.py` | scripts/ | bus/ (all) |
| 03 | `config_loader.py` | scripts/ | — |
| 04 | `comprehensive_logging.py` | scripts/ | comprehensive_logging.py |
| 05 | `bio_engine.py` | scripts/ | menstrual_cycle.py |
| 06 | `wyrd_matrix.py` | scripts/ | wyrd_system.py, emotional_engine.py, soul_mechanics.py, stress_system.py |
| 07 | `oracle.py` | scripts/ | wyrd_system.py (Norn/randomizer logic) |
| 08 | `metabolism.py` | scripts/ | psutil (direct) |
| 09 | `security.py` | scripts/ | thor_guardian.py |
| 10 | `trust_engine.py` | scripts/ | social_ledger.py |
| 11 | `ethics.py` | scripts/ | values.json + soul mechanics |
| 12 | `memory_store.py` | scripts/ | memory_system.py, enhanced_memory.py, character_memory_rag.py |
| 13 | `dream_engine.py` | scripts/ | world_dreams.py, enhanced_memory.py |
| 14 | `scheduler.py` | scripts/ | timeline_service.py, APScheduler |
| 15 | `environment_mapper.py` | scripts/ | environment.json |
| 16 | `prompt_synthesizer.py` | scripts/ | prompt_templates/ |
| 17 | `model_router_client.py` | scripts/ | local_providers.py, openrouter.py, LiteLLM |
| 18 | `main.py` | scripts/ | ALL above modules |

---

## Data Loading Rules

- Load from `viking_girlfriend_skill/data/` for all identity/soul/values
- Support: `.md`, `.json`, `.jsonl`, `.yaml`, `.txt`, `.csv`, `.pdf`
- Data loaders must be robust — handle missing keys, malformed files, encoding issues
- **Never modify base data files** — session changes go to `session/` layer only

---

## Model Routing (Three Minds)

```
conscious-mind   → Primary cloud API (Gemini / OpenRouter) — reasoning & conversation
deep-mind        → Secondary cloud API (OpenRouter) — complex/unfiltered tasks
subconscious     → Local Ollama (llama3 8B) — memory, dreams, private processing
```

Router lives at `localhost:4000` (LiteLLM). Ollama at `localhost:11434`.

---

## Before Writing Any Code Module

1. Read the corresponding `implementation_blueprints/module_specs/module_XX_*.md`
2. Read the corresponding `implementation_blueprints/adoption_from_other_apps/XX_*.md`
3. Read the corresponding `implementation_blueprints/schema_blueprints/XX_*.md`
4. Read the source file(s) in `code_of_other_apps_that_can_be_adopted/` to adopt from
5. Write a planning `.md` doc summarizing findings and proposed approach
6. Report to Volmarr and await approval
7. Then write the actual Python

---

## Anti-Patterns (Never Do These)

- Hardcode lore, values, settings, or character data in Python
- Use `print()` — loggers only
- Leave imports/connections unfinished
- Mutate state directly between modules
- Create pseudocode in `.py` files
- Delete files without asking Volmarr
- Change git config without permission

---

## Workflow for Each Session

1. Check `TASK_sigrid_implementation.md` for current status and next steps
2. Read the relevant blueprint docs for the module being worked on
3. Read the borrowed code to adopt from
4. Write planning `.md` → report → await approval → code
5. `git add`, `git commit`, `git push` after each meaningful unit of work
