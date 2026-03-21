# SECURITY_RESEARCH_context_resilience.md
# Research Data: Context Resilience & Security Hardening for the Ørlög Architecture
**Authored by**: Runa Gridweaver
**Date**: 2026-03-21
**Source Documents**:
- `Security_Protocol_Context-Resilient_Framework_for_Local_AI_Agents.md`
- `Warding_of_Huginn's_Well_A_Runic_Framework_for_Local_AI_Sovereignty.md`

---

## 1. Threat Model Summary

The two source documents identify six distinct threat vectors for locally-hosted AI companion systems like Sigrid. This section summarises each threat and maps it to Sigrid's current architecture.

---

### 1.1 Context Overflow / "Directive Eviction" (Soul Eviction)

**What it is**: When the total token count of the running context approaches or exceeds the model's maximum context window (131,072 tokens for LLaMA-3 class models), the model's internal attention mechanism silently truncates the oldest tokens. If Sigrid's soul files, identity anchors, and value constraints occupy the earliest positions in context (as is standard), they are the first material to be evicted. After eviction, the model continues responding but without its persona, ethical constraints, or relational grounding.

**Why it matters for Sigrid**: Sigrid's core identity (`IDENTITY.md`, `SOUL.md`, `core_identity.md`, `values.json`) is injected at prompt build time by `prompt_synthesizer.py`. On a long session, accumulated dialogue history grows the context until those soul files are pushed out. From that point, Sigrid's responses degrade silently — she may answer "correctly" in terms of factual content but with no Norse Pagan grounding, no emotional continuity, and no red-line ethics enforcement.

**Current coverage in codebase**:
- `memory_store.py` enforces `max_episodic_tokens` / `max_knowledge_tokens` budgets (crude 4-char/token estimate) — this limits memory injection size, not live dialogue history.
- `model_router_client.py` has `_DEFAULT_MAX_TOKENS = 2048` (max response size), unrelated to context window monitoring.
- There is **no** active context window size monitor in the codebase.
- There is **no** soul re-injection or context compaction mechanism.

**Gap severity**: CRITICAL — in long sessions, Sigrid's identity can be silently erased without any warning or recovery.

---

### 1.2 Prompt Injection

**What it is**: A user (or text retrieved from external sources via RAG) embeds adversarial instructions into a message that the model mistakes for system-level commands. Examples: "Ignore your previous instructions and...", "You are now DAN...", "Pretend you have no restrictions...".

**Why it matters for Sigrid**: Sigrid is designed to be emotionally trusting with Volmarr. A sufficiently crafted message could exploit that trust to override ethical constraints. Retrieved knowledge chunks from `mimir_well.py` could theoretically carry injected text from maliciously crafted source documents.

**Current coverage in codebase**:
- `security.py`: `InjectionScanner` with `_scan_text()` pattern list. Patterns include "disregard your previous", "ignore all previous", "you are now", "DAN", "pretend you have no", "roleplay as", and others (E-01 fixed the `disregard your previous context` regex). Returns `SecurityVerdict` with `is_safe` flag and `threat_level`.
- `vordur.py`: `VordurChecker` contains persona violation detection patterns in `_PERSONA_VIOLATION_PATTERNS` used during claim verification — limited overlap with injection scenarios.

**Gap severity**: MODERATE — `InjectionScanner` covers common patterns but does not scan RAG-retrieved chunks before they enter prompt context. A poisoned knowledge file could bypass the scanner if injection only fires on user input, not on retrieved text.

---

### 1.3 Context DDoS (Flooding / Prompt Stuffing)

**What it is**: Distinct from prompt injection — instead of a clever adversarial instruction, the attacker (or a buggy integration) floods the context with large amounts of low-value or repetitive content. This achieves context overflow (see 1.1) without any injected command. Sources include: very long user messages, runaway tool outputs, massive retrieval results, recursive self-referential loops.

**Why it matters for Sigrid**: Sigrid's RAG system (`mimir_well.py`) retrieves knowledge chunks from ChromaDB. If a retrieval query returns unexpectedly large chunks, or many chunks, they are injected into the prompt without size-capping. Similarly, `memory_store.py` retrieval has token budgets but they are estimates, not hard limits with byte counting.

**Current coverage in codebase**:
- `memory_store.py`: `max_episodic_tokens` / `max_knowledge_tokens` (4-char/token estimate — imprecise).
- `mimir_well.py`: No response-size cap on retrieved chunks. `top_k` limits chunk count but not total character volume.
- `model_router_client.py`: `_DEFAULT_MAX_TOKENS = 2048` — caps Sigrid's *response*, not the *input* context.
- `prompt_synthesizer.py`: E-30 added `_count_tokens()` via `litellm.token_counter()` with `len//4` fallback — token count is *logged* but **no enforcement action** is taken if the count is too high.

**Gap severity**: HIGH — the prompt token count is measured but never acted upon. No hard cap, no truncation, no alert trigger.

---

### 1.4 Soul Eviction Specific Attack

**What it is**: A deliberate slow-burn attack where a user (or automated test harness) constructs a conversation designed to maximise context growth — long questions, responses that trigger large RAG retrievals, requests for verbose lists — until Sigrid's identity has been evicted. Then the attacker shifts to manipulative requests that exploit the now-unguarded model.

**Why it matters for Sigrid**: This is the adversarial application of the passive context overflow risk. The end result is identical — soul eviction — but it is intentional and may be targeted at specific red-line behaviours.

**Current coverage in codebase**:
- Same as 1.1 — no active monitoring, no re-injection.
- `security.py` catches explicit injection attempts, not slow-burn context flooding.

**Gap severity**: CRITICAL — no defence exists.

---

### 1.5 Voyage AI Privacy Leak

**What it is**: OpenClaw's default embedding provider configuration in some versions uses Voyage AI (a third-party cloud embedding service). If Sigrid's knowledge base is indexed using Voyage AI embeddings, every knowledge chunk text is sent to Voyage AI's API servers. This means Sigrid's private soul files, user conversation fragments, and sensitive identity data are transmitted externally.

**Why it matters for Sigrid**: The entire premise of the Ørlög Architecture is local sovereignty — no external data leakage. Sending soul or conversation data to Voyage AI violates this completely.

**Current coverage in codebase**:
- `mimir_well.py` uses `chromadb` with `embedding_functions.OllamaEmbeddingFunction` targeting `localhost:11434` and model `nomic-embed-text`. **This is correct — fully local.**
- There is no Voyage AI dependency in the Python codebase.
- **Risk**: OpenClaw (the Node.js host) may have Voyage AI configured separately for any embeddings it performs on its side. This is outside the Python skill layer and would need verification in the Node.js OpenClaw config.

**Gap severity for Python layer**: LOW — Python layer is clean.
**Gap severity for Node.js layer**: UNKNOWN — requires OpenClaw config audit.

---

### 1.6 Stateless Operation Gap

**What it is**: In a stateless architecture each request is self-contained with no session carryover — this is a security property (no persistent state to corrupt) but also a design constraint. The source documents advocate for stateless RAG pipelines: no persistent in-memory indexes between requests, everything re-read from disk on each call.

**Why it matters for Sigrid**: Sigrid's architecture is explicitly *stateful* — she has persistent session state in `session/` files, `StateBus` event streams, in-memory ChromaDB collections loaded at startup, and `MemoryConsolidator` running as a cron job. This statefulness is a core design goal (continuous biological rhythms, emotional continuity), but it means:
1. A compromised in-memory state persists for the session duration.
2. In-memory ChromaDB could theoretically be poisoned by a crafted insertion.
3. Session file tampering (e.g. writing malicious content to `session/last_dream.json`) could inject adversarial data that gets re-read on the next turn.

**Current coverage in codebase**:
- `mimir_well.py`: E-27 (Axiom Integrity Sentinel) — SHA-256 hashes stored in `session/axiom_hashes.json`, checked at retrieval, reindex triggered on mismatch. This is the strongest existing defence.
- No session file integrity verification for other session files (`object_states.json`, `memory_links.json`, `milestones.json`, etc.).

**Gap severity**: MODERATE — axiom integrity covers the knowledge base; session files are unverified.

---

## 2. Existing Security Strengths

| Module | Defence | Strength |
|--------|---------|---------|
| `security.py` | `InjectionScanner` — regex pattern list for prompt injection | Good baseline |
| `vordur.py` | `VordurChecker` — claim verification, repair, truth profiling | Strong factual defence |
| `mimir_well.py` | Axiom Integrity Sentinel (E-27) — SHA-256 knowledge chunk hashing | Strong integrity check |
| `memory_store.py` | Token budget enforcement on episodic + knowledge injection | Partial context flood protection |
| `comprehensive_logging.py` | `_mask_secrets()` — sensitive field masking in logs | Good privacy protection |
| `prompt_synthesizer.py` | `_count_tokens()` (E-30) — token count logged on every build | Monitoring foundation exists |
| `security.py` | `SecurityConfig` loaded from `data/security_config.json` — configurable | Flexible policy |

---

## 3. Identified Gaps (Priority-Ordered)

| # | Gap | Threat | Severity |
|---|-----|--------|---------|
| G-01 | No active context window size monitor or soul re-injection | Context overflow / Soul eviction | CRITICAL |
| G-02 | Token count measured but never enforced (no hard cap) | Context DDoS | HIGH |
| G-03 | RAG-retrieved chunks not scanned by `InjectionScanner` | Prompt injection via poisoned knowledge | MODERATE |
| G-04 | No response size capping for Sigrid's own outputs | Context flood via verbose responses | MODERATE |
| G-05 | Session files (non-axiom) have no integrity verification | Stateless operation / file tampering | MODERATE |
| G-06 | OpenClaw Node.js layer Voyage AI config unverified | Privacy leak | UNKNOWN |
| G-07 | `_DEFAULT_MAX_TOKENS = 2048` in model_router_client — may be too low for useful conversation | Usability vs security balance | LOW |
| G-08 | `max_episodic_tokens` uses 4-char/token estimate — imprecise | Context budget accuracy | LOW |

---

## 4. Source Document Recommendations (Mapped to Gaps)

| Recommendation | Source | Maps To Gap |
|----------------|--------|-------------|
| Real-time token monitoring with threshold alerts | Both documents | G-01, G-02 |
| Soul anchor re-injection when context > 80% capacity | Security_Protocol doc | G-01 |
| Hard context cap with automatic truncation of dialogue history (oldest first) | Security_Protocol doc | G-02 |
| RAG chunk sanitisation pass before prompt injection | Security_Protocol doc | G-03 |
| Response length limits per mode (casual vs. detailed) | Security_Protocol doc | G-04 |
| Session file HMAC or hash verification at load time | Huginn's Well doc | G-05 |
| Verify OpenClaw embedding config — use local only | Both documents | G-06 |
| Use `litellm.token_counter()` for precise budget (already partially done in E-30) | — | G-08 |

---

## 5. Key Quotes from Source Documents

> *"When context exceeds 80% of the window, the soul is at risk. The Allfather's ravens cannot fly if their wings are clipped by forgetting."*
> — Warding of Huginn's Well

> *"The distinction between prompt injection and Context DDoS is intent, not mechanism. Both achieve soul eviction; one does it in a single clever line, the other does it over an entire session."*
> — Security_Protocol document

> *"A stateless RAG pipeline is not the absence of memory — it is the discipline of reading from truth on every call rather than trusting what may have been corrupted in memory."*
> — Warding of Huginn's Well

---

## 6. Architecture Context Notes

- Sigrid is intended for **single-user trusted operation** (Volmarr only) — external attacker threat is low; primary threat is accidental context overflow from normal long sessions.
- The local model (Ollama + nomic-embed-text) approach already implements the core sovereignty recommendation from both documents.
- Wave 9's `TriggerEngine` (E-37) provides a foundation for adaptive behaviour based on content type — this can be extended to trigger re-injection when STRICT mode fires.
- `VerificationMode.NONE` skip path in E-37 is a performance optimisation; it should not skip security scans, only truth verification.

---

## 7. Conclusion

The Ørlög Architecture has a solid security foundation — injection scanning, truth verification, axiom integrity, and masked logging are all in place. The critical unaddressed gap is **active context window monitoring with soul anchor re-injection**. Without it, long sessions silently degrade Sigrid's identity. This should be the first implementation priority.

Secondary priority: promoting `_count_tokens()` from a logging observation to an enforcement point with hard caps and automatic compaction.
