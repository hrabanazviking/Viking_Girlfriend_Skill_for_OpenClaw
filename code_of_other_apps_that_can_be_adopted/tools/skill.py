from __future__ import annotations

import asyncio
import base64
import importlib.util
import inspect
import json
import os
import shlex
import shutil
import sys
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus, urlencode

import httpx

from clawlite.core.skills import SkillsLoader
from clawlite.tools.base import Tool, ToolContext
from clawlite.tools.registry import ToolRegistry
from clawlite.utils.logging import bind_event


class SkillTool(Tool):
    """Execute skills discovered by `SkillsLoader`.

    This tool is required to turn SKILL.md discovery into actual execution.
    Without it, skills would appear in prompt context but would not be callable.
    """

    name = "run_skill"
    description = "Execute a discovered SKILL.md binding with deterministic contracts."

    MAX_TIMEOUT_SECONDS = 120.0
    MAX_SKILL_ARGS = 32
    MAX_ARG_CHARS = 4000
    SUMMARY_MAX_SOURCE_CHARS = 12000

    def __init__(
        self,
        *,
        loader: SkillsLoader,
        registry: ToolRegistry,
        memory: Any | None = None,
        provider: Any | None = None,
    ) -> None:
        self.loader = loader
        self.registry = registry
        self.memory = memory
        self.provider = provider

    @staticmethod
    def _policy_reason(raw: Any) -> str:
        text = str(raw or "").strip()
        if not text:
            return "unspecified"
        return text.replace("\n", " ").replace("\r", " ")

    async def _memory_policy_allows(self, *, session_id: str) -> tuple[bool, str]:
        memory = self.memory
        if memory is None:
            return True, ""

        policy_fn = getattr(memory, "integration_policy", None)
        if not callable(policy_fn):
            return True, ""

        try:
            verdict = policy_fn("skill", session_id=session_id)
            if inspect.isawaitable(verdict):
                verdict = await verdict
        except Exception as exc:
            return False, f"policy_exception:{exc.__class__.__name__.lower()}"

        if isinstance(verdict, bool):
            return verdict, "" if verdict else "blocked"

        if isinstance(verdict, dict):
            allowed_raw = verdict.get("allowed", verdict.get("allow", verdict.get("ok", True)))
            allowed = bool(allowed_raw)
            reason = self._policy_reason(verdict.get("reason", verdict.get("message", verdict.get("detail", ""))))
            return allowed, reason if not allowed else ""

        allowed_attr = getattr(verdict, "allowed", None)
        if allowed_attr is not None:
            allowed = bool(allowed_attr)
            reason = self._policy_reason(getattr(verdict, "reason", ""))
            return allowed, reason if not allowed else ""

        return True, ""

    def args_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "input": {"type": "string"},
                "args": {"type": "array", "items": {"type": "string"}},
                "timeout": {"type": "number", "default": 30},
                "query": {"type": "string"},
                "location": {"type": "string"},
                "tool_arguments": {"type": "object"},
            },
            "required": ["name"],
        }

    @staticmethod
    def _extra_args(arguments: dict[str, Any]) -> list[str]:
        values = arguments.get("args")
        if isinstance(values, list):
            return [str(item) for item in values if str(item).strip()]
        raw = str(arguments.get("input", "")).strip()
        return shlex.split(raw) if raw else []

    @classmethod
    def _guard_extra_args(cls, values: list[str]) -> str | None:
        if len(values) > cls.MAX_SKILL_ARGS:
            return f"skill_args_exceeded:max={cls.MAX_SKILL_ARGS}"
        for value in values:
            if len(value) > cls.MAX_ARG_CHARS:
                return f"skill_arg_too_large:max_chars={cls.MAX_ARG_CHARS}"
            if "\x00" in value or "\n" in value or "\r" in value:
                return "skill_arg_invalid_character"
        return None

    @classmethod
    def _timeout_value(cls, arguments: dict[str, Any]) -> float:
        raw = float(arguments.get("timeout", 30) or 30)
        if raw < 1:
            return 1.0
        if raw > cls.MAX_TIMEOUT_SECONDS:
            return cls.MAX_TIMEOUT_SECONDS
        return raw

    @staticmethod
    def _join_command(argv: list[str]) -> str:
        if not argv:
            return ""
        return shlex.join(argv)

    async def _run_command_via_exec_tool(
        self,
        *,
        spec_name: str,
        argv: list[str],
        timeout: float,
        ctx: ToolContext,
        env_overrides: dict[str, str] | None = None,
    ) -> str:
        command = self._join_command(argv)
        if not command:
            raise ValueError("empty command")
        tool_arguments: dict[str, Any] = {"command": command, "timeout": timeout}
        if env_overrides:
            tool_arguments["env"] = dict(env_overrides)
        try:
            return await self.registry.execute(
                "exec",
                tool_arguments,
                session_id=ctx.session_id,
                channel=ctx.channel,
                user_id=ctx.user_id,
            )
        except RuntimeError as exc:
            error = str(exc)
            if error.startswith("tool_blocked_by_safety_policy:exec:"):
                return f"skill_blocked:{spec_name}:{error}"
            if error.startswith("tool_requires_approval:exec:"):
                return f"skill_requires_approval:{spec_name}:{error}"
            raise

    @staticmethod
    def _exec_output_exit_code(payload: str) -> int | None:
        line = str(payload or "").splitlines()[0:1]
        if not line or not line[0].startswith("exit="):
            return None
        try:
            return int(line[0].split("=", 1)[1].strip())
        except ValueError:
            return None

    @staticmethod
    def _exec_output_stream(payload: str, key: str) -> str:
        prefix = f"{key}="
        for line in str(payload or "").splitlines():
            if line.startswith(prefix):
                return line[len(prefix) :].strip()
        return ""

    @staticmethod
    def _weather_code_description(code: int) -> str:
        mapping = {
            0: "clear sky",
            1: "mainly clear",
            2: "partly cloudy",
            3: "overcast",
            45: "fog",
            48: "rime fog",
            51: "light drizzle",
            53: "moderate drizzle",
            55: "dense drizzle",
            61: "slight rain",
            63: "moderate rain",
            65: "heavy rain",
            71: "slight snow",
            73: "moderate snow",
            75: "heavy snow",
            80: "rain showers",
            81: "strong rain showers",
            82: "violent rain showers",
            95: "thunderstorm",
        }
        return mapping.get(int(code), "unknown")

    @staticmethod
    def _web_fetch_error_message(payload: dict[str, Any], default: str) -> str:
        error = payload.get("error", {}) if isinstance(payload, dict) else {}
        if isinstance(error, dict):
            message = str(error.get("message", "") or "").strip()
            if message:
                return message
            code = str(error.get("code", "") or "").strip()
            if code:
                return code
        return default

    @staticmethod
    def _web_fetch_result_text(payload: dict[str, Any]) -> str:
        result = payload.get("result", {}) if isinstance(payload, dict) else {}
        if not isinstance(result, dict):
            return ""
        return str(result.get("text", "") or "").strip()

    async def _fetch_web_payload(
        self,
        *,
        url: str,
        ctx: ToolContext,
        max_chars: int,
        mode: str = "auto",
        unavailable_reason: str = "weather_fetch_unavailable",
        failure_reason: str = "weather_fetch_failed",
    ) -> dict[str, Any]:
        if self.registry.get("web_fetch") is None:
            raise RuntimeError(unavailable_reason)

        tool_arguments: dict[str, Any] = {"url": url, "max_chars": max_chars}
        if mode != "auto":
            tool_arguments["mode"] = mode

        try:
            raw = await self.registry.execute(
                "web_fetch",
                tool_arguments,
                session_id=ctx.session_id,
                channel=ctx.channel,
                user_id=ctx.user_id,
            )
        except RuntimeError as exc:
            message = str(exc or "").strip() or failure_reason
            if message.startswith("tool_blocked_by_safety_policy:web_fetch:"):
                raise RuntimeError(message) from exc
            if message.startswith("tool_requires_approval:web_fetch:"):
                raise RuntimeError(message) from exc
            raise RuntimeError(f"{failure_reason}:{message}") from exc

        try:
            decoded = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"{failure_reason}:invalid_payload") from exc
        if not isinstance(decoded, dict):
            raise RuntimeError(f"{failure_reason}:invalid_payload")
        return decoded

    @classmethod
    def _web_fetch_json_payload(cls, payload: dict[str, Any], *, failure_reason: str) -> dict[str, Any]:
        text = cls._web_fetch_result_text(payload)
        if not text:
            raise RuntimeError(f"{failure_reason}:empty_payload")
        try:
            decoded = json.loads(text)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"{failure_reason}:invalid_payload") from exc
        if not isinstance(decoded, dict):
            raise RuntimeError(f"{failure_reason}:invalid_payload")
        return decoded

    async def _run_weather(self, arguments: dict[str, Any], ctx: ToolContext, *, spec_name: str) -> str:
        location = str(arguments.get("location") or arguments.get("input") or "").strip()
        if not location:
            location = "Sao Paulo"

        wttr_url = f"https://wttr.in/{quote_plus(location)}?format=3"
        try:
            wttr_payload = await self._fetch_web_payload(
                url=wttr_url,
                ctx=ctx,
                max_chars=256,
                failure_reason="weather_fetch_failed",
            )
        except RuntimeError as exc:
            reason = str(exc or "").strip() or "weather_fetch_failed"
            if (
                reason == "weather_fetch_unavailable"
                or reason.startswith("tool_blocked_by_safety_policy:web_fetch:")
                or reason.startswith("tool_requires_approval:web_fetch:")
            ):
                return f"skill_blocked:{spec_name}:{reason}"
            wttr_payload = {"ok": False, "error": {"message": reason}}

        if wttr_payload.get("ok"):
            wttr_text = self._web_fetch_result_text(wttr_payload)
            if wttr_text:
                return wttr_text

        geocode_url = "https://geocoding-api.open-meteo.com/v1/search?" + urlencode(
            {"name": location, "count": 1, "language": "en", "format": "json"}
        )
        try:
            geocode_fetch = await self._fetch_web_payload(
                url=geocode_url,
                ctx=ctx,
                max_chars=4096,
                mode="json",
                failure_reason="weather_geocode_failed",
            )
            if not geocode_fetch.get("ok"):
                raise RuntimeError(
                    f"weather_geocode_failed:{self._web_fetch_error_message(geocode_fetch, 'geocode_failed')}"
                )
            geocode_payload = self._web_fetch_json_payload(geocode_fetch, failure_reason="weather_geocode_failed")
            results = geocode_payload.get("results", []) if isinstance(geocode_payload, dict) else []
            if not isinstance(results, list) or not results:
                raise RuntimeError(f"weather_location_not_found:{location}")
            first = results[0] if isinstance(results[0], dict) else {}
            latitude = first.get("latitude")
            longitude = first.get("longitude")
            if latitude is None or longitude is None:
                raise RuntimeError(f"weather_location_not_found:{location}")
            resolved_name = str(first.get("name", location) or location).strip()
            country = str(first.get("country", "") or "").strip()

            forecast_url = "https://api.open-meteo.com/v1/forecast?" + urlencode(
                {
                    "latitude": latitude,
                    "longitude": longitude,
                    "current_weather": "true",
                    "timezone": "auto",
                }
            )
            forecast_fetch = await self._fetch_web_payload(
                url=forecast_url,
                ctx=ctx,
                max_chars=4096,
                mode="json",
                failure_reason="weather_forecast_failed",
            )
            if not forecast_fetch.get("ok"):
                raise RuntimeError(
                    f"weather_forecast_failed:{self._web_fetch_error_message(forecast_fetch, 'forecast_failed')}"
                )
            forecast_payload = self._web_fetch_json_payload(forecast_fetch, failure_reason="weather_forecast_failed")
            current = forecast_payload.get("current_weather", {}) if isinstance(forecast_payload, dict) else {}
            if not isinstance(current, dict) or not current:
                raise RuntimeError("weather_current_unavailable")
            place = resolved_name if not country else f"{resolved_name}, {country}"
            return (
                f"{place}: {current.get('temperature')}°C, "
                f"{self._weather_code_description(int(current.get('weathercode', 0) or 0))}, "
                f"wind {current.get('windspeed')} km/h"
            )
        except (KeyError, RuntimeError, ValueError) as exc:
            reason = str(exc or "").strip() or "weather_fetch_failed"
            return f"skill_blocked:{spec_name}:{reason}"

    @staticmethod
    def _script_tool_arguments(script_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        payload = arguments.get("tool_arguments")
        if isinstance(payload, dict):
            return payload

        if script_name == "web_search":
            query = str(arguments.get("query") or arguments.get("input") or "").strip()
            if not query:
                raise ValueError("query or input is required for web-search skill")
            limit = int(arguments.get("limit", 5) or 5)
            return {"query": query, "limit": limit}

        return {}

    async def _precheck_github_auth(
        self,
        *,
        spec_name: str,
        timeout: float,
        ctx: ToolContext,
        env_overrides: dict[str, str] | None = None,
    ) -> str | None:
        resolved_env = env_overrides or {}
        if os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN"):
            return None
        if resolved_env.get("GH_TOKEN") or resolved_env.get("GITHUB_TOKEN"):
            return None
        if self.registry.get("exec") is None:
            return None
        result = await self._run_command_via_exec_tool(
            spec_name=spec_name,
            argv=["gh", "auth", "status"],
            timeout=min(timeout, 15.0),
            ctx=ctx,
            env_overrides=resolved_env,
        )
        if result.startswith(f"skill_blocked:{spec_name}:"):
            return result
        exit_code = self._exec_output_exit_code(result)
        if exit_code is None or exit_code == 0:
            return None
        stderr = self._exec_output_stream(result, "stderr")
        detail = stderr or "gh auth status failed"
        return f"skill_auth_required:{spec_name}:gh:{detail}"

    async def _load_summary_source(self, arguments: dict[str, Any], ctx: ToolContext) -> tuple[str, str]:
        payload = arguments.get("tool_arguments")
        source_input = ""
        if isinstance(payload, dict):
            source_input = str(payload.get("input") or payload.get("url") or payload.get("path") or "").strip()
        if not source_input:
            source_input = str(arguments.get("input") or arguments.get("url") or arguments.get("path") or "").strip()
        if not source_input:
            extra = self._extra_args(arguments)
            source_input = extra[0] if extra else ""
        if not source_input:
            raise ValueError("input is required for summarize skill")

        if source_input.startswith(("http://", "https://")):
            if self.registry.get("web_fetch") is None:
                raise RuntimeError("summary_source_fetch_unavailable")
            raw = await self.registry.execute(
                "web_fetch",
                {"url": source_input, "max_chars": self.SUMMARY_MAX_SOURCE_CHARS},
                session_id=ctx.session_id,
                channel=ctx.channel,
                user_id=ctx.user_id,
            )
            decoded = json.loads(raw)
            if not decoded.get("ok"):
                message = decoded.get("error", {}).get("message", "web_fetch_failed")
                raise RuntimeError(f"summary_source_fetch_failed:{message}")
            result = decoded.get("result", {})
            return source_input, str(result.get("text", "") or "").strip()

        read_tool_name = "read" if self.registry.get("read") is not None else "read_file"
        if self.registry.get(read_tool_name) is None:
            raise RuntimeError("summary_source_reader_unavailable")
        text = await self.registry.execute(
            read_tool_name,
            {"path": source_input, "allow_large_file": True, "limit": self.SUMMARY_MAX_SOURCE_CHARS},
            session_id=ctx.session_id,
            channel=ctx.channel,
            user_id=ctx.user_id,
        )
        return source_input, str(text or "").strip()

    async def _run_summarize(self, arguments: dict[str, Any], ctx: ToolContext, *, spec_name: str, timeout: float) -> str:
        argv = ["summarize", *self._extra_args(arguments)]
        source_input = str(arguments.get("input") or arguments.get("url") or arguments.get("path") or "").strip()
        if len(argv) == 1 and source_input:
            argv.append(source_input)
        if shutil.which("summarize") is not None and self.registry.get("exec") is not None:
            result = await self._run_command_via_exec_tool(spec_name=spec_name, argv=argv, timeout=timeout, ctx=ctx)
            exit_code = self._exec_output_exit_code(result)
            if exit_code in {None, 0}:
                return result
        if self.provider is None:
            return f"skill_blocked:{spec_name}:provider_unavailable_for_summary"
        try:
            source_label, source_text = await self._load_summary_source(arguments, ctx)
        except (KeyError, RuntimeError, ValueError) as exc:
            reason = str(exc or "").strip() or "summary_source_reader_unavailable"
            if not reason.startswith("summary_source_"):
                reason = "summary_source_reader_unavailable"
            return f"skill_blocked:{spec_name}:{reason}"
        if not source_text:
            return f"skill_blocked:{spec_name}:summary_source_empty"
        response = await self.provider.complete(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are ClawLite summarizing content. Preserve hard facts, numbers, dates, deadlines, "
                        "owners, and unresolved risks. Be concise and specific."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Summarize this source.\nSource: {source_label}\n\n{source_text[:self.SUMMARY_MAX_SOURCE_CHARS]}",
                },
            ],
            tools=[],
            max_tokens=500,
            temperature=0.2,
        )
        text = str(getattr(response, "text", "") or "").strip()
        if not text:
            return f"skill_blocked:{spec_name}:provider_empty_summary"
        return text

    @staticmethod
    def _skill_config_path(arguments: dict[str, Any]) -> str:
        payload = arguments.get("tool_arguments")
        if isinstance(payload, dict):
            value = payload.get("config") or payload.get("config_path") or payload.get("configPath") or ""
            return str(value or "").strip()
        return str(arguments.get("config") or arguments.get("config_path") or arguments.get("configPath") or "").strip()

    @staticmethod
    def _skill_payload(arguments: dict[str, Any]) -> dict[str, Any]:
        payload = arguments.get("tool_arguments")
        return dict(payload) if isinstance(payload, dict) else {}

    @staticmethod
    def _load_module_from_path(module_name: str, path: Path) -> Any:
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"module_load_failed:{path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module

    async def _run_healthcheck(self, arguments: dict[str, Any], *, timeout: float) -> str:
        from clawlite.cli.ops import diagnostics_snapshot, fetch_gateway_diagnostics
        from clawlite.config.loader import DEFAULT_CONFIG_PATH, load_config

        config_path = self._skill_config_path(arguments)
        cfg = load_config(config_path or None)
        resolved_config_path = str(Path(config_path).expanduser()) if config_path else str(DEFAULT_CONFIG_PATH)
        payload = diagnostics_snapshot(cfg, config_path=resolved_config_path, include_validation=True)
        args_payload = self._skill_payload(arguments)
        gateway_url = str(args_payload.get("gateway_url") or args_payload.get("gatewayUrl") or "").strip()
        token = str(args_payload.get("token") or "").strip()
        if gateway_url:
            payload["gateway_probe"] = await asyncio.to_thread(
                fetch_gateway_diagnostics,
                gateway_url=gateway_url,
                timeout=min(timeout, 10.0),
                token=token,
            )
        return json.dumps(payload, ensure_ascii=False)

    async def _run_model_usage(self, arguments: dict[str, Any]) -> str:
        payload = self._skill_payload(arguments)
        provider = str(payload.get("provider") or arguments.get("provider") or "codex").strip().lower() or "codex"
        mode = str(payload.get("mode") or arguments.get("mode") or "current").strip().lower() or "current"
        input_path = str(payload.get("input") or arguments.get("input") or "").strip() or None
        explicit_model = str(payload.get("model") or arguments.get("model") or "").strip() or None
        output_format = str(payload.get("format") or arguments.get("format") or "text").strip().lower() or "text"
        pretty = bool(payload.get("pretty", arguments.get("pretty", False)))
        days_raw = payload.get("days", arguments.get("days"))
        days_text = str(days_raw or "").strip()
        days = int(days_text) if days_text else None
        if provider not in {"codex", "claude"}:
            raise ValueError("provider must be codex or claude")
        if mode not in {"current", "all"}:
            raise ValueError("mode must be current or all")
        if output_format not in {"text", "json"}:
            raise ValueError("format must be text or json")

        script_path = Path(__file__).resolve().parents[1] / "skills" / "model-usage" / "scripts" / "model_usage.py"
        module = self._load_module_from_path("clawlite_skill_model_usage_runtime", script_path)
        usage_payload = module.load_payload(input_path, provider)
        entries = module.parse_daily_entries(usage_payload)
        entries = module.filter_by_days(entries, days)

        if mode == "all":
            totals = module.aggregate_costs(entries)
            if output_format == "json":
                body = module.build_json_all(provider, totals)
                return json.dumps(body, ensure_ascii=False, indent=2 if pretty else None)
            return module.render_text_all(provider, totals)

        model = explicit_model
        latest_model_date = None
        if not model:
            model, latest_model_date = module.pick_current_model(entries)
        if not model:
            raise RuntimeError("model_usage_current_model_unavailable")
        totals = module.aggregate_costs(entries)
        total_cost = float(totals.get(model, 0.0))
        latest_cost_date, latest_cost = module.latest_day_cost(entries, model)
        if output_format == "json":
            body = module.build_json_current(
                provider,
                model,
                latest_model_date,
                total_cost,
                latest_cost,
                latest_cost_date,
                len(entries),
            )
            return json.dumps(body, ensure_ascii=False, indent=2 if pretty else None)
        return module.render_text_current(
            provider,
            model,
            latest_model_date,
            total_cost,
            latest_cost,
            latest_cost_date,
            len(entries),
        )

    async def _run_session_logs(self, arguments: dict[str, Any]) -> str:
        from clawlite.config.loader import load_config
        from clawlite.session.store import SessionStore

        payload = self._skill_payload(arguments)
        config_path = self._skill_config_path(arguments)
        cfg = load_config(config_path or None)
        sessions_root = Path(cfg.state_path).expanduser() / "sessions"
        sessions_root.mkdir(parents=True, exist_ok=True)
        session_id = str(payload.get("session_id") or payload.get("sessionId") or arguments.get("session_id") or arguments.get("sessionId") or "").strip()
        query = str(payload.get("query") or arguments.get("query") or "").strip().lower()
        role_filter = str(payload.get("role") or arguments.get("role") or "").strip().lower()
        channel_filter = str(payload.get("channel") or arguments.get("channel") or "").strip().lower()
        limit_raw = payload.get("limit", arguments.get("limit", 20))
        limit = max(1, min(200, int(limit_raw or 20)))

        def _iter_rows(path: Path) -> list[dict[str, Any]]:
            rows: list[dict[str, Any]] = []
            for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
                raw = line.strip()
                if not raw:
                    continue
                try:
                    decoded = json.loads(raw)
                except Exception:
                    continue
                if not isinstance(decoded, dict):
                    continue
                rows.append(decoded)
            return rows

        def _resolve_session_path(raw_session_id: str) -> Path | None:
            store = SessionStore(root=sessions_root)
            candidate_names = [
                store._safe_session_id(raw_session_id),
                raw_session_id.replace(":", "_"),
                raw_session_id.replace(":", "-"),
            ]
            seen: set[str] = set()
            for candidate in candidate_names:
                clean = str(candidate or "").strip()
                if not clean or clean in seen:
                    continue
                seen.add(clean)
                path = sessions_root / f"{clean}.jsonl"
                if path.exists():
                    return path
            for path in sessions_root.glob("*.jsonl"):
                rows = _iter_rows(path)
                if any(str(row.get("session_id", "") or "").strip() == raw_session_id for row in rows):
                    return path
            return None

        def _matches(row: dict[str, Any]) -> bool:
            role = str(row.get("role", "")).strip().lower()
            content = str(row.get("content", "") or "")
            metadata = row.get("metadata", {})
            channel = str(metadata.get("channel", "") if isinstance(metadata, dict) else "").strip().lower()
            if role_filter and role != role_filter:
                return False
            if channel_filter and channel != channel_filter:
                return False
            if query and query not in content.lower():
                return False
            return True

        if session_id:
            path = _resolve_session_path(session_id)
            if path is None:
                return json.dumps({"status": "failed", "error": "session_not_found", "session_id": session_id}, ensure_ascii=False)
            rows = [row for row in _iter_rows(path) if _matches(row)]
            rows = rows[-limit:]
            role_counts: dict[str, int] = {}
            for row in rows:
                role = str(row.get("role", "")).strip().lower()
                if role:
                    role_counts[role] = role_counts.get(role, 0) + 1
            return json.dumps(
                {
                    "status": "ok",
                    "session_id": session_id,
                    "count": len(rows),
                    "role_counts": role_counts,
                    "messages": rows,
                },
                ensure_ascii=False,
            )

        session_rows: list[dict[str, Any]] = []
        for path in sorted(sessions_root.glob("*.jsonl"), key=lambda item: item.stat().st_mtime_ns, reverse=True):
            rows = _iter_rows(path)
            resolved_session_id = str(path.stem)
            if rows:
                first_session_id = str(rows[0].get("session_id", "") or "").strip()
                if first_session_id:
                    resolved_session_id = first_session_id
            if query or role_filter or channel_filter:
                matched = [row for row in rows if _matches(row)]
                if not matched:
                    continue
                for row in matched[:limit]:
                    session_rows.append(
                        {
                            "session_id": resolved_session_id,
                            "ts": str(row.get("ts", "") or ""),
                            "role": str(row.get("role", "") or ""),
                            "content": str(row.get("content", "") or ""),
                            "metadata": row.get("metadata", {}) if isinstance(row.get("metadata", {}), dict) else {},
                        }
                    )
                    if len(session_rows) >= limit:
                        break
            else:
                preview = rows[-1] if rows else {}
                session_rows.append(
                    {
                        "session_id": resolved_session_id,
                        "message_count": len(rows),
                        "last_ts": str(preview.get("ts", "") or ""),
                        "last_role": str(preview.get("role", "") or ""),
                        "last_content": str(preview.get("content", "") or "")[:160],
                    }
                )
            if len(session_rows) >= limit:
                break
        return json.dumps({"status": "ok", "count": len(session_rows), "sessions": session_rows[:limit]}, ensure_ascii=False)

    async def _run_coding_agent(self, arguments: dict[str, Any], ctx: ToolContext) -> str:
        payload = self._skill_payload(arguments)
        task = str(payload.get("task") or arguments.get("task") or arguments.get("input") or "").strip()
        tasks = payload.get("tasks")
        target_tool = self.registry.get("sessions_spawn")
        if target_tool is None:
            return "skill_script_unavailable:coding_agent"
        if not task and not isinstance(tasks, list):
            return json.dumps(
                {
                    "status": "ok",
                    "mode": "guide",
                    "available_tools": ["sessions_spawn", "subagents", "session_status", "sessions_history", "process", "apply_patch"],
                    "message": "Provide task or tasks to delegate coding work.",
                },
                ensure_ascii=False,
            )

        call_arguments: dict[str, Any] = {}
        if isinstance(tasks, list) and tasks:
            call_arguments["tasks"] = [str(item) for item in tasks if str(item).strip()]
        elif task:
            call_arguments["task"] = task
        for key in ("session_id", "sessionId", "target_sessions", "targetSessions", "share_scope", "shareScope"):
            value = payload.get(key)
            if value not in {None, ""}:
                call_arguments[key] = value
        return await self.registry.execute(
            "sessions_spawn",
            call_arguments,
            session_id=ctx.session_id,
            channel=ctx.channel,
            user_id=ctx.user_id,
        )

    async def _run_memory(self, arguments: dict[str, Any], ctx: ToolContext, *, spec_name: str) -> str:
        payload = self._skill_payload(arguments)
        action = str(payload.get("action", arguments.get("action", "guide")) or "guide").strip().lower()

        if action == "guide":
            return json.dumps(
                {
                    "status": "ok",
                    "mode": "guide",
                    "skill": spec_name,
                    "backend": "memory_tools",
                    "usage": "Set tool_arguments.action and provide action-specific fields in tool_arguments.",
                    "available_actions": ["recall", "search", "get", "learn", "forget", "analyze", "request"],
                    "examples": [
                        {"action": "recall", "tool_arguments": {"action": "recall", "query": "timezone preference", "limit": 5}},
                        {"action": "learn", "tool_arguments": {"action": "learn", "text": "User prefers concise updates."}},
                        {"action": "forget", "tool_arguments": {"action": "forget", "query": "deprecated preference", "dry_run": True}},
                    ],
                },
                ensure_ascii=False,
            )

        action_map = {
            "recall": "memory_recall",
            "search": "memory_search",
            "get": "memory_get",
            "learn": "memory_learn",
            "forget": "memory_forget",
            "analyze": "memory_analyze",
        }

        if action == "request":
            requested_tool = str(payload.get("tool", arguments.get("tool", "")) or "").strip()
            if not requested_tool:
                raise ValueError("tool is required for memory request")
            if requested_tool not in {
                "memory_recall",
                "memory_search",
                "memory_get",
                "memory_learn",
                "memory_forget",
                "memory_analyze",
            }:
                raise ValueError("tool must be one of: memory_recall, memory_search, memory_get, memory_learn, memory_forget, memory_analyze")
            target_tool = requested_tool
        else:
            target_tool = action_map.get(action)
            if not target_tool:
                raise ValueError("action must be one of: guide, recall, search, get, learn, forget, analyze, request")

        if self.registry.get(target_tool) is None:
            return f"skill_blocked:{spec_name}:{target_tool}_not_registered"

        tool_args = dict(payload)
        tool_args.pop("action", None)
        tool_args.pop("tool", None)

        try:
            return await self.registry.execute(
                target_tool,
                tool_args,
                session_id=ctx.session_id,
                channel=ctx.channel,
                user_id=ctx.user_id,
            )
        except RuntimeError as exc:
            text = str(exc)
            if text.startswith(f"tool_blocked_by_safety_policy:{target_tool}:"):
                return f"skill_blocked:{spec_name}:{exc}"
            if text.startswith(f"tool_requires_approval:{target_tool}:"):
                return f"skill_requires_approval:{spec_name}:{exc}"
            raise

    async def _run_skald(self, arguments: dict[str, Any], *, spec_name: str) -> str:
        payload = self._skill_payload(arguments)
        action = str(payload.get("action", arguments.get("action", "guide")) or "guide").strip().lower()

        if action == "guide":
            return json.dumps(
                {
                    "status": "ok",
                    "mode": "guide",
                    "skill": spec_name,
                    "backend": "provider",
                    "usage": "Provide source text with tool_arguments.input/text and optional style/tone.",
                    "available_actions": ["story", "summary", "retell"],
                    "examples": [
                        {"action": "story", "tool_arguments": {"action": "story", "input": "Deployment failed after schema migration.", "style": "concise"}},
                        {"action": "summary", "tool_arguments": {"action": "summary", "input": "Long project history..."}},
                    ],
                },
                ensure_ascii=False,
            )

        if self.provider is None:
            return f"skill_blocked:{spec_name}:provider_unavailable"

        source = str(payload.get("input", payload.get("text", arguments.get("input", arguments.get("text", "")))) or "").strip()
        if not source:
            raise ValueError("input is required for skald")

        style = str(payload.get("style", arguments.get("style", "concise")) or "concise").strip()
        tone = str(payload.get("tone", arguments.get("tone", "direct")) or "direct").strip()
        mode = "narrative_story" if action in {"story", "retell"} else "structured_summary"

        response = await self.provider.complete(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are Skald, a precise narrative synthesizer. Preserve hard facts and produce clear, "
                        "human-readable storytelling with technical accuracy."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Mode: {mode}\nStyle: {style}\nTone: {tone}\n\n"
                        f"Turn this into a clean narrative with setup, journey, current state, and key takeaways.\n\n{source[:12000]}"
                    ),
                },
            ],
            tools=[],
            max_tokens=800,
            temperature=0.4,
        )
        text = str(getattr(response, "text", "") or "").strip()
        if not text:
            return f"skill_blocked:{spec_name}:provider_empty_response"
        return text

    async def _run_skill_creator(self, arguments: dict[str, Any], ctx: ToolContext, *, spec_name: str) -> str:
        payload = self._skill_payload(arguments)
        action = str(payload.get("action", arguments.get("action", "guide")) or "guide").strip().lower()

        if action == "guide":
            return json.dumps(
                {
                    "status": "ok",
                    "mode": "guide",
                    "skill": spec_name,
                    "backend": "template",
                    "usage": "Use action=scaffold to generate SKILL.md frontmatter and section template.",
                    "available_actions": ["scaffold"],
                    "examples": [
                        {
                            "action": "scaffold",
                            "tool_arguments": {
                                "action": "scaffold",
                                "name": "example-skill",
                                "description": "Do one focused task",
                                "script": "example_tool",
                            },
                        }
                    ],
                },
                ensure_ascii=False,
            )

        if action != "scaffold":
            raise ValueError("action must be one of: guide, scaffold")

        name = str(payload.get("name", arguments.get("name", "")) or "").strip()
        description = str(payload.get("description", arguments.get("description", "")) or "").strip()
        if not name or not description:
            raise ValueError("name and description are required for skill_creator scaffold")

        script = str(payload.get("script", arguments.get("script", "")) or "").strip()
        command = str(payload.get("command", arguments.get("command", "")) or "").strip()
        if script and command:
            raise ValueError("provide either script or command, not both")

        header_lines = [
            "---",
            f"name: {name}",
            f"description: {description}",
            "always: false",
            'metadata: {"clawlite":{"emoji":"🛠️"}}',
        ]
        if script:
            header_lines.append(f"script: {script}")
        if command:
            header_lines.append(f"command: {command}")
        header_lines.append("---")

        title = str(payload.get("title", arguments.get("title", name.replace("-", " ").title())) or name).strip()
        body = (
            f"# {title}\n\n"
            "Use this skill when the user asks for this workflow.\n\n"
            "## What it does\n\n"
            "- Explain the primary trigger\n"
            "- Describe expected inputs\n"
            "- Describe expected outputs\n"
        )
        content = "\n".join(header_lines) + "\n\n" + body

        target_path = str(payload.get("path", arguments.get("path", "")) or "").strip()
        if not target_path:
            return json.dumps({"status": "ok", "mode": "preview", "content": content}, ensure_ascii=False)

        write_tool = "write" if self.registry.get("write") is not None else "write_file"
        if self.registry.get(write_tool) is None:
            return f"skill_blocked:{spec_name}:write_tool_not_registered"

        await self.registry.execute(
            write_tool,
            {"path": target_path, "content": content},
            session_id=ctx.session_id,
            channel=ctx.channel,
            user_id=ctx.user_id,
        )
        return json.dumps({"status": "ok", "mode": "written", "path": target_path}, ensure_ascii=False)

    @staticmethod
    def _gh_value(payload: dict[str, Any], arguments: dict[str, Any], *keys: str) -> str:
        for key in keys:
            value = payload.get(key, arguments.get(key))
            text = str(value or "").strip()
            if text:
                return text
        return ""

    @staticmethod
    def _gh_label_values(payload: dict[str, Any], arguments: dict[str, Any]) -> list[str]:
        raw = payload.get("labels", arguments.get("labels"))
        if raw is None:
            raw = payload.get("label", arguments.get("label"))
        if isinstance(raw, list):
            return [str(item).strip() for item in raw if str(item).strip()]
        text = str(raw or "").strip()
        if not text:
            return []
        return [item.strip() for item in text.split(",") if item.strip()]

    @staticmethod
    def _gh_bool(payload: dict[str, Any], arguments: dict[str, Any], *keys: str) -> bool:
        for key in keys:
            if key in payload:
                return bool(payload.get(key))
            if key in arguments:
                return bool(arguments.get(key))
        return False

    async def _run_gh_issues(
        self,
        arguments: dict[str, Any],
        ctx: ToolContext,
        *,
        spec_name: str,
        timeout: float,
        env_overrides: dict[str, str],
    ) -> str:
        if self.registry.get("exec") is None:
            return f"skill_blocked:{spec_name}:exec_tool_not_registered"

        payload = self._skill_payload(arguments)
        extra_args = self._extra_args(arguments)
        if extra_args:
            auth_error = await self._precheck_github_auth(spec_name=spec_name, timeout=timeout, ctx=ctx)
            if auth_error is not None:
                return auth_error
            return await self._run_command_via_exec_tool(
                spec_name=spec_name,
                argv=["gh", "issue", *extra_args],
                timeout=timeout,
                ctx=ctx,
                env_overrides=env_overrides,
            )

        action = self._gh_value(payload, arguments, "action").lower() or "guide"
        repo = self._gh_value(payload, arguments, "repo", "repository")
        issue_number = self._gh_value(payload, arguments, "issue", "issue_number", "number")
        title = self._gh_value(payload, arguments, "title")
        body = self._gh_value(payload, arguments, "body")
        state = self._gh_value(payload, arguments, "state")
        search = self._gh_value(payload, arguments, "search", "query")
        assignee = self._gh_value(payload, arguments, "assignee")
        labels = self._gh_label_values(payload, arguments)
        wants_comments = self._gh_bool(payload, arguments, "comments", "include_comments")

        if action == "guide":
            return json.dumps(
                {
                    "status": "ok",
                    "mode": "guide",
                    "skill": spec_name,
                    "backend": "gh issue",
                    "available_actions": ["list", "view", "comment", "create"],
                    "required_fields": {
                        "list": ["repo(optional)"],
                        "view": ["issue"],
                        "comment": ["issue", "body"],
                        "create": ["title"],
                    },
                    "examples": {
                        "list": {"tool_arguments": {"action": "list", "repo": "owner/repo", "state": "open", "limit": 10}},
                        "view": {"tool_arguments": {"action": "view", "repo": "owner/repo", "issue": 123, "comments": True}},
                        "comment": {"tool_arguments": {"action": "comment", "repo": "owner/repo", "issue": 123, "body": "Investigating this now."}},
                        "create": {"tool_arguments": {"action": "create", "repo": "owner/repo", "title": "Bug title", "body": "Steps to reproduce"}},
                    },
                },
                ensure_ascii=False,
            )

        argv = ["gh", "issue"]
        if action == "list":
            argv.append("list")
            if repo:
                argv.extend(["--repo", repo])
            if state:
                argv.extend(["--state", state])
            if search:
                argv.extend(["--search", search])
            if assignee:
                argv.extend(["--assignee", assignee])
            if labels:
                argv.extend(["--label", ",".join(labels)])
            limit_value = payload.get("limit", arguments.get("limit", 20))
            limit = max(1, min(100, int(limit_value or 20)))
            argv.extend(["--limit", str(limit)])
        elif action == "view":
            if not issue_number:
                raise ValueError("issue is required for gh-issues view")
            argv.extend(["view", issue_number])
            if repo:
                argv.extend(["--repo", repo])
            if wants_comments:
                argv.append("--comments")
        elif action == "comment":
            if not issue_number:
                raise ValueError("issue is required for gh-issues comment")
            if not body:
                raise ValueError("body is required for gh-issues comment")
            argv.extend(["comment", issue_number])
            if repo:
                argv.extend(["--repo", repo])
            argv.extend(["--body", body])
        elif action == "create":
            if not title:
                raise ValueError("title is required for gh-issues create")
            argv.append("create")
            if repo:
                argv.extend(["--repo", repo])
            argv.extend(["--title", title])
            if body:
                argv.extend(["--body", body])
            if assignee:
                argv.extend(["--assignee", assignee])
            if labels:
                argv.extend(["--label", ",".join(labels)])
        else:
            raise ValueError("action must be one of: guide, list, view, comment, create")

        auth_error = await self._precheck_github_auth(
            spec_name=spec_name,
            timeout=timeout,
            ctx=ctx,
            env_overrides=env_overrides,
        )
        if auth_error is not None:
            return auth_error
        return await self._run_command_via_exec_tool(
            spec_name=spec_name,
            argv=argv,
            timeout=timeout,
            ctx=ctx,
            env_overrides=env_overrides,
        )

    async def _run_github(
        self,
        arguments: dict[str, Any],
        ctx: ToolContext,
        *,
        spec_name: str,
        timeout: float,
        env_overrides: dict[str, str],
    ) -> str:
        if self.registry.get("exec") is None:
            return f"skill_blocked:{spec_name}:exec_tool_not_registered"

        payload = self._skill_payload(arguments)
        extra_args = self._extra_args(arguments)
        if extra_args:
            auth_error = await self._precheck_github_auth(spec_name=spec_name, timeout=timeout, ctx=ctx)
            if auth_error is not None:
                return auth_error
            return await self._run_command_via_exec_tool(
                spec_name=spec_name,
                argv=["gh", *extra_args],
                timeout=timeout,
                ctx=ctx,
                env_overrides=env_overrides,
            )

        action = self._gh_value(payload, arguments, "action").lower() or "guide"
        repo = self._gh_value(payload, arguments, "repo", "repository")
        number = self._gh_value(payload, arguments, "number", "issue", "pr")
        state = self._gh_value(payload, arguments, "state")
        search = self._gh_value(payload, arguments, "search", "query")
        author = self._gh_value(payload, arguments, "author")
        assignee = self._gh_value(payload, arguments, "assignee")
        labels = self._gh_label_values(payload, arguments)
        wants_comments = self._gh_bool(payload, arguments, "comments", "include_comments")

        if action == "guide":
            return json.dumps(
                {
                    "status": "ok",
                    "mode": "guide",
                    "skill": spec_name,
                    "backend": "gh",
                    "usage": "Set tool_arguments.action and provide action-specific fields in tool_arguments.",
                    "available_actions": [
                        "list_issues",
                        "list_prs",
                        "view_issue",
                        "view_pr",
                        "pr_checks",
                        "run_list",
                        "search_issues",
                        "search_prs",
                        "api",
                    ],
                    "examples": [
                        {"action": "list_issues", "tool_arguments": {"action": "list_issues", "repo": "owner/repo", "state": "open", "limit": 20}},
                        {"action": "list_prs", "tool_arguments": {"action": "list_prs", "repo": "owner/repo", "state": "open", "limit": 20}},
                        {"action": "api", "tool_arguments": {"action": "api", "path": "repos/owner/repo/pulls", "method": "GET"}},
                    ],
                },
                ensure_ascii=False,
            )

        limit_value = payload.get("limit", arguments.get("limit", 20))
        limit = max(1, min(200, int(limit_value or 20)))

        argv: list[str]
        if action == "list_issues":
            argv = ["gh", "issue", "list"]
            if repo:
                argv.extend(["--repo", repo])
            if state:
                argv.extend(["--state", state])
            if search:
                argv.extend(["--search", search])
            if assignee:
                argv.extend(["--assignee", assignee])
            if labels:
                argv.extend(["--label", ",".join(labels)])
            argv.extend(["--limit", str(limit)])
        elif action == "list_prs":
            argv = ["gh", "pr", "list"]
            if repo:
                argv.extend(["--repo", repo])
            if state:
                argv.extend(["--state", state])
            if search:
                argv.extend(["--search", search])
            if author:
                argv.extend(["--author", author])
            if labels:
                argv.extend(["--label", ",".join(labels)])
            argv.extend(["--limit", str(limit)])
        elif action == "view_issue":
            if not number:
                raise ValueError("number is required for github view_issue")
            argv = ["gh", "issue", "view", number]
            if repo:
                argv.extend(["--repo", repo])
            if wants_comments:
                argv.append("--comments")
        elif action == "view_pr":
            if not number:
                raise ValueError("number is required for github view_pr")
            argv = ["gh", "pr", "view", number]
            if repo:
                argv.extend(["--repo", repo])
            if wants_comments:
                argv.append("--comments")
        elif action == "pr_checks":
            if not number:
                raise ValueError("number is required for github pr_checks")
            argv = ["gh", "pr", "checks", number]
            if repo:
                argv.extend(["--repo", repo])
        elif action == "run_list":
            argv = ["gh", "run", "list", "--limit", str(limit)]
            if repo:
                argv.extend(["--repo", repo])
        elif action == "search_issues":
            if not search:
                raise ValueError("query is required for github search_issues")
            argv = ["gh", "search", "issues", "--limit", str(limit), search]
            if repo:
                argv.extend(["--repo", repo])
            if state:
                argv.extend(["--state", state])
        elif action == "search_prs":
            if not search:
                raise ValueError("query is required for github search_prs")
            argv = ["gh", "search", "prs", "--limit", str(limit), search]
            if repo:
                argv.extend(["--repo", repo])
            if state:
                argv.extend(["--state", state])
        elif action == "api":
            path = self._gh_value(payload, arguments, "path")
            if not path:
                raise ValueError("path is required for github api")
            method = self._gh_value(payload, arguments, "method") or "GET"
            argv = ["gh", "api", path, "--method", method.upper()]
            if repo:
                argv.extend(["--repo", repo])
        else:
            raise ValueError(
                "action must be one of: guide, list_issues, list_prs, view_issue, view_pr, pr_checks, run_list, search_issues, search_prs, api"
            )

        auth_error = await self._precheck_github_auth(
            spec_name=spec_name,
            timeout=timeout,
            ctx=ctx,
            env_overrides=env_overrides,
        )
        if auth_error is not None:
            return auth_error
        return await self._run_command_via_exec_tool(
            spec_name=spec_name,
            argv=argv,
            timeout=timeout,
            ctx=ctx,
            env_overrides=env_overrides,
        )

    async def _run_clawhub(
        self,
        arguments: dict[str, Any],
        ctx: ToolContext,
        *,
        spec_name: str,
        timeout: float,
        env_overrides: dict[str, str],
    ) -> str:
        if self.registry.get("exec") is None:
            return f"skill_blocked:{spec_name}:exec_tool_not_registered"

        payload = self._skill_payload(arguments)
        extra_args = self._extra_args(arguments)
        if extra_args:
            return await self._run_command_via_exec_tool(
                spec_name=spec_name,
                argv=["npx", "--yes", "clawhub@latest", *extra_args],
                timeout=timeout,
                ctx=ctx,
                env_overrides=env_overrides,
            )

        action = str(payload.get("action", arguments.get("action", "guide")) or "guide").strip().lower()
        workdir = str(
            payload.get("workdir", arguments.get("workdir", os.getenv("CLAWLITE_SKILLS_WORKDIR", str(Path.home() / ".clawlite" / "workspace"))))
            or ""
        ).strip()
        limit_raw = payload.get("limit", arguments.get("limit", 10))
        limit = max(1, min(100, int(limit_raw or 10)))
        query = str(payload.get("query", arguments.get("query", "")) or "").strip()
        slug = str(payload.get("slug", arguments.get("slug", "")) or "").strip()

        if action == "guide":
            return json.dumps(
                {
                    "status": "ok",
                    "mode": "guide",
                    "skill": spec_name,
                    "backend": "npx clawhub@latest",
                    "usage": "Set tool_arguments.action and provide action-specific fields in tool_arguments.",
                    "available_actions": ["search", "install", "list", "update"],
                    "defaults": {"workdir": workdir, "limit": limit},
                    "examples": [
                        {"action": "search", "tool_arguments": {"action": "search", "query": "github", "limit": 5}},
                        {"action": "install", "tool_arguments": {"action": "install", "slug": "weather", "workdir": "~/.clawlite/workspace"}},
                        {"action": "update", "tool_arguments": {"action": "update", "all": True, "workdir": "~/.clawlite/workspace"}},
                    ],
                },
                ensure_ascii=False,
            )

        argv: list[str] = ["npx", "--yes", "clawhub@latest"]
        if action == "search":
            if not query:
                raise ValueError("query is required for clawhub search")
            argv.extend(["search", query, "--limit", str(limit)])
        elif action == "install":
            if not slug:
                raise ValueError("slug is required for clawhub install")
            argv.extend(["install", slug, "--workdir", workdir])
        elif action == "list":
            argv.extend(["list", "--workdir", workdir])
        elif action == "update":
            update_all = bool(payload.get("all", arguments.get("all", True)))
            argv.append("update")
            if update_all:
                argv.append("--all")
            argv.extend(["--workdir", workdir])
        else:
            raise ValueError("action must be one of: guide, search, install, list, update")

        return await self._run_command_via_exec_tool(
            spec_name=spec_name,
            argv=argv,
            timeout=timeout,
            ctx=ctx,
            env_overrides=env_overrides,
        )

    async def _run_onepassword(
        self,
        arguments: dict[str, Any],
        ctx: ToolContext,
        *,
        spec_name: str,
        timeout: float,
        env_overrides: dict[str, str],
    ) -> str:
        if self.registry.get("exec") is None:
            return f"skill_blocked:{spec_name}:exec_tool_not_registered"

        payload = self._skill_payload(arguments)
        extra_args = self._extra_args(arguments)
        if extra_args:
            return await self._run_command_via_exec_tool(
                spec_name=spec_name,
                argv=["op", *extra_args],
                timeout=timeout,
                ctx=ctx,
                env_overrides=env_overrides,
            )

        action = str(payload.get("action", arguments.get("action", "guide")) or "guide").strip().lower()
        vault = str(payload.get("vault", arguments.get("vault", "")) or "").strip()
        item = str(payload.get("item", arguments.get("item", "")) or "").strip()
        field = str(payload.get("field", arguments.get("field", "")) or "").strip()
        reference = str(payload.get("reference", arguments.get("reference", "")) or "").strip()

        if action == "guide":
            return json.dumps(
                {
                    "status": "ok",
                    "mode": "guide",
                    "skill": spec_name,
                    "backend": "op",
                    "usage": "Set tool_arguments.action and provide action-specific fields in tool_arguments.",
                    "auth": {"required_env": ["OP_SERVICE_ACCOUNT_TOKEN"]},
                    "available_actions": ["whoami", "vault_list", "item_list", "item_get", "read", "request"],
                    "examples": [
                        {"action": "whoami", "tool_arguments": {"action": "whoami"}},
                        {"action": "item_get", "tool_arguments": {"action": "item_get", "item": "GitHub Token", "field": "password"}},
                        {"action": "read", "tool_arguments": {"action": "read", "reference": "op://Private/GitHub Token/password"}},
                    ],
                },
                ensure_ascii=False,
            )

        argv: list[str] = ["op"]
        if action == "whoami":
            argv.append("whoami")
        elif action == "vault_list":
            argv.extend(["vault", "list"])
        elif action == "item_list":
            argv.extend(["item", "list"])
            if vault:
                argv.extend(["--vault", vault])
        elif action == "item_get":
            if not item:
                raise ValueError("item is required for onepassword item_get")
            argv.extend(["item", "get", item])
            if vault:
                argv.extend(["--vault", vault])
            if field:
                argv.extend(["--fields", f"label={field}"])
        elif action == "read":
            if not reference:
                raise ValueError("reference is required for onepassword read")
            argv.extend(["read", reference])
        elif action == "request":
            command = str(payload.get("command", arguments.get("command", "")) or "").strip()
            if not command:
                raise ValueError("command is required for onepassword request")
            argv.extend(shlex.split(command))
        else:
            raise ValueError("action must be one of: guide, whoami, vault_list, item_list, item_get, read, request")

        return await self._run_command_via_exec_tool(
            spec_name=spec_name,
            argv=argv,
            timeout=timeout,
            ctx=ctx,
            env_overrides=env_overrides,
        )

    async def _run_docker(
        self,
        arguments: dict[str, Any],
        ctx: ToolContext,
        *,
        spec_name: str,
        timeout: float,
        env_overrides: dict[str, str],
    ) -> str:
        if self.registry.get("exec") is None:
            return f"skill_blocked:{spec_name}:exec_tool_not_registered"

        payload = self._skill_payload(arguments)
        extra_args = self._extra_args(arguments)
        if extra_args:
            return await self._run_command_via_exec_tool(
                spec_name=spec_name,
                argv=["docker", *extra_args],
                timeout=timeout,
                ctx=ctx,
                env_overrides=env_overrides,
            )

        action = str(payload.get("action", arguments.get("action", "guide")) or "guide").strip().lower()
        target = str(payload.get("target", payload.get("container", arguments.get("target", ""))) or "").strip()
        service = str(payload.get("service", arguments.get("service", "")) or "").strip()
        tail_raw = payload.get("tail", arguments.get("tail", 100))
        tail = max(1, min(2000, int(tail_raw or 100)))

        if action == "guide":
            return json.dumps(
                {
                    "status": "ok",
                    "mode": "guide",
                    "skill": spec_name,
                    "backend": "docker",
                    "usage": "Set tool_arguments.action and provide action-specific fields in tool_arguments.",
                    "available_actions": [
                        "ps",
                        "ps_all",
                        "logs",
                        "inspect",
                        "compose_ps",
                        "compose_logs",
                        "compose_up",
                        "compose_down",
                        "request",
                    ],
                    "examples": [
                        {"action": "ps", "tool_arguments": {"action": "ps"}},
                        {"action": "logs", "tool_arguments": {"action": "logs", "target": "api", "tail": 200}},
                        {"action": "compose_up", "tool_arguments": {"action": "compose_up"}},
                    ],
                },
                ensure_ascii=False,
            )

        argv: list[str] = ["docker"]
        if action == "ps":
            argv.append("ps")
        elif action == "ps_all":
            argv.extend(["ps", "-a"])
        elif action == "logs":
            if not target:
                raise ValueError("target is required for docker logs")
            argv.extend(["logs", target, "--tail", str(tail)])
        elif action == "inspect":
            if not target:
                raise ValueError("target is required for docker inspect")
            argv.extend(["inspect", target])
        elif action == "compose_ps":
            argv.extend(["compose", "ps"])
        elif action == "compose_logs":
            argv.extend(["compose", "logs", "--tail", str(tail)])
            if service:
                argv.append(service)
        elif action == "compose_up":
            argv.extend(["compose", "up", "-d"])
        elif action == "compose_down":
            argv.extend(["compose", "down"])
        elif action == "request":
            command = str(payload.get("command", arguments.get("command", "")) or "").strip()
            if not command:
                raise ValueError("command is required for docker request")
            argv.extend(shlex.split(command))
        else:
            raise ValueError("action must be one of: guide, ps, ps_all, logs, inspect, compose_ps, compose_logs, compose_up, compose_down, request")

        return await self._run_command_via_exec_tool(
            spec_name=spec_name,
            argv=argv,
            timeout=timeout,
            ctx=ctx,
            env_overrides=env_overrides,
        )

    async def _run_tmux(
        self,
        arguments: dict[str, Any],
        ctx: ToolContext,
        *,
        spec_name: str,
        timeout: float,
        env_overrides: dict[str, str],
    ) -> str:
        if self.registry.get("exec") is None:
            return f"skill_blocked:{spec_name}:exec_tool_not_registered"

        if not (sys.platform.startswith("linux") or sys.platform.startswith("darwin")):
            return f"skill_blocked:{spec_name}:platform_not_supported"

        payload = self._skill_payload(arguments)
        extra_args = self._extra_args(arguments)
        if extra_args:
            return await self._run_command_via_exec_tool(
                spec_name=spec_name,
                argv=["tmux", *extra_args],
                timeout=timeout,
                ctx=ctx,
                env_overrides=env_overrides,
            )

        action = str(payload.get("action", arguments.get("action", "guide")) or "guide").strip().lower()
        socket = str(payload.get("socket", arguments.get("socket", "")) or "").strip()
        session = str(payload.get("session", arguments.get("session", "")) or "").strip()
        target = str(payload.get("target", arguments.get("target", "")) or "").strip()

        def _prefix() -> list[str]:
            base = ["tmux"]
            if socket:
                base.extend(["-S", socket])
            return base

        if action == "guide":
            return json.dumps(
                {
                    "status": "ok",
                    "mode": "guide",
                    "skill": spec_name,
                    "backend": "tmux",
                    "usage": "Set tool_arguments.action and provide action-specific fields in tool_arguments.",
                    "platform": "linux|darwin",
                    "available_actions": [
                        "list_sessions",
                        "new_session",
                        "send_keys",
                        "capture",
                        "kill_session",
                        "kill_server",
                        "request",
                    ],
                    "examples": [
                        {"action": "list_sessions", "tool_arguments": {"action": "list_sessions", "socket": "/tmp/clawlite.sock"}},
                        {"action": "new_session", "tool_arguments": {"action": "new_session", "session": "clawlite-shell", "socket": "/tmp/clawlite.sock"}},
                        {"action": "capture", "tool_arguments": {"action": "capture", "target": "clawlite-shell:0.0", "lines": 200}},
                    ],
                },
                ensure_ascii=False,
            )

        argv = _prefix()
        if action == "list_sessions":
            argv.append("list-sessions")
        elif action == "new_session":
            if not session:
                raise ValueError("session is required for tmux new_session")
            window = str(payload.get("window", arguments.get("window", "shell")) or "shell").strip()
            argv.extend(["new", "-d", "-s", session, "-n", window])
        elif action == "send_keys":
            if not target:
                raise ValueError("target is required for tmux send_keys")
            text = str(payload.get("text", arguments.get("text", "")) or "").strip()
            if not text:
                raise ValueError("text is required for tmux send_keys")
            literal = bool(payload.get("literal", arguments.get("literal", True)))
            argv.extend(["send-keys", "-t", target])
            if literal:
                argv.append("-l")
            argv.append(text)
            send_enter = bool(payload.get("enter", arguments.get("enter", True)))
            if send_enter:
                argv.append("Enter")
        elif action == "capture":
            if not target:
                raise ValueError("target is required for tmux capture")
            lines = max(20, min(5000, int(payload.get("lines", arguments.get("lines", 200)) or 200)))
            argv.extend(["capture-pane", "-p", "-J", "-t", target, "-S", f"-{lines}"])
        elif action == "kill_session":
            if not session:
                raise ValueError("session is required for tmux kill_session")
            argv.extend(["kill-session", "-t", session])
        elif action == "kill_server":
            argv.append("kill-server")
        elif action == "request":
            command = str(payload.get("command", arguments.get("command", "")) or "").strip()
            if not command:
                raise ValueError("command is required for tmux request")
            argv.extend(shlex.split(command))
        else:
            raise ValueError("action must be one of: guide, list_sessions, new_session, send_keys, capture, kill_session, kill_server, request")

        return await self._run_command_via_exec_tool(
            spec_name=spec_name,
            argv=argv,
            timeout=timeout,
            ctx=ctx,
            env_overrides=env_overrides,
        )

    @staticmethod
    def _obsidian_vault(arguments: dict[str, Any], *, env_overrides: dict[str, str] | None = None) -> Path:
        payload = SkillTool._skill_payload(arguments)
        raw = str(payload.get("vault", arguments.get("vault", "")) or "").strip()
        if not raw and env_overrides:
            raw = str(env_overrides.get("OBSIDIAN_VAULT", "") or "").strip()
        if not raw:
            raw = str(os.getenv("OBSIDIAN_VAULT", "") or "").strip()
        if not raw:
            raise RuntimeError("obsidian_vault_missing")
        root = Path(raw).expanduser().resolve()
        if not root.exists() or not root.is_dir():
            raise RuntimeError("obsidian_vault_not_found")
        return root

    @staticmethod
    def _obsidian_resolve_note(root: Path, note_path: str) -> Path:
        if not note_path.strip():
            raise ValueError("path is required")
        target = (root / note_path.strip()).expanduser().resolve()
        if target != root and root not in target.parents:
            raise ValueError("path_outside_vault")
        return target

    async def _run_obsidian(
        self,
        arguments: dict[str, Any],
        *,
        spec_name: str,
        env_overrides: dict[str, str] | None = None,
    ) -> str:
        payload = self._skill_payload(arguments)
        action = str(payload.get("action", arguments.get("action", "guide")) or "guide").strip().lower()

        if action == "guide":
            return json.dumps(
                {
                    "status": "ok",
                    "mode": "guide",
                    "skill": spec_name,
                    "backend": "filesystem",
                    "usage": "Set OBSIDIAN_VAULT env (or tool_arguments.vault), then provide action-specific fields.",
                    "available_actions": ["list", "read", "write", "append", "search"],
                    "examples": [
                        {"action": "list", "tool_arguments": {"action": "list", "limit": 20}},
                        {"action": "read", "tool_arguments": {"action": "read", "path": "notes/today.md"}},
                        {"action": "append", "tool_arguments": {"action": "append", "path": "notes/today.md", "content": "\n## Update\nDone."}},
                    ],
                },
                ensure_ascii=False,
            )

        try:
            root = self._obsidian_vault(arguments, env_overrides=env_overrides)
        except RuntimeError as exc:
            return f"skill_blocked:{spec_name}:{str(exc)}"

        limit_raw = payload.get("limit", arguments.get("limit", 50))
        limit = max(1, min(500, int(limit_raw or 50)))

        if action == "list":
            notes = [str(path.relative_to(root).as_posix()) for path in sorted(root.rglob("*.md"))]
            return json.dumps({"status": "ok", "count": len(notes[:limit]), "notes": notes[:limit]}, ensure_ascii=False)

        if action in {"read", "write", "append"}:
            note_path = str(payload.get("path", arguments.get("path", "")) or "").strip()
            target = self._obsidian_resolve_note(root, note_path)
            if action == "read":
                if not target.exists() or not target.is_file():
                    raise ValueError("note_not_found")
                text = target.read_text(encoding="utf-8", errors="ignore")
                return json.dumps({"status": "ok", "path": str(target.relative_to(root).as_posix()), "content": text}, ensure_ascii=False)
            content = str(payload.get("content", arguments.get("content", "")) or "")
            target.parent.mkdir(parents=True, exist_ok=True)
            if action == "write":
                target.write_text(content, encoding="utf-8")
            else:
                with target.open("a", encoding="utf-8") as handle:
                    handle.write(content)
            return json.dumps({"status": "ok", "path": str(target.relative_to(root).as_posix())}, ensure_ascii=False)

        if action == "search":
            query = str(payload.get("query", arguments.get("query", "")) or "").strip()
            if not query:
                raise ValueError("query is required for obsidian search")
            matches: list[dict[str, Any]] = []
            lowered = query.lower()
            for note in sorted(root.rglob("*.md")):
                text = note.read_text(encoding="utf-8", errors="ignore")
                if lowered not in text.lower():
                    continue
                snippet = ""
                for line in text.splitlines():
                    if lowered in line.lower():
                        snippet = line.strip()
                        break
                matches.append({"path": str(note.relative_to(root).as_posix()), "snippet": snippet})
                if len(matches) >= limit:
                    break
            return json.dumps({"status": "ok", "count": len(matches), "matches": matches}, ensure_ascii=False)

        raise ValueError("action must be one of: guide, list, read, write, append, search")

    async def _run_apple_notes(
        self,
        arguments: dict[str, Any],
        ctx: ToolContext,
        *,
        spec_name: str,
        timeout: float,
        env_overrides: dict[str, str],
    ) -> str:
        if self.registry.get("exec") is None:
            return f"skill_blocked:{spec_name}:exec_tool_not_registered"

        if not sys.platform.startswith("darwin"):
            return f"skill_blocked:{spec_name}:platform_not_supported"

        payload = self._skill_payload(arguments)
        extra_args = self._extra_args(arguments)
        if extra_args:
            return await self._run_command_via_exec_tool(
                spec_name=spec_name,
                argv=["osascript", *extra_args],
                timeout=timeout,
                ctx=ctx,
                env_overrides=env_overrides,
            )

        action = str(payload.get("action", arguments.get("action", "guide")) or "guide").strip().lower()
        account = str(payload.get("account", arguments.get("account", "iCloud")) or "iCloud").strip()
        folder = str(payload.get("folder", arguments.get("folder", "Notes")) or "Notes").strip()
        note = str(payload.get("note", payload.get("name", arguments.get("note", ""))) or "").strip()

        if action == "guide":
            return json.dumps(
                {
                    "status": "ok",
                    "mode": "guide",
                    "skill": spec_name,
                    "backend": "osascript",
                    "usage": "Set tool_arguments.action and provide action-specific fields in tool_arguments.",
                    "platform": "darwin",
                    "available_actions": ["list", "read", "search", "create", "append", "request"],
                    "examples": [
                        {"action": "list", "tool_arguments": {"action": "list", "folder": "Notes"}},
                        {"action": "read", "tool_arguments": {"action": "read", "note": "Daily"}},
                        {"action": "create", "tool_arguments": {"action": "create", "note": "Todo", "body": "- task"}},
                    ],
                },
                ensure_ascii=False,
            )

        def _esc(text: str) -> str:
            return str(text or "").replace("\\", "\\\\").replace('"', '\\"')

        script = ""
        if action == "list":
            script = (
                f'tell application "Notes"\n'
                f'  set noteNames to {{}}\n'
                f'  repeat with n in notes of folder "{_esc(folder)}" of account "{_esc(account)}"\n'
                f'    set end of noteNames to name of n\n'
                f'  end repeat\n'
                f'  return noteNames\n'
                f'end tell'
            )
        elif action == "read":
            if not note:
                raise ValueError("note is required for apple_notes read")
            script = (
                f'tell application "Notes"\n'
                f'  set theNote to note "{_esc(note)}" of folder "{_esc(folder)}" of account "{_esc(account)}"\n'
                f'  return body of theNote\n'
                f'end tell'
            )
        elif action == "search":
            query = str(payload.get("query", arguments.get("query", "")) or "").strip()
            if not query:
                raise ValueError("query is required for apple_notes search")
            script = (
                f'tell application "Notes"\n'
                f'  set results to {{}}\n'
                f'  repeat with n in notes of folder "{_esc(folder)}" of account "{_esc(account)}"\n'
                f'    if name of n contains "{_esc(query)}" then\n'
                f'      set end of results to name of n\n'
                f'    end if\n'
                f'  end repeat\n'
                f'  return results\n'
                f'end tell'
            )
        elif action == "create":
            if not note:
                raise ValueError("note is required for apple_notes create")
            body = str(payload.get("body", arguments.get("body", "")) or "").strip()
            script = (
                f'tell application "Notes"\n'
                f'  tell account "{_esc(account)}"\n'
                f'    make new note at folder "{_esc(folder)}" with properties {{name:"{_esc(note)}", body:"{_esc(body)}"}}\n'
                f'  end tell\n'
                f'end tell'
            )
        elif action == "append":
            if not note:
                raise ValueError("note is required for apple_notes append")
            body = str(payload.get("body", arguments.get("body", "")) or "").strip()
            if not body:
                raise ValueError("body is required for apple_notes append")
            script = (
                f'tell application "Notes"\n'
                f'  set theNote to note "{_esc(note)}" of folder "{_esc(folder)}" of account "{_esc(account)}"\n'
                f'  set body of theNote to (body of theNote) & "<br>{_esc(body)}"\n'
                f'end tell'
            )
        elif action == "request":
            script = str(payload.get("script", arguments.get("script", "")) or "").strip()
            if not script:
                raise ValueError("script is required for apple_notes request")
        else:
            raise ValueError("action must be one of: guide, list, read, search, create, append, request")

        return await self._run_command_via_exec_tool(
            spec_name=spec_name,
            argv=["osascript", "-e", script],
            timeout=timeout,
            ctx=ctx,
            env_overrides=env_overrides,
        )

    @staticmethod
    def _notion_token(arguments: dict[str, Any], *, env_overrides: dict[str, str] | None = None) -> str:
        payload = SkillTool._skill_payload(arguments)
        for key in ("token", "api_key", "notion_api_key", "notionApiKey"):
            text = str(payload.get(key, arguments.get(key, "")) or "").strip()
            if text:
                return text
        if env_overrides:
            text = str(env_overrides.get("NOTION_API_KEY", "") or "").strip()
            if text:
                return text
        text = str(os.getenv("NOTION_API_KEY", "") or "").strip()
        if text:
            return text
        raise RuntimeError("notion_auth_missing")

    @staticmethod
    def _notion_version(arguments: dict[str, Any]) -> str:
        payload = SkillTool._skill_payload(arguments)
        version = str(payload.get("notion_version", arguments.get("notion_version", "")) or "").strip()
        if version:
            return version
        return "2022-06-28"

    @staticmethod
    def _notion_json_payload(arguments: dict[str, Any], *keys: str) -> dict[str, Any]:
        payload = SkillTool._skill_payload(arguments)
        for key in keys:
            value = payload.get(key)
            if isinstance(value, dict):
                return value
        return {}

    async def _notion_request(
        self,
        *,
        method: str,
        path: str,
        payload: dict[str, Any],
        timeout: float,
        token: str,
        notion_version: str,
        spec_name: str,
    ) -> str:
        clean_method = str(method or "").strip().upper()
        if clean_method not in {"GET", "POST", "PATCH", "DELETE"}:
            raise ValueError("notion_invalid_method")
        clean_path = str(path or "").strip()
        if not clean_path:
            raise ValueError("notion_path_required")
        if not clean_path.startswith("/"):
            clean_path = f"/{clean_path}"

        headers = {
            "Authorization": f"Bearer {token}",
            "Notion-Version": notion_version,
            "Content-Type": "application/json",
        }
        url = f"https://api.notion.com/v1{clean_path}"

        try:
            async with httpx.AsyncClient(timeout=max(5.0, min(timeout, 60.0))) as client:
                if clean_method == "GET":
                    response = await client.get(url, headers=headers, params=payload or None)
                elif clean_method == "POST":
                    response = await client.post(url, headers=headers, json=payload)
                elif clean_method == "PATCH":
                    response = await client.patch(url, headers=headers, json=payload)
                else:
                    delete_content = json.dumps(payload, ensure_ascii=False) if payload else None
                    response = await client.request("DELETE", url, headers=headers, content=delete_content)
        except httpx.HTTPError as exc:
            return f"skill_blocked:{spec_name}:notion_request_failed:{exc.__class__.__name__.lower()}"

        try:
            decoded = response.json()
        except ValueError:
            decoded = {
                "status_code": int(response.status_code),
                "text": str(response.text or "").strip(),
            }

        if int(response.status_code) >= 400:
            if isinstance(decoded, dict):
                detail = str(decoded.get("message", decoded.get("code", "notion_http_error")) or "notion_http_error").strip()
            else:
                detail = "notion_http_error"
            return f"skill_blocked:{spec_name}:notion_http_error:{response.status_code}:{detail}"

        return json.dumps(decoded, ensure_ascii=False)

    async def _run_notion(
        self,
        arguments: dict[str, Any],
        *,
        spec_name: str,
        timeout: float,
        env_overrides: dict[str, str] | None = None,
    ) -> str:
        payload = self._skill_payload(arguments)
        action = str(payload.get("action", arguments.get("action", "guide")) or "guide").strip().lower()
        notion_version = self._notion_version(arguments)

        def _resolve_data_payload() -> dict[str, Any]:
            for key in ("data", "body", "payload"):
                value = payload.get(key)
                if isinstance(value, dict):
                    return dict(value)
            return {}

        if action == "guide":
            return json.dumps(
                {
                    "status": "ok",
                    "mode": "guide",
                    "skill": spec_name,
                    "backend": "notion_api",
                    "default_notion_version": notion_version,
                    "usage": "Set tool_arguments.action and provide action-specific fields in tool_arguments.",
                    "auth": {"required_env": ["NOTION_API_KEY"]},
                    "available_actions": [
                        "search",
                        "page_get",
                        "page_create",
                        "page_update",
                        "database_query",
                        "blocks_children",
                        "blocks_append",
                        "request",
                    ],
                    "examples": [
                        {"action": "search", "tool_arguments": {"action": "search", "query": "incident runbook"}},
                        {"action": "page_get", "tool_arguments": {"action": "page_get", "page_id": "<page_id>"}},
                        {"action": "database_query", "tool_arguments": {"action": "database_query", "database_id": "<db_id>", "data": {"page_size": 10}}},
                    ],
                },
                ensure_ascii=False,
            )

        try:
            token = self._notion_token(arguments, env_overrides=env_overrides)
        except RuntimeError as exc:
            return f"skill_blocked:{spec_name}:{str(exc)}"

        if action == "search":
            query = str(payload.get("query", arguments.get("query", "")) or "").strip()
            search_payload = _resolve_data_payload()
            if query and "query" not in search_payload:
                search_payload["query"] = query
            return await self._notion_request(
                method="POST",
                path="/search",
                payload=search_payload,
                timeout=timeout,
                token=token,
                notion_version=notion_version,
                spec_name=spec_name,
            )

        if action == "page_get":
            page_id = str(payload.get("page_id", payload.get("pageId", arguments.get("page_id", ""))) or "").strip()
            if not page_id:
                raise ValueError("page_id is required for notion page_get")
            return await self._notion_request(
                method="GET",
                path=f"/pages/{page_id}",
                payload={},
                timeout=timeout,
                token=token,
                notion_version=notion_version,
                spec_name=spec_name,
            )

        if action == "page_create":
            create_payload = _resolve_data_payload()
            if not create_payload:
                raise ValueError("data is required for notion page_create")
            return await self._notion_request(
                method="POST",
                path="/pages",
                payload=create_payload,
                timeout=timeout,
                token=token,
                notion_version=notion_version,
                spec_name=spec_name,
            )

        if action == "page_update":
            page_id = str(payload.get("page_id", payload.get("pageId", arguments.get("page_id", ""))) or "").strip()
            if not page_id:
                raise ValueError("page_id is required for notion page_update")
            update_payload = _resolve_data_payload()
            if not update_payload:
                raise ValueError("data is required for notion page_update")
            return await self._notion_request(
                method="PATCH",
                path=f"/pages/{page_id}",
                payload=update_payload,
                timeout=timeout,
                token=token,
                notion_version=notion_version,
                spec_name=spec_name,
            )

        if action == "database_query":
            database_id = str(payload.get("database_id", payload.get("databaseId", arguments.get("database_id", ""))) or "").strip()
            if not database_id:
                raise ValueError("database_id is required for notion database_query")
            query_payload = _resolve_data_payload()
            return await self._notion_request(
                method="POST",
                path=f"/databases/{database_id}/query",
                payload=query_payload,
                timeout=timeout,
                token=token,
                notion_version=notion_version,
                spec_name=spec_name,
            )

        if action == "blocks_children":
            block_id = str(payload.get("block_id", payload.get("blockId", arguments.get("block_id", ""))) or "").strip()
            if not block_id:
                raise ValueError("block_id is required for notion blocks_children")
            query: dict[str, Any] = {}
            if "page_size" in payload:
                query["page_size"] = payload.get("page_size")
            if "start_cursor" in payload:
                query["start_cursor"] = payload.get("start_cursor")
            return await self._notion_request(
                method="GET",
                path=f"/blocks/{block_id}/children",
                payload=query,
                timeout=timeout,
                token=token,
                notion_version=notion_version,
                spec_name=spec_name,
            )

        if action == "blocks_append":
            block_id = str(payload.get("block_id", payload.get("blockId", arguments.get("block_id", ""))) or "").strip()
            if not block_id:
                raise ValueError("block_id is required for notion blocks_append")
            append_payload = _resolve_data_payload()
            if not append_payload:
                raise ValueError("data is required for notion blocks_append")
            return await self._notion_request(
                method="POST",
                path=f"/blocks/{block_id}/children",
                payload=append_payload,
                timeout=timeout,
                token=token,
                notion_version=notion_version,
                spec_name=spec_name,
            )

        if action == "request":
            method = str(payload.get("method", arguments.get("method", "GET")) or "GET").strip().upper()
            path = str(payload.get("path", arguments.get("path", "")) or "").strip()
            data = _resolve_data_payload()
            return await self._notion_request(
                method=method,
                path=path,
                payload=data,
                timeout=timeout,
                token=token,
                notion_version=notion_version,
                spec_name=spec_name,
            )

        raise ValueError("action must be one of: guide, search, page_get, page_create, page_update, database_query, blocks_children, blocks_append, request")

    @staticmethod
    def _jira_auth(arguments: dict[str, Any], *, env_overrides: dict[str, str] | None = None) -> tuple[str, str, str]:
        payload = SkillTool._skill_payload(arguments)

        def _pick(*keys: str) -> str:
            for key in keys:
                value = str(payload.get(key, arguments.get(key, "")) or "").strip()
                if value:
                    return value
            if env_overrides:
                for key in keys:
                    value = str(env_overrides.get(key.upper(), "") or "").strip()
                    if value:
                        return value
            for key in keys:
                value = str(os.getenv(key.upper(), "") or "").strip()
                if value:
                    return value
            return ""

        base_url = _pick("jira_base_url", "base_url")
        email = _pick("jira_email", "email")
        token = _pick("jira_api_token", "api_token", "token")
        if not base_url or not email or not token:
            raise RuntimeError("jira_auth_missing")
        return base_url.rstrip("/"), email, token

    async def _jira_request(
        self,
        *,
        method: str,
        base_url: str,
        email: str,
        token: str,
        path: str,
        payload: dict[str, Any],
        timeout: float,
        spec_name: str,
    ) -> str:
        clean_method = str(method or "").strip().upper()
        if clean_method not in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
            raise ValueError("jira_invalid_method")
        clean_path = str(path or "").strip()
        if not clean_path:
            raise ValueError("jira_path_required")
        if not clean_path.startswith("/"):
            clean_path = f"/{clean_path}"

        creds = base64.b64encode(f"{email}:{token}".encode("utf-8")).decode("ascii")
        headers = {
            "Authorization": f"Basic {creds}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        url = f"{base_url}/rest/api/3{clean_path}"

        try:
            async with httpx.AsyncClient(timeout=max(5.0, min(timeout, 60.0))) as client:
                if clean_method == "GET":
                    response = await client.get(url, headers=headers, params=payload or None)
                else:
                    response = await client.request(clean_method, url, headers=headers, json=payload or None)
        except httpx.HTTPError as exc:
            return f"skill_blocked:{spec_name}:jira_request_failed:{exc.__class__.__name__.lower()}"

        try:
            decoded = response.json()
        except ValueError:
            decoded = {
                "status_code": int(response.status_code),
                "text": str(response.text or "").strip(),
            }

        if int(response.status_code) >= 400:
            detail = "jira_http_error"
            if isinstance(decoded, dict):
                messages = decoded.get("errorMessages")
                if isinstance(messages, list) and messages:
                    detail = str(messages[0] or detail)
                else:
                    detail = str(decoded.get("message", detail) or detail)
            return f"skill_blocked:{spec_name}:jira_http_error:{response.status_code}:{detail}"
        return json.dumps(decoded, ensure_ascii=False)

    async def _run_jira(
        self,
        arguments: dict[str, Any],
        *,
        spec_name: str,
        timeout: float,
        env_overrides: dict[str, str] | None = None,
    ) -> str:
        payload = self._skill_payload(arguments)
        action = str(payload.get("action", arguments.get("action", "guide")) or "guide").strip().lower()

        def _data() -> dict[str, Any]:
            for key in ("data", "body", "payload"):
                value = payload.get(key)
                if isinstance(value, dict):
                    return dict(value)
            return {}

        if action == "guide":
            return json.dumps(
                {
                    "status": "ok",
                    "mode": "guide",
                    "skill": spec_name,
                    "backend": "jira_rest_v3",
                    "usage": "Set tool_arguments.action and provide action-specific fields in tool_arguments.",
                    "auth": {"required_env": ["JIRA_BASE_URL", "JIRA_EMAIL", "JIRA_API_TOKEN"]},
                    "available_actions": [
                        "issue_get",
                        "search",
                        "issue_create",
                        "transition_list",
                        "transition_issue",
                        "comment_add",
                        "request",
                    ],
                    "examples": [
                        {"action": "search", "tool_arguments": {"action": "search", "jql": "project = CORE", "max_results": 20}},
                        {"action": "issue_get", "tool_arguments": {"action": "issue_get", "issue_key": "CORE-123"}},
                        {"action": "comment_add", "tool_arguments": {"action": "comment_add", "issue_key": "CORE-123", "text": "Investigating now."}},
                    ],
                },
                ensure_ascii=False,
            )

        try:
            base_url, email, token = self._jira_auth(arguments, env_overrides=env_overrides)
        except RuntimeError as exc:
            return f"skill_blocked:{spec_name}:{str(exc)}"

        issue_key = str(payload.get("issue_key", payload.get("issueKey", arguments.get("issue_key", ""))) or "").strip()

        if action == "issue_get":
            if not issue_key:
                raise ValueError("issue_key is required for jira issue_get")
            return await self._jira_request(
                method="GET",
                base_url=base_url,
                email=email,
                token=token,
                path=f"/issue/{issue_key}",
                payload={},
                timeout=timeout,
                spec_name=spec_name,
            )

        if action == "search":
            query = str(payload.get("jql", arguments.get("jql", "")) or "").strip()
            if not query:
                raise ValueError("jql is required for jira search")
            max_results = int(payload.get("max_results", payload.get("maxResults", arguments.get("max_results", 20))) or 20)
            return await self._jira_request(
                method="GET",
                base_url=base_url,
                email=email,
                token=token,
                path="/search",
                payload={"jql": query, "maxResults": max(1, min(max_results, 200))},
                timeout=timeout,
                spec_name=spec_name,
            )

        if action == "issue_create":
            create_payload = _data()
            if not create_payload:
                raise ValueError("data is required for jira issue_create")
            return await self._jira_request(
                method="POST",
                base_url=base_url,
                email=email,
                token=token,
                path="/issue",
                payload=create_payload,
                timeout=timeout,
                spec_name=spec_name,
            )

        if action == "transition_list":
            if not issue_key:
                raise ValueError("issue_key is required for jira transition_list")
            return await self._jira_request(
                method="GET",
                base_url=base_url,
                email=email,
                token=token,
                path=f"/issue/{issue_key}/transitions",
                payload={},
                timeout=timeout,
                spec_name=spec_name,
            )

        if action == "transition_issue":
            if not issue_key:
                raise ValueError("issue_key is required for jira transition_issue")
            transition_id = str(payload.get("transition_id", payload.get("transitionId", arguments.get("transition_id", ""))) or "").strip()
            transition_payload = _data()
            if transition_id:
                transition_payload["transition"] = {"id": transition_id}
            if not transition_payload:
                raise ValueError("transition_id or data is required for jira transition_issue")
            return await self._jira_request(
                method="POST",
                base_url=base_url,
                email=email,
                token=token,
                path=f"/issue/{issue_key}/transitions",
                payload=transition_payload,
                timeout=timeout,
                spec_name=spec_name,
            )

        if action == "comment_add":
            if not issue_key:
                raise ValueError("issue_key is required for jira comment_add")
            comment_payload = _data()
            if not comment_payload:
                text = str(payload.get("text", arguments.get("text", "")) or "").strip()
                if not text:
                    raise ValueError("text or data is required for jira comment_add")
                comment_payload = {
                    "body": {
                        "type": "doc",
                        "version": 1,
                        "content": [{"type": "paragraph", "content": [{"type": "text", "text": text}]}],
                    }
                }
            return await self._jira_request(
                method="POST",
                base_url=base_url,
                email=email,
                token=token,
                path=f"/issue/{issue_key}/comment",
                payload=comment_payload,
                timeout=timeout,
                spec_name=spec_name,
            )

        if action == "request":
            method = str(payload.get("method", arguments.get("method", "GET")) or "GET").strip().upper()
            path = str(payload.get("path", arguments.get("path", "")) or "").strip()
            return await self._jira_request(
                method=method,
                base_url=base_url,
                email=email,
                token=token,
                path=path,
                payload=_data(),
                timeout=timeout,
                spec_name=spec_name,
            )

        raise ValueError("action must be one of: guide, issue_get, search, issue_create, transition_list, transition_issue, comment_add, request")

    @staticmethod
    def _linear_token(arguments: dict[str, Any], *, env_overrides: dict[str, str] | None = None) -> str:
        payload = SkillTool._skill_payload(arguments)
        for key in ("token", "api_key", "linear_api_key", "linearApiKey"):
            text = str(payload.get(key, arguments.get(key, "")) or "").strip()
            if text:
                return text
        if env_overrides:
            text = str(env_overrides.get("LINEAR_API_KEY", "") or "").strip()
            if text:
                return text
        text = str(os.getenv("LINEAR_API_KEY", "") or "").strip()
        if text:
            return text
        raise RuntimeError("linear_auth_missing")

    async def _linear_request(
        self,
        *,
        endpoint: str,
        token: str,
        query: str,
        variables: dict[str, Any],
        timeout: float,
        spec_name: str,
    ) -> str:
        if not query.strip():
            raise ValueError("linear_query_required")
        headers = {
            "Authorization": token,
            "Content-Type": "application/json",
        }
        payload = {"query": query, "variables": variables or {}}
        try:
            async with httpx.AsyncClient(timeout=max(5.0, min(timeout, 60.0))) as client:
                response = await client.post(endpoint, headers=headers, json=payload)
        except httpx.HTTPError as exc:
            return f"skill_blocked:{spec_name}:linear_request_failed:{exc.__class__.__name__.lower()}"

        try:
            decoded = response.json()
        except ValueError:
            decoded = {"status_code": int(response.status_code), "text": str(response.text or "").strip()}
        if int(response.status_code) >= 400:
            return f"skill_blocked:{spec_name}:linear_http_error:{response.status_code}"
        if isinstance(decoded, dict) and decoded.get("errors"):
            first = decoded.get("errors")
            detail = "linear_graphql_error"
            if isinstance(first, list) and first:
                first_item = first[0]
                if isinstance(first_item, dict):
                    detail = str(first_item.get("message", detail) or detail)
            return f"skill_blocked:{spec_name}:linear_graphql_error:{detail}"
        return json.dumps(decoded, ensure_ascii=False)

    async def _run_linear(
        self,
        arguments: dict[str, Any],
        *,
        spec_name: str,
        timeout: float,
        env_overrides: dict[str, str] | None = None,
    ) -> str:
        payload = self._skill_payload(arguments)
        action = str(payload.get("action", arguments.get("action", "guide")) or "guide").strip().lower()
        endpoint = str(payload.get("endpoint", arguments.get("endpoint", "https://api.linear.app/graphql")) or "https://api.linear.app/graphql").strip()

        if action == "guide":
            return json.dumps(
                {
                    "status": "ok",
                    "mode": "guide",
                    "skill": spec_name,
                    "backend": "linear_graphql",
                    "endpoint": endpoint,
                    "usage": "Set tool_arguments.action and provide action-specific fields in tool_arguments.",
                    "auth": {"required_env": ["LINEAR_API_KEY"]},
                    "available_actions": ["issues_list", "issue_create", "issue_update", "request"],
                    "examples": [
                        {"action": "issues_list", "tool_arguments": {"action": "issues_list", "first": 20, "state": "In Progress"}},
                        {"action": "issue_create", "tool_arguments": {"action": "issue_create", "title": "Fix auth bug", "team_id": "<team_id>"}},
                        {"action": "request", "tool_arguments": {"action": "request", "query": "query { viewer { id name } }"}},
                    ],
                },
                ensure_ascii=False,
            )

        try:
            token = self._linear_token(arguments, env_overrides=env_overrides)
        except RuntimeError as exc:
            return f"skill_blocked:{spec_name}:{str(exc)}"

        if action == "issues_list":
            first = int(payload.get("first", arguments.get("first", 20)) or 20)
            state_name = str(payload.get("state", arguments.get("state", "")) or "").strip()
            query = (
                "query IssuesList($first: Int!, $state: String) { "
                "issues(first: $first, filter: { state: { name: { eq: $state } } }) { "
                "nodes { id identifier title priority state { name } assignee { name } } } }"
            )
            variables: dict[str, Any] = {"first": max(1, min(first, 100)), "state": state_name or None}
            if not state_name:
                query = (
                    "query IssuesList($first: Int!) { "
                    "issues(first: $first) { nodes { id identifier title priority state { name } assignee { name } } } }"
                )
                variables = {"first": max(1, min(first, 100))}
            return await self._linear_request(
                endpoint=endpoint,
                token=token,
                query=query,
                variables=variables,
                timeout=timeout,
                spec_name=spec_name,
            )

        if action == "issue_create":
            title = str(payload.get("title", arguments.get("title", "")) or "").strip()
            team_id = str(payload.get("team_id", payload.get("teamId", arguments.get("team_id", ""))) or "").strip()
            if not title or not team_id:
                raise ValueError("title and team_id are required for linear issue_create")
            query = (
                "mutation IssueCreate($title: String!, $teamId: String!, $description: String, $priority: Float) { "
                "issueCreate(input: { title: $title, teamId: $teamId, description: $description, priority: $priority }) "
                "{ issue { id identifier url } } }"
            )
            variables = {
                "title": title,
                "teamId": team_id,
                "description": str(payload.get("description", arguments.get("description", "")) or "").strip() or None,
                "priority": payload.get("priority", arguments.get("priority")),
            }
            return await self._linear_request(
                endpoint=endpoint,
                token=token,
                query=query,
                variables=variables,
                timeout=timeout,
                spec_name=spec_name,
            )

        if action == "issue_update":
            issue_id = str(payload.get("issue_id", payload.get("issueId", arguments.get("issue_id", ""))) or "").strip()
            update_input = payload.get("input")
            if not issue_id or not isinstance(update_input, dict) or not update_input:
                raise ValueError("issue_id and input are required for linear issue_update")
            query = (
                "mutation IssueUpdate($id: String!, $input: IssueUpdateInput!) { "
                "issueUpdate(id: $id, input: $input) { issue { id identifier title state { name } } } }"
            )
            return await self._linear_request(
                endpoint=endpoint,
                token=token,
                query=query,
                variables={"id": issue_id, "input": dict(update_input)},
                timeout=timeout,
                spec_name=spec_name,
            )

        if action == "request":
            query = str(payload.get("query", arguments.get("query", "")) or "").strip()
            raw_variables = payload.get("variables")
            variables: dict[str, Any]
            if isinstance(raw_variables, dict):
                variables = dict(raw_variables)
            else:
                variables = {}
            return await self._linear_request(
                endpoint=endpoint,
                token=token,
                query=query,
                variables=variables,
                timeout=timeout,
                spec_name=spec_name,
            )

        raise ValueError("action must be one of: guide, issues_list, issue_create, issue_update, request")

    @staticmethod
    def _trello_auth(arguments: dict[str, Any], *, env_overrides: dict[str, str] | None = None) -> tuple[str, str, str]:
        payload = SkillTool._skill_payload(arguments)

        def _pick(*keys: str) -> str:
            for key in keys:
                value = str(payload.get(key, arguments.get(key, "")) or "").strip()
                if value:
                    return value
            if env_overrides:
                for key in keys:
                    value = str(env_overrides.get(key.upper(), "") or "").strip()
                    if value:
                        return value
            for key in keys:
                value = str(os.getenv(key.upper(), "") or "").strip()
                if value:
                    return value
            return ""

        api_key = _pick("trello_api_key", "api_key", "key")
        token = _pick("trello_token", "token")
        base_url = _pick("trello_base_url", "base_url") or "https://api.trello.com/1"
        if not api_key or not token:
            raise RuntimeError("trello_auth_missing")
        return base_url.rstrip("/"), api_key, token

    async def _trello_request(
        self,
        *,
        method: str,
        base_url: str,
        api_key: str,
        token: str,
        path: str,
        payload: dict[str, Any],
        timeout: float,
        spec_name: str,
    ) -> str:
        clean_method = str(method or "").strip().upper()
        if clean_method not in {"GET", "POST", "PUT", "DELETE"}:
            raise ValueError("trello_invalid_method")
        clean_path = str(path or "").strip()
        if not clean_path:
            raise ValueError("trello_path_required")
        if not clean_path.startswith("/"):
            clean_path = f"/{clean_path}"

        url = f"{base_url}{clean_path}"
        query_params = {"key": api_key, "token": token}
        if clean_method == "GET":
            query_params.update(payload)

        try:
            async with httpx.AsyncClient(timeout=max(5.0, min(timeout, 60.0))) as client:
                if clean_method == "GET":
                    response = await client.get(url, params=query_params)
                else:
                    response = await client.request(clean_method, url, params=query_params, json=payload or None)
        except httpx.HTTPError as exc:
            return f"skill_blocked:{spec_name}:trello_request_failed:{exc.__class__.__name__.lower()}"

        try:
            decoded = response.json()
        except ValueError:
            decoded = {
                "status_code": int(response.status_code),
                "text": str(response.text or "").strip(),
            }

        if int(response.status_code) >= 400:
            detail = "trello_http_error"
            if isinstance(decoded, dict):
                detail = str(decoded.get("message", decoded.get("error", detail)) or detail)
            return f"skill_blocked:{spec_name}:trello_http_error:{response.status_code}:{detail}"
        return json.dumps(decoded, ensure_ascii=False)

    async def _run_trello(
        self,
        arguments: dict[str, Any],
        *,
        spec_name: str,
        timeout: float,
        env_overrides: dict[str, str] | None = None,
    ) -> str:
        payload = self._skill_payload(arguments)
        action = str(payload.get("action", arguments.get("action", "guide")) or "guide").strip().lower()

        if action == "guide":
            return json.dumps(
                {
                    "status": "ok",
                    "mode": "guide",
                    "skill": spec_name,
                    "backend": "trello_rest_v1",
                    "usage": "Set tool_arguments.action and provide action-specific fields in tool_arguments.",
                    "auth": {"required_env": ["TRELLO_API_KEY", "TRELLO_TOKEN"]},
                    "available_actions": [
                        "boards_list",
                        "board_lists",
                        "board_cards",
                        "list_cards",
                        "list_create",
                        "card_create",
                        "card_move",
                        "card_comment",
                        "card_archive",
                        "request",
                    ],
                    "examples": [
                        {"action": "boards_list", "tool_arguments": {"action": "boards_list", "fields": "id,name,url"}},
                        {"action": "card_create", "tool_arguments": {"action": "card_create", "list_id": "<list_id>", "name": "Follow up"}},
                        {"action": "card_move", "tool_arguments": {"action": "card_move", "card_id": "<card_id>", "list_id": "<target_list_id>"}},
                    ],
                },
                ensure_ascii=False,
            )

        try:
            base_url, api_key, token = self._trello_auth(arguments, env_overrides=env_overrides)
        except RuntimeError as exc:
            return f"skill_blocked:{spec_name}:{str(exc)}"

        board_id = str(payload.get("board_id", payload.get("boardId", arguments.get("board_id", ""))) or "").strip()
        list_id = str(payload.get("list_id", payload.get("listId", arguments.get("list_id", ""))) or "").strip()
        card_id = str(payload.get("card_id", payload.get("cardId", arguments.get("card_id", ""))) or "").strip()

        if action == "boards_list":
            return await self._trello_request(
                method="GET",
                base_url=base_url,
                api_key=api_key,
                token=token,
                path="/members/me/boards",
                payload={"fields": str(payload.get("fields", arguments.get("fields", "id,name,url")) or "id,name,url")},
                timeout=timeout,
                spec_name=spec_name,
            )

        if action == "board_lists":
            if not board_id:
                raise ValueError("board_id is required for trello board_lists")
            return await self._trello_request(
                method="GET",
                base_url=base_url,
                api_key=api_key,
                token=token,
                path=f"/boards/{board_id}/lists",
                payload={},
                timeout=timeout,
                spec_name=spec_name,
            )

        if action == "board_cards":
            if not board_id:
                raise ValueError("board_id is required for trello board_cards")
            return await self._trello_request(
                method="GET",
                base_url=base_url,
                api_key=api_key,
                token=token,
                path=f"/boards/{board_id}/cards",
                payload={},
                timeout=timeout,
                spec_name=spec_name,
            )

        if action == "list_cards":
            if not list_id:
                raise ValueError("list_id is required for trello list_cards")
            return await self._trello_request(
                method="GET",
                base_url=base_url,
                api_key=api_key,
                token=token,
                path=f"/lists/{list_id}/cards",
                payload={},
                timeout=timeout,
                spec_name=spec_name,
            )

        if action == "list_create":
            if not board_id:
                raise ValueError("board_id is required for trello list_create")
            name = str(payload.get("name", arguments.get("name", "")) or "").strip()
            if not name:
                raise ValueError("name is required for trello list_create")
            pos = str(payload.get("pos", arguments.get("pos", "bottom")) or "bottom").strip()
            return await self._trello_request(
                method="POST",
                base_url=base_url,
                api_key=api_key,
                token=token,
                path="/lists",
                payload={"name": name, "idBoard": board_id, "pos": pos},
                timeout=timeout,
                spec_name=spec_name,
            )

        if action == "card_create":
            if not list_id:
                raise ValueError("list_id is required for trello card_create")
            name = str(payload.get("name", arguments.get("name", "")) or "").strip()
            if not name:
                raise ValueError("name is required for trello card_create")
            card_payload: dict[str, Any] = {"idList": list_id, "name": name}
            desc = str(payload.get("desc", arguments.get("desc", "")) or "").strip()
            if desc:
                card_payload["desc"] = desc
            return await self._trello_request(
                method="POST",
                base_url=base_url,
                api_key=api_key,
                token=token,
                path="/cards",
                payload=card_payload,
                timeout=timeout,
                spec_name=spec_name,
            )

        if action == "card_move":
            if not card_id or not list_id:
                raise ValueError("card_id and list_id are required for trello card_move")
            return await self._trello_request(
                method="PUT",
                base_url=base_url,
                api_key=api_key,
                token=token,
                path=f"/cards/{card_id}",
                payload={"idList": list_id},
                timeout=timeout,
                spec_name=spec_name,
            )

        if action == "card_comment":
            if not card_id:
                raise ValueError("card_id is required for trello card_comment")
            text = str(payload.get("text", arguments.get("text", "")) or "").strip()
            if not text:
                raise ValueError("text is required for trello card_comment")
            return await self._trello_request(
                method="POST",
                base_url=base_url,
                api_key=api_key,
                token=token,
                path=f"/cards/{card_id}/actions/comments",
                payload={"text": text},
                timeout=timeout,
                spec_name=spec_name,
            )

        if action == "card_archive":
            if not card_id:
                raise ValueError("card_id is required for trello card_archive")
            return await self._trello_request(
                method="PUT",
                base_url=base_url,
                api_key=api_key,
                token=token,
                path=f"/cards/{card_id}",
                payload={"closed": True},
                timeout=timeout,
                spec_name=spec_name,
            )

        if action == "request":
            method = str(payload.get("method", arguments.get("method", "GET")) or "GET").strip().upper()
            path = str(payload.get("path", arguments.get("path", "")) or "").strip()
            body = payload.get("data")
            if not isinstance(body, dict):
                body = {}
            return await self._trello_request(
                method=method,
                base_url=base_url,
                api_key=api_key,
                token=token,
                path=path,
                payload=body,
                timeout=timeout,
                spec_name=spec_name,
            )

        raise ValueError("action must be one of: guide, boards_list, board_lists, board_cards, list_cards, list_create, card_create, card_move, card_comment, card_archive, request")

    @staticmethod
    def _spotify_pick(
        arguments: dict[str, Any],
        *keys: str,
        env_overrides: dict[str, str] | None = None,
    ) -> str:
        payload = SkillTool._skill_payload(arguments)
        for key in keys:
            value = str(payload.get(key, arguments.get(key, "")) or "").strip()
            if value:
                return value
        if env_overrides:
            for key in keys:
                value = str(env_overrides.get(key.upper(), "") or "").strip()
                if value:
                    return value
        for key in keys:
            value = str(os.getenv(key.upper(), "") or "").strip()
            if value:
                return value
        return ""

    async def _spotify_client_credentials_token(
        self,
        *,
        client_id: str,
        client_secret: str,
        timeout: float,
        spec_name: str,
    ) -> str:
        creds = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("ascii")
        headers = {
            "Authorization": f"Basic {creds}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        try:
            async with httpx.AsyncClient(timeout=max(5.0, min(timeout, 60.0))) as client:
                response = await client.post(
                    "https://accounts.spotify.com/api/token",
                    headers=headers,
                    data={"grant_type": "client_credentials"},
                )
        except httpx.HTTPError as exc:
            raise RuntimeError(f"skill_blocked:{spec_name}:spotify_auth_request_failed:{exc.__class__.__name__.lower()}") from exc

        try:
            decoded = response.json()
        except ValueError:
            decoded = {}
        if int(response.status_code) >= 400:
            detail = "spotify_auth_http_error"
            if isinstance(decoded, dict):
                detail = str(decoded.get("error_description", decoded.get("error", detail)) or detail)
            raise RuntimeError(f"skill_blocked:{spec_name}:spotify_auth_http_error:{response.status_code}:{detail}")
        if not isinstance(decoded, dict):
            raise RuntimeError(f"skill_blocked:{spec_name}:spotify_auth_invalid_payload")
        token = str(decoded.get("access_token", "") or "").strip()
        if not token:
            raise RuntimeError(f"skill_blocked:{spec_name}:spotify_auth_missing_access_token")
        return token

    async def _spotify_token(
        self,
        arguments: dict[str, Any],
        *,
        timeout: float,
        spec_name: str,
        env_overrides: dict[str, str] | None = None,
    ) -> str:
        access_token = self._spotify_pick(
            arguments,
            "spotify_access_token",
            "access_token",
            "token",
            env_overrides=env_overrides,
        )
        if access_token:
            return access_token

        client_id = self._spotify_pick(arguments, "spotify_client_id", "client_id", env_overrides=env_overrides)
        client_secret = self._spotify_pick(arguments, "spotify_client_secret", "client_secret", env_overrides=env_overrides)
        if not client_id or not client_secret:
            raise RuntimeError("spotify_auth_missing")
        return await self._spotify_client_credentials_token(
            client_id=client_id,
            client_secret=client_secret,
            timeout=timeout,
            spec_name=spec_name,
        )

    async def _spotify_request(
        self,
        *,
        method: str,
        token: str,
        path: str,
        params: dict[str, Any],
        payload: dict[str, Any],
        timeout: float,
        spec_name: str,
    ) -> str:
        clean_method = str(method or "").strip().upper()
        if clean_method not in {"GET", "POST", "PUT", "DELETE"}:
            raise ValueError("spotify_invalid_method")
        clean_path = str(path or "").strip()
        if not clean_path:
            raise ValueError("spotify_path_required")
        if not clean_path.startswith("/"):
            clean_path = f"/{clean_path}"

        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        url = f"https://api.spotify.com/v1{clean_path}"
        try:
            async with httpx.AsyncClient(timeout=max(5.0, min(timeout, 60.0))) as client:
                if clean_method == "GET":
                    response = await client.get(url, headers=headers, params=params or None)
                else:
                    response = await client.request(
                        clean_method,
                        url,
                        headers=headers,
                        params=params or None,
                        json=payload or None,
                    )
        except httpx.HTTPError as exc:
            return f"skill_blocked:{spec_name}:spotify_request_failed:{exc.__class__.__name__.lower()}"

        if int(response.status_code) == 204:
            return json.dumps({"ok": True, "status_code": 204}, ensure_ascii=False)

        try:
            decoded = response.json()
        except ValueError:
            decoded = {"status_code": int(response.status_code), "text": str(response.text or "").strip()}

        if int(response.status_code) >= 400:
            detail = "spotify_http_error"
            if isinstance(decoded, dict):
                error = decoded.get("error")
                if isinstance(error, dict):
                    detail = str(error.get("message", detail) or detail)
                else:
                    detail = str(error or detail)
            return f"skill_blocked:{spec_name}:spotify_http_error:{response.status_code}:{detail}"
        return json.dumps(decoded, ensure_ascii=False)

    async def _run_spotify(
        self,
        arguments: dict[str, Any],
        *,
        spec_name: str,
        timeout: float,
        env_overrides: dict[str, str] | None = None,
    ) -> str:
        payload = self._skill_payload(arguments)
        action = str(payload.get("action", arguments.get("action", "guide")) or "guide").strip().lower()

        if action == "guide":
            return json.dumps(
                {
                    "status": "ok",
                    "mode": "guide",
                    "skill": spec_name,
                    "backend": "spotify_web_api",
                    "usage": "Set tool_arguments.action and provide action-specific fields in tool_arguments.",
                    "auth": {
                        "required_env": ["SPOTIFY_CLIENT_ID", "SPOTIFY_CLIENT_SECRET"],
                        "optional_env": ["SPOTIFY_ACCESS_TOKEN"],
                    },
                    "available_actions": [
                        "playback_state",
                        "play",
                        "pause",
                        "next",
                        "previous",
                        "volume",
                        "search",
                        "track_get",
                        "album_get",
                        "playlist_get",
                        "queue_add",
                        "request",
                    ],
                    "examples": [
                        {"action": "search", "tool_arguments": {"action": "search", "query": "radiohead", "type": "track", "limit": 5}},
                        {"action": "playback_state", "tool_arguments": {"action": "playback_state"}},
                        {"action": "queue_add", "tool_arguments": {"action": "queue_add", "uri": "spotify:track:<track_id>"}},
                    ],
                },
                ensure_ascii=False,
            )

        try:
            token = await self._spotify_token(
                arguments,
                timeout=timeout,
                spec_name=spec_name,
                env_overrides=env_overrides,
            )
        except RuntimeError as exc:
            message = str(exc)
            if message.startswith("skill_blocked:"):
                return message
            return f"skill_blocked:{spec_name}:{message}"

        if action == "playback_state":
            return await self._spotify_request(
                method="GET",
                token=token,
                path="/me/player",
                params={},
                payload={},
                timeout=timeout,
                spec_name=spec_name,
            )

        if action in {"play", "pause", "next", "previous"}:
            method = "PUT" if action in {"play", "pause"} else "POST"
            route = {
                "play": "/me/player/play",
                "pause": "/me/player/pause",
                "next": "/me/player/next",
                "previous": "/me/player/previous",
            }[action]
            device_id = str(payload.get("device_id", payload.get("deviceId", arguments.get("device_id", ""))) or "").strip()
            params = {"device_id": device_id} if device_id else {}
            body = payload.get("data")
            if not isinstance(body, dict):
                body = {}
            return await self._spotify_request(
                method=method,
                token=token,
                path=route,
                params=params,
                payload=body,
                timeout=timeout,
                spec_name=spec_name,
            )

        if action == "volume":
            value_raw = payload.get("volume_percent", arguments.get("volume_percent"))
            if value_raw in {None, ""}:
                raise ValueError("volume_percent is required for spotify volume")
            volume_percent = max(0, min(int(str(value_raw)), 100))
            return await self._spotify_request(
                method="PUT",
                token=token,
                path="/me/player/volume",
                params={"volume_percent": volume_percent},
                payload={},
                timeout=timeout,
                spec_name=spec_name,
            )

        if action == "search":
            query = str(payload.get("query", payload.get("q", arguments.get("query", ""))) or "").strip()
            if not query:
                raise ValueError("query is required for spotify search")
            result_types = str(payload.get("type", arguments.get("type", "track,album,playlist")) or "track,album,playlist").strip()
            limit = max(1, min(int(str(payload.get("limit", arguments.get("limit", 10)) or 10)), 50))
            return await self._spotify_request(
                method="GET",
                token=token,
                path="/search",
                params={"q": query, "type": result_types, "limit": limit},
                payload={},
                timeout=timeout,
                spec_name=spec_name,
            )

        if action in {"track_get", "album_get", "playlist_get"}:
            item_id = str(payload.get("id", arguments.get("id", "")) or "").strip()
            if not item_id:
                raise ValueError("id is required for spotify track_get/album_get/playlist_get")
            route = {
                "track_get": f"/tracks/{item_id}",
                "album_get": f"/albums/{item_id}",
                "playlist_get": f"/playlists/{item_id}",
            }[action]
            return await self._spotify_request(
                method="GET",
                token=token,
                path=route,
                params={},
                payload={},
                timeout=timeout,
                spec_name=spec_name,
            )

        if action == "queue_add":
            uri = str(payload.get("uri", arguments.get("uri", "")) or "").strip()
            if not uri:
                raise ValueError("uri is required for spotify queue_add")
            device_id = str(payload.get("device_id", payload.get("deviceId", arguments.get("device_id", ""))) or "").strip()
            params = {"uri": uri}
            if device_id:
                params["device_id"] = device_id
            return await self._spotify_request(
                method="POST",
                token=token,
                path="/me/player/queue",
                params=params,
                payload={},
                timeout=timeout,
                spec_name=spec_name,
            )

        if action == "request":
            method = str(payload.get("method", arguments.get("method", "GET")) or "GET").strip().upper()
            path = str(payload.get("path", arguments.get("path", "")) or "").strip()
            params = payload.get("params")
            if not isinstance(params, dict):
                params = {}
            body = payload.get("data")
            if not isinstance(body, dict):
                body = {}
            return await self._spotify_request(
                method=method,
                token=token,
                path=path,
                params=params,
                payload=body,
                timeout=timeout,
                spec_name=spec_name,
            )

        raise ValueError("action must be one of: guide, playback_state, play, pause, next, previous, volume, search, track_get, album_get, playlist_get, queue_add, request")

    async def _dispatch_script(
        self,
        script_name: str,
        arguments: dict[str, Any],
        ctx: ToolContext,
        *,
        spec_name: str,
        env_overrides: dict[str, str] | None = None,
    ) -> str:
        if script_name == "weather":
            return await self._run_weather(arguments, ctx, spec_name=spec_name)
        if script_name == "summarize":
            return await self._run_summarize(arguments, ctx, spec_name=spec_name, timeout=self._timeout_value(arguments))
        if script_name == "healthcheck":
            return await self._run_healthcheck(arguments, timeout=self._timeout_value(arguments))
        if script_name == "model_usage":
            return await self._run_model_usage(arguments)
        if script_name == "session_logs":
            return await self._run_session_logs(arguments)
        if script_name == "coding_agent":
            return await self._run_coding_agent(arguments, ctx)
        if script_name == "memory":
            return await self._run_memory(arguments, ctx, spec_name=spec_name)
        if script_name == "skald":
            return await self._run_skald(arguments, spec_name=spec_name)
        if script_name == "skill_creator":
            return await self._run_skill_creator(arguments, ctx, spec_name=spec_name)
        if script_name == "gh_issues":
            return await self._run_gh_issues(
                arguments,
                ctx,
                spec_name=spec_name,
                timeout=self._timeout_value(arguments),
                env_overrides=env_overrides or {},
            )
        if script_name == "github":
            return await self._run_github(
                arguments,
                ctx,
                spec_name=spec_name,
                timeout=self._timeout_value(arguments),
                env_overrides=env_overrides or {},
            )
        if script_name == "clawhub":
            return await self._run_clawhub(
                arguments,
                ctx,
                spec_name=spec_name,
                timeout=self._timeout_value(arguments),
                env_overrides=env_overrides or {},
            )
        if script_name == "onepassword":
            return await self._run_onepassword(
                arguments,
                ctx,
                spec_name=spec_name,
                timeout=self._timeout_value(arguments),
                env_overrides=env_overrides or {},
            )
        if script_name == "docker":
            return await self._run_docker(
                arguments,
                ctx,
                spec_name=spec_name,
                timeout=self._timeout_value(arguments),
                env_overrides=env_overrides or {},
            )
        if script_name == "tmux":
            return await self._run_tmux(
                arguments,
                ctx,
                spec_name=spec_name,
                timeout=self._timeout_value(arguments),
                env_overrides=env_overrides or {},
            )
        if script_name == "obsidian":
            return await self._run_obsidian(
                arguments,
                spec_name=spec_name,
                env_overrides=env_overrides,
            )
        if script_name == "apple_notes":
            return await self._run_apple_notes(
                arguments,
                ctx,
                spec_name=spec_name,
                timeout=self._timeout_value(arguments),
                env_overrides=env_overrides or {},
            )
        if script_name == "notion":
            return await self._run_notion(
                arguments,
                spec_name=spec_name,
                timeout=self._timeout_value(arguments),
                env_overrides=env_overrides,
            )
        if script_name == "jira":
            return await self._run_jira(
                arguments,
                spec_name=spec_name,
                timeout=self._timeout_value(arguments),
                env_overrides=env_overrides,
            )
        if script_name == "linear":
            return await self._run_linear(
                arguments,
                spec_name=spec_name,
                timeout=self._timeout_value(arguments),
                env_overrides=env_overrides,
            )
        if script_name == "trello":
            return await self._run_trello(
                arguments,
                spec_name=spec_name,
                timeout=self._timeout_value(arguments),
                env_overrides=env_overrides,
            )
        if script_name == "spotify":
            return await self._run_spotify(
                arguments,
                spec_name=spec_name,
                timeout=self._timeout_value(arguments),
                env_overrides=env_overrides,
            )

        target_tool = self.registry.get(script_name)
        if target_tool is not None and script_name != self.name:
            tool_arguments = self._script_tool_arguments(script_name, arguments)
            try:
                return await self.registry.execute(
                    script_name,
                    tool_arguments,
                    session_id=ctx.session_id,
                    channel=ctx.channel,
                    user_id=ctx.user_id,
                )
            except RuntimeError as exc:
                if str(exc).startswith(f"tool_blocked_by_safety_policy:{script_name}:"):
                    return f"skill_blocked:{spec_name}:{exc}"
                if str(exc).startswith(f"tool_requires_approval:{script_name}:"):
                    return f"skill_requires_approval:{spec_name}:{exc}"
                raise

        return f"skill_script_unavailable:{script_name}"

    async def run(self, arguments: dict[str, Any], ctx: ToolContext) -> str:
        name = str(arguments.get("name", "")).strip()
        log = bind_event("tool.skill", session=ctx.session_id, tool=self.name)
        if not name:
            raise ValueError("skill name is required")

        spec = self.loader.get(name)
        if spec is None:
            raise ValueError(f"skill_not_found:{name}")
        if not spec.enabled:
            return f"skill_disabled:{spec.name}"
        if not spec.available:
            details = ", ".join([*spec.missing, *spec.contract_issues])
            return f"skill_unavailable:{spec.name}:{details}"

        extra_args = self._extra_args(arguments)
        args_guard_error = self._guard_extra_args(extra_args)
        if args_guard_error:
            return f"skill_blocked:{spec.name}:{args_guard_error}"

        allowed, reason = await self._memory_policy_allows(session_id=ctx.session_id)
        if not allowed:
            return f"skill_blocked:{spec.name}:memory_policy:{reason}"

        timeout = self._timeout_value(arguments)
        env_overrides = self.loader.resolved_env_overrides(spec)

        if spec.execution_kind == "command":
            argv = [*spec.execution_argv, *extra_args]
            if spec.execution_argv and spec.execution_argv[0] == "gh":
                auth_error = await self._precheck_github_auth(
                    spec_name=spec.name,
                    timeout=timeout,
                    ctx=ctx,
                    env_overrides=env_overrides,
                )
                if auth_error is not None:
                    return auth_error
            log.info("running skill command skill={}", spec.name)
            if self.registry.get("exec") is not None:
                return await self._run_command_via_exec_tool(
                    spec_name=spec.name,
                    argv=argv,
                    timeout=timeout,
                    ctx=ctx,
                    env_overrides=env_overrides,
                )
            return f"skill_blocked:{spec.name}:exec_tool_not_registered"

        if spec.execution_kind == "script":
            log.info("running skill script skill={} script={}", spec.name, spec.execution_target)
            return await self._dispatch_script(
                spec.execution_target,
                arguments,
                ctx,
                spec_name=spec.name,
                env_overrides=env_overrides,
            )

        if spec.execution_kind == "invalid":
            details = ", ".join(spec.contract_issues)
            return f"skill_invalid_contract:{spec.name}:{details}"

        return f"skill_not_executable:{spec.name}"
