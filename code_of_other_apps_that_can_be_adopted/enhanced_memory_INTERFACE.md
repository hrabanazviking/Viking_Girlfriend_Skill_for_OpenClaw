# enhanced_memory.py — INTERFACE.md

## Class: `TurnSummary`

A comprehensive summary of a single turn.

### `to_dict()`

### `to_memory_text()`
Convert to text suitable for AI memory context.

## Class: `AITurnSummarizer`

Uses AI to generate accurate, detailed turn summaries.

No more vague "Mystical event" or "Quest-related event" summaries.
Every turn gets a proper, specific summary of what actually happened.

### `summarize_turn(turn_number, player_input, narrative, location, time_of_day, characters_present, state_changes, character_data)`
Generate a comprehensive turn summary using AI.

### `get_recent_summaries(count)`
Get the most recent turn summaries.

### `get_summaries_for_ai(count)`
Get formatted summaries for AI context.

### `get_summary_by_tag(tag)`
Get all summaries with a specific tag.

## Class: `EnhancedMemoryManager`

Enhanced memory manager that uses AI for accurate event tracking.

Replaces the old vague event system with proper turn summaries.

### `start_session(session_id, player_character, starting_location)`
Start a new memory session.

### `process_turn(turn_number, player_input, narrative, game_state)`
Process a complete turn and generate memories.

This is the main entry point for turn processing.

### `add_character_memory(character_id, event_type, description, importance)`
Add a memory related to a character.

### `add_location_memory(location_id, event_type, description, importance)`
Add a memory related to a location.

### `add_relationship_memory(character1, character2, change_type, description)`
Add a memory about relationship between characters.

### `get_character_context(character_id, max_memories)`
Get memory context for a character.

### `get_location_context(location_id, max_memories)`
Get memory context for a location.

### `get_full_context_for_ai(game_state, max_items)`
Get complete memory context for AI processing.

## Module Functions

### `create_enhanced_memory_manager(llm_callable, data_path)`
Create an enhanced memory manager.

---
**Contract Version**: 1.0 | v8.0.0
