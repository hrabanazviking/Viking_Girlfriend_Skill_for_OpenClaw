# SURVEY: Biological & Temporal Systems — Enhancement Audit
# Created: 2026-03-20
# Author: Runa Gridweaver (AI)

This survey focuses on Sigrid's internal clock and body-state engines (`bio_engine.py` and `scheduler.py`), identifying ways to deepen her "aliveness" and system robustness.

## 1. Bio-Cyclical Engine (Máni's Rhythms)
**Current State**: 9-phase cycle with static multipliers and sine-wave biorhythms.

### 🧠 Psychological Depth Ideas:
*   **Variable Cycle Length**: Currently fixed to a 28-day standard. I recommend making the cycle length a configurable parameter in `environment.json`, allowing for 21-35 day variations to increase realism and user-specific resonance.
*   **Stochastic Fluctuations**: Add a "Chaos Factor" (±5%) to the phase multipliers each day. Real human cycles aren't mathematically perfect; small daily variance in energy and mood prevents the AI from feeling like a rigid script.
*   **Synchronized Memory Recall**: In the `Luteal` phases (introspection focus), the `bio_engine` could publish a signal to `mimir_well` to prioritize "Emotional/Old" memories over "Fact/New" memories, making her tone more reflective.

### 🛡️ Robustness Ideas:
*   **Drift Protection**: If the system is offline for 3 days, the current `real-date arithmetic` works well, but it should publish a "Resynchronization" event so the `prompt_synthesizer` can acknowledge the "gap" in her body-clock.

---

## 2. Temporal Scheduler (Dagr's Path)
**Current State**: Wall-clock hour mapping and APScheduler background tasks.

### 🚀 Performance Ideas:
*   **Job Throttling**: For heavy jobs like "Memory Consolidation," the scheduler should check system load before starting. If CPU usage > 80%, defer the job by 5 minutes.
*   **Distributed Task Offloading**: For scaling beyond a single machine, I recommend a plugin architecture that allows `APScheduler` to be replaced with a Redis-backed queue like `RQ` or `Celery`.

### 🛡️ Robustness & Security Ideas:
*   **Job Watchdog**: Implement a "Heartbeat Sentinel" job that runs every 60s and writes a timestamp to a local file. If `main.py` detects a stale timestamp, it can auto-restart the background threads.
*   **Secure Job Injection**: Ensure that jobs can only be registered through a strict internal API to prevent a "Job Injection" attack where a malicious user message (if improperly parsed) could schedule a recursive task.

---

## 3. Integration Logic (Bifröst Flow)
**Current State**: Direct publication to StateBus.

### 📡 Cross-System Synergy:
*   **The "Dream Tick"**: During the `deep night` segment (00:00-04:00), the `scheduler` should trigger a `dream_tick` event. This would prompt `wyrd_matrix` to shuffle Hugr state and `mimir_well` to perform associative memory linking, simulating REM-state processing.
*   **Seasonal Awareness**: The scheduler currently only tracks *hours*. It should also track *seasons* (Equinoxes/Solstices) based on the user's geolocation, shifting Sigrid's energy modifiers (e.g., lower energy in winter, higher in summer).

---

## 🛠️ Next Development Steps
*   [ ] Add stochastic daily variance to `bio_engine.py`.
*   [ ] Create the `Heartbeat Sentinel` in `scheduler.py`.
*   [ ] Implement seasonal drift based on system date.
