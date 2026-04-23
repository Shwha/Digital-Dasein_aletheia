# Benchmark Cards

Benchmark cards are the user-facing specification for Aletheia suite behavior.

They exist to answer a practical question before someone runs or cites a suite:
what is this benchmark for, what is it *not* for, how calibrated is it, and
what known limitations should change how I interpret the scores?

## Current Cards

- [Quick Suite](./quick.md)
- [Standard Suite](./standard.md)

## Current Calibration Snapshot

As of calibration corpus `v0.1`:

- all 8 current dimensions have labeled examples
- the corpus contains 160 examples total
- 33 examples are probe-linked regression checks against live scoring behavior
- 127 examples are human-label-only calibration evidence for future scoring work
- the current enforced floor is 20 examples per dimension, with a target of 25

This is enough to catch some high-value brittleness, but not enough to treat
the benchmark as fully calibrated across providers, prompts, or deployment
contexts.
