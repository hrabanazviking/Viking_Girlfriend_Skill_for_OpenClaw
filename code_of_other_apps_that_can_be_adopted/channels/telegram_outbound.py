from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from loguru import logger

from clawlite.channels.telegram_delivery import (
    TelegramAuthCircuitBreaker,
    TelegramCircuitOpenError,
    TelegramRetryPolicy,
    is_auth_failure,
    is_formatting_error,
    is_thread_not_found_error,
    is_transient_failure,
    retry_after_delay_s,
    retry_delay_s,
)


@dataclass(slots=True)
class TelegramOutboundRuntime:
    bot: Any
    policy: TelegramRetryPolicy
    send_timeout_s: float
    send_auth_breaker: TelegramAuthCircuitBreaker
    signals: dict[str, int]
    split_message: Callable[[str], list[str]]
    render_outbound_text: Callable[[str], tuple[str, str | None]]
    normalize_api_message_thread_id: Callable[..., int | None]
    threadless_retry_allowed: Callable[..., bool]
    resolve_media_sender: Callable[[Any, str], tuple[Any, str]]
    resolve_outbound_media_payload: Callable[[dict[str, Any]], Awaitable[Any]]
    sync_auth_breaker_signal_transition: Callable[..., None]
    on_send_auth_success: Callable[[], None]
    on_send_auth_failure: Callable[[], None]


def _remember_message_id(result: Any, message_ids: list[int]) -> None:
    if result is None:
        return
    raw_message_id = getattr(result, "message_id", None)
    try:
        message_id = int(raw_message_id)
    except (TypeError, ValueError):
        return
    if message_id > 0:
        message_ids.append(message_id)


async def send_text_chunks(
    *,
    runtime: TelegramOutboundRuntime,
    chat_id: str,
    text: str,
    outbound_parse_mode: str,
    reply_to_message_id: int | None,
    thread_state: dict[str, int | None],
    reply_markup: Any | None,
    message_ids: list[int],
) -> int:
    chunks = runtime.split_message(text)
    policy = runtime.policy.normalized()

    for idx, chunk in enumerate(chunks, start=1):
        payload_text, payload_parse_mode = runtime.render_outbound_text(
            chunk,
            parse_mode=outbound_parse_mode,
        )
        formatting_fallback_used = False

        for attempt in range(1, policy.max_attempts + 1):
            runtime.sync_auth_breaker_signal_transition(
                breaker=runtime.send_auth_breaker,
                key_prefix="send",
            )
            if runtime.send_auth_breaker.is_open:
                raise TelegramCircuitOpenError("telegram auth circuit is open")
            active_thread_id = runtime.normalize_api_message_thread_id(
                chat_id=chat_id,
                message_thread_id=thread_state.get("message_thread_id"),
            )
            try:
                payload: dict[str, Any] = {
                    "chat_id": chat_id,
                    "text": payload_text,
                    "parse_mode": payload_parse_mode,
                    "reply_to_message_id": reply_to_message_id,
                }
                if reply_markup is not None:
                    payload["reply_markup"] = reply_markup
                if active_thread_id is not None:
                    payload["message_thread_id"] = active_thread_id
                send_result = await asyncio.wait_for(
                    runtime.bot.send_message(**payload),
                    timeout=max(1.0, float(runtime.send_timeout_s)),
                )
                _remember_message_id(send_result, message_ids)
                runtime.on_send_auth_success()
                break
            except TypeError as exc:
                if active_thread_id is None or "message_thread_id" not in str(exc):
                    raise
                thread_state["message_thread_id"] = None
                send_result = await asyncio.wait_for(
                    runtime.bot.send_message(
                        chat_id=chat_id,
                        text=payload_text,
                        parse_mode=payload_parse_mode,
                        reply_to_message_id=reply_to_message_id,
                        reply_markup=reply_markup,
                    ),
                    timeout=max(1.0, float(runtime.send_timeout_s)),
                )
                _remember_message_id(send_result, message_ids)
                runtime.on_send_auth_success()
                break
            except Exception as exc:
                if (
                    payload_parse_mode
                    and not formatting_fallback_used
                    and is_formatting_error(exc)
                ):
                    payload_text = chunk
                    payload_parse_mode = None
                    formatting_fallback_used = True
                    continue
                if (
                    active_thread_id is not None
                    and runtime.threadless_retry_allowed(chat_id=chat_id)
                    and is_thread_not_found_error(exc)
                ):
                    logger.warning(
                        "telegram outbound thread not found chat={} chunk={}/{}; retrying without message_thread_id",
                        chat_id,
                        idx,
                        len(chunks),
                    )
                    thread_state["message_thread_id"] = None
                    continue

                if is_auth_failure(exc):
                    runtime.on_send_auth_failure()
                    raise

                logger.error(
                    "telegram outbound failed chat={} chunk={}/{} attempt={}/{} error={}",
                    chat_id,
                    idx,
                    len(chunks),
                    attempt,
                    policy.max_attempts,
                    exc,
                )
                if attempt >= policy.max_attempts or not is_transient_failure(exc):
                    raise

                runtime.signals["send_retry_count"] += 1
                delay_s = retry_after_delay_s(exc)
                if delay_s is None:
                    delay_s = retry_delay_s(policy, attempt)
                else:
                    runtime.signals["send_retry_after_count"] += 1
                if delay_s > 0:
                    await asyncio.sleep(delay_s)
    return len(chunks)


async def send_media_items(
    *,
    runtime: TelegramOutboundRuntime,
    chat_id: str,
    items: list[dict[str, Any]],
    caption_text: str | None,
    outbound_parse_mode: str,
    reply_to_message_id: int | None,
    thread_state: dict[str, int | None],
    reply_markup: Any | None,
    message_ids: list[int],
    media_type_supports_caption: Callable[[str], bool],
) -> int:
    policy = runtime.policy.normalized()
    caption_index: int | None = None
    if caption_text:
        for idx, item in enumerate(items, start=1):
            if media_type_supports_caption(str(item.get("type", "") or "").strip()):
                caption_index = idx
                break

    for idx, item in enumerate(items, start=1):
        sender, payload_key = runtime.resolve_media_sender(runtime.bot, str(item["type"]))
        raw_caption = caption_text if idx == caption_index else None
        if raw_caption:
            caption_payload, caption_parse_mode = runtime.render_outbound_text(
                raw_caption,
                parse_mode=outbound_parse_mode,
            )
        else:
            caption_payload, caption_parse_mode = None, None
        formatting_fallback_used = False

        for attempt in range(1, policy.max_attempts + 1):
            runtime.sync_auth_breaker_signal_transition(
                breaker=runtime.send_auth_breaker,
                key_prefix="send",
            )
            if runtime.send_auth_breaker.is_open:
                raise TelegramCircuitOpenError("telegram auth circuit is open")
            active_thread_id = runtime.normalize_api_message_thread_id(
                chat_id=chat_id,
                message_thread_id=thread_state.get("message_thread_id"),
            )
            try:
                media_payload = await runtime.resolve_outbound_media_payload(item)
                payload: dict[str, Any] = {
                    "chat_id": chat_id,
                    payload_key: media_payload,
                }
                if idx == 1 and reply_to_message_id is not None:
                    payload["reply_to_message_id"] = reply_to_message_id
                if idx == 1 and reply_markup is not None:
                    payload["reply_markup"] = reply_markup
                if active_thread_id is not None:
                    payload["message_thread_id"] = active_thread_id
                if caption_payload is not None:
                    payload["caption"] = caption_payload
                    payload["parse_mode"] = caption_parse_mode
                send_result = await asyncio.wait_for(
                    sender(**payload),
                    timeout=max(1.0, float(runtime.send_timeout_s)),
                )
                _remember_message_id(send_result, message_ids)
                runtime.on_send_auth_success()
                break
            except TypeError as exc:
                if active_thread_id is None or "message_thread_id" not in str(exc):
                    raise
                thread_state["message_thread_id"] = None
                media_payload = await runtime.resolve_outbound_media_payload(item)
                payload = {
                    "chat_id": chat_id,
                    payload_key: media_payload,
                }
                if idx == 1 and reply_to_message_id is not None:
                    payload["reply_to_message_id"] = reply_to_message_id
                if idx == 1 and reply_markup is not None:
                    payload["reply_markup"] = reply_markup
                if caption_payload is not None:
                    payload["caption"] = caption_payload
                    payload["parse_mode"] = caption_parse_mode
                send_result = await asyncio.wait_for(
                    sender(**payload),
                    timeout=max(1.0, float(runtime.send_timeout_s)),
                )
                _remember_message_id(send_result, message_ids)
                runtime.on_send_auth_success()
                break
            except Exception as exc:
                if (
                    caption_parse_mode
                    and not formatting_fallback_used
                    and is_formatting_error(exc)
                ):
                    caption_payload = raw_caption
                    caption_parse_mode = None
                    formatting_fallback_used = True
                    continue
                if (
                    active_thread_id is not None
                    and runtime.threadless_retry_allowed(chat_id=chat_id)
                    and is_thread_not_found_error(exc)
                ):
                    logger.warning(
                        "telegram outbound media thread not found chat={} media={}/{} type={}; retrying without message_thread_id",
                        chat_id,
                        idx,
                        len(items),
                        item["type"],
                    )
                    thread_state["message_thread_id"] = None
                    continue

                if is_auth_failure(exc):
                    runtime.on_send_auth_failure()
                    raise

                logger.error(
                    "telegram outbound media failed chat={} media={}/{} type={} attempt={}/{} error={}",
                    chat_id,
                    idx,
                    len(items),
                    item["type"],
                    attempt,
                    policy.max_attempts,
                    exc,
                )
                if attempt >= policy.max_attempts or not is_transient_failure(exc):
                    raise

                runtime.signals["send_retry_count"] += 1
                delay_s = retry_after_delay_s(exc)
                if delay_s is None:
                    delay_s = retry_delay_s(policy, attempt)
                else:
                    runtime.signals["send_retry_after_count"] += 1
                if delay_s > 0:
                    await asyncio.sleep(delay_s)
    return len(items)
