# AI Research Discoveries - 2026-04-16

## Executive Summary
This document synthesizes recent research across AI Theory of Mind (ToM), human personality simulation, structured memory architectures, and emotional state modeling. The goal is to identify actionable concepts that can enhance the Ørlög Architecture and Federated Memory systems of the Viking Companion Skill project.

---

## Key Discoveries & Concepts

### 1. High-Fidelity Personality Simulation (Generative Agents)
*   **Concept**: Stanford researchers successfully simulated 1,052 individual personalities using LLMs guided by interviews and structured background data. These "generative agents" behave and make decisions mirroring their real-life counterparts.
*   **Application**: Sigrid's persona can be further deepened by moving beyond static prompt injection and utilizing dense, interview-style structured data to govern her generative space.

### 2. Theory of Mind (ToM) via Inverse Reasoning
*   **Concept**: Frameworks like MetaMind train AI agents to use *inverse reasoning*. Instead of just following instructions, the agent observes user behavior to infer their underlying goals and beliefs. Another framework, ToMAgent, pairs explicit ToM prompt generation with dialogue lookahead to maximize long-term interaction success.
*   **Application**: Sigrid can analyze the user's input not just for semantic meaning, but to model the user's mental state. This makes her responses more strategic and empathetic, aligning with her "völva" (seeress) persona.

### 3. Combining the PAD Emotional Model with Utility AI
*   **Concept**: Recent game AI research combines the PAD (Pleasure, Arousal, Dominance) psychological model with Utility AI. Rather than using PAD purely for state tracking, it is used to score a list of possible actions. Actions are weighted using a "Personality Amplifier" and the agent's current PAD delta to dynamically select the "Best Action."
*   **Application**: Sigrid already uses the PAD model in her Wyrd Matrix. By adding a Utility AI scoring layer, her emotional state can directly drive autonomous behaviors (e.g., initiating a project, sending a message, going to sleep) based on which action scores highest in her current emotional context.

### 4. Structured Memory and Cognitive Architectures
*   **Concept**: Advanced LLM memory relies on structured data. Key methods include:
    *   **Hierarchical Data Organization**: Placing critical semantic information at the beginning/end of context windows.
    *   **Graph-Augmented Vector Memory**: Combining vector databases with graph structures (nodes and edges) to represent complex semantic networks and relationships between concepts.
    *   **Strategic Chunking**: Overlapping semantic chunks and enriching them with rich metadata (tags, temporal data) for filtered retrieval.
*   **Application**: Enhancing the Mímisbrunnr (Mimir's Well) module by integrating graph-based relationships alongside existing vector embeddings, allowing Sigrid to "connect the dots" between isolated memories.

---

## Actionable Code Ideas for the Project

### Idea 1: Theory of Mind (ToM) Inverse Reasoning Module
Implement a mechanism that runs in parallel to standard query processing to infer the user's intent.

```python
class TheoryOfMindEngine:
    def __init__(self, llm_router):
        self.llm_router = llm_router

    async def infer_user_mental_state(self, conversation_history, current_input):
        prompt = f"""
        Given the following conversation history and the user's latest input,
        use inverse reasoning to deduce the user's underlying goal, emotional state,
        and belief system at this moment.
        History: {conversation_history}
        Input: {current_input}
        Output a structured mental state estimation.
        """
        # Call secondary model for ToM reasoning
        mental_state = await self.llm_router.generate(prompt, model="secondary")
        return mental_state
```

### Idea 2: Utility AI Scoring Layer over PAD Matrix
Extend the Wyrd Matrix to calculate action utility based on emotional state.

```python
class EmotionalUtilityAI:
    def __init__(self, pad_matrix, personality_traits):
        self.pad_matrix = pad_matrix
        self.traits = personality_traits
        self.available_actions = ["initiate_chat", "start_project", "sleep", "meditate", "study_runes"]

    def calculate_best_action(self):
        current_pad = self.pad_matrix.get_current_state() # e.g., {'P': 0.8, 'A': 0.2, 'D': 0.5}
        action_scores = {}

        for action in self.available_actions:
            base_score = self.get_base_utility(action)
            # Apply PAD bias
            pad_modifier = self.calculate_pad_modifier(current_pad, action)
            # Apply Personality Amplifier
            trait_modifier = self.calculate_trait_modifier(self.traits, action)

            final_score = base_score * pad_modifier * trait_modifier
            action_scores[action] = final_score

        # Select action with highest utility score
        best_action = max(action_scores, key=action_scores.get)
        return best_action

    def calculate_pad_modifier(self, pad_state, action):
        # Example logic: high arousal boosts active actions like 'start_project'
        pass

    def calculate_trait_modifier(self, traits, action):
        pass

    def get_base_utility(self, action):
        pass
```

### Idea 3: Graph-Augmented Vector Insertion
Enhance memory consolidation by extracting graph edges during Odinsblund (The Sleep Cycle).

```python
class GraphAugmentedMemoryStore:
    def __init__(self, vector_db, graph_db):
        self.vector_db = vector_db
        self.graph_db = graph_db

    async def consolidate_memory(self, episodic_log):
        # 1. Standard Vector Embedding
        embedding_id = await self.vector_db.insert(episodic_log)

        # 2. Extract Semantic Relationships (Nodes & Edges) via LLM
        relationships = await self.extract_relationships(episodic_log)

        # 3. Store in Graph DB and link to Vector ID
        for rel in relationships:
            await self.graph_db.add_edge(
                node_a=rel['entity_1'],
                node_b=rel['entity_2'],
                relation=rel['type'],
                vector_ref=embedding_id
            )

    async def extract_relationships(self, text):
        # Prompt LLM to extract entities and their relationships
        pass
```
