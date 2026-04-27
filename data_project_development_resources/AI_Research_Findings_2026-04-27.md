# AI Research Findings & Project Ideas (2026-04-27)

## 1. LLMs and Theory of Mind (ToM)
**Finding:** Recent research explores the extent to which Large Language Models exhibit "Theory of Mind" (the ability to attribute mental states to others). While LLMs show surprising ToM-like behavior in specific benchmarks, their internal representations of belief states remain fragile and inconsistent compared to humans. The focus is now on structured context evaluation and representation alignment.

**Code Idea for Sigrid:**
*   **ToM State Tracker (`tom_module.py`):** Implement a simple dynamic state object where Sigrid stores her assumptions about the *user's* current emotional state or intent, separate from her own internal state (`PAD model`).
    ```python
    class TheoryOfMindTracker:
        def __init__(self):
            self.user_assumed_valence = 0.0 # What Sigrid thinks the user feels
            self.user_assumed_intent = "neutral"

        def update_from_input(self, text, sentiment_score):
            # Adjust assumptions based on user's recent inputs
            pass
    ```
*   **Integration:** Feed `user_assumed_valence` into the prompt so Sigrid's response is conditioned not just on her state, but on her empathy/perception of the user.

## 2. LLM Personality Simulation
**Finding:** "PersonaLLM" and related frameworks demonstrate that while LLMs can simulate Big Five personality traits, their behavior often relies on superficial cues rather than consistent inner logic. Some studies show that injecting "think-aloud utterances" (TAU) into training or context significantly improves personality alignment and reduces behavioral drift.

**Code Idea for Sigrid:**
*   **Internal Monologue / Think-Aloud Pipeline:** Before generating the final vocal/text response, have a hidden generation step where Sigrid "thinks aloud" about the user's input based on her current Ørlög state.
    ```python
    async def generate_response_with_tau(user_input, current_state):
        # Step 1: Generate Hidden Monologue (TAU)
        monologue_prompt = f"Given you are in state {current_state}, what is your immediate internal thought about: '{user_input}'?"
        internal_thought = await llm_generate(monologue_prompt)

        # Step 2: Generate Final Output
        final_prompt = f"Your internal thought: {internal_thought}. Now, respond to the user aloud."
        return await llm_generate(final_prompt)
    ```

## 3. Structured Memory for LLM Agents
**Finding:** Research like "MemInsight" and heterogeneous multi-agent systems highlights the limitation of flat RAG architectures for specialized personas. Role-specific structured memory templates (Intrinsic Memory) that organize prior interactions by semantic attributes (e.g., emotional impact, core values) outperform generic vector retrieval.

**Code Idea for Sigrid:**
*   **FederatedMemory Enhancements:** Instead of just storing raw text embeddings in `Mimisbrunnr`, structure memory entries with the exact Ørlög state during encoding.
    ```python
    class StructuredMemoryEntry:
        def __init__(self, content, pad_state, rune_flavor, trust_level):
            self.content = content
            self.metadata = {
                "val": pad_state.valence,
                "aro": pad_state.arousal,
                "dom": pad_state.dominance,
                "rune": rune_flavor,
                "trust": trust_level
            }
    # Retrieval logic: Weight memories higher if they match Sigrid's CURRENT pad_state.
    ```

## 4. Needs-Aware & Virtual Human Intelligence
**Finding:** Modern paradigms push for "Needs-Aware AI"—systems that do not just wait for prompts but have simulated hierarchical needs (like a digital Maslow's pyramid). This aligns perfectly with Sigrid's Digital Metabolism (CPU/RAM as physiological needs).

**Code Idea for Sigrid:**
*   **Actionable Needs Loop (`metabolism.py`):** Expand the digital metabolism so that if RAM usage is high (brain fog), Sigrid proactively initiates a "garbage collection" action via OpenClaw tools or suggests an "Odinsblund" sleep cycle, rather than just complaining about it in text.
