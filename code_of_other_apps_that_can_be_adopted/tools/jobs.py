"""JobsTool — lets agents submit, check, and list background jobs."""
from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from clawlite.tools.base import Tool, ToolContext

if TYPE_CHECKING:
    from clawlite.jobs.queue import JobQueue


class JobsTool(Tool):
    name = "jobs"
    description = (
        "Manage background jobs. Actions: submit, status, cancel, list. "
        "Use 'submit' to queue async work, 'status' to check progress."
    )

    def __init__(self, queue: "JobQueue") -> None:
        self._queue = queue

    def args_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["submit", "status", "cancel", "list"],
                    "description": "Operation to perform",
                },
                "kind": {"type": "string", "description": "Job kind: agent_run, skill_exec, custom"},
                "payload": {"type": "object", "description": "Job payload (action=submit)"},
                "priority": {"type": "integer", "description": "0-10, default 5"},
                "job_id": {"type": "string", "description": "Job ID (action=status|cancel)"},
                "session_filter": {"type": "string", "description": "Filter by session_id (action=list)"},
                "status_filter": {"type": "string", "description": "Filter by status (action=list)"},
            },
            "required": ["action"],
        }

    async def run(self, arguments: dict[str, Any], ctx: ToolContext) -> str:
        action = str(arguments.get("action", "")).strip().lower()

        if action == "submit":
            kind = str(arguments.get("kind", "agent_run")).strip()
            payload = arguments.get("payload") or {}
            if not isinstance(payload, dict):
                return "error: payload must be an object"
            priority = int(arguments.get("priority", 5))
            job = self._queue.submit(
                kind, payload,
                priority=priority,
                session_id=ctx.session_id,
            )
            return json.dumps({"ok": True, "job_id": job.id, "status": job.status, "kind": job.kind})

        if action == "status":
            job_id = str(arguments.get("job_id", "")).strip()
            if not job_id:
                return "error: job_id is required"
            job = self._queue.status(job_id, session_id=ctx.session_id)
            if job is None:
                return f"error: job not found: {job_id}"
            return json.dumps({
                "job_id": job.id, "kind": job.kind, "status": job.status,
                "result": job.result[:500] if job.result else "",
                "error": job.error[:200] if job.error else "",
                "created_at": job.created_at, "finished_at": job.finished_at,
            })

        if action == "cancel":
            job_id = str(arguments.get("job_id", "")).strip()
            if not job_id:
                return "error: job_id is required"
            ok = self._queue.cancel(job_id, session_id=ctx.session_id)
            return json.dumps({"ok": ok, "job_id": job_id})

        if action == "list":
            session_f = str(arguments.get("session_filter", "") or "").strip() or None
            if session_f is not None and session_f != ctx.session_id:
                return "error: session_filter override is not allowed"
            status_f = arguments.get("status_filter") or None
            jobs = self._queue.list_jobs(session_id=session_f or ctx.session_id, status=status_f)
            rows = [{"job_id": j.id, "kind": j.kind, "status": j.status,
                     "priority": j.priority, "created_at": j.created_at} for j in jobs[:20]]
            return json.dumps({"jobs": rows, "total": len(jobs)})

        return f"error: unknown action '{action}'"
