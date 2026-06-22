# AI & LLM Research Report - 2026-04-26

This report compiles recent research on AI, LLMs, data science, structured data methods, ways of representing human personality via AI, theory of mind, virtual human intelligence simulation, and structured memory concepts.

## Search Query: LLM AND "structured data" AND "data science"
### BIASINSPECTOR: Detecting Bias in Structured Data through LLM Agents
**Link:** http://arxiv.org/abs/2504.04855v1

Detecting biases in structured data is a complex and time-consuming task. Existing automated techniques are limited in diversity of data types and heavily reliant on human case-by-case handling, resulting in a lack of generalizability. Currently, large language model (LLM)-based agents have made significant progress in data science, but their ability to detect data biases is still insufficiently explored. To address this gap, we introduce the first end-to-end, multi-agent synergy framework, BIASINSPECTOR, designed for automatic bias detection in structured data based on specific user requirements. It first develops a multi-stage plan to analyze user-specified bias detection tasks and then implements it with a diverse and well-suited set of tools. It delivers detailed results that include explanations and visualizations. To address the lack of a standardized framework for evaluating the capability of LLM agents to detect biases in data, we further propose a comprehensive benchmark that includes multiple evaluation metrics and a large set of test cases. Extensive experiments demonstrate that our framework achieves exceptional overall performance in structured data bias detection, setting a new milestone for fairer data applications.

### Data Science Students Perspectives on Learning Analytics: An Application of Human-Led and LLM Content Analysis
**Link:** http://arxiv.org/abs/2502.10409v1

Objective This study is part of a series of initiatives at a UK university designed to cultivate a deep understanding of students' perspectives on analytics that resonate with their unique learning needs. It explores collaborative data processing undertaken by postgraduate students who examined an Open University Learning Analytics Dataset (OULAD).
  Methods A qualitative approach was adopted, integrating a Retrieval-Augmented Generation (RAG) and a Large Language Model (LLM) technique with human-led content analysis to gather information about students' perspectives based on their submitted work. The study involved 72 postgraduate students in 12 groups.
  Findings The analysis of group work revealed diverse insights into essential learning analytics from the students' perspectives. All groups adopted a structured data science methodology. The questions formulated by the groups were categorised into seven themes, reflecting their specific areas of interest. While there was variation in the selected variables to interpret correlations, a consensus was found regarding the general results.
  Conclusion A significant outcome of this study is that students specialising in data science exhibited a deeper understanding of learning analytics, effectively articulating their interests through inferences drawn from their analyses. While human-led content analysis provided a general understanding of students' perspectives, the LLM offered nuanced insights.

### DSAEval: Evaluating Data Science Agents on a Wide Range of Real-World Data Science Problems
**Link:** http://arxiv.org/abs/2601.13591v1

Recent LLM-based data agents aim to automate data science tasks ranging from data analysis to deep learning. However, the open-ended nature of real-world data science problems, which often span multiple taxonomies and lack standard answers, poses a significant challenge for evaluation. To address this, we introduce DSAEval, a benchmark comprising 641 real-world data science problems grounded in 285 diverse datasets, covering both structured and unstructured data (e.g., vision and text). DSAEval incorporates three distinctive features: (1) Multimodal Environment Perception, which enables agents to interpret observations from multiple modalities including text and vision; (2) Multi-Query Interactions, which mirror the iterative and cumulative nature of real-world data science projects; and (3) Multi-Dimensional Evaluation, which provides a holistic assessment across reasoning, code, and results. We systematically evaluate 11 advanced agentic LLMs using DSAEval. Our results show that Claude-Sonnet-4.5 achieves the strongest overall performance, GPT-5.2 is the most efficient, and MiMo-V2-Flash is the most cost-effective. We further demonstrate that multimodal perception consistently improves performance on vision-related tasks, with gains ranging from 2.04% to 11.30%. Overall, while current data science agents perform well on structured data and routine data anlysis workflows, substantial challenges remain in unstructured domains. Finally, we offer critical insights and outline future research directions to advance the development of data science agents.


## Search Query: LLM AND "theory of mind"
### A Survey of Theory of Mind in Large Language Models: Evaluations, Representations, and Safety Risks
**Link:** http://arxiv.org/abs/2502.06470v1

Theory of Mind (ToM), the ability to attribute mental states to others and predict their behaviour, is fundamental to social intelligence. In this paper, we survey studies evaluating behavioural and representational ToM in Large Language Models (LLMs), identify important safety risks from advanced LLM ToM capabilities, and suggest several research directions for effective evaluation and mitigation of these risks.

### LLM Theory of Mind and Alignment: Opportunities and Risks
**Link:** http://arxiv.org/abs/2405.08154v1

Large language models (LLMs) are transforming human-computer interaction and conceptions of artificial intelligence (AI) with their impressive capacities for conversing and reasoning in natural language. There is growing interest in whether LLMs have theory of mind (ToM); the ability to reason about the mental and emotional states of others that is core to human social intelligence. As LLMs are integrated into the fabric of our personal, professional and social lives and given greater agency to make decisions with real-world consequences, there is a critical need to understand how they can be aligned with human values. ToM seems to be a promising direction of inquiry in this regard. Following the literature on the role and impacts of human ToM, this paper identifies key areas in which LLM ToM will show up in human:LLM interactions at individual and group levels, and what opportunities and risks for alignment are raised in each. On the individual level, the paper considers how LLM ToM might manifest in goal specification, conversational adaptation, empathy and anthropomorphism. On the group level, it considers how LLM ToM might facilitate collective alignment, cooperation or competition, and moral judgement-making. The paper lays out a broad spectrum of potential implications and suggests the most pressing areas for future research.

### ToMAP: Training Opponent-Aware LLM Persuaders with Theory of Mind
**Link:** http://arxiv.org/abs/2505.22961v2

Large language models (LLMs) have shown promising potential in persuasion, but existing works on training LLM persuaders are still preliminary. Notably, while humans are skilled in modeling their opponent's thoughts and opinions proactively and dynamically, current LLMs struggle with such Theory of Mind (ToM) reasoning, resulting in limited diversity and opponent awareness. To address this limitation, we introduce Theory of Mind Augmented Persuader (ToMAP), a novel approach for building more flexible persuader agents by incorporating two theory of mind modules that enhance the persuader's awareness and analysis of the opponent's mental state. Specifically, we begin by prompting the persuader to consider possible objections to the target central claim, and then use a text encoder paired with a trained MLP classifier to predict the opponent's current stance on these counterclaims. Our carefully designed reinforcement learning schema enables the persuader learns how to analyze opponent-related information and utilize it to generate more effective arguments. Experiments show that the ToMAP persuader, while containing only 3B parameters, outperforms much larger baselines, like GPT-4o, with a relative gain of 39.4% across multiple persuadee models and diverse corpora. Notably, ToMAP exhibits complex reasoning chains and reduced repetition during training, which leads to more diverse and effective arguments. The opponent-aware feature of ToMAP also makes it suitable for long conversations and enables it to employ more logical and opponent-aware strategies. These results underscore our method's effectiveness and highlight its potential for developing more persuasive language agents. Code is available at: https://github.com/ulab-uiuc/ToMAP.


## Search Query: LLM AND personality AND simulation
### Exploring Big Five Personality and AI Capability Effects in LLM-Simulated Negotiation Dialogues
**Link:** http://arxiv.org/abs/2506.15928v3

This paper presents an evaluation framework for agentic AI systems in mission-critical negotiation contexts, addressing the need for AI agents that can adapt to diverse human operators and stakeholders. Using Sotopia as a simulation testbed, we present two experiments that systematically evaluated how personality traits and AI agent characteristics influence LLM-simulated social negotiation outcomes--a capability essential for a variety of applications involving cross-team coordination and civil-military interactions. Experiment 1 employs causal discovery methods to measure how personality traits impact price bargaining negotiations, through which we found that Agreeableness and Extraversion significantly affect believability, goal achievement, and knowledge acquisition outcomes. Sociocognitive lexical measures extracted from team communications detected fine-grained differences in agents' empathic communication, moral foundations, and opinion patterns, providing actionable insights for agentic AI systems that must operate reliably in high-stakes operational scenarios. Experiment 2 evaluates human-AI job negotiations by manipulating both simulated human personality and AI system characteristics, specifically transparency, competence, adaptability, demonstrating how AI agent trustworthiness impact mission effectiveness. These findings establish a repeatable evaluation methodology for experimenting with AI agent reliability across diverse operator personalities and human-agent team dynamics, directly supporting operational requirements for reliable AI systems. Our work advances the evaluation of agentic AI workflows by moving beyond standard performance metrics to incorporate social dynamics essential for mission success in complex operations.

### Evaluating the Simulation of Human Personality-Driven Susceptibility to Misinformation with LLMs
**Link:** http://arxiv.org/abs/2506.23610v1

Large language models (LLMs) make it possible to generate synthetic behavioural data at scale, offering an ethical and low-cost alternative to human experiments. Whether such data can faithfully capture psychological differences driven by personality traits, however, remains an open question. We evaluate the capacity of LLM agents, conditioned on Big-Five profiles, to reproduce personality-based variation in susceptibility to misinformation, focusing on news discernment, the ability to judge true headlines as true and false headlines as false. Leveraging published datasets in which human participants with known personality profiles rated headline accuracy, we create matching LLM agents and compare their responses to the original human patterns. Certain trait-misinformation associations, notably those involving Agreeableness and Conscientiousness, are reliably replicated, whereas others diverge, revealing systematic biases in how LLMs internalize and express personality. The results underscore both the promise and the limits of personality-aligned LLMs for behavioral simulation, and offer new insight into modeling cognitive diversity in artificial agents.

### LLMs Simulate Big Five Personality Traits: Further Evidence
**Link:** http://arxiv.org/abs/2402.01765v1

An empirical investigation into the simulation of the Big Five personality traits by large language models (LLMs), namely Llama2, GPT4, and Mixtral, is presented. We analyze the personality traits simulated by these models and their stability. This contributes to the broader understanding of the capabilities of LLMs to simulate personality traits and the respective implications for personalized human-computer interaction.


## Search Query: LLM AND memory AND structure
### Efficient In-Memory Acceleration of Sparse Block Diagonal LLMs
**Link:** http://arxiv.org/abs/2510.11192v1

Structured sparsity enables deploying large language models (LLMs) on resource-constrained systems. Approaches like dense-to-sparse fine-tuning are particularly compelling, achieving remarkable structured sparsity by reducing the model size by over 6.7x, while still maintaining acceptable accuracy. Despite this reduction, LLM inference, especially the decode stage being inherently memory-bound, is extremely expensive on conventional Von-Neumann architectures. Compute-in-memory (CIM) architectures mitigate this by performing computations directly in memory, and when paired with sparse LLMs, enable storing and computing the entire model in memory, eliminating the data movement on the off-chip bus and improving efficiency. Nonetheless, naively mapping sparse matrices onto CIM arrays leads to poor array utilization and diminished computational efficiency. In this paper, we present an automated framework with novel mapping and scheduling strategies to accelerate sparse LLM inference on CIM accelerators. By exploiting block-diagonal sparsity, our approach improves CIM array utilization by over 50%, achieving more than 4x reduction in both memory footprint and the number of required floating-point operations.

### OptPipe: Memory- and Scheduling-Optimized Pipeline Parallelism for LLM Training
**Link:** http://arxiv.org/abs/2510.05186v1

Pipeline parallelism (PP) has become a standard technique for scaling large language model (LLM) training across multiple devices. However, despite recent progress in reducing memory consumption through activation offloading, existing approaches remain largely heuristic and coarse-grained, often overlooking the fine-grained trade-offs between memory, computation, and scheduling latency. In this work, we revisit the pipeline scheduling problem from a principled optimization perspective. We observe that prevailing strategies either rely on static rules or aggressively offload activations without fully leveraging the interaction between memory constraints and scheduling efficiency. To address this, we formulate scheduling as a constrained optimization problem that jointly accounts for memory capacity, activation reuse, and pipeline bubble minimization. Solving this model yields fine-grained schedules that reduce pipeline bubbles while adhering to strict memory budgets. Our approach complements existing offloading techniques: whereas prior approaches trade memory for time in a fixed pattern, we dynamically optimize the tradeoff with respect to model structure and hardware configuration. Experimental results demonstrate that our method consistently improves both throughput and memory utilization. In particular, we reduce idle pipeline time by up to 50% under the same per-device memory limit, and in some cases, enable the training of larger models within limited memory budgets.

### Externalization in LLM Agents: A Unified Review of Memory, Skills, Protocols and Harness Engineering
**Link:** http://arxiv.org/abs/2604.08224v1

Large language model (LLM) agents are increasingly built less by changing model weights than by reorganizing the runtime around them. Capabilities that earlier systems expected the model to recover internally are now externalized into memory stores, reusable skills, interaction protocols, and the surrounding harness that makes these modules reliable in practice. This paper reviews that shift through the lens of externalization. Drawing on the idea of cognitive artifacts, we argue that agent infrastructure matters not merely because it adds auxiliary components, but because it transforms hard cognitive burdens into forms that the model can solve more reliably. Under this view, memory externalizes state across time, skills externalize procedural expertise, protocols externalize interaction structure, and harness engineering serves as the unification layer that coordinates them into governed execution. We trace a historical progression from weights to context to harness, analyze memory, skills, and protocols as three distinct but coupled forms of externalization, and examine how they interact inside a larger agent system. We further discuss the trade-off between parametric and externalized capability, identify emerging directions such as self-evolving harnesses and shared agent infrastructure, and discuss open challenges in evaluation, governance, and the long-term co-evolution of models and external infrastructure. The result is a systems-level framework for explaining why practical agent progress increasingly depends not only on stronger models, but on better external cognitive infrastructure.


## Discoveries and Code Ideas to Improve the Project

1.  **Theory of Mind (ToM) Implementation for Agent Alignment & Empathy:**
    *   **Discovery:** Recent papers show that LLMs can simulate ToM, enabling them to predict human mental states, objections, and adapt conversational strategies dynamically (e.g., ToMAP framework). They also note that ToM patterns activate specific sub-networks in the model.
    *   **Project Application:** We can enhance Sigrid's 'Drengskapr Validation' and 'Wyrd Matrix' by explicitly prompting or fine-tuning her to maintain an internal model of the user's emotional and mental state.
    *   **Code Idea:** Create a `TheoryOfMind` class within the `WyrdMatrix` that explicitly models the user's inferred state based on conversation history.
        ```python
        class UserMentalState:
            def __init__(self):
                self.inferred_mood = "neutral"
                self.inferred_belief = {} # What the user believes about a topic
                self.receptivity_to_advice = 0.5 # Scale 0-1
        ```

2.  **Personality Simulation and Evaluation:**
    *   **Discovery:** LLMs are increasingly evaluated on their ability to stably simulate Big Five personality traits, with findings showing this impacts negotiation, susceptibility to misinformation, and believability.
    *   **Project Application:** Ensure Sigrid's 'Heathen Third Path' persona is anchored in a consistent Big Five or similar personality profile matrix to ensure her reactions remain stable over long interactions.
    *   **Code Idea:** Define a static personality vector and calculate deviations during her Chrono-Biological cycles.

3.  **Hierarchical and Externalized Memory (From earlier web search and arXiv):**
    *   **Discovery:** As context windows grow, the shift is towards *hierarchical memory* and *externalized memory* (skills, protocols). LLMs that can recall sprint retrospectives or long-term interactions reduce institutional knowledge loss.
    *   **Project Application:** The `Odinsblund (The Sleep Cycle)` is already a great start. This can be enhanced by creating a multi-tiered memory system (Short-term context -> Episodic Memory (daily logs) -> Semantic Memory (core knowledge)).
    *   **Code Idea:** In the memory consolidation step, classify information before storing it in vector DB.
        ```python
        def consolidate_memory(daily_logs):
            for log in daily_logs:
                if is_factual_knowledge(log):
                    store_semantic_memory(log)
                elif is_personal_event(log):
                    store_episodic_memory(log)
        ```

4.  **Agentic AI and Autonomous Workflows:**
    *   **Discovery:** Agentic AI is moving from chatbots to systems that understand goals, interact with tools/APIs, and adapt.
    *   **Project Application:** Enhance the "Autonomous Project Generator" by giving Sigrid access to explicit tools (like bash execution, file reading) so she can genuinely learn new coding libraries by executing and testing code herself, not just reading about it.
    *   **Code Idea:** Implement a tool-use loop where Sigrid can propose an action (e.g., `run_tests`), execute it, and interpret the results to update her internal state.
