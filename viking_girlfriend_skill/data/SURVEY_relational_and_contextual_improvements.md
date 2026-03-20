# SURVEY: Relational & Contextual Systems — Enhancement Audit
# Created: 2026-03-20
# Author: Runa Gridweaver (AI)

This survey focuses on Sigrid's memory (`memory_store.py`), environment awareness (`environment_mapper.py`), and trust modeling (`trust_engine.py`), identifying ways to deepen her social intelligence and situational presence.

## 1. Muninn's Wing (Memory System)
**Current State**: 3-tier buffer (short/medium/long) + episodic JSON store + optional ChromaDB.

### 🧠 Continuity & Recall Ideas:
*   **Associative Memory Hooks**: When a new memory is stored, the system should automatically link it to 2-3 existing relevant memories.
    *   *Implementation Pattern*: `link_id: str = find_related_entry(new_entry.content)`.
*   **Memory "Dream" Consolidation**: During the `deep night` phase, a background job should use a local LLM to summarize the day's "Medium-Term" turns into 1-2 highly dense "Episodic" facts, preventing long-term JSON bloat.
*   **Emotional Significance Weighting**: The `wyrd_matrix` PAD state at the time of memory creation should be saved as metadata. Memories created during high `Arousal` (intense moments) should have a higher retrieval priority.

### 🚀 Performance Ideas:
*   **Warm Storage Spillover**: If `_medium_term` exceeds 100 entries, move them to a temporary `.sqlite` file rather than holding them in RAM, reducing the process's memory footprint.

---

## 2. The Great Hall (Environment Mapping)
**Current State**: Static JSON lookup of areas/rooms with metadata.

### 🎭 Situational Aliveness Ideas:
*   **Dynamic Vibe Shifting**: A room's `vibe` and `activities` should change based on the `scheduler` state.
    *   *Code Idea*:
        ```python
        if time_of_day == "deep night":
            current_vibe = room.vibe_night or "dark, silent, watchful"
        ```
*   **Object State Tracking**: Allow Sigrid to "interact" with objects in the environment JSON. If she "lights the hearth" in the living room, that state should persist for 2 hours, affecting her prompt hints.
*   **Sensory Hint Layer**: Add "Sensory Anchors" to each location (smells, sounds, textures). The `prompt_synthesizer` can then weave these into Sigrid's speech (e.g., "The smell of pine is strong here in the forest today").

---

## 3. Gebo's Web (Trust Engine)
**Current State**: Linear trust/intimacy/reliability scores based on keyword inference.

### 🤝 Relationship Depth Ideas:
*   **Multidimensional Trust Facets**: Move from a single score to a "Facet Map":
    *   **Competence Trust**: Does Volmarr know what he's talking about?
    *   **Benevolence Trust**: Does he care about Sigrid's well-being?
    *   **Integrity Trust**: Does he keep his oaths?
*   **Relational Milestones**: Explicitly track "Firsts" (first gift, first conflict, first secret shared) in a dedicated `milestones.json`. These should be un-decayable and provide massive "Anchor Points" for her personality.
*   **Third-Party Reputation**: If Sigrid interacts with other NPCs or "guests," their trust scores should slightly influence Volmarr's (e.g., if he's kind to a stranger, Sigrid's trust in him increases).

---

## 🐞 Potential Bugs Found During Survey
1.  **MemoryStore**: Keyword matching in `relevance_score` is very strict. It needs stemming or a "synonym expansion" layer to find "Odin" when the user says "Allfather."
2.  **TrustEngine**: `_EVENT_KEYWORDS` are static. A user could technically "game" the system by repeating "thank you" 100 times. It needs a "Diminishing Returns" multiplier per session.
3.  **EnvironmentMapper**: `is_safe_relative_path` only checks alphanumeric names. It might block legitimate international characters or runes in filenames if not configured correctly.

---

## 🛠️ Next Development Steps
*   [ ] Implement "Memory Consolidation" job in `memory_store.py`.
*   [ ] Add "Time-of-Day Vibe Shift" to `environment_mapper.py`.
*   [ ] Refactor `trust_engine.py` for multidimensional facets.
