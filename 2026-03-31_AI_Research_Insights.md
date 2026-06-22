# 2026-03-31 AI Research Insights & Ideas

## 1. Personalized Simulation & LLM Theory of Mind
### Research Findings
Recent research (e.g., "HumanLLM") emphasizes a shift from general-purpose pretraining to personalized understanding. LLMs are exhibiting nascent human-like characteristics such as personality traits and rudimentary Theory of Mind. A critical gap remains in simulating individual cognition because standard pretraining relies on disconnected text snippets, missing the continuous, situated context that shapes an individual's behavior over time. The goal is to build models capable of deeper, personalized simulation of human cognition, inner states, and motivations, allowing intelligent NPCs and emotional companions to accurately predict motivations and infer inner states.

Furthermore, there's interest in modeling the efficiency of human brain parameter activation to make LLMs less energy-expensive and more scalable when encoding Theory of Mind.

### Application to Viking Companion Project
For **Sigrid**, the **Ørlög Architecture** already provides biological and emotional state simulation (Chrono-Biological Engine, Wyrd Matrix). To enhance this, we can introduce **Continuous Situated Context** tracking. Instead of just passing the recent conversation and current mood state, the prompt construction could dynamically include long-term behavioral patterns and inferred "inner states" of both Sigrid and the user.

## 2. Structured & Graph-Based AI Memory Concepts
### Research Findings
AI memory systems in 2026 are moving beyond simple vector databases (which only provide similarity embeddings). Key concepts include:
*   **Graph-Based Context Storage:** Storing knowledge as interconnected nodes and relationships (Ontology-based validation). This enables human-like semantic reasoning by bridging separate pieces of data.
*   **Typed Relationships:** Memories shouldn't just be "similar." They should have structured relationships like "supports," "contradicts," "supersedes," or "depends_on." This allows the agent to explore connections logically.
*   **Extraction and Update Pipelines (e.g., Mem0):** Systems use a two-phase pipeline:
    *   *Extraction Phase:* Ingests latest exchange, rolling summary, and recent messages to extract concise candidate memories using an LLM.
    *   *Update Phase:* Compares new facts to similar existing entries and chooses an operation: ADD, UPDATE, DELETE (contradictions), or NOOP. This minimizes tokens and keeps the memory store coherent and non-redundant.
*   **Hierarchical Memory:** For deep context understanding over long timeframes (e.g., month-long projects), hierarchical memory allows LLMs to track complex arguments and understand intricate relationships between disparate pieces of information.

### Application to Viking Companion Project
The current **FederatedMemory** architecture can be upgraded to support a **Graph-Based Memory Store** with **Typed Relationships**. During the daily memory consolidation (Odinsblund sleep cycle), the system could run an "Extraction and Update" pipeline to maintain a coherent, non-redundant long-term memory graph.

## Code Ideas & Implementation Blueprints

### Idea 1: Typed Memory Relationships in `FederatedMemory`

Instead of simply saving text and vector embeddings, memories can be stored as nodes with defined relationships.

```python
from enum import Enum
from pydantic import BaseModel
from typing import List, Optional

class MemoryRelationshipType(Enum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    SUPERSEDES = "supersedes"
    RELATES_TO = "relates_to"

class MemoryEdge(BaseModel):
    target_memory_id: str
    relationship_type: MemoryRelationshipType
    weight: float = 1.0

class StructuredMemoryNode(BaseModel):
    memory_id: str
    content: str
    embedding: List[float]
    timestamp: float
    edges: List[MemoryEdge] = []

    def add_relationship(self, target_id: str, rel_type: MemoryRelationshipType):
        self.edges.append(MemoryEdge(target_memory_id=target_id, relationship_type=rel_type))

# Example usage during Memory Consolidation:
# If a new fact contradicts an old fact:
# old_node.add_relationship(new_node.memory_id, MemoryRelationshipType.SUPERSEDES)
```

### Idea 2: Extraction and Update Pipeline (Mem0 concept)

A structured approach to updating the memory store during the sleep cycle or background processing.

```python
import asyncio

class MemoryUpdateOperation(Enum):
    ADD = "add"
    UPDATE = "update"
    DELETE = "delete"
    NOOP = "noop"

async def process_new_fact(new_fact_text: str, current_memory_store):
    # 1. Retrieve top-k similar existing memories (vector search)
    similar_memories = await current_memory_store.search_similar(new_fact_text, k=3)

    if not similar_memories:
        return MemoryUpdateOperation.ADD, new_fact_text

    # 2. Use LLM to decide the operation based on the new fact and similar memories
    # Prompt the LLM: "Does the new fact contradict, update, or add to these existing facts?"
    decision_prompt = f"New Fact: {new_fact_text}\nExisting Facts: {similar_memories}\nAction (ADD, UPDATE, DELETE, NOOP):"

    # Mock LLM call
    operation_decision = await llm_decide_memory_action(decision_prompt)

    return operation_decision

async def llm_decide_memory_action(prompt: str) -> MemoryUpdateOperation:
    # Logic to call primary model (e.g., Gemini) to classify the action
    pass
```

### Idea 3: Enhancing Wyrd Matrix with Continuous Situated Context

Integrating historical emotional patterns into the prompt.

```python
class WyrdMatrixContext:
    def __init__(self):
        self.emotional_history = [] # List of (timestamp, PAD_vector)

    def get_situated_context_summary(self) -> str:
        # Analyze the emotional history to provide a narrative for the prompt
        if not self.emotional_history:
            return "Sigrid's emotional state is neutral."

        # Mock analysis
        recent_trend = "steadily increasing in energy and joy"
        return f"Over the past few days, Sigrid's mood has been {recent_trend}. This situated context colors her current reaction."

# When building the LLM prompt in the Ørlög Architecture:
# prompt += f"\n[Inner State Context]: {wyrd_matrix.get_situated_context_summary()}"
```
