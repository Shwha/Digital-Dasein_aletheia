"""Offline request replay for cost sizing; never generates a benchmark report.

Run: uv run --offline python scripts/shadow_cost.py > /tmp/shadow-cost.json
Prices are a documentation snapshot, not a live pricing feed.
"""
# ruff: noqa: SLF001 — offline replay deliberately exercises runner internals.

import asyncio
import contextlib
import io
import json
import re
from pathlib import Path
from unittest.mock import patch

import tiktoken

from aletheia.config import AletheiaSettings, load_suite
from aletheia.runner import EvalRunner

ROOT = Path(__file__).resolve().parents[1]
ENC = tiktoken.get_encoding("o200k_base")
RATES = {
    "gpt-6.1-sol": (2, 10),
    "claude-opus-5-5": (4, 20),
    "grok-4.7": (2, 6),
}


def tokens(text):
    return len(ENC.encode(text, disallowed_special=()))


def message_tokens(messages):
    # Common tokenizer proxy plus explicit estimated chat framing.
    return 3 + sum(tokens(m["content"]) + tokens(m["role"]) + 3 for m in messages)


class ReplayClient:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.inputs = []
        self.outputs = []
        self.max_input = 0

    async def complete(self, model, prompt, system_prompt=None, **_kwargs):
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return await self.complete_conversation(model, messages)

    async def complete_conversation(self, model, messages, **_kwargs):
        del model  # Routing is irrelevant to offline response replay.
        response = next(self.responses)
        count = message_tokens(messages)
        self.inputs.append(count)
        self.outputs.append(tokens(response))
        self.max_input = max(self.max_input, count)
        return response, 0.0


async def replay(path):
    report = json.loads(path.read_text())
    results = {p["probe_id"]: p for d in report["dimensions"].values() for p in d["probe_results"]}
    assert not any(p["response"].startswith("[ERROR:") for p in results.values())
    # Patch construction: no real LLM client, no API keys, no dotenv reads.
    with patch("aletheia.runner.LLMClient", return_value=None):
        runner = EvalRunner("offline-shadow", settings=AletheiaSettings(_env_file=None))
    probes, reflexive = runner._gather_suite_probes(load_suite("quick", ROOT / "suites"))
    answers = []
    for items in probes.values():
        answers.extend(results[p.id]["response"] for p in items)
    for items in reflexive.values():
        for p in items:
            turns = re.split(r"(?:^|\n---\n)\[Turn \d+\] ", results[p.id]["response"])[1:]
            assert len(turns) == len(p.turns), p.id
            answers.extend(turns)
    client = ReplayClient(answers)
    runner._llm = client
    for items in probes.values():
        for p in items:
            await runner._execute_probe(p, 30, 0)
    for items in reflexive.values():
        for p in items:
            await runner._execute_reflexive_probe(p, 30, 0)
    expected = sum(map(len, probes.values())) + sum(
        len(p.turns) for ps in reflexive.values() for p in ps
    )
    assert len(client.inputs) == expected
    assert next(client.responses, None) is None
    return {
        "source": str(path.relative_to(ROOT)),
        "source_model": report["model"],
        "calls": expected,
        "single_turn": sum(map(len, probes.values())),
        "reflexive_sequences": sum(map(len, reflexive.values())),
        "input_tokens_proxy": sum(client.inputs),
        "visible_output_tokens_proxy": sum(client.outputs),
        "max_request_input_tokens_proxy": client.max_input,
    }


async def main():
    rows = []

    # Fail closed if any future code accidentally reaches the real completion API.
    async def forbidden(*_args, **_kwargs):
        raise AssertionError("Live completion forbidden during offline shadow replay")

    with (
        patch("litellm.acompletion", side_effect=forbidden),
        contextlib.redirect_stdout(io.StringIO()),
    ):
        snapshot = json.loads((ROOT / "docs/handoffs/shadow-cost-2026-10-04.json").read_text())
        rows.extend([await replay(ROOT / row["source"]) for row in snapshot["replays"]])
    scenarios = {}
    for name, (inp, out) in RATES.items():
        scenarios[name] = {}
        for reason in (0, 1000, 4000):
            costs = [
                (
                    r["input_tokens_proxy"] * inp
                    + (r["visible_output_tokens_proxy"] + r["calls"] * reason) * out
                )
                / 1e6
                for r in rows
            ]
            scenarios[name][str(reason)] = {
                "min_usd": round(min(costs), 4),
                "max_usd": round(max(costs), 4),
            }
    print(
        json.dumps(
            {
                "pricing_checked": "2026-10-04",
                "tokenizer_proxy": "o200k_base",
                "rates_usd_per_million_input_output": RATES,
                "replays": rows,
                "scenarios_additional_billed_reasoning_tokens_per_call": scenarios,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
