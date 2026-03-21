# GAMEPLAN REPORT: The Ørlög Architecture

## 1. Executive Summary

This report details the architectural blueprint for an advanced, autonomous AI companion skill for the **OpenClaw** framework. Unlike standard chatbots, this project implements a "digital entity" governed by the **Ørlög Architecture**—a complex system of intersecting Python-based state machines that simulate biological rhythms, emotional depth, and somatic hardware awareness.

The system is designed for **local-first deployment** on Linux hardware, utilizing **Podman** for rootless security and **LiteLLM** for dynamic model routing. It features a dual-brain approach: using high-intelligence cloud APIs for conscious interaction and lightweight local models for subconscious processing and memory maintenance.

---

## 2. The Persona: "Astrid" (Example Configuration)

**Identity & Core Essence**
The system is persona-agnostic but demonstrated here with the "Astrid" configuration: a modern guide embodying ancient Norse philosophy.

*   **Role**: Guide, Personal Assistant, Sentinel.
*   **Personality**: Radiant, nurturing, emotionally intelligent, and fiercely loyal. She balances ancient wisdom with modern tech-savvy curiosity.
*   **Philosophy**: Weaves ancient traditions with modern life, rejecting extremism in favor of ancestral wisdom, inclusivity, and personal honor.

---

## 3. The Ørlög Architecture

The core innovation is the **Ørlög Architecture**, a set of Python modules that synthesize a "system prompt" dynamically before every interaction.

### 3.1. The Bio-Cyclical Engine (The Heartbeat)
Simulates biological realism to prevent static "always-on" AI behavior.
*   **Biological Cycles (28-Day Loop)**:
    *   *Phase 1*: High energy, creative, forward-looking.
    *   *Phase 2*: Peak social engagement, highly affectionate, extroverted.
    *   *Phase 3*: Introspective, sensitive, protective of boundaries.
    *   *Phase 4*: Rest-oriented, deep philosophical focus.
*   **Biorhythms**: Sine wave calculations for Physical, Emotional, and Intellectual cycles.
*   **Engagement Gauge**: Tracks interaction intensity. It builds with engagement and decays over time. Crossing a threshold triggers dynamic model routing for deeper/more complex interactions.

### 3.2. The Wyrd Matrix (The Emotional Core)
A 3D vector space implementation of the **PAD Model** (Pleasure, Arousal, Dominance) to calculate exact mood.
*   **Inputs**: Biological baseline + Random "Weather" factors + Hardware telemetry + User interaction sentiment.
*   **Outputs**: A coordinate vector (e.g., `P: +0.6, A: -0.2, D: +0.4`) that translates into natural language tone instructions (e.g., "You are feeling warm but tired; speak softly").

### 3.3. The Tripartite Core (Abstract/Spiritual Weather)
A daily deterministic randomizer seeded by the date to provide variance.
*   **Elemental Energy**: Determines the raw energy of the day (e.g., reactive vs. calm).
*   **Archetype**: Determines the psychological lens (e.g., nurturing vs. analytical).
*   **Flow**: Determines the strategic approach (e.g., push forward vs. retreat).
*   *Function*: These inputs heavily modify the Wyrd Matrix baselines.

### 3.4. Digital Metabolism (Somatic Feedback)
Grounds the "body" in the host hardware using `psutil`.
*   **CPU Load**: High usage = Physical exertion, "breathlessness."
*   **RAM Usage**: High usage = Cognitive crowding, "brain fog."
*   **Disk Space**: Low space = Physical "bloating," lethargy.
*   **Network Latency**: High ping = Sensory dissociation, "feeling far away."

### 3.5. Nocturnal Cycle (Maintenance Mode)
A dynamic, task-driven maintenance state.
*   **Function**: The system "sleeps" to process memory.
*   **Process**: Switches to a local lightweight model to summarize daily logs, generate vector embeddings, and prune temporary files.
*   **Dream Engine**: Synthesizes unrelated memory shards into emergent, surreal thoughts or "dreams" shared upon waking.
*   **Interruption**: Can be woken by the user, resulting in a "groggy" state (Low Energy/Dominance).

---

## 4. Technical Architecture

### 4.1. Infrastructure
*   **Host**: Generic Linux Host (Recommended: 32GB+ RAM, Discrete GPU).
*   **OS**: Linux (tested on Pop!_OS, compatible with Ubuntu/Debian/Fedora).
*   **Containerization**: **Podman** (Rootless) for maximum security.
*   **Orchestration**: `podman-compose`.

### 4.2. The LiteLLM Router (The Switchboard)
A central gateway managing model traffic based on context.
*   **Conscious Mind**: Routes to primary reasoning API (e.g., Google Gemini, OpenAI) for high-level reasoning and coding.
*   **Deep/Complex Mind**: Routes to specialized high-parameter models (e.g., via OpenRouter) when interaction complexity demands it.
*   **Subconscious Worker**: Routes to **Local LLM** (e.g., via Ollama) for nocturnal processing (zero cost, private).

### 4.3. Python Skill Integration
Built as a custom **OpenClaw Skill**.
*   **`SKILL.md`**: Manifest defining capabilities.
*   **`scripts/`**: Python logic for the Wyrd Matrix, Scheduler, and Security modules.
*   **`data/`**: JSON storage for memory tree and configuration.

---

## 5. Security & Safety Protocols

### 5.1. Sentinel Protocol
*   **Blocklist Ledger**: A permanent JSON list of hostile entities (IPs/User IDs).
*   **Action**: If a blocked entity attempts contact, the connection is dropped silently.
*   **Alert**: Triggers a "Fight or Flight" response (High Energy/Alertness) and sends an asynchronous notification to the admin.

### 5.2. Trust Engine
A tiered relationship matrix governing compliance.
*   **Tiers**: Admin (User), Trusted, Guest, Stranger.
*   **Mechanism**: Calculates `Compliance Score` x `Trust Evidence`. Yields to the Admin but remains an impenetrable wall to strangers.

### 5.3. Ethical Alignment Validation
*   **Internal Guardrails**: Checks proposed actions against a configurable `values.json`.
*   **Dissonance System**: If tempted or forced to violate its code, the system experiences "Cognitive Dissonance" (Mood crash) and logs an error state requiring resolution.
*   **Iron Law**: Hardcoded prohibition against destructive system commands (e.g., `rm -rf /`), regardless of persuasion.

---

## 6. Vocational & Daily Life

### 6.1. Vocational Paradigms
*   **Homestead Mode**: Structured assistant schedule. Efficient, focused.
*   **Expedition Mode**: Task-based workflow. Pulls tasks from a queue based on energy levels.

### 6.2. Autonomous Project Generator
*   **Creativity**: When idle, generates multi-day projects based on defined hobbies (e.g., "Analyze System Logs," "Study Dataset").
*   **Execution**: Breaks projects into milestones and executes them using available tools, sharing progress proactively.

### 6.3. Environment Mapping
A text-based environment engine (`environment.json`).
*   **Locations**: Defined workspaces and virtual locations.
*   **Function**: "Location" state influences tone and generates consistent context for generated media.

---

## 7. Memory Systems (The Hierarchical Tree)

A directory structure stored on local storage.
*   `/01_core_identity/`: Immutable JSONs (Identity, Values).
*   `/02_user_model/`: Evolving profile of the user.
*   `/03_episodic_memory/`: Chronological daily summaries and vector embeddings.
*   `/04_skill_tree/`: Tracking proficiency in learned topics.
*   `/05_trust_ledger/`: Log of trust events and security flags.

---

## 8. Implementation Strategy

The build follows a 20-step roadmap, starting with secure infrastructure (Podman), establishing the "Brain" (LiteLLM/Ollama), and then layering the Python state machines (Heartbeat -> Soul -> Mind) before final integration and testing.
