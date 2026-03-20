from __future__ import annotations

from typing import Any


def telegram_signals_payload(
    *,
    signals: dict[str, Any],
    send_auth_breaker_open: bool,
    typing_auth_breaker_open: bool,
    typing_keepalive_active: int,
    webhook_mode_active: bool,
    offset_snapshot: Any,
) -> dict[str, Any]:
    return {
        **signals,
        "send_auth_breaker_open": bool(send_auth_breaker_open),
        "typing_auth_breaker_open": bool(typing_auth_breaker_open),
        "typing_keepalive_active": int(typing_keepalive_active),
        "webhook_mode_active": bool(webhook_mode_active),
        "offset_next": int(getattr(offset_snapshot, "next_offset", 0) or 0),
        "offset_watermark_update_id": getattr(offset_snapshot, "safe_update_id", None),
        "offset_highest_completed_update_id": getattr(
            offset_snapshot,
            "highest_completed_update_id",
            None,
        ),
        "offset_pending_count": int(getattr(offset_snapshot, "pending_count", 0) or 0),
        "offset_min_pending_update_id": getattr(
            offset_snapshot,
            "min_pending_update_id",
            None,
        ),
    }


def telegram_operator_status_payload(
    *,
    mode: str,
    webhook_requested: bool,
    webhook_mode_active: bool,
    webhook_path: str,
    webhook_url_configured: bool,
    webhook_secret_configured: bool,
    offset_path: str,
    offset_snapshot: Any,
    pending_requests: list[dict[str, Any]],
    approved_entries: list[str],
    connected: bool,
    running: bool,
    last_error: str,
) -> dict[str, Any]:
    pending_count = len(pending_requests)
    approved_count = len(approved_entries)
    pending_updates = int(getattr(offset_snapshot, "pending_count", 0) or 0)
    hints: list[str] = []
    if webhook_requested and not webhook_url_configured:
        hints.append("Webhook mode is requested but no webhook URL is configured.")
    if webhook_requested and not webhook_mode_active:
        hints.append(
            "Webhook mode is requested but not active; try refreshing Telegram transport."
        )
    if pending_updates > 0:
        hints.append(
            f"{pending_updates} Telegram updates are still pending; replay inbound events or reconcile the next offset carefully."
        )
    if pending_count > 0:
        hints.append(f"{pending_count} Telegram pairing request(s) are pending review.")
    if last_error:
        hints.append(
            "Telegram recorded a transport error; inspect the error and consider refreshing transport state."
        )
    return {
        "mode": str(mode or "polling"),
        "webhook_requested": bool(webhook_requested),
        "webhook_mode_active": bool(webhook_mode_active),
        "webhook_path": str(webhook_path or ""),
        "webhook_url_configured": bool(webhook_url_configured),
        "webhook_secret_configured": bool(webhook_secret_configured),
        "offset_path": str(offset_path or ""),
        "offset_next": int(getattr(offset_snapshot, "next_offset", 0) or 0),
        "offset_watermark_update_id": getattr(offset_snapshot, "safe_update_id", None),
        "offset_highest_completed_update_id": getattr(
            offset_snapshot,
            "highest_completed_update_id",
            None,
        ),
        "offset_pending_count": pending_updates,
        "offset_min_pending_update_id": getattr(
            offset_snapshot,
            "min_pending_update_id",
            None,
        ),
        "pairing_pending_count": pending_count,
        "pairing_approved_count": approved_count,
        "pairing_pending": list(pending_requests),
        "pairing_approved": list(approved_entries),
        "connected": bool(connected),
        "running": bool(running),
        "last_error": str(last_error or ""),
        "hints": hints,
    }
