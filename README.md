# TestRail CLI

[![Tests](https://github.com/mokson/testrail-cli/workflows/Tests/badge.svg)](https://github.com/mokson/testrail-cli/actions/workflows/test.yml)
[![Lint](https://github.com/mokson/testrail-cli/workflows/Lint/badge.svg)](https://github.com/mokson/testrail-cli/actions/workflows/lint.yml)
[![PyPI version](https://badge.fury.io/py/py-testrail-cli.svg)](https://badge.fury.io/py/py-testrail-cli)
[![Python Version](https://img.shields.io/pypi/pyversions/py-testrail-cli.svg)](https://pypi.org/project/py-testrail-cli/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

A powerful Python-based CLI for complete TestRail REST API access with CSV-driven case management.

## Features

- **Complete API Coverage**: Access all TestRail REST API endpoints through intuitive commands
- **Multi-Profile Support**: Manage multiple TestRail instances with named profiles
- **CSV Import/Export**: Bulk import test cases from CSV with field mapping
- **Flexible Output**: JSON, table, or filtered field output formats
- **CI/CD Ready**: Perfect for automation pipelines and scripting
- **Type-Safe**: Full type hints and mypy validation
- **Well-Tested**: Comprehensive test coverage with pytest
- **Modern Tooling**: Built with Poetry, Ruff, and pre-commit hooks

## Installation

### Using pip

```bash
pip install py-testrail-cli
```

### Using pipx (recommended for CLI tools)

```bash
pipx install py-testrail-cli
```

### Using Poetry

```bash
poetry add py-testrail-cli
```

> The installed executable remains `testrail`.

### From source

```bash
git clone https://github.com/mokson/testrail-cli.git
cd testrail-cli
poetry install
```

## Quick Start

### Interactive Configuration

```bash
testrail config init
```

This will prompt you for your TestRail URL, email, and API key, then create `~/.testrail-cli.yaml`.

### Environment Variables

```bash
export TESTRAIL_URL=https://your-org.testrail.io
export TESTRAIL_EMAIL=your-email@example.com
export TESTRAIL_PASSWORD=your-api-key

testrail projects list
```

### Configuration File

Create `~/.testrail-cli.yaml`:

```yaml
profiles:
  default:
    url: https://your-org.testrail.io
    email: your-email@example.com
    password: your-api-key
    timeout: 30
    verify: true

  staging:
    url: https://staging.testrail.io
    email: staging@example.com
    password: staging-api-key
```

Use profiles with `--profile` flag:

```bash
testrail --profile staging projects list
```

**Configuration Precedence**: CLI flags > Environment variables > Config file

See `examples/example-config.yaml` for all configuration options.

## Common Use Cases

### Managing Projects and Suites

```bash
# List all projects
testrail projects list

# Create a new project
testrail projects add --name "My New Project" --announcement "Welcome!"

# List suites for a project
testrail suites list --project-id 1

# List sections within a suite
testrail sections list --project-id 1 --suite-id 5
```

### Working with Test Cases

```bash
# List all test cases
testrail cases list --project-id 1 --suite-id 5

# Filter by priority and creation date
testrail cases list --project-id 1 --priority-id 1,2 --created-after 2024-01-01

# Filter by specific case IDs
testrail cases list --project-id 1 --case-ids 123,124,125

# Add a new test case
testrail cases add \
  --section-id 10 \
  --title "Test user login with valid credentials" \
  --priority-id 2 \
  --estimate "5m" \
  --refs "JIRA-123"

# Update existing test case
testrail cases update 123 --title "Updated test title" --priority-id 1

# Update using a JSON file (for complex fields)
testrail cases update 123 --json update.json

# Update via stdin
echo '{"custom_preconds": "New preconditions"}' | testrail cases update 123 --file -

# Delete test case (soft delete)
testrail cases delete 123 --soft 1 --yes
```

### CSV Import: Bulk Test Case Creation

The CSV import feature is perfect for migrating test cases or bulk creation:

```bash
testrail cases import \
  --project-id 1 \
  --suite-id 5 \
  --csv test-cases.csv \
  --section-path "API/Authentication" \
  --template-id 2 \
  --steps-field custom_steps_separated \
  --create-missing-sections \
  --mapping field-mapping.yaml
```

**Example CSV (one row per step, `case_id` required)** (`test-cases.csv`):

```csv
case_id,title,section,priority_id,type_id,template_id,estimate,refs,step,expected,additional_info,mission,goals,preconds
,Checkout happy path,Checkout/Payments,2,1,3m,REQ-400,Open checkout,Form renders,,,
,Checkout happy path,Checkout/Payments,2,1,3m,REQ-400,Enter valid card,Payment succeeds,,,
,Exploratory Session,Exploratory,2,1,30m,REQ-600,,,,,Test App,Find Bugs,
```

- `case_id` column is mandatory; leave it blank to create, set it to update/overwrite (including steps).
- Specify the TestRail template via `--template-id` (overrides any CSV value).
- Each step is a separate CSV row repeating the case fields; the importer groups rows by `case_id` (or `title`+`section` when `case_id` is empty).
- `--steps-field` controls which TestRail field receives the steps (`custom_steps_separated` by default, or `custom_steps`/`custom_gherkin` for text/BDD templates).
- **Supported Template Fields**: The importer automatically maps standard CSV columns to TestRail custom fields:
  - `mission` -> `custom_mission` (Exploratory templates)
  - `goals` -> `custom_goals` (Exploratory templates)
  - `preconds` / `preconditions` -> `custom_preconds` (Steps templates)

**Export to CSV (same format as import)**:

```bash
testrail cases export \
  --project-id 1 \
  --suite-id 5 \
  --csv exported-cases.csv \
  --priority-id 1,2
```

You can export by filters (suite/section/priority/type) or explicit `--case-ids`, edit the CSV, and re-import with `cases import`.

See `examples/example-cases.csv` and `examples/example-mapping.yaml` for the reference format.

### Test Runs and Results

```bash
# Create a new test run
testrail runs add \
  --project-id 1 \
  --suite-id 5 \
  --name "Sprint 10 Regression" \
  --include-all true \
  --assignedto-id 5

# Add a single test result
testrail results add \
  --test-id 1001 \
  --status-id 1 \
  --comment "Test passed successfully" \
  --elapsed "5m"

# Bulk add results from JSON file
testrail results add-bulk --run-id 50 --results-file results.json

# Close a test run
testrail runs close 50
```

**Bulk Results Format** (`results.json`):

```json
[
  {
    "test_id": 1001,
    "status_id": 1,
    "comment": "Test passed",
    "elapsed": "2m"
  },
  {
    "test_id": 1002,
    "status_id": 5,
    "comment": "Test failed: timeout",
    "defects": "BUG-456",
    "elapsed": "5m"
  }
]
```

### Test Plans and Milestones

```bash
# List milestones
testrail milestones list --project-id 1

# Create a milestone
testrail milestones add \
  --project-id 1 \
  --name "Release 2.0" \
  --description "Q4 2024 Release" \
  --due-on 2024-12-31

# List test plans
testrail plans list --project-id 1 --is-completed 0

# Close a test plan
testrail plans close 25
```

### Output Formats and Filtering

```bash
# JSON output (default)
testrail projects list --output json

# Table output
testrail projects list --output table

# Table with specific fields only
testrail projects list --output table --fields id,name,is_completed

# Filter specific fields in JSON
testrail cases list --project-id 1 --suite-id 5 --fields id,title,priority_id
```

### Raw API Access

For endpoints not yet covered by specific commands, use the `raw` command:

```bash
# GET request
testrail raw --endpoint get_projects --method GET

# POST with inline data
testrail raw \
  --endpoint add_case/123 \
  --method POST \
  --data title="New test case" \
  --data priority_id=2

# POST with JSON file
testrail raw \
  --endpoint add_run/1 \
  --method POST \
  --payload-file run.json
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: TestRail Integration

on:
  workflow_run:
    workflows: ["Tests"]
    types: [completed]

jobs:
  upload-results:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install TestRail CLI
        run: pipx install testrail-cli

      - name: Upload test results
        env:
          TESTRAIL_URL: ${{ secrets.TESTRAIL_URL }}
          TESTRAIL_EMAIL: ${{ secrets.TESTRAIL_EMAIL }}
          TESTRAIL_PASSWORD: ${{ secrets.TESTRAIL_API_KEY }}
        run: |
          testrail results add-bulk --run-id ${{ secrets.RUN_ID }} --results-file results.json
          testrail runs close ${{ secrets.RUN_ID }}
```

### Jenkins Pipeline Example

```groovy
pipeline {
    agent any
    stages {
        stage('Upload Results') {
            steps {
                withCredentials([
                    string(credentialsId: 'testrail-url', variable: 'TESTRAIL_URL'),
                    string(credentialsId: 'testrail-email', variable: 'TESTRAIL_EMAIL'),
                    string(credentialsId: 'testrail-key', variable: 'TESTRAIL_PASSWORD')
                ]) {
                    sh '''
                        testrail results add-bulk --run-id ${RUN_ID} --results-file results.json
                        [ $? -eq 0 ] && testrail runs close ${RUN_ID}
                    '''
                }
            }
        }
    }
}
```

### Shell Script Example

```bash
#!/bin/bash
set -e

RUN_ID=$1
RESULTS_FILE="test-results.json"

# Upload results to TestRail
echo "Uploading test results to TestRail run ${RUN_ID}..."
testrail results add-bulk --run-id "${RUN_ID}" --results-file "${RESULTS_FILE}"

# Close the run if upload succeeded
if [ $? -eq 0 ]; then
    echo "Closing test run ${RUN_ID}..."
    testrail runs close "${RUN_ID}"
    echo "Test run closed successfully"
else
    echo "Failed to upload results"
    exit 1
fi
```

## Available Commands

### Core Resources

- `projects` - Manage projects
- `suites` - Manage test suites
- `sections` - Manage test sections
- `cases` - Manage test cases (includes CSV import)
- `runs` - Manage test runs
- `plans` - Manage test plans
- `tests` - View individual tests
- `results` - Add and manage test results
- `milestones` - Manage milestones
- `attachments` - Manage attachments

### Administrative

- `users` - List users
- `statuses` - List test statuses
- `priorities` - List priorities
- `case-types` - List case types
- `case-fields` - List custom case fields
- `result-fields` - List custom result fields

### Utilities

- `config` - Initialize and manage configuration
- `raw` - Direct API endpoint access

Use `testrail <command> --help` for detailed options on any command.

## Getting Your TestRail API Key

1. Log in to your TestRail instance
2. Click on your profile icon (top right)
3. Select "My Settings"
4. Go to the "API Keys" section
5. Click "Add Key"
6. Copy the generated API key (treat it like a password)

## Documentation

- [Installation Guide](docs/installation.md)
- [Configuration Guide](docs/configuration.md)
- [Command Reference](docs/commands/)
- [CSV Import Guide](docs/csv-import.md)
- [Development Guide](docs/development.md)
- [Contributing Guidelines](CONTRIBUTING.md)

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/mokson/testrail-cli.git
cd testrail-cli

# Install dependencies
poetry install

# Set up pre-commit hooks
make pre-commit
```

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
poetry run pytest --cov

# Run specific test file
poetry run pytest tests/unit/test_config.py
```

### Code Quality

```bash
# Format code
make format

# Run linter
make lint

# Type check
make type-check

# Run all checks
make lint && make type-check && make test
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed development guidelines.

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md).

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/mokson/testrail-cli/issues)
- **Discussions**: [GitHub Discussions](https://github.com/mokson/testrail-cli/discussions)
- **Documentation**: [docs/](docs/)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes in each release.

## Acknowledgments

- Built with [Typer](https://typer.tiangolo.com/) for CLI framework
- Uses [Rich](https://rich.readthedocs.io/) for beautiful terminal output
- API wrapper provided by [testrail-api](https://pypi.org/project/testrail-api/)
