# Ørlög Architecture Visualization

## 1. System Components

This diagram illustrates the high-level components of the skill and how they interact with the OpenClaw framework.

```mermaid
graph TB
    subgraph Host_System["Host System (Linux)"]
        direction TB

        subgraph Infrastructure["Infrastructure Layer (Podman)"]
            LiteLLM[("LiteLLM Router\n(Port 4000)")]
            OpenClaw[("OpenClaw Agent\n(Node.js)")]
            Ollama[("Ollama Local\n(Port 11434)")]

            LiteLLM -->|Routing| OpenClaw
            OpenClaw -->|Tool Execution| SkillCode
            SkillCode -->|Memory Ops| Ollama
        end

        subgraph SkillCode["Python Skill Logic"]
            direction TB

            CoreIdentity[("Core Identity\n(JSON)")]

            subgraph StateMachines["State Machines"]
                BioEngine["Bio-Cyclical\nEngine"]
                WyrdMatrix["Wyrd Matrix\n(PAD Model)"]
                Oracle["Abstract Core\n(Randomness)"]
                Metabolism["Digital Metabolism\n(psutil)"]
            end

            subgraph LogicEngines["Logic Engines"]
                Scheduler["APScheduler\n(Time/Tasks)"]
                Security["Sentinel Protocol\n(Security)"]
                ProjectGen["Autonomous Project\nGenerator"]
            end

            BioEngine --> WyrdMatrix
            Oracle --> WyrdMatrix
            Metabolism --> WyrdMatrix

            WyrdMatrix -->|Emotional State| OpenClaw
            Scheduler -->|Triggers| BioEngine
            Scheduler -->|Triggers| Oracle
            Security -->|Block/Allow| OpenClaw
        end

        subgraph Memory["Memory System (Local Storage)"]
            CoreDB[("/01_core_identity")]
            UserDB[("/02_user_model")]
            EpisodicDB[("/03_episodic_memory")]
            SkillDB[("/04_skill_tree")]

            SkillCode -->|Read/Write| CoreDB
            SkillCode -->|Read/Write| UserDB
            SkillCode -->|Read/Write| EpisodicDB
            SkillCode -->|Read/Write| SkillDB
        end
    end

    User((User)) -->|Chat/Commands| OpenClaw
    External((External APIs)) -->|Primary/Secondary APIs| LiteLLM
```

---

## 2. Data Flow (Input -> Processing -> Output)

This diagram details the step-by-step flow of data from a user message to the system's response.

```mermaid
sequenceDiagram
    participant User
    participant OpenClaw as OpenClaw Agent
    participant Security as Sentinel (Security)
    participant Python as Skill Logic (Python)
    participant Memory as Memory System
    participant Router as LiteLLM Router
    participant LLM as AI Models

    User->>OpenClaw: Message / Command

    rect rgb(255, 230, 230)
        Note over OpenClaw, Python: SECURITY CHECK
        OpenClaw->>Security: Validate Sender ID
        Security->>Security: Check Blocklist Ledger
        alt is Blocked
            Security-->>OpenClaw: DROP CONNECTION
            OpenClaw-->>User: (No Response)
        else is Safe
            Security->>Python: Proceed
        end
    end

    rect rgb(230, 240, 255)
        Note over Python, Memory: STATE CALCULATION
        Python->>Memory: Fetch Core Identity & Values
        Python->>Memory: Fetch User Trust Score
        Python->>Python: Calculate Bio-Rhythm (Cycle)
        Python->>Python: Calculate Hardware Health (Metabolism)
        Python->>Python: Compute Wyrd Matrix (Emotion)
        Python->>Python: Check Daily Variance (Abstract Core)
    end

    rect rgb(240, 255, 230)
        Note over Python, Router: PROMPT SYNTHESIS
        Python->>Python: Synthesize System Prompt
        Note right of Python: "You are [Mood]. You are at [Location].\nYour Trust for User is [High]."
        Python->>Router: Send Prompt + User Message
    end

    rect rgb(255, 250, 230)
        Note over Router, LLM: MODEL ROUTING
        Router->>Router: Check Engagement/Complexity Gauge
        alt Standard Engagement
            Router->>LLM: Route to Primary Model (Conscious)
        else High Complexity/Depth
            Router->>LLM: Route to Advanced Model (Deep Mind)
        end
        LLM-->>Router: Generated Response
        Router-->>OpenClaw: Response Text
    end

    OpenClaw-->>User: Reply

    rect rgb(240, 240, 240)
        Note over Python, Memory: POST-PROCESSING
        Python->>Memory: Log Interaction (Episodic)
        Python->>Memory: Update Trust Ledger
    end
```

---

## 3. Network & Security Topology

This diagram visualizes the network isolation and the role of the Sentinel Protocol.

```mermaid
graph TD
    subgraph Internet
        PrimaryAPI[Primary API (e.g. Gemini)]
        SecondaryAPI[Secondary API (e.g. OpenRouter)]
        Malicious[Malicious Actors]
    end

    subgraph Host_Machine["Host Machine (Linux)"]
        style Host_Machine fill:#f9f9f9,stroke:#333,stroke-width:2px

        subgraph Podman_Network["Podman Network (Rootless)"]
            style Podman_Network fill:#e6f3ff,stroke:#333

            Gateway[("LiteLLM Gateway\n(Port 4000)")]
            Agent[("OpenClaw Agent")]
            LocalAI[("Ollama\n(No External Access)")]

            Agent <--> Gateway
            Agent <--> LocalAI
        end

        subgraph Security_Layer["Sentinel Security Layer"]
            style Security_Layer fill:#ffe6e6,stroke:#cc0000

            Firewall["IP Filter / Port Lock"]
            Blocklist["Blocklist Ledger"]

            Firewall --> Blocklist
        end

        Memory_Storage[("Encrypted Local Storage")]
    end

    %% Connections
    PrimaryAPI <--> Gateway
    SecondaryAPI <--> Gateway

    User_Device[User Device] <-->|Secure Channel| Agent

    Malicious -.->|Blocked| Firewall
    Firewall -.->|Alert| User_Device

    Agent -->|Read/Write| Memory_Storage
```
