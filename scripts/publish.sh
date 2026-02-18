#!/usr/bin/env bash
# Publish notebooklm-wrapper to PyPI.
# Requires: hatch, and PyPI credentials (hatch config or env vars).
# Usage: ./scripts/publish.sh [--test]
#   --test  Publish to TestPyPI instead of PyPI

set -e

cd "$(dirname "$0")/.."

if [[ -d .venv ]]; then
  echo "Activating .venv..."
  source .venv/bin/activate
fi

echo "Installing/updating dev dependencies..."
pip install -e ".[dev]" -q

echo "Running tests..."
pytest -q

echo "Building package..."
hatch build

if [[ "$1" == "--test" ]]; then
  echo "Publishing to TestPyPI..."
  hatch publish -r testpypi
else
  echo "Publishing to PyPI..."
  hatch publish
fi

echo "Done."
