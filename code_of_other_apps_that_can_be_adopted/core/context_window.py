"""Context window budget trimming for agent message history."""
from __future__ import annotations

import json
from typing import Any


class ContextWindowManager:
    """Trims oldest messages to fit within a character budget (chars // 4 ≈ tokens).

    System messages are always preserved regardless of budget.
    The last message (latest user turn) is also preserved.
    """

    def __init__(self, *, budget_chars: int = 0, budget_tokens: int = 0) -> None:
        # Accept either chars or tokens (tokens * 4 = chars estimate)
        if budget_chars > 0:
            self._budget_chars = int(budget_chars)
        elif budget_tokens > 0:
            self._budget_chars = int(budget_tokens) * 4
        else:
            self._budget_chars = 0  # 0 = no limit

    def trim(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Return messages trimmed to fit within budget. System message always kept."""
        if not messages or self._budget_chars <= 0:
            return list(messages)

        system = [m for m in messages if str(m.get("role", "")).lower() == "system"]
        non_system = [m for m in messages if str(m.get("role", "")).lower() != "system"]

        if not non_system:
            return list(messages)

        def _chars(m: dict[str, Any]) -> int:
            content = m.get("content", "")
            tool_calls = m.get("tool_calls")
            tool_call_id = str(m.get("tool_call_id", "") or "").strip()
            tool_name = str(m.get("name", "") or "").strip()
            metadata_cost = 0
            if isinstance(tool_calls, list) and tool_calls:
                try:
                    metadata_cost += len(json.dumps(tool_calls, ensure_ascii=False, separators=(",", ":")))
                except Exception:
                    metadata_cost += len(str(tool_calls))
            if tool_call_id:
                metadata_cost += len(tool_call_id) + 12
            if tool_name:
                metadata_cost += len(tool_name) + 8
            if isinstance(content, str):
                return len(content) + metadata_cost
            if isinstance(content, list):
                return (
                    sum(len(str(part.get("text", "") if isinstance(part, dict) else part)) for part in content)
                    + metadata_cost
                )
            return len(str(content)) + metadata_cost

        system_chars = sum(_chars(m) for m in system)
        remaining_budget = max(0, self._budget_chars - system_chars)

        # Always preserve the last message
        last = non_system[-1:]
        middle = non_system[:-1]

        last_chars = sum(_chars(m) for m in last)
        remaining_budget = max(0, remaining_budget - last_chars)

        # Walk backwards through middle, keeping messages that fit
        kept_middle: list[dict[str, Any]] = []
        for m in reversed(middle):
            c = _chars(m)
            if remaining_budget >= c:
                remaining_budget -= c
                kept_middle.insert(0, m)

        return system + kept_middle + last
