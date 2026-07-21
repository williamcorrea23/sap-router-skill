#!/bin/bash
set -e

echo "Running tests..."

# Run with coverage
uv run pytest tests/ \
    --cov=app \
    --cov-report=term-missing \
    --cov-report=html:coverage_html \
    -v \
    "$@"

echo ""
echo "Coverage report generated in coverage_html/"