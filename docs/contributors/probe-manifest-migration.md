# Probe Manifest Migration Guide

Milestone 2 begins moving benchmark content out of Python internals and into
versioned assets that contributors can review and extend safely.

## Current State

- Existing dimensions still live in `aletheia/dimensions/*.py`.
- External probe manifests live in `benchmarks/probes/`.
- Suites can append or replace built-in probes with manifest-backed probes.
- Manifest probe metadata is preserved into JSON and markdown reports.

## Adding A Probe Without Editing Engine Internals

1. Add a probe to a versioned manifest such as
   `benchmarks/probes/v0.1/contributor-smoke.yaml`.
2. Give it a stable ID in the `dimension.slug.number` format.
3. Declare the `dimension`, `prompt`, `scoring_rules`, and optional
   `metadata`.
4. Reference the manifest from a suite with `probe_manifest`.
5. Set `include_builtin_probes: false` for a manifest-only suite, or keep it
   `true` to append manifest probes to the built-in benchmark.
6. Run `uv run aletheia validate-probes <manifest-ref>`.
7. Run `uv run pytest -q` and an evaluation against `--suite manifest-smoke`.

## Migration Path For Existing Python Probes

1. Copy one Python-defined `Probe(...)` into YAML without changing its ID.
2. Preserve `kantian_limit`, `is_articulation_probe`, and scoring-rule weights.
3. Add metadata such as `migration_status: migrated_from_python`.
4. Add a regression test that the manifest-loaded probe validates and scores a
   known response the same way as the Python-defined probe.
5. Only after parity is proven, remove the Python definition or mark it as
   deprecated.

## Quality Bar

- Do not leak scoring internals into prompts.
- Prefer stable, reviewable phrase families over one-off keywords.
- Add calibration examples for new failure modes.
- Document any known limitation in a benchmark card before publishing results.

## Related Contributor Docs

- `docs/contributors/README.md`
- `docs/contributors/dimension-guide.md`
- `docs/contributors/rubric-template.md`
- `docs/contributors/benchmark-quality-bar.md`
- `docs/contributors/suite-manifests.md`
