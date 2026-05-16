# AI Research Insights (2026-05-04)

This document outlines the latest research discoveries in AI, LLMs, data science, structured data methods, virtual human intelligence simulation, and structured memory concepts, specifically aimed at improving the Viking Companion Skill project.

## Key Discoveries & Ideas

### 1. Structured Memory for Long-Horizon Behavior in LLMs (StructMem)
**Source**: *StructMem: Structured Memory for Long-Horizon Behavior in LLMs* (arXiv:2604.21748)

**Concept**:
Current memory systems face a trade-off: flat memory is efficient but lacks relational structure, while graph memory is expensive and fragile. StructMem uses a hierarchical approach:
- **Event-Level Binding**: Extracts factual and relational entries from interactions and temporally anchors them (e.g., tying facts and relations to a specific timestamp/turn).
- **Cross-Event Consolidation**: Periodically retrieves semantically related buffered events and synthesizes cross-event hypotheses to improve multi-hop and temporal reasoning.

**Code Ideas for Viking Skill**:
- Implement an **Event-Level Binder** for Astrid and Sigrid's `FederatedMemory`. Instead of just storing string logs of what a user says, store `[Timestamp, Factual_Extraction, Relational_Dynamics]` as a single unit.
- Implement a **Cross-Event Consolidator** within the `Odinsblund` (sleep cycle) process. During consolidation, cluster memories not just by decay, but by semantic similarity, and use the LLM to write a *synthesized* macro-memory that explicitly maps causal/temporal links between user actions across different sessions.

### 2. Dynamic Theory of Mind as a Temporal Memory Problem
**Source**: *Dynamic Theory of Mind as a Temporal Memory Problem: Evidence from Large Language Models* (arXiv:2603.14646)

**Concept**:
Theory of Mind (ToM) in LLMs is often evaluated statically, but real interaction requires "temporal belief tracking" - the ability to represent, update, and retrieve others' beliefs over time. Research shows LLMs easily infer current beliefs after an update but struggle severely to recall *prior* beliefs due to recency bias and interference.

**Code Ideas for Viking Skill**:
- **Belief Tracking System**: Implement a specific sub-module in the persona tracking system for the user's *belief state*. This shouldn't overwrite old beliefs but append them to a trajectory: `[Prior Belief, Turn Trigger, New Belief]`.
- **Inner Speech Verification**: Adopt the "inner speech prompting" paradigm mentioned in the research. When Astrid/Sigrid prepares a response, generate a hidden `(thought)` block that explicitly states their current hypothesis of the user's belief and intention, enforcing a structured ToM state *before* generating the outward-facing reply. This counters recency bias by explicitly loading historical context.

## Summary

The latest literature emphasizes moving beyond flat retrieval or rigid graphs toward **temporally-anchored event architectures** and **dynamic belief tracking**. For a virtual persona project simulating Viking intelligence and maintaining long-term relationships, tracking the *timeline of evolving user beliefs* and periodically *synthesizing cross-event memories* are key to creating more convincing, agentic behavior.
