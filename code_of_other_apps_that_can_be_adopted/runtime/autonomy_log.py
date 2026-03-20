from __future__ import annotations

import json
import os
import threading
import uuid
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(nested) for key, nested in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


class AutonomyLog:
    def __init__(self, *, path: str | Path, max_entries: int = 200) -> None:
        self.path = Path(path)
        self.max_entries = max(1, int(max_entries or 1))
        self._lock = threading.Lock()
        self._events: deque[dict[str, Any]] = deque(maxlen=self.max_entries)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._load()

    @staticmethod
    def _flush_and_fsync(handle: Any) -> None:
        handle.flush()
        try:
            os.fsync(handle.fileno())
        except Exception:
            pass

    def _payload(self) -> dict[str, Any]:
        return {
            "version": 1,
            "events": list(self._events),
        }

    def _atomic_write(self) -> None:
        temp_path = self.path.parent / f".{self.path.name}.{uuid.uuid4().hex}.tmp"
        try:
            with temp_path.open("w", encoding="utf-8") as fh:
                json.dump(self._payload(), fh, ensure_ascii=False, indent=2)
                fh.write("\n")
                self._flush_and_fsync(fh)
            os.replace(temp_path, self.path)
            dir_fd = -1
            try:
                dir_fd = os.open(str(self.path.parent), os.O_RDONLY)
                os.fsync(dir_fd)
            except Exception:
                pass
            finally:
                if dir_fd >= 0:
                    try:
                        os.close(dir_fd)
                    except Exception:
                        pass
        finally:
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except Exception:
                    pass

    def _load(self) -> None:
        if not self.path.exists():
            self._atomic_write()
            return
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            self._events.clear()
            self._atomic_write()
            return
        rows = payload.get("events", []) if isinstance(payload, dict) else []
        self._events.clear()
        if isinstance(rows, list):
            for row in rows[-self.max_entries :]:
                if isinstance(row, dict):
                    self._events.append(dict(row))

    def record(
        self,
        *,
        source: str,
        action: str,
        status: str,
        summary: str = "",
        metadata: dict[str, Any] | None = None,
        event_at: str = "",
    ) -> dict[str, Any]:
        entry = {
            "event_id": uuid.uuid4().hex[:12],
            "at": str(event_at or datetime.now(timezone.utc).isoformat(timespec="seconds")),
            "source": str(source or "").strip() or "autonomy",
            "action": str(action or "").strip() or "unknown",
            "status": str(status or "").strip() or "unknown",
            "summary": str(summary or "").strip(),
            "metadata": _json_safe(dict(metadata or {})),
        }
        with self._lock:
            self._events.append(entry)
            self._atomic_write()
        return dict(entry)

    def snapshot(self, *, limit: int = 20) -> dict[str, Any]:
        bounded_limit = max(1, int(limit or 1))
        with self._lock:
            rows = list(self._events)
        by_source: dict[str, int] = {}
        by_action: dict[str, int] = {}
        by_status: dict[str, int] = {}
        for row in rows:
            source = str(row.get("source", "") or "").strip() or "autonomy"
            action = str(row.get("action", "") or "").strip() or "unknown"
            status = str(row.get("status", "") or "").strip() or "unknown"
            by_source[source] = by_source.get(source, 0) + 1
            by_action[action] = by_action.get(action, 0) + 1
            by_status[status] = by_status.get(status, 0) + 1
        return {
            "enabled": True,
            "path": str(self.path),
            "max_entries": self.max_entries,
            "total": len(rows),
            "last_event_at": str(rows[-1].get("at", "") or "") if rows else "",
            "counts": {
                "by_source": dict(sorted(by_source.items())),
                "by_action": dict(sorted(by_action.items())),
                "by_status": dict(sorted(by_status.items())),
            },
            "recent": rows[-bounded_limit:],
        }
