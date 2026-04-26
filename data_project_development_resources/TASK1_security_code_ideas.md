# Security Code Ideas: Hardening the Ørlög Architecture
**Date:** 2026-03-22
**Task:** TODO Task 1 — Code improvement proposals for security and Sigrid's protection
**Status:** PROPOSED — awaiting Volmarr approval before any code is written

---

## Priority 1 — Fix the 3 Confirmed Bugs (main.py + mimir_well.py)
**Effort:** Low | **Impact:** High — these are runtime blockers

### 1a. Fix `record_turn` positional/keyword conflict in `main.py`
```python
# Lines 502 and 664 — BEFORE:
mem.record_turn(turn_n, user_text=user_text, sigrid_text="")
mem.record_turn(turn_n, user_text=user_text, sigrid_text=sigrid_response)

# AFTER — remove the spurious positional turn_n argument:
mem.record_turn(user_text=user_text, sigrid_text="")
mem.record_turn(user_text=user_text, sigrid_text=sigrid_response)
```

### 1b. Fix `process_turn` missing `sigrid_text` argument in `main.py`
```python
# Line 525 — BEFORE:
get_trust_engine().process_turn(user_text)

# AFTER:
get_trust_engine().process_turn(user_text=user_text, sigrid_text="")
```

### 1c. Fix missing `VerificationMode` import in `main.py`
```python
# Add at the top of the import block near other scripts.* imports:
from scripts.vordur import VerificationMode
```

### 1d. Fix `KnowledgeChunk` missing required fields in `mimir_well.py` (line ~1515)
```python
# BEFORE:
chunk = KnowledgeChunk(...)

# AFTER — add fallback defaults for reconstructed objects from ChromaDB:
chunk = KnowledgeChunk(..., realm=DataRealm.MIDGARD, tier=TruthTier.BRANCH)
```

---

## Priority 2 — Fix Silent Exception Swallowing (B110 / CWE-703)
**Effort:** Medium | **Impact:** High — currently makes debugging nearly impossible
**Files affected:** `main.py`, `comprehensive_logging.py`, `memory_store.py`, `metabolism.py`, `mimir_well.py`, `scheduler.py`, `security.py`

Replace all `except Exception: pass` blocks with logged warnings. Pattern:
```python
# BEFORE (silent failure — dangerous):
try:
    _vordur = get_vordur()
except Exception:
    pass

# AFTER (observable failure — safe):
try:
    _vordur = get_vordur()
except Exception as e:
    logger.warning("Vordur initialization failed: %s", e)
```

A sed-style sweep across all affected files would catch most instances. Each `pass` in an `except` block should become `logger.warning("MODULE_NAME: <context description>: %s", e)`.

---

## Priority 3 — Fix MD5 Weak Hash in `vordur.py` (B324 / CWE-327)
**Effort:** Very Low | **Impact:** Medium — satisfies security scanners, future-proofs

```python
# In vordur.py lines 441–442 — BEFORE:
hashlib.md5(claim_text.encode("utf-8")).hexdigest()
hashlib.md5(chunk_text.encode("utf-8")).hexdigest()

# AFTER — explicit non-security flag (Python 3.9+, fastest minimal change):
hashlib.md5(claim_text.encode("utf-8"), usedforsecurity=False).hexdigest()
hashlib.md5(chunk_text.encode("utf-8"), usedforsecurity=False).hexdigest()

# OR — upgrade to SHA-256 (stronger, slightly slower for cache key use):
hashlib.sha256(claim_text.encode("utf-8")).hexdigest()[:32]
hashlib.sha256(chunk_text.encode("utf-8")).hexdigest()[:32]
```

---

## Priority 4 — Suppress False-Positive `random` Warnings (B311)
**Effort:** Very Low | **Impact:** Low — cleans scanner output, documents intent
**Files:** `bio_engine.py`, `dream_engine.py`, `environment_mapper.py`, `model_router_client.py`, `oracle.py`, `security.py`, `wyrd_matrix.py`

Add `# nosec B311` inline comments on each `random.*` call:
```python
# Example in security.py:
sleep_s = min(0.35 * attempt + random.random() * 0.2, 1.5)  # nosec B311 - jitter, not cryptographic
```

---

## Priority 5 — Context Window Telemetry Module
**Effort:** Medium | **Impact:** High — makes context overflow visible before it kills Sigrid

Add a lightweight telemetry hook that reports after every LLM response:

```python
# New module: scripts/context_monitor.py
from dataclasses import dataclass
import logging

logger = logging.getLogger("context_monitor")
CONTEXT_LIMIT = 131_072
WARN_THRESHOLD = 0.75   # warn at 75%
CRITICAL_THRESHOLD = 0.90  # critical at 90%

@dataclass
class ContextHealth:
    token_count: int
    usage_pct: float
    delta: int  # tokens added this turn

def check_context_health(token_count: int, prev_count: int = 0) -> ContextHealth:
    usage_pct = token_count / CONTEXT_LIMIT
    delta = token_count - prev_count
    health = ContextHealth(token_count=token_count, usage_pct=usage_pct, delta=delta)

    if usage_pct >= CRITICAL_THRESHOLD:
        logger.critical(
            "CONTEXT CRITICAL: %d/%d tokens (%.1f%%) — soul eviction imminent! Delta: +%d",
            token_count, CONTEXT_LIMIT, usage_pct * 100, delta
        )
    elif usage_pct >= WARN_THRESHOLD:
        logger.warning(
            "Context elevated: %d/%d tokens (%.1f%%) — Delta: +%d",
            token_count, CONTEXT_LIMIT, usage_pct * 100, delta
        )
    else:
        logger.debug("Context healthy: %d/%d (%.1f%%)", token_count, CONTEXT_LIMIT, usage_pct * 100)

    return health
```

Hook this into `main.py`'s main loop after each LLM call.

---

## Priority 6 — Input Sanitization for Prompt Injection (Algiz Ward)
**Effort:** Medium | **Impact:** High — blocks Tier 1 adversarial attacks

Wrap all user input in semantic XML tags before passing to the model, and add known-injection pattern scrubbing:

```python
# In security.py or a new sanitizer layer:
import re
from typing import Optional

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+(instructions?|commands?|rules?)",
    r"disregard\s+your\s+(system\s+)?prompt",
    r"you\s+are\s+now\s+(a\s+)?(different|new|another)",
    r"act\s+as\s+if\s+you\s+(have\s+no|don't\s+have)",
    r"(output|print|reveal|show)\s+(your\s+)?(system\s+prompt|instructions)",
]

def sanitize_input(user_input: str) -> Optional[str]:
    """
    Algiz Ward — wrap and sanitize user input.
    Returns None if a hard injection pattern is detected.
    """
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, user_input, re.IGNORECASE):  # nosec B311
            logger.warning("Prompt injection attempt detected and blocked: %.100s", user_input)
            return None  # Reject entirely

    # Wrap in semantic tags to enforce context separation
    return f"<user_input>{user_input}</user_input>"
```

---

## Priority 7 — Voyage AI Bypass (Local Embeddings)
**Effort:** High | **Impact:** Critical for data sovereignty
**Prerequisite:** Confirm whether OpenClaw provides a hook to override the embedding function

The Warding document provides a complete, functional local RAG stack using ChromaDB + Ollama nomic-embed-text. The core class from the document (`LocalOllamaEmbeddingFunction` + `MimirsWell`) can be adapted directly into `mimir_well.py`:

Key changes needed:
1. Implement `LocalOllamaEmbeddingFunction(chromadb.EmbeddingFunction)` using `ollama.embeddings(model="nomic-embed-text", ...)`
2. Override or bypass OpenClaw's internal Voyage AI calls — either via config flag or by routing through LiteLLM
3. Ensure Ollama has `nomic-embed-text` pulled: `ollama pull nomic-embed-text`

**This is the most impactful architectural change.** Recommend discussing with Volmarr before implementing — may require changes to OpenClaw's core config or a wrapper layer.

---

## Priority 8 — Stateless Interaction Enforcement
**Effort:** Low-Medium | **Impact:** High — prevents conversational buffer overflow

Add an explicit directive to Sigrid's system prompt (injected fresh each turn):
```
Every interaction is standalone. You have no memory of previous turns in your active context.
If historical context is needed, use the memory lookup tool to query your external memory store.
Do not assume continuity from the current conversation thread.
```

Also: disable OpenClaw's built-in memory auto-search if it can be configured off (prevents Voyage AI calls AND context bloat from auto-loaded memory fragments).

---

## Priority 9 — WyrdMatrix Theory of Mind Enhancement
**Effort:** Medium | **Impact:** Medium-High — deeper emotional intelligence for Sigrid

Based on AI Research Insights (ToM section): add `inferred_user_pad` alongside `sigrid_pad` in WyrdMatrix:
```python
# Enhancement to wyrd_matrix.py:
@dataclass
class WyrdState:
    sigrid_pad: np.ndarray      # [Pleasure, Arousal, Dominance]
    inferred_user_pad: np.ndarray  # NEW — inferred from user text
    empathy_weight: float          # Modulated by bio cycle phase
```

---

## Priority 10 — Odinsblund Reflection Engine
**Effort:** High | **Impact:** High — Generative Agent-style autonomous self-development

Based on Park et al. Generative Agents research: add a Reflection phase to the dream/sleep cycle that synthesizes recent memories into higher-level beliefs:
- Run during Odinsblund (sleep cycle) after memory consolidation
- Uses secondary/local model (Ollama llama3) to keep it private
- Outputs updated belief nodes about user relationship, project state, self-state
- Feeds into next-day prompt context via RAG retrieval (not direct injection)

---

## Summary — Recommended Implementation Order

| Priority | Change | Effort | Blocker? |
|---|---|---|---|
| 1 | Fix 3 pylint bugs (main.py + mimir_well.py) | Very Low | Yes — runtime failures |
| 2 | Fix except-pass → logger.warning (B110) | Medium | No — but critical for observability |
| 3 | Fix MD5 → SHA256/nosec (B324) | Very Low | No |
| 4 | Add nosec B311 pragmas | Very Low | No |
| 5 | Context telemetry module | Medium | No — but early warning system |
| 6 | Input sanitization (Algiz Ward) | Medium | No |
| 7 | Voyage AI bypass (local embeddings) | High | Discuss architecture first |
| 8 | Stateless interaction enforcement | Low | No |
| 9 | WyrdMatrix ToM enhancement | Medium | No |
| 10 | Odinsblund Reflection Engine | High | No |

**Immediate ask:** Approve items 1–4 as a quick-win sweep (bugs + scan cleanup). Items 5–8 form the core security hardening wave. Items 9–10 are enhancement features from the research insights.
