from __future__ import annotations

import base64
import json
import os
import time
from pathlib import Path
from typing import Any

import httpx


GOOGLE_OAUTH_TOKEN_URL = "https://oauth2.googleapis.com/token"


def _read_oauth_payload(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _pick_value(payload: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = str(payload.get(key, "") or "").strip()
        if value:
            return value
    return ""


def _extract_client_id_from_id_token(id_token: str) -> str:
    token = str(id_token or "").strip()
    if not token:
        return ""
    parts = token.split(".")
    if len(parts) < 2:
        return ""
    payload_part = parts[1]
    padding = "=" * (-len(payload_part) % 4)
    try:
        decoded = base64.urlsafe_b64decode((payload_part + padding).encode("utf-8"))
        payload = json.loads(decoded.decode("utf-8"))
    except Exception:
        return ""
    if not isinstance(payload, dict):
        return ""
    return _pick_value(payload, "azp", "aud")


def _token_target(payload: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    tokens = payload.get("tokens")
    if isinstance(tokens, dict):
        return tokens, True
    return payload, False


def load_gemini_auth_state(path: str | Path | None = None) -> dict[str, str]:
    raw_path = str(path or os.getenv("CLAWLITE_GEMINI_AUTH_PATH", "") or "").strip()
    candidates: list[Path] = []
    if raw_path:
        candidates.append(Path(raw_path).expanduser())
    candidates.append(Path.home() / ".gemini" / "oauth_creds.json")

    for candidate in candidates:
        payload = _read_oauth_payload(candidate)
        if not payload:
            continue
        source_payload, has_tokens_block = _token_target(payload)
        token = _pick_value(source_payload, "access_token", "accessToken", "token")
        refresh_token = _pick_value(source_payload, "refresh_token", "refreshToken")
        account_id = _pick_value(source_payload, "account_id", "accountId", "organization")
        id_token = _pick_value(source_payload, "id_token", "idToken")
        client_id = (
            _pick_value(
                source_payload,
                "client_id",
                "clientId",
                "oauth_client_id",
                "oauthClientId",
            )
            or _pick_value(
                payload,
                "client_id",
                "clientId",
                "oauth_client_id",
                "oauthClientId",
            )
            or os.getenv("GEMINI_OAUTH_CLIENT_ID", "").strip()
            or _extract_client_id_from_id_token(id_token)
        )
        client_secret = (
            _pick_value(
                source_payload,
                "client_secret",
                "clientSecret",
                "oauth_client_secret",
                "oauthClientSecret",
            )
            or _pick_value(
                payload,
                "client_secret",
                "clientSecret",
                "oauth_client_secret",
                "oauthClientSecret",
            )
            or os.getenv("GEMINI_OAUTH_CLIENT_SECRET", "").strip()
        )
        token_url = (
            _pick_value(
                payload,
                "token_url",
                "tokenUrl",
                "oauth_token_url",
                "oauthTokenUrl",
            )
            or GOOGLE_OAUTH_TOKEN_URL
        )
        if token or refresh_token:
            return {
                "access_token": token,
                "refresh_token": refresh_token,
                "account_id": account_id,
                "client_id": client_id,
                "client_secret": client_secret,
                "token_url": token_url,
                "source": f"file:{candidate}" if token else "",
                "path": str(candidate),
                "id_token": id_token,
                "has_tokens_block": "true" if has_tokens_block else "false",
            }
    return {
        "access_token": "",
        "refresh_token": "",
        "account_id": "",
        "client_id": os.getenv("GEMINI_OAUTH_CLIENT_ID", "").strip(),
        "client_secret": os.getenv("GEMINI_OAUTH_CLIENT_SECRET", "").strip(),
        "token_url": GOOGLE_OAUTH_TOKEN_URL,
        "source": "",
        "path": str(candidates[-1]) if candidates else str(Path.home() / ".gemini" / "oauth_creds.json"),
        "id_token": "",
        "has_tokens_block": "false",
    }


def load_gemini_auth_file(path: str | Path | None = None) -> dict[str, str]:
    state = load_gemini_auth_state(path)
    return {
        "access_token": str(state.get("access_token", "") or "").strip(),
        "account_id": str(state.get("account_id", "") or "").strip(),
        "source": str(state.get("source", "") or "").strip(),
    }


def _persist_gemini_auth_state(
    *,
    path: Path,
    payload: dict[str, Any],
    access_token: str,
    refresh_token: str,
    expires_in: int | None,
) -> dict[str, str]:
    updated = dict(payload) if isinstance(payload, dict) else {}
    target, has_tokens_block = _token_target(updated)
    target["access_token"] = access_token
    if refresh_token:
        target["refresh_token"] = refresh_token
    expiry_millis = None
    if expires_in is not None and expires_in > 0:
        expiry_millis = int(time.time() * 1000) + (int(expires_in) * 1000)
        target["expiry_date"] = expiry_millis
        target["expires_at"] = expiry_millis
    if has_tokens_block:
        updated["tokens"] = target
    else:
        updated.update(target)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(updated, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "account_id": _pick_value(target, "account_id", "accountId", "organization"),
        "source": f"file:{path}",
        "path": str(path),
    }


async def refresh_gemini_auth_file(path: str | Path | None = None, *, timeout: float = 15.0) -> dict[str, str]:
    state = load_gemini_auth_state(path)
    refresh_token = str(state.get("refresh_token", "") or "").strip()
    auth_path = Path(str(state.get("path", "") or "")).expanduser()
    if not refresh_token or not auth_path:
        raise RuntimeError("provider_oauth_refresh_unavailable:gemini_oauth")

    client_id = str(state.get("client_id", "") or "").strip()
    client_secret = str(state.get("client_secret", "") or "").strip()
    token_url = str(state.get("token_url", "") or GOOGLE_OAUTH_TOKEN_URL).strip() or GOOGLE_OAUTH_TOKEN_URL

    form: dict[str, str] = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    if client_id:
        form["client_id"] = client_id
    if client_secret:
        form["client_secret"] = client_secret

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            token_url,
            data=form,
            headers={
                "content-type": "application/x-www-form-urlencoded",
                "accept": "application/json",
            },
        )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise RuntimeError("provider_oauth_refresh_invalid_payload:gemini_oauth")

    access_token = _pick_value(payload, "access_token", "accessToken", "token")
    if not access_token:
        raise RuntimeError("provider_oauth_refresh_missing_token:gemini_oauth")
    next_refresh_token = _pick_value(payload, "refresh_token", "refreshToken") or refresh_token
    expires_in_raw = payload.get("expires_in", payload.get("expiresIn"))
    try:
        expires_in = int(expires_in_raw) if expires_in_raw is not None else None
    except Exception:
        expires_in = None

    original_payload = _read_oauth_payload(auth_path)
    return _persist_gemini_auth_state(
        path=auth_path,
        payload=original_payload,
        access_token=access_token,
        refresh_token=next_refresh_token,
        expires_in=expires_in,
    )
