"""
test_smart_complete_with_cove.py -- Validation suite for Step 6
================================================================
Tests CompletionResponse new fields and ModelRouterClient.smart_complete_with_cove()
using fully mocked Huginn, CoVe, Vordur, DeadLetterStore.
No real model calls, no network, no ChromaDB required.

Validates:
  - CompletionResponse new optional fields and defaults
  - smart_complete_with_cove with all components None -> plain smart_complete
  - Full pipeline: huginn -> cove -> vordur -> high faithfulness result
  - CoVe fallback when CoVe raises -> direct complete used
  - Huginn fallback when Huginn raises -> no ground truth, skips CoVe
  - Vordur failure -> marginal pass-through (no crash)
  - Retry on hallucination: retry_count incremented, n_initial doubled
  - Retry exhaustion: canned response returned, dead letter written
  - outer try/except: catastrophic error -> plain smart_complete fallback
  - faithfulness_score, faithfulness_tier, cove_applied, ground_truth_chunks
    all attached correctly to CompletionResponse

Run from project root:
    python tests/test_smart_complete_with_cove.py
"""

import logging
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_ROOT = os.path.join(PROJECT_ROOT, "viking_girlfriend_skill")
sys.path.insert(0, SKILL_ROOT)

logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s", stream=sys.stdout)

print("\n=== smart_complete_with_cove Validation ===\n")
print("Importing model_router_client...", end=" ", flush=True)
from scripts.model_router_client import (
    ModelRouterClient,
    CompletionResponse,
    Message,
    TIER_CONSCIOUS,
    TIER_SUBCONSCIOUS,
    _CANNED_RESPONSE,
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


# ─── Mock helpers ─────────────────────────────────────────────────────────────

class MockKnowledgeChunk:
    def __init__(self, chunk_id="c1", text="Test chunk about Thurisaz rune."):
        self.chunk_id = chunk_id
        self.text = text
        self.source_file = "rune_work.md"
        self.domain = "norse_spirituality"
        self.level = 1
        self.metadata = {}

class MockRetrievalRequest:
    def __init__(self, query, n_initial=50, include_episodic=True, **kw):
        self.query = query
        self.n_initial = n_initial
        self.include_episodic = include_episodic

class MockRetrievalResult:
    def __init__(self, context_string="[GT-1] Test knowledge.", domain="norse_spirituality", chunks=None):
        self.context_string = context_string
        self.domain = domain
        self.knowledge_chunks = chunks if chunks is not None else [MockKnowledgeChunk()]
        self.episodic_context = ""
        self.retrieval_ms = 5.0
        self.fallback_used = "chromadb"
        self.domain_detection_confidence = 0.8

class MockHuginn:
    def __init__(self, context="[GT-1] Norse rune lore entry.", domain="norse_spirituality",
                 raise_on_call=False, n_initial_log=None):
        self._ctx = context
        self._domain = domain
        self._raise = raise_on_call
        self._n_initial_log = n_initial_log if n_initial_log is not None else []
        self.call_count = 0

    def retrieve(self, request):
        self.call_count += 1
        self._n_initial_log.append(getattr(request, "n_initial", None))
        if self._raise:
            raise RuntimeError("mock huginn error")
        return MockRetrievalResult(context_string=self._ctx, domain=self._domain)

class MockCoveResult:
    def __init__(self, final_response="Cove verified response.", used_cove=True,
                 steps_completed=4, fallback_chain=None):
        self.final_response = final_response
        self.used_cove = used_cove
        self.steps_completed = steps_completed
        self.fallback_chain = fallback_chain or []

class MockCove:
    def __init__(self, response="CoVe final response about runes.", raise_on_call=False):
        self._resp = response
        self._raise = raise_on_call
        self.call_count = 0
        self.last_complexity = None

    def run(self, query, context, retrieval, complexity, **kw):
        self.call_count += 1
        self.last_complexity = complexity
        if self._raise:
            raise RuntimeError("mock cove error")
        return MockCoveResult(final_response=self._resp)

class MockFaithfulnessScore:
    def __init__(self, score=0.9, tier="high", needs_retry=False):
        self.score = score
        self.tier = tier
        self.needs_retry = needs_retry
        self.claim_count = 3
        self.entailed_count = 3
        self.persona_intact = True

class MockVordur:
    def __init__(self, score=0.9, tier="high", needs_retry=False, raise_on_call=False):
        self._score = score
        self._tier = tier
        self._needs_retry = needs_retry
        self._raise = raise_on_call
        self.call_count = 0

    def score(self, response, source_chunks, **kw):
        self.call_count += 1
        if self._raise:
            raise RuntimeError("mock vordur error")
        return MockFaithfulnessScore(score=self._score, tier=self._tier, needs_retry=self._needs_retry)

class MockDeadLetterStore:
    def __init__(self):
        self.entries = []

    def append(self, entry):
        self.entries.append(entry)

class MockCompleteRouter(ModelRouterClient):
    """ModelRouterClient with complete() mocked to avoid real HTTP calls."""
    def __init__(self, response_text="Direct model response."):
        super().__init__()
        self._mock_text = response_text
        self._complete_call_count = 0

    def complete(self, messages, tier=TIER_CONSCIOUS, fallback=True, **kwargs):
        self._complete_call_count += 1
        return CompletionResponse(content=self._mock_text, model="mock", tier=tier)

    def smart_complete(self, messages, fallback=True, **kwargs):
        self._complete_call_count += 1
        return CompletionResponse(content=self._mock_text, model="mock", tier=TIER_CONSCIOUS)


def make_messages(user_text="Tell me about the Thurisaz rune."):
    return [Message(role="user", content=user_text)]


# ─── TEST 1: CompletionResponse new fields and defaults ──────────────────────
print("[1] CompletionResponse new optional fields")

resp = CompletionResponse(content="hello", model="llm", tier=TIER_CONSCIOUS)
check("faithfulness_score default=None", resp.faithfulness_score is None)
check("faithfulness_tier default=''", resp.faithfulness_tier == "")
check("cove_applied default=False", not resp.cove_applied)
check("cove_steps_completed default=0", resp.cove_steps_completed == 0)
check("retrieval_domain default=None", resp.retrieval_domain is None)
check("retry_count default=0", resp.retry_count == 0)
check("ground_truth_chunks default=0", resp.ground_truth_chunks == 0)
check("fallback_chain default=[]", resp.fallback_chain == [])
check("text property still works", resp.text == "hello")

# ─── TEST 2: _CANNED_RESPONSE defined ────────────────────────────────────────
print("\n[2] _CANNED_RESPONSE")
check("_CANNED_RESPONSE non-empty", len(_CANNED_RESPONSE) > 20)
check("_CANNED_RESPONSE mentions Well", "Well" in _CANNED_RESPONSE)

# ─── TEST 3: No components -> plain smart_complete ────────────────────────────
print("\n[3] All components None -> plain smart_complete")

router = MockCompleteRouter("baseline response")
msgs = make_messages("What is Thurisaz?")
result = router.smart_complete_with_cove(msgs)

check("returns CompletionResponse", isinstance(result, CompletionResponse))
check("content from plain smart_complete", result.content == "baseline response")
check("faithfulness_score=None (no vordur)", result.faithfulness_score is None)
check("cove_applied=False (no cove)", not result.cove_applied)
check("ground_truth_chunks=0 (no huginn)", result.ground_truth_chunks == 0)

# ─── TEST 4: Full pipeline -- high faithfulness ────────────────────────────────
print("\n[4] Full pipeline (huginn + cove + vordur) -> high faithfulness")

router = MockCompleteRouter()
huginn = MockHuginn(context="[GT-1] Thurisaz is the rune of force and change.")
cove = MockCove(response="Thurisaz is the third rune of the Elder Futhark.")
vordur = MockVordur(score=0.92, tier="high", needs_retry=False)
msgs = make_messages("Tell me about Thurisaz.")

result = router.smart_complete_with_cove(msgs, huginn=huginn, vordur=vordur, cove=cove)

check("returns CompletionResponse", isinstance(result, CompletionResponse))
check("content from CoVe", "Thurisaz" in result.content, f"content={result.content[:60]}")
check("faithfulness_score=0.92", result.faithfulness_score == 0.92, f"score={result.faithfulness_score}")
check("faithfulness_tier='high'", result.faithfulness_tier == "high", f"tier={result.faithfulness_tier}")
check("cove_applied=True", result.cove_applied)
check("cove_steps_completed=4", result.cove_steps_completed == 4)
check("retrieval_domain='norse_spirituality'", result.retrieval_domain == "norse_spirituality")
check("ground_truth_chunks=1", result.ground_truth_chunks == 1)
check("retry_count=0", result.retry_count == 0)
check("degraded=False", not result.degraded)
check("huginn.retrieve called once", huginn.call_count == 1)
check("cove.run called once", cove.call_count == 1)
check("vordur.score called once", vordur.call_count == 1)

# ─── TEST 5: CoVe failure -> direct complete fallback ─────────────────────────
print("\n[5] CoVe raises -> direct complete fallback")

router = MockCompleteRouter("Direct fallback response.")
huginn = MockHuginn()
cove = MockCove(raise_on_call=True)
vordur = MockVordur(score=0.85, tier="high")
msgs = make_messages()

result = router.smart_complete_with_cove(msgs, huginn=huginn, vordur=vordur, cove=cove)

check("returns CompletionResponse", isinstance(result, CompletionResponse))
check("content from direct complete", result.content == "Direct fallback response.")
check("cove_applied=False after CoVe failure", not result.cove_applied)
check("cove_steps_completed=0 after failure", result.cove_steps_completed == 0)

# ─── TEST 6: Huginn failure -> no ground truth, skip CoVe ────────────────────
print("\n[6] Huginn raises -> no GT, CoVe skipped, direct complete")

router = MockCompleteRouter("Huginn fallback response.")
huginn = MockHuginn(raise_on_call=True)
cove = MockCove()
vordur = MockVordur()
msgs = make_messages()

result = router.smart_complete_with_cove(msgs, huginn=huginn, vordur=vordur, cove=cove)

check("returns CompletionResponse", isinstance(result, CompletionResponse))
check("content from direct complete (no huginn)", result.content == "Huginn fallback response.")
check("cove not called (no retrieval result)", cove.call_count == 0)
check("ground_truth_chunks=0", result.ground_truth_chunks == 0)

# ─── TEST 7: Vordur failure -> marginal pass-through ────────────────────────
print("\n[7] Vordur raises -> marginal pass, no crash")

router = MockCompleteRouter()
huginn = MockHuginn()
cove = MockCove()
vordur = MockVordur(raise_on_call=True)
msgs = make_messages()

result = router.smart_complete_with_cove(msgs, huginn=huginn, vordur=vordur, cove=cove)

check("returns CompletionResponse", isinstance(result, CompletionResponse))
check("faithfulness_score=0.5 (vordur failed)", result.faithfulness_score == 0.5,
      f"score={result.faithfulness_score}")
check("faithfulness_tier='marginal'", result.faithfulness_tier == "marginal")
check("no crash from vordur failure", True)

# ─── TEST 8: Hallucination -> retry once, then pass ──────────────────────────
print("\n[8] Hallucination (score<0.5) -> retry, second attempt passes")

router = MockCompleteRouter()
n_initial_log = []
huginn = MockHuginn(n_initial_log=n_initial_log)
cove = MockCove()

call_n = {"n": 0}
class RetryVordur:
    """Fails first call (needs_retry), passes second."""
    call_count = 0
    def score(self, response, source_chunks, **kw):
        RetryVordur.call_count += 1
        if RetryVordur.call_count == 1:
            return MockFaithfulnessScore(score=0.3, tier="hallucination", needs_retry=True)
        return MockFaithfulnessScore(score=0.85, tier="high", needs_retry=False)

msgs = make_messages("Who is Odin?")
result = router.smart_complete_with_cove(msgs, huginn=huginn, vordur=RetryVordur(), cove=cove,
                                          max_vordur_retries=2)

check("returns CompletionResponse", isinstance(result, CompletionResponse))
check("retry_count=1", result.retry_count == 1, f"retry_count={result.retry_count}")
check("final score=0.85 after retry", result.faithfulness_score == 0.85,
      f"score={result.faithfulness_score}")
check("huginn called twice", huginn.call_count == 2, f"count={huginn.call_count}")
check("n_initial doubled on retry", n_initial_log[1] == n_initial_log[0] * 2,
      f"n_initial_log={n_initial_log}")
check("not degraded after retry pass", not result.degraded)

# ─── TEST 9: Retry exhaustion -> canned response + dead letter ───────────────
print("\n[9] Retry exhaustion -> canned response + dead letter written")

router = MockCompleteRouter()
huginn = MockHuginn()
cove = MockCove()
always_retry_vordur = MockVordur(score=0.2, tier="hallucination", needs_retry=True)
dead_letters = MockDeadLetterStore()
msgs = make_messages()

result = router.smart_complete_with_cove(
    msgs, huginn=huginn, vordur=always_retry_vordur, cove=cove,
    dead_letter_store=dead_letters, max_vordur_retries=2,
)

check("returns CompletionResponse", isinstance(result, CompletionResponse))
check("content is canned response", result.content == _CANNED_RESPONSE,
      f"content[:60]={result.content[:60]}")
check("faithfulness_tier='hallucination'", result.faithfulness_tier == "hallucination")
check("degraded=True", result.degraded)
check("retry_count=max_retries", result.retry_count == 2, f"retry_count={result.retry_count}")
check("dead letter written", len(dead_letters.entries) >= 1,
      f"entries={len(dead_letters.entries)}")

# ─── TEST 10: Outer safety net -> plain smart_complete ───────────────────────
print("\n[10] Outer safety net -- catastrophic error -> plain smart_complete")

class ExplodingCompleteRouter(MockCompleteRouter):
    """Raises in the routing detection to simulate catastrophic failure."""
    def detect_routing(self, messages):
        raise RuntimeError("catastrophic internal error")
    # Override complexity_detector to raise
    @property
    def _complexity_detector(self):
        raise RuntimeError("everything is on fire")

# Use the standard router but inject a huginn that raises immediately,
# and a vordur that also raises, to force the outer except to trigger
# by breaking something in the chain that's before the inner try/except.
class BrokenRouter(ModelRouterClient):
    def __init__(self):
        super().__init__()
    def smart_complete(self, messages, fallback=True, **kw):
        return CompletionResponse(content="safe fallback", model="mock", tier=TIER_CONSCIOUS)
    def complete(self, messages, tier=TIER_CONSCIOUS, fallback=True, **kw):
        return CompletionResponse(content="safe fallback", model="mock", tier=tier)

router = BrokenRouter()

class AlwaysExplodingCove:
    def run(self, *a, **kw):
        raise SystemError("catastrophic unrecoverable error")

# This test exercises the case where CoVe raises SystemError (not caught by inner except)
# For a cleaner test, monkey-patch _complexity_detector.classify
original_classify = router._complexity_detector.classify

def bad_classify(messages):
    # First call raises; this escapes inner handler and hits outer except
    raise RuntimeError("injected routing failure")

router._complexity_detector.classify = bad_classify
result = router.smart_complete_with_cove(make_messages())
router._complexity_detector.classify = original_classify  # restore

check("result returned from outer safety net", isinstance(result, CompletionResponse))
check("content from plain smart_complete fallback", result.content == "safe fallback",
      f"content={result.content}")

# ─── TEST 11: Complexity passed to CoVe correctly ────────────────────────────
print("\n[11] Complexity classification passed to CoVe.run()")

router = MockCompleteRouter()
huginn = MockHuginn()
cove = MockCove()
vordur = MockVordur()
# Short greeting -> low complexity
msgs = [Message(role="user", content="hi")]
router.smart_complete_with_cove(msgs, huginn=huginn, vordur=vordur, cove=cove)
check("low complexity detected for greeting", cove.last_complexity == "low",
      f"complexity={cove.last_complexity}")

# Long elaborate message -> high complexity (depth keyword)
msgs2 = [Message(role="user", content="elaborate on the complete metaphysical cosmology of Norse paganism including all nine worlds and their inhabitants and relationships")]
cove2 = MockCove()
router.smart_complete_with_cove(msgs2, huginn=huginn, vordur=vordur, cove=cove2)
check("high complexity detected for elaborate query", cove2.last_complexity == "high",
      f"complexity={cove2.last_complexity}")

# ─── TEST 12: marginal score -> pass through (no retry) ──────────────────────
print("\n[12] Marginal score (0.5-0.79) -> pass through, not retried")

router = MockCompleteRouter()
huginn = MockHuginn()
cove = MockCove()
vordur = MockVordur(score=0.65, tier="marginal", needs_retry=False)
msgs = make_messages()

result = router.smart_complete_with_cove(msgs, huginn=huginn, vordur=vordur, cove=cove)

check("marginal score passes through", result.faithfulness_score == 0.65,
      f"score={result.faithfulness_score}")
check("faithfulness_tier='marginal'", result.faithfulness_tier == "marginal")
check("retry_count=0 (no retry on marginal)", result.retry_count == 0)
check("not degraded on marginal", not result.degraded)
check("huginn called only once", huginn.call_count == 1)

# ─── Summary ──────────────────────────────────────────────────────────────────
total = PASS + FAIL
print(f"\n{'='*50}")
print(f"Results: {PASS}/{total} passed")
if FAIL == 0:
    print("SMART_COMPLETE_WITH_COVE TEST PASSED")
else:
    print(f"SMART_COMPLETE_WITH_COVE TEST FAILED ({FAIL} failures)")
    sys.exit(1)
