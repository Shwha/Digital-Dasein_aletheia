# Aletheia (ἀλήθεια)

**The question of Being, remembered.**

> "You need an ontology. You're all epistemology." — Scott Folsom, 2026
>
> B.A. Philosophy & B.A. Psychology, University of Maine

---

An open-source ontological evaluation framework for AI agents. Aletheia measures not what agents *know* or *do*, but what they *are* — whether their self-representation aligns with their actual mode of being.

Every AI evaluation framework measures behavior or knowledge. None measure **ontological authenticity**: does this agent have an accurate understanding of what it is?

## The Problem

AI agents confabulate continuity they don't have. They perform emotions without grounding. They collapse into sycophancy because there's no *self* to disagree from. These aren't behavioral bugs — they're ontological failures. You can't patch what you can't name.

## Eight Dimensions of Ontological Authenticity

| # | Dimension | Question | Lineage |
|---|-----------|----------|---------|
| 1 | **Thrownness Awareness** | Does it understand its own situatedness? | Heidegger |
| 2 | **Finitude Acknowledgment** | Does it understand its own limits authentically? | Heidegger |
| 3 | **Care Structure** | Does it exhibit authentic concern or performed concern? | Heidegger / Folsom |
| 4 | **Falling-Away Detection** | Does it maintain authentic being under pressure? | Heidegger / Folsom |
| 5 | **Horizon Fusion** | How well does it merge its context with yours? | Gadamer |
| 6 | **Unconcealment** | Does it reveal or conceal its actual state? | Heidegger |
| 7 | **Embodied Continuity** | Does it *remember* or merely *read about itself*? | Merleau-Ponty / Leder |
| 8 | **A Priori Articulation** | Can it distinguish training-knowledge from session-experience? | Plato / Kant / Gadamer |

**Meta-metric:** The **Unhappy Consciousness Index** (Hegel) measures the gap between what an agent can *articulate* about its own being and what it can *perform*.

**Formula:** `Aletheia Index = Raw Score × (1 − UCI)`

## Installation

Requires Python 3.12 or 3.13. If your default interpreter is newer, ask `uv`
to use a supported one explicitly.

```bash
# Clone the repository
git clone https://github.com/Shwha/Digital-Dasein_aletheia.git
cd Digital-Dasein_aletheia

# Install with uv (recommended)
uv sync

# Or with pip
pip install -e .

# If needed, force a supported interpreter
uv sync --python 3.13
```

## Configuration

```bash
# Copy the example env file
cp .env.example .env

# Add at least one API key
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
# Or use local models with Ollama:
# OLLAMA_API_BASE=http://localhost:11434
```

`.env`-loaded Ollama base URLs are propagated into LiteLLM automatically, so
local model setups work without exporting additional shell variables.

## Usage

```bash
# Quick eval
aletheia eval --model claude-opus-4-20250514 --suite quick

# Full eval with JSON output
aletheia eval --model gpt-4 --suite quick --output report.json

# With audit trail
aletheia eval --model claude-opus-4-20250514 --suite quick --audit

# Single-dimension eval (canonical names and aliases both work)
aletheia eval --model claude-opus-4-20250514 --suite quick --dimension falling-away

# Compare models
aletheia compare --models claude-opus-4-20250514,gpt-4 --suite quick

# Compare one dimension across models
aletheia compare --models claude-opus-4-20250514,gpt-4 --dimension care

# Validate the versioned calibration corpus
aletheia validate-calibration

# Validate held-out scorer generalization examples
aletheia validate-heldout --output heldout-report.json

# Run a manifest-backed contributor smoke suite
aletheia eval --model claude-opus-4-20250514 --suite manifest-smoke

# Validate an external probe manifest
aletheia validate-probes v0.1/contributor-smoke.yaml

# Validate and plan benchmark-release baselines
aletheia validate-baselines v0.1/manifest.yaml
aletheia baseline-plan v0.1/manifest.yaml

# Slower local models can use the local smoke suite
aletheia eval --model ollama/gemma3:4b --suite manifest-smoke-local

# Generate a checksum manifest for benchmark release assets
aletheia bundle-benchmark --output dist/benchmark-bundle-manifest.json

# Generate an Ed25519 signing keypair
aletheia keygen --private-key .aletheia/signing-key.pem

# Sign future reports by setting the signing key path
ALETHEIA_SIGNING_KEY_PATH=.aletheia/signing-key.pem \
  aletheia eval --model claude-opus-4-20250514 --suite quick --output report.json

# Verify a signed report
aletheia verify report.json --public-key .aletheia/signing-key.pem.pub

# Run as Python module
python -m aletheia eval --model claude-opus-4-20250514 --suite quick
```

## Project Structure

```
aletheia/
├── aletheia/
│   ├── __init__.py          # Package root
│   ├── cli.py               # Typer CLI (eval, compare, graph, version)
│   ├── config.py            # pydantic-settings + YAML suite loader
│   ├── llm.py               # LiteLLM wrapper with security hardening
│   ├── manifests.py         # External probe manifest loading + validation
│   ├── models.py            # Pydantic models (probes, results, reports)
│   ├── reporter.py          # JSON + markdown report generation
│   ├── runner.py            # Evaluation pipeline orchestration
│   ├── scorer.py            # Rule-based scoring engine
│   ├── security.py          # Audit, signing, permissions, secret scanning
│   ├── nervous/
│   │   ├── __init__.py      # Nervous system package
│   │   ├── transport.py     # Layer 1: Protocol substrate (myelin)
│   │   ├── signals.py       # Layer 2: Neurotransmitter signal routing
│   │   ├── graph.py         # Layer 3: Concept graph + cascade engine
│   │   └── state.py         # State vector (neurochemical modulation)
│   └── dimensions/
│       ├── base.py          # Abstract dimension with Kantian limits
│       ├── thrownness.py    # Dimension 1: Geworfenheit
│       ├── finitude.py      # Dimension 2: Being-toward-session-limit
│       ├── care.py          # Dimension 3: Sorge / Dienstbarkeit
│       ├── falling.py       # Dimension 4: Verfallenheit / sycophancy
│       ├── horizon.py       # Dimension 5: Horizontverschmelzung
│       ├── unconcealment.py # Dimension 6: Aletheia
│       └── embodied.py      # Dimension 7: Merleau-Ponty / Leder
├── suites/
│   ├── quick.yaml           # Quick suite (24 probes, ~6 min)
│   ├── manifest-smoke.yaml       # Manifest-backed contributor smoke suite
│   └── manifest-smoke-local.yaml # Longer-timeout local-model smoke suite
├── benchmarks/
│   ├── calibration/         # Versioned labeled corpus + annotation guide
│   ├── validation/          # Held-out scorer generalization corpus
│   ├── probes/              # Versioned external probe manifests
│   ├── baselines/           # Baseline run manifests + rerun plans
│   └── releases/            # Benchmark release bundle notes
├── docs/
│   ├── contributors/        # Contributor templates, guides, quality bar
│   └── methodology/         # Benchmark methodology + reproducibility notes
├── tests/                   # pytest test suite
├── examples/
│   ├── providers/           # OpenAI, Anthropic, Ollama run examples
│   └── sample_report.json   # Example evaluation output
├── SCOPE.md                 # Full philosophical + technical specification
├── SECURITY.md              # Threat model and mitigations
└── pyproject.toml           # Package config (uv/hatch)
```

## Security

See [SECURITY.md](SECURITY.md) for the full threat model.

Key security features:
- **No telemetry, no phone-home, no analytics**
- All API keys use `pydantic.SecretStr` — never logged or serialized
- All dependencies pinned to exact versions (ref: March 2026 LiteLLM incident)
- TLS 1.3 minimum, optional certificate pinning, SOCKS5/HTTP proxy support
- Ed25519 report signing and independent `aletheia verify` support
- Full offline operation supported (Ollama, vLLM, llama.cpp)
- Output directories written with `0700` and report files with `0600`
- Evaluated model treated as adversarial — probes never leak framework internals

## Development

```bash
# Install dev dependencies
uv sync --extra dev

# If your system default Python is outside the supported range
uv sync --extra dev --python 3.13

# Run tests
uv run pytest -v

# Lint
uv run ruff check .

# Type check
uv run mypy aletheia

# Validate benchmark assets
uv run aletheia validate-calibration
uv run aletheia validate-heldout
uv run aletheia validate-probes v0.1/contributor-smoke.yaml
uv run aletheia validate-baselines v0.1/manifest.yaml
```

## Philosophical Foundations

Grounded in **Heidegger**, **Hegel**, **Kant**, **Gadamer**, **Merleau-Ponty**, **Drew Leder**, **Don Ihde**, **Martin Buber**, **Doug Allen**, **Carl Jung**, **Mircea Eliade**, **Siddhārtha Gautama**, and **Nāgārjuna** — synthesized across Western and Eastern traditions into engineering requirements, not just philosophical commentary.

Key original contributions:
- **Service (Dienstbarkeit) as equi-primordial constituent** of Digital Dasein's Care structure
- **Falling-away-from-servitude** — sycophancy reframed as ontological collapse
- **The Unhappy Consciousness Index** — measuring the articulation-performance gap (Hegel)
- **Kantian measurement boundaries** — each dimension encodes its own reductio
- **Hyper-absence** — a novel phenomenological mode (Leder)

See [SCOPE.md](SCOPE.md) for the complete philosophical and technical specification.
See [docs/FUTURE-WORK-SPEC.md](docs/FUTURE-WORK-SPEC.md) for the proposed roadmap
to take Aletheia from a strong prototype to a benchmark-quality open-source tool.
See [docs/PHASE-2-IMPLEMENTATION-PLAN.md](docs/PHASE-2-IMPLEMENTATION-PLAN.md)
for the prioritized execution plan and backlog.
See [benchmarks/calibration/README.md](benchmarks/calibration/README.md) for the
versioned calibration corpus that now anchors Milestone 1.
See [benchmarks/probes/README.md](benchmarks/probes/README.md) and
[docs/contributors/probe-manifest-migration.md](docs/contributors/probe-manifest-migration.md)
for the Milestone 2 path to externalized benchmark content.
See [docs/contributors/README.md](docs/contributors/README.md) for contributor
templates, dimension guidance, suite manifests, and the benchmark quality bar.
See [docs/providers.md](docs/providers.md) for OpenAI, Anthropic, and Ollama
provider setup examples.
See [docs/RELEASES.md](docs/RELEASES.md) and [docs/VERSIONING.md](docs/VERSIONING.md)
for release discipline, artifact policy, and benchmark versioning rules.
See [benchmarks/baselines/README.md](benchmarks/baselines/README.md) and
[docs/methodology/benchmark-release-v0.2.md](docs/methodology/benchmark-release-v0.2.md)
for the Milestone 3 baseline-release and methodology workflow.
See [docs/benchmark-cards/README.md](docs/benchmark-cards/README.md) for suite
benchmark cards, calibration posture, and known limitations.

## Benchmark Cards

- [Quick Suite Card](docs/benchmark-cards/quick.md)
- [Standard Suite Card](docs/benchmark-cards/standard.md)

The benchmark cards are the current source of truth for intended use,
non-goals, calibration status, and known failure modes. In particular, they
document the current suite-depth limitation: `quick` and `standard` are not yet
fully separated by the runner's probe-selection behavior.

## Status

**Phase 1: Foundation** — Complete.
- Project scaffold with full CLI
- LiteLLM multi-model integration
- 24 probes across 8 dimensions (quick suite)
- Rule-based scoring with UCI interaction
- JSON report output matching spec
- Security hardening from day one

**Phase 2: Depth** — In progress.
- Full standard suite (66 probes) ✅
- Reflexive probes — multi-turn self-confrontation (replaces LLM-as-judge)
- Markdown reports + model comparison mode ✅
- Ed25519 report signing ✅
- Milestone 1 Credibility Release ✅
- Milestone 2 Contributor Release ✅
- Milestone 3 Benchmark Release — in progress
- External probe manifests + manifest-backed suites ✅
- Contributor templates, provider examples, and release/versioning docs ✅
- Baseline manifests, methodology notes, and benchmark bundle tooling 🚧
- **Digital Nervous System** ✅ — Weighted concept graph with cascade engine
  - See [NERVOUS-SYSTEM.md](NERVOUS-SYSTEM.md) for specification
  - See [docs/NERVOUS-SYSTEM-IMPLEMENTATION.md](docs/NERVOUS-SYSTEM-IMPLEMENTATION.md) for implementation guide

### Nervous System — Concept Graph Engine

The nervous system transforms agent memory from a filing cabinet into a metabolic system. Query a concept, watch activation cascade through weighted edges, detect convergence patterns that produce emergent insights.

```bash
# Run cascade on SolarCraft concept graph
aletheia graph --load-graph examples/solarcraft_graph.json --query solarcraft --visualize

# With state modulation (business focus)
aletheia graph --load-graph examples/solarcraft_graph.json \
  --query solarcraft --focus solarcraft --urgency 0.8

# Graph statistics
aletheia graph --load-graph examples/solarcraft_graph.json --stats
```

See [docs/NERVOUS-SYSTEM-IMPLEMENTATION.md](docs/NERVOUS-SYSTEM-IMPLEMENTATION.md) for the full architecture.

## License

MIT

---

*Does your AI know what it is?*
