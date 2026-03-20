# TASK: RAG Self-Correction Loop
# Created: 2026-03-20
# Status: PLANNING

## Concept (Volmarr's Idea)

After Sigrid generates a response, she should self-check it against her own
memory, knowledge, and ethics — and regenerate if the response is inconsistent
or misaligned. This is a RAG-powered (Retrieval-Augmented Generation) inner loop
that gives Sigrid a form of self-awareness about what she says.

Norse framing: Mimir's Well — before speaking, Sigrid drinks from her own
accumulated memory. If what she is about to say contradicts what she knows or
who she is, she draws it back and speaks again with corrected understanding.

---

## Architecture Design

The self-correction loop runs between Step 9 (router response) and Step 10
(memory record) in `_handle_turn()`. It is optional per request and only
fires when confidence criteria are met.

```
 ┌──────────────────────────────────────────────────────────────────┐
 │  smart_complete(messages) → first_response                        │
 │        ↓                                                          │
 │  SelfCorrectionChecker.check(                                     │
 │      user_text, first_response, memory_context, ethics_state     │
 │  ) → CorrectionResult                                            │
 │        ↓  (if needs_correction=True)                              │
 │  smart_complete(messages + correction_hint) → final_response     │
 └──────────────────────────────────────────────────────────────────┘
```

Max 1 correction pass — never recursive.
Correction uses the SAME tier as the original (no downgrade).

---

## New Components

### 1. `scripts/self_correction.py` (new module)

**`CorrectionResult` dataclass**:
```python
@dataclass
class CorrectionResult:
    needs_correction: bool
    reasons: List[str]          # human-readable reasons for correction
    correction_hint: str        # injected context for the re-generation
    rag_hits: List[str]         # episodic memory chunks that flagged the issue
    ethics_conflict: bool       # True if ethics evaluation triggered
    contradiction_score: float  # 0.0–1.0 how strongly the response contradicts memory
```

**`SelfCorrectionChecker` class**:
- `check(user_text, response_text, memory_context, ethics_state) → CorrectionResult`
- Uses three parallel signals:
  1. **RAG contradiction check** — retrieve top-N episodic memories relevant to
     the response, scan for direct contradictions (e.g., "I never said X" vs
     a stored memory that says she did)
  2. **Ethics alignment check** — run `ethics.evaluate_action(response_text)`;
     if `alignment_score < ethics_conflict_threshold` → flag for correction
  3. **Persona consistency check** — lightweight regex patterns for known
     persona violations (e.g., claiming to be male, denying Norse identity,
     claiming to be a different AI)
- Combines signals with configurable weights into `contradiction_score`
- Only triggers correction if `contradiction_score >= correction_threshold`
  (default 0.6) to avoid over-correcting normal responses
- On correction: builds `correction_hint` = a compact injected message:
  ```
  [SELF-CORRECT — internal, not shown to user]:
  Your previous response may conflict with known facts or your values.
  Relevant memory: {rag_hits joined}
  Ethics concern: {reason if any}
  Please regenerate with these facts in mind.
  ```

### 2. `memory_store.py` additions

**`MemoryStore.check_response_consistency(query, response_text) → List[str]`**
- Retrieves top-6 episodic memories relevant to both query AND response
- Returns list of memory strings that contain potential contradictions
- Uses keyword overlap for offline mode; ChromaDB semantic search when available
- Called by `SelfCorrectionChecker`

### 3. `model_router_client.py` additions

**`ModelRouterClient.smart_complete_with_correction(messages, checker) → CompletionResponse`**
- Wraps `smart_complete()` with one optional correction pass
- `checker: Optional[SelfCorrectionChecker]` — if None, skips correction
- Adds `correction_applied: bool` and `correction_reasons: List[str]` to
  `CompletionResponse`
- Logs correction events to the state bus as `router_correction` events

---

## Integration in `main.py`

In `_handle_turn()`, between steps 9 and 10:

```python
# Step 9 — router (existing)
result = router.smart_complete(messages)

# Step 9b — self-correction (NEW)
if correction_checker is not None:
    correction = correction_checker.check(
        user_text=clean_text,
        response_text=result.content,
        memory_context=memory_ctx,
        ethics_state=ethics.get_state(),
    )
    if correction.needs_correction:
        logger.info("Self-correction triggered: %s", correction.reasons)
        # Inject correction context and regenerate
        correction_messages = messages + [
            Message("system", correction.correction_hint),
        ]
        result = router.smart_complete(correction_messages)
        result.correction_applied = True
        result.correction_reasons = correction.reasons
```

---

## Configuration (model_router config block)

```yaml
self_correction:
  enabled: true
  correction_threshold: 0.60    # 0.0–1.0 contradiction score to trigger
  ethics_conflict_threshold: -0.3  # alignment_score below this triggers
  max_rag_hits: 6               # episodic memories to retrieve
  persona_check: true           # check for persona consistency violations
```

---

## Implementation Order

1. `memory_store.py` — add `check_response_consistency()` method
2. `self_correction.py` — new module: `CorrectionResult`, `SelfCorrectionChecker`
3. `model_router_client.py` — add `smart_complete_with_correction()`
4. `main.py` — wire `correction_checker` into `_handle_turn()`
5. `tests/test_self_correction.py` — test suite for all correction scenarios
6. Update `ops/launch_calibration.py` — add `scripts.self_correction` to import check

---

## Test Cases to Cover

- Response that contradicts a stored episodic memory → correction triggered
- Response with ethics violation (alignment_score < threshold) → triggered
- Response that claims wrong gender/identity → persona check triggers
- Normal accurate response → no correction (contradiction_score < threshold)
- Correction pass itself is factually correct → no second pass (max 1)
- `checker=None` → smart_complete runs unchanged (backward compatible)
- ChromaDB unavailable → falls back to keyword-based memory check

---

## Key Design Constraints

- Must NOT break the existing `smart_complete()` call (backward compatible)
- Max 1 correction pass — no recursion, no loops
- Correction prompt injected as `role=system` to keep it invisible to user
- `CompletionResponse` gains `correction_applied` and `correction_reasons` fields
  (default False / [] for backward compat)
- Self-correction always uses the same tier as the original call
- Persona check uses pure regex (no external call) — zero latency

---

## Session Resume Instructions

On session start: read this file → read existing `memory_store.py` (check_response_consistency),
`model_router_client.py` (smart_complete), `main.py` (_handle_turn) →
implement in order listed above → test → commit each module separately.
