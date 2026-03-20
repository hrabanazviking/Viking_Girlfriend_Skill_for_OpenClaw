# turn_processor.py — README_AI.md

## Purpose
Turn Processor v3.0 - Comprehensive Turn Management
====================================================

Handles everything that happens each turn:
1. Draw rune and prepare influence data
2. Gather complete state context
3. Build AI prompt with all context
4. Process AI response
5. Run housekeeping (extract characters, quests, locations)
6. Update memory systems
7. Track quest progress
8. Generate random interactions based on rune

This is the central coordinator that makes all systems work tog

## Technical Architecture
- **Classes**: 5 main classes
  - `TurnContext`: Complete context for a single turn.
  - `TurnResult`: Result of processing a turn.
  - `RuneSystem`: Comprehensive rune system with full influence data.

## Key Components
### `TurnContext`
Complete context for a single turn.

### `TurnResult`
Result of processing a turn.

### `RuneSystem`
Comprehensive rune system with full influence data.
**Methods**: __init__, _load_runes, draw_rune, get_rune, _expand_rune

### `TurnProcessor`
Central turn processor that coordinates all game systems.
**Methods**: __init__, prepare_turn, build_ai_prompt, generate_random_interaction, extract_quest_mentions

### `QuestTracker`
Tracks quests including AI-generated ones.
**Methods**: __init__, load_all_quests, offer_quest, accept_quest, decline_quest

## Dependencies
```
import random
import re
import yaml
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, field, asdict
```

---
**Last Updated**: February 18, 2026 | v8.0.0
