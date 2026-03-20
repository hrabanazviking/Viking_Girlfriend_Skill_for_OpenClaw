# turn_processor.py — INTERFACE.md

## Class: `TurnContext`

Complete context for a single turn.

## Class: `TurnResult`

Result of processing a turn.

## Class: `RuneSystem`

Comprehensive rune system with full influence data.

### `draw_rune()`
Draw a random rune and return full influence data.

### `get_rune(name)`
Get a specific rune by name.

## Class: `TurnProcessor`

Central turn processor that coordinates all game systems.

### `prepare_turn(player_action)`
Prepare complete context for a turn.

This gathers ALL relevant state to pass to the AI.

### `build_ai_prompt(context)`
Build comprehensive AI prompt from turn context.

This creates a complete prompt with all state information.

### `generate_random_interaction(context)`
Generate a random NPC interaction based on rune and chaos.

Returns a description to include in the AI prompt, or None.

### `extract_quest_mentions(ai_response)`
Extract potential new quests from AI response.

### `process_response(context, ai_response)`
Process the AI response and extract information.

This handles:
- Summarizing the response
- Extracting new characters/quests/locations
- Detecting combat
- Tracking state changes

## Class: `QuestTracker`

Tracks quests including AI-generated ones.

### `load_all_quests()`
Load all available quests from files.

### `offer_quest(quest)`
Offer a quest to the player (not yet accepted).

Returns quest ID.

### `accept_quest(quest_id)`
Accept an offered quest.

### `decline_quest(quest_id)`
Decline an offered quest.

### `abandon_quest(quest_id)`
Abandon an active quest.

### `update_quest_progress(quest_id, update)`
Update progress on a quest.

### `get_active_quests()`
Get list of active quests.

### `get_pending_quests()`
Get list of offered but not accepted quests.

### `to_dict()`
Serialize quest state.

### `from_dict(data)`
Load quest state.

---
**Contract Version**: 1.0 | v8.0.0
