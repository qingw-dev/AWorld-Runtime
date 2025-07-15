# AWorld-Runtime
Scaling Agent Training via Runtime Definitions and Parallelizations

## Code Quality

This project uses [ruff](https://github.com/astral-sh/ruff) for linting and formatting.

### Quick Commands

```bash
# Check code quality
uv run ruff check .

# Fix auto-fixable issues
uv run ruff check . --fix

# Format code
uv run ruff format .

# Run all checks
uv run ruff check . && uv run ruff format --check .