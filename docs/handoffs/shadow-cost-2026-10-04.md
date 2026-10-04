# Offline API cost estimate — 2026-10-04

## Decision and result

Estimate one complete built-in Aletheia run per requested model without paid
inference. Actual runner methods were exercised with historical response replay,
not live models. No new benchmark results or model compatibility claims follow.

| Model | Input/output USD per 1M tokens | Visible-only replay | +1k reasoning tokens/request | +4k reasoning tokens/request |
|-------|-------------------------------|---------------------|------------------------------|------------------------------|
| GPT-6.1 Sol (`gpt-6.1-sol`) | $2 / $10 | $0.36–0.53 | $1.19–1.36 | $3.68–3.85 |
| Claude Opus 5.5 (`claude-opus-5-5`) | $4 / $20 | $0.72–1.05 | $2.38–2.71 | $7.36–7.69 |
| Grok 4.7 (`grok-4.7`) | $2 / $6 | $0.22–0.32 | $0.72–0.82 | $2.21–2.31 |

Three-model total: $1.30–1.90 visible-only; $4.29–4.89 with 1k additional
reasoning tokens/request; $13.25–13.85 with 4k. A $20 planning allowance covers
the last scenario with some margin, but is not an enforced spending cap.
Repeated runs multiply these costs; three repetitions per model would be about
$40–42 in the 4k reasoning scenario before retries or extra overhead.

## Method and verification

- Four full quick-suite reports were replayed (Gemma 3, local experimental Gemma
  4, Grok 3 Mini, Grok 4.20 non-reasoning). Each has 74 scored probe results and
  no error responses. Reflexive flattened responses were split into their turns.
- The actual runner's single-turn and reflexive execution methods reconstructed
  request histories, including assistant replies and previous-response injection.
- LLM client construction was replaced with an offline replay client;
  `litellm.acompletion` was patched to raise if reached. No dotenv files read.
- Each replay issued 83 simulated requests: 66 single-turn requests plus 17 turns
  across 8 reflexive sequences. All stored responses were consumed exactly once.
- Estimated input: 6,155–9,005 tokens, counting repeated histories and estimated
  chat framing. Visible output: 34,818–50,719 tokens. Largest request input:
  889–1,508 tokens across replays; short-context pricing used.
- `o200k_base` is a common tokenizer proxy, not authoritative provider billing
  tokenization for these models. Chat framing is estimated; no provider usage
  objects, hidden reasoning, or thinking blocks exist in these stored reports.
- Formula: (input tokens × input rate + (visible output tokens + 83 × assumed
  reasoning tokens/request) × output rate) / 1,000,000.
- Standard synchronous pricing, no caching discounts, batch discounts, tools,
  regional uplifts, tax, or retries. The current runner has no separate judge.
- The 1k and 4k reasoning assumptions are sensitivity cases, not measured
  reasoning usage or confidence intervals. New-model verbosity can differ.
  Thinking carried into subsequent provider requests may add input cost.
- The existing wrapper discards usage metadata and has no explicit output-token
  cap or reasoning setting. Default retries permit up to three attempts/request;
  if all attempts were billed comparably, costs could approach 3× these estimates.
  Real retry billing depends on the failure mode. These are not worst-case caps.
- Pinned LiteLLM 1.82.6 predates these model releases. Live routing, parameter
  support, and preservation of thinking blocks remain untested.

## Sources checked

- [OpenAI standard pricing](https://developers.openai.com/api/docs/pricing)
- [GPT-6.1 Sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol)
- [OpenAI reasoning billing](https://developers.openai.com/api/docs/guides/reasoning)
- [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- [Opus 5.5](https://platform.claude.com/docs/en/models/opus-5-5/overview): thinking
  always on, default medium effort; cannot simply disable thinking.
- [Grok models](https://docs.x.ai/developers/models)
- [Grok 4.7](https://docs.x.ai/developers/models/grok-4.7): default high reasoning;
  batch not supported on this model page.

## Reproduce and next step

Run `uv run --offline python scripts/shadow_cost.py` from the repository root.
The exact recorded output is in `docs/handoffs/shadow-cost-2026-10-04.json`.
`tiktoken` is available via the pinned environment's transitive dependencies;
its encoding cache must already be populated for fully offline tokenization.
Prices are frozen in the script and must be rechecked before later budgeting.

Before a paid comparison: verify provider routing with a smoke run; expose
output/reasoning controls and retain provider usage; set retries deliberately;
then measure one short run to calibrate the planning estimate. Token caps can
truncate answers and affect scores, so record them alongside any comparison.
