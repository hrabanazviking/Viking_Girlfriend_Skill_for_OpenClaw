"""
Runestone — Tamper-Evident Audit Log
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Runes were carved into stone to record deeds that must not be forgotten
or denied. The Runestone log is ClawLite's append-only forensic record.

Each line is a JSON object (JSONL). Records are chained with a rolling
SHA-256 hash — each record includes the digest of the record before it,
so any deletion or modification of an earlier entry breaks the chain and
becomes detectable on the next read.

What is recorded:
  - BLOCK / WARN events from the Ægishjálmr injection guard
  - High-priority findings from Huginn & Muninn's raven counsel
  - Critical autonomy events (consecutive failures, recovery actions)
  - Self-evolution proposals (Þing votes and decisions)

The log is append-only. There is no delete. There is no overwrite.
Odin remembers all.

Architecture:
  RunestoneLog — append-only JSONL writer with SHA-256 chain
  set_runestone(log) — register a global RunestoneLog for injection_guard

Tamper detection:
  RunestoneLog.verify_chain() → (is_intact, first_broken_line)
  Returns True, -1 if intact; False, N if the chain breaks at line N.
"""
from __future__ import annotations

import hashlib
import json
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

# ── Constants ──────────────────────────────────────────────────────────────────

_GENESIS_PREV = "0" * 64   # All-zero hash for the first record
_MAX_FILE_BYTES = 10 * 1024 * 1024   # rotate at 10 MB
_RUNE_EVENT = "ᚱ"   # Raidho — the journey; each record is a step


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Record dataclass ───────────────────────────────────────────────────────────

@dataclass(slots=True)
class RunestoneRecord:
    """
    A single immutable entry in the Runestone log.

    Fields:
        seq       — monotone sequence number (0-based within the file)
        timestamp — UTC ISO-8601
        kind      — event category (e.g. "injection_block", "raven_high")
        source    — originating component or channel
        details   — arbitrary key→value payload
        prev_hash — SHA-256 of the raw JSON of the previous record
        this_hash — SHA-256 of this record's JSON (without this_hash field)
    """
    seq: int
    timestamp: str
    kind: str
    source: str
    details: dict[str, Any]
    prev_hash: str
    this_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "seq": self.seq,
            "ts": self.timestamp,
            "kind": self.kind,
            "source": self.source,
            "details": self.details,
            "prev": self.prev_hash,
            "hash": self.this_hash,
        }


def _hash_record(d: dict[str, Any]) -> str:
    """SHA-256 of a stable JSON serialization (no 'hash' field included)."""
    payload = {k: v for k, v in d.items() if k != "hash"}
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode()).hexdigest()


# ── RunestoneLog ───────────────────────────────────────────────────────────────

class RunestoneLog:
    """
    Append-only tamper-evident JSONL audit log.

    Thread-safe. All writes go through a threading.Lock.
    Files rotate when they exceed _MAX_FILE_BYTES — the rotated file is
    renamed with a .N suffix and a fresh chain starts in the active file.

    Usage:
        log = RunestoneLog(path="/var/clawlite/runestone.jsonl")
        log.append(kind="injection_block", source="telegram",
                   details={"threats": ["system_override"], "preview": "..."})
    """

    def __init__(self, path: str | Path, *, max_file_bytes: int = _MAX_FILE_BYTES) -> None:
        self._path = Path(path).expanduser()
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._max_file_bytes = max(4096, int(max_file_bytes))
        self._lock = threading.Lock()
        self._seq = 0
        self._prev_hash = _GENESIS_PREV
        # Optional post-append callback (used by Gjallarhorn)
        self._on_append: Callable[[RunestoneRecord], None] | None = None

        # Restore seq and prev_hash from existing file
        self._restore_state()

    def set_on_append(self, cb: Callable[[RunestoneRecord], None]) -> None:
        """Register a callback invoked after every successful append."""
        self._on_append = cb

    def _restore_state(self) -> None:
        """Read existing file to restore seq counter and prev_hash chain."""
        if not self._path.exists():
            return
        try:
            lines = self._path.read_text(encoding="utf-8").splitlines()
            for raw in reversed(lines):
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    rec = json.loads(raw)
                    self._seq = int(rec.get("seq", 0)) + 1
                    self._prev_hash = str(rec.get("hash", _GENESIS_PREV))
                    return
                except Exception:
                    continue
        except Exception:
            pass

    def append(
        self,
        *,
        kind: str,
        source: str,
        details: dict[str, Any] | None = None,
    ) -> RunestoneRecord:
        """
        Carve a new rune into the stone — append one record to the log.

        Thread-safe. Returns the written RunestoneRecord.
        """
        with self._lock:
            rec_dict: dict[str, Any] = {
                "seq": self._seq,
                "ts": _utc_now(),
                "kind": str(kind or "event"),
                "source": str(source or "unknown"),
                "details": dict(details or {}),
                "prev": self._prev_hash,
            }
            this_hash = _hash_record(rec_dict)
            rec_dict["hash"] = this_hash

            record = RunestoneRecord(
                seq=rec_dict["seq"],
                timestamp=rec_dict["ts"],
                kind=rec_dict["kind"],
                source=rec_dict["source"],
                details=rec_dict["details"],
                prev_hash=rec_dict["prev"],
                this_hash=this_hash,
            )

            self._write_line(json.dumps(rec_dict, ensure_ascii=False, sort_keys=False))
            self._seq += 1
            self._prev_hash = this_hash
        # Fire callback outside the lock — must not block the writer
        if self._on_append is not None:
            try:
                self._on_append(record)
            except Exception:
                pass
        return record

    def _write_line(self, line: str) -> None:
        """Write a single JSONL line, rotating if needed."""
        try:
            if self._path.exists() and self._path.stat().st_size >= self._max_file_bytes:
                self._rotate()
            with self._path.open("a", encoding="utf-8") as fh:
                fh.write(line + "\n")
        except Exception:
            pass  # Runestone never crashes the caller

    def _rotate(self) -> None:
        """Rename active log to .1 (evicting older .1 if present)."""
        rotated = self._path.with_suffix(self._path.suffix + ".1")
        try:
            if rotated.exists():
                rotated.unlink()
            self._path.rename(rotated)
        except Exception:
            pass
        # Fresh chain in the new file
        self._prev_hash = _GENESIS_PREV

    def tail(self, n: int = 20) -> list[dict[str, Any]]:
        """Return the last N records as dicts."""
        if not self._path.exists():
            return []
        try:
            lines = self._path.read_text(encoding="utf-8").splitlines()
            records: list[dict[str, Any]] = []
            for raw in lines:
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    records.append(json.loads(raw))
                except Exception:
                    continue
            return records[-n:]
        except Exception:
            return []

    def verify_chain(self) -> tuple[bool, int]:
        """
        Verify the SHA-256 chain integrity of the active log file.

        Returns:
            (True, -1)  — chain is intact
            (False, N)  — chain broken at 0-based line N
        """
        if not self._path.exists():
            return True, -1
        try:
            lines = [l.strip() for l in self._path.read_text(encoding="utf-8").splitlines() if l.strip()]
        except Exception:
            return False, 0

        prev = _GENESIS_PREV
        for i, raw in enumerate(lines):
            try:
                rec = json.loads(raw)
            except Exception:
                return False, i
            if rec.get("prev") != prev:
                return False, i
            expected = _hash_record(rec)
            if rec.get("hash") != expected:
                return False, i
            prev = rec["hash"]
        return True, -1


# ── Global hook for injection_guard ───────────────────────────────────────────

_runestone: RunestoneLog | None = None


def set_runestone(log: RunestoneLog) -> None:
    """
    Register the global RunestoneLog for injection_guard to write to.

    Call once at startup after creating a RunestoneLog:
        from clawlite.core.runestone import RunestoneLog, set_runestone
        set_runestone(RunestoneLog("/var/clawlite/runestone.jsonl"))
    """
    global _runestone
    _runestone = log


def audit(
    *,
    kind: str,
    source: str,
    details: dict[str, Any] | None = None,
) -> None:
    """
    Write one record to the global RunestoneLog if one is registered.
    Safe to call even when no log is registered — it is a no-op.
    """
    if _runestone is not None:
        try:
            _runestone.append(kind=kind, source=source, details=details)
        except Exception:
            pass


__all__ = [
    "RunestoneLog",
    "RunestoneRecord",
    "audit",
    "set_runestone",
]
