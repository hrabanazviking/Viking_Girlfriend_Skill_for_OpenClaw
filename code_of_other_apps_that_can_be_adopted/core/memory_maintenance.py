from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable


async def start_periodic_task(
    *,
    owner: Any,
    task_attr: str,
    interval_attr: str,
    interval_s: float,
    default_interval_s: float,
    loop_factory: Callable[[], Awaitable[Any]],
) -> None:
    existing = getattr(owner, task_attr, None)
    if existing and not existing.done():
        return
    setattr(owner, interval_attr, max(60.0, float(interval_s or default_interval_s)))
    setattr(owner, task_attr, asyncio.create_task(loop_factory()))


async def stop_periodic_task(*, owner: Any, task_attr: str) -> None:
    task = getattr(owner, task_attr, None)
    if task and not task.done():
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    setattr(owner, task_attr, None)


async def periodic_task_loop(
    *,
    interval_s: float,
    work: Callable[[], Awaitable[Any]],
    diagnostics: dict[str, Any],
    error_prefix: str,
) -> None:
    while True:
        try:
            await asyncio.sleep(interval_s)
            await work()
        except asyncio.CancelledError:
            break
        except Exception as exc:
            diagnostics["last_error"] = f"{error_prefix}: {exc}"


async def purge_decayed_records(
    *,
    read_history_records: Callable[[], list[Any]],
    decay_penalty: Callable[[Any], float],
    delete_records_by_ids: Callable[[set[str]], dict[str, Any]],
    diagnostics: dict[str, Any],
    threshold: float,
) -> dict[str, int]:
    expired_ids: set[str] = set()

    try:
        history = await asyncio.to_thread(read_history_records)
    except Exception:
        history = []

    for row in history:
        if float(getattr(row, "decay_rate", 0.0) or 0.0) <= 0.0:
            continue
        if decay_penalty(row) >= threshold:
            row_id = str(getattr(row, "id", "") or "").strip()
            if row_id:
                expired_ids.add(row_id)

    if not expired_ids:
        return {"purged": 0}

    try:
        deleted = await asyncio.to_thread(delete_records_by_ids, expired_ids)
        purged = int(deleted.get("deleted_count", 0) or 0)
    except Exception as exc:
        diagnostics["last_error"] = f"decay_purge: {exc}"
        purged = 0

    if purged > 0:
        diagnostics["decay_gc_purged"] = int(diagnostics.get("decay_gc_purged", 0)) + purged

    return {"purged": purged}


async def consolidate_categories(
    *,
    backend: Any,
    threshold: int,
    add_record: Callable[..., Any],
    diagnostics: dict[str, Any],
) -> dict[str, int]:
    results: dict[str, int] = {}
    fetch = getattr(backend, "fetch_layer_records", None)
    if not callable(fetch):
        return results

    try:
        all_rows: list[dict[str, Any]] = await asyncio.to_thread(fetch, layer="item", limit=4000)
    except Exception as exc:
        diagnostics["last_error"] = f"consolidation_fetch: {exc}"
        return results

    by_category: dict[str, list[dict[str, Any]]] = {}
    for row in all_rows:
        payload = row.get("payload", {})
        if not isinstance(payload, dict):
            continue
        meta = payload.get("metadata") or {}
        if bool(meta.get("consolidated", False)):
            continue
        mem_type = str(payload.get("memory_type", "") or "").strip()
        if mem_type not in ("event", ""):
            continue
        category = str(row.get("category", "") or "context").strip()
        by_category.setdefault(category, []).append(row)

    upsert = getattr(backend, "upsert_layer_record", None)
    for category, rows in by_category.items():
        if len(rows) < threshold:
            continue

        lines: list[str] = []
        for row in rows:
            payload = row.get("payload", {})
            text = str(payload.get("text", "") or "").strip()
            if text:
                lines.append(text)
        if not lines:
            continue

        summary = f"[{category}] {len(lines)} events: " + " | ".join(lines[:20])
        now = datetime.now(timezone.utc).isoformat()

        try:
            await asyncio.to_thread(
                add_record,
                summary,
                source="consolidation",
                memory_type="knowledge",
                metadata={"consolidated_from": category, "consolidated_count": len(lines)},
            )
        except Exception as exc:
            diagnostics["last_error"] = f"consolidation_add: {exc}"
            continue

        if callable(upsert):
            for row in rows:
                payload = row.get("payload", {})
                if not isinstance(payload, dict):
                    continue
                meta = dict(payload.get("metadata") or {})
                meta["consolidated"] = True
                meta["consolidated_at"] = now
                updated_payload = {**payload, "metadata": meta}
                try:
                    await asyncio.to_thread(
                        upsert,
                        layer=row.get("layer", "item"),
                        record_id=row["record_id"],
                        payload=updated_payload,
                        category=row.get("category", "context"),
                        created_at=row.get("created_at", now),
                        updated_at=now,
                    )
                except Exception:
                    pass

        results[category] = len(lines)

    return results
