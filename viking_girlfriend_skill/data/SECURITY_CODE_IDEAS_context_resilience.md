# SECURITY_CODE_IDEAS_context_resilience.md
# Code Implementation Ideas: Context Resilience & Security Hardening
**Authored by**: Runa Gridweaver
**Date**: 2026-03-21
**Implements gaps from**: SECURITY_RESEARCH_context_resilience.md

> **PLANNING ONLY — no pseudocode in .md files per CLAUDE.md rules.**
> All ideas below are design proposals. Await Volmarr's go-ahead before writing any Python.

---

## Priority 1 — G-01: Context Window Monitor + Soul Re-injection

**Target module**: `prompt_synthesizer.py` (primary), `model_router_client.py` (trigger point)

**Idea**: Add a `ContextGuard` class to `prompt_synthesizer.py` that:
1. Receives the full assembled prompt token count from the existing `_count_tokens()` call (E-30).
2. Compares it against a configurable threshold (e.g. 80% of 131,072 = ~104,858 tokens).
3. If threshold is exceeded:
   - Emits a `context.overflow_warning` event on `StateBus`.
   - Triggers **soul anchor re-injection**: calls a new `_build_soul_anchor_block()` method that assembles a compact version of `IDENTITY.md` + `SOUL.md` + `values.json` core constraints (target: ~2,000 tokens, not the full soul file).
   - The soul anchor block is prepended to the final prompt, pushing it back into attention range.
4. Optionally: triggers **dialogue compaction** — summarises the oldest N turns of dialogue history into a short memory entry, then removes the raw turns. This reclaims context space without losing continuity.

**Config keys to add in `security_config.json`**:
- `context_overflow_threshold_ratio` (float, default 0.80) — fraction of max context at which to act.
- `soul_anchor_enabled` (bool, default true) — whether to re-inject soul anchor.
- `dialogue_compaction_enabled` (bool, default true) — whether to compact old turns.
- `compaction_window_turns` (int, default 10) — how many old turns to collapse per compaction pass.
- `max_context_tokens` (int, default 104858) — absolute max; can be overridden per model.

**State bus events**:
- `context.overflow_warning` — published when threshold crossed.
- `context.soul_reinjected` — published after soul anchor block is added.
- `context.dialogue_compacted` — published after compaction, includes `turns_compacted` count.

**New method in `PromptSynthesizer`**:
- `_build_soul_anchor_block() -> str` — loads IDENTITY.md + SOUL.md summary sections + top 10 values from values.json, formats as compact system text block.
- `_compact_dialogue_history(turns: List[dict], n: int) -> Tuple[List[dict], str]` — returns `(remaining_turns, compaction_summary)`. Uses subconscious model tier to summarise.

**Tests to write**:
- `tests/test_context_guard.py` (new, ~15 tests):
  - `ContextGuard` initialises with default thresholds.
  - `check(token_count, max_tokens)` returns `ContextStatus(is_safe, ratio, action_needed)`.
  - Status is safe when ratio < threshold.
  - Status triggers action when ratio >= threshold.
  - `_build_soul_anchor_block()` returns non-empty string containing identity keywords.
  - Soul anchor block is under 3,000 tokens.
  - Event published when overflow threshold crossed.
  - Never raises on malformed input.

---

## Priority 2 — G-02: Hard Token Cap with Automatic Truncation

**Target module**: `prompt_synthesizer.py`

**Idea**: Promote `_count_tokens()` from a log-only call to an enforcement point in `build_prompt()`:
1. After assembling all sections, call `_count_tokens()` on the assembled prompt.
2. If count exceeds `max_context_tokens`:
   - Log a WARNING with the overage.
   - Truncate the *dialogue history section* (oldest turns first) until the count is under the cap.
   - If still over after removing all history, truncate RAG-retrieved knowledge chunks (keep soul/identity sections intact).
   - Never truncate the soul anchor block, identity section, or ethics section.
3. Add a `tokens_used: int` field to the `PromptBuildResult` returned by `build_prompt()` so callers can observe the final size.

**Section truncation priority order** (most truncatable → least):
1. Dialogue history (oldest turns)
2. RAG knowledge chunks
3. Environment block
4. Biological state
5. Memory episodic section
6. Wyrd matrix / ethics (compress to summary)
7. Soul/identity — NEVER truncated

**Config keys** (reuse from G-01 `security_config.json` additions):
- `max_context_tokens` — already proposed above.
- `protected_sections` (list of str, default `["identity", "soul", "ethics"]`) — never truncated.

**Tests to write**:
- `tests/test_prompt_truncation.py` (new, ~10 tests):
  - `build_prompt()` returns token count in result.
  - Prompt under cap → no truncation.
  - Prompt over cap → dialogue history reduced.
  - After truncation, `tokens_used <= max_context_tokens`.
  - Identity section always preserved after truncation.
  - Truncation event published on StateBus.

---

## Priority 3 — G-03: RAG Chunk Injection Scanning

**Target module**: `mimir_well.py` (retrieval path), `security.py` (scanner reuse)

**Idea**: In `MimirWell.retrieve()`, after fetching chunks from ChromaDB and before returning them for prompt injection, run each chunk's text through `InjectionScanner.scan()`. If a chunk returns `is_safe=False` with `threat_level >= "moderate"`:
1. Log a WARNING including `chunk_id` and `threat_level`.
2. Exclude the chunk from the returned results (filter it out).
3. Publish `security.rag_chunk_blocked` on StateBus with `chunk_id` and `threat_level`.
4. Increment a `rag_chunks_blocked` counter in `MimirState`.

**Why not alert and refuse the whole retrieval?** Because a single poisoned chunk in a large knowledge base should not break the whole RAG system — surgical removal is better than full refusal.

**Existing reuse**: `InjectionScanner` already exists in `security.py`. This is purely a wiring change in `mimir_well.py`.

**Config key**:
- `rag_injection_scan_enabled` (bool, default true) in `security_config.json`.
- `rag_injection_min_threat_level` (str, default "moderate") — minimum threat to block.

**New MimirState fields**:
- `rag_chunks_blocked: int` — lifetime count of blocked chunks.
- `last_blocked_chunk_id: Optional[str]` — for debugging.

**Tests to write**:
- `tests/test_mimir_rag_security.py` (new, ~10 tests):
  - Clean chunks pass through unchanged.
  - Chunk with injection pattern is removed from results.
  - `rag_chunks_blocked` counter increments.
  - `security.rag_chunk_blocked` event published.
  - Disabled by config → no scanning, no blocking.
  - Empty result set when all chunks are poisoned → returns empty list, no exception.

---

## Priority 4 — G-04: Response Size Capping

**Target module**: `model_router_client.py`

**Idea**: Add per-mode response size limits to `smart_complete_with_cove()` and the underlying `_route_completion()` call:
1. Define `_RESPONSE_SIZE_CAPS: Dict[str, int]` mapping conversation mode / verification mode to `max_tokens` values.
   - Casual greeting → 256 tokens
   - NONE verification mode → 512 tokens
   - Standard IRONSWORN → 1024 tokens
   - STRICT mode → 1500 tokens (more complex verification needed)
   - Uncapped (explicit tool use) → `_DEFAULT_MAX_TOKENS` (2048)
2. `TriggerEngine.detect_mode()` result from E-37 already determines the mode — reuse it to select the cap.
3. Pass the selected `max_tokens` to the LiteLLM completion call.

**This is low-risk and low-effort** — it reuses the E-37 TriggerEngine already in place.

**Config key**:
- `response_caps_by_mode` (dict, str → int) in `security_config.json` — allows overriding defaults.

**Tests to write** (extend `tests/test_model_router_client.py`):
- `_get_response_cap(VerificationMode.NONE)` returns <= 512.
- `_get_response_cap(VerificationMode.STRICT)` returns >= 1000.
- Cap is passed correctly to the completion kwargs.

---

## Priority 5 — G-05: Session File Integrity Verification

**Target module**: `runtime_kernel.py` (load time), new utility in `security.py`

**Idea**: Add a `SessionFileGuard` to `security.py`:
1. On session start (called from `runtime_kernel.py`), compute SHA-256 of all files in `session/`.
2. Store a manifest `session/.integrity_manifest.json` with `{filename: sha256_hash, timestamp}`.
3. On each subsequent session file *read*, optionally verify hash against manifest.
4. If mismatch: log WARNING, publish `security.session_file_tampered`, and reload from the last known-good backup (if any) or return empty defaults.

**Simpler version** (lower effort): Only verify the integrity of session files that contain text that could be injected into prompts:
- `session/last_dream.json` — dream content appears in prompt
- `session/association_cache.json` — associations appear in memory retrieval
- `session/object_states.json` — object state descriptions appear in environment block

Skip integrity checking on purely numeric/structural session files (`heartbeat.json`, `milestones.json` etc.) as these cannot carry injection payloads.

**Config key**:
- `session_integrity_check_enabled` (bool, default true).
- `session_integrity_text_files_only` (bool, default true) — only check text-injectable files.

**Tests to write**:
- `tests/test_session_integrity.py` (new, ~8 tests):
  - Manifest created on init.
  - Clean file passes verification.
  - Tampered file detected.
  - Tampered file triggers warning event.
  - Disabled config → no verification, no error.

---

## Priority 6 — G-08: Precise Token Budget (Minor Polish)

**Target module**: `memory_store.py`

**Idea**: Replace the `len(text) // 4` estimate in token budget enforcement with `litellm.token_counter()` (already imported in `prompt_synthesizer.py`). Import it in `memory_store.py` with a `len(text) // 4` fallback (matching E-30's pattern).

**Impact**: More accurate episodic and knowledge injection budgets — less risk of budget exhaustion or undershoot.

**No new tests needed** — existing budget tests cover the behaviour; only the internal calculation changes.

---

## Summary of Proposed Changes

| # | Gap | Module | Effort |
|---|-----|--------|--------|
| P-1 | G-01 Context monitor + soul re-injection | `prompt_synthesizer.py` | Medium-High |
| P-2 | G-02 Hard token cap + auto-truncation | `prompt_synthesizer.py` | Medium |
| P-3 | G-03 RAG chunk injection scan | `mimir_well.py` + `security.py` | Low |
| P-4 | G-04 Response size capping | `model_router_client.py` | Low |
| P-5 | G-05 Session file integrity | `security.py` + `runtime_kernel.py` | Medium |
| P-6 | G-08 Precise token budget | `memory_store.py` | Very Low |

**Recommended implementation order**: P-3 → P-4 → P-6 (low effort, high safety) → P-2 → P-1 → P-5

**Suggested test count**: ~53 new tests across 4 new test files + 1 extension.

---

## What This Does NOT Touch

- Sigrid's persona, soul files, or identity data (read-only base data).
- The ChromaDB knowledge base contents.
- The OpenClaw Node.js layer (Voyage AI risk on that side requires separate investigation by Volmarr in the OpenClaw config — out of scope for Python skill).
- Any existing passing tests — all changes are additive per CLAUDE.md Immutable Laws.
