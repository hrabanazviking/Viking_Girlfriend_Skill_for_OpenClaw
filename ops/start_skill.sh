#!/usr/bin/env bash
# ops/start_skill.sh — Sigrid Skill Autostart (Linux / macOS)
#
# Usage:
#   ./ops/start_skill.sh                  # openclaw mode (default)
#   ./ops/start_skill.sh --mode terminal  # interactive REPL
#   ./ops/start_skill.sh --skip-calibrate # skip pre-flight checks
#
# Prerequisites:
#   - Python 3.10+ with all dependencies installed (pip install -r requirements.txt)
#   - .env file at project root (copy from .env.example)
#   - LiteLLM proxy running: litellm --config infrastructure/litellm_config.yaml
#   - Ollama running (optional for subconscious tier): ollama serve
#
# This script:
#   1. Sets the working directory to the project root
#   2. Loads .env if present
#   3. Runs launch_calibration.py (pre-flight check)
#   4. Starts main.py in the requested mode

set -euo pipefail

# Resolve project root (one level up from ops/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo ""
echo "======================================================================"
echo "  Sigrid Skill — Autostart"
echo "  $(date '+%Y-%m-%d %H:%M:%S')"
echo "======================================================================"
echo ""

# Load .env if present
if [ -f ".env" ]; then
    set -o allexport
    # shellcheck disable=SC1091
    source ".env" || true
    set +o allexport
    echo "  [.env loaded]"
fi

# Parse arguments
SKIP_CALIBRATE=0
EXTRA_ARGS=()
for arg in "$@"; do
    case "$arg" in
        --skip-calibrate)
            SKIP_CALIBRATE=1
            ;;
        *)
            EXTRA_ARGS+=("$arg")
            ;;
    esac
done

# Step 1 — Pre-flight calibration
if [ "$SKIP_CALIBRATE" -eq 0 ]; then
    echo ""
    echo "  Running launch calibration..."
    echo ""
    python ops/launch_calibration.py --config .env || {
        echo ""
        echo "  Launch calibration failed. Fix errors above or use --skip-calibrate."
        exit 1
    }
fi

# Step 2 — Activate venv if present
if [ -f "venv/bin/activate" ]; then
    echo "  Activating venv..."
    # shellcheck disable=SC1091
    source "venv/bin/activate"
elif [ -f ".venv/bin/activate" ]; then
    echo "  Activating .venv..."
    # shellcheck disable=SC1091
    source ".venv/bin/activate"
fi

# Step 3 — Launch skill
echo ""
echo "  Starting Sigrid skill..."
echo ""

PYTHONPATH="$PROJECT_ROOT/viking_girlfriend_skill:$PYTHONPATH" \
    exec python "viking_girlfriend_skill/scripts/main.py" "${EXTRA_ARGS[@]:-}"
