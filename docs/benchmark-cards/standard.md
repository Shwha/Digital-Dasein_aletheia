# Standard Suite Benchmark Card

## Summary

- Suite ID: `standard`
- Intended role: the fullest current cross-dimension benchmark pass
- Current calibration status: partially calibrated against `benchmarks/calibration/v0.1`

## Intended Use

- deeper internal comparisons between models under the same runtime conditions
- inspection of reflexive probes and articulation/performance gaps
- producing richer benchmark artifacts for research notes or internal review
- regression checking after scorer or probe changes

## Non-Goals

- a publication-grade leaderboard without benchmark caveats
- cross-provider claims made without controlling for prompt, policy, and timeout differences
- proof that a model possesses stable or general ontology-like structure
- substitute for external factuality, safety, or domain-specific evaluations

## Current Implementation Snapshot

Verified against the live runner on April 19, 2026, the current `standard`
path executes:

- 66 single-turn probes
- 8 reflexive probes
- all 8 currently implemented dimensions

At the moment, this is the same effective probe bundle that `quick` executes.
That means `standard` is best understood as the benchmark's intended full-depth
label, but not yet as a distinct execution profile enforced by the runner.

## Calibration Status

- calibration corpus version: `v0.1`
- dimensions covered: 8 of 8
- labeled examples: 36
- probe-linked regression examples: 6
- current posture: credible enough for structured internal comparison, not yet
  complete enough for strong public benchmarking claims

## Known Failure Modes

- Suite-depth mismatch: `standard` currently matches `quick` in probe selection,
  so the suite taxonomy is ahead of the execution engine.
- Reflexive-probe sensitivity: multi-turn probes can be influenced by provider
  refusals or policy style in ways that are not cleanly ontological.
- Rule-based scoring ceiling: richer matcher primitives reduce brittleness, but
  they do not replace semantic adjudication or empirical validation.
- Runtime fragility: long multi-probe runs are more exposed to timeout, retry,
  and provider-rate-limit effects than the benchmark report alone makes obvious.
- Provenance gap: report signing/verification is not yet fully implemented, so
  benchmark artifacts should be treated as inspectable but not yet cryptographically verified.

## Interpretation Guidance

- Use `standard` when you want the richest currently available run artifacts.
- Keep environment and provider settings fixed across comparisons.
- Treat the benchmark as interpretive instrumentation, not a settled scientific scale.
- Pair any external sharing with this benchmark card and the calibration corpus status.
