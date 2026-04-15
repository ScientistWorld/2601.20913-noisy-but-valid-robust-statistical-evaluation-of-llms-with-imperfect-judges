#!/bin/bash
# Download all data and models needed for this environment.
#
# This paper uses synthetic data only — no external downloads required.
# All data is generated procedurally by data/synthetic.py.
#
# Estimated total download size: 0 GB
# Estimated disk usage: < 1 MB (generated data)

set -e

cd "$(dirname "$0")/.."

# Ensure data directory exists
mkdir -p data/downloads

echo "No external downloads needed — this paper uses synthetic data only."
