# TASK: Mímir-Vörðr — The Warden of the Well
# Created: 2026-03-20
# Status: PLANNING → READY TO BUILD

## Vision

**Mímir-Vörðr** is a Multi-Domain RAG System with Integrated Verification.
It is the intelligence layer that makes Sigrid accurate without needing a larger
model. Smart memory utilization over horse-power.

Three Norse concepts form the system:

| Component | Norse Name | Function |
|-----------|-----------|----------|
| Knowledge database | Mímisbrunnr | The Ground Truth Well — 57 indexed knowledge files |
| Retrieval engine | Huginn's Ara | Flies out, retrieves, reranks, returns only the truth |
| Truth guard | Vörðr | Watches the output, scores faithfulness, blocks hallucinations |

---

## The Three-Stage Pipeline

```
User query
    │
    ▼
┌────────────────────────────────────────────────────────────────┐
│  STAGE I — RETRIEVAL (Huginn's Ara)                            │
│                                                                │
│  query → retrieve 50 chunks from Mímisbrunnr                  │
│        → rerank to top 3 (highest relevance + faithfulness)    │
│        → inject as "Ground Truth" context into prompt          │
└────────────────────────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────────────────────────┐
│  STAGE II — GENERATION & CoVe (model_router_client)            │
│                                                                │
│  Step 1: Draft initial response from retrieved context         │
│  Step 2: Plan verification questions ("Does the Well say X?")  │
│  Step 3: Execute questions against Mímisbrunnr                 │
│  Step 4: Revise final response based on verification findings  │
└────────────────────────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────────────────────────┐
│  STAGE III — TRUTH GUARD (Vörðr)                               │
│                                                                │
│  Extract factual claims from response                          │
│  Verify each claim against source chunks via Judge model       │
│  Compute Faithfulness Score (0.0–1.0)                          │
│  Score ≥ 0.8 → pass through                                    │
│  Score 0.5–0.79 → append marginal warning, log                 │
│  Score < 0.5 → discard, re-run retrieval (max 2 retries)       │
└────────────────────────────────────────────────────────────────┘
    │
    ▼
Final response → memory_store.record_turn()
```

---

## Module Inventory (4 new files)

### 1. `viking_girlfriend_skill/scripts/mimir_well.py` — Mímisbrunnr

The deep knowledge store. Indexes the 57 knowledge_reference/ files plus the
identity anchor files (core_identity.md, SOUL.md, values.json) into ChromaDB
with a three-level hierarchy.

**Hierarchy levels:**
```
Level 1 — Raw      : Individual document chunks (512 tokens max)
Level 2 — Cluster  : Domain thematic summaries (Norse / Coding / AI / Spirit / Social)
Level 3 — Axiom    : Sigrid's non-negotiable core truths (identity + values)
```

**Domains (metadata filter key):**
```
norse_spirituality    freyjas_aett, tyrs_aett, heimdalls_aett, rune_poems,
                      voluspa, galdrabok, trolldom, heathen_path
norse_culture         viking_history, culture, social_protocols, honor,
                      frith, sexuality, cities, geography
norse_mythology       gods, goddesses, eddas, cosmology
coding                ai_python_guides, artificial_intelligence,
                      software_engineering, data_science, cybersecurity,
                      system_administration
character             core_identity, SOUL, values, emotional_expressions,
                      agents, identity
roleplay              bondmaids, viking_roleplay, gm_mindset, conversations
```

**Key classes:**
```python
@dataclass
class KnowledgeChunk:
    chunk_id: str          # uuid
    text: str              # raw chunk text (≤512 tokens)
    source_file: str       # relative path in knowledge_reference/
    domain: str            # see domain table above
    level: int             # 1=raw, 2=cluster, 3=axiom
    metadata: Dict[str, Any]

@dataclass
class RetrievalPacket:
    query: str
    chunks: List[KnowledgeChunk]   # reranked top-N
    domain_filter: Optional[str]
    retrieval_time_ms: float

class MimirWell:
    def ingest_all(self, data_root: Path) -> int
        # Loads all knowledge_reference/ files + identity files
        # Chunks them, embeds, stores in ChromaDB collection "mimir_well"
        # Returns number of chunks ingested
    def retrieve(self, query: str, n: int = 50,
                 domain: Optional[str] = None) -> List[KnowledgeChunk]
        # Semantic search — optional domain pre-filter (metadata)
        # Returns n candidates sorted by similarity
    def rerank(self, query: str, chunks: List[KnowledgeChunk],
               n: int = 3) -> List[KnowledgeChunk]
        # Scores by: ChromaDB similarity + keyword overlap (BM25-inspired)
        # Returns top-n most faithful chunks
    def get_axioms(self) -> List[KnowledgeChunk]
        # Returns all level=3 chunks (Sigrid's core truths)
        # Used by Vörðr for persona consistency check
    def get_context_string(self, chunks: List[KnowledgeChunk]) -> str
        # Formats chunks as numbered "Ground Truth" citations
    def get_state(self) -> MimirState
    def publish(self, bus: StateBus) -> None
```

**Chunking strategy:**
- JSON/JSONL: split by record, max 512 tokens per chunk
- Markdown: split by `##` heading, then by 512 tokens if needed
- YAML: split by top-level key
- Each chunk stores its source + position metadata

**Collection name:** `mimir_well` (separate from `sigrid_episodic`)

---

### 2. `viking_girlfriend_skill/scripts/vordur.py` — The Vörðr

The Warden. Extracts claims from a response and verifies each against the
retrieved source chunks using the subconscious (Ollama) as Judge model.

**Key classes:**
```python
@dataclass
class Claim:
    text: str              # one extracted factual claim
    source_sentence: str   # the sentence in the response it came from

@dataclass(frozen=True)
class Verdict:
    ENTAILED    = "entailed"     # source logically supports the claim
    NEUTRAL     = "neutral"      # source neither supports nor contradicts
    CONTRADICTED = "contradicted" # source directly contradicts the claim

@dataclass
class ClaimVerification:
    claim: Claim
    verdict: Verdict
    confidence: float      # 0.0–1.0
    supporting_chunk_id: Optional[str]  # chunk that provided the verdict

@dataclass
class FaithfulnessScore:
    score: float           # 0.0–1.0 weighted average
    tier: str              # "high" | "marginal" | "hallucination"
    claim_count: int
    entailed_count: int
    neutral_count: int
    contradicted_count: int
    verifications: List[ClaimVerification]
    needs_retry: bool      # True if score < low_threshold

class VordurChecker:
    # Thresholds (configurable)
    high_threshold: float = 0.80
    marginal_threshold: float = 0.50
    # low < marginal = hallucination alert → retry

    def extract_claims(self, response: str) -> List[Claim]
        # Uses subconscious tier: "Extract factual claims as a bullet list"
        # Returns List[Claim] (one per sentence with a verifiable assertion)
    def verify_claim(self, claim: Claim,
                     source_chunks: List[KnowledgeChunk]) -> ClaimVerification
        # Uses subconscious tier: structured prompt asking for
        # ENTAILED / NEUTRAL / CONTRADICTED + one-line reason
        # Prompt: "Source: {chunk}. Claim: {claim}. Does the source entail,
        #          contradict, or is neutral toward this claim? Answer in one
        #          word: ENTAILED, NEUTRAL, or CONTRADICTED."
    def score(self, response: str,
              source_chunks: List[KnowledgeChunk]) -> FaithfulnessScore
        # Runs extract_claims → verify_claim for each
        # Computes weighted score: entailed=1.0, neutral=0.5, contradicted=0.0
    def persona_check(self, response: str,
                      axioms: List[KnowledgeChunk]) -> bool
        # Pure regex: checks for known persona violations
        # (wrong gender, denying Norse identity, claiming to be ChatGPT/Claude, etc.)
        # Returns True if persona is intact
    def get_state(self) -> VordurState
    def publish(self, bus: StateBus) -> None
```

**Judge model:** TIER_SUBCONSCIOUS (Ollama llama3) — cheap, local, private.
Falls back to a lightweight TIER_CONSCIOUS call if Ollama is unreachable.

---

### 3. `viking_girlfriend_skill/scripts/huginn.py` — Huginn's Ara

The retrieval orchestrator. Sits between the query and the model call.
Knows which domain to search, retrieves, reranks, and returns ready-to-inject
context.

```python
@dataclass
class RetrievalResult:
    query: str
    domain: Optional[str]        # detected or explicit
    chunks: List[KnowledgeChunk] # top-3 reranked
    context_string: str          # formatted for prompt injection
    retrieval_ms: float

class HuginnRetriever:
    def detect_domain(self, query: str) -> Optional[str]
        # Lightweight keyword→domain mapping
        # "rune", "odin", "futhark" → "norse_spirituality"
        # "python", "code", "function" → "coding"
        # "values", "honor", "soul" → "character"
        # None → no pre-filter (search all)
    def retrieve(self, query: str,
                 n_initial: int = 50,
                 n_final: int = 3,
                 domain: Optional[str] = None) -> RetrievalResult
        # detect_domain() if domain not explicit
        # mimir_well.retrieve(query, n=n_initial, domain=domain)
        # mimir_well.rerank(query, chunks, n=n_final)
        # returns formatted RetrievalResult
    def get_state(self) -> HuginnState
    def publish(self, bus: StateBus) -> None
```

---

### 4. `viking_girlfriend_skill/scripts/cove_pipeline.py` — Chain-of-Verification

The four-prompt CoVe pipeline. Only runs for high or medium complexity requests
(would be wasteful on greetings). Activated when `use_cove=True` in config.

```python
@dataclass
class CoveResult:
    draft: str                    # Step 1 output
    verification_questions: List[str]  # Step 2 output
    qa_pairs: List[Tuple[str, str]]    # (question, answer from Well)
    final_response: str           # Step 4 output
    faithfulness_score: Optional[FaithfulnessScore]
    used_cove: bool               # False if skipped (low complexity)

class CovePipeline:
    def run(self, query: str, context: str,
            retrieval: RetrievalResult,
            complexity: ComplexityLevel) -> CoveResult
        # Step 1: draft(query, context) → using chosen tier
        # Step 2: plan_questions(draft, context) → using subconscious
        #   Prompt: "Given this draft response and source, write 3
        #            verification questions to check factual accuracy."
        # Step 3: execute_questions(questions, mimir_well) → subconscious
        #   Each question answered by retrieving from MimirWell
        # Step 4: revise(draft, qa_pairs) → using chosen tier
        #   Prompt: "Revise your draft using these verified Q&A pairs.
        #            Stay faithful to the source."
        # Only runs Steps 2-4 if complexity in ("medium", "high")
        # Low complexity → returns draft directly (skip CoVe)
```

---

## Integration Changes to Existing Modules

### `memory_store.py` — add knowledge-augmented retrieval

```python
def get_context_with_knowledge(
    self,
    query: str,
    huginn: Optional[HuginnRetriever] = None,
) -> str:
    """Returns combined episodic memory context + knowledge context."""
    episodic_ctx = self.get_context(query)    # existing
    if huginn is not None:
        retrieval = huginn.retrieve(query)
        return episodic_ctx + "\n\n" + retrieval.context_string
    return episodic_ctx
```

### `model_router_client.py` — add `smart_complete_with_cove()`

```python
def smart_complete_with_cove(
    self,
    messages: List[Message],
    huginn: Optional[HuginnRetriever] = None,
    vordur: Optional[VordurChecker] = None,
    cove: Optional[CovePipeline] = None,
    fallback: bool = True,
    **kwargs: Any,
) -> CompletionResponse:
    """
    Full Mímir-Vörðr pipeline:
      1. Detect complexity + coding intent (existing)
      2. Huginn retrieves Ground Truth context (if huginn provided)
      3. CoVe pipeline: draft → verify → revise (if cove provided)
      4. Vörðr scores faithfulness (if vordur provided)
      5. Retry if score < low_threshold (max 2 retries)
      6. Return final CompletionResponse with faithfulness_score attached
    """
```

**CompletionResponse gains:**
```python
faithfulness_score: Optional[float] = None
faithfulness_tier: str = ""         # "high" | "marginal" | "hallucination" | ""
cove_applied: bool = False
retrieval_domain: str = ""
retry_count: int = 0
```

### `main.py` — wire Mímir-Vörðr into `_handle_turn()`

```python
# New singletons initialized in _init_all_modules():
mimir_well     = init_mimir_well_from_config(config)
huginn         = init_huginn_from_config(config)
vordur         = init_vordur_from_config(config)
cove           = init_cove_pipeline_from_config(config)

# In _handle_turn(), Step 9 becomes:
result = router.smart_complete_with_cove(
    messages,
    huginn=huginn,
    vordur=vordur,
    cove=cove,
    fallback=True,
)
```

---

## Faithfulness Score Thresholds

| Score | Tier | Action |
|-------|------|--------|
| 0.8 – 1.0 | high | Pass through. Log score. |
| 0.5 – 0.79 | marginal | Pass through. Log + append `[Sigrid adds silently: I may be less certain here.]` to internal metadata (not shown to user) |
| < 0.5 | hallucination | Discard. Re-run retrieval with expanded n_initial. Max 2 retries. If still failing, respond with graceful "I'm not certain — let me draw from the Well again." |

---

## RAGAS-inspired Metrics (stored in VordurState)

| Metric | Definition |
|--------|-----------|
| **Faithfulness** | fraction of claims entailed by source chunks |
| **Answer Relevance** | cosine similarity between response embedding and query embedding |
| **Context Precision** | fraction of retrieved chunks that were actually cited |

---

## Knowledge Graph (Phase 2 Enhancement)

Phase 1 uses flat ChromaDB retrieval with metadata filtering.
Phase 2 adds a JSON relationship graph for key Norse concepts:

```json
{
  "Thurisaz": {
    "related": ["Thor", "protection", "power", "threshold"],
    "aett": "Heimdall",
    "type": "rune"
  },
  "Uruz": {
    "related": ["strength", "vitality", "wild_ox", "endurance"],
    "aett": "Freyja",
    "type": "rune"
  }
}
```

When querying about "Thurisaz", the graph expands the query to also retrieve
chunks about Thor, protection, and threshold — before semantic search.

---

## Implementation Order

| Step | Module | Depends On | Deliverable |
|------|--------|-----------|-------------|
| 1 | `mimir_well.py` | config_loader, state_bus, chromadb | MimirWell + ingestion of all 57 files |
| 2 | `vordur.py` | mimir_well, model_router_client (subconscious) | VordurChecker + faithfulness scoring |
| 3 | `huginn.py` | mimir_well | HuginnRetriever + domain detection |
| 4 | `cove_pipeline.py` | huginn, model_router_client | CoVe 4-step pipeline |
| 5 | Extend `memory_store.py` | huginn | get_context_with_knowledge() |
| 6 | Extend `model_router_client.py` | vordur, huginn, cove | smart_complete_with_cove() |
| 7 | Extend `main.py` | all above | full pipeline wired |
| 8 | `tests/test_mimirvordur.py` | all above | 40+ test cases |
| 9 | Extend `ops/launch_calibration.py` | new modules | import + init checks |

---

## Configuration Block (added to base config)

```yaml
mimir_well:
  collection_name: mimir_well        # ChromaDB collection
  persist_dir: data/chromadb_mimir   # separate from episodic store
  chunk_size_tokens: 512
  chunk_overlap_tokens: 64
  n_retrieve: 50                     # candidates before rerank
  n_final: 3                         # chunks kept after rerank
  auto_ingest: true                  # ingest on first startup if collection empty

huginn:
  n_initial: 50
  n_final: 3
  domain_detection: true

vordur:
  enabled: true
  high_threshold: 0.80
  marginal_threshold: 0.50
  persona_check: true
  judge_tier: subconscious           # which tier acts as the Critic

cove_pipeline:
  enabled: true
  min_complexity: medium             # skip CoVe for low complexity
  n_verification_questions: 3
```

---

## Test Coverage Plan (`tests/test_mimirvordur.py`)

```
T01  MimirWell ingest — loads knowledge_reference/ without error
T02  MimirWell retrieve — returns KnowledgeChunks for a Norse query
T03  MimirWell rerank — reduces 50 candidates to 3
T04  MimirWell domain filter — "rune" query stays in norse_spirituality domain
T05  MimirWell get_axioms — returns level=3 chunks
T06  MimirWell context_string — formats chunks with citation numbers
T07  VordurChecker extract_claims — mocked subconscious, returns Claim list
T08  VordurChecker verify_claim ENTAILED — mocked verdict
T09  VordurChecker verify_claim CONTRADICTED — score impact
T10  VordurChecker score high — response faithful to source → ≥ 0.80
T11  VordurChecker score low — response contradicts source → < 0.50
T12  VordurChecker persona_check — blocks "I am ChatGPT" claim
T13  VordurChecker faithfulness tier labels
T14  HuginnRetriever domain_detection — Norse keywords → norse_spirituality
T15  HuginnRetriever domain_detection — coding keywords → coding
T16  HuginnRetriever domain_detection — no match → None (global search)
T17  HuginnRetriever retrieve — returns RetrievalResult with chunks
T18  HuginnRetriever context_string in result
T19  CovePipeline run low complexity → skips CoVe, returns draft directly
T20  CovePipeline run medium complexity → full 4-step (mocked LLM)
T21  CovePipeline verification questions generated
T22  CovePipeline revise incorporates qa_pairs
T23  ModelRouterClient.smart_complete_with_cove → faithfulness_score attached
T24  ModelRouterClient retry on hallucination → retry_count incremented
T25  ModelRouterClient faithfulness_tier in response
T26  MemoryStore.get_context_with_knowledge → merges episodic + knowledge
T27  Full pipeline: query → huginn → cove → vordur → response with score
T28  Full pipeline: hallucination detected → retry → score improves
T29  Full pipeline: Ollama down → vordur falls back to conscious tier
T30  Full pipeline: huginn unavailable → graceful degradation (no crash)
```

---

## Key Design Constraints

- MimirWell ingestion is idempotent — safe to call on every startup
- VordurChecker NEVER modifies Sigrid's voice — only scores and retries
- CoVe always uses the same tier as the original router selection
- Max 2 Vörðr retries per response — never infinite loops
- All new modules follow the existing pattern:
  `init_X_from_config()` singleton, `get_state() → XState`, `publish(bus)`
- CompletionResponse gains optional faithfulness fields — backward compatible
  (existing callers unaffected)
- Judge model (subconscious/Ollama) prompts must work with llama3 8B
  — keep prompts short, structured, single-word-answer format

---

## Session Resume Instructions

On session start: read this file → check Implementation Order table →
pick the next module not yet marked DONE → read the relevant existing modules
(config_loader, memory_store, model_router_client for API patterns) →
plan → report → code one module at a time → test → commit → proceed.

Start with: `mimir_well.py`
