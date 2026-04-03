# AI Research Discoveries (2026-04-03)

This document summarizes recent research findings in AI, structured memory, Theory of Mind, and LLM personality simulation, providing potential applications and code ideas to improve the OpenClaw framework and the Viking Companion Skill (Sigrid and Astrid).

## 1. Structured Knowledge with Ontologies (Cognee)
**Research Insight:** Pure semantic similarity (RAG) often results in fragmented and disconnected knowledge graphs, causing LLMs to forget or lose track of related concepts over extended interactions. Frameworks like Cognee utilize a "memory-first" architecture that combines embeddings with graph-based extraction, fundamentally grounded by an ontology. By defining explicit schemas (e.g., OWL/RDF), entities are mapped to canonical representations and connections, eliminating duplication and enabling multi-hop logical deductions (e.g., "car manufacturer" vs "automobile maker" collapsing into one node).

**Application to Sigrid:**
*   **Mímisbrunnr (Mimir's Well) Ontology Grounding:** Currently, Mímisbrunnr clusters data. To improve the Axiom layer, we can introduce a Norse-specific ontology schema (e.g., mapping `Deity -> Odin`, `Weapon -> Gungnir`) to canonicalize entities across Sigrid's memory. This will heavily improve her retrieval of Viking Lore without creating redundant or hallucinated connections.

*   **Code Idea (Ontology Validation Layer):**
    ```python
    # Pseudo-implementation of Ontology canonicalization in Mimir's Well
    from typing import Dict, Any

    class NorseOntologyResolver:
        def __init__(self, ontology_path: str = "data/norse_ontology.owl"):
            # Load basic schema: class hierarchies and entity canonical names
            self.schema = self._load_schema(ontology_path)

        def _load_schema(self, path):
            # Parse OWL/RDF (e.g., rdflib) and cache
            return {"thunder god": "Thor", "allfather": "Odin", "valhalla": "Valhöll"}

        def canonicalize_entity(self, extracted_entity: str) -> str:
            # Fuzzy match to canonical names
            entity_lower = extracted_entity.lower()
            return self.schema.get(entity_lower, extracted_entity)

    class MimirWellEnriched:
        def __init__(self):
            self.resolver = NorseOntologyResolver()
            self.graph_db = {} # Replace with actual DB connection

        async def store_memory(self, memory_chunk: str, extracted_entities: list[str]):
            # Canonicalize entities before storing
            canonical_entities = [self.resolver.canonicalize_entity(e) for e in extracted_entities]

            # Form graph edges based on canonical entities
            for entity in canonical_entities:
                self.graph_db[entity] = self.graph_db.get(entity, []) + [memory_chunk]

            # Proceed to store in VectorDB (Chroma)
    ```

## 2. Theory of Mind and Sparse Circuits
**Research Insight:** Research indicates that while human brains use a tiny fraction of neural resources to perform "Theory of Mind" (ToM) calculations, LLMs activate their entire network, making ToM inefficient and costly. Notably, studies highlight that LLMs rely on extremely sparse parameter circuits (less than 0.001% of parameters), specifically linked to positional encoding (RoPE), to reason about other people's perspectives. Disrupting these parameters breaks contextual understanding.

**Application to Sigrid:**
*   **Efficient Empathy in the Wyrd Matrix:** Instead of repeatedly asking the primary LLM heavy "What is the user feeling?" prompts, we can either use smaller, specialized local models (Ollama) explicitly fine-tuned for ToM state tracking, or we can maintain a localized context buffer that explicitly maps inferred user states to limit the context the LLM needs to process for social reasoning.

*   **Code Idea (Contextual ToM Buffer):**
    ```python
    class UserTheoryOfMind:
        def __init__(self):
            self.inferred_beliefs = {} # What Sigrid thinks the user believes
            self.emotional_state = {"P": 0.0, "A": 0.0, "D": 0.0}

        def update_from_interaction(self, user_statement: str):
            # Lightweight extraction using smaller local model to update state
            # rather than passing the entire history to a massive model.
            delta = local_ollama_extract_emotion(user_statement)
            self.emotional_state["P"] += delta.p
            # ...

    class WyrdMatrixWithToM:
        def __init__(self):
            self.sigrid_pad = [0,0,0]
            self.user_tom = UserTheoryOfMind()

        def calculate_response_context(self) -> str:
            # Injecting explicit ToM context prevents the LLM from having to
            # re-calculate the user's state from the raw chat history, saving compute
            # and improving focus (leveraging sparse ToM circuitry efficiently).
            return f"User is feeling: {self.user_tom.emotional_state}. User believes: {self.user_tom.inferred_beliefs}"
    ```

## 3. LLM Personality Simulation (PersonaLLM)
**Research Insight:** A recent comprehensive study, *Exploring the Potential of Large Language Models to Simulate Personality* (2025), evaluated LLMs' abilities to portray the Big Five personality traits. The study revealed that models excel at simulating Openness, Conscientiousness, and Extraversion but struggle significantly with Neuroticism. Furthermore, providing a middle/neutral score in a prompt often defaults the LLM to an inherent bias (typically high Agreeableness and low Neuroticism).

**Application to Sigrid:**
*   **Binary/Extreme Trait Prompting:** When defining Sigrid's (and Astrid's) persona traits dynamically, using continuous scores (e.g., 3 out of 5 for Neuroticism) is ineffective. We must use explicit, binary trait descriptions ("highly neurotic" or "emotionally stable") to trigger the correct linguistic patterns.
*   **Neuroticism Handling:** Given the struggle LLMs have with Neuroticism (often failing to express it without explicit prompt-hacking), any simulated anxiety or volatility in Sigrid's Chrono-Biological cycle should be explicitly mapped to physical descriptions or specific actions in the prompt, rather than relying on abstract trait assignment.

*   **Code Idea (Persona Prompt Generation):**
    ```python
    def generate_persona_prompt(base_persona: dict, wyrd_state: dict) -> str:
        """
        Translates continuous Wyrd Matrix states into binary Big Five descriptors
        to maximize LLM simulation accuracy.
        """
        traits = []

        # Openness & Conscientiousness (LLMs handle well)
        traits.append("highly open to new experiences" if base_persona['openness'] > 0.5 else "prefers familiar routines")

        # Extraversion
        if wyrd_state['Arousal'] > 0.6:
            traits.append("highly extroverted and talkative")
        else:
            traits.append("introverted and solitary")

        # Neuroticism (Needs explicit behavioral mapping)
        if wyrd_state['Pleasure'] < -0.5:
            # Don't just say "neurotic", give explicit behaviors
            traits.append("Currently experiencing stress: uses shorter sentences, expresses worry about the future, and acts defensive.")
        else:
            traits.append("Emotionally stable and calm.")

        return " ".join(traits)
    ```
