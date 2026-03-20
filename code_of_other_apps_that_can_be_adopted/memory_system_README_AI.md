# memory_system.py — README_AI.md

## Purpose
Memory System v3.0 - Robust Multi-Level Memory
===============================================

Implements a three-tier memory system:
1. Short-term: Last 5 turns (full detail)
2. Medium-term: Last 20 turns (summarized)
3. Long-term: Entire session (highly condensed)

Each turn generates AI summaries that feed into memory.
Memory is passed to the AI every turn for context.

## Technical Architecture
- **Classes**: 4 main classes
  - `TurnMemory`: Memory of a single turn.
  - `SessionMemory`: Complete memory for a session.
  - `MemorySystemV3`: Enhanced memory system with AI-powered summarization.

## Key Components
### `TurnMemory`
Memory of a single turn.
**Methods**: to_dict, from_dict

### `SessionMemory`
Complete memory for a session.
**Methods**: add_turn, _summarize_turn, _condense_summaries, _extract_facts, get_context_for_ai

### `MemorySystemV3`
Enhanced memory system with AI-powered summarization.
**Methods**: __init__, start_session, load_session, save_session, record_turn

### `AISummarizer`
Uses the game's AI to generate summaries.
**Methods**: __init__, summarize, generate_narrative_summary

## Dependencies
```
import json
import yaml
import os
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib
```

---
**Last Updated**: February 18, 2026 | v8.0.0
