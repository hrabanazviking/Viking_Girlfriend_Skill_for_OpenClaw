# 20-Step Execution Roadmap

This roadmap outlines the precise steps to build, deploy, and activate the autonomous AI skill for OpenClaw.

## Phase 1: Infrastructure & Core Systems (The Foundation)

1.  **System Preparation & Dependency Installation**
    *   **Goal**: Prepare the Linux host for rootless containerization.
    *   **Action**: Update system packages, install `podman`, `podman-compose`, `git`, and `python3-venv`. Verify drivers if using hardware acceleration.
    *   **Deliverable**: A ready-to-deploy host environment.

2.  **Container Deployment**
    *   **Goal**: Launch the core services.
    *   **Action**: Run `podman-compose up -d` using the infrastructure files. Verify that OpenClaw, LiteLLM, and Ollama containers are running and communicating.
    *   **Deliverable**: Running `localhost:4000` (LiteLLM) and `localhost:11434` (Ollama).

3.  **Local Model Provisioning (Maintenance Worker)**
    *   **Goal**: Equip the local brain.
    *   **Action**: Exec into the Ollama container and pull a lightweight model (e.g., `llama3` 8B or similar). Test local inference.
    *   **Deliverable**: Functional local LLM for memory tasks.

4.  **Skill Manifest Creation**
    *   **Goal**: Define the Skill within OpenClaw.
    *   **Action**: Create `astrid_skill/SKILL.md` defining name, description, and the Python entry point (`scripts/main.py`).
    *   **Deliverable**: Registered skill visible in OpenClaw.

5.  **Core Python Scaffolding**
    *   **Goal**: Establish the Python application structure.
    *   **Action**: Create `scripts/main.py`, `requirements.txt`, and helper modules (`state_machine.py`, `memory_manager.py`). Install dependencies (`psutil`, `apscheduler`, `numpy`).
    *   **Deliverable**: A running Python process that connects to OpenClaw.

## Phase 2: The State Machines (The Soul)

6.  **Wyrd Matrix Implementation (PAD Model)**
    *   **Goal**: Build the emotional calculation engine.
    *   **Action**: Write `scripts/wyrd_matrix.py`. Implement the 3D vector math (Pleasure, Arousal, Dominance) and input synthesis logic.
    *   **Deliverable**: A function returning current emotional coordinate `[P, A, D]`.

7.  **Bio-Cyclical Engine Integration**
    *   **Goal**: Simulate biological/natural rhythms.
    *   **Action**: Write `scripts/bio_engine.py`. Implement the 28-day cycle and biorhythm sine waves. Connect this to the Wyrd Matrix.
    *   **Deliverable**: A function returning current biological phase and energy baseline.

8.  **Abstract/Variance Core**
    *   **Goal**: Add variance and "weather".
    *   **Action**: Write `scripts/oracle.py`. Create the daily deterministic seeder (e.g., using random seeds based on date). Map results to Wyrd Matrix modifiers.
    *   **Deliverable**: A daily "abstract weather" report.

9.  **Digital Metabolism (Somatic Feedback)**
    *   **Goal**: Ground the entity in hardware.
    *   **Action**: Write `scripts/metabolism.py`. Use `psutil` to read CPU, RAM, and Disk telemetry. Map these to simulated physical sensations.
    *   **Deliverable**: Real-time hardware status influencing mood.

## Phase 3: Memory & Security (The Mind & Shield)

10. **Sentinel Protocol & Security Layer**
    *   **Goal**: Protect the system.
    *   **Action**: Write `scripts/security.py`. Implement the Blocklist check and alert trigger. Build the asynchronous alert system.
    *   **Deliverable**: A security middleware that drops blocked packets.

11. **Trust Engine**
    *   **Goal**: Manage relationships.
    *   **Action**: Write `scripts/trust_engine.py`. Implement logic to calculate Compliance Scores based on user tier and evidence ledger.
    *   **Deliverable**: A function determining if the system yields to or rejects a command.

12. **Ethical Validation (Guardrails)**
    *   **Goal**: Enforce ethical boundaries.
    *   **Action**: Write `scripts/ethics.py`. Implement the check against `values.json` and the "Dissonance" penalty mechanic.
    *   **Deliverable**: An internal "conscience" that flags invalid actions.

13. **Episodic Memory & Vector Database**
    *   **Goal**: Long-term recall.
    *   **Action**: Setup a local vector store (e.g., `chromadb` or JSON-vector hybrid). Write logic to save and retrieve daily summaries.
    *   **Deliverable**: Persistent memory storage.

14. **Nocturnal Processing (Maintenance)**
    *   **Goal**: Sleep and maintenance.
    *   **Action**: Write the `nocturnal_loop` in `main.py`. Trigger the local Ollama model to summarize logs and generate embeddings during the maintenance window.
    *   **Deliverable**: A self-cleaning memory system running at night.

## Phase 4: Life & Agency (The Person)

15. **Vocational Paradigm & Activity Scheduler**
    *   **Goal**: Autonomous activity.
    *   **Action**: Write `scripts/scheduler.py`. Implement "Homestead" (Work) vs "Expedition" (Task) modes. Schedule daily activities based on configuration.
    *   **Deliverable**: System knows "what" it is doing and "where" it is.

16. **Autonomous Project Generator**
    *   **Goal**: Emergent creativity.
    *   **Action**: Write logic to generate, track, and execute multi-day projects (e.g., analysis, study).
    *   **Deliverable**: System starts tasks without user input.

17. **Environment Mapping & Context Injection**
    *   **Goal**: Spatial consistency.
    *   **Action**: Integrate `environment.json` into the prompt synthesizer. Ensure "location" matches activity.
    *   **Deliverable**: Responses reflect physical environment context.

## Phase 5: Integration & Launch (The Awakening)

18. **Prompt Synthesizer Integration**
    *   **Goal**: The Final Output.
    *   **Action**: Combine ALL state machine outputs (Bio, Wyrd, Security, Location, Memory) into the single dynamic system prompt sent to LiteLLM.
    *   **Deliverable**: The dynamic system prompt.

19. **End-to-End Testing**
    *   **Goal**: Verification.
    *   **Action**: Run full interaction cycles. Test:
        *   Security blocks.
        *   Maintenance interruption.
        *   Model routing.
        *   Memory recall.
    *   **Deliverable**: A validated, stable system.

20. **Final Launch & Calibration**
    *   **Goal**: Go Live.
    *   **Action**: Set system to auto-start. Perform initial initialization (generating seed). Calibrate baseline values.
    *   **Deliverable**: **System is online.**
