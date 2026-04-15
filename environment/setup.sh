#!/bin/bash
# Install Python packages into the container overlay.
# This paper only needs numpy and scipy for statistical computations.
set -e

python3 -m pip install --break-system-packages uv
uv pip install --system numpy scipy
