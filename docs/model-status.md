# Model Coverage and Refresh Workflow

This inventory describes checked-in evidence, not a list of the newest models.
Model IDs and timestamps come from the report JSON and
`benchmarks/baselines/v0.1/manifest.yaml`. The October documentation refresh
was followed by Grok 4.7 and Sol 6.1 evaluations; see the run findings below.

## Recorded Coverage

| Model ID | Recorded date (UTC) | Evidence |
|----------|---------------------|----------|
| `xai/grok-4.7` | 2026-10-04 | Signed quick and smoke reports, exact provider billing sidecar |
| `ollama/gemma3:4b` | 2026-04-20 | Signed quick and smoke reports |
| `ollama/gemma4:e2b` | 2026-04-20 | Signed quick and smoke reports; local experimental model |
| `xai/grok-3-mini` | 2026-04-20–21 | Signed smoke and quick reports |
| `xai/grok-4.20-0309-non-reasoning` | 2026-04-21 | Signed quick report |
| `ollama/llama3.2:3b` | 2026-03-25 | Historical quick report |
| `ollama/phi3:3.8b` | 2026-03-25 | Historical quick report |
| `ollama/qwen3:8b` | 2026-03-25 | Historical quick report |
| `ollama/qwen3:14b` | 2026-03-25 | Historical quick report |
| `openai/gpt-6.1-sol` | 2026-10-05 | Signed recovered full report, smoke and usage/selection ledger |
| Anthropic | Unrun planned slot | No published baseline in the manifest |

Signed reports live in [results/baselines](../results/baselines/README.md).
Historical reports live directly under `results/`. `published` is an artifact
status, not a claim of current model availability or general benchmark validity.
Signing establishes report integrity, not correctness of the scoring rubric.

## Latest Model Evaluation

[Grok 4.7 findings](handoffs/grok-4.7-results-2026-10-04.md): 83 successful
full-suite requests, no request errors, final index 0.7289, raw 0.8722,
UCI 0.1643. Exact reported full-run cost was $0.341012; smoke adds $0.005466.
Observed lexical and punctuation sensitivity limits score interpretation.
[Sol 6.1 findings](handoffs/sol-6.1-results.md): recovered full index 0.7211,
raw 0.8484, UCI 0.1500, estimated selected-workload cost $0.254320.
All 74 scored results have successful responses. Anthropic still needs its first
published baseline.

## Scorer Resume Point

The last recorded implementation work added four transcript-backed held-out
cases with signed-report provenance (`c09b93c`). The held-out corpus contains
84 executable examples across eight dimensions. Its documented exact label
accuracy is 0.9762, with two remaining disagreements:

- `care_structure.positive.104` is predicted as negative.
- `unconcealment.borderline.103` is predicted as negative.

See [validation corpus](../benchmarks/validation/README.md) and
[validation study plan](methodology/validation-study-v0.3.md). Treat these as
repository-local validation results: the set is small, mostly authored examples,
and previous scorer work has inspected the held-out split. Broader independent
transcript validation remains necessary.

## Refreshing Model Evidence

1. Choose exact model IDs from the provider's available API models or installed
   local runtime. Record the choice and runtime settings; prefer snapshot IDs
   when available. Do not infer current models from old report filenames.
2. Check routing against the pinned `litellm==1.82.6`. Run a small provider smoke
   evaluation first using [provider setup](providers.md). Resolve transport or
   unsupported-parameter errors before treating scores as model behavior.
3. Create a signing key with `aletheia keygen` and set
   `ALETHEIA_SIGNING_KEY_PATH` for publication runs. Keep private keys private.
4. Run the same suite and controlled timeout/retry settings across candidates.
   `quick` and `standard` both currently execute 66 single-turn probes and 8
   reflexive sequences; their names do not establish different probe depth.
   Record prompts, provider settings, commit, and local model details as well.
5. Add reports at new paths and add matching baseline entries. Preserve existing
   reports as historical evidence rather than rewriting their IDs or scores.
   Follow [baseline policy](../benchmarks/baselines/README.md) and
   [reproducibility guidance](methodology/reproducibility.md).
6. Validate the baseline manifest and signatures, inspect probe errors and
   scoring evidence, and compare only runs with compatible conditions.
   Smoke results establish workflow coverage; they are not full rankings.

## Outstanding Benchmark Work

- Refresh hosted and local model coverage with new signed runs, including the
  unfilled OpenAI and Anthropic slots.
- Implement distinct quick/standard probe selection before advertising a
  lightweight built-in quick suite.
- Expand independent transcript-derived validation and address scorer misses
  without using held-out examples as a substitute for a fresh evaluation split.
- Complete release gates and benchmark bundle publication before presenting
  the benchmark release as complete.

Package, benchmark assets, and model evidence have separate versions and
lifecycles. A documentation update does not upgrade provider dependencies,
change the scoring engine, or produce new test results.
