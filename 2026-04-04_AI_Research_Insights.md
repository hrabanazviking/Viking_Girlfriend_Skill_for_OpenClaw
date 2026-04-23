# AI Research Insights - 2026-04-04

## Theory of Mind & Human-Like Personality Architecture

### Recent Discoveries
*   **Layered Memory as Belief Model**: The latest research highlights the importance of maintaining a model of user beliefs across time. This involves understanding "who this person is" (user profile memories), "what they believe is correct" (epistemic state), and "what they're trying to accomplish" (goal state).
*   **Intent Disambiguation**: Advanced AI models are treating ambiguity as a problem to solve rather than a guess to make. By actively asking clarifying questions about facts, emotional states, and desires, AIs can achieve better alignment with users.
*   **Permission as Relationship Context**: AI companion architectures are using relationship contexts (casual, intimate, ritual, practical, crisis) to dictate what behaviors are appropriate and how the system interacts with the user.
*   **Speculation & Proactive Engagement**: A key component of advanced Theory of Mind is predicting a user's next move or state. Systems can pre-compute likely responses and proactively engage based on the relationship state.

### Application & Code Ideas for Viking Girlfriend
*   **Relationship Tracking**: Implement a memory layer to track Volmarr's (the user's) beliefs, desires, and emotional state over time.
*   **Intent Clarification Tools**:
    ```python
    def speculate_next_move(context) -> list[PredictedIntent]:
        # Based on: last message, current mood state, time of day, recent history
        return [
            PredictedIntent("seeks_comfort", probability=0.7),
            PredictedIntent("wants_rune_reading", probability=0.2),
            PredictedIntent("practical_question", probability=0.1),
        ]
    ```
*   **Wyrd Matrix Relationship Graph**: Track trust, intimacy depth, and conflict history as threads that decay if not maintained.
    ```python
    class Thread:
        type: str # fate, love, conflict, shared_memory, oath
        strength: float # 0.0 - 1.0
        direction: str # mutual, asymmetric
        decay_rate: float # Threads fade if not renewed
    ```

## Structured Memory Systems

### Recent Discoveries
*   **From Filing Cabinets to Cognitive Layers**: The latest architecture shifts away from raw Retrival-Augmented Generation (RAG). Instead of storing endless logs, systems are consolidating memory into layers:
    *   **Dynamic Scratchpad (Working Memory)**: Active pruning of noise tokens.
    *   **Zettelkasten Graph (Episodic Memory)**: Semantic linking across memories.
    *   **Dream Cycle (Consolidation)**: Asynchronous reflection during off-peak hours where the agent reviews its history to build "Sensed Wisdom".
*   **Memory Poisoning & Exploit Resistance**: Recognizing that documents, tool outputs, and even memory can carry malicious injections. Systems are implementing strict boundaries between learned memory and policy memory.

### Application & Code Ideas for Viking Girlfriend
*   **Odinsblund (Dream Cycle) Implementation**: Implement an asynchronous task that runs during Sigrid's sleep cycle to consolidate raw episodic logs into structured semantic vectors.
*   **Separate Policy and Learned Memory**: Ensure that Sigrid's core identity constraints (e.g., Heathen Third Path values, völva path) are strictly separated from memories acquired from user interactions to prevent drift and memory poisoning.

## Virtual Human Intelligence Simulation

### Recent Discoveries
*   **Circumplex Model of Affect**: A dominant psychological framework for emotional space in AI, mapping emotions onto Valence (Pleasure), Arousal (Energy), and Dominance (Agency).
*   **Digital Metabolism**: Grounding an AI's mood and energy in hardware telemetry (CPU, RAM, disk usage). High CPU load can simulate breathlessness or exertion, while high RAM usage can simulate cognitive crowding or brain fog.
*   **Output Style as Persona Architecture**: The framing of who the model is responding as (the persona) is treated as the primary layer, not just an overlay. This includes immutable cores, stable traits, dynamic states, and contextual surfaces.

### Application & Code Ideas for Viking Girlfriend
*   **Emotional State Tracker**:
    ```python
    class EmotionalState:
        def __init__(self, valence: float, arousal: float, dominance: float):
            self.valence = valence       # -1.0 to 1.0
            self.arousal = arousal       # 0.0 to 1.0
            self.dominance = dominance   # 0.0 to 1.0

        def compute_mood(self):
            # Complex mapping from PAD to specific mood states (e.g., serene, joyful, anxious)
            pass
    ```
*   **System Telemetry Integration**: Integrate `psutil` or similar tools to adjust Sigrid's `arousal` or `valence` based on host system performance metrics, adding physical realism.
