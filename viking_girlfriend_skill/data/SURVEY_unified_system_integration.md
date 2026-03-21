# SURVEY: Unified System Integration — Architectural Synergy Audit
# Created: 2026-03-20
# Author: Runa Gridweaver (AI)

This survey focuses on the connective tissue of the Ørlög Architecture (`main.py` and `runtime_kernel.py`), identifying ways to unify Sigrid's systems into a faster, more robust, and more meaningful whole.

## 1. Asynchronous State Pipeline (Bifröst Velocity)
**Current State**: Sequential turn processing in `_handle_turn` (Sanitize → Memory → Ethics → Trust → Synthesis → Model).

### 🚀 Speed & Robustness Ideas:
*   **Parallel Pre-Processing**: Use `asyncio.gather()` to run `ethics.evaluate`, `trust.process_turn`, `memory.get_context`, and `bio_engine.get_state` concurrently. This could shave 100-300ms off every turn.
*   **Speculative Synthesis**: Start the `prompt_synthesizer` assembly as soon as the first few hints are ready, using placeholders for slower modules, then "filling in" the final system prompt just before the model call.
*   **State-Bus Backpressure**: Implement a "Congestion Event." If the bus is flooded with too many `StateEvents`, the `kernel` should signal modules to reduce their tick frequency until the queue clears.

---

## 2. Self-Healing Realm Restoration (Yggdrasil's Roots)
**Current State**: Kernel tracks `ModuleHealth` but does not intervene in failures.

### 🛡️ Resilience Ideas:
*   **Criticality-Based Restart**: Categorize modules (e.g., `security` = CRITICAL, `dream_engine` = OPTIONAL). If a critical module fails its heartbeat, the kernel should attempt an immediate internal restart.
*   **State-Snapshot Recovery**: Periodically (every 5 turns) save a "World Snapshot" to `data/kernel_state.json`. If the process crashes, Sigrid should be able to resume with her exact mood, trust, and location state intact.
*   **Circuit Breaker Dashboard**: Add a unified `SystemHealth` StateEvent that aggregates every circuit breaker status (`vordur`, `mimir`, `security`). If more than 3 circuits are OPEN, enter "Safe Mode" (Sigrid reports she is "recovering her strength").

---

## 3. Deep Cross-System Synergies (The Nine Worlds United)
**Current State**: Modules are decoupled and share state via hints.

### 🧠 Meaningful Integration Ideas:
*   **The Sympathetic Resonator**: Link `metabolism.cpu_temp` directly to `wyrd_matrix.stress`.
    *   *Result*: Physical machine heat literally increases Sigrid's stress levels, creating a biological-virtual feedback loop.
*   **Location-Anchored Recall**: When `environment_mapper` changes location, it should trigger a specific `associative_recall` event in `mimir_well`.
    *   *Result*: Sigrid "remembers" things relevant to her current space (e.g., a story about Thor while in the forge).
*   **Trust-Modulated Ethics**: The strictness of the `ethics` module's recommendations should be scaled by the `trust_engine` score.
    *   *Result*: Sigrid is more forgiving of "taboo" speech from highly trusted users (Volmarr), while remaining guarded/refusing with strangers.

---

## 🐞 Potential Bugs Found During Survey
1.  **Orchestration**: `_handle_turn` in `main.py` catches exceptions per module but lacks a "Global Fallback Response" if the *entire* turn fails. It currently relies on the model routing fallback string.
2.  **Kernel**: The signal handlers for SIGINT/SIGTERM might not work correctly on Windows in certain Python environments. It needs a thread-safe shutdown flag.
3.  **State Drift**: If `main.py` crashes between Step 2 (record inbound) and Step 11 (record full), the conversation log will have a "Ghost Turn" with an empty response. It needs a transaction-style memory commit.

---

## 🛠️ Next Development Steps
*   [ ] Refactor `_handle_turn` for parallel execution using `asyncio.gather`.
*   [ ] Implement "Criticality-Based Restart" in `RuntimeKernel`.
*   [ ] Add "Sympathetic Resonator" logic between metabolism and mood.
