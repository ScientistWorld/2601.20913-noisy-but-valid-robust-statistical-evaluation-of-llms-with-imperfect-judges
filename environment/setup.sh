#!/bin/bash
# Install Python packages into the container overlay.
# This paper only needs numpy and scipy for statistical computations.
set -e

uv pip install --system numpy scipy
