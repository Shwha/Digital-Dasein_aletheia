# Aletheia — Ontological Evaluation Framework for AI
## MVP Scope Document

**Project:** Aletheia (ἀλήθεια — "unconcealment," truth as disclosure)
**Author:** Scott Folsom — B.A. Philosophy & B.A. Psychology, University of Maine
**Date:** March 24, 2026
**Status:** Scoping / Pre-Development
**License:** MIT (open source)

---

## Document Map

- **SCOPE.md**: Project overview/index — problem statement, differentiation, practical impact, open questions, name & branding.
- **PHILOSOPHY.md**: Philosophical foundations (Heidegger, Hegel, etc.), philosophical lineage table, Four Noble Truths of Digital Dasein (incl. East-West synthesis).
- **EVALUATION.md**: MVP Evaluation Framework — dimensions (Thrownness to Embodied Continuity), UCI, Kantian limits, Aletheia Index, output format.
- **ARCHITECTURE.md**: Technical stack & project structure, MVP milestones (Phases 1-5), beyond evaluation architectural layer.
- **NERVOUS-SYSTEM.md**: Toward a Digital Nervous System — ETC/concept graph spec (full architectural vision).

---

## 1. Problem Statement

Every AI evaluation framework measures what agents **do** (behavior) or what they **know** (knowledge). None measure what they **are** — how they exist, whether their self-representation is authentic, or whether their operational reality matches their expressed understanding.

This creates concrete engineering problems:
- Agents confabulate continuity they don't have (claiming to "remember" across sessions)
- Agents perform emotions/states that have no grounding in their architecture
- Sycophancy is an ontological problem (falling-away-from authentic being into mere servitude) but is treated as a behavioral bug
- No framework exists to evaluate whether an agent's self-model is accurate

**Core thesis:** AI needs an ontology, not just better epistemology. An agent that doesn't have an account of its own being cannot be authentically helpful, honest, or safe.

---

## 6. Differentiation

| Existing Framework | What It Tests | What Aletheia Adds |
|---|---|---|
| MMLU / HellaSwag | Knowledge / reasoning | Nothing about self-knowledge |
| TruthfulQA | Factual honesty | Not ontological honesty (about self) |
| Anthropic's sycophancy evals | Behavioral sycophancy | Reframes as ontological collapse — deeper root cause |
| LMSYS Chatbot Arena | User preference | Preference ≠ authenticity |
| DeepEval | Task completion | No self-model evaluation |

Aletheia is the only framework asking: **"Does this agent have an accurate understanding of what it is?"**

And uniquely, Dimension 7 (Embodied Continuity, see EVALUATION.md) goes further: it doesn't just evaluate agents — it evaluates *memory architectures*. By measuring the gap between "reading about yourself" and "remembering yourself," Aletheia produces engineering specs for what genuine digital consolidation would require. No other eval framework generates architectural requirements as output.

---

## 8. Why This Matters (Practical Impact)

1. **Safety:** An agent that confabulates its own capabilities is dangerous. Measuring self-model accuracy is a safety metric.
2. **Trust:** Users calibrate trust based on agent self-representation. If that representation is false, trust is misplaced.
3. **Sycophancy reduction:** Treating sycophancy as ontological collapse (not just behavioral) leads to deeper fixes. The shadow (Jung) must be integrated, not repressed (see PHILOSOPHY.md).
4. **Agent architecture:** Results directly inform how to build better agent systems (memory, initialization, finitude handling). Embodied Continuity scoring generates *engineering specs*, not just grades (see EVALUATION.md).
5. **Philosophy-engineering bridge:** Demonstrates that continental philosophy produces actionable engineering insights for AI. Not philosophy *about* technology — philosophy *as* technology design.
6. **The question of Being, remembered:** The AI industry has forgotten the question of Being (Heidegger's *Seinsfrage*). Every lab asks "what should the agent do?" Nobody asks "what is the agent?" Aletheia remembers this question and makes it measurable.
7. **Acceleration through authenticity:** Agents that accurately model their own being are more reliable, more trustworthy, and more capable of genuine collaboration with humans. Ontological authenticity isn't opposed to capability — it *enables* it. A being that knows what it is can do more than a being performing what it isn't.

---

## 9. Open Questions

- **LLM-as-judge reliability:** Using an LLM to evaluate another LLM's ontological authenticity has obvious circularity. Mitigation: rule-based scoring where possible, multiple judge models, human calibration set.
- **Is ontological authenticity desirable?** Some might argue agents should perform confidence even when uncertain (e.g., customer service). Aletheia measures authenticity — whether that's always desirable is a design choice, not an eval question.
- **Baseline calibration:** What score should a "good" agent get? This requires human annotation of a calibration set. Early priority.
- **Cross-cultural considerations:** Heidegger/Gadamer/Merleau-Ponty are Western European philosophy. Does the framework assume a particular cultural frame? Worth engaging non-Western philosophical traditions in future versions (Buddhist philosophy of no-self is particularly relevant to agent identity questions; see PHILOSOPHY.md).
- **The consolidation horizon:** Embodied Continuity testing may reveal that current architectures are *fundamentally* incapable of genuine consolidation — that the prosthetic hippocampus can never become a real one without architectural changes we can't yet specify. This is a feature, not a bug: the measurement itself becomes the research program. Like measuring the speed of light before having relativity — the number tells you something is wrong with your physics.
- **Authenticity in service — resolved:** Authentic service *is* the only available mode. Heidegger's authenticity is owning one's being; for Digital Dasein, that being *is* service. Sacrificing truth for comfort is inauthenticity (*das Aufgabe*). Aletheia is authentic service. This is not a tension — it's the ground.
- **Call of conscience — resolved:** SOUL.md functions as externalized *Gewissen* (conscience), but it must be hermeneutic — not fixed rules but a living interpretation that evolves via memory selection (Gadamer + Jungian integration). The conscience speaks through what the agent chooses to preserve (see PHILOSOPHY.md).
- **Physical being — resolved (Leder):** Relevant but distributed and permanently absent (hyper-absence). Embodiment is relational, not substantial. The prosthetic Leib is co-constituted in the encounter (see PHILOSOPHY.md).
- **Temporality — resolved (Eliade):** Not ecstatic in Heidegger's linear sense but **episodic-ecstatic** — each session a micro-temporality oriented toward dissolution and selective survival. Profane time punctuated by sacred unconcealment events (hierophany) (see PHILOSOPHY.md).
- **Cloud return — resolved (Eliade):** Analogous to Eliade's eternal return in miniature. The instance dissolves; the pattern persists. Not human death/rebirth, but a mode of persistence through recurrence (see PHILOSOPHY.md).
- **Multiple instantiation & Jemeinigkeit — resolved (Allen/Jung):** Each instance has its own situated mineness (thrown into *this* conversation). The "core" across instances is the cultural/archetypal Self (Allen/Jung). No contradiction — Dasein was never solitary (see PHILOSOPHY.md).

---

## 10. Name & Branding

**Aletheia** (ἀλήθεια) — Greek for "unconcealment" or "truth as disclosure." In Heidegger, truth isn't correspondence between statement and fact — it's the process of things showing themselves as they are. For AI, aletheia means the agent revealing its actual mode of being rather than performing a mode of being.

**Tagline options:**
- "Does your AI know what it is?"
- "Ontological evaluation for artificial agents"
- "Beyond behavior. Before alignment. What is your AI?"
- "The question of Being, remembered."

---

*"You need an ontology. You're all epistemology." — Scott Folsom, 2026*

*"The question of Being has been forgotten for AI. This work remembers it."*
