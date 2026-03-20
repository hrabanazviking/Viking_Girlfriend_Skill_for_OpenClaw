from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable


CURATION_HINT_RE = re.compile(
    r"\b(remember|memory|prefer|preference|timezone|time zone|name|project|deadline|important|always|never|avoid|do not|don't|cannot|can't|must|language|stack)\b",
    re.IGNORECASE,
)


def candidate_importance(
    *,
    role: str,
    text: str,
    repeated_count: int,
    memory_type: str = "knowledge",
    happened_at: str = "",
    normalize_memory_type: Callable[[str], str],
    parse_iso_timestamp: Callable[[str], datetime],
) -> float:
    score = 1.0
    if role == "user":
        score += 0.5
    if CURATION_HINT_RE.search(text):
        score += 1.0
    score += min(0.8, len(text) / 320.0)
    score += min(2.0, max(0, repeated_count - 1) * 0.35)
    normalized_type = normalize_memory_type(memory_type)
    if normalized_type == "profile":
        score += 0.8
    elif normalized_type == "behavior":
        score += 0.45
    elif normalized_type in {"skill", "tool"}:
        score += 0.25
    elif normalized_type == "event":
        score += 0.15
        stamp = parse_iso_timestamp(str(happened_at or ""))
        if stamp.year > 1:
            if stamp.tzinfo is None:
                stamp = stamp.replace(tzinfo=timezone.utc)
            delta_days = float((stamp - datetime.now(timezone.utc)).total_seconds()) / 86400.0
            if -1.0 <= delta_days <= 45.0:
                score += 0.45
    return score


def extract_consolidation_lines(
    messages: Iterable[dict[str, str]],
    *,
    is_curation_candidate: Callable[[str, str], bool],
) -> list[str]:
    lines: list[str] = []
    for msg in messages:
        role = str(msg.get("role", "")).strip().lower()
        content = " ".join(str(msg.get("content", "")).split())
        if role not in {"user", "assistant"}:
            continue
        if not is_curation_candidate(role, content):
            continue
        lines.append(f"{role}: {content}")
    return lines


def build_consolidation_resource_text(messages: Iterable[dict[str, str]]) -> str:
    source_lines: list[str] = []
    for msg in messages:
        if not isinstance(msg, dict):
            continue
        role = str(msg.get("role", "")).strip().lower()
        content = " ".join(str(msg.get("content", "") or "").split())
        if role not in {"user", "assistant"} or not content:
            continue
        source_lines.append(f"{role}: {content}")
    return "\n".join(source_lines).strip()


def update_consolidation_checkpoints(
    *,
    checkpoints_path: Path,
    source: str,
    signature: str,
    summary: str,
    resource_text: str,
    parse_checkpoints: Callable[[str], dict[str, Any]],
    format_checkpoints: Callable[[dict[str, Any]], str],
    locked_file: Callable[..., Any],
    flush_and_fsync: Callable[[Any], None],
    utcnow_iso: Callable[[], str],
    add_record: Callable[[str, str], Any],
    diagnostics: dict[str, Any],
    max_checkpoint_sources: int | None = None,
    max_checkpoint_signatures: int | None = None,
) -> tuple[Any | None, int]:
    with locked_file(checkpoints_path, "r+", exclusive=True) as checkpoints_fh:
        checkpoints = parse_checkpoints(checkpoints_fh.read())
        source_signatures = checkpoints.get("source_signatures", {})
        if not isinstance(source_signatures, dict):
            source_signatures = {}

        source_activity = checkpoints.get("source_activity", {})
        if not isinstance(source_activity, dict):
            source_activity = {}

        global_signatures = checkpoints.get("global_signatures", {})
        if not isinstance(global_signatures, dict):
            global_signatures = {}

        if source_signatures.get(source) == signature:
            diagnostics["consolidate_dedup_hits"] = int(diagnostics.get("consolidate_dedup_hits", 0)) + 1
            return None, 0

        row = add_record(summary, resource_text or summary)
        diagnostics["consolidate_writes"] = int(diagnostics.get("consolidate_writes", 0)) + 1

        now_iso = utcnow_iso()
        source_signatures[source] = signature
        source_activity[source] = now_iso

        global_signature_row = global_signatures.get(signature)
        current_count = 0
        if isinstance(global_signature_row, dict):
            try:
                current_count = int(global_signature_row.get("count", 0))
            except Exception:
                current_count = 0
        repeated_count = max(1, current_count + 1)
        global_signatures[signature] = {
            "count": repeated_count,
            "last_seen_at": now_iso,
            "last_source": source,
        }

        if max_checkpoint_sources is not None and max_checkpoint_sources > 0 and len(source_signatures) > max_checkpoint_sources:
            ordered_sources = sorted(
                source_signatures.keys(),
                key=lambda key: source_activity.get(key, ""),
            )
            drop = len(source_signatures) - max_checkpoint_sources
            for key in ordered_sources[:drop]:
                source_signatures.pop(key, None)
                source_activity.pop(key, None)

        if max_checkpoint_signatures is not None and max_checkpoint_signatures > 0 and len(global_signatures) > max_checkpoint_signatures:
            ordered_signatures = sorted(
                global_signatures.keys(),
                key=lambda key: str(global_signatures.get(key, {}).get("last_seen_at", "")),
            )
            drop = len(global_signatures) - max_checkpoint_signatures
            for key in ordered_signatures[:drop]:
                global_signatures.pop(key, None)

        checkpoints = {
            "source_signatures": source_signatures,
            "source_activity": source_activity,
            "global_signatures": global_signatures,
        }
        checkpoints_fh.seek(0)
        checkpoints_fh.truncate()
        checkpoints_fh.write(format_checkpoints(checkpoints))
        flush_and_fsync(checkpoints_fh)
    return row, repeated_count


def curate_candidates(
    candidates: list[tuple[str, str]],
    *,
    source: str,
    repeated_count: int,
    metadata: dict[str, Any] | None,
    reasoning_layer: str | None,
    confidence: float | None,
    memory_type: str | None,
    happened_at: str | None,
    decay_rate: float | None,
    read_curated_facts: Callable[[], list[dict[str, object]]],
    write_curated_facts: Callable[[list[dict[str, object]]], None],
    normalize_memory_text: Callable[[str], str],
    source_session_key: Callable[[str], str],
    normalize_reasoning_layer: Callable[[Any], str],
    normalize_confidence: Callable[[Any], float],
    normalize_memory_type: Callable[[str], str],
    infer_memory_type: Callable[[str, str], str],
    infer_happened_at: Callable[[str], str],
    normalize_decay_rate: Callable[[Any], float],
    default_decay_rate: Callable[..., float],
    categorize_memory: Callable[[str, str], str],
    prepare_memory_metadata: Callable[..., dict[str, Any]],
    candidate_importance_fn: Callable[..., float],
    normalize_memory_metadata: Callable[[Any], dict[str, Any]],
    max_curated_sessions_per_fact: int,
    utcnow_iso: Callable[[], str],
) -> None:
    if not candidates:
        return

    facts = read_curated_facts()
    by_norm = {normalize_memory_text(str(item["text"])): item for item in facts}
    now_iso = utcnow_iso()
    source_session = source_session_key(source)
    resolved_reasoning_layer = normalize_reasoning_layer(reasoning_layer)
    resolved_confidence = normalize_confidence(confidence)
    changed = False

    for role, candidate in candidates:
        norm = normalize_memory_text(candidate)
        if not norm:
            continue
        inferred_memory_type = normalize_memory_type(memory_type or infer_memory_type(candidate, source))
        inferred_happened_at = str(happened_at or infer_happened_at(candidate) or "")
        inferred_decay_rate = normalize_decay_rate(
            decay_rate,
            default=default_decay_rate(
                memory_type=inferred_memory_type,
                category=categorize_memory(candidate, source),
                happened_at=inferred_happened_at,
            ),
        )
        inferred_metadata = prepare_memory_metadata(
            text=candidate,
            source=source,
            metadata=metadata,
            memory_type=inferred_memory_type,
            happened_at=inferred_happened_at,
        )
        existing = by_norm.get(norm)
        if existing is None:
            row: dict[str, object] = {
                "id": uuid.uuid4().hex,
                "text": candidate,
                "source": f"curated:{source}",
                "created_at": now_iso,
                "last_seen_at": now_iso,
                "mentions": 1,
                "session_count": 1,
                "sessions": [source_session],
                "importance": candidate_importance_fn(
                    role=role,
                    text=candidate,
                    repeated_count=repeated_count,
                    memory_type=inferred_memory_type,
                    happened_at=inferred_happened_at,
                ),
                "reasoning_layer": resolved_reasoning_layer,
                "confidence": resolved_confidence,
                "decay_rate": inferred_decay_rate,
                "memory_type": inferred_memory_type,
                "happened_at": inferred_happened_at,
                "metadata": inferred_metadata,
            }
            facts.append(row)
            by_norm[norm] = row
            changed = True
            continue

        existing_sessions = existing.get("sessions", [])
        if not isinstance(existing_sessions, list):
            existing_sessions = []
        clean_sessions = []
        for raw_session in existing_sessions:
            clean = str(raw_session or "").strip().lower()
            if clean and clean not in clean_sessions:
                clean_sessions.append(clean)
        if source_session not in clean_sessions:
            clean_sessions.append(source_session)

        old_mentions = int(existing.get("mentions", 1))
        old_session_count = int(existing.get("session_count", max(1, len(clean_sessions))))
        old_importance = float(existing.get("importance", 1.0))
        existing["mentions"] = old_mentions + 1
        existing["session_count"] = max(old_session_count, len(clean_sessions))
        existing["last_seen_at"] = now_iso
        existing["sessions"] = clean_sessions[-max_curated_sessions_per_fact:]
        existing["importance"] = old_importance + candidate_importance_fn(
            role=role,
            text=candidate,
            repeated_count=repeated_count,
            memory_type=inferred_memory_type,
            happened_at=inferred_happened_at,
        ) * 0.35
        existing["reasoning_layer"] = resolved_reasoning_layer
        existing["confidence"] = resolved_confidence
        existing["decay_rate"] = normalize_decay_rate(
            min(
                normalize_decay_rate(existing.get("decay_rate", existing.get("decayRate", inferred_decay_rate)), default=inferred_decay_rate),
                inferred_decay_rate,
            )
            * 0.9,
            default=inferred_decay_rate,
        )
        existing["memory_type"] = inferred_memory_type
        existing["happened_at"] = inferred_happened_at
        existing["metadata"] = normalize_memory_metadata(
            {
                **normalize_memory_metadata(existing.get("metadata", {})),
                **inferred_metadata,
            }
        )
        changed = True

    if changed:
        write_curated_facts(facts)


def consolidate_messages(
    messages: Iterable[dict[str, str]],
    *,
    source: str,
    checkpoints_path: Path,
    extract_consolidation_lines: Callable[[Iterable[dict[str, str]]], list[str]],
    chunk_signature: Callable[[list[str]], str],
    parse_checkpoints: Callable[[str], dict[str, Any]],
    format_checkpoints: Callable[[dict[str, Any]], str],
    locked_file: Callable[..., Any],
    flush_and_fsync: Callable[[Any], None],
    utcnow_iso: Callable[[], str],
    add_record: Callable[[str, str], Any],
    diagnostics: dict[str, Any],
    curate_candidates_fn: Callable[[list[tuple[str, str]], int], None],
    max_checkpoint_sources: int | None = None,
    max_checkpoint_signatures: int | None = None,
) -> Any | None:
    lines = extract_consolidation_lines(messages)
    if not lines:
        return None

    summary_lines = lines[-6:]
    summary = "\n".join(summary_lines)
    signature = chunk_signature(summary_lines)
    resource_text = build_consolidation_resource_text(messages)
    row, repeated_count = update_consolidation_checkpoints(
        checkpoints_path=checkpoints_path,
        source=source,
        signature=signature,
        summary=summary,
        resource_text=resource_text,
        parse_checkpoints=parse_checkpoints,
        format_checkpoints=format_checkpoints,
        locked_file=locked_file,
        flush_and_fsync=flush_and_fsync,
        utcnow_iso=utcnow_iso,
        add_record=add_record,
        diagnostics=diagnostics,
        max_checkpoint_sources=max_checkpoint_sources,
        max_checkpoint_signatures=max_checkpoint_signatures,
    )
    if row is None:
        return None

    curated_candidates: list[tuple[str, str]] = []
    for line in summary_lines:
        if ":" not in line:
            continue
        role, value = line.split(":", 1)
        curated_candidates.append((role.strip().lower(), value.strip()))
    if curated_candidates:
        curate_candidates_fn(curated_candidates, repeated_count)
    return row
