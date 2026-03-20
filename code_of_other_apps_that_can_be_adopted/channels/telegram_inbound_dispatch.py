from __future__ import annotations

import hashlib
from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class TelegramInboundDispatchState:
    signature: str
    msg_key: tuple[str, int]
    command: str
    command_args: str
    is_command: bool
    local_action: str | None


def build_inbound_dispatch_state(
    *,
    text: str,
    chat_id: str,
    message_id: int,
    parse_command,
    handle_commands: bool,
) -> TelegramInboundDispatchState:
    signature = hashlib.sha256(text.encode("utf-8")).hexdigest()
    msg_key = (chat_id, message_id)
    command, command_args = parse_command(text)
    is_command = bool(command)
    local_action: str | None = None
    if handle_commands and command in {"start", "help"}:
        local_action = command
    return TelegramInboundDispatchState(
        signature=signature,
        msg_key=msg_key,
        command=command,
        command_args=command_args,
        is_command=is_command,
        local_action=local_action,
    )
