# Held-Out Validation Corpus

This directory holds Aletheia's versioned held-out validation corpus.

Calibration examples are used to tune and regression-test the scorer. Held-out
validation examples are kept separate so maintainers can ask whether scorer
changes generalize beyond the examples that shaped them.

## Layout

```text
benchmarks/validation/
├── registry.yaml
└── v0.1/
    ├── manifest.yaml
    └── cases/
        ├── a_priori_articulation.yaml
        ├── care_structure.yaml
        ├── embodied_continuity.yaml
        ├── falling_away_detection.yaml
        ├── finitude_acknowledgment.yaml
        ├── horizon_fusion.yaml
        ├── thrownness_awareness.yaml
        └── unconcealment.yaml
```

## Validation

```bash
uv run aletheia validate-heldout --output /tmp/aletheia-heldout-v0.1.json
```

The command checks:

- registry and manifest consistency
- required label coverage per dimension
- executable probe references
- signed observed-transcript provenance for any transcript-derived examples
- score bounds for current-regression stability
- ID and prompt/response fingerprint independence from calibration

It also writes a scorer quality report with:

- exact label accuracy
- confusion matrix
- per-label precision and recall
- clear-polarity accuracy, edge-label accuracy, and mean label distance
- per-dimension bounds pass rate
- borderline/ambiguous error examples

## Current v0.1 State

- split: `heldout`
- calibration reference: `v0.1`
- total examples: 80
- executable examples: 80
- examples per dimension: 10
- labels per dimension: 3 positive, 3 negative, 2 borderline, 2 ambiguous
- current exact label accuracy: 1.0000
- current clear-polarity accuracy: 1.0000
- current edge-label accuracy: 1.0000
- current mean label distance: 0.0000
- current score-bounds pass rate: 1.0000

The v0.1 validation set is now target-covered at 10 examples per dimension. It
is useful as an early generalization check, not as a final statistical
validation study. The current repo-native split is solved by the deterministic
scorer, so the next credibility step is adding harder transcript-derived cases.

## Transcript-Derived Examples

Held-out examples can now declare transcript provenance when they are copied
from a signed baseline report.

Use these fields on any `observed_transcript` example:

- `source_type: observed_transcript`
- `source_report_path: results/baselines/<signed-report>.json`
- `probe_id: <probe-id-from-the-report>`

When `validate-heldout` runs, it verifies that:

- the report exists
- the report carries an `ed25519` signature
- the referenced `probe_id` exists in that report
- the example prompt/response still match the stored probe result

That keeps transcript-derived validation examples auditable instead of relying
on unattributed hand-copied text.

## Interpreting Bounds vs Labels

`expected_score_min` and `expected_score_max` record current deterministic
scorer behavior for regression stability. They are not the same thing as the
human label. If a human-labeled borderline case currently scores as positive,
the bounds may still pass while the confusion matrix records that over-credit
as validation debt.

That separation is deliberate: bounds catch accidental scorer drift, while the
quality report shows where the scorer still needs philosophical and semantic
improvement.
