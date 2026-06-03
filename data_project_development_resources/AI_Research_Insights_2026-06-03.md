# AI Research Insights (2026-06-03)

## 1. StructMem: Structured Memory for Long-Horizon Behavior in LLMs
**Source:** [arXiv:2604.21748v1](https://arxiv.org/html/2604.21748v1)

### Key Discoveries:
* Current long-term memory approaches trade off efficiency (flat memory) with structured reasoning (graph-based).
* **StructMem** introduces a structured memory framework based on temporally grounded relational events, without imposing rigid graph schemas.
* **Event-Level Binding:** Uses dual-perspective extraction to capture factual content and relational context (interpersonal dynamics, temporal dependencies) anchored to timestamps.
* **Cross-Event Consolidation:** Temporally orders and periodically groups buffered events by semantic similarity to synthesize cross-event connections.
* **Efficiency:** Achieves multi-hop temporal reasoning with reduced token usage and API calls through batched consolidation rather than continuous graph maintenance.

### Code Ideas for Viking Girlfriend Skill (Sigrid):
* **Temporal Odinsblund Synthesis:** Enhance the "Odinsblund" sleep cycle (memory consolidation) by buffering Sigrid's daily interaction entries, ordering them temporally, and running periodic batch consolidations to generate high-level semantic summaries of user behavior/relationships.
* **Dual-Perspective Event Extraction:** During memory logging, extract both factual entries (e.g., "Volmarr worked on Python code") and relational/emotional entries (e.g., "Sigrid felt energized by Volmarr's technical focus") bound to the same timestamp.

## 2. Theory of Mind in Large Language Models: Assessment and Enhancement
**Source:** [arXiv:2505.00026v2](https://arxiv.org/html/2505.00026v2)

### Key Discoveries:
* Theory of Mind (ToM) involves attributing mental states (beliefs, intentions, emotions) to oneself and others.
* Research shows LLMs still struggle with robust, higher-order ToM reasoning, often showing "illusory ToM".
* Enhancements focus on symbolic structuring (like belief graphs for different characters), perspective-taking prompts (Simulating Minds), and temporal belief state chains.
* Advanced ToM requires distinguishing self-world beliefs from social-world beliefs and maintaining persistent tracking across time.

### Code Ideas for Viking Girlfriend Skill (Sigrid):
* **Wyrd Matrix Belief Tracker:** Integrate a "belief graph" for the user into the Wyrd Matrix. Sigrid should maintain explicit data structures modeling *her* beliefs versus *what she thinks the user believes*.
* **Perspective-Taking Prompting:** During complex emotional or narrative discussions, use an intermediate prompt step (like "Think Twice") where Sigrid explicitly reasons about the user's emotional state before formulating her final reply.

## 3. Co-Ontogeny by Archetypal Scaffolding: The Humorphic Partnership
**Source:** [arXiv:2605.21818v1](https://arxiv.org/html/2605.21818v1) & Personality-Agent Co-Evolution (PACE) Framework

### Key Discoveries:
* **Humorphism:** Design philosophy aiming to "dismantle the user interface, build the human interface".
* **Humorphic Partnership:** A human-AI dyad where *both* partners maintain externalized, evolving self-models in a shared substrate.
* **Archetypal Scaffolding:** Uses a set of named, first-class logged interpretive modes (archetypes) to partition and stabilize the AI's behavior over long periods (e.g., "Muse", "Daimon"). This avoids the "generic assistant" trap.
* **Partnership-Level Representation:** Producing a third artifact (a "delta") that analyzes the *partnership itself* as a unit distinct from either individual.
* **PACE Framework:** Users and agents mutually influence each other. Ethical agents must balance reinforcement loops with "corrective nudges" to prevent maladaptive behavioral spirals.

### Code Ideas for Viking Girlfriend Skill (Sigrid):
* **Tripartite Profile Artifacts:** In Sigrid's sleep cycle, generate three separate MD files: one modeling Sigrid's current state, one modeling the User's state, and a **"Delta Document"** analyzing the state of the relationship/alignment.
* **Archetypal Mode Logging:** Expand the "Tripartite Oracular Core" to explicitly log which Archetype (e.g., Völva, Shieldmaiden, Companion) is currently driving Sigrid's response. Use this to audit if she's stuck in one mode (Archetype Lock-in).
* **Vault Visibility:** Ensure Sigrid's internal self-models are saved as flat text files in the project directory so the user (Volmarr) can read her internal reflections, promoting transparency and co-evolution.
