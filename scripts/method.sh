#!/bin/bash
# The method is a statistical certification procedure; it needs no training.
# Certifiers live in method/certifiers/<name>.py and are executed by the
# evaluators on instances the evaluators generate. This script runs every
# certifier on the public train-slice instances.
#
# Usage:
#   bash scripts/method.sh

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
bash "${ROOT}/scripts/evaluate_train.sh"
