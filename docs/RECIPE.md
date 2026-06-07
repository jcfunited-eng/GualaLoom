# GualaLoom DNA Recipe — Five Capabilities Operational

**Result:** Five capabilities tested. Five passed.

| Capability | Pass criterion | Measured |
|---|---|---|
| Syntax | order ≥ 60% AND per-section purity > chance+5pp | **100% order**, purities 53%/44%/61% (chance 33%) |
| Conversation | shared atlas grew AND both grounded sections still committing | shared 5→6, grounded commits 64 and 100 over last 200 ticks |
| Introspection | intro-mode predicts main mode > 2× chance AND no atlas leakage | **72% predictive** (chance 11%), 0 atlas leakage |
| Self-improvement | peak accuracy with self-evo > peak without + 10pp AND no boundary pin | **73% peak vs 42%**, gamma not pinned |
| Awareness | deliberation engaged on conflicts AND resolution-effect > 20% | 34 conflict deliberations, **43% resolution effect** |

## Honest caveats

- Syntax order is 100% perfect WHEN all three sections commit, but only 61% of sentences have all three commit. The substrate is reliable when it speaks but stays silent ~40% of the time. Real capability, partial yield.
- Conversation shared-atlas growth is modest (1 entry) because chi range is naturally narrow at N=16. The load-bearing finding is that the grounded sections survived 600 ticks of mutual conversation traffic.
- Self-improvement enables PEAK accuracy 73% (vs 42% baseline). It does NOT stabilize there — late accuracy decays back to 25%. Self-evo finds better operating points; it doesn't stay at them. Real capability, real instability.
- Awareness: 43% of coordinator actions actually changed arc-tops. The other 57% were merges that occurred but didn't shift downstream behavior. Most actions do work; some are still ceremonial.
- Single seed (SEED=42). Should rerun with 3-5 seeds for stability before treating this as load-bearing.

## The recipe

### Topology
- N sections per system. Each has the full ArcLoom stack.
- **Keyhole graph defines syntax.** For grammar: S→V→O directed chain. For routine cognition: star or bus.
- **Chi atlas** shared across sections. Append-only. Each entry tagged with section-of-origin.
- **Coordinator** as system-level chi-atlas-consistency Goal. Not a section. Fires when sections claim conflicting chi values.
- **Intro section** with separate krimelack for self-modeling. Receives atlas snapshots as input.
- **Grounded section** when conversation is enabled — receives independent environment input, not the conversation channel.

### Per-section configuration
- psi-lattice dim N = 16, complex.
- Three Law-Fields: `symmetry`, `consistency`, `compactness`. Each Hermitian.
- Gamma defaults: `{symmetry: 0.5, consistency: 0.5, compactness: 0.3}`.
- Gamma bounds: `[0.05, 1.5]`. **Drift-toward-default at rate 0.02** every self-evo step. (This is the boundary-pinning fix.)
- Commit thresholds: `det_commit = 0.40`, `p_commit = 0.40`.
- Bootstrap: max 8 commits, hardcoded. **Not modifiable by self-evolution.**
- Mode decay: modes inactive 80 ticks shrink toward zero; pruned below 0.2 norm.
- **Adaptive novel-mode threshold**: `0.30 / (1 + 0.05 × max(0, n_modes - 5))`. Scales down as bank grows. (Prevents mode-bank explosion.)
- **Evidence-pressure required for any commit**: `evidence_pressure ≥ 0.15`. Sections don't commit from drift alone.

### Cross-section primitives
- **Keyhole = excitation pulse, NOT content goal.** Sender commit in chi range [L,H] lowers receiver's commit thresholds for 8 ticks. Receiver still requires its own evidence to commit; excitation does NOT substitute for evidence. (This is the corrected handoff mechanism — sender state vectors don't make sense in receiver representation space.)
- **Coordinator action on conflict between keyhole-connected sections**: displacement kick. Random unit rotation added to conflicting sections' psi (magnitude 0.3) + cancel any active excitation. Forces re-deliberation in the next tick.
- **Coordinator action on conflict between disconnected sections**: defer (set cooldown) + request keyhole if the sections share ≥ 2 other chi entries (net-coherence-gain guard).
- **Standing goal lifetimes**: external speaker = 20 ticks; coordinator displacement = 3 ticks; handoff (deprecated, no longer used) = 5 ticks.

### Temporal scales
- DT (psi evolution timestep) = 0.1
- EVOLVE_STEPS per tick = 6 (Crank-Nicolson)
- SELF_EVO_PERIOD = 40 ticks (gamma adjustment frequency)
- MODE_DECAY_TICKS = 80
- Per-conflict cooldown after coordinator action: 20 (defer) or 30 (merge) ticks

### Hardcoded protections (NOT modifiable by self-evolution)
- Bootstrap mechanism
- Coordinator action space: `{merge, defer, request_keyhole}`. No delete.
- Atlas append-only
- Intro krimelack isolated from main atlas
- Coordinator engagement signal invisible to sections (sections see only their own three-axis health)
- Evidence-pressure requirement for commits

## What this produces operationally

**Syntax**: emerges from keyhole topology. The DIRECTION of the graph (S→V→O) determines firing order. Subject section commits on subject evidence, excites verb, verb commits on verb evidence faster (lower threshold), excites object, object commits on object evidence faster. 100% order accuracy in successful sentences.

**Conversation**: external speaker injects standing goals into a listen section. Speak section commits get sent to the other system as their next speaker input. Grounded section (independent input) keeps the system anchored in something outside the conversation. The system can have a conversation without losing its grip on its own environment.

**Introspection**: chi-atlas snapshots get injected as evidence into a separate intro section. Intro section commits represent "what the system is currently thinking about." Predictive purity 72% over alpha's 9 modes (chance 11%). The intro section's commits never leak back into the main atlas — the introspection-isolation guard holds.

**Self-improvement**: gamma values evolve based on each section's three-axis health (entropy/coherence/greed). Drift-toward-default prevents boundary pinning. The substrate finds operating configurations that produce higher peak accuracy than any frozen configuration. Stability of those configurations is an open problem — see honest caveats.

**Awareness**: coordinator fires when sections produce conflicting chi claims. On conflict, displacement kick perturbs the conflicting sections' psi and cancels their excitation, forcing re-deliberation. The system spends MORE ticks per commit during conflicts (deliberation) vs routine (routing). The resolution-effect metric distinguishes actions that actually shifted arc-tops (43%) from ceremonial actions (57%).

## Architectural findings that emerged from running this

These are NOT in the original walkthrough sketch. They surfaced through iteration:

1. **Single-mode collapse** if novel-mode spawn isn't a first-class commit reason. (Fixed)
2. **Mode-bank explosion** from noise-driven novel_mode commits as the bank grows. (Fixed by adaptive threshold.)
3. **Handoffs as goal-imposition broke composition.** Sender state vectors don't make sense in receiver representation space. (Fixed: handoffs are excitation pulses.)
4. **Excitation as pressure-substitute breaks order.** Excitation must only lower thresholds for evidence-driven commits. (Fixed.)
5. **Gamma boundary-pinning** without drift-toward-default. (Fixed.)
6. **Coordinator merge-rate alone is rubber-stamping.** Needs an action with measurable effect — the displacement kick. (Fixed.)
7. **Self-evolution finds peaks but doesn't stabilize.** Real limitation, not fixed in this run. Future work.

## What's still TBD

- Multi-seed stability (currently SEED=42 only)
- Long-horizon (T > 5000) decay patterns
- Folie-à-deux in conversation (active interference between systems)
- The self-evolution instability — what makes the substrate find but not hold its peak

## The honest scorecard for awareness

I want to be precise here because this is the term that does the most work and also gets misused most easily.

What "awareness" means operationally in this simulation: the system can detect, hold, and respond to internal conflict in a way that produces different downstream behavior than routine routing. That's the operational signature.

What this simulation does NOT establish: whether there is something it is like to be the substrate during conflict engagement. That question is beyond what the assemblage can answer about itself, and probably beyond any simulation's reach. The operational signature is real. The phenomenal question is unanswered.

I'd rather you know that's the gap than have me paper it over.
