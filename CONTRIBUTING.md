# Contributing to TestRail CLI

Thank you for your interest in contributing to TestRail CLI! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md) to ensure a welcoming environment for all contributors.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Poetry (for dependency management)
- Git

### Development Setup

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/testrail-cli.git
   cd testrail-cli
   ```

3. Install Poetry if you haven't already:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

4. Install dependencies:
   ```bash
   poetry install
   ```

5. Set up pre-commit hooks:
   ```bash
   make pre-commit
   # or
   poetry run pre-commit install
   ```

## Development Workflow

### Running Tests

Run the full test suite:
```bash
make test
# or
poetry run pytest
```

Run tests with coverage:
```bash
poetry run pytest --cov --cov-report=html
```

### Code Quality

Format code:
```bash
make format
# or
poetry run ruff format .
```

Run linter:
```bash
make lint
# or
poetry run ruff check .
```

Run type checker:
```bash
make type-check
# or
poetry run mypy testrail_cli
```

### Running the CLI

Run the CLI in development mode:
```bash
poetry run testrail --help
```

## Making Changes

### Branch Naming

Use descriptive branch names:
- `feature/add-new-command` - New features
- `fix/bug-description` - Bug fixes
- `docs/update-readme` - Documentation updates
- `refactor/improve-code` - Code refactoring

### Commit Messages

Write clear, descriptive commit messages:
- Use the imperative mood ("Add feature" not "Added feature")
- Keep the first line under 50 characters
- Add a blank line before the body
- Explain what and why, not how

Example:
```
Add support for custom fields in test cases

This commit adds the ability to set custom fields when creating
or updating test cases through the CLI.

Fixes #123
```

### Writing Tests

- Write tests for all new features and bug fixes
- Aim for at least 80% code coverage
- Place unit tests in `tests/unit/`
- Place integration tests in `tests/integration/`
- Use descriptive test names that explain what is being tested

### Type Hints

- Add type hints to all function signatures
- Use `from typing import` for complex types
- Run `mypy` to check for type errors

### Documentation

- Update relevant documentation when making changes
- Add docstrings to all public functions and classes
- Update the README if adding new features
- Add examples for new functionality

## Pull Request Process

1. **Create a Pull Request**
   - Push your changes to your fork
   - Create a pull request against the `main` branch
   - Fill out the PR template with all relevant information

2. **PR Requirements**
   - All tests must pass
   - Code must pass linting and type checking
   - Code coverage should not decrease
   - Documentation must be updated

3. **Review Process**
   - Maintainers will review your PR
   - Address any feedback or requested changes
   - Once approved, a maintainer will merge your PR

4. **After Merge**
   - Delete your feature branch
   - Pull the latest changes from main

## Reporting Bugs

Use the GitHub issue tracker to report bugs:

1. Check if the bug has already been reported
2. If not, create a new issue using the bug report template
3. Include:
   - Clear description of the bug
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)
   - Relevant logs or error messages

## Suggesting Features

We welcome feature suggestions:

1. Check if the feature has already been suggested
2. Create a new issue using the feature request template
3. Describe:
   - The problem the feature would solve
   - How you envision the feature working
   - Any alternative solutions you've considered

## Development Tips

### Useful Commands

```bash
# Run specific test file
poetry run pytest tests/unit/test_config.py

# Run tests matching a pattern
poetry run pytest -k "test_config"

# Run tests with verbose output
poetry run pytest -v

# Watch for changes and re-run tests
poetry run pytest-watch

# Generate coverage report
poetry run pytest --cov --cov-report=html
open htmlcov/index.html
```

### Project Structure

```
testrail-cli/
├── testrail_cli/          # Main package
│   ├── commands/          # CLI command modules
│   ├── __main__.py       # CLI entry point
│   ├── client.py         # TestRail API client
│   ├── config.py         # Configuration management
│   └── io.py             # Output formatting
├── tests/                # Test suite
│   ├── unit/            # Unit tests
│   ├── integration/     # Integration tests
│   └── fixtures/        # Test data
├── docs/                # Documentation
└── examples/            # Example files
```

### Common Issues

**Poetry lock file conflicts:**
```bash
poetry lock --no-update
```

**Pre-commit hooks failing:**
```bash
poetry run pre-commit run --all-files
```

**Type checking errors:**
```bash
poetry run mypy testrail_cli --show-error-codes
```

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.

## Questions?

If you have questions or need help:
- Open a GitHub Discussion
- Comment on a relevant issue
- Reach out to the maintainers

Thank you for contributing to TestRail CLI!
