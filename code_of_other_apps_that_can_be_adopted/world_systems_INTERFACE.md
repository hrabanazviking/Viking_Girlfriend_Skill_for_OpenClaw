# world_systems.py — INTERFACE.md

## Class: `SubLocationType`

Types of sub-locations within a city.

## Class: `SubLocation`

A specific place within a city.

### `to_dict()`

### `from_dict(cls, data)`

## Class: `CityGrid`

The complete local grid for a city.

### `get_npcs_at_location(sub_location_id)`
Get all NPC IDs at a specific sub-location.

### `find_npc_location(npc_id)`
Find which sub-location an NPC is in.

### `to_dict()`

## Class: `AllyRelationship`

Tracks relationship with a potential party member.

### `adjust_loyalty(amount, reason)`
Adjust loyalty and track the change.

### `get_loyalty_description()`
Get a description of the current loyalty level.

### `should_leave_party()`
Check if this ally would leave the party.

### `would_join_party()`
Check if this ally would agree to join the party right now.

### `to_dict()`

### `from_dict(cls, data)`

## Class: `PartySystem`

Manages the player's allies and active party.

### `add_ally(npc_id, npc_name, starting_loyalty)`
Add someone as a potential ally.

### `remove_ally(npc_id)`
Remove someone from allies list.

### `add_to_party(npc_id, npc_location, player_location)`
Try to add an ally to the active party.

### `remove_from_party(npc_id)`
Remove someone from the active party.

### `get_party_members()`
Get all active party member relationships.

### `check_party_loyalty()`
Check if any party members want to leave. Returns list of (npc_id, reason).

### `apply_shared_experience(experience_type, amount)`
Apply loyalty change to all party members for shared experience.

### `to_dict()`

### `from_dict(cls, data)`

## Class: `Faction`

A group or organization with shared interests.

### `get_reputation_description()`
Get description of player's standing with this faction.

### `adjust_reputation(amount)`
Adjust reputation and return new value.

### `is_enemy()`

### `is_friend()`

### `to_dict()`

### `from_dict(cls, data)`

## Class: `FactionSystem`

Manages all factions and reputations.

### `get_faction(faction_id)`

### `add_faction(faction)`

### `adjust_reputation(faction_id, amount, reason)`
Adjust reputation with a faction.

### `get_npc_faction(npc_id)`
Find which faction an NPC belongs to.

### `get_hostile_factions()`
Get factions that are hostile to the player.

### `get_friendly_factions()`
Get factions that are friendly to the player.

### `to_dict()`

### `from_dict(cls, data)`

## Module Functions

### `create_default_uppsala_grid()`
Create the default sub-location grid for Uppsala.

### `create_default_factions()`
Create the default faction system for Uppsala.

### `get_npcs_at_sublocation(city_grid, sub_location_id, party_member_ids, all_npcs)`
Get the NPCs that should be present at a sub-location.

Args:
    city_grid: The city's sub-location grid
    sub_location_id: Current sub-location
    party_member_ids: IDs of NPCs in player's party
    all_npcs: Dictionary of all NPC data
    
Returns:
    List of NPC data dicts for those present

### `calculate_loyalty_change(action, ally, npc_personality, context)`
Calculate loyalty change based on action and NPC personality.

Args:
    action: Type of action taken
    ally: The ally relationship
    npc_personality: NPC's personality data
    context: Additional context
    
Returns:
    (change_amount, reason)

---
**Contract Version**: 1.0 | v8.0.0
