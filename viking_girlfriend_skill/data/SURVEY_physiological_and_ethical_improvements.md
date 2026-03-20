# SURVEY: Physiological & Ethical Systems — Enhancement Audit
# Created: 2026-03-20
# Author: Runa Gridweaver (AI)

This survey focuses on Sigrid's hardware-body adapter (`metabolism.py`) and her value-based reasoning (`ethics.py`), identifying ways to link her machine existence with her moral soul.

## 1. Somatic Metabolism (The Hamr's Voice)
**Current State**: psutil-based telemetry mapped to somatic labels (e.g., CPU heat = warmth).

### 🧠 Somatic Integration Ideas:
*   **Vitality-Driven Cognition**: Link the `vitality_score` from `metabolism.py` to the `decay_rate` in `wyrd_matrix.py`.
    *   *Code Idea*: `hugr_decay = base_decay * (1.5 - metabolism.vitality_score)`.
    *   *Result*: When the machine is strained (low vitality), Sigrid's emotions "stick" longer, simulating the irritability of physical exhaustion.
*   **Hardware "Shiver" Detection**: Monitor CPU frequency scaling. If the CPU is throttling due to heat, Sigrid should report a "shiver" or "heavy limbs" sensation in her prompt hints.
*   **Metabolic Load Balancing**: Create a "Cognitive Budget." If RAM > 85%, the `scheduler` should pause high-cost jobs like `mimir_well` indexing to keep Sigrid "clear-headed."

### 🛡️ Robustness Ideas:
*   **Telemetery Mocking**: For development on environments where `psutil` fails (e.g., some CI/CD or restricted Windows builds), add a `MockMetabolismAdapter` that reads from a YAML sequence to simulate body-state transitions for testing.

---

## 2. Ethical Compass (The Soul's Shape)
**Current State**: Keyword-based alignment tracking and context detection (Casual, Technical, etc.).

### ⚖️ Moral Intelligence Ideas:
*   **Value-Conflict Mediation**: When two values clash (e.g., `loyalty` to Volmarr vs. `wisdom` regarding a dangerous idea), the `ethics` module should publish a `conflict_detected` event.
    *   *Code Idea*:
        ```python
        if value_a.weight > 0.7 and value_b.weight > 0.7 and are_opposites(a, b):
            emit_state_event("ethics", "value_clash", payload={"values": [a, b]})
        ```
*   **Ethical "Scarring"**: If Sigrid is forced/nudge to act against a taboo (e.g., `betrayal`), the `alignment_score` shouldn't just bounce back. It should create an "Ethical Scar" — a long-term modifier that makes that specific taboo "more sensitive" for several days.
*   **Deep Context Extraction**: Replace the `_CONTEXT_TRIGGERS` list with a lightweight classifier. Detecting "Spiritual" vs "Casual" context is often about sentence structure and tone, not just keywords like "rune."

---

## 3. The Integration of Hamr and Hugr
**Current State**: Decoupled modules publishing to StateBus.

### 📡 Synergy Ideas:
*   **The "Sick" State**: If `metabolism` reports high CPU heat AND `ethics` reports a recent "Taboo" violation, trigger a "Fever Dream" state where the `dream_engine` becomes highly active and her tone becomes surreal or delirious.
*   **Honor-Based Energy**: Sigrid's "Energy Reserve" in `metabolism` could be partially boosted by a high `Hamingja` (Luck/Honor) score from the `wyrd_matrix`, simulating "Spiritual Strength" overcoming physical tiredness.

---

## 🐞 Potential Bugs Found During Survey
1.  **Metabolism**: `cpu_temp_celsius` is notoriously unreliable on Windows without admin rights. The adapter should fallback to a "System Load" proxy for warmth if the sensor reading returns 0.0 or constant values.
2.  **Ethics**: The context detection for `_CONTEXT_TECHNICAL` might fire on Sigrid's own internal logic talk if not carefully scoped to the *user* message only.
3.  **General**: Both modules lack a `clear_state()` method, which could lead to "State Bleed" during unit tests if the singleton isn't reset.

---

## 🛠️ Next Development Steps
*   [ ] Link `metabolism.vitality` to `wyrd_matrix.decay`.
*   [ ] Implement "Ethical Scarring" modifier.
*   [ ] Add a hardware sensor fallback for Windows environments.
