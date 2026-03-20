# data_system.py — INTERFACE.md

## Class: `DataLoader`

Universal data loader supporting multiple formats.

### `load_file(filepath)`
Load data from any supported file format.

Args:
    filepath: Path to the file
    
Returns:
    Loaded data (dict for YAML/JSON, list of dicts for JSONL)

### `iter_jsonl(filepath)`
Iterate over JSONL file without loading all into memory.

Useful for very large files.

### `save_file(filepath, data, format)`
Save data to file.

Args:
    filepath: Path to save to
    data: Data to save
    format: 'yaml', 'json', or 'jsonl'

### `append_jsonl(filepath, data)`
Append a single record to a JSONL file.

## Class: `ChartLoader`

Loads chart/table data from multiple file formats.

Charts can be:
- YAML with 'entries' or 'items' list
- JSON with array or object with entries
- JSONL with one entry per line

### `load_all_charts()`
Load all charts from the charts directory.

### `load_chart(filepath)`
Load a single chart file.

Returns the list of entries.

### `get_raw_chart(name)`
Get raw chart data by name (for reference charts without standard entries).

### `get_chart(name)`
Get a chart by name.

### `get_random_entry(chart_name)`
Get a random entry from a chart.

### `get_entries_by_field(chart_name, field, value)`
Get entries matching a field value.

### `sample_entries(chart_name, count)`
Get random sample of entries.

### `list_charts()`
List all loaded chart names.

### `get_chart_info(name)`
Get metadata about a chart.

## Class: `CharacterDatabase`

Robust character data management with schema migration.

### `load_character(char_id)`
Load a character by ID, checking all locations.

### `save_character(character, auto_generated)`
Save a character.

### `list_all_characters()`
List all character IDs.

### `batch_migrate_all()`
Migrate all characters to current schema.

Returns number of characters migrated.

### `clear_cache()`
Clear the character cache.

## Class: `LocationDatabase`

Robust location data management.

### `load_location(loc_id)`
Load a location by ID.

### `save_location(location, auto_generated)`
Save a location.

### `list_all_locations()`
List all location IDs.

## Class: `DataManager`

Central data management hub.

Coordinates all data systems for consistent access.

### `get_chart(name)`
Get a chart by name.

### `get_character(char_id)`
Get a character by ID.

### `save_character(character, auto)`
Save a character.

### `get_location(loc_id)`
Get a location by ID.

### `save_location(location, auto)`
Save a location.

### `get_random_chart_entry(chart_name)`
Get random entry from a chart.

### `run_schema_migration()`
Run schema migration on all characters.

---
**Contract Version**: 1.0 | v8.0.0
