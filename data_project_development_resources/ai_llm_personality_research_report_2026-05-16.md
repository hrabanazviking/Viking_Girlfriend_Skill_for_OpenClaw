# AI Research Data - Theory of Mind, LLMs, and Persona

Based on the latest available academic reviews and insights:

## Key Findings

1. **Psychological Theories in LLMs** (from "A Review of Incorporating Psychological Theories in LLMs")
   - Theory of Mind (ToM) offers a framework for evaluating how individuals understand and attribute mental states (beliefs, desires, intentions) to others. Benchmarks are increasingly probing different facets of ToM in LLMs, including social reasoning, white lies, and temporally evolving mental states.
   - **Debates**: Does GPT-4 (which solves ~75% of false-belief tasks, matching a 6-year-old) show emergent ToM-like reasoning, or is it pattern matching? Minor prompt changes can derail results.

2. **Personality Simulation and Evaluation**
   - **Consistency Issues**: LLMs often struggle with personality consistency. For example, language switching can alter displayed traits, and traits like Neuroticism and Agreeableness are harder to align.
   - **Enhancing Role-Play**: Training with psychometrically valid data (Big Five traits) and incorporating cognitive architectures (like Dual-process theory for fast/slow thinking) can improve persona stability.
   - **Social Dynamics**: Modeling social influence (persuasion) and group dynamics using multi-agent setups. LLMs can mimic conformity and in-group bias, which is useful for realistic simulation but needs guardrails.

3. **Memory and Cognitive Evaluation**
   - Implementations of short-term (working memory) and long-term (episodic/semantic memory) architectures are essential for personalized LLM thought processes and mitigating "catastrophic forgetting."
   - Cognitive load limits are being explored, mimicking human constraints to test if limiting context makes LLMs process information more like humans.

## Ideas for OpenClaw / Viking Girlfriend Skill

1. **Dual-Process Architecture (System 1/System 2)**
   - Sigrid currently uses LiteLLM to route between models. We could explicitly implement a "System 1" (fast, intuitive responses for casual chatter via a smaller local model) and a "System 2" (deliberative, deeper reasoning via Gemini/Claude for complex problem-solving or deep metaphysical discussions).

2. **Enhanced Odinsblund (Memory Consolidation)**
   - Incorporate **Schema Theory**: Instead of just summarizing daily logs into vector embeddings, extract and update "Schemas" (core beliefs about the user, relationship status, or current projects). This provides structured, highly compressed memory anchors that persist across sessions.

3. **Dynamic Theory of Mind (ToM) Module**
   - Add a `belief_tracker.py` that runs in the background to infer the user's current emotional/mental state based on recent conversation history. This could feed into the **Wyrd Matrix** to adjust her PAD (Pleasure, Arousal, Dominance) state based on empathy rather than just her internal cycle.

4. **Structured Personality Checks**
   - Build a lightweight test suite to periodically evaluate Sigrid's generated text against the "Big Five" personality traits aligned with her character (e.g., High Openness, High Extraversion, Low Neuroticism). If traits drift, apply corrective prompts or fine-tuning.
