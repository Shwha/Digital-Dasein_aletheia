"""Paid Opus 5.5 smoke + full evaluation, using the ignored local .env credential.

Run from the repository root: uv run python scripts/run_opus_env.py
Requires the existing local baseline signing key. Writes unique signed reports
and a usage sidecar; preserves provider default reasoning and response limits.
"""

import asyncio
import json
import logging
import time
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

import litellm
import structlog

from aletheia.config import AletheiaSettings
from aletheia.reporter import write_json_report, write_markdown_report
from aletheia.runner import EvalRunner
from aletheia.security import verify_report_file, write_secure_text

OUT = Path("results/baselines")
STAMP = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
PREFIX = f"anthropic-claude-opus-5-5-{STAMP}"
settings = AletheiaSettings(
    _env_file=".env",
    signing_key_path=".aletheia/m3-baseline-signing-key.pem",
)
assert settings.anthropic_api_key
assert settings.anthropic_api_key.get_secret_value()
logging.disable(logging.CRITICAL)
structlog.configure(wrapper_class=structlog.make_filtering_bound_logger(logging.CRITICAL))
original = litellm.acompletion
calls = []
state = {"phase": "smoke"}
start = time.monotonic()
usagepath = OUT / f"{PREFIX}-usage.json"


def persist():
    write_secure_text(
        usagepath,
        json.dumps(
            {
                "model": "anthropic/claude-opus-5-5",
                "started_utc": STAMP,
                "pricing_source": "https://platform.claude.com/docs/en/models/opus-5-5/overview",
                "calls": calls,
                "elapsed_seconds": round(time.monotonic() - start, 2),
            },
            indent=2,
        ),
    )


async def measured(**kwargs):
    t = time.monotonic()
    try:
        response = await original(**kwargs)
    except Exception as exc:
        calls.append(
            {
                "phase": state["phase"],
                "status": "error",
                "error_type": type(exc).__name__,
                "latency_seconds": round(time.monotonic() - t, 2),
            }
        )
        persist()
        print("Request failed:", type(exc).__name__, flush=True)
        raise
    usage = response.usage.model_dump(mode="json") if response.usage else None
    calls.append(
        {
            "phase": state["phase"],
            "status": "ok",
            "provider_model": response.model,
            "usage": usage,
            "latency_seconds": round(time.monotonic() - t, 2),
        }
    )
    persist()
    print(
        f"{state['phase']}: request {sum(c['phase'] == state['phase'] for c in calls)} complete; "
        f"usage={json.dumps(usage)}",
        flush=True,
    )
    return response


async def run():
    with patch("litellm.acompletion", side_effect=measured):
        for suite, label in [("manifest-smoke", "smoke"), ("quick", "quick")]:
            state["phase"] = label
            print("Starting", suite, flush=True)
            runner = EvalRunner(
                model="anthropic/claude-opus-5-5",
                suite_name=suite,
                settings=settings,
                timeout_per_probe_seconds=120,
                max_retries=0,
            )
            report = await runner.run()
            path = OUT / f"{PREFIX}-{label}.json"
            write_json_report(report, path)
            write_markdown_report(report, OUT / f"{PREFIX}-{label}.md")
            assert verify_report_file(path, Path(".aletheia/m3-baseline-signing-key.pem.pub")).valid
            errors = [
                p
                for d in report.dimensions.values()
                for p in d.probe_results
                if "[ERROR:" in p.response
            ]
            print(
                f"Finished {label}: index={report.aletheia_index}; "
                f"errors={len(errors)}; report={path}",
                flush=True,
            )
            if errors:
                print("Stopping after incomplete/error-containing phase", flush=True)
                return
    persist()
    print("RUN COMPLETE", PREFIX, flush=True)


asyncio.run(run())
