# AI Research Discoveries: 2026 State of the Art
**Date: 2026-04-05**

This document compiles the latest 2025-2026 research findings in AI, LLMs, Theory of Mind, structured memory, personality simulation, and structured data methods, specifically focusing on applications for the Viking Girlfriend Skill project.

## 1. Theory of Mind (ToM) & Personality Simulation

### Adaptive Theory of Mind (A-ToM)
* **Research**: *Adaptive Theory of Mind for LLM-based Multi-Agent Coordination* (arXiv:2603.16264). Researchers found that misaligned ToM orders between interacting entities can impair coordination. An A-ToM agent estimates its partner's likely ToM order and aligns with it.
* **Project Implication**: Sigrid/Astrid shouldn't over-complicate or over-simplify their reasoning about the user's state. They need to adapt to how complex the user's interactions are.

### Dynamic Theory of Mind as a Temporal Memory Problem
* **Research**: *Dynamic Theory of Mind as a Temporal Memory Problem: Evidence from Large Language Models* (arXiv:2603.14646). LLMs suffer from recency bias and struggle to maintain/retrieve prior belief states once an update occurs.
* **Project Implication**: Relying on the LLM's implicit context window to remember what the user *used to believe* will fail. We need an explicit tracker for past vs. current beliefs in the memory system.

### Deficits in Mental Self-Modeling
* **Research**: *Selective Deficits in LLM Mental Self-Modeling in a Behavior-Based Test of Theory of Mind* (arXiv:2603.26089). Frontier LLMs fail at self-modeling tasks unless provided a "scratchpad" in the form of a reasoning trace.
* **Project Implication**: The persona agents must be forced to use an internal `<thought>` or scratchpad phase before answering, allowing them to construct a model of their own ongoing state.

### Re-evaluating LLM Personality
* **Research**: *LLMs Aren't Human: A Critical Perspective on LLM Personality* (arXiv:2603.19030). Applying human "Big Five" personality traits to LLMs is fundamentally flawed. Functional evaluations and LLM-specific frameworks for characterizing stable behavior are required.
* **Project Implication**: Instead of just prompting "You are high in openness," we should define functional, stable behavioral rules (e.g., "Always respond to new magic concepts with curiosity and reference to the Galdrabók").

## 2. Structured Memory Concepts

### Cognitive Gist-Driven RAG (CogitoRAG)
* **Research**: *Understand Then Memory: A Cognitive Gist-Driven RAG Framework with Global Semantic Diffusion* (arXiv:2602.15895). Linear semantic retrieval lacks macro-level comprehension. Simulating human memory by first constructing a "global gist memory base" ensures precise extraction guided by complete semantic context.
* **Project Implication**: `Mímisbrunnr` should store high-level "gists" of episodes. When querying, it should fetch the gist first to form a macro-context, then fetch specific semantic nodes.

## 3. Structured Data Methods

### LLMStructBench & Parsing Strategy
* **Research**: *LLMStructBench: Benchmarking Large Language Model Structured Data Extraction* (arXiv:2602.14743). When extracting JSON/structured data from text, the prompting strategy is more important than model size for reliability and structural validity.
* **Project Implication**: We can use smaller local models (via Ollama) for JSON extraction if we optimize our structural prompts and schemas, saving token costs and latency.

---

## Proposed Code Implementations

### A. Reasoning Scratchpad for Self-Modeling
```python
# To improve the agent's ToM and self-awareness, wrap inputs to require a reasoning block.
def apply_scratchpad_prompt(base_prompt: str) -> str:
    return base_prompt + """
Before responding, you MUST write your internal thoughts inside a <scratchpad> block.
Use this space to model your own current mental state and the user's likely state.
<scratchpad>
[Your internal reasoning here]
</scratchpad>
[Your actual response]
"""
```

### B. Dynamic Belief Tracker (Temporal ToM)
```python
# Instead of overwriting memory, log belief changes over time.
class TemporalBeliefRecord:
    def __init__(self, subject: str):
        self.subject = subject
        self.belief_timeline = [] # List of tuples: (timestamp, belief_state)

    def update_belief(self, new_belief: str, timestamp: float):
        self.belief_timeline.append((timestamp, new_belief))

    def get_belief_at_time(self, timestamp: float) -> str:
        # Retrieve the belief held by the subject right before the given timestamp
        pass
```

### C. Gist-Driven Memory Store (CogitoRAG implementation)
```python
class GistMemoryStore:
    def __init__(self):
        self.global_gists = [] # High-level summaries
        self.semantic_nodes = {} # Detailed episodic data

    async def retrieve(self, query: str):
        # 1. Fetch relevant gists to establish global context
        gist_context = await self._search_gists(query)

        # 2. Use the gist to guide detailed retrieval
        enhanced_query = f"{query} [Context: {gist_context}]"
        detailed_nodes = await self._search_semantic_nodes(enhanced_query)
        return detailed_nodes
```
