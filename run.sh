#!/usr/bin/env bash
# python-counter-hapax-lab runner – Linux / macOS
set -euo pipefail
cd "$(dirname "$0")"

# Find a python interpreter
if command -v python3 >/dev/null 2>&1; then
    PY=python3
elif command -v python >/dev/null 2>&1; then
    PY=python
else
    echo "error: python not found in PATH" >&2
    exit 1
fi

echo "=== python-counter-hapax-lab ==="
echo "python: $($PY --version)"
echo

echo "--- run_lab.py ---"
"$PY" run_lab.py
RUNNER_EXIT=$?

echo
echo "--- unittest ---"
"$PY" -m unittest tests.test_hapax -v
UNITTEST_EXIT=$?

echo
if [ $RUNNER_EXIT -eq 0 ] && [ $UNITTEST_EXIT -eq 0 ]; then
    echo "all checks passed ✓"
    exit 0
else
    echo "FAILED (run_lab exit=$RUNNER_EXIT, unittest exit=$UNITTEST_EXIT)" >&2
    exit 1
fi
