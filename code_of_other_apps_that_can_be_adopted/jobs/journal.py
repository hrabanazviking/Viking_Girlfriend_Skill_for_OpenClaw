"""SQLite persistence journal for JobQueue (mirrors BusJournal pattern)."""
from __future__ import annotations

import json
import sqlite3
import threading
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from clawlite.jobs.queue import Job

_SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    kind TEXT NOT NULL,
    payload TEXT NOT NULL,
    priority INTEGER NOT NULL DEFAULT 5,
    session_id TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'queued',
    result TEXT NOT NULL DEFAULT '',
    error TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT '',
    started_at TEXT NOT NULL DEFAULT '',
    finished_at TEXT NOT NULL DEFAULT '',
    max_retries INTEGER NOT NULL DEFAULT 0,
    retry_count INTEGER NOT NULL DEFAULT 0
);
"""


class JobJournal:
    """Append/update SQLite journal for JobQueue persistence."""

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)
        self._conn: sqlite3.Connection | None = None
        self._lock = threading.Lock()

    def open(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self._path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    def close(self) -> None:
        if self._conn is not None:
            try:
                self._conn.close()
            except Exception:
                pass
            self._conn = None

    def save(self, job: "Job") -> None:
        if self._conn is None:
            return
        with self._lock:
            self._conn.execute(
                """INSERT INTO jobs (id, kind, payload, priority, session_id, status, result,
                   error, created_at, started_at, finished_at, max_retries, retry_count)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(id) DO UPDATE SET
                   status=excluded.status, result=excluded.result, error=excluded.error,
                   started_at=excluded.started_at, finished_at=excluded.finished_at,
                   retry_count=excluded.retry_count""",
                (
                    job.id, job.kind, json.dumps(job.payload), job.priority,
                    job.session_id, job.status, job.result, job.error,
                    job.created_at, job.started_at, job.finished_at,
                    job.max_retries, job.retry_count,
                ),
            )
            self._conn.commit()

    def load_queued(self) -> list["Job"]:
        """Return all jobs in 'queued' status (for restart recovery)."""
        from clawlite.jobs.queue import Job
        if self._conn is None:
            return []
        with self._lock:
            rows = self._conn.execute(
                "SELECT * FROM jobs WHERE status='queued' ORDER BY priority DESC, created_at ASC"
            ).fetchall()
        result: list[Job] = []
        for row in rows:
            try:
                j = Job(
                    id=row["id"], kind=row["kind"],
                    payload=json.loads(row["payload"]),
                    priority=row["priority"], session_id=row["session_id"],
                    status=row["status"], result=row["result"], error=row["error"],
                    created_at=row["created_at"], started_at=row["started_at"],
                    finished_at=row["finished_at"], max_retries=row["max_retries"],
                    retry_count=row["retry_count"],
                )
                result.append(j)
            except Exception:
                pass
        return result

    def load_all(self) -> list["Job"]:
        from clawlite.jobs.queue import Job
        if self._conn is None:
            return []
        with self._lock:
            rows = self._conn.execute(
                "SELECT * FROM jobs ORDER BY created_at DESC"
            ).fetchall()
        result = []
        for row in rows:
            try:
                result.append(Job(
                    id=row["id"], kind=row["kind"],
                    payload=json.loads(row["payload"]),
                    priority=row["priority"], session_id=row["session_id"],
                    status=row["status"], result=row["result"], error=row["error"],
                    created_at=row["created_at"], started_at=row["started_at"],
                    finished_at=row["finished_at"], max_retries=row["max_retries"],
                    retry_count=row["retry_count"],
                ))
            except Exception:
                pass
        return result
