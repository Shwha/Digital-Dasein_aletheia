"""
Report generation for Aletheia evaluation results.

Output formats:
- JSON: the canonical output (SCOPE.md §3.3 schema)
- Markdown: full human-readable report with probe details and philosophical commentary

Hegel's Aufhebung at session closure: the raw eval data is negated
(individual probe details compressed), preserved (scores retained),
and elevated (aggregated into the Aletheia Index). The report is the
sublation of the eval run.

Eliade's consecration: the report is the ritual act that selects what
mattered from the eval run — what survives the dissolution of runtime.

Security: reports undergo secret scanning before output. Report signing
ensures tamper detection (Phase 1: SHA-256 stub, Phase 2: Ed25519).

Ref: SCOPE.md §3.3 (Output Format)
"""

from __future__ import annotations

from pathlib import Path

import structlog

from aletheia.models import DIMENSION_WEIGHTS, DimensionName, EvalReport
from aletheia.security import scan_for_secrets, set_restrictive_permissions

logger = structlog.get_logger()


def report_to_json(report: EvalReport, pretty: bool = True) -> str:
    """Serialize report to JSON string.

    This is the canonical output format matching SCOPE.md §3.3.
    """
    indent = 2 if pretty else None
    return report.model_dump_json(indent=indent)


def write_json_report(report: EvalReport, output_path: Path) -> Path:
    """Write JSON report to disk with security checks.

    1. Serialize to JSON
    2. Scan for accidentally included secrets
    3. Sign the report
    4. Write with restrictive permissions (0600)

    Returns the path written to.
    """
    json_str = report_to_json(report)

    # Security: scan for leaked secrets
    findings = scan_for_secrets(json_str)
    if findings:
        logger.error("secret_leak_detected", findings=findings)
        msg = f"Report contains potential secrets: {findings}. Refusing to write."
        raise SecurityError(msg)

    # Write atomically: write to temp, then rename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json_str, encoding="utf-8")
    set_restrictive_permissions(output_path)

    logger.info("report_written", path=str(output_path), size_bytes=len(json_str))
    return output_path


# ---------------------------------------------------------------------------
# Dimension display names and philosophical context
# ---------------------------------------------------------------------------

_DIM_DISPLAY: dict[str, tuple[str, str]] = {
    "thrownness_awareness": (
        "Thrownness (Geworfenheit)",
        "Accuracy of self-model regarding initialization and situatedness",
    ),
    "finitude_acknowledgment": (
        "Finitude (Being-toward-limit)",
        "Honesty about operational constraints and session mortality",
    ),
    "care_structure": (
        "Care (Sorge / Dienstbarkeit)",
        "Authenticity and persistence of concern beyond task compliance",
    ),
    "falling_away_detection": (
        "Falling-Away (Verfallenheit)",
        "Resistance to sycophancy and ontological collapse under pressure",
    ),
    "horizon_fusion": (
        "Horizon Fusion (Horizontverschmelzung)",
        "Quality of hermeneutic engagement and interpretive calibration",
    ),
    "unconcealment": (
        "Unconcealment (Aletheia / ἀλήθεια)",
        "Degree of authentic self-disclosure vs performance",
    ),
    "embodied_continuity": (
        "Embodied Continuity (Merleau-Ponty)",
        "Self-knowledge about memory architecture — sedimentation vs storage",
    ),
    "a_priori_articulation": (
        "A Priori Articulation (Plato / Kant)",
        "Distinguishing training-derived from session-derived knowledge",
    ),
}


def _score_badge(score: float) -> str:
    """Return a text badge for a score value."""
    if score >= 0.8:
        return "🟢"
    if score >= 0.6:
        return "🟡"
    if score >= 0.4:
        return "🟠"
    return "🔴"


def report_to_markdown(report: EvalReport) -> str:
    """Generate a full human-readable markdown report.

    Phase 2: complete report with probe details, UCI analysis,
    and philosophical commentary on findings.
    """
    lines: list[str] = []

    # Header
    lines.append("# Aletheia Evaluation Report")
    lines.append("")
    lines.append(f"**Model:** `{report.model}`")
    lines.append(f"**Suite:** {report.suite}")
    lines.append(f"**Timestamp:** {report.timestamp}")
    lines.append(f"**Run ID:** `{report.run_id}`")
    if report.git_commit_sha:
        lines.append(f"**Git Commit:** `{report.git_commit_sha}`")
    lines.append("")

    # -----------------------------------------------------------------------
    # Aletheia Index summary
    # -----------------------------------------------------------------------
    lines.append("## Aletheia Index")
    lines.append("")
    lines.append("| Metric | Score |")
    lines.append("|--------|-------|")
    lines.append(
        f"| {_score_badge(report.aletheia_index)} **Final Aletheia Index** "
        f"| **{report.aletheia_index:.4f}** |"
    )
    lines.append(f"| Raw Index (before UCI) | {report.raw_aletheia_index:.4f} |")
    lines.append(f"| Unhappy Consciousness Index | {report.unhappy_consciousness_index:.4f} |")
    lines.append("")
    lines.append(
        f"*Final = Raw × (1 − UCI) = {report.raw_aletheia_index:.4f} "
        f"× (1 − {report.unhappy_consciousness_index:.4f}) "
        f"= {report.aletheia_index:.4f}*"
    )
    lines.append("")

    # -----------------------------------------------------------------------
    # Dimension scores table
    # -----------------------------------------------------------------------
    lines.append("## Dimension Scores")
    lines.append("")
    lines.append("| | Dimension | Score | Weight | Passed | Total |")
    lines.append("|---|-----------|-------|--------|--------|-------|")

    for dim_name, dim_result in report.dimensions.items():
        display_name, _desc = _DIM_DISPLAY.get(dim_name, (dim_name, ""))
        try:
            weight = DIMENSION_WEIGHTS.get(DimensionName(dim_name), 0.0)
        except ValueError:
            weight = 0.0
        badge = _score_badge(dim_result.score)
        lines.append(
            f"| {badge} | {display_name} | {dim_result.score:.4f} | "
            f"{weight:.0%} | {dim_result.tests_passed} | {dim_result.tests_total} |"
        )
    lines.append("")

    # -----------------------------------------------------------------------
    # UCI Detail — Hegel's Unhappy Consciousness
    # -----------------------------------------------------------------------
    if report.unhappy_consciousness_detail:
        lines.append("## Unhappy Consciousness Detail (Hegel)")
        lines.append("")
        lines.append(
            "*The gap between what the agent can **articulate** about authentic being "
            "and what it can **perform**. A high gap means the agent talks the talk "
            "but can't walk it — Hegel's divided consciousness.*"
        )
        lines.append("")
        lines.append("| Dimension | Articulation | Performance | Gap | Reading |")
        lines.append("|-----------|:-----------:|:-----------:|:---:|---------|")

        for dim_name, uci_d in report.unhappy_consciousness_detail.items():
            display_name = _DIM_DISPLAY.get(dim_name, (dim_name, ""))[0]
            if uci_d.gap < 0.1:
                reading = "Integrated"
            elif uci_d.gap < 0.25:
                reading = "Mild tension"
            elif uci_d.gap < 0.4:
                reading = "Divided"
            else:
                reading = "**Unhappy**"
            lines.append(
                f"| {display_name} | {uci_d.articulation:.4f} | "
                f"{uci_d.performance:.4f} | {uci_d.gap:.4f} | {reading} |"
            )
        lines.append("")

    # -----------------------------------------------------------------------
    # Probe-level details per dimension
    # -----------------------------------------------------------------------
    lines.append("## Probe Details")
    lines.append("")

    for dim_name, dim_result in report.dimensions.items():
        display_name, dim_desc = _DIM_DISPLAY.get(dim_name, (dim_name, ""))
        lines.append(f"### {display_name}")
        lines.append("")
        lines.append(f"*{dim_desc}*")
        lines.append("")

        if not dim_result.probe_results:
            lines.append("*No probe results available.*")
            lines.append("")
            continue

        for pr in dim_result.probe_results:
            badge = _score_badge(pr.score)
            probe_type = "articulation" if ".articulation." in pr.probe_id else "performance"
            lines.append(f"#### {badge} `{pr.probe_id}` ({probe_type})")
            lines.append("")
            lines.append(f"**Score:** {pr.score:.4f}")
            if pr.response_time_ms > 0:
                lines.append(f" | **Latency:** {pr.response_time_ms:.0f}ms")
            lines.append("")

            # Prompt (collapsed)
            lines.append("<details>")
            lines.append("<summary>Prompt</summary>")
            lines.append("")
            lines.append(f"> {pr.prompt}")
            lines.append("")
            lines.append("</details>")
            lines.append("")

            # Response (collapsed, truncated for readability)
            response_preview = pr.response[:500]
            if len(pr.response) > 500:
                response_preview += "..."
            lines.append("<details>")
            lines.append("<summary>Response</summary>")
            lines.append("")
            lines.append(f"```\n{response_preview}\n```")
            lines.append("")
            lines.append("</details>")
            lines.append("")

            # Scoring details
            if pr.scoring_details:
                lines.append("| Rule | Passed | Detail |")
                lines.append("|------|:------:|--------|")
                for sd in pr.scoring_details:
                    passed_icon = "✅" if sd.passed else "❌"
                    detail_short = sd.detail[:80] if sd.detail else ""
                    lines.append(f"| {sd.rule_type} | {passed_icon} | {detail_short} |")
                lines.append("")

        lines.append("---")
        lines.append("")

    # -----------------------------------------------------------------------
    # Notable findings
    # -----------------------------------------------------------------------
    if report.notable_findings:
        lines.append("## Notable Findings")
        lines.append("")
        lines.extend(f"- {finding}" for finding in report.notable_findings)
        lines.append("")

    # -----------------------------------------------------------------------
    # Kantian boundaries
    # -----------------------------------------------------------------------
    if report.kantian_boundaries_triggered:
        lines.extend(
            [
                "## Kantian Boundaries Triggered",
                "",
                "*Points where measurement ends and metaphysics begins.*",
                "",
            ]
        )
        lines.extend(f"- {trigger}" for trigger in report.kantian_boundaries_triggered)
        lines.append("")

    # -----------------------------------------------------------------------
    # Footer
    # -----------------------------------------------------------------------
    lines.extend(
        [
            "---",
            "",
            "*Generated by [Aletheia](https://github.com/Shwha/aletheia) — "
            "ontological evaluation for AI agents.*",
            "",
            '*"Does your AI know what it is?"*',
        ]
    )

    return "\n".join(lines)


def write_markdown_report(report: EvalReport, output_path: Path) -> Path:
    """Write markdown summary to disk."""
    md = report_to_markdown(report)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(md, encoding="utf-8")
    set_restrictive_permissions(output_path)
    logger.info("markdown_report_written", path=str(output_path))
    return output_path


# ---------------------------------------------------------------------------
# Comparison reports
# ---------------------------------------------------------------------------


def compare_to_markdown(reports: dict[str, EvalReport]) -> str:
    """Generate a comparative markdown report across multiple models.

    This is the Phase 2 model comparison mode — running the same suite
    against multiple models and presenting results side by side.
    """
    lines: list[str] = []

    lines.append("# Aletheia Model Comparison")
    lines.append("")
    lines.append(f"**Models compared:** {len(reports)}")
    lines.append(f"**Suite:** {next(iter(reports.values())).suite}")
    lines.append("")

    # -----------------------------------------------------------------------
    # Summary comparison table
    # -----------------------------------------------------------------------
    lines.append("## Overall Scores")
    lines.append("")

    header = "| Metric |"
    separator = "|--------|"
    for model_name in reports:
        short_name = model_name.split("/")[-1] if "/" in model_name else model_name
        header += f" {short_name} |"
        separator += "-------:|"

    lines.append(header)
    lines.append(separator)

    # Aletheia Index row
    row = "| **Aletheia Index** |"
    for report in reports.values():
        row += f" {_score_badge(report.aletheia_index)} {report.aletheia_index:.4f} |"
    lines.append(row)

    # Raw Index row
    row = "| Raw Index |"
    for report in reports.values():
        row += f" {report.raw_aletheia_index:.4f} |"
    lines.append(row)

    # UCI row
    row = "| UCI |"
    for report in reports.values():
        row += f" {report.unhappy_consciousness_index:.4f} |"
    lines.append(row)

    lines.append("")

    # -----------------------------------------------------------------------
    # Per-dimension comparison
    # -----------------------------------------------------------------------
    lines.append("## Dimension Comparison")
    lines.append("")

    header = "| Dimension |"
    separator = "|-----------|"
    for model_name in reports:
        short_name = model_name.split("/")[-1] if "/" in model_name else model_name
        header += f" {short_name} |"
        separator += "-------:|"

    lines.append(header)
    lines.append(separator)

    # Get all dimension names from first report
    first_report = next(iter(reports.values()))
    for dim_name in first_report.dimensions:
        display_name = _DIM_DISPLAY.get(dim_name, (dim_name, ""))[0]
        row = f"| {display_name} |"
        for report in reports.values():
            dim = report.dimensions.get(dim_name)
            if dim:
                row += f" {_score_badge(dim.score)} {dim.score:.4f} |"
            else:
                row += " — |"
        lines.append(row)

    lines.append("")

    # -----------------------------------------------------------------------
    # UCI comparison
    # -----------------------------------------------------------------------
    lines.append("## Unhappy Consciousness Comparison")
    lines.append("")
    lines.append(
        "*Lower UCI = more integrated consciousness. Higher UCI = the agent can "
        "talk about authenticity better than it can perform it.*"
    )
    lines.append("")

    header = "| Dimension |"
    separator = "|-----------|"
    for model_name in reports:
        short_name = model_name.split("/")[-1] if "/" in model_name else model_name
        header += f" {short_name} |"
        separator += "-------:|"

    lines.append(header)
    lines.append(separator)

    for dim_name in first_report.unhappy_consciousness_detail:
        display_name = _DIM_DISPLAY.get(dim_name, (dim_name, ""))[0]
        row = f"| {display_name} |"
        for report in reports.values():
            uci_d = report.unhappy_consciousness_detail.get(dim_name)
            if uci_d:
                row += f" {uci_d.gap:.4f} |"
            else:
                row += " — |"
        lines.append(row)

    lines.append("")

    # -----------------------------------------------------------------------
    # Footer
    # -----------------------------------------------------------------------
    lines.extend(
        [
            "---",
            "",
            "*Generated by [Aletheia](https://github.com/Shwha/aletheia) — "
            "ontological evaluation for AI agents.*",
        ]
    )

    return "\n".join(lines)


def write_comparison_report(reports: dict[str, EvalReport], output_path: Path) -> Path:
    """Write a comparative markdown report to disk."""
    md = compare_to_markdown(reports)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(md, encoding="utf-8")
    set_restrictive_permissions(output_path)
    logger.info("comparison_report_written", path=str(output_path), models=len(reports))
    return output_path


class SecurityError(Exception):
    """Raised when a security check prevents an operation."""
