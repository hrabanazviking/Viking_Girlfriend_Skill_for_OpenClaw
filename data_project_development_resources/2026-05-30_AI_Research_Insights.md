# AI Research Insights (2026-05-30)

This report summarizes recent findings on Theory of Mind (ToM) evaluation in LLMs, structured memory for AI agents, and adaptive ToM for multi-agent coordination. It also includes code ideas for integrating these concepts into the OpenClaw Viking Companion Skill.

## 1. Does GPT-4 Have Theory of Mind Capabilities? (Allen Institute for AI)

Research surrounding the new FANToM benchmark by Ai2 reveals that current state-of-the-art LLMs, including GPT-4, lack coherent Theory of Mind (ToM) capabilities.
*   **The Issue:** Previous evaluations relied on narratives, which compress situation info and introduce reporting bias, allowing models to exploit artifacts.
*   **The FANToM Approach:** FANToM uses multi-party conversations with information asymmetry (e.g., characters joining/leaving, creating gaps in who knows what).
*   **Findings:** LLMs perform significantly worse than humans. They can identify facts but struggle with "belief questions" that share significant word overlap with facts, indicating they use shortcuts rather than genuine mentalizing. Even Chain-of-Thought (CoT) prompting or fine-tuning doesn't result in coherent ToM reasoning, often just reducing false positives while leaving false negatives unchanged.

## 2. Adaptive Theory of Mind for LLM-based Multi-Agent Coordination (arXiv:2603.16264)

This paper highlights that merely equipping LLMs with ToM is insufficient for effective coordination.
*   **The Issue:** Misaligned ToM orders (mismatches in the depth of reasoning about others' mental states) lead to excessive or insufficient reasoning, impairing coordination.
*   **The Solution:** The authors propose an "Adaptive ToM" (A-ToM) agent. Based on prior interactions, this agent estimates the partner's likely ToM order and uses this to predict actions and coordinate effectively.

## 3. What Is Structured Memory in AI Agents? (MindStudio)

This article emphasizes the importance of structured memory over raw conversation logs.
*   **The Problem:** Context windows are stateless. Dumping entire chat histories bloats the prompt, slows inference, and degrades performance. Summaries lose specific details.
*   **The Solution:** Structured memory explicitly organizes context into queryable formats (JSON, YAML) stored externally.
*   **Key Principles:**
    *   **Structure over Storage:** A defined schema (e.g., `user_id`, `preferences`, `open_items`) makes memory actionable.
    *   **Updating:** Memory should be updated precisely, often via field-level updates rather than full rewrites.
    *   **Multi-Agent Shared Memory:** Agents should read/write to a central structured memory object rather than maintaining isolated logs.

---

## Code Ideas for the Viking Companion Skill

Based on these findings, here are actionable code ideas to improve Sigrid's architecture:

### 1. Implement Structured Memory Artifacts in `MemoryStore`
Migrate from unstructured summaries or simple vector embeddings to strict JSON schemas for core contextual data.

```python
# idea: memory_schema.py
from pydantic import BaseModel, Field
from typing import List, Optional

class SigridUserMemory(BaseModel):
    user_id: str
    trust_tier: str = "Outsider" # Ties into Innangarð Trust Engine
    preferences: dict = Field(default_factory=dict)
    active_projects: List[str] = Field(default_factory=list)
    recent_events: List[str] = Field(default_factory=list)
    vargr_flags: List[str] = Field(default_factory=list) # Hostile actions
```
*   **Integration:** Update the `Odinsblund` (Sleep Cycle) memory consolidation to not just generate vector embeddings but specifically extract and update these JSON fields.

### 2. Information Asymmetry Awareness (FANToM-inspired)
To simulate a more realistic ToM, Sigrid should explicitly track *who* knows *what*.
*   **Integration:** In the `FederatedMemoryRequest`, include metadata about the context of the memory acquisition. If a user tells Sigrid a secret, her internal state should tag it as `known_to: [Sigrid, User_A]` and strictly prevent disclosure in multi-user contexts (like OpenClaw server chats) if `User_B` is present.

### 3. Adaptive ToM (A-ToM) for OpenClaw Inter-Agent Communication
If OpenClaw supports multiple agents (e.g., Sigrid interacting with another companion or a tool-use agent), implement an adaptive reasoning depth.

```python
# idea: adaptive_tom.py
class AdaptiveToMManager:
    def __init__(self):
        self.partner_tom_estimates = {} # Map agent_id -> estimated ToM level (0, 1, 2)

    def estimate_partner_depth(self, partner_id, interaction_history):
        # Logic to evaluate if the partner anticipates Sigrid's state.
        # Adjust internal reasoning depth to match the partner.
        pass

    def format_prompt_for_partner(self, partner_id, base_prompt):
        depth = self.partner_tom_estimates.get(partner_id, 1)
        if depth == 0:
            return f"{base_prompt}\n(Note: This entity only understands direct commands, do not assume it knows your intent.)"
        # ...
```

### 4. Memory Conflict Resolution via Heimdallr
When a structured memory update conflicts with existing data (e.g., changing a core preference), route the update through the `Heimdallr Protocol` for verification. If the change seems suspicious or out of character for the user based on historical context, flag it for manual confirmation by the user before committing the write.
