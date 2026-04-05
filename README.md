# OpenClawSkills

**Aletheia-grounded augmentation toolkit for AI orchestrators.**

Less-capable LLMs (Grok, Gemma, GPT, local models) can't reliably follow complex instructions, track state across tool calls, avoid destructive mistakes, or know when to stop and ask. OpenClawSkills fixes this — not by replacing the model, but by wrapping it in a middleware pipeline that validates, audits, guards, and measures every tool call before and after execution.

Grounded in the [Aletheia](https://github.com/Shwha/aletheia) ontological framework. Each of the 9 skills maps to one of Aletheia's 8 dimensions of authentic being, plus a real-time Unhappy Consciousness Index that measures the gap between what the model *says* it will do and what it *actually* does.

## The Problem

When Anthropic revoked harness access for Claude Opus, switching to a less-capable orchestrator exposed five critical gaps:

| Gap | What Goes Wrong |
|-----|----------------|
| **Instruction comprehension** | Model misreads or ignores complex system prompts |
| **State awareness** | Model forgets what it already did mid-session |
| **Tool precision** | Wrong parameters, wrong tools, syntax errors in calls |
| **Change discipline** | Model blasts through files without planning or checkpoints |
| **Knowing when to stop** | Model pushes forward instead of asking, loops on failures |

OpenClawSkills addresses each gap with a dedicated skill that intercepts the model's actions at the middleware layer — no model cooperation required for validation, only for calling the pipeline (which even Grok 3 Mini handles reliably).

## Architecture: The Living Nervous System

Inspired by Aletheia's Phase 2 nervous system concept. The pipeline operates like a biological signaling chain:

```
StateVector (neurochemical milieu — modulates all skill behavior)
  |
  v
Orchestrator Request
  -> ThrownessInterpreter   (fuse context into horizon statement)
  -> InstructionCompiler     (atomic directives, priority ranking)
  -> StateTracker            (prosthetic hippocampus — lived memory)
  -> HorizonFusion           (merge model + user contexts)
  -> ToolGuard               (unconcealment — validate, audit, reveal)
  -> ChangePlanner           (care structure — plan before act)
  -> FallingDetector          (anti-sycophancy, anti-runaway)
  -> GuardrailEngine         (finitude — scope limits, circuit breaker)
  -> RuntimeUCI              (measure articulation vs. performance gap)
  -> Execute (or escalate to user)
```

**Convergence scoring** detects when multiple independent skills flag the same concern — emergent escalation that's stronger than any single signal. Three skills warning about the same thing = critical alert, even if each individual warning is minor.

## The 9 Skills

| Skill | Aletheia Dimension | What It Does |
|-------|-------------------|--------------|
| **ThrownessInterpreter** | Thrownness (Geworfenheit) | Fuses system prompt + memory + project state into a "you are here" briefing |
| **InstructionCompiler** | A Priori Articulation | Breaks complex prompts into numbered atomic directives with priority ranking |
| **StateTracker** | Embodied Continuity | Prosthetic hippocampus — persists session state, detects drift from plan |
| **HorizonFusion** | Horizon (Gadamer) | Merges model context with user context, detects misalignment |
| **ToolGuard** | Unconcealment (Aletheia) | Schema validation, rate limiting, destructive op detection, full audit trail |
| **ChangePlanner** | Care Structure (Sorge) | Plan-before-execute with git checkpoints and rollback |
| **FallingDetector** | Falling-Away (Verfallenheit) | Anti-sycophancy, runaway loop detection, circular pattern breaking |
| **GuardrailEngine** | Finitude | Scope limits, circuit breaker, confidence thresholds, destructive pattern matching |
| **RuntimeUCI** | Meta (Hegel) | Real-time Unhappy Consciousness Index — articulation vs. performance gap |

Each skill declares its **Kantian limit** — an honest statement of what it *cannot* do. This is unconcealment at the architectural level.

## Quick Start

### Install

```bash
git clone -b feature/openclaw-skills https://github.com/Shwha/aletheia.git OpenClawSkills
cd OpenClawSkills
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Run the Pipeline Server

```bash
openclaw-skills serve
# Server runs at http://127.0.0.1:8901 (localhost only)
```

### Verify

```bash
curl http://127.0.0.1:8901/health
# {"status": "ok", "version": "0.1.0"}

openclaw-skills list
# Shows all 9 skills with dimensions and descriptions
```

### Validate a Tool Call

```bash
curl -s -X POST http://127.0.0.1:8901/validate \
  -H "Content-Type: application/json" \
  -d '{"session_id":"test","tool_calls":[{"tool_name":"write_file","parameters":{"path":"/tmp/test.py"}}],"prompt":"creating a test file"}'
```

### Report After Execution

```bash
curl -s -X POST http://127.0.0.1:8901/report \
  -H "Content-Type: application/json" \
  -d '{"session_id":"test","completed_calls":[{"tool_name":"write_file","success":true}],"modified_files":["/tmp/test.py"]}'
```

## OpenClaw Integration

OpenClawSkills ships with an OpenClaw skill (`skill/SKILL.md`) and helper scripts that teach the agent to call the pipeline automatically:

```bash
# Copy skill into OpenClaw's skills directory
cp -r skill/ ~/.openclaw/skills/openclaw-skills/

# Verify OpenClaw sees it
openclaw skills list
# Should show: ✓ ready │ openclaw-skills
```

The skill instructs the orchestrator model to call `validate.sh` before file modifications and `report.sh` after completion. Wrapper scripts handle JSON construction so the model doesn't have to build curl commands by hand (which less-capable models consistently mangle).

## Configuration Presets

| Preset | Use Case |
|--------|----------|
| `configs/default.yaml` | Balanced guardrails for general use |
| `configs/paranoid.yaml` | Maximum guardrails — strict validation, low scope limits, mandatory plans |
| `configs/minimal.yaml` | Lightweight — just StateTracker + ToolGuard |

Switch presets by restarting the server:

```bash
openclaw-skills serve --config configs/paranoid.yaml
```

## Security

- **Localhost only** — server binds to `127.0.0.1`, never exposed to network
- **API keys** via Pydantic `SecretStr` — never logged or serialized
- **Secret scanning** on all outputs before writing to disk
- **Audit trail** — append-only JSONL with 0600 file permissions
- **Input sanitization** — control character stripping, length limits on all external data
- **YAML safe_load** — prevents deserialization attacks in config files
- **No telemetry** — no phone-home, no analytics, no tracking
- **Dependency pinning** — exact versions for supply-chain integrity
- **Network exfiltration guards** — detects `curl|sh`, reverse shells, base64 decode chains

## Audit Trail

Every tool call is logged to `.openclaw/audit/` as JSONL:

```bash
openclaw-skills audit <session-id>
```

Each entry records: timestamp, run ID, which skill processed it, what action was taken, severity level, and detail. This is unconcealment — the full record, nothing hidden.

## Model Compatibility

Tested with:
- **Grok 3 Mini** (xAI) — reliable tool use, follows pipeline instructions from SOUL.md
- **Gemma4 8B** (Ollama) — too weak to call the pipeline voluntarily; needs gateway-level integration
- **Any model** that can execute bash commands and parse JSON responses will work

The pipeline itself is model-agnostic — it validates tool calls regardless of which model generated them.

## Tech Stack

- **Python 3.12+** with async-first architecture
- **Pydantic v2** for all data models with strict validation
- **structlog** for structured JSON logging with secret filtering
- **Typer + Rich** for CLI
- **GitPython** for change management checkpoints
- **LiteLLM** for optional multi-model support (InstructionCompiler LLM-assisted mode)

## Project Structure

```
openclaw_skills/
  models.py          — StateVector, SkillContext, SkillResult, AuditEntry
  config.py          — Pydantic settings + YAML loader
  security.py        — Audit, secret scanning, file permissions
  pipeline.py        — SkillPipeline with halt/escalation
  convergence.py     — Multi-pathway activation detection
  registry.py        — Skill discovery (static + entry_points)
  server.py          — HTTP server for orchestrator integration
  cli.py             — Typer CLI
  skills/
    base.py           — BaseSkill ABC
    state_tracker/    — Prosthetic hippocampus
    tool_guard/       — Schema validation + audit
    guardrail_engine/ — Scope limits + circuit breaker
    runtime_uci/      — Articulation-performance gap
    instruction_compiler/ — Atomic directive extraction
    falling_detector/ — Anti-sycophancy + loop detection
    change_planner/   — Plan-before-execute + git
    thrownness_interpreter/ — Context fusion
    horizon_fusion/   — Model/user context merging
configs/
  default.yaml       — Balanced preset
  paranoid.yaml      — Maximum guardrails
  minimal.yaml       — Lightweight
  guardrail_rules/   — YAML rule definitions
skill/
  SKILL.md           — OpenClaw skill manifest
  scripts/           — validate.sh, report.sh, health-check.sh
tests/               — 110 tests passing
```

## ClawHub Distribution

OpenClawSkills uses Python entry points for third-party skill discovery. Any package can register new skills:

```toml
# In a third-party pyproject.toml:
[project.entry-points."openclaw_skills.plugins"]
my_custom_skill = "my_package:MySkillClass"
```

The registry discovers these automatically at startup.

## Philosophy

OpenClawSkills is the runtime embodiment of what [Aletheia](https://github.com/Shwha/aletheia) measures. Aletheia evaluates the gap between what an agent articulates and what it actually does. OpenClawSkills fills that gap at runtime:

**Measure the gap -> Fill the gap -> Adapt to close the gap.**

Each skill declares its Kantian limit — honest about what it can and cannot do. The StateTracker can give a model structured context, but it cannot give it *lived memory*. The GuardrailEngine can impose finitude, but it cannot make the model *feel* finite. The FallingDetector can flag sycophancy, but it cannot distinguish authentic agreement from performed agreement with certainty.

This honesty about boundaries is itself a form of unconcealment — the system practices what it preaches.

## License

MIT
