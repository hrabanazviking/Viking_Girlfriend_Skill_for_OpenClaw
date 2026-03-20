from __future__ import annotations

from typing import Any, Protocol

from clawlite.tools.base import Tool, ToolContext


class MessageAPI(Protocol):
    async def send(
        self,
        *,
        channel: str,
        target: str,
        text: str,
        metadata: dict[str, Any] | None = None,
    ) -> str: ...


class MessageTool(Tool):
    name = "message"
    description = "Send proactive message to a channel target."
    _CHANNEL_CAPABILITIES: dict[str, dict[str, object]] = {
        "telegram": {
            "actions": {"send", "reply", "edit", "delete", "react", "create_topic"},
            "buttons": True,
            "media": True,
        },
        "discord": {
            "actions": {"send"},
            "buttons": True,
            "media": False,
        },
    }
    TELEGRAM_MEDIA_TYPES = {
        "animation",
        "audio",
        "document",
        "photo",
        "sticker",
        "video",
        "video_note",
        "voice",
    }

    def __init__(self, api: MessageAPI) -> None:
        self.api = api

    @classmethod
    def channel_capabilities(cls, channel: str) -> dict[str, object]:
        normalized = str(channel or "").strip().lower()
        configured = cls._CHANNEL_CAPABILITIES.get(normalized)
        if configured is None:
            return {
                "actions": ["send"],
                "buttons": False,
                "media": False,
            }
        return {
            "actions": sorted(str(item) for item in configured.get("actions", set())),
            "buttons": bool(configured.get("buttons", False)),
            "media": bool(configured.get("media", False)),
        }

    def args_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "channel": {"type": "string"},
                "target": {"type": "string"},
                "text": {"type": "string"},
                "action": {
                    "type": "string",
                    "enum": ["send", "reply", "edit", "delete", "react", "create_topic"],
                    "default": "send",
                },
                "message_id": {"type": "integer"},
                "emoji": {"type": "string"},
                "reply_to_message_id": {"type": "integer"},
                "topic_name": {"type": "string"},
                "topic_icon_color": {"type": "integer"},
                "topic_icon_custom_emoji_id": {"type": "string"},
                "metadata": {"type": "object"},
                "media": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": sorted(self.TELEGRAM_MEDIA_TYPES),
                            },
                            "file_id": {"type": "string"},
                            "url": {"type": "string"},
                            "path": {"type": "string"},
                            "filename": {"type": "string"},
                        },
                        "required": ["type"],
                    },
                },
                "buttons": {
                    "type": "array",
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "text": {"type": "string"},
                                "callback_data": {"type": "string"},
                                "url": {"type": "string"},
                            },
                        },
                    },
                },
            },
            "required": ["channel", "target"],
        }

    @staticmethod
    def _coerce_int(value: Any) -> int | None:
        if value is None:
            return None
        try:
            out = int(value)
        except (TypeError, ValueError):
            return None
        return out

    @staticmethod
    def _validate_buttons(buttons: Any) -> list[list[dict[str, str]]]:
        if not isinstance(buttons, list):
            raise ValueError("buttons must be a list of rows")
        normalized_rows: list[list[dict[str, str]]] = []
        for row in buttons:
            if not isinstance(row, list):
                raise ValueError("buttons rows must be lists")
            normalized_row: list[dict[str, str]] = []
            for button in row:
                if not isinstance(button, dict):
                    raise ValueError("each button must be an object")
                text = str(button.get("text", "")).strip()
                if not text:
                    raise ValueError("each button must include non-empty text")

                has_callback = "callback_data" in button and str(button.get("callback_data", "")).strip() != ""
                has_url = "url" in button and str(button.get("url", "")).strip() != ""
                if has_callback == has_url:
                    raise ValueError("each button must include exactly one of callback_data or url")

                normalized_button: dict[str, str] = {"text": text}
                if has_callback:
                    normalized_button["callback_data"] = str(button.get("callback_data", "")).strip()
                if has_url:
                    normalized_button["url"] = str(button.get("url", "")).strip()
                normalized_row.append(normalized_button)
            normalized_rows.append(normalized_row)
        return normalized_rows

    @staticmethod
    def _discord_components_from_buttons(buttons: list[list[dict[str, str]]]) -> list[dict[str, Any]]:
        components: list[dict[str, Any]] = []
        for row in buttons:
            discord_row: dict[str, Any] = {"type": 1, "components": []}
            for button in row:
                entry: dict[str, Any] = {
                    "type": 2,
                    "label": str(button.get("text", "") or "")[:80],
                }
                callback_data = str(button.get("callback_data", "") or "").strip()
                url = str(button.get("url", "") or "").strip()
                if callback_data:
                    entry["style"] = 1
                    entry["custom_id"] = callback_data[:100]
                elif url:
                    entry["style"] = 5
                    entry["url"] = url
                discord_row["components"].append(entry)
            if discord_row["components"]:
                components.append(discord_row)
        return components

    @classmethod
    def _validate_media(cls, media: Any) -> list[dict[str, Any]]:
        if not isinstance(media, list):
            raise ValueError("media must be a list of objects")
        normalized_media: list[dict[str, Any]] = []
        for index, item in enumerate(media, start=1):
            if not isinstance(item, dict):
                raise ValueError("media items must be objects")
            media_type = str(item.get("type", "") or "").strip().lower()
            if media_type not in cls.TELEGRAM_MEDIA_TYPES:
                raise ValueError(f"media item {index} has invalid type")

            file_id = str(item.get("file_id", "") or "").strip()
            url = str(item.get("url", "") or "").strip()
            path = str(item.get("path", "") or "").strip()
            if not any((file_id, url, path)):
                raise ValueError(f"media item {index} requires file_id, url, or path")

            normalized_item: dict[str, Any] = {"type": media_type}
            if file_id:
                normalized_item["file_id"] = file_id
            if url:
                normalized_item["url"] = url
            if path:
                normalized_item["path"] = path
            filename = str(item.get("filename", "") or "").strip()
            if filename:
                normalized_item["filename"] = filename
            normalized_media.append(normalized_item)
        return normalized_media

    async def run(self, arguments: dict, ctx: ToolContext) -> str:
        channel = str(arguments.get("channel", "")).strip() or ctx.channel
        target = str(arguments.get("target", "")).strip()
        text = str(arguments.get("text", "")).strip()
        action = str(arguments.get("action", "send") or "send").strip().lower()
        allowed_actions = {"send", "reply", "edit", "delete", "react", "create_topic"}
        if action not in allowed_actions:
            raise ValueError("invalid action")
        if not channel or not target:
            raise ValueError("channel and target are required")
        capabilities = self.channel_capabilities(channel)
        if action not in set(capabilities["actions"]):
            supported = ", ".join(capabilities["actions"])
            raise ValueError(f"message action `{action}` is not supported on `{channel}` (supported: {supported})")

        raw_metadata = arguments.get("metadata")
        metadata: dict[str, Any] | None = None
        if raw_metadata is not None:
            if not isinstance(raw_metadata, dict):
                raise ValueError("metadata must be an object")
            metadata = dict(raw_metadata)

        media_items: list[dict[str, Any]] | None = None
        if "media" in arguments and arguments.get("media") is not None:
            if not bool(capabilities["media"]):
                raise ValueError(f"media is not supported on `{channel}`")
            media_items = self._validate_media(arguments.get("media"))

        message_id = self._coerce_int(arguments.get("message_id"))
        reply_to_message_id = self._coerce_int(arguments.get("reply_to_message_id"))
        emoji = str(arguments.get("emoji", "") or "").strip()
        topic_name = str(arguments.get("topic_name", "") or "").strip()
        topic_icon_color = self._coerce_int(arguments.get("topic_icon_color"))
        topic_icon_custom_emoji_id = str(arguments.get("topic_icon_custom_emoji_id", "") or "").strip()

        if action == "send":
            if not text and not media_items:
                raise ValueError("send action requires non-empty text")
        elif action == "reply":
            if not text and not media_items:
                raise ValueError("reply action requires non-empty text")
            metadata_reply_to = self._coerce_int((metadata or {}).get("reply_to_message_id"))
            effective_reply_to = (
                reply_to_message_id
                if reply_to_message_id is not None
                else message_id
                if message_id is not None
                else metadata_reply_to
            )
            if effective_reply_to is None:
                raise ValueError("reply action requires reply_to_message_id or message_id")
            reply_to_message_id = effective_reply_to
        elif action == "edit":
            if not text or message_id is None:
                raise ValueError("edit action requires non-empty text and message_id")
        elif action == "delete":
            if message_id is None:
                raise ValueError("delete action requires message_id")
        elif action == "react":
            if message_id is None or not emoji:
                raise ValueError("react action requires message_id and non-empty emoji")
        elif action == "create_topic":
            if not topic_name:
                raise ValueError("create_topic action requires non-empty topic_name")

        should_bridge_action = action != "send"
        if should_bridge_action:
            metadata = dict(metadata or {})
            metadata["_telegram_action"] = action
            if message_id is not None:
                metadata["_telegram_action_message_id"] = message_id
            if emoji:
                metadata["_telegram_action_emoji"] = emoji
            if topic_name:
                metadata["_telegram_action_topic_name"] = topic_name
            if topic_icon_color is not None:
                metadata["_telegram_action_topic_icon_color"] = topic_icon_color
            if topic_icon_custom_emoji_id:
                metadata["_telegram_action_topic_icon_custom_emoji_id"] = topic_icon_custom_emoji_id
            if action == "reply" and reply_to_message_id is not None:
                metadata["reply_to_message_id"] = reply_to_message_id

        if "buttons" in arguments and arguments.get("buttons") is not None:
            keyboard = self._validate_buttons(arguments.get("buttons"))
            metadata = dict(metadata or {})
            if channel == "telegram":
                metadata["_telegram_inline_keyboard"] = keyboard
            elif channel == "discord":
                metadata["discord_components"] = self._discord_components_from_buttons(keyboard)
            else:
                raise ValueError(f"buttons are not supported on `{channel}`")

        if media_items is not None:
            metadata = dict(metadata or {})
            metadata["_telegram_media"] = media_items

        return await self.api.send(channel=channel, target=target, text=text, metadata=metadata)
