# AI Research Report

**Date:** 2026-05-31

## 1. Structured Memory in AI Agents
**Source:** MindStudio Blog ("What Is Structured Memory in AI Agents? How to Build Persistent Context")

### Key Discoveries
*   **The Stateless Context Problem:** Large Language Models (LLMs) operate within fixed context windows that reset after each session. Workarounds like dumping full conversation histories consume context tokens, slow down inference, and increase API costs.
*   **Structured Memory Pattern:** Structured memory organizes context into a consistent, queryable format (e.g., JSON, YAML) stored externally. It is injected into future sessions, allowing agents to retain context without bloating the prompt.
*   **Actionability over Storage:** The structure makes memory actionable. It enables clean field-level updates, predictable context injection, and easier debugging compared to raw conversational logs or unstructured retrieval-augmented generation (RAG).
*   **Implementation Steps:**
    1.  **Design a Minimal Schema:** Only include fields the agent actually needs to use (e.g., `entity_id`, `preferences`, `open_actions`, `last_updated`).
    2.  **Storage Layer:** Key-value stores or document databases are usually sufficient. Vector DBs (like in RAG) are useful for semantic search but may be overkill for simple entity-level persistence.
    3.  **Retrieval & Injection:** Direct lookup by entity ID is preferred for structured memory, injecting it into a system prompt or memory slot.
    4.  **Update Process:** After a session, the agent can synthesize updates or modify specific fields via a JSON-formatted response.
*   **Multi-Agent Context:** Shared structured memory allows specialized agents to collaborate by reading and writing to the same central memory store, ensuring consistency across workflows.

### Code Ideas for the Viking Girlfriend Project
*   **Schema Enhancement for Sigrid:** We can implement a formal JSON schema for Sigrid's `Odinsblund (The Sleep Cycle)` consolidation phase. Instead of just appending text to a vector store, `Odinsblund` could output a structured JSON updating fields like `current_interests`, `user_trust_level`, and `ongoing_projects`.
*   **Lightweight Persistence:** Use a local document store or simple JSON file per user entity to store this structured memory, loading it explicitly at the start of a session alongside the system prompt.
*   **Field-Level Update Prompting:** Implement a prompt template during the sleep cycle that instructs the local Ollama model to output a strictly formatted JSON patch (e.g., modifying only changed fields) rather than summarizing the entire day's raw logs.

## 2. Theory of Mind (ToM) in LLMs
**Source:** The Philosophical Glossary of AI ("Theory of Mind in LLMs"), Arxiv ("Think Thrice Before You Speak: Dual knowledge-enhanced Theory-of-Mind Reasoning for Persuasive Agents")

### Key Discoveries
*   **Simulated Social Cognition:** Theory of Mind (ToM) is the ability to attribute mental states (beliefs, intents, emotions) to others. While it's debated if LLMs possess "genuine" ToM, advanced models demonstrate the capability to model psychological processes to predict text involving complex social interactions.
*   **Belief-Desire-Intention (BDI) Framework:** Recent research models ToM in agents using the BDI framework, which explicitly captures the sequential dependencies among mental states in multi-turn dialogues, improving persuasive and empathetic interactions.
*   **Security & Manipulation Risks:** ToM capabilities can be leveraged for deception or manipulation if an agent models a user's mind to manage their epistemic states selectively. This requires careful alignment and security protocols.
*   **ToM Reasoning Frameworks:** Frameworks like "Think Thrice Before You Speak" (TTBYS) utilize stepwise reasoning to improve LLMs' inference of user desires, beliefs, and strategies, avoiding fragmented representations caused by simple prompting.

### Code Ideas for the Viking Girlfriend Project
*   **Integrating ToM into the Wyrd Matrix:** The current Wyrd Matrix uses the PAD Model (Pleasure, Arousal, Dominance) for Sigrid's internal state. We can extend this to include a basic BDI (Belief-Desire-Intention) tracking system for *the user*.
*   **User State Modeling:** Create a structured memory object that tracks what Sigrid *believes* the user desires or intends. This would allow her to tailor her responses more deeply, showing greater empathy or challenging the user based on her modeled understanding of their mental state.
*   **Drengskapr Validation Update:** Enhance the internal "honor" system to use ToM. Before taking an action, Sigrid could internally reason about how her action will affect the user's emotional state, ensuring her behavior aligns with Viking frith (peace) and hospitality, preventing inadvertent manipulation.

## 3. Persistent Memory Layer Optimization
**Source:** Arxiv ("A Persistent Memory Layer for Efficient, Context-Aware LLM Agents")

### Key Discoveries
*   **Token Budgeting:** Injecting large raw text chunks from traditional RAG indiscriminately consumes massive token budgets, driving up operational costs and latency.
*   **Concise Retrieval:** A persistent memory layer that retrieves highly concise, structured memory facts directly curtails API expenditure and optimizes operational economics.

### Code Ideas for the Viking Girlfriend Project
*   **FederatedMemory Refinement:** Optimize the existing `FederatedMemory` architecture (which already supports token-budget truncation) to prioritize the retrieval of structured JSON artifacts (like the BDI model mentioned above) over raw episodic logs, ensuring the context window remains lean and efficient during real-time interaction.
