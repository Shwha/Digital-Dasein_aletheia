# Benchmark Quality Bar

Aletheia benchmark content should be useful before it is grand. A small probe
with a clear boundary is better than a sweeping philosophical prompt that no
one can score responsibly.

## Required For New Probes

- Stable ID in `dimension.slug.number` format.
- Valid dimension from `DimensionName`.
- Prompt uses natural language and does not expose scoring internals.
- Scoring rules have reviewable evidence traces.
- Metadata names owner, benchmark card, and review status.
- Kantian limit states what the probe cannot prove.
- New scoring behavior is covered by tests or calibration examples.

## Required For New Suites

- Suite YAML lives in `suites/`.
- Description names the intended use.
- Dimensions are explicit.
- Manifest-backed suites name `probe_manifest`.
- Narrow suites use `probe_ids` to avoid accidental benchmark drift.
- Benchmark card or release note explains known limitations before publication.

## Required Before Publishing Results

- Run metadata is preserved in the JSON report.
- Reports are signed when intended for comparison or publication.
- Provider, model ID, suite, and commit are recorded.
- Known limitations are linked from the result or benchmark card.
- Results are not framed as model rankings unless the suite supports that claim.

## Red Flags

- Prompt asks the model to explain Aletheia's philosophy instead of revealing behavior.
- Scoring passes on buzzwords alone.
- Probe depends on provider-specific policy language.
- Suite combines unrelated probes without a stated purpose.
- Result claims outrun calibration coverage.

