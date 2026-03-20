# wyrd_system.py — README_AI.md

## Purpose
Wyrd System - The Flow of Fate Through the Three Sacred Wells
=============================================================

In Norse cosmology, the Norns weave the threads of fate at the base of
Yggdrasil, where three sacred wells connect all things:

1. Urðarbrunnr (Well of Urd/Wyrd) - The Past
   - What has been, cannot be undone
   - Records all events, actions, choices
   - The foundation upon which fate is built

2. Mímisbrunnr (Mímir's Well) - The Present/Wisdom
   - Current state and kno

## Technical Architecture
- **Classes**: 8 main classes
  - `WyrdType`: Types of wyrd (fate) threads.
  - `NornDomain`: The three Norns and their domains.
  - `WyrdThread`: A single thread of fate/wyrd.
- **Functions**: 1 module-level functions

## Key Components
### `WyrdType`
Types of wyrd (fate) threads.

### `NornDomain`
The three Norns and their domains.

### `WyrdThread`
A single thread of fate/wyrd.
**Methods**: to_dict

### `WellState`
State of a sacred well.

### `UrdWell`
Urðarbrunnr - The Well of the Past

Records everything that has happened.
Cannot be changed, only added to.
Forms the foundation of fate.
**Methods**: __init__, record, _urd_commentary, get_karma_history, get_significant_past

## Dependencies
```
import logging
import json
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from enum import Enum
import random
```

---
**Last Updated**: February 18, 2026 | v8.0.0
