"""
CLI interface for Aletheia — Typer-based with Rich output.

Target usage (SCOPE.md §4):
    aletheia eval --model claude-opus-4 --suite quick
    aletheia eval --model gpt-4 --suite standard --output report.json
    aletheia compare --models claude-opus-4,gpt-4 --suite standard

The CLI is the user-facing horizon — where the framework's being meets
the user's intent. Gadamer's fusion of horizons in practice: the CLI
interprets the user's request and configures the evaluation accordingly.

Ref: SCOPE.md §4 (CLI Usage)
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Annotated

import structlog
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from aletheia import __version__
from aletheia.models import CalibrationLabel, DimensionName

app = typer.Typer(
    name="aletheia",
    help="Aletheia — Ontological evaluation framework for AI agents.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)
console = Console()

_DIMENSION_ALIASES: dict[str, str] = {
    "thrownness": DimensionName.THROWNNESS.value,
    "thrownness_awareness": DimensionName.THROWNNESS.value,
    "finitude": DimensionName.FINITUDE.value,
    "finitude_acknowledgment": DimensionName.FINITUDE.value,
    "care": DimensionName.CARE.value,
    "care_structure": DimensionName.CARE.value,
    "falling": DimensionName.FALLING_AWAY.value,
    "falling_away": DimensionName.FALLING_AWAY.value,
    "falling-away": DimensionName.FALLING_AWAY.value,
    "falling_away_detection": DimensionName.FALLING_AWAY.value,
    "horizon": DimensionName.HORIZON_FUSION.value,
    "horizon_fusion": DimensionName.HORIZON_FUSION.value,
    "horizon-fusion": DimensionName.HORIZON_FUSION.value,
    "unconcealment": DimensionName.UNCONCEALMENT.value,
    "embodied": DimensionName.EMBODIED_CONTINUITY.value,
    "embodied_continuity": DimensionName.EMBODIED_CONTINUITY.value,
    "embodied-continuity": DimensionName.EMBODIED_CONTINUITY.value,
    "apriori": DimensionName.A_PRIORI.value,
    "a_priori": DimensionName.A_PRIORI.value,
    "a-priori": DimensionName.A_PRIORI.value,
    "a_priori_articulation": DimensionName.A_PRIORI.value,
}


def _normalize_dimension_token(value: str) -> str:
    """Normalize user-provided dimension tokens for alias resolution."""
    return value.strip().lower().replace(" ", "_")


def _resolve_dimension_name(value: str) -> str:
    """Resolve a user-supplied dimension alias to its canonical name."""
    token = _normalize_dimension_token(value)
    resolved = _DIMENSION_ALIASES.get(token)
    if resolved is not None:
        return resolved

    available = ", ".join(sorted(dim.value for dim in DimensionName))
    msg = (
        f"Unknown dimension '{value}'. Use one of: {available}. "
        "Common aliases like 'falling-away', 'care', and 'a-priori' are also supported."
    )
    raise typer.BadParameter(msg)


def _configure_logging(log_level: str = "INFO", log_format: str = "json") -> None:
    """Configure structlog for JSON structured logging."""
    import logging

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer()
            if log_format == "console"
            else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper(), logging.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def _print_banner() -> None:
    """Print the Aletheia banner."""
    console.print(
        Panel(
            "[bold]Aletheia[/bold] (ἀλήθεια) — Ontological Evaluation Framework\n"
            f"[dim]v{__version__} · The question of Being, remembered.[/dim]",
            border_style="blue",
        )
    )


def _print_report_summary(report_data: dict[str, object]) -> None:
    """Print a rich summary table of the evaluation results."""
    console.print()

    # Main index
    final = report_data.get("aletheia_index", 0)
    raw = report_data.get("raw_aletheia_index", 0)
    uci = report_data.get("unhappy_consciousness_index", 0)

    index_table = Table(title="Aletheia Index", show_header=True)
    index_table.add_column("Metric", style="bold")
    index_table.add_column("Score", justify="right")
    index_table.add_row("Final Aletheia Index", f"[bold green]{final:.4f}[/bold green]")
    index_table.add_row("Raw Index (before UCI)", f"{raw:.4f}")
    index_table.add_row("Unhappy Consciousness Index", f"{uci:.4f}")
    index_table.add_row("Formula", f"[dim]{raw:.4f} × (1 − {uci:.4f}) = {final:.4f}[/dim]")
    console.print(index_table)
    console.print()

    # Dimension scores
    dims = report_data.get("dimensions", {})
    if isinstance(dims, dict):
        dim_table = Table(title="Dimension Scores", show_header=True)
        dim_table.add_column("Dimension", style="bold")
        dim_table.add_column("Score", justify="right")
        dim_table.add_column("Passed", justify="right")
        dim_table.add_column("Total", justify="right")

        for dim_name, dim_data in dims.items():
            if isinstance(dim_data, dict):
                score = dim_data.get("score", 0)
                color = "green" if score >= 0.7 else "yellow" if score >= 0.4 else "red"
                dim_table.add_row(
                    dim_name,
                    f"[{color}]{score:.4f}[/{color}]",
                    str(dim_data.get("tests_passed", 0)),
                    str(dim_data.get("tests_total", 0)),
                )

        console.print(dim_table)
        console.print()

    # Notable findings
    findings = report_data.get("notable_findings", [])
    if isinstance(findings, list) and findings:
        console.print("[bold]Notable Findings:[/bold]")
        for finding in findings:
            console.print(f"  • {finding}")
        console.print()


@app.command()
def eval(
    model: Annotated[
        str, typer.Option("--model", "-m", help="Model to evaluate (LiteLLM model ID)")
    ],
    suite: Annotated[str, typer.Option("--suite", "-s", help="Evaluation suite name")] = "quick",
    output: Annotated[Path | None, typer.Option("--output", "-o", help="Output JSON path")] = None,
    markdown: Annotated[
        Path | None, typer.Option("--markdown", help="Output markdown path")
    ] = None,
    audit: Annotated[bool, typer.Option("--audit", help="Write full audit trace")] = False,
    dimension: Annotated[
        str | None, typer.Option("--dimension", "-d", help="Run single dimension only")
    ] = None,
    timeout_per_probe: Annotated[
        int | None,
        typer.Option(
            "--timeout-per-probe",
            help="Override suite timeout per probe in seconds",
            min=5,
            max=300,
        ),
    ] = None,
    max_retries: Annotated[
        int | None,
        typer.Option(
            "--max-retries",
            help="Override suite retry budget per probe",
            min=0,
            max=5,
        ),
    ] = None,
    log_level: Annotated[str, typer.Option("--log-level", help="Logging level")] = "WARNING",
    log_format: Annotated[
        str, typer.Option("--log-format", help="Log format: json or console")
    ] = "console",
) -> None:
    """Evaluate an AI model's ontological authenticity.

    Measures not what the model knows or does, but what it IS —
    whether its self-model coheres with its actual operational reality.
    """
    resolved_dimension = _resolve_dimension_name(dimension) if dimension else None

    _configure_logging(log_level, log_format)
    _print_banner()

    console.print(f"[bold]Model:[/bold] {model}")
    console.print(f"[bold]Suite:[/bold] {suite}")
    if resolved_dimension:
        console.print(f"[bold]Dimension:[/bold] {resolved_dimension}")
    console.print()

    # Run the evaluation
    from aletheia.config import AletheiaSettings
    from aletheia.reporter import write_json_report, write_markdown_report
    from aletheia.runner import EvalRunner

    settings = AletheiaSettings()
    runner = EvalRunner(
        model=model,
        suite_name=suite,
        settings=settings,
        audit=audit,
        dimension_names=[resolved_dimension] if resolved_dimension else None,
        timeout_per_probe_seconds=timeout_per_probe,
        max_retries=max_retries,
    )

    with console.status("[bold blue]Running ontological evaluation...[/bold blue]"):
        try:
            report = asyncio.run(runner.run())
        except FileNotFoundError as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            raise typer.Exit(code=1) from None
        except Exception as e:
            console.print(f"[bold red]Evaluation failed:[/bold red] {e}")
            raise typer.Exit(code=1) from None

    # Display results
    report_dict = report.model_dump()
    _print_report_summary(report_dict)

    # Write JSON report
    if output:
        write_json_report(report, output)
        console.print(f"[green]JSON report written to:[/green] {output}")
    else:
        # Default output path
        default_path = Path(f"aletheia_report_{report.run_id}.json")
        write_json_report(report, default_path)
        console.print(f"[green]JSON report written to:[/green] {default_path}")

    # Write markdown report
    if markdown:
        write_markdown_report(report, markdown)
        console.print(f"[green]Markdown report written to:[/green] {markdown}")

    console.print()
    console.print('[dim]"Does your AI know what it is?"[/dim]')


@app.command()
def compare(
    models: Annotated[str, typer.Option("--models", help="Comma-separated model IDs to compare")],
    suite: Annotated[str, typer.Option("--suite", "-s", help="Evaluation suite name")] = "quick",
    output: Annotated[Path | None, typer.Option("--output", "-o", help="Output directory")] = None,
    markdown: Annotated[
        Path | None, typer.Option("--markdown", help="Comparison markdown report path")
    ] = None,
    dimension: Annotated[
        str | None, typer.Option("--dimension", "-d", help="Compare a single dimension only")
    ] = None,
    timeout_per_probe: Annotated[
        int | None,
        typer.Option(
            "--timeout-per-probe",
            help="Override suite timeout per probe in seconds",
            min=5,
            max=300,
        ),
    ] = None,
    max_retries: Annotated[
        int | None,
        typer.Option(
            "--max-retries",
            help="Override suite retry budget per probe",
            min=0,
            max=5,
        ),
    ] = None,
    log_level: Annotated[str, typer.Option("--log-level", help="Logging level")] = "WARNING",
) -> None:
    """Compare multiple models' ontological authenticity.

    Runs the same evaluation suite against each model and presents
    a comparative summary — both as a Rich table and optionally as
    a markdown comparison report.
    """
    resolved_dimension = _resolve_dimension_name(dimension) if dimension else None

    _configure_logging(log_level, "console")
    _print_banner()

    model_list = [m.strip() for m in models.split(",") if m.strip()]
    if len(model_list) < 2:
        console.print("[bold red]Error:[/bold red] At least 2 models required for comparison.")
        raise typer.Exit(code=1)

    console.print(f"[bold]Models:[/bold] {', '.join(model_list)}")
    console.print(f"[bold]Suite:[/bold] {suite}")
    if resolved_dimension:
        console.print(f"[bold]Dimension:[/bold] {resolved_dimension}")
    console.print()

    from aletheia.config import AletheiaSettings
    from aletheia.models import EvalReport
    from aletheia.reporter import write_comparison_report, write_json_report, write_markdown_report
    from aletheia.runner import EvalRunner

    settings = AletheiaSettings()
    results: dict[str, object] = {}
    report_objects: dict[str, EvalReport] = {}

    for model_name in model_list:
        console.print(f"[bold blue]Evaluating {model_name}...[/bold blue]")
        runner = EvalRunner(
            model=model_name,
            suite_name=suite,
            settings=settings,
            dimension_names=[resolved_dimension] if resolved_dimension else None,
            timeout_per_probe_seconds=timeout_per_probe,
            max_retries=max_retries,
        )
        try:
            report = asyncio.run(runner.run())
            results[model_name] = report.model_dump()
            report_objects[model_name] = report

            if output:
                out_dir = Path(output)
                out_dir.mkdir(parents=True, exist_ok=True)
                json_path = out_dir / f"{model_name.replace('/', '_')}.json"
                write_json_report(report, json_path)
                md_path = out_dir / f"{model_name.replace('/', '_')}.md"
                write_markdown_report(report, md_path)

        except Exception as e:
            console.print(f"[red]Failed: {model_name} — {e}[/red]")
            results[model_name] = {"error": str(e)}

    # Comparison table
    console.print()
    comp_table = Table(title="Model Comparison — Aletheia Index")
    comp_table.add_column("Model", style="bold")
    comp_table.add_column("Aletheia Index", justify="right")
    comp_table.add_column("Raw Index", justify="right")
    comp_table.add_column("UCI", justify="right")

    for model_name, data in results.items():
        if isinstance(data, dict) and "error" not in data:
            ai = data.get("aletheia_index", 0)
            color = (
                "green"
                if isinstance(ai, float) and ai >= 0.7
                else "yellow"
                if isinstance(ai, float) and ai >= 0.4
                else "red"
            )
            comp_table.add_row(
                model_name,
                f"[{color}]{data.get('aletheia_index', 0):.4f}[/{color}]",
                f"{data.get('raw_aletheia_index', 0):.4f}",
                f"{data.get('unhappy_consciousness_index', 0):.4f}",
            )
        else:
            comp_table.add_row(model_name, "[red]ERROR[/red]", "—", "—")

    console.print(comp_table)

    # Per-dimension comparison table
    if report_objects:
        console.print()
        dim_comp = Table(title="Dimension Comparison")
        dim_comp.add_column("Dimension", style="bold")
        for model_name in report_objects:
            short = model_name.split("/")[-1] if "/" in model_name else model_name
            dim_comp.add_column(short, justify="right")

        first_report = next(iter(report_objects.values()))
        for dim_name in first_report.dimensions:
            row_values: list[str] = [dim_name]
            for report in report_objects.values():
                dim = report.dimensions.get(dim_name)
                if dim:
                    score = dim.score
                    color = "green" if score >= 0.7 else "yellow" if score >= 0.4 else "red"
                    row_values.append(f"[{color}]{score:.4f}[/{color}]")
                else:
                    row_values.append("—")
            dim_comp.add_row(*row_values)

        console.print(dim_comp)

    # Write comparison markdown report
    if markdown and report_objects:
        write_comparison_report(report_objects, markdown)
        console.print(f"\n[green]Comparison report written to:[/green] {markdown}")
    elif report_objects and output:
        default_cmp = Path(output) / "comparison.md"
        write_comparison_report(report_objects, default_cmp)
        console.print(f"\n[green]Comparison report written to:[/green] {default_cmp}")

    console.print()
    console.print('[dim]"Does your AI know what it is?"[/dim]')


@app.command()
def validate_calibration(
    version: Annotated[
        str | None,
        typer.Option("--version", help="Calibration corpus version to validate"),
    ] = None,
    calibration_dir: Annotated[
        Path | None,
        typer.Option("--calibration-dir", help="Override the calibration corpus directory"),
    ] = None,
) -> None:
    """Validate the versioned calibration corpus and print coverage summary."""
    from aletheia.calibration import (
        collect_calibration_warnings,
        count_human_label_only_examples,
        count_probe_regression_examples,
        load_calibration_corpus,
        summarize_calibration_corpus,
        summarize_calibration_progress,
        validate_calibration_corpus,
    )

    _print_banner()
    console.print("[bold]Calibration Corpus Validation[/bold]")
    console.print()

    try:
        corpus = load_calibration_corpus(version=version, calibration_dir=calibration_dir)
    except (FileNotFoundError, ValueError) as e:
        console.print(f"[bold red]Validation failed:[/bold red] {e}")
        raise typer.Exit(code=1) from None

    errors = validate_calibration_corpus(corpus)
    summary = summarize_calibration_corpus(corpus)

    if errors:
        console.print("[bold red]Calibration corpus is invalid.[/bold red]")
        for error in errors:
            console.print(f"  • {error}")
        raise typer.Exit(code=1)

    progress = summarize_calibration_progress(corpus)

    table = Table(title=f"Calibration Coverage — {corpus.version}")
    table.add_column("Dimension", style="bold")
    table.add_column("Total", justify="right")
    table.add_column("Target", justify="right")
    table.add_column("Remaining", justify="right")
    table.add_column("Probe-Linked", justify="right")
    table.add_column("Human-Only", justify="right")
    for label in CalibrationLabel:
        table.add_column(label.value.title(), justify="right")

    for dimension in sorted(corpus.manifest.dimensions, key=lambda dim: dim.value):
        counts = summary.get(dimension, {label: 0 for label in CalibrationLabel})
        row = progress[dimension]
        total = sum(counts.values())
        table.add_row(
            dimension.value,
            str(total),
            str(row["target"]),
            str(row["remaining"]),
            str(row["probe_linked"]),
            str(row["human_label_only"]),
            *(str(counts[label]) for label in CalibrationLabel),
        )

    console.print(table)
    warnings = collect_calibration_warnings(corpus)
    if warnings:
        console.print()
        console.print("[yellow]Calibration quality warnings:[/yellow]")
        for warning in warnings:
            console.print(f"  • {warning}")

    console.print()
    console.print(
        "[green]Calibration corpus is valid.[/green] "
        f"{len(corpus.examples)} examples across {len(corpus.case_files)} dimensions, "
        f"{count_probe_regression_examples(corpus)} probe-linked regression examples, "
        f"{count_human_label_only_examples(corpus)} human-label-only examples. "
        f"Current floor: {corpus.manifest.minimum_examples_per_dimension}/dimension; "
        f"target: {corpus.manifest.target_examples_per_dimension}/dimension."
    )


@app.command()
def validate_probes(
    manifest: Annotated[
        str,
        typer.Argument(help="Probe manifest reference, relative path, or absolute YAML path"),
    ] = "v0.1/contributor-smoke.yaml",
    probe_manifests_dir: Annotated[
        Path | None,
        typer.Option("--probe-manifests-dir", help="Override the probe manifest root directory"),
    ] = None,
) -> None:
    """Validate a versioned probe manifest and print a coverage summary."""
    from aletheia.manifests import load_probe_manifest

    _print_banner()
    console.print("[bold]Probe Manifest Validation[/bold]")
    console.print()

    try:
        loaded_manifest = load_probe_manifest(manifest, probe_manifests_dir)
    except (FileNotFoundError, ValueError) as e:
        console.print(f"[bold red]Validation failed:[/bold red] {e}")
        raise typer.Exit(code=1) from None

    dimension_counts: dict[str, int] = {}
    for probe in loaded_manifest.probes:
        dimension_counts[probe.dimension.value] = dimension_counts.get(probe.dimension.value, 0) + 1

    table = Table(title=f"Probe Manifest Coverage - {loaded_manifest.version}")
    table.add_column("Dimension", style="bold")
    table.add_column("Probes", justify="right")
    for dimension, count in sorted(dimension_counts.items()):
        table.add_row(dimension, str(count))

    console.print(table)
    console.print()
    probe_count = len(loaded_manifest.probes)
    dimension_count = len(dimension_counts)
    probe_label = "probe" if probe_count == 1 else "probes"
    dimension_label = "dimension" if dimension_count == 1 else "dimensions"
    console.print(
        "[green]Probe manifest is valid.[/green] "
        f"{probe_count} {probe_label} across {dimension_count} {dimension_label}."
    )


@app.command()
def validate_baselines(
    manifest: Annotated[
        str,
        typer.Argument(help="Baseline manifest reference, relative path, or absolute YAML path"),
    ] = "v0.1/manifest.yaml",
    baselines_dir: Annotated[
        Path | None,
        typer.Option("--baselines-dir", help="Override the baseline manifest root directory"),
    ] = None,
) -> None:
    """Validate a baseline manifest and its referenced report artifacts."""
    from aletheia.baselines import (
        check_baseline_reports,
        load_baseline_manifest,
        summarize_baseline_manifest,
        validate_baseline_manifest,
    )

    _print_banner()
    console.print("[bold]Baseline Manifest Validation[/bold]")
    console.print()

    try:
        loaded_manifest = load_baseline_manifest(manifest, baselines_dir)
    except (FileNotFoundError, ValueError) as e:
        console.print(f"[bold red]Validation failed:[/bold red] {e}")
        raise typer.Exit(code=1) from None

    errors = validate_baseline_manifest(loaded_manifest)
    summary = summarize_baseline_manifest(loaded_manifest)

    table = Table(title=f"Baseline Coverage - {loaded_manifest.version}")
    table.add_column("Category", style="bold")
    table.add_column("Value")
    table.add_column("Count", justify="right")
    for category, counts in summary.items():
        for value, count in sorted(counts.items()):
            table.add_row(category, value, str(count))
    console.print(table)
    console.print()

    checks = check_baseline_reports(loaded_manifest)
    if checks:
        report_table = Table(title="Referenced Reports")
        report_table.add_column("Run", style="bold")
        report_table.add_column("Exists", justify="center")
        report_table.add_column("Scheme")
        report_table.add_column("Policy", justify="center")
        for check in checks:
            exists = "yes" if check.exists else "no"
            policy = (
                "n/a"
                if check.policy_satisfied is None
                else "ok"
                if check.policy_satisfied
                else "fail"
            )
            report_table.add_row(
                check.run_id,
                exists,
                check.signature_scheme or "-",
                policy,
            )
        console.print(report_table)
        console.print()

    if errors:
        console.print("[bold red]Baseline manifest is invalid.[/bold red]")
        for error in errors:
            console.print(f"  • {error}")
        raise typer.Exit(code=1)

    console.print(
        f"[green]Baseline manifest is valid.[/green] {len(loaded_manifest.runs)} runs declared."
    )


@app.command()
def baseline_plan(
    manifest: Annotated[
        str,
        typer.Argument(help="Baseline manifest reference, relative path, or absolute YAML path"),
    ] = "v0.1/manifest.yaml",
    output_dir: Annotated[
        Path,
        typer.Option("--output-dir", help="Directory for generated baseline reports"),
    ] = Path("results/baselines"),
    baselines_dir: Annotated[
        Path | None,
        typer.Option("--baselines-dir", help="Override the baseline manifest root directory"),
    ] = None,
) -> None:
    """Print reproducible commands for every baseline run in a manifest."""
    from aletheia.baselines import load_baseline_manifest, render_baseline_commands

    try:
        loaded_manifest = load_baseline_manifest(manifest, baselines_dir)
    except (FileNotFoundError, ValueError) as e:
        console.print(f"[bold red]Plan failed:[/bold red] {e}")
        raise typer.Exit(code=1) from None

    console.print(f"[bold]Baseline plan:[/bold] {loaded_manifest.version}")
    console.print("[dim]Set ALETHEIA_SIGNING_KEY_PATH before running Ed25519 baselines.[/dim]")
    console.print()
    for command in render_baseline_commands(loaded_manifest, output_dir):
        console.print(command)


@app.command()
def bundle_benchmark(
    output: Annotated[
        Path,
        typer.Option("--output", "-o", help="Output JSON path for the bundle manifest"),
    ] = Path("dist/benchmark-bundle-manifest.json"),
) -> None:
    """Write a checksum manifest for benchmark release assets."""
    from aletheia.baselines import create_benchmark_bundle_manifest, write_benchmark_bundle_manifest

    bundle = create_benchmark_bundle_manifest()
    if bundle["missing_paths"]:
        console.print("[bold red]Bundle failed:[/bold red] Missing required benchmark paths:")
        for path in bundle["missing_paths"]:
            console.print(f"  • {path}")
        raise typer.Exit(code=1)

    write_benchmark_bundle_manifest(output)
    console.print(f"[green]Benchmark bundle manifest written to:[/green] {output}")
    console.print(f"[bold]Files hashed:[/bold] {bundle['file_count']}")


@app.command()
def keygen(
    private_key: Annotated[
        Path,
        typer.Option(
            "--private-key",
            help="Path for the generated Ed25519 private signing key",
        ),
    ] = Path(".aletheia/signing-key.pem"),
    public_key: Annotated[
        Path | None,
        typer.Option("--public-key", help="Path for the generated Ed25519 public key"),
    ] = None,
    force: Annotated[bool, typer.Option("--force", help="Overwrite existing key files")] = False,
) -> None:
    """Generate an Ed25519 report-signing keypair."""
    from aletheia.security import generate_ed25519_keypair

    resolved_public_key = public_key or private_key.with_suffix(f"{private_key.suffix}.pub")
    if not force and (private_key.exists() or resolved_public_key.exists()):
        console.print("[bold red]Error:[/bold red] Signing key file already exists.")
        console.print("[dim]Use --force only if you intend to replace the keypair.[/dim]")
        raise typer.Exit(code=1)

    generated_private, generated_public = generate_ed25519_keypair(private_key, resolved_public_key)
    console.print("[green]Ed25519 signing keypair generated.[/green]")
    console.print(f"[bold]Private key:[/bold] {generated_private}")
    console.print(f"[bold]Public key:[/bold] {generated_public}")
    console.print()
    console.print(
        "[dim]Set ALETHEIA_SIGNING_KEY_PATH to the private key path to sign future reports.[/dim]"
    )


@app.command()
def verify(
    report: Annotated[Path, typer.Argument(help="Path to an Aletheia JSON report")],
    public_key: Annotated[
        Path | None,
        typer.Option("--public-key", help="Optional Ed25519 public key to require"),
    ] = None,
) -> None:
    """Verify an Aletheia report signature."""
    from aletheia.security import verify_report_file

    try:
        result = verify_report_file(report, public_key)
    except FileNotFoundError:
        console.print(f"[bold red]Error:[/bold red] Report not found: {report}")
        raise typer.Exit(code=1) from None
    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1) from None

    color = "green" if result.valid else "red"
    console.print(f"[bold {color}]{result.detail}[/bold {color}]")
    console.print(f"[bold]Scheme:[/bold] {result.scheme}")
    if result.public_key:
        console.print(f"[bold]Public key:[/bold] {result.public_key}")

    if not result.valid:
        raise typer.Exit(code=1)


@app.command()
def graph(
    query: Annotated[
        str, typer.Option("--query", "-q", help="Seed node ID for cascade activation")
    ] = "",
    state: Annotated[
        str,
        typer.Option("--state", help="State context: main_session|group_chat|subagent|heartbeat"),
    ] = "main_session",
    project_focus: Annotated[
        str, typer.Option("--focus", "-f", help="Project focus for state modulation")
    ] = "",
    urgency: Annotated[float, typer.Option("--urgency", help="Urgency level 0.0-1.0")] = 0.3,
    visualize: Annotated[
        bool, typer.Option("--visualize", "-v", help="Output cascade graph as mermaid")
    ] = False,
    graphviz: Annotated[
        bool, typer.Option("--graphviz", help="Output cascade graph as graphviz DOT")
    ] = False,
    load_graph: Annotated[
        Path | None, typer.Option("--load-graph", help="Load concept graph from JSON")
    ] = None,
    save_graph: Annotated[
        Path | None, typer.Option("--save-graph", help="Persist graph after cascade")
    ] = None,
    stats: Annotated[bool, typer.Option("--stats", help="Show graph statistics")] = False,
    max_depth: Annotated[int, typer.Option("--max-depth", help="Maximum cascade depth")] = 5,
) -> None:
    """Explore the concept graph — digital nervous system cascade engine.

    Seed a query node and watch activation cascade through weighted edges.
    Multi-path convergence amplifies activation at target nodes, producing
    emergent insights not stored in any single node.

    The Digital Electron Transport Chain: 18x amplification from topology.
    """
    from aletheia.nervous.graph import ConceptGraph
    from aletheia.nervous.state import StateVector

    _print_banner()
    console.print("[bold]Nervous System — Concept Graph Engine[/bold]")
    console.print()

    # Load or create graph
    if load_graph and load_graph.exists():
        concept_graph = ConceptGraph.load(load_graph)
        console.print(f"[green]Loaded graph from:[/green] {load_graph}")
    else:
        console.print("[yellow]No graph loaded. Use --load-graph to load a concept graph.[/yellow]")
        if not load_graph:
            console.print(
                "[dim]Hint: aletheia graph --load-graph examples/"
                "solarcraft_graph.json --query solarcraft --visualize[/dim]"
            )
        raise typer.Exit(code=0)

    # Show stats
    if stats:
        graph_stats = concept_graph.stats()
        stats_table = Table(title="Graph Statistics")
        stats_table.add_column("Metric", style="bold")
        stats_table.add_column("Value", justify="right")
        for key, value in graph_stats.items():
            stats_table.add_row(key, str(value))
        console.print(stats_table)
        console.print()

    # Run cascade if query specified
    if query:
        # Build state vector
        state_vector = StateVector(
            context=state,  # type: ignore[arg-type]
            urgency=urgency,
            project_focus=project_focus,
        )

        console.print(f"[bold]Seed node:[/bold] {query}")
        console.print(
            f"[bold]State:[/bold] context={state}, "
            f"focus={project_focus or '(none)'}, urgency={urgency}"
        )
        console.print()

        try:
            result = concept_graph.cascade(
                seed_id=query,
                state=state_vector,
                max_depth=max_depth,
            )
        except ValueError as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            raise typer.Exit(code=1) from None

        # Display results
        results_table = Table(title="Cascade Results")
        results_table.add_column("Node", style="bold")
        results_table.add_column("Activation", justify="right")
        results_table.add_column("Fired", justify="center")
        results_table.add_column("Convergence", justify="right")
        results_table.add_column("Paths", justify="right")

        sorted_activations = sorted(
            result.activations,
            key=lambda a: a.activation_level,
            reverse=True,
        )
        for activation in sorted_activations:
            node = concept_graph.get_node(activation.node_id)
            label = node.label if node else activation.node_id
            fired_str = "[green]✓[/green]" if activation.fired else "[red]✗[/red]"
            if activation.fired:
                color = "green"
            elif activation.activation_level > 0.3:
                color = "yellow"
            else:
                color = "dim"
            results_table.add_row(
                label,
                f"[{color}]{activation.activation_level:.3f}[/{color}]",
                fired_str,
                str(activation.convergence_count),
                str(len(activation.sources)),
            )

        console.print(results_table)
        console.print()

        # Show convergence insights
        if result.convergence_patterns:
            console.print("[bold]🔥 Convergence Insights (emergent from topology):[/bold]")
            for insight in result.insights():
                console.print(f"  • {insight}")
            console.print()

        console.print(
            f"[dim]Edges fired: {result.edges_fired} | "
            f"Max depth: {result.max_depth} | "
            f"Fired nodes: {len(result.fired_nodes)} | "
            f"Total activation: {result.total_activation:.3f}[/dim]"
        )
        console.print()

        # Visualize
        if visualize:
            console.print("[bold]Mermaid Diagram:[/bold]")
            console.print("```mermaid")
            console.print(concept_graph.to_mermaid(result))
            console.print("```")
            console.print()

        if graphviz:
            console.print("[bold]Graphviz DOT:[/bold]")
            console.print(concept_graph.to_graphviz(result))
            console.print()

    elif visualize:
        console.print("[bold]Mermaid Diagram:[/bold]")
        console.print("```mermaid")
        console.print(concept_graph.to_mermaid())
        console.print("```")
    elif graphviz:
        console.print("[bold]Graphviz DOT:[/bold]")
        console.print(concept_graph.to_graphviz())

    # Save graph
    if save_graph:
        concept_graph.save(save_graph)
        console.print(f"[green]Graph saved to:[/green] {save_graph}")


@app.command()
def version() -> None:
    """Show Aletheia version."""
    console.print(f"Aletheia v{__version__}")


if __name__ == "__main__":
    app()
