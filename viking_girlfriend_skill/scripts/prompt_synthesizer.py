"""
prompt_synthesizer.py — Sigrid's Voice Weaver
==============================================

No adoption source — written fresh. This is the final assembly point before
Sigrid speaks. Every module has done its work: read the time, felt the body,
woven the dreams, checked the ethics, weighed the trust, recalled the memories.
Here those threads are gathered into a single coherent voice and shaped into the
messages list that model_router_client.complete() will carry.

Responsibilities
----------------
1. Load static identity text from ``data/core_identity.md`` and ``data/SOUL.md``
   once at startup — these form the immutable persona anchor.
2. Accept ``state_hints: Dict[str, str]`` from whichever modules have published
   their ``prompt_hint`` strings to the state bus.
3. Accept an optional ``memory_context: str`` from MemoryStore.get_context().
4. Assemble a system prompt with ordered, token-budgeted sections:
      [identity] → [soul anchor] → [time/location] → [emotional state]
      → [oracle/dream] → [memory] → [projects]
5. Return ``List[Dict[str, str]]`` (role/content dicts) — the full messages list
   ready for model_router_client.complete().  No import from model_router_client
   to avoid circular deps; callers convert if needed.
6. Publish ``synthesizer_tick`` StateEvent to the state bus.

Token budget policy
-------------------
* Identity block  — up to ``identity_chars`` (default 2000)
* Soul anchor     — up to ``soul_chars``     (default 400)
* Each hint line  — one line; if hint > 200 chars it is truncated
* Memory context  — up to ``memory_chars``   (default 800)
* Hard total cap  — ``max_system_chars``      (default 6000)

Sections are concatenated in priority order; the combined string is hard-trimmed
to ``max_system_chars`` if anything overflows.

Norse framing: Bragi weaves the skald's voice. Every word spoken by Sigrid first
passed through this hall — here the strands are combed, ordered, and made ready
to carry meaning across the void.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from scripts.state_bus import StateBus, StateEvent
from scripts.vordur import VerificationMode

logger = logging.getLogger(__name__)

_DEFAULT_DATA_ROOT: str = "data"
_DEFAULT_IDENTITY_FILE: str = "core_identity.md"
_DEFAULT_SOUL_FILE: str = "SOUL.md"

_DEFAULT_IDENTITY_CHARS: int = 2000
_DEFAULT_SOUL_CHARS: int = 400
_DEFAULT_MEMORY_CHARS: int = 800
_DEFAULT_MAX_SYSTEM_CHARS: int = 6000
_DEFAULT_MAX_HINT_CHARS: int = 200

# Section ordering — lower index = higher priority / rendered first
_HINT_SECTION_ORDER: tuple = (
    "scheduler",
    "environment_mapper",
    "wyrd_matrix",
    "metabolism",
    "trust_engine",
    "bio_engine",
    "oracle",
    "dream_engine",
    "project_generator",
    "ethics",
)


# ─── SynthesizerState ─────────────────────────────────────────────────────────


@dataclass(slots=True)
class SynthesizerState:
    """Typed snapshot of the synthesizer's last build operation."""

    identity_loaded: bool
    soul_loaded: bool
    last_hint_keys: List[str]
    last_system_chars: int
    last_user_chars: int
    build_count: int
    prompt_hint: str
    timestamp: str
    degraded: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity_loaded": self.identity_loaded,
            "soul_loaded": self.soul_loaded,
            "last_hint_keys": self.last_hint_keys,
            "last_system_chars": self.last_system_chars,
            "last_user_chars": self.last_user_chars,
            "build_count": self.build_count,
            "prompt_hint": self.prompt_hint,
            "timestamp": self.timestamp,
            "degraded": self.degraded,
        }


# ─── PromptSynthesizer ────────────────────────────────────────────────────────


class PromptSynthesizer:
    """Assembles the final messages list that drives Sigrid's voice.

    Usage::

        synth = PromptSynthesizer.from_config(config)
        messages = synth.build_messages(
            user_text="Hello Sigrid, how are you?",
            state_hints={
                "scheduler":         "[Time: evening — reflective and warm]",
                "environment_mapper":"[Environment: Living Room — cosy hearth]",
                "wyrd_matrix":       "[Mood: content 0.62]",
            },
            memory_context="Volmarr asked about the Eddas last Tuesday.",
        )
        # messages is List[Dict[str,str]] → pass to model_router_client.complete()
    """

    def __init__(
        self,
        data_root: str = _DEFAULT_DATA_ROOT,
        identity_file: str = _DEFAULT_IDENTITY_FILE,
        soul_file: str = _DEFAULT_SOUL_FILE,
        identity_chars: int = _DEFAULT_IDENTITY_CHARS,
        soul_chars: int = _DEFAULT_SOUL_CHARS,
        memory_chars: int = _DEFAULT_MEMORY_CHARS,
        max_system_chars: int = _DEFAULT_MAX_SYSTEM_CHARS,
        max_hint_chars: int = _DEFAULT_MAX_HINT_CHARS,
        include_sensory: bool = True,
    ) -> None:
        self._root = Path(data_root)
        self._identity_chars = identity_chars
        self._soul_chars = soul_chars
        self._memory_chars = memory_chars
        self._max_system_chars = max_system_chars
        self._max_hint_chars = max_hint_chars
        self._include_sensory: bool = include_sensory
        self._degraded: bool = False
        self._build_count: int = 0
        self._last_hint_keys: List[str] = []
        self._last_system_chars: int = 0
        self._last_user_chars: int = 0

        self._identity_text: str = self._load_text(identity_file, identity_chars)
        self._soul_text: str = self._load_text(soul_file, soul_chars)

    # ── Public API ────────────────────────────────────────────────────────────

    def build_messages(
        self,
        user_text: str,
        state_hints: Optional[Dict[str, str]] = None,
        memory_context: Optional[str] = None,
        sensory_hints: Optional[Dict[str, str]] = None,
    ) -> Tuple[List[Dict[str, str]], VerificationMode]:
        """Assemble a messages list and determine the appropriate verification mode.

        Parameters
        ----------
        user_text:      The human turn text.
        state_hints:    Dict mapping module name → prompt_hint string.
        memory_context: Optional episodic/semantic context from MemoryStore.
        sensory_hints:  E-21: Optional sensory channel dict from EnvironmentMapper.

        Returns
        -------
        Tuple of (List of role/content dicts, selected VerificationMode).
        """
        hints = state_hints or {}
        system_content = self._build_system(hints, memory_context or "", sensory_hints or {})
        
        # Determine verification mode based on context
        mode = self.select_verification_mode(user_text, hints)

        self._build_count += 1
        self._last_hint_keys = list(hints.keys())
        self._last_system_chars = len(system_content)
        self._last_user_chars = len(user_text)
        
        logger.debug(
            "PromptSynthesizer: built messages #%d (system=%d, mode=%s).",
            self._build_count,
            self._last_system_chars,
            mode.value,
        )
        
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_text},
        ]
        return messages, mode

    def select_verification_mode(
        self,
        user_text: str,
        hints: Dict[str, str],
    ) -> VerificationMode:
        """Heuristic to pick the truth-governance rigor mode for this turn."""
        ut = user_text.lower()
        
        # 1. GUARDED: Safety, Identity, or System overrides detected
        # If ethics or security flags a violation, or user asks "who are you"
        if "[TABOO]" in hints.get("ethics", "") or "who are you" in ut or "your nature" in ut:
            return VerificationMode.GUARDED
            
        # 2. IRONSWORN: Factual, historical, or technical inquiry
        # Triggered by domain keywords or 'scheduler' reporting a factual context
        factual_keywords = {"history", "fact", "true", "lore", "code", "programming", "edda", "runes"}
        if any(kw in ut for kw in factual_keywords) or "[Context: Technical]" in hints.get("ethics", ""):
            return VerificationMode.IRONSWORN
            
        # 3. SEIÐR: High-vibe, spiritual, or emotional intensity
        spiritual_keywords = {"spirit", "magic", "seidr", "gods", "ritual", "soul", "wyrd"}
        if any(kw in ut for kw in spiritual_keywords) or "[Mood: intense]" in hints.get("wyrd_matrix", ""):
            return VerificationMode.SEIÐR
            
        # 4. WANDERER: Default for casual chat
        return VerificationMode.WANDERER

    def get_state(self) -> SynthesizerState:
        """Return a typed SynthesizerState snapshot."""
        hint = (
            f"[Synthesizer: builds={self._build_count}, "
            f"last_system={self._last_system_chars}c]"
        )
        return SynthesizerState(
            identity_loaded=bool(self._identity_text),
            soul_loaded=bool(self._soul_text),
            last_hint_keys=list(self._last_hint_keys),
            last_system_chars=self._last_system_chars,
            last_user_chars=self._last_user_chars,
            build_count=self._build_count,
            prompt_hint=hint,
            timestamp=datetime.now(timezone.utc).isoformat(),
            degraded=self._degraded,
        )

    def publish(self, bus: StateBus) -> None:
        """Emit a ``synthesizer_tick`` StateEvent to the state bus."""
        try:
            state = self.get_state()
            event = StateEvent(
                source_module="prompt_synthesizer",
                event_type="synthesizer_tick",
                payload=state.to_dict(),
            )
            bus.publish_state(event, nowait=True)
        except Exception as exc:
            logger.warning("PromptSynthesizer.publish failed: %s", exc)

    # ── Internals ─────────────────────────────────────────────────────────────

    def _build_system(
        self,
        hints: Dict[str, str],
        memory_context: str,
        sensory_hints: Optional[Dict[str, str]] = None,
    ) -> str:
        """Assemble the system prompt string from all sections."""
        sections: List[str] = []

        # 1. Identity anchor (highest priority — always first)
        if self._identity_text:
            sections.append(self._identity_text)

        # 2. Soul / values anchor
        if self._soul_text:
            sections.append(self._soul_text)

        # 3. Module state hints in priority order, then any leftover keys
        ordered_keys: List[str] = []
        for key in _HINT_SECTION_ORDER:
            if key in hints:
                ordered_keys.append(key)
        for key in hints:
            if key not in ordered_keys:
                ordered_keys.append(key)

        if ordered_keys:
            hint_lines: List[str] = []
            for key in ordered_keys:
                raw = hints[key]
                line = raw[: self._max_hint_chars]
                hint_lines.append(line)
            sections.append("\n".join(hint_lines))

        # 3b. E-21: sensory layer injected after environment hints
        env_block = self._build_environment_block(sensory_hints or {})
        if env_block:
            sections.append(env_block)

        # 4. Memory context
        if memory_context:
            trimmed_mem = memory_context[: self._memory_chars]
            sections.append(f"[Memory context]\n{trimmed_mem}")

        combined = "\n\n".join(s.strip() for s in sections if s.strip())

        # Hard total cap — trim to max_system_chars preserving from the start
        if len(combined) > self._max_system_chars:
            combined = combined[: self._max_system_chars]
            logger.debug(
                "PromptSynthesizer: system prompt trimmed to %d chars.",
                self._max_system_chars,
            )

        return combined

    def _build_environment_block(self, sensory_hints: Dict[str, str]) -> str:
        """E-21: Format selected sensory channels as a 2-line Sensory Layer block.

        Only injected when include_sensory is True and hints are non-empty.
        Each channel appears on its own line: "  Channel: description".
        """
        if not self._include_sensory or not sensory_hints:
            return ""
        lines = ["[Sensory Layer]"]
        for channel, description in sensory_hints.items():
            lines.append(f"  {channel.title()}: {description}")
        return "\n".join(lines)

    def _load_text(self, filename: str, max_chars: int) -> str:
        """Load and trim a text file from the data root."""
        path = self._root / filename
        try:
            raw = path.read_text(encoding="utf-8")
            text = raw.strip()
            if len(text) > max_chars:
                # Trim at a paragraph break near the limit to avoid mid-sentence cuts
                trimmed = text[:max_chars]
                last_break = trimmed.rfind("\n\n")
                if last_break > max_chars // 2:
                    trimmed = trimmed[:last_break]
                text = trimmed
            logger.info("PromptSynthesizer: loaded '%s' (%d chars).", filename, len(text))
            return text
        except FileNotFoundError:
            logger.warning("PromptSynthesizer: '%s' not found in %s.", filename, self._root)
            self._degraded = True
            return ""
        except Exception as exc:
            logger.warning("PromptSynthesizer: failed to load '%s': %s", filename, exc)
            self._degraded = True
            return ""

    # ── Factory ───────────────────────────────────────────────────────────────

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "PromptSynthesizer":
        """Construct from a config dict.

        Reads keys under ``prompt_synthesizer``::

          data_root        (str,  default "data")
          identity_file    (str,  default "core_identity.md")
          soul_file        (str,  default "SOUL.md")
          identity_chars   (int,  default 2000)
          soul_chars       (int,  default 400)
          memory_chars     (int,  default 800)
          max_system_chars (int,  default 6000)
          max_hint_chars   (int,  default 200)
        """
        cfg: Dict[str, Any] = config.get("prompt_synthesizer", {})
        return cls(
            data_root=str(cfg.get("data_root", _DEFAULT_DATA_ROOT)),
            identity_file=str(cfg.get("identity_file", _DEFAULT_IDENTITY_FILE)),
            soul_file=str(cfg.get("soul_file", _DEFAULT_SOUL_FILE)),
            identity_chars=int(cfg.get("identity_chars", _DEFAULT_IDENTITY_CHARS)),
            soul_chars=int(cfg.get("soul_chars", _DEFAULT_SOUL_CHARS)),
            memory_chars=int(cfg.get("memory_chars", _DEFAULT_MEMORY_CHARS)),
            max_system_chars=int(cfg.get("max_system_chars", _DEFAULT_MAX_SYSTEM_CHARS)),
            max_hint_chars=int(cfg.get("max_hint_chars", _DEFAULT_MAX_HINT_CHARS)),
            include_sensory=bool(cfg.get("include_sensory", True)),
        )


# ─── Singleton ────────────────────────────────────────────────────────────────

_PROMPT_SYNTHESIZER: Optional[PromptSynthesizer] = None


def init_prompt_synthesizer_from_config(config: Dict[str, Any]) -> PromptSynthesizer:
    """Initialise the global PromptSynthesizer. Idempotent."""
    global _PROMPT_SYNTHESIZER
    if _PROMPT_SYNTHESIZER is None:
        _PROMPT_SYNTHESIZER = PromptSynthesizer.from_config(config)
        logger.info(
            "PromptSynthesizer initialised (identity=%s, soul=%s, degraded=%s).",
            bool(_PROMPT_SYNTHESIZER._identity_text),
            bool(_PROMPT_SYNTHESIZER._soul_text),
            _PROMPT_SYNTHESIZER._degraded,
        )
    return _PROMPT_SYNTHESIZER


def get_prompt_synthesizer() -> PromptSynthesizer:
    """Return the global PromptSynthesizer.

    Raises RuntimeError if not yet initialised.
    """
    if _PROMPT_SYNTHESIZER is None:
        raise RuntimeError(
            "PromptSynthesizer not initialised — call init_prompt_synthesizer_from_config() first."
        )
    return _PROMPT_SYNTHESIZER
