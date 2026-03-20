from __future__ import annotations

from typing import Final


_CHANNEL_READINESS: Final[dict[str, str]] = {
    "telegram": "stable",
    "discord": "stable",
    "slack": "beta",
    "email": "beta",
    "whatsapp": "beta",
    "signal": "beta",
    "googlechat": "beta",
    "matrix": "beta",
    "irc": "beta",
    "imessage": "experimental",
    "dingtalk": "experimental",
    "feishu": "experimental",
    "mochat": "experimental",
    "qq": "experimental",
}


def channel_readiness(name: str) -> str:
    normalized = str(name or "").strip().lower()
    if not normalized:
        return "experimental"
    return _CHANNEL_READINESS.get(normalized, "experimental")


def readiness_catalog() -> dict[str, str]:
    return dict(sorted(_CHANNEL_READINESS.items()))


__all__ = ["channel_readiness", "readiness_catalog"]
