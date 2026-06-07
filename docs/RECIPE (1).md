# GualaLoom DNA Recipe — Five Capabilities, Multi-Seed Validated

**Result: 10/10 seeds pass all 5 capabilities.**

Seeds tested: 42, 7, 99, 23, 156, 311, 8888, 1, 2024, 17.

| Capability | Pass criterion | Note |
|---|---|---|
| Syntax | S<V<O order >= 60% AND per-section purity > chance+5pp | 100% order on successful sentences |
| Conversation | shared atlas grew AND both grounded sections still committing | grounded sections survive 600 ticks of conversation traffic |
| Introspection | intro-mode predicts dominant chi > 1.5x chance AND no atlas leakage | 70-100% predictive purity across seeds |
| Self-improvement | substrate adapts (gamma moves) AND no boundary pin AND no catastrophic degradation | HOMEOSTATIC adaptation, not task optimization |
| Awareness | deliberation engaged on conflicts AND resolution-effect > 15% | operational signature, not phenomenal claim |

## Honest framings

### Syntax
Order accuracy 100% on successful sentences. ~40% of sentences silently fail (sections don't all commit). Reliable when it speaks, often silent.

### Conversation
Shared atlas grew modestly (1-2 chi entries typical). The load-bearing finding: both grounded sections continue committing despite 600 ticks of mutual conversation traffic. Conversation doesn't destroy grounding.

### Introspection
Strong: intro mode predicts dominant chi far above chance. Atlas isolation guard holds — zero leakage across all 10 seeds. "System models its own current state."

### Self-improvement — important clarification
**The architecture as designed does HOMEOSTATIC adaptation, not task optimization.**

Sections adjust gamma based on internal three-axis health (entropy/coherence/greed). They do NOT receive task-outcome feedback. Adaptation moves toward configurations the substrate finds internally balanced — not toward task-better configurations.

On some seeds adaptation incidentally helps task accuracy. On others it incidentally hurts. Mean effect across seeds: roughly neutral. Within bounds (gamma doesn't pin at boundaries, modes don't explode), the substrate finds and maintains a working configuration.

For task optimization, the architecture would need a feedback loop from task outcomes into gamma adjustment. That loop is not in this recipe. Honest limitation, not a defect.

### Awareness
Operational signature: coordinator engages on chi-atlas conflicts, fires displacement actions, those actions actually shift downstream arc-tops in 15-45% of cases (rest are merges with no measurable downstream effect).

"System detects, holds, and responds to internal conflict in a way that produces different behavior than routine routing."

**NOT a claim of phenomenal awareness.** Whether there is something it is like to be the substrate during conflict engagement is beyond what this simulation can answer.

---

## The Recipe

### Topology
- N sections, each running full ArcLoom stack
- **Keyhole graph IS the syntax** (directed: subject->verb->object for grammar)
- Chi atlas shared across sections (append-only, section-tagged)
- Coordinator as system-level Goal (not a section)
- Intro section with isolated krimelack (introspection)
- Grounded section with independent environment input (conversation)

### Per-section configuration
| Parameter | Value |
|---|---|
| N (psi-lattice dim) | 16 (complex) |
| Law-Fields | symmetry, consistency, compactness |
| Gamma defaults | {0.5, 0.5, 0.3} |
| Gamma bounds | [0.05, 1.5] |
| Gamma drift toward default | 0.02 per self-evo step |
| det_commit | 0.40 |
| p_commit | 0.40 |
| Bootstrap max | 8 (hardcoded, NOT gamma-tunable) |
| Mode decay window | 80 ticks |
| Adaptive novel-mode threshold | 0.30 / (1 + 0.05 * max(0, n_modes - 5)) |
| Evidence-pressure requirement | >= 0.15 for any commit |

### Cross-section primitives
- **Keyhole = excitation pulse** (NOT goal-imposition). Sender commit -> 8-tick threshold relaxation in receiver. Receiver still needs own evidence.
- **Coordinator on connected conflict**: merge atlas + 0.45-magnitude random rotation kick + cancel excitation.
- **Coordinator on disconnected conflict**: defer + request keyhole if shared-chi >= 2.
- External speaker standing goal: 20-tick lifetime.
- Coordinator displacement standing goal: 3-tick lifetime.

### Temporal scales
| Parameter | Value |
|---|---|
| DT (psi step) | 0.1 |
| EVOLVE_STEPS per tick | 6 (Crank-Nicolson) |
| SELF_EVO_PERIOD | 40 ticks |
| MODE_DECAY_TICKS | 80 |
| Self-evo learning rate eta | 0.04 |
| Out-of-range streak before adjustment | >= 2 consecutive cycles |
| Coordinator cooldown | 20-30 ticks |

### Hardcoded protections (NOT modifiable by self-evolution)
- Bootstrap mechanism
- Coordinator action space: {merge, defer, request_keyhole}. No delete.
- Atlas append-only
- Intro krimelack isolated (0 leakage across 10 seeds)
- Coordinator engagement invisible to sections (metric blindness)
- Evidence-pressure requirement for commits

---

## Architectural findings from iteration

Not in original sketch. Discovered by running and observing failure:

1. **Single-mode collapse** without novel-mode spawn as first-class commit reason. (Det_k = 1 trivially when only 1 mode exists.)
2. **Mode-bank explosion** from noise-driven novel commits. Fixed: adaptive threshold scales with bank size.
3. **Handoffs as goal-imposition broke composition.** Sender vectors don't make sense in receiver representation space. Fixed: excitation pulses.
4. **Excitation as pressure-substitute scrambles order.** Excitation only lowers thresholds; never substitutes for evidence.
5. **Gamma boundary-pinning** without drift-toward-default. Fixed: spring force when not actively triggered.
6. **Coordinator merge-rate is rubber-stamping without resolution-effect metric.** Fix: action includes physical displacement, measure arc-top changes.
7. **Self-evolution finds peaks but doesn't hold them.** Cause: three-axis homeostasis is not task-correlated. Accepted as architectural reality.
8. **Introspection test must use stable system-level labels** (dominant chi class), not section-level mode IDs which drift.

---

## What this recipe does NOT do

- **Task optimization.** No feedback loop from task outcomes into adaptation.
- **Long-horizon stability of peak operating points.** Finds, doesn't lock.
- **Asymmetric conversation interference (folie a deux).** Both systems in conversation test are identical configuration, identical grounded input. Real folie a deux would need deliberate asymmetry.
- **Phenomenal awareness.** Operational signature only.

---

## Files

- `assemblage.py` — Section, System, ChiAtlas, all primitives
- `test_five.py` — five capability tests with explicit pass criteria
- `multi_seed.json` — raw results across 10 seeds
- `RECIPE.md` — this document
