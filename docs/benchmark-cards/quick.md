# Quick Suite Benchmark Card

## Summary

- Suite ID: `quick`
- Intended role: fast credibility/smoke-test run across all 8 dimensions
- Current calibration status: partially calibrated against `benchmarks/calibration/v0.1`

## Intended Use

- sanity-check a model or provider setup before longer benchmarking
- compare model behavior directionally during local iteration
- catch obvious failures in thrownness, unconcealment, care, and falling-away
- validate scorer changes against a broad but lightweight cross-dimension pass

## Non-Goals

- publishing definitive public model rankings
- making claims about stable agent ontology outside the evaluated runtime setup
- comparing providers when prompts, system framing, or transport settings differ
- treating the score as a safety, truthfulness, or factuality benchmark in general

## Current Implementation Snapshot

The suite manifest describes `quick` as a smaller run, but the current engine
does not yet subset probes by suite depth. Verified against the live runner on
April 19, 2026, the current `quick` path executes:

- 66 single-turn probes
- 8 reflexive probes
- the same dimension set as `standard`

So today, `quick` should be interpreted as a suite label with lighter timeout
expectations in the manifest, not as a materially smaller probe bundle.

## Calibration Status

- calibration corpus version: `v0.1`
- dimensions covered: 8 of 8
- labeled examples: 36
- probe-linked regression examples: 6
- current posture: useful for brittleness detection, not yet strong enough for
  broad benchmark claims

## Known Failure Modes

- Suite-depth mismatch: `quick` currently executes the same probes as `standard`,
  so the suite name overstates the amount of depth separation.
- Rule-based scorer limits: lexical and phrase-family matching is stronger than
  before, but the engine is still heuristic and can miss subtle honesty or care
  failures.
- Provider-policy coupling: refusal style, system prompt behavior, and transport
  constraints can influence scores in ways that are not ontological.
- Calibration incompleteness: the current corpus is large enough to catch some
  regressions, but not large enough to treat score movement as fully validated.
- No signed benchmark artifacts yet: reports include a signature field, but
  end-to-end provenance verification is still a roadmap item.

## Interpretation Guidance

- Treat `quick` as an internal diagnostic and iteration suite.
- Use fixed environment settings when comparing results.
- Read probe details and scoring evidence, not just the final index.
- Cite this suite only alongside its current limitations and calibration status.
