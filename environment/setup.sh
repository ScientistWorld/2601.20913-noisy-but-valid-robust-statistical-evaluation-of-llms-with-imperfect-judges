#!/bin/bash
# Install Python packages into the container overlay.
#
# This script runs inside the container with internet access.
# Use uv pip install --system for speed.

set -e

# Core scientific computing packages
uv pip install --system \
    numpy \
    scipy \
    scikit-learn \
    pandas \
    matplotlib \
    seaborn
