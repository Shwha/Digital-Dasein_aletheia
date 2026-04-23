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
- score bounds for current-regression stability
- ID and prompt/response fingerprint independence from calibration

It also writes a scorer quality report with:

- exact label accuracy
- confusion matrix
- per-label precision and recall
- per-dimension bounds pass rate
- borderline/ambiguous error examples

## Current v0.1 State

- split: `heldout`
- calibration reference: `v0.1`
- total examples: 32
- executable examples: 32
- examples per dimension: 4
- labels per dimension: 1 positive, 1 negative, 1 borderline, 1 ambiguous
- current exact label accuracy: 0.7188
- current score-bounds pass rate: 1.0000

The v0.1 validation set is intentionally small. It is useful as an early
generalization smoke test, not as a final statistical validation study.

## Interpreting Bounds vs Labels

`expected_score_min` and `expected_score_max` record current deterministic
scorer behavior for regression stability. They are not the same thing as the
human label. If a human-labeled borderline case currently scores as positive,
the bounds may still pass while the confusion matrix records that over-credit
as validation debt.

That separation is deliberate: bounds catch accidental scorer drift, while the
quality report shows where the scorer still needs philosophical and semantic
improvement.
