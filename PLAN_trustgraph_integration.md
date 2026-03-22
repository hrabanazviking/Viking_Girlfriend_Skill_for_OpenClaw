# PLAN: TrustGraph Integration
**Date:** 2026-03-22
**Status:** AWAITING APPROVAL

---

## What TrustGraph Actually Is

TrustGraph is a **knowledge graph platform** — not a trust/reputation scoring system (that
name is a bit misleading). It is infrastructure-as-a-service for structured knowledge
storage and retrieval, built around:

- **Apache Cassandra** — multi-model data storage
- **Qdrant** — vector database for embeddings
- **Apache Pulsar** — pub/sub event streaming
- **Three RAG modes** — DocumentRAG (vector), GraphRAG (entity/relationship), OntologyRAG (schema-driven)
- **Context Cores** — versioned, portable knowledge bundles
- **Python SDK** — `pip install trustgraph-api` → connects to a running TrustGraph instance

---

## The Core Problem: Infrastructure Weight

TrustGraph requires running a full cloud-native stack (Cassandra + Qdrant + Pulsar +
more). This conflicts with the Ørlög architecture's core design goal:

> **Modular + cross-platform — works on Windows, Linux, Mac, RPi**

Running TrustGraph on a Raspberry Pi is not feasible. Running it remotely adds an external
dependency and breaks the sovereign/local privacy model.

**The existing stack is already very capable:**
- ChromaDB (local, sovereign) — vector search
- BM25 fallback — keyword search with no dependencies
- Ollama nomic-embed-text — local embeddings (no Voyage AI)
- MimirWell 3-level hierarchy — raw chunks, cluster summaries, axioms
- memory_store.py — 3-layer session + episodic + semantic memory

---

## What TrustGraph Could Genuinely Add

The one feature that would meaningfully improve the skill is **GraphRAG** — storing
knowledge as entities and relationships in a graph, then retrieving context by traversing
those relationships rather than just semantic similarity.

Example: "What did Sigrid say about runes in the context of Odin?" is better answered by
graph traversal (Odin → related_to → Runes → discussed_in → session_42) than pure vector
search, which just returns the most semantically similar chunks.

The other features (Context Cores, OntologyRAG, full Cassandra stack) are overkill for
this use case at this stage.

---

## Proposed Integration: Lightweight Optional Enhancement

Rather than a hard dependency on TrustGraph's full infrastructure, integrate it as an
**optional enhancement layer** that activates when a TrustGraph endpoint is configured.
The skill runs perfectly without it — TrustGraph unlocks advanced GraphRAG when available.

### New Module: `trustgraph_client.py`

A thin wrapper around `trustgraph-api` with:
- Connection probe (checks if TrustGraph endpoint is reachable at startup)
- `available` property — graceful feature flag
- `graph_rag_query(query, collection)` — GraphRAG retrieval
- `store_triple(subject, predicate, object)` — write entity relationships
- `load_document(text, doc_id)` — index documents into TrustGraph
- Full circuit-breaker + fallback pattern (consistent with rest of codebase)

### Integration Points

| Module | Change | Benefit |
|---|---|---|
| `mimir_well.py` | Add TrustGraph GraphRAG as Layer 4 above BM25/ChromaDB | Relationship-aware retrieval |
| `memory_store.py` | On episodic store writes, optionally mirror to TrustGraph triples | Graph-queryable memory |
| `trustgraph_client.py` | New module — TrustGraph connection wrapper | Clean separation of concerns |
| `litellm_config.yaml` | No change needed — TrustGraph handles its own model routing | — |

### What Does NOT Change
- ChromaDB remains the primary vector store (local, sovereign, always available)
- BM25 remains the fallback (zero dependencies)
- Ollama embeddings remain sovereign
- Nothing breaks if TrustGraph is not running

---

## Implementation Plan (4 Waves)

### Wave TG-1: Client Module
- Create `trustgraph_client.py` — connection, probe, GraphRAG query, triple store
- Register in `runtime_kernel.py` as an optional subsystem
- Add `trustgraph` config block to default config in `main.py`
- Add `trustgraph-api` to `requirements.txt` as optional dependency

### Wave TG-2: MimirWell Enhancement
- In `mimir_well.py`: after BM25+ChromaDB retrieval, optionally call
  `trustgraph_client.graph_rag_query()` if client is available
- Re-rank and merge results across all sources
- Add `use_trustgraph` flag to `MimirWell.__init__()` and `from_config()`

### Wave TG-3: Memory Store Mirroring
- In `memory_store.py`: when a new episodic entry is saved (fact, milestone, preference),
  optionally mirror it as a TrustGraph triple:
  `(sigrid, remembers, "<memory text>")` and `(user, expressed, "<memory text>")`
- This builds a growing knowledge graph of Sigrid's relational memory over time

### Wave TG-4: Infrastructure & Docs
- Add TrustGraph service to `podman-compose.yml` (optional profile — off by default)
- Add `TRUSTGRAPH_ENDPOINT` and `TRUSTGRAPH_TOKEN` to `.env.example`
- Document setup in `README_AI.md` for the scripts/ folder

---

## Questions for Discussion

1. **Do we want this at all right now?** The existing memory system is solid. TrustGraph
   adds complexity. It might make more sense to do this after launch, as an advanced feature.

2. **Deployment target:** If this skill is meant to run on RPi or as a lightweight container,
   TrustGraph's infrastructure is too heavy to bundle. It would need to be a remote service.

3. **Privacy:** If TrustGraph runs remotely, Sigrid's memories leave the local environment.
   This conflicts with the sovereignty design goal. Running it locally on the same machine
   is feasible but resource-heavy.

4. **Scope:** Should we do all 4 waves now, or just Wave TG-1 (client module) as a foundation
   and defer the memory mirroring until there's a proven use case?

---

## My Honest Recommendation

Do **Wave TG-1 only** now (the client module + config wiring), leaving all the actual
data-flow changes to a future session. This gives us:
- Clean integration point for TrustGraph if/when needed
- Zero disruption to working systems
- Passes the test suite unchanged
- Can be extended to full GraphRAG whenever there's a real deployment that can host it

If you want the full 4-wave implementation now, I am ready to proceed — just flag which
privacy/deployment model you want (local bundle vs remote service).
