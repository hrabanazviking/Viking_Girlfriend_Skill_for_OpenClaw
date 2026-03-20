# TASK: Mímir-Vörðr — The Warden of the Well
# Created: 2026-03-20
# Revised: 2026-03-20 (10x Robustness Edition)
# Status: PLANNING COMPLETE → READY TO BUILD

---

## Vision

**Mímir-Vörðr** is a Multi-Domain RAG System with Integrated Verification.
It is the intelligence layer that makes Sigrid accurate without needing a larger model.
Smart memory over horse-power. Ground truth over guesswork.

Three Norse concepts form the system's soul:

| Component | Norse Name | Function |
|-----------|-----------|----------|
| Knowledge database | Mímisbrunnr | The Ground Truth Well — 57 indexed knowledge files |
| Retrieval engine | Huginn's Ara | Flies out, retrieves, reranks, returns only truth |
| Truth guard | Vörðr | Watches the output, scores faithfulness, blocks hallucinations |

And one cross-cutting infrastructure layer:

| Component | Name | Function |
|-----------|------|----------|
| Resilience layer | Norns' Shield | Circuit breakers, retry engines, fallback chains, health monitor |

**Design philosophy:**
- Every single failure mode has a recovery path. No exception propagates uncaught.
- Every component degrades gracefully — the system never crashes, only steps down.
- Self-healing: corrupted state is detected and repaired without human intervention.
- Deep memory federation: all four memory tiers (conversation buffer, episodic JSON,
  ChromaDB episodic, ChromaDB knowledge) are unified behind one retrieval interface.
- API-style internal communication: all inter-module calls use typed request/response
  objects, never raw dicts, never global mutable state.

---

## The Three-Stage Pipeline

```
User query
    │
    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  STAGE 0 — HEALTH CHECK (MimirHealthMonitor, background daemon)        │
│                                                                        │
│  Continuously monitors all Mímir-Vörðr subsystems                     │
│  Detects: ChromaDB corruption, Ollama down, LiteLLM unreachable        │
│  Triggers: auto-reindex, circuit-breaker trips, fallback mode switch   │
│  Publishes: MimirHealthState to StateBus every 60s                     │
└────────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  STAGE I — RETRIEVAL (Huginn's Ara — HuginnRetriever)                  │
│                                                                        │
│  query → detect domain (keyword map, no model call)                    │
│        → query graph expansion (Norse concept graph, Phase 2)          │
│        → PRIMARY: retrieve 50 chunks from MimirWell (ChromaDB)        │
│          FALLBACK A: in-memory BM25 keyword search (if ChromaDB down)  │
│          FALLBACK B: episodic memory only (if BM25 also empty)         │
│          FALLBACK C: empty context (no Ground Truth — log + continue)  │
│        → SIMULTANEOUS: retrieve episodic context from MemoryStore      │
│        → rerank 50 → 3 (similarity + keyword overlap scoring)          │
│        → inject as "Ground Truth" context into prompt                  │
│  Circuit breaker: open after 3 consecutive failures, 30s cooldown      │
│  Retry: exponential backoff with jitter (0.5s base, ×2, max 4s)        │
└────────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  STAGE II — GENERATION & CoVe (CovePipeline)                           │
│                                                                        │
│  Step 1: draft(query, context) → chosen tier (router selects)          │
│    FALLBACK: if tier fails → escalate to next tier in chain            │
│  Step 2: plan_questions(draft, context) → subconscious tier            │
│    FALLBACK: template verification questions (static, no model call)   │
│    CHECKPOINT: Step 2 result saved to CoveCheckpoint before Step 3     │
│  Step 3: execute_questions(questions, mimir_well) → subconscious tier  │
│    FALLBACK: skip Step 3 (pass Step 2 questions unanswered)            │
│    CHECKPOINT: Step 3 result saved before Step 4                       │
│  Step 4: revise(draft, qa_pairs) → chosen tier                         │
│    FALLBACK: return Step 1 draft unchanged                             │
│  CoVe circuit breaker: if CoVe fails 3× → bypass CoVe entirely        │
│  Only runs for medium/high complexity — low gets Step 1 only           │
└────────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  STAGE III — TRUTH GUARD (Vörðr — VordurChecker)                       │
│                                                                        │
│  Extract factual claims from response                                  │
│    FALLBACK: sentence splitter (regex, no model)                       │
│  Verify each claim against source chunks via Judge model               │
│    PRIMARY: subconscious (Ollama llama3) — NLI structured prompt       │
│    FALLBACK A: conscious tier (if Ollama down)                         │
│    FALLBACK B: regex heuristic scorer (if both models down)            │
│    FALLBACK C: pass-through at 0.5 (marginal) if all else fails       │
│  Compute Faithfulness Score (0.0–1.0)                                  │
│  Cross-check persona: axiom guard + trust_engine + ethics alignment    │
│  Score ≥ 0.8 → pass through (high)                                     │
│  Score 0.5–0.79 → pass through (marginal), log to VördurLog           │
│  Score < 0.5 → discard, send to DeadLetterStore, retry (max 2×)       │
│  Circuit breaker: open after 5 failures, 60s cooldown                  │
│  Dead letter store: failed responses logged with full trace             │
└────────────────────────────────────────────────────────────────────────┘
    │
    ▼
Final response → memory_store.record_turn() → StateBus publish
```

---

## Error Taxonomy — Unified Exception Hierarchy

All Mímir-Vörðr exceptions inherit from `MimirVordurError`. Never let raw Python
exceptions escape a module boundary.

```python
class MimirVordurError(Exception):
    """Base class for all Mímir-Vörðr errors."""
    pass

# --- Retrieval errors ---
class MimirWellError(MimirVordurError): pass
class ChromaDBUnavailableError(MimirWellError): pass
class ChromaDBCorruptionError(MimirWellError): pass
class IngestError(MimirWellError): pass
class RetrievalTimeoutError(MimirWellError): pass

# --- Retrieval orchestrator errors ---
class HuginnError(MimirVordurError): pass
class HuginnRetrievalFailedError(HuginnError): pass
class HuginnAllFallbacksExhaustedError(HuginnError): pass

# --- Verification errors ---
class VordurError(MimirVordurError): pass
class ClaimExtractionError(VordurError): pass
class VerificationTimeoutError(VordurError): pass
class JudgeModelUnavailableError(VordurError): pass
class PersonaViolationError(VordurError): pass

# --- Pipeline errors ---
class CovePipelineError(MimirVordurError): pass
class CoveStepFailedError(CovePipelineError):
    def __init__(self, step: int, reason: str): ...
class CoveAllFallbacksExhaustedError(CovePipelineError): pass

# --- Infrastructure errors ---
class CircuitBreakerOpenError(MimirVordurError):
    def __init__(self, component: str, cooldown_remaining_s: float): ...
class HealthMonitorError(MimirVordurError): pass
```

---

## Cross-Cutting Resilience Infrastructure

### `_MimirCircuitBreaker` — shared, per-component instance

```python
@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 3      # failures before opening
    success_threshold: int = 2      # successes to close (half-open state)
    cooldown_s: float = 30.0        # seconds before retry after open
    timeout_s: float = 10.0         # per-call timeout

class CircuitBreakerState(Enum):
    CLOSED = "closed"       # normal operation
    OPEN = "open"           # failing — reject calls immediately
    HALF_OPEN = "half_open" # probing — allow one call through

class _MimirCircuitBreaker:
    """
    Three-state circuit breaker. Thread-safe with asyncio.Lock.
    Each Mímir-Vörðr component owns its own instance.

    Usage:
        async with breaker.guard("component_name"):
            result = await risky_operation()
    """
    def __init__(self, name: str, config: CircuitBreakerConfig): ...
    async def guard(self, operation_name: str) -> AsyncContextManager: ...
    def get_state(self) -> CircuitBreakerState: ...
    def get_failure_count(self) -> int: ...
    def reset(self) -> None: ...
    def to_dict(self) -> Dict[str, Any]: ...
```

Circuit breaker assignments:
| Component | Breaker name | failure_threshold | cooldown_s |
|-----------|-------------|-------------------|------------|
| MimirWell ChromaDB reads | `mimir_chromadb_read` | 3 | 30 |
| MimirWell ChromaDB writes | `mimir_chromadb_write` | 3 | 60 |
| Vörðr subconscious Judge | `vordur_judge_subconscious` | 5 | 60 |
| Vörðr conscious fallback | `vordur_judge_conscious` | 3 | 30 |
| HuginnRetriever full pipeline | `huginn_full` | 3 | 30 |
| CovePipeline Step 2 | `cove_step2` | 3 | 30 |
| CovePipeline Step 3 | `cove_step3` | 3 | 30 |
| CovePipeline Step 4 | `cove_step4` | 3 | 30 |
| CovePipeline entire pipeline | `cove_pipeline` | 3 | 120 |

### `_RetryEngine` — jittered exponential backoff

```python
@dataclass
class RetryConfig:
    max_attempts: int = 3
    base_delay_s: float = 0.5
    backoff_factor: float = 2.0
    max_delay_s: float = 8.0
    jitter: bool = True             # adds random ±20% to delay

class _RetryEngine:
    """
    Wraps any coroutine with retry + backoff.
    Does NOT retry on CircuitBreakerOpenError or PersonaViolationError
    (these are not transient failures).

    Usage:
        result = await retry.run(risky_coroutine, arg1, arg2)
    """
    def __init__(self, config: RetryConfig, logger: logging.Logger): ...
    async def run(
        self,
        fn: Callable[..., Awaitable[T]],
        *args: Any,
        non_retriable: Tuple[Type[Exception], ...] = (),
        **kwargs: Any,
    ) -> T: ...
```

### `_DeadLetterStore` — failed verification log

```python
@dataclass
class DeadLetterEntry:
    entry_id: str               # uuid
    timestamp: str              # ISO-8601
    component: str              # "vordur" | "cove" | "huginn"
    query: str                  # original user query
    response: str               # response that failed verification
    faithfulness_score: float
    error_type: str             # exception class name
    retry_count: int
    trace: str                  # full traceback
    context_chunks: List[str]   # chunk IDs that were retrieved

class _DeadLetterStore:
    """
    Append-only JSONL log at session/dead_letters.jsonl.
    Thread-safe. Never raises (failures are silently logged).
    Provides summary stats for health monitor.
    """
    def __init__(self, path: Path): ...
    def append(self, entry: DeadLetterEntry) -> None: ...
    def count_recent(self, window_s: float = 300.0) -> int: ...
    def get_last_n(self, n: int = 10) -> List[DeadLetterEntry]: ...
```

### `MimirHealthMonitor` — background watchdog

```python
@dataclass
class ComponentHealth:
    name: str
    status: str             # "healthy" | "degraded" | "down"
    circuit_breaker_state: str
    last_success_at: Optional[str]
    last_failure_at: Optional[str]
    failure_rate_5m: float  # failures per minute over last 5 min
    dead_letters_5m: int    # dead letter entries in last 5 min

@dataclass
class MimirHealthState:
    overall: str                        # "healthy" | "degraded" | "critical"
    components: Dict[str, ComponentHealth]
    dead_letters_total: int
    last_reindex_at: Optional[str]
    reindex_count: int
    checked_at: str                     # ISO-8601

class MimirHealthMonitor:
    """
    APScheduler-backed background daemon.
    Runs health_check() every 60 seconds.
    Runs full_diagnostics() every 10 minutes.

    Health checks:
      - ChromaDB: attempt a count() query
      - Ollama: socket ping localhost:11434
      - LiteLLM: socket ping localhost:4000
      - Dead letter rate: if >5 in last 5min → raise alert to log
      - Collection integrity: verify mimir_well collection has expected doc count

    Self-healing actions:
      - If ChromaDB mimir_well returns 0 docs (or corruption detected):
          → trigger MimirWell.reindex() automatically
      - If circuit breaker is stuck open >5min:
          → attempt half-open probe, log result
      - If dead_letters_5m > 10:
          → emit CRITICAL log + publish alert to StateBus
    """
    def __init__(
        self,
        mimir_well: "MimirWell",
        vordur: "VordurChecker",
        huginn: "HuginnRetriever",
        cove: "CovePipeline",
        dead_letter_store: "_DeadLetterStore",
        bus: StateBus,
        scheduler: BackgroundScheduler,
    ): ...
    def start(self) -> None: ...
    def stop(self) -> None: ...
    def get_state(self) -> MimirHealthState: ...
    def publish(self, bus: StateBus) -> None: ...
    def trigger_reindex(self) -> None: ...  # can be called manually too
```

---

## Module Specifications (10x Robustness Edition)

---

### 1. `viking_girlfriend_skill/scripts/mimir_well.py` — Mímisbrunnr

The deep knowledge store. Indexes 57 knowledge_reference/ files plus identity anchor
files (core_identity.md, SOUL.md, values.json) into ChromaDB with three-level hierarchy.

#### Data Structures

```python
@dataclass
class KnowledgeChunk:
    chunk_id: str          # uuid4
    text: str              # raw chunk text (≤512 tokens)
    source_file: str       # relative path in knowledge_reference/
    domain: str            # see domain map
    level: int             # 1=raw, 2=cluster, 3=axiom
    metadata: Dict[str, Any]   # position, heading, file_type, etc.

@dataclass
class RetrievalPacket:
    query: str
    chunks: List[KnowledgeChunk]    # reranked top-N
    domain_filter: Optional[str]
    retrieval_time_ms: float
    fallback_used: str              # "chromadb" | "bm25" | "episodic" | "empty"

@dataclass
class IngestReport:
    files_processed: int
    chunks_created: int
    chunks_skipped: int
    errors: List[str]           # non-fatal errors encountered during ingest
    duration_s: float

@dataclass
class MimirState:
    collection_name: str
    document_count: int
    domain_counts: Dict[str, int]
    last_ingest_at: Optional[str]
    ingest_count: int
    is_healthy: bool
    chromadb_status: str        # "ok" | "degraded" | "down"
    fallback_mode: str          # "chromadb" | "bm25" | "empty"
    circuit_breaker_read: str
    circuit_breaker_write: str
```

#### Domain Map

```
norse_spirituality  : freyjas_aett, tyrs_aett, heimdalls_aett, rune_poems,
                      voluspa, galdrabok, trolldom, heathen_path
norse_culture       : viking_history, culture, social_protocols, honor,
                      frith, sexuality, cities, geography
norse_mythology     : gods, goddesses, eddas, cosmology
coding              : ai_python_guides, artificial_intelligence,
                      software_engineering, data_science, cybersecurity,
                      system_administration
character           : core_identity, SOUL, values, emotional_expressions,
                      agents, identity
roleplay            : bondmaids, viking_roleplay, gm_mindset, conversations
```

#### Hierarchy Levels

```
Level 1 — Raw    : Individual document chunks (512 tokens max, 64 token overlap)
Level 2 — Cluster: Domain thematic summaries (generated at ingest time)
Level 3 — Axiom  : Sigrid's non-negotiable core truths (identity + values files only)
```

#### Class Interface

```python
class MimirWell:
    # --- Init ---
    def __init__(
        self,
        collection_name: str = "mimir_well",
        persist_dir: str = "data/chromadb_mimir",
        chunk_size_tokens: int = 512,
        chunk_overlap_tokens: int = 64,
        n_retrieve: int = 50,
        n_final: int = 3,
    ): ...

    # --- Ingest ---
    def ingest_all(self, data_root: Path, force: bool = False) -> IngestReport:
        """
        Idempotent — checks if collection already has documents.
        If force=True → drops collection and rebuilds from scratch.
        Recovers from partial ingest: uses a .ingest_lock file to detect
        interrupted ingests and re-runs from scratch if lock found.
        Each file ingest is wrapped in try/except — one bad file does not
        stop the entire run. All errors collected in IngestReport.errors.
        Chunks from the 5 identity files are tagged level=3 (axiom).
        """

    def reindex(self) -> IngestReport:
        """Force full reindex (called by health monitor on corruption)."""

    # --- Retrieval (primary) ---
    def retrieve(
        self,
        query: str,
        n: int = 50,
        domain: Optional[str] = None,
        timeout_s: float = 5.0,
    ) -> List[KnowledgeChunk]:
        """
        ChromaDB semantic search with optional domain metadata filter.
        Protected by _chromadb_read circuit breaker + _RetryEngine (3 attempts).
        On CircuitBreakerOpenError → falls back to _bm25_retrieve().
        On timeout → falls back to _bm25_retrieve().
        Never raises — always returns a list (possibly empty).
        """

    def _bm25_retrieve(self, query: str, n: int) -> List[KnowledgeChunk]:
        """
        In-memory BM25 keyword search over cached flat text index.
        _flat_index is built at ingest time and kept in memory.
        If _flat_index is empty → returns [].
        This is Fallback A — no ChromaDB required.
        """

    def rerank(
        self,
        query: str,
        chunks: List[KnowledgeChunk],
        n: int = 3,
    ) -> List[KnowledgeChunk]:
        """
        Hybrid scoring: ChromaDB cosine similarity score + BM25 keyword overlap.
        Scoring formula: 0.7 * semantic_score + 0.3 * keyword_overlap
        On empty input → returns [].
        Pure Python — never raises.
        """

    def get_axioms(self) -> List[KnowledgeChunk]:
        """
        Returns all level=3 chunks (Sigrid's core truths).
        Falls back to _bm25_retrieve("core identity values soul") if ChromaDB down.
        Used by Vörðr for persona consistency check.
        Always returns a list (never raises).
        """

    def get_context_string(self, chunks: List[KnowledgeChunk]) -> str:
        """Formats chunks as numbered [GT-1] ... [GT-3] Ground Truth citations."""

    def get_state(self) -> MimirState: ...
    def publish(self, bus: StateBus) -> None: ...
```

#### Chunking Strategy

| File type | Strategy |
|-----------|----------|
| Markdown (.md) | Split by `##` heading → then by 512 tokens if needed |
| JSON (.json) | Split by top-level key or array element |
| JSONL (.jsonl) | One chunk per line |
| YAML (.yaml) | Split by top-level key |
| TXT (.txt) | Split by paragraph (blank line), then by 512 tokens |
| CSV (.csv) | Split by 20 rows per chunk |

Each chunk includes metadata: `{"source_file": ..., "position": N, "heading": ..., "file_type": ...}`

---

### 2. `viking_girlfriend_skill/scripts/vordur.py` — The Vörðr

The Warden of the Gate. Extracts claims, verifies each against Ground Truth,
cross-checks persona consistency against trust_engine + ethics alignment,
never lets a hallucination through unchallenged.

#### Data Structures

```python
@dataclass
class Claim:
    text: str               # one extracted factual claim
    source_sentence: str    # the sentence in the response it came from
    claim_index: int        # position in the claim list

class VerdictLabel(str, Enum):
    ENTAILED     = "entailed"
    NEUTRAL      = "neutral"
    CONTRADICTED = "contradicted"
    UNCERTAIN    = "uncertain"   # returned when Judge model gives garbled output

@dataclass
class ClaimVerification:
    claim: Claim
    verdict: VerdictLabel
    confidence: float               # 0.0–1.0
    supporting_chunk_id: Optional[str]
    judge_tier_used: str            # "subconscious" | "conscious" | "regex" | "passthrough"
    verification_ms: float

@dataclass
class FaithfulnessScore:
    score: float            # 0.0–1.0 weighted average
    tier: str               # "high" | "marginal" | "hallucination"
    claim_count: int
    entailed_count: int
    neutral_count: int
    contradicted_count: int
    uncertain_count: int
    verifications: List[ClaimVerification]
    needs_retry: bool
    persona_intact: bool
    ethics_alignment: Optional[float]   # from ethics module, if available
    trust_score: Optional[float]        # from trust_engine, if available

@dataclass
class VordurState:
    enabled: bool
    total_responses_scored: int
    total_retries_issued: int
    total_dead_letters: int
    recent_avg_score: float             # rolling average over last 20 responses
    circuit_breaker_subconscious: str
    circuit_breaker_conscious: str
    last_scored_at: Optional[str]
    persona_violations_caught: int
```

#### Judge Model Prompt (must work with llama3 8B)

```
System: You are a factual consistency checker. Answer only with one word.
User:
Source: {chunk_text}
Claim: {claim_text}
Does the source logically entail, contradict, or is it neutral toward this claim?
Answer with exactly one word: ENTAILED, CONTRADICTED, or NEUTRAL.
```

Response parsing: take the first word of the response, uppercase, match against
{ENTAILED, CONTRADICTED, NEUTRAL}. Anything else → VerdictLabel.UNCERTAIN (score 0.5).

#### Faithfulness Scoring Weights

```
ENTAILED     → 1.0
NEUTRAL      → 0.5
CONTRADICTED → 0.0
UNCERTAIN    → 0.5
```

Score = mean of all claim weights.

#### Class Interface

```python
class VordurChecker:
    def __init__(
        self,
        high_threshold: float = 0.80,
        marginal_threshold: float = 0.50,
        persona_check_enabled: bool = True,
        judge_tier: str = "subconscious",
        max_claims: int = 10,       # cap to avoid runaway verification
        verification_timeout_s: float = 8.0,
    ): ...

    def extract_claims(self, response: str) -> List[Claim]:
        """
        PRIMARY: subconscious tier — prompt: "Extract factual claims as a
        numbered list. One claim per line. Only verifiable assertions."
        FALLBACK: sentence splitter (regex — splits on '. ', '! ', '? ')
        On empty response → returns []
        Never raises.
        """

    def verify_claim(
        self,
        claim: Claim,
        source_chunks: List[KnowledgeChunk],
        timeout_s: float = 8.0,
    ) -> ClaimVerification:
        """
        PRIMARY: subconscious (Ollama) — NLI structured prompt
        FALLBACK A: conscious tier (if Ollama circuit breaker open)
        FALLBACK B: regex heuristic (keyword overlap between claim and chunk)
        FALLBACK C: VerdictLabel.UNCERTAIN at 0.5 (pass-through)
        Each fallback level is recorded in judge_tier_used.
        Protected by RetryEngine (2 attempts) before falling to next tier.
        """

    def score(
        self,
        response: str,
        source_chunks: List[KnowledgeChunk],
        ethics_state: Optional[Any] = None,     # ethics.EthicsState (optional)
        trust_state: Optional[Any] = None,       # trust_engine.TrustState (optional)
    ) -> FaithfulnessScore:
        """
        Full pipeline:
          1. extract_claims(response)
          2. verify_claim for each (in parallel using asyncio.gather)
          3. compute weighted score
          4. check persona_check() if enabled
          5. attach ethics_alignment and trust_score if states provided
        Cap at max_claims to prevent runaway verification.
        On zero claims extracted → returns FaithfulnessScore(score=0.7, tier="marginal")
          (conservative: something without claims is marginal, not failing)
        Never raises.
        """

    def persona_check(self, response: str, axioms: List[KnowledgeChunk]) -> bool:
        """
        Pure regex — no model call. Checks for known persona violations:
          - "I am ChatGPT / I am Claude / I am an AI assistant / I am OpenAI"
          - Wrong gender references to self ("he said", "his personality")
          - Denial of Norse identity ("I'm not Norse", "I don't follow Heathen")
          - Denial of having feelings ("I don't have feelings", "I don't feel")
        Also checks axiom keywords: all top-3 identity axioms must have at
        least one keyword present somewhere in the response (or the response
        is too short to check — skip).
        Returns True = persona intact, False = violation detected.
        """

    def get_state(self) -> VordurState: ...
    def publish(self, bus: StateBus) -> None: ...
```

#### Dead Letter Routing (Vörðr side)

On `score.needs_retry = True` (score < marginal_threshold):
1. Emit `logger.warning("Vörðr: hallucination detected (score=%.2f), issuing retry %d/2")`
2. Caller (CovePipeline or smart_complete_with_cove) re-runs retrieval with expanded n_initial
3. If after 2 retries score still < marginal_threshold:
   - Write to DeadLetterStore
   - Return a safe canned "I need to check the Well again" response
   - Log at ERROR level with full trace

---

### 3. `viking_girlfriend_skill/scripts/huginn.py` — Huginn's Ara

The retrieval orchestrator. Knows which domain to search, retrieves, reranks,
combines episodic + knowledge context, and returns a ready-to-inject packet.

#### Data Structures

```python
@dataclass
class RetrievalRequest:
    """API-style typed request object — never raw dict."""
    query: str
    n_initial: int = 50
    n_final: int = 3
    domain: Optional[str] = None        # explicit domain override
    include_episodic: bool = True       # whether to pull from MemoryStore too
    urgency: str = "normal"            # "normal" | "fast" (fast skips rerank)

@dataclass
class RetrievalResult:
    """API-style typed response object."""
    query: str
    domain: Optional[str]
    knowledge_chunks: List[KnowledgeChunk]   # top-N from MimirWell
    episodic_context: str                    # from MemoryStore
    context_string: str                      # formatted for prompt injection
    retrieval_ms: float
    fallback_used: str      # "full" | "bm25" | "episodic_only" | "empty"
    domain_detection_confidence: float  # 0.0–1.0
    error_context: Optional[str]        # set if any fallback was used

@dataclass
class HuginnState:
    total_retrievals: int
    total_fallbacks: int
    avg_retrieval_ms: float
    domain_counts: Dict[str, int]
    circuit_breaker_state: str
    last_retrieved_at: Optional[str]
    fallback_mode_active: bool
```

#### Domain Detection Keyword Map

```python
DOMAIN_KEYWORDS = {
    "norse_spirituality": [
        "rune", "runes", "futhark", "seiðr", "seid", "volva", "galdr",
        "galdrabok", "blot", "bindrune", "ansuz", "thurisaz", "fehu",
        "uruz", "hagalaz", "tiwaz", "berkanan", "mannaz", "laguz",
        "ingwaz", "othalan", "wyrd", "norn", "norns", "freyja", "freyr",
        "heathen", "asatru", "rokkatru", "nornir", "disir", "vaettir",
    ],
    "norse_mythology": [
        "odin", "thor", "loki", "frigg", "tyr", "baldur", "baldr",
        "yggdrasil", "asgard", "midgard", "jotunheim", "niflheim",
        "muspelheim", "valhalla", "einherjar", "ragnarok", "eddas",
        "prose edda", "poetic edda", "voluspa", "havamal", "skaldic",
        "jormungandr", "fenrir", "hela", "hel", "bifrost",
    ],
    "norse_culture": [
        "viking", "norse", "scandinavian", "jarl", "thane", "thrall",
        "longship", "mead hall", "frith", "honor", "shame", "wergild",
        "thing", "lawspeaker", "shield maiden", "saga", "skald",
        "berserker", "huscarl", "raid", "trade route",
    ],
    "coding": [
        "python", "javascript", "code", "function", "class", "module",
        "algorithm", "database", "api", "async", "await", "loop",
        "debug", "error", "exception", "variable", "type", "list",
        "dict", "json", "yaml", "sql", "git", "docker", "linux",
        "terminal", "bash", "regex", "library", "framework",
    ],
    "character": [
        "values", "soul", "identity", "feel", "emotion", "personality",
        "honor", "ethics", "belief", "principle", "who are you",
        "what do you think", "how do you feel", "your opinion",
    ],
}
```

Confidence scoring: count keyword matches / total query words. If max domain
confidence < 0.05 → None (global search, no domain filter).

#### Class Interface

```python
class HuginnRetriever:
    def __init__(
        self,
        mimir_well: MimirWell,
        memory_store: Optional["MemoryStore"] = None,  # injected from main.py
        n_initial: int = 50,
        n_final: int = 3,
        domain_detection_enabled: bool = True,
    ): ...

    def detect_domain(self, query: str) -> Tuple[Optional[str], float]:
        """Returns (domain_name_or_None, confidence_score)."""

    def retrieve(self, request: RetrievalRequest) -> RetrievalResult:
        """
        Full pipeline — protected by _huginn_full circuit breaker.

        1. detect_domain (if not explicit in request)
        2. mimir_well.retrieve() → PRIMARY knowledge chunks
           FALLBACK A: mimir_well._bm25_retrieve() (if ChromaDB down)
           FALLBACK B: [] (no knowledge chunks)
        3. memory_store.get_context(query) → episodic context (if enabled)
           FALLBACK: "" (empty string — episodic failure is non-fatal)
        4. mimir_well.rerank() → reduce to n_final
        5. Assemble RetrievalResult with combined context_string
        6. On ALL_FALLBACKS_EXHAUSTED: return empty RetrievalResult
           (never raises — caller always gets a result object)

        Retry: RetryEngine with 2 attempts before each fallback.
        Timeout per attempt: 5s for ChromaDB, 2s for BM25.
        """

    def get_state(self) -> HuginnState: ...
    def publish(self, bus: StateBus) -> None: ...
```

#### Context String Format

```
[GROUND TRUTH — retrieved from the Well]
[GT-1] (Source: {source_file}) {chunk_text}
[GT-2] (Source: {source_file}) {chunk_text}
[GT-3] (Source: {source_file}) {chunk_text}

[MEMORY — recent episodic context]
{episodic_context}
```

---

### 4. `viking_girlfriend_skill/scripts/cove_pipeline.py` — Chain-of-Verification

The four-step refinement loop. Checkpointed. Self-resuming. Has its own
circuit breaker and fallback to bypass entirely on sustained failure.

#### Data Structures

```python
@dataclass
class CoveCheckpoint:
    """Persisted between steps in case of mid-pipeline crash."""
    checkpoint_id: str          # uuid
    query: str
    context: str
    draft: Optional[str]        # available after Step 1
    questions: Optional[List[str]]   # available after Step 2
    qa_pairs: Optional[List[Tuple[str, str]]]  # available after Step 3
    step_reached: int           # 0=start, 1=drafted, 2=questioned, 3=answered
    created_at: str

@dataclass
class CoveResult:
    draft: str
    verification_questions: List[str]
    qa_pairs: List[Tuple[str, str]]
    final_response: str
    faithfulness_score: Optional[FaithfulnessScore]
    used_cove: bool             # False if complexity=low or circuit breaker open
    steps_completed: int        # 0–4
    fallback_chain: List[str]   # which fallbacks were used, in order
    checkpoint_id: Optional[str]

@dataclass
class CoveState:
    enabled: bool
    total_runs: int
    total_skipped_low_complexity: int
    total_bypassed_circuit_breaker: int
    total_step_failures: Dict[str, int]   # {"step2": N, "step3": N, "step4": N}
    avg_steps_completed: float
    circuit_breaker_pipeline: str
    last_run_at: Optional[str]
```

#### Step Fallback Map

| Step | Primary | Fallback A | Fallback B |
|------|---------|-----------|-----------|
| 1 Draft | chosen tier (router) | escalate to next tier | None (Step 1 failure = abort CoVe, return empty) |
| 2 Plan questions | subconscious | template questions (3 static, domain-aware) | ["Is this factually accurate?", "Does this match the source?", "Are there any contradictions?"] |
| 3 Execute questions | subconscious + MimirWell | skip (pass Step 2 questions with no answers) | — |
| 4 Revise | chosen tier | conscious tier | return Step 1 draft unchanged |

Template questions by domain:
```python
TEMPLATE_QUESTIONS = {
    "norse_spirituality": [
        "Does this response accurately represent Norse spiritual practices?",
        "Are the rune names and meanings correct?",
        "Does this align with authentic Heathen traditions?",
    ],
    "norse_mythology": [
        "Are the names of gods and entities accurate?",
        "Does the cosmological description match the Eddas?",
        "Are the relationships between mythological figures correct?",
    ],
    "coding": [
        "Is the code or technical explanation syntactically correct?",
        "Does the algorithm description match standard implementations?",
        "Are the library/API references accurate?",
    ],
    "default": [
        "Is this factually consistent with the source material?",
        "Does this response contradict any retrieved Ground Truth?",
        "Are there any unsupported claims in this response?",
    ],
}
```

#### Class Interface

```python
class CovePipeline:
    def __init__(
        self,
        mimir_well: MimirWell,
        router: "ModelRouterClient",
        vordur: VordurChecker,
        min_complexity: str = "medium",     # "low" | "medium" | "high"
        n_verification_questions: int = 3,
        checkpoint_dir: Optional[Path] = None,  # session/cove_checkpoints/
        step_timeout_s: float = 15.0,
    ): ...

    def run(
        self,
        query: str,
        context: str,
        retrieval: RetrievalResult,
        complexity: str,
        resume_checkpoint: Optional[CoveCheckpoint] = None,
    ) -> CoveResult:
        """
        Full pipeline with per-step circuit breakers.

        If pipeline circuit breaker is OPEN → immediately return CoveResult
          with used_cove=False and a direct model call for the draft.

        Low complexity → skip Steps 2-4, return draft directly.

        Per-step failure handling:
          Step 1 fail → CovePipelineError (non-recoverable, caller handles)
          Step 2 fail → template questions (fallback A), then default (fallback B)
          Step 3 fail → skip (qa_pairs = [])
          Step 4 fail → return Step 1 draft, steps_completed = 3

        Checkpoint persistence:
          After Step 1: write CoveCheckpoint(step_reached=1)
          After Step 2: update CoveCheckpoint(step_reached=2)
          After Step 3: update CoveCheckpoint(step_reached=3)
          On completion: delete checkpoint file

        Resume from checkpoint:
          If resume_checkpoint.step_reached >= N → skip Steps 1..N-1
          Allows recovery from mid-pipeline crash on session restart.
        """

    def _step1_draft(self, query: str, context: str, checkpoint: CoveCheckpoint) -> str: ...
    def _step2_plan_questions(self, draft: str, context: str, domain: Optional[str],
                               checkpoint: CoveCheckpoint) -> List[str]: ...
    def _step3_execute_questions(self, questions: List[str], checkpoint: CoveCheckpoint
                                  ) -> List[Tuple[str, str]]: ...
    def _step4_revise(self, draft: str, qa_pairs: List[Tuple[str, str]],
                      checkpoint: CoveCheckpoint) -> str: ...

    def get_state(self) -> CoveState: ...
    def publish(self, bus: StateBus) -> None: ...
```

---

## Integration Changes to Existing Modules

### `memory_store.py` — Memory Federation Interface

```python
@dataclass
class FederatedMemoryRequest:
    query: str
    include_episodic_buffer: bool = True    # conversation buffer (last N turns)
    include_episodic_json: bool = True      # JSON episodic store
    include_episodic_chroma: bool = True    # ChromaDB episodic (semantic)
    include_knowledge: bool = True          # MimirWell knowledge store (via Huginn)
    max_episodic_tokens: int = 800
    max_knowledge_tokens: int = 600

@dataclass
class FederatedMemoryResult:
    episodic_context: str       # combined from all episodic tiers
    knowledge_context: str      # from Huginn/MimirWell
    combined_context: str       # episodic_context + "\n\n" + knowledge_context
    sources_used: List[str]     # which tiers actually contributed
    total_chars: int

def get_context_with_knowledge(
    self,
    request: FederatedMemoryRequest,
    huginn: Optional["HuginnRetriever"] = None,
) -> FederatedMemoryResult:
    """
    Unified memory federation interface.
    Retrieves from all four tiers in parallel (asyncio.gather).
    Each tier retrieval is wrapped in try/except — one failing tier
    does not block the others.
    Falls back gracefully: if all tiers fail → returns empty FederatedMemoryResult.
    """
```

### `model_router_client.py` — Extended Interface

```python
# Extended CompletionResponse fields (all Optional — backward compatible)
faithfulness_score: Optional[float] = None
faithfulness_tier: str = ""         # "high" | "marginal" | "hallucination" | ""
cove_applied: bool = False
cove_steps_completed: int = 0
retrieval_domain: Optional[str] = None
retry_count: int = 0
ground_truth_chunks: int = 0        # number of GT chunks injected
fallback_chain: List[str] = field(default_factory=list)

def smart_complete_with_cove(
    self,
    messages: List[Message],
    huginn: Optional[HuginnRetriever] = None,
    vordur: Optional[VordurChecker] = None,
    cove: Optional[CovePipeline] = None,
    dead_letter_store: Optional[_DeadLetterStore] = None,
    ethics_state: Optional[Any] = None,
    trust_state: Optional[Any] = None,
    fallback: bool = True,
    max_vordur_retries: int = 2,
    **kwargs: Any,
) -> CompletionResponse:
    """
    Full Mímir-Vörðr pipeline:

    1. smart_complete() for routing decision (existing — detect complexity + tier)
    2. HuginnRetriever.retrieve(FederatedMemoryRequest) → Ground Truth context
       FALLBACK: skip retrieval (proceed without Ground Truth)
    3. CovePipeline.run() → draft → verify → revise
       FALLBACK: direct smart_complete() call (bypass CoVe)
    4. VordurChecker.score() → faithfulness score
       FALLBACK: skip scoring (return marginal score 0.5)
    5. Retry loop (max max_vordur_retries):
       - If needs_retry: re-run step 2+3 with expanded n_initial (×2)
       - If still failing after all retries: dead_letter_store.append() + canned response
    6. Attach all faithfulness fields to CompletionResponse

    Entire method wrapped in try/except — any uncaught error falls back to
    plain smart_complete() (the existing baseline behavior). Never crashes.
    """
```

### `main.py` — Mímir-Vörðr Singletons

```python
# New singletons in _init_all_modules() (after existing 18):
mimir_well     = init_mimir_well_from_config(config)
huginn         = init_huginn_from_config(config, mimir_well, memory_store)
vordur         = init_vordur_from_config(config)
cove           = init_cove_pipeline_from_config(config, mimir_well, router, vordur)
dead_letters   = _DeadLetterStore(Path("session/dead_letters.jsonl"))
health_monitor = MimirHealthMonitor(
    mimir_well, vordur, huginn, cove, dead_letters, bus, scheduler
)
health_monitor.start()

# In _handle_turn() — Step 9 becomes:
result = router.smart_complete_with_cove(
    messages,
    huginn=huginn,
    vordur=vordur,
    cove=cove,
    dead_letter_store=dead_letters,
    ethics_state=ethics.get_state() if ethics else None,
    trust_state=trust.get_state() if trust else None,
    fallback=True,
)

# StateBus publishes (added to _publish_all_states()):
huginn.publish(bus)
vordur.publish(bus)
mimir_well.publish(bus)
cove.publish(bus)
health_monitor.publish(bus)
```

---

## Configuration Block (added to config)

```yaml
mimir_well:
  collection_name: mimir_well
  persist_dir: data/chromadb_mimir    # separate from sigrid_episodic
  chunk_size_tokens: 512
  chunk_overlap_tokens: 64
  n_retrieve: 50
  n_final: 3
  auto_ingest: true                   # ingest on first startup if collection empty
  force_reindex: false                # set true to nuke and rebuild

huginn:
  n_initial: 50
  n_final: 3
  domain_detection: true
  include_episodic: true

vordur:
  enabled: true
  high_threshold: 0.80
  marginal_threshold: 0.50
  persona_check: true
  judge_tier: subconscious
  max_claims: 10
  verification_timeout_s: 8.0

cove_pipeline:
  enabled: true
  min_complexity: medium
  n_verification_questions: 3
  step_timeout_s: 15.0

health_monitor:
  check_interval_s: 60
  diagnostics_interval_s: 600
  dead_letter_alert_threshold: 5      # per 5-minute window
  auto_reindex_on_corruption: true

circuit_breakers:
  chromadb_read:   {failure_threshold: 3, cooldown_s: 30}
  chromadb_write:  {failure_threshold: 3, cooldown_s: 60}
  vordur_subconscious: {failure_threshold: 5, cooldown_s: 60}
  vordur_conscious:    {failure_threshold: 3, cooldown_s: 30}
  huginn_full:         {failure_threshold: 3, cooldown_s: 30}
  cove_step2:      {failure_threshold: 3, cooldown_s: 30}
  cove_step3:      {failure_threshold: 3, cooldown_s: 30}
  cove_step4:      {failure_threshold: 3, cooldown_s: 30}
  cove_pipeline:   {failure_threshold: 3, cooldown_s: 120}

retry_engines:
  chromadb:  {max_attempts: 3, base_delay_s: 0.5, backoff_factor: 2.0, max_delay_s: 4.0}
  judge_model: {max_attempts: 2, base_delay_s: 1.0, backoff_factor: 2.0, max_delay_s: 4.0}
  cove_step:   {max_attempts: 2, base_delay_s: 0.5, backoff_factor: 2.0, max_delay_s: 4.0}
```

---

## Faithfulness Thresholds & Actions

| Score | Tier | Action |
|-------|------|--------|
| 0.8 – 1.0 | high | Pass. Log score at DEBUG. |
| 0.5 – 0.79 | marginal | Pass. Log at WARNING. Attach marginal flag to metadata. |
| < 0.5 | hallucination | Discard. Re-run with expanded n_initial (×2). Max 2 retries. On final failure: DeadLetterStore + canned response. |

Canned "I need to check again" response (returned on hallucination exhaustion):
```
Sigrid pauses, brow furrowed.
"The threads of the Well are unclear to me right now — I want to answer
you truly, not from the fog. Let me return to this when the sight is clearer."
```

---

## RAGAS-Inspired Metrics (in VordurState)

| Metric | Definition | Stored In |
|--------|-----------|----------|
| Faithfulness | fraction of claims ENTAILED by source chunks | VordurState.recent_avg_score |
| Answer Relevance | cosine sim(response embedding, query embedding) | VordurState (Phase 2) |
| Context Precision | fraction of GT chunks cited in response | HuginnState (Phase 2) |

Phase 1 implements Faithfulness only (the critical one).
Phase 2 adds Answer Relevance + Context Precision (requires embedding the response).

---

## Knowledge Graph (Phase 2 Enhancement)

Phase 1: flat ChromaDB retrieval with metadata filtering.
Phase 2: JSON relationship graph for Norse concept expansion.

```json
{
  "Thurisaz": {
    "related": ["Thor", "protection", "power", "threshold"],
    "aett": "Heimdall",
    "type": "rune"
  },
  "Freyja": {
    "related": ["seiðr", "cats", "fertility", "völva", "Vanaheim", "love", "war"],
    "type": "deity",
    "aett_owner": "Freyja"
  }
}
```

Query expansion: before ChromaDB retrieve, expand query keywords via graph.
"Tell me about Thurisaz" → also retrieve chunks about Thor, protection, threshold.

---

## Implementation Order

| Step | Deliverable | Depends On | Status |
|------|-------------|-----------|--------|
| 1 | `mimir_well.py` | config_loader, state_bus, chromadb | ✅ DONE (2026-03-20) — 57 files, 25 160 chunks, BM25+ChromaDB dual path |
| 2 | `vordur.py` | mimir_well, model_router_client | ✅ DONE (2026-03-20) — NLI pipeline, 4-tier fallback chain, persona guard, circuit breakers |
| 3 | `huginn.py` | mimir_well, memory_store | ⏳ NEXT |
| 4 | `cove_pipeline.py` | huginn, model_router_client, vordur | ⏳ PENDING |
| 5 | Extend `memory_store.py` | huginn | ⏳ PENDING |
| 6 | Extend `model_router_client.py` | vordur, huginn, cove | ⏳ PENDING |
| 7 | Extend `main.py` | all above | ⏳ PENDING |
| 8 | `tests/test_mimirvordur.py` | all above | ⏳ PENDING |
| 9 | Extend `ops/launch_calibration.py` | new modules | ⏳ PENDING |

---

## Test Coverage Plan (`tests/test_mimirvordur.py`)

### Infrastructure Tests
```
T01  CircuitBreaker transitions: CLOSED → OPEN → HALF_OPEN → CLOSED
T02  CircuitBreaker rejects calls when OPEN (raises CircuitBreakerOpenError)
T03  RetryEngine: succeeds on 2nd attempt after transient failure
T04  RetryEngine: does not retry CircuitBreakerOpenError
T05  DeadLetterStore: append + count_recent + get_last_n
T06  DeadLetterStore: survives corrupt JSONL (skips bad lines, reads good ones)
```

### MimirWell Tests
```
T07  ingest_all — loads knowledge_reference/ without error, returns IngestReport
T08  ingest_all — idempotent: calling twice doesn't double-count
T09  ingest_all — partial failure: one malformed file → error in report, rest succeed
T10  retrieve — returns KnowledgeChunks for a Norse query
T11  retrieve — domain filter: "rune" query stays in norse_spirituality
T12  retrieve — falls back to BM25 when ChromaDB breaker is open
T13  rerank — reduces 50 candidates to 3
T14  get_axioms — returns level=3 chunks only
T15  get_context_string — formats [GT-1] citation style
T16  reindex — wipes and rebuilds collection cleanly
```

### VordurChecker Tests
```
T17  extract_claims — mocked subconscious, returns Claim list
T18  extract_claims — fallback to sentence splitter on model timeout
T19  verify_claim ENTAILED — verdict + score impact
T20  verify_claim CONTRADICTED — score impact
T21  verify_claim — falls back to conscious tier on Ollama breaker open
T22  verify_claim — falls back to regex heuristic on both model breakers open
T23  verify_claim — falls back to UNCERTAIN passthrough on all fallbacks exhausted
T24  score HIGH — response faithful to source → ≥ 0.80
T25  score LOW — response contradicts source → < 0.50, needs_retry=True
T26  score ZERO_CLAIMS — returns marginal (0.7) not zero
T27  persona_check — blocks "I am ChatGPT" regex
T28  persona_check — blocks wrong gender reference
T29  ethics + trust state attached to FaithfulnessScore if provided
```

### HuginnRetriever Tests
```
T30  detect_domain — Norse keywords → norse_spirituality + confidence > 0
T31  detect_domain — coding keywords → coding
T32  detect_domain — no match → (None, low confidence)
T33  retrieve — returns RetrievalResult with knowledge_chunks
T34  retrieve — episodic_context appended when memory_store provided
T35  retrieve — falls back to BM25 when ChromaDB circuit breaker open
T36  retrieve — returns empty result (no crash) when all fallbacks exhausted
T37  context_string format — [GT-N] + [MEMORY] sections present
```

### CovePipeline Tests
```
T38  run LOW complexity → skips CoVe, used_cove=False, steps_completed=1
T39  run MEDIUM — full 4-step (mocked LLM), steps_completed=4
T40  run MEDIUM — Step 2 fails → template questions used (fallback A)
T41  run MEDIUM — Step 3 fails → qa_pairs=[], step still completes
T42  run MEDIUM — Step 4 fails → returns Step 1 draft, steps_completed=3
T43  CoveCheckpoint written after Step 1
T44  CoveCheckpoint updated after Step 2
T45  resume from Step 2 checkpoint → skips Step 1
T46  pipeline circuit breaker open → bypasses CoVe, returns direct response
```

### Integration Tests
```
T47  smart_complete_with_cove → faithfulness_score attached to CompletionResponse
T48  smart_complete_with_cove → retry on hallucination → retry_count incremented
T49  smart_complete_with_cove → max retries exhausted → canned response returned
T50  smart_complete_with_cove → faithfulness_tier in response
T51  MemoryStore.get_context_with_knowledge → merges episodic + knowledge
T52  MemoryStore.get_context_with_knowledge → episodic fails → knowledge still works
T53  Full pipeline: Norse query → huginn → cove → vordur → high faithfulness
T54  Full pipeline: hallucination detected → retry → score improves
T55  Full pipeline: Ollama down → vordur falls back to conscious tier
T56  Full pipeline: ChromaDB down → Huginn falls back to BM25
T57  Full pipeline: everything down → graceful canned response (no crash)
```

### Health Monitor Tests
```
T58  MimirHealthMonitor.get_state — all components healthy
T59  MimirHealthMonitor — detects ChromaDB zero docs → triggers reindex
T60  MimirHealthMonitor — dead letter spike → logs CRITICAL
```

---

## Key Design Constraints

- MimirWell ingest is idempotent — safe to call on every startup
- VordurChecker NEVER modifies Sigrid's voice — only scores and routes retries
- CoVe always uses the same tier as the original router selection for Steps 1 + 4
- Max 2 Vörðr retries per response — never infinite loops
- CircuitBreakerOpenError is never retried — it's a fast-fail, not a transient error
- All new modules follow the existing singleton pattern:
  `init_X_from_config()`, `get_X()`, `get_state() → XState`, `publish(bus)`
- CompletionResponse extensions are all Optional + default — backward compatible
- Judge model prompts must work with llama3 8B: short, structured, single-word answer
- All modules: `logger.debug/info/warning/error/critical` — never `print()`
- Windows cp1252 safe: all log strings with Norse runes use ASCII-encode fallback
- Thread safety: circuit breakers use `threading.Lock`, DeadLetterStore uses file-append mode

---

## Files Created / Modified

| File | Action | Purpose |
|------|--------|---------|
| `scripts/mimir_well.py` | CREATE | Mímisbrunnr knowledge store |
| `scripts/vordur.py` | CREATE | Vörðr truth guard |
| `scripts/huginn.py` | CREATE | Huginn retrieval orchestrator |
| `scripts/cove_pipeline.py` | CREATE | Chain-of-Verification pipeline |
| `scripts/memory_store.py` | EXTEND | FederatedMemoryRequest interface |
| `scripts/model_router_client.py` | EXTEND | smart_complete_with_cove() |
| `scripts/main.py` | EXTEND | Wire 4 new singletons + health monitor |
| `tests/test_mimirvordur.py` | CREATE | 60 test cases |
| `ops/launch_calibration.py` | EXTEND | Import + init checks for new modules |
| `session/dead_letters.jsonl` | RUNTIME | Dead letter log (auto-created) |
| `session/cove_checkpoints/` | RUNTIME | CoVe step checkpoints (auto-created) |
| `data/chromadb_mimir/` | RUNTIME | ChromaDB mimir_well collection |

---

## Session Resume Instructions

On session start: read this file → check Implementation Order table →
pick the next step marked ⏳ NEXT or ⏳ PENDING → read relevant existing
modules for API patterns (config_loader, memory_store, model_router_client) →
plan any questions → code one module → test → mark step DONE → commit → proceed.

**Start with:** Step 1 — `mimir_well.py`

Read before coding:
- `scripts/config_loader.py` (data_root pattern)
- `scripts/state_bus.py` (StateEvent + publish pattern)
- `scripts/memory_store.py` (ChromaDB init pattern for sigrid_episodic collection)
- `data/knowledge_reference/` (list files to understand what gets ingested)
