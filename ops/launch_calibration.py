"""
ops/launch_calibration.py — Sigrid Launch Calibrator
=====================================================

Run before starting the skill to validate the environment, check service
reachability, dry-run all 18 module initialisations, pre-seed the oracle
and Wyrd Matrix, and write a calibrated runtime config to
``session/calibrated_config.json``.

Usage:
    python ops/launch_calibration.py [--strict] [--quiet] [--config .env]

    --strict   Exit 1 if any WARNING-level check fails (default: only on ERROR)
    --quiet    Suppress passing check lines; show only warnings and errors
    --config   Path to .env file (default: ./.env)

Exit codes:
    0  All checks passed (or only warnings with --strict not set)
    1  One or more ERROR-level checks failed
    2  --strict and one or more WARNING-level checks failed

Norse framing: Before the völva speaks, Huginn and Muninn fly the nine worlds
to confirm all is in order. This script is their flight — every thread
checked, every knot confirmed, before Sigrid's voice rises.
"""

from __future__ import annotations

import argparse
import importlib
import json
import logging
import os
import platform
import sys
import time
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ─── Path bootstrap ───────────────────────────────────────────────────────────

_OPS_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _OPS_DIR.parent
_SKILL_ROOT = _PROJECT_ROOT / "viking_girlfriend_skill"

sys.path.insert(0, str(_SKILL_ROOT))

# ─── Result types ─────────────────────────────────────────────────────────────

STATUS_OK = "OK"
STATUS_WARN = "WARN"
STATUS_ERROR = "ERROR"
STATUS_SKIP = "SKIP"


@dataclass
class CheckResult:
    name: str
    status: str       # OK | WARN | ERROR | SKIP
    message: str
    detail: str = ""


# ─── LaunchCalibrator ─────────────────────────────────────────────────────────


class LaunchCalibrator:
    """Validates the environment and calibrates defaults before skill launch."""

    _MIN_PYTHON = (3, 10)

    _REQUIRED_PACKAGES = [
        "numpy", "apscheduler", "psutil", "requests",
        "yaml",    # pyyaml
        "litellm",
    ]
    _OPTIONAL_PACKAGES = [
        ("chromadb",           "semantic memory (T3 ChromaDB layer)"),
        ("sentence_transformers", "semantic memory (embedding model)"),
        ("ollama",             "Ollama Python client (optional)"),
        ("pypdf",              "PDF knowledge loading"),
    ]

    _REQUIRED_ENV_VARS = [
        ("PRIMARY_MODEL_NAME",  "Primary cloud model name"),
        ("PRIMARY_API_KEY",     "Primary cloud API key"),
        ("SECONDARY_MODEL_NAME","Secondary cloud model name"),
        ("SECONDARY_API_KEY",   "Secondary cloud API key"),
        ("CODE_MODEL_NAME",     "Code-specialist model name"),
        ("CODE_API_KEY",        "Code model API key"),
    ]
    _OPTIONAL_ENV_VARS = [
        ("LITELLM_ENDPOINT",   "http://localhost:4000"),
        ("OLLAMA_ENDPOINT",    "http://localhost:11434"),
        ("OLLAMA_MODEL",       "llama3"),
        ("SIGRID_LOG_LEVEL",   "INFO"),
        ("SIGRID_MODE",        "openclaw"),
        ("SIGRID_BIRTH_DATE",  "2004-08-12"),
        ("SIGRID_CYCLE_START_DATE", "2026-03-01"),
    ]

    _REQUIRED_DATA_FILES = [
        "core_identity.md",
        "SOUL.md",
        "values.json",
        "environment.json",
        "AGENTS.md",
    ]

    _SKILL_MODULES = [
        ("scripts.state_bus",          "StateBus"),
        ("scripts.config_loader",      "ConfigLoader"),
        ("scripts.crash_reporting",    "CrashReporter"),
        ("scripts.comprehensive_logging", "InteractionLog"),
        ("scripts.runtime_kernel",     "RuntimeKernel"),
        ("scripts.security",           "SecurityLayer"),
        ("scripts.wyrd_matrix",        "WyrdMatrix"),
        ("scripts.bio_engine",         "BioEngine"),
        ("scripts.oracle",             "Oracle"),
        ("scripts.metabolism",         "MetabolismAdapter"),
        ("scripts.trust_engine",       "TrustEngine"),
        ("scripts.ethics",             "EthicsEngine"),
        ("scripts.memory_store",       "MemoryStore"),
        ("scripts.dream_engine",       "DreamEngine"),
        ("scripts.scheduler",          "SchedulerService"),
        ("scripts.project_generator",  "ProjectGenerator"),
        ("scripts.environment_mapper", "EnvironmentMapper"),
        ("scripts.prompt_synthesizer", "PromptSynthesizer"),
        ("scripts.model_router_client","ModelRouterClient"),
        ("scripts.main",               "(main entry)"),
    ]

    def __init__(
        self,
        env_file: str = ".env",
        strict: bool = False,
        quiet: bool = False,
    ) -> None:
        self._env_file = Path(env_file)
        self._strict = strict
        self._quiet = quiet
        self._results: List[CheckResult] = []
        self._env: Dict[str, str] = {}
        self._calibrated: Dict[str, Any] = {}

    # ── Public ────────────────────────────────────────────────────────────────

    def run_all(self) -> bool:
        """Run all checks in order. Returns True if launch should proceed."""
        self._print_banner()

        self._load_dotenv()
        self._check_python_version()
        self._check_packages()
        self._check_env_vars()
        self._check_data_files()
        self._check_service_health()
        self._check_module_imports()
        self._check_module_init()
        self._calibrate_seeds()
        self._write_calibrated_config()

        return self._print_report()

    # ── Checks ────────────────────────────────────────────────────────────────

    def _load_dotenv(self) -> None:
        """Load .env file if present — sets os.environ for subsequent checks."""
        if self._env_file.exists():
            try:
                with open(self._env_file, encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#") or "=" not in line:
                            continue
                        key, _, value = line.partition("=")
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if key and key not in os.environ:
                            os.environ[key] = value
                            self._env[key] = value
                self._record(STATUS_OK, ".env loaded",
                             f"Loaded {len(self._env)} variable(s) from {self._env_file}")
            except Exception as exc:
                self._record(STATUS_WARN, ".env parse error", str(exc))
        else:
            self._record(STATUS_WARN, ".env not found",
                         f"Expected at {self._env_file.resolve()} — "
                         f"copy .env.example and fill in API keys")

    def _check_python_version(self) -> None:
        v = sys.version_info
        required = self._MIN_PYTHON
        if (v.major, v.minor) >= required:
            self._record(STATUS_OK, "Python version",
                         f"{v.major}.{v.minor}.{v.micro} (>= {required[0]}.{required[1]} required)")
        else:
            self._record(STATUS_ERROR, "Python version",
                         f"{v.major}.{v.minor} — need {required[0]}.{required[1]}+")

    def _check_packages(self) -> None:
        for pkg in self._REQUIRED_PACKAGES:
            try:
                importlib.import_module(pkg)
                self._record(STATUS_OK, f"package:{pkg}", f"{pkg} importable")
            except ImportError:
                install_name = "PyYAML" if pkg == "yaml" else pkg
                self._record(STATUS_ERROR, f"package:{pkg}",
                             f"Missing — run: pip install {install_name}")

        for pkg, purpose in self._OPTIONAL_PACKAGES:
            try:
                importlib.import_module(pkg)
                self._record(STATUS_OK, f"package:{pkg} (optional)", f"{pkg} available")
            except ImportError:
                self._record(STATUS_WARN, f"package:{pkg} (optional)",
                             f"Not installed — needed for {purpose}")

    def _check_env_vars(self) -> None:
        for var, description in self._REQUIRED_ENV_VARS:
            val = os.environ.get(var, "")
            if val and not val.startswith("your_"):
                self._record(STATUS_OK, f"env:{var}", f"{description} — set")
            elif val.startswith("your_"):
                self._record(STATUS_ERROR, f"env:{var}",
                             f"{description} — placeholder not replaced in .env")
            else:
                self._record(STATUS_ERROR, f"env:{var}",
                             f"{description} — not set. Add to .env")

        for var, default in self._OPTIONAL_ENV_VARS:
            val = os.environ.get(var, default)
            self._record(STATUS_OK, f"env:{var} (optional)", f"= {val!r}")

    def _check_data_files(self) -> None:
        data_dir = _SKILL_ROOT / "data"
        for filename in self._REQUIRED_DATA_FILES:
            path = data_dir / filename
            if path.exists() and path.stat().st_size > 0:
                self._record(STATUS_OK, f"data:{filename}",
                             f"{path.stat().st_size} bytes")
            elif path.exists():
                self._record(STATUS_WARN, f"data:{filename}", "File exists but is empty")
            else:
                self._record(STATUS_ERROR, f"data:{filename}",
                             f"Missing — expected at {path}")

    def _check_service_health(self) -> None:
        """Ping LiteLLM and Ollama. Failures are WARN, not ERROR (services may start later)."""
        import socket
        litellm_ep = os.environ.get("LITELLM_ENDPOINT", "http://localhost:4000")
        ollama_ep = os.environ.get("OLLAMA_ENDPOINT", "http://localhost:11434")

        for name, endpoint in [("LiteLLM proxy", litellm_ep), ("Ollama", ollama_ep)]:
            host, port = self._parse_host_port(endpoint)
            if host and port:
                try:
                    s = socket.create_connection((host, port), timeout=2)
                    s.close()
                    self._record(STATUS_OK, f"service:{name}", f"Reachable at {endpoint}")
                except (OSError, ConnectionRefusedError):
                    self._record(STATUS_WARN, f"service:{name}",
                                 f"Not reachable at {endpoint} — "
                                 f"start before using cloud/local tiers")
            else:
                self._record(STATUS_WARN, f"service:{name}",
                             f"Could not parse endpoint: {endpoint!r}")

    def _check_module_imports(self) -> None:
        """Verify all 20 skill scripts import without error."""
        for mod_name, cls_name in self._SKILL_MODULES:
            try:
                importlib.import_module(mod_name)
                self._record(STATUS_OK, f"import:{mod_name}", f"{cls_name} importable")
            except ImportError as exc:
                self._record(STATUS_ERROR, f"import:{mod_name}",
                             f"ImportError: {exc}")
            except Exception as exc:
                self._record(STATUS_WARN, f"import:{mod_name}",
                             f"Unexpected error: {exc}")

    def _check_module_init(self) -> None:
        """Dry-run init of key modules with calibrated config."""
        data_root = str(_SKILL_ROOT / "data")
        cfg: Dict[str, Any] = {
            "ethics": {"data_root": data_root},
            "memory_store": {
                "data_root": data_root,
                "semantic_enabled": False,
            },
            "environment_mapper": {"data_root": data_root},
            "prompt_synthesizer": {"data_root": data_root},
            "bio": {
                "birth_date": os.environ.get("SIGRID_BIRTH_DATE", "2004-08-12"),
                "cycle_start_date": os.environ.get("SIGRID_CYCLE_START_DATE", "2026-03-01"),
            },
            "oracle": {"session_seed": "calibration"},
            "model_router": {
                "litellm_base_url": os.environ.get("LITELLM_ENDPOINT", "http://localhost:4000"),
                "ollama_base_url": os.environ.get("OLLAMA_ENDPOINT", "http://localhost:11434"),
                "ollama_model": os.environ.get("OLLAMA_MODEL", "llama3"),
            },
            "scheduler": {"timezone": "local"},
            "project_generator": {"data_root": data_root},
        }
        self._calibrated["base_config"] = cfg

        # Key modules to init-check
        init_checks: List[Tuple[str, str]] = [
            ("scripts.security",          "init_security_from_config"),
            ("scripts.ethics",            "init_ethics_from_config"),
            ("scripts.trust_engine",      "init_trust_engine_from_config"),
            ("scripts.memory_store",      "init_memory_store_from_config"),
            ("scripts.dream_engine",      "init_dream_engine_from_config"),
            ("scripts.scheduler",         "init_scheduler_from_config"),
            ("scripts.environment_mapper","init_environment_mapper_from_config"),
            ("scripts.prompt_synthesizer","init_prompt_synthesizer_from_config"),
            ("scripts.model_router_client","init_model_router_from_config"),
        ]

        for mod_name, fn_name in init_checks:
            try:
                mod = importlib.import_module(mod_name)
                fn = getattr(mod, fn_name, None)
                if fn is None:
                    self._record(STATUS_WARN, f"init:{mod_name}",
                                 f"{fn_name} not found — skipped")
                    continue
                fn(cfg)
                self._record(STATUS_OK, f"init:{mod_name}", f"{fn_name}() succeeded")
            except Exception as exc:
                self._record(STATUS_WARN, f"init:{mod_name}", f"{fn_name}() raised: {exc}")

    def _calibrate_seeds(self) -> None:
        """Pre-seed oracle and Wyrd Matrix with today's values."""
        try:
            from scripts.oracle import Oracle
            oracle = Oracle(session_seed="sigrid")
            today = datetime.now(timezone.utc).date()
            state = oracle.get_daily_oracle(reference_date=today)
            self._calibrated["oracle_seed"] = {
                "date": today.isoformat(),
                "rune": state.rune_name,
                "rune_symbol": state.rune_symbol,
                "tarot": state.tarot_name,
                "hexagram": state.iching_number,
                "world_tone": state.world_tone,
                "world_desire": state.world_desire,
                "world_focus": state.world_focus,
            }
            # Use ASCII-safe rune symbol for Windows console compatibility
            rune_display = state.rune_symbol.encode("ascii", "replace").decode("ascii")
            self._record(STATUS_OK, "oracle seed",
                         f"Rune={rune_display} {state.rune_name} | "
                         f"Tarot={state.tarot_name} | "
                         f"I Ching={state.iching_number} | "
                         f"Tone={state.world_tone}")
        except Exception as exc:
            self._record(STATUS_WARN, "oracle seed", f"Failed: {exc}")

        try:
            from scripts.wyrd_matrix import WyrdMatrix
            wm = WyrdMatrix()
            wm_state = wm.get_state()
            self._calibrated["wyrd_baseline"] = {
                "pad_pleasure": wm_state.pad_pleasure,
                "pad_arousal": wm_state.pad_arousal,
                "pad_dominance": wm_state.pad_dominance,
                "hamingja": wm_state.hamingja,
            }
            self._record(STATUS_OK, "wyrd baseline",
                         f"P={wm_state.pad_pleasure:.2f} "
                         f"A={wm_state.pad_arousal:.2f} "
                         f"D={wm_state.pad_dominance:.2f} "
                         f"Hamingja={wm_state.hamingja:.2f}")
        except Exception as exc:
            self._record(STATUS_WARN, "wyrd baseline", f"Failed: {exc}")

        try:
            from scripts.bio_engine import BioEngine
            birth = os.environ.get("SIGRID_BIRTH_DATE", "2004-08-12")
            cycle_start = os.environ.get("SIGRID_CYCLE_START_DATE", "2026-03-01")
            bio = BioEngine(
                birth_date=date.fromisoformat(birth),
                cycle_start_date=date.fromisoformat(cycle_start),
            )
            bio_state = bio.get_state()
            self._calibrated["bio_baseline"] = {
                "phase_name": bio_state.phase_name,
                "cycle_day": bio_state.cycle_day,
                "biorhythm_physical": round(bio_state.biorhythm_physical, 3),
            }
            self._record(STATUS_OK, "bio baseline",
                         f"Phase={bio_state.phase_name} "
                         f"Day={bio_state.cycle_day} "
                         f"Physical={bio_state.biorhythm_physical:.2f}")
        except Exception as exc:
            self._record(STATUS_WARN, "bio baseline", f"Failed: {exc}")

        try:
            from scripts.scheduler import SchedulerService
            sched = SchedulerService()
            tod = sched.time_of_day()
            self._calibrated["time_of_day"] = tod
            self._record(STATUS_OK, "time of day", tod)
        except Exception as exc:
            self._record(STATUS_WARN, "time of day", f"Failed: {exc}")

    def _write_calibrated_config(self) -> None:
        """Write session/calibrated_config.json for main.py to consume at startup."""
        session_dir = _PROJECT_ROOT / "session"
        try:
            session_dir.mkdir(parents=True, exist_ok=True)
            out_path = session_dir / "calibrated_config.json"
            payload = {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "platform": platform.system(),
                "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "calibration": self._calibrated,
                "env_summary": {
                    "litellm_endpoint": os.environ.get("LITELLM_ENDPOINT", "http://localhost:4000"),
                    "ollama_endpoint": os.environ.get("OLLAMA_ENDPOINT", "http://localhost:11434"),
                    "ollama_model": os.environ.get("OLLAMA_MODEL", "llama3"),
                    "skill_mode": os.environ.get("SIGRID_MODE", "openclaw"),
                    "log_level": os.environ.get("SIGRID_LOG_LEVEL", "INFO"),
                    "primary_contact": os.environ.get("SIGRID_PRIMARY_CONTACT", "volmarr"),
                },
            }
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            self._record(STATUS_OK, "calibrated config written",
                         f"session/calibrated_config.json ({out_path.stat().st_size} bytes)")
        except Exception as exc:
            self._record(STATUS_WARN, "calibrated config",
                         f"Could not write session/calibrated_config.json: {exc}")

    # ── Report ────────────────────────────────────────────────────────────────

    def _print_banner(self) -> None:
        width = 70
        print("=" * width)
        print("  Sigrid Skill — Launch Calibrator".center(width))
        print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".center(width))
        print("  Project root: " + str(_PROJECT_ROOT))
        print("=" * width)
        print()

    def _print_report(self) -> bool:
        """Print summary and return True if launch should proceed."""
        ok = sum(1 for r in self._results if r.status == STATUS_OK)
        warn = sum(1 for r in self._results if r.status == STATUS_WARN)
        error = sum(1 for r in self._results if r.status == STATUS_ERROR)
        skip = sum(1 for r in self._results if r.status == STATUS_SKIP)

        if not self._quiet:
            print()
        print("-" * 70)
        print(f"  Checks: {ok} OK  |  {warn} WARN  |  {error} ERROR  |  {skip} SKIP")
        print("-" * 70)

        if error > 0:
            print()
            print("  LAUNCH BLOCKED -- fix the ERROR items above before starting.")
            print()
            for r in self._results:
                if r.status == STATUS_ERROR:
                    print(f"    [ERROR] {r.name}: {r.message}")
            print()
            return False

        if warn > 0 and self._strict:
            print()
            print("  LAUNCH BLOCKED (--strict) -- resolve WARN items or remove --strict.")
            print()
            return False

        if warn > 0:
            print()
            print("  LAUNCH ALLOWED -- warnings present. Some features may be degraded:")
            for r in self._results:
                if r.status == STATUS_WARN:
                    print(f"    [WARN] {r.name}: {r.message}")
            print()
        else:
            print()
            print("  ALL CHECKS PASSED -- Sigrid is ready to launch.")
            print()

        print("  To start:")
        mode = os.environ.get("SIGRID_MODE", "openclaw")
        if platform.system() == "Windows":
            print("    ops\\start_skill.bat")
        else:
            print("    ./ops/start_skill.sh")
        print(f"    (mode: {mode})")
        print()
        print("=" * 70)
        return True

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _record(self, status: str, name: str, message: str, detail: str = "") -> None:
        r = CheckResult(name=name, status=status, message=message, detail=detail)
        self._results.append(r)
        if self._quiet and status == STATUS_OK:
            return
        prefix = {
            STATUS_OK:    "  [OK  ]",
            STATUS_WARN:  "  [WARN]",
            STATUS_ERROR: "  [ERR ]",
            STATUS_SKIP:  "  [SKIP]",
        }.get(status, "  [    ]")
        line = f"{prefix} {name}: {message}"
        # Safe print — replace un-encodable chars for Windows cp1252 consoles
        try:
            print(line)
        except UnicodeEncodeError:
            print(line.encode(sys.stdout.encoding or "ascii", "replace").decode(
                sys.stdout.encoding or "ascii"))

    @staticmethod
    def _parse_host_port(endpoint: str) -> Tuple[Optional[str], Optional[int]]:
        """Parse 'http://host:port' into (host, port) tuple."""
        try:
            stripped = endpoint.replace("http://", "").replace("https://", "")
            host, _, port_str = stripped.partition(":")
            port = int(port_str.split("/")[0]) if port_str else 80
            return host or None, port
        except (ValueError, AttributeError):
            return None, None


# ─── Entry point ──────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sigrid Skill — Launch Calibrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--strict", action="store_true",
        help="Exit 2 if any WARNING-level check fails",
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Suppress passing check lines; show only warnings and errors",
    )
    parser.add_argument(
        "--config", default=str(_PROJECT_ROOT / ".env"),
        help="Path to .env file (default: ./.env)",
    )
    args = parser.parse_args()

    calibrator = LaunchCalibrator(
        env_file=args.config,
        strict=args.strict,
        quiet=args.quiet,
    )
    ok = calibrator.run_all()

    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
