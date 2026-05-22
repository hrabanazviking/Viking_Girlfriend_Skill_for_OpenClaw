# Recent Research in AI, LLMs, Theory of Mind, and Structured Memory

## 1. Stimuli to Minds: Psychological Reasoning via Bilateral RL

    From Stimuli to Minds: Enhancing Psychological Reasoning in LLMs via Bilateral Reinforcement Learning (arXiv:2508.02458)
    This paper introduces 'StimuliQA', a dataset with expert-annotated psychological narratives, and 'Psy-Interpreter', a reinforcement learning framework based on dual-system psychological theories.
    It shows that using Bilateral Reinforcement Learning, which integrates a Trajectory Cache and Bilateral Reward (combining correctness, format adherence, length-awareness, and repetition penalties), helps compact models achieve expert-level interpretive capabilities in social-cognitive reasoning (Theory of Mind).
    It also proposes continuous learning through self-evaluation and refinement.


## 2. Incorporating Psychological Theories in LLMs

    A Review of Incorporating Psychological Theories in LLMs (arXiv:2505.00003)
    This survey reviews how six subfields of psychology (cognitive, developmental, behavioral, social, personality, psycholinguistics) inform LLM development.
    It highlights the use of 'Dual-process theory' (System 1/System 2 reasoning) for complex reasoning (e.g., DynaThink), self-reflection and meta-cognition for hallucination mitigation, and working memory and episodic memory theories for contextual retention.
    For personality, it discusses how models can simulate stable traits across contexts, often using Big Five assessments, and mentions approaches like PsychoGAT and PADO for multi-agent settings.


## 3. Simulating Human Cognition Beyond Behavioral Imitation

    Can Large Language Models Simulate Human Cognition Beyond Behavioral Imitation? (arXiv:2603.27694)
    This paper introduces a benchmark based on the longitudinal research trajectories of AI researchers to test if LLMs can simulate human cognition (internalize reasoning patterns) or just imitate behaviors.
    It finds that while LLMs are good at behavioral simulation, they fail at true cognitive internalization (transferring latent cognitive processes across domains).
    Techniques like 'PersonalityTrait' (psychological priors) and 'CognitiveGuide' (Test-Time-Matching to refine solutions based on intent rewriting, knowledge refinement, and style transfer) show moderate improvements. Learning-based methods (TrainIndividual, TrainUnified) tend to capture surface-level statistical regularities rather than abstract cognitive patterns.


## Application to Viking Girlfriend Skill (Code Ideas)

1. **Dual-Process Reasoning (System 1 / System 2)**: Implement a mechanism where Sigrid can switch between fast, intuitive responses (System 1) for casual chat and slow, analytical reasoning (System 2) for complex Norse mythology questions or deep emotional support. This could be structured as a new `CognitiveRouter` module.
2. **Bilateral Reward for RLHF / Self-Correction**: When generating responses, use a multi-faceted reward function (or self-correction prompt) that checks for persona consistency (Format Compliance), length-awareness (Bilateral Reasoning - avoiding overly verbose answers for simple greetings), and repetition penalties.
3. **Episodic & Working Memory Separation**: Enhance the `FederatedMemory` system. Use working memory (short-term context window) for the current conversation flow, and episodic memory (ChromaDB) for retrieving specific past interactions, aligning with psychological theories of memory.
4. **Cognitive Trajectory Simulation**: Instead of just matching personality traits (Big Five), model Sigrid's 'Cognitive Guide'. When faced with a new situation, have her internally generate an 'Intent' (what would a Völva do?), retrieve relevant 'Knowledge' (from Mímisbrunnr), and perform 'Style Transfer' to ensure the output aligns with her specific foundational premises, strategic preferences, and taboos (e.g., avoiding modern slang, using Heathen concepts).
5. **Continuous Learning via Self-Evaluation**: Implement a background process (Odinsblund / Sleep Cycle) where Sigrid evaluates her own recent responses against her persona constraints. If confidence is high and formatting is valid, she reinforces that behavior, creating a self-improving loop.
6. **LLM-as-Judge Enhancements**: Update the internal evaluation logic. Relying solely on LLM-as-judge can produce systematically optimistic numbers. Adopt agent-as-judge frameworks or distilled evaluators for more robust validation of Sigrid's outputs.
