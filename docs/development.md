# Development Guide

This guide is for contributors who want to develop and improve TestRail CLI.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Poetry (dependency management)
- Git
- A TestRail instance for testing (optional)

### Initial Setup

1. **Fork and Clone**

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/testrail-cli.git
cd testrail-cli

# Add upstream remote
git remote add upstream https://github.com/mokson/testrail-cli.git
```

2. **Install Poetry**

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. **Install Dependencies**

```bash
poetry install
```

This installs all dependencies including development tools.

4. **Activate Virtual Environment**

```bash
poetry shell
```

5. **Install Pre-commit Hooks**

```bash
poetry run pre-commit install
```

## Project Structure

```
testrail-cli/
├── .github/               # GitHub Actions workflows and templates
│   ├── workflows/         # CI/CD workflows
│   └── ISSUE_TEMPLATE/    # Issue templates
├── docs/                  # Documentation
├── examples/              # Example files
├── scripts/               # Helper scripts
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   ├── fixtures/         # Test data
│   └── conftest.py       # Pytest fixtures
├── testrail_cli/         # Main package
│   ├── commands/         # CLI command modules
│   ├── __init__.py       # Package initialization
│   ├── __main__.py       # CLI entry point
│   ├── client.py         # TestRail API client
│   ├── config.py         # Configuration management
│   ├── csv_import.py     # CSV import logic
│   └── io.py             # Output formatting
├── pyproject.toml        # Project configuration
├── Makefile              # Common development tasks
└── README.md             # Main documentation
```

## Development Workflow

### Making Changes

1. **Create a Feature Branch**

```bash
git checkout -b feature/your-feature-name
```

2. **Make Your Changes**

Edit code, add features, fix bugs.

3. **Write Tests**

Always add tests for new features:

```bash
# Run tests as you develop
poetry run pytest tests/unit/test_your_module.py -v
```

4. **Format and Lint**

```bash
# Format code
poetry run ruff format .

# Check linting
poetry run ruff check .

# Type check
poetry run mypy testrail_cli
```

Or use the Makefile:

```bash
make format
make lint
make type-check
```

5. **Run Full Test Suite**

```bash
poetry run pytest
```

Or:

```bash
make test
```

### Running the CLI in Development

```bash
# Run directly
poetry run testrail --help

# Or activate shell first
poetry shell
testrail --help
```

## Testing

### Test Structure

- **Unit tests** (`tests/unit/`): Test individual functions and classes
- **Integration tests** (`tests/integration/`): Test CLI commands end-to-end
- **Fixtures** (`tests/conftest.py`): Shared test data and mocks

### Running Tests

```bash
# All tests
poetry run pytest

# Specific test file
poetry run pytest tests/unit/test_config.py

# Specific test function
poetry run pytest tests/unit/test_config.py::TestLoadConfig::test_load_config_with_explicit_path

# With coverage
poetry run pytest --cov

# With verbose output
poetry run pytest -v

# Stop on first failure
poetry run pytest -x
```

### Writing Tests

Example unit test:

```python
def test_config_loading(tmp_path):
    """Test that configuration loads correctly."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text("profiles:\n  default:\n    url: https://test.io\n")

    config = load_config(str(config_file))

    assert "profiles" in config
    assert config["profiles"]["default"]["url"] == "https://test.io"
```

Example integration test:

```python
from typer.testing import CliRunner
from testrail_cli.__main__ import cli

runner = CliRunner()

def test_projects_list_command():
    """Test projects list command."""
    result = runner.invoke(cli, ["projects", "list", "--help"])
    assert result.exit_code == 0
    assert "List all projects" in result.stdout
```

### Coverage Reports

```bash
# Generate HTML coverage report
poetry run pytest --cov --cov-report=html

# Open report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## Code Quality Tools

### Ruff (Linter and Formatter)

Ruff is an extremely fast Python linter and formatter.

```bash
# Format code
poetry run ruff format .

# Check formatting
poetry run ruff format --check .

# Lint code
poetry run ruff check .

# Fix auto-fixable issues
poetry run ruff check --fix .
```

Configuration in `pyproject.toml`:

```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "UP", "ARG", "SIM"]
ignore = ["E501"]
```

### Mypy (Type Checker)

```bash
# Type check entire package
poetry run mypy testrail_cli

# Check specific file
poetry run mypy testrail_cli/config.py

# Show error codes
poetry run mypy testrail_cli --show-error-codes
```

### Pre-commit Hooks

Pre-commit hooks run automatically before each commit:

```bash
# Install hooks
poetry run pre-commit install

# Run manually on all files
poetry run pre-commit run --all-files

# Skip hooks for a commit (not recommended)
git commit --no-verify
```

Hooks configured in `.pre-commit-config.yaml`:

- Trailing whitespace removal
- YAML validation
- Ruff formatting and linting
- Mypy type checking

## Adding New Commands

### Step 1: Create Command Module

Create `testrail_cli/commands/your_command.py`:

```python
"""Your command description."""

import typer
from rich.console import Console

app = typer.Typer(help="Your command help text")
console = Console()


@app.command("list")
def list_items(
    project_id: int = typer.Option(..., help="Project ID"),
):
    """List items for a project."""
    console.print(f"Listing items for project {project_id}")
```

### Step 2: Register Command

Add to `testrail_cli/__main__.py`:

```python
from testrail_cli.commands import your_command

app.add_typer(your_command.app, name="your-command")
```

### Step 3: Write Tests

Create `tests/unit/test_your_command.py`:

```python
def test_your_command():
    """Test your command logic."""
    # Add tests here
    pass
```

Create `tests/integration/test_your_command_cli.py`:

```python
from typer.testing import CliRunner
from testrail_cli.__main__ import cli

runner = CliRunner()

def test_your_command_cli():
    """Test your command via CLI."""
    result = runner.invoke(cli, ["your-command", "list", "--help"])
    assert result.exit_code == 0
```

### Step 4: Add Documentation

Update relevant docs:

- Add command to README.md
- Create `docs/commands/your-command.md`
- Update CHANGELOG.md

## Debugging

### Using Python Debugger

```python
# Add breakpoint
breakpoint()

# Or use pdb
import pdb; pdb.set_trace()
```

### Verbose Output

```bash
# Add --help to see all options
testrail your-command --help
```

### Testing Against Real TestRail

Create a test configuration:

```yaml
# ~/.testrail-cli-test.yaml
profiles:
  test:
    url: https://test.testrail.io
    email: test@example.com
    password: test-api-key
```

Use it:

```bash
poetry run testrail --config ~/.testrail-cli-test.yaml projects list
```

## Building and Publishing

### Local Build

```bash
# Build distribution
poetry build

# Check dist/ directory
ls -l dist/
```

### Version Bumping

Update version in `pyproject.toml` and `testrail_cli/__init__.py`.

### Publishing (Maintainers Only)

```bash
# Test PyPI
poetry publish -r testpypi

# Production PyPI
poetry publish
```

## Documentation

### Building Docs Locally

Documentation is in Markdown. View with any Markdown viewer or:

```bash
# Using grip (GitHub-flavored Markdown viewer)
pip install grip
grip README.md
```

### Documentation Standards

- Use clear, concise language
- Include code examples
- Add screenshots/GIFs where helpful
- Keep docs in sync with code

## Common Tasks (Makefile)

```bash
# Install dependencies
make dev

# Run tests
make test

# Format code
make format

# Run linter
make lint

# Type check
make type-check

# Clean build artifacts
make clean

# Build distribution
make build
```

## Continuous Integration

GitHub Actions workflows run automatically on:

- Push to main/develop
- Pull requests
- Tag creation (releases)

Workflows:

- **test.yml**: Runs tests on multiple Python versions and OSes
- **lint.yml**: Runs linting and type checking
- **release.yml**: Builds and publishes releases

## Troubleshooting

### Poetry Lock Issues

```bash
poetry lock --no-update
```

### Dependency Conflicts

```bash
poetry update
```

### Pre-commit Hook Failures

```bash
# Fix formatting
poetry run ruff format .

# Fix auto-fixable lint issues
poetry run ruff check --fix .

# Re-run hooks
poetry run pre-commit run --all-files
```

### Test Failures

```bash
# Run with verbose output
poetry run pytest -vv

# Run with print statements
poetry run pytest -s

# Run specific test with debugging
poetry run pytest tests/unit/test_config.py::test_name -vv -s
```

## Resources

- [Poetry Documentation](https://python-poetry.org/docs/)
- [Typer Documentation](https://typer.tiangolo.com/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [TestRail API Reference](https://www.gurock.com/testrail/docs/api)

## Getting Help

- Open an issue on GitHub
- Start a discussion
- Check existing issues and PRs
- Read CONTRIBUTING.md

## Best Practices

1. **Write Tests First**: TDD approach ensures better code
2. **Keep Functions Small**: Single responsibility principle
3. **Add Type Hints**: Helps catch errors early
4. **Document Code**: Docstrings for all public functions
5. **Follow Style Guide**: Ruff will enforce this
6. **Update Tests**: When fixing bugs, add regression tests
7. **Keep Commits Atomic**: One logical change per commit
8. **Write Good Commit Messages**: Explain what and why

## Code Review Checklist

Before submitting a PR:

- [ ] All tests pass
- [ ] Code is formatted (ruff format)
- [ ] No linting errors (ruff check)
- [ ] Type checking passes (mypy)
- [ ] Tests added for new features
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Commit messages are clear

Happy coding!
