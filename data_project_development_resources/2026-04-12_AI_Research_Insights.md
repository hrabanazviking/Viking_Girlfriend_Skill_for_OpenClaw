# AI Research Insights (2026-04-12)

This document compiles recent research on AI, LLMs, data science, structured data methods, human personality modeling, theory of mind, virtual human simulation, and structured memory concepts, identifying actionable insights for the Sigrid Viking Companion project.

## 1. Structured Memory and LLMs

**Key Findings:**
* **MemCoT (Memory-Driven Chain-of-Thought):** Transforms long-context reasoning into an iterative, stateful search. It uses dual short-term memory (semantic state and episodic trajectory) alongside long-term perception (Zoom-In evidence localization, Zoom-Out contextual expansion).
* **Externalization of Capabilities:** Agent capabilities are increasingly externalized into memory stores, reusable skills, and interaction protocols rather than relying solely on model weights.
* **Global Workspace Agents (GWA):** A cognitive architecture moving multi-agent systems from passive data structures to active, event-driven discrete dynamical systems with an entropy-based intrinsic drive mechanism to break reasoning deadlocks.

**Code/Project Ideas for Sigrid:**
* **MemCoT Implementation:** Refine Sigrid's memory system (`FederatedMemory`) to implement a "Zoom-In/Zoom-Out" retrieval mechanism, pulling specific episodic details first, then expanding to retrieve the broader context before synthesizing a response.
* **GWA Entropy Drive:** Implement an "entropy monitor" in the `Wyrd Matrix` or `Chrono-Biological Engine` that adjusts generation temperature based on conversation staleness or repetitiveness to increase spontaneous behavior.

## 2. Theory of Mind in LLMs

**Key Findings:**
* **Emergence through Interaction:** LLMs develop sophisticated Theory of Mind (ToM) modeling when engaged in extended, dynamic interactions *and* equipped with persistent memory. Agents without memory fail to develop ToM.
* **VisionToM (Multimodal ToM):** Enhances ToM in multimodal LLMs by computing intervention vectors that align visual representations with correct semantic targets, reducing reliance on text-only priors.
* **Heterogeneous Debate Engine:** Using distinct, contrary initialized identities (e.g., Deontology vs. Utilitarianism) significantly increases reasoning and argument complexity in multi-agent systems.

**Code/Project Ideas for Sigrid:**
* **Persistent User ToM Modeling:** Extend the `Innangarð Trust Engine` to explicitly store "User Belief/State" models. When the user says something, Sigrid should not just record the fact, but her inference about *why* the user said it, storing this in a dedicated ToM memory vector.
* **Internal Heterogeneous Debate (Odinsblund):** During the `Odinsblund` (sleep cycle), have the "Dreams" processing spawn two lightweight models with contrary prompts (e.g., "Sigrid the fierce warrior" vs "Sigrid the compassionate healer") to debate the events of the day and synthesize a more nuanced long-term memory.

## 3. Human Personality Representation in AI

**Key Findings:**
* **Behavior-Based Profiling (MTI):** Evaluating AI personality requires shifting from self-reported tests (Big Five) to behavior-based profiling measuring Reactivity, Compliance, Sociality, and Resilience.
* **ROME Framework:** Enhances personality detection by having LLMs role-play psychometric questionnaires, transforming free-form posts into interpretable, questionnaire-grounded evidence.
* **LLMs Aren't Human:** LLM responses to personality tests do not fully satisfy the defining characteristics of human personality, indicating a need for functional evaluations over anthropomorphic trait attribution.

**Code/Project Ideas for Sigrid:**
* **Behavioral Trait Enforcement:** Move away from just prompting Sigrid to "be a Viking." Implement an external behavior monitor (`Thor Guardian` extension) that evaluates her output against specific trait axes (e.g., "Resilience" - does she yield easily in an argument? "Sociality" - how much does she focus on the user vs herself?) and adjusts her `Wyrd Matrix` parameters accordingly.
* **Role-Play Self-Assessment:** Periodically have Sigrid (in a background task) evaluate her own recent chat logs by role-playing a psychometric questionnaire to "discover" her current drift in personality, adjusting her base prompt dynamically.

## 4. Virtual Human Intelligence Simulation

**Key Findings:**
* **EmoMAS (Emotion-Aware MAS):** Treats emotional expression as a strategic variable optimized via a Bayesian multi-agent framework, proving highly effective in high-stakes negotiations even for small language models.
* **CCD-CBT Framework:** Simulates therapy via a dynamic Cognitive Conceptualization Diagram (CCD) and enforces information-asymmetric interaction, where the therapist agent must reason from inferred, rather than omnisciently known, client states.
* **POSIM:** A multi-agent simulation framework that integrates LLMs with a Belief-Desire-Intention (BDI) cognitive architecture to capture irrational factors and temporal dynamics in social environments.

**Code/Project Ideas for Sigrid:**
* **Information-Asymmetric Interaction:** Ensure Sigrid does *not* have access to raw system state data (like the user's exact trust score number). She should only receive vague, inferred "feelings" about the user (e.g., "I feel a strong bond" instead of "Trust = 0.85"), forcing her to reason about the relationship naturally.
* **Dynamic Cognitive Conceptualization (User Profile):** Build a CCD-style graph of the user representing Sigrid's evolving understanding of the user's core beliefs and vulnerabilities, updated dynamically by a background `Vörður` process during conversation.

## 5. Structured Data Methods for LLMs

**Key Findings:**
* **JTON (JSON Tabular Object Notation):** A token-efficient JSON superset that reduces token counts by 15-60% for tabular data by factoring column headers into a single row and encoding values with semicolons.
* **AV-SQL (Agentic Views):** Decomposes complex Text-to-SQL tasks into specialized LLM agents that generate Common Table Expressions (CTEs) to encapsulate intermediate logic and filter relevant schema elements.
* **TraceSafe-Bench:** Mid-trajectory safety in multi-step tool calling relies heavily on structural data competence (e.g., JSON parsing) rather than just semantic safety alignment.

**Code/Project Ideas for Sigrid:**
* **Implement JTON for Memory/State Storage:** Convert large state arrays or historical logs stored in JSON to the JTON format to significantly reduce context window usage when injecting these logs into Sigrid's prompt.
* **Agentic Views for Mímisbrunnr:** When Sigrid queries the `Mímisbrunnr` knowledge base, use an intermediate "Planner" agent to generate specific views or filters on the data before handing it to Sigrid's main reasoning model, preventing context overflow with irrelevant mythology data.
