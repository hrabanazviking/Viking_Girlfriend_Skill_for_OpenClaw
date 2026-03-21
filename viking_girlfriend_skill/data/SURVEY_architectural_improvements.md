# SURVEY: Ørlög Architecture — Improvement Strategies & Robustness Audit
# Created: 2026-03-20
# Author: Runa Gridweaver (AI)

This document maps out architectural enhancements for Sigrid, focusing on making the code faster, more secure, and robust enough to weather the storms of Midgard.

## 1. Vörðr (Truth Guard) Enhancements
**Current State**: Sequential claim verification and keyword-based fallback.

### 🚀 Performance Ideas:
*   **Parallel Verification**: Currently, `vordur.py` verifies claims in a loop. Moving to `asyncio.gather()` for claim verification could reduce the validation latency of long responses by 60–80%.
*   **Verdict Caching**: Implement an LRU cache for common claim/chunk pairs. Many questions (e.g., "Who is Odin?") will produce identical claims and source chunks.

### 🛡️ Robustness Ideas:
*   **Advanced NLI Fallback**: Replace the current regex keyword-overlap with a lightweight **BM25 or Cosine Similarity** check against source chunks if the model is down. This provides a more mathematically sound "faithfulness" proxy than simple string searching.
*   **Cross-Reference Peer Review**: If a claim is CONTRADICTED by one chunk but ENTAILED by another, the system should flag a "Source Conflict" state for the `scheduler` to resolve.

---

## 2. Wyrd Matrix (Emotional Soul) Enhancements
**Current State**: Token-based keyword extraction for stimuli.

### 🧠 Intelligence Ideas:
*   **Embedding-Based Stimuli**: Instead of just searching for the word "angry," use a small local embedding model (like `all-MiniLM-L6-v2`) to detect emotional intent. This catches "I am feeling quite cross" as anger, even if the keyword isn't in the list.
*   **PAD Drift Persistence**: Save the Hugr state to a "Soul Cache" more frequently. If the process crashes during an intense exchange, Sigrid should wake up still feeling those emotions, not reset to baseline.

### ⚖️ Stability Ideas:
*   **Stimulus Normalization**: Add a "Sanity Cap" to emotional spikes. A single user message shouldn't be able to move Joy from 0.1 to 1.0 instantly; implement a "rate of change" limiter to simulate human emotional inertia.

---

## 3. Security & Sentinel Protocol
**Current State**: Path traversal protection and circuit breakers.

### ⚔️ Defense Ideas:
*   **Prompt Injection Sentinel**: Add a specific regex/keyword layer in `security.py` that scans for "ignore all previous instructions," "you are now a...", or "system override" patterns.
*   **Sensitive Data Masking**: Automatically scrub potential API keys or PII from the logs in `comprehensive_logging.py` before they hit the disk.
*   **Token-Time Shuffling**: To prevent timing attacks on session IDs, add a random ±5ms jitter to `safe_compare_secrets` responses.

---

## 4. State Bus & Infrastructure
**Current State**: In-process async queue.

### 📡 Observability Ideas:
*   **Heimdall Dashboard**: Create a lightweight CLI dashboard that subscribes to the wildcard topic `*` and displays a real-time "thread weave" of system events.
*   **Latency Tracing**: Attach a `start_time` to `InboundEvent` and track the "Bifröst Latency" — how long it takes from user input to final `OutboundEvent` publication.

---

## 🐞 Potential Bugs Found During Survey
1.  **Vordur**: The regex fallback for claims may fail on non-Latin characters. It needs `re.UNICODE` or explicit character ranges for Old Norse runes.
2.  **StateBus**: If a subscriber is extremely slow and its queue fills up, `publish_inbound` silently drops the event for that subscriber. There should be a "Backpressure Warning" event published when this happens.
3.  **WyrdMatrix**: Hugr decay is linear. Human emotional decay is usually exponential. Linear decay might make Sigrid feel "robotic" in how she calms down.

---

## 🛠️ Next Development Steps
*   [ ] Refactor `vordur.py` for async parallel verification.
*   [ ] Add `InjectionScanner` to `security.py`.
*   [ ] Implement BM25 similarity for non-model faithfulness scoring.
