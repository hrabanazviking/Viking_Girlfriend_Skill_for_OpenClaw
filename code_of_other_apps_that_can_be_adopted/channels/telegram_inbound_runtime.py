from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True, frozen=True)
class TelegramInboundEmitPayload:
    session_id: str
    user_id: str
    text: str
    metadata: dict[str, Any]
    chat_id: str
    thread_id: int | None


def media_group_key(message: Any) -> str:
    group_id = str(getattr(message, "media_group_id", "") or "").strip()
    if not group_id:
        return ""
    chat_id = str(getattr(message, "chat_id", "") or "").strip()
    if not chat_id:
        return ""
    return f"{chat_id}:{group_id}"


def merge_media_counts(target: dict[str, int], counts: dict[str, Any]) -> None:
    for media_type, raw_count in dict(counts or {}).items():
        normalized_type = str(media_type or "").strip().lower()
        if not normalized_type:
            continue
        try:
            count = max(0, int(raw_count or 0))
        except (TypeError, ValueError):
            continue
        if count <= 0:
            continue
        target[normalized_type] = int(target.get(normalized_type, 0) or 0) + count


def append_unique_text(rows: list[str], text: str) -> None:
    normalized = str(text or "").strip()
    if not normalized:
        return
    if normalized in rows:
        return
    rows.append(normalized)


def build_inbound_emit_payload(
    *,
    session_id: str,
    user_id: str,
    text: str,
    metadata: dict[str, Any],
    coerce_thread_id,
) -> TelegramInboundEmitPayload:
    return TelegramInboundEmitPayload(
        session_id=str(session_id or ""),
        user_id=str(user_id or ""),
        text=str(text or ""),
        metadata=dict(metadata or {}),
        chat_id=str(metadata.get("chat_id", "") or ""),
        thread_id=coerce_thread_id(metadata.get("message_thread_id")),
    )


def build_media_group_flush_payload(
    *,
    buffer: dict[str, Any],
    build_media_placeholder,
    coerce_thread_id,
) -> TelegramInboundEmitPayload | None:
    texts = list(buffer.get("texts", []))
    counts = dict(buffer.get("media_counts", {}))
    media_types = sorted(counts.keys())
    media_items = list(buffer.get("media_items", []))
    if counts:
        placeholder = build_media_placeholder({"has_media": True, "counts": counts})
        if placeholder and placeholder not in texts:
            texts.insert(0, placeholder)
    combined_text = "\n\n".join(
        text for text in texts if isinstance(text, str) and text.strip()
    ).strip()
    if not combined_text:
        return None
    metadata = dict(buffer.get("metadata", {}))
    metadata["text"] = combined_text
    metadata["media_present"] = bool(counts)
    metadata["media_types"] = media_types
    metadata["media_counts"] = counts
    metadata["media_total_count"] = int(sum(counts.values()))
    metadata["media_items"] = media_items
    metadata["media_group_id"] = str(buffer.get("media_group_id", "") or "")
    metadata["message_ids"] = list(buffer.get("message_ids", []))
    metadata["update_ids"] = list(buffer.get("update_ids", []))
    metadata["media_group_message_count"] = len(metadata["message_ids"])
    return build_inbound_emit_payload(
        session_id=str(buffer.get("session_id", "") or ""),
        user_id=str(buffer.get("user_id", "") or ""),
        text=combined_text,
        metadata=metadata,
        coerce_thread_id=coerce_thread_id,
    )


async def emit_payload_with_typing(
    payload: TelegramInboundEmitPayload,
    *,
    start_typing,
    stop_typing,
    emit,
) -> None:
    if payload.chat_id:
        start_typing(chat_id=payload.chat_id, message_thread_id=payload.thread_id)
    try:
        await emit(
            session_id=payload.session_id,
            user_id=payload.user_id,
            text=payload.text,
            metadata=payload.metadata,
        )
    finally:
        if payload.chat_id:
            await stop_typing(
                chat_id=payload.chat_id,
                message_thread_id=payload.thread_id,
            )
