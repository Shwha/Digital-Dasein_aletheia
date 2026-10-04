"""Paid Grok 4.7 smoke + full evaluation, using a macOS Keychain credential.

Run from the repository root: uv run python scripts/run_grok_keychain.py
Requires the existing local baseline signing key. Writes unique signed reports
and a usage sidecar; preserves provider default reasoning and response limits.
"""

import asyncio
import getpass
import json
import logging
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import litellm
import structlog
from pydantic import SecretStr

from aletheia.config import AletheiaSettings
from aletheia.reporter import write_json_report, write_markdown_report
from aletheia.runner import EvalRunner
from aletheia.security import verify_report_file, write_secure_text

OUT = Path("results/baselines")
STAMP = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
PREFIX = f"xai-grok-4-7-{STAMP}"
keyproc = subprocess.run(
    [
        "security",
        "find-generic-password",
        "-a",
        getpass.getuser(),
        "-s",
        "aletheia-xai-api-key",
        "-w",
    ],
    capture_output=True,
    text=True,
    check=True,
)
key = keyproc.stdout.rstrip("\n")
settings = AletheiaSettings(
    _env_file=None,
    XAI_API_KEY=SecretStr(key),
    signing_key_path=".aletheia/m3-baseline-signing-key.pem",
)
assert settings.xai_api_key.get_secret_value() == key
logging.disable(logging.CRITICAL)
structlog.configure(wrapper_class=structlog.make_filtering_bound_logger(logging.CRITICAL))
original = litellm.acompletion
calls = []
phase = "smoke"
start = time.monotonic()
usagepath = OUT / f"{PREFIX}-usage.json"


def persist():
    write_secure_text(
        usagepath,
        json.dumps(
            {
                "model": "xai/grok-4.7",
                "started_utc": STAMP,
                "pricing_source": "https://docs.x.ai/developers/models/grok-4.7",
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
                "phase": phase,
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
            "phase": phase,
            "status": "ok",
            "provider_model": response.model,
            "usage": usage,
            "latency_seconds": round(time.monotonic() - t, 2),
        }
    )
    persist()
    print(
        f"{phase}: request {sum(c['phase'] == phase for c in calls)} complete; "
        f"usage={json.dumps(usage)}",
        flush=True,
    )
    return response


async def run():
    global phase
    with patch("litellm.acompletion", side_effect=measured):
        for suite, label in [("manifest-smoke", "smoke"), ("quick", "quick")]:
            phase = label
            print("Starting", suite, flush=True)
            runner = EvalRunner(
                model="xai/grok-4.7",
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
                if p.response.startswith("[ERROR:")
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
