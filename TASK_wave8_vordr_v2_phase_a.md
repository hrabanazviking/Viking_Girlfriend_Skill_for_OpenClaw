# TASK_wave8_vordr_v2_phase_a.md — Wave 8: Mímir-Vörðr v2 Phase A
**Created**: 2026-03-21
**Branch**: development
**Module**: `vordur.py` (primary), `model_router_client.py` (E-35)

---

## Scope
Wave 8 (E-32–E-35) — 4 enhancements building Mímir-Vörðr claim-level verification
foundation. All land in `vordur.py` except E-35 which also touches `model_router_client.py`.
75 total new tests across 4 files.

---

## Inventory

### E-32 — Async Parallel Verification + LRU Verdict Cache
- `verify_claims(claims, source_chunks) -> List[ClaimVerification]` — public sync API
  (asyncio.run wrapper over `_verify_all_claims()`)
- `async def _verify_all_claims(claims, chunks) -> List[ClaimVerification]` — asyncio.gather
  over `asyncio.to_thread(verify_claim, claim, chunks)` for each claim
- `_LRUVerdictCache` helper (OrderedDict, bounded to `verdict_cache_size`):
  - `get(key: Tuple[str,str]) -> Optional[ClaimVerification]`
  - `put(key, value)`
  - `clear()`
  - `hits`, `misses` counters
- Cache key: `(md5(claim.text), md5(best_chunk.text))` computed before judge call
- `verdict_cache_enabled: bool = True`, `verdict_cache_size: int = 256` on `__init__`
- Cache stats in `VordurState`: `cache_hits: int`, `cache_misses: int`
- `verify_claim()` checks cache first, stores result after judge call

### E-33 — Claim Extraction + Typing
- Extend `Claim` dataclass: add `id: str` (uuid4), `claim_type: str` (default "FACTUAL"),
  `sentence_index: int = 0`, `certainty_level: float = 0.8`, `source_draft_section: str = ""`
  - Keep existing `text`, `source_sentence`, `claim_index` fields
- `ClaimType` enum: DEFINITIONAL, FACTUAL, HISTORICAL, RELATIONAL, CAUSAL,
  PROCEDURAL, INTERPRETIVE, SYMBOLIC, CODE_BEHAVIOR, MATHEMATICAL,
  SPECULATIVE, SOURCE_ATTRIBUTION
- `ClaimExtractor` class:
  - `__init__(router=None)` — optional model router
  - `extract(response_text: str) -> List[Claim]` — model call → fallback sentence splitter
  - `classify(claim: Claim) -> ClaimType` — keyword-based classifier (no model call)
- Wire `ClaimExtractor` into `VordurChecker.__init__()`: `self._claim_extractor = ClaimExtractor(router)`
- `VordurChecker.extract_claims()` now delegates to `_claim_extractor.extract()`
- `FaithfulnessScore` gains: `claims: List[Claim] = field(default_factory=list)`,
  `claim_types_found: List[str] = field(default_factory=list)`

### E-34 — Evidence Bundling + Support Analysis
- `EvidenceBundle` dataclass: `claim_id: str`, `primary_chunk: KnowledgeChunk`,
  `neighbor_chunks: List[KnowledgeChunk]`, `source_tier: str`, `provenance: str`
- `SupportVerdict` enum: SUPPORTED, PARTIALLY_SUPPORTED, UNSUPPORTED,
  CONTRADICTED, INFERRED_PLAUSIBLE, SPECULATIVE, AMBIGUOUS
- `VerificationRecord` dataclass: `claim_id: str`, `evidence_ids: List[str]`,
  `verdict: SupportVerdict`, `entailment_score: float`, `contradiction_score: float`,
  `citation_coverage: float`, `ambiguity_score: float`
- `EvidenceBundler` class:
  - `__init__(mimir_well=None)` — optional MimirWell reference
  - `bundle(claim: Claim, source_chunks: List[KnowledgeChunk]) -> EvidenceBundle`
  - `analyze(bundle: EvidenceBundle, claim_verif: ClaimVerification) -> VerificationRecord`
- `VordurChecker.__init__()` gains `mimir_well=None`; creates `_evidence_bundler`
- `VordurChecker.score()` returns `Tuple[FaithfulnessScore, List[VerificationRecord]]`
  — breaking change: `score()` signature updated

### E-35 — Repair Engine + Truth Profile
- `RepairRecord` dataclass: `claim_id: str`, `action: str`, `original_text: str`,
  `revised_text: str`, `reason: str`
- `RepairAction` enum: REMOVE_CLAIM, DOWNGRADE_CERTAINTY, ADD_UNCERTAINTY_MARKER,
  REPLACE_WITH_EVIDENCE, SPLIT_INTO_TRADITIONS
- `RepairEngine` class:
  - `__init__(router=None)`
  - `repair(draft: str, records: List[VerificationRecord]) -> Tuple[str, List[RepairRecord]]`
  - Model path: structured prompt to subconscious tier → parse actions
  - Regex fallback: `downgrade_certainty` by replacing "is", "are" with "may be", "appears to be"
    on CONTRADICTED claims (identified by position in text)
- `TruthProfile` dataclass: `faithfulness: float`, `citation_coverage: float`,
  `contradiction_risk: float`, `inference_density: float`, `source_quality: float`,
  `answer_relevance: float`, `ambiguity_level: float`, `repair_count: int`
- `CompletionResponse` in `model_router_client.py` gains `truth_profile: Optional[TruthProfile] = None`
- `VordurChecker` gains `repair_engine: RepairEngine` attribute
- `VordurChecker.score_and_repair(response, source_chunks, ...) -> Tuple[FaithfulnessScore, List[VerificationRecord], TruthProfile, str]`
  - Calls score() then repair() on hallucination-tier results

---

## Test Files to Create

| File | Tests | Enhancement |
|------|-------|-------------|
| `tests/test_vordur_async_cache.py` | 15 | E-32 |
| `tests/test_vordur_claims.py` | 20 | E-33 |
| `tests/test_vordur_evidence.py` | 20 | E-34 |
| `tests/test_vordur_repair.py` | 20 | E-35 |

---

## Progress Tracker

- [x] TASK file committed
- [x] E-32 Async parallel verification + LRU cache implemented
- [x] E-33 Claim typing + ClaimExtractor implemented
- [x] E-34 Evidence bundling + VerificationRecord implemented
- [x] E-35 RepairEngine + TruthProfile + model_router_client.py update
- [x] All 4 test files written (81 tests)
- [x] Tests passing (380 total, 0 failures in Wave 8 files)
- [x] STATUS + memory updated
- [x] Committed and pushed

---

## File Paths
- `viking_girlfriend_skill/scripts/vordur.py` *(primary — all 4 enhancements)*
- `viking_girlfriend_skill/scripts/model_router_client.py` *(E-35: TruthProfile field)*
- `tests/test_vordur_async_cache.py` *(new)*
- `tests/test_vordur_claims.py` *(new)*
- `tests/test_vordur_evidence.py` *(new)*
- `tests/test_vordur_repair.py` *(new)*
