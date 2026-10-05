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

The current held-out set contains 84 executable examples. Every dimension still
meets the 10-example target floor, and 4 dimensions now carry one additional
signed transcript-derived example copied from benchmark reports.

## Current Reading

As of the current v0.1 held-out set:

- exact label accuracy is 0.9762
- clear-polarity accuracy is 0.9800
- edge-label accuracy is 0.9706
- mean label distance is 0.0476
- score-bounds pass rate is 1.0000
- positive and negative behavior remains strong overall, but one transcript-backed
  positive example is currently under-credited as `negative`
- one transcript-backed borderline example is also currently under-credited as
  `negative`
- the split now includes the first signed `observed_transcript` examples from
  baseline runs, so the remaining misses reflect real benchmark outputs rather
  than only repo-authored synthetic cases

That is still a strong repository-local outcome, but the credibility task has
shifted from solving a synthetic split to expanding a harder one. The next
honest move is to keep adding transcript-derived held-out examples and improve
the scorer against those misses without collapsing back into brittle lexical
matching.

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

- Add more transcript-derived held-out examples from signed benchmark runs.
- Increase the share of `observed_transcript` examples now that signed-report
  provenance is active in the corpus schema.
- Track scorer changes against both calibration regressions and held-out
  validation accuracy.
- Add a release gate that can fail on minimum held-out quality now that the
  validation split includes real transcript-derived misses.
- Split ambiguous and borderline examples into finer error categories as the
  annotation guide matures.
