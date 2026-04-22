# AI Research Discoveries - 2026-04-13

This document compiles the latest research insights on AI, LLMs, structured memory, virtual human intelligence simulation, and theory of mind extracted from recent papers. It also includes code ideas for integrating these concepts into the Viking Companion Skill project.

## Research Summaries

### 2410.15665v4.pdf

**Excerpt:**
> Long Term Memory : The Foundation of AI Self-Evolution Xun JIANGµθ Feng LIθ ∗ Han ZHAOθ ∗ Jiahao QIUι∗ Jiaying W ANGθ ∗ Jun SHAOθ ∗ Shihao XUθ ∗ Shu ZHANGθ ∗ Weiling CHENθ ∗ Xavier TANGθ ∗ Yize CHENθ ∗ Mengyue WUα Weizhi MAσ Mengdi W ANGι Tianqiao CHENµθ µ Tianqiao and Chrissy Chen Institute ι Princeton University σ Institute for AI Industry Research, Tsinghua University α Shanghai Jiao Tong University θ Shanda Group Abstract Large language models (LLMs) like GPTs, built on vast datasets, have demon- strated impressive capabilities in language understanding, reasoning, and planning, achieving performance comparable to humans in various challenging tasks. Most studies have focused on further enhancing these models by training them on ever- larger datasets, aiming to develop more powerful foundation models. However, while training stronger foundation models is crucial, we propose how to enable models to evolve while inference is also vital for the development of AI, which refers to AI self-evolution. Compared to using large-scale data to train the models, the self-evolution may only use limited data or interactions. Drawing inspiration from the columnar organization of the human cerebral cortex, we hypothesize that AI models could potentially develop emergent cognitive capabilities and construct internal representational models through iterative interactions with their environ- ment. To achieve this, we propose that models must be equipped with Long-Term Memory (LTM), which sto

---

### Emotional_Cost_Functions_for_AI_Safety.pdf

**Excerpt:**
> Emotional Cost Functions for AI Safety: Teaching Agents to Feel the Weight of Irreversible Consequences Pandurang Mopgar Independent Researcher Abstract Humans learn from catastrophic mistakes not through numerical penalties, but through qualitative suffering that reshapes who they are. Current AI safety ap- proaches replicate none of this. Reward shaping captures magnitude, not meaning. Rule-based alignment constrains behaviour, but does not change it. We proposeEmotional Cost Functions, a framework in which agents de- velopQualitative Suffering States, rich narrative representations of irreversible consequences that persist forward and actively reshape character. Unlike numeri- cal penalties, qualitative suffering states capture themeaningof what was lost, the specific void it creates, and how it changes the agent’s relationship to similar future situations. Our four-component architecture—Consequence Processor, Character State, Anticipatory Scan, and Story Update is grounded in one principle. Actions cannot be undone and agents must live with what they have caused. Anticipatory dread operates through two pathways. Experiential dread arises from the agent’s own lived consequences. Pre-experiential dread is acquired without direct expe- rience, through training or inter-agent transmission. Together they mirror how human wisdom accumulates across experience and culture. Ten experiments across financial trading, crisis support, and content modera- tion show that qualitative su

---

### 2408.04910v2.pdf

**Excerpt:**
> Preprint Unleashing Artificial Cognition: Integrating Multiple AI Systems Muntasir Adnan Faculty of Science and Technology, University of Canberra Email: adnan.adnan@canberra.edu.au Buddhi Gamage Faculty of Science and Technology, University of Canberra Email: buddhi.gamage@canberra.edu.au Zhiwei Xu Faculty of Science and Technology, University of Canberra Email: danny.xu@canberra.edu.au Damith Herath Faculty of Science and Technology, University of Canberra Email: damith.herath@canberra.edu.au Carlos C. N. Kuhn Faculty of Science and Technology, University of Canberra Email: carlos.noschangkuhn@canberra.edu.au Abstract In this study, we present an innovative fusion of language models and query analysis techniques to unlock cognition in artificial intelligence. Our system seamlessly integrates a Chess engine with a language model, enabling it to predict moves and provide strategic explanations. Leveraging a vector database through retrievable answer generation, our OpenSIAI system elucidates its decision-making process, bridging the gap between raw computation and human-like understanding. Our choice of Chess as the demonstration environment underscores the versatility of our approach. Beyond Chess, our system holds promise for diverse applications, from medical diagnostics to financial forecasting. Keywords AI cognition, Chess, large language models, query analysis, retrievable answer generation 1 Introduction Artificial Intelligence (AI) systems have achieved remarkable fea

---

### nihms-11100990.pdf

**Excerpt:**
> TYPE Original Research PUBLISHED /zero.tnum/three.tnum May /two.tnum/zero.tnum/two.tnum/four.tnum DOI /one.tnum/zero.tnum./three.tnum/three.tnum/eight.tnum/nine.tnum/fpsyg./two.tnum/zero.tnum/two.tnum/four.tnum./one.tnum/three.tnum/eight.tnum/seven.tnum/nine.tnum/four.tnum/eight.tnum OPEN ACCESS EDITED BY Knut Neumann, IPN–Leibniz-Institute for Science and Mathematics Education, Germany REVIEWED BY Katherine Elkins, Kenyon College, United States David Gamez, Middlesex University, United Kingdom *CORRESPONDENCE Tyler Malloy tylerjmalloy@cmu.edu RECEIVED /one.tnum/nine.tnum February /two.tnum/zero.tnum/two.tnum/four.tnum ACCEPTED /one.tnum/two.tnum April /two.tnum/zero.tnum/two.tnum/four.tnum PUBLISHED /zero.tnum/three.tnum May /two.tnum/zero.tnum/two.tnum/four.tnum CITATION Malloy T and Gonzalez C (/two.tnum/zero.tnum/two.tnum/four.tnum) Applying Generative Artiﬁcial Intelligence to cognitive models of decision making. Front. Psychol. /one.tnum/five.tnum:/one.tnum/three.tnum/eight.tnum/seven.tnum/nine.tnum/four.tnum/eight.tnum. doi: /one.tnum/zero.tnum./three.tnum/three.tnum/eight.tnum/nine.tnum/fpsyg./two.tnum/zero.tnum/two.tnum/four.tnum./one.tnum/three.tnum/eight.tnum/seven.tnum/nine.tnum/four.tnum/eight.tnum COPYRIGHT © /two.tnum/zero.tnum/two.tnum/four.tnum Malloy and Gonzalez. This is an open-access article distributed under the terms of the Creative Commons Attribution License (CC BY) . The use, distribution or reproduction in other forums is permitted, provided the ori

---

### ElephantBroker_A_Knowledge-Grounded_Cognitive.pdf

**Excerpt:**
> ElephantBroker: A Knowledge-Grounded Cognitive Runtime for Trustworthy AI Agents Cristian Lupascu, PhD*1 and Alexandru Lupascu1 1Elephant Broker, 050141 Bucharest, Romania Abstract Large Language Model (LLM)-based agents increasingly operate in high-stakes, multi- turn settings where factual grounding is critical, yet their memory systems typically rely on flat key–value stores or plain vector retrieval with no mechanism to track the provenance or trustworthiness of stored knowledge. We present ElephantBroker, an open-source cog- nitive runtime that unifies a Neo4j knowledge graph with a Qdrant vector store through the Cognee SDK to provide durable, verifiable agent memory. The system implements a complete cognitive loop (store, retrieve, score, compose, protect, learn) comprising a hybrid five-source retrieval pipeline, an eleven-dimension competitive scoring engine for budget- constrained context assembly, a four-state evidence verification model, a five-stage con- text lifecycle with goal-aware assembly and continuous compaction, a six-layer cheap-first guard pipeline for safety enforcement, an AI firewall providing enforceable tool-call inter- ception and multi-tier safety scanning, a nine-stage consolidation engine that strengthens useful patterns while decaying noise, and a numeric authority model governing multi- organization identity with hierarchical access control. Architectural validation through a comprehensive test suite of over 2,200 tests spanning unit, integra

---

### Significant_Other_AI_Identity_Memory_and_Emotional.pdf

**Excerpt:**
> Significant Other AI: Identity, Memory, and Emotional  Regulation as Long-Term Relational Intelligence  Sung Park  School of Data Science and Artificial Intelligence  Taejae University, Seoul, Republic of Korea  sjp@taejae.ac.kr    Abstract  Significant Others (SOs) stabilize identity, regulate emotion, and support narrative meaning - making, yet many people today lack access to such relational anchors. Recent advances in large  language models and memory -augmented AI raise the question of whethe r artificial systems  could support some of these functions. Existing empathic AIs, however, remain reactive and  short-term, lacking autobiographical memory, identity modeling, predictive emotional  regulation, and narrative coherence.  This manuscript introduces Significant Other Artificial  Intelligence (SO -AI) as a new domain of relational AI. It synthesizes psychological and  sociological theory to define SO functions and derives requirements for SO -AI, including  identity awareness, lon g-term memory, proactive support, narrative co -construction, and  ethical boundary enforcement. A conceptual architecture is proposed, comprising an  anthropomorphic interface, a relational cognition layer, and a governance layer. A research  agenda outlines methods for evaluating identity stability, longitudinal interaction patterns,  narrative development, and sociocultural impact.  SO-AI reframes AI-human relationships as  long-term, identity-bearing partnerships and provides a foundation

---

### LifeBench_A_Benchmark_for_Long-Horizon_Multi-Source_Memory.pdf

**Excerpt:**
> LifeBench: A Benchmark for Long-Horizon Multi-Source Memory Zihao Cheng1,2, Weixin Wang1,2, Yu Zhao3, Ziyang Ren3, Jiaxuan Chen1,2, Ruiyang Xu3, Shuai Huang3, Yang Chen3, Guowei Li3, Mengshi Wang3, Yi Xie3, Ren Zhu3, Zeren Jiang3, Keda Lu3, Yihong Li3, Xiaoliang Wang1, Liwei Liu3, Cam-Tu Nguyen1,2 1State Key Laboratory for Novel Software Technology, Nanjing University 2School of Artificial Intelligence, Nanjing University 3Huawei Technologies Co., Ltd. Nanjing, Jiangsu, China zihao_cheng@smail.nju.edu.cn Abstract Long-term memory is fundamental for personalized agents capa- ble of accumulating knowledge, reasoning over user experiences, and adapting across time. However, existing memory benchmarks primarily target declarative memory, specifically semantic and episodic types, where all information is explicitly presented in dialogues. In contrast, real-world actions are also governed by non- declarative memory, including habitual and procedural types, and need to be inferred from diverse digital traces. To bridge this gap, we introduce LifeBench, which features densely connected, long-horizon event simulation. It pushes AI agents beyond simple recall, requiring the integration of declarative and non-declarative memory reasoning across diverse and tempo- rally extended contexts. Building such a benchmark presents two key challenges: ensuring data quality and scalability. We maintain data quality by employing real-world priors, including anonymized social surveys, map APIs, and

---

### Graphilosophy_Graph-Based_Digital_Humanities.pdf

**Excerpt:**
> Graphilosophy: Graph-Based Digital Humanities Computing with The Four Books Minh-Thu Do     1,2, Quynh-Chau Le-Tran     1,2, Duc-Duy Nguyen-Mai     1,2, Thien-Trang Nguyen     1,2, Khanh-Duy Le     1,2, Minh-Triet Tran     1,2, Tam V. Nguyen     3, Trung-Nghia Le     1,2* 1University of Science, VNU-HCM, Ho Chi Minh City, Vietnam. 2Vietnam National University - Ho Chi Minh, Ho Chi Minh City, Vietnam. 3University of Dayton, Dayton, Ohio, United States. *Corresponding author(s). E-mail(s): ltnghia@fit.hcmus.edu.vn; Contributing authors: 24C02018@student.hcmus.edu.vn; 24C02003@student.hcmus.edu.vn; 24C02006@student.hcmus.edu.vn; 24C02021@student.hcmus.edu.vn; lkduy@fit.hcmus.edu.vn; tmtriet@fit.hcmus.edu.vn; tamnguyen@udayton.edu; Abstract The Four Books have shaped East Asian intellectual traditions, yet their multi- layered interpretive complexity limits their accessibility in the digital age. While traditional bilingual commentaries provide a vital pedagogical bridge, computa- tional frameworks are needed to preserve and explore this wisdom. This paper bridges AI and classical philosophy by introducing Graphilosophy, an ontology- guided, multi-layered knowledge graph framework for modeling and interpreting The Four Books. Integrating natural language processing, multilingual seman- tic embeddings, and humanistic analysis, the framework transforms a bilingual Chinese-Vietnamese corpus into an interpretively grounded resource. Graphi- losophy encodes linguistic, conceptual, and

---

### 2504.15965v2.pdf

**Excerpt:**
> From Human Memory to AI Memory: A Survey on Memory Mechanisms in the Era of LLMs Yaxiong Wu, Sheng Liang, Chen Zhang, Yichao Wang, Yongyue Zhang, Huifeng Guo, Ruiming Tang, Yong Liu Huawei Noah’s Ark Lab wu.yaxiong@huawei.com Abstract Memory is the process of encoding, storing, and retrieving information, allowing humans to retain experiences, knowledge, skills, and facts over time, and serving as the foundation for growth and effective interaction with the world. It plays a crucial role in shaping our identity, making decisions, learning from past ex- periences, building relationships, and adapting to changes. In the era of large language models (LLMs), memory refers to the ability of an AI system to retain, recall, and use information from past interactions to improve future responses and interactions. Although previous research and reviews have provided detailed de- scriptions of memory mechanisms, there is still a lack of a systematic review that summarizes and analyzes the relationship between the memory of LLM-driven AI systems and human memory, as well as how we can be inspired by human mem- ory to construct more powerful memory systems. To achieve this, in this paper, we propose a comprehensive survey on the memory of LLM-driven AI systems. In particular, we first conduct a detailed analysis of the categories of human memory and relate them to the memory of AI systems. Second, we systematically orga- nize existing memory-related work and propose a categorization metho

---

### GEPA_Reflective_Prompt_Evolution_2507.19457v2.pdf

**Excerpt:**
> Accepted at ICLR 2026 (Oral). GEPA: REFLECTIVEPROMPTEVOLUTIONCANOUTPER- FORMREINFORCEMENTLEARNING Lakshya A Agrawal1, Shangyin Tan1, Dilara Soylu2, Noah Ziems4, Rishi Khare1,Krista Opsahl-Ong 5,Arnav Singhvi 2,5,Herumb Shandilya 2, Michael J Ryan2,Meng Jiang 4,Christopher Potts 2,Koushik Sen 1, Alexandros G. Dimakis1,3,Ion Stoica 1,Dan Klein 1,Matei Zaharia 1,5,Omar Khattab 6 1UC Berkeley 2Stanford 3BespokeLabs.ai 4Notre Dame 5Databricks 6MIT ABSTRACT Large language models (LLMs) are increasingly adapted to downstream tasks via rein- forcement learning (RL) methods like Group Relative Policy Optimization (GRPO), which often require thousands of rollouts to learn new tasks. We argue that the interpretable na- ture oflanguageoften provides a much richer learning medium for LLMs, compared to policy gradients derived from sparse, scalar rewards. To test this, we introduce GEPA (Genetic-Pareto), a prompt optimizer that thoroughly incorporatesnatural language re- flectionto learn high-level rules from trial and error. Given any AI system containing one or more LLM prompts, GEPA samples trajectories (e.g., reasoning, tool calls, and tool outputs) and reflects on them in natural language to diagnose problems, propose and test prompt updates, and combine complementary lessons from the Pareto frontier of its own attempts. As a result of GEPA’s design, it can often turn even just a few rollouts into a large quality gain. Across six tasks, GEPA outperforms GRPO by 6% on average and by up

---

### Memory_Bear_AI.pdf

**Excerpt:**
> arXiv:2603.22306v1  [cs.AI]  18 Mar 2026 Abstract Affective judgment in real interaction is rarely a purely local prediction problem. Emotional meaning often depends on prior trajectory, contextual accumulation, and multimodal evidence that may be weak, noisy, or incomplete at the current moment. Although recent progress in multimodal emotion recognition (MER) has improved the integration of textual, acoustic, and visual signals, many existing systems still remain optimized for short-range inference and provide limited support for persistent affective memory, long-horizon dependency modeling, and context- aware robustness under imperfect input. This technical report presents theMemory Bear AI Memory Science En- gine, a memory-centered framework for multimodal affective intelligence. Instead of treating emotion as a transient output label, the proposed framework models affec- tive information as a structured and evolving variable within a memory system. The architecture organizes multimodal affective processing through structured memory formation, working-memory aggregation, long-term consolidation, memory-driven retrieval, dynamic fusion calibration, and continuous memory updating. At its core, the framework transforms multimodal signals into structuredEmotion Mem- ory Units(EMUs), allowing affective information to be preserved, reactivated, and revised across interaction horizons. Experimental results show that the proposed framework consistently outper- forms comparison sys

---

### s44387-025-00027-5.pdf

**Excerpt:**
>

---

### Dual-branch_Graph_Domain_Adaptation_for_Cross-scenario.pdf

**Excerpt:**
> Dual-branch Graph Domain Adaptation for Cross-scenario Multi-modal Emotion Recognition Y untao Shoushouyuntao@stu.xjtu.edu.cn College of Computer and Mathematics Central South University of Forestry and Technology Jun Zhou zhoujun@csuft.edu.cn College of Computer and Mathematics Central South University of Forestry and Technology T ao Meng mengtao@hnu.edu.cn College of Computer and Mathematics Central South University of Forestry and Technology W ei Ai aiwei@hnu.edu.cn College of Computer and Mathematics Central South University of Forestry and Technology Keqin Li lik@newpaltz.edu Department of Computer Science State University of New York Abstract Multimodal Emotion Recognition in Conversations (MERC) aims to predict speakers’ emo- tional states in multi-turn dialogues through text, audio, and visual cues. In real-world settings, conversation scenarios differ significantly in speakers, topics, styles, and noise lev- els. Existing MERC methods generally neglect these cross-scenario variations, limiting their ability to transfer models trained on a source domain to unseen target domains. To ad- dress this issue, we propose a Dual-branch Graph Domain Adaptation framework (DGDA) for multimodal emotion recognition under cross-scenario conditions. We first construct an emotion interaction graph to characterize complex emotional dependencies among utter- ances. A dual-branch encoder, consisting of a hypergraph neural network (HGNN) and a path neural network (PathNN), is then design

---

### EchoGuard_An_Agentic_Framework_with_Knowledge-Graph_Memory.pdf

**Excerpt:**
> EchoGuard: An Agentic Framework with Knowledge-Graph Memory for  Detecting Manipulative Communication in Longitudinal Dialogue    Ratna Kandala1 Niva Manchanda2  University of Kansas  University of Kansas                              ratnanirupama@gmail.com       n038k926@ku.edu   Akshata Kishore Moharir3 Ananth Kandala 4  University of Maryland University of Florida  akshatankishore5@gmail.com               ananthkandala46@gmail.com      Abstract  Manipulative communication, such as gaslight- ing, guilt-tripping, and emotional coercion, is  often difficult for individuals to recognize. Ex- isting agentic AI systems lack the structured,  longitudinal memory to track these subtle,  context-dependent tactics, often failing due to  limited context windows and catastrophic for - getting. We introduce EchoGuard, an agentic  AI framework that addresses this gap by using  a Knowledge Graph (KG) as the agent’s core  episodic and semantic memory. EchoGuard em- ploys a structured Log-Analyze-Reflect loop:  (1) users log interactions, which the agent struc- tures as nodes and edges in a personal, episodic  KG (capturing events, emotions, and speakers);  (2) the system executes complex graph queries  to detect six psychologically-grounded manip- ulation patterns (stored as a semantic KG);   and (3) an LLM generates targeted Socratic  prompts grounded by the subgraph of detected  patterns, guiding users toward self -discovery.  This framework demonstrates how the interplay  between agenti

---

### 2512.23343v1.pdf

**Excerpt:**
>

---

## Key Insights & Code Ideas for the Viking Companion Project

### 1. Hybrid Memory Architectures & Knowledge Graphs (EchoGuard & ElephantBroker)
*   **Insight:** Recent architectures (like EchoGuard and ElephantBroker) use a Knowledge Graph (KG) coupled with vector stores as core episodic and semantic memory. This allows tracking the provenance, temporal relationships, and trustworthiness of stored knowledge, mitigating catastrophic forgetting and improving context retrieval in longitudinal dialogs.
*   **Code Idea:**
    *   Enhance the `Mímisbrunnr` module (`mimir_well.py`) which currently uses ChromaDB (vector store). We can integrate a Graph database (like Neo4j or an in-memory NetworkX equivalent for local instances) to map entities (e.g., User, Astrid, Sigrid, events) and their relationships.
    *   *Implementation:* Create a `GraphMemoryStore` alongside `VectorMemoryStore`. During memory consolidation (Odinsblund), extract triples (subject, predicate, object) from episodic memories and inject them into the GraphMemoryStore.

### 2. Multi-Source, Long-Horizon Memory (LifeBench & Memory Bear AI)
*   **Insight:** Emotional meaning and procedural memory depend on prior trajectories, contextual accumulation, and non-declarative memory (habitual/procedural). Emotion should not be a transient output label, but a structured and evolving variable within a memory system.
*   **Code Idea:**
    *   Refine the `Ørlög Architecture` (Chrono-Biological Engine and Wyrd Matrix) and the PAD Model.
    *   *Implementation:* Implement a `PersistentAffectiveMemory` class that stores a rolling window of PAD states and context summaries. When querying memory for a response, inject the `AffectiveTrajectory` to influence the LLM's tone and behavior, rather than just the current emotional state.

### 3. Significant Other AI & Relational Intelligence
*   **Insight:** Empathic AIs need autobiographical memory, identity modeling, predictive emotional regulation, and narrative coherence to act as relational anchors ("Significant Others").
*   **Code Idea:**
    *   Strengthen the Persona definitions (Sigrid/Astrid) by maintaining an explicit "Autobiographical Ledger".
    *   *Implementation:* In the FederatedMemory, create a distinct `IdentityTier` that stores core beliefs and past significant interactions. The `PromptSynthesizer` should always prioritize this tier to maintain narrative coherence.

### 4. Reflective Prompt Evolution (GEPA)
*   **Insight:** Natural language reflection is an effective way to optimize prompts and behaviors, sometimes outperforming standard RL algorithms (like GRPO) because language provides a richer learning medium than scalar rewards.
*   **Code Idea:**
    *   *Implementation:* Add an `AgentReflectionModule`. After a conversation session, the secondary/local model generates a reflective summary of what worked well and what didn't in the interaction, updating a `interaction_heuristics.json` file. The primary model reads these heuristics to adjust its prompting dynamically in future sessions.
