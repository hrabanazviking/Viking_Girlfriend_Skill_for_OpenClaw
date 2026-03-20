# wyrd_system.py — INTERFACE.md

## Class: `WyrdType`

Types of wyrd (fate) threads.

## Class: `NornDomain`

The three Norns and their domains.

## Class: `WyrdThread`

A single thread of fate/wyrd.

### `to_dict()`

## Class: `WellState`

State of a sacred well.

## Class: `UrdWell`

Urðarbrunnr - The Well of the Past

Records everything that has happened.
Cannot be changed, only added to.
Forms the foundation of fate.

### `record(thread)`
Record a thread of fate in the well of the past.

### `get_karma_history()`
Get karma changes over time.

### `get_significant_past(limit)`
Get most significant past events.

## Class: `MimirWell`

Mímisbrunnr - The Well of Wisdom/Present

Reflects the current state of all things.
Where knowledge and insight dwell.
Odin gave an eye for a drink from this well.

### `reflect(game_state)`
Reflect the current state in the well.
Returns wisdom about the present moment.

### `update_relationship(char1, char2, change)`
Update relationship between two characters.

### `add_oath(oath)`
Record an oath made.

### `speak_wisdom(game_state)`
Speak wisdom about the present moment.
Called by /wyrd command to display Mimir's wisdom.

## Class: `HvergelmiWell`

Hvergelmir - The Roaring Cauldron of Potential

Where possibility churns.
The source of all rivers (outcomes).
Níðhöggr gnaws at the roots here.

### `divine(context)`
Divine the future possibilities.
Returns probability-weighted outcomes.

### `add_prophecy(content, conditions)`
Add a prophecy that may come to pass.

### `check_prophecies(current_state)`
Check if any prophecies should be fulfilled.

### `speak_prophecy(context)`
Speak prophecy about the future.
Called by /wyrd command to display Skuld's prophecy.

## Class: `WyrdSystem`

The complete Wyrd system integrating all three wells.

All game events flow through this system:
1. Events are recorded in Urðarbrunnr (past)
2. Current state is reflected in Mímisbrunnr (present)
3. Possibilities are calculated in Hvergelmir (future)

### `process_event(event_type, content, characters, location, turn_number, importance, karma_shift, chaos_impact, caused_by)`
Process an event through all three wells.

This is the main entry point for the Wyrd system.
Every significant game event should flow through here.

### `get_current_wyrd(game_state)`
Get the complete wyrd state for AI processing.

Returns a summary of past, present, and future threads
that should inform AI decisions.

### `process_turn_summary(turn_number, player_action, narrative_result, characters_involved, location, significant_events)`
Process a complete turn through the Wyrd system.

This should be called at the end of each turn to record
everything that happened.

### `get_wyrd_summary_for_ai(max_past)`
Get a text summary of Wyrd for AI consumption.

This should be included in AI prompts to inform behavior.

### `save_state(filepath)`
Save the complete Wyrd state.

## Module Functions

### `create_wyrd_system(data_path)`
Create a Wyrd system instance.

---
**Contract Version**: 1.0 | v8.0.0
