## Summary

Describe the change and why it belongs in Aletheia.

## Change Type

- [ ] Engine behavior
- [ ] Probe or suite manifest
- [ ] Calibration corpus
- [ ] Benchmark card or methodology docs
- [ ] Provider example or contributor workflow
- [ ] Security, signing, or provenance

## Benchmark Checklist

- [ ] Probe IDs are stable and follow `dimension.slug.number`.
- [ ] Prompts do not leak scoring internals.
- [ ] Scoring rules include reviewable evidence traces.
- [ ] Metadata names owner, benchmark card, and review status where relevant.
- [ ] Known limitations are documented before results are published.
- [ ] Benchmark-affecting changes explain whether scores may move.

## Validation

Paste the commands you ran:

```bash
uv run ruff check .
uv run mypy aletheia
uv run pytest -q
```

For benchmark changes, also run:

```bash
uv run aletheia validate-calibration
uv run aletheia validate-probes v0.1/contributor-smoke.yaml
```

## Notes For Reviewers

Call out any philosophical, scoring, security, or release-versioning questions
that deserve extra attention.

