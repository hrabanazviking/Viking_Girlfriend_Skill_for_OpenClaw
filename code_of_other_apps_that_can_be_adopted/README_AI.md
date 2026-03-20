# Game Systems — README_AI

This folder contains 19 subsystems that together form the mechanical and narrative heart of the engine. Each system is a Python file; they are all stateless (except for internal caches) and are orchestrated by `core/engine.py`.

## Categories

### Core Turn Processing
- `turn_processor.py` – coordinates the turn (v3.0)
- `memory_system.py` – three‑tier memory (short/medium/long)
- `enhanced_memory.py` – AI‑generated 5W+H summaries
- `housekeeping.py` – auto‑generates characters, quests, locations from narration
- `data_system.py` – universal YAML/JSON/JSONL loader

### Mystical & Fate
- `chaos_system.py` – advanced Mythic 2E chaos with moon, sabbat, action modifiers
- `wyrd_system.py` – Three Wells fate tracking (Urd/Mimir/Hvergelmir)
- `rune_intent.py` – short‑term fate (1‑3 turns) via rune spreads
- `fate_threads.py` – symbolic recurrence (5‑10 turns)
- `saga_gravity.py` – long‑term narrative anchors (10‑50+ turns)
- `story_phase.py` – monomyth arc direction (10‑20 turns per phase)
- `world_will.py` – world consciousness desires and tones (8‑12 turn shifts)
- `mythic_age.py` – era‑level world atmosphere (20+ turns per age)
- `mythic_mirror.py` – player archetype detection and reflection
- `world_dreams.py` – between‑turn atmospheric dream visions (every 7 turns)

### Mechanics & World
- `dice_system.py` – D&D 5E dice mechanics
- `rag_system.py` – BM25 retrieval for lore
- `character_memory_rag.py` – per‑NPC memory retrieval
- `comprehensive_logging.py` – deep observability
- `world_systems.py` – city grids, party, factions, NPC behavior
- `mead_hall_system.py` – dynamic population of skalds, bondmaids, patrons

### Emotional & Stress
- `emotional_engine.py` – per‑character Plutchik wheel channels + decay (Tier 2)
- `stress_system.py` – cumulative stress tracking + threshold events

### Prompt Quality (T3-A / T3-B)
- `context_optimizer.py` – prepend "State of the Game" SOTG block to every AI prompt (arXiv:2603.09022 MEMO)
- `memory_hardening.py` – identity drift detection + elastic memory windows (arXiv:2603.09043 / arXiv:2603.09716)
- `memory_query_engine.py` – structured Muninn query surface; supports elastic limit via game_state

## Interaction
All systems are called from `engine.py` at specific points in the turn. They never call each other directly (to avoid circular dependencies). Data is exchanged via `GameState` and return values. Each subsystem is wrapped in `try/except` for graceful degradation.