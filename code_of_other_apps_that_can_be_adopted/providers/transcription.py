from __future__ import annotations

import asyncio
from pathlib import Path
import random
from typing import Any

import httpx

from clawlite.providers.reliability import is_quota_429_error, parse_retry_after_seconds


class TranscriptionProvider:
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = "https://api.groq.com/openai/v1",
        model: str = "whisper-large-v3-turbo",
        timeout_s: float = 90.0,
        retry_max_attempts: int = 3,
        retry_initial_backoff_s: float = 0.5,
        retry_max_backoff_s: float = 8.0,
        retry_jitter_s: float = 0.2,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_s = max(0.1, float(timeout_s))
        self.retry_max_attempts = max(1, int(retry_max_attempts))
        self.retry_initial_backoff_s = max(0.0, float(retry_initial_backoff_s))
        self.retry_max_backoff_s = max(self.retry_initial_backoff_s, float(retry_max_backoff_s))
        self.retry_jitter_s = max(0.0, float(retry_jitter_s))

    def _retry_delay(self, attempt: int, *, retry_after_s: float | None = None) -> float:
        if retry_after_s is not None:
            return max(0.0, float(retry_after_s))
        base = self.retry_initial_backoff_s * (2 ** max(0, attempt - 1))
        capped = min(base, self.retry_max_backoff_s)
        return max(0.0, capped + random.uniform(0.0, self.retry_jitter_s))

    @staticmethod
    def _error_detail(response: httpx.Response | None) -> str:
        if response is None:
            return ""
        detail = ""
        try:
            payload = response.json()
        except Exception:
            payload = None
        if isinstance(payload, dict):
            error_obj = payload.get("error")
            if isinstance(error_obj, dict):
                detail = str(error_obj.get("message", "")).strip()
            if not detail:
                detail = str(payload.get("message", "") or payload.get("detail", "")).strip()
        if not detail:
            detail = (response.text or "").strip()
        return " ".join(detail.split())[:300]

    async def transcribe(self, audio_path: str | Path, *, language: str = "pt") -> str:
        path = Path(audio_path)
        if not path.exists():
            raise FileNotFoundError(str(path))

        headers = {"authorization": f"Bearer {self.api_key}"}
        data: dict[str, Any] = {"model": self.model, "language": language}

        url = f"{self.base_url}/audio/transcriptions"
        async with httpx.AsyncClient(timeout=self.timeout_s) as client:
            for attempt in range(1, self.retry_max_attempts + 1):
                try:
                    with path.open("rb") as audio_fp:
                        files = {"file": (path.name, audio_fp, "audio/mpeg")}
                        response = await client.post(url, headers=headers, files=files, data=data)
                    response.raise_for_status()
                    payload = response.json()
                    return str(payload.get("text", "")).strip()
                except httpx.HTTPStatusError as exc:
                    status = exc.response.status_code if exc.response is not None else None
                    detail = self._error_detail(exc.response)
                    retry_after = parse_retry_after_seconds(exc.response.headers.get("retry-after") if exc.response is not None else "")
                    hard_quota = status == 429 and is_quota_429_error(detail)
                    should_retry = (
                        status is not None
                        and status in {408, 429, 500, 502, 503, 504}
                        and not hard_quota
                        and attempt < self.retry_max_attempts
                    )
                    if should_retry:
                        await asyncio.sleep(self._retry_delay(attempt, retry_after_s=retry_after if status == 429 else None))
                        continue
                    raise
                except (httpx.TimeoutException, httpx.RequestError):
                    if attempt < self.retry_max_attempts:
                        await asyncio.sleep(self._retry_delay(attempt))
                        continue
                    raise
