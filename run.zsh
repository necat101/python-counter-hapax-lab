#!/usr/bin/env zsh
# python-counter-hapax-lab runner – zsh
set -euo pipefail
cd "${0:a:h}"

# Find a python interpreter
if (( $+commands[python3] )); then
    PY=python3
elif (( $+commands[python] )); then
    PY=python
else
    print -u2 "error: python not found in PATH"
    exit 1
fi

print "=== python-counter-hapax-lab ==="
print "python: $($PY --version)"
print

print "--- run_lab.py ---"
"$PY" run_lab.py
RUNNER_EXIT=$?

print
print "--- unittest ---"
"$PY" -m unittest tests.test_hapax -v
UNITTEST_EXIT=$?

print
if (( RUNNER_EXIT == 0 && UNITTEST_EXIT == 0 )); then
    print "all checks passed ✓"
    exit 0
else
    print -u2 "FAILED (run_lab exit=$RUNNER_EXIT, unittest exit=$UNITTEST_EXIT)"
    exit 1
fi
