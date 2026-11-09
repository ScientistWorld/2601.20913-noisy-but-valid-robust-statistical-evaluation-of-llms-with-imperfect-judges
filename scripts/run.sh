#!/bin/bash
# CPU job: reproduce the reference end to end from the final code (canonical,
# train-slice and hidden-test scores), run the hardening audit (reference,
# better/weaker variants and shortcuts through the hidden test), check that the
# hidden test is byte-for-byte reproducible, and validate the workspace.

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"
status=0

run() {
  local label="$1"
  shift
  echo ""
  echo "=== ${label} ==="
  "$@" || { echo "!!! step failed (rc=$?): ${label}"; status=1; }
}

run "reproduce: canonical, train-slice and hidden-test scores of the reference" \
  bash scripts/reproduce.sh
run "hardening audit (variants and shortcuts through the hidden test)" \
  python3 redteam/hardening/audit.py
run "audit summary" \
  python3 redteam/hardening/summarize.py
run "hidden test re-run reproduces the saved reference scores byte for byte" \
  bash -c 'cp scoring/scores_test.json /tmp/scores_test.saved.json && bash scripts/evaluate_test.sh > /tmp/rerun.log 2>&1 && cmp scoring/scores_test.json /tmp/scores_test.saved.json && echo identical'
run "validate" \
  python3 validate.py --post-design

echo ""
echo "=== job finished (status ${status}) ==="
exit "${status}"
