# Grok 4.7 evaluation — blocked at authentication preflight

## Requested run

Run `xai/grok-4.7` through the built-in Aletheia suite, report findings, and
retain the run artifacts in the repository. Intended settings: `quick`,
120-second timeout per request, zero retries, and the existing local Ed25519
baseline signing key. The full suite has 83 requests: 66 single-turn probes
and 17 turns across 8 reflexive sequences.

## Observed preflight result

- The working tree was clean before preflight.
- Aletheia settings loaded an xAI credential from the repository's `.env`
  using the supported `xAI_API_Key` spelling. No process-level xAI key override
  was present. The value was not an obvious example placeholder.
- The existing local baseline signing key was present.
- Two read-only `GET https://api.x.ai/v1/models` attempts returned HTTP 400.
  The second inspected the provider's structured error:
  `code: invalid-argument`, `error: Incorrect API key provided. You can obtain
  an API key from https://console.x.ai.`
- No inference requests were made. No model availability, LiteLLM routing,
  model behavior, score, or inference cost was established by this preflight.
- No benchmark report or baseline manifest entry was created: an authentication
  failure is not a zero-scoring model result.

## Resume

Replace the invalid xAI credential in `.env` locally; do not put it in chat,
Git, a board note, or a report. Recheck the model-list endpoint, then run a
small signed smoke evaluation before the full suite. Preserve usage metadata
for actual cost reporting if possible, and save new reports at distinct paths.
Verify signatures and the baseline manifest before committing the successful
run data. Preserve the existing historical baselines.

The latest estimate and its limitations remain in
[the offline cost analysis](shadow-cost-2026-10-04.md). No paid evaluation was
completed in this attempt.
