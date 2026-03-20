from __future__ import annotations

import asyncio
import contextlib
import json
import os
import threading
import uuid
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Awaitable, Callable
from zoneinfo import ZoneInfo

from loguru import logger

from clawlite.scheduler.types import CronJob, CronPayload, CronSchedule
from clawlite.utils.logging import bind_event, setup_logging

try:
    import fcntl
except Exception:  # pragma: no cover
    fcntl = None

try:
    import portalocker
except Exception:  # pragma: no cover
    portalocker = None

try:
    from croniter import croniter
except Exception:  # pragma: no cover
    croniter = None


JobCallback = Callable[[CronJob], Awaitable[str | None]]
DEFAULT_CALLBACK_TIMEOUT_SECONDS = 300.0
DEFAULT_COMPLETED_JOB_RETENTION_SECONDS = 7 * 24 * 60 * 60


class CronService:
    _PATH_LOCKS: dict[str, threading.RLock] = {}
    _PATH_LOCKS_GUARD = threading.Lock()
    _LOOP_SLEEP_MIN_SECONDS = 0.05
    _LOOP_SLEEP_MAX_SECONDS = 5.0
    _OVERDUE_THRESHOLD_SECONDS = 1.0
    _MAX_CLEANUP_WAIT_SECONDS = 5.0

    def __init__(
        self,
        store_path: str | Path | None = None,
        default_timezone: str = "UTC",
        lease_seconds: int = 30,
        callback_timeout_seconds: float = DEFAULT_CALLBACK_TIMEOUT_SECONDS,
        max_concurrent_jobs: int = 2,
        completed_job_retention_seconds: int = DEFAULT_COMPLETED_JOB_RETENTION_SECONDS,
    ) -> None:
        setup_logging()
        self.path = Path(store_path) if store_path else (Path.home() / ".clawlite" / "state" / "cron_jobs.json")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock_path = self.path.with_name(f"{self.path.name}.lock")
        self._jobs: dict[str, CronJob] = {}
        self._task: asyncio.Task[Any] | None = None
        self._on_job: JobCallback | None = None
        self.default_timezone = self._normalize_timezone(default_timezone)
        self._instance_id = uuid.uuid4().hex
        self._lease_seconds = max(5, int(lease_seconds or 30))
        self._callback_timeout_seconds = max(0.1, float(callback_timeout_seconds or DEFAULT_CALLBACK_TIMEOUT_SECONDS))
        self._max_concurrent_jobs = max(1, int(max_concurrent_jobs or 1))
        self._completed_job_retention_seconds = max(0, int(completed_job_retention_seconds or 0))
        self._cleanup_interval_seconds = 60.0
        self._last_cleanup_monotonic = 0.0
        self._running_tasks: dict[str, asyncio.Task[None]] = {}
        self._diag: dict[str, int | str] = {
            "load_attempts": 0,
            "load_success": 0,
            "load_failures": 0,
            "save_attempts": 0,
            "save_retries": 0,
            "save_failures": 0,
            "save_success": 0,
            "concurrency_limit": self._max_concurrent_jobs,
            "completed_job_retention_seconds": self._completed_job_retention_seconds,
            "max_active_jobs": 0,
            "job_success_count": 0,
            "job_failure_count": 0,
            "schedule_error_count": 0,
            "cleanup_runs": 0,
            "cleanup_pruned_jobs": 0,
            "cleanup_pruned_invalid_rows": 0,
            "cleanup_cleared_expired_leases": 0,
            "cleanup_recovered_corrupt_store": 0,
            "lease_claimed": 0,
            "lease_skipped_active": 0,
            "lease_stale_recovered": 0,
            "lease_released_on_stop": 0,
            "lease_finalize_mismatch": 0,
            "lease_finalize_missing": 0,
            "last_job_id": "",
            "last_job_name": "",
            "last_job_session_id": "",
            "last_job_trigger": "",
            "last_job_status": "",
            "last_job_error": "",
            "last_job_due_iso": "",
            "last_job_started_iso": "",
            "last_job_completed_iso": "",
            "last_job_lag_s": 0.0,
            "max_job_lag_s": 0.0,
            "overdue_run_count": 0,
            "last_load_error": "",
            "last_save_error": "",
            "last_cleanup_iso": "",
            "last_cleanup_error": "",
            "last_recovered_store_path": "",
        }
        self._load()

    @classmethod
    def _path_lock(cls, path: Path) -> threading.RLock:
        key = str(path.expanduser().resolve())
        with cls._PATH_LOCKS_GUARD:
            lock = cls._PATH_LOCKS.get(key)
            if lock is None:
                lock = threading.RLock()
                cls._PATH_LOCKS[key] = lock
            return lock

    @staticmethod
    def _lock_backend_name() -> str:
        if fcntl is not None:
            return "fcntl"
        if portalocker is not None:
            return "portalocker"
        return "threading"

    def _task_snapshot(self) -> tuple[str, str]:
        task = self._task
        if task is None:
            return ("stopped", "")
        if task.cancelled():
            return ("cancelled", "")
        if not task.done():
            return ("running", "")
        try:
            exc = task.exception()
        except asyncio.CancelledError:
            return ("cancelled", "")
        if exc is not None:
            return ("failed", str(exc))
        return ("done", "")

    @staticmethod
    def _normalize_timezone(value: str | None) -> str:
        candidate = (value or "UTC").strip() or "UTC"
        try:
            ZoneInfo(candidate)
        except Exception as exc:
            raise ValueError(f"unknown timezone '{candidate}'") from exc
        return candidate

    def _load(self) -> None:
        self._diag["load_attempts"] = int(self._diag.get("load_attempts", 0) or 0) + 1
        self._diag["last_recovered_store_path"] = ""
        now = self._now()
        try:
            with self._store_lock():
                rows = self._read_rows_unlocked()
                jobs, invalid_rows = self._rows_to_jobs(rows)
                jobs, cleanup = self._sweep_jobs(jobs, now=now)
                cleanup["pruned_invalid_rows"] = int(cleanup.get("pruned_invalid_rows", 0) or 0) + invalid_rows
                if invalid_rows > 0 or cleanup["changed"]:
                    self._write_rows_unlocked([asdict(item) for item in jobs.values()])
                self._jobs = jobs
                self._record_cleanup(now=now, cleanup=cleanup)
        except json.JSONDecodeError as exc:
            recovered_path = ""
            try:
                with self._store_lock():
                    recovered_path = self._recover_corrupt_store_unlocked(exc)
                    self._jobs = {}
            except OSError as recover_exc:
                self._diag["load_failures"] = int(self._diag.get("load_failures", 0) or 0) + 1
                self._diag["last_load_error"] = str(recover_exc)
                bind_event("cron.state").error("cron load recovery failed path={} error={}", self.path, recover_exc)
                return
            else:
                if recovered_path:
                    self._diag["cleanup_recovered_corrupt_store"] = int(
                        self._diag.get("cleanup_recovered_corrupt_store", 0) or 0
                    ) + 1
                    self._diag["last_recovered_store_path"] = recovered_path
                else:
                    self._diag["load_failures"] = int(self._diag.get("load_failures", 0) or 0) + 1
                    self._diag["last_load_error"] = str(exc)
                    bind_event("cron.state").error("cron load failed path={} error={}", self.path, exc)
                    return
        except (OSError, ValueError) as exc:
            self._diag["load_failures"] = int(self._diag.get("load_failures", 0) or 0) + 1
            self._diag["last_load_error"] = str(exc)
            bind_event("cron.state").error("cron load failed path={} error={}", self.path, exc)
            return
        if self._diag.get("last_recovered_store_path"):
            self._diag["load_failures"] = int(self._diag.get("load_failures", 0) or 0) + 1
            self._diag["last_load_error"] = "cron_store_recovered_from_corruption"
            bind_event("cron.state").warning(
                "cron load recovered corrupt store path={} backup={}",
                self.path,
                self._diag.get("last_recovered_store_path", ""),
            )
            return
        self._diag["load_success"] = int(self._diag.get("load_success", 0) or 0) + 1
        self._diag["last_load_error"] = ""
        if self._jobs:
            logger.info("cron jobs loaded count={} path={}", len(self._jobs), self.path)

    def _save(self) -> None:
        items = [asdict(job) for job in self._jobs.values()]
        for attempt in range(2):
            self._diag["save_attempts"] = int(self._diag.get("save_attempts", 0) or 0) + 1
            if attempt > 0:
                self._diag["save_retries"] = int(self._diag.get("save_retries", 0) or 0) + 1
            try:
                with self._store_lock():
                    self._write_rows_unlocked(items)
            except OSError as exc:
                self._diag["save_failures"] = int(self._diag.get("save_failures", 0) or 0) + 1
                self._diag["last_save_error"] = str(exc)
                bind_event("cron.state").error("cron save failed attempt={} path={} error={}", attempt + 1, self.path, exc)
                if attempt == 0:
                    continue
                return
            self._diag["save_success"] = int(self._diag.get("save_success", 0) or 0) + 1
            self._diag["last_save_error"] = ""
            return

    async def _save_async(self) -> None:
        await asyncio.to_thread(self._save)

    @contextlib.contextmanager
    def _store_lock(self):
        fd: int | None = None
        lock_file = None
        fallback_lock = self._path_lock(self.path) if fcntl is None and portalocker is None else None
        try:
            if fallback_lock is not None:
                fallback_lock.acquire()
            lock_file = self._lock_path.open("a+b")
            fd = lock_file.fileno()
            if fcntl is not None:
                fcntl.flock(fd, fcntl.LOCK_EX)
            elif portalocker is not None:
                portalocker.lock(lock_file, portalocker.LOCK_EX)
            yield
        finally:
            if fd is not None and fcntl is not None:
                fcntl.flock(fd, fcntl.LOCK_UN)
            elif lock_file is not None and portalocker is not None:
                portalocker.unlock(lock_file)
            if lock_file is not None:
                lock_file.close()
            if fallback_lock is not None:
                fallback_lock.release()

    def _read_rows_unlocked(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        if isinstance(raw, dict) and isinstance(raw.get("jobs"), list):
            rows = raw["jobs"]
        elif isinstance(raw, list):
            rows = raw
        else:
            raise ValueError("invalid_payload")
        out: list[dict[str, Any]] = []
        for row in rows:
            if isinstance(row, dict):
                out.append(row)
        return out

    def _read_jobs_unlocked(self) -> dict[str, CronJob]:
        jobs: dict[str, CronJob] = {}
        for row in self._read_rows_unlocked():
            job = self._job_from_row(row)
            if job is not None:
                jobs[job.id] = job
        return jobs

    def _rows_to_jobs(self, rows: list[dict[str, Any]]) -> tuple[dict[str, CronJob], int]:
        jobs: dict[str, CronJob] = {}
        invalid_rows = 0
        for row in rows:
            job = self._job_from_row(row)
            if job is None:
                invalid_rows += 1
                continue
            jobs[job.id] = job
        return jobs, invalid_rows

    def _write_rows_unlocked(self, rows: list[dict[str, Any]]) -> None:
        payload = json.dumps(rows, ensure_ascii=False, indent=2)
        tmp_path = self.path.with_name(f"{self.path.name}.{os.getpid()}.tmp")
        with tmp_path.open("w", encoding="utf-8") as tmp_file:
            tmp_file.write(payload)
            tmp_file.flush()
            os.fsync(tmp_file.fileno())
        os.replace(tmp_path, self.path)
        dir_fd: int | None = None
        try:
            dir_fd = os.open(str(self.path.parent), os.O_RDONLY)
            os.fsync(dir_fd)
        except OSError:
            try:
                dir_fd = os.open(str(self.path), os.O_RDONLY)
                os.fsync(dir_fd)
            except OSError:
                pass
        finally:
            if dir_fd is not None:
                os.close(dir_fd)

    def _job_from_row(self, row: dict[str, Any]) -> CronJob | None:
        try:
            schedule = CronSchedule(**row["schedule"])
            schedule.timezone = self._normalize_timezone(schedule.timezone or self.default_timezone)
            payload = CronPayload(**row["payload"])
            return CronJob(
                id=row["id"],
                name=row["name"],
                session_id=row["session_id"],
                schedule=schedule,
                payload=payload,
                enabled=bool(row.get("enabled", True)),
                next_run_iso=str(row.get("next_run_iso", "")),
                last_run_iso=str(row.get("last_run_iso", "")),
                last_status=str(row.get("last_status", "idle") or "idle"),
                last_error=str(row.get("last_error", "") or ""),
                consecutive_failures=int(row.get("consecutive_failures", 0) or 0),
                run_count=int(row.get("run_count", 0) or 0),
                lease_token=str(row.get("lease_token", "") or ""),
                lease_owner=str(row.get("lease_owner", "") or ""),
                lease_expires_iso=str(row.get("lease_expires_iso", "") or ""),
                lease_claimed_iso=str(row.get("lease_claimed_iso", "") or ""),
            )
        except Exception:
            return None

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def _compute_next(schedule: CronSchedule, now: datetime) -> datetime | None:
        tz_name = (schedule.timezone or "UTC").strip() or "UTC"
        tz = ZoneInfo(tz_name)
        if schedule.kind == "every":
            seconds = max(1, int(schedule.every_seconds or 1))
            return now + timedelta(seconds=seconds)
        if schedule.kind == "at":
            if not schedule.run_at_iso:
                return None
            try:
                dt = datetime.fromisoformat(schedule.run_at_iso)
            except ValueError:
                return None
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=tz)
            return dt.astimezone(timezone.utc)
        if schedule.kind == "cron":
            if croniter is None:
                raise RuntimeError("croniter is required for cron expressions")
            if not schedule.cron_expr.strip():
                return None
            base = now.astimezone(tz)
            next_local = croniter(schedule.cron_expr, base).get_next(datetime)
            if next_local.tzinfo is None:
                next_local = next_local.replace(tzinfo=tz)
            return next_local.astimezone(timezone.utc)
        return None

    async def start(self, on_job: JobCallback) -> None:
        self._on_job = on_job
        if self._task is not None:
            task_state, _task_error = self._task_snapshot()
            if task_state in {"failed", "cancelled", "done"}:
                self._task = None
            else:
                return
        self._task = asyncio.create_task(self._loop())
        logger.info("cron service started path={}", self.path)

    async def stop(self) -> None:
        if self._task is None:
            return
        bind_event("cron.lifecycle").info("cron service stopping")
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass
        self._task = None
        await self._cancel_running_tasks()
        released = await asyncio.to_thread(self._release_owned_leases)
        if released:
            bind_event("cron.lifecycle").warning("cron stop released_owned_leases count={}", released)
        bind_event("cron.lifecycle").info("cron service stopped")

    def status(self) -> dict[str, Any]:
        task_state, task_error = self._task_snapshot()
        return {
            "running": task_state == "running",
            "worker_state": task_state,
            "jobs": len(self._jobs),
            "store_path": str(self.path),
            "default_timezone": self.default_timezone,
            "lock_backend": self._lock_backend_name(),
            "load_attempts": int(self._diag.get("load_attempts", 0) or 0),
            "load_success": int(self._diag.get("load_success", 0) or 0),
            "load_failures": int(self._diag.get("load_failures", 0) or 0),
            "save_attempts": int(self._diag.get("save_attempts", 0) or 0),
            "save_retries": int(self._diag.get("save_retries", 0) or 0),
            "save_failures": int(self._diag.get("save_failures", 0) or 0),
            "save_success": int(self._diag.get("save_success", 0) or 0),
            "concurrency_limit": int(self._diag.get("concurrency_limit", self._max_concurrent_jobs) or self._max_concurrent_jobs),
            "completed_job_retention_seconds": int(
                self._diag.get("completed_job_retention_seconds", self._completed_job_retention_seconds)
                or self._completed_job_retention_seconds
            ),
            "active_jobs": len(self._running_tasks),
            "max_active_jobs": int(self._diag.get("max_active_jobs", 0) or 0),
            "job_success_count": int(self._diag.get("job_success_count", 0) or 0),
            "job_failure_count": int(self._diag.get("job_failure_count", 0) or 0),
            "schedule_error_count": int(self._diag.get("schedule_error_count", 0) or 0),
            "cleanup_runs": int(self._diag.get("cleanup_runs", 0) or 0),
            "cleanup_pruned_jobs": int(self._diag.get("cleanup_pruned_jobs", 0) or 0),
            "cleanup_pruned_invalid_rows": int(self._diag.get("cleanup_pruned_invalid_rows", 0) or 0),
            "cleanup_cleared_expired_leases": int(self._diag.get("cleanup_cleared_expired_leases", 0) or 0),
            "cleanup_recovered_corrupt_store": int(self._diag.get("cleanup_recovered_corrupt_store", 0) or 0),
            "lease_claimed": int(self._diag.get("lease_claimed", 0) or 0),
            "lease_skipped_active": int(self._diag.get("lease_skipped_active", 0) or 0),
            "lease_stale_recovered": int(self._diag.get("lease_stale_recovered", 0) or 0),
            "lease_released_on_stop": int(self._diag.get("lease_released_on_stop", 0) or 0),
            "lease_finalize_mismatch": int(self._diag.get("lease_finalize_mismatch", 0) or 0),
            "lease_finalize_missing": int(self._diag.get("lease_finalize_missing", 0) or 0),
            "last_job_id": str(self._diag.get("last_job_id", "") or ""),
            "last_job_name": str(self._diag.get("last_job_name", "") or ""),
            "last_job_session_id": str(self._diag.get("last_job_session_id", "") or ""),
            "last_job_trigger": str(self._diag.get("last_job_trigger", "") or ""),
            "last_job_status": str(self._diag.get("last_job_status", "") or ""),
            "last_job_error": str(self._diag.get("last_job_error", "") or ""),
            "last_job_due_iso": str(self._diag.get("last_job_due_iso", "") or ""),
            "last_job_started_iso": str(self._diag.get("last_job_started_iso", "") or ""),
            "last_job_completed_iso": str(self._diag.get("last_job_completed_iso", "") or ""),
            "last_job_lag_s": float(self._diag.get("last_job_lag_s", 0.0) or 0.0),
            "max_job_lag_s": float(self._diag.get("max_job_lag_s", 0.0) or 0.0),
            "overdue_run_count": int(self._diag.get("overdue_run_count", 0) or 0),
            "last_load_error": str(self._diag.get("last_load_error", "") or ""),
            "last_save_error": str(self._diag.get("last_save_error", "") or ""),
            "last_cleanup_iso": str(self._diag.get("last_cleanup_iso", "") or ""),
            "last_cleanup_error": str(self._diag.get("last_cleanup_error", "") or ""),
            "last_recovered_store_path": str(self._diag.get("last_recovered_store_path", "") or ""),
            "last_error": task_error,
        }

    def _mark_schedule_error(self, job: CronJob, exc: Exception) -> None:
        job.last_status = "schedule_error"
        job.last_error = str(exc)
        job.consecutive_failures = int(job.consecutive_failures or 0) + 1
        self._diag["schedule_error_count"] = int(self._diag.get("schedule_error_count", 0) or 0) + 1
        bind_event("cron.job", session=job.session_id).error("cron schedule error id={} error={}", job.id, exc)

    @staticmethod
    def _normalize_datetime(value: str) -> datetime:
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt

    def _recover_corrupt_store_unlocked(self, exc: Exception) -> str:
        if not self.path.exists():
            return ""
        stamp = self._now().strftime("%Y%m%dT%H%M%SZ")
        backup = self.path.with_name(f"{self.path.stem}.corrupt-{stamp}-{uuid.uuid4().hex[:8]}{self.path.suffix}")
        os.replace(self.path, backup)
        bind_event("cron.state").warning(
            "cron store moved aside after load failure path={} backup={} error={}",
            self.path,
            backup,
            exc,
        )
        return str(backup)

    def _completed_job_at(self, job: CronJob) -> datetime | None:
        raw = str(job.last_run_iso or "").strip()
        if not raw:
            return None
        try:
            return self._normalize_datetime(raw)
        except ValueError:
            return None

    def _should_prune_completed_job(self, job: CronJob, *, now: datetime) -> bool:
        if job.enabled or str(job.next_run_iso or "").strip():
            return False
        if str(job.last_status or "").strip() in {"", "idle"}:
            return False
        completed_at = self._completed_job_at(job)
        if completed_at is None:
            return False
        age_seconds = (now - completed_at).total_seconds()
        return age_seconds >= float(self._completed_job_retention_seconds)

    def _sweep_jobs(self, jobs: dict[str, CronJob], *, now: datetime) -> tuple[dict[str, CronJob], dict[str, int | bool]]:
        pruned_jobs = 0
        cleared_expired_leases = 0
        for job_id, job in list(jobs.items()):
            if str(job.lease_token or "").strip() and not self._is_lease_active(job, now):
                self._clear_lease(job)
                jobs[job_id] = job
                cleared_expired_leases += 1
            if self._should_prune_completed_job(job, now=now):
                jobs.pop(job_id, None)
                pruned_jobs += 1
        return jobs, {
            "changed": bool(pruned_jobs or cleared_expired_leases),
            "pruned_jobs": pruned_jobs,
            "cleared_expired_leases": cleared_expired_leases,
            "pruned_invalid_rows": 0,
        }

    def _record_cleanup(self, *, now: datetime, cleanup: dict[str, int | bool], error: str = "") -> None:
        cleared_expired_leases = int(cleanup.get("cleared_expired_leases", 0) or 0)
        self._diag["cleanup_runs"] = int(self._diag.get("cleanup_runs", 0) or 0) + 1
        self._diag["cleanup_pruned_jobs"] = int(self._diag.get("cleanup_pruned_jobs", 0) or 0) + int(
            cleanup.get("pruned_jobs", 0) or 0
        )
        self._diag["cleanup_pruned_invalid_rows"] = int(
            self._diag.get("cleanup_pruned_invalid_rows", 0) or 0
        ) + int(cleanup.get("pruned_invalid_rows", 0) or 0)
        self._diag["cleanup_cleared_expired_leases"] = int(
            self._diag.get("cleanup_cleared_expired_leases", 0) or 0
        ) + cleared_expired_leases
        self._diag["lease_stale_recovered"] = int(self._diag.get("lease_stale_recovered", 0) or 0) + cleared_expired_leases
        self._diag["last_cleanup_iso"] = now.isoformat()
        self._diag["last_cleanup_error"] = str(error or "")

    def _run_cleanup_pass(self) -> bool:
        now = self._now()
        cleanup = {"changed": False, "pruned_jobs": 0, "cleared_expired_leases": 0, "pruned_invalid_rows": 0}
        try:
            with self._store_lock():
                rows = self._read_rows_unlocked()
                jobs, invalid_rows = self._rows_to_jobs(rows)
                jobs, cleanup = self._sweep_jobs(jobs, now=now)
                cleanup["pruned_invalid_rows"] = int(cleanup.get("pruned_invalid_rows", 0) or 0) + invalid_rows
                if invalid_rows > 0 or cleanup["changed"]:
                    self._write_rows_unlocked([asdict(item) for item in jobs.values()])
                self._jobs = jobs
        except (json.JSONDecodeError, ValueError) as exc:
            recovered_path = ""
            try:
                with self._store_lock():
                    recovered_path = self._recover_corrupt_store_unlocked(exc)
                    self._jobs = {}
            except OSError as recover_exc:
                self._record_cleanup(now=now, cleanup=cleanup, error=str(recover_exc))
                bind_event("cron.state").warning("cron cleanup recovery failed path={} error={}", self.path, recover_exc)
                return False
            if recovered_path:
                self._diag["cleanup_recovered_corrupt_store"] = int(
                    self._diag.get("cleanup_recovered_corrupt_store", 0) or 0
                ) + 1
                self._diag["last_recovered_store_path"] = recovered_path
            self._record_cleanup(now=now, cleanup=cleanup, error=str(exc))
            return bool(recovered_path)
        except OSError as exc:
            self._record_cleanup(now=now, cleanup=cleanup, error=str(exc))
            bind_event("cron.state").warning("cron cleanup failed path={} error={}", self.path, exc)
            return False

        self._record_cleanup(now=now, cleanup=cleanup)
        return bool(cleanup["changed"] or cleanup["pruned_invalid_rows"])

    def _record_job_snapshot(
        self,
        *,
        job: CronJob,
        trigger: str,
        due_iso: str,
        started_at: datetime,
        completed_at: datetime,
    ) -> None:
        normalized_due = str(due_iso or "").strip()
        lag_s = 0.0
        if normalized_due:
            try:
                due_at = self._normalize_datetime(normalized_due)
            except ValueError:
                normalized_due = ""
            else:
                lag_s = max(0.0, (started_at - due_at).total_seconds())
                if lag_s >= self._OVERDUE_THRESHOLD_SECONDS:
                    self._diag["overdue_run_count"] = int(self._diag.get("overdue_run_count", 0) or 0) + 1
                self._diag["max_job_lag_s"] = max(float(self._diag.get("max_job_lag_s", 0.0) or 0.0), float(lag_s))

        self._diag["last_job_id"] = str(job.id or "")
        self._diag["last_job_name"] = str(job.name or "")
        self._diag["last_job_session_id"] = str(job.session_id or "")
        self._diag["last_job_trigger"] = str(trigger or "")
        self._diag["last_job_status"] = str(job.last_status or "")
        self._diag["last_job_error"] = str(job.last_error or "")
        self._diag["last_job_due_iso"] = normalized_due
        self._diag["last_job_started_iso"] = started_at.isoformat()
        self._diag["last_job_completed_iso"] = completed_at.isoformat()
        self._diag["last_job_lag_s"] = float(lag_s)

    def _is_lease_active(self, job: CronJob, now: datetime) -> bool:
        if not job.lease_token or not job.lease_expires_iso:
            return False
        try:
            expires = self._normalize_datetime(job.lease_expires_iso)
        except ValueError:
            return False
        return expires > now

    def _clear_lease(self, job: CronJob) -> None:
        job.lease_token = ""
        job.lease_owner = ""
        job.lease_expires_iso = ""
        job.lease_claimed_iso = ""

    def _release_owned_leases(self) -> int:
        released = 0
        with self._store_lock():
            jobs = self._read_jobs_unlocked()
            changed = False
            for job in jobs.values():
                if str(job.lease_owner or "") != self._instance_id or not str(job.lease_token or ""):
                    continue
                self._clear_lease(job)
                if not str(job.last_status or "").strip() or job.last_status == "idle":
                    job.last_status = "interrupted"
                job.last_error = "service_stopped_before_commit"
                jobs[job.id] = job
                released += 1
                changed = True
            if changed:
                self._write_rows_unlocked([asdict(item) for item in jobs.values()])
                self._jobs = jobs
            else:
                self._jobs = jobs
        if released:
            self._diag["lease_released_on_stop"] = int(self._diag.get("lease_released_on_stop", 0) or 0) + released
        return released

    def _try_claim_job(
        self,
        job_id: str,
        now: datetime,
        *,
        require_due: bool,
        allow_disabled: bool,
        session_id: str | None = None,
    ) -> tuple[CronJob | None, str]:
        token = uuid.uuid4().hex
        claimed: CronJob | None = None
        with self._store_lock():
            jobs = self._read_jobs_unlocked()
            job = jobs.get(job_id)
            if job is None:
                self._jobs = jobs
                return None, "missing"
            if session_id is not None and job.session_id != session_id:
                self._jobs = jobs
                return None, "forbidden"
            if not allow_disabled and not job.enabled:
                self._jobs = jobs
                return None, "disabled"
            if require_due:
                if not job.next_run_iso:
                    self._jobs = jobs
                    return None, "not_due"
                try:
                    next_run = self._normalize_datetime(job.next_run_iso)
                except ValueError:
                    self._jobs = jobs
                    return None, "not_due"
                if next_run > now:
                    self._jobs = jobs
                    return None, "not_due"
            stale_recovered = False
            if self._is_lease_active(job, now):
                self._diag["lease_skipped_active"] = int(self._diag.get("lease_skipped_active", 0) or 0) + 1
                self._jobs = jobs
                return None, "active"
            if job.lease_token and job.lease_expires_iso:
                stale_recovered = True
            job.lease_token = token
            job.lease_owner = self._instance_id
            job.lease_claimed_iso = now.isoformat()
            job.lease_expires_iso = (now + timedelta(seconds=self._lease_seconds)).isoformat()
            jobs[job.id] = job
            self._write_rows_unlocked([asdict(item) for item in jobs.values()])
            self._jobs = jobs
            claimed = job
        self._diag["lease_claimed"] = int(self._diag.get("lease_claimed", 0) or 0) + 1
        if stale_recovered:
            self._diag["lease_stale_recovered"] = int(self._diag.get("lease_stale_recovered", 0) or 0) + 1
        return claimed, "claimed"

    def _try_claim_due_job(self, job_id: str, now: datetime) -> CronJob | None:
        claimed, reason = self._try_claim_job(
            job_id,
            now,
            require_due=True,
            allow_disabled=False,
        )
        if reason != "claimed":
            return None
        return claimed

    def _commit_job_result(
        self,
        *,
        job_id: str,
        lease_token: str,
        now: datetime,
        callback_failed: bool,
        claimed_job: CronJob,
    ) -> bool:
        committed = False
        with self._store_lock():
            jobs = self._read_jobs_unlocked()
            job = jobs.get(job_id)
            if job is None:
                self._diag["lease_finalize_missing"] = int(self._diag.get("lease_finalize_missing", 0) or 0) + 1
                self._jobs = jobs
                return False
            if job.lease_token != lease_token:
                self._diag["lease_finalize_mismatch"] = int(self._diag.get("lease_finalize_mismatch", 0) or 0) + 1
                self._jobs = jobs
                return False
            job.last_status = claimed_job.last_status
            job.last_error = claimed_job.last_error
            job.consecutive_failures = int(claimed_job.consecutive_failures or 0)
            job.run_count = int(job.run_count or 0) + 1
            if callback_failed:
                try:
                    after_failed = self._compute_next(job.schedule, now)
                    job.next_run_iso = after_failed.isoformat() if after_failed else ""
                except Exception as exc:
                    self._mark_schedule_error(job, exc)
                    job.next_run_iso = ""
                self._clear_lease(job)
                jobs[job.id] = job
                self._write_rows_unlocked([asdict(item) for item in jobs.values()])
                self._jobs = jobs
                return True
            job.last_run_iso = now.isoformat()
            run_once = bool(job.payload.metadata.get("run_once"))
            if run_once:
                jobs.pop(job.id, None)
                bind_event("cron.job", session=job.session_id).info("cron job auto-removed after run_once id={}", job.id)
                self._write_rows_unlocked([asdict(item) for item in jobs.values()])
                self._jobs = jobs
                return True
            try:
                after = self._compute_next(job.schedule, now)
            except Exception as exc:
                self._mark_schedule_error(job, exc)
                after = None
            if job.schedule.kind == "at":
                job.enabled = False
                job.next_run_iso = ""
            else:
                job.next_run_iso = after.isoformat() if after else ""
            self._clear_lease(job)
            jobs[job.id] = job
            self._write_rows_unlocked([asdict(item) for item in jobs.values()])
            self._jobs = jobs
            committed = True
        return committed

    def _compute_loop_sleep_seconds(self, now: datetime) -> float:
        nearest_delta: float | None = None
        for job in self._jobs.values():
            if not job.enabled or not job.next_run_iso:
                continue
            try:
                next_run = self._normalize_datetime(job.next_run_iso)
            except ValueError:
                continue
            delta_s = (next_run - now).total_seconds()
            if nearest_delta is None or delta_s < nearest_delta:
                nearest_delta = delta_s

        if nearest_delta is None:
            return self._LOOP_SLEEP_MAX_SECONDS

        bounded = max(self._LOOP_SLEEP_MIN_SECONDS, min(self._LOOP_SLEEP_MAX_SECONDS, nearest_delta))
        return float(bounded)

    async def _cancel_running_tasks(self) -> None:
        pending = [task for task in self._running_tasks.values() if not task.done()]
        if not pending:
            self._running_tasks.clear()
            return
        for task in pending:
            task.cancel()
        done, still_pending = await asyncio.wait(pending, timeout=self._MAX_CLEANUP_WAIT_SECONDS)
        for task in done:
            with contextlib.suppress(asyncio.CancelledError, Exception):
                task.result()
        for task in still_pending:
            bind_event("cron.lifecycle").warning("cron run task still pending after cancel")
        self._running_tasks = {
            job_id: task for job_id, task in self._running_tasks.items() if not task.done()
        }

    def _track_running_task(self, job_id: str, task: asyncio.Task[None]) -> None:
        self._running_tasks[job_id] = task
        active_jobs = len(self._running_tasks)
        self._diag["max_active_jobs"] = max(int(self._diag.get("max_active_jobs", 0) or 0), active_jobs)

        def _cleanup(_task: asyncio.Task[None], *, claimed_job_id: str = job_id) -> None:
            current = self._running_tasks.get(claimed_job_id)
            if current is _task:
                self._running_tasks.pop(claimed_job_id, None)

        task.add_done_callback(_cleanup)

    async def _run_claimed_job(self, claimed: CronJob, *, due_iso: str, started_at: datetime, trigger: str) -> None:
        callback_failed = False
        if self._on_job is not None:
            logger.info("cron job executing id={} session={} name={}", claimed.id, claimed.session_id, claimed.name)
            try:
                await asyncio.wait_for(self._on_job(claimed), timeout=self._callback_timeout_seconds)
                logger.info("cron job executed id={} session={}", claimed.id, claimed.session_id)
                claimed.last_status = "success"
                claimed.last_error = ""
                claimed.consecutive_failures = 0
                self._diag["job_success_count"] = int(self._diag.get("job_success_count", 0) or 0) + 1
            except asyncio.CancelledError:
                raise
            except asyncio.TimeoutError:
                callback_failed = True
                claimed.last_status = "failed"
                claimed.last_error = f"callback_timeout after {self._callback_timeout_seconds}s"
                claimed.consecutive_failures = int(claimed.consecutive_failures or 0) + 1
                self._diag["job_failure_count"] = int(self._diag.get("job_failure_count", 0) or 0) + 1
                logger.error(
                    "cron job timed out id={} session={} timeout={}s",
                    claimed.id,
                    claimed.session_id,
                    self._callback_timeout_seconds,
                )
            except Exception as exc:
                callback_failed = True
                claimed.last_status = "failed"
                claimed.last_error = str(exc)
                claimed.consecutive_failures = int(claimed.consecutive_failures or 0) + 1
                self._diag["job_failure_count"] = int(self._diag.get("job_failure_count", 0) or 0) + 1
                logger.error("cron job failed id={} session={} error={}", claimed.id, claimed.session_id, exc)
        self._record_job_snapshot(
            job=claimed,
            trigger=trigger,
            due_iso=due_iso,
            started_at=started_at,
            completed_at=self._now(),
        )
        await asyncio.to_thread(
            self._commit_job_result,
            job_id=claimed.id,
            lease_token=claimed.lease_token,
            now=self._now(),
            callback_failed=callback_failed,
            claimed_job=claimed,
        )

    async def _loop(self) -> None:
        while True:
            loop_monotonic = asyncio.get_running_loop().time()
            if loop_monotonic - self._last_cleanup_monotonic >= self._cleanup_interval_seconds:
                await asyncio.to_thread(self._run_cleanup_pass)
                self._last_cleanup_monotonic = loop_monotonic
            now = self._now()
            changed = False
            for job in list(self._jobs.values()):
                if not job.enabled:
                    continue
                if not job.next_run_iso:
                    try:
                        next_dt = self._compute_next(job.schedule, now)
                    except Exception as exc:
                        self._mark_schedule_error(job, exc)
                        changed = True
                        continue
                    job.next_run_iso = next_dt.isoformat() if next_dt else ""
                    changed = True
            if changed:
                await asyncio.to_thread(self._save)

            due_job_ids: list[str] = []
            changed = False
            for job in list(self._jobs.values()):
                if not job.enabled or not job.next_run_iso:
                    continue
                try:
                    next_run = self._normalize_datetime(job.next_run_iso)
                except ValueError as exc:
                    self._mark_schedule_error(job, exc)
                    job.next_run_iso = ""
                    changed = True
                    continue
                if next_run <= now:
                    due_job_ids.append(job.id)

            if changed:
                await asyncio.to_thread(self._save)

            available_slots = max(0, self._max_concurrent_jobs - len(self._running_tasks))
            for job_id in due_job_ids[:available_slots]:
                claimed = await asyncio.to_thread(self._try_claim_due_job, job_id, now)
                if claimed is None:
                    continue
                due_iso = str(claimed.next_run_iso or "")
                started_at = self._now()
                run_task = asyncio.create_task(
                    self._run_claimed_job(
                        claimed,
                        due_iso=due_iso,
                        started_at=started_at,
                        trigger="loop",
                    )
                )
                self._track_running_task(claimed.id, run_task)
            sleep_seconds = self._compute_loop_sleep_seconds(self._now())
            await asyncio.sleep(sleep_seconds)

    def list_jobs(self, *, session_id: str | None = None) -> list[dict[str, Any]]:
        rows = list(self._jobs.values())
        if session_id:
            rows = [item for item in rows if item.session_id == session_id]
        out: list[dict[str, Any]] = []
        for item in sorted(rows, key=lambda j: j.name):
            row = asdict(item)
            row["expression"] = self._schedule_to_expression(item.schedule)
            row["timezone"] = item.schedule.timezone
            out.append(row)
        return out

    async def add_job(
        self,
        *,
        session_id: str,
        expression: str,
        prompt: str,
        name: str = "",
        timezone_name: str | None = None,
        channel: str = "",
        target: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> str:
        schedule = self._parse_expression(expression, timezone_name=timezone_name)
        now = self._now()
        next_run = self._compute_next(schedule, now)
        job_id = uuid.uuid4().hex
        job = CronJob(
            id=job_id,
            name=name or f"job-{job_id[:8]}",
            session_id=session_id,
            schedule=schedule,
            payload=CronPayload(prompt=prompt, channel=channel, target=target, metadata=metadata or {}),
            next_run_iso=next_run.isoformat() if next_run else "",
        )
        self._jobs[job_id] = job
        await self._save_async()
        logger.info(
            "cron job created id={} session={} schedule_kind={} name={}",
            job_id,
            session_id,
            schedule.kind,
            job.name,
        )
        return job_id

    def _owned_job(self, job_id: str, *, session_id: str | None = None) -> CronJob | None:
        job = self._jobs.get(job_id)
        if job is None:
            return None
        if session_id is not None and job.session_id != session_id:
            return None
        return job

    def remove_job(self, job_id: str, *, session_id: str | None = None) -> bool:
        job = self._owned_job(job_id, session_id=session_id)
        if job is None:
            return False
        self._jobs.pop(job.id, None)
        if job is not None:
            self._save()
            bind_event("cron.job", session=job.session_id).info("cron job removed id={}", job.id)
        return True

    def enable_job(self, job_id: str, *, enabled: bool, session_id: str | None = None) -> bool:
        job = self._owned_job(job_id, session_id=session_id)
        if job is None:
            return False
        job.enabled = enabled
        if enabled and not job.next_run_iso:
            next_dt = self._compute_next(job.schedule, self._now())
            job.next_run_iso = next_dt.isoformat() if next_dt else ""
        self._save()
        bind_event("cron.job", session=job.session_id).info("cron job updated id={} enabled={}", job.id, enabled)
        return True

    def get_job(self, job_id: str, *, session_id: str | None = None) -> CronJob | None:
        return self._owned_job(job_id, session_id=session_id)

    async def run_job(
        self,
        job_id: str,
        *,
        on_job: JobCallback | None = None,
        force: bool = False,
        session_id: str | None = None,
    ) -> str | None:
        claimed, reason = await asyncio.to_thread(
            self._try_claim_job,
            job_id,
            self._now(),
            require_due=False,
            allow_disabled=force,
            session_id=session_id,
        )
        if reason in {"missing", "forbidden"}:
            raise KeyError(job_id)
        if reason == "disabled":
            raise RuntimeError("cron_job_disabled")
        if reason == "active":
            raise RuntimeError("cron_job_already_running")
        if claimed is None:
            raise KeyError(job_id)
        callback = on_job or self._on_job
        if callback is None:
            raise RuntimeError("cron_job_callback_missing")
        due_iso = str(claimed.next_run_iso or "")
        started_at = self._now()
        try:
            out = await asyncio.wait_for(callback(claimed), timeout=self._callback_timeout_seconds)
            claimed.last_status = "success"
            claimed.last_error = ""
            claimed.consecutive_failures = 0
            self._diag["job_success_count"] = int(self._diag.get("job_success_count", 0) or 0) + 1
        except asyncio.TimeoutError as exc:
            timeout_error = f"callback_timeout after {self._callback_timeout_seconds}s"
            claimed.last_status = "failed"
            claimed.last_error = timeout_error
            claimed.consecutive_failures = int(claimed.consecutive_failures or 0) + 1
            self._diag["job_failure_count"] = int(self._diag.get("job_failure_count", 0) or 0) + 1
            self._record_job_snapshot(
                job=claimed,
                trigger="manual",
                due_iso=due_iso,
                started_at=started_at,
                completed_at=self._now(),
            )
            await asyncio.to_thread(
                self._commit_job_result,
                job_id=claimed.id,
                lease_token=claimed.lease_token,
                now=self._now(),
                callback_failed=True,
                claimed_job=claimed,
            )
            raise TimeoutError(timeout_error) from exc
        except Exception as exc:
            claimed.last_status = "failed"
            claimed.last_error = str(exc)
            claimed.consecutive_failures = int(claimed.consecutive_failures or 0) + 1
            self._diag["job_failure_count"] = int(self._diag.get("job_failure_count", 0) or 0) + 1
            self._record_job_snapshot(
                job=claimed,
                trigger="manual",
                due_iso=due_iso,
                started_at=started_at,
                completed_at=self._now(),
            )
            await asyncio.to_thread(
                self._commit_job_result,
                job_id=claimed.id,
                lease_token=claimed.lease_token,
                now=self._now(),
                callback_failed=True,
                claimed_job=claimed,
            )
            raise
        self._record_job_snapshot(
            job=claimed,
            trigger="manual",
            due_iso=due_iso,
            started_at=started_at,
            completed_at=self._now(),
        )
        await asyncio.to_thread(
            self._commit_job_result,
            job_id=claimed.id,
            lease_token=claimed.lease_token,
            now=self._now(),
            callback_failed=False,
            claimed_job=claimed,
        )
        current = self.get_job(claimed.id, session_id=session_id)
        if current is None:
            bind_event("cron.job", session=claimed.session_id).info(
                "cron job manually auto-removed after run_once id={}",
                claimed.id,
            )
            return out
        bind_event("cron.job", session=current.session_id).info(
            "cron job manually executed id={} enabled={}",
            current.id,
            current.enabled,
        )
        return out

    def _schedule_to_expression(self, schedule: CronSchedule) -> str:
        if schedule.kind == "every":
            return f"every {max(1, int(schedule.every_seconds or 1))}"
        if schedule.kind == "at":
            return f"at {schedule.run_at_iso}"
        return schedule.cron_expr

    def _parse_expression(self, expression: str, *, timezone_name: str | None = None) -> CronSchedule:
        expr = expression.strip()
        tz_name = self._normalize_timezone(timezone_name or self.default_timezone)
        if expr.startswith("every "):
            raw = expr.split(" ", 1)[1].strip().lower()
            if raw.endswith("s"):
                raw = raw[:-1]
            return CronSchedule(kind="every", every_seconds=max(1, int(raw)), timezone=tz_name)
        if expr.startswith("at "):
            return CronSchedule(kind="at", run_at_iso=expr.split(" ", 1)[1].strip(), timezone=tz_name)
        return CronSchedule(kind="cron", cron_expr=expr, timezone=tz_name)
