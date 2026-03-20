"""
trust_engine.py — Sigrid's Relationship Trust Ledger
=====================================================

Adapted from social_ledger.py. Tracks the living fabric of Sigrid's
relationships — the web of Gebo (ᚷ), the gift rune, where all bonds
are woven from reciprocity, kept oaths, warmth freely given, and
friction honestly faced.

Each contact (person Sigrid interacts with) has a TrustLedger: a set of
scores and a timestamped event log. Events are inferred from conversation
text or recorded explicitly. Scores shift slowly — trust is earned across
many turns, not granted in one exchange.

Primary contact is Volmarr (the partner). He begins with elevated initial
trust (configured). Guests and strangers begin at a neutral baseline.

Published to the state bus as a ``trust_tick`` event so prompt_synthesizer
can colour Sigrid's relational tone appropriately.

Norse framing: Gebo (ᚷ) — gift creates bond, bond creates obligation,
obligation freely honoured deepens both. Every interaction is a rune
inscribed on the web of wyrd between two souls.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from scripts.state_bus import StateBus, StateEvent

logger = logging.getLogger(__name__)


# ─── Constants ────────────────────────────────────────────────────────────────

_DEFAULT_PRIMARY_CONTACT: str = "volmarr"
_DEFAULT_PRIMARY_TRUST: float = 0.75     # pre-existing deep bond
_DEFAULT_STRANGER_TRUST: float = 0.30    # cautious openness to new contacts
_TRUST_CLAMP: Tuple[float, float] = (0.0, 1.0)
_FRICTION_DECAY_RATE: float = 0.05       # per decay call — grief fades, but slowly
_RECENT_EVENT_WINDOW: int = 8            # events included in TrustState summary
_MAX_EVENT_LOG: int = 200                # cap stored events per ledger


# ─── Event registry ───────────────────────────────────────────────────────────
# Each entry: event_type -> (trust_delta, intimacy_delta, reliability_delta, friction_delta)
# Small deltas — trust builds through many acts, not single gestures.

_EVENT_IMPACTS: Dict[str, Tuple[float, float, float, float]] = {
    # Positive warmth
    "warmth_shown":        (+0.02, +0.03, +0.00, -0.01),
    "humor_shared":        (+0.01, +0.02, +0.00,  0.00),
    "support_offered":     (+0.03, +0.04, +0.01, -0.02),
    "trust_affirmed":      (+0.04, +0.02, +0.02, -0.01),
    "boundary_respected":  (+0.03, +0.01, +0.03, -0.02),

    # Gift / reciprocity (Gebo)
    "gift_given":          (+0.02, +0.02, +0.00,  0.00),   # Sigrid gives
    "gift_received":       (+0.01, +0.01, +0.00,  0.00),   # Sigrid receives

    # Oath / promise
    "oath_kept":           (+0.05, +0.02, +0.05, -0.02),
    "oath_broken":         (-0.08, -0.03, -0.08, +0.06),

    # Repair
    "apology_given":       (+0.02, +0.01, +0.01, -0.04),

    # Conflict
    "conflict_mild":       (-0.01, -0.01, +0.00, +0.02),
    "conflict_harsh":      (-0.05, -0.03, -0.02, +0.08),

    # Violation
    "insult":              (-0.06, -0.04, -0.02, +0.07),
    "boundary_violated":   (-0.10, -0.05, -0.05, +0.10),
}

# Keyword triggers for text-inference: event_type -> list of trigger phrases
_EVENT_KEYWORDS: Dict[str, List[str]] = {
    "warmth_shown":       ["thank", "appreciate", "care", "love", "miss you", "glad you"],
    "humor_shared":       ["haha", "lol", "funny", "laugh", "joke", "hilarious", "heh"],
    "support_offered":    ["here for you", "support", "help you", "got you", "i'm with"],
    "trust_affirmed":     ["trust you", "i trust", "i believe you", "rely on you"],
    "boundary_respected": ["of course", "understood", "respect that", "i understand"],
    "gift_given":         ["gave you", "gift for you", "brought you", "made this for"],
    "gift_received":      ["thank you for", "you gave", "you brought", "you made"],
    "oath_kept":          ["kept my promise", "as promised", "i said i would", "honored"],
    "oath_broken":        ["broke my promise", "i lied", "i failed you", "betrayed"],
    "apology_given":      ["sorry", "apologize", "forgive me", "i was wrong", "my fault"],
    "conflict_mild":      ["disagree", "not sure about", "i don't think", "but actually"],
    "conflict_harsh":     ["furious", "angry at you", "that was wrong", "you hurt", "unacceptable"],
    "insult":             ["stupid", "idiot", "useless", "pathetic", "worthless"],
    "boundary_violated":  ["stop", "don't do that", "you crossed", "that's not okay", "no means no"],
}

# Relationship labels by trust score band
_RELATIONSHIP_LABELS: Tuple[Tuple[float, str], ...] = (
    (0.20, "hostile"),
    (0.40, "wary"),
    (0.60, "neutral"),
    (0.80, "trusted"),
    (1.01, "deep bond"),
)


# ─── TrustLedger ──────────────────────────────────────────────────────────────


@dataclass
class TrustLedger:
    """Per-contact relationship state — scores + timestamped event log.

    Scores are bounded: trust/intimacy/reliability in [0, 1],
    friction in [0, 1], gift_balance unbounded (positive = received more).
    """

    contact_id: str

    trust_score: float = _DEFAULT_STRANGER_TRUST
    intimacy_score: float = 0.0
    reliability_score: float = 0.5
    friction_score: float = 0.0
    gift_balance: float = 0.0           # positive: Sigrid has received more gifts
                                        # negative: Sigrid has given more

    events: List[Dict[str, Any]] = field(default_factory=list)
    first_seen: str = ""
    last_seen: str = ""

    def apply_event(self, event_type: str, magnitude: float = 1.0) -> None:
        """Update scores from a named event, scaled by magnitude (0.0–2.0)."""
        impacts = _EVENT_IMPACTS.get(event_type)
        if impacts is None:
            logger.debug("TrustLedger: unknown event type '%s' ignored.", event_type)
            return

        t_d, i_d, r_d, f_d = impacts
        scale = max(0.0, min(magnitude, 2.0))

        self.trust_score = _clamp(self.trust_score + t_d * scale)
        self.intimacy_score = _clamp(self.intimacy_score + i_d * scale)
        self.reliability_score = _clamp(self.reliability_score + r_d * scale)
        self.friction_score = _clamp(self.friction_score + f_d * scale)

        # Gebo balance tracking
        if event_type == "gift_given":
            self.gift_balance -= abs(t_d) * scale
        elif event_type == "gift_received":
            self.gift_balance += abs(t_d) * scale

    def record_event_entry(
        self,
        event_type: str,
        magnitude: float,
        note: str = "",
    ) -> None:
        """Append a timestamped event to the log, capping at _MAX_EVENT_LOG."""
        now = datetime.now(timezone.utc).isoformat()
        self.last_seen = now
        if not self.first_seen:
            self.first_seen = now
        entry: Dict[str, Any] = {
            "ts": now,
            "event": event_type,
            "magnitude": round(magnitude, 3),
        }
        if note:
            entry["note"] = note
        self.events.append(entry)
        if len(self.events) > _MAX_EVENT_LOG:
            self.events = self.events[-_MAX_EVENT_LOG:]

    def apply_friction_decay(self) -> None:
        """Let friction fade gently — Sigrid holds no permanent grudge."""
        self.friction_score = max(0.0, self.friction_score - _FRICTION_DECAY_RATE)

    def relationship_label(self) -> str:
        """Translate trust_score into a human-readable bond label."""
        for threshold, label in _RELATIONSHIP_LABELS:
            if self.trust_score < threshold:
                return label
        return "deep bond"

    def recent_event_types(self, n: int = _RECENT_EVENT_WINDOW) -> List[str]:
        """Return the n most recent event type names."""
        return [e["event"] for e in self.events[-n:]]


# ─── TrustState ───────────────────────────────────────────────────────────────


@dataclass(slots=True)
class TrustState:
    """Typed snapshot of the primary contact's trust ledger.

    Published to the state bus so prompt_synthesizer can tune
    Sigrid's relational warmth, caution, playfulness, or guardedness.
    """

    contact_id: str
    trust_score: float
    intimacy_score: float
    reliability_score: float
    friction_score: float
    gift_balance: float

    relationship_label: str         # hostile / wary / neutral / trusted / deep bond
    recent_events: List[str]        # last N event type names
    prompt_hint: str                # one-line relational context for prompt injection

    timestamp: str
    degraded: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-safe dict for state bus payload."""
        return {
            "contact_id": self.contact_id,
            "scores": {
                "trust": round(self.trust_score, 3),
                "intimacy": round(self.intimacy_score, 3),
                "reliability": round(self.reliability_score, 3),
                "friction": round(self.friction_score, 3),
                "gift_balance": round(self.gift_balance, 3),
            },
            "relationship_label": self.relationship_label,
            "recent_events": self.recent_events,
            "prompt_hint": self.prompt_hint,
            "timestamp": self.timestamp,
            "degraded": self.degraded,
        }


# ─── TrustEngine ──────────────────────────────────────────────────────────────


class TrustEngine:
    """Gebo's ledger — tracks the living fabric of Sigrid's relationships.

    Maintains one TrustLedger per contact_id. Events are inferred from
    conversation text or recorded explicitly. Scores shift gradually;
    friction decays across turns. The primary contact (Volmarr) begins
    with elevated trust reflecting their pre-existing bond.
    """

    def __init__(
        self,
        primary_contact_id: str = _DEFAULT_PRIMARY_CONTACT,
        primary_contact_initial_trust: float = _DEFAULT_PRIMARY_TRUST,
        stranger_initial_trust: float = _DEFAULT_STRANGER_TRUST,
    ) -> None:
        self._primary_contact_id = primary_contact_id
        self._primary_initial_trust = primary_contact_initial_trust
        self._stranger_initial_trust = stranger_initial_trust
        self._ledgers: Dict[str, TrustLedger] = {}

        # Pre-seed the primary contact ledger
        self._ensure_ledger(primary_contact_id)

    # ── Public API ────────────────────────────────────────────────────────────

    def process_turn(
        self,
        user_text: str,
        sigrid_text: str,
        contact_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Infer trust events from a conversation turn and update the ledger.

        Scans both user_text and sigrid_text for keyword triggers.
        Returns a summary dict of what was detected and applied.
        """
        cid = contact_id or self._primary_contact_id
        ledger = self._ensure_ledger(cid)
        combined = f"{user_text} {sigrid_text}".lower()
        inferred = self._infer_events(combined)
        for event_type in inferred:
            ledger.apply_event(event_type)
            ledger.record_event_entry(event_type, magnitude=1.0)

        return {
            "contact_id": cid,
            "inferred_events": inferred,
            "trust_score": round(ledger.trust_score, 3),
            "relationship_label": ledger.relationship_label(),
        }

    def record_event(
        self,
        event_type: str,
        magnitude: float = 1.0,
        note: str = "",
        contact_id: Optional[str] = None,
    ) -> None:
        """Manually record a specific trust event — bypasses text inference.

        Use this for explicit milestones (first meeting, major oath, etc.)
        that may not surface clearly from keyword scanning.
        """
        cid = contact_id or self._primary_contact_id
        ledger = self._ensure_ledger(cid)
        ledger.apply_event(event_type, magnitude=magnitude)
        ledger.record_event_entry(event_type, magnitude=magnitude, note=note)
        logger.debug(
            "TrustEngine: recorded '%s' for '%s' (magnitude=%.2f).",
            event_type, cid, magnitude,
        )

    def apply_friction_decay(self, contact_id: Optional[str] = None) -> None:
        """Decay friction score — call once per session tick or conversation end."""
        cid = contact_id or self._primary_contact_id
        ledger = self._ensure_ledger(cid)
        before = ledger.friction_score
        ledger.apply_friction_decay()
        if before > 0.0:
            logger.debug(
                "TrustEngine: friction decay for '%s': %.3f → %.3f.",
                cid, before, ledger.friction_score,
            )

    def get_ledger(self, contact_id: Optional[str] = None) -> TrustLedger:
        """Return the TrustLedger for a contact (creates if absent)."""
        return self._ensure_ledger(contact_id or self._primary_contact_id)

    def get_state(self, contact_id: Optional[str] = None) -> TrustState:
        """Build a TrustState snapshot for the given (or primary) contact."""
        cid = contact_id or self._primary_contact_id
        ledger = self._ensure_ledger(cid)
        label = ledger.relationship_label()
        recent = ledger.recent_event_types()
        hint = self._build_prompt_hint(ledger, label)
        return TrustState(
            contact_id=cid,
            trust_score=ledger.trust_score,
            intimacy_score=ledger.intimacy_score,
            reliability_score=ledger.reliability_score,
            friction_score=ledger.friction_score,
            gift_balance=ledger.gift_balance,
            relationship_label=label,
            recent_events=recent,
            prompt_hint=hint,
            timestamp=datetime.now(timezone.utc).isoformat(),
            degraded=False,
        )

    def publish(self, bus: StateBus, contact_id: Optional[str] = None) -> None:
        """Emit a ``trust_tick`` StateEvent to the state bus."""
        try:
            state = self.get_state(contact_id)
            event = StateEvent(
                source_module="trust_engine",
                event_type="trust_tick",
                payload=state.to_dict(),
            )
            bus.publish_state(event, nowait=True)
        except Exception as exc:
            logger.warning("TrustEngine.publish failed: %s", exc)

    # ── Internals ─────────────────────────────────────────────────────────────

    def _ensure_ledger(self, contact_id: str) -> TrustLedger:
        """Return existing ledger or create a fresh one with correct initial trust."""
        if contact_id not in self._ledgers:
            initial_trust = (
                self._primary_initial_trust
                if contact_id == self._primary_contact_id
                else self._stranger_initial_trust
            )
            ledger = TrustLedger(
                contact_id=contact_id,
                trust_score=initial_trust,
            )
            self._ledgers[contact_id] = ledger
            logger.debug(
                "TrustEngine: new ledger for '%s' (initial trust=%.2f).",
                contact_id, initial_trust,
            )
        return self._ledgers[contact_id]

    def _infer_events(self, lowered_text: str) -> List[str]:
        """Scan lowered combined text for keyword triggers.

        Returns a deduplicated list of inferred event types (order preserved).
        """
        inferred: List[str] = []
        for event_type, keywords in _EVENT_KEYWORDS.items():
            if any(kw in lowered_text for kw in keywords):
                inferred.append(event_type)
        return inferred

    def _build_prompt_hint(self, ledger: TrustLedger, label: str) -> str:
        """Compose a one-line relational context summary for prompt injection."""
        parts: List[str] = [f"bond={label}"]

        if ledger.friction_score >= 0.3:
            parts.append("friction present")
        elif ledger.intimacy_score >= 0.5:
            parts.append("deep intimacy")

        if ledger.reliability_score >= 0.8:
            parts.append("highly reliable")
        elif ledger.reliability_score < 0.3:
            parts.append("unreliable history")

        # Gebo balance awareness
        if ledger.gift_balance > 0.1:
            parts.append("Gebo: received more")
        elif ledger.gift_balance < -0.1:
            parts.append("Gebo: given more")

        recent = ledger.recent_event_types(3)
        if recent:
            parts.append(f"recent: {', '.join(recent)}")

        return f"[Trust/{ledger.contact_id}: {'; '.join(parts)}]"

    # ── Factory ───────────────────────────────────────────────────────────────

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "TrustEngine":
        """Construct from a config dict.

        Reads keys under ``trust_engine``:
          primary_contact_id            (str,   default "volmarr")
          primary_contact_initial_trust (float, default 0.75)
          stranger_initial_trust        (float, default 0.30)
        """
        cfg: Dict[str, Any] = config.get("trust_engine", {})
        return cls(
            primary_contact_id=str(
                cfg.get("primary_contact_id", _DEFAULT_PRIMARY_CONTACT)
            ),
            primary_contact_initial_trust=float(
                cfg.get("primary_contact_initial_trust", _DEFAULT_PRIMARY_TRUST)
            ),
            stranger_initial_trust=float(
                cfg.get("stranger_initial_trust", _DEFAULT_STRANGER_TRUST)
            ),
        )


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _clamp(value: float) -> float:
    """Clamp a score to [0.0, 1.0]."""
    lo, hi = _TRUST_CLAMP
    return max(lo, min(hi, value))


# ─── Singleton ────────────────────────────────────────────────────────────────

_TRUST_ENGINE: Optional[TrustEngine] = None


def init_trust_engine_from_config(config: Dict[str, Any]) -> TrustEngine:
    """Initialise the global TrustEngine from a config dict.

    Idempotent — returns the existing instance if already initialised.
    """
    global _TRUST_ENGINE
    if _TRUST_ENGINE is None:
        _TRUST_ENGINE = TrustEngine.from_config(config)
        primary = _TRUST_ENGINE._primary_contact_id
        initial = _TRUST_ENGINE._primary_initial_trust
        logger.info(
            "TrustEngine initialised (primary='%s', initial_trust=%.2f).",
            primary, initial,
        )
    return _TRUST_ENGINE


def get_trust_engine() -> TrustEngine:
    """Return the global TrustEngine.

    Raises RuntimeError if ``init_trust_engine_from_config()`` has not been called.
    """
    if _TRUST_ENGINE is None:
        raise RuntimeError(
            "TrustEngine not initialised — call init_trust_engine_from_config() first."
        )
    return _TRUST_ENGINE
