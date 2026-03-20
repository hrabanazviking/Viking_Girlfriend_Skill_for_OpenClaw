# world_systems.py — README_AI.md

## Purpose
World Systems - Location Grid, Party, Loyalty, and Factions
============================================================

Implements:
1. Local Grid System - Sub-locations within cities (buildings, areas)
2. Party System - Allies list + active party management
3. Loyalty System - NPC relationship tracking
4. Faction System - Group reputation tracking
5. NPC Behavior Rules - Social appropriateness

Key Principles:
- NPCs stay in their designated locations, don't follow you
- Party members must be 

## Technical Architecture
- **Classes**: 7 main classes
  - `SubLocationType`: Types of sub-locations within a city.
  - `SubLocation`: A specific place within a city.
  - `CityGrid`: The complete local grid for a city.
- **Functions**: 4 module-level functions

## Key Components
### `SubLocationType`
Types of sub-locations within a city.

### `SubLocation`
A specific place within a city.
**Methods**: to_dict, from_dict

### `CityGrid`
The complete local grid for a city.
**Methods**: get_npcs_at_location, find_npc_location, to_dict

### `AllyRelationship`
Tracks relationship with a potential party member.
**Methods**: adjust_loyalty, get_loyalty_description, should_leave_party, would_join_party, to_dict

### `PartySystem`
Manages the player's allies and active party.
**Methods**: add_ally, remove_ally, add_to_party, remove_from_party, get_party_members

## Dependencies
```
import random
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime
```

---
**Last Updated**: February 18, 2026 | v8.0.0
