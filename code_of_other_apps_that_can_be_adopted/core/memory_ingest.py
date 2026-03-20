from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from html import unescape
from pathlib import Path
from typing import Any, Iterable


def metadata_hint(metadata: dict[str, Any] | None) -> str:
    if not isinstance(metadata, dict):
        return ""
    for key in ("transcript", "caption", "description", "summary"):
        value = str(metadata.get(key, "") or "").strip()
        if value:
            return value[:600]
    return ""


def compact_whitespace(value: str) -> str:
    return " ".join(str(value or "").split())


def try_ocr_image_text(target: Path) -> str:
    try:
        from PIL import Image  # type: ignore
        import pytesseract  # type: ignore
    except Exception:
        return ""
    try:
        with Image.open(target) as image:
            extracted = pytesseract.image_to_string(image)
    except Exception:
        return ""
    return compact_whitespace(extracted)


def try_transcribe_audio_text(target: Path) -> str:
    try:
        import whisper  # type: ignore

        model = whisper.load_model("base")
        result = model.transcribe(str(target))
        if isinstance(result, dict):
            return compact_whitespace(str(result.get("text", "") or ""))
    except Exception:
        pass
    try:
        from faster_whisper import WhisperModel  # type: ignore

        model = WhisperModel("base", device="cpu", compute_type="int8")
        segments, _ = model.transcribe(str(target))
        joined = " ".join(str(getattr(seg, "text", "") or "") for seg in segments)
        return compact_whitespace(joined)
    except Exception:
        return ""


def memory_text_from_file(
    file_path: str,
    *,
    modality: str,
    metadata: dict[str, Any] | None,
    text_like_suffixes: Iterable[str],
) -> str:
    target = Path(file_path).expanduser()
    suffix = target.suffix.lower()
    hint = metadata_hint(metadata)
    if suffix in set(text_like_suffixes):
        try:
            content = target.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            content = ""
        excerpt = compact_whitespace(content)[:4000].strip()
        if excerpt:
            return excerpt

    image_suffixes = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".tif", ".tiff"}
    audio_suffixes = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac"}
    modality_clean = str(modality or "").strip().lower()

    if suffix in image_suffixes or modality_clean == "image":
        ocr_text = try_ocr_image_text(target)
        if ocr_text:
            return ocr_text[:4000]

    if suffix in audio_suffixes or modality_clean == "audio":
        transcript = try_transcribe_audio_text(target)
        if transcript:
            return transcript[:4000]

    synthetic = [f"Ingested {modality} file reference: {target.name} ({target})."]
    if modality_clean == "image":
        synthetic.append("OCR hook unavailable; stored as reference.")
    if modality_clean == "audio":
        synthetic.append("Transcription hook unavailable; stored as reference.")
    if hint:
        synthetic.append(f"Supplemental metadata: {hint}")
    return compact_whitespace(" ".join(synthetic))[:4000]


def memory_text_from_url(
    url: str,
    *,
    modality: str,
    metadata: dict[str, Any] | None,
) -> str:
    raw_url = str(url or "").strip()
    hint = metadata_hint(metadata)
    if not raw_url:
        parts = [f"Ingested {modality} URL reference: {raw_url}."]
        if hint:
            parts.append(f"Supplemental metadata: {hint}")
        return compact_whitespace(" ".join(parts))[:4000]

    try:
        request = urllib.request.Request(raw_url, headers={"User-Agent": "ClawLiteMemory/1.0"})
        with urllib.request.urlopen(request, timeout=6.0) as response:
            payload = response.read(200_000)
            headers = getattr(response, "headers", None)

        content_type = ""
        charset = "utf-8"
        if headers is not None:
            try:
                content_type = str(headers.get_content_type() or "").strip().lower()
            except Exception:
                content_type = ""
            try:
                charset = str(headers.get_content_charset() or "utf-8").strip() or "utf-8"
            except Exception:
                charset = "utf-8"
            if not content_type:
                try:
                    content_type = str(headers.get("Content-Type", "") or "").split(";", 1)[0].strip().lower()
                except Exception:
                    content_type = ""

        decoded = payload.decode(charset, errors="ignore")
        extracted = ""
        if "json" in content_type:
            try:
                parsed = json.loads(decoded)
                if isinstance(parsed, (dict, list)):
                    extracted = json.dumps(parsed, ensure_ascii=False)
                else:
                    extracted = str(parsed)
            except Exception:
                extracted = decoded
        elif "html" in content_type:
            without_scripts = re.sub(r"(?is)<script[^>]*>.*?</script>", " ", decoded)
            without_styles = re.sub(r"(?is)<style[^>]*>.*?</style>", " ", without_scripts)
            no_tags = re.sub(r"(?s)<[^>]+>", " ", without_styles)
            extracted = unescape(no_tags)
        elif content_type.startswith("text/") or not content_type:
            extracted = decoded

        compact = compact_whitespace(extracted)[:4000]
        if compact:
            return compact
    except (urllib.error.URLError, TimeoutError, ValueError):
        pass
    except Exception:
        pass

    parts = [f"Ingested {modality} URL reference: {raw_url}."]
    if hint:
        parts.append(f"Supplemental metadata: {hint}")
    return compact_whitespace(" ".join(parts))[:4000]


__all__ = [
    "compact_whitespace",
    "memory_text_from_file",
    "memory_text_from_url",
    "metadata_hint",
    "try_ocr_image_text",
    "try_transcribe_audio_text",
]
