# character_memory_rag.py — README_AI.md

## Purpose
Character Memory RAG System for Norse Saga Engine
=================================================

A separate RAG system specifically for character memories and histories.
Each character can have their own memory folder that tracks:
- Interactions with the player
- Activities and events
- Relationship changes
- Backstory expansions
- Personality observations

This allows characters to "remember" past interactions and
build complex, emergent backstories through play.

## Technical Architecture
- **Classes**: 3 main classes
  - `CharacterMemory`: A single memory entry for a character.
  - `CharacterMemoryIndex`: Index of all memories for a character.
  - `CharacterMemoryRAG`: RAG system for character memories.

Structure:
    data/character_memory/
    ├── _index.yaml       
- **Functions**: 2 module-level functions

## Key Components
### `CharacterMemory`
A single memory entry for a character.
**Methods**: to_dict, from_dict

### `CharacterMemoryIndex`
Index of all memories for a character.
**Methods**: to_dict

### `CharacterMemoryRAG`
RAG system for character memories.

Structure:
    data/character_memory/
    ├── _index.yaml           # Global index of all character memories
    ├── volmarr_ragnarsson/
    │   ├── _index.yaml    
**Methods**: __init__, _load_global_index, _save_global_index, get_character_folder, add_memory

## Dependencies
```
import os
import logging
import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
```

---
**Last Updated**: February 18, 2026 | v8.0.0
