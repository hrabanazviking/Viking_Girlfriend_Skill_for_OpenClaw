# character_memory_rag.py — INTERFACE.md

## Class: `CharacterMemory`

A single memory entry for a character.

### `to_dict()`

### `from_dict(cls, data)`

## Class: `CharacterMemoryIndex`

Index of all memories for a character.

### `to_dict()`

## Class: `CharacterMemoryRAG`

RAG system for character memories.

Structure:
    data/character_memory/
    ├── _index.yaml           # Global index of all character memories
    ├── volmarr_ragnarsson/
    │   ├── _index.yaml       # Character-specific index
    │   ├── memories.yaml     # All memories in one file
    │   └── backstory.yaml    # Expanded backstory elements
    ├── inga_the_fair/
    │   ├── _index.yaml
    │   ├── memories.yaml
    │   └── backstory.yaml
    └── ...

### `get_character_folder(character_id)`
Get or create a character's memory folder.

### `add_memory(character_id, character_name, memory_type, content, session_id, turn_number, related_characters, location, importance, tags)`
Add a memory for a character.

Args:
    character_id: Character's unique ID
    character_name: Character's display name
    memory_type: Type of memory (interaction, observation, event, relationship, backstory)
    content: The memory content
    session_id: Current session ID
    turn_number: Current turn number
    related_characters: Other characters involved
    location: Where the memory occurred
    importance: Importance level 1-5
    tags: Additional tags for searching
    
Returns:
    True if successful

### `get_memories(character_id, memory_type, limit, min_importance, tags, related_character)`
Retrieve memories for a character.

Args:
    character_id: Character's unique ID
    memory_type: Filter by type (optional)
    limit: Maximum memories to return
    min_importance: Minimum importance level
    tags: Filter by tags (any match)
    related_character: Filter by related character
    
Returns:
    List of matching memories

### `search_memories(query, character_id, limit)`
Search memories across all or specific character(s).

Args:
    query: Search query
    character_id: Limit to specific character (optional)
    limit: Maximum results
    
Returns:
    List of (character_id, memory, relevance_score) tuples

### `get_memory_summary(character_id)`
Get a summary of a character's memories.

### `add_backstory_element(character_id, character_name, element_type, content, source)`
Add or expand a character's backstory.

Args:
    character_id: Character's unique ID
    character_name: Character's display name
    element_type: Type of backstory element (childhood, family, event, secret, etc.)
    content: The backstory content
    source: Where this came from (gameplay, ai_generated, manual)
    
Returns:
    True if successful

### `get_backstory(character_id)`
Get a character's expanded backstory.

### `build_context_for_character(character_id, include_backstory, include_recent, max_memories)`
Build a context string for AI prompting about this character.

Args:
    character_id: Character's unique ID
    include_backstory: Include backstory elements
    include_recent: Include recent memories
    max_memories: Maximum memories to include
    
Returns:
    Formatted context string

### `auto_generate_memory_from_turn(character_id, character_name, narrative, player_action, session_id, turn_number, location, player_name)`
Automatically extract and store memories from a turn's narrative.

Args:
    character_id: NPC's character ID
    character_name: NPC's name
    narrative: The AI-generated narrative
    player_action: What the player did
    session_id: Current session
    turn_number: Current turn
    location: Current location
    player_name: Player character's name
    
Returns:
    List of memory types added

### `get_all_character_ids()`
Get list of all characters with memories.

### `export_character_memories(character_id)`
Export all memories for a character as a dict.

## Module Functions

### `create_memory_system(data_path)`
Create and return a CharacterMemoryRAG instance.

### `extract_character_mentions(text, known_characters)`
Extract which known characters are mentioned in text.

Args:
    text: Text to search
    known_characters: List of character names to look for
    
Returns:
    List of mentioned character names

---
**Contract Version**: 1.0 | v8.0.0
