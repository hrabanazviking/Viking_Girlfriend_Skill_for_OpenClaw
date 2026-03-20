# enhanced_memory.py — README_AI.md

## Purpose
AI-Enhanced Memory and Turn Summary System
===========================================

Replaces vague memory events like "Mystical event" with accurate,
AI-generated summaries of exactly what happened each turn.

Every turn summary includes:
- WHO: All characters involved
- WHAT: Specific actions taken
- WHEN: Turn number and time of day
- WHERE: Exact location
- WHY: Motivations and context
- HOW: Methods and outcomes

The AI generates these summaries, ensuring accuracy and detail.

## Technical Architecture
- **Classes**: 3 main classes
  - `TurnSummary`: A comprehensive summary of a single turn.
  - `AITurnSummarizer`: Uses AI to generate accurate, detailed turn summaries.

No more vague "Mystical event" or "Quest-rel
  - `EnhancedMemoryManager`: Enhanced memory manager that uses AI for accurate event tracking.

Replaces the old vague event syst
- **Functions**: 1 module-level functions

## Key Components
### `TurnSummary`
A comprehensive summary of a single turn.
**Methods**: to_dict, to_memory_text

### `AITurnSummarizer`
Uses AI to generate accurate, detailed turn summaries.

No more vague "Mystical event" or "Quest-related event" summaries.
Every turn gets a proper, specific summary of what actually happened.
**Methods**: __init__, summarize_turn, _parse_ai_response, _basic_summary, get_recent_summaries

### `EnhancedMemoryManager`
Enhanced memory manager that uses AI for accurate event tracking.

Replaces the old vague event system with proper turn summaries.
**Methods**: __init__, start_session, process_turn, _create_memories_from_summary, add_character_memory

## Dependencies
```
import logging
import json
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
```

---
**Last Updated**: February 18, 2026 | v8.0.0
