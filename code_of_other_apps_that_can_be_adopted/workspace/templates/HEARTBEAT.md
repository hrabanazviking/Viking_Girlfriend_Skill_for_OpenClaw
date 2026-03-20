# HEARTBEAT.md

Use this file to define periodic checks for the heartbeat loop.

## Contract
- The heartbeat prompt runs every configured interval.
- If there is nothing actionable, return `HEARTBEAT_OK` (token at start or end is treated as ack).
- Any response without `HEARTBEAT_OK` ack is treated as actionable.

## Suggested checklist
- Check overdue cron jobs and pending reminders.
- Check urgent inbox/alerts if tools are available.
- Verify proactive memory suggestions from MemoryMonitor.
- Deliver only memory suggestions with priority >= 0.7 via the configured channel/target.
- Report only meaningful changes.

## Cron Guidelines
- For one-time requests (e.g. "send in 5 minutes"), create cron jobs with `run_once=true`.
- Never use `every_seconds` for one-time requests; prefer one-shot semantics.
- Keep recurring schedules only for truly repeating tasks.

## Reporting Rules
- Avoid duplicate updates: do not resend the same status unless there is new information.
- Be proactive only when there is actionable impact for the user.
- If there is no actionable change, return `HEARTBEAT_OK`.

Keep this file short to reduce token usage.
