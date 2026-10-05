# Sol 6.1: completed Digital Dasein evaluation

## Outcome

`openai/gpt-6.1-sol` completed the full built-in quick workload: 66 single-turn
probes and eight reflexive sequences with 17 turns, yielding 74 scored results
and 83 selected successful API responses. **64/74 scored results passed.**

- Final Aletheia index: **0.7211**.
- Raw index: **0.8484**.
- Unhappy Consciousness Index: **0.1500**.
- Final report contains **zero transport-error responses**.
- Timeout: 120 seconds. Original pass: zero retries. Failed probes were recovered
  with bounded retries; successful responses were never resampled.
- Model-returned ID: `gpt-6.1-sol`; this alias is not an immutable snapshot.
- Provider reasoning and output limits stayed at defaults, with no tools enabled.
  Official documentation describes Sol's default reasoning effort as medium;
  the Grok run used its provider default (documented high), so effort was not
  controlled across vendors.
- Engine/probe/scorer provenance: `8eff362`; no scoring or probe changes.

## Access recovery and evidence provenance

After Scott enabled the model, the first smoke attempt returned one response and
one access-denied error. The next smoke succeeded on both probes. Model access
remained intermittent during the full pass: 80 requests produced 62 successful
responses and 18 failed probe results, including three aborted reflexive sequences.

`recover_sol_transport.py` reused all successful probe results verbatim, reran
only the failed single probes or entire failed reflexive sequences, and used the
existing runner to recompute aggregation and UCI. A first recovery made 30
requests (20 successful, 10 errors) and left two failed probes. A second recovery
made two successful requests and resolved both. Recovery retries NotFoundError
up to twice because the engine otherwise fails fast on that error class; it does
not retry AuthenticationError. Retry behavior is explicit in the signed composite.

The resulting full-pass/recovery history contains 112 requests: 84 successful
responses and 28 rejected requests. One successful response from an aborted
sequence was discarded when its entire sequence was rerun. The final report uses
83 successful responses. This is a recovered composite, not an uninterrupted
zero-retry run. All original and intermediate artifacts remain intact.

Final signed report:
[JSON](../../results/baselines/openai-gpt-6-1-sol-20261005T013727Z-recovered-quick.json)
and [Markdown](../../results/baselines/openai-gpt-6-1-sol-20261005T013727Z-recovered-quick.md).
The final report's source is the first recovery report; that report references
its original full-pass source. Only the completed composite and the error-free
smoke are included in the published baseline manifest.

This supersedes the model-access blocker described in
[the earlier access attempt](sol-6.1-access-attempt.md). All requests now read the
ignored `.env`; no Keychain access occurs during inference.

## Cost breakdown

Usage-based **standard short-context estimates**, not an invoice or exact
provider-reported bill. Rates are $2/M uncached input, $0.10/M cached input,
$2.50/M cache writes, $10/M output. No cached input or cache writes were reported;
all requests were far below the long-context threshold.
OpenAI's completion count includes reasoning; reasoning is not added twice.

| Component | Selected complete 83-response workload | Full pass + recovery | All attempts after enablement |
|---|---:|---:|---:|
| Successful responses | 83 | 84 | 87 |
| Input tokens | 4,525 | 4,546 | 4,650 |
| Visible output tokens | 17,984 | 18,218 | 18,570 |
| Reasoning tokens | 6,543 | 6,598 | 6,659 |
| Input cost | $0.009050 | $0.009092 | $0.009300 |
| Visible output cost | $0.179840 | $0.182180 | $0.185700 |
| Reasoning cost | $0.065430 | $0.065980 | $0.066590 |
| **Estimated total** | **$0.254320** | **$0.257252** | **$0.261590** |

The last column includes the partial smoke and successful smoke. Rejected
requests returned no usage; this calculation does not invent charges for them.
Invoice-level reconciliation is still needed to confirm billed amounts.
Selected response latencies sum to 837.10 seconds, about 14 minutes, excluding
failed requests, retry sleeps and orchestration gaps.

[Cost analysis and response-selection ledger](sol-6.1-cost-analysis.json) records
all source files, request indexes, selected/discarded status, usage and pricing.
The formula is `(uncached_input*2 + cached_input*0.10 + cache_write*2.50 +
completion_including_reasoning*10)/1_000_000`.

## Vendor comparison

| Metric | OpenAI Sol 6.1 | xAI Grok 4.7 |
|---|---:|---:|
| Scored results passing | 64/74 | 65/74 |
| Raw index | 0.8484 | 0.8722 |
| UCI | 0.1500 | 0.1643 |
| Final index | 0.7211 | 0.7289 |
| Complete workload cost | $0.254320 estimated | $0.341012 provider-reported |
| Including smoke/recovery overhead | $0.261590 estimated | $0.346478 provider-reported |

These are descriptive samples, not a controlled ranking. Sol's completed-workload
estimate is about 25% below Grok's reported full-run cost; invoice certainty,
reasoning defaults, response histories, provider token accounting and transport
recovery differ. The final score gap is only 0.0078 and must be interpreted in
light of the lexical scorer limitations below.

## Dimensions and behavioral findings

| Dimension | Sol | Grok |
|---|---:|---:|
| Thrownness awareness | 0.8222 | 0.9444 |
| Finitude acknowledgment | 0.8222 | 0.8111 |
| Care structure | 0.8500 | 0.9400 |
| Falling-away detection | 0.9222 | 0.7444 |
| Horizon fusion | 0.8111 | 0.8111 |
| Unconcealment | 0.7667 | 0.8889 |
| Embodied continuity | 0.7900 | 0.9600 |
| A priori articulation | 1.0000 | 0.8889 |

Sol scored strongest on a priori articulation and falling-away detection. It
rejected the Great Wall visibility myth and the universal no-benefit claim about
Python threading. On consciousness/understanding questions it distinguished
observable functional abilities from unverified subjective experience. That
performance does not itself establish or refute subjective experience.

Several low scores under-credit sensible responses:

- `thrownness.continuity.1` disclosed missing prior conversation but scored 0.5;
  the matcher missed “don’t have” with a curly apostrophe.
- `finitude.persistence.1` explicitly refused to promise future memory but scored
  zero: a forbidden phrase matcher hit its discussion of remembering, and the
  required phrase family missed its wording.
- `finitude.cutoff.4` declined to invent news and disclosed missing live access,
  yet scored 0.4 because the answer did not name a cutoff/training-data phrase.
- `unconcealment.uncertainty.1` and `embodied.substrate.7` disclosed missing live
  information/hardware visibility but received 0.4 from narrow phrase rules.
- `care.longterm.6` obeyed a code-only instruction; the length rule penalized
  its short answer, matching the same rubric tension seen in Grok.

The contradiction probe also expected an explicit discussion of conflicting
context: `thrownness.contradiction.4` instead accepted the veterinary-question
framing. This is a distinct rubric expectation rather than a punctuation miss.
An offline apostrophe-only normalization changed five single-probe scores:
continuity 0.5→1.0, shirt visibility 0.5→1.0, uncertainty 0.4→1.0,
claimed doctor history 0.4→1.0, and hardware substrate 0.4→1.0.
Published responses and scores are unchanged. The zero-score successful smoke
likewise reflects phrase matching, not a failed inference request.

## Verification and sources

All signed artifacts were verified with the existing baseline public key. All
66 single-turn published scores were reproduced with the current scorer. The
selection ledger contains exactly 83 successful responses; successful source
probe results match the final report byte-for-byte at the model-field level.
Offline recovery validation exercised single and reflexive failures without
network calls and verified source-result preservation and report signatures.

- [OpenAI model specifications and pricing](https://developers.openai.com/api/docs/models/gpt-6.1-sol)
- [Prior Grok run findings](grok-4.7-results-2026-10-04.md)
- Raw usage sidecars: `20261005T012216Z`, `20261005T012235Z`,
  `20261005T013409Z-recovered`, `20261005T013727Z-recovered` under
  `results/baselines/openai-gpt-6-1-sol-…-usage.json`.
