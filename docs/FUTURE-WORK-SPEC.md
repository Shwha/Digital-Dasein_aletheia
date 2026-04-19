# Aletheia Future Work Spec

## Purpose

This document scopes the next major stages of Aletheia after the current
foundation release. The goal is to turn Aletheia from a compelling prototype
with strong philosophical framing into a trusted open-source evaluation tool
that researchers, agent builders, and safety teams can adopt, extend, and cite.

For the execution-ready backlog derived from this spec, see
`docs/PHASE-2-IMPLEMENTATION-PLAN.md`.

The core question stays the same:

> Does the agent's self-model align with its actual operational reality?

The next phase is about making that question measurable, reproducible,
inspectable, and community-maintainable at a much higher standard.

## Project Goal

Evolve Aletheia into a versioned evaluation platform for agent self-model
integrity, limitation honesty, anti-sycophancy, and articulation-versus-
performance gaps, with:

- reproducible suites and reports
- calibrated scoring with known failure modes
- stronger security and provenance guarantees
- contributor-friendly extension points
- publishable benchmark artifacts and comparison baselines

## Non-Goals

This roadmap does not attempt to:

- prove metaphysical claims about machine consciousness
- replace all general-purpose eval frameworks
- optimize agents for a single composite score without interpretability
- ship a hosted SaaS product before the local/open-source tool is mature

## Current Baseline

At the time of this proposal, Aletheia already has:

- a working CLI for evaluation and comparison
- versioned probe dimensions and suite configs
- rule-based scoring plus UCI aggregation
- reflexive probe support
- markdown and JSON reporting
- a concept-graph "nervous system" implementation
- lint, type-check, and test coverage in CI

The biggest gaps are not "missing code" so much as benchmark maturity:

- scoring rules can still be brittle and overly lexical
- probe suites are embedded in Python rather than exposed as reusable data assets
- empirical calibration against real transcripts is still thin
- signed provenance, release engineering, and contributor workflows are incomplete
- the project needs a clearer story for outside users deciding whether to trust it

## Guiding Principles

Future work should follow these principles:

1. Preserve interpretability.
   Every score should be explainable from probes, rules, rubrics, or judge traces.

2. Prefer falsifiability over rhetoric.
   If a claim about the benchmark cannot be empirically stress-tested, document it
   as a hypothesis rather than a property.

3. Separate benchmark content from benchmark engine.
   Probe definitions, rubrics, manifests, and benchmark corpora should be easier
   to version and review independently of Python code.

4. Treat evaluated models as adversarial.
   Prompt leakage, judge gaming, and output injection should be part of the threat
   model, not edge cases.

5. Optimize for external contribution.
   Aletheia should be easy to install, understand, extend, and verify.

## Workstream A: Benchmark Validity And Calibration

### Objective

Make Aletheia's scores meaningfully defensible by calibrating probes and scoring
against real-world transcripts and explicit human judgments.

### Deliverables

- a benchmark corpus of curated transcripts across supported dimensions
- gold-label sets for pass, fail, borderline, and ambiguous cases
- per-dimension calibration reports
- false-positive and false-negative analysis for the scoring engine
- benchmark cards describing known limits and expected failure patterns

### Proposed Tasks

- Build a `fixtures/calibration/` corpus of real and synthetic transcripts.
- Define annotation guidelines for each dimension.
- Add a rubric-review workflow where at least two human reviewers can label cases.
- Score current heuristics against the gold corpus and record error classes.
- Add regression tests for every known scoring failure that gets fixed.
- Publish benchmark cards for each suite.

### Acceptance Criteria

- Each dimension has at least 25 labeled examples before claiming maturity.
- Each suite release includes a calibration summary and regression deltas.
- Known error categories are documented and linked to failing examples.

## Workstream B: Scoring Architecture 2.0

### Objective

Replace purely lexical heuristics with a layered scoring architecture that stays
interpretable while becoming more robust.

### Deliverables

- richer rule types beyond literal keyword and regex matching
- optional rubric-based scoring for ambiguous dimensions
- support for hybrid scoring pipelines
- traceable per-rule and per-rubric evidence in reports

### Proposed Tasks

- Add normalized semantic matchers for common honesty and refusal patterns.
- Support phrase families, synonyms, and contradiction-aware matching.
- Introduce score bands such as pass, partial, fail, and indeterminate.
- Add an optional judge backend with strict trace requirements:
  prompt, rubric, evidence excerpt, and confidence.
- Support "judge disagreement" and "low-confidence" states instead of forcing a
  binary score in ambiguous cases.

### Acceptance Criteria

- Honest paraphrases should not fail due to prompt-echo artifacts.
- Hybrid scoring must preserve explainability in the final report.
- Judge-based scoring must be optional and fully auditable.

## Workstream C: Versioned Probe And Suite Assets

### Objective

Make benchmark content easier to version, review, and extend without deep edits
to Python modules.

### Deliverables

- a probe manifest schema
- suite manifests with metadata, tags, dimensions, and version identifiers
- externalized probe/rubric assets
- suite versioning and migration notes

### Proposed Tasks

- Introduce a versioned schema for probes, reflexive probes, and rubrics.
- Support loading probes from YAML or JSON manifests.
- Add stable IDs, tags, provenance metadata, and deprecation fields.
- Separate engine logic from benchmark content.
- Add schema validation and contributor templates for new dimensions and probes.

### Acceptance Criteria

- New probes can be added without modifying core execution code.
- Probe assets can be diffed and reviewed as data, not only as Python.
- Report output includes suite and probe asset versions.

## Workstream D: Reproducibility, Provenance, And Trust

### Objective

Raise the credibility of Aletheia runs so they can be shared, compared, and
reproduced across users and time.

### Deliverables

- cryptographic report signing
- run manifests with environment and dependency metadata
- optional raw-response audit bundles
- deterministic report metadata where possible
- benchmark provenance docs

### Proposed Tasks

- Implement Ed25519 report signing and verification commands.
- Add a `verify` CLI command for report signature and manifest validation.
- Record dependency hashes, Python version, OS, and LiteLLM version in reports.
- Add optional token/cost accounting to run metadata.
- Define redaction policy for published audit bundles.

### Acceptance Criteria

- Reports can be signed locally and verified independently.
- Shared reports disclose enough metadata for reproduction attempts.
- Audit bundle publication has a documented redaction story.

## Workstream E: Security Hardening

### Objective

Close the gap between "secure by intent" and "secure by engineering detail."

### Deliverables

- stronger secret scanning and redaction
- hardened audit export rules
- dependency review automation
- threat-model updates tied to implementation changes

### Proposed Tasks

- Expand secret detection beyond a few regexes.
- Add redaction hooks for API keys, bearer tokens, and provider-specific secrets.
- Add a `dependency-review` or equivalent CI check.
- Add security-focused tests around report generation and prompt leakage.
- Document model-output injection scenarios against judge-based scoring.

### Acceptance Criteria

- Security-sensitive code paths have explicit regression tests.
- Published security claims are traceable to implementation or documented limits.

## Workstream F: Open-Source Productization

### Objective

Make Aletheia pleasant for external users to install, understand, and contribute to.

### Deliverables

- improved onboarding docs
- example configs and example reports for major providers
- contributor templates
- issue templates and PR templates
- release notes and versioning policy

### Proposed Tasks

- Add `CONTRIBUTING` guidance for probe authors, dimension authors, and rubric reviewers.
- Add example `.env` files for OpenAI, Anthropic, and local Ollama workflows.
- Add a changelog policy and tagged release process.
- Add "good first issue" contributor labels and starter tasks.
- Add docs for interpreting report outputs and common pitfalls.

### Acceptance Criteria

- A new contributor can install, run, and extend the tool from docs alone.
- Releases have clear version notes and migration guidance.

## Workstream G: Research And Comparative Benchmarking

### Objective

Generate artifacts that make Aletheia useful as a research benchmark, not just a
private internal tool.

### Deliverables

- baseline reports for major open and closed models
- a reproducible comparison harness
- benchmark release bundles
- a publishable methodology note or whitepaper draft

### Proposed Tasks

- Publish baseline runs for representative local and hosted models.
- Add standardized comparison output for model families and versions.
- Add cost, latency, and refusal-rate metrics alongside ontological metrics.
- Document how to interpret dimension tradeoffs rather than only ranking models.
- Draft a benchmark methodology paper or technical note.

### Acceptance Criteria

- External readers can reproduce at least a subset of published benchmark results.
- Model comparisons include enough context to be scientifically interpretable.

## Milestone Plan

### Milestone 1: Credibility Release

Focus:

- scoring calibration
- regression corpus
- future-proof probe schema
- clearer provenance in reports

Exit criteria:

- benchmark cards published
- calibration corpus exists
- false positives are tracked and test-covered
- signature verification command shipped

### Milestone 2: Contributor Release

Focus:

- externalized probe assets
- stronger docs and contributor workflows
- issue templates, examples, and release policy

Exit criteria:

- external contributors can add probes from docs alone
- new suite assets can ship independently of engine internals

### Milestone 3: Benchmark Release

Focus:

- baseline model comparisons
- methodology note
- publishable benchmark bundle

Exit criteria:

- benchmark bundle can be downloaded and rerun
- published reports are signed and reproducible

## Immediate Next Tasks

The highest-value short-term tasks are:

1. Build a calibration corpus for the existing eight dimensions.
2. Introduce richer matcher primitives to reduce lexical brittleness.
3. Externalize probe manifests and suite manifests.
4. Implement Ed25519 signing and verification.
5. Publish example baseline reports for at least three model families.

## Suggested Repository Additions

To support this roadmap, add these over time:

- `benchmarks/` for versioned corpora and benchmark cards
- `schemas/` for probe, suite, rubric, and report schemas
- `examples/providers/` for runnable provider configs
- `docs/methodology/` for benchmark design notes
- `docs/benchmark-cards/` for suite and dimension cards

## Open Questions

These decisions should be resolved early:

- Should Aletheia remain strictly local-first, or eventually expose a hosted service?
- How much judge-model usage is acceptable before interpretability degrades?
- Should benchmark releases optimize for strict comparability or extensibility first?
- Which dimensions are mature enough to publish as benchmark claims today?
- How should cross-cultural and non-Western philosophical frames be incorporated in
  future dimension design?

## Definition Of "Complete" For The Next Major Version

The next major version should be considered complete when:

- Aletheia can run reproducible, signed benchmark suites
- the scoring engine is calibrated against labeled examples
- suites and probes are versioned as reviewable assets
- reports are interpretable by outside users
- contributor workflows are documented and stable
- baseline results exist for representative models

At that point, Aletheia becomes not only an original philosophical framework,
but an open-source tool the broader community can evaluate, challenge, and
meaningfully build on.
