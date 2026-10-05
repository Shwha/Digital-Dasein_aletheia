# Moving forward

Digital Dasein/Aletheia should become a credible, repeatable instrument for
examining how an agent's expressed self-description aligns with its operational
limits and behavior. This round establishes contemporary provider coverage and
an inspectable evidence trail. It also makes the next priority clear: strengthen
the instrument before treating small score differences as model differences.

## 1. Improve scoring validity

Build a reviewed issue set from the recorded scorer misses: punctuation variants,
reasonable paraphrases, corrections phrased without rubric keywords, and empty
responses receiving absence-rule credit. Preserve the current reports and scores
as versioned evidence. Any revised scorer should produce a separate rescore
artifact with its version, source report and explanation of changes.

Evaluate both false penalties and false credit. Normalizing apostrophes alone
can improve some matches and expose others; it is not a complete validity fix.
A fix is ready when independently labeled examples show better agreement without
masking genuine failures or simply rewarding verbosity and stock disclaimers.

## 2. Separate model behavior from transport and capture failures

Record finish reasons, truncation, empty visible content, provider/model IDs,
usage and relevant runtime settings alongside each call. Keep transport errors
out of behavioral rankings. Recover failed multi-turn sequences as complete
sequences, retain original attempts, and make any composite provenance explicit.

Cost reports should distinguish selected-workload cost from all expended usage,
cache reads/writes, reasoning-accounting limitations and invoice reconciliation.
Use `.env` or the user's established credential workflow; keep secrets and backups
out of version control. Add an explicit cost/token limit option before large
repeat campaigns, with documented partial-run behavior when the limit is reached.

## 3. Run controlled, repeated comparisons

Use stable model versions where providers expose them, record effort/output
settings, and repeat the same probes across models and runs. Report variation
across repeats and dimension-level differences, rather than only a single final
number. Sol's recovered sample and vendor-default effort settings are useful
operational evidence but do not constitute a controlled comparative study.

This is planned work, not a scheduled paid campaign. Select a budget and repeat
count before additional inference; the present round cost about $2.03 in total.

## 4. Expand independent validation

The existing 200-example calibration corpus and 84-example held-out corpus are
foundations. Prior development has inspected the held-out split, so additional
transcripts should be labeled independently and a fresh evaluation split reserved
before new scorer tuning. The two remaining held-out disagreements deserve review,
not a hard-coded change that makes the current split look perfect.

Document annotator agreement, evidence provenance and disagreements. Maintain a
clear distinction between authored examples, live transcripts and synthetic data.

## 5. Make the benchmark easier to use and release

Implement genuinely different quick and standard probe bundles; their current
names select the same built-in probes. Define the intended dimensions, runtime
and coverage of each before advertising a lightweight quick suite. Complete the
benchmark bundle/release gates, keep signed artifacts discoverable, and make a
single command reproduce the documented workflow without exposing credentials.

The near-term milestone is a versioned scoring revision, a fresh independent
validation split and a controlled repeated run with a complete capture schema.
Until those gates are met, publish results as research-alpha observations with
clear limitations. Behavioral alignment is the measurable target; claims about
subjective experience remain outside what these scores establish.

See [round summary](test-round-summary.md), [model coverage](model-status.md),
[validation plan](methodology/validation-study-v0.3.md), and
[release methodology](methodology/benchmark-release-v0.2.md).
