"""Config command for initializing TestRail CLI configuration."""

import typer

from ..config import init_config
from ..io import console

app = typer.Typer(help="Manage TestRail CLI configuration")


@app.command("init")
def config_init(
    profile: str = typer.Option("default", help="Profile name"),
    url: str = typer.Option(..., prompt="TestRail URL", help="TestRail instance URL"),
    email: str = typer.Option(..., prompt="Email", help="User email"),
    password: str = typer.Option(
        ..., prompt="API Key/Password", hide_input=True, help="Password or API key"
    ),
) -> None:
    """Initialize or update TestRail CLI configuration."""
    try:
        config_path = init_config(profile, url, email, password)
        console.print(f"[green]Configuration saved to {config_path}[/green]")
        console.print(f"[dim]Profile: {profile}[/dim]")
    except Exception as e:
        console.print(f"[red]Failed to save configuration: {e}[/red]")
        raise typer.Exit(1) from None
