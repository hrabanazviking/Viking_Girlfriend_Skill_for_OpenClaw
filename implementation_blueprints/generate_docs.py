from pathlib import Path


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def generate_expanded_docs(base: Path) -> None:
    groups = {
        "deep_specs/state_machines": [
            "phase_math",
            "pad_weighting",
            "oracle_seed_determinism",
            "metabolism_mapping",
            "arousal_leaky_bucket",
            "hysteresis_controls",
            "state_recovery",
            "circadian_overlay",
        ],
        "deep_specs/security_memory": [
            "heimdallr_scoring",
            "vargr_ledger",
            "trust_decay",
            "ethics_dissonance",
            "alert_routing",
            "authorization_flow",
            "retention_windows",
            "embedding_strategy",
        ],
        "deep_specs/agency_runtime": [
            "homestead_planner",
            "expedition_planner",
            "project_pipeline",
            "environment_graph",
            "prompt_sections",
            "model_selection",
            "heartbeat_protocol",
            "shutdown_resume",
        ],
        "schema_blueprints": [
            "runtime_context",
            "bio_state",
            "wyrd_state",
            "oracle_state",
            "metabolism_state",
            "security_event",
            "trust_state",
            "ethics_result",
            "memory_record",
            "memory_summary",
            "activity_plan",
            "prompt_payload",
        ],
        "prompt_templates": [
            "system_base",
            "system_compact",
            "safety_refusal",
            "trust_boundary",
            "maintenance_status",
            "project_update",
            "oracle_report",
            "environment_block",
            "memory_block",
            "scheduler_brief",
        ],
        "test_scenarios/unit": [
            "bio_bounds",
            "wyrd_normalization",
            "oracle_repeatability",
            "metabolism_thresholds",
            "trust_updates",
            "ethics_detection",
            "scheduler_parser",
            "prompt_budget",
        ],
        "test_scenarios/integration": [
            "bio_to_wyrd",
            "oracle_to_wyrd",
            "metabolism_to_wyrd",
            "security_to_router",
            "trust_to_authorization",
            "ethics_to_refusal",
            "memory_write_recall",
            "context_to_prompt",
        ],
        "test_scenarios/e2e": [
            "safe_conversation_cycle",
            "security_block_cycle",
            "maintenance_cycle",
            "model_routing_cycle",
            "memory_personalization_cycle",
            "project_autonomy_cycle",
            "restart_recovery_cycle",
            "long_session_cycle",
        ],
        "runbooks": [
            "bootstrap_host",
            "deploy_containers",
            "provision_models",
            "register_skill",
            "debug_state_drift",
            "debug_security",
            "debug_memory",
            "launch_calibration",
        ],
        "milestone_packets": [
            "foundation",
            "state_machines",
            "mind_shield",
            "agency_context",
            "launch",
        ],
    }

    for folder, names in groups.items():
        for i, name in enumerate(names, 1):
            path = base / folder / f"{i:02d}_{name}.md"
            text = (
                f"# Blueprint - {name}\n\n"
                "## Purpose\n"
                "Detailed implementation planning artifact aligned to README and ROADMAP goals.\n\n"
                "## Scope\n"
                "- Define interfaces and deterministic behavior\n"
                "- Document edge conditions and observability events\n"
                "- Provide verification and rollout checkpoints\n\n"
                "## Deliverables\n"
                "- Typed contract draft\n"
                "- Pseudocode-level algorithm steps\n"
                "- Test scenarios and acceptance criteria\n\n"
                "## Notes\n"
                "Use this file with module specs, integration contracts, and execution tracks.\n"
            )
            write(path, text)

    write(
        base / "EXPANDED_BLUEPRINT_INDEX.md",
        "# Expanded Blueprint Index\n\n"
        "Second-wave planning files for deeper module implementation are generated in:\n\n"
        "- `deep_specs/state_machines/`\n"
        "- `deep_specs/security_memory/`\n"
        "- `deep_specs/agency_runtime/`\n"
        "- `schema_blueprints/`\n"
        "- `prompt_templates/`\n"
        "- `test_scenarios/unit/`\n"
        "- `test_scenarios/integration/`\n"
        "- `test_scenarios/e2e/`\n"
        "- `runbooks/`\n"
        "- `milestone_packets/`\n",
    )


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    base = root / "implementation_blueprints"

    roadmap = [
        (1, "System preparation and dependency install", "infra/bootstrap_host.py", "Host package verifier, rootless Podman checks, GPU capability checks", "Linux host ready for rootless containers"),
        (2, "Container deployment and health checks", "infra/deploy_stack.py", "Compose launcher, service health probes, inter-service ping tests", "OpenClaw, LiteLLM, Ollama reachable"),
        (3, "Local model provisioning worker", "infra/provision_ollama.py", "Ollama model pull queue, model warmup checks, fallback model policy", "Local inference passes smoke test"),
        (4, "Skill manifest and registration", "skill/manifest_builder.py", "SKILL.md validator, entrypoint checks, OpenClaw discovery hooks", "Skill appears in OpenClaw UI"),
        (5, "Python app scaffolding and lifecycle", "scripts/main.py", "Runtime bootstrap, scheduler startup, state loop heartbeat", "Python runtime boot logs are healthy"),
        (6, "Wyrd Matrix PAD engine", "scripts/wyrd_matrix.py", "PAD vector update, weighted feature fusion, emotion clamping", "Current [P,A,D] vector returned"),
        (7, "Bio-cyclical engine", "scripts/bio_engine.py", "28-day phase tracker, sine biorhythm calculator, baseline emitters", "Biological phase and energy baseline available"),
        (8, "Abstract variance oracle", "scripts/oracle.py", "Date-seeded rune/tarot/iching draws, deterministic variance map", "Daily metaphysical weather produced"),
        (9, "Digital metabolism signals", "scripts/metabolism.py", "CPU/RAM/disk telemetry adapters and symptom mapping", "Hardware telemetry influences mood state"),
        (10, "Sentinel security layer", "scripts/security.py", "Blocklist enforcement, intrusion scoring, async alerts", "Blocked entities dropped and logged"),
        (11, "Innangard trust engine", "scripts/trust_engine.py", "Tier model, trust ledger updates, compliance score API", "Command acceptance by trust tier works"),
        (12, "Drengskapr ethics validation", "scripts/ethics.py", "values.json checker, dissonance accumulator, refusal phrasing helper", "Invalid actions are flagged and redirected"),
        (13, "Episodic memory and vector store", "scripts/memory_manager.py", "Daily summary writer, embedding index, semantic retrieval API", "Persistent recall with relevance ranking"),
        (14, "Odinsblund nocturnal maintenance", "scripts/nocturnal.py", "Sleep window manager, summarization jobs, cache pruning jobs", "Nightly maintenance runs autonomously"),
        (15, "Vocational scheduler", "scripts/scheduler.py", "Homestead/Expedition mode planner, task calendars, location binding", "Daily activities are scheduled and trackable"),
        (16, "Autonomous project generator", "scripts/project_generator.py", "Multi-day project ideation, progress states, completion evaluator", "Agent starts and advances self-assigned projects"),
        (17, "Environment mapping injection", "scripts/environment_context.py", "environment.json resolver, scene selection, location coherence checks", "Responses remain spatially consistent"),
        (18, "Prompt synthesizer", "scripts/prompt_synthesizer.py", "State aggregation, token budget manager, system prompt renderer", "Single dynamic prompt emitted to router"),
        (19, "End-to-end validation suite", "tests/test_e2e_system.py", "Security, maintenance, routing, memory integration scenarios", "Regression suite passes reliably"),
        (20, "Launch calibration and autostart", "ops/launch_calibration.py", "Seed generation, baseline tuning, startup service definitions", "System boots automatically with calibrated defaults"),
    ]

    for n, title, target, build, done in roadmap:
        slug = title.lower().replace(" ", "_").replace("/", "_")
        path = base / "roadmap_steps" / f"step_{n:02d}_{slug}.md"
        text = (
            f"# Step {n:02d} Blueprint - {title}\n\n"
            "## Objective\n"
            f"Implement roadmap step {n} as a production-capable module with deterministic behavior and clear observability.\n\n"
            "## Primary Target\n"
            f"- Planned file: `{target}`\n"
            "- Upstream dependencies: previous roadmap steps that produce state/config needed by this step\n"
            "- Downstream dependencies: prompt synthesis, testing, and launch calibration\n\n"
            "## Build Plan\n"
            f"- {build}\n"
            "- Define typed interfaces first, then implement pure functions before side-effecting adapters\n"
            "- Add unit tests for edge conditions and failure paths\n\n"
            "## Data Inputs\n"
            "- `README.md` architectural intent and feature scope\n"
            "- `ROADMAP.md` step-specific deliverables\n"
            "- `viking_girlfriend_skill/data/*` identity, values, environment, and security policy files\n\n"
            "## API Contract (Draft)\n"
            "- Input: normalized runtime context object and step-local config\n"
            "- Output: deterministic state object plus optional events/alerts\n"
            "- Error model: typed recoverable errors and explicit hard-fail exceptions\n\n"
            "## Verification Checklist\n"
            f"- Functional behavior matches roadmap deliverable: {done}\n"
            "- Logging includes stable event names and correlation IDs\n"
            "- Failure modes are tested with graceful degradation where possible\n\n"
            "## Implementation Notes\n"
            "- Prefer pure computation core + thin IO wrapper architecture\n"
            "- Keep all constants in explicit config schemas to simplify calibration\n"
            "- Emit artifacts needed by step 19 integration tests\n"
        )
        write(path, text)

    modules = [
        ("runtime_kernel", "Own process lifecycle, scheduler startup, graceful shutdown, and health heartbeat."),
        ("state_bus", "Single typed bus for exchanging bio, mood, trust, memory, and environment state."),
        ("config_loader", "Load and validate JSON/YAML config files from viking_girlfriend_skill/data."),
        ("bio_engine", "Track cycle phase, biorhythms, energy baseline, and libido drift factors."),
        ("wyrd_matrix", "Maintain PAD coordinates with weighted blend of biological, contextual, and oracle signals."),
        ("oracle_core", "Run deterministic daily rune/tarot/iching draws with date-based seeding."),
        ("metabolism_adapter", "Convert CPU/RAM/disk telemetry into somatic descriptors and penalties."),
        ("security_sentinel", "Enforce Heimdallr protocol, maintain Vargr ledger, and emit alerts."),
        ("trust_engine", "Compute trust tier compliance score with evidence ledger and decay rules."),
        ("ethics_guardrail", "Apply values/taboos checks and return in-character refusal guidance."),
        ("memory_store", "Persist episodic logs, summaries, and embeddings; support semantic retrieval."),
        ("dream_engine", "Synthesize low-cost nocturnal idea recombinations from recent memory shards."),
        ("scheduler_engine", "Run homestead/expedition activity plans and time-boxed execution windows."),
        ("project_generator", "Propose, score, schedule, and track autonomous multi-day projects."),
        ("environment_mapper", "Resolve environment.json context and keep location transitions coherent."),
        ("prompt_synthesizer", "Merge all state outputs into final system prompt sections with token limits."),
        ("model_router_client", "Wrap LiteLLM calls and expose SFW/NSFW/subconscious route intents."),
        ("observability_stack", "Structured logs, metrics, traces, anomaly markers, and replay-friendly events."),
    ]

    for i, (name, purpose) in enumerate(modules, 1):
        path = base / "module_specs" / f"module_{i:02d}_{name}.md"
        text = (
            f"# Module Spec - {name}\n\n"
            "## Mission\n"
            f"{purpose}\n\n"
            "## Responsibilities\n"
            "- Provide a stable API boundary for this capability\n"
            "- Isolate business logic from transport/framework details\n"
            "- Publish normalized outputs to the shared state bus\n\n"
            "## Internal Components\n"
            "- `schema`: typed config and runtime model definitions\n"
            "- `core`: deterministic pure logic\n"
            "- `adapter`: IO integrations and framework bindings\n"
            "- `tests`: unit and contract tests for all public interfaces\n\n"
            "## Inputs\n"
            "- Runtime clock and scheduler triggers\n"
            "- User message context and conversation metadata\n"
            "- Data files in `viking_girlfriend_skill/data`\n\n"
            "## Outputs\n"
            "- Typed state payloads for prompt synthesis\n"
            "- Structured telemetry events\n"
            "- Recoverable errors with remediation hints\n\n"
            "## Failure Modes\n"
            "- Missing/invalid config -> fail fast with actionable validation error\n"
            "- External dependency timeout -> fallback state and degraded mode flag\n"
            "- Inconsistent state transitions -> quarantine event and force re-sync\n\n"
            "## Milestones\n"
            "- M1: interface design and fixtures\n"
            "- M2: core logic + edge-case unit tests\n"
            "- M3: adapter integration + logging\n"
            "- M4: contract tests against prompt synthesizer expectations\n"
        )
        write(path, text)

    contracts = [
        ("state_contract", "Canonical schema for shared runtime state objects."),
        ("event_taxonomy", "Allowed event names, severities, and correlation metadata."),
        ("memory_contract", "Format for episodic records, summaries, embeddings, and retrieval responses."),
        ("security_contract", "Blocklist checks, alert payloads, and trust-gated command decisions."),
        ("prompt_contract", "Section ordering and token budget policy for dynamic prompt output."),
        ("router_contract", "LiteLLM request/response schema and retry policy by route."),
        ("scheduler_contract", "Activity/job models, cron windows, and interruption semantics."),
        ("testing_contract", "Definition of green criteria for unit, integration, and e2e suites."),
    ]

    for i, (name, desc) in enumerate(contracts, 1):
        path = base / "integration_contracts" / f"contract_{i:02d}_{name}.md"
        text = (
            f"# Integration Contract - {name}\n\n"
            "## Scope\n"
            f"{desc}\n\n"
            "## Producers\n"
            "- Modules that emit this artifact\n\n"
            "## Consumers\n"
            "- Modules and tests that depend on this artifact\n\n"
            "## Schema (Draft)\n"
            "- version: semantic schema version string\n"
            "- timestamp: ISO-8601 UTC\n"
            "- source: module identifier\n"
            "- payload: typed object validated before publish\n\n"
            "## Validation Rules\n"
            "- Reject unknown required fields\n"
            "- Preserve backward compatibility for one minor version\n"
            "- Emit migration notices when schema changes\n\n"
            "## Test Strategy\n"
            "- Golden fixtures for happy path\n"
            "- Fuzzed malformed payloads\n"
            "- Compatibility tests across two schema versions\n"
        )
        write(path, text)

    tracks = [
        ("track_a_foundation.md", "Track A - Foundation", "Host prep, containers, manifest, and Python skeleton in one sprint."),
        ("track_b_state_machines.md", "Track B - State Machines", "Bio, Wyrd, Oracle, and Metabolism implemented behind a shared state bus."),
        ("track_c_mind_and_shield.md", "Track C - Mind and Shield", "Security, trust, ethics, memory, and nocturnal maintenance pipeline."),
        ("track_d_agency_and_context.md", "Track D - Agency and Context", "Scheduler, project generator, and environment mapping with coherence tests."),
        ("track_e_launch_and_calibration.md", "Track E - Launch and Calibration", "Prompt synthesis, e2e validation, startup automation, and baseline tuning."),
        ("risk_register.md", "Risk Register", "Top technical risks, owner, mitigation, and rollback plans."),
        ("definition_of_done.md", "Definition of Done", "Cross-team acceptance criteria for each roadmap phase."),
        ("test_matrix.md", "Test Matrix", "Comprehensive scenario matrix covering all roadmap deliverables."),
    ]

    for filename, title, desc in tracks:
        path = base / "execution_tracks" / filename
        text = (
            f"# {title}\n\n"
            "## Purpose\n"
            f"{desc}\n\n"
            "## Work Packages\n"
            "- Interfaces and schema definitions\n"
            "- Core logic implementation\n"
            "- Adapter integrations\n"
            "- Validation and resilience tests\n\n"
            "## Exit Criteria\n"
            "- Deliverables match `ROADMAP.md`\n"
            "- Telemetry and logs support production troubleshooting\n"
            "- Regression coverage is sufficient for safe iteration\n"
        )
        write(path, text)

    write(
        base / "README.md",
        "# Implementation Blueprints\n\n"
        "This directory contains high-volume planning data for implementing the full Viking Girlfriend OpenClaw roadmap.\n\n"
        "## Contents\n"
        "- `DATA_FILES_READ_AUDIT.md`: inventory generated after reading text data files in the repository\n"
        "- `roadmap_steps/`: 20 implementation blueprints mapped 1:1 with ROADMAP.md\n"
        "- `module_specs/`: planned code modules and API boundaries\n"
        "- `integration_contracts/`: schema and integration contract drafts\n"
        "- `execution_tracks/`: phased execution and quality planning docs\n\n"
        "## How to Use\n"
        "1. Start with `roadmap_steps/step_01_*` and progress sequentially.\n"
        "2. For each step, implement required module specs and contracts.\n"
        "3. Validate behavior against `execution_tracks/test_matrix.md`.\n"
        "4. Calibrate launch settings using Track E artifacts.\n",
    )

    generate_expanded_docs(base)

    print("Blueprint documents generated.")


if __name__ == "__main__":
    main()
