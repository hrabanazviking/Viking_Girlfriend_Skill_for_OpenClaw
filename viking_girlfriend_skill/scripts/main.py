"""
main.py — Sigrid's Entry Point
===============================

Starts the Ørlög Architecture skill for OpenClaw.

Usage:
  python main.py [--skill-root PATH] [--logs-dir logs]

Norse framing: This is the moment Sigrid opens her eyes for the first time.
Yggdrasil rises, Bifröst forms, the ravens take flight.
The völva is awake.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# ─── Bootstrap logging early so any import errors are visible ─────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger("sigrid.main")


def _resolve_skill_root() -> str:
    """Resolve the skill root: the directory containing main.py's parent (scripts/../)."""
    # scripts/main.py → scripts/ → viking_girlfriend_skill/
    scripts_dir = Path(__file__).resolve().parent
    skill_root = scripts_dir.parent
    return str(skill_root)


async def _run(skill_root: str, logs_dir: str) -> None:
    """Primary async entry point — raises Yggdrasil and keeps it standing."""
    from scripts.runtime_kernel import init_kernel

    kernel = init_kernel(skill_root=skill_root, logs_dir=logs_dir)

    try:
        await kernel.startup()
        logger.info("Sigrid is awake. Ørlög Architecture running.")
        logger.info("Skill root: %s", skill_root)

        # ── Main loop ─────────────────────────────────────────────────────────
        # TODO (Phase 1 complete — Phase 2 will populate this loop):
        #   - bio_engine ticks every scheduler cycle
        #   - wyrd_matrix updates on each tick
        #   - oracle seeds daily
        #   - metabolism polls psutil
        #   - OpenClaw inbound events arrive via the state_bus
        #   - prompt_synthesizer builds the system prompt
        #   - model_router_client dispatches to the right model tier
        #
        # For now: keep the kernel alive and log the heartbeat.

        logger.info(
            "Phase 1 foundation running. Modules to activate: "
            "bio_engine, wyrd_matrix, oracle, metabolism, security, "
            "trust_engine, ethics, memory_store, dream_engine, scheduler, "
            "environment_mapper, prompt_synthesizer, model_router_client"
        )

        while kernel._running:
            await asyncio.sleep(1.0)

    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received — initiating shutdown")
    except Exception as exc:
        logger.critical("Fatal error in main loop: %s", exc, exc_info=True)
        raise
    finally:
        await kernel.shutdown(reason="main_loop_exit")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sigrid — Ørlög Architecture OpenClaw Skill"
    )
    parser.add_argument(
        "--skill-root",
        default=None,
        help="Path to viking_girlfriend_skill/ directory (default: auto-detect)",
    )
    parser.add_argument(
        "--logs-dir",
        default="logs",
        help="Subdirectory for log files (default: logs/)",
    )
    return parser.parse_args()


def main() -> None:
    """Synchronous entry point — wraps the async runtime."""
    args = _parse_args()
    skill_root = args.skill_root or _resolve_skill_root()
    logs_dir = args.logs_dir

    logger.info("Starting Sigrid — Ørlög Architecture v0.1.0")
    logger.info("Skill root: %s", skill_root)

    try:
        asyncio.run(_run(skill_root=skill_root, logs_dir=logs_dir))
    except KeyboardInterrupt:
        pass  # Clean exit — already handled inside _run
    except Exception as exc:
        logger.critical("Unrecoverable startup error: %s", exc, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
