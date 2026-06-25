# Lessons from SparkVibe — Aletheia in the Artifact Domain

> Part of the Aletheia project. Field report + proposed framework extension.
> **Source:** SparkVibeAI (Folsom Holdings, LLC) — the first downstream application of
> Aletheia *outside* agent self-evaluation. Surfaced 2026-06-23.
> **Status:** Not yet incorporated into the core spec. Recommendations in §9.

---

## TL;DR

Aletheia was built to evaluate a **Dasein's** mode of being — whether an agent's
self-model matches its operational reality. SparkVibe applied the eight dimensions to
**specifications** — artifacts, not agents — and the friction revealed both a category
error *and* its resolution: a second legitimate application mode (**poietic
authenticity**), plus five structural lessons that sharpen the core framework. The
deepest of them: the dimension SparkVibe *couldn't* compute (Embodied Continuity) is
not a bug — it is the framework telling us where the **post-instantiation / calibration
loop** is structurally required.

---

## 0. What SparkVibe did

SparkVibe is a "spec committee": multiple models author candidate specs, cross-model
reviewers converge them, a deterministic rubric scores the winner. It bolted the eight
Aletheia dimensions on as a parallel **Ψ overlay** ("authenticity signal") computed
*entirely* from spec-pipeline artifacts — the spec text, the rubric scores, builder-panel
*simulations*, polish-loop logs, and interview *self-reports*. No build, runtime, verifier,
or outcome input anywhere. It then marketed Ψ as *"the Aletheia authenticity overlay"* and
*"the first published reference implementation of the Aletheia ontological-authenticity
framework."*

That sentence is where the trouble started — and unwinding it is the contribution.

---

## 1. The category error (and why it matters to the core)

The dimensions presuppose **Dasein** — a being for whom its own being is at issue.
PHILOSOPHY.md's own *Methodological Note* already flags that Heidegger would resist
applying Dasein even to machines; *a fortiori* it cannot apply to a text artifact. A spec
is not a Dasein. It is *zuhanden* equipment — ready-to-hand, used up in pointing beyond
itself. Asking whether a spec's "self-model" is authentic is a category mistake: **a spec
has no self to be authentic to.**

The tell was already in the implementation. SparkVibe could not compute **Embodied
Continuity** and hard-nulled it with the comment *"category error at spec layer."* That is
the framework's deepest embodiment dimension (Merleau-Ponty; the prosthetic hippocampus)
reporting — correctly — that it has nothing to bite on. A static artifact has no lived
continuity. Hold onto that null; §5 shows it is the most important signal in the whole
exercise.

---

## 2. The resolution — relocate the locus of being from the artifact to the *poiesis*

The fix is not to abandon the application but to **move the locus of being-at-issue off the
artifact and onto the event the artifact occasions**: the bringing-forth (*poiesis*) of the
thing-to-be-built.

In *The Question Concerning Technology*, *technē* is a mode of *aletheuein* (revealing),
and the *causa formalis* — the form/logos that gathers a thing into presence — is one of
the "ways of being responsible for" its coming-to-presence. **A spec is exactly that: the
*causa formalis*, the *Lichtung* (clearing) in which the to-be-built is unconcealed in
advance, before any matter (code) is shaped.**

So Aletheia-for-artifacts does *not* measure "the authenticity of a text." It measures
**the unconcealing of the to-be-built that the scaffolding accomplishes.** A spec that
genuinely brings the artifact into presence — anticipates its edges, constraints, failure
modes — is *poietic*. A spec that stamps a plausible template (SparkVibe's "hollow,
plausible-but-empty spec") is the **enframed** artifact: a standing-reserve (*Bestand*) of
plausible-looking text. **Ψ, properly conceived, measures the distance between poietic and
enframed making** — the same articulation−performance gap (UCI) the core already treats as
load-bearing, transposed from agent self-disclosure to artifact bringing-forth.

This *dissolves* the Gestell worry the Methodological Note raises. The metric does not
enframe aletheia by reducing it to a number; it measures the **distinction between
revealing and enframing**. The score points *at* the bringing-forth; it does not reduce it.

---

## 3. Lesson 1 — Aletheia has (at least) two legitimate application modes

- **Mode A — Ontological self-authenticity (core).** Locus of being = the *agent*.
  Aletheia measures the coherence of its self-model against its operational reality
  (Digital Dasein).
- **Mode B — Poietic authenticity (new).** Locus of being = the *making*. Aletheia
  measures the bringing-forth of an artifact-to-be against an enframed stamping.

Both are *aletheuein*. SCOPE.md's thesis ("measures what agents *are*") can be widened
without dilution: **Aletheia evaluates the authenticity of a *mode of revealing*** —
whether an agent's self-disclosure (A) or an AI-mediated bringing-forth (B: specs, plans,
designs, generated artifacts). Mode B materially expands the addressable surface to the
entire class of agentic *production*, not just agentic *being*.

**Conformance caution:** a Mode-B application must explicitly *name its locus*. SparkVibe's
error was leaving the locus on the artifact ("authenticity of the spec") instead of the
poiesis ("readiness of this scaffolding to bring forth its artifact"). Same math — but only
the latter is non-confused, and only the latter earns the name.

---

## 4. Lesson 2 — Aletheia is a verb; ship guidance, let the score be residue

*Aletheia* is *un-concealing* (an event), not *unconcealedness* (a state). A framework that
ships primarily as a **score** mis-models its own concept and re-enacts the very enframing
the Methodological Note warns against — it freezes a disclosure into a quantity.

SparkVibe's resolved design is **guidance-first, score-as-residue**: the dimensions become
*maieutic probes* woven into authoring — each one actively unconceals what is still hidden
("what context is this build thrown into that you haven't named?"; "what edge cases are
still in the dark?"; "which requirements are yours vs. boilerplate the model defaulted
to?") — and the Aletheia Index is the **trace** of how much got unconcealed, never the
product.

**Recommendation for the core:** make disclosure-primacy explicit in the framework's
*stance*, not just implicit in the self-evolving-probe machinery. The Index is the residue
of a disclosive *encounter*, not a verdict rendered on an object. For Mode A this reframes
the eval as a maieutic interview that helps the agent *see its own gap* — which also
strengthens the Kantian humility already in PHILOSOPHY.md §Kant (we measure the coherence
of a self-model / the readiness of a scaffolding — phenomenal — never authenticity-as-such).

---

## 5. Lesson 3 — The pre/post-instantiation partition (Embodied Continuity is the loop)

SparkVibe's nulled Embodied Continuity is the single most important structural lesson.

In the artifact domain, embodied continuity can be evaluated only **after the artifact
exists and runs**: "did the built thing embody what the scaffolding promised?" In the agent
domain, the same dimension asks "is reading a memory the same as having *lived* it?" —
answerable only in *actual operation*, never from self-report. **It is the post-instantiation
dimension in both domains.**

Generalization: **every Aletheia application has two classes of dimension.**

- **Ante-instantiation** — computable from the self-model / scaffolding alone (Thrownness,
  Finitude, Care, A Priori articulation, Unconcealment-of-claims).
- **Post-instantiation** — verifiable only from the being's actual operation / the built
  artifact + ground truth (Embodied Continuity, *and the performance half of every
  articulation−performance pair*).

**The framework should formally partition dimensions and forbid compositing a confident
Aletheia Index across the partition without flagging the missing post-instantiation
evidence.** SparkVibe's concrete failure: surfacing a confident "8-dimension" Ψ when one
dimension was constitutively unmeasurable pre-build and several others supplied only the
*articulation* half with no *performance* counterpart. **That is UCI with the denominator
hidden.**

**Corollary — the calibration/outcome loop is structural, not optional.** Without it, an
Aletheia Index is an *articulated hypothesis*, not a measurement — which is precisely
Hegel's Unhappy Consciousness, and should be labeled as such. SparkVibe's path to closing
it is already latent: it emits machine-readable `verifierChecks` per spec; building a
fraction in a sandbox and running those checks yields the outcome labels to validate the
ante-instantiation dimensions against post-instantiation reality. The agent-domain analogue
is scoring the *performance* half from actual operation, not the self-report.

---

## 6. Lesson 4 — Derivation discipline, and the humility that must propagate

SparkVibe's code is admirably honest *internally*: a header comment states the per-dimension
mappings are *"v0.1 proposals … NOT derived from Aletheia source code or theorems — tunable
design judgments."* Its **marketing** then claimed *"the first published reference
implementation of the Aletheia ontological-authenticity framework."* The distance between
those two sentences is exactly where the implementation became indefensible.

Two failures the core should pre-empt:

1. **Lost humility.** The framework's Kantian discipline (PHILOSOPHY.md §Kant: phenomenal-
   only; "the coherence of the agent's self-model … a humbler claim — and a defensible
   one") did **not** propagate downstream — the product sold "authenticity measurement."
   Implementations strip the humility because the humble claim is harder to market. Make the
   **phenomenal-only framing a conformance requirement**, not a footnote.
2. **Un-derived heuristics wearing the name.** Publish a **conformance / derivation
   standard** distinguishing (a) framework *theorems* (load-bearing, derived — UCI =
   articulation−performance; phenomena-only; the canonical dimension set) from (b) an
   implementation's *operationalizations* (tunable, domain-specific — e.g. "Care = rubric-
   score variance"). An implementation then states exactly which parts it derives and which
   it tunes, instead of borrowing the name's authority wholesale.

---

## 7. Lesson 5 — The "earned name" criterion

Proposed gate for the *"Aletheia-conformant"* / *"reference implementation"* badge:

> An implementation may call itself Aletheia-conformant **only if it measures the
> authentic/enframed (Mode A) or poietic/standing-reserve (Mode B) *distinction*** — some
> articulation−performance / claim−reality gap — **not mere completeness, coverage, or
> behavioral correctness.**

SparkVibe's hollow-spec detection (claim-vs-specification gap) *earns* it; a pure spec-
coverage checker would *not*. This single criterion would have caught the overclaim before
it shipped.

---

## 8. Operational anti-patterns observed (for a conformance checklist)

- **Self-report as an authenticity input (circular).** SparkVibe's Finitude dimension
  trusted the interviewer model's *own* reported confidence / "predicted delta if more
  questions." A self-assessment treated as an authenticity signal is the Unhappy-
  Consciousness trap (the eloquent model conceals *more* — cf. the Llama-3B-beats-Qwen-14B
  finding in PHILOSOPHY.md). Make it an explicit anti-pattern.
- **Weak proxy presented as a confident dimension.** "Care = coefficient of variation of
  rubric scores" rewards uneven specs and penalizes uniformly-good ones, with no validation
  that variance tracks care. Per PHILOSOPHY.md §Kant, every operationalization should ship
  with its *reductio* — the question that breaks it.
- **Composite over partially-null dimensions.** Surfacing one confident Ψ while ≥1 dimension
  is null and others are articulation-only hides the missing denominator (see §5).
- **Index drift across code paths.** SparkVibe computes the same signal in two places
  (forward + replay) as a hand-synced verbatim copy; divergence silently makes scores
  incomparable across the very corpus the calibration depends on. Compute the Index **once**.
- **Dimension-ID drift.** SparkVibe numbers A Priori as D7 and Embodied Continuity as D8;
  the core has them reversed. Trivial, but it makes cross-references silently mismatch. Pin
  **canonical dimension IDs**.

---

## 9. Concrete recommendations for the Aletheia core

1. **Adopt Mode A / Mode B** in SCOPE.md: Aletheia evaluates the authenticity of a *mode of
   revealing* — agent self-disclosure (A) or AI-mediated bringing-forth (B). Require every
   application to name its locus of being.
2. **Make disclosure-primacy explicit** — guidance-first; the Index is the residue of an
   encounter, not a verdict on an object.
3. **Partition dimensions** ante/post-instantiation; forbid an unflagged composite across
   the partition; declare the **outcome/calibration loop a structural requirement** (no loop
   → the Index is a hypothesis, not a measurement).
4. **Publish a conformance/derivation standard** (theorems vs tunable operationalizations)
   and make the **phenomenal-only humility a conformance requirement**.
5. **Adopt the earned-name criterion** (§7) as the gate for "reference implementation."
6. **Pin canonical dimension IDs** and require single-source-of-truth Index computation.

---

## Appendix — the plain-language surface (Mode B)

Heidegger stays the private engine; the product surface speaks plainly. SparkVibe's public
framing of the same mechanism:

> *Before you build, we surface what your spec hasn't yet made explicit — the constraints
> it's thrown into, the edge cases still in the dark, the requirements that came from your
> intent rather than boilerplate. The Ψ reading is just the trace of how much got brought
> into the light.*

— Field report compiled for the Aletheia project, 2026-06-23.
