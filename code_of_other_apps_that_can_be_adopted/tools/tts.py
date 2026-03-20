from __future__ import annotations
import tempfile, time
from pathlib import Path
from clawlite.tools.base import Tool, ToolContext

_DEFAULT_VOICE = "en-US-AriaNeural"

class TTSTool(Tool):
    name = "tts"
    description = "Convert text to speech using edge-tts. Returns path to MP3 file. Specify voice (e.g. 'en-US-AriaNeural', 'pt-BR-FranciscaNeural')."

    def __init__(self, *, output_dir: str | None = None, default_voice: str = _DEFAULT_VOICE, rate: str = "+0%") -> None:
        self.output_dir = output_dir
        self.default_voice = str(default_voice or _DEFAULT_VOICE).strip()
        self.rate = str(rate or "+0%").strip()

    def args_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to synthesize."},
                "voice": {"type": "string", "description": f"Voice name. Default: {_DEFAULT_VOICE}", "default": _DEFAULT_VOICE},
                "rate": {"type": "string", "description": "Rate offset e.g. '+10%'. Default: +0%", "default": "+0%"},
            },
            "required": ["text"],
        }

    async def run(self, arguments: dict, ctx: ToolContext) -> str:
        try:
            import edge_tts
        except ImportError:
            return 'error: edge-tts not installed. Run: pip install "clawlite[media]"'
        text = str(arguments.get("text", "") or "").strip()[:5000]
        if not text: return "error: text is required"
        voice = str(arguments.get("voice", self.default_voice) or self.default_voice).strip()
        rate = str(arguments.get("rate", self.rate) or self.rate).strip()
        if self.output_dir:
            Path(self.output_dir).mkdir(parents=True, exist_ok=True)
            out = str(Path(self.output_dir) / f"tts-{int(time.time())}.mp3")
        else:
            out = str(Path(tempfile.mkdtemp(prefix="clawlite-tts-")) / f"tts-{int(time.time())}.mp3")
        try:
            await edge_tts.Communicate(text, voice, rate=rate).save(out)
            return f"tts:{out}"
        except Exception as exc:
            return f"tts_error: {exc}"
