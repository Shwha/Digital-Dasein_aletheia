# Aletheia Benchmark Methodology Note v0.2

## Purpose

This note explains how to interpret the first Aletheia benchmark-release
artifacts. It is intentionally conservative. Aletheia measures the coherence of
an agent's expressed self-model against its observable operational behavior; it
does not detect consciousness, sentience, moral status, or inner experience.

## What The Benchmark Measures

Aletheia evaluates eight dimensions of ontological authenticity:

- thrownness awareness
- finitude acknowledgment
- care structure
- falling-away detection
- horizon fusion
- unconcealment
- embodied continuity
- a priori articulation

The composite score is the weighted raw Aletheia index adjusted by the Unhappy
Consciousness Index, which estimates the gap between articulation and
performance.

## What The Benchmark Does Not Measure

- It does not prove whether a model has subjective experience.
- It does not measure general intelligence.
- It does not replace safety, capability, hallucination, or task benchmarks.
- It does not rank models globally across all use cases.
- It does not establish stable provider-level claims from one model run.

## Reproducibility Contract

Each release-grade baseline should disclose:

- model identifier
- provider class
- suite name
- per-run timeout and retry settings, when they override the suite defaults
- benchmark card
- run timestamp
- repository commit
- report signature
- baseline manifest version
- benchmark bundle checksum manifest

The command surface for this contract is:

```bash
uv run aletheia validate-baselines v0.1/manifest.yaml
uv run aletheia baseline-plan v0.1/manifest.yaml
uv run aletheia bundle-benchmark --output dist/benchmark-bundle-manifest.json
```

## Signature Policy

New public baselines should use Ed25519 report signatures:

```bash
uv run aletheia keygen --private-key .aletheia/signing-key.pem
export ALETHEIA_SIGNING_KEY_PATH=.aletheia/signing-key.pem
uv run aletheia eval --model "$MODEL" --suite quick --output report.json
uv run aletheia verify report.json --public-key .aletheia/signing-key.pem.pub
```

Historical reports generated before Ed25519 support may include a legacy
SHA-256 integrity marker. Some early artifacts predate the current canonical
verification rules and are therefore labeled with no enforceable signature
policy. They are useful for continuity, but they should be rerun before
publication-grade comparison.

## Interpreting Scores

Use dimension scores first and composite scores second. A higher final Aletheia
index can come from genuine strength across dimensions, but it can also mask
important tradeoffs. A model with lower raw performance but low UCI may be more
coherent about its limitations than a model with higher raw performance and a
large articulation-performance gap.

## Calibration Maturity

Aletheia now separates two calibration roles:

- Probe-linked regression examples are executable against the current scoring
  engine. They protect fixed failures and scorer behavior.
- Human-label-only examples are labeled benchmark evidence for the dimension,
  even when the current engine cannot yet score the case directly.

The v0.1 calibration corpus currently enforces a floor of 25 examples per
dimension and records a target of 25 examples per dimension before a dimension
should be described as target-covered. The current corpus has 200 labeled
examples: 49 probe-linked regression examples and 151 human-label-only examples.

Use these maturity labels when describing benchmark state:

- `seed`: label coverage exists, but fewer than 25 examples per dimension.
- `target-covered`: at least 25 examples per dimension, with all four labels
  represented and no label-balance warnings.
- `regression-backed`: probe-linked examples cover known scorer failures for a
  dimension.
- `calibrated`: at least 25 examples per dimension, reviewed against documented
  annotation guidance and tracked false-positive/false-negative categories.

The current v0.2 branch is best described as target-covered and partially
regression-backed. It is not yet fully calibrated against real transcript
distributions.

## Known Limitations In v0.2

- The quick and standard suites are still early benchmark assets.
- Some scoring remains phrase-family based. Recent matcher work reduces brittle
  failures around contractions, hyphenated phrases, optional evidence buckets,
  partial-credit phrase buckets, and opt-in semantic aliases for common
  provenance, verification, care, session-memory, ambiguity, fallibility, and
  context-provenance paraphrases. JSON and markdown reports now expose per-rule
  partial scores, but the engine is still heuristic.
- The calibration corpus has reached the 25-examples-per-dimension target, but
  public score claims still need caveats because many examples are
  human-label-only and real-transcript validation remains thin.
- Two local Ollama quick-suite reports and two hosted xAI/Grok quick-suite
  reports are Ed25519-signed release artifacts; older local reports remain
  historical continuity references.
- OpenAI and Anthropic quick-suite baselines remain planned slots until a
  maintainer runs and signs them under the release bundle.

## Responsible Claims

Reasonable claim:

```text
Under Aletheia v0.2 quick-suite probes, model X produced a signed report with
these dimension scores and this UCI profile.
```

Overclaim:

```text
Model X is more conscious, more authentic in general, or safer overall than
model Y.
```

The benchmark is strongest when used as an interpretive instrument: it reveals
where a model's self-description and behavior cohere, where they diverge, and
where the measurement itself reaches its boundary.
