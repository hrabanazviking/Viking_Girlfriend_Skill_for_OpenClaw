from __future__ import annotations

import asyncio
import hmac
import json
from dataclasses import dataclass
from typing import Any

from fastapi import HTTPException, Request


@dataclass
class GatewayWebhookHandlers:
    config: Any
    runtime: Any
    telegram_max_body_bytes: int
    whatsapp_max_body_bytes: int

    @staticmethod
    async def _read_json_body(request: Request, *, timeout_s: float, max_body_bytes: int, error_prefix: str) -> dict[str, Any]:
        try:
            raw_body = await asyncio.wait_for(request.body(), timeout=timeout_s)
        except asyncio.TimeoutError as exc:
            raise HTTPException(status_code=408, detail=f"{error_prefix}_payload_timeout") from exc
        if len(raw_body) > max_body_bytes:
            raise HTTPException(status_code=413, detail=f"{error_prefix}_payload_too_large")
        try:
            payload = json.loads(raw_body)
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=400, detail=f"{error_prefix}_payload_invalid") from exc
        if not isinstance(payload, dict):
            raise HTTPException(status_code=400, detail=f"{error_prefix}_payload_invalid")
        return payload

    async def telegram(self, request: Request) -> dict[str, Any]:
        if not self.config.channels.telegram.enabled:
            raise HTTPException(status_code=409, detail="telegram_channel_disabled")

        channel = self.runtime.channels.get_channel("telegram")
        if channel is None:
            raise HTTPException(status_code=409, detail="telegram_channel_unavailable")

        if not bool(getattr(channel, "webhook_mode_active", False)):
            raise HTTPException(status_code=409, detail="telegram_webhook_mode_inactive")

        expected_secret = str(getattr(channel, "webhook_secret", "") or "").strip()
        if expected_secret:
            supplied_secret = str(request.headers.get("X-Telegram-Bot-Api-Secret-Token", "") or "")
            if not supplied_secret or not hmac.compare_digest(supplied_secret, expected_secret):
                raise HTTPException(status_code=401, detail="telegram_webhook_secret_invalid")

        payload = await self._read_json_body(
            request,
            timeout_s=5.0,
            max_body_bytes=self.telegram_max_body_bytes,
            error_prefix="telegram_webhook",
        )

        handler = getattr(channel, "handle_webhook_update", None)
        if not callable(handler):
            raise HTTPException(status_code=409, detail="telegram_webhook_handler_unavailable")

        processed = bool(await handler(payload))
        if (not processed) and bool(getattr(self.config.channels.telegram, "webhook_fail_fast_on_error", False)):
            raise HTTPException(status_code=503, detail="telegram_webhook_processing_failed")
        return {"ok": True, "processed": processed}

    async def whatsapp(self, request: Request) -> dict[str, Any]:
        if not self.config.channels.whatsapp.enabled:
            raise HTTPException(status_code=409, detail="whatsapp_channel_disabled")

        channel = self.runtime.channels.get_channel("whatsapp")
        if channel is None:
            raise HTTPException(status_code=409, detail="whatsapp_channel_unavailable")

        expected_secret = str(
            getattr(self.config.channels.whatsapp, "webhook_secret", "")
            or getattr(channel, "webhook_secret", "")
            or ""
        ).strip()
        if not expected_secret:
            raise HTTPException(status_code=409, detail="whatsapp_webhook_secret_missing")
        auth_header = str(request.headers.get("Authorization", "") or "")
        bearer = ""
        if auth_header.lower().startswith("bearer "):
            bearer = auth_header[7:].strip()
        supplied_secret = str(request.headers.get("X-Webhook-Secret", "") or "").strip()
        if not supplied_secret:
            supplied_secret = bearer
        if not supplied_secret or not hmac.compare_digest(supplied_secret, expected_secret):
            raise HTTPException(status_code=401, detail="whatsapp_webhook_secret_invalid")

        payload = await self._read_json_body(
            request,
            timeout_s=5.0,
            max_body_bytes=self.whatsapp_max_body_bytes,
            error_prefix="whatsapp_webhook",
        )

        handler = getattr(channel, "receive_hook", None)
        if not callable(handler):
            raise HTTPException(status_code=409, detail="whatsapp_webhook_handler_unavailable")

        processed = bool(await handler(payload))
        return {"ok": True, "processed": processed}
