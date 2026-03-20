# data_system.py — README_AI.md

## Purpose
Data System v3.0 - Robust Future-Proof Data Management
=======================================================

Supports:
- YAML files
- JSON files
- JSONL files (JSON Lines - one JSON object per line)
- Automatic schema migration
- Data validation
- Extensible fields

All data operations go through this system for consistency.

## Technical Architecture
- **Classes**: 5 main classes
  - `DataLoader`: Universal data loader supporting multiple formats.
  - `ChartLoader`: Loads chart/table data from multiple file formats.

Charts can be:
- YAML with 'entries' or 'items' 
  - `CharacterDatabase`: Robust character data management with schema migration.

## Key Components
### `DataLoader`
Universal data loader supporting multiple formats.
**Methods**: load_file, _load_yaml, _load_json, _load_jsonl, iter_jsonl

### `ChartLoader`
Loads chart/table data from multiple file formats.

Charts can be:
- YAML with 'entries' or 'items' list
- JSON with array or object with entries
- JSONL with one entry per line
**Methods**: __init__, load_all_charts, load_chart, get_raw_chart, get_chart

### `CharacterDatabase`
Robust character data management with schema migration.
**Methods**: __init__, load_character, save_character, _migrate_schema, _deep_merge

### `LocationDatabase`
Robust location data management.
**Methods**: __init__, load_location, save_location, list_all_locations

### `DataManager`
Central data management hub.

Coordinates all data systems for consistent access.
**Methods**: __init__, get_chart, get_character, save_character, get_location

## Dependencies
```
import json
import yaml
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Iterator
from datetime import datetime
import logging
```

---
**Last Updated**: February 18, 2026 | v8.0.0
