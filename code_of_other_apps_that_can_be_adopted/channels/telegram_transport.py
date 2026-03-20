from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True, frozen=True)
class TelegramWebhookDeleteResult:
    deleted: bool
    legacy: bool = False
    error: str = ""


@dataclass(slots=True, frozen=True)
class TelegramWebhookActivationResult:
    activated: bool
    connected: bool = False
    webhook_mode_active: bool = False
    last_error: str = ""
    bot_init_error: bool = False
    missing: tuple[str, ...] = ()
    bot_missing_set_webhook: bool = False


def webhook_requested(*, mode: str, webhook_enabled: bool) -> bool:
    return str(mode or "").strip().lower() == "webhook" or bool(webhook_enabled)


def operator_refresh_summary(
    *,
    mode: str,
    webhook_requested: bool,
    webhook_mode_active: bool,
    connected: bool,
    last_error: str,
) -> dict[str, Any]:
    return {
        "mode": str(mode or "polling"),
        "webhook_requested": bool(webhook_requested),
        "offset_reloaded": False,
        "webhook_deleted": False,
        "webhook_activated": False,
        "bot_initialized": False,
        "connected": bool(connected),
        "webhook_mode_active": bool(webhook_mode_active),
        "last_error": str(last_error or ""),
    }


async def delete_webhook(*, bot: Any) -> TelegramWebhookDeleteResult:
    if bot is None or not hasattr(bot, "delete_webhook"):
        return TelegramWebhookDeleteResult(deleted=False)
    try:
        await bot.delete_webhook(drop_pending_updates=False)
        return TelegramWebhookDeleteResult(deleted=True)
    except TypeError as exc:
        if "drop_pending_updates" not in str(exc):
            return TelegramWebhookDeleteResult(deleted=False, error=str(exc))
        try:
            await bot.delete_webhook()
            return TelegramWebhookDeleteResult(deleted=True, legacy=True)
        except Exception as legacy_exc:  # pragma: no cover
            return TelegramWebhookDeleteResult(
                deleted=False,
                error=str(legacy_exc),
            )
    except Exception as exc:  # pragma: no cover
        return TelegramWebhookDeleteResult(deleted=False, error=str(exc))


async def activate_webhook(
    *,
    ensure_bot: Callable[[], Awaitable[Any]],
    webhook_url: str,
    webhook_secret: str,
    allowed_updates: list[str],
) -> TelegramWebhookActivationResult:
    missing: list[str] = []
    if not str(webhook_url or "").strip():
        missing.append("webhook_url")
    if not str(webhook_secret or "").strip():
        missing.append("webhook_secret")
    if missing:
        return TelegramWebhookActivationResult(
            activated=False,
            missing=tuple(missing),
        )
    try:
        bot = await ensure_bot()
    except Exception as exc:  # pragma: no cover
        return TelegramWebhookActivationResult(
            activated=False,
            last_error=str(exc),
            bot_init_error=True,
        )
    if not hasattr(bot, "set_webhook"):
        return TelegramWebhookActivationResult(
            activated=False,
            bot_missing_set_webhook=True,
        )
    try:
        await bot.set_webhook(
            url=str(webhook_url or ""),
            secret_token=str(webhook_secret or ""),
            allowed_updates=list(allowed_updates),
        )
        return TelegramWebhookActivationResult(
            activated=True,
            connected=True,
            webhook_mode_active=True,
        )
    except Exception as exc:
        return TelegramWebhookActivationResult(
            activated=False,
            last_error=str(exc),
        )
