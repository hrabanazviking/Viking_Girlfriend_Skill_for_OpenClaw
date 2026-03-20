from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True, frozen=True)
class TelegramCallbackQueryPayload:
    query_id: str
    callback_data: str
    callback_text: str
    chat_id: str
    chat_type: str
    user_id: str
    username: str
    thread_id: int | None
    message_id: int
    chat_instance: str
    update_id: int


@dataclass(slots=True, frozen=True)
class TelegramMessageReactionPayload:
    chat_id: str
    chat_type: str
    user_id: str
    username: str
    thread_id: int | None
    message_id: int
    is_bot: bool
    old_reaction: Any
    new_reaction: Any
    update_id: int


def extract_callback_query_payload(
    item: Any,
    *,
    coerce_thread_id,
) -> TelegramCallbackQueryPayload | None:
    callback_query = getattr(item, "callback_query", None)
    if callback_query is None:
        return None
    callback_query_id = str(getattr(callback_query, "id", "") or "")
    callback_data = str(getattr(callback_query, "data", "") or "")
    callback_text = callback_data.strip() or "[telegram callback_query]"
    callback_message = getattr(callback_query, "message", None)
    callback_message_chat = getattr(callback_message, "chat", None)
    callback_chat_type = str(getattr(callback_message_chat, "type", "") or "")
    callback_chat_id = str(
        getattr(callback_message, "chat_id", "")
        or getattr(callback_message_chat, "id", "")
        or ""
    )
    callback_from_user = getattr(callback_query, "from_user", None)
    callback_user_id = str(getattr(callback_from_user, "id", "") or callback_chat_id)
    callback_username = str(getattr(callback_from_user, "username", "") or "").strip()
    callback_thread_id = coerce_thread_id(
        getattr(callback_message, "message_thread_id", None)
    )
    try:
        callback_message_id = int(getattr(callback_message, "message_id", 0) or 0)
    except (TypeError, ValueError):
        callback_message_id = 0
    return TelegramCallbackQueryPayload(
        query_id=callback_query_id,
        callback_data=callback_data,
        callback_text=callback_text,
        chat_id=callback_chat_id,
        chat_type=callback_chat_type,
        user_id=callback_user_id,
        username=callback_username,
        thread_id=callback_thread_id,
        message_id=callback_message_id,
        chat_instance=str(getattr(callback_query, "chat_instance", "") or ""),
        update_id=int(getattr(item, "update_id", 0) or 0),
    )


def callback_query_metadata(
    *,
    payload: TelegramCallbackQueryPayload,
    callback_data: str,
    callback_signed: bool,
) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "channel": "telegram",
        "chat_id": payload.chat_id,
        "chat_type": payload.chat_type,
        "is_group": payload.chat_type != "private",
        "update_kind": "callback_query",
        "is_callback_query": True,
        "callback_query_id": payload.query_id,
        "callback_data": callback_data,
        "callback_signed": callback_signed,
        "callback_chat_instance": payload.chat_instance,
        "user_id": int(payload.user_id or 0),
        "username": payload.username,
        "text": callback_data.strip() or "[telegram callback_query]",
        "update_id": payload.update_id,
    }
    if payload.message_id > 0:
        metadata["message_id"] = payload.message_id
    if payload.thread_id is not None:
        metadata["message_thread_id"] = payload.thread_id
    return metadata


def extract_message_reaction_payload(
    item: Any,
    *,
    coerce_thread_id,
) -> TelegramMessageReactionPayload | None:
    message_reaction = getattr(item, "message_reaction", None)
    if message_reaction is None:
        return None
    reaction_chat = getattr(message_reaction, "chat", None)
    reaction_chat_type = str(getattr(reaction_chat, "type", "") or "")
    chat_id = str(
        getattr(message_reaction, "chat_id", "")
        or getattr(reaction_chat, "id", "")
        or ""
    )
    try:
        message_id = int(getattr(message_reaction, "message_id", 0) or 0)
    except (TypeError, ValueError):
        message_id = 0
    reactor = getattr(message_reaction, "user", None) or getattr(
        message_reaction, "from_user", None
    )
    reactor_user_id = str(getattr(reactor, "id", "") or chat_id)
    reactor_username = str(getattr(reactor, "username", "") or "").strip()
    reaction_thread_id = coerce_thread_id(
        getattr(message_reaction, "message_thread_id", None)
    )
    return TelegramMessageReactionPayload(
        chat_id=chat_id,
        chat_type=reaction_chat_type,
        user_id=reactor_user_id,
        username=reactor_username,
        thread_id=reaction_thread_id,
        message_id=message_id,
        is_bot=bool(getattr(reactor, "is_bot", False)),
        old_reaction=getattr(message_reaction, "old_reaction", None),
        new_reaction=getattr(message_reaction, "new_reaction", None),
        update_id=int(getattr(item, "update_id", 0) or 0),
    )


def message_reaction_metadata(
    *,
    payload: TelegramMessageReactionPayload,
    reaction_added: list[str],
    reaction_new: list[str],
    reaction_old: list[str],
) -> tuple[str, dict[str, Any]]:
    reaction_marker = " ".join(reaction_added)
    reaction_text = f"[telegram reaction] {reaction_marker}".strip()
    metadata: dict[str, Any] = {
        "channel": "telegram",
        "chat_id": payload.chat_id,
        "chat_type": payload.chat_type,
        "is_group": payload.chat_type != "private",
        "update_kind": "message_reaction",
        "is_message_reaction": True,
        "message_id": payload.message_id,
        "user_id": payload.user_id,
        "username": payload.username,
        "reaction_added": reaction_added,
        "reaction_new": reaction_new,
        "reaction_old": reaction_old,
        "update_id": payload.update_id,
        "text": reaction_text,
    }
    if payload.thread_id is not None:
        metadata["message_thread_id"] = payload.thread_id
    return reaction_text, metadata
