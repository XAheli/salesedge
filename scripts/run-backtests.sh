#!/usr/bin/env bash
# SalesEdge — Backtesting Suite Runner
# Replays historical data through scoring models and reports metrics.
#
# Usage:
#   ./scripts/run-backtests.sh                          # Run all backtests
#   ./scripts/run-backtests.sh --model deal_risk        # Specific model
#   ./scripts/run-backtests.sh --start 2024-01-01 --end 2024-06-30

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/backend"
RESULTS_DIR="$PROJECT_ROOT/backend/tests/backtesting/results"

MODEL=""
START_DATE=""
END_DATE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --model)   MODEL="$2"; shift 2 ;;
        --start)   START_DATE="$2"; shift 2 ;;
        --end)     END_DATE="$2"; shift 2 ;;
        --help|-h) echo "Usage: $0 [--model MODEL] [--start YYYY-MM-DD] [--end YYYY-MM-DD]"; exit 0 ;;
        *)         echo "Unknown option: $1"; exit 1 ;;
    esac
done

mkdir -p "$RESULTS_DIR"

echo "============================================"
echo "  SalesEdge Backtesting Suite"
echo "  $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================"

if [ ! -d "$BACKEND_DIR/.venv" ]; then
    echo "ERROR: Virtual environment not found. Run 'make bootstrap' first."
    exit 1
fi

PYTHON="$BACKEND_DIR/.venv/bin/python"
PYTEST="$BACKEND_DIR/.venv/bin/pytest"

if [ ! -f "$PYTEST" ]; then
    echo "ERROR: pytest not found in venv. Run 'pip install pytest' in backend venv."
    exit 1
fi

PYTEST_ARGS=(
    "$BACKEND_DIR/tests/backtesting/"
    "-v"
    "--tb=short"
    "-m" "slow"
    "--junitxml=$RESULTS_DIR/backtest-results.xml"
)

if [ -n "$MODEL" ]; then
    echo "Running backtests for model: $MODEL"
    PYTEST_ARGS+=("-k" "$MODEL")
else
    echo "Running all backtests..."
fi

if [ -n "$START_DATE" ]; then
    export BACKTEST_START_DATE="$START_DATE"
    echo "Start date: $START_DATE"
fi

if [ -n "$END_DATE" ]; then
    export BACKTEST_END_DATE="$END_DATE"
    echo "End date: $END_DATE"
fi

echo ""

cd "$BACKEND_DIR"
"$PYTEST" "${PYTEST_ARGS[@]}" 2>&1 | tee "$RESULTS_DIR/backtest-log-$(date +%Y%m%d).txt"

EXIT_CODE=${PIPESTATUS[0]}

echo ""
echo "============================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo "  BACKTESTS PASSED"
else
    echo "  BACKTESTS FAILED (exit code: $EXIT_CODE)"
fi
echo "  Results: $RESULTS_DIR/"
echo "============================================"

exit $EXIT_CODE
