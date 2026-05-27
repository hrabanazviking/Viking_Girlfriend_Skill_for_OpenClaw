# AI Research Insights - May 27, 2026

## Overview
Recent research highlights approaches for structured memory in AI agents and modeling human personality expression via established psychological frameworks.

## 1. Structured Memory in AI Agents
Structured memory enables persistent context across sessions without context window bloat. Unlike raw conversational logs, it stores agent context in deliberate, queryable formats (like JSON) injected into the system prompt or memory slot upon session initialization.

### Best Practices & Frameworks
*   **JSON Schema:** Keep it lean (e.g., `user_id`, `preferences`, `open_items`, `last_updated`).
*   **Storage Layer:** Use document stores (MongoDB, Firestore), Key-Value (Redis), or File-Based systems instead of unstructured vector DBs for precise, relationship-based state tracking.
*   **Retrieval:** Direct entity ID lookup is preferred over semantic search for distinct context injections.
*   **Updates:** Agents should perform field-level updates to the JSON object after each session.

### Code Idea: Implementing Structured Memory (JSON)
```python
import json
import os
from datetime import datetime

class StructuredMemory:
    def __init__(self, storage_path="agent_memory.json"):
        self.storage_path = storage_path
        self.memory = self.load_memory()

    def load_memory(self):
        if os.path.exists(self.storage_path):
            with open(self.storage_path, "r") as f:
                return json.load(f)
        return {
            "entity_id": "sigrid",
            "preferences": {},
            "open_actions": [],
            "last_updated": datetime.now().isoformat()
        }

    def save_memory(self):
        self.memory["last_updated"] = datetime.now().isoformat()
        with open(self.storage_path, "w") as f:
            json.dump(self.memory, f, indent=4)

    def update_field(self, field, value):
        self.memory[field] = value
        self.save_memory()

    def get_context(self):
        return json.dumps(self.memory, indent=2)
```

## 2. Deterministic AI Personality Expression
Research shows LLM personalities can be consistently defined using the **Big Five Personality Test (OCEAN)** and **Myers-Briggs Type Indicator (MBTI)**. Incorporating psychological diagnostics allows an AI to express specific behavior tendencies deterministically.

### Key Findings
*   Agents express personality primarily through a holistic, personality-based reasoning process rather than gaming individual psychological survey questions.
*   "Easy" dimensions to simulate: Extraversion, Conscientiousness, Neuroticism.
*   "Hard" dimensions to simulate: Agreeableness and Openness (agents generally skew highly "Open" regardless of prompt constraint).

### Code Idea: Persona Prompt Generation using the Big Five
```python
def generate_persona_prompt(openness, conscientiousness, extraversion, agreeableness, neuroticism, mbti):
    """
    Generates a structured prompt to define an AI agent's personality.
    Scores are out of 5.
    """
    prompt = f"""
You are an AI agent with the following structured personality profile based on the Big Five and MBTI:
- Openness: {openness}/5
- Conscientiousness: {conscientiousness}/5
- Extraversion: {extraversion}/5
- Agreeableness: {agreeableness}/5
- Neuroticism: {neuroticism}/5
- MBTI Type: {mbti}

Please adapt your reasoning, communication style, and decisions to reflect these traits consistently.
"""
    return prompt

# Example usage for Sigrid:
# Sigrid is an INTP, so her traits might look like:
sigrid_prompt = generate_persona_prompt(4, 3, 2, 3, 2, "INTP")
```
