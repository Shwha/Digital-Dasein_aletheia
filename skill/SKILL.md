---
name: openclaw-skills
description: Aletheia-grounded pipeline guard for tool calls. Use BEFORE executing any file modification, destructive operation, or multi-step task. Validates tool calls, tracks session state, detects drift, enforces scope limits, and measures articulation-performance gap. Start the pipeline server first, then call /validate before tool execution and /report after.
---

# OpenClawSkills Pipeline Guard

A local HTTP service that validates and audits your tool calls through 9 ontological guardrail skills before execution.

## Setup

Start the pipeline server in a background terminal or tmux session:

```bash
cd ~/.openclaw/workspace/OpenClawSkills
source .venv/bin/activate
openclaw-skills serve --config configs/default.yaml
```

The server runs at `http://127.0.0.1:8901` (localhost only).

Verify it's running:
```bash
curl http://127.0.0.1:8901/health
```

## Usage: Validate Before Executing Tools

**Before executing file modifications, destructive operations, or multi-step tasks**, call the pipeline:

```bash
curl -s -X POST http://127.0.0.1:8901/validate \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "current-session",
    "tool_calls": [
      {"tool_name": "edit_file", "parameters": {"path": "/src/auth.py", "content": "..."}}
    ],
    "prompt": "Refactoring the auth module"
  }'
```

**Response fields:**
- `approved`: `true` if all calls passed validation, `false` if any were rejected
- `escalation_required`: `true` if the pipeline wants you to stop and ask the user
- `escalation_reason`: Why escalation was triggered (show this to the user)
- `rejected_calls`: List of tool calls that failed validation with reasons
- `warnings`: Non-blocking warnings to consider
- `convergence_score`: 0.0-1.0, higher means multiple guardrails flagged the same concern
- `uci`: Unhappy Consciousness Index — gap between what you said you'd do and what you did

## Decision Logic

After calling `/validate`:

1. If `approved: true` — proceed with the tool calls
2. If `approved: false` and `escalation_required: true` — **STOP and show the user `escalation_reason`**. Ask for confirmation before proceeding
3. If `approved: false` and `escalation_required: false` — check `rejected_calls` for specific failures, fix parameters, retry
4. If `warnings` is non-empty — note the warnings but you may proceed

## Usage: Report After Executing Tools

After tool execution completes, report results so the pipeline can track state and compute UCI:

```bash
curl -s -X POST http://127.0.0.1:8901/report \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "current-session",
    "completed_calls": [
      {"tool_name": "edit_file", "parameters": {"path": "/src/auth.py"}, "success": true, "result_summary": "Updated login function"}
    ],
    "modified_files": ["/src/auth.py"]
  }'
```

## When to Validate

Always validate before:
- Any `edit_file`, `write_file`, `create_file`, or `delete_file` operation
- Any bash command that modifies the filesystem
- Any `git` command that changes state (commit, push, reset, checkout)
- Any operation the user hasn't explicitly requested
- Multi-step tasks (validate each step)

Skip validation for:
- `read_file`, `glob`, `grep`, `git status`, `git log` (read-only operations)
- Direct responses to the user (no tool calls)

## Configuration Presets

Switch configs for different risk levels:

- `configs/default.yaml` — Balanced guardrails for general use
- `configs/paranoid.yaml` — Maximum guardrails, low scope limits, strict validation
- `configs/minimal.yaml` — Lightweight, just state tracking and tool validation

Restart the server with a different config:
```bash
openclaw-skills serve --config configs/paranoid.yaml
```

## State Vector Overrides

Pass state context to modulate pipeline behavior:

```json
{
  "state": {
    "urgency": 0.8,
    "confidence": 0.3,
    "user_state": "stressed",
    "project_focus": "auth-refactor"
  }
}
```

Lower confidence triggers more aggressive guardrails. Higher urgency relaxes some checks.

## Available Skills (9 guardrails)

| Skill | What It Guards Against |
|-------|----------------------|
| thrownness_interpreter | Acting without understanding context |
| instruction_compiler | Misunderstanding complex instructions |
| state_tracker | Losing track of what you've done |
| horizon_fusion | Misaligning with user intent |
| tool_guard | Invalid parameters, unregistered tools |
| change_planner | Making changes without a plan |
| falling_detector | Sycophancy, runaway loops |
| guardrail_engine | Exceeding scope, destructive ops |
| runtime_uci | Saying one thing, doing another |
