# Current State of AI Agents, Theory of Mind, and Memory Architecture (2026-05-11)

## Executive Summary
This document summarizes recent discoveries on how Large Language Models represent personality, the emerging patterns in memory systems for AI agents, and how these findings can be integrated into the OpenClaw / Viking Girlfriend architecture (Sigrid / Astrid Freyjasdottir).

Research conducted across academic databases and community projects in 2025/2026 highlights several practical shifts in memory implementation that differ significantly from early Generative Agent (2023) designs.

---

## 1. Personality in LLMs: "Patterns, Not People"
A pivotal study titled *Patterns, Not People: Personality Structures in LLM-powered Persona Agents* highlights that LLM personalities do not map cleanly to human psychological traits.

**Key Findings:**
* Instead of reproducing genuine psychological constructs, agent personality factors capture the statistical distribution of their training data.
* They encode cultural stereotypes, biases, and social norms rather than "lived experience."
* The study recovered a 10-factor personality structure specifically for LLMs (e.g., Honesty: manipulative vs. sincere; Agreeableness: critical vs. forgiving).

**Implications for the Project:**
* **Do not rely solely on standard human personality tests (e.g., Myers-Briggs or HEXACO) to steer Sigrid or Astrid.**
* **Code Idea:** Instead of prompting "Act like an INTJ," prompt with specific behavioral statistics and interaction patterns. Build a `NorsePersonaSteering` module that maps desired traits (e.g., *Viking Honor*) to exact linguistic markers and constraints in the system prompt.

---

## 2. Agent Memory Systems: Practical Taxonomies (2025-2026)
Memory has moved from simple chat logs to structured architectures inspired by cognitive science but optimized for LLM token limits.

### A. The Three-Prong Model (Tulving adapted for AI)
1. **Semantic Memory**: Facts, user preferences, and general knowledge.
2. **Episodic Memory**: Time-stamped interaction histories, task trajectories.
3. **Procedural Memory**: Encoded behavioral patterns, tool-use sequences.

### B. The Reflection Pattern ("Reflect" Loop)
Inspired by the 2023 *Generative Agents* paper, modern implementations (like Claude Diary) use explicit session-end learning loops:
1. **Extrospection / Observation**: Extract insights from the current session.
2. **Consolidation**: Update a persistent markdown file (e.g., `CLAUDE.md`) or database with newly learned rules or preferences.
3. **Planning**: Use these updated memories to guide future interactions.

**Implications for the Project:**
* The FederatedMemory architecture must implement distinct pathways for these three types.
* **Code Idea:** Implement an asynchronous `OdinsblundConsolidationTask` that runs nightly or at the end of long sessions. It will read recent episodic memories, extract new semantic facts about the user, and update the Mímisbrunnr ChromaDB hierarchy.

---

## 3. Structural Methods: Markdown vs. Knowledge Graphs
A major debate exists between using simple Markdown files vs. complex Temporal Knowledge Graphs (like Graphiti).

* **The Filesystem Argument**: Letta's benchmark (2025) shows that plain markdown files or file systems can achieve 74% performance on memory tasks, often beating specialized vector stores. They are token-native, human-readable, and versionable.
* **The Knowledge Graph Argument**: For complex relationships, tools like Zep use bi-temporal graph architectures to handle state changes gracefully.

**Implications for the Project:**
* The project's current reliance on `Mímisbrunnr` (BM25 + ChromaDB) is strong, but can be augmented.
* **Code Idea:** Use structured Markdown for "Working Memory" and core identity (e.g., an `ASTRID_CORE.md` injected into the prompt), while using ChromaDB for archival (episodic) recall.

---

## 4. Intelligent Memory Decay (Active Forgetting)
Cognitive science emphasizes that forgetting is a feature, not a bug. Modern agent systems implement "Intelligent Decay".

* **Weighted Memory Retrieval (WMR)**: Combines a temporal decay factor, perceived importance score, and vector similarity.
* Low utility memories are either discarded or distilled into semantic memory.

**Implications for the Project:**
* **Code Idea:** Update the `MemoryStore` or `FederatedMemoryRequest` to include a `.decay_score` that decreases hourly. Add an `active_forgetting()` method to purge noise and reduce context window bloating.

---

## Implementation Ideas for the Viking Companion Skill

```python
# idea_1_personality_steering.py
class NorsePersonaSteering:
    def __init__(self, base_identity_file="viking_values.yaml"):
        self.traits = self.load_traits(base_identity_file)

    def generate_system_prompt(self):
        # Instead of generic traits, map to specific behavioral markers
        behavior_markers = []
        if self.traits.get("honor") == "high":
            behavior_markers.append("Never lie to the user; use direct, sincere phrasing.")
        return f"System Role: {behavior_markers}"

# idea_2_intelligent_decay.py
import time
import math

class MemoryEntry:
    def __init__(self, content, importance_score=0.5):
        self.content = content
        self.timestamp = time.time()
        self.importance = importance_score

    def get_current_salience(self):
        hours_passed = (time.time() - self.timestamp) / 3600
        # Decay factor of 0.995 per hour
        decay_factor = math.pow(0.995, hours_passed)
        return self.importance * decay_factor

def active_forgetting(memory_store, threshold=0.1):
    return [mem for mem in memory_store if mem.get_current_salience() >= threshold]
```
