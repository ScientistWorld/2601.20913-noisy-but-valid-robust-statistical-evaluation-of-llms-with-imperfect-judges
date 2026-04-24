#!/bin/bash
set -euo pipefail

echo "Installing Python dependencies"
uv --version
uv pip install --system --quiet numpy scipy
