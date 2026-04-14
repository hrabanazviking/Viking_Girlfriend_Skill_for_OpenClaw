# 2026-04-14 AI Research Insights

This document summarizes recent discoveries and papers related to AI, LLMs, data science, structured data methods, human personality representation via AI, theory of mind, virtual human intelligence simulation, and structured memory concepts.

## Discovered Research Topics

### Graphilosophy Graph-Based Digital Humanities

**Brief:** arXiv:2603.28755v1 [cs.CY] 30 Mar 2026  Graphilosophy: Graph-Based Digital Humanities Computing with The Four Books Minh-Thu Do 1,2 , Quynh-Chau Le-Tran 1,2 , Duc-Duy Nguyen-Mai 1,2 , Thien-Trang Nguyen 1,2 , Khanh-Duy Le 1,2 , Minh-Triet Tran 1,2 , Tam V. Nguyen 3 , Trung-Nghia Le 1,2* 1  2  University of Science, VNU-HCM, Ho Chi Minh City, Vietnam. Vietnam National University - Ho Chi Minh, Ho Chi Minh City, Vietnam. 3 University of Dayton, Dayton, Ohio, United States.  *Corresponding author(s). E-mail(s): ltnghia@fit.hcmus.edu.vn; Contributing authors: 24C02018@student.hcmus.edu.vn; 24C02003@student.hcmus.edu.vn; 24C02006@student.hcmus.edu.vn; 24C02021@student.hcmus.edu.vn; lkduy@fit.hcmus.edu.vn; tmtriet@fit.hcmus.edu.vn; tamnguyen@udayton.edu; Abstract The Four Books have shaped East Asian intellectual traditions, yet their multilayered interpretive complexity limits their accessibility in the digital age. While traditional bilingual commentaries provide a vital pedagogical bridge, computational frameworks are needed to preserve and explore this wisdom. This paper bridges AI and classical philosophy by introducing Graphilosophy, an ontologyguided, multi-layered knowledge graph framework for modeling and interpreting The Four Books. Integrating natural language processing, multilingual semantic embeddings, and humanistic analysis, the framework transforms a bilingual Chinese-Vietnamese corpus into an interpretively grounded resource. Graphilosophy encodes linguistic, conc...

### ElephantBroker A Knowledge-Grounded Cognitive

**Brief:** ElephantBroker: A Knowledge-Grounded Cognitive Runtime for Trustworthy AI Agents Cristian Lupascu, PhD* 1 and Alexandru Lupascu1  arXiv:2603.25097v1 [cs.AI] 26 Mar 2026  1 Elephant Broker, 050141 Bucharest, Romania  Abstract Large Language Model (LLM)-based agents increasingly operate in high-stakes, multiturn settings where factual grounding is critical, yet their memory systems typically rely on flat key–value stores or plain vector retrieval with no mechanism to track the provenance or trustworthiness of stored knowledge. We present ElephantBroker, an open-source cognitive runtime that unifies a Neo4j knowledge graph with a Qdrant vector store through the Cognee SDK to provide durable, verifiable agent memory. The system implements a complete cognitive loop (store, retrieve, score, compose, protect, learn) comprising a hybrid five-source retrieval pipeline, an eleven-dimension competitive scoring engine for budgetconstrained context assembly, a four-state evidence verification model, a five-stage context lifecycle with goal-aware assembly and continuous compaction, a six-layer cheap-first guard pipeline for safety enforcement, an AI firewall providing enforceable tool-call interception and multi-tier safety scanning, a nine-stage consolidation engine that strengthens useful patterns while decaying noise, and a numeric authority model governing multiorganization identity with hierarchical access control. Architectural validation through a comprehensive test suite of over 2,...

### Emotional Cost Functions for AI Safety

**Brief:** Emotional Cost Functions for AI Safety:  arXiv:2603.14531v1 [cs.AI] 15 Mar 2026  Teaching Agents to Feel the Weight of Irreversible Consequences Pandurang Mopgar Independent Researcher  Abstract Humans learn from catastrophic mistakes not through numerical penalties, but through qualitative suffering that reshapes who they are. Current AI safety approaches replicate none of this. Reward shaping captures magnitude, not meaning. Rule-based alignment constrains behaviour, but does not change it. We propose Emotional Cost Functions, a framework in which agents develop Qualitative Suffering States, rich narrative representations of irreversible consequences that persist forward and actively reshape character. Unlike numerical penalties, qualitative suffering states capture the meaning of what was lost, the specific void it creates, and how it changes the agent’s relationship to similar future situations. Our four-component architecture—Consequence Processor, Character State, Anticipatory Scan, and Story Update is grounded in one principle. Actions cannot be undone and agents must live with what they have caused. Anticipatory dread operates through two pathways. Experiential dread arises from the agent’s own lived consequences. Pre-experiential dread is acquired without direct experience, through training or inter-agent transmission. Together they mirror how human wisdom accumulates across experience and culture. Ten experiments across financial trading, crisis support, and content...

### 2410.15665v4

**Brief:** Long Term Memory : The Foundation of AI Self-Evolution  arXiv:2410.15665v4 [cs.AI] 11 May 2025  Xun JIANGµθ Feng LIθ ∗ Han ZHAOθ ∗ θ∗ θ∗ Jun SHAO Shihao XU Shu ZHANGθ ∗ θ∗ α Yize CHEN Mengyue WU Weizhi MAσ  Jiahao QIUι∗ Jiaying WANGθ ∗ θ∗ Weiling CHEN Xavier TANGθ ∗ ι Mengdi WANG Tianqiao CHENµθ  µ  Tianqiao and Chrissy Chen Institute ι Princeton University σ Institute for AI Industry Research, Tsinghua University α Shanghai Jiao Tong University θ Shanda Group  Abstract Large language models (LLMs) like GPTs, built on vast datasets, have demonstrated impressive capabilities in language understanding, reasoning, and planning, achieving performance comparable to humans in various challenging tasks. Most studies have focused on further enhancing these models by training them on everlarger datasets, aiming to develop more powerful foundation models. However, while training stronger foundation models is crucial, we propose how to enable models to evolve while inference is also vital for the development of AI, which refers to AI self-evolution. Compared to using large-scale data to train the models, the self-evolution may only use limited data or interactions. Drawing inspiration from the columnar organization of the human cerebral cortex, we hypothesize that AI models could potentially develop emergent cognitive capabilities and construct internal representational models through iterative interactions with their environment. To achieve this, we propose that models must be equipped...

### 2504.15965v2

**Brief:** arXiv:2504.15965v2 [cs.IR] 23 Apr 2025  From Human Memory to AI Memory: A Survey on Memory Mechanisms in the Era of LLMs  Yaxiong Wu, Sheng Liang, Chen Zhang, Yichao Wang, Yongyue Zhang, Huifeng Guo, Ruiming Tang, Yong Liu Huawei Noah’s Ark Lab wu.yaxiong@huawei.com  Abstract Memory is the process of encoding, storing, and retrieving information, allowing humans to retain experiences, knowledge, skills, and facts over time, and serving as the foundation for growth and effective interaction with the world. It plays a crucial role in shaping our identity, making decisions, learning from past experiences, building relationships, and adapting to changes. In the era of large language models (LLMs), memory refers to the ability of an AI system to retain, recall, and use information from past interactions to improve future responses and interactions. Although previous research and reviews have provided detailed descriptions of memory mechanisms, there is still a lack of a systematic review that summarizes and analyzes the relationship between the memory of LLM-driven AI systems and human memory, as well as how we can be inspired by human memory to construct more powerful memory systems. To achieve this, in this paper, we propose a comprehensive survey on the memory of LLM-driven AI systems. In particular, we first conduct a detailed analysis of the categories of human memory and relate them to the memory of AI systems. Second, we systematically organize existing memory-related work...

### 2408.04910v2

**Brief:** Preprint  Unleashing Artificial Cognition: Integrating Multiple AI Systems Muntasir Adnan Faculty of Science and Technology, University of Canberra Email: adnan.adnan@canberra.edu.au  Buddhi Gamage Faculty of Science and Technology, University of Canberra Email: buddhi.gamage@canberra.edu.au  Zhiwei Xu  arXiv:2408.04910v2 [cs.AI] 12 Aug 2024  Faculty of Science and Technology, University of Canberra Email: danny.xu@canberra.edu.au  Damith Herath Faculty of Science and Technology, University of Canberra Email: damith.herath@canberra.edu.au  Carlos C. N. Kuhn Faculty of Science and Technology, University of Canberra Email: carlos.noschangkuhn@canberra.edu.au  Abstract In this study, we present an innovative fusion of language models and query analysis techniques to unlock cognition in artificial intelligence. Our system seamlessly integrates a Chess engine with a language model, enabling it to predict moves and provide strategic explanations. Leveraging a vector database through retrievable answer generation, our OpenSIAI system elucidates its decision-making process, bridging the gap between raw computation and human-like understanding. Our choice of Chess as the demonstration environment underscores the versatility of our approach. Beyond Chess, our system holds promise for diverse applications, from medical diagnostics to financial forecasting. Keywords AI cognition, Chess, large language models, query analysis, retrievable answer generation  1 Introduction Artificial Intell...

### Significant Other AI Identity Memory and Emotional

**Brief:** Significant Other AI: Identity, Memory, and Emotional Regulation as Long-Term Relational Intelligence Sung Park School of Data Science and Artificial Intelligence Taejae University, Seoul, Republic of Korea sjp@taejae.ac.kr Abstract Significant Others (SOs) stabilize identity, regulate emotion, and support narrative meaningmaking, yet many people today lack access to such relational anchors. Recent advances in large language models and memory-augmented AI raise the question of whether artificial systems could support some of these functions. Existing empathic AIs, however, remain reactive and short-term, lacking autobiographical memory, identity modeling, predictive emotional regulation, and narrative coherence. This manuscript introduces Significant Other Artificial Intelligence (SO-AI) as a new domain of relational AI. It synthesizes psychological and sociological theory to define SO functions and derives requirements for SO-AI, including identity awareness, long-term memory, proactive support, narrative co-construction, and ethical boundary enforcement. A conceptual architecture is proposed, comprising an anthropomorphic interface, a relational cognition layer, and a governance layer. A research agenda outlines methods for evaluating identity stability, longitudinal interaction patterns, narrative development, and sociocultural impact. SO-AI reframes AI-human relationships as long-term, identity-bearing partnerships and provides a foundational blueprint for investigating w...

### LifeBench A Benchmark for Long-Horizon Multi-Source Memory

**Brief:** LifeBench: A Benchmark for Long-Horizon Multi-Source Memory Zihao Cheng1,2 , Weixin Wang1,2 , Yu Zhao3 , Ziyang Ren3 , Jiaxuan Chen1,2 , Ruiyang Xu3 , Shuai Huang3 , Yang Chen3 , Guowei Li3 , Mengshi Wang3 , Yi Xie3 , Ren Zhu3 , Zeren Jiang3 , Keda Lu3 , Yihong Li3 , Xiaoliang Wang1 , Liwei Liu3 , Cam-Tu Nguyen1,2 1 State Key Laboratory for Novel Software Technology, Nanjing University 2 School of Artificial Intelligence, Nanjing University 3 Huawei Technologies Co., Ltd.  arXiv:2603.03781v1 [cs.AI] 4 Mar 2026  Nanjing, Jiangsu, China zihao_cheng@smail.nju.edu.cn  Abstract Long-term memory is fundamental for personalized agents capable of accumulating knowledge, reasoning over user experiences, and adapting across time. However, existing memory benchmarks primarily target declarative memory, specifically semantic and episodic types, where all information is explicitly presented in dialogues. In contrast, real-world actions are also governed by nondeclarative memory, including habitual and procedural types, and need to be inferred from diverse digital traces. To bridge this gap, we introduce LifeBench, which features densely connected, long-horizon event simulation. It pushes AI agents beyond simple recall, requiring the integration of declarative and non-declarative memory reasoning across diverse and temporally extended contexts. Building such a benchmark presents two key challenges: ensuring data quality and scalability. We maintain data quality by employing real-world prio...

### Memory Bear AI

**Brief:** arXiv:2603.22306v1 [cs.AI] 18 Mar 2026  Abstract Affective judgment in real interaction is rarely a purely local prediction problem. Emotional meaning often depends on prior trajectory, contextual accumulation, and multimodal evidence that may be weak, noisy, or incomplete at the current moment. Although recent progress in multimodal emotion recognition (MER) has improved the integration of textual, acoustic, and visual signals, many existing systems still remain optimized for short-range inference and provide limited support for persistent affective memory, long-horizon dependency modeling, and contextaware robustness under imperfect input. This technical report presents the Memory Bear AI Memory Science Engine, a memory-centered framework for multimodal affective intelligence. Instead of treating emotion as a transient output label, the proposed framework models affective information as a structured and evolving variable within a memory system. The architecture organizes multimodal affective processing through structured memory formation, working-memory aggregation, long-term consolidation, memory-driven retrieval, dynamic fusion calibration, and continuous memory updating. At its core, the framework transforms multimodal signals into structured Emotion Memory Units (EMUs), allowing affective information to be preserved, reactivated, and revised across interaction horizons. Experimental results show that the proposed framework consistently outperforms comparison systems ac...

### s44387-025-00027-5

**Brief:** ...

### Dual-branch Graph Domain Adaptation for Cross-scenario

**Brief:** Dual-branch Graph Domain Adaptation for Cross-scenario Multi-modal Emotion Recognition Yuntao Shou  shouyuntao@stu.xjtu.edu.cn  College of Computer and Mathematics Central South University of Forestry and Technology  arXiv:2603.26840v1 [eess.AS] 27 Mar 2026  Jun Zhou  zhoujun@csuft.edu.cn  College of Computer and Mathematics Central South University of Forestry and Technology  Tao Meng  mengtao@hnu.edu.cn  College of Computer and Mathematics Central South University of Forestry and Technology  Wei Ai  aiwei@hnu.edu.cn  College of Computer and Mathematics Central South University of Forestry and Technology  Keqin Li  lik@newpaltz.edu  Department of Computer Science State University of New York  Abstract  Multimodal Emotion Recognition in Conversations (MERC) aims to predict speakers’ emotional states in multi-turn dialogues through text, audio, and visual cues. In real-world settings, conversation scenarios differ significantly in speakers, topics, styles, and noise levels. Existing MERC methods generally neglect these cross-scenario variations, limiting their ability to transfer models trained on a source domain to unseen target domains. To address this issue, we propose a Dual-branch Graph Domain Adaptation framework (DGDA) for multimodal emotion recognition under cross-scenario conditions. We first construct an emotion interaction graph to characterize complex emotional dependencies among utterances. A dual-branch encoder, consisting of a hypergraph neural network (HGNN) an...

### 2512.23343v1

**Brief:** ...

### nihms-11100990

**Brief:** TYPE Original Research PUBLISHED 03 May 2024 DOI 10.3389/fpsyg.2024.1387948  OPEN ACCESS EDITED BY  Knut Neumann, IPN–Leibniz-Institute for Science and Mathematics Education, Germany REVIEWED BY  Katherine Elkins, Kenyon College, United States David Gamez, Middlesex University, United Kingdom  Applying Generative Artiﬁcial Intelligence to cognitive models of decision making Tyler Malloy* and Cleotilde Gonzalez Dynamic Decision Making Laboratory, Department of Social and Decision Sciences, Dietrich College, Carnegie Mellon University, Pittsburgh, PA, United States  *CORRESPONDENCE  Tyler Malloy tylerjmalloy@cmu.edu RECEIVED 19 February 2024 ACCEPTED 12 April 2024 PUBLISHED 03 May 2024 CITATION  Malloy T and Gonzalez C (2024) Applying Generative Artiﬁcial Intelligence to cognitive models of decision making. Front. Psychol. 15:1387948. doi: 10.3389/fpsyg.2024.1387948 COPYRIGHT  © 2024 Malloy and Gonzalez. This is an open-access article distributed under the terms of the Creative Commons Attribution License (CC BY). The use, distribution or reproduction in other forums is permitted, provided the original author(s) and the copyright owner(s) are credited and that the original publication in this journal is cited, in accordance with accepted academic practice. No use, distribution or reproduction is permitted which does not comply with these terms.  Introduction: Generative Artiﬁcial Intelligence has made signiﬁcant impacts in many ﬁelds, including computational cognitive modeling...

### GEPA Reflective Prompt Evolution 2507.19457v2

**Brief:** Accepted at ICLR 2026 (Oral).  GEPA: R EFLECTIVE P ROMPT E VOLUTION C AN O UTPER FORM R EINFORCEMENT L EARNING Lakshya A Agrawal1 , Shangyin Tan1 , Dilara Soylu2 , Noah Ziems4 , Rishi Khare1 , Krista Opsahl-Ong5 , Arnav Singhvi2,5 , Herumb Shandilya2 , Michael J Ryan2 , Meng Jiang4 , Christopher Potts2 , Koushik Sen1 , Alexandros G. Dimakis1,3 , Ion Stoica1 , Dan Klein1 , Matei Zaharia1,5 , Omar Khattab6 UC Berkeley  2  Stanford  3  4  BespokeLabs.ai  Notre Dame  5  Databricks  6  MIT  A BSTRACT Large language models (LLMs) are increasingly adapted to downstream tasks via reinforcement learning (RL) methods like Group Relative Policy Optimization (GRPO), which often require thousands of rollouts to learn new tasks. We argue that the interpretable nature of language often provides a much richer learning medium for LLMs, compared to policy gradients derived from sparse, scalar rewards. To test this, we introduce GEPA (Genetic-Pareto), a prompt optimizer that thoroughly incorporates natural language reflection to learn high-level rules from trial and error. Given any AI system containing one or more LLM prompts, GEPA samples trajectories (e.g., reasoning, tool calls, and tool outputs) and reflects on them in natural language to diagnose problems, propose and test prompt updates, and combine complementary lessons from the Pareto frontier of its own attempts. As a result of GEPA’s design, it can often turn even just a few rollouts into a large quality gain. Across six tasks, GEPA...

### EchoGuard An Agentic Framework with Knowledge-Graph Memory

**Brief:** EchoGuard: An Agentic Framework with Knowledge-Graph Memory for Detecting Manipulative Communication in Longitudinal Dialogue Ratna Kandala1 University of Kansas ratnanirupama@gmail.com Akshata Kishore Moharir3 University of Maryland akshatankishore5@gmail.com  Abstract Manipulative communication, such as gaslighting, guilt-tripping, and emotional coercion, is often difficult for individuals to recognize. Existing agentic AI systems lack the structured, longitudinal memory to track these subtle, context-dependent tactics, often failing due to limited context windows and catastrophic forgetting. We introduce EchoGuard, an agentic AI framework that addresses this gap by using a Knowledge Graph (KG) as the agent’s core episodic and semantic memory. EchoGuard employs a structured Log-Analyze-Reflect loop: (1) users log interactions, which the agent structures as nodes and edges in a personal, episodic KG (capturing events, emotions, and speakers); (2) the system executes complex graph queries to detect six psychologically-grounded manipulation patterns (stored as a semantic KG); and (3) an LLM generates targeted Socratic prompts grounded by the subgraph of detected patterns, guiding users toward self-discovery. This framework demonstrates how the interplay between agentic architectures and Knowledge Graphs can empower individuals in recognizing manipulative communication while maintaining personal autonomy and safety. We present the theoretical foundation, framework design, a com...

## Potential Code Implementations and Ideas

Based on the research topics gathered (including long-horizon memory, knowledge-graph memory structures, theory of mind simulations, and emotional cost functions), the following code ideas could improve the Sigrid OpenClaw skill:

### 1. Graph-Based / Structured Memory Implementation
Expanding the current `FederatedMemory` with an explicit knowledge graph mechanism for relational memory, inspired by "EchoGuard" or "ElephantBroker".

```python
class GraphMemoryStore:
    def __init__(self):
        self.nodes = {}
        self.edges = []

    def add_entity(self, entity_id, properties):
        self.nodes[entity_id] = properties

    def add_relation(self, source_id, target_id, relation_type):
        self.edges.append({"source": source_id, "target": target_id, "type": relation_type})

    def query_relations(self, entity_id):
        return [e for e in self.edges if e["source"] == entity_id or e["target"] == entity_id]
```

### 2. Emotional Cost Functions for AI Safety
Integrating "Emotional Cost Functions" into the existing `vordur` (Warden) or PAD Model, calculating the psychological or safety "cost" of responses.

```python
def calculate_emotional_safety_cost(pad_state, input_text):
    # Base cost from current PAD
    valence, arousal, dominance = pad_state

    # Simple mock cost function: high arousal and low valence increase cost/risk
    cost = (1.0 - valence) * arousal * 10

    # If cost exceeds a threshold, fallback to Heimdallr protocol
    if cost > 8.0:
        return True, cost # Trigger circuit breaker
    return False, cost
```

### 3. Theory of Mind Context Tracker
To improve Sigrid's "Theory of Mind" (modeling the user's belief states), tracking specific user assumptions independently from general episodic memory.

```python
class TheoryOfMindTracker:
    def __init__(self):
        self.user_beliefs = {} # Maps topic to what the AI believes the user thinks
        self.user_emotional_state_estimate = (0.5, 0.5, 0.5) # User's estimated PAD

    def update_belief(self, topic, user_statement, confidence):
        self.user_beliefs[topic] = {
            "statement": user_statement,
            "confidence": confidence,
            "last_updated": time.time()
        }
```
