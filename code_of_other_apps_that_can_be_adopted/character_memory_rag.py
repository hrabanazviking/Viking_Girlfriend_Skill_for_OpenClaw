"""
Character Memory RAG System for Norse Saga Engine
=================================================

A separate RAG system specifically for character memories and histories.
Each character can have their own memory folder that tracks:
- Interactions with the player
- Activities and events
- Relationship changes
- Backstory expansions
- Personality observations

This allows characters to "remember" past interactions and
build complex, emergent backstories through play.
"""

import logging
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class CharacterMemory:
    """A single memory entry for a character."""
    timestamp: str
    session_id: str
    turn_number: int
    memory_type: str  # interaction, observation, event, relationship, backstory
    content: str
    related_characters: List[str] = field(default_factory=list)
    location: str = ""
    importance: int = 1  # 1-5, higher = more important
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "session_id": self.session_id,
            "turn_number": self.turn_number,
            "memory_type": self.memory_type,
            "content": self.content,
            "related_characters": self.related_characters,
            "location": self.location,
            "importance": self.importance,
            "tags": self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CharacterMemory":
        return cls(
            timestamp=data.get("timestamp", ""),
            session_id=data.get("session_id", ""),
            turn_number=data.get("turn_number", 0),
            memory_type=data.get("memory_type", "observation"),
            content=data.get("content", ""),
            related_characters=data.get("related_characters", []),
            location=data.get("location", ""),
            importance=data.get("importance", 1),
            tags=data.get("tags", [])
        )


@dataclass
class CharacterMemoryIndex:
    """Index of all memories for a character."""
    character_id: str
    character_name: str
    total_memories: int = 0
    last_updated: str = ""
    memory_types: Dict[str, int] = field(default_factory=dict)
    related_characters: Dict[str, int] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "character_id": self.character_id,
            "character_name": self.character_name,
            "total_memories": self.total_memories,
            "last_updated": self.last_updated,
            "memory_types": self.memory_types,
            "related_characters": self.related_characters
        }


class CharacterMemoryRAG:
    """
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
    """
    
    def __init__(self, data_path: str):
        self.data_path = Path(data_path)
        self.memory_root = self.data_path / "character_memory"
        self.memory_root.mkdir(parents=True, exist_ok=True)
        
        # Global index
        self.global_index: Dict[str, CharacterMemoryIndex] = {}
        self._load_global_index()
        
        # Memory cache
        self._memory_cache: Dict[str, List[CharacterMemory]] = {}
    
    def _load_global_index(self):
        """Load the global index of all character memories."""
        index_file = self.memory_root / "_index.yaml"
        
        if index_file.exists():
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f) or {}
                
                for char_id, char_data in data.get("characters", {}).items():
                    self.global_index[char_id] = CharacterMemoryIndex(
                        character_id=char_id,
                        character_name=char_data.get("character_name", char_id),
                        total_memories=char_data.get("total_memories", 0),
                        last_updated=char_data.get("last_updated", ""),
                        memory_types=char_data.get("memory_types", {}),
                        related_characters=char_data.get("related_characters", {})
                    )
            except Exception as e:
                logger.error(f"Error loading global memory index: {e}")
    
    def _save_global_index(self):
        """Save the global index."""
        index_file = self.memory_root / "_index.yaml"
        
        data = {
            "version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "characters": {
                char_id: idx.to_dict()
                for char_id, idx in self.global_index.items()
            }
        }
        
        try:
            with open(index_file, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
        except Exception as e:
            logger.error(f"Error saving global memory index: {e}")
    
    def get_character_folder(self, character_id: str) -> Path:
        """Get or create a character's memory folder."""
        folder = self.memory_root / character_id.lower().replace(" ", "_")
        folder.mkdir(parents=True, exist_ok=True)
        return folder
    
    def add_memory(
        self,
        character_id: str,
        character_name: str,
        memory_type: str,
        content: str,
        session_id: str = "",
        turn_number: int = 0,
        related_characters: List[str] = None,
        location: str = "",
        importance: int = 1,
        tags: List[str] = None
    ) -> bool:
        """
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
        """
        try:
            char_folder = self.get_character_folder(character_id)
            memories_file = char_folder / "memories.yaml"
            
            # Create memory entry
            memory = CharacterMemory(
                timestamp=datetime.now().isoformat(),
                session_id=session_id,
                turn_number=turn_number,
                memory_type=memory_type,
                content=content,
                related_characters=related_characters or [],
                location=location,
                importance=importance,
                tags=tags or []
            )
            
            # Load existing memories
            memories = []
            if memories_file.exists():
                try:
                    with open(memories_file, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f) or {}
                    memories = [CharacterMemory.from_dict(m) for m in data.get("memories", [])]
                except Exception as e:
                    logger.warning(f"Error loading memories for {character_id}: {e}")
            
            # Add new memory
            memories.append(memory)
            
            # Save memories
            data = {
                "character_id": character_id,
                "character_name": character_name,
                "last_updated": datetime.now().isoformat(),
                "memories": [m.to_dict() for m in memories]
            }
            
            with open(memories_file, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
            
            # Update character index
            char_index_file = char_folder / "_index.yaml"
            if character_id not in self.global_index:
                self.global_index[character_id] = CharacterMemoryIndex(
                    character_id=character_id,
                    character_name=character_name
                )
            
            idx = self.global_index[character_id]
            idx.total_memories = len(memories)
            idx.last_updated = datetime.now().isoformat()
            idx.memory_types[memory_type] = idx.memory_types.get(memory_type, 0) + 1
            
            for related in (related_characters or []):
                idx.related_characters[related] = idx.related_characters.get(related, 0) + 1
            
            # Save character index
            with open(char_index_file, 'w', encoding='utf-8') as f:
                yaml.dump(idx.to_dict(), f, allow_unicode=True, default_flow_style=False)
            
            # Update global index
            self._save_global_index()
            
            # Update cache
            self._memory_cache[character_id] = memories
            
            logger.info(f"Added {memory_type} memory for {character_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding memory for {character_id}: {e}")
            return False
    
    def get_memories(
        self,
        character_id: str,
        memory_type: str = None,
        limit: int = 50,
        min_importance: int = 1,
        tags: List[str] = None,
        related_character: str = None
    ) -> List[CharacterMemory]:
        """
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
        """
        # Check cache first
        if character_id in self._memory_cache:
            memories = self._memory_cache[character_id]
        else:
            # Load from file
            char_folder = self.get_character_folder(character_id)
            memories_file = char_folder / "memories.yaml"
            
            if not memories_file.exists():
                return []
            
            try:
                with open(memories_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f) or {}
                memories = [CharacterMemory.from_dict(m) for m in data.get("memories", [])]
                self._memory_cache[character_id] = memories
            except Exception as e:
                logger.error(f"Error loading memories for {character_id}: {e}")
                return []
        
        # Filter memories
        filtered = []
        for m in memories:
            if memory_type and m.memory_type != memory_type:
                continue
            if m.importance < min_importance:
                continue
            if tags and not any(t in m.tags for t in tags):
                continue
            if related_character and related_character not in m.related_characters:
                continue
            filtered.append(m)
        
        # Sort by importance (descending) then by timestamp (descending)
        filtered.sort(key=lambda m: (m.importance, m.timestamp), reverse=True)
        
        return filtered[:limit]
    
    def search_memories(
        self,
        query: str,
        character_id: str = None,
        limit: int = 10
    ) -> List[Tuple[str, CharacterMemory, float]]:
        """
        Search memories across all or specific character(s).
        
        Args:
            query: Search query
            character_id: Limit to specific character (optional)
            limit: Maximum results
            
        Returns:
            List of (character_id, memory, relevance_score) tuples
        """
        results = []
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        # Determine which characters to search
        if character_id:
            char_ids = [character_id]
        else:
            char_ids = list(self.global_index.keys())
        
        for char_id in char_ids:
            memories = self.get_memories(char_id, limit=100)
            
            for memory in memories:
                content_lower = memory.content.lower()
                
                # Simple relevance scoring
                score = 0.0
                
                # Exact phrase match
                if query_lower in content_lower:
                    score += 2.0
                
                # Word matches
                content_words = set(content_lower.split())
                matches = query_words.intersection(content_words)
                score += len(matches) * 0.5
                
                # Tag matches
                if any(query_lower in tag.lower() for tag in memory.tags):
                    score += 1.0
                
                # Importance boost
                score *= (1 + memory.importance * 0.1)
                
                if score > 0:
                    results.append((char_id, memory, score))
        
        # Sort by score
        results.sort(key=lambda x: x[2], reverse=True)
        
        return results[:limit]
    
    def get_memory_summary(self, character_id: str) -> Dict[str, Any]:
        """Get a summary of a character's memories."""
        if character_id not in self.global_index:
            return {"character_id": character_id, "has_memories": False}
        
        idx = self.global_index[character_id]
        memories = self.get_memories(character_id, limit=5, min_importance=3)
        
        return {
            "character_id": character_id,
            "character_name": idx.character_name,
            "has_memories": True,
            "total_memories": idx.total_memories,
            "memory_types": idx.memory_types,
            "related_characters": idx.related_characters,
            "recent_important": [m.content[:100] for m in memories]
        }
    
    def add_backstory_element(
        self,
        character_id: str,
        character_name: str,
        element_type: str,
        content: str,
        source: str = "gameplay"
    ) -> bool:
        """
        Add or expand a character's backstory.
        
        Args:
            character_id: Character's unique ID
            character_name: Character's display name
            element_type: Type of backstory element (childhood, family, event, secret, etc.)
            content: The backstory content
            source: Where this came from (gameplay, ai_generated, manual)
            
        Returns:
            True if successful
        """
        try:
            char_folder = self.get_character_folder(character_id)
            backstory_file = char_folder / "backstory.yaml"
            
            # Load existing backstory
            backstory = {"elements": []}
            if backstory_file.exists():
                try:
                    with open(backstory_file, 'r', encoding='utf-8') as f:
                        backstory = yaml.safe_load(f) or {"elements": []}
                except Exception:
                    pass
            
            # Add new element
            element = {
                "type": element_type,
                "content": content,
                "source": source,
                "added": datetime.now().isoformat()
            }
            backstory["elements"].append(element)
            backstory["character_id"] = character_id
            backstory["character_name"] = character_name
            backstory["last_updated"] = datetime.now().isoformat()
            
            # Save
            with open(backstory_file, 'w', encoding='utf-8') as f:
                yaml.dump(backstory, f, allow_unicode=True, default_flow_style=False)
            
            # Also add as a memory for searchability
            self.add_memory(
                character_id=character_id,
                character_name=character_name,
                memory_type="backstory",
                content=f"[{element_type}] {content}",
                importance=3,
                tags=["backstory", element_type]
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding backstory for {character_id}: {e}")
            return False
    
    def get_backstory(self, character_id: str) -> Dict[str, Any]:
        """Get a character's expanded backstory."""
        char_folder = self.get_character_folder(character_id)
        backstory_file = char_folder / "backstory.yaml"
        
        if not backstory_file.exists():
            return {"character_id": character_id, "elements": []}
        
        try:
            with open(backstory_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {"elements": []}
        except Exception as e:
            logger.error(f"Error loading backstory for {character_id}: {e}")
            return {"character_id": character_id, "elements": []}
    
    def build_context_for_character(
        self,
        character_id: str,
        include_backstory: bool = True,
        include_recent: bool = True,
        max_memories: int = 10
    ) -> str:
        """
        Build a context string for AI prompting about this character.
        
        Args:
            character_id: Character's unique ID
            include_backstory: Include backstory elements
            include_recent: Include recent memories
            max_memories: Maximum memories to include
            
        Returns:
            Formatted context string
        """
        parts = []
        
        if character_id not in self.global_index:
            return ""
        
        idx = self.global_index[character_id]
        parts.append(f"=== Character Memory Context for {idx.character_name} ===")
        
        # Backstory
        if include_backstory:
            backstory = self.get_backstory(character_id)
            if backstory.get("elements"):
                parts.append("\n--- Backstory Elements ---")
                for elem in backstory["elements"][-5:]:  # Last 5 elements
                    parts.append(f"• [{elem['type']}] {elem['content']}")
        
        # Recent important memories
        if include_recent:
            memories = self.get_memories(character_id, limit=max_memories, min_importance=2)
            if memories:
                parts.append("\n--- Recent Memories ---")
                for m in memories:
                    loc_str = f" at {m.location}" if m.location else ""
                    parts.append(f"• [{m.memory_type}]{loc_str}: {m.content}")
        
        # Relationship summary
        if idx.related_characters:
            parts.append("\n--- Relationships ---")
            sorted_relations = sorted(idx.related_characters.items(), key=lambda x: x[1], reverse=True)
            for char_name, count in sorted_relations[:5]:
                parts.append(f"• {char_name}: {count} interactions")
        
        return "\n".join(parts)
    
    def auto_generate_memory_from_turn(
        self,
        character_id: str,
        character_name: str,
        narrative: str,
        player_action: str,
        session_id: str,
        turn_number: int,
        location: str = "",
        player_name: str = ""
    ) -> List[str]:
        """
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
        """
        added = []
        narrative_lower = narrative.lower()
        char_name_lower = character_name.lower()
        
        # Skip if character not mentioned in narrative
        if char_name_lower not in narrative_lower:
            return added
        
        # Detect interaction types
        interaction_keywords = {
            "conversation": ["says", "tells", "asks", "replies", "speaks", "whispers", "mentions"],
            "physical": ["touches", "embraces", "kisses", "holds", "takes hand", "hugs"],
            "service": ["serves", "brings", "offers", "prepares", "cleans", "helps"],
            "emotional": ["smiles", "laughs", "cries", "blushes", "frowns", "sighs"],
            "combat": ["attacks", "defends", "fights", "strikes", "dodges"],
        }
        
        related = [player_name] if player_name else []
        
        for interaction_type, keywords in interaction_keywords.items():
            if any(kw in narrative_lower for kw in keywords):
                # Extract relevant sentence(s)
                sentences = narrative.split('.')
                relevant = []
                for sentence in sentences:
                    if char_name_lower in sentence.lower() and any(kw in sentence.lower() for kw in keywords):
                        relevant.append(sentence.strip())
                
                if relevant:
                    content = ". ".join(relevant[:2])  # Max 2 sentences
                    if content:
                        self.add_memory(
                            character_id=character_id,
                            character_name=character_name,
                            memory_type="interaction",
                            content=content,
                            session_id=session_id,
                            turn_number=turn_number,
                            related_characters=related,
                            location=location,
                            importance=2,
                            tags=[interaction_type]
                        )
                        added.append(f"interaction:{interaction_type}")
                        break  # One memory per turn per character
        
        return added
    
    def get_all_character_ids(self) -> List[str]:
        """Get list of all characters with memories."""
        return list(self.global_index.keys())
    
    def export_character_memories(self, character_id: str) -> Dict[str, Any]:
        """Export all memories for a character as a dict."""
        return {
            "index": self.global_index.get(character_id, CharacterMemoryIndex(character_id, character_id)).to_dict(),
            "memories": [m.to_dict() for m in self.get_memories(character_id, limit=1000)],
            "backstory": self.get_backstory(character_id)
        }


# ============================================================================
# INTEGRATION HELPERS
# ============================================================================

def create_memory_system(data_path: str) -> CharacterMemoryRAG:
    """Create and return a CharacterMemoryRAG instance."""
    return CharacterMemoryRAG(data_path)


def extract_character_mentions(text: str, known_characters: List[str]) -> List[str]:
    """
    Extract which known characters are mentioned in text.
    
    Args:
        text: Text to search
        known_characters: List of character names to look for
        
    Returns:
        List of mentioned character names
    """
    text_lower = text.lower()
    mentioned = []
    
    for char in known_characters:
        # Check full name
        if char.lower() in text_lower:
            mentioned.append(char)
            continue
        
        # Check first name only
        first_name = char.split()[0].lower()
        if len(first_name) > 2 and first_name in text_lower:
            mentioned.append(char)
    
    return mentioned
