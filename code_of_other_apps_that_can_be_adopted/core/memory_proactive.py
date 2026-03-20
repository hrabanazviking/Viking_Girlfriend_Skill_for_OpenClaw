from __future__ import annotations

import concurrent.futures
import logging
import re
import time
from typing import Any

logger = logging.getLogger(__name__)

_WORD_RE = re.compile(r"\b[A-Za-z][A-Za-z0-9_]{2,}\b")
_STOP_WORDS = frozenset({
    "the", "and", "for", "with", "that", "this", "what", "how", "does",
    "can", "will", "you", "are", "was", "has", "have", "been", "from",
    "into", "when", "where", "which", "your", "they", "their",
})


def _extract_topics(text: str, max_topics: int = 4) -> list[str]:
    words = _WORD_RE.findall(text)
    seen: dict[str, int] = {}
    for w in words:
        lower = w.lower()
        if lower not in _STOP_WORDS and len(lower) > 3:
            seen[lower] = seen.get(lower, 0) + 1
    ranked = sorted(seen.items(), key=lambda kv: -kv[1])
    return [k for k, _ in ranked[:max_topics]]


class ProactiveContextLoader:
    """Pre-warms memory context before agent turns."""

    def __init__(
        self,
        memory: Any,
        *,
        cache_ttl_s: float = 30.0,
        timeout_s: float = 0.5,
        max_snippets: int = 6,
    ) -> None:
        self._memory = memory
        self._cache_ttl_s = max(0.01, float(cache_ttl_s))
        self._timeout_s = max(0.01, float(timeout_s))
        self._max_snippets = max(1, int(max_snippets))
        self._cache: dict[str, tuple[list[str], float]] = {}

    def warm(self, user_text: str, *, session_id: str) -> list[str]:
        cache_key = f"{session_id}:{user_text[:100]}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            result, expires_at = cached
            if time.monotonic() < expires_at:
                return result

        topics = _extract_topics(user_text)
        if not topics:
            return []

        snippets: list[str] = []
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
                future = ex.submit(self._recall_topics, topics)
                snippets = future.result(timeout=self._timeout_s)
        except concurrent.futures.TimeoutError:
            logger.debug("proactive recall timeout session=%s", session_id)
        except Exception as exc:
            logger.debug("proactive recall error session=%s err=%s", session_id, exc)

        self._cache[cache_key] = (snippets, time.monotonic() + self._cache_ttl_s)
        return snippets

    def _recall_topics(self, topics: list[str]) -> list[str]:
        recall_fn = getattr(self._memory, "recall", None)
        if not callable(recall_fn):
            return []
        seen: set[str] = set()
        results: list[str] = []
        for topic in topics:
            try:
                records = recall_fn(topic, limit=3) or []
                for rec in records:
                    text = str(getattr(rec, "text", rec) or "").strip()
                    if text and text not in seen:
                        seen.add(text)
                        results.append(text)
                        if len(results) >= self._max_snippets:
                            return results
            except Exception:
                continue
        return results

    def invalidate(self, session_id: str) -> None:
        stale = [k for k in self._cache if k.startswith(f"{session_id}:")]
        for k in stale:
            del self._cache[k]
