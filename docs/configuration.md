# Configuration Guide

This guide explains how to configure TestRail CLI to connect to your TestRail instance.

## Configuration Methods

TestRail CLI supports three configuration methods with the following precedence:

1. **CLI flags** (highest priority)
2. **Environment variables**
3. **Configuration file** (lowest priority)

## Quick Setup: Interactive Configuration

The easiest way to get started:

```bash
testrail config init
```

This will prompt you for:

- TestRail URL
- Email address
- API key

It creates `~/.testrail-cli.yaml` with secure permissions (600 on Unix).

## Configuration File

### Location

TestRail CLI searches for configuration files in this order:

1. Path specified with `--config` flag
2. `./.testrail-cli.yaml` (current directory)
3. `~/.testrail-cli.yaml` (home directory)

### Basic Configuration

Create `~/.testrail-cli.yaml`:

```yaml
profiles:
  default:
    url: https://your-org.testrail.io
    email: your-email@example.com
    password: your-api-key
    timeout: 30
    verify: true
```

### Multi-Profile Configuration

Manage multiple TestRail instances:

```yaml
profiles:
  default:
    url: https://prod.testrail.io
    email: prod@example.com
    password: prod-api-key

  staging:
    url: https://staging.testrail.io
    email: staging@example.com
    password: staging-api-key
    timeout: 60
    verify: true

  dev:
    url: https://dev.testrail.io
    email: dev@example.com
    password: dev-api-key
    verify: false  # For self-signed certificates
```

Use a specific profile:

```bash
testrail --profile staging projects list
```

### Configuration Options

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `url` | string | TestRail instance URL (required) | - |
| `email` | string | Your email address (required) | - |
| `password` | string | API key or password (required) | - |
| `timeout` | integer | Request timeout in seconds | 30 |
| `verify` | boolean | Verify SSL certificates | true |
| `proxy` | string | HTTP proxy URL | - |

### Security Best Practices

1. **File Permissions**: The config file is automatically set to 600 (owner read/write only) on Unix systems.

2. **Use API Keys**: Always use API keys instead of passwords:
   - Go to TestRail > My Settings > API Keys
   - Generate a new API key
   - Use the key as the `password` value

3. **Protect Your Config**:

```bash
# Verify permissions
ls -la ~/.testrail-cli.yaml

# Set correct permissions if needed
chmod 600 ~/.testrail-cli.yaml
```

4. **Don't Commit Config Files**:

```bash
# Add to .gitignore
echo ".testrail-cli.yaml" >> .gitignore
```

## CSV Import/Export Round-Trip

Use a single CSV shape (one row per step) to export, edit, and re-import test cases:

```bash
# Export
testrail cases export --project-id 1 --suite-id 5 --csv exported.csv

# Re-import (create/update using the same file)
testrail cases import --project-id 1 --suite-id 5 --csv exported.csv --template-id 2 --steps-field custom_steps_separated
```

- CSV must include a `case_id` column. Leave it blank to create, set it to update (steps are overwritten).
- Each step is its own row; repeat the case fields for every row of the same case.
- `--template-id` and `--steps-field` control where step data lands (e.g., `custom_steps_separated`, `custom_steps`, `custom_gherkin`).
- You can export by filters (`suite-id`, `section-id`, `priority-id`, `type-id`) or explicit `--case-ids`, then edit and re-import without changing the columns.

## Environment Variables

Set environment variables for temporary configuration or CI/CD:

```bash
export TESTRAIL_URL="https://your-org.testrail.io"
export TESTRAIL_EMAIL="your-email@example.com"
export TESTRAIL_PASSWORD="your-api-key"
```

Available variables:

- `TESTRAIL_URL`
- `TESTRAIL_EMAIL`
- `TESTRAIL_PASSWORD`

### CI/CD Example

#### GitHub Actions

```yaml
- name: Upload test results
  env:
    TESTRAIL_URL: ${{ secrets.TESTRAIL_URL }}
    TESTRAIL_EMAIL: ${{ secrets.TESTRAIL_EMAIL }}
    TESTRAIL_PASSWORD: ${{ secrets.TESTRAIL_API_KEY }}
  run: testrail results add-bulk --run-id 123 --results-file results.json
```

#### GitLab CI

```yaml
upload_results:
  script:
    - testrail results add-bulk --run-id $RUN_ID --results-file results.json
  variables:
    TESTRAIL_URL: $TESTRAIL_URL
    TESTRAIL_EMAIL: $TESTRAIL_EMAIL
    TESTRAIL_PASSWORD: $TESTRAIL_API_KEY
```

## CLI Flags

Override configuration for a single command:

```bash
testrail \
  --url https://custom.testrail.io \
  --email custom@example.com \
  --password custom-key \
  projects list
```

Available global flags:

- `--url`: TestRail URL
- `--email`: Email address
- `--password`: API key/password
- `--profile`: Profile name from config
- `--config`: Path to config file
- `--timeout`: Request timeout
- `--insecure`: Disable SSL verification
- `--proxy`: HTTP proxy URL

## Getting Your API Key

1. Log in to TestRail
2. Click your profile icon (top right)
3. Select "My Settings"
4. Navigate to "API Keys" section
5. Click "Add Key"
6. Copy the generated key
7. Use it as the `password` in your configuration

## Proxy Configuration

### Configuration File

```yaml
profiles:
  default:
    url: https://your-org.testrail.io
    email: your-email@example.com
    password: your-api-key
    proxy: http://proxy.company.com:8080
```

### Environment Variable

```bash
export TESTRAIL_PROXY="http://proxy.company.com:8080"
```

### CLI Flag

```bash
testrail --proxy http://proxy.company.com:8080 projects list
```

## Self-Signed Certificates

If your TestRail instance uses self-signed certificates:

### Option 1: Disable Verification (Not Recommended for Production)

```yaml
profiles:
  default:
    url: https://your-org.testrail.io
    email: your-email@example.com
    password: your-api-key
    verify: false
```

Or use the `--insecure` flag:

```bash
testrail --insecure projects list
```

### Option 2: Use Custom CA Certificate (Recommended)

```bash
# Set the CA bundle path
export REQUESTS_CA_BUNDLE=/path/to/ca-bundle.crt
testrail projects list
```

## Troubleshooting

### Connection Issues

Test your connection:

```bash
testrail projects list
```

Common issues:

1. **Invalid URL**: Ensure URL doesn't have trailing slash
2. **Wrong API Key**: Regenerate API key in TestRail
3. **Network Issues**: Check proxy settings
4. **SSL Errors**: Use `--insecure` for testing (fix certificates for production)

### Configuration Not Found

Check search paths:

```bash
# Current directory
ls -la .testrail-cli.yaml

# Home directory
ls -la ~/.testrail-cli.yaml
```

### Permission Denied

Fix file permissions:

```bash
chmod 600 ~/.testrail-cli.yaml
```

### Profile Not Found

List available profiles:

```bash
cat ~/.testrail-cli.yaml | grep -A 5 "profiles:"
```

## Example Configurations

### Minimal Configuration

```yaml
profiles:
  default:
    url: https://example.testrail.io
    email: user@example.com
    password: api-key
```

### Complete Configuration

```yaml
profiles:
  production:
    url: https://prod.testrail.io
    email: prod@example.com
    password: prod-api-key
    timeout: 60
    verify: true
    proxy: http://proxy.company.com:8080

  staging:
    url: https://staging.testrail.io
    email: staging@example.com
    password: staging-api-key
    timeout: 30
    verify: true

  local:
    url: http://localhost:8080
    email: dev@example.com
    password: dev-api-key
    verify: false
```

### CI/CD Configuration (Environment Variables Only)

```bash
#!/bin/bash
# ci-testrail.sh

export TESTRAIL_URL="${CI_TESTRAIL_URL}"
export TESTRAIL_EMAIL="${CI_TESTRAIL_EMAIL}"
export TESTRAIL_PASSWORD="${CI_TESTRAIL_API_KEY}"

testrail results add-bulk --run-id "${RUN_ID}" --results-file results.json
```

## Next Steps

- [Command Reference](commands/) - Learn available commands
- [CSV Import Guide](csv-import.md) - Bulk import test cases
- [Development Guide](development.md) - Contribute to the project
