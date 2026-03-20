from __future__ import annotations

import datetime as dt
import json
import os
import secrets
from collections import deque
from pathlib import Path
from typing import Any


class TelegramUpdateDedupeState:
    def __init__(self, *, state_path: Path, limit: int) -> None:
        self.state_path = state_path
        self.limit = max(1, int(limit or 1))
        self.keys: set[str] = set()
        self.order: deque[str] = deque()

    @staticmethod
    def _normalize_key(raw: Any) -> str:
        key = str(raw or "").strip()
        if key.startswith("polling:") or key.startswith("webhook:"):
            _, _, normalized = key.partition(":")
            key = normalized.strip()
        return key

    def payload(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "updated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "keys": list(self.order),
        }

    def _trim(self) -> None:
        while len(self.order) > self.limit:
            oldest = self.order.popleft()
            self.keys.discard(oldest)

    def load(self) -> None:
        path = self.state_path
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            return
        if not path.exists():
            return

        data = json.loads(path.read_text(encoding="utf-8"))
        keys_raw = data.get("keys", []) if isinstance(data, dict) else []
        if not isinstance(keys_raw, list):
            return

        normalized: deque[str] = deque(maxlen=self.limit)
        seen_local: set[str] = set()
        for item in keys_raw:
            key = self._normalize_key(item)
            if not key or key in seen_local:
                continue
            seen_local.add(key)
            normalized.append(key)

        self.order = deque(normalized)
        self.keys = set(self.order)

    def refresh(self) -> bool:
        path = self.state_path
        if not path.exists():
            return False

        data = json.loads(path.read_text(encoding="utf-8"))
        keys_raw = data.get("keys", []) if isinstance(data, dict) else []
        if not isinstance(keys_raw, list):
            return False

        changed = False
        for item in keys_raw:
            key = self._normalize_key(item)
            if not key or key in self.keys:
                continue
            self.keys.add(key)
            self.order.append(key)
            changed = True

        if changed:
            self._trim()
        return changed

    def contains(self, dedupe_key: str) -> bool:
        key = str(dedupe_key or "").strip()
        return bool(key) and key in self.keys

    def commit(self, dedupe_key: str) -> bool:
        key = str(dedupe_key or "").strip()
        if not key or key in self.keys:
            return False
        self.keys.add(key)
        self.order.append(key)
        self._trim()
        return True

    def persist(self) -> None:
        path = self.state_path
        tmp_path = path.with_suffix(f"{path.suffix}.tmp.{secrets.token_hex(4)}")
        dir_fd: int | None = None
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            encoded_payload = json.dumps(self.payload()).encode("utf-8")
            with tmp_path.open("wb") as handle:
                handle.write(encoded_payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(tmp_path, path)
            try:
                open_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                dir_fd = os.open(str(path.parent), open_flags)
                os.fsync(dir_fd)
            except OSError:
                pass
        except Exception:
            try:
                if tmp_path.exists():
                    tmp_path.unlink()
            except OSError:
                pass
            raise
        finally:
            if dir_fd is not None:
                try:
                    os.close(dir_fd)
                except OSError:
                    pass
