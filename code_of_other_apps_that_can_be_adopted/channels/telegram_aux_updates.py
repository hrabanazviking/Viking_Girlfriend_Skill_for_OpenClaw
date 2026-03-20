from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True, frozen=True)
class TelegramAuxUpdateEvent:
    signal_key: str
    update_kind: str
    chat_id: str
    chat_type: str
    user_id: str
    username: str
    text: str
    extra_metadata: dict[str, Any]


def extract_aux_update_event(item: Any) -> TelegramAuxUpdateEvent | None:
    deleted_business_messages = getattr(item, "deleted_business_messages", None)
    if deleted_business_messages is not None:
        deleted_chat = getattr(deleted_business_messages, "chat", None)
        deleted_chat_id = str(
            getattr(deleted_business_messages, "chat_id", "")
            or getattr(deleted_chat, "id", "")
            or ""
        )
        deleted_chat_type = str(getattr(deleted_chat, "type", "") or "")
        deleted_message_ids = getattr(deleted_business_messages, "message_ids", None)
        normalized_deleted_ids = (
            [int(item_id) for item_id in deleted_message_ids]
            if isinstance(deleted_message_ids, list)
            else []
        )
        return TelegramAuxUpdateEvent(
            signal_key="deleted_business_messages_received_count",
            update_kind="deleted_business_messages",
            chat_id=deleted_chat_id,
            chat_type=deleted_chat_type,
            user_id=deleted_chat_id,
            username="",
            text="[telegram deleted business messages]",
            extra_metadata={
                "is_deleted_business_messages": True,
                "business_connection_id": str(
                    getattr(deleted_business_messages, "business_connection_id", "") or ""
                ).strip(),
                "message_ids": normalized_deleted_ids,
            },
        )

    message_reaction_count = getattr(item, "message_reaction_count", None)
    if message_reaction_count is not None:
        reaction_count_chat = getattr(message_reaction_count, "chat", None)
        reaction_count_chat_id = str(
            getattr(message_reaction_count, "chat_id", "")
            or getattr(reaction_count_chat, "id", "")
            or ""
        )
        reaction_count_chat_type = str(getattr(reaction_count_chat, "type", "") or "")
        try:
            reaction_count_message_id = int(
                getattr(message_reaction_count, "message_id", 0) or 0
            )
        except (TypeError, ValueError):
            reaction_count_message_id = 0
        return TelegramAuxUpdateEvent(
            signal_key="message_reaction_count_received_count",
            update_kind="message_reaction_count",
            chat_id=reaction_count_chat_id,
            chat_type=reaction_count_chat_type,
            user_id=reaction_count_chat_id,
            username="",
            text="[telegram reaction count]",
            extra_metadata={
                "is_message_reaction_count": True,
                "message_id": reaction_count_message_id,
            },
        )

    chat_boost = getattr(item, "chat_boost", None)
    if chat_boost is not None:
        boost_chat = getattr(chat_boost, "chat", None)
        boost_row = getattr(chat_boost, "boost", None) or chat_boost
        boost_source = getattr(boost_row, "source", None)
        boost_user = getattr(boost_source, "user", None) or getattr(
            boost_source, "from_user", None
        )
        boost_chat_id = str(
            getattr(boost_chat, "id", "") or getattr(chat_boost, "chat_id", "") or ""
        )
        boost_chat_type = str(getattr(boost_chat, "type", "") or "")
        boost_user_id = str(getattr(boost_user, "id", "") or boost_chat_id)
        boost_username = str(getattr(boost_user, "username", "") or "").strip()
        return TelegramAuxUpdateEvent(
            signal_key="chat_boost_received_count",
            update_kind="chat_boost",
            chat_id=boost_chat_id,
            chat_type=boost_chat_type,
            user_id=boost_user_id,
            username=boost_username,
            text="[telegram chat boost]",
            extra_metadata={
                "is_chat_boost": True,
                "boost_id": str(getattr(boost_row, "boost_id", "") or "").strip(),
            },
        )

    removed_chat_boost = getattr(item, "removed_chat_boost", None)
    if removed_chat_boost is not None:
        removed_chat = getattr(removed_chat_boost, "chat", None)
        removed_boost = getattr(removed_chat_boost, "boost", None) or removed_chat_boost
        removed_source = getattr(removed_boost, "source", None)
        removed_user = getattr(removed_source, "user", None) or getattr(
            removed_source, "from_user", None
        )
        removed_chat_id = str(
            getattr(removed_chat, "id", "")
            or getattr(removed_chat_boost, "chat_id", "")
            or ""
        )
        removed_chat_type = str(getattr(removed_chat, "type", "") or "")
        removed_user_id = str(getattr(removed_user, "id", "") or removed_chat_id)
        removed_username = str(getattr(removed_user, "username", "") or "").strip()
        return TelegramAuxUpdateEvent(
            signal_key="removed_chat_boost_received_count",
            update_kind="removed_chat_boost",
            chat_id=removed_chat_id,
            chat_type=removed_chat_type,
            user_id=removed_user_id,
            username=removed_username,
            text="[telegram removed chat boost]",
            extra_metadata={
                "is_removed_chat_boost": True,
                "boost_id": str(getattr(removed_boost, "boost_id", "") or "").strip(),
            },
        )

    purchased_paid_media = getattr(item, "purchased_paid_media", None)
    if purchased_paid_media is not None:
        paid_media_chat = getattr(purchased_paid_media, "chat", None)
        paid_media_user = getattr(purchased_paid_media, "from_user", None) or getattr(
            purchased_paid_media, "user", None
        )
        paid_media_chat_id = str(
            getattr(purchased_paid_media, "chat_id", "")
            or getattr(paid_media_chat, "id", "")
            or ""
        )
        paid_media_chat_type = str(getattr(paid_media_chat, "type", "") or "")
        paid_media_user_id = str(getattr(paid_media_user, "id", "") or paid_media_chat_id)
        paid_media_username = str(getattr(paid_media_user, "username", "") or "").strip()
        return TelegramAuxUpdateEvent(
            signal_key="purchased_paid_media_received_count",
            update_kind="purchased_paid_media",
            chat_id=paid_media_chat_id,
            chat_type=paid_media_chat_type,
            user_id=paid_media_user_id,
            username=paid_media_username,
            text="[telegram purchased paid media]",
            extra_metadata={
                "is_purchased_paid_media": True,
                "payload": str(getattr(purchased_paid_media, "payload", "") or "").strip(),
            },
        )

    return None
