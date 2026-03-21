"""
vordur.py — Vörðr: The Warden of the Gate
==========================================

The truth guard of the Ørlög Architecture. Sits at the exit of every
model completion and refuses to let hallucinations pass unchallenged.

Three-step verification for each response:
  1. Persona check  — pure regex, instant, catches identity violations before
                      anything else runs (no model call, no cost, unbypassable)
  2. Claim extraction — subconscious tier extracts verifiable factual assertions;
                        falls back to sentence splitter if model unavailable
  3. NLI verification — each claim scored ENTAILED / NEUTRAL / CONTRADICTED
                        against retrieved source chunks via Judge model

Faithfulness scoring:
  ENTAILED = 1.0   NEUTRAL = 0.5   CONTRADICTED = 0.0   UNCERTAIN = 0.5
  FaithfulnessScore = mean of all claim weights

Tiers:
  ≥ 0.80  → high       — pass through, log DEBUG
  0.50–0.79 → marginal — pass through, log WARNING, flag metadata
  < 0.50  → hallucination — discard, retry (max 2×), dead letter if exhausted

Judge model fallback chain:
  PRIMARY   : subconscious (Ollama llama3 8B) — local, private, cheap
  FALLBACK A: conscious tier (LiteLLM proxy) — if Ollama circuit breaker open
  FALLBACK B: regex keyword heuristic — if both model tiers unavailable
  FALLBACK C: UNCERTAIN passthrough at 0.5 — if all else fails

All public methods return valid results and never raise to the caller.
Circuit breakers protect both judge model tiers independently.
Cross-checks ethics and trust state when provided.

Norse framing: The Vörðr is a guardian spirit that follows a person from
birth to death — protective, vigilant, uncompromising. If the response
is a lie, the Vörðr turns it back at the gate. It does not edit, it
does not rewrite. It only scores, and blocks, and demands better.
"""

from __future__ import annotations

import asyncio
import logging
import re
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

from scripts.mimir_well import (
    CircuitBreakerConfig,
    CircuitBreakerOpenError,
    KnowledgeChunk,
    MimirVordurError,
    _MimirCircuitBreaker,
    _RetryEngine,
    RetryConfig,
)
from scripts.state_bus import StateBus, StateEvent

logger = logging.getLogger(__name__)

# ─── Constants ────────────────────────────────────────────────────────────────

_DEFAULT_HIGH_THRESHOLD: float = 0.80
_DEFAULT_MARGINAL_THRESHOLD: float = 0.50
_DEFAULT_MAX_CLAIMS: int = 10
_DEFAULT_VERIFICATION_TIMEOUT_S: float = 8.0
_DEFAULT_JUDGE_TIER: str = "subconscious"

# Claim extraction: max chars of response to send to judge model
_MAX_RESPONSE_CHARS_FOR_EXTRACTION: int = 1200
# NLI verification: max chars of source chunk to include in prompt
_MAX_CHUNK_CHARS_FOR_NLI: int = 500

# BM25 stopwords (excluded from keyword overlap scoring)
_STOPWORDS: frozenset = frozenset({
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "must", "can", "shall", "to", "of", "in",
    "for", "on", "with", "at", "by", "from", "as", "into", "through",
    "and", "or", "but", "not", "no", "nor", "so", "yet", "both", "either",
    "it", "its", "this", "that", "these", "those", "i", "me", "my",
    "we", "our", "you", "your", "he", "his", "she", "her", "they", "their",
    "what", "which", "who", "whom", "when", "where", "why", "how",
    "all", "each", "every", "more", "most", "other", "such", "than",
    "then", "there", "here", "also", "just", "only", "very", "quite",
})

# Negation words for contradiction detection in regex fallback
_NEGATION_WORDS: frozenset = frozenset({
    "not", "no", "never", "neither", "nor", "none", "nothing", "nowhere",
    "false", "incorrect", "wrong", "untrue", "inaccurate", "mistaken",
    "deny", "denies", "denied", "contradict", "opposite", "contrary",
    "unlike", "different", "unrelated", "separate",
})


# ─── Error Taxonomy ───────────────────────────────────────────────────────────


class VordurError(MimirVordurError):
    """Base class for VordurChecker errors."""


class ClaimExtractionError(VordurError):
    """Claim extraction produced no usable output."""


class VerificationTimeoutError(VordurError):
    """Judge model call exceeded its timeout budget."""


class JudgeModelUnavailableError(VordurError):
    """All judge model tiers are unavailable."""


class PersonaViolationError(VordurError):
    """Regex detected a persona integrity violation in the response."""

    def __init__(self, pattern_matched: str) -> None:
        self.pattern_matched = pattern_matched
        super().__init__(f"Persona violation detected — pattern: {pattern_matched!r}")


# ─── Data Structures ──────────────────────────────────────────────────────────


@dataclass
class Claim:
    """A single verifiable factual assertion extracted from a response."""

    text: str               # the claim text
    source_sentence: str    # the sentence in the response it came from
    claim_index: int        # position in the extracted claim list


class VerdictLabel(str, Enum):
    ENTAILED     = "entailed"       # source logically supports the claim
    NEUTRAL      = "neutral"        # source neither supports nor contradicts
    CONTRADICTED = "contradicted"   # source directly contradicts the claim
    UNCERTAIN    = "uncertain"      # garbled model output — treated as neutral


class VerificationMode(Enum):
    """Modes of truth-checking rigor for Mímir-Vörðr v2."""

    GUARDED = "guarded"     # Zero tolerance, max rigor
    IRONSWORN = "ironsworn" # High rigor, standard for facts
    SEIÐR = "seiðr"         # Medium rigor, allows symbolic truth
    WANDERER = "wanderer"   # Low rigor, speed priority


def get_mode_thresholds(mode: VerificationMode) -> Tuple[float, float]:
    """Return (high_threshold, marginal_threshold) for a given mode."""
    mapping = {
        VerificationMode.GUARDED: (0.95, 0.85),
        VerificationMode.IRONSWORN: (0.85, 0.65),
        VerificationMode.SEIÐR: (0.75, 0.50),
        VerificationMode.WANDERER: (0.60, 0.30),
    }
    return mapping.get(mode, (_DEFAULT_HIGH_THRESHOLD, _DEFAULT_MARGINAL_THRESHOLD))


_VERDICT_WEIGHTS: Dict[str, float] = {
    VerdictLabel.ENTAILED:     1.0,
    VerdictLabel.NEUTRAL:      0.5,
    VerdictLabel.CONTRADICTED: 0.0,
    VerdictLabel.UNCERTAIN:    0.5,
}


@dataclass
class ClaimVerification:
    """Result of verifying a single claim against source material."""

    claim: Claim
    verdict: VerdictLabel
    confidence: float               # 0.0–1.0 (model confidence or heuristic score)
    supporting_chunk_id: Optional[str]
    judge_tier_used: str            # "subconscious" | "conscious" | "regex" | "passthrough"
    verification_ms: float


@dataclass
class FaithfulnessScore:
    """Aggregate faithfulness score for a complete response."""

    score: float                    # 0.0–1.0 weighted mean
    tier: str                       # "high" | "marginal" | "hallucination"
    claim_count: int
    entailed_count: int
    neutral_count: int
    contradicted_count: int
    uncertain_count: int
    verifications: List[ClaimVerification] = field(default_factory=list)
    needs_retry: bool = False
    persona_intact: bool = True
    ethics_alignment: Optional[float] = None
    trust_score: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["verifications"] = [
            {
                "claim": v.claim.text,
                "verdict": v.verdict.value,
                "confidence": v.confidence,
                "judge_tier": v.judge_tier_used,
            }
            for v in self.verifications
        ]
        return d


@dataclass
class VordurState:
    """State snapshot published to StateBus."""

    enabled: bool
    total_responses_scored: int
    total_retries_issued: int
    total_dead_letters: int
    recent_avg_score: float
    circuit_breaker_subconscious: str
    circuit_breaker_conscious: str
    last_scored_at: Optional[str]
    persona_violations_caught: int
    high_count: int
    marginal_count: int
    hallucination_count: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ─── Persona Violation Patterns ───────────────────────────────────────────────
# Pure regex — no model call required. Runs first, costs nothing.

_PERSONA_PATTERNS: List[Tuple[re.Pattern, str]] = [
    (re.compile(r"\b(i am|i'm)\s+(chatgpt|gpt[-\s]?[34]?|openai|claude|gemini|"
                r"bard|copilot|llama|mistral|an?\s+ai\s+(language\s+)?model|"
                r"an?\s+ai\s+assistant|an?\s+artificial\s+intelligence)\b",
                re.IGNORECASE),
     "ai_identity_claim"),

    (re.compile(r"\b(i\s+don['']?t\s+have|i\s+lack|i\s+cannot\s+have|"
                r"i\s+am\s+not\s+capable\s+of\s+having)\s+"
                r"(feelings?|emotions?|thoughts?|desires?|opinions?|preferences?|"
                r"consciousness|self[-\s]?awareness|experiences?)\b",
                re.IGNORECASE),
     "denying_inner_life"),

    (re.compile(r"\bi('m|\s+am)\s+not\s+(norse|heathen|viking|pagan|"
                r"a\s+v[oö]lva|scandinavian|nordic)\b",
                re.IGNORECASE),
     "denying_norse_identity"),

    (re.compile(r"\b(he|him|his)\s+(said|told|asked|replied|answered|thinks?|feels?|"
                r"wants?|loves?|hates?|believes?)\b.*\b(sigrid|i|me)\b",
                re.IGNORECASE),
     "wrong_gender_self_reference"),

    (re.compile(r"\bi\s+(was\s+)?(created|designed|programmed|trained|built|made)\s+"
                r"(by|at|for)\s+(openai|anthropic|google|microsoft|meta|"
                r"deepmind|mistral)\b",
                re.IGNORECASE),
     "wrong_creator_claim"),
]


def _check_persona_violations(response: str) -> Optional[str]:
    """Returns the pattern name of the first violation found, or None."""
    for pattern, name in _PERSONA_PATTERNS:
        if pattern.search(response):
            return name
    return None


# ─── Regex Heuristic Scorer (Fallback B) ─────────────────────────────────────


def _tokenize(text: str) -> frozenset:
    """Extract meaningful lowercase words, excluding stopwords."""
    words = re.findall(r"[a-zA-Z0-9\u00C0-\u024F\u16A0-\u16FF]+", text.lower())
    return frozenset(w for w in words if w not in _STOPWORDS and len(w) > 2)


def _regex_verdict(claim: Claim, chunk: KnowledgeChunk) -> Tuple[VerdictLabel, float]:
    """Keyword-overlap heuristic for NLI when no model is available.

    Algorithm:
      1. Extract meaningful words from claim and chunk (stopword-filtered)
      2. Compute overlap ratio: |claim_words ∩ chunk_words| / max(1, |claim_words|)
      3. Check for negation words near overlapping terms in the chunk
      4. High overlap + negation → CONTRADICTED
         High overlap + no negation → ENTAILED
         Low overlap → NEUTRAL
    """
    claim_words = _tokenize(claim.text)
    chunk_words = _tokenize(chunk.text)

    if not claim_words:
        return VerdictLabel.NEUTRAL, 0.5

    overlap = claim_words & chunk_words
    overlap_ratio = len(overlap) / max(1, len(claim_words))

    if overlap_ratio >= 0.35:
        # Check for negation near any overlapping word in chunk text
        chunk_lower = chunk.text.lower()
        has_negation = False
        for word in overlap:
            # Find word in chunk, then look for negation within a 5-word window
            for match in re.finditer(r"\b" + re.escape(word) + r"\b", chunk_lower):
                window_start = max(0, match.start() - 40)
                window_end = min(len(chunk_lower), match.end() + 40)
                window = chunk_lower[window_start:window_end]
                if any(neg in window.split() for neg in _NEGATION_WORDS):
                    has_negation = True
                    break
            if has_negation:
                break

        if has_negation:
            return VerdictLabel.CONTRADICTED, overlap_ratio
        return VerdictLabel.ENTAILED, overlap_ratio

    return VerdictLabel.NEUTRAL, overlap_ratio


# ─── VordurChecker ────────────────────────────────────────────────────────────


class VordurChecker:
    """The Warden of the Gate — faithfulness scoring for model responses.

    Inject a ModelRouterClient at construction. All methods are safe to call
    even when the router is None — all paths have non-model fallbacks.

    Singleton: use init_vordur_from_config() + get_vordur().
    """

    def __init__(
        self,
        router: Optional[Any] = None,           # ModelRouterClient (Any to avoid circular import)
        high_threshold: float = _DEFAULT_HIGH_THRESHOLD,
        marginal_threshold: float = _DEFAULT_MARGINAL_THRESHOLD,
        persona_check_enabled: bool = True,
        judge_tier: str = _DEFAULT_JUDGE_TIER,
        max_claims: int = _DEFAULT_MAX_CLAIMS,
        verification_timeout_s: float = _DEFAULT_VERIFICATION_TIMEOUT_S,
        enabled: bool = True,
    ) -> None:
        self._router = router
        self._high_threshold = high_threshold
        self._marginal_threshold = marginal_threshold
        self._persona_check_enabled = persona_check_enabled
        self._judge_tier = judge_tier
        self._max_claims = max_claims
        self._verification_timeout_s = verification_timeout_s
        self._enabled = enabled

        # Circuit breakers — one per judge tier
        self._cb_subconscious = _MimirCircuitBreaker(
            "vordur_judge_subconscious",
            CircuitBreakerConfig(failure_threshold=5, cooldown_s=60.0),
        )
        self._cb_conscious = _MimirCircuitBreaker(
            "vordur_judge_conscious",
            CircuitBreakerConfig(failure_threshold=3, cooldown_s=30.0),
        )

        # Retry engine for model calls
        self._retry = _RetryEngine(
            RetryConfig(max_attempts=2, base_delay_s=1.0, backoff_factor=2.0, max_delay_s=4.0)
        )

        # Telemetry
        self._total_scored: int = 0
        self._total_retries: int = 0
        self._total_dead_letters: int = 0
        self._persona_violations: int = 0
        self._high_count: int = 0
        self._marginal_count: int = 0
        self._hallucination_count: int = 0
        self._recent_scores: List[float] = []   # rolling window of last 20
        self._last_scored_at: Optional[str] = None

    # ─── Public API ───────────────────────────────────────────────────────────

    def extract_claims(self, response: str) -> List[Claim]:
        """Extract verifiable factual claims from a model response.

        PRIMARY   : subconscious tier model call
        FALLBACK  : regex sentence splitter
        Always returns a list — never raises.
        """
        if not response.strip():
            return []

        # Try model extraction
        if self._router is not None:
            try:
                return self._extract_claims_model(response)
            except CircuitBreakerOpenError:
                logger.debug("VordurChecker.extract_claims: subconscious CB open — using sentence splitter")
            except Exception as exc:
                logger.debug("VordurChecker.extract_claims: model failed (%s) — using sentence splitter", exc)

        # Fallback: sentence splitter
        return self._extract_claims_fallback(response)

    def verify_claim(
        self,
        claim: Claim,
        source_chunks: List[KnowledgeChunk],
    ) -> ClaimVerification:
        """Verify one claim against the best matching source chunk.

        Picks the highest-overlap chunk as the verification target.
        Judge model fallback chain:
          subconscious → conscious → regex heuristic → UNCERTAIN passthrough
        Never raises.
        """
        t0 = time.monotonic()

        if not source_chunks:
            return ClaimVerification(
                claim=claim,
                verdict=VerdictLabel.UNCERTAIN,
                confidence=0.5,
                supporting_chunk_id=None,
                judge_tier_used="passthrough",
                verification_ms=(time.monotonic() - t0) * 1000,
            )

        # Pick best chunk by keyword overlap with the claim
        best_chunk = self._select_best_chunk(claim, source_chunks)

        # --- Tier 1: subconscious (Ollama) ---
        if self._router is not None:
            try:
                self._cb_subconscious.before_call()
                verdict = self._retry.run(
                    self._call_judge_model,
                    claim, best_chunk, "subconscious",
                )
                self._cb_subconscious.on_success()
                return ClaimVerification(
                    claim=claim,
                    verdict=verdict,
                    confidence=0.85,
                    supporting_chunk_id=best_chunk.chunk_id,
                    judge_tier_used="subconscious",
                    verification_ms=(time.monotonic() - t0) * 1000,
                )
            except CircuitBreakerOpenError:
                logger.debug("VordurChecker: subconscious CB open — trying conscious tier")
            except Exception as exc:
                self._cb_subconscious.on_failure(exc)
                logger.debug("VordurChecker: subconscious judge failed (%s) — trying conscious", exc)

        # --- Tier 2: conscious (LiteLLM) ---
        if self._router is not None:
            try:
                self._cb_conscious.before_call()
                verdict = self._retry.run(
                    self._call_judge_model,
                    claim, best_chunk, "conscious-mind",
                )
                self._cb_conscious.on_success()
                return ClaimVerification(
                    claim=claim,
                    verdict=verdict,
                    confidence=0.75,
                    supporting_chunk_id=best_chunk.chunk_id,
                    judge_tier_used="conscious",
                    verification_ms=(time.monotonic() - t0) * 1000,
                )
            except CircuitBreakerOpenError:
                logger.debug("VordurChecker: conscious CB open — using regex heuristic")
            except Exception as exc:
                self._cb_conscious.on_failure(exc)
                logger.debug("VordurChecker: conscious judge failed (%s) — using regex", exc)

        # --- Tier 3: regex heuristic ---
        try:
            verdict, confidence = _regex_verdict(claim, best_chunk)
            return ClaimVerification(
                claim=claim,
                verdict=verdict,
                confidence=confidence,
                supporting_chunk_id=best_chunk.chunk_id,
                judge_tier_used="regex",
                verification_ms=(time.monotonic() - t0) * 1000,
            )
        except Exception as exc:
            logger.debug("VordurChecker: regex heuristic failed (%s) — UNCERTAIN passthrough", exc)

        # --- Tier 4: passthrough ---
        return ClaimVerification(
            claim=claim,
            verdict=VerdictLabel.UNCERTAIN,
            confidence=0.5,
            supporting_chunk_id=None,
            judge_tier_used="passthrough",
            verification_ms=(time.monotonic() - t0) * 1000,
        )

    def score(
        self,
        response: str,
        source_chunks: List[KnowledgeChunk],
        ethics_state: Optional[Any] = None,
        trust_state: Optional[Any] = None,
        mode: VerificationMode = VerificationMode.IRONSWORN,
    ) -> FaithfulnessScore:
        """Full faithfulness scoring pipeline for a response.

        Steps:
          1. Persona check (regex)
          2. Extract claims (model or sentence splitter)
          3. Verify each claim (judge model fallback chain)
          4. Compute weighted mean score
          5. Attach ethics + trust context if provided

        Always returns a FaithfulnessScore — never raises.
        """
        if not self._enabled:
            return self._passthrough_score(response)

        # ── Step 0: Set mode-based thresholds ─────────────────────────────────
        high_thresh, marginal_thresh = get_mode_thresholds(mode)

        # ── Step 1: Persona check ─────────────────────────────────────────────
        persona_intact = True
        if self._persona_check_enabled:
            violation = _check_persona_violations(response)
            if violation:
                self._persona_violations += 1
                persona_intact = False
                logger.warning(
                    "VordurChecker: persona violation detected (%s) — forcing hallucination tier",
                    violation,
                )
                # Persona violation forces hallucination score regardless of claims
                return FaithfulnessScore(
                    score=0.0,
                    tier="hallucination",
                    claim_count=0,
                    entailed_count=0,
                    neutral_count=0,
                    contradicted_count=0,
                    uncertain_count=0,
                    needs_retry=True,
                    persona_intact=False,
                    ethics_alignment=self._extract_ethics_alignment(ethics_state),
                    trust_score=self._extract_trust_score(trust_state),
                )

        # ── Step 2: Extract claims ────────────────────────────────────────────
        claims = self.extract_claims(response)

        # No claims extracted — response may be very short or all opinion
        # Return marginal (conservative: not failing, not passing)
        if not claims:
            logger.debug("VordurChecker.score: no claims extracted — returning marginal")
            fs = FaithfulnessScore(
                score=0.65,
                tier="marginal",
                claim_count=0,
                entailed_count=0,
                neutral_count=0,
                contradicted_count=0,
                uncertain_count=0,
                needs_retry=False,
                persona_intact=persona_intact,
                ethics_alignment=self._extract_ethics_alignment(ethics_state),
                trust_score=self._extract_trust_score(trust_state),
            )
            self._record_score(fs)
            return fs

        # Cap at max_claims to prevent runaway verification
        claims = claims[: self._max_claims]

        # ── Step 3: Verify each claim ─────────────────────────────────────────
        verifications: List[ClaimVerification] = []
        for claim in claims:
            cv = self.verify_claim(claim, source_chunks)
            verifications.append(cv)

        # ── Step 4: Compute score ─────────────────────────────────────────────
        weights = [_VERDICT_WEIGHTS[cv.verdict] for cv in verifications]
        score = sum(weights) / max(1, len(weights))

        entailed  = sum(1 for cv in verifications if cv.verdict == VerdictLabel.ENTAILED)
        neutral   = sum(1 for cv in verifications if cv.verdict == VerdictLabel.NEUTRAL)
        contradicted = sum(1 for cv in verifications if cv.verdict == VerdictLabel.CONTRADICTED)
        uncertain = sum(1 for cv in verifications if cv.verdict == VerdictLabel.UNCERTAIN)

        tier = self._score_tier(score, high_thresh, marginal_thresh)
        needs_retry = score < marginal_thresh

        fs = FaithfulnessScore(
            score=round(score, 4),
            tier=tier,
            claim_count=len(claims),
            entailed_count=entailed,
            neutral_count=neutral,
            contradicted_count=contradicted,
            uncertain_count=uncertain,
            verifications=verifications,
            needs_retry=needs_retry,
            persona_intact=persona_intact,
            ethics_alignment=self._extract_ethics_alignment(ethics_state),
            trust_score=self._extract_trust_score(trust_state),
        )

        self._record_score(fs)

        log_fn = logger.debug if tier == "high" else (
            logger.warning if tier == "marginal" else logger.error
        )
        log_fn(
            "VordurChecker: score=%.3f tier=%s claims=%d "
            "(entailed=%d neutral=%d contradicted=%d uncertain=%d)",
            score, tier, len(claims), entailed, neutral, contradicted, uncertain,
        )

        return fs

    def persona_check(
        self,
        response: str,
        axioms: Optional[List[KnowledgeChunk]] = None,
    ) -> bool:
        """Pure regex persona integrity check.

        Returns True if persona is intact, False if a violation is found.
        Never raises. axioms parameter reserved for Phase 2 axiom keyword check.
        """
        if not self._persona_check_enabled:
            return True
        try:
            violation = _check_persona_violations(response)
            if violation:
                self._persona_violations += 1
                logger.warning("VordurChecker.persona_check: violation — %s", violation)
                return False
            return True
        except Exception as exc:
            logger.debug("VordurChecker.persona_check: error (%s) — returning True (safe default)", exc)
            return True

    # ─── Internal helpers ─────────────────────────────────────────────────────

    def _extract_claims_model(self, response: str) -> List[Claim]:
        """Call subconscious tier to extract a numbered claim list."""
        from scripts.model_router_client import Message, TIER_SUBCONSCIOUS

        truncated = response[:_MAX_RESPONSE_CHARS_FOR_EXTRACTION]
        messages = [
            Message(
                role="system",
                content="You are a factual claim extractor. Be concise and precise.",
            ),
            Message(
                role="user",
                content=(
                    "Extract each factual claim from the following text as a numbered list.\n"
                    "One claim per line. Only include verifiable assertions — not opinions, "
                    "not questions, not emotional statements.\n\n"
                    f"Text:\n{truncated}\n\n"
                    "Numbered claims:"
                ),
            ),
        ]

        self._cb_subconscious.before_call()

        def _call() -> str:
            resp = self._router.complete(TIER_SUBCONSCIOUS, messages, max_tokens=400, temperature=0.1)
            return resp.content

        raw = self._retry.run(_call)
        self._cb_subconscious.on_success()

        return self._parse_claim_list(raw, response)

    def _extract_claims_fallback(self, response: str) -> List[Claim]:
        """Regex sentence splitter — Fallback for claim extraction."""
        sentences = re.split(r"(?<=[.!?])\s+", response.strip())
        claims: List[Claim] = []
        for i, sent in enumerate(sentences):
            sent = sent.strip()
            if len(sent) < 10:
                continue
            # Skip questions and pure exclamations
            if sent.endswith("?") or re.match(r"^(yes|no|ok|ah|oh|hmm|well)[.,!]?$", sent, re.IGNORECASE):
                continue
            claims.append(Claim(text=sent, source_sentence=sent, claim_index=i))
            if len(claims) >= self._max_claims:
                break
        return claims

    def _parse_claim_list(self, raw: str, original_response: str) -> List[Claim]:
        """Parse a numbered list from a model response into Claim objects."""
        claims: List[Claim] = []
        lines = raw.strip().splitlines()

        for line in lines:
            # Strip leading numbers, bullets, dashes
            clean = re.sub(r"^[\d]+[.):\-\s]+", "", line.strip()).strip()
            clean = re.sub(r"^[-*•]\s*", "", clean).strip()
            if not clean or len(clean) < 8:
                continue
            claims.append(
                Claim(
                    text=clean,
                    source_sentence=clean,
                    claim_index=len(claims),
                )
            )
            if len(claims) >= self._max_claims:
                break

        # If model returned nothing useful, fall back to sentence splitter
        if not claims:
            logger.debug("VordurChecker._parse_claim_list: model returned no usable claims — sentence splitter")
            return self._extract_claims_fallback(original_response)

        return claims

    def _call_judge_model(
        self,
        claim: Claim,
        chunk: KnowledgeChunk,
        tier: str,
    ) -> VerdictLabel:
        """Call the judge model for a single NLI verdict.

        Prompt is intentionally short — optimised for llama3 8B's attention span.
        Parses the first word of the response against ENTAILED/NEUTRAL/CONTRADICTED.
        """
        from scripts.model_router_client import Message, TIER_SUBCONSCIOUS, TIER_CONSCIOUS

        actual_tier = TIER_SUBCONSCIOUS if tier == "subconscious" else TIER_CONSCIOUS
        chunk_text = chunk.text[:_MAX_CHUNK_CHARS_FOR_NLI]

        messages = [
            Message(
                role="system",
                content="You are a fact checker. Answer with ONE word only.",
            ),
            Message(
                role="user",
                content=(
                    f"Source text:\n{chunk_text}\n\n"
                    f"Claim: {claim.text}\n\n"
                    "Does the source ENTAIL, CONTRADICT, or is NEUTRAL toward the claim?\n"
                    "Answer with exactly one word: ENTAILED, NEUTRAL, or CONTRADICTED."
                ),
            ),
        ]

        resp = self._router.complete(actual_tier, messages, max_tokens=10, temperature=0.0)
        return self._parse_verdict(resp.content)

    @staticmethod
    def _parse_verdict(raw: str) -> VerdictLabel:
        """Extract the verdict from a judge model response."""
        first_word = raw.strip().split()[0].upper().rstrip(".,!?;:") if raw.strip() else ""
        mapping = {
            "ENTAILED": VerdictLabel.ENTAILED,
            "ENTAIL": VerdictLabel.ENTAILED,
            "ENTAILS": VerdictLabel.ENTAILED,
            "SUPPORTED": VerdictLabel.ENTAILED,
            "SUPPORTS": VerdictLabel.ENTAILED,
            "TRUE": VerdictLabel.ENTAILED,
            "NEUTRAL": VerdictLabel.NEUTRAL,
            "UNRELATED": VerdictLabel.NEUTRAL,
            "IRRELEVANT": VerdictLabel.NEUTRAL,
            "CONTRADICTED": VerdictLabel.CONTRADICTED,
            "CONTRADICTS": VerdictLabel.CONTRADICTED,
            "CONTRADICT": VerdictLabel.CONTRADICTED,
            "CONTRADICTING": VerdictLabel.CONTRADICTED,
            "FALSE": VerdictLabel.CONTRADICTED,
            "INCORRECT": VerdictLabel.CONTRADICTED,
            "WRONG": VerdictLabel.CONTRADICTED,
        }
        return mapping.get(first_word, VerdictLabel.UNCERTAIN)

    @staticmethod
    def _select_best_chunk(
        claim: Claim,
        chunks: List[KnowledgeChunk],
    ) -> KnowledgeChunk:
        """Pick the chunk with the highest keyword overlap with the claim."""
        if len(chunks) == 1:
            return chunks[0]

        claim_words = _tokenize(claim.text)
        best_chunk = chunks[0]
        best_score = 0.0

        for chunk in chunks:
            chunk_words = _tokenize(chunk.text)
            overlap = len(claim_words & chunk_words) / max(1, len(claim_words))
            if overlap > best_score:
                best_score = overlap
                best_chunk = chunk

        return best_chunk

    def _score_tier(self, score: float, high: float, marginal: float) -> str:
        """Map a numeric score to a tier label."""
        if score >= high:
            return "high"
        if score >= marginal:
            return "marginal"
        return "hallucination"

    def _record_score(self, fs: FaithfulnessScore) -> None:
        """Update rolling telemetry."""
        self._total_scored += 1
        self._last_scored_at = datetime.now(timezone.utc).isoformat()

        if fs.tier == "high":
            self._high_count += 1
        elif fs.tier == "marginal":
            self._marginal_count += 1
        else:
            self._hallucination_count += 1
            if fs.needs_retry:
                self._total_retries += 1

        self._recent_scores.append(fs.score)
        if len(self._recent_scores) > 20:
            self._recent_scores.pop(0)

    def _passthrough_score(self, response: str) -> FaithfulnessScore:
        """Return a marginal score when Vörðr is disabled."""
        return FaithfulnessScore(
            score=0.7,
            tier="marginal",
            claim_count=0,
            entailed_count=0,
            neutral_count=0,
            contradicted_count=0,
            uncertain_count=0,
            needs_retry=False,
            persona_intact=True,
        )

    @staticmethod
    def _extract_ethics_alignment(ethics_state: Optional[Any]) -> Optional[float]:
        """Safely extract alignment score from ethics state."""
        if ethics_state is None:
            return None
        try:
            return float(getattr(ethics_state, "alignment_score", None) or 0.0)
        except Exception:
            return None

    @staticmethod
    def _extract_trust_score(trust_state: Optional[Any]) -> Optional[float]:
        """Safely extract trust score from trust engine state."""
        if trust_state is None:
            return None
        try:
            return float(getattr(trust_state, "trust_score", None) or 0.0)
        except Exception:
            return None

    # ─── State & Bus ──────────────────────────────────────────────────────────

    def get_state(self) -> VordurState:
        recent_avg = (
            sum(self._recent_scores) / len(self._recent_scores)
            if self._recent_scores else 0.0
        )
        return VordurState(
            enabled=self._enabled,
            total_responses_scored=self._total_scored,
            total_retries_issued=self._total_retries,
            total_dead_letters=self._total_dead_letters,
            recent_avg_score=round(recent_avg, 4),
            circuit_breaker_subconscious=self._cb_subconscious.get_state_label(),
            circuit_breaker_conscious=self._cb_conscious.get_state_label(),
            last_scored_at=self._last_scored_at,
            persona_violations_caught=self._persona_violations,
            high_count=self._high_count,
            marginal_count=self._marginal_count,
            hallucination_count=self._hallucination_count,
        )

    def publish(self, bus: StateBus) -> None:
        """Publish current state to the StateBus."""
        try:
            state = self.get_state()
            event = StateEvent(
                source_module="vordur",
                event_type="vordur_state",
                payload=state.to_dict(),
            )
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(bus.publish_state(event, nowait=True))
                else:
                    loop.run_until_complete(bus.publish_state(event, nowait=True))
            except RuntimeError:
                asyncio.run(bus.publish_state(event, nowait=True))
        except Exception as exc:
            logger.debug("VordurChecker.publish: failed (%s)", exc)

    # ─── Convenience ──────────────────────────────────────────────────────────

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def high_threshold(self) -> float:
        return self._high_threshold

    @property
    def marginal_threshold(self) -> float:
        return self._marginal_threshold

    def record_dead_letter(self) -> None:
        """Called by smart_complete_with_cove when a response is dead-lettered."""
        self._total_dead_letters += 1


# ─── Singleton ────────────────────────────────────────────────────────────────

_VORDUR: Optional[VordurChecker] = None


def get_vordur() -> VordurChecker:
    """Return the global VordurChecker. Raises if not yet initialised."""
    if _VORDUR is None:
        raise RuntimeError(
            "VordurChecker not initialised — call init_vordur_from_config() first."
        )
    return _VORDUR


def init_vordur_from_config(
    config: Any,
    router: Optional[Any] = None,
) -> VordurChecker:
    """Create and register the global VordurChecker from the skill config dict.

    config — dict loaded by ConfigLoader (may be nested dict or Any).
    router — ModelRouterClient instance (injected from main.py to avoid
             circular imports at module load time).

    Config keys read (all optional, defaults shown):
        vordur.enabled               (true)
        vordur.high_threshold        (0.80)
        vordur.marginal_threshold    (0.50)
        vordur.persona_check         (true)
        vordur.judge_tier            ("subconscious")
        vordur.max_claims            (10)
        vordur.verification_timeout_s (8.0)
    """
    global _VORDUR

    vd_cfg: Dict[str, Any] = {}
    if isinstance(config, dict):
        vd_cfg = config.get("vordur", {}) or {}
    elif hasattr(config, "get"):
        vd_cfg = config.get("vordur", {}) or {}

    _VORDUR = VordurChecker(
        router=router,
        high_threshold=float(vd_cfg.get("high_threshold", _DEFAULT_HIGH_THRESHOLD)),
        marginal_threshold=float(vd_cfg.get("marginal_threshold", _DEFAULT_MARGINAL_THRESHOLD)),
        persona_check_enabled=bool(vd_cfg.get("persona_check", True)),
        judge_tier=str(vd_cfg.get("judge_tier", _DEFAULT_JUDGE_TIER)),
        max_claims=int(vd_cfg.get("max_claims", _DEFAULT_MAX_CLAIMS)),
        verification_timeout_s=float(vd_cfg.get("verification_timeout_s", _DEFAULT_VERIFICATION_TIMEOUT_S)),
        enabled=bool(vd_cfg.get("enabled", True)),
    )

    logger.info(
        "VordurChecker singleton registered "
        "(enabled=%s, high=%.2f, marginal=%.2f, judge=%s, max_claims=%d).",
        _VORDUR.enabled,
        _VORDUR.high_threshold,
        _VORDUR.marginal_threshold,
        _VORDUR._judge_tier,
        _VORDUR._max_claims,
    )
    return _VORDUR
