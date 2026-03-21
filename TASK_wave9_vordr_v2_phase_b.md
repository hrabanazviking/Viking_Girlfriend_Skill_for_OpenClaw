# TASK_wave9_vordr_v2_phase_b.md — Wave 9: Mímir-Vörðr v2 Phase B (FINAL WAVE)
**Created**: 2026-03-21
**Branch**: development
**Module**: `vordur.py` (primary), `model_router_client.py` (E-37)

---

## Scope
Wave 9 (E-36–E-38) — 3 enhancements completing Mímir-Vörðr v2 full verification.
All land in `vordur.py`; E-37 also touches `model_router_client.py`.
60 total new tests across 3 files.

---

## Inventory

### E-36 — Contradiction Analyzer
- `ContradictionType` enum: `CLAIM_VS_SOURCE`, `INTER_SOURCE`, `INTRA_RESPONSE`,
  `TRADITION_DIVERGENCE`, `NONE`
- `ContradictionRecord` dataclass: `claim_ids: List[str]`, `chunk_ids: List[str]`,
  `contradiction_type: ContradictionType`, `severity: float`, `description: str`
- `ContradictionAnalyzer` class:
  - `analyze(claims, records, chunks) -> List[ContradictionRecord]`
  - `CLAIM_VS_SOURCE`: claim's NLI verdict is CONTRADICTED (from VerificationRecord)
  - `INTER_SOURCE`: two chunks that share overlapping topics but diverge significantly
  - `INTRA_RESPONSE`: same claim_type extracted multiple times with conflicting content
  - `TRADITION_DIVERGENCE`: symbolic/historical ClaimType with CONTRADICTED verdict
    → treated as PARTIALLY_SUPPORTED, not hallucination
  - `NONE`: no contradiction detected (returned as empty list)
- `TruthProfile` gains `contradictions: List["ContradictionRecord"]` field (default [])
- `_build_truth_profile()` in VordurChecker populates contradictions field

### E-37 — Verification Modes + Trigger Engine
- Extend `VerificationMode` enum (keep existing GUARDED/IRONSWORN/SEIÐR/WANDERER):
  - Add `NONE = "none"` — skip Vörðr entirely (performance path)
  - Add `STRICT = "strict"` — full pipeline (extract + bundle + support + contradiction + repair + truth)
  - Add `INTERPRETIVE = "interpretive"` — allow symbolic truth, tradition divergence = OK
  - Add `SPECULATIVE = "speculative"` — hedged claims treated as always NEUTRAL not CONTRADICTED
- Extend `get_mode_thresholds()` for new modes
- `TriggerEngine` class:
  - `__init__(config: dict = None)` — configurable thresholds
  - `detect_mode(query: str, draft: str, context: dict = None) -> VerificationMode`
  - Triggers → STRICT: dates/numbers/named entities, strong certainty language
    ("always", "never", "all", "proved", "proven", "fact"), code for execution,
    mixed domains, numbers/statistics
  - Triggers → INTERPRETIVE: symbolic/spiritual/mythic content
  - Triggers → SPECULATIVE: hedged language ("may", "perhaps", "probably")
  - Triggers → NONE: very short responses (<50 chars), casual greetings
  - Default: IRONSWORN (existing high-rigor mode)
- Update `smart_complete_with_cove()` in model_router_client.py:
  - Add `trigger_engine: Optional[Any] = None` param
  - After routing stage: call `trigger_engine.detect_mode(query, draft, {})` if provided
  - NONE mode: skip Stage 4 (Vörðr scoring) entirely
  - Other modes: pass detected VerificationMode to `vordur.score()`

### E-38 — Domain-Specific Validators
- `DomainValidator` abstract base class:
  - `domain: str` class attribute
  - `validate(claim: Claim, chunks: List[KnowledgeChunk]) -> Tuple[VerdictLabel, float, str]`
    → `(verdict, confidence, reason)`. Never raises.
- `CodeValidator(DomainValidator)`:
  - `domain = "code"`
  - `validate()`: attempts `ast.parse(claim.text)` — if SyntaxError → CONTRADICTED (0.8, "syntax error")
  - If no code-like content detected → NEUTRAL passthrough
  - Otherwise → ENTAILED (0.7, "code structure valid")
- `HistoricalValidator(DomainValidator)`:
  - `domain = "historical"`
  - `validate()`: checks for universal quantifiers ("all", "always", "every", "never")
    → downgrades to NEUTRAL (0.6, "universal claim in historical context")
  - If primary source keywords present ("edda", "saga", "chronicle", "according to")
    → ENTAILED boost (0.9)
  - Otherwise → NEUTRAL (0.5, "historical claim unconfirmed")
- `SymbolicValidator(DomainValidator)`:
  - `domain = "symbolic"`
  - `validate()`: symbolic/mythic claims are always INFERRED_PLAUSIBLE
  - Returns NEUTRAL (0.7, "symbolic interpretation") by default
  - No CONTRADICTED on symbolic claims (tradition divergence is OK)
- `ProceduralValidator(DomainValidator)`:
  - `domain = "procedural"`
  - `validate()`: checks for ordered step keywords ("first", "then", "next", "finally")
    present in both claim and any chunk → ENTAILED
  - Missing order words in chunks → NEUTRAL (0.5, "step order unverified")
- `_DOMAIN_VALIDATORS: Dict[str, DomainValidator]` module-level registry
- `get_domain_validator(claim_type: str) -> Optional[DomainValidator]`
- `VordurChecker.verify_claim()` checks for domain validator after cache check, before judge call;
  if validator returns non-UNCERTAIN verdict, use it (skip judge call)

---

## Test Files to Create

| File | Tests | Enhancement |
|------|-------|-------------|
| `tests/test_vordur_contradiction.py` | 15 | E-36 |
| `tests/test_vordur_trigger.py` | 20 | E-37 |
| `tests/test_vordur_domain_validators.py` | 25 | E-38 |

---

## Progress Tracker

- [x] TASK file committed
- [x] E-36 ContradictionAnalyzer implemented
- [x] E-37 TriggerEngine + VerificationMode extension + smart_complete_with_cove update
- [x] E-38 DomainValidators + registry + VordurChecker integration
- [x] All 3 test files written (63 tests)
- [x] Tests passing (443 total, 0 failures in Wave 9 files)
- [x] STATUS + memory + ENHANCEMENT_PLAN tracker updated
- [x] Committed and pushed

---

## File Paths
- `viking_girlfriend_skill/scripts/vordur.py` *(primary — all 3 enhancements)*
- `viking_girlfriend_skill/scripts/model_router_client.py` *(E-37: trigger_engine param)*
- `tests/test_vordur_contradiction.py` *(new)*
- `tests/test_vordur_trigger.py` *(new)*
- `tests/test_vordur_domain_validators.py` *(new)*
