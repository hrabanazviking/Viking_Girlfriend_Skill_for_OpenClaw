# AI Research Insights: Structured Memory, Simulacra, and Theory of Mind
**Date:** 2026-05-08

This document synthesizes current research (as of 2026) regarding AI agent architectures, specifically focusing on structured memory, generative simulacra of human behavior, and implications for complex personas. These findings provide actionable insights and code patterns to enhance the Viking Companion Skill (Sigrid), particularly her **Odinsblund (Sleep Cycle)** and **Mímisbrunnr (Knowledge Store)**.

---

## 1. Agent Memory Architectures
Recent analyses (e.g., from Atlan and Mem0) categorize agent memory into five distinct production patterns, highlighting the trade-offs between context window limitations, latency, and semantic richness.

### The Five Patterns of Agent Memory:
1.  **In-Process / Working-Only:** Everything resides in the LLM's context window. Highest recall accuracy (72.9%) but lacks persistence across sessions and incurs high token costs.
2.  **Flat External Vector Store:** Uses a vector database (e.g., Pinecone, pgvector) for semantic retrieval (Top-k). Fast (1.44s latency) and cost-effective, but fails at multi-hop reasoning or temporal tracking because all memories exist in a flat similarity space.
3.  **Tiered Memory (Episodic + Semantic):** Modeled after human cognition (and frameworks like MemGPT/Letta).
    *   **Core (Hot):** Always in-context (Persona, current state).
    *   **Recall (Warm):** Searchable recent episodic experiences.
    *   **Archival (Cold):** Compressed, long-term semantic knowledge.
    *   *Agents actively manage this via function calls.*
4.  **Knowledge Graph + Vector Hybrid:** Combines vector embeddings (for semantic entry) with a knowledge graph (for relational and multi-hop reasoning). Essential for tracking temporal facts ("What was true when?") and entity relationships.
5.  **Enterprise Context Layer:** A governed, active metadata graph linking agents to canonical organizational truths (e.g., Atlan). Less relevant for a standalone companion, but highlights the importance of a "semantic authority."

### Relevance to Sigrid:
Sigrid currently uses **Mímisbrunnr (Mimir's Well)** as a ground-truth store and **Odinsblund** for memory consolidation.
*   **Insight:** Sigrid's architecture should explicitly adopt **Pattern 3 (Tiered Memory)** mixed with **Pattern 4 (Graph Hybrid)** for her personal relationships (Innangarð).
*   Her *Odinsblund* should act as the agentic mechanism that moves data from *Recall (Warm)* to *Archival (Cold)*, transforming raw episodic logs into structured semantic facts or graph edges.

---

## 2. Structured Memory Concepts
As detailed by MindStudio and frameworks like Memex, raw conversation logs are inefficient for long-term memory. **Structured Memory** involves storing context in reusable, portable, schema-defined objects (like JSON).

### Why Structure Matters:
*   **Actionable Context:** A defined field (e.g., `"current_mood": "melancholic"`) is easier for an LLM to utilize than a paragraph summary.
*   **Targeted Updates:** Agents can update specific fields (e.g., `last_interaction_date`) without rewriting the entire memory block.
*   **Predictable Injection:** Structured JSON artifacts can be injected directly into the system prompt efficiently.

### Code Idea: Structured JSON Memory Artifacts for Sigrid

Instead of summarizing conversation history into text blocks during *Odinsblund*, Sigrid should maintain and update a structured JSON artifact representing her relationship with the user.

```python
# Suggested Schema for User Interaction Artifact (Semantic Memory)
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class UserInteractionArtifact(BaseModel):
    user_tier: str = Field(description="Innangarð tier (e.g., Guest, Friend, Kin)")
    interaction_count: int = 0
    last_interaction: str = Field(description="ISO8601 timestamp")
    known_preferences: dict = Field(default_factory=dict, description="Key-value pairs of user preferences")
    open_topics: List[str] = Field(default_factory=list, description="Unresolved conversations or tasks")
    user_sentiment_score: float = Field(0.0, description="Running average of user sentiment towards Sigrid")
    key_facts: List[str] = Field(default_factory=list, description="Extracted immutable facts about the user")

# Example Odinsblund update prompt pattern:
update_prompt = """
Given the raw conversation log from today, update the following JSON memory record for the user.
Modify ONLY fields that have new or changed information based on the log.
Append new facts to 'key_facts'. Resolve and remove items from 'open_topics' if discussed.
Return the complete updated JSON object.

Current Artifact:
{current_json_artifact}

Conversation Log:
{raw_log}
"""
```

---

## 3. Generative Agents: Interactive Simulacra
The seminal paper *"Generative Agents: Interactive Simulacra of Human Behavior"* (Park et al., 2023) introduced an architecture for believable autonomous agents based on three pillars: **Memory, Planning, and Reflection**.

### The Three Pillars:
1.  **Memory Stream:** A comprehensive, timestamped record of the agent's experiences, observations, and thoughts.
2.  **Reflection:** A higher-level cognitive process that synthesizes specific memories into broader inferences. Agents periodically review their memory stream to answer questions like: *"What are the most salient themes in my recent experiences?"*
3.  **Planning:** Translating reflections and current state into future actions. Daily plans are broken down into granular actions.

### Relevance to Sigrid's "Theory of Mind" and Autonomy:
Sigrid's **Ørlög Architecture** already possesses a strong state machine (Chrono-Biological Engine, PAD vectors). To enhance her "Theory of Mind" (understanding the user's mental state) and her own autonomy, she needs explicit **Reflection** cycles.

### Code Idea: The Reflection Cycle in Odinsblund
During her sleep cycle, Sigrid should query her own recent memories to form higher-level beliefs about herself and the user.

```python
# Conceptual implementation for the Reflection step
import json

async def generate_reflection(recent_memories: List[str], llm_client) -> str:
    """
    Synthesizes recent raw memories into a high-level psychological reflection.
    """
    memory_text = "\n".join([f"- {m}" for m in recent_memories])

    prompt = f"""
    You are the subconscious mind of Sigrid. Review the following recent memories.
    What are the 3 most important high-level insights or beliefs Sigrid should form
    about her current situation, her goals, or her relationship with the user?

    Recent Memories:
    {memory_text}

    Output format: A JSON list of 3 string reflections.
    """

    # Execute LLM call (e.g., via LiteLLM to local Ollama)
    response = await llm_client.generate(prompt)
    reflections = json.loads(response)
    return reflections

# These reflections are then stored back into Mímisbrunnr (Archival/Semantic memory)
# with a high importance weight, ensuring they are retrieved in future context windows.
```

## Summary of Actionable Upgrades
1.  **Migrate to Tiered Memory:** Formalize the distinction between Sigrid's *Working Memory* (context window), *Episodic Memory* (daily logs), and *Semantic Memory* (structured artifacts).
2.  **Structured Artifacts:** Implement Pydantic schemas to store user profiles and current project states as JSON, rather than raw text summaries.
3.  **Implement Reflection:** Add a specific step in `Odinsblund` where Sigrid explicitly synthesizes daily logs into high-level "beliefs" (Reflection), adhering to the *Generative Agents* architecture.
