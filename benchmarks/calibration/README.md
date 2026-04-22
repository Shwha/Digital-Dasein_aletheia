# Calibration Corpus

This directory holds the versioned calibration corpus for Aletheia.

The goal is simple: scoring changes should be checked against labeled examples
 before they are treated as benchmark improvements. The corpus is intentionally
 inspectable and repository-native so contributors can review, diff, and extend
 it without specialized tooling.

## Layout

```text
benchmarks/calibration/
├── annotation-guide.md
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
aletheia validate-calibration
```

That command validates the registry and manifest, checks label coverage per
dimension, and summarizes probe-linked regression examples that can run against
the current engine.

The current maturity target is 25 labeled examples per dimension. The manifest
also carries a lower enforced floor so incremental corpus growth can be checked
in without pretending the benchmark is fully calibrated.

Current `v0.1` coverage:

- enforced floor: 20 examples per dimension
- target: 25 examples per dimension
- total labeled examples: 160
- probe-linked regression examples: 33
- human-label-only examples: 127

Probe-linked examples protect current scoring behavior. Human-label-only
examples preserve broader annotation evidence for cases that the current engine
cannot yet score faithfully.

## Contribution Notes

- Add new examples to the latest version unless you are preserving an older
  release for reproducibility.
- Use `fixed_failure` only when the example is tied to a concrete engine
  failure or regression and includes a `probe_id` plus score bound.
- Keep rationales short and explicit enough that another contributor can audit
  the label without guessing at intent.
