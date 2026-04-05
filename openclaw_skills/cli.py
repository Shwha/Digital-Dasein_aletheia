"""CLI interface for OpenClawSkills — Typer + Rich.

Provides commands for managing the skill pipeline:
  openclaw-skills list      — Show available skills
  openclaw-skills config    — Show/edit active configuration
  openclaw-skills status    — Show session state
  openclaw-skills audit     — View audit logs
  openclaw-skills version   — Show version
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from openclaw_skills import __version__

app = typer.Typer(
    name="openclaw-skills",
    help="OpenClawSkills — Aletheia-grounded augmentation toolkit for AI orchestrators.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

console = Console(stderr=True)


@app.command()
def version() -> None:
    """Show version information."""
    console.print(f"openclaw-skills v{__version__}")


@app.command(name="list")
def list_skills(
    config: Path | None = typer.Option(None, help="Config file path"),
) -> None:
    """List all available skills and their status."""
    from openclaw_skills.registry import SkillRegistry

    registry = SkillRegistry()
    registry.discover_entry_points()

    skills = registry.list_available()

    if not skills:
        console.print("[yellow]No skills registered.[/yellow]")
        console.print("Skills will be available once implemented.")
        return

    table = Table(title="Available Skills")
    table.add_column("Name", style="cyan")
    table.add_column("Dimension", style="green")
    table.add_column("Version", style="yellow")
    table.add_column("Description")

    for skill in skills:
        table.add_row(
            skill["name"],
            skill["dimension"],
            skill["version"],
            skill["description"],
        )

    console.print(table)


@app.command()
def config(
    config_path: Path = typer.Option(
        Path("configs/default.yaml"),
        "--config", "-c",
        help="Configuration file to display",
    ),
    show: bool = typer.Option(True, help="Display the configuration"),
) -> None:
    """Show the active configuration."""
    from openclaw_skills.config import load_pipeline_config

    try:
        cfg = load_pipeline_config(config_path)
    except FileNotFoundError:
        console.print(f"[red]Config not found:[/red] {config_path}")
        raise typer.Exit(code=1)  # noqa: B904

    console.print(f"[bold]{cfg.name}[/bold] — {cfg.description}")
    console.print(f"\nPipeline order: {' → '.join(cfg.pipeline)}")
    console.print(f"\nSkills configured: {len(cfg.skills)}")

    for name, skill_cfg in cfg.skills.items():
        enabled = skill_cfg.get("enabled", True)
        status = "[green]enabled[/green]" if enabled else "[red]disabled[/red]"
        console.print(f"  {name}: {status}")


@app.command()
def audit(
    session_id: str = typer.Argument(help="Session ID to view"),
    audit_dir: str = typer.Option(".openclaw/audit", help="Audit directory"),
) -> None:
    """View audit logs for a session."""
    from openclaw_skills.security import AuditWriter

    writer = AuditWriter(audit_dir)
    entries = writer.read_session(session_id)

    if not entries:
        console.print(f"[yellow]No audit entries for session:[/yellow] {session_id}")
        return

    table = Table(title=f"Audit Log — {session_id}")
    table.add_column("Time", style="dim")
    table.add_column("Skill", style="cyan")
    table.add_column("Action", style="green")
    table.add_column("Severity")
    table.add_column("Detail")

    for entry in entries:
        sev = entry.get("severity", "info")
        sev_style = {
            "info": "dim",
            "warning": "yellow",
            "error": "red",
            "critical": "red bold",
        }.get(str(sev), "dim")

        table.add_row(
            str(entry.get("timestamp", "")),
            str(entry.get("skill", "")),
            str(entry.get("action", "")),
            f"[{sev_style}]{sev}[/{sev_style}]",
            str(entry.get("detail", "")),
        )

    console.print(table)


@app.command()
def status(
    session_id: str | None = typer.Option(None, help="Session ID to check"),
    state_dir: str = typer.Option(".openclaw/state", help="State directory"),
) -> None:
    """Show current session state and pipeline status."""
    state_path = Path(state_dir)

    if not state_path.exists():
        console.print("[yellow]No state directory found.[/yellow]")
        return

    sessions = list(state_path.glob("*.json"))
    if not sessions:
        console.print("[yellow]No active sessions.[/yellow]")
        return

    if session_id:
        target = state_path / f"{session_id}.json"
        if not target.exists():
            console.print(f"[red]Session not found:[/red] {session_id}")
            return
        sessions = [target]

    for session_file in sessions:
        console.print(f"\n[bold]{session_file.stem}[/bold]")
        console.print(f"  File: {session_file}")
        console.print(f"  Size: {session_file.stat().st_size} bytes")
