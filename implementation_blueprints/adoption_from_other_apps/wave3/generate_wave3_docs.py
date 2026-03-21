from pathlib import Path


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    root = Path(__file__).resolve().parents[3]
    base = root / "implementation_blueprints" / "adoption_from_other_apps" / "wave3"
    step_dir = base / "roadmap_step_import_plans"
    risk_dir = base / "per_import_risks"
    seq_dir = base / "execution_sequences"

    step_map = {
        1: [("data_system.py", "Establish reliable multi-format config/data loader"), ("comprehensive_logging.py", "Set baseline startup logging and diagnostics")],
        2: [("local_providers.py", "Bring up local provider adapters for service checks"), ("openrouter.py", "Optional cloud route validation path")],
        3: [("local_providers.py", "Model listing/health hooks for local runtime"), ("thor_guardian.py", "Guard provisioning operations with retries/circuit breaker")],
        4: [("turn_processor.py", "Use orchestration skeleton for skill registration flow")],
        5: [("turn_processor.py", "Core cycle orchestration scaffold"), ("timeline_service.py", "Deterministic runtime time progression"), ("comprehensive_logging.py", "Per-cycle structured logging")],
        6: [("emotional_engine.py", "Signal engine for PAD inputs"), ("stress_system.py", "Threshold events feeding PAD dominance"), ("personality_engine.py", "Behavior modulation overlays")],
        7: [("menstrual_cycle.py", "Primary bio-cyclical phase engine")],
        8: [("wyrd_system.py", "Primary fate/oracle state model"), ("world_will.py", "Ambient intent context layer"), ("story_phase.py", "Long-arc thematic phase support")],
        9: [("emotional_engine.py", "Reuse telemetry-to-affect mapping patterns")],
        10: [("thor_guardian.py", "Primary resilience and guarded execution wrapper"), ("crash_reporting.py", "Structured incident reporting")],
        11: [("social_ledger.py", "Evidence ledger pattern for trust updates"), ("relationship_graph.py", "Scoring transforms for trust shifts")],
        12: [("social_protocol_engine.py", "Policy validation gate pattern"), ("memory_hardening.py", "Context drift and safety reinforcement")],
        13: [("memory_system.py", "Session memory data model"), ("enhanced_memory.py", "Summarization pipeline"), ("character_memory_rag.py", "Indexed memory retrieval"), ("memory_query_engine.py", "Selective memory querying")],
        14: [("enhanced_memory.py", "Night summarization primitives"), ("world_dreams.py", "Optional nocturnal recombination patterns")],
        15: [("timeline_service.py", "Schedule time axis and segment transitions"), ("turn_processor.py", "Activity execution orchestration hooks")],
        16: [("story_phase.py", "Project lifecycle phase patterns"), ("world_will.py", "Goal pressure modulation ideas")],
        17: [("world_systems.py", "Location/context coherence structures"), ("timeline_service.py", "Temporal coherence companion context")],
        18: [("turn_processor.py", "Prompt assembly pipeline shape"), ("enhanced_context_builder.py", "Context sectioning and ordering approach"), ("local_providers.py", "Provider call surface pattern")],
        19: [("comprehensive_logging.py", "Testable event/log envelope"), ("thor_guardian.py", "Failure-path behavior under test")],
        20: [("comprehensive_logging.py", "Calibration signal extraction from logs"), ("timeline_service.py", "Stable baseline timing for comparisons")],
    }

    for step in range(1, 21):
        rows = step_map.get(step, [])
        lines = [f"# Roadmap Step {step:02d} Import Plan", "", "## Import Order"]
        if not rows:
            lines.append("- No direct imports planned for this step.")
        for i, (mod, why) in enumerate(rows, 1):
            lines.append(f"- {i}. `code_of_other_apps_that_can_be_adopted/{mod}` - {why}.")
        lines += [
            "",
            "## Adapter Notes",
            "- Keep imports behind adapter boundaries in target modules.",
            "- Preserve deterministic behavior and typed outputs.",
            "- Remove game-specific assumptions during adaptation.",
            "",
            "## Validation Gate",
            "- Unit coverage for imported logic paths.",
            "- Integration coverage against state bus and prompt contracts.",
            "- Security and logging checks pass before enabling by default.",
        ]
        write(step_dir / f"step_{step:02d}_import_order.md", "\n".join(lines))

    risks = [
        ("data_system.py", "Schema mismatch across YAML/JSON variants", "Enforce schema validators at loader boundary"),
        ("memory_system.py", "Context bloat and stale summary drift", "Cap context windows and nightly compaction"),
        ("enhanced_memory.py", "Nondeterministic summary outputs", "Seeded summarization tests with golden fixtures"),
        ("character_memory_rag.py", "Index growth and slow retrieval", "Periodic index rebuild and bounded result counts"),
        ("memory_query_engine.py", "Unsafe queries returning sensitive memory", "Trust-tier filters before query execution"),
        ("memory_hardening.py", "Over-aggressive blocking or suppression", "Tune thresholds with replay scenarios"),
        ("menstrual_cycle.py", "Phase edge-case rollover errors", "Boundary tests for day and cycle transitions"),
        ("emotional_engine.py", "Oscillation and unstable affect states", "Hysteresis and decay clamps"),
        ("stress_system.py", "Threshold spam events", "Debounce and cooldown on threshold emissions"),
        ("wyrd_system.py", "Overly large fate payloads", "Token-budgeted summarization of fate state"),
        ("world_will.py", "Atmosphere drift not grounded in signals", "Tie updates to measurable state changes"),
        ("story_phase.py", "Phase progression disconnected from outcomes", "Gate transitions on explicit completion metrics"),
        ("social_ledger.py", "Trust evidence skew from keyword heuristics", "Weighted evidence with manual override hooks"),
        ("relationship_graph.py", "Complex graph logic increases coupling", "Flatten to user-centric trust ledger"),
        ("social_protocol_engine.py", "False positives in compliance gating", "Human-readable reason codes and retry path"),
        ("thor_guardian.py", "Circuit opens too aggressively", "Per-operation thresholds and cooldown tuning"),
        ("crash_reporting.py", "PII leakage in exception metadata", "Redaction pass before log persistence"),
        ("comprehensive_logging.py", "Excessive log volume", "Sampling plus retention tiers"),
        ("local_providers.py", "Provider timeout cascades", "Strict timeouts and fallback lanes"),
        ("openrouter.py", "Unexpected provider behavior variance", "Provider allowlist and health checks"),
        ("turn_processor.py", "Monolithic orchestrator complexity", "Split pre, call, post stages with contracts"),
        ("timeline_service.py", "Timeline drift after restarts", "Persist canonical clock state each cycle"),
        ("world_systems.py", "Carried-over RPG mechanics pollution", "Adopt location context only"),
        ("voice_bridge.py", "Audio pipeline instability", "Feature flag and isolated subprocess boundaries"),
        ("religion_system.py", "Misalignment with project values constraints", "Restrict to scoring framework, not doctrine content"),
        ("witch_system.py", "Noisy lore extraction from broad corpora", "Source whitelists and quality filters"),
        ("rag_system.py", "Retrieval irrelevance on mixed datasets", "Hybrid scoring and domain filters"),
    ]

    for i, (mod, risk, mitigation) in enumerate(risks, 1):
        text = (
            f"# Import Risk - {mod}\n\n"
            "## Source\n"
            f"- `code_of_other_apps_that_can_be_adopted/{mod}`\n\n"
            "## Primary Risk\n"
            f"- {risk}.\n\n"
            "## Mitigation\n"
            f"- {mitigation}.\n\n"
            "## Required Test\n"
            "- Add at least one failing regression case then verify fix.\n"
            "- Verify behavior in degraded/fallback mode.\n"
        )
        write(risk_dir / f"risk_{i:02d}_{mod.replace('.py', '')}.md", text)

    write(
        seq_dir / "sequence_01_fastest_value_path.md",
        "# Sequence 01 Fastest Value Path\n\n"
        "1. Import `data_system.py` patterns for loader normalization.\n"
        "2. Import `memory_system.py` and `enhanced_memory.py` for usable memory context.\n"
        "3. Import `menstrual_cycle.py` and `emotional_engine.py` for living state.\n"
        "4. Import `thor_guardian.py` and `comprehensive_logging.py` for safe operations.\n"
        "5. Import `turn_processor.py` patterns to connect pre/call/post stages.\n",
    )

    write(
        seq_dir / "sequence_02_low_risk_path.md",
        "# Sequence 02 Low Risk Path\n\n"
        "1. Start with loader, logging, and timeline modules.\n"
        "2. Add security wrapper and crash reporting.\n"
        "3. Add memory stack with strict trust filtering.\n"
        "4. Add bio/emotion/wyrd modules behind feature flags.\n"
        "5. Enable routing and optional voice only after e2e pass.\n",
    )

    write(
        base / "WAVE3_INDEX.md",
        "# Wave3 Index\n\n"
        "## Added\n"
        "- `roadmap_step_import_plans/` (20 files)\n"
        "- `per_import_risks/` (27 files)\n"
        "- `execution_sequences/` (2 files)\n",
    )

    print("Wave3 docs generated.")


if __name__ == "__main__":
    main()
