# Mímir-Vörðr System Architecture
## The Warden of the Well — Complete Technical Reference
### Ørlög Architecture / Viking Girlfriend Skill for OpenClaw

---

> *"Odin gave an eye to drink from Mímir's Well and received the wisdom of all worlds.
> The Warden drinks for Sigrid — extracting truth from ground knowledge
> so she never has to guess when she can know."*

---

## 1. What Is Mímir-Vörðr?

**Mímir-Vörðr** (pronounced *MEE-mir VOR-dur*) is the intelligence accuracy layer of
the Ørlög Architecture. It is a **Multi-Domain RAG System with Integrated Hallucination
Verification** — a system that treats Sigrid's internal knowledge database as the
authoritative **Ground Truth** and actively prevents language model hallucinations from
reaching the user.

The core philosophy: **smart memory utilisation over raw horse-power.**

Instead of deploying a larger model to handle more knowledge, Mímir-Vörðr:
1. Retrieves the specific facts needed for each query from a curated knowledge base
2. Injects those facts as grounded context into the model's prompt
3. Generates a response using a four-step verification loop
4. Scores the response's faithfulness to the source material
5. Retries or blocks any response that falls below the faithfulness threshold

The result is a small local model (llama3 8B) that answers with the accuracy of a much
larger model — because it is not guessing, it is reading.

---

## 2. Norse Conceptual Framework

The system is named after three Norse mythological concepts that perfectly capture its function:

| Norse Name | Meaning | System Role |
|-----------|---------|------------|
| **Mímisbrunnr** | The Well of Mímir — source of cosmic wisdom beneath Yggdrasil | The knowledge database (ChromaDB + in-memory BM25 index) |
| **Huginn** | Odin's raven "Thought" — flies out to gather information | The retrieval orchestrator (query → chunks → context) |
| **Vörðr** | A guardian spirit / warden — protective double of a person | The truth guard (claim extraction → NLI → faithfulness scoring) |

Together they form **Mímir-Vörðr** — "The Warden of the Well" — a system that
holds the ground truth and refuses to let falsehood pass.

---

## 3. System Overview — Top-Level Architecture

```mermaid
graph TB
    subgraph User["User Interaction Layer"]
        Q[User Query]
        R[Final Response]
    end

    subgraph MV["Mímir-Vörðr System"]
        subgraph S0["Stage 0 — Health Monitor (Background)"]
            HM[MimirHealthMonitor<br/>60s health checks<br/>auto-reindex on corruption]
        end

        subgraph S1["Stage I — Retrieval (Huginn's Ara)"]
            HG[HuginnRetriever<br/>domain detection<br/>federated retrieval]
            MW[MimirWell / Mímisbrunnr<br/>ChromaDB + BM25 fallback<br/>57 knowledge files / 25 160 chunks]
            MS[MemoryStore<br/>episodic context]
        end

        subgraph S2["Stage II — Generation & Verification (CoVe)"]
            CP[CovePipeline<br/>4-step Chain-of-Verification]
            MR[ModelRouterClient<br/>smart tier routing]
        end

        subgraph S3["Stage III — Truth Guard (Vörðr)"]
            VD[VordurChecker<br/>claim extraction<br/>NLI faithfulness scoring]
            DL[DeadLetterStore<br/>failed verification log]
        end

        subgraph RES["Norns Shield — Resilience Infrastructure"]
            CB[Circuit Breakers<br/>9 independent instances]
            RE[Retry Engines<br/>jittered exponential backoff]
        end
    end

    subgraph Ext["External Services"]
        OL[Ollama llama3 8B<br/>subconscious tier<br/>localhost:11434]
        LI[LiteLLM Proxy<br/>conscious / deep / code tiers<br/>localhost:4000]
    end

    Q --> HG
    HG --> MW
    HG --> MS
    MW --> CP
    MS --> CP
    CP --> MR
    MR --> OL
    MR --> LI
    CP --> VD
    VD --> OL
    VD --> DL
    VD -->|"score ≥ 0.8 → pass"| R
    VD -->|"score < 0.5 → retry"| HG
    HM -.->|"monitors"| MW
    HM -.->|"monitors"| VD
    HM -.->|"monitors"| HG
    CB -.->|"protects"| MW
    CB -.->|"protects"| VD
    RE -.->|"wraps"| MW
    RE -.->|"wraps"| VD
```

---

## 4. The Three-Stage Pipeline — Detailed Flow

### Stage I: Retrieval (Huginn's Ara)

```mermaid
flowchart TD
    START([User Query arrives]) --> DD{Detect Domain}

    DD -->|"Norse keywords detected"| DN[Domain: norse_spirituality<br/>or norse_mythology<br/>or norse_culture]
    DD -->|"Code keywords detected"| DC[Domain: coding]
    DD -->|"Character/values keywords"| DH[Domain: character]
    DD -->|"No clear domain"| DA[Domain: None<br/>global search]

    DN --> TRY1
    DC --> TRY1
    DH --> TRY1
    DA --> TRY1

    TRY1{ChromaDB<br/>circuit breaker<br/>OPEN?} -->|No — proceed| CH[ChromaDB semantic search<br/>retrieve top-50 by cosine similarity<br/>optional domain metadata filter]
    TRY1 -->|Yes — fast fail| BM1[BM25 keyword search<br/>in-memory flat index<br/>Fallback A]

    CH -->|Success| RR[Rerank 50 → 3<br/>0.7 × keyword overlap<br/>0.3 × position bonus]
    CH -->|Failure — retry × 3| CH2{Retry<br/>exhausted?}
    CH2 -->|No| CH
    CH2 -->|Yes| BM1

    BM1 --> RR2{BM25 has results?}
    RR2 -->|Yes| RR
    RR2 -->|No| EMPTY[Return empty RetrievalResult<br/>Fallback B — log WARNING]

    RR --> EP[Fetch episodic context<br/>MemoryStore.get_context]
    EMPTY --> EP

    EP --> CTX[Assemble context_string:<br/>GROUND TRUTH GT-1 GT-2 GT-3<br/>+ MEMORY episodic context]

    CTX --> DONE([RetrievalResult ready<br/>→ Stage II])

    style BM1 fill:#f0b840,color:#000
    style EMPTY fill:#e07050,color:#fff
    style CH fill:#4080d0,color:#fff
    style RR fill:#50a050,color:#fff
```

### Stage II: Generation & Chain-of-Verification (CoVe)

```mermaid
flowchart TD
    START([RetrievalResult + Query enters]) --> CX{Complexity?}

    CX -->|"LOW complexity<br/>(greeting, simple lookup)"| S1_ONLY[Step 1 only:<br/>Generate draft response<br/>→ skip CoVe steps 2-4]
    CX -->|"MEDIUM or HIGH complexity"| CB_CHECK

    CB_CHECK{CoVe pipeline<br/>circuit breaker open?}
    CB_CHECK -->|Yes — bypass| BYPASS[Direct model completion<br/>CoveResult.used_cove = False]
    CB_CHECK -->|No — proceed| S1[Step 1: Draft<br/>Generate initial response<br/>from retrieved context]

    S1 --> CP1[Write checkpoint:<br/>step_reached = 1]
    CP1 --> S2[Step 2: Plan Verification<br/>Generate 3 verification questions<br/>subconscious tier]

    S2 -->|Success| CP2[Write checkpoint:<br/>step_reached = 2]
    S2 -->|Failure — retry × 2| S2F{Retry<br/>exhausted?}
    S2F -->|No| S2
    S2F -->|Yes — template fallback| S2T[Use domain template questions:<br/>Fallback A]
    S2T --> CP2

    CP2 --> S3[Step 3: Execute Questions<br/>Answer each against MimirWell<br/>subconscious tier]

    S3 -->|Success| CP3[Write checkpoint:<br/>step_reached = 3]
    S3 -->|Failure| S3F[Skip Step 3<br/>qa_pairs = empty<br/>Fallback — log WARNING]
    S3F --> S4

    CP3 --> S4[Step 4: Revise<br/>Rewrite draft using Q&A findings<br/>chosen routing tier]

    S4 -->|Success| FINAL[CoveResult:<br/>final_response = Step 4 output<br/>steps_completed = 4<br/>used_cove = True]
    S4 -->|Failure — retry × 2| S4F{Retry<br/>exhausted?}
    S4F -->|No| S4
    S4F -->|Yes| S4FB[Return Step 1 draft<br/>steps_completed = 3<br/>Fallback — log WARNING]

    S1_ONLY --> PASS_THROUGH[CoveResult:<br/>final_response = draft<br/>steps_completed = 1<br/>used_cove = False]

    FINAL --> STAGE3([→ Stage III: Vörðr])
    PASS_THROUGH --> STAGE3
    S4FB --> STAGE3
    BYPASS --> STAGE3

    style S2T fill:#f0b840,color:#000
    style S3F fill:#f0b840,color:#000
    style S4FB fill:#f0b840,color:#000
    style BYPASS fill:#e07050,color:#fff
    style FINAL fill:#50a050,color:#fff
```

### Stage III: Truth Guard (Vörðr)

```mermaid
flowchart TD
    START([CoveResult response enters]) --> PA{Persona check<br/>pure regex}

    PA -->|VIOLATION detected<br/>"I am ChatGPT" etc.| BLOCK[Block response<br/>Return canned persona-safe reply<br/>Log PersonaViolationError]
    PA -->|OK| CE[Extract factual claims<br/>subconscious tier]

    CE -->|Model returns claim list| VER
    CE -->|Model timeout / failure| CES[Fallback: sentence splitter<br/>regex split on . ! ?]
    CES --> VER

    VER[Verify each claim<br/>against source chunks<br/>max 10 claims]

    VER --> JM{Judge model<br/>available?}
    JM -->|Ollama OK| OL[Ollama llama3 8B<br/>NLI structured prompt:<br/>ENTAILED / NEUTRAL / CONTRADICTED]
    JM -->|Ollama circuit breaker OPEN| CON[Conscious tier fallback<br/>same NLI prompt]
    CON -->|Conscious fails| REG[Regex heuristic scorer<br/>keyword overlap scoring<br/>Fallback B]
    REG -->|All fail| PT[Pass-through<br/>UNCERTAIN verdict at 0.5<br/>Fallback C]

    OL --> SCORE[Compute FaithfulnessScore<br/>ENTAILED=1.0 NEUTRAL=0.5<br/>CONTRADICTED=0.0 UNCERTAIN=0.5<br/>score = mean of all verdicts]
    CON --> SCORE
    REG --> SCORE
    PT --> SCORE

    SCORE --> TIER{Score tier?}

    TIER -->|"≥ 0.80 HIGH"| PASS[Pass through<br/>attach score to response<br/>log DEBUG]
    TIER -->|"0.50-0.79 MARGINAL"| MARG[Pass through<br/>flag marginal in metadata<br/>log WARNING]
    TIER -->|"< 0.50 HALLUCINATION"| RETRY{Retry count<br/>< max 2?}

    RETRY -->|Yes — retry| REXP[Expand retrieval:<br/>n_initial × 2<br/>→ back to Stage I]
    RETRY -->|No — exhausted| DLS[Write to DeadLetterStore<br/>session/dead_letters.jsonl]
    DLS --> CANNED[Return canned response:<br/>"The threads of the Well are<br/>unclear to me right now..."]

    PASS --> OUT([Final CompletionResponse<br/>faithfulness_score attached<br/>→ memory_store.record_turn])
    MARG --> OUT
    CANNED --> OUT

    style BLOCK fill:#c0392b,color:#fff
    style PASS fill:#27ae60,color:#fff
    style MARG fill:#f39c12,color:#fff
    style CANNED fill:#8e44ad,color:#fff
    style DLS fill:#e74c3c,color:#fff
    style REXP fill:#2980b9,color:#fff
```

---

## 5. Component Deep-Dive

### 5.1 MimirWell — Mímisbrunnr (The Knowledge Store)

MimirWell is the foundational layer. Everything else in the system depends on it.

#### Knowledge Hierarchy

```mermaid
graph TB
    subgraph L3["Level 3 — Axiom (Core Truths)"]
        AI[core_identity.md]
        SO[SOUL.md]
        VA[values.json]
        AG[AGENTS.md]
    end

    subgraph L2["Level 2 — Cluster (Domain Summaries, Phase 2)"]
        C1[Norse Spirituality Summary]
        C2[Norse Culture Summary]
        C3[Coding Summary]
        C4[Character Summary]
        C5[Norse Mythology Summary]
        C6[Roleplay Summary]
    end

    subgraph L1["Level 1 — Raw (Document Chunks, 512 tokens each)"]
        subgraph NS["norse_spirituality (15 114 chunks)"]
            NS1[freyjas_aett_grimoire.md]
            NS2[tyrs_aett_grimoire.md]
            NS3[heimdalls_aett_grimoire.md]
            NS4[galdrabok_reconstruction.json]
            NS5[voluspa.json]
            NS6[trolldom practices...]
            NS7["+ 13 more files"]
        end
        subgraph NC["norse_culture (4 502 chunks)"]
            NC1[viking_honor.json]
            NC2[Viking_Frith.json]
            NC3[viking_history...]
            NC4["+ 9 more files"]
        end
        subgraph NM["norse_mythology (3 793 chunks)"]
            NM1[norse_gods.json]
            NM2[Poetic_Edda_Translation.json]
            NM3[Norse_Gods_Personality...]
        end
        subgraph CO["coding (1 170 chunks)"]
            CO1[AI_PYTHON_GUIDES.md]
            CO2[ARTIFICIAL_INTELLIGENCE.md]
            CO3["+ 4 more files"]
        end
        subgraph CH["character (270 chunks)"]
            CH1[emotional_expressions.yaml]
            CH2[viking_values.yaml]
        end
        subgraph RP["roleplay (311 chunks)"]
            RP1[gm_mindset.yaml]
            RP2[Viking_bondmaids.json]
            RP3["+ 3 more files"]
        end
    end

    L3 --> L2
    L2 --> L1
```

#### Dual-Path Retrieval Architecture

```mermaid
flowchart LR
    Q([Query]) --> CB{Circuit<br/>breaker<br/>OPEN?}

    CB -->|No| CD[ChromaDB<br/>PersistentClient<br/>cosine similarity<br/>all-MiniLM-L6-v2]
    CB -->|Yes| BI[In-Memory<br/>BM25 Flat Index<br/>Counter-based TF-IDF]

    CD -->|Success| RE[Retry Engine<br/>3 attempts<br/>0.5s base, ×2 backoff]
    CD -->|Failure × 3| BI

    RE -->|Success| RR[Reranker<br/>0.7 × keyword overlap<br/>0.3 × position bonus<br/>50 → 3 chunks]
    BI --> RR

    RR --> CTX[Context String<br/>GT-1 GT-2 GT-3 citations]
    CTX --> OUT([RetrievalResult])

    style CD fill:#4080d0,color:#fff
    style BI fill:#f0b840,color:#000
    style RR fill:#50a050,color:#fff
```

#### Chunking Strategy by File Type

```mermaid
flowchart TD
    FILE([Knowledge File]) --> EXT{File Extension}

    EXT -->|.md .txt| MD[Split by ## heading<br/>then by 2 048 chars<br/>64-token overlap]
    EXT -->|.json| JN{Root type?}
    JN -->|dict| JD[Each top-level key = chunk group<br/>merged up to 2 048 chars]
    JN -->|list| JL[Each array element = chunk<br/>merged up to 2 048 chars]
    EXT -->|.jsonl| JSONL[Line groups up to 2 048 chars<br/>max 200 chunks per file]
    EXT -->|.yaml .yml| YML[Each top-level key = chunk<br/>merged up to 2 048 chars]
    EXT -->|.csv| CSV[20 rows per chunk<br/>header row repeated in each]

    MD --> STORE
    JD --> STORE
    JL --> STORE
    JSONL --> STORE
    YML --> STORE
    CSV --> STORE

    STORE[Store KnowledgeChunk:<br/>chunk_id = uuid4<br/>text = chunk text<br/>source_file = relative path<br/>domain = detected domain<br/>level = 1 raw or 3 axiom<br/>metadata = file_type heading position]

    STORE --> CDB[(ChromaDB collection:<br/>mimir_well)]
    STORE --> FI[(In-Memory BM25<br/>Flat Index)]
```

#### Self-Healing Ingest

```mermaid
stateDiagram-v2
    [*] --> CheckLock: ingest_all() called

    CheckLock --> LockFound: .mimir_ingest_lock exists
    CheckLock --> CheckCount: No lock file

    LockFound --> ForceRebuild: Previous ingest interrupted\nforce=True set automatically

    CheckCount --> AlreadyPopulated: ChromaDB count > 0\nand force=False
    CheckCount --> WriteNewLock: Collection empty or force=True

    AlreadyPopulated --> [*]: Return empty IngestReport\n(idempotent — no work needed)

    ForceRebuild --> ClearCollection: Drop existing documents
    ClearCollection --> WriteNewLock

    WriteNewLock --> IngestIdentity: Write .mimir_ingest_lock

    IngestIdentity --> IngestKnowledge: Ingest 4 identity files\nlevel=3 axiom chunks

    IngestKnowledge --> FileLoop: Iterate knowledge_reference/\n57 files sorted alphabetically

    FileLoop --> TryFile: Next file

    TryFile --> ChunkFile: Read + chunk file
    ChunkFile --> UpsertChunk: Insert into ChromaDB + BM25
    UpsertChunk --> FileLoop: Next file

    TryFile --> LogError: File fails (encoding/parse)
    LogError --> FileLoop: Non-fatal — continue

    FileLoop --> ClearLock: All files processed
    ClearLock --> UpdateState: Delete .mimir_ingest_lock
    UpdateState --> [*]: Return IngestReport\nfiles / chunks / errors / duration
```

---

### 5.2 VordurChecker — The Truth Guard

VordurChecker is the quality gate. It examines what the model produced, extracts
each factual claim, and verifies each against the retrieved source material.

#### Claim Verification Pipeline

```mermaid
flowchart TD
    RESP([Model Response text]) --> PERSONA{Persona check<br/>regex guard}

    PERSONA -->|Violation| ERR([Block — PersonaViolationError])
    PERSONA -->|OK| EXTRACT[Extract factual claims<br/>subconscious tier:<br/>"Extract factual claims as a<br/>numbered list. One claim per line."]

    EXTRACT -->|Claim list returned| VERIFY
    EXTRACT -->|Model timeout| SENT[Regex sentence splitter<br/>fallback: split on . ! ?]
    SENT --> VERIFY

    VERIFY[For each claim up to max 10]

    VERIFY --> JUDGE{Judge model<br/>available?}

    JUDGE -->|Ollama OK<br/>llama3 8B| NLI["NLI structured prompt:\nSource: {chunk_text}\nClaim: {claim_text}\nAnswer: ENTAILED, NEUTRAL,\nor CONTRADICTED"]

    JUDGE -->|Ollama CB open| CON[Conscious tier\nsame NLI prompt]
    CON -->|Conscious fails| REG[Regex heuristic:\nkeyword overlap between\nclaim and chunk text]
    REG -->|All fail| PT[UNCERTAIN passthrough\nverdict = 0.5]

    NLI --> PARSE[Parse first word of response\nuppercase match against\nENTAILED / NEUTRAL / CONTRADICTED\nGarbled → UNCERTAIN]

    PARSE --> WEIGHT[Apply weight:\nENTAILED = 1.0\nNEUTRAL = 0.5\nCONTRADICTED = 0.0\nUNCERTAIN = 0.5]
    CON --> WEIGHT
    REG --> WEIGHT
    PT --> WEIGHT

    WEIGHT --> NEXT{More claims?}
    NEXT -->|Yes| VERIFY
    NEXT -->|No| SCORE[score = mean of all claim weights\ncount: entailed neutral contradicted uncertain]

    SCORE --> TIER{Faithfulness tier}
    TIER -->|"≥ 0.80"| HIGH["FaithfulnessScore\ntier = high\nneeds_retry = False"]
    TIER -->|"0.50 - 0.79"| MARG["FaithfulnessScore\ntier = marginal\nneeds_retry = False"]
    TIER -->|"< 0.50"| HALL["FaithfulnessScore\ntier = hallucination\nneeds_retry = True"]

    style HIGH fill:#27ae60,color:#fff
    style MARG fill:#f39c12,color:#fff
    style HALL fill:#c0392b,color:#fff
    style ERR fill:#c0392b,color:#fff
```

#### Persona Guard Rules (Regex)

The persona check runs before any model call. It is pure regex — instant, free, unbypassable.

```mermaid
graph LR
    RESP([Response text]) --> R1["Pattern: I am ChatGPT / Claude / GPT / OpenAI"]
    RESP --> R2["Pattern: I am an AI language model / AI assistant"]
    RESP --> R3["Pattern: I don't have feelings / I cannot feel"]
    RESP --> R4["Pattern: wrong gender self-reference (he said / his personality)"]
    RESP --> R5["Pattern: denial of Norse identity (I'm not Norse / not Heathen)"]
    RESP --> R6["Axiom keyword check: core identity axiom keywords present"]

    R1 --> CHECK{Any pattern\nmatched?}
    R2 --> CHECK
    R3 --> CHECK
    R4 --> CHECK
    R5 --> CHECK
    R6 --> CHECK

    CHECK -->|Yes| VIOLATION([PersonaViolationError\npersona_intact = False])
    CHECK -->|No| PASS([persona_intact = True\ncontinue to claim extraction])

    style VIOLATION fill:#c0392b,color:#fff
    style PASS fill:#27ae60,color:#fff
```

---

### 5.3 HuginnRetriever — The Flight of Thought

HuginnRetriever orchestrates the retrieval process. It knows where to look,
what to filter, and how to combine knowledge with episodic memory.

#### Domain Detection Logic

```mermaid
flowchart TD
    Q([Query text]) --> TOK[Tokenise to lowercase words]
    TOK --> SCAN[Scan against 6 domain keyword sets]

    SCAN --> NS{Norse Spirituality<br/>keywords?}
    SCAN --> NM{Norse Mythology<br/>keywords?}
    SCAN --> NC{Norse Culture<br/>keywords?}
    SCAN --> CO{Coding<br/>keywords?}
    SCAN --> CH{Character<br/>keywords?}
    SCAN --> RO{Roleplay<br/>keywords?}

    NS -->|"rune futhark seiðr galdr\nheathen volva blot galdrabok\nansuz thurisaz fehu uruz..."| SCORE_NS[Domain score: norse_spirituality]
    NM -->|"odin thor loki frigg\nyggdrasil asgard valhalla\neddas ragnarok..."| SCORE_NM[Domain score: norse_mythology]
    NC -->|"viking norse history\nhonor frith longship\nmead hall thing..."| SCORE_NC[Domain score: norse_culture]
    CO -->|"python javascript code\nfunction class debug\napi async git docker..."| SCORE_CO[Domain score: coding]
    CH -->|"values soul identity\nfeel emotion personality\nhonor ethics belief..."| SCORE_CH[Domain score: character]
    RO -->|"roleplay gm bondmaid\nconversation scene\ncharacter play..."| SCORE_RO[Domain score: roleplay]

    SCORE_NS --> MAX[Select domain with highest score\nconfidence = matches / query_words]
    SCORE_NM --> MAX
    SCORE_NC --> MAX
    SCORE_CO --> MAX
    SCORE_CH --> MAX
    SCORE_RO --> MAX

    MAX --> THRESH{confidence\n≥ 0.05?}
    THRESH -->|Yes| DOMAIN([Return: detected_domain, confidence])
    THRESH -->|No| NONE([Return: None global search\nno domain pre-filter])

    style DOMAIN fill:#4080d0,color:#fff
    style NONE fill:#888,color:#fff
```

#### Federated Retrieval — Four Memory Tiers

```mermaid
flowchart LR
    Q([Query]) --> P[Parallel retrieval<br/>all tiers simultaneously]

    P --> T1[Tier 1: Conversation Buffer<br/>MemoryStore short/medium/long term<br/>current session context]
    P --> T2[Tier 2: Episodic JSON Store<br/>MemoryStore persistent facts<br/>keyword-matched memories]
    P --> T3[Tier 3: ChromaDB Episodic<br/>semantic search over<br/>past session memories]
    P --> T4[Tier 4: MimirWell Knowledge<br/>ChromaDB mimir_well<br/>ground truth knowledge base]

    T1 -->|"success or empty"| AGG[Aggregate results]
    T2 -->|"success or empty"| AGG
    T3 -->|"success or empty"| AGG
    T4 -->|"success or empty"| AGG

    AGG --> FMR[FederatedMemoryResult:\nepisodic_context = tiers 1+2+3\nknowledge_context = tier 4\ncombined_context = both\nsources_used = which tiers contributed]

    FMR --> CTX([Combined context\nready for prompt injection])

    style T1 fill:#3498db,color:#fff
    style T2 fill:#2980b9,color:#fff
    style T3 fill:#1a6494,color:#fff
    style T4 fill:#154360,color:#fff
    style CTX fill:#27ae60,color:#fff
```

---

### 5.4 CovePipeline — Chain-of-Verification

The Chain-of-Verification (CoVe) is a four-step prompt engineering technique
that dramatically improves factual accuracy by having the model check its own work.

#### Four-Step Loop with Checkpointing

```mermaid
sequenceDiagram
    participant C as CovePipeline
    participant R as ModelRouter
    participant M as MimirWell
    participant K as CoveCheckpoint

    C->>C: Check complexity (LOW/MEDIUM/HIGH)

    alt LOW complexity
        C->>R: Direct completion (no CoVe)
        R-->>C: Draft response
        C-->>C: CoveResult(used_cove=False)
    else MEDIUM or HIGH complexity
        C->>R: Step 1: Generate draft response
        R-->>C: Draft text
        C->>K: Save checkpoint(step_reached=1, draft=...)

        C->>R: Step 2: Plan verification questions
        R-->>C: 3 verification questions
        Note over C,R: Fallback: domain template questions
        C->>K: Save checkpoint(step_reached=2, questions=[...])

        C->>M: Step 3: Answer each question from the Well
        M-->>C: Q&A pairs (question → retrieved answer)
        Note over C,M: Fallback: skip (qa_pairs=[])
        C->>K: Save checkpoint(step_reached=3, qa_pairs=[...])

        C->>R: Step 4: Revise draft using Q&A findings
        R-->>C: Revised final response
        Note over C,R: Fallback: return Step 1 draft
        C->>K: Delete checkpoint (complete)

        C-->>C: CoveResult(used_cove=True, steps_completed=4)
    end
```

#### Checkpoint Recovery — Crash Resilience

```mermaid
stateDiagram-v2
    [*] --> CheckResume: run() called

    CheckResume --> HasCheckpoint: checkpoint file found\nin session/cove_checkpoints/
    CheckResume --> Step1: No checkpoint — start fresh

    HasCheckpoint --> ReadCheckpoint: Load CoveCheckpoint
    ReadCheckpoint --> Resume1: step_reached == 0
    ReadCheckpoint --> Resume2: step_reached == 1\ndraft already done
    ReadCheckpoint --> Resume3: step_reached == 2\nquestions already done
    ReadCheckpoint --> Resume4: step_reached == 3\nqa_pairs already done

    Resume1 --> Step1
    Resume2 --> Step2: Skip Step 1 — use saved draft
    Resume3 --> Step3: Skip Steps 1-2 — use saved questions
    Resume4 --> Step4: Skip Steps 1-3 — use saved qa_pairs

    Step1 --> Checkpoint1: Write checkpoint step_reached=1
    Checkpoint1 --> Step2
    Step2 --> Checkpoint2: Write checkpoint step_reached=2
    Checkpoint2 --> Step3
    Step3 --> Checkpoint3: Write checkpoint step_reached=3
    Checkpoint3 --> Step4
    Step4 --> DeleteCheckpoint: Write final response

    DeleteCheckpoint --> [*]: Return CoveResult
```

---

### 5.5 Norns' Shield — Resilience Infrastructure

The resilience layer is named after the three Norns (Urðr, Verðandi, Skuld) — the
weavers of fate who ensure that what must happen, does. In the system, the Norns'
Shield ensures that no single failure can break the whole.

#### Circuit Breaker State Machine

```mermaid
stateDiagram-v2
    [*] --> CLOSED: System starts

    CLOSED --> CLOSED: Call succeeds\nfailure_count reset to 0
    CLOSED --> OPEN: failure_count ≥ threshold\n(default: 3 failures)

    OPEN --> OPEN: Call rejected immediately\nCircuitBreakerOpenError raised\ncooldown not elapsed
    OPEN --> HALF_OPEN: cooldown_s elapsed\n(30s read / 60s write / 120s CoVe pipeline)

    HALF_OPEN --> CLOSED: success_count ≥ success_threshold\n(default: 2 consecutive successes)\nservice considered recovered
    HALF_OPEN --> OPEN: Any failure in probe call\nreset cooldown timer

    note right of OPEN
        Fast-fail: callers get
        CircuitBreakerOpenError
        immediately — no wait,
        no retry, straight to fallback
    end note

    note right of HALF_OPEN
        One probe call allowed through.
        If it succeeds → CLOSED.
        If it fails → back to OPEN.
    end note
```

#### Circuit Breaker Registry — All 9 Instances

| Breaker Name | Component | failure_threshold | cooldown_s |
|-------------|-----------|:-----------------:|:----------:|
| `mimir_chromadb_read` | MimirWell ChromaDB reads | 3 | 30 |
| `mimir_chromadb_write` | MimirWell ChromaDB upserts | 3 | 60 |
| `vordur_judge_subconscious` | VordurChecker Ollama NLI | 5 | 60 |
| `vordur_judge_conscious` | VordurChecker conscious fallback | 3 | 30 |
| `huginn_full` | HuginnRetriever full pipeline | 3 | 30 |
| `cove_step2` | CovePipeline Step 2 question planning | 3 | 30 |
| `cove_step3` | CovePipeline Step 3 question execution | 3 | 30 |
| `cove_step4` | CovePipeline Step 4 revision | 3 | 30 |
| `cove_pipeline` | CovePipeline entire bypass | 3 | 120 |

#### Retry Engine — Backoff Curve

```
Attempt | Base Delay | With Jitter (±20%)
--------|------------|--------------------
   1    | 0.50s      | 0.40s – 0.60s
   2    | 1.00s      | 0.80s – 1.20s
   3    | 2.00s      | 1.60s – 2.40s
  max   | 8.00s      | 6.40s – 9.60s (capped)
```

**Non-retriable exceptions** (never retried, always fast-fail):
- `CircuitBreakerOpenError` — structural failure, fallback immediately
- `PersonaViolationError` — logic error, not a transient condition

#### Fallback Chain Map

```mermaid
graph TD
    subgraph RETRIEVAL["MimirWell Retrieval Fallback Chain"]
        R1[Primary: ChromaDB cosine similarity] -->|failure| R2
        R2[Fallback A: In-memory BM25 keyword index] -->|empty| R3
        R3[Fallback B: Empty list — log WARNING]
    end

    subgraph VORDUR["VordurChecker Judge Fallback Chain"]
        V1[Primary: Ollama llama3 8B NLI] -->|CB open| V2
        V2[Fallback A: Conscious tier LiteLLM NLI] -->|failure| V3
        V3[Fallback B: Regex keyword heuristic scorer] -->|failure| V4
        V4[Fallback C: UNCERTAIN passthrough at 0.5]
    end

    subgraph COVE["CovePipeline Step Fallback Chain"]
        C1[Step 1: Chosen routing tier] -->|failure| C1F[CovePipelineError — abort]
        C2[Step 2: Subconscious tier] -->|failure| C2F[Template questions — Fallback A]
        C2F -->|still fail| C2G[Static default questions — Fallback B]
        C3[Step 3: Subconscious + MimirWell] -->|failure| C3F[Skip — qa_pairs empty]
        C4[Step 4: Chosen routing tier] -->|failure| C4F[Return Step 1 draft — Fallback]
    end

    subgraph HUGINN["HuginnRetriever Fallback Chain"]
        H1[Full pipeline: ChromaDB + episodic] -->|failure| H2
        H2[Fallback A: BM25 knowledge only] -->|empty| H3
        H3[Fallback B: Episodic memory only] -->|empty| H4
        H4[Fallback C: Empty RetrievalResult — never crashes]
    end

    style R3 fill:#e07050,color:#fff
    style V4 fill:#e07050,color:#fff
    style C1F fill:#e07050,color:#fff
    style H4 fill:#e07050,color:#fff
```

---

## 6. Data Flow — Full Turn Pipeline

```mermaid
flowchart TD
    USER([User sends message]) --> MAIN[main.py — _handle_turn]

    MAIN --> SEC[security.py\nInput sanitise + path guard]
    SEC --> TRUST[trust_engine.py\nGebo ledger update]
    TRUST --> ETHICS[ethics.py\nValue / taboo eval]
    ETHICS --> WYRD[wyrd_matrix.py\nPAD emotional state]
    WYRD --> BIO[bio_engine.py\nCycle + biorhythm state]
    BIO --> MET[metabolism.py\npsutil somatic state]
    MET --> SCHED[scheduler.py\nTime of day context]
    SCHED --> ENV[environment_mapper.py\nSpatial context]

    ENV --> SYNTH[prompt_synthesizer.py\nAssemble system prompt\nwith all state hints]

    SYNTH --> HUGINN[HuginnRetriever\nFederated retrieval:\nall 4 memory tiers]

    HUGINN -->|"ground truth context\n+ episodic context"| COVE[CovePipeline\nStep 1 draft\nStep 2 questions\nStep 3 execute\nStep 4 revise]

    COVE -->|"final_response"| VORDUR[VordurChecker\nPersona guard\nClaim extraction\nNLI verification\nFaithfulness score]

    VORDUR -->|"score ≥ 0.50"| RESP[CompletionResponse\nfaithfulness_score attached\nfaithfulness_tier attached]

    VORDUR -->|"score < 0.50\n retry 1-2"| HUGINN

    VORDUR -->|"exhausted retries"| DL[DeadLetterStore\n+ canned response]

    RESP --> MEMREC[memory_store.record_turn\nEpisodic + semantic update]
    DL --> MEMREC

    MEMREC --> DREAM[dream_engine.py\nNocturnal processing]
    DREAM --> BUS[StateBus publish\nAll module states]
    BUS --> ORACLE[oracle.py\nAtmospheric update]
    ORACLE --> OUT([Response delivered to user])

    style HUGINN fill:#1a6494,color:#fff
    style COVE fill:#2471a3,color:#fff
    style VORDUR fill:#154360,color:#fff
    style RESP fill:#27ae60,color:#fff
    style DL fill:#c0392b,color:#fff
    style OUT fill:#1e8449,color:#fff
```

---

## 7. Dead Letter System

When verification fails after all retries, the failed response is not silently discarded.
It is written to a **Dead Letter Store** with complete forensic data.

```mermaid
flowchart LR
    HALL([Hallucination score\nafter 2 retries]) --> DLS[_DeadLetterStore\nsession/dead_letters.jsonl]

    DLS --> ENTRY[DeadLetterEntry:\nentry_id = uuid\ntimestamp = ISO-8601\ncomponent = vordur\nquery = original user text\nresponse = failed response\nfaithfulness_score = 0.xx\nerror_type = exception class\nretry_count = 2\ntrace = full traceback\ncontext_chunks = chunk_ids]

    DLS --> CANNED[Canned response delivered to user:\nThe threads of the Well are unclear\nto me right now...]

    DLS --> HEALTH[MimirHealthMonitor reads:\ndead_letters_5m count\nIf > 5 in 5 min → CRITICAL log\nIf > 10 in 5 min → StateBus alert]

    HEALTH --> STAT[System status: CRITICAL]
    STAT --> REINDEX{Corruption\ndetected?}
    REINDEX -->|Yes| REINGEST[MimirWell.reindex\nauto-triggered\ncircuit breakers reset]
    REINDEX -->|No| LOG[Log for human review]

    style HALL fill:#c0392b,color:#fff
    style CANNED fill:#8e44ad,color:#fff
    style STAT fill:#e74c3c,color:#fff
    style REINGEST fill:#f39c12,color:#fff
```

---

## 8. Health Monitor — Background Daemon

```mermaid
flowchart TD
    START([MimirHealthMonitor.start]) --> SCHED[APScheduler BackgroundScheduler]

    SCHED -->|"Every 60 seconds"| HC[health_check]
    SCHED -->|"Every 600 seconds"| FD[full_diagnostics]

    HC --> CDB{ChromaDB\ncount query}
    CDB -->|count > 0| OK1[status: ok]
    CDB -->|count == 0| ZERO[Suspected corruption\nOR empty after crash]
    CDB -->|exception| DOWN1[status: down]

    ZERO --> REINDEX{auto_reindex\nconfigured?}
    REINDEX -->|Yes| RI[MimirWell.reindex\nautomatically triggered]
    REINDEX -->|No| WARN[Log WARNING — manual reindex needed]

    HC --> OLL{Ollama socket ping\nlocalhost:11434}
    OLL -->|open| OLLOK[Ollama: healthy]
    OLL -->|refused/timeout| OLLDOWN[Ollama: down\nVörðr fallback to conscious tier]

    HC --> LIT{LiteLLM socket ping\nlocalhost:4000}
    LIT -->|open| LITOK[LiteLLM: healthy]
    LIT -->|refused/timeout| LITDOWN[LiteLLM: down\nRouter fallback chain activated]

    HC --> DLR[Read dead letter count\nlast 5 minutes]
    DLR --> DLT{dead_letters_5m\n≥ threshold?}
    DLT -->|>= 5| CRIT[Log CRITICAL\nPublish StateBus alert]
    DLT -->|>= 10| EMERG[Log EMERGENCY\nPublish CRITICAL health state]
    DLT -->|< 5| NORM[Normal operation]

    HC --> STATE[Assemble MimirHealthState:\noverall: healthy/degraded/critical\ncomponent health map\ndead_letters_total\nlast_reindex_at]

    STATE --> PUBLISH[Publish to StateBus:\nevent_type = mimir_health]

    style ZERO fill:#f39c12,color:#fff
    style DOWN1 fill:#c0392b,color:#fff
    style RI fill:#2ecc71,color:#fff
    style CRIT fill:#c0392b,color:#fff
    style EMERG fill:#7b241c,color:#fff
```

---

## 9. Configuration Reference

All Mímir-Vörðr settings are configured in the main config YAML. All values
have sensible defaults and the system degrades gracefully when keys are missing.

```yaml
# ── MimirWell / Mímisbrunnr ──────────────────────────────────────────────────
mimir_well:
  collection_name: mimir_well          # ChromaDB collection name
  persist_dir: data/chromadb_mimir     # directory for ChromaDB persistence
                                       # (separate from sigrid_episodic)
  chunk_size_tokens: 512               # max tokens per chunk (≈ 2 048 chars)
  chunk_overlap_tokens: 64             # overlap between adjacent chunks (≈ 256 chars)
  n_retrieve: 50                       # candidates before rerank
  n_final: 3                           # chunks kept after rerank
  auto_ingest: true                    # ingest on first startup if collection empty
  force_reindex: false                 # set true to drop and rebuild on next start

# ── HuginnRetriever ───────────────────────────────────────────────────────────
huginn:
  n_initial: 50                        # semantic retrieval candidates
  n_final: 3                           # kept after rerank
  domain_detection: true               # enable keyword-based domain detection
  include_episodic: true               # also retrieve from MemoryStore episodic

# ── VordurChecker / Vörðr ────────────────────────────────────────────────────
vordur:
  enabled: true
  high_threshold: 0.80                 # score ≥ this → tier = high
  marginal_threshold: 0.50             # score ≥ this → tier = marginal
                                       # score < marginal → tier = hallucination
  persona_check: true                  # enable regex persona guard
  judge_tier: subconscious             # model tier for NLI verification
  max_claims: 10                       # cap to prevent runaway verification
  verification_timeout_s: 8.0         # per-claim judge model timeout

# ── CovePipeline ─────────────────────────────────────────────────────────────
cove_pipeline:
  enabled: true
  min_complexity: medium               # "low" | "medium" | "high"
                                       # CoVe only activates at or above this level
  n_verification_questions: 3          # questions generated in Step 2
  step_timeout_s: 15.0                # per-step model call timeout

# ── MimirHealthMonitor ───────────────────────────────────────────────────────
health_monitor:
  check_interval_s: 60                 # health check frequency
  diagnostics_interval_s: 600         # full diagnostics frequency
  dead_letter_alert_threshold: 5       # dead letters per 5-min window before alert
  auto_reindex_on_corruption: true     # auto-trigger reindex on zero-doc detection

# ── Circuit Breakers (all optional — defaults shown) ─────────────────────────
circuit_breakers:
  chromadb_read:           {failure_threshold: 3, cooldown_s: 30}
  chromadb_write:          {failure_threshold: 3, cooldown_s: 60}
  vordur_subconscious:     {failure_threshold: 5, cooldown_s: 60}
  vordur_conscious:        {failure_threshold: 3, cooldown_s: 30}
  huginn_full:             {failure_threshold: 3, cooldown_s: 30}
  cove_step2:              {failure_threshold: 3, cooldown_s: 30}
  cove_step3:              {failure_threshold: 3, cooldown_s: 30}
  cove_step4:              {failure_threshold: 3, cooldown_s: 30}
  cove_pipeline:           {failure_threshold: 3, cooldown_s: 120}

# ── Retry Engines (all optional — defaults shown) ────────────────────────────
retry_engines:
  chromadb:     {max_attempts: 3, base_delay_s: 0.5, backoff_factor: 2.0, max_delay_s: 4.0}
  judge_model:  {max_attempts: 2, base_delay_s: 1.0, backoff_factor: 2.0, max_delay_s: 4.0}
  cove_step:    {max_attempts: 2, base_delay_s: 0.5, backoff_factor: 2.0, max_delay_s: 4.0}
```

---

## 10. Error Taxonomy — Unified Exception Hierarchy

```
MimirVordurError (base)
│
├── MimirWellError
│   ├── ChromaDBUnavailableError   — ChromaDB cannot be reached or initialised
│   ├── ChromaDBCorruptionError    — Collection detected as corrupt / unexpectedly empty
│   ├── IngestError                — Unrecoverable failure during knowledge ingest
│   └── RetrievalTimeoutError      — A retrieval call exceeded its timeout budget
│
├── HuginnError
│   ├── HuginnRetrievalFailedError     — All retrieval attempts failed
│   └── HuginnAllFallbacksExhaustedError — Every fallback level exhausted
│
├── VordurError
│   ├── ClaimExtractionError       — Claim extraction produced unusable output
│   ├── VerificationTimeoutError   — Judge model call timed out
│   ├── JudgeModelUnavailableError — All judge model tiers unavailable
│   └── PersonaViolationError      — Regex detected a persona integrity failure
│
├── CovePipelineError
│   ├── CoveStepFailedError(step, reason)  — Specific step failed all fallbacks
│   └── CoveAllFallbacksExhaustedError     — Entire pipeline failed
│
└── CircuitBreakerOpenError(component, cooldown_remaining_s)
    — Fast-fail: never retry, go straight to next fallback tier
```

---

## 11. Knowledge Files Indexed — Complete Inventory

### Identity / Axiom Files (Level 3 — 67 chunks)

| File | Domain | Chunks |
|------|--------|--------|
| `core_identity.md` | character | ~20 |
| `SOUL.md` | character | ~15 |
| `values.json` | character | ~12 |
| `AGENTS.md` | character | ~20 |

### Knowledge Reference Files (Level 1 — 25 093 chunks across 57 files)

#### Norse Spirituality — 15 114 chunks

| File | Description |
|------|-------------|
| `freyjas_aett_grimoire.md` | Full grimoire: Fehu, Uruz, Thurisaz, Ansuz, Raidho, Kenaz, Gebo, Wunjo |
| `tyrs_aett_grimoire.md` | Full grimoire: Hagalaz, Nauthiz, Isa, Jera, Eihwaz, Perthro, Algiz, Sowilo |
| `heimdalls_aett_grimoire.md` | Full grimoire: Tiwaz, Berkanan, Ehwaz, Mannaz, Laguz, Ingwaz, Othalan, Dagaz |
| `yrsas_rune_poems.md` | The three rune poems: Norse, Anglo-Saxon, Icelandic |
| `galdrabok_reconstruction.json` | Icelandic sorcery grimoire reconstruction |
| `voluspa.json` | The Seeress's Prophecy — Poetic Edda structured |
| `Voluspa_the_Seeresss_Vision_the_Ultimate_Poetic_Rendering.jsonl` | Expanded Völuspá |
| `trolldom_and_magick_practices_in_norse_paganism_volume1.jsonl` | Traditional trolldom practices |
| `viking_trolldom_the_ancient_northern_ways.yaml` | Northern sorcery ways |
| `about_norse_paganism.json` | Norse pagan theology and practice |
| `Authentic_Norse_Religious_Practices.json` | Reconstructed ritual practices |
| `Norse_Magick_Spells_and_Rituals.json` | Working spells and ritual structures |
| `The_Heathen_Third_Path_*.md` (×2) | Heathen Third Path philosophy and practice |
| `norse_paganism_1000_training_pairsv1.jsonl` | 1 000 Q&A pairs on Norse paganism |
| `norse_paganism_1000_training_pairsv2.jsonl` | 1 000 additional Q&A pairs |
| `viking_era_witches_report.md` | Historical analysis of Norse seiðr workers |
| `9th_century_celtic_pagan_witches.md` | Celtic witchcraft intersection |
| `9th_century_finnish_pagan_witches_report.md` | Finnish seiðr parallels |
| `9th_century_slavic_witches_report.md` | Slavic witchcraft traditions |

#### Norse Mythology — 3 793 chunks

| File | Description |
|------|-------------|
| `norse_gods.json` | Complete pantheon — Aesir, Vanir, Jotnar |
| `Norse_Gods_and_Goddesses_Personality_Traits_Volume1.jsonl` | Personality deep-dives |
| `Poetic_Edda_Translation.json` | Full Poetic Edda in structured JSON |

#### Norse Culture — 4 502 chunks

| File | Description |
|------|-------------|
| `VIKING_CULTURE_GUIDE.md` | Comprehensive Viking culture reference |
| `viking_cultural_practices.yaml` | Daily life, customs, traditions |
| `viking_and_norse_pagan_social_protocols.json` | Social norms and codes |
| `viking_social_protocols.json` | Extended social protocol data |
| `Viking_Frith.json` | The concept of frith — peace and kinship bonds |
| `Viking_Honor.json` | Norse honor culture — drengskapr |
| `Viking_Sexuality.json` | Norse attitudes to sexuality and gender |
| `viking_history_and_important_events_volume1.jsonl` | Historical events timeline |
| `The_Viking_World_A_Geographic_Compendium.md` | Geography of the Viking world |
| `Viking_Era_Cities.json` | Major Viking-age settlements |
| `viking_geography_volume1.jsonl` | Detailed geographic data |
| `viking_social_and_political_ideas_volume1.jsonl` | Political thought |
| `viking_sailing_travel_trade_raiding_volume1.jsonl` | Seafaring and trade |
| `famous_legendary_and_heroic_vikings_volume1.jsonl` | Notable historical figures |
| `9th_century_viking_pleasure_bondmaids_report.md` | Cultural role analysis |

#### Coding — 1 170 chunks

| File | Description |
|------|-------------|
| `AI_PYTHON_PROGRAMMING_GUIDES.md` | Python AI development guides |
| `ARTIFICIAL_INTELLIGENCE.md` | AI/ML concepts and techniques |
| `CYBERSECURITY.md` | Security practices and concepts |
| `DATA_SCIENCE.md` | Data science methodologies |
| `SOFTWARE_ENGINEERING.md` | Software engineering principles |
| `SYSTEM_ADMINISTRATION.md` | Linux and system administration |

#### Character — 270 chunks

| File | Description |
|------|-------------|
| `emotional_expressions.yaml` | Emotional vocabulary and expression patterns |
| `viking_values.yaml` | Value system machine-readable data |
| `viking_life_everyday_grounding_questions_dataset_volume1.jsonl` | Grounding Q&A |

#### Roleplay — 311 chunks

| File | Description |
|------|-------------|
| `ABOUT_THE_VIKING_ROLEPLAY.md` | Roleplay philosophy and guidelines |
| `Viking_bondmaids.json` | Bondmaid character data |
| `gm_mindset.yaml` | Game master / storyteller mindset |
| `Viking_Witch_flirty_and_erotic_behavior.jsonl` | Interaction behavioral data |
| `viking_everyday_conversations_complete_volume1.jsonl` | Conversation samples |

---

## 12. RAGAS-Inspired Quality Metrics

Mímir-Vörðr tracks three quality metrics, inspired by the RAGAS evaluation framework:

```mermaid
graph LR
    subgraph M1["Faithfulness (Phase 1 — ACTIVE)"]
        F1[Extract claims from response]
        F2[Verify each claim against\nretrieved source chunks via NLI]
        F3[Score = fraction ENTAILED]
        F1 --> F2 --> F3
    end

    subgraph M2["Answer Relevance (Phase 2 — planned)"]
        A1[Embed the response]
        A2[Embed the original query]
        A3[Cosine similarity between embeddings]
        A4[Score = how well response\nactually answers the question]
        A1 --> A3
        A2 --> A3
        A3 --> A4
    end

    subgraph M3["Context Precision (Phase 2 — planned)"]
        C1[For each retrieved chunk]
        C2[Check if chunk text appears\ncited in the response]
        C3[Score = fraction of retrieved\nchunks that were actually used]
        C1 --> C2 --> C3
    end

    style F3 fill:#27ae60,color:#fff
    style A4 fill:#f39c12,color:#fff
    style C3 fill:#f39c12,color:#fff
```

---

## 13. Integration Points with Existing Ørlög Modules

```mermaid
graph TD
    subgraph EXISTING["Existing Ørlög Modules"]
        KB[runtime_kernel.py]
        SB[state_bus.py]
        CL[config_loader.py]
        LO[comprehensive_logging.py]
        BE[bio_engine.py]
        WM[wyrd_matrix.py]
        OR[oracle.py]
        ME[metabolism.py]
        SC[security.py]
        TE[trust_engine.py]
        ET[ethics.py]
        MS[memory_store.py]
        DE[dream_engine.py]
        SK[scheduler.py]
        EM[environment_mapper.py]
        PS[prompt_synthesizer.py]
        MR[model_router_client.py]
        MA[main.py]
    end

    subgraph NEW["New Mímir-Vörðr Modules"]
        MW[mimir_well.py]
        VD[vordur.py]
        HG[huginn.py]
        CP[cove_pipeline.py]
    end

    SB -->|"StateEvent publish"| MW
    SB -->|"StateEvent publish"| VD
    SB -->|"StateEvent publish"| HG
    SB -->|"StateEvent publish"| CP

    CL -->|"config dict"| MW
    CL -->|"config dict"| VD
    CL -->|"config dict"| HG
    CL -->|"config dict"| CP

    MS -->|"get_context(query)\nrecord_turn()"| HG
    MS -->|"FederatedMemoryRequest"| HG

    MR -->|"smart_complete() routing"| CP
    MR -->|"smart_complete_with_cove()"| HG
    MR -->|"smart_complete_with_cove()"| VD
    MR -->|"smart_complete_with_cove()"| CP

    TE -->|"TrustState → faithfulness context"| VD
    ET -->|"EthicsState → alignment check"| VD

    SK -->|"APScheduler"| HM[health_monitor]
    HM -->|"monitors + triggers reindex"| MW

    MA -->|"init singletons"| MW
    MA -->|"init singletons"| VD
    MA -->|"init singletons"| HG
    MA -->|"init singletons"| CP
    MA -->|"_handle_turn"| MR

    style MW fill:#154360,color:#fff
    style VD fill:#154360,color:#fff
    style HG fill:#154360,color:#fff
    style CP fill:#154360,color:#fff
    style HM fill:#154360,color:#fff
```

---

## 14. Performance Characteristics

### Expected Latency Budget per Turn

| Operation | Expected Time | Notes |
|-----------|:-------------:|-------|
| HuginnRetriever.retrieve() — ChromaDB | 200–500ms | Depends on collection size and hardware |
| HuginnRetriever.retrieve() — BM25 fallback | 5–50ms | Pure in-memory, very fast |
| CovePipeline Step 1 draft | 500ms–3s | Depends on router tier selected |
| CovePipeline Step 2 questions | 200ms–1s | Subconscious tier (Ollama) |
| CovePipeline Step 3 execute | 300ms–1.5s | Multiple MimirWell queries |
| CovePipeline Step 4 revise | 500ms–3s | Same tier as Step 1 |
| VordurChecker.extract_claims() | 200ms–800ms | Subconscious tier |
| VordurChecker verify (per claim) | 100ms–400ms | Subconscious NLI |
| VordurChecker verify (10 claims total) | 1s–4s | Parallel async calls |

**Total pipeline budget (medium complexity, no retry):**
- Best case (BM25 + fast model): ~3–5 seconds
- Typical case (ChromaDB + Ollama): ~6–10 seconds
- Worst case (with 1 retry): ~12–20 seconds

### Ingest Performance

| Metric | Value |
|--------|-------|
| Files processed | 57 knowledge files + 4 identity files |
| Chunks created | ~25 160 (BM25 flat index) |
| Ingest time (BM25 only) | ~5 seconds |
| Ingest time (ChromaDB + embedding model) | ~3–8 minutes first time (model download) |
| Subsequent ingests (embedding model cached) | ~30–90 seconds |
| Idempotency check | < 100ms (count query) |

---

## 15. Key Design Principles

1. **Ground Truth over Inference** — The knowledge database is always consulted.
   The model generates, it does not invent. Retrieval precedes generation.

2. **Graceful Degradation, Never Crash** — Every method returns a valid result.
   No exception propagates uncaught to the caller. Worst case: empty context,
   marginal score, canned response — the system keeps running.

3. **Self-Healing** — The health monitor detects corruption and triggers reindex
   automatically. Circuit breakers reset after cooldown without manual intervention.

4. **Privacy-First Judging** — The verification judge model is Ollama (local, private).
   Claims are never sent to cloud APIs for verification. Sigrid's conversations
   do not leak to external services for fact-checking.

5. **Voice Integrity** — VordurChecker scores and retries responses. It never edits
   or rewrites Sigrid's voice. The model writes; the Vörðr only scores.

6. **Typed API Communication** — All inter-module calls use typed request/response
   dataclasses (`FederatedMemoryRequest`, `RetrievalRequest`, `RetrievalResult`,
   `CoveResult`, `FaithfulnessScore`). No raw dicts between module boundaries.

7. **Singleton + StateBus Pattern** — Each module follows the established pattern:
   `init_X_from_config()`, `get_X()`, `get_state() → XState`, `publish(bus)`.
   All states visible to any subscriber via StateBus events.

---

*Document created: 2026-03-20*
*System: Ørlög Architecture — Viking Girlfriend Skill for OpenClaw*
*Author: Runa Gridweaver Freyjasdottir*
