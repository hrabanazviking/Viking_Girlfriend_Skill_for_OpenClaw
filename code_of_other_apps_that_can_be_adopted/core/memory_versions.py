from __future__ import annotations

import gzip
import json
import re
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


def export_memory_payload(
    *,
    history_rows: list[Any],
    curated_rows: list[Any],
    checkpoints_path: Path,
    parse_checkpoints: Callable[[str], dict[str, dict[str, object]]],
    profile_path: Path,
    privacy_path: Path,
    load_json_dict: Callable[[Path, dict[str, Any]], dict[str, Any]],
    default_profile: Callable[[], dict[str, Any]],
    default_privacy: Callable[[], dict[str, Any]],
    utcnow_iso: Callable[[], str],
) -> dict[str, Any]:
    checkpoints_raw = checkpoints_path.read_text(encoding="utf-8") if checkpoints_path.exists() else ""
    return {
        "version": 1,
        "exported_at": utcnow_iso(),
        "history": [asdict(row) for row in history_rows],
        "curated": [asdict(row) for row in curated_rows],
        "checkpoints": parse_checkpoints(checkpoints_raw),
        "profile": load_json_dict(profile_path, default_profile()),
        "privacy": load_json_dict(privacy_path, default_privacy()),
    }


def import_memory_payload(
    *,
    payload: dict[str, Any],
    record_from_payload: Callable[[dict[str, Any]], Any | None],
    encrypt_text_for_category: Callable[[str, str], str],
    atomic_write_text_locked: Callable[[Path, str], None],
    history_path: Path,
    curated_enabled: bool,
    write_curated_facts: Callable[[list[dict[str, object]]], None],
    checkpoints_path: Path,
    format_checkpoints: Callable[[dict[str, dict[str, object]]], str],
    profile_path: Path,
    privacy_path: Path,
    write_json_dict: Callable[[Path, dict[str, Any]], None],
    default_profile: Callable[[], dict[str, Any]],
    default_privacy: Callable[[], dict[str, Any]],
) -> None:
    if not isinstance(payload, dict):
        return
    history_rows = payload.get("history", [])
    curated_rows = payload.get("curated", [])
    checkpoints = payload.get("checkpoints", {})
    profile = payload.get("profile", {})
    privacy = payload.get("privacy", {})

    history_lines: list[str] = []
    if isinstance(history_rows, list):
        for row in history_rows:
            if not isinstance(row, dict):
                continue
            parsed = record_from_payload(row)
            if parsed is None:
                continue
            stored = asdict(parsed)
            stored["text"] = encrypt_text_for_category(str(parsed.text or ""), parsed.category)
            history_lines.append(json.dumps(stored, ensure_ascii=False))
    atomic_write_text_locked(history_path, ("\n".join(history_lines) + "\n") if history_lines else "")

    if curated_enabled and isinstance(curated_rows, list):
        facts = [row for row in curated_rows if isinstance(row, dict)]
        write_curated_facts(facts)

    if isinstance(checkpoints, dict):
        atomic_write_text_locked(checkpoints_path, format_checkpoints(checkpoints))

    if isinstance(profile, dict):
        merged_profile = default_profile()
        merged_profile.update(profile)
        write_json_dict(profile_path, merged_profile)

    if isinstance(privacy, dict):
        merged_privacy = default_privacy()
        merged_privacy.update(privacy)
        write_json_dict(privacy_path, merged_privacy)


def write_snapshot_payload(
    *,
    payload: dict[str, Any],
    versions_path: Path,
    tag: str = "",
    advance_branch: bool = True,
    branch_name: str = "",
    current_branch_name: Callable[[], str],
    advance_branch_head: Callable[[str, str], None],
) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    safe_tag = re.sub(r"[^a-zA-Z0-9_-]+", "-", str(tag or "").strip()).strip("-")
    version_id = f"{stamp}-{safe_tag}" if safe_tag else stamp
    version_path = versions_path / f"{version_id}.json.gz"
    with gzip.open(version_path, "wt", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False)
    if advance_branch:
        current_branch = branch_name or current_branch_name()
        advance_branch_head(current_branch, version_id)
    return version_id


def create_memory_branch(
    *,
    name: str,
    from_version: str = "",
    checkout: bool = False,
    load_branches_metadata: Callable[[], dict[str, Any]],
    save_branches_metadata: Callable[[dict[str, Any]], None],
    sync_branch_head_file: Callable[[], None],
    current_branch_head: Callable[[], str],
    utcnow_iso: Callable[[], str],
) -> dict[str, Any]:
    clean_name = re.sub(r"[^a-zA-Z0-9_.-]+", "-", str(name or "").strip()).strip("-")
    if not clean_name:
        raise ValueError("branch name is required")
    meta = load_branches_metadata()
    branches = meta.get("branches", {})
    if not isinstance(branches, dict):
        branches = {}
    if clean_name in branches:
        raise ValueError(f"branch already exists: {clean_name}")

    base_version = str(from_version or "").strip() or current_branch_head()
    now_iso = utcnow_iso()
    branches[clean_name] = {
        "head": base_version,
        "created_at": now_iso,
        "updated_at": now_iso,
    }
    meta["branches"] = branches
    if checkout:
        meta["current"] = clean_name
    save_branches_metadata(meta)
    sync_branch_head_file()
    return {
        "name": clean_name,
        "head": base_version,
        "current": str(meta.get("current", "main") or "main"),
        "checkout": bool(checkout),
    }


def list_memory_branches(*, load_branches_metadata: Callable[[], dict[str, Any]]) -> dict[str, Any]:
    meta = load_branches_metadata()
    return {
        "current": str(meta.get("current", "main") or "main"),
        "branches": meta.get("branches", {}),
    }


def checkout_memory_branch(
    *,
    name: str,
    set_current_branch: Callable[[str], None],
    current_branch_head: Callable[[], str],
) -> dict[str, Any]:
    clean_name = str(name or "").strip()
    if not clean_name:
        raise ValueError("branch name is required")
    set_current_branch(clean_name)
    return {"current": clean_name, "head": current_branch_head()}


def load_version_payload(*, versions_path: Path, version_id: str) -> dict[str, Any]:
    clean_version_id = str(version_id or "").strip()
    if not clean_version_id:
        return {}
    version_path = versions_path / f"{clean_version_id}.json.gz"
    if not version_path.exists():
        return {}
    with gzip.open(version_path, "rt", encoding="utf-8") as fh:
        payload = json.load(fh)
    return payload if isinstance(payload, dict) else {}


def merge_record_lists(preferred: list[dict[str, Any]], fallback: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for row in fallback:
        if not isinstance(row, dict):
            continue
        row_id = str(row.get("id", "")).strip()
        if row_id:
            merged[row_id] = dict(row)
    for row in preferred:
        if not isinstance(row, dict):
            continue
        row_id = str(row.get("id", "")).strip()
        if row_id:
            merged[row_id] = dict(row)
    return sorted(merged.values(), key=lambda item: (str(item.get("created_at", "")), str(item.get("id", ""))))


def merge_profile_conservative(source: dict[str, Any], target: dict[str, Any]) -> dict[str, Any]:
    merged = dict(target)
    for key, value in source.items():
        current_value = merged.get(key)
        if key not in merged or current_value is None or current_value == "" or current_value == [] or current_value == {}:
            merged[key] = value
    source_interests = source.get("interests", [])
    target_interests = target.get("interests", [])
    if isinstance(source_interests, list) and isinstance(target_interests, list):
        merged["interests"] = sorted({str(item) for item in source_interests + target_interests if str(item).strip()})
    return merged


def merge_privacy_conservative(source: dict[str, Any], target: dict[str, Any]) -> dict[str, Any]:
    merged = dict(target)
    for key in ("never_memorize_patterns", "ephemeral_categories", "encrypted_categories"):
        src_list = source.get(key, [])
        tgt_list = target.get(key, [])
        if isinstance(src_list, list) and isinstance(tgt_list, list):
            merged[key] = sorted({str(item) for item in src_list + tgt_list if str(item).strip()})
    src_ttl = source.get("ephemeral_ttl_days")
    tgt_ttl = target.get("ephemeral_ttl_days")
    try:
        src_ttl_i = int(src_ttl)
    except Exception:
        src_ttl_i = 0
    try:
        tgt_ttl_i = int(tgt_ttl)
    except Exception:
        tgt_ttl_i = 0
    ttl_candidates = [val for val in (src_ttl_i, tgt_ttl_i) if val > 0]
    if ttl_candidates:
        merged["ephemeral_ttl_days"] = min(ttl_candidates)
    merged["audit_log"] = bool(source.get("audit_log", True)) and bool(target.get("audit_log", True))
    return merged


def merge_memory_branches(
    *,
    source_branch: str,
    target_branch: str,
    tag: str = "merge",
    load_branches_metadata: Callable[[], dict[str, Any]],
    save_branches_metadata: Callable[[dict[str, Any]], None],
    sync_branch_head_file: Callable[[], None],
    versions_path: Path,
    utcnow_iso: Callable[[], str],
    write_snapshot_payload: Callable[..., str],
    import_payload: Callable[[dict[str, Any]], None],
) -> dict[str, Any]:
    meta = load_branches_metadata()
    branches = meta.get("branches", {})
    if not isinstance(branches, dict):
        raise ValueError("branch metadata missing")
    source_row = branches.get(source_branch)
    target_row = branches.get(target_branch)
    if not isinstance(source_row, dict) or not isinstance(target_row, dict):
        raise ValueError("source or target branch not found")

    source_head = str(source_row.get("head", "") or "")
    target_head = str(target_row.get("head", "") or "")
    if not source_head or not target_head:
        raise ValueError("source and target branches must have head versions")

    source_payload = load_version_payload(versions_path=versions_path, version_id=source_head)
    target_payload = load_version_payload(versions_path=versions_path, version_id=target_head)
    merged_payload = {
        "version": 1,
        "exported_at": utcnow_iso(),
        "history": merge_record_lists(
            list(source_payload.get("history", [])) if isinstance(source_payload.get("history", []), list) else [],
            list(target_payload.get("history", [])) if isinstance(target_payload.get("history", []), list) else [],
        ),
        "curated": merge_record_lists(
            list(source_payload.get("curated", [])) if isinstance(source_payload.get("curated", []), list) else [],
            list(target_payload.get("curated", [])) if isinstance(target_payload.get("curated", []), list) else [],
        ),
        "checkpoints": target_payload.get("checkpoints", {}),
        "profile": merge_profile_conservative(
            dict(source_payload.get("profile", {})) if isinstance(source_payload.get("profile", {}), dict) else {},
            dict(target_payload.get("profile", {})) if isinstance(target_payload.get("profile", {}), dict) else {},
        ),
        "privacy": merge_privacy_conservative(
            dict(source_payload.get("privacy", {})) if isinstance(source_payload.get("privacy", {}), dict) else {},
            dict(target_payload.get("privacy", {})) if isinstance(target_payload.get("privacy", {}), dict) else {},
        ),
    }

    version_id = write_snapshot_payload(
        merged_payload,
        tag=f"{tag}-{source_branch}-into-{target_branch}",
        advance_branch=False,
    )
    meta = load_branches_metadata()
    branches = meta.get("branches", {})
    if not isinstance(branches, dict):
        branches = {}
    target_meta = branches.get(target_branch, {})
    if not isinstance(target_meta, dict):
        target_meta = {}
    target_meta["head"] = version_id
    target_meta["updated_at"] = utcnow_iso()
    if "created_at" not in target_meta:
        target_meta["created_at"] = utcnow_iso()
    branches[target_branch] = target_meta
    meta["branches"] = branches
    save_branches_metadata(meta)
    sync_branch_head_file()

    current_branch = str(meta.get("current", "main") or "main")
    imported = False
    if current_branch == target_branch:
        import_payload(merged_payload)
        imported = True
    return {
        "source": source_branch,
        "target": target_branch,
        "source_head": source_head,
        "target_head_before": target_head,
        "target_head_after": version_id,
        "version": version_id,
        "imported": imported,
    }


def rollback_memory_version(
    *,
    version_id: str,
    versions_path: Path,
    import_payload: Callable[[dict[str, Any]], None],
) -> None:
    clean_version_id = str(version_id or "").strip()
    if not clean_version_id:
        return
    version_path = versions_path / f"{clean_version_id}.json.gz"
    if not version_path.exists():
        raise FileNotFoundError(str(version_path))
    payload = load_version_payload(versions_path=versions_path, version_id=clean_version_id)
    import_payload(payload)


def diff_memory_versions(*, versions_path: Path, version_a: str, version_b: str) -> dict[str, Any]:
    left = load_version_payload(versions_path=versions_path, version_id=version_a)
    right = load_version_payload(versions_path=versions_path, version_id=version_b)

    left_history = {
        str(item.get("id", "")): str(item.get("text", ""))
        for item in left.get("history", [])
        if isinstance(item, dict) and str(item.get("id", "")).strip()
    }
    right_history = {
        str(item.get("id", "")): str(item.get("text", ""))
        for item in right.get("history", [])
        if isinstance(item, dict) and str(item.get("id", "")).strip()
    }
    left_ids = set(left_history.keys())
    right_ids = set(right_history.keys())
    added_ids = sorted(right_ids - left_ids)
    removed_ids = sorted(left_ids - right_ids)
    changed_ids = sorted(
        row_id for row_id in left_ids.intersection(right_ids) if left_history.get(row_id) != right_history.get(row_id)
    )

    return {
        "added": {row_id: right_history[row_id] for row_id in added_ids},
        "removed": {row_id: left_history[row_id] for row_id in removed_ids},
        "changed": {
            row_id: {"from": left_history[row_id], "to": right_history[row_id]}
            for row_id in changed_ids
        },
        "counts": {
            "added": len(added_ids),
            "removed": len(removed_ids),
            "changed": len(changed_ids),
        },
    }
