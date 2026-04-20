# Aletheia Phase 2 Implementation Plan

## Purpose

This document turns the broader future-work roadmap into an execution-ready plan.
It is intentionally narrower than `docs/FUTURE-WORK-SPEC.md`: the spec explains
where Aletheia should go, while this plan defines what to build next, in what
order, and how to break the work into contributor-friendly issues.

## Planning Goals

This plan is optimized for four outcomes:

1. Increase benchmark credibility quickly.
2. Reduce scoring brittleness in the current engine.
3. Make the project easier for outside contributors to extend safely.
4. Publish enough benchmark structure and artifacts that Aletheia starts to feel
   like a real platform rather than a single promising repository.

## Milestones

### Milestone 1: Credibility Release

Focus:

- benchmark calibration corpus
- scoring regression coverage
- richer matcher primitives
- signed, inspectable run metadata

Definition of done:

- at least one labeled calibration set exists for each current dimension
- scoring failure modes are documented and regression-tested
- report signing and verification are no longer stubs
- benchmark documentation includes known limitations

### Milestone 2: Contributor Release

Focus:

- externalized probe and suite assets
- contributor workflows
- release/versioning discipline
- example provider setups and benchmark cards

Implementation status: complete on the Milestone 2 contributor-release branch.

Definition of done:

- new probes can be added without editing engine internals
- contributors have templates and docs for dimensions, probes, and rubrics
- releases and migrations are documented

### Milestone 3: Benchmark Release

Focus:

- reproducible baseline runs
- comparison harness polish
- benchmark bundle publication
- methodology note / whitepaper draft

Definition of done:

- published baselines can be rerun
- benchmark artifacts are signed and versioned
- outside users can interpret results with sufficient context

## Prioritized Backlog

Priority is expressed as `P0`, `P1`, and `P2`.

- `P0`: unlocks project credibility or prevents misleading benchmark claims
- `P1`: materially improves contributor value and long-term maintainability
- `P2`: important follow-on work after the foundation is stable

## Issue Map

### P0

1. Build a labeled calibration corpus for the eight current dimensions.
   Why first: without labeled examples, improvements to scoring are hard to
   evaluate and easy to overclaim.

2. Add richer matcher primitives for rule-based scoring.
   Why next: this directly addresses the most visible false positives and
   increases trust in current reports.

3. Add benchmark cards and known-failure documentation for current suites.
   Why next: users need to understand what Aletheia can and cannot claim today.

4. Implement Ed25519 report signing and verification.
   Why next: this turns provenance and report trust from aspiration into feature.

### P1

5. Externalize probe and suite manifests into versioned assets.
   Why: this separates benchmark content from engine code and lowers the barrier
   to contribution.

6. Add contributor templates and extension guides for probes, dimensions, and rubrics.
   Why: open-source growth depends on clear contribution paths.

7. Add example provider configurations and reproducible local workflows.
   Why: outside users need fast paths for OpenAI, Anthropic, and Ollama runs.

### P2

8. Publish baseline comparison runs for representative models.
   Why: benchmark artifacts make the project feel real and test reproducibility.

9. Draft a methodology note or whitepaper describing the benchmark design.
   Why: this creates a citeable artifact and clarifies epistemic boundaries.

## Suggested Execution Order

### Track A: Credibility

1. calibration corpus
2. richer scoring primitives
3. benchmark cards
4. provenance/signing

### Track B: Open-Source Readiness

1. probe/suite manifests
2. contributor templates
3. provider examples

### Track C: Publication

1. baseline reports
2. methodology note

Tracks A and B can run partly in parallel, but Track A should lead. Aletheia
needs stronger benchmark legitimacy before it asks the community to take the
scores too seriously.

## Acceptance Criteria By Work Item

### Calibration Corpus

- create a `benchmarks/calibration/` directory with versioned fixtures
- document annotation guidance per dimension
- include positive, negative, borderline, and ambiguous examples
- add regression tests derived from at least the first ten fixed failures

### Richer Matcher Primitives

- add synonym/phrase-family matching support
- support contradiction-aware patterns where useful
- preserve evidence traces in scoring output
- demonstrate reduced false positives on the calibration corpus

### Benchmark Cards

- one card per suite
- include intended use, non-goals, known failure modes, and calibration status
- link benchmark cards from README

### Signing And Verification

- implement Ed25519 signing
- add a `verify` CLI command
- include signature/provenance validation docs
- test tamper detection end to end

Implementation status: complete on `main`.

### Probe / Suite Manifest Externalization

- define a schema for probe and suite assets
- support loading versioned manifests from disk
- preserve stable IDs and metadata in reports
- document migration path from Python-defined probes

Implementation status: complete on the Milestone 2 contributor-release branch.

### Contributor Templates

- add templates for new probe sets and new dimensions
- document review expectations and benchmark quality bar
- add PR checklist for benchmark changes

Implementation status: complete on the Milestone 2 contributor-release branch.

### Provider Examples

- add runnable examples for OpenAI, Anthropic, and Ollama
- document environment setup and expected outputs
- include at least one example comparison run

Implementation status: complete on the Milestone 2 contributor-release branch.

### Baseline Reports

- publish signed reports for a representative open model, hosted model, and local model
- include run metadata, suite version, and benchmark card references

### Methodology Note

- explain benchmark philosophy, measurement boundaries, scoring design,
  failure modes, and reproducibility expectations

## Recommended Contributor Labels

If label management is added later, these labels would be useful:

- `roadmap`
- `benchmark`
- `scoring`
- `security`
- `docs`
- `good first issue`
- `research`
- `release`

## Risks To Manage

- mistaking lexical robustness for benchmark validity
- publishing comparisons without sufficient calibration context
- overloading contributors with philosophy before they can build productively
- letting engine and benchmark content evolve without versioning boundaries

## Immediate Next Step

Begin Milestone 3 by producing reproducible signed baseline runs and a
methodology note that explains how to interpret Aletheia results responsibly.
