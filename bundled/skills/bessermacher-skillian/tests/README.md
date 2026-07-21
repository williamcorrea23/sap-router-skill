# Skillian Tests

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_api.py

# Run specific test class
uv run pytest tests/test_api.py::TestHealthEndpoint

# Run specific test
uv run pytest tests/test_api.py::TestHealthEndpoint::test_health_check

# Run with verbose output
uv run pytest -v

# Run and stop on first failure
uv run pytest -x