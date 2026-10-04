# Sol 6.1 evaluation attempt: project model access denied

The OpenAI credential was retrieved once, privately, and written directly into
this repository's ignored `.env`. Readback matched the retrieved value; no key
was displayed. Existing environment settings were preserved, the prior `.env`
was backed up locally, and both files have mode 0600. Credential backups are now
ignored explicitly. Subsequent requests use `.env` and do not access Keychain.

## Actual requests and outcome

- `GET /v1/models`: HTTP 200, proving successful API authentication.
- Models visible to this key: `gpt-5.3-codex`, `gpt-5.5-pro`,
  `gpt-5.5-pro-2026-04-23`, `gpt-5.6-sol`, `gpt-5.6-terra`.
- `GET /v1/models/gpt-6.1-sol`: HTTP 404, “That model does not exist.”
- Two manifest-smoke Chat Completions requests: `NotFoundError`, provider says
  the project does not have access to `gpt-6.1-sol`.
- Independent Responses API request with the exact same model ID: HTTP 403,
  `model_not_found`, explicitly stating project model access is denied.

No successful inference response, token usage, or behavioral score was obtained.
The full suite did not run. The smoke report's zero index reflects transport
errors and must not be interpreted as model quality. No measured inference cost
can be reported. Reports are excluded from the published baseline manifest.

## Preserved diagnostics

- `results/baselines/openai-gpt-6-1-sol-20261004T224126Z-smoke.json`
- `results/baselines/openai-gpt-6-1-sol-20261004T224126Z-smoke.md`
- `results/baselines/openai-gpt-6-1-sol-20261004T224126Z-usage.json`

The smoke report is signed with the existing local baseline signing key.
The usage sidecar preserves both request failures without credentials.

## Resume

`uv run python scripts/run_sol_env.py` uses `.env`, preserves provider reasoning
and output defaults, runs smoke then the 83-request full quick suite, and stops
before the full phase if smoke contains transport errors. Timeout is 120 seconds
per probe, retries zero, matching the Grok evaluation. Every attempt creates
new report paths. Usage is captured for subsequent pricing analysis; OpenAI
completion tokens include reasoning tokens, so do not add reasoning twice.

The remaining prerequisite is OpenAI project access to `gpt-6.1-sol`.
Do not replace or regenerate the now-authenticating credential as a purported
fix, and do not silently substitute an accessible older Sol model.
Official model reference: https://developers.openai.com/api/docs/models/gpt-6.1-sol
