from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True, frozen=True)
class TelegramInboundMessageUpdate:
    message: Any
    update_kind: str
    is_edit: bool


@dataclass(slots=True, frozen=True)
class TelegramInboundMessageContext:
    base_text: str
    chat_id: str
    thread_id: int | None
    chat_type: str
    user_id: str
    username: str
    first_name: str
    message_id: int


def select_inbound_message(item: Any) -> TelegramInboundMessageUpdate | None:
    for field_name, is_edit in (
        ("message", False),
        ("edited_message", True),
        ("business_message", False),
        ("edited_business_message", True),
        ("channel_post", False),
        ("edited_channel_post", True),
    ):
        message = getattr(item, field_name, None)
        if message is not None:
            return TelegramInboundMessageUpdate(
                message=message,
                update_kind=field_name,
                is_edit=is_edit,
            )

    message = getattr(item, "effective_message", None)
    if message is None:
        return None
    is_edit = bool(
        getattr(item, "edited_message", None)
        or getattr(item, "edited_business_message", None)
        or getattr(item, "edited_channel_post", None)
    )
    return TelegramInboundMessageUpdate(
        message=message,
        update_kind="effective_message",
        is_edit=is_edit,
    )


def extract_inbound_message_context(
    message: Any,
    *,
    coerce_thread_id,
) -> TelegramInboundMessageContext:
    base_text = (
        getattr(message, "text", "") or getattr(message, "caption", "") or ""
    ).strip()
    chat_id = str(getattr(message, "chat_id", "") or "")
    thread_id = coerce_thread_id(getattr(message, "message_thread_id", None))
    user = getattr(message, "from_user", None)
    chat = getattr(message, "chat", None)
    chat_type = str(getattr(chat, "type", "") or "")
    user_id = str(getattr(user, "id", "") or chat_id)
    username = str(getattr(user, "username", "") or "").strip()
    first_name = str(getattr(user, "first_name", "") or "").strip()
    try:
        message_id = int(getattr(message, "message_id", 0) or 0)
    except (TypeError, ValueError):
        message_id = 0
    return TelegramInboundMessageContext(
        base_text=base_text,
        chat_id=chat_id,
        thread_id=thread_id,
        chat_type=chat_type,
        user_id=user_id,
        username=username,
        first_name=first_name,
        message_id=message_id,
    )
