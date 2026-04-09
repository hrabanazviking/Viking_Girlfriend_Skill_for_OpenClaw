# Recent Research Discoveries in AI, LLMs, and Virtual Humans (2025-2026)

## 1. Adaptive Memory Structures for LLM Agents
Recent research, such as "Choosing How to Remember: Adaptive Memory Structures for LLM Agents" (arXiv:2602.14038), highlights that long-horizon interactions require agents to accumulate, retain, and retrieve information across many turns while user goals and contexts evolve over time.

Three main memory paradigms were identified:
1.  **Flat retrieval-based memory:** Good for simple facts but limited in relational reasoning.
2.  **Explicitly structured memory:** Organizes memory into linked notes or graph-like representations. Excellent for relational reasoning but often rigid.
3.  **Policy-managed memory systems:** Regulates memory via controllers (e.g., decay, redundancy filtering, or RL-based controllers).

**Impact on Project:**
Our `FederatedMemory` system can be enhanced by incorporating a "Policy-Managed Memory Decay" system to handle memory truncation more naturally, and "Explicitly structured memory" through Knowledge Graphs (Triple Stores) for relational reasoning between Norse mythology entities.

## 2. Theory of Mind (ToM) Inference
The JHU-Amazon Initiative for Interactive AI (AI2AI 2025-2026) is heavily investing in continuous Theory of Mind inference from streaming multimodal inputs. The goal is "mental state guided proactive AI assistance and communication".

**Impact on Project:**
Sigrid and Astrid should not just react; they should maintain a running hypothesis of the *user's* current mental and emotional state (e.g., stressed, inquisitive, seeking comfort) and proactively adjust their dialogue style.

## 3. Personality Prompting for Embodied Virtual Agents
Research from the USC Viterbi School of Engineering presented at IVA 2025 ("Can LLMs Generate Behaviors for Embodied Virtual Agents Based on Personality Prompting?") proves that virtual human avatars can adapt to assume certain personality traits dynamically, rather than relying on static system prompts. This increases empathy and realism.

**Impact on Project:**
Instead of a static persona prompt for Sigrid, we can use a dynamic "Personality Matrix" that shifts her expressed traits (e.g., stoicism vs. warmth) based on the context of the conversation and the user's trust tier (Innangarð).

---

# Code Ideas and Implementation Concepts

## Idea 1: Policy-Managed Memory Decay System
Implement a memory decay function to naturally age out less important episodic memories while preserving core beliefs and high-trust interactions.

```python
from datetime import datetime, timedelta
from typing import List, Dict

class EpisodicMemory:
    def __init__(self, content: str, importance: float):
        self.content = content
        self.timestamp = datetime.now()
        self.importance = importance # 0.0 to 1.0
        self.reinforcement_count = 0

    def get_salience(self) -> float:
        """Calculate current salience based on time decay and importance."""
        age_days = (datetime.now() - self.timestamp).days
        # Decay factor: importance resists decay, age increases it.
        decay = (age_days * 0.1) / (self.importance + 0.1)
        # Reinforcement boosts salience
        boost = self.reinforcement_count * 0.2
        return max(0.0, self.importance - decay + boost)

    def reinforce(self):
        self.reinforcement_count += 1
```

## Idea 2: Theory of Mind (ToM) State Tracker
A simple state tracker to maintain an active hypothesis of the user's current mood.

```python
from enum import Enum
from pydantic import BaseModel

class UserMentalState(Enum):
    STRESSED = "stressed"
    CURIOUS = "curious"
    GRIEVING = "grieving"
    JOYFUL = "joyful"
    NEUTRAL = "neutral"

class TheoryOfMindTracker(BaseModel):
    current_hypothesis: UserMentalState = UserMentalState.NEUTRAL
    confidence_score: float = 0.5
    evidence_log: list[str] = []

    def update_hypothesis(self, new_state: UserMentalState, evidence: str, confidence: float):
        self.current_hypothesis = new_state
        self.confidence_score = confidence
        self.evidence_log.append(evidence)
        if len(self.evidence_log) > 5:
            self.evidence_log.pop(0) # Keep only recent evidence

    def get_prompt_modifier(self) -> str:
        if self.current_hypothesis == UserMentalState.STRESSED and self.confidence_score > 0.7:
            return "The user seems stressed. Respond with grounded, calming Norse wisdom. Be concise and supportive."
        elif self.current_hypothesis == UserMentalState.CURIOUS:
            return "The user is curious. Provide detailed historical or mythological context."
        return ""
```

## Idea 3: Dynamic Personality Matrix
Adjusting Sigrid's personality based on relationship progress (Wyrd/Frith).

```python
class PersonalityMatrix:
    def __init__(self, base_warmth: float, base_stoicism: float):
        self.warmth = base_warmth
        self.stoicism = base_stoicism

    def adjust_for_trust_tier(self, trust_tier: str):
        if trust_tier == "Innangarð": # Inner circle
            self.warmth += 0.3
            self.stoicism -= 0.2
        elif trust_tier == "Utangarð": # Outsider
            self.warmth -= 0.2
            self.stoicism += 0.3

        # Bound values
        self.warmth = max(0.0, min(1.0, self.warmth))
        self.stoicism = max(0.0, min(1.0, self.stoicism))

    def generate_system_instruction(self) -> str:
        return f"Adopt a persona with a warmth level of {self.warmth:.1f}/1.0 and a stoicism level of {self.stoicism:.1f}/1.0."
```
