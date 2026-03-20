from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable

logger = logging.getLogger(__name__)

LLMRunner = Callable[[str], Awaitable[str]]

_PROMPT = """Summarize these {n} memory records about "{category}" into 2-3 concise key facts. Plain sentences only.

Records:
{records}

Summary:"""


class LLMConsolidator:
    """Summarizes episodic memory records using LLM, falls back to concatenation."""

    def __init__(
        self,
        run_llm: LLMRunner | None = None,
        *,
        max_records_per_call: int = 10,
        max_text_chars: int = 4000,
    ) -> None:
        self._run_llm = run_llm
        self._max_records = max(1, int(max_records_per_call))
        self._max_chars = max(100, int(max_text_chars))

    async def consolidate(self, records: list[Any], *, category: str = "general") -> str | None:
        if not records:
            return None
        trimmed = records[: self._max_records]
        if self._run_llm is not None:
            try:
                return await self._llm_consolidate(trimmed, category=category)
            except Exception as exc:
                logger.warning("llm consolidation failed category=%s error=%s", category, exc)
        return self._deterministic_consolidate(trimmed)

    async def _llm_consolidate(self, records: list[Any], *, category: str) -> str:
        texts = "\n".join(
            f"- {str(getattr(r, 'text', r) or '').strip()}"
            for r in records
            if str(getattr(r, "text", r) or "").strip()
        )
        if not texts:
            return self._deterministic_consolidate(records) or ""
        if len(texts) > self._max_chars:
            texts = texts[: self._max_chars] + "\n[truncated]"
        prompt = _PROMPT.format(n=len(records), category=category, records=texts)
        result = await self._run_llm(prompt)
        return str(result or "").strip()

    @staticmethod
    def _deterministic_consolidate(records: list[Any]) -> str:
        parts = [str(getattr(r, "text", r) or "").strip() for r in records]
        return " | ".join(p for p in parts if p)
