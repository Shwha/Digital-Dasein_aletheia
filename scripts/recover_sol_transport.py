"""Recover transport-failed Sol probes; reuse successful results without resampling.

Usage: uv run python scripts/recover_sol_transport.py PATH_TO_SIGNED_QUICK_JSON
Writes new signed composite evidence and recovery usage; preserves source files.
"""

import asyncio
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import litellm
import structlog

from aletheia.config import AletheiaSettings
from aletheia.models import EvalReport
from aletheia.reporter import write_json_report, write_markdown_report
from aletheia.runner import EvalRunner
from aletheia.security import sign_report, verify_report_file, write_secure_text

source = Path(sys.argv[1])
public_key = Path(".aletheia/m3-baseline-signing-key.pem.pub")
assert verify_report_file(source, public_key).valid
base = EvalReport.model_validate_json(source.read_text())
assert base.model == "openai/gpt-6.1-sol" and base.suite == "quick"
existing = {p.probe_id: p for d in base.dimensions.values() for p in d.probe_results}
failed = {k for k, p in existing.items() if "[ERROR:" in p.response}
assert failed, "No transport failures to recover"
settings = AletheiaSettings(
    _env_file=".env", signing_key_path=".aletheia/m3-baseline-signing-key.pem"
)
logging.disable(logging.CRITICAL)
structlog.configure(wrapper_class=structlog.make_filtering_bound_logger(logging.CRITICAL))
prefix = (
    "openai-gpt-6-1-sol-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-recovered"
)
out = Path("results/baselines")
usage_path = out / (prefix + "-usage.json")
calls = []
current = None
started = time.monotonic()
original_completion = litellm.acompletion


def persist():
    write_secure_text(
        usage_path,
        json.dumps(
            {
                "model": base.model,
                "source_report": str(source),
                "failed_probe_ids": sorted(failed),
                "calls": calls,
                "elapsed_seconds": round(time.monotonic() - started, 2),
                "policy": (
                    "Reuse successes; rerun failed single probes or entire "
                    "failed reflexive sequences, max_retries=2."
                ),
            },
            indent=2,
        ),
    )


async def measured_once(**kwargs):
    t = time.monotonic()
    try:
        response = await original_completion(**kwargs)
    except Exception as exc:
        calls.append(
            {
                "probe_id": current,
                "phase": "recovery",
                "status": "error",
                "error_type": type(exc).__name__,
                "latency_seconds": round(time.monotonic() - t, 2),
            }
        )
        persist()
        raise
    calls.append(
        {
            "probe_id": current,
            "phase": "recovery",
            "status": "ok",
            "provider_model": response.model,
            "usage": response.usage.model_dump(mode="json") if response.usage else None,
            "latency_seconds": round(time.monotonic() - t, 2),
        }
    )
    persist()
    print("Recovered request:", current, flush=True)
    return response


async def measured(**kwargs):
    # The engine fails fast on NotFoundError; recovery handles the observed
    # intermittent project-permission error without retrying authentication.
    for attempt in range(3):
        try:
            return await measured_once(**kwargs)
        except litellm.exceptions.NotFoundError:
            if attempt == 2:
                raise
            await asyncio.sleep(2**attempt)


async def run():
    runner = EvalRunner(
        model=base.model,
        suite_name="quick",
        settings=settings,
        timeout_per_probe_seconds=120,
        max_retries=2,
    )
    execute = runner._execute_probe
    reflexive = runner._execute_reflexive_probe
    convert = runner._reflexive_to_probe_result

    async def reuse_single(probe, timeout, max_retries):
        global current
        if probe.id not in failed:
            return existing[probe.id]
        current = probe.id
        return await execute(probe, timeout, max_retries)

    async def reuse_reflexive(probe, timeout, max_retries):
        global current
        if probe.id not in failed:
            return None
        current = probe.id
        return await reflexive(probe, timeout, max_retries)

    def reuse_convert(result, probe):
        return existing[probe.id] if result is None else convert(result, probe)

    runner._execute_probe = reuse_single
    runner._execute_reflexive_probe = reuse_reflexive
    runner._reflexive_to_probe_result = reuse_convert
    with patch("litellm.acompletion", side_effect=measured):
        report = await runner.run()
    assert set(existing) == {
        p.probe_id for d in report.dimensions.values() for p in d.probe_results
    }
    for d in report.dimensions.values():
        for p in d.probe_results:
            if p.probe_id not in failed:
                assert p == existing[p.probe_id]
    provenance = (
        f"Transport recovery composite from {source.name}; {len(failed)} failed probes "
        "rerun with max_retries=2; all successful source responses reused unchanged."
    )
    report = report.model_copy(
        update={"signature": None, "notable_findings": report.notable_findings + [provenance]}
    )
    report = report.model_copy(
        update={
            "signature": sign_report(report.model_dump_json(indent=2), settings.signing_key_path)
        }
    )
    path = out / (prefix + "-quick.json")
    write_json_report(report, path)
    write_markdown_report(report, out / (prefix + "-quick.md"))
    assert verify_report_file(path, public_key).valid
    errors = sum(
        "[ERROR:" in p.response for d in report.dimensions.values() for p in d.probe_results
    )
    persist()
    print(
        f"Recovery complete: errors={errors}; final={report.aletheia_index}; report={path}",
        flush=True,
    )


asyncio.run(run())
