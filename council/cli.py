"""CLI entry point for The CISO Council.

Commands:
    serve       Start the War Room web UI (default: localhost:8000)
    run         Run a council session from the terminal
    validate    Validate all scenario YAML files
    personas    List available council personas
    scenarios   List available scenarios
"""

from __future__ import annotations

import click
from rich.console import Console
from rich.table import Table

console = Console()


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    """The CISO Council: AI-powered GRC decision council."""
    if ctx.invoked_subcommand is None:
        # Default to serve if no subcommand given
        ctx.invoke(serve)


@main.command()
@click.option("--host", default="127.0.0.1", help="Host to bind to")
@click.option("--port", default=8000, help="Port to bind to")
@click.option("--reload", is_flag=True, help="Enable auto-reload for development")
def serve(host: str, port: int, reload: bool):
    """Start the War Room web interface."""
    import uvicorn

    console.print()
    console.print("[bold yellow]THE CISO COUNCIL[/bold yellow] [dim]War Room[/dim]")
    console.print(f"[dim]Starting at[/dim] [cyan]http://{host}:{port}[/cyan]")
    console.print("[dim]Press Ctrl+C to stop[/dim]")
    console.print()

    uvicorn.run(
        "council.server:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )


@main.command()
@click.option("--scenario", "-s", required=True, help="Path to scenario YAML file")
@click.option("--members", "-m", default=None, help="Comma-separated persona IDs")
@click.option("--format", "-f", "fmt", default=None, help="Output format: markdown, json, or both")
def run(scenario: str, members: str | None, fmt: str | None):
    """Run a council session from the terminal."""
    import asyncio
    from council.config import load_config
    from council.session import CouncilSession
    from council.report import save_report

    member_list = [m.strip() for m in members.split(",")] if members else None

    config = load_config()
    if fmt:
        config.output.format = fmt

    session = CouncilSession(config)
    try:
        report = asyncio.run(session.run(scenario_path=scenario, members=member_list))
    except (ValueError, FileNotFoundError) as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise SystemExit(1)

    from pathlib import Path
    output_dir = Path(__file__).parent.parent / config.output.directory
    saved = save_report(report, output_dir=output_dir, fmt=config.output.format)
    for path in saved:
        console.print(f"[green]Saved:[/green] {path}")

    # Print the top recommendation to terminal.
    if report.top_recommendation:
        console.print()
        console.print("[bold]Top Recommendation:[/bold]")
        console.print(report.top_recommendation)


@main.command()
def personas():
    """List all available council personas."""
    from council.personas import list_personas as get_personas

    table = Table(title="Council Personas", border_style="dim")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="bold")
    table.add_column("Title")
    table.add_column("Sector")
    table.add_column("Risk", justify="center")
    table.add_column("Style")

    for p in get_personas():
        risk_display = "█" * p.risk_appetite.value + "░" * (5 - p.risk_appetite.value)
        risk_colour = (
            "green" if p.risk_appetite.value <= 2
            else "yellow" if p.risk_appetite.value <= 3
            else "red"
        )
        table.add_row(
            p.id,
            p.name,
            p.title,
            f"{p.org_context.size} {p.org_context.sector}",
            f"[{risk_colour}]{risk_display}[/{risk_colour}]",
            p.decision_style.value.replace("_", " "),
        )

    console.print(table)


@main.command()
def scenarios():
    """List all available scenarios."""
    from pathlib import Path

    import yaml

    scenarios_dir = Path(__file__).parent.parent / "scenarios"
    table = Table(title="Available Scenarios", border_style="dim")
    table.add_column("Domain", style="cyan")
    table.add_column("Title", style="bold")
    table.add_column("Path", style="dim")

    for yaml_path in sorted(scenarios_dir.rglob("*.yaml")):
        try:
            with open(yaml_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            table.add_row(
                data.get("domain", "?").replace("_", " "),
                data.get("title", yaml_path.stem),
                str(yaml_path.relative_to(scenarios_dir.parent)),
            )
        except Exception:
            continue

    console.print(table)


@main.command()
def validate():
    """Validate all scenario YAML files."""
    from pathlib import Path

    import yaml

    scenarios_dir = Path(__file__).parent.parent / "scenarios"
    valid = 0
    invalid = 0
    required_fields = ["title", "domain", "context", "dilemma"]

    for yaml_path in sorted(scenarios_dir.rglob("*.yaml")):
        try:
            with open(yaml_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            missing = [f for f in required_fields if f not in data]
            if missing:
                console.print(f"[red]FAIL[/red] {yaml_path.name}: missing {', '.join(missing)}")
                invalid += 1
            else:
                console.print(f"[green]PASS[/green] {yaml_path.name}")
                valid += 1
        except Exception as e:
            console.print(f"[red]ERROR[/red] {yaml_path.name}: {e}")
            invalid += 1

    console.print()
    console.print(f"[bold]Results:[/bold] {valid} passed, {invalid} failed")


if __name__ == "__main__":
    main()
