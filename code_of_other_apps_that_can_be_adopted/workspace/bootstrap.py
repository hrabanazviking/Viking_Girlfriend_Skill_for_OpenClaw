from __future__ import annotations

import secrets
from pathlib import Path
from typing import Any

from clawlite.config.loader import load_config, save_config
from clawlite.workspace.loader import WorkspaceLoader


def bootstrap_install_workspace(
    *,
    config_path: str | Path | None = None,
    profile: str | None = None,
) -> dict[str, Any]:
    cfg = load_config(config_path, profile=profile)
    created_or_updated = WorkspaceLoader(workspace_path=cfg.workspace_path).bootstrap()

    existing_token = str(cfg.gateway.auth.token or "").strip()
    token_seeded = False
    if not existing_token:
        cfg.gateway.auth.token = secrets.token_urlsafe(24)
        token_seeded = True

    saved_path = save_config(cfg, path=config_path)
    return {
        "ok": True,
        "workspace_path": str(cfg.workspace_path),
        "saved_path": str(saved_path),
        "created_or_updated_count": len(created_or_updated),
        "token_seeded": token_seeded,
        "gateway_auth_token_configured": bool(str(cfg.gateway.auth.token or "").strip()),
    }


__all__ = ["bootstrap_install_workspace"]
