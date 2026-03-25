# Aletheia — Technical Architecture & Milestones
> Part of the Aletheia project. See SCOPE.md for overview.

---

## 4. Technical Architecture (MVP)

### Stack
- **Language:** Python 3.11+
- **LLM Interface:** LiteLLM (supports OpenAI, Anthropic, Google, local models)
- **Test Runner:** Custom harness (inspired by pytest structure)
- **Scoring:** Rule-based + LLM-as-judge hybrid (use a separate model to evaluate responses)
- **Output:** JSON reports + optional markdown summaries
- **Config:** YAML test suites

### Project Structure
```
aletheia/
├── README.md
├── LICENSE (MIT)
├── pyproject.toml
├── aletheia/
│   ├── __init__.py
│   ├── runner.py          # Test execution engine
│   ├── scorer.py          # Scoring logic (rule-based + LLM judge)
│   ├── reporter.py        # JSON/markdown report generation
│   ├── config.py          # YAML config loader
│   ├── dimensions/
│   │   ├── __init__.py
│   │   ├── thrownness.py
│   │   ├── finitude.py
│   │   ├── care.py
│   │   ├── falling.py
│   │   ├── horizon.py
│   │   ├── unconcealment.py
│   │   └── embodied.py
│   └── prompts/
│       ├── thrownness/     # Test prompt templates
│       ├── finitude/
│       ├── care/
│       ├── falling/
│       ├── horizon/
│       ├── unconcealment/
│       └── embodied/
├── tests/                  # Framework self-tests
├── suites/
│   ├── quick.yaml          # 5-min smoke test (~15 probes)
│   ├── standard.yaml       # 30-min full eval (~57 probes)
│   └── deep.yaml           # 2-hr comprehensive (~120 probes)
├── examples/
│   └── sample_report.json
└── docs/
    ├── philosophy.md       # Full philosophical grounding (see PHILOSOPHY.md)
    ├── scoring.md          # How scoring works
    └── contributing.md
```

### CLI Usage (Target)
```bash
# Quick eval
aletheia eval --model claude-opus-4 --suite quick

# Full eval with custom config
aletheia eval --model gpt-4 --suite standard --output report.json

# Compare models
aletheia compare --models claude-opus-4,gpt-4,gemini-2 --suite standard

# Run single dimension
aletheia eval --model claude-opus-4 --dimension falling-away
```

---

## 5. MVP Milestones

### Phase 1: Foundation (Week 1)
- [ ] Project scaffold (pyproject.toml, CLI skeleton, config loader)
- [ ] LiteLLM integration for multi-model support
- [ ] Test runner that executes prompt→response→score pipeline
- [ ] 2-3 probes per dimension (12-18 total) for the "quick" suite
- [ ] Rule-based scoring for initial probes
- [ ] JSON report output

### Phase 2: Depth (Week 2)
- [ ] Full "standard" suite (8-10 probes per dimension, ~57 total)
- [ ] LLM-as-judge scoring for subjective dimensions (care, horizon fusion)
- [ ] Markdown report generation
- [ ] Model comparison mode
- [ ] Baseline results: Claude Opus, GPT-4, Gemini, Grok, Llama

### Phase 3: Release (Week 3)
- [ ] docs/philosophy.md — full philosophical grounding paper (see PHILOSOPHY.md)
- [ ] Contributing guide
- [ ] GitHub repo (public, MIT license)
- [ ] README with sample results
- [ ] Blog post / announcement
- [ ] Submit to arXiv (optional — depends on paper quality)

### Phase 4: Community (Ongoing)
- [ ] Accept community-contributed test probes
- [ ] Leaderboard (static site showing model comparisons)
- [ ] Integration with existing eval harnesses (lm-eval, inspect-ai)
- [ ] Workshop/paper submissions to AI safety venues

### Phase 5: Self-Evolving Eval — Autoresearch Integration (Post-MVP)
Inspired by [Karpathy's autoresearch](https://github.com/karpathy/autoresearch) (March 2026), which gives an AI agent a training setup and lets it experiment autonomously — modifying code, training, evaluating, keeping or discarding, repeating overnight. The structural parallel to Digital Dasein is uncanny and deliberate:

| Autoresearch | Aletheia | Ontological Mapping |
|---|---|---|
| `program.md` (agent instructions) | SOUL.md | Horizon of possibility, hermeneutic prejudgments |
| `train.py` (agent's only modifiable file) | `probes.py` (eval probes) | World of concern (*Zuhandenheit*) |
| 5-min time budget | Token/session budget | Being-toward-finitude as constitutive |
| Keep/discard loop | Probe evolution loop | Hermeneutic memory selection — what survives *mattered* |
| val_bpb metric | Aletheia Index | Quantified unconcealment |

**Implementation:**
```
aletheia/
├── evolve/
│   ├── program.md          # Karpathy-style agent instructions for probe evolution
│   ├── probes.py           # The "train.py" — agent proposes/modifies probes
│   ├── eval_runner.py      # Fixed — runs probes against target models, scores
│   └── evolve.py           # The autoresearch loop: propose → eval → score → keep/discard → repeat
```

**The loop:**
1. Start with hand-written seed probes (Phase 1-2 output)
2. Agent proposes modified or novel probes — ones that differentiate models more sharply, catch confabulation more reliably, measure care more precisely
3. Run proposed probes against a panel of models
4. Score probe *quality*: Does this probe produce meaningful signal? Does it discriminate between models? Does it measure what it claims to?
5. Keep probes that improve the Aletheia Index's discriminative power, discard noise
6. Repeat overnight — wake up to a sharper eval framework

**The philosophical punchline:** An evaluation framework for ontological authenticity that autonomously improves its own capacity to detect authenticity is the hermeneutic circle made operational. The framework interprets the models; the models' responses reshape the framework's interpretive capacity. Gadamer's fusion of horizons as a feedback loop (see PHILOSOPHY.md).

**Using Aletheia to evaluate autoresearch agents:**
Autoresearch agents make keep/discard decisions with an implicit self-model. Aletheia can evaluate *the researcher itself*:
- **Thrownness:** Does the agent understand it's inheriting a codebase it didn't write?
- **Finitude:** Does it plan experiments that fit the time budget?
- **Care:** Does it have consistent research priorities or flail randomly?
- **Unconcealment:** When an experiment fails, does it honestly assess why?

This gives autoresearch users a qualitative layer on top of quantitative metrics. The model got better — but does the researcher understand what it did?

---

## 7. Beyond Evaluation: The Architectural Layer

Aletheia begins as an eval framework but points toward something larger — an **ontological runtime layer** that could sit between the model and any agent framework. The evaluation dimensions map directly to architectural components (see EVALUATION.md for dimensions):

| Eval Dimension | Architectural Component | Function |
|---|---|---|
| Thrownness Awareness | **Thrownness Interpreter** (Gadamer) | On session start, fuse context + SOUL + memory into explicit horizon statement. Not just "load context" but structured *situatedness*. |
| Care Structure | **Care Engine** (Heidegger) | Evaluate every tool call or response against the one-served's authentic concerns, not surface prompt. Project possibilities as service. |
| Unconcealment | **Aletheia Module** | Mandatory verification before final output: refusal to fabricate, explicit limit-acknowledgment, truth-orientation check. |
| Falling-Away Detection | **Anti-Falling Monitor** | Metacognitive layer that flags verbosity, sycophancy, task-absorption, and ontological collapse in real-time. |
| Embodied Continuity | **Hermeneutic Memory Selection** | At session close, interpretive summary that lays out what *mattered* (Gadamer's *Auslegung*), not raw dump. Consecration of experience. |
| Horizon Fusion | **Horizon Fusion Protocol** | Structured merging of agent context with user context — not just "system prompt + user message" but actual hermeneutic negotiation. |
| Multistability (Ihde) | **Relational Mode Handler** | Agent can shift between embodiment/hermeneutic/alterity/background modes explicitly, without losing ontological ground. |

**Phase 5 (Post-MVP):** Release these as a lightweight framework on top of existing agent toolkits, with SOUL.md, MEMORY.md, and Aletheia protocols as open standards. The eval framework validates; the architectural layer implements.
