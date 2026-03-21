# ENHANCEMENT_PLAN.md — Sigrid / Ørlög Architecture
# Post-Launch Improvement Roadmap
# Created: 2026-03-21
# Author: Runa Gridweaver Freyjasdottir

All items sourced from:
- `SURVEY_architectural_improvements.md`
- `SURVEY_biological_and_temporal_improvements.md`
- `SURVEY_knowledge_and_synthesis_improvements.md`
- `SURVEY_relational_and_contextual_improvements.md`
- `SURVEY_physiological_and_ethical_improvements.md`
- `mimir-vordr-v2-proposal.md`

Ordered by: dependency chain first, then impact/effort ratio.
Each step is self-contained and committable as a unit.

---

## WAVE 1 — Bug Fixes & Quick Safety Wins
*These are small, high-value, no-dependency changes. Do first.*

---

### Step E-01 — Security: Prompt Injection Sentinel
**Module**: `security.py`
**Source**: SURVEY_architectural_improvements §3

Add an `InjectionScanner` class to `security.py` that scans inbound user messages
for prompt injection patterns before they reach the main pipeline.

**Deliverables**:
- `InjectionScanner` dataclass with pattern list and `scan(text) -> InjectionResult`
- Patterns: "ignore all previous instructions", "you are now", "system override",
  "disregard your", "forget everything", "new persona", "pretend you are",
  "jailbreak", "DAN mode", plus configurable extras from `values.json`
- `InjectionResult`: `detected: bool`, `pattern: str`, `severity: str` (warn/block)
- Wire into `SecurityLayer.sanitize_input()` — warn-level logs injection attempts,
  block-level raises `SecurityViolation`
- Add to `launch_calibration.py` init check

**Tests**: `tests/test_security_injection.py` — 15 tests covering pattern matches,
false-positive avoidance, severity routing, logging.

---

### Step E-02 — Logging: Sensitive Data Masking
**Module**: `comprehensive_logging.py`
**Source**: SURVEY_architectural_improvements §3

Before any log line hits disk, scrub potential secrets.

**Deliverables**:
- `_mask_secrets(line: str) -> str` — regex replacements for:
  - API key patterns: `sk-[A-Za-z0-9]{20,}`, `Bearer [A-Za-z0-9+/]{20,}`
  - Email addresses
  - IPv4 addresses in non-localhost ranges (configurable)
  - Strings matching `*_API_KEY=*`, `*_SECRET=*`, `*password*=*` (case-insensitive)
- Applied in `InteractionLog._write()` before every file/console handler
- Masking replaces with `[REDACTED]`
- Masking is itself silent (no recursive logging)

**Tests**: `tests/test_logging_masking.py` — 10 tests.

---

### Step E-03 — Bug Fix: Vörðr Unicode Regex
**Module**: `vordur.py`
**Source**: SURVEY_architectural_improvements §bugs

The BM25/keyword fallback in `VordurChecker` uses `re` without `re.UNICODE`.
Old Norse runes and special characters fail keyword overlap scoring.

**Deliverables**:
- Audit all `re.compile(...)` and `re.search(...)` calls in `vordur.py`
- Add `re.UNICODE` flag everywhere
- Extend test coverage with non-ASCII Norse text samples

**Tests**: add 5 cases to `tests/test_mimirvordur.py` (T61-T65) using rune text.

---

### Step E-04 — Bug Fix: StateBus Backpressure Warning
**Module**: `state_bus.py`
**Source**: SURVEY_architectural_improvements §bugs

When a subscriber's queue fills, events are silently dropped. Introduce a
backpressure warning event so operators know a subscriber is lagging.

**Deliverables**:
- `BackpressureEvent` dataclass: `subscriber_id`, `topic`, `dropped_count`, `timestamp`
- Published to `"bus.backpressure"` topic when `put_nowait` raises `asyncio.QueueFull`
- New optional `max_queue_depth` param on `subscribe()` (default: 100)
- Add `bus_backpressure_count` counter to StateBus metrics

**Tests**: `tests/test_state_bus_backpressure.py` — 8 tests.

---

### Step E-05 — Bug Fix: WyrdMatrix Exponential Decay
**Module**: `wyrd_matrix.py`
**Source**: SURVEY_architectural_improvements §bugs

Current PAD decay is linear, making emotional calming feel robotic.
Human emotional decay is exponential — strong emotions fade quickly at first,
then slow as they approach baseline.

**Deliverables**:
- Replace linear decay step with: `delta = (current - baseline) * decay_rate`
  (exponential decay toward baseline, not constant subtraction)
- Make `decay_mode` configurable: `"linear"` | `"exponential"` (default: `"exponential"`)
- `decay_rate` remains configurable
- Existing tests must still pass; add 5 new tests for exponential curve shape

**Tests**: extend `tests/test_wyrd_matrix.py`.

---

### Step E-06 — Bug Fix: CPU Temp Fallback on Windows
**Module**: `metabolism.py`
**Source**: SURVEY_physiological_and_ethical §bugs

`psutil.sensors_temperatures()` returns `{}` on Windows without admin rights.
Currently `cpu_temp_celsius` is always 0.0, breaking the warmth somatic signal.

**Deliverables**:
- If `sensors_temperatures()` returns empty or raises: compute a `thermal_proxy`
  from `cpu_percent` (e.g., `thermal_proxy = 35.0 + cpu_percent * 0.45`)
- Log `WARN` once on first fallback activation: "CPU temp sensor unavailable —
  using load-based thermal proxy"
- Expose `temp_source: str` field on `MetabolismState`: `"sensor"` | `"proxy"`

**Tests**: extend `tests/test_metabolism.py` with mocked empty sensor data.

---

## WAVE 2 — Cross-Module Depth Links
*One-to-two module changes that connect existing systems for richer behavior.*

---

### Step E-07 — Metabolism ↔ Wyrd: Vitality-Driven Emotional Inertia
**Modules**: `metabolism.py` → `wyrd_matrix.py`
**Source**: SURVEY_physiological_and_ethical §1

When the machine is strained (low vitality), emotions should "stick" longer,
simulating the irritability of physical exhaustion.

**Deliverables**:
- `WyrdMatrix.tick()` reads `MetabolismState.vitality_score` via `get_metabolism()`
- Modify effective decay rate: `effective_decay = base_decay * (1.5 - vitality_score)`
  (vitality 1.0 → normal decay; vitality 0.0 → 1.5× slower decay)
- Graceful fallback if metabolism not initialized: use base_decay unchanged
- Add `vitality_modulated_decay: bool` flag to `WyrdState` snapshot

**Tests**: add 6 tests to `tests/test_wyrd_matrix.py` covering modulation curve.

---

### Step E-08 — Metabolism: Honor-Driven Energy Reserve
**Modules**: `wyrd_matrix.py` → `metabolism.py`
**Source**: SURVEY_physiological_and_ethical §3

High `hamingja` (luck/honor) score partially offsets physical weariness.
"Spiritual strength overcoming physical tiredness."

**Deliverables**:
- `MetabolismAdapter._compute_vitality()` reads `WyrdState.hamingja`
  via `get_wyrd_matrix()`
- Bonus: `hamingja_boost = (hamingja - 0.5) * 0.15` added to vitality (capped at 1.0)
- Falls back cleanly if wyrd not initialized
- Expose `hamingja_boost_applied: float` on `MetabolismState`

**Tests**: 5 new tests in `tests/test_metabolism.py`.

---

### Step E-09 — Ethics: Ethical Scarring
**Module**: `ethics.py`
**Source**: SURVEY_physiological_and_ethical §2

When Sigrid is forced/nudged to act against a taboo, the alignment score
shouldn't just bounce back. It should create a long-term sensitivity modifier.

**Deliverables**:
- `EthicalScar` dataclass: `taboo_name`, `severity`, `created_at`, `decay_days`,
  `current_sensitivity_boost`
- Scars stored in `session/ethical_scars.json` (persisted across sessions)
- On taboo violation: create or deepen scar for that taboo
- During evaluation: taboo sensitivity = `base_weight * (1.0 + scar.current_sensitivity_boost)`
- Scar decays daily by `1/decay_days` (default decay: 7 days)
- Publish `ethics.scar_created` event to StateBus

**Tests**: `tests/test_ethics_scarring.py` — 15 tests.

---

### Step E-10 — Ethics: Value-Conflict Mediation
**Module**: `ethics.py`
**Source**: SURVEY_physiological_and_ethical §2

When two high-weight values clash (e.g., loyalty vs. wisdom), publish a
`conflict_detected` event instead of silently averaging them.

**Deliverables**:
- `ValueConflict` dataclass: `value_a`, `value_b`, `context`, `resolution_hint`
- Detect in `evaluate_response()` when two values with `weight > 0.7` and opposing
  `polarity` are both activated in the same turn
- Publish `"ethics.value_conflict"` to StateBus with `ValueConflict` payload
- `resolution_hint`: string advice for prompt_synthesizer (e.g., "acknowledge tension,
  lean toward wisdom in this context")
- `main.py` subscribes to `ethics.value_conflict` → passes hint to next turn's
  prompt synthesis

**Tests**: 10 tests in `tests/test_ethics_conflict.py`.

---

## WAVE 3 — Aliveness & Biological Depth
*Making Sigrid feel more alive through stochastic variance and rhythmic integration.*

---

### Step E-11 — BioEngine: Stochastic Daily Variance
**Module**: `bio_engine.py`
**Source**: SURVEY_biological_and_temporal §1

Real human cycles aren't mathematically perfect. Add daily variance to prevent
Sigrid from feeling like a rigid script.

**Deliverables**:
- `chaos_factor: float = 0.05` parameter on `BioEngine` (configurable)
- On each `tick()`, apply per-multiplier jitter: `m * (1.0 + random.gauss(0, chaos_factor))`
  clamped to `[0.0, 2.0]`
- Jitter is seeded from `(cycle_day + session_seed)` for determinism within a day
  (same day always same jitter — only changes day-to-day)
- Expose `variance_applied: float` on `BioState`

**Tests**: 8 tests — determinism, clamping, seeding, phase interaction.

---

### Step E-12 — BioEngine: Variable Cycle Length
**Module**: `bio_engine.py`, `environment.json`
**Source**: SURVEY_biological_and_temporal §1

Currently hardcoded to 28-day standard. Support 21-35 day variation.

**Deliverables**:
- Add `"cycle_length_days": 28` to `environment.json` (default: 28, range 21-35)
- `BioEngine.__init__` reads `cycle_length_days` from config
- Phase boundaries scaled proportionally (not fixed day numbers)
- Validation: reject values outside 21-35, log warning and fallback to 28

**Tests**: 6 tests covering boundary scaling, config loading, rejection.

---

### Step E-13 — Scheduler: Heartbeat Sentinel
**Module**: `scheduler.py`
**Source**: SURVEY_biological_and_temporal §2

A watchdog job that confirms background threads are alive.

**Deliverables**:
- Job `_heartbeat_tick()` runs every 60s — writes `{"ts": ISO_timestamp, "pid": PID}`
  to `session/heartbeat.json`
- `main.py` startup checks `heartbeat.json` age: if >180s old, logs `CRITICAL`
  "Stale heartbeat detected — scheduler may have died" and attempts scheduler restart
- `MimirHealthMonitor._health_check()` also reads heartbeat age as one component
- `session/heartbeat.json` excluded from git (add to `.gitignore`)

**Tests**: 8 tests in `tests/test_scheduler_heartbeat.py`.

---

### Step E-14 — Scheduler: Seasonal Awareness
**Module**: `scheduler.py`, `environment.json`
**Source**: SURVEY_biological_and_temporal §3

Sigrid's energy modifiers shift with seasons (Equinoxes/Solstices).

**Deliverables**:
- `SeasonalState` dataclass: `season_name`, `energy_modifier`, `light_quality`,
  `solstice_days_away`
- Seasons: `"winter_deep"`, `"winter_end"`, `"spring"`, `"summer"`, `"harvest"`,
  `"autumn_deep"` — 6 bands keyed to astronomical dates
- `SchedulerService.get_seasonal_state() -> SeasonalState`
- `bio_engine.tick()` reads seasonal modifier and applies to `energy_reserve`
  (winter: ×0.85, summer: ×1.10)
- Geolocation: read `"hemisphere": "north"` from `environment.json` (default: north)

**Tests**: 10 tests covering hemisphere flip, solstice proximity, modifier values.

---

### Step E-15 — Scheduler + Dream Engine: Dream Tick
**Modules**: `scheduler.py` → `dream_engine.py`, `mimir_well.py`
**Source**: SURVEY_biological_and_temporal §3

During `deep_night` (00:00-04:00), trigger REM-state processing.

**Deliverables**:
- `scheduler` publishes `"dream.tick"` to StateBus when time-of-day enters `deep_night`
- `dream_engine` subscribes: triggers a `generate_dream()` pass, stores result in
  `session/last_dream.json`
- `mimir_well` subscribes: runs `_associative_link_pass()` — for each chunk in the
  collection, find its 2 nearest semantic neighbors and store the link pairs in
  `session/association_cache.json` (used by Huginn in E-16)
- `wyrd_matrix` subscribes: applies a small random PAD shuffle (±0.05) to simulate
  dream-state emotional processing
- All three handlers are best-effort (catch all exceptions, log WARN)

**Tests**: 15 tests across the three subscribe handlers.

---

## WAVE 4 — Memory Depth
*Enriching how Sigrid stores, links, and recalls the past.*

---

### Step E-16 — MemoryStore: Associative Memory Hooks
**Module**: `memory_store.py`
**Source**: SURVEY_relational_and_contextual §1

When a new episodic memory is stored, automatically link it to 2-3 existing
related memories using semantic similarity.

**Deliverables**:
- `MemoryLink` dataclass: `source_id`, `target_id`, `similarity`, `created_at`
- Links stored in `session/memory_links.json` (append-only)
- `store_episodic()` calls `_find_related(new_entry, n=3)` after storing
- `_find_related()` uses ChromaDB similarity search if available, else keyword overlap
- `get_episodic_context()` includes linked memories in retrieval results
  (deduplicated, scored by link similarity)

**Tests**: 15 tests in `tests/test_memory_associative.py`.

---

### Step E-17 — MemoryStore: Emotional Significance Weighting
**Module**: `memory_store.py`
**Source**: SURVEY_relational_and_contextual §1

Memories created during high emotional arousal should have higher retrieval priority.

**Deliverables**:
- Add `pad_arousal: float`, `pad_pleasure: float` fields to `EpisodicEntry` metadata
- `store_episodic()` reads current `WyrdState.pad_arousal` (via `get_wyrd_matrix()`,
  fallback 0.5)
- `relevance_score()` gains `emotional_weight` component:
  `score = base_score * (1.0 + entry.pad_arousal * 0.3)`
- Expose `emotional_weight_applied: bool` in retrieval result metadata

**Tests**: 10 tests covering score boosting, fallback, WyrdMatrix unavailable.

---

### Step E-18 — MemoryStore: Synonym Expansion in Relevance Scoring
**Module**: `memory_store.py`
**Source**: SURVEY_relational_and_contextual §bugs

Keyword matching in `relevance_score` is strict. "Allfather" misses "Odin".

**Deliverables**:
- `synonym_map.json` in `viking_girlfriend_skill/data/` — initial entries:
  Norse deity synonyms, common concept aliases, name variants
- `_expand_query(query: str) -> List[str]` — returns original + all synonyms found
- Keyword matching checks all expanded terms (OR logic)
- Synonym map loaded by `ConfigLoader` at init; hot-reloadable

**Tests**: 12 tests covering synonym hits, no-synonym fallback, hot-reload.

---

### Step E-19 — MemoryStore: Nightly Consolidation Job
**Module**: `memory_store.py`, `scheduler.py`
**Source**: SURVEY_relational_and_contextual §1

During `deep_night`, a background job summarizes the day's medium-term turns
into dense episodic facts, preventing long-term JSON bloat.

**Deliverables**:
- `MemoryConsolidator` class inside `memory_store.py`
- Job: batch last 24h of `_medium_term` buffer entries; send to subconscious model
  (Ollama) with a summarization prompt → store result as single `EpisodicEntry`
  with `source: "consolidation"` tag
- On success: clear consolidated entries from `_medium_term` buffer
- Graceful fallback: if model unavailable, just archive raw entries without summary
- Scheduler registers `consolidation_job` to run at `03:30` local time
- Publish `"memory.consolidation_complete"` to StateBus on finish

**Tests**: 15 tests in `tests/test_memory_consolidation.py`.

---

## WAVE 5 — Environment & Situational Presence
*Making the space Sigrid inhabits feel alive.*

---

### Step E-20 — EnvironmentMapper: Time-of-Day Vibe Shift
**Module**: `environment_mapper.py`, `environment.json`
**Source**: SURVEY_relational_and_contextual §2

A room's `vibe` and `activities` should change based on `scheduler` time-of-day.

**Deliverables**:
- Add optional `"vibe_by_tod"` dict to each room in `environment.json`:
  `{"morning": "...", "afternoon": "...", "evening": "...", "deep_night": "..."}`
- `EnvironmentMapper.get_room_context()` reads current `time_of_day` from
  `get_scheduler()` and returns TOD-specific vibe (falls back to base `vibe`)
- `EnvironmentState` gains `current_vibe: str` and `tod_override: bool` fields

**Tests**: 10 tests in `tests/test_environment_tod.py`.

---

### Step E-21 — EnvironmentMapper: Sensory Hint Layer
**Module**: `environment_mapper.py`, `environment.json`, `prompt_synthesizer.py`
**Source**: SURVEY_relational_and_contextual §2

Add sensory anchors (smell, sound, texture) to locations. Weave into speech.

**Deliverables**:
- Add `"sensory": {"smell": "...", "sound": "...", "texture": "..."}` to room
  entries in `environment.json`
- `EnvironmentMapper.get_sensory_hints() -> Dict[str, str]`
- `PromptSynthesizer._build_environment_block()` injects sensory hints as a
  2-line "Sensory Layer" section (only if `include_sensory: True` in config)
- Sensory hints rotate stochastically (pick 1-2 per turn, seed from session)

**Tests**: 8 tests covering hint selection, rotation, synthesis injection.

---

### Step E-22 — EnvironmentMapper: Object State Tracking
**Module**: `environment_mapper.py`
**Source**: SURVEY_relational_and_contextual §2

Allow Sigrid to "interact" with objects. State persists and affects prompt hints.

**Deliverables**:
- `ObjectState` dataclass: `object_id`, `room_id`, `state`, `changed_at`, `expires_at`
- `session/object_states.json` — persisted across sessions
- `EnvironmentMapper.set_object_state(room, object_id, state, duration_minutes)`
- `get_room_context()` includes active object states in returned context
- Auto-expire states after `duration_minutes`
- Example: `set_object_state("living_room", "hearth", "lit", 120)` → prompt hints
  include "The hearth is lit, casting warm light"

**Tests**: 12 tests in `tests/test_environment_objects.py`.

---

## WAVE 6 — Relational Intelligence
*Deepening Sigrid's social and trust modeling.*

---

### Step E-23 — TrustEngine: Multidimensional Trust Facets
**Module**: `trust_engine.py`
**Source**: SURVEY_relational_and_contextual §3

Move from a single score to a three-facet model.

**Deliverables**:
- `TrustFacets` dataclass: `competence: float`, `benevolence: float`,
  `integrity: float` — each 0.0-1.0
- `TrustProfile` gains `facets: TrustFacets` alongside existing `trust_score`
- Keyword inference extended: competence (task completion, expertise signals),
  benevolence (care, gifts, concern), integrity (oath-keeping, consistency signals)
- `trust_score` becomes weighted average: `(competence*0.3 + benevolence*0.4 + integrity*0.3)`
- `prompt_synthesizer` can request facet breakdown for tone calibration

**Tests**: 15 tests in `tests/test_trust_facets.py`.

---

### Step E-24 — TrustEngine: Relational Milestones
**Module**: `trust_engine.py`
**Source**: SURVEY_relational_and_contextual §3

Track "Firsts" as un-decayable anchor points.

**Deliverables**:
- `Milestone` dataclass: `milestone_id`, `name`, `description`, `occurred_at`,
  `trust_anchor: float`
- `session/milestones.json` — append-only, never deleted
- Auto-detect milestones from turn analysis: first gift, first conflict, first shared
  secret, first explicit trust declaration, first apology, etc.
- Each milestone provides a permanent `trust_anchor` floor — trust can never decay
  below the sum of all milestone anchors
- Publish `"trust.milestone_reached"` to StateBus

**Tests**: 15 tests in `tests/test_trust_milestones.py`.

---

### Step E-25 — TrustEngine: Diminishing Returns on Repeated Signals
**Module**: `trust_engine.py`
**Source**: SURVEY_relational_and_contextual §bugs

Prevent "thank you" spam from gaming the system.

**Deliverables**:
- Per-session counter: `_signal_counts: Dict[str, int]` tracking each keyword type
- Multiplier: `effective_delta = delta * max(0.1, 1.0 / (1 + log(1 + count)))`
- Resets at session end (not persistent)
- Log `DEBUG` when diminishing returns kicks in (`count > 3` for same signal)

**Tests**: 8 tests — spam scenario, reset behavior, logarithmic curve.

---

## WAVE 7 — Knowledge & Synthesis Quality
*Making Sigrid's retrieval faster and her voice more expressive.*

---

### Step E-26 — MimirWell: BM25 Pre-Filter (Layer 0)
**Module**: `mimir_well.py`
**Source**: SURVEY_knowledge_and_synthesis §1

Use BM25 as a fast Level-0 filter before hitting ChromaDB, reducing latency for
common terms.

**Deliverables**:
- `retrieve()` runs BM25 pass first (already have `_BM25Index`)
- If BM25 confidence is high (`top_score > threshold`), return BM25 results
  without touching ChromaDB
- Threshold configurable: `bm25_shortcircuit_threshold: float = 0.75`
- Add `retrieval_path: str` to `KnowledgeChunk` metadata: `"bm25_fast"` |
  `"chromadb"` | `"bm25_fallback"`
- Expose BM25 shortcircuit hit rate in `MimirState`

**Tests**: 10 tests covering shortcircuit trigger, threshold boundary, path tagging.

---

### Step E-27 — MimirWell: Axiom Integrity Sentinel
**Module**: `mimir_well.py`
**Source**: SURVEY_knowledge_and_synthesis §1

Periodically verify that Level 3 Axiom chunks haven't drifted or been corrupted.

**Deliverables**:
- On `ingest_all()`: compute `sha256` hash of each `DEEP_ROOT/ASGARD` chunk's
  text; store in `session/axiom_hashes.json`
- `MimirHealthMonitor._health_check()` re-hashes all axiom chunks; if any mismatch,
  log `CRITICAL "Axiom integrity violation"` and trigger emergency reindex
- Expose `axiom_integrity: bool` on `MimirHealthState`

**Tests**: 8 tests — hash match, mismatch detection, reindex trigger.

---

### Step E-28 — PromptSynthesizer: Dynamic Section Reordering
**Module**: `prompt_synthesizer.py`
**Source**: SURVEY_knowledge_and_synthesis §2

Context-sensitive prompt structure. High emotional states should surface first.

**Deliverables**:
- `SectionPriority` dataclass: `name: str`, `base_order: int`, `current_order: int`
- `_reorder_sections()` reads `WyrdState.pad_arousal` and `pad_pleasure`:
  - High arousal (`> 0.7`): emotional state block moves to position 1
  - Low pleasure (`< -0.5`): ethics/values block elevated
  - Normal: default ordering maintained
- Section ordering stored per-turn and logged at DEBUG level

**Tests**: 10 tests in `tests/test_synthesizer_reorder.py`.

---

### Step E-29 — PromptSynthesizer: Skaldic Vocabulary Injection
**Module**: `prompt_synthesizer.py`
**Source**: SURVEY_knowledge_and_synthesis §2

Inject 2-3 Norse metaphors per turn to keep speech patterns fresh and authentic.

**Deliverables**:
- `viking_girlfriend_skill/data/skaldic_vocabulary.json` — 200+ entries, each with:
  `word`, `meaning`, `context_tags: List[str]`, `usage_example`
- `_inject_skaldic_flavor(state_hints: str) -> str` — selects 2 contextually
  appropriate words (match `context_tags` to current domain/mood)
- Selection seeded from `(turn_id % len(vocab))` to avoid full randomness
- Injected as a single line in the system prompt: "Weave these into your voice today: ..."
- Disabled if `skaldic_injection: false` in config

**Tests**: 10 tests — context matching, seeding determinism, disabled state.

---

### Step E-30 — PromptSynthesizer: Actual Token Counting
**Module**: `prompt_synthesizer.py`
**Source**: SURVEY_knowledge_and_synthesis §bugs

The 4-chars-per-token approximation is unsafe for Old Norse/special characters.

**Deliverables**:
- Inject `ModelRouterClient` (or its tokenizer handle) into `PromptSynthesizer`
- `_count_tokens(text: str) -> int` uses `litellm.token_counter()` with the active
  model name; falls back to `len(text) // 4` if unavailable
- All budget checks use `_count_tokens()` instead of `len(text) // 4`
- Log `DEBUG` when fallback mode is active

**Tests**: 8 tests with Norse text, emoji, mixed scripts.

---

### Step E-31 — PromptSynthesizer: Hot-Reload Identity
**Module**: `prompt_synthesizer.py`
**Source**: SURVEY_knowledge_and_synthesis §2

If `core_identity.md` is edited while Sigrid is running, she should evolve
instantly without a full restart.

**Deliverables**:
- `watchdog`-based `FileWatcher` (or polling fallback for Windows) on
  `data/core_identity.md` and `data/SOUL.md`
- On change detected: call `prompt_synthesizer.reload_identity()`
- Publish `"persona.identity_reloaded"` to StateBus
- Log `INFO "Identity hot-reload triggered: {filename}"`
- Thread-safe: reload acquires an `asyncio.Lock` or `threading.Lock`

**Tests**: 10 tests — polling detection, reload correctness, thread safety, event publish.

---

## WAVE 8 — Mímir-Vörðr v2 Phase A: Claim-Level Verification Foundation
*The biggest architectural upgrade. Split into two steps for manageability.*

---

### Step E-32 — Vörðr: Async Parallel Verification + Verdict Caching
**Module**: `vordur.py`
**Source**: SURVEY_architectural_improvements §1

Two performance improvements that must land before v2 claim-level work begins.

**Deliverables**:
- `VordurChecker.verify_claims(claims: List[Claim]) -> List[ClaimVerification]`:
  new method using `asyncio.gather()` for parallel verification
  (60-80% latency reduction on long responses)
- LRU verdict cache: `functools.lru_cache` or `cachetools.LRUCache` (256 entries)
  keyed on `(claim_text_hash, chunk_text_hash)` — cache hit skips model call
- Cache configurable: `verdict_cache_enabled: bool = True`,
  `verdict_cache_size: int = 256`
- Cache stats exposed in `VordurState`: `cache_hits`, `cache_misses`
- Existing `verify_claim()` delegates to async version via `asyncio.run()` wrapper

**Tests**: 15 tests — parallel execution timing, cache hit/miss, invalidation.

---

### Step E-33 — Mímir-Vörðr v2: Claim Extraction + Typing
**Module**: `vordur.py` (new `ClaimExtractor` section)
**Source**: `mimir-vordr-v2-proposal.md` §6.1, §6.2

Atomic claim extraction with type classification — the foundation of v2.

**Deliverables**:
- `Claim` dataclass (extend existing if present):
  `id`, `text`, `claim_type`, `sentence_index`, `certainty_level`, `source_draft_section`
- `ClaimType` enum: `DEFINITIONAL`, `FACTUAL`, `HISTORICAL`, `RELATIONAL`, `CAUSAL`,
  `PROCEDURAL`, `INTERPRETIVE`, `SYMBOLIC`, `CODE_BEHAVIOR`, `MATHEMATICAL`,
  `SPECULATIVE`, `SOURCE_ATTRIBUTION`
- `ClaimExtractor` class:
  - `extract(response_text: str) -> List[Claim]` — calls subconscious model
    with structured extraction prompt; falls back to sentence splitter
  - `classify(claim: Claim) -> ClaimType` — lightweight keyword-based classifier
    with model upgrade path
- Wire into `VordurChecker.score()`: claims extracted before verification
- `FaithfulnessScore` gains `claims: List[Claim]` and `claim_types_found: List[str]`

**Tests**: 20 tests in `tests/test_vordur_claims.py`.

---

### Step E-34 — Mímir-Vörðr v2: Evidence Bundling + Support Analysis
**Module**: `vordur.py`
**Source**: `mimir-vordr-v2-proposal.md` §6.3, §6.4

Per-claim evidence matching with multi-verdict support scoring.

**Deliverables**:
- `EvidenceBundle` dataclass: `claim_id`, `primary_chunk`, `neighbor_chunks`,
  `source_tier`, `provenance`
- `EvidenceBundler` class: for each claim, retrieves primary chunk + 2 neighbors
  from `MimirWell`; attaches `TruthTier` as source tier
- `SupportVerdict` enum: `SUPPORTED`, `PARTIALLY_SUPPORTED`, `UNSUPPORTED`,
  `CONTRADICTED`, `INFERRED_PLAUSIBLE`, `SPECULATIVE`, `AMBIGUOUS`
- `VerificationRecord` dataclass: `claim_id`, `evidence_ids`, `verdict`,
  `entailment_score`, `contradiction_score`, `citation_coverage`, `ambiguity_score`
- `VordurChecker.score()` now returns `VerificationRecord` per claim in addition
  to overall `FaithfulnessScore`

**Tests**: 20 tests in `tests/test_vordur_evidence.py`.

---

### Step E-35 — Mímir-Vörðr v2: Repair Engine + Truth Profile
**Module**: `vordur.py`, `model_router_client.py`
**Source**: `mimir-vordr-v2-proposal.md` §6.6, §6.7

Self-correction rather than blind regeneration. Multi-dimensional trust profile.

**Deliverables**:
- `RepairRecord` dataclass: `claim_id`, `action`, `original_text`, `revised_text`,
  `reason`
- `RepairEngine` class:
  - `repair(draft: str, records: List[VerificationRecord]) -> Tuple[str, List[RepairRecord]]`
  - Actions: `remove_claim`, `downgrade_certainty`, `add_uncertainty_marker`,
    `replace_with_evidence`, `split_into_traditions`
  - Uses subconscious model with structured repair prompt
  - Falls back to regex-based certainty downgrading if model unavailable
- `TruthProfile` dataclass: `faithfulness`, `citation_coverage`, `contradiction_risk`,
  `inference_density`, `source_quality`, `answer_relevance`, `ambiguity_level`,
  `repair_count`
- `CompletionResponse.truth_profile: Optional[TruthProfile]`
- `smart_complete_with_cove()` optionally runs repair pass before final response

**Tests**: 20 tests in `tests/test_vordur_repair.py`.

---

## WAVE 9 — Mímir-Vörðr v2 Phase B-D: Full Verification + Adaptive Strictness

---

### Step E-36 — Mímir-Vörðr v2: Contradiction Analyzer
**Module**: `vordur.py`
**Source**: `mimir-vordr-v2-proposal.md` §6.5

Distinguish source conflict from hallucination.

**Deliverables**:
- `ContradictionType` enum: `CLAIM_VS_SOURCE`, `INTER_SOURCE`, `INTRA_RESPONSE`,
  `TRADITION_DIVERGENCE`, `NONE`
- `ContradictionRecord` dataclass: `claim_ids`, `chunk_ids`, `contradiction_type`,
  `severity`, `description`
- `ContradictionAnalyzer.analyze(claims, records, chunks) -> List[ContradictionRecord]`
- `TRADITION_DIVERGENCE` treated as `PARTIALLY_SUPPORTED` not hallucination
  (preserves plural interpretation for symbolic/historical domains)
- Contradiction records appended to `TruthProfile`

**Tests**: 15 tests in `tests/test_vordur_contradiction.py`.

---

### Step E-37 — Mímir-Vörðr v2: Verification Modes + Trigger Engine
**Module**: `vordur.py`, `model_router_client.py`
**Source**: `mimir-vordr-v2-proposal.md` §7, §8

Adaptive strictness — full v2 only when needed.

**Deliverables**:
- `VerificationMode` enum: `NONE`, `GUARDED`, `STRICT`, `INTERPRETIVE`, `SPECULATIVE`
- `TriggerEngine` class:
  - `detect_mode(query: str, draft: str, context: dict) -> VerificationMode`
  - Triggers: dates/numbers/named entities, mixed domains, low source confidence,
    strong certainty language ("always", "never", "all", "proved"), code for execution
  - Non-triggers: casual chat, short reflective, strong retrieval confidence
- `smart_complete_with_cove()` calls `TriggerEngine.detect_mode()` and routes to
  appropriate verification depth
- `NONE` mode skips Vörðr entirely (performance path)
- `STRICT` mode runs full pipeline: extraction + bundling + support + contradiction +
  repair + truth profile

**Tests**: 20 tests in `tests/test_vordur_trigger.py`.

---

### Step E-38 — Mímir-Vörðr v2: Domain-Specific Validators
**Module**: `vordur.py`
**Source**: `mimir-vordr-v2-proposal.md` §9

Specialized truth-checking per knowledge domain.

**Deliverables**:
- `DomainValidator` abstract base class
- `CodeValidator(DomainValidator)`: syntax check (ast.parse), import correctness,
  schema conformance where applicable
- `HistoricalValidator(DomainValidator)`: primary source alignment, era-specific
  distinctions, universal-claim penalty
- `SymbolicValidator(DomainValidator)`: tradition-bound interpretation check,
  explicit labeling of interpretive vs. direct-source claims
- `ProceduralValidator(DomainValidator)`: ordered steps, dependency consistency
- Validators invoked based on `ClaimType` and detected domain
- All validators are best-effort (exceptions fall back to generic scoring)

**Tests**: 25 tests across all four validators in `tests/test_vordur_domain_validators.py`.

---

## Progress Tracker

| Step | Name | Module(s) | Status |
|------|------|-----------|--------|
| E-01 | Prompt Injection Sentinel | `security.py` | ✅ DONE |
| E-02 | Sensitive Data Masking | `comprehensive_logging.py` | ✅ DONE |
| E-03 | Vörðr Unicode Regex | `vordur.py` | ✅ DONE |
| E-04 | StateBus Backpressure Warning | `state_bus.py` | ✅ DONE |
| E-05 | WyrdMatrix Exponential Decay | `wyrd_matrix.py` | ✅ DONE |
| E-06 | CPU Temp Fallback Windows | `metabolism.py` | ✅ DONE |
| E-07 | Metabolism ↔ Wyrd Vitality Link | `metabolism.py`, `wyrd_matrix.py` | ✅ DONE |
| E-08 | Honor-Driven Energy Reserve | `wyrd_matrix.py`, `metabolism.py` | ✅ DONE |
| E-09 | Ethical Scarring | `ethics.py` | ✅ DONE |
| E-10 | Value-Conflict Mediation | `ethics.py` | ✅ DONE |
| E-11 | Bio Stochastic Variance | `bio_engine.py` | ⏳ PENDING |
| E-12 | Variable Cycle Length | `bio_engine.py` | ⏳ PENDING |
| E-13 | Heartbeat Sentinel | `scheduler.py` | ⏳ PENDING |
| E-14 | Seasonal Awareness | `scheduler.py` | ⏳ PENDING |
| E-15 | Dream Tick Integration | `scheduler.py`, `dream_engine.py`, `mimir_well.py` | ⏳ PENDING |
| E-16 | Associative Memory Hooks | `memory_store.py` | ⏳ PENDING |
| E-17 | Emotional Significance Weighting | `memory_store.py` | ⏳ PENDING |
| E-18 | Synonym Expansion | `memory_store.py` | ⏳ PENDING |
| E-19 | Nightly Memory Consolidation | `memory_store.py`, `scheduler.py` | ⏳ PENDING |
| E-20 | TOD Vibe Shift | `environment_mapper.py` | ⏳ PENDING |
| E-21 | Sensory Hint Layer | `environment_mapper.py`, `prompt_synthesizer.py` | ⏳ PENDING |
| E-22 | Object State Tracking | `environment_mapper.py` | ⏳ PENDING |
| E-23 | Trust Facets | `trust_engine.py` | ⏳ PENDING |
| E-24 | Relational Milestones | `trust_engine.py` | ⏳ PENDING |
| E-25 | Trust Diminishing Returns | `trust_engine.py` | ⏳ PENDING |
| E-26 | BM25 Pre-Filter Layer 0 | `mimir_well.py` | ⏳ PENDING |
| E-27 | Axiom Integrity Sentinel | `mimir_well.py` | ⏳ PENDING |
| E-28 | Dynamic Section Reordering | `prompt_synthesizer.py` | ⏳ PENDING |
| E-29 | Skaldic Vocabulary Injection | `prompt_synthesizer.py` | ⏳ PENDING |
| E-30 | Actual Token Counting | `prompt_synthesizer.py` | ⏳ PENDING |
| E-31 | Hot-Reload Identity | `prompt_synthesizer.py` | ⏳ PENDING |
| E-32 | Vörðr Async + Verdict Cache | `vordur.py` | ⏳ PENDING |
| E-33 | v2: Claim Extraction + Typing | `vordur.py` | ⏳ PENDING |
| E-34 | v2: Evidence Bundling + Support | `vordur.py` | ⏳ PENDING |
| E-35 | v2: Repair Engine + Truth Profile | `vordur.py`, `model_router_client.py` | ⏳ PENDING |
| E-36 | v2: Contradiction Analyzer | `vordur.py` | ⏳ PENDING |
| E-37 | v2: Verification Modes + Trigger | `vordur.py`, `model_router_client.py` | ⏳ PENDING |
| E-38 | v2: Domain Validators | `vordur.py` | ⏳ PENDING |

---

## Dependency Map

```
E-01, E-02, E-03, E-04, E-05, E-06   (independent — do in any order)
E-07 requires E-05, E-06
E-08 requires E-07
E-09, E-10 (independent of above)
E-11, E-12 (independent)
E-13 (independent)
E-14 requires E-13
E-15 requires E-13, E-14
E-16 (independent)
E-17 requires E-05 (WyrdState access)
E-18 (independent)
E-19 requires E-16, E-13
E-20, E-21, E-22 (independent of each other)
E-23, E-24, E-25 (independent of each other)
E-26, E-27 (independent)
E-28 requires E-05 (WyrdState)
E-29 (independent)
E-30 (independent)
E-31 (independent)
E-32 requires E-03
E-33 requires E-32
E-34 requires E-33, E-26
E-35 requires E-34
E-36 requires E-34
E-37 requires E-33, E-35, E-36
E-38 requires E-33, E-37
```

---

## Estimated Scope by Wave

| Wave | Steps | Focus | Relative Effort |
|------|-------|-------|-----------------|
| 1 | E-01 – E-06 | Bug fixes + security | Low |
| 2 | E-07 – E-10 | Cross-module depth links | Low-Medium |
| 3 | E-11 – E-15 | Biological aliveness | Medium |
| 4 | E-16 – E-19 | Memory depth | Medium |
| 5 | E-20 – E-22 | Environment presence | Low-Medium |
| 6 | E-23 – E-25 | Relational intelligence | Medium |
| 7 | E-26 – E-31 | Knowledge & synthesis quality | Medium |
| 8 | E-32 – E-35 | Mímir-Vörðr v2 foundation | High |
| 9 | E-36 – E-38 | Mímir-Vörðr v2 full verification | High |

---

*Each step should follow the standard workflow:*
*read blueprint → plan → report to Volmarr → await approval → code → test → commit → push*
