from __future__ import annotations

from typing import Any, Callable

from clawlite.channels.telegram_offset_store import TelegramOffsetStore


class TelegramOffsetRuntime:
    def __init__(self, *, offset_store: TelegramOffsetStore) -> None:
        self.offset_store = offset_store
        self.next_offset = 0

    def reset(self) -> None:
        self.next_offset = 0

    def apply_snapshot(self, snapshot: Any) -> tuple[int, bool]:
        previous_offset = max(0, int(self.next_offset or 0))
        next_offset = max(0, int(getattr(snapshot, "next_offset", 0) or 0))
        self.next_offset = next_offset
        return next_offset, next_offset > previous_offset

    def load(self) -> int:
        snapshot = self.offset_store.refresh_from_disk()
        next_offset, _advanced = self.apply_snapshot(snapshot)
        return next_offset

    def sync_next_offset(self, next_offset: int) -> tuple[Any, int, bool]:
        snapshot = self.offset_store.sync_next_offset(next_offset)
        resolved_offset, advanced = self.apply_snapshot(snapshot)
        return snapshot, resolved_offset, advanced

    def persist_operation(self, callback: Callable[[], Any]) -> tuple[Any, int, bool]:
        snapshot = callback()
        next_offset, advanced = self.apply_snapshot(snapshot)
        return snapshot, next_offset, advanced

    def begin(self, update_id: int) -> tuple[Any, int, bool]:
        return self.persist_operation(lambda: self.offset_store.begin(update_id))

    def complete(
        self,
        update_id: int,
        *,
        tracked_pending: bool = True,
    ) -> tuple[Any, int, bool]:
        return self.persist_operation(
            lambda: self.offset_store.mark_completed(
                update_id,
                tracked_pending=tracked_pending,
            )
        )

    def force_commit(self, update_id: int) -> tuple[Any, int, bool]:
        return self.persist_operation(lambda: self.offset_store.force_commit(update_id))

    def is_stale(self, update_id: int) -> bool:
        return self.offset_store.is_safe_committed(update_id)

    def should_begin_webhook_tracking(self, update_id: int) -> bool:
        return update_id == self.next_offset or self.offset_store.is_pending(update_id)

    def webhook_completion_policy(self, update_id: int) -> tuple[bool, bool]:
        return True, bool(
            self.offset_store.is_pending(update_id) or update_id == self.next_offset
        )
