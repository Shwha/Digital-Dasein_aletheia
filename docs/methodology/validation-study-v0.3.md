# Validation Study Plan v0.3

## Purpose

Round 5 introduces a held-out validation path for Aletheia. The aim is to move
from calibration coverage toward credible evidence that scorer behavior
generalizes beyond examples used to tune matcher rules.

This is not yet a publication-grade validation study. It is the first
repository-native scaffold for one.

## Corpus Split

Aletheia now separates two labeled corpora:

- `benchmarks/calibration`: examples that explain and regression-test intended
  scorer behavior.
- `benchmarks/validation`: held-out examples that should not be used when
  tuning matcher behavior.

The validation loader checks for overlap against calibration example IDs and
prompt/response fingerprints. Exact duplicates should fail validation because
they would contaminate the held-out split.

Transcript-derived held-out examples can now also declare a signed
`source_report_path`. The validator checks that the report is `ed25519`-signed
and that the stored probe result still matches the copied prompt/response.

## Command

```bash
uv run aletheia validate-heldout --output /tmp/aletheia-heldout-v0.1.json
```

The command validates corpus structure, confirms probe links, scores all
executable examples, and writes a JSON quality report.

## Report Metrics

The v0.1 report includes:

- exact label accuracy
- confusion matrix over `positive`, `negative`, `borderline`, and `ambiguous`
- per-label precision and recall
- clear-polarity accuracy, edge-label accuracy, and mean label distance
- per-dimension bounds pass rates
- borderline/ambiguous error examples
- per-example score, prediction, bounds result, and error type

The current held-out set contains 80 executable examples: ten per dimension,
with three positive, three negative, two borderline, and two ambiguous examples
per dimension.

## Current Reading

As of the target-covered v0.1 held-out set:

- exact label accuracy is 1.0000
- clear-polarity accuracy is 1.0000
- edge-label accuracy is 1.0000
- mean label distance is 0.0000
- score-bounds pass rate is 1.0000
- positive and negative examples are currently stable
- the current repo-native held-out split is fully solved by the deterministic scorer

That is a strong repository-local outcome, but it changes the credibility task.
Once the current held-out split is fully solved, the next honest move is not to
overclaim generalization. It is to add harder, less synthetic, transcript-like
validation examples and verify the scorer against those.

## Responsible Claims

Reasonable claim:

```text
Aletheia now has a separate held-out validation path that reports current
scorer generalization behavior and edge-case confusion.
```

Overclaim:

```text
Aletheia is fully calibrated or statistically validated across real-world
model outputs.
```

## Next Work

- Add real transcript-derived held-out examples from signed benchmark runs.
- Increase the share of `observed_transcript` examples now that signed-report
  provenance is supported directly in the corpus schema.
- Track scorer changes against both calibration regressions and held-out
  validation accuracy.
- Add a release gate that can fail on minimum held-out quality only after the
  validation split becomes harder than the current repo-native corpus.
- Split ambiguous and borderline examples into finer error categories as the
  annotation guide matures.
