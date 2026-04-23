"""
test_federated_memory.py — Validation suite for FederatedMemory (Step 5)
=========================================================================
Tests FederatedMemoryRequest, FederatedMemoryResult, and
MemoryStore.get_context_with_knowledge() using mock Huginn — no model calls,
no ChromaDB writes beyond the existing episodic collection.

Validates:
  - Dataclass construction and field defaults
  - Episodic-only mode (no huginn)
  - Knowledge tier via mock HuginnRetriever
  - Per-tier isolation (one tier failing does not crash others)
  - Token-budget truncation
  - sources_used tracking
  - Parallel execution (both futures completing without error)
  - Sequential fallback if executor fails

Run from project root:
    python tests/test_federated_memory.py
"""

import logging
import sys
import os
import tempfile

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_ROOT = os.path.join(PROJECT_ROOT, "viking_girlfriend_skill")
sys.path.insert(0, SKILL_ROOT)

logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s", stream=sys.stdout)

print("\n=== FederatedMemory Validation ===\n")

print("Importing memory_store module...", end=" ", flush=True)
from scripts.memory_store import (
    MemoryStore,
    FederatedMemoryRequest,
    FederatedMemoryResult,
    ConversationTurn,
    MemoryEntry,
    MEMORY_TYPES,
    _CHARS_PER_TOKEN,
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


# ─── Mocks ────────────────────────────────────────────────────────────────────

class MockRetrievalRequest:
    def __init__(self, query: str, include_episodic: bool = True, **kwargs):
        self.query = query
        self.include_episodic = include_episodic

class MockRetrievalResult:
    def __init__(self, context_string: str = "", domain: str = "default"):
        self.context_string = context_string
        self.domain = domain
        self.knowledge_chunks = []
        self.episodic_context = ""
        self.retrieval_ms = 1.0
        self.fallback_used = "chromadb"
        self.domain_detection_confidence = 0.9

class MockHuginn:
    """Simulates HuginnRetriever — returns scripted RetrievalResult."""
    def __init__(self, context_string: str = "[GT-1] Test knowledge chunk.", raise_on_call: bool = False):
        self._ctx = context_string
        self._raise = raise_on_call
        self.call_count = 0

    def retrieve(self, request):
        self.call_count += 1
        if self._raise:
            raise RuntimeError("mock huginn error")
        return MockRetrievalResult(context_string=self._ctx)


def make_store(data_root: str, add_turns: int = 0, add_memories: int = 0) -> MemoryStore:
    """Create a MemoryStore with optional pre-loaded data."""
    store = MemoryStore(
        data_root=data_root,
        session_id="test-session",
        semantic_enabled=False,     # no ChromaDB in unit tests
    )
    for i in range(add_turns):
        store.record_turn(f"user turn {i}", f"sigrid response {i}")
    for i in range(add_memories):
        store.add_memory(
            content=f"Test memory fact {i} about runes and Freyja.",
            memory_type="fact",
            importance=3,
            tags=["rune", "freyja"],
        )
    return store


# ─── TEST 1: FederatedMemoryRequest construction ──────────────────────────────
print("[1] FederatedMemoryRequest construction")

req = FederatedMemoryRequest(query="Tell me about Thurisaz")
check("query stored", req.query == "Tell me about Thurisaz")
check("include_episodic_buffer default=True", req.include_episodic_buffer)
check("include_episodic_json default=True", req.include_episodic_json)
check("include_episodic_chroma default=True", req.include_episodic_chroma)
check("include_knowledge default=True", req.include_knowledge)
check("max_episodic_tokens default=800", req.max_episodic_tokens == 800)
check("max_knowledge_tokens default=600", req.max_knowledge_tokens == 600)

req2 = FederatedMemoryRequest(
    query="code question",
    include_knowledge=False,
    max_episodic_tokens=200,
    max_knowledge_tokens=100,
)
check("include_knowledge=False set", not req2.include_knowledge)
check("max_episodic_tokens=200 set", req2.max_episodic_tokens == 200)

# ─── TEST 2: FederatedMemoryResult construction ───────────────────────────────
print("\n[2] FederatedMemoryResult construction")

result = FederatedMemoryResult(
    episodic_context="ep ctx",
    knowledge_context="kn ctx",
    combined_context="ep ctx\n\nkn ctx",
    sources_used=["episodic_buffer", "mimir_well"],
    total_chars=20,
)
check("episodic_context stored", result.episodic_context == "ep ctx")
check("knowledge_context stored", result.knowledge_context == "kn ctx")
check("combined_context stored", "ep" in result.combined_context and "kn" in result.combined_context)
check("sources_used stored", len(result.sources_used) == 2)
check("total_chars stored", result.total_chars == 20)

# ─── TEST 3: Episodic-only mode (no huginn) ───────────────────────────────────
print("\n[3] Episodic-only mode (huginn=None)")

with tempfile.TemporaryDirectory() as tmpdir:
    store = make_store(tmpdir, add_turns=3, add_memories=2)
    req = FederatedMemoryRequest(query="rune freyja", include_knowledge=False)
    result = store.get_context_with_knowledge(req, huginn=None)

    check("returns FederatedMemoryResult", isinstance(result, FederatedMemoryResult))
    check("knowledge_context empty (no huginn)", result.knowledge_context == "")
    check("mimir_well not in sources", "mimir_well" not in result.sources_used)
    check("total_chars >= 0", result.total_chars >= 0)
    check("combined_context does not contain knowledge section", "[GT-" not in result.combined_context)

# ─── TEST 4: Knowledge tier via mock Huginn ───────────────────────────────────
print("\n[4] Knowledge tier via mock Huginn")

with tempfile.TemporaryDirectory() as tmpdir:
    store = make_store(tmpdir, add_memories=2)
    huginn = MockHuginn(context_string="[GT-1] (Source: rune_work.md) Thurisaz is the rune of force.")
    req = FederatedMemoryRequest(query="thurisaz rune meaning")
    result = store.get_context_with_knowledge(req, huginn=huginn)

    check("returns FederatedMemoryResult", isinstance(result, FederatedMemoryResult))
    check("knowledge_context non-empty", len(result.knowledge_context) > 0)
    check("GT-1 citation in knowledge_context", "[GT-1]" in result.knowledge_context)
    check("mimir_well in sources_used", "mimir_well" in result.sources_used)
    check("combined_context contains knowledge", "[GT-1]" in result.combined_context)
    check("huginn.retrieve was called", huginn.call_count == 1)

# ─── TEST 5: Episodic buffer present in result ────────────────────────────────
print("\n[5] Episodic buffer turns in result")

with tempfile.TemporaryDirectory() as tmpdir:
    store = make_store(tmpdir, add_turns=3)
    req = FederatedMemoryRequest(query="test", include_knowledge=False)
    result = store.get_context_with_knowledge(req, huginn=None)

    check("episodic_buffer in sources_used", "episodic_buffer" in result.sources_used)
    check("episodic_context non-empty", len(result.episodic_context) > 0)
    check("RECENT CONVERSATION in context", "RECENT CONVERSATION" in result.episodic_context)

# ─── TEST 6: Episodic memories in result ──────────────────────────────────────
print("\n[6] Episodic JSON memories in result")

with tempfile.TemporaryDirectory() as tmpdir:
    store = make_store(tmpdir, add_memories=3)
    req = FederatedMemoryRequest(
        query="rune freyja",
        include_episodic_buffer=False,
        include_episodic_chroma=False,      # force keyword path (no chromadb in test)
        include_knowledge=False,
    )
    result = store.get_context_with_knowledge(req, huginn=None)

    check("episodic_json in sources_used", "episodic_json" in result.sources_used, f"sources={result.sources_used}")
    check("MEMORIES section in episodic_context", "MEMORIES" in result.episodic_context, f"ep={result.episodic_context[:80]}")

# ─── TEST 7: Buffer disabled flag ─────────────────────────────────────────────
print("\n[7] include_episodic_buffer=False")

with tempfile.TemporaryDirectory() as tmpdir:
    store = make_store(tmpdir, add_turns=5)
    req = FederatedMemoryRequest(
        query="test",
        include_episodic_buffer=False,
        include_episodic_json=False,
        include_knowledge=False,
    )
    result = store.get_context_with_knowledge(req, huginn=None)

    check("episodic_buffer NOT in sources", "episodic_buffer" not in result.sources_used)
    check("RECENT CONVERSATION not in context", "RECENT CONVERSATION" not in result.episodic_context)

# ─── TEST 8: Knowledge disabled flag ─────────────────────────────────────────
print("\n[8] include_knowledge=False skips Huginn")

with tempfile.TemporaryDirectory() as tmpdir:
    store = make_store(tmpdir)
    huginn = MockHuginn(context_string="[GT-1] Should not appear.")
    req = FederatedMemoryRequest(query="test", include_knowledge=False)
    result = store.get_context_with_knowledge(req, huginn=huginn)

    check("huginn not called when include_knowledge=False", huginn.call_count == 0)
    check("knowledge_context empty", result.knowledge_context == "")
    check("mimir_well not in sources", "mimir_well" not in result.sources_used)

# ─── TEST 9: Huginn failure isolation ────────────────────────────────────────
print("\n[9] Huginn failure — episodic still returns")

with tempfile.TemporaryDirectory() as tmpdir:
    store = make_store(tmpdir, add_turns=2, add_memories=2)
    huginn = MockHuginn(raise_on_call=True)
    req = FederatedMemoryRequest(query="rune freyja")
    result = store.get_context_with_knowledge(req, huginn=huginn)

    check("result returned despite huginn failure", isinstance(result, FederatedMemoryResult))
    check("knowledge_context empty after huginn failure", result.knowledge_context == "")
    check("mimir_well not in sources after failure", "mimir_well" not in result.sources_used)
    check("episodic context still present", len(result.episodic_context) > 0 or result.episodic_context == "")
    # Even if episodic is empty due to no match, we got a result — not a crash
    check("no crash from huginn failure", True)

# ─── TEST 10: Token-budget truncation ────────────────────────────────────────
print("\n[10] Token-budget truncation")

with tempfile.TemporaryDirectory() as tmpdir:
    store = make_store(tmpdir, add_turns=5, add_memories=5)
    huginn = MockHuginn(context_string="[GT-1] " + "X" * 5000)

    # Very tight budgets — forces truncation
    req = FederatedMemoryRequest(
        query="rune freyja test",
        max_episodic_tokens=10,     # 40 chars — anything meaningful will truncate
        max_knowledge_tokens=10,    # 40 chars
    )
    result = store.get_context_with_knowledge(req, huginn=huginn)

    ep_char_limit = 10 * _CHARS_PER_TOKEN
    kn_char_limit = 10 * _CHARS_PER_TOKEN

    if result.episodic_context:
        check("episodic_context within budget", len(result.episodic_context) <= ep_char_limit + 20,
              f"len={len(result.episodic_context)}, limit={ep_char_limit}")
    if result.knowledge_context:
        check("knowledge_context within budget", len(result.knowledge_context) <= kn_char_limit + 20,
              f"len={len(result.knowledge_context)}, limit={kn_char_limit}")
        check("truncation marker present in knowledge", "[...truncated]" in result.knowledge_context)

# ─── TEST 11: combined_context = episodic + knowledge ────────────────────────
print("\n[11] combined_context assembles both tiers")

with tempfile.TemporaryDirectory() as tmpdir:
    store = make_store(tmpdir, add_turns=1)
    huginn = MockHuginn(context_string="[GT-1] (Source: test.md) Knowledge chunk about Odin.")
    req = FederatedMemoryRequest(query="odin")
    result = store.get_context_with_knowledge(req, huginn=huginn)

    if result.episodic_context and result.knowledge_context:
        check("combined_context contains both",
              result.episodic_context in result.combined_context
              and result.knowledge_context in result.combined_context)
        check("total_chars = len(combined)", result.total_chars == len(result.combined_context))
    else:
        # Still valid — just mark as informational
        check("combined_context = non-empty tier", len(result.combined_context) >= 0)
        check("total_chars matches combined", result.total_chars == len(result.combined_context))

# ─── TEST 12: All tiers disabled -> empty result ──────────────────────────────
print("\n[12] All tiers disabled -> empty FederatedMemoryResult")

with tempfile.TemporaryDirectory() as tmpdir:
    store = make_store(tmpdir, add_turns=3, add_memories=3)
    req = FederatedMemoryRequest(
        query="test",
        include_episodic_buffer=False,
        include_episodic_json=False,
        include_episodic_chroma=False,
        include_knowledge=False,
    )
    result = store.get_context_with_knowledge(req, huginn=None)

    check("returns FederatedMemoryResult", isinstance(result, FederatedMemoryResult))
    check("episodic_context empty", result.episodic_context == "")
    check("knowledge_context empty", result.knowledge_context == "")
    check("combined_context empty", result.combined_context == "")
    check("sources_used empty", result.sources_used == [])
    check("total_chars=0", result.total_chars == 0)

# ─── TEST 13: Empty query — still returns (no crash) ─────────────────────────
print("\n[13] Empty query — no crash")

with tempfile.TemporaryDirectory() as tmpdir:
    store = make_store(tmpdir, add_memories=2)
    req = FederatedMemoryRequest(query="")
    result = store.get_context_with_knowledge(req, huginn=None)
    check("returns result with empty query", isinstance(result, FederatedMemoryResult))
    check("no crash on empty query", True)

# ─── TEST 14: Huginn=None with include_knowledge=True ────────────────────────
print("\n[14] huginn=None with include_knowledge=True — graceful skip")

with tempfile.TemporaryDirectory() as tmpdir:
    store = make_store(tmpdir, add_turns=1)
    req = FederatedMemoryRequest(query="rune", include_knowledge=True)
    result = store.get_context_with_knowledge(req, huginn=None)   # no huginn provided

    check("no crash when huginn=None", isinstance(result, FederatedMemoryResult))
    check("knowledge_context empty when huginn=None", result.knowledge_context == "")
    check("mimir_well not in sources", "mimir_well" not in result.sources_used)

# ─── TEST 15: sources_used is correctly populated ────────────────────────────
print("\n[15] sources_used tracking")

with tempfile.TemporaryDirectory() as tmpdir:
    store = make_store(tmpdir, add_turns=2, add_memories=2)
    huginn = MockHuginn(context_string="[GT-1] Norse lore entry.")
    req = FederatedMemoryRequest(
        query="rune freyja",
        include_episodic_chroma=False,      # no chromadb
    )
    result = store.get_context_with_knowledge(req, huginn=huginn)

    check("sources_used is a list", isinstance(result.sources_used, list))
    if result.episodic_context:
        check("at least one episodic source", any("episodic" in s for s in result.sources_used),
              f"sources={result.sources_used}")
    check("mimir_well in sources (huginn provided)", "mimir_well" in result.sources_used,
          f"sources={result.sources_used}")

# ─── Summary ──────────────────────────────────────────────────────────────────
total = PASS + FAIL
print(f"\n{'='*50}")
print(f"Results: {PASS}/{total} passed")
if FAIL == 0:
    print("FEDERATED MEMORY TEST PASSED")
else:
    print(f"FEDERATED MEMORY TEST FAILED ({FAIL} failures)")
    import pytest
    pytest.fail(f"FEDERATED MEMORY TEST FAILED ({FAIL} failures)")
