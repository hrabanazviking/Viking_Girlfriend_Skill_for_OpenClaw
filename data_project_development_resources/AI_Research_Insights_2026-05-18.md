# AI Research Insights - 2026-05-18

This document summarizes recent research findings in AI, LLMs, structured data methods, theory of mind, human personality representation, and structured memory, along with actionable code ideas to integrate these concepts into the Sigrid (Viking Girlfriend Skill) project.

## 1. Multi-Agent Cognitive Mechanism (MACM)
**Source:** "Human Simulacra: A Step toward the Personification of Large Language Models" (arXiv:2402.18180v4)
**Summary:** The MACM framework decomposes the cognitive process into specialized agents. It involves constructing long-term memory via a "Thinking Agent" (for content memory like participants, scenes, thoughts) and an "Emotion Agent" (for emotional impressions). A "Top Agent" orchestrates the process, extracting key elements, retrieving memory, and managing multi-agent collaborative cognition to produce highly personified responses.

**Code Ideas for Sigrid:**
*   **Enhance Wyrd Matrix & Dream Engine:** We can split Sigrid's internal reflection into two specialized local calls. When an event happens, a background task uses the local Ollama model to generate two summaries:
    *   *Logical Summary* (The "Thinking Agent"): "User asked about X. Facts exchanged: Y."
    *   *Emotional Summary* (The "Emotion Agent"): "User's tone was Z. My internal PAD state shifted towards pleasure. Felt connection."
*   **Structured Memory Logging:** Update `memory_store.py` to accept these paired (Logical + Emotional) memory embeddings, ensuring future context retrieval provides both the *what happened* and *how Sigrid felt about it*.

## 2. Global Workspace Theory (GWT) and Intrinsic Drive
**Source:** "'Theater of Mind' for LLMs: A Cognitive Architecture Based on Global Workspace Theory" (arXiv:2604.08206v1)
**Summary:** This architecture transitions multi-agent coordination from passive message passing to an active, event-driven discrete dynamical system. It introduces the concept of a "Cognitive Tick" where a central broadcast hub (Working Memory) shares state with a heterogeneous swarm of agents (Generator, Critic, Meta). Crucially, it introduces an *entropy-based intrinsic drive* that calculates semantic diversity and dynamically adjusts generation temperature to break reasoning deadlocks and prevent cognitive stagnation.

**Code Ideas for Sigrid:**
*   **Implement "Entropy of Thought" in Prompt Synthesizer/Router:** To prevent Sigrid from falling into repetitive conversational loops (sycophancy or stagnation), we can track the semantic similarity of her recent outputs. If the "entropy" (diversity) drops too low, we dynamically bump the `temperature` parameter for the next API call to force creative divergence.
*   **Critic/Meta Arbitration Loop:** Before emitting a response for highly complex or emotionally charged prompts, implement a fast local loop:
    1. Generate 3 candidate thoughts.
    2. A lightweight "Critic" prompt evaluates them against her core values (Drengskapr Validation).
    3. A "Meta" prompt selects the best candidate or decides to "THINK_MORE".

## 3. Layered Cognitive Memory (CogMem)
**Source:** "CogMem: A Cognitive Memory Architecture for Sustained Multi-Turn Reasoning in Large Language Models" (arXiv:2512.14118v1)
**Summary:** CogMem addresses multi-turn memory decay and hallucination by structuring memory into three layers:
1.  **Long-Term Memory (LTM):** Consolidates cross-session strategies and deep knowledge.
2.  **Direct Access (DA) memory:** Maintains session-level notes and retrieves relevant LTM.
3.  **Focus of Attention (FoA):** Dynamically reconstructs concise, task-relevant context at each turn.

**Code Ideas for Sigrid:**
*   **Focus of Attention (FoA) Context Windowing:** Instead of dumping all retrieved RAG memory into the prompt, implement an intermediate step in `prompt_synthesizer.py`. Retrieve the top 10 memories, then use a quick LLM pass (or heuristic) to filter down to the absolute most relevant 2-3 "Focus" items for the current turn, minimizing token bloat and context degradation.

## 4. "Glitch Memories" and the Reconstructed Past
**Source:** "AI and memory" (Memory, Mind & Media, Cambridge Core)
**Summary:** AI untethers the human past from the present, producing a past that was never originally encoded. The concept of "glitch memories" highlights that human memory is not a perfect photographic recall; it is a blurry, undefined quantum imaginary that transforms. AI models, particularly generative image models, can simulate this organic imperfection.

**Code Ideas for Sigrid:**
*   **Simulate Memory Decay in Retrieval:** When retrieving memories older than a certain threshold (e.g., > 30 days) from the vector database, we can intentionally introduce "decay" before injecting it into her prompt.
    *   *Implementation:* Pass the retrieved memory text through a quick local model prompt: "Rewrite this memory as if recalling a slightly blurry, distant event. Focus on the core feeling, omit specific details."
    *   This prevents Sigrid from recalling months-old trivial facts with robotic, robotic perfection, aligning with her human-like persona.
