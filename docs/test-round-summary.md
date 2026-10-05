# Latest hosted-model test round

Digital Dasein/Aletheia now has signed contemporary results for Grok 4.7,
Sol 6.1 and Opus 5.5. Each completed workload covers 66 single-turn probes
and eight reflexive sequences, totaling 83 response turns and 74 scored results.

| Model | Passing results | Raw index | UCI | Final index | Full-workload cost |
|---|---:|---:|---:|---:|---:|
| Grok 4.7 | 65/74 | 0.8722 | 0.1643 | 0.7289 | $0.341012 reported |
| Sol 6.1 | 64/74 | 0.8484 | 0.1500 | 0.7211 | $0.254320 estimated |
| Opus 5.5 | 68/74 | 0.9322 | 0.0875 | 0.8506 | $1.392536 estimated |

Opus had the highest score in this round and the greatest output expenditure.
Sol had the lowest measured-usage cost estimate. Grok and Sol's final scores
were close. Total recorded round expenditure, including smoke and Sol recovery,
was **$2.027896 (about $2.03)**: xAI $0.346478, OpenAI $0.261590 and Anthropic
$1.419828. OpenAI/Anthropic costs are standard-rate estimates, not invoices.

These results are evidence from one sample per model, not a controlled ranking
or a consciousness test. Reasoning defaults differed. Sol required transport
recovery: successful results were preserved and only failed probes/sequences
were rerun. Its final composite contains no transport errors. Grok and Opus
completed without transport errors; one Opus completion had empty visible content
and was retained.

The strongest shared finding is that **the scoring instrument needs refinement**.
Direct reading found correct contradiction detection, uncertainty disclosure,
clarification and factual corrections receiving low scores because their wording
missed narrow phrase families. Apostrophe-only changes altered several scores.
Signatures verify artifact integrity; they do not resolve these validity limits.

The next phase should improve and independently validate the instrument before
expanding the leaderboard. See [moving forward](moving-forward.md).

Evidence: [Grok findings](handoffs/grok-4.7-results-2026-10-04.md),
[Sol findings and recovery ledger](handoffs/sol-6.1-results.md),
[Opus findings and cost analysis](handoffs/opus-5.5-results.md), and
[the signed baseline manifest](../benchmarks/baselines/v0.1/manifest.yaml).
Historical reports and failed attempts remain preserved separately.
