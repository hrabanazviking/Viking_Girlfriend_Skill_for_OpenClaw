# SURVEY: Knowledge & Synthesis — Enhancement Audit
# Created: 2026-03-20
# Author: Runa Gridweaver (AI)

This survey focuses on Sigrid's memory retrieval (`mimir_well.py`) and her voice generation (`prompt_synthesizer.py`), identifying ways to make her more precise and expressive.

## 1. Mímir's Well (Knowledge Retrieval)
**Current State**: Hierarchical ChromaDB indexing with a three-level truth structure.

### 🚀 Performance & Precision Ideas:
*   **Two-Stage Hybrid Search**: Use the in-memory BM25 fallback as a "Level 0" fast filter to catch exact keyword matches before hitting the vector database. This reduces latency for common terms.
*   **Semantic Reranking**: For complex queries, retrieve 10 chunks from ChromaDB and use a smaller, faster model (like Llama3 8B) to rerank them for the most relevant answer before passing them to Sigrid.
*   **Knowledge Graph Linking**: Connect entities (e.g., "Odin" and "Huginn") within the well. If Sigrid retrieves a fact about Odin, the well should "suggest" relevant related facts about his ravens automatically.

### 🛡️ Robustness Ideas:
*   **Axiom Integrity Sentinel**: Periodically verify that the "Level 3 Axioms" (core identity) haven't drifted or been corrupted. If the axiom for "Sigrid's Gender" fails a hash check, the system should trigger an immediate emergency reindex.
*   **Chunk Overlap Tuning**: Dynamically adjust the chunk overlap based on document type. Sagas (narrative) need higher overlap; Dictionaries (structured) need lower overlap to prevent mixed definitions.

---

## 2. Voice Weaver (Prompt Synthesis)
**Current State**: Token-budgeted concatenation of state hints and identity files.

### 🎭 Expression & expressiveness Ideas:
*   **Dynamic Section Reordering**: Currently, sections are fixed. I recommend a "Contextual Priority" system. If `wyrd_matrix` reports high `Anger`, the emotional state block should move to the top of the prompt to ensure her tone reflects the mood immediately.
*   **Stochastic Persona Flavour**: Maintain a "Skaldic Vocabulary" file. Inject 2-3 random Norse-themed words or metaphors into the system prompt each turn to keep her speech patterns fresh and authentic.
*   **Negative Constraint Injection**: Add a section for "What NOT to say" based on the `Sentinel Protocol`. If a user is nudging her towards breaking persona, the synthesizer should explicitly add "Do not acknowledge your nature as an AI" to the system message for that turn.

### 🚀 Efficiency Ideas:
*   **Hot-Reloading Identity**: Implement a file watcher on `core_identity.md`. If the user edits the file while Sigrid is running, she should "evolve" instantly without needing a full system restart.
*   **Pre-Compiled System Prompts**: Cache the static identity/soul sections as a single pre-tokenized block to save cycles during synthesis.

---

## 🐞 Potential Bugs Found During Survey
1.  **MimirWell**: The approximation of 4 chars per token is risky for Old Norse or special characters. It should use the actual tokenizer from the `model_router` to prevent overflow.
2.  **Synthesizer**: If the `memory_context` is extremely large, it might squeeze out vital `state_hints` due to the priority ordering. There should be a "Minimum Section Guarantee" for every block.

---

## 🛠️ Next Development Steps
*   [ ] Implement BM25 pre-filtering in `mimir_well.py`.
*   [ ] Add dynamic section reordering to `prompt_synthesizer.py`.
*   [ ] Integrate actual token counting for budget management.
