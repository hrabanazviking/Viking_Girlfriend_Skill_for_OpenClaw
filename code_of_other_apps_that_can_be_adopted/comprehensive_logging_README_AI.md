# comprehensive_logging.py — README_AI.md

## Purpose
Comprehensive Logging System for Norse Saga Engine
===================================================

Logs EVERY text input and output from all AI and scripted functions.
Includes:
- Full AI prompts and responses
- Data path tracing through Yggdrasil realms
- Error tracking with stack traces
- Turn-by-turn session logging
- Memory formation events
- Character data feeds

All logs are stored in the logs/ directory.

## Technical Architecture
- **Classes**: 3 main classes
  - `AICallLog`: Record of a single AI call.
  - `TurnLog`: Complete log of a single game turn.
  - `ComprehensiveLogger`: Comprehensive logging system that captures everything.
- **Functions**: 3 module-level functions

## Key Components
### `AICallLog`
Record of a single AI call.

### `TurnLog`
Complete log of a single game turn.

### `ComprehensiveLogger`
Comprehensive logging system that captures everything.
**Methods**: __init__, _setup_loggers, _get_call_id, start_turn, end_turn

## Dependencies
```
import logging
import json
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from functools import wraps
from dataclasses import dataclass, field, asdict
import threading
```

---
**Last Updated**: February 18, 2026 | v8.0.0
