"""TestRail CLI main entrypoint."""

import sys

import typer
from rich.console import Console

from . import __version__
from .client import TestRailClient

# Import command modules
from .commands import (
    attachments,
    case_fields,
    case_types,
    cases,
    config,
    milestones,
    plans,
    priorities,
    projects,
    raw,
    result_fields,
    results,
    runs,
    sections,
    statuses,
    suites,
    tests,
    users,
)
from .config import resolve_config

app = typer.Typer(
    help="TestRail CLI - Python CLI for complete TestRail REST API access",
    no_args_is_help=True,
)

# Global options
profile_option = typer.Option(None, help="Config profile name")
url_option = typer.Option(None, help="TestRail URL", envvar="TESTRAIL_URL")
email_option = typer.Option(None, help="User email", envvar="TESTRAIL_EMAIL")
password_option = typer.Option(None, help="Password/API key", envvar="TESTRAIL_PASSWORD")
config_path_option = typer.Option(None, help="Config file path")
insecure_option = typer.Option(False, help="Skip TLS verification")
timeout_option = typer.Option(None, help="Request timeout in seconds")
proxy_option = typer.Option(None, help="Proxy URL")
retries_option = typer.Option(0, help="Number of retries on failure")
retry_backoff_option = typer.Option(1.0, help="Retry backoff in seconds")
verbose_option = typer.Option(False, help="Verbose output")
quiet_option = typer.Option(False, help="Quiet mode (suppress info)")


def _version_callback(value: bool) -> None:
    """Print version and exit when --version is provided."""
    if value:
        Console().print(f"TestRail CLI version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    ctx: typer.Context,
    _version: bool | None = typer.Option(
        None,
        "--version",
        "-V",
        help="Show version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
    profile: str | None = profile_option,
    url: str | None = url_option,
    email: str | None = email_option,
    password: str | None = password_option,
    config_path: str | None = config_path_option,
    insecure: bool = insecure_option,
    timeout: int | None = timeout_option,
    proxy: str | None = proxy_option,
    retries: int = retries_option,
    retry_backoff: float = retry_backoff_option,
    verbose: bool = verbose_option,
    quiet: bool = quiet_option,
) -> None:
    """
    TestRail CLI - Complete TestRail REST API access from the command line.

    Supports configuration via:
    - Command line flags
    - Environment variables (TESTRAIL_URL, TESTRAIL_EMAIL, TESTRAIL_PASSWORD)
    - Config file (~/.testrail-cli.yaml)
    """
    # Skip client initialization for config init command
    if ctx.invoked_subcommand == "config":
        return

    # Resolve configuration
    try:
        config = resolve_config(
            profile=profile,
            url=url,
            email=email,
            password=password,
            timeout=timeout,
            proxy=proxy,
            insecure=insecure,
            config_path=config_path,
        )

        # Create client
        client = TestRailClient(
            url=config["url"],
            email=config["email"],
            password=config["password"],
            timeout=config["timeout"],
            verify=config["verify"],
            proxy=config.get("proxy"),
        )

        # Store in context for subcommands
        ctx.ensure_object(dict)
        ctx.obj["client"] = client
        ctx.obj["verbose"] = verbose
        ctx.obj["quiet"] = quiet
        ctx.obj["retries"] = retries
        ctx.obj["retry_backoff"] = retry_backoff

    except Exception as e:
        if not quiet:
            error_console = Console()
            error_console.print(f"[red]Configuration error: {e}[/red]")
        sys.exit(1)


# Register command groups
app.add_typer(config.app, name="config")
app.add_typer(projects.app, name="projects")
app.add_typer(suites.app, name="suites")
app.add_typer(sections.app, name="sections")
app.add_typer(cases.app, name="cases")
app.add_typer(runs.app, name="runs")
app.add_typer(plans.app, name="plans")
app.add_typer(tests.app, name="tests")
app.add_typer(results.app, name="results")
app.add_typer(attachments.app, name="attachments")
app.add_typer(milestones.app, name="milestones")
app.add_typer(users.app, name="users")
app.add_typer(statuses.app, name="statuses")
app.add_typer(priorities.app, name="priorities")
app.add_typer(case_types.app, name="case-types")
app.add_typer(case_fields.app, name="case-fields")
app.add_typer(result_fields.app, name="result-fields")
app.add_typer(raw.app, name="raw")

# Expose the Typer app as the CLI entrypoint (used by tests and console_scripts)
cli = app


if __name__ == "__main__":
    cli()
