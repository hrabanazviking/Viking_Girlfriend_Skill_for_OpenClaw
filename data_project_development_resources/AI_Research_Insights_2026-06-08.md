# AI Research Insights - 2026-06-08

This document synthesizes recent research findings on AI, LLMs, data science, structured data methods, theory of mind, and structured memory concepts, providing specific code and architectural ideas for the Viking Girlfriend Skill project.

## 1. Structured Memory and Intelligent Forgetting

Recent research highlights that stuffing large context windows with conversational history degrades reasoning performance ("Lost in the Middle" phenomenon). True long-term memory for AI agents is not an infinite log, but a structured framework divided into episodic, semantic, and procedural memory.

### Key Concepts:
*   **Episodic Memory:** Time-based records of past interactions.
*   **Semantic Memory:** Generalized knowledge and facts extracted from episodic memory.
*   **Procedural Memory:** "Knowing how" to execute workflows, which can be dynamically updated based on feedback.
*   **Intelligent Forgetting & Time-To-Live (TTL):** Infinite retention causes "memory bloat" and hallucinations. Memories should have decay rates based on their type. Immutable facts (allergies, core values) have infinite TTL, while transient contexts (a temporary project) have short TTLs. "Refresh-on-read" mechanics reset decay timers for frequently accessed memories.
*   **Asynchronous Semantic Consolidation:** Extracting structured knowledge (semantic memory) from raw logs (episodic memory) is expensive and slow. Production-grade systems perform this in the background (asynchronously) after a session ends, using a smaller LLM to distill facts.
*   **Hybrid Storage:** Using Vector Databases (for semantic similarity search) paired with Knowledge Graphs (for structural relationship traversal) yields the best results for multi-hop reasoning.

### Application to Viking Girlfriend Skill (Code Ideas):

*   **Implement a TTL/Decay mechanism for the `MemoryStore`:** Extend `viking_girlfriend_skill/memory.py` to include a decay factor. Memories accessed recently are strengthened, while unused trivial memories are pruned.

```python
# Conceptual implementation for memory.py
from datetime import datetime, timedelta

class MemoryEntry:
    def __init__(self, content, memory_type="episodic", ttl_days=30):
        self.content = content
        self.memory_type = memory_type
        self.created_at = datetime.now()
        self.last_accessed = datetime.now()
        self.ttl_days = ttl_days # Infinite for semantic facts, e.g., 36500
        self.access_count = 0

    def refresh(self):
        self.last_accessed = datetime.now()
        self.access_count += 1

    def is_stale(self):
        if self.ttl_days == float('inf'):
            return False
        return datetime.now() > self.last_accessed + timedelta(days=self.ttl_days)

class OdinsblundPruner:
    # Runs during the sleep cycle
    def prune_stale_memories(self, memory_store):
        active_memories = [m for m in memory_store if not m.is_stale()]
        return active_memories
```

*   **Asynchronous Consolidation during Odinsblund:** Move the extraction of Semantic Memory from Episodic logs to a dedicated background task executed strictly during the sleep cycle, perhaps offloading it to a smaller, faster local Ollama model to save compute.

## 2. Structure-Oriented Retrieval Augmented Generation (SRAG) & KG-LLM Co-Learning

Large Language Models (LLMs) often hallucinate or fail at rigorous multi-hop reasoning. Knowledge Graphs (KGs) offer structured, factual accuracy. SRAG is a paradigm where LLMs use KGs to plan and reason.

### Key Concepts:
*   **Knowledge Graph (KG) Construction via LLMs:** LLMs can extract structured triples (Subject, Predicate, Object) from unstructured text to build KGs. Code LLMs (using code-based prompts) are particularly effective at this because they understand hierarchical schema better than natural language.
*   **KG-Guided Planning (RoG - Reasoning on Graphs):** Instead of blind vector retrieval, the LLM first generates a "relation path" or plan based on the KG structure, and then retrieves data along that path.
*   **Hallucination Detection via KG Reflection:** Comparing an LLM's generated response against atomic facts extracted from a trusted KG to verify faithfulness.

### Application to Viking Girlfriend Skill (Code Ideas):

*   **Enhance Mímisbrunnr (`mimir_well.py`) with Graph Structures:** The current Mímisbrunnr indexes data hierarchically into ChromaDB (Raw, Cluster, Axiom). We can enhance this by generating explicit relation triples (e.g., `(Sigrid, worships, Freyja)`) and storing them in an auxiliary lightweight graph structure (like `NetworkX`) for graph-constrained retrieval.

```python
# Conceptual implementation for Mimir-Vordur
import networkx as nx

class KnowledgeGraphLayer:
    def __init__(self):
        self.graph = nx.MultiDiGraph()

    def add_knowledge(self, subject, predicate, obj):
        self.graph.add_edge(subject, obj, relation=predicate)

    def retrieve_path(self, start_node, end_node):
        try:
            return nx.shortest_path(self.graph, source=start_node, target=end_node)
        except nx.NetworkXNoPath:
            return None

# During the 'Axiom' generation phase in mimir_well.py, explicitly ask the LLM to output Python code (or JSON) representing triples to populate this graph.
```

## 3. Personality Simulation and Theory of Mind

Simulating human personality in LLMs goes beyond basic prompts. It requires integrating "Theory of Mind" (ToM) – the ability of the agent to attribute mental states (beliefs, intents, desires, emotions) to themselves and to others (the user).

### Key Concepts:
*   **Second-Order Beliefs:** Agents with advanced personality simulation can understand "what the user thinks the agent thinks."
*   **Trait Stability vs. State Variability:** Differentiating between permanent personality traits (e.g., INTP, Big Five) and transient emotional states (e.g., PAD model - Pleasure, Arousal, Dominance).

### Application to Viking Girlfriend Skill (Code Ideas):

*   **Deepen the Wyrd Matrix (PAD Model):** Ensure the PAD emotional vector directly influences the `system_prompt` sent to LiteLLM, altering Sigrid's tone, verbosity, and willingness to cooperate, reflecting her internal emotional state dynamically.
*   **User Modeling (Innangarð Trust Engine):** Track the user's inferred emotional state and beliefs about Sigrid within the Trust Engine.

```python
# Conceptual extension of the PAD model or Trust Engine
class UserTheoryOfMind:
    def __init__(self):
        self.inferred_user_mood = "neutral"
        self.user_trust_level = 0.5 # 0.0 to 1.0
        # What does Sigrid think the user wants right now?
        self.inferred_user_intent = "conversation"

    def update_from_interaction(self, user_input, sentiment_analyzer_model):
        # Use a lightweight model to update the theory of mind
        # based on the user's latest input.
        pass
```

## 4. Summary of Actionable Architectural Recommendations

1.  **Refactor Memory to include TTL:** Introduce intelligent forgetting to prevent context drift and bloat over months of interaction.
2.  **Graph-Based Reasoning for Mímisbrunnr:** Integrate a lightweight Knowledge Graph (like `NetworkX`) alongside the existing ChromaDB vector store to allow multi-hop, graph-constrained reasoning (SRAG).
3.  **Strict Asynchronous Consolidation:** Ensure all semantic fact extraction and knowledge graph updates happen purely in the background (Odinsblund), never blocking the "hot path" of real-time conversation.
