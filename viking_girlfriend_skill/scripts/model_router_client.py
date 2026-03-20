"""
model_router_client.py — Sigrid's Four-Mind Model Router
=========================================================

Routes inference requests across four tiers defined in
``infrastructure/litellm_config.yaml``.  Two detectors work together
to pick the right tier for every request:

  _CodingIntentDetector  — scores 0.0–1.0 for coding vs. conversational
  _ComplexityDetector    — classifies "low / medium / high" workload

Routing matrix (smart_complete):

  complexity=high   → deep-mind      (most capable, any task type)
  complexity=medium + coding  → code-mind     (coding specialist)
  complexity=medium + convo   → conscious-mind (general reasoning)
  complexity=low    → subconscious   (local, fast, free)

Tiers:

  conscious-mind     Primary cloud model (Gemini / OpenRouter).
                     Used for: medium-complexity general conversation.

  code-mind          Coding-specialized cloud model (Deepseek-Coder /
                     Codestral / Qwen2.5-Coder via OpenRouter).
                     Used for: medium-complexity code tasks.

  deep-mind          Secondary cloud model (OpenRouter / alternative).
                     Used for: any high-complexity request — deep reasoning,
                     long creative work, emotional depth, hard coding tasks.

  subconscious       Local Ollama model (llama3 or equivalent).
                     Used for: low-complexity tasks — quick questions,
                     greetings, memory ops, private processing. Zero cost.

Routing flows through LiteLLM proxy (localhost:4000) for the cloud tiers.
The subconscious tier talks to Ollama directly (localhost:11434).

``complete(tier, messages)`` routes to a specified tier.
``smart_complete(messages)`` runs both detectors and routes automatically.

Fallback chains:
  code-mind      → conscious-mind → deep-mind → subconscious
  conscious-mind → deep-mind      → subconscious
  deep-mind      → subconscious
  subconscious   → conscious-mind → deep-mind  (low fallback escalates up)

All retry logic uses jittered exponential backoff. Circuit-breakers protect
each LiteLLM tier independently.

Norse framing: Huginn (thought) and Muninn (memory) fly to four branches
of Yggdrasil. The conscious mind speaks in the hall; the code mind forges
in Nidavellir — where the dwarves craft perfect things from raw ore; the
deep mind whispers in the mead; the subconscious dreams in the roots.
The Norns weigh every request before choosing the right branch.
"""

from __future__ import annotations

import json
import logging
import random
import re
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional

from scripts.state_bus import StateBus, StateEvent

logger = logging.getLogger(__name__)

# ─── Tier names ───────────────────────────────────────────────────────────────

TIER_CONSCIOUS: str = "conscious-mind"
TIER_CODE: str = "code-mind"
TIER_DEEP: str = "deep-mind"
TIER_SUBCONSCIOUS: str = "subconscious"
ALL_TIERS = (TIER_CONSCIOUS, TIER_CODE, TIER_DEEP, TIER_SUBCONSCIOUS)

_DEFAULT_LITELLM_BASE: str = "http://localhost:4000"
_DEFAULT_OLLAMA_BASE: str = "http://localhost:11434"
_DEFAULT_OLLAMA_MODEL: str = "llama3"
_DEFAULT_MAX_TOKENS: int = 2048
_DEFAULT_TEMPERATURE: float = 0.8
_DEFAULT_TIMEOUT: int = 120
_DEFAULT_RETRIES: int = 3
_DEFAULT_CODING_THRESHOLD: float = 0.30
_DEFAULT_HIGH_WORD_THRESHOLD: int = 80    # words in last message → high complexity
_DEFAULT_LOW_WORD_THRESHOLD: int = 12     # words in last message → low complexity candidate
_CIRCUIT_FAILURE_THRESHOLD: int = 5
_CIRCUIT_COOLDOWN_S: int = 60

ComplexityLevel = Literal["low", "medium", "high"]


# ─── Core types ───────────────────────────────────────────────────────────────


@dataclass
class Message:
    """Chat message. role must be 'system', 'user', or 'assistant'."""
    role: str
    content: str


@dataclass
class CompletionResponse:
    """Response from any inference tier."""
    content: str
    model: str
    tier: str
    usage: Dict[str, int] = field(default_factory=dict)
    finish_reason: str = "stop"
    degraded: bool = False
    raw_response: Dict[str, Any] = field(default_factory=dict)

    @property
    def text(self) -> str:
        """Alias for content — convenience accessor."""
        return self.content


class ModelRouterError(Exception):
    """Raised when all tiers are exhausted or a hard error occurs."""
    pass


# ─── Coding intent detector ───────────────────────────────────────────────────


class _CodingIntentDetector:
    """Scores a user message for coding intent on a 0.0–1.0 scale.

    Signals and their weights:

      Code fences    (```) in any message        0.55   — very strong
      File extension (.py .js .ts .rs etc.)      0.30   — strong
      Language names (python, javascript, …)     0.20   — strong
      Error/debug    (error, traceback, bug, …)  0.30   — strong
      Code keywords  (def, class, import, …)     0.15   — moderate
      Action verbs   (implement, debug, fix, …)  0.15   — moderate
      Tech nouns     (function, api, query, …)   0.08   — light

    Scores from multiple signals accumulate and are clamped to 1.0.
    All matching is case-insensitive against the combined text of user turns.
    """

    _CODE_FENCE = re.compile(r"```")

    _FILE_EXTENSIONS = re.compile(
        r"\b\w+\.(py|js|ts|tsx|jsx|rs|go|java|cpp|cc|cxx|cs|rb|php|sh|bash|"
        r"sql|html|css|scss|yaml|yml|json|toml|lua|swift|kt|dart|r|m|f90)\b",
        re.IGNORECASE,
    )

    _LANGUAGE_NAMES = re.compile(
        r"\b(python|javascript|typescript|js|ts|rust|golang|golang\b|java|"
        r"c\+\+|c#|csharp|ruby|php|bash|shell|powershell|sql|html|css|"
        r"react|vue|angular|svelte|node|nodejs|django|flask|fastapi|"
        r"postgres|postgresql|mysql|sqlite|mongodb|redis)\b",
        re.IGNORECASE,
    )

    _ERROR_TERMS = re.compile(
        # Standalone error words AND camelCase exception types (TypeError, AttributeError, etc.)
        r"(\b\w*Error\b|\b\w*Exception\b|"
        r"\b(traceback|stacktrace|stack\s*trace|"
        r"bug|bugs|broken|crash|crashes|segfault|null\s*pointer|"
        r"undefined|not\s+defined|syntax\s+error|type\s+error|"
        r"attribute\s+error|import\s+error|module\s+not\s+found|"
        r"unexpected\s+token|cannot\s+read\s+property|"
        r"fails|failing|broken\s+code|not\s+working)\b)",
        re.IGNORECASE,
    )

    _CODE_CONSTRUCTS = re.compile(
        r"\b(def\s+\w|class\s+\w|function\s+\w|lambda|import\s+\w|"
        r"from\s+\w+\s+import|require\(|export\s+(default\s+)?|"
        r"const\s+\w|let\s+\w|var\s+\w|async\s+def|async\s+function|"
        r"async/await|await\s+\w|return\s+\w|try:|except\s+\w|catch\s*\(|finally:|"
        r"#include|namespace\s+\w|struct\s+\w|fn\s+\w|pub\s+fn|"
        r"impl\s+\w|use\s+\w+::|mod\s+\w)\b",
        re.IGNORECASE,
    )

    _ACTION_VERBS = re.compile(
        r"\b(implement|implementing|implementation|"
        r"debug|debugging|debugs|"
        r"refactor|refactoring|"
        r"optimize|optimise|optimizing|"
        r"write\s+(me\s+a?|a|the|some|this|code|function|class|script)|"
        r"create\s+(a\s+)?(function|class|script|module|api|endpoint|route)|"
        r"build\s+(a\s+)?(function|class|script|tool|module|api)|"
        r"fix\s+(this|the|my|a|the\s+bug|code|error|issue|problem)|"
        r"code\s+(this|it|the|for)|"
        r"generate\s+(code|a\s+function|a\s+class|a\s+script)|"
        r"add\s+(a\s+)?(function|method|feature|class|test)|"
        r"test\s+(this|the|my|a)|"
        r"unit\s+test|integration\s+test)\b",
        re.IGNORECASE,
    )

    _TECH_NOUNS = re.compile(
        r"\b(function|method|class|module|package|library|framework|"
        r"api|endpoint|route|controller|service|repository|"
        r"database|query|schema|migration|index|table|"
        r"algorithm|data\s*structure|loop|iterator|generator|"
        r"variable|array|list|dict|dictionary|object|struct|"
        r"decorator|middleware|plugin|hook|callback|"
        r"dockerfile|container|pipeline|ci\/cd|deploy|"
        r"regex|pattern|parse|serialize|deserialize)\b",
        re.IGNORECASE,
    )

    def score(self, messages: List[Message]) -> float:
        """Return a 0.0–1.0 coding intent score for the given messages."""
        # Consider all user turns for context; weight the last one more heavily
        user_texts = [m.content for m in messages if m.role == "user"]
        if not user_texts:
            return 0.0

        last_text = user_texts[-1]
        full_context = " ".join(user_texts)

        score = 0.0

        # Code fences — check full context (user may paste code across turns)
        if self._CODE_FENCE.search(full_context):
            score += 0.55

        # File extension in the last user message — strong coding signal
        if self._FILE_EXTENSIONS.search(last_text):
            score += 0.30

        # Language names — check last text primarily, context for extra boost
        lang_in_last = bool(self._LANGUAGE_NAMES.search(last_text))
        lang_in_ctx = bool(self._LANGUAGE_NAMES.search(full_context))
        if lang_in_last:
            score += 0.20
        elif lang_in_ctx:
            score += 0.08

        # Error/debug terms in last text
        if self._ERROR_TERMS.search(last_text):
            score += 0.30

        # Code constructs in last text (def, class, import, etc.)
        if self._CODE_CONSTRUCTS.search(last_text):
            score += 0.15

        # Action verbs in last text
        if self._ACTION_VERBS.search(last_text):
            score += 0.15

        # Tech nouns in last text
        noun_matches = len(self._TECH_NOUNS.findall(last_text))
        if noun_matches >= 2:
            score += 0.08
        elif noun_matches == 1:
            score += 0.04

        clamped = min(score, 1.0)
        logger.debug(
            "_CodingIntentDetector: raw=%.2f clamped=%.2f last=%r",
            score, clamped, last_text[:60],
        )
        return clamped

    def is_coding(self, messages: List[Message], threshold: float) -> bool:
        return self.score(messages) >= threshold


# ─── Complexity detector ──────────────────────────────────────────────────────


class _ComplexityDetector:
    """Classifies a request as 'low', 'medium', or 'high' complexity.

    High complexity signals (any one → high):
      • Word count of last user message ≥ high_word_threshold (default 80)
      • Multiple distinct questions (≥ 2 question marks in last message)
      • Depth/analysis keywords: elaborate, analyze, architecture, compare, …
      • Emotional depth keywords: crisis, suicidal, trauma, overwhelmed, …
      • Complex code scope: refactor entire, design system, from scratch, …

    Low complexity signals (all must be true → low):
      • Word count of last user message ≤ low_word_threshold (default 12)
      • No high-complexity signals
      • Matches greeting / simple acknowledgment / single-lookup patterns

    Everything else → medium.
    """

    _DEPTH_KEYWORDS = re.compile(
        r"\b(elaborate|in\s+detail|comprehensive|thoroughly|thorough|"
        r"deep\s+dive|deep\s+analysis|in-depth|analyze|analyse|analysis|"
        r"compare\s+and\s+contrast|pros\s+and\s+cons|trade.?offs?|"
        r"architecture|system\s+design|design\s+pattern|best\s+practice|"
        r"from\s+scratch|entire\s+(codebase|project|system|module)|"
        r"refactor\s+(the\s+)?(entire|whole|full|all)|"
        r"step.by.step|walk\s+me\s+through|explain\s+(in\s+full|completely|"
        r"everything|how\s+it\s+works|the\s+whole)|"
        r"philosophical|theology|metaphysics|epistemology|"
        r"compare\s+\w+\s+(to|with|vs\.?|versus)|"
        r"strategic|long.?term|roadmap|plan\s+out)\b",
        re.IGNORECASE,
    )

    _EMOTIONAL_DEPTH = re.compile(
        r"\b(crisis|suicidal|suicide|self.?harm|trauma|traumatic|"
        r"breakdown|falling\s+apart|overwhelmed|desperate|hopeless|"
        r"grief|grieving|abuse|abused|panic\s+attack|dissociat|"
        r"deeply\s+spiritual|sacred\s+rite|ritual\s+for|"
        r"life\s+changing|meaning\s+of\s+(life|existence)|"
        r"existential|want\s+to\s+die|can.?t\s+(go\s+on|cope|do\s+this))\b",
        re.IGNORECASE,
    )

    # Greeting/ack tokens — searched (not full-string matched) for very short texts (≤ 5 words)
    _GREETING_TOKENS = re.compile(
        r"\b(hi+|hey|hello|heil|hail|howdy|sup|yo+|greetings|salutations|"
        r"ok+|okay|got\s+it|thanks?|thank\s+you|cheers|"
        r"yes|no|sure|definitely|absolutely|sounds\s+good|"
        r"makes\s+sense|understood|cool|nice|great|perfect|"
        r"haha|lol|lmao|agreed|fair\s+enough|fair\s+point|"
        r"good\s+(morning|evening|night|day))\b",
        re.IGNORECASE,
    )

    # Single-fact lookups only — "tell me about" is NOT a simple lookup
    _SIMPLE_LOOKUP = re.compile(
        r"^\s*(what\s+is\b|what.?s\b|who\s+is\b|who.?s\b|"
        r"where\s+is\b|when\s+is\b|"
        r"define\b|meaning\s+of\b|"
        r"what\s+does\s+\w+\s+mean|how\s+do\s+you\s+spell)\b",
        re.IGNORECASE,
    )

    def __init__(
        self,
        high_word_threshold: int = _DEFAULT_HIGH_WORD_THRESHOLD,
        low_word_threshold: int = _DEFAULT_LOW_WORD_THRESHOLD,
    ) -> None:
        self._high_words = high_word_threshold
        self._low_words = low_word_threshold

    def classify(self, messages: List[Message]) -> ComplexityLevel:
        """Return 'low', 'medium', or 'high' for the given message list."""
        user_texts = [m.content for m in messages if m.role == "user"]
        if not user_texts:
            return "medium"

        last_text = user_texts[-1]
        word_count = len(last_text.split())
        question_count = last_text.count("?")

        # ── High signals ──────────────────────────────────────────────────────
        if word_count >= self._high_words:
            logger.debug("_ComplexityDetector: high (word_count=%d)", word_count)
            return "high"
        if question_count >= 2:
            logger.debug("_ComplexityDetector: high (multi-question count=%d)", question_count)
            return "high"
        if self._DEPTH_KEYWORDS.search(last_text):
            logger.debug("_ComplexityDetector: high (depth keyword)")
            return "high"
        if self._EMOTIONAL_DEPTH.search(last_text):
            logger.debug("_ComplexityDetector: high (emotional depth keyword)")
            return "high"

        # ── Low signals ───────────────────────────────────────────────────────
        # Very short texts (≤5 words): any greeting / ack token → low
        if word_count <= 5:
            if self._GREETING_TOKENS.search(last_text):
                logger.debug("_ComplexityDetector: low (greeting token, %d words)", word_count)
                return "low"
        # Short texts (≤ low_words threshold): single-fact lookups only → low
        if word_count <= self._low_words:
            if self._SIMPLE_LOOKUP.match(last_text.strip()):
                logger.debug("_ComplexityDetector: low (simple lookup, %d words)", word_count)
                return "low"

        logger.debug("_ComplexityDetector: medium (word_count=%d)", word_count)
        return "medium"


# ─── Routing logic ────────────────────────────────────────────────────────────


def _select_tier(complexity: ComplexityLevel, is_coding: bool) -> str:
    """Pure function — maps (complexity, is_coding) to a tier name.

    Matrix:
      high   + any    → deep-mind      (full capacity, no compromise)
      medium + coding → code-mind      (coding specialist)
      medium + convo  → conscious-mind (general reasoning)
      low    + any    → subconscious   (local, free, fast)
    """
    if complexity == "high":
        return TIER_DEEP
    if complexity == "low":
        return TIER_SUBCONSCIOUS
    # medium
    return TIER_CODE if is_coding else TIER_CONSCIOUS


# ─── Retry helper ─────────────────────────────────────────────────────────────


def _with_retries(operation, attempts: int = 3) -> Any:
    """Jittered exponential backoff retry loop. Raises last exception."""
    last_error: Optional[Exception] = None
    for attempt in range(1, max(1, attempts) + 1):
        try:
            return operation()
        except Exception as exc:
            last_error = exc
            if attempt >= attempts:
                break
            delay = min(1.5 * attempt, 6.0) + random.uniform(0, 0.4)
            logger.debug("Retry %d/%d after %.1fs: %s", attempt, attempts, delay, exc)
            time.sleep(delay)
    if last_error:
        raise last_error
    raise ModelRouterError("Retry loop exhausted with no error captured")


# ─── Safe JSON parsing ────────────────────────────────────────────────────────


def _safe_json(response: Any) -> Dict[str, Any]:
    try:
        data = response.json()
        return data if isinstance(data, dict) else {"_raw": data}
    except Exception:
        try:
            return {"_raw_text": response.text[:2000]}
        except Exception:
            return {}


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


# ─── Cloud tier client (LiteLLM proxy) ───────────────────────────────────────


class _LiteLLMTierClient:
    """Sends requests to LiteLLM proxy for a named tier model."""

    def __init__(
        self,
        tier: str,
        base_url: str,
        max_tokens: int,
        temperature: float,
        timeout: int,
        retries: int,
    ) -> None:
        self._tier = tier
        self._base_url = base_url.rstrip("/")
        self._max_tokens = max_tokens
        self._temperature = temperature
        self._timeout = timeout
        self._retries = retries
        self._failures: int = 0
        self._circuit_open_until: float = 0.0

    def complete(self, messages: List[Message], **kwargs: Any) -> CompletionResponse:
        """POST to LiteLLM /chat/completions with the tier model name."""
        import requests

        if self._circuit_open():
            raise ModelRouterError(f"{self._tier} circuit is temporarily open")

        msg_dicts = [{"role": str(m.role), "content": str(m.content)} for m in messages]
        payload: Dict[str, Any] = {
            "model": self._tier,
            "messages": msg_dicts,
            "max_tokens": int(kwargs.get("max_tokens", self._max_tokens)),
            "temperature": float(kwargs.get("temperature", self._temperature)),
            "stream": False,
        }

        def _request() -> Dict[str, Any]:
            resp = requests.post(
                f"{self._base_url}/chat/completions",
                json=payload,
                timeout=self._timeout,
            )
            resp.raise_for_status()
            return _safe_json(resp)

        try:
            data = _with_retries(_request, attempts=self._retries)
            choices = data.get("choices", [])
            if not choices:
                raise ModelRouterError(f"No choices in {self._tier} response")
            first = choices[0] if isinstance(choices[0], dict) else {}
            msg = first.get("message", {})
            content = str(msg.get("content", "")) if isinstance(msg, dict) else ""
            raw_usage = data.get("usage", {})
            usage = {
                "prompt_tokens": _safe_int(raw_usage.get("prompt_tokens", 0)),
                "completion_tokens": _safe_int(raw_usage.get("completion_tokens", 0)),
                "total_tokens": _safe_int(raw_usage.get("total_tokens", 0)),
            }
            self._failures = 0
            self._circuit_open_until = 0.0
            return CompletionResponse(
                content=content,
                model=data.get("model", self._tier),
                tier=self._tier,
                usage=usage,
                finish_reason=str(first.get("finish_reason", "stop")),
                raw_response=data,
            )

        except requests.exceptions.ConnectionError:
            self._record_failure()
            raise ModelRouterError(
                f"Cannot connect to LiteLLM at {self._base_url}. "
                f"Is the LiteLLM proxy running?"
            )
        except requests.exceptions.Timeout:
            self._record_failure()
            raise ModelRouterError(
                f"{self._tier} request timed out after {self._timeout}s."
            )
        except ModelRouterError:
            self._record_failure()
            raise
        except Exception as exc:
            self._record_failure()
            raise ModelRouterError(f"{self._tier} error: {exc}") from exc

    def check_health(self) -> bool:
        """Ping LiteLLM to verify reachability."""
        try:
            import requests
            resp = requests.get(f"{self._base_url}/health", timeout=5)
            return resp.status_code < 500
        except Exception:
            return False

    def _circuit_open(self) -> bool:
        return time.monotonic() < self._circuit_open_until

    def _record_failure(self) -> None:
        self._failures += 1
        if self._failures >= _CIRCUIT_FAILURE_THRESHOLD:
            cooldown = min(_CIRCUIT_COOLDOWN_S, 2 ** min(self._failures - _CIRCUIT_FAILURE_THRESHOLD, 5))
            self._circuit_open_until = time.monotonic() + cooldown
            logger.warning(
                "%s circuit opened for %ds after %d failures.",
                self._tier, cooldown, self._failures,
            )


# ─── Subconscious tier client (Ollama direct) ─────────────────────────────────


class _OllamaTierClient:
    """Talks directly to Ollama for subconscious-tier processing."""

    def __init__(
        self,
        base_url: str,
        model: str,
        max_tokens: int,
        temperature: float,
        timeout: int,
        retries: int,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._max_tokens = max_tokens
        self._temperature = temperature
        self._timeout = timeout
        self._retries = retries
        self._failures: int = 0

    def complete(self, messages: List[Message], **kwargs: Any) -> CompletionResponse:
        """POST to Ollama /api/chat."""
        import requests

        msg_dicts = [{"role": str(m.role), "content": str(m.content)} for m in messages]
        payload: Dict[str, Any] = {
            "model": self._model,
            "messages": msg_dicts,
            "stream": False,
            "options": {
                "temperature": float(kwargs.get("temperature", self._temperature)),
                "num_predict": int(kwargs.get("max_tokens", self._max_tokens)),
            },
        }

        def _request() -> Dict[str, Any]:
            resp = requests.post(
                f"{self._base_url}/api/chat",
                json=payload,
                timeout=self._timeout,
            )
            resp.raise_for_status()
            return _safe_json(resp)

        try:
            data = _with_retries(_request, attempts=self._retries)
            content = ""
            msg_data = data.get("message")
            if isinstance(msg_data, dict):
                content = str(msg_data.get("content", ""))
            if not content:
                content = str(data.get("response", ""))
            usage = {
                "prompt_tokens": _safe_int(data.get("prompt_eval_count", 0)),
                "completion_tokens": _safe_int(data.get("eval_count", 0)),
                "total_tokens": (
                    _safe_int(data.get("prompt_eval_count", 0))
                    + _safe_int(data.get("eval_count", 0))
                ),
            }
            self._failures = 0
            return CompletionResponse(
                content=content,
                model=self._model,
                tier=TIER_SUBCONSCIOUS,
                usage=usage,
                finish_reason="stop",
                raw_response=data,
            )

        except requests.exceptions.ConnectionError:
            self._failures += 1
            raise ModelRouterError(
                f"Cannot connect to Ollama at {self._base_url}. "
                f"Start Ollama before using the subconscious tier."
            )
        except requests.exceptions.Timeout:
            self._failures += 1
            raise ModelRouterError(f"Ollama timed out after {self._timeout}s.")
        except Exception as exc:
            self._failures += 1
            raise ModelRouterError(f"Ollama error: {exc}") from exc

    def check_health(self) -> bool:
        """Ping Ollama to verify reachability."""
        try:
            import requests
            resp = requests.get(f"{self._base_url}/api/tags", timeout=5)
            return resp.status_code < 500
        except Exception:
            return False


# ─── RouterState ──────────────────────────────────────────────────────────────


@dataclass(slots=True)
class RouterState:
    """Typed snapshot of model router health."""

    tier_health: Dict[str, bool]       # tier → reachable?
    last_tier_used: str
    total_completions: int
    total_fallbacks: int
    total_coding_completions: int      # completions routed to code-mind
    total_deep_completions: int        # completions routed to deep-mind (high complexity)
    total_low_completions: int         # completions routed to subconscious (low complexity)
    last_intent_score: float           # most recent coding intent score (0–1)
    last_complexity: str               # "low" | "medium" | "high"
    prompt_hint: str
    timestamp: str
    degraded: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tier_health": self.tier_health,
            "last_tier_used": self.last_tier_used,
            "total_completions": self.total_completions,
            "total_fallbacks": self.total_fallbacks,
            "total_coding_completions": self.total_coding_completions,
            "total_deep_completions": self.total_deep_completions,
            "total_low_completions": self.total_low_completions,
            "last_intent_score": round(self.last_intent_score, 3),
            "last_complexity": self.last_complexity,
            "prompt_hint": self.prompt_hint,
            "timestamp": self.timestamp,
            "degraded": self.degraded,
        }


# ─── ModelRouterClient ────────────────────────────────────────────────────────


class ModelRouterClient:
    """Four-mind model router with dual intent + complexity routing.

    Use ``complete(tier, messages)`` to route to a specific tier.
    Use ``smart_complete(messages)`` to run both detectors and route
    automatically to the right tier for the task.

    Routing matrix (smart_complete):
      high complexity  → deep-mind      (any task type)
      medium + coding  → code-mind
      medium + convo   → conscious-mind
      low complexity   → subconscious   (local, free, fast)

    Fallback chains:
      code-mind      → conscious-mind → deep-mind → subconscious
      conscious-mind → deep-mind      → subconscious
      deep-mind      → subconscious
      subconscious   → conscious-mind → deep-mind
    """

    def __init__(
        self,
        litellm_base_url: str = _DEFAULT_LITELLM_BASE,
        ollama_base_url: str = _DEFAULT_OLLAMA_BASE,
        ollama_model: str = _DEFAULT_OLLAMA_MODEL,
        max_tokens: int = _DEFAULT_MAX_TOKENS,
        temperature: float = _DEFAULT_TEMPERATURE,
        timeout: int = _DEFAULT_TIMEOUT,
        retries: int = _DEFAULT_RETRIES,
        coding_intent_threshold: float = _DEFAULT_CODING_THRESHOLD,
        high_word_threshold: int = _DEFAULT_HIGH_WORD_THRESHOLD,
        low_word_threshold: int = _DEFAULT_LOW_WORD_THRESHOLD,
    ) -> None:
        self._conscious = _LiteLLMTierClient(
            TIER_CONSCIOUS, litellm_base_url, max_tokens, temperature, timeout, retries,
        )
        self._code = _LiteLLMTierClient(
            TIER_CODE, litellm_base_url, max_tokens, temperature, timeout, retries,
        )
        self._deep = _LiteLLMTierClient(
            TIER_DEEP, litellm_base_url, max_tokens, temperature, timeout, retries,
        )
        self._subconscious = _OllamaTierClient(
            ollama_base_url, ollama_model, max_tokens, temperature, timeout, retries,
        )
        self._tier_clients: Dict[str, Any] = {
            TIER_CONSCIOUS:    self._conscious,
            TIER_CODE:         self._code,
            TIER_DEEP:         self._deep,
            TIER_SUBCONSCIOUS: self._subconscious,
        }
        self._intent_detector = _CodingIntentDetector()
        self._complexity_detector = _ComplexityDetector(
            high_word_threshold=high_word_threshold,
            low_word_threshold=low_word_threshold,
        )
        self._coding_intent_threshold = coding_intent_threshold

        self._last_tier: str = ""
        self._last_intent_score: float = 0.0
        self._last_complexity: ComplexityLevel = "medium"
        self._total_completions: int = 0
        self._total_fallbacks: int = 0
        self._total_coding_completions: int = 0
        self._total_deep_completions: int = 0
        self._total_low_completions: int = 0

    # ── Public API ────────────────────────────────────────────────────────────

    def smart_complete(
        self,
        messages: List[Message],
        fallback: bool = True,
        **kwargs: Any,
    ) -> CompletionResponse:
        """Run both detectors and route to the optimal tier.

        Step 1 — _ComplexityDetector classifies the request:
          high   → deep-mind  (no further discrimination needed)
          low    → subconscious
          medium → step 2

        Step 2 (medium only) — _CodingIntentDetector decides specialization:
          coding  → code-mind
          convo   → conscious-mind

        Falls back through the tier's degradation chain on failure.
        """
        complexity = self._complexity_detector.classify(messages)
        self._last_complexity = complexity

        intent_score = self._intent_detector.score(messages)
        self._last_intent_score = intent_score
        is_coding = intent_score >= self._coding_intent_threshold

        chosen_tier = _select_tier(complexity, is_coding)

        logger.info(
            "smart_complete: complexity=%s intent_score=%.2f is_coding=%s → tier=%s",
            complexity, intent_score, is_coding, chosen_tier,
        )
        return self.complete(messages, tier=chosen_tier, fallback=fallback, **kwargs)

    def complete(
        self,
        messages: List[Message],
        tier: str = TIER_CONSCIOUS,
        fallback: bool = True,
        **kwargs: Any,
    ) -> CompletionResponse:
        """Route a completion request to the specified tier.

        If ``fallback=True`` and the requested tier fails, attempts the
        degradation chain for that tier. Returns a degraded CompletionResponse
        if all tiers in the chain are exhausted.
        """
        if tier not in ALL_TIERS:
            logger.warning("ModelRouterClient: unknown tier '%s' — defaulting to conscious-mind.", tier)
            tier = TIER_CONSCIOUS

        tier_order = self._fallback_chain(tier) if fallback else [tier]

        for attempt_tier in tier_order:
            client = self._tier_clients[attempt_tier]
            try:
                response = client.complete(messages, **kwargs)
                self._last_tier = attempt_tier
                self._total_completions += 1
                if attempt_tier == TIER_CODE or tier == TIER_CODE:
                    self._total_coding_completions += 1
                if attempt_tier == TIER_DEEP or tier == TIER_DEEP:
                    self._total_deep_completions += 1
                if attempt_tier == TIER_SUBCONSCIOUS or tier == TIER_SUBCONSCIOUS:
                    self._total_low_completions += 1
                if attempt_tier != tier:
                    self._total_fallbacks += 1
                    logger.info(
                        "ModelRouterClient: fell back from %s to %s.",
                        tier, attempt_tier,
                    )
                return response
            except ModelRouterError as exc:
                logger.warning(
                    "ModelRouterClient: %s failed (%s)%s.",
                    attempt_tier, exc,
                    " — trying fallback" if fallback and attempt_tier != tier_order[-1] else "",
                )

        # All tiers exhausted
        logger.error("ModelRouterClient: all tiers exhausted for request.")
        self._total_fallbacks += 1
        return CompletionResponse(
            content="[Sigrid is momentarily unreachable — all inference tiers unavailable]",
            model="none",
            tier="none",
            degraded=True,
        )

    def detect_routing(
        self, messages: List[Message]
    ) -> Dict[str, Any]:
        """Return the full routing decision for diagnostics, without making a call.

        Returns a dict with keys:
          complexity   ("low" | "medium" | "high")
          intent_score (float 0–1)
          is_coding    (bool)
          chosen_tier  (str)
        """
        complexity = self._complexity_detector.classify(messages)
        score = self._intent_detector.score(messages)
        is_coding = score >= self._coding_intent_threshold
        return {
            "complexity": complexity,
            "intent_score": round(score, 3),
            "is_coding": is_coding,
            "chosen_tier": _select_tier(complexity, is_coding),
        }

    def detect_coding_intent(self, messages: List[Message]) -> tuple[float, bool]:
        """Return ``(score, is_coding)`` — kept for backward compatibility."""
        score = self._intent_detector.score(messages)
        return score, score >= self._coding_intent_threshold

    def health_check(self) -> Dict[str, bool]:
        """Check reachability of all tiers. Returns {tier: bool}."""
        return {tier: self._tier_clients[tier].check_health() for tier in ALL_TIERS}

    # ── State bus integration ─────────────────────────────────────────────────

    def get_state(self) -> RouterState:
        """Build a typed RouterState snapshot (no live health pings — uses cached failure state)."""
        tier_health = {
            TIER_CONSCIOUS:    self._conscious._failures < _CIRCUIT_FAILURE_THRESHOLD,
            TIER_CODE:         self._code._failures < _CIRCUIT_FAILURE_THRESHOLD,
            TIER_DEEP:         self._deep._failures < _CIRCUIT_FAILURE_THRESHOLD,
            TIER_SUBCONSCIOUS: self._subconscious._failures < 5,
        }
        any_degraded = not any(tier_health.values())
        is_coding = self._last_intent_score >= self._coding_intent_threshold
        intent_label = f"{'code' if is_coding else 'convo'}({self._last_intent_score:.2f})"
        prompt_hint = (
            f"[Router: last={self._last_tier or 'idle'}, "
            f"complexity={self._last_complexity}, intent={intent_label}, "
            f"completions={self._total_completions}, fallbacks={self._total_fallbacks}]"
        )
        return RouterState(
            tier_health=tier_health,
            last_tier_used=self._last_tier,
            total_completions=self._total_completions,
            total_fallbacks=self._total_fallbacks,
            total_coding_completions=self._total_coding_completions,
            total_deep_completions=self._total_deep_completions,
            total_low_completions=self._total_low_completions,
            last_intent_score=self._last_intent_score,
            last_complexity=self._last_complexity,
            prompt_hint=prompt_hint,
            timestamp=datetime.now(timezone.utc).isoformat(),
            degraded=any_degraded,
        )

    def publish(self, bus: StateBus) -> None:
        """Emit a ``router_tick`` StateEvent to the state bus."""
        try:
            state = self.get_state()
            event = StateEvent(
                source_module="model_router_client",
                event_type="router_tick",
                payload=state.to_dict(),
            )
            bus.publish_state(event, nowait=True)
        except Exception as exc:
            logger.warning("ModelRouterClient.publish failed: %s", exc)

    # ── Internals ─────────────────────────────────────────────────────────────

    def _fallback_chain(self, starting_tier: str) -> List[str]:
        """Return the degradation chain for a starting tier.

        code-mind      → conscious-mind → deep-mind → subconscious
        conscious-mind → deep-mind      → subconscious
        deep-mind      → subconscious
        subconscious   → conscious-mind → deep-mind   (escalate if local fails)
        """
        chains: Dict[str, List[str]] = {
            TIER_CODE:         [TIER_CODE, TIER_CONSCIOUS, TIER_DEEP, TIER_SUBCONSCIOUS],
            TIER_CONSCIOUS:    [TIER_CONSCIOUS, TIER_DEEP, TIER_SUBCONSCIOUS],
            TIER_DEEP:         [TIER_DEEP, TIER_SUBCONSCIOUS],
            TIER_SUBCONSCIOUS: [TIER_SUBCONSCIOUS, TIER_CONSCIOUS, TIER_DEEP],
        }
        return chains.get(starting_tier, [TIER_CONSCIOUS, TIER_DEEP, TIER_SUBCONSCIOUS])

    # ── Factory ───────────────────────────────────────────────────────────────

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "ModelRouterClient":
        """Construct from a config dict.

        Reads keys under ``model_router``::

          litellm_base_url          (str,   default "http://localhost:4000")
          ollama_base_url           (str,   default "http://localhost:11434")
          ollama_model              (str,   default "llama3")
          max_tokens                (int,   default 2048)
          temperature               (float, default 0.8)
          timeout                   (int,   default 120)
          retries                   (int,   default 3)
          coding_intent_threshold   (float, default 0.30)
          high_word_threshold       (int,   default 80)   — words → high complexity
          low_word_threshold        (int,   default 12)   — words → low complexity candidate
        """
        cfg: Dict[str, Any] = config.get("model_router", {})
        return cls(
            litellm_base_url=str(cfg.get("litellm_base_url", _DEFAULT_LITELLM_BASE)),
            ollama_base_url=str(cfg.get("ollama_base_url", _DEFAULT_OLLAMA_BASE)),
            ollama_model=str(cfg.get("ollama_model", _DEFAULT_OLLAMA_MODEL)),
            max_tokens=int(cfg.get("max_tokens", _DEFAULT_MAX_TOKENS)),
            temperature=float(cfg.get("temperature", _DEFAULT_TEMPERATURE)),
            timeout=int(cfg.get("timeout", _DEFAULT_TIMEOUT)),
            retries=int(cfg.get("retries", _DEFAULT_RETRIES)),
            coding_intent_threshold=float(
                cfg.get("coding_intent_threshold", _DEFAULT_CODING_THRESHOLD)
            ),
            high_word_threshold=int(cfg.get("high_word_threshold", _DEFAULT_HIGH_WORD_THRESHOLD)),
            low_word_threshold=int(cfg.get("low_word_threshold", _DEFAULT_LOW_WORD_THRESHOLD)),
        )


# ─── Singleton ────────────────────────────────────────────────────────────────

_MODEL_ROUTER: Optional[ModelRouterClient] = None


def init_model_router_from_config(config: Dict[str, Any]) -> ModelRouterClient:
    """Initialise the global ModelRouterClient. Idempotent."""
    global _MODEL_ROUTER
    if _MODEL_ROUTER is None:
        _MODEL_ROUTER = ModelRouterClient.from_config(config)
        logger.info(
            "ModelRouterClient initialised (coding_threshold=%.2f, "
            "high_words=%d, low_words=%d).",
            _MODEL_ROUTER._coding_intent_threshold,
            _MODEL_ROUTER._complexity_detector._high_words,
            _MODEL_ROUTER._complexity_detector._low_words,
        )
    return _MODEL_ROUTER


def get_model_router() -> ModelRouterClient:
    """Return the global ModelRouterClient.

    Raises RuntimeError if not yet initialised.
    """
    if _MODEL_ROUTER is None:
        raise RuntimeError(
            "ModelRouterClient not initialised — call init_model_router_from_config() first."
        )
    return _MODEL_ROUTER
