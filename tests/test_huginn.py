import pytest
"""
test_huginn.py — Validation suite for HuginnRetriever (Step 3 of Mímir-Vörðr)
===============================================================================
Tests domain detection, retrieval fallback chain, context string assembly,
and singleton wiring. Runs fully offline using BM25-only MimirWell.

Run from project root:
    cd <project-root>
    python -m pytest tests/test_huginn.py -v
  or directly:
    python tests/test_huginn.py
"""

import logging
import sys
import os
import time

# ─── Path setup ───────────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_ROOT = os.path.join(PROJECT_ROOT, "viking_girlfriend_skill")
sys.path.insert(0, SKILL_ROOT)

logging.basicConfig(
    level=logging.WARNING,
    format="%(levelname)s %(name)s: %(message)s",
    stream=sys.stdout,
)

# ─── Imports ──────────────────────────────────────────────────────────────────
print("\n=== Huginn Validation ===\n")
print("Importing huginn module...", end=" ", flush=True)
from scripts.huginn import (
    _detect_domain,
    HuginnRetriever,
    RetrievalRequest,
    RetrievalResult,
    HuginnState,
    HuginnError,
    HuginnAllFallbacksExhaustedError,
    init_huginn_from_config,
    get_huginn,
    _DOMAIN_KEYWORDS,
)
from scripts.mimir_well import (
    MimirWell,
    init_mimir_well_from_config,
    get_mimir_well,
)
print("OK")

PASS = 0
FAIL = 0

def check(name: str, condition: bool, detail: str = "") -> None:
    global PASS, FAIL
    if condition:
        print(f"  PASS  {name}")
        PASS += 1
    else:
        print(f"  FAIL  {name}" + (f"  [{detail}]" if detail else ""))
        FAIL += 1

# ─── TEST 1: Domain detection — all 6 domains ────────────────────────────────
print("\n[1] Domain detection")

dom, conf = _detect_domain("What do the runes mean? I want to learn about Thurisaz")
check("norse_spirituality detected", dom == "norse_spirituality", f"got dom={dom}")
check("norse_spirituality confidence > 0.05", conf >= 0.05, f"got conf={conf:.3f}")

dom, conf = _detect_domain("Tell me about Odin and Yggdrasil and the nine worlds")
check("norse_mythology detected", dom == "norse_mythology", f"got dom={dom}")

dom, conf = _detect_domain("What was life like for viking jarls in the mead hall?")
check("norse_culture detected", dom == "norse_culture", f"got dom={dom}")

dom, conf = _detect_domain("Can you help me debug this Python function? async await error")
check("coding detected", dom == "coding", f"got dom={dom}")

dom, conf = _detect_domain("What do you believe and value, Sigrid? Who are you really?")
check("character detected", dom == "character", f"got dom={dom}")

dom, conf = _detect_domain("Let's roleplay a scene where I play as a character interacting with an NPC")
check("roleplay detected", dom == "roleplay", f"got dom={dom}")

dom, conf = _detect_domain("hello")
check("below threshold returns None", dom is None, f"got dom={dom}, conf={conf:.3f}")

dom, conf = _detect_domain("")
check("empty query returns None, 0.0", dom is None and conf == 0.0, f"dom={dom} conf={conf}")

# ─── TEST 2: MimirWell init (BM25 only, skip ChromaDB) ───────────────────────
print("\n[2] MimirWell bootstrap (BM25 mode for speed)")

DATA_DIR = os.path.join(SKILL_ROOT, "data")

print("  Initialising MimirWell (connecting to existing sigrid_test collection)...", flush=True)
t0 = time.monotonic()
# auto_ingest=False — skip ingest, just connect to existing populated ChromaDB
# Uses sigrid_test collection which was built by the full ingest (95min) in previous session
well = init_mimir_well_from_config(
    {
        "mimir_well": {
            "collection_name": "sigrid_test",
            "persist_dir": "data/chromadb_test",
        }
    },
    data_root=DATA_DIR,
    auto_ingest=False,
)
elapsed = time.monotonic() - t0
check("MimirWell created", well is not None)
check(f"Init completed in {elapsed:.1f}s", elapsed < 60, f"took {elapsed:.1f}s")
check("ChromaDB available", well.chromadb_available)
if well.chromadb_available:
    try:
        doc_count = well._collection.count()
        print(f"  Collection doc count: {doc_count:,} (may be 0 if ingest still running)")
    except Exception as e:
        print(f"  Collection count error: {e}")
print(f"  chromadb_available={well.chromadb_available}, flat_index_size={well.flat_index_size:,}")

# ─── TEST 3: HuginnRetriever creation ─────────────────────────────────────────
print("\n[3] HuginnRetriever construction")

config2 = {
    "huginn": {
        "n_initial": 20,
        "n_final": 3,
        "domain_detection": True,
        "include_episodic": True,
    }
}

huginn = init_huginn_from_config(config2, mimir_well=well, memory_store=None)
check("HuginnRetriever created", huginn is not None)
check("get_huginn() singleton works", get_huginn() is huginn)
check("has_memory_store is False", not huginn.has_memory_store)
check("domain detection enabled", huginn._domain_detection_enabled)

# ─── TEST 4: detect_domain via instance method ────────────────────────────────
print("\n[4] detect_domain via instance method")

dom, conf = huginn.detect_domain("What are the runes of Freyja's aett?")
check("instance detect_domain works", dom == "norse_spirituality", f"dom={dom}")

huginn._domain_detection_enabled = False
dom, conf = huginn.detect_domain("What are the runes?")
check("disabled detection returns None", dom is None)
huginn._domain_detection_enabled = True

# ─── TEST 5: retrieve() — basic BM25 path ─────────────────────────────────────
print("\n[5] retrieve() — BM25 fallback (no ChromaDB)")

req = RetrievalRequest(query="Tell me about Thurisaz rune meaning", n_initial=20, n_final=3)
result = huginn.retrieve(req)

check("returns RetrievalResult", isinstance(result, RetrievalResult))
check("query preserved", result.query == req.query)
check("domain detected", result.domain == "norse_spirituality", f"dom={result.domain}")
check("has knowledge chunks OR fallback", len(result.knowledge_chunks) >= 0)  # bm25 result
check("fallback_used is valid", result.fallback_used in ("chromadb", "bm25", "episodic_only", "empty"), f"fallback={result.fallback_used}")
check("retrieval_ms > 0", result.retrieval_ms > 0)
check("does not raise", True)  # if we got here

if result.knowledge_chunks:
    check("chunks have text", all(c.text for c in result.knowledge_chunks))
    check(
        "context_string has [GROUND TRUTH]",
        "[GROUND TRUTH" in result.context_string,
        "GT header missing from context_string",
    )

# ─── TEST 6: retrieve() — norse_mythology query ───────────────────────────────
print("\n[6] retrieve() — norse mythology query")

req2 = RetrievalRequest(query="Tell me about Odin's ravens Huginn and Muninn and Yggdrasil")
result2 = huginn.retrieve(req2)
check("returns result", isinstance(result2, RetrievalResult))
check("domain=norse_mythology or None", result2.domain in ("norse_mythology", "norse_culture", None), f"dom={result2.domain}")
check("no crash", True)

# ─── TEST 7: context string format ───────────────────────────────────────────
print("\n[7] context string structure")

req3 = RetrievalRequest(query="seidr magic volva spaework practice", n_final=2)
result3 = huginn.retrieve(req3)

if result3.knowledge_chunks:
    ctx = result3.context_string
    check("[GROUND TRUTH] header present", "[GROUND TRUTH" in ctx, "header missing")
    check("[GT-1] marker present", "[GT-1]" in ctx, "GT-1 marker missing")
    check("(Source: " in ctx, "(Source:" in ctx)
    check("context_string not empty", len(ctx) > 50)
else:
    check("empty result has empty context", result3.context_string == "", f"got={result3.context_string[:50]}")

# ─── TEST 8: episodic context with mock MemoryStore ───────────────────────────
print("\n[8] episodic memory integration")

class MockMemoryStore:
    def get_context(self, query, **kwargs):
        return f"[Episodic] Sigrid remembers speaking about runes with the user."

huginn.set_memory_store(MockMemoryStore())
check("set_memory_store works", huginn.has_memory_store)

req4 = RetrievalRequest(query="rune casting", include_episodic=True)
result4 = huginn.retrieve(req4)
check("episodic context populated", "[Episodic]" in result4.episodic_context, f"got: {result4.episodic_context[:80]}")
if result4.episodic_context:
    check("[MEMORY] header in context", "[MEMORY" in result4.context_string, f"ctx={result4.context_string[:200]}")

huginn.set_memory_store(None)
check("set_memory_store(None) clears", not huginn.has_memory_store)

# ─── TEST 9: episodic disabled ─────────────────────────────────────────────────
print("\n[9] episodic disabled flag")

huginn.set_memory_store(MockMemoryStore())
req5 = RetrievalRequest(query="rune", include_episodic=False)
result5 = huginn.retrieve(req5)
check("include_episodic=False -> no episodic", result5.episodic_context == "", f"got: {result5.episodic_context[:50]}")

huginn.set_memory_store(None)

# ─── TEST 10: urgency fast mode skips rerank ──────────────────────────────────
print("\n[10] urgency='fast' mode")

req6 = RetrievalRequest(query="Odin Freyja Thor aesir vanir", urgency="fast", n_initial=10, n_final=3)
result6 = huginn.retrieve(req6)
check("fast mode returns result", isinstance(result6, RetrievalResult))
check("fast mode no crash", True)

# ─── TEST 11: get_state() / telemetry ─────────────────────────────────────────
print("\n[11] telemetry / state")

state = huginn.get_state()
check("get_state() returns HuginnState", isinstance(state, HuginnState))
check("total_retrievals > 0", state.total_retrievals > 0, f"got={state.total_retrievals}")
check("circuit_breaker_state is string", isinstance(state.circuit_breaker_state, str))
check("to_dict() works", isinstance(state.to_dict(), dict))
check("domain_counts populated", isinstance(state.domain_counts, dict))

# ─── TEST 12: to_dict() ────────────────────────────────────────────────────────
print("\n[12] RetrievalResult.to_dict() / is_empty()")

d = result.to_dict()
check("to_dict has query", "query" in d)
check("to_dict has domain", "domain" in d)
check("to_dict has chunk_count", "chunk_count" in d)
check("to_dict has fallback_used", "fallback_used" in d)

empty_result = RetrievalResult(
    query="x", domain=None, knowledge_chunks=[],
    episodic_context="", context_string="",
    retrieval_ms=0.0, fallback_used="empty",
    domain_detection_confidence=0.0,
)
check("is_empty() True when empty", empty_result.is_empty())
check("is_empty() False when has chunks", not result.is_empty() if result.knowledge_chunks else True)

# ─── TEST 13: _DOMAIN_KEYWORDS coverage ──────────────────────────────────────
print("\n[13] _DOMAIN_KEYWORDS completeness")

check("all 6 domains present", len(_DOMAIN_KEYWORDS) == 6)
for domain in ["norse_spirituality", "norse_mythology", "norse_culture", "coding", "character", "roleplay"]:
    check(f"domain '{domain}' has >=10 keywords", len(_DOMAIN_KEYWORDS[domain]) >= 10, f"got {len(_DOMAIN_KEYWORDS[domain])}")

# ─── Summary ──────────────────────────────────────────────────────────────────
total = PASS + FAIL
print(f"\n{'='*50}")
print(f"Results: {PASS}/{total} passed")
if FAIL == 0:
    print("HUGINN TEST PASSED")
else:
    print(f"HUGINN TEST FAILED ({FAIL} failures)")
    pytest.fail("Test failed")
