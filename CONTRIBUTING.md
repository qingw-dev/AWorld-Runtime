# Contributing Guidelines

## Code Quality Standards

This project enforces strict code quality standards using ruff for both linting and formatting.

### Before Committing

1. **Install pre-commit hooks** (recommended):
   ```bash
   uv add --dev pre-commit
   uv run pre-commit install

2. **Manual checks**:
    ```bash
    # Check linting
    uv run ruff check .

    # Fix auto-fixable issues
    uv run ruff check . --fix

    # Check formatting
    uv run ruff format --check .

    # Format code
    uv run ruff format .
    ```

### Development Setup
1. Clone the repository
2. Install dependencies: `uv sync --all-extras`
3. Install pre-commit hooks: `uv run pre-commit install`
4. Make your changes
5. Run tests: `uv run pytest`
6. Commit and push

### CI/CD
All pull requests must pass:

- Ruff linting checks
- Ruff formatting checks
- All tests
The CI will automatically run these checks on every push and pull request.