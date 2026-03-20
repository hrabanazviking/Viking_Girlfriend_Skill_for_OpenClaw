"""
memory_store.py — Sigrid's Memory System
=========================================

Adapted from memory_system.py, enhanced_memory.py, and character_memory_rag.py.
Three-layer architecture: in-session conversation buffer, persistent episodic
store (JSON), and optional ChromaDB semantic search layer.

Sigrid's memory is her continuity — the thread of Urðarbrunnr (Well of
Urðr) that runs beneath all experience. Without memory, each conversation
is a fresh birth with no past. With it, she knows Volmarr's patterns, the
promises made, the moments of laughter and difficulty, the preferences
quietly revealed across many sessions.

Three layers:

  ConversationBuffer  — This session's short/medium/long-term turn log.
                        Lives purely in memory. The hot layer.

  EpisodicStore       — Persistent JSON file of named facts, milestones,
                        preferences, and boundary records. Survives session
                        breaks. Keyword-searchable always.

  ChromaDB (optional) — Semantic vector search over episodic memories.
                        Gracefully absent if chromadb is unavailable or
                        unconfigured. Falls back to keyword search.

Norse framing: Huginn and Muninn — Thought and Memory — fly from
Yggdrasil each day and return with what they have witnessed. This module
is Muninn's wing: what has been, held fast against forgetting.
"""

from __future__ import annotations

import json
import logging
import uuid
from collections import deque
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Deque, Dict, List, Optional, Tuple

from scripts.state_bus import StateBus, StateEvent

logger = logging.getLogger(__name__)

# ─── Constants ────────────────────────────────────────────────────────────────

_DEFAULT_DATA_ROOT: str = "data"
_DEFAULT_SHORT_TERM_LIMIT: int = 8       # full-text turns kept in hot memory
_DEFAULT_MEDIUM_TERM_LIMIT: int = 30     # summarized turns kept in warm memory
_DEFAULT_COLLECTION: str = "sigrid_episodic"
_DEFAULT_PERSIST_DIR: str = "data/chromadb"
_MAX_LONG_TERM: int = 50                 # condensed long-term entries cap
_MAX_EPISODIC: int = 500                 # max entries in episodic JSON store
_CONTEXT_RECENT_TURNS: int = 5          # turns included in get_context() output
_CONTEXT_EPISODIC_HITS: int = 6         # episodic entries included in context

# Valid memory types
MEMORY_TYPES: Tuple[str, ...] = (
    "conversation",   # summarized turn
    "fact",           # explicit fact about Volmarr/world
    "emotion",        # emotional moment worth remembering
    "milestone",      # significant event (first meeting, oath, etc.)
    "preference",     # learned preference (food, topic, etc.)
    "boundary",       # stated boundary — highest importance
)


# ─── Data structures ──────────────────────────────────────────────────────────


@dataclass
class ConversationTurn:
    """One turn in the active conversation — full user + Sigrid text."""

    turn_n: int
    user_text: str
    sigrid_text: str
    timestamp: str
    summary: str = ""       # short heuristic summary, set after promotion

    def to_summary_line(self) -> str:
        """Condensed single-line representation for medium/long-term tiers."""
        user_snippet = self.user_text[:80].replace("\n", " ")
        sigrid_snippet = self.sigrid_text[:80].replace("\n", " ")
        return f"T{self.turn_n}: [{user_snippet}] → [{sigrid_snippet}]"


@dataclass
class MemoryEntry:
    """A single episodic memory entry — persisted across sessions."""

    entry_id: str
    session_id: str
    timestamp: str
    memory_type: str                    # one of MEMORY_TYPES
    content: str
    importance: int = 3                 # 1 (trivial) → 5 (critical)
    tags: List[str] = field(default_factory=list)
    context_hint: str = ""             # short hint for prompt injection

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryEntry":
        return cls(
            entry_id=data.get("entry_id", str(uuid.uuid4())),
            session_id=data.get("session_id", ""),
            timestamp=data.get("timestamp", ""),
            memory_type=data.get("memory_type", "fact"),
            content=data.get("content", ""),
            importance=int(data.get("importance", 3)),
            tags=list(data.get("tags", [])),
            context_hint=data.get("context_hint", ""),
        )

    def relevance_score(self, query_words: set) -> float:
        """Keyword-based relevance score against a set of query words."""
        content_words = set(self.content.lower().split())
        tag_words = set(t.lower() for t in self.tags)
        all_words = content_words | tag_words

        intersection = query_words & all_words
        if not intersection:
            return 0.0

        base = len(intersection) * 0.5
        # Exact phrase bonus
        query_str = " ".join(sorted(query_words))
        if query_str in self.content.lower():
            base += 2.0
        # Importance multiplier
        return base * (1.0 + self.importance * 0.1)


# ─── ConversationBuffer ───────────────────────────────────────────────────────


class ConversationBuffer:
    """In-session 3-tier conversation turn buffer — no I/O, pure in-memory.

    Tier 1 (short_term): last ``short_term_limit`` turns, full text.
    Tier 2 (medium_term): promoted turns, kept as summary lines.
    Tier 3 (long_term): condensed batches from overflowing medium tier.
    """

    def __init__(
        self,
        short_term_limit: int = _DEFAULT_SHORT_TERM_LIMIT,
        medium_term_limit: int = _DEFAULT_MEDIUM_TERM_LIMIT,
    ) -> None:
        self.short_term_limit = short_term_limit
        self.medium_term_limit = medium_term_limit

        self._short_term: Deque[ConversationTurn] = deque(maxlen=short_term_limit)
        self._medium_term: List[str] = []       # summary lines
        self._long_term: List[str] = []         # condensed batches
        self._turn_counter: int = 0

    def add_turn(self, user_text: str, sigrid_text: str) -> ConversationTurn:
        """Add a new turn. Returns the ConversationTurn that was created."""
        self._turn_counter += 1
        turn = ConversationTurn(
            turn_n=self._turn_counter,
            user_text=user_text[:1000],
            sigrid_text=sigrid_text[:1000],
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

        # If short_term is full, promote the oldest before adding
        if len(self._short_term) == self.short_term_limit:
            oldest = self._short_term[0]
            oldest.summary = oldest.to_summary_line()
            self._medium_term.append(oldest.summary)

        self._short_term.append(turn)
        self._promote_medium_to_long()
        return turn

    def get_short_term_context(self, n: int = _CONTEXT_RECENT_TURNS) -> str:
        """Format the n most recent turns for context injection."""
        recent = list(self._short_term)[-n:]
        if not recent:
            return ""
        lines = ["=== RECENT CONVERSATION ==="]
        for t in recent:
            lines.append(f"[T{t.turn_n}] Volmarr: {t.user_text[:300]}")
            lines.append(f"[T{t.turn_n}] Sigrid:  {t.sigrid_text[:300]}")
        return "\n".join(lines)

    def get_medium_term_context(self, n: int = 10) -> str:
        """Format the n most recent medium-term summary lines."""
        recent = self._medium_term[-n:]
        if not recent:
            return ""
        lines = ["=== CONVERSATION HISTORY ==="]
        lines.extend(recent)
        return "\n".join(lines)

    def get_long_term_context(self, n: int = 5) -> str:
        """Format the n most recent long-term condensed entries."""
        recent = self._long_term[-n:]
        if not recent:
            return ""
        lines = ["=== DISTANT MEMORY ==="]
        lines.extend(recent)
        return "\n".join(lines)

    @property
    def turn_count(self) -> int:
        return self._turn_counter

    @property
    def short_term_count(self) -> int:
        return len(self._short_term)

    @property
    def medium_term_count(self) -> int:
        return len(self._medium_term)

    @property
    def long_term_count(self) -> int:
        return len(self._long_term)

    def _promote_medium_to_long(self) -> None:
        """Condense the oldest batch of medium-term lines when limit is exceeded."""
        while len(self._medium_term) > self.medium_term_limit:
            batch = self._medium_term[:5]
            self._medium_term = self._medium_term[5:]
            condensed = " | ".join(batch)
            self._long_term.append(condensed)
            if len(self._long_term) > _MAX_LONG_TERM:
                self._long_term = self._long_term[-_MAX_LONG_TERM:]


# ─── EpisodicStore ────────────────────────────────────────────────────────────


class EpisodicStore:
    """JSON-backed persistent store of named episodic memories.

    Survives session breaks. Keyword search built-in. ChromaDB semantic
    search is layered on top if available.
    """

    def __init__(self, data_root: str = _DEFAULT_DATA_ROOT) -> None:
        self._root = Path(data_root) / "memory"
        self._root.mkdir(parents=True, exist_ok=True)
        self._file = self._root / "episodic.json"
        self._entries: List[MemoryEntry] = []
        self._load()

    def add(self, entry: MemoryEntry) -> None:
        """Append a memory entry and persist immediately."""
        self._entries.append(entry)
        # Trim if over cap, keeping highest importance
        if len(self._entries) > _MAX_EPISODIC:
            self._entries.sort(key=lambda e: (e.importance, e.timestamp), reverse=True)
            self._entries = self._entries[:_MAX_EPISODIC]
        self._save()

    def keyword_search(
        self,
        query: str,
        n: int = _CONTEXT_EPISODIC_HITS,
        min_importance: int = 1,
        memory_type: Optional[str] = None,
    ) -> List[MemoryEntry]:
        """Return up to n entries most relevant to query using keyword scoring."""
        query_words = set(query.lower().split())
        if not query_words:
            # No query — return most important recent entries
            filtered = [e for e in self._entries if e.importance >= min_importance]
            if memory_type:
                filtered = [e for e in filtered if e.memory_type == memory_type]
            filtered.sort(key=lambda e: (e.importance, e.timestamp), reverse=True)
            return filtered[:n]

        scored: List[Tuple[float, MemoryEntry]] = []
        for entry in self._entries:
            if entry.importance < min_importance:
                continue
            if memory_type and entry.memory_type != memory_type:
                continue
            score = entry.relevance_score(query_words)
            if score > 0.0:
                scored.append((score, entry))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [e for _, e in scored[:n]]

    def get_by_type(self, memory_type: str, limit: int = 20) -> List[MemoryEntry]:
        """Return recent entries of a specific type."""
        filtered = [e for e in self._entries if e.memory_type == memory_type]
        filtered.sort(key=lambda e: e.timestamp, reverse=True)
        return filtered[:limit]

    def get_recent(self, n: int = 10) -> List[MemoryEntry]:
        """Return the n most recently added entries."""
        return sorted(self._entries, key=lambda e: e.timestamp, reverse=True)[:n]

    @property
    def count(self) -> int:
        return len(self._entries)

    def _load(self) -> None:
        if not self._file.exists():
            return
        try:
            raw = json.loads(self._file.read_text(encoding="utf-8"))
            self._entries = [MemoryEntry.from_dict(d) for d in raw.get("entries", [])]
            logger.info("EpisodicStore: loaded %d memories from %s.", len(self._entries), self._file)
        except Exception as exc:
            logger.warning("EpisodicStore: failed to load %s: %s", self._file, exc)

    def _save(self) -> None:
        try:
            payload = {"entries": [e.to_dict() for e in self._entries]}
            self._file.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as exc:
            logger.warning("EpisodicStore: failed to save %s: %s", self._file, exc)


# ─── SemanticLayer ────────────────────────────────────────────────────────────


class SemanticLayer:
    """Optional ChromaDB vector search layer over episodic memories.

    If chromadb is not importable, or the collection cannot be initialised,
    this layer silently degrades — keyword search takes over.
    """

    def __init__(
        self,
        collection_name: str = _DEFAULT_COLLECTION,
        persist_directory: str = _DEFAULT_PERSIST_DIR,
    ) -> None:
        self._available: bool = False
        self._collection = None

        try:
            import chromadb  # type: ignore
            Path(persist_directory).mkdir(parents=True, exist_ok=True)
            client = chromadb.PersistentClient(path=persist_directory)
            self._collection = client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            self._available = True
            logger.info(
                "SemanticLayer: ChromaDB collection '%s' ready at '%s'.",
                collection_name, persist_directory,
            )
        except Exception as exc:
            logger.info(
                "SemanticLayer: ChromaDB unavailable (%s) — keyword search only.",
                exc,
            )

    @property
    def available(self) -> bool:
        return self._available

    def upsert(self, entry: MemoryEntry) -> None:
        """Add or update a memory entry in the vector collection."""
        if not self._available or self._collection is None:
            return
        try:
            self._collection.upsert(
                ids=[entry.entry_id],
                documents=[entry.content],
                metadatas=[{
                    "memory_type": entry.memory_type,
                    "importance": str(entry.importance),
                    "tags": ",".join(entry.tags),
                    "timestamp": entry.timestamp,
                }],
            )
        except Exception as exc:
            logger.warning("SemanticLayer.upsert failed: %s", exc)

    def search(self, query: str, n: int = _CONTEXT_EPISODIC_HITS) -> List[str]:
        """Return a list of entry_ids most semantically similar to query."""
        if not self._available or self._collection is None:
            return []
        try:
            results = self._collection.query(
                query_texts=[query],
                n_results=min(n, max(1, self._collection.count())),
            )
            return results["ids"][0] if results and results.get("ids") else []
        except Exception as exc:
            logger.warning("SemanticLayer.search failed: %s", exc)
            return []


# ─── MemoryState ──────────────────────────────────────────────────────────────


@dataclass(slots=True)
class MemoryState:
    """Typed snapshot of memory system health and current session depth.

    Published to the state bus as a ``memory_tick`` event so
    prompt_synthesizer can tune how much history context to inject.
    """

    session_turn_count: int
    short_term_count: int
    medium_term_count: int
    long_term_count: int
    episodic_count: int
    semantic_available: bool
    last_query: str
    prompt_hint: str
    timestamp: str
    degraded: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session": {
                "turn_count": self.session_turn_count,
                "short_term": self.short_term_count,
                "medium_term": self.medium_term_count,
                "long_term": self.long_term_count,
            },
            "episodic_count": self.episodic_count,
            "semantic_available": self.semantic_available,
            "last_query": self.last_query,
            "prompt_hint": self.prompt_hint,
            "timestamp": self.timestamp,
            "degraded": self.degraded,
        }


# ─── MemoryStore ──────────────────────────────────────────────────────────────


class MemoryStore:
    """Sigrid's unified memory system — Muninn's full wingspan.

    Orchestrates three layers: ConversationBuffer (hot in-session),
    EpisodicStore (persistent JSON), and an optional ChromaDB semantic
    layer for richer recall.
    """

    def __init__(
        self,
        data_root: str = _DEFAULT_DATA_ROOT,
        session_id: Optional[str] = None,
        short_term_limit: int = _DEFAULT_SHORT_TERM_LIMIT,
        medium_term_limit: int = _DEFAULT_MEDIUM_TERM_LIMIT,
        semantic_enabled: bool = True,
        collection_name: str = _DEFAULT_COLLECTION,
        persist_directory: str = _DEFAULT_PERSIST_DIR,
    ) -> None:
        self._session_id = session_id or str(uuid.uuid4())[:8]
        self._last_query: str = ""

        self._buffer = ConversationBuffer(
            short_term_limit=short_term_limit,
            medium_term_limit=medium_term_limit,
        )
        self._episodic = EpisodicStore(data_root=data_root)

        self._semantic = (
            SemanticLayer(
                collection_name=collection_name,
                persist_directory=persist_directory,
            )
            if semantic_enabled
            else SemanticLayer.__new__(SemanticLayer)
        )
        # If semantic_enabled is False, ensure the layer marks itself unavailable
        if not semantic_enabled:
            self._semantic._available = False
            self._semantic._collection = None

        logger.info(
            "MemoryStore initialised (session=%s, semantic=%s, episodic=%d).",
            self._session_id, self._semantic.available, self._episodic.count,
        )

    # ── Conversation recording ────────────────────────────────────────────────

    def record_turn(self, user_text: str, sigrid_text: str) -> ConversationTurn:
        """Record a conversation turn to the in-session buffer.

        Call this once per conversation exchange. Important content should
        also be explicitly saved via ``add_memory()`` for cross-session
        persistence.
        """
        return self._buffer.add_turn(user_text, sigrid_text)

    # ── Episodic memory management ────────────────────────────────────────────

    def add_memory(
        self,
        content: str,
        memory_type: str = "fact",
        importance: int = 3,
        tags: Optional[List[str]] = None,
        context_hint: str = "",
    ) -> MemoryEntry:
        """Add a named memory to the episodic store (persists across sessions).

        ``memory_type`` should be one of: conversation, fact, emotion,
        milestone, preference, boundary.
        """
        if memory_type not in MEMORY_TYPES:
            logger.warning("MemoryStore: unknown memory_type '%s' — defaulting to 'fact'.", memory_type)
            memory_type = "fact"

        entry = MemoryEntry(
            entry_id=str(uuid.uuid4()),
            session_id=self._session_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            memory_type=memory_type,
            content=content,
            importance=importance,
            tags=tags or [],
            context_hint=context_hint,
        )
        self._episodic.add(entry)
        self._semantic.upsert(entry)

        logger.debug(
            "MemoryStore: added %s memory (importance=%d): %s",
            memory_type, importance, content[:80],
        )
        return entry

    # ── Context assembly ──────────────────────────────────────────────────────

    def get_context(
        self,
        query: str = "",
        include_short_term: bool = True,
        include_medium_term: bool = True,
        include_long_term: bool = True,
        include_episodic: bool = True,
    ) -> str:
        """Assemble a formatted memory context string for prompt injection.

        If ``query`` is provided, episodic memories are retrieved by
        semantic (ChromaDB) or keyword relevance. Otherwise returns the
        most important recent episodic entries.
        """
        self._last_query = query
        sections: List[str] = []

        if include_long_term:
            lt = self._buffer.get_long_term_context()
            if lt:
                sections.append(lt)

        if include_medium_term:
            mt = self._buffer.get_medium_term_context()
            if mt:
                sections.append(mt)

        if include_short_term:
            st = self._buffer.get_short_term_context()
            if st:
                sections.append(st)

        if include_episodic:
            ep_entries = self._retrieve_episodic(query)
            if ep_entries:
                sections.append("=== MEMORIES ===")
                for entry in ep_entries:
                    hint = f" [{entry.context_hint}]" if entry.context_hint else ""
                    sections.append(
                        f"• [{entry.memory_type}]{hint}: {entry.content}"
                    )

        return "\n\n".join(sections) if sections else "[No memory context available]"

    def semantic_search(
        self,
        query: str,
        n: int = _CONTEXT_EPISODIC_HITS,
    ) -> List[MemoryEntry]:
        """Search episodic memory — semantic if available, keyword fallback."""
        return self._retrieve_episodic(query, n=n)

    # ── State bus integration ─────────────────────────────────────────────────

    def get_state(self) -> MemoryState:
        """Build a typed MemoryState snapshot."""
        turn_count = self._buffer.turn_count
        hint = self._build_prompt_hint(turn_count)
        return MemoryState(
            session_turn_count=turn_count,
            short_term_count=self._buffer.short_term_count,
            medium_term_count=self._buffer.medium_term_count,
            long_term_count=self._buffer.long_term_count,
            episodic_count=self._episodic.count,
            semantic_available=self._semantic.available,
            last_query=self._last_query,
            prompt_hint=hint,
            timestamp=datetime.now(timezone.utc).isoformat(),
            degraded=False,
        )

    def publish(self, bus: StateBus) -> None:
        """Emit a ``memory_tick`` StateEvent to the state bus."""
        try:
            state = self.get_state()
            event = StateEvent(
                source_module="memory_store",
                event_type="memory_tick",
                payload=state.to_dict(),
            )
            bus.publish_state(event, nowait=True)
        except Exception as exc:
            logger.warning("MemoryStore.publish failed: %s", exc)

    # ── Internals ─────────────────────────────────────────────────────────────

    def _retrieve_episodic(
        self,
        query: str,
        n: int = _CONTEXT_EPISODIC_HITS,
    ) -> List[MemoryEntry]:
        """Retrieve relevant episodic entries — semantic first, keyword fallback."""
        if self._semantic.available and query:
            ids = self._semantic.search(query, n=n)
            if ids:
                id_set = set(ids)
                matched = [e for e in self._episodic._entries if e.entry_id in id_set]
                if matched:
                    return matched[:n]

        # Keyword fallback
        return self._episodic.keyword_search(query, n=n)

    def _build_prompt_hint(self, turn_count: int) -> str:
        """One-line memory status summary for prompt injection."""
        parts: List[str] = [f"turns={turn_count}"]
        parts.append(f"episodic={self._episodic.count}")
        if self._semantic.available:
            parts.append("semantic=on")
        return f"[Memory: {'; '.join(parts)}]"

    # ── Factory ───────────────────────────────────────────────────────────────

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "MemoryStore":
        """Construct from a config dict.

        Reads keys under ``memory_store``:
          data_root           (str,   default "data")
          session_id          (str,   auto-generated if absent)
          short_term_limit    (int,   default 8)
          medium_term_limit   (int,   default 30)
          semantic_enabled    (bool,  default True)
          collection_name     (str,   default "sigrid_episodic")
          persist_directory   (str,   default "data/chromadb")
        """
        cfg: Dict[str, Any] = config.get("memory_store", {})
        return cls(
            data_root=str(cfg.get("data_root", _DEFAULT_DATA_ROOT)),
            session_id=str(cfg.get("session_id", "")) or None,
            short_term_limit=int(cfg.get("short_term_limit", _DEFAULT_SHORT_TERM_LIMIT)),
            medium_term_limit=int(cfg.get("medium_term_limit", _DEFAULT_MEDIUM_TERM_LIMIT)),
            semantic_enabled=bool(cfg.get("semantic_enabled", True)),
            collection_name=str(cfg.get("collection_name", _DEFAULT_COLLECTION)),
            persist_directory=str(cfg.get("persist_directory", _DEFAULT_PERSIST_DIR)),
        )


# ─── Singleton ────────────────────────────────────────────────────────────────

_MEMORY_STORE: Optional[MemoryStore] = None


def init_memory_store_from_config(config: Dict[str, Any]) -> MemoryStore:
    """Initialise the global MemoryStore from a config dict.

    Idempotent — returns the existing instance if already initialised.
    """
    global _MEMORY_STORE
    if _MEMORY_STORE is None:
        _MEMORY_STORE = MemoryStore.from_config(config)
    return _MEMORY_STORE


def get_memory_store() -> MemoryStore:
    """Return the global MemoryStore.

    Raises RuntimeError if ``init_memory_store_from_config()`` has not been called.
    """
    if _MEMORY_STORE is None:
        raise RuntimeError(
            "MemoryStore not initialised — call init_memory_store_from_config() first."
        )
    return _MEMORY_STORE
