"""
test_cove_pipeline.py — Validation suite for CovePipeline (Step 4)
===================================================================
Tests all CoVe logic paths using mock router/vordur — no model calls required.
Validates checkpoint persistence, fallback chain, complexity gating,
circuit breaker bypass, and step failure recovery.

Run from project root:
    python tests/test_cove_pipeline.py
"""

import logging
import sys
import os
import json
import tempfile
from pathlib import Path

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_ROOT = os.path.join(PROJECT_ROOT, "viking_girlfriend_skill")
sys.path.insert(0, SKILL_ROOT)

logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s", stream=sys.stdout)

print("\n=== CovePipeline Validation ===\n")
print("Importing cove_pipeline module...", end=" ", flush=True)
from scripts.cove_pipeline import (
    CovePipeline,
    CoveCheckpoint,
    CoveResult,
    CoveState,
    CovePipelineError,
    CoveStepFailedError,
    TEMPLATE_QUESTIONS,
    init_cove_from_config,
    get_cove,
)
from scripts.mimir_well import init_mimir_well_from_config
from scripts.huginn import RetrievalResult, RetrievalRequest
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

class MockResponse:
    def __init__(self, content: str):
        self.content = content

class MockRouter:
    """Simulates ModelRouterClient — returns scripted responses."""
    def __init__(self, responses: dict = None):
        self._responses = responses or {}
        self._call_log = []

    def complete(self, messages, tier=None, timeout_s=None, **kwargs):
        self._call_log.append({"tier": tier, "msg": messages[-1].content[:60] if messages else ""})
        # If 'raise' is set, raise an error
        if self._responses.get("raise"):
            raise RuntimeError("mock model error")
        # Return scripted response or default
        return MockResponse(self._responses.get("content", "This is a mock draft response."))

class MockMessage:
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content

class MockVordur:
    def score(self, response, chunks, **kwargs):
        return None

DATA_DIR = os.path.join(SKILL_ROOT, "data")

# ─── Bootstrap MimirWell (no ingest) ─────────────────────────────────────────
print("[0] MimirWell bootstrap (no ingest)...")
well = init_mimir_well_from_config(
    {"mimir_well": {"collection_name": "sigrid_test", "persist_dir": "data/chromadb_test"}},
    data_root=None,
    auto_ingest=False,
)
check("MimirWell created", well is not None)

# ─── Make a minimal RetrievalResult ──────────────────────────────────────────
def make_retrieval(domain=None):
    return RetrievalResult(
        query="test query",
        domain=domain,
        knowledge_chunks=[],
        episodic_context="",
        context_string="[GROUND TRUTH]\n[GT-1] Test source chunk about runes.",
        retrieval_ms=5.0,
        fallback_used="bm25",
        domain_detection_confidence=0.2,
    )

# ─── TEST 1: CovePipeline construction ────────────────────────────────────────
print("\n[1] CovePipeline construction")

with tempfile.TemporaryDirectory() as tmpdir:
    router = MockRouter({"content": "A draft response about runes."})
    vordur = MockVordur()
    cove = CovePipeline(
        mimir_well=well,
        router=router,
        vordur=vordur,
        checkpoint_dir=Path(tmpdir),
    )
    check("CovePipeline created", cove is not None)
    check("checkpoint_dir is set", cove._checkpoint_dir == Path(tmpdir))
    check("n_questions default=3", cove._n_questions == 3)
    check("min_complexity default=medium", cove._min_complexity == "medium")

# ─── TEST 2: Singleton ─────────────────────────────────────────────────────────
print("\n[2] Singleton")

with tempfile.TemporaryDirectory() as tmpdir:
    router = MockRouter({"content": "A draft."})
    vordur = MockVordur()
    config = {
        "cove": {
            "min_complexity": "low",
            "n_verification_questions": 2,
            "checkpoint_dir": tmpdir,
            "step_timeout_s": 10.0,
        }
    }
    cove_singleton = init_cove_from_config(config, well, router, vordur)
    check("init_cove_from_config returns CovePipeline", isinstance(cove_singleton, CovePipeline))
    check("get_cove() returns singleton", get_cove() is cove_singleton)
    check("min_complexity set from config", cove_singleton._min_complexity == "low")
    check("n_questions set from config", cove_singleton._n_questions == 2)

# ─── TEST 3: Low complexity bypass ───────────────────────────────────────────
print("\n[3] Low complexity bypass")

with tempfile.TemporaryDirectory() as tmpdir:
    router = MockRouter({"content": "Quick answer."})
    cove = CovePipeline(well, router, MockVordur(), min_complexity="medium", checkpoint_dir=Path(tmpdir))
    retrieval = make_retrieval()
    result = cove.run("simple question", "[GT-1] context", retrieval, complexity="low")
    check("returns CoveResult", isinstance(result, CoveResult))
    check("used_cove=False for low complexity", not result.used_cove)
    check("steps_completed=1", result.steps_completed == 1)
    check("no verification questions", result.verification_questions == [])
    check("no qa_pairs", result.qa_pairs == [])
    check("final_response = draft", result.final_response == result.draft)
    check("fallback_chain has low_complexity_skip", "low_complexity_skip" in result.fallback_chain)
    check("total_skipped_low incremented", cove._total_skipped_low == 1)

# ─── TEST 4: Medium complexity — full CoVe path ───────────────────────────────
print("\n[4] Medium complexity — full pipeline (mock router)")

with tempfile.TemporaryDirectory() as tmpdir:
    # Router returns different content per step based on message content
    call_count = {"n": 0}
    class SequencedRouter:
        def complete(self, messages, tier=None, timeout_s=None, **kwargs):
            call_count["n"] += 1
            n = call_count["n"]
            if n == 1:
                return MockResponse("This is the initial draft about Thurisaz rune.")
            elif n == 2:
                return MockResponse("1. Is the rune name correct?\n2. Is the meaning accurate?\n3. Is the direction correct?")
            elif n <= 5:  # answering questions
                return MockResponse("Yes, this is consistent with the source.")
            else:
                return MockResponse("This is the revised and verified final response.")

    cove = CovePipeline(well, SequencedRouter(), MockVordur(), checkpoint_dir=Path(tmpdir))
    retrieval = make_retrieval(domain="norse_spirituality")
    result = cove.run("Tell me about Thurisaz", "[GT-1] Thurisaz is the rune of the giant.", retrieval, complexity="medium")

    check("CoveResult returned", isinstance(result, CoveResult))
    check("used_cove=True", result.used_cove)
    check("steps_completed=4", result.steps_completed == 4, f"got {result.steps_completed}")
    check("draft non-empty", len(result.draft) > 0)
    check("final_response non-empty", len(result.final_response) > 0)
    check("no error_context", result.error_context is None)
    check("total_runs incremented", cove._total_runs == 1)

# ─── TEST 5: Step 2 fallback — model returns empty → template questions ───────
print("\n[5] Step 2 fallback to template questions")

with tempfile.TemporaryDirectory() as tmpdir:
    call_count = {"n": 0}
    class RouterStep2Fails:
        def complete(self, messages, tier=None, timeout_s=None, **kwargs):
            call_count["n"] += 1
            if call_count["n"] == 1:
                return MockResponse("Draft answer about seidr magic.")
            if call_count["n"] == 2:
                return MockResponse("")  # empty → triggers template fallback
            return MockResponse("Answer to question. Revised response.")

    cove = CovePipeline(well, RouterStep2Fails(), MockVordur(), checkpoint_dir=Path(tmpdir))
    retrieval = make_retrieval(domain="norse_spirituality")
    result = cove.run("What is seidr?", "[GT-1] Seidr is Norse magic.", retrieval, complexity="medium")

    check("result returned", isinstance(result, CoveResult))
    check("used_cove=True", result.used_cove, f"used_cove={result.used_cove}")
    # Template questions should be used
    if result.verification_questions:
        check("template questions used (norse_spirituality)", any(
            "rune" in q.lower() or "norse" in q.lower() or "heathen" in q.lower()
            for q in result.verification_questions
        ))
    check("fallback_chain has step2 fallback", any("step2" in f for f in result.fallback_chain), f"chain={result.fallback_chain}")

# ─── TEST 6: Step 4 fallback — returns Step 1 draft ──────────────────────────
print("\n[6] Step 4 fallback to Step 1 draft")

with tempfile.TemporaryDirectory() as tmpdir:
    call_count = {"n": 0}
    class RouterStep4Fails:
        def complete(self, messages, tier=None, timeout_s=None, **kwargs):
            call_count["n"] += 1
            if call_count["n"] == 1:
                return MockResponse("The original draft response.")
            if call_count["n"] == 2:
                return MockResponse("1. Is this accurate?\n2. Any errors?\n3. Consistent?")
            if call_count["n"] <= 5:
                return MockResponse("Yes, consistent with source.")
            raise RuntimeError("Step 4 model error")  # Step 4 fails

    cove = CovePipeline(well, RouterStep4Fails(), MockVordur(), checkpoint_dir=Path(tmpdir))
    retrieval = make_retrieval()
    result = cove.run("Test query", "[GT-1] context.", retrieval, complexity="medium")

    check("result returned", isinstance(result, CoveResult))
    check("final_response = original draft", result.final_response == result.draft, f"final={result.final_response[:50]}")
    check("fallback chain has step4 fallback", any("step4" in f for f in result.fallback_chain), f"chain={result.fallback_chain}")
    check("steps_completed >= 3", result.steps_completed >= 3, f"got {result.steps_completed}")

# ─── TEST 7: Circuit breaker bypass ──────────────────────────────────────────
print("\n[7] Circuit breaker bypass")

with tempfile.TemporaryDirectory() as tmpdir:
    router = MockRouter({"content": "Direct draft, bypassed CoVe."})
    cove = CovePipeline(well, router, MockVordur(), checkpoint_dir=Path(tmpdir))

    # Manually open the pipeline circuit breaker
    for _ in range(5):
        try:
            cove._cb_pipeline.on_failure(RuntimeError("test failure"))
        except Exception:
            pass

    retrieval = make_retrieval()
    result = cove.run("query after CB open", "[GT-1] context", retrieval, complexity="medium")

    check("result returned after CB bypass", isinstance(result, CoveResult))
    check("used_cove=False after CB bypass", not result.used_cove)
    check("total_bypassed_cb incremented", cove._total_bypassed_cb > 0)
    check("fallback_chain has pipeline_cb_bypass", "pipeline_cb_bypass" in result.fallback_chain)

# ─── TEST 8: Checkpoint save and load ────────────────────────────────────────
print("\n[8] Checkpoint persistence")

with tempfile.TemporaryDirectory() as tmpdir:
    cove = CovePipeline(well, MockRouter(), MockVordur(), checkpoint_dir=Path(tmpdir))

    cp = CoveCheckpoint(
        checkpoint_id="test_abc",
        query="test query",
        context="[GT-1] source",
        domain="norse_spirituality",
        draft="The initial draft.",
        questions=["Is this accurate?", "Any errors?"],
        qa_pairs=[("Is this accurate?", "Yes."), ("Any errors?", "No.")],
        step_reached=3,
    )
    cove._save_checkpoint(cp)

    loaded = cove.load_checkpoint("test_abc")
    check("checkpoint saved and loaded", loaded is not None)
    check("checkpoint_id preserved", loaded.checkpoint_id == "test_abc")
    check("draft preserved", loaded.draft == "The initial draft.")
    check("questions preserved", loaded.questions == ["Is this accurate?", "Any errors?"])
    check("qa_pairs preserved", len(loaded.qa_pairs) == 2)
    check("step_reached preserved", loaded.step_reached == 3)
    check("domain preserved", loaded.domain == "norse_spirituality")

    # Test list_checkpoints
    cp2 = CoveCheckpoint(checkpoint_id="test_xyz", query="q", context="c", domain=None)
    cove._save_checkpoint(cp2)
    ids = cove.list_checkpoints()
    check("list_checkpoints returns both IDs", "test_abc" in ids and "test_xyz" in ids, f"ids={ids}")

    # Test delete
    cove._delete_checkpoint(cp)
    check("checkpoint deleted", cove.load_checkpoint("test_abc") is None)

# ─── TEST 9: Checkpoint resume ────────────────────────────────────────────────
print("\n[9] Checkpoint resume (skip steps 1-2)")

with tempfile.TemporaryDirectory() as tmpdir:
    call_count = {"n": 0}
    class RouterCheckStep:
        def complete(self, messages, tier=None, timeout_s=None, **kwargs):
            call_count["n"] += 1
            return MockResponse(f"Response to call {call_count['n']}")

    # Simulate a checkpoint where Step 2 is already done (step_reached=2)
    prior = CoveCheckpoint(
        checkpoint_id="resume_test",
        query="resuming query",
        context="[GT-1] resumed context",
        domain="coding",
        draft="Prior Step 1 draft.",
        questions=["Is the API correct?", "Any syntax errors?", "Is the logic sound?"],
        qa_pairs=None,
        step_reached=2,
    )

    cove = CovePipeline(well, RouterCheckStep(), MockVordur(), checkpoint_dir=Path(tmpdir))
    retrieval = make_retrieval(domain="coding")
    result = cove.run(
        "resuming query", "[GT-1] resumed context", retrieval,
        complexity="medium", resume_checkpoint=prior
    )

    check("result returned from resume", isinstance(result, CoveResult))
    # draft should be preserved from checkpoint
    check("draft from checkpoint", result.draft == "Prior Step 1 draft.", f"draft={result.draft[:60]}")
    check("questions from checkpoint", result.verification_questions == prior.questions)
    check("steps_completed=4", result.steps_completed == 4, f"got {result.steps_completed}")
    # Only Steps 3 and 4 should have been called (2 model calls, not 4)
    check("fewer model calls (skipped 1+2)", call_count["n"] <= 4, f"calls={call_count['n']}")

# ─── TEST 10: _parse_questions ────────────────────────────────────────────────
print("\n[10] _parse_questions()")

raw1 = "1. Is the rune name correct?\n2. Is the direction accurate?\n3. Does it match the Eddas?"
qs = CovePipeline._parse_questions(raw1)
check("parses 3 numbered questions", len(qs) == 3, f"got {len(qs)}")
check("no leading numbers in parsed", not any(q[0].isdigit() for q in qs))

raw2 = "- Does this align with traditions?\n- Are the gods named correctly?"
qs2 = CovePipeline._parse_questions(raw2)
check("parses bullet questions", len(qs2) == 2, f"got {len(qs2)}")

qs3 = CovePipeline._parse_questions("")
check("empty input -> []", qs3 == [])

qs4 = CovePipeline._parse_questions("Short.")
check("too-short line filtered", len(qs4) == 0, f"got {qs4}")

# ─── TEST 11: TEMPLATE_QUESTIONS coverage ─────────────────────────────────────
print("\n[11] TEMPLATE_QUESTIONS coverage")

check("all 6 domains + default present", "default" in TEMPLATE_QUESTIONS)
for domain in ["norse_spirituality", "norse_mythology", "norse_culture", "coding", "character", "roleplay", "default"]:
    check(f"domain '{domain}' has 3 questions", len(TEMPLATE_QUESTIONS[domain]) == 3, f"got {len(TEMPLATE_QUESTIONS[domain])}")

# ─── TEST 12: CoveResult.to_dict() ────────────────────────────────────────────
print("\n[12] CoveResult.to_dict()")

dummy = CoveResult(
    draft="draft", verification_questions=["q1", "q2"],
    qa_pairs=[("q1", "a1")], final_response="final",
    used_cove=True, steps_completed=4, fallback_chain=[], checkpoint_id="abc",
)
d = dummy.to_dict()
check("to_dict has used_cove", "used_cove" in d)
check("to_dict has steps_completed", "steps_completed" in d)
check("to_dict has n_questions", d["n_questions"] == 2)
check("to_dict has n_qa_pairs", d["n_qa_pairs"] == 1)

# ─── TEST 13: CoveState / get_state() ─────────────────────────────────────────
print("\n[13] CoveState / get_state()")

with tempfile.TemporaryDirectory() as tmpdir:
    cove = CovePipeline(well, MockRouter(), MockVordur(), checkpoint_dir=Path(tmpdir))
    cove._total_runs = 5
    cove._steps_completed_history = [4, 4, 3, 2, 4]
    state = cove.get_state()
    check("returns CoveState", isinstance(state, CoveState))
    check("total_runs=5", state.total_runs == 5)
    check("avg_steps_completed correct", state.avg_steps_completed == 3.4, f"got {state.avg_steps_completed}")
    check("circuit_breaker_pipeline is string", isinstance(state.circuit_breaker_pipeline, str))
    check("to_dict works", isinstance(state.to_dict(), dict))

# ─── TEST 14: _should_use_cove() ──────────────────────────────────────────────
print("\n[14] _should_use_cove()")

with tempfile.TemporaryDirectory() as tmpdir:
    cove_m = CovePipeline(well, MockRouter(), MockVordur(), min_complexity="medium", checkpoint_dir=Path(tmpdir))
    check("medium min + low query -> False", not cove_m._should_use_cove("low"))
    check("medium min + medium query -> True", cove_m._should_use_cove("medium"))
    check("medium min + high query -> True", cove_m._should_use_cove("high"))

    cove_h = CovePipeline(well, MockRouter(), MockVordur(), min_complexity="high", checkpoint_dir=Path(tmpdir))
    check("high min + medium query -> False", not cove_h._should_use_cove("medium"))
    check("high min + high query -> True", cove_h._should_use_cove("high"))

    cove_l = CovePipeline(well, MockRouter(), MockVordur(), min_complexity="low", checkpoint_dir=Path(tmpdir))
    check("low min + low query -> True", cove_l._should_use_cove("low"))

# ─── Summary ──────────────────────────────────────────────────────────────────
total = PASS + FAIL
print(f"\n{'='*50}")
print(f"Results: {PASS}/{total} passed")
if FAIL == 0:
    print("COVE TEST PASSED")
else:
    print(f"COVE TEST FAILED ({FAIL} failures)")
    sys.exit(1)
