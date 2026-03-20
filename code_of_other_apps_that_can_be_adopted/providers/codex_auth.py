from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def _codex_auth_path(path: str | Path | None = None) -> Path:
    raw = str(path or os.getenv("CLAWLITE_CODEX_AUTH_PATH", "") or "").strip()
    if raw:
        return Path(raw).expanduser()
    return Path.home() / ".codex" / "auth.json"


def _pick_value(payload: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = payload.get(key)
        text = str(value or "").strip()
        if text:
            return text
    return ""


def load_codex_auth_file(path: str | Path | None = None) -> dict[str, str]:
    auth_path = _codex_auth_path(path)
    empty = {
        "access_token": "",
        "account_id": "",
        "auth_mode": "",
        "source": "",
        "path": str(auth_path),
    }

    try:
        payload = json.loads(auth_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return dict(empty)

    if not isinstance(payload, dict):
        return dict(empty)

    tokens_payload = payload.get("tokens")
    tokens = dict(tokens_payload) if isinstance(tokens_payload, dict) else {}
    access_token = _pick_value(tokens, "access_token", "accessToken", "token") or _pick_value(
        payload,
        "access_token",
        "accessToken",
        "token",
    )
    account_id = _pick_value(tokens, "account_id", "accountId", "org_id", "orgId", "organization") or _pick_value(
        payload,
        "account_id",
        "accountId",
        "org_id",
        "orgId",
        "organization",
    )
    auth_mode = _pick_value(payload, "auth_mode", "authMode")

    return {
        "access_token": access_token,
        "account_id": account_id,
        "auth_mode": auth_mode,
        "source": f"file:{auth_path}" if access_token else "",
        "path": str(auth_path),
    }


def resolve_codex_auth_snapshot(
    *,
    config_token: str = "",
    config_account_id: str = "",
    config_source: str = "",
    env_token: str = "",
    env_token_name: str = "",
    env_account_id: str = "",
    file_auth: dict[str, str] | None = None,
) -> dict[str, str]:
    cfg_token = str(config_token or "").strip()
    cfg_account = str(config_account_id or "").strip()
    cfg_source = str(config_source or "").strip()
    file_payload = dict(file_auth or {})
    file_token = str(file_payload.get("access_token", "") or "").strip()
    file_account = str(file_payload.get("account_id", "") or "").strip()
    file_source = str(file_payload.get("source", "") or "").strip()
    source_is_file_snapshot = cfg_source.startswith("file:")

    if env_token:
        return {
            "access_token": str(env_token or "").strip(),
            "account_id": str(env_account_id or "").strip() or file_account or cfg_account,
            "source": f"env:{env_token_name}" if env_token_name else "env",
        }

    if source_is_file_snapshot and file_token:
        return {
            "access_token": file_token,
            "account_id": file_account or cfg_account,
            "source": file_source or cfg_source,
        }

    if cfg_token:
        return {
            "access_token": cfg_token,
            "account_id": cfg_account or file_account,
            "source": cfg_source or "config",
        }

    if file_token:
        return {
            "access_token": file_token,
            "account_id": file_account or cfg_account,
            "source": file_source,
        }

    return {
        "access_token": "",
        "account_id": cfg_account or file_account or str(env_account_id or "").strip(),
        "source": "disabled" if cfg_source == "disabled" else "",
    }
