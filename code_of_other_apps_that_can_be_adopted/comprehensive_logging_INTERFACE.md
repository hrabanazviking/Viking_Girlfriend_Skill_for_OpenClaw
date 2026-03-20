# comprehensive_logging.py — INTERFACE.md

## Class: `AICallLog`

Record of a single AI call.

## Class: `TurnLog`

Complete log of a single game turn.

## Class: `ComprehensiveLogger`

Comprehensive logging system that captures everything.

### `start_turn(turn_number, player_input, player_character, location)`
Start logging a new turn.

### `end_turn(narrative_output)`
End the current turn and save.

### `log_ai_call(realm, call_type, prompt, response, context, characters, processing_time, success, error, data_sources, data_path)`
Log a complete AI call with full details.

### `log_character_data_feed(character_id, character_name, data_fed, destination)`
Log when character data is fed to AI.

### `log_memory_formation(memory_type, content, importance, related_characters, tags)`
Log memory formation events.

### `log_error(error, context)`
Log an error with full traceback.

### `log_warning(message, context)`
Log a warning.

### `log_data_path(path_elements, data_type)`
Log a data path through the system.

### `log_state_change(key, old_value, new_value)`
Log a game state change.

### `get_turn_summary(turn_number)`
Get summary of a specific turn.

### `get_session_summary()`
Get summary of entire session.

## Module Functions

### `log_ai_function(realm, call_type)`
Decorator to automatically log AI function calls.

### `get_comprehensive_logger()`
Get or create the global comprehensive logger.

### `init_comprehensive_logger(logs_dir)`
Initialize the global comprehensive logger.

---
**Contract Version**: 1.0 | v8.0.0
