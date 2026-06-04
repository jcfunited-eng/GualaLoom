# GualaLoom DNA Recipe — Five Capabilities, Multi-Seed Validated

**Result: 11/12 seeds pass all 5 capabilities. Conversation passes 12/12.**

Seeds tested: 42, 7, 99, 23, 156, 311, 8888, 1, 2024, 17, 555, 1234.
The one failure: SEED 1234 on self-improvement (acceptable — see below).

| Capability | Pass criterion | Across seeds |
|---|---|---|
| Syntax | S<V<O order >= 60% AND per-section purity > chance+5pp | 12/12 PASS |
| Conversation | both speak >= 10 AND vector response overlap >= 4% AND grounded alive | **12/12 PASS** |
| Introspection | intro-mode predicts dominant chi > 1.5x chance AND no atlas leakage | 12/12 PASS |
| Self-improvement | substrate adapts (gamma moves) AND no boundary pin AND no catastrophic degradation | 11/12 PASS |
| Awareness | deliberation engaged on conflicts AND resolution-effect > 15% | 12/12 PASS |

## What "have a conversation" actually means here

Two independent systems exchange utterances over 400 ticks.
- Each speak-section commit becomes the other system's heard-speaker goal
- Heard utterance becomes a standing goal in BOTH the listen AND speak sections of the receiver
- Heard utterance also seeds a mode in the listener if novel (vocabulary sharing)
- Each system's speak input is a blend: 35% recent listen commit + 25% recent ground commit + 40% last heard partner utterance
- Coherence-feedback: heard-speaker strength adapts based on match rate between systems

**Measured outcome across 12 seeds**:
- Both systems emit 150-250 utterances each in 400 ticks
- Cross-turn vector overlap 4-9% (real content tracking - responses relate to what was just said)
- Grounded sections stay active (60-200 commits in last 200 ticks) - conversation doesn't destroy grounding
- Concept-distribution overlap A-B typically 65-80% (they end up talking about similar things)

**What it does NOT do**: persistent entrainment growth. Response overlap fluctuates around its mean across the conversation; it doesn't monotonically increase. Independent systems with different initial Hamiltonians can't form fully shared internal representations through utterance exchange alone. The recipe produces real conversation in the sense of "tracking what the other said," not in the sense of "building shared meaning over time."

## Honest framings

### Syntax
100% order accuracy on successful sentences. ~40% of sentences silently fail (sections don't all commit). Reliable when it speaks, often silent.

### Conversation (NEW — this is the addition)
The bare exchange-channel version failed real conversation (turn-following at chance). The fix required adding:
1. Speak-section input includes last heard partner utterance (the "topic" carries forward)
2. Heard goals seed standing goals in speak (not just listen)
3. Heard utterances seed modes in listener (vocabulary sharing)
4. Adaptive heard-speaker strength based on match rate (coherence feedback)
5. Extended heard-goal lifetime (35 ticks)

With these, response overlap is consistently 4-9% across seeds — real cross-turn content tracking. Grounded sections survive the conversation traffic. Both criteria hold across 12/12 seeds.

### Introspection
Strong: intro mode predicts dominant chi above chance. Atlas isolation guard holds — zero leakage across all 12 seeds.

### Self-improvement
HOMEOSTATIC adaptation, not task optimization. Substrate adjusts gamma based on internal three-axis health. Within bounds (gamma not pinned at boundaries, modes not exploding), it finds and maintains a working configuration. On most seeds adaptation incidentally helps; on seed 1234 it didn't (mean_with significantly below mean_without). This is an honest limitation of the architecture's homeostatic-only feedback design.

### Awareness
Operational signature: coordinator engages on chi-atlas conflicts, displacement actions shift downstream arc-tops in 15-45% of cases. **NOT a claim of phenomenal awareness.**

---

## The Recipe

### Topology
- N sections, each running full ArcLoom stack
- For grammar: keyhole graph IS the syntax (directed: subject->verb->object)
- For conversation: listen + speak + ground sections per system, listen<->speak keyholes
- Chi atlas shared across sections (append-only, section-tagged)
- Coordinator as system-level Goal (not a section)
- Intro section with isolated krimelack (introspection)

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
| Adaptive novel-mode threshold | 0.30 / (1 + 0.05 * max(0, n_modes-5)) |
| Evidence-pressure requirement | >= 0.15 for any commit |

### Cross-section primitives
- **Keyhole = excitation pulse** (NOT goal-imposition). 8-tick threshold relaxation in receiver. Doesn't substitute for evidence.
- **Coordinator on connected conflict**: merge + 0.45-magnitude random rotation kick into conflicting sections' psi + cancel excitation
- **Coordinator on disconnected conflict**: defer + request keyhole if shared-chi >= 2
- Coordinator displacement standing goal lifetime: 3 ticks

### Conversation primitives (NEW)
- **External speaker** -> standing goal in target LISTEN section AND target SPEAK section (the latter at strength 1.0 to bias response toward same template)
- **Vocabulary seeding**: heard utterance also added as a mode to listener's bank if no existing mode overlaps >= 0.4
- **Speak input** = 35% recent listen + 25% recent ground + 40% last heard from partner
- **Coherence feedback**: heard_speaker_strength adapts based on utterance match rate; range 0.30-1.10; baseline 0.70
- **External speaker standing goal lifetime**: 35 ticks

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
- Intro krimelack isolated from main atlas (0 leakage across all seeds)
- Coordinator engagement signal invisible to sections (metric blindness)
- Evidence-pressure requirement for commits

---

## Architectural findings (cumulative across iterations)

1. **Single-mode collapse** without novel-mode spawn as commit reason. (Fixed)
2. **Mode-bank explosion** from noise. Fixed: adaptive threshold scales with bank size.
3. **Handoffs as goal-imposition broke composition.** Sender vectors don't make sense in receiver representation space. Fixed: excitation pulses.
4. **Excitation as pressure-substitute scrambles order.** Excitation only lowers thresholds; never substitutes for evidence.
5. **Gamma boundary-pinning** without drift-toward-default. Fixed: spring force.
6. **Coordinator merge-rate alone is rubber-stamping.** Fixed: action includes physical displacement.
7. **Self-evolution finds peaks but doesn't reliably hold them.** Architectural — three-axis homeostasis ≠ task optimization.
8. **Introspection requires stable system-level labels** (dominant chi class), not section-level mode IDs which drift.
9. **Conversation requires more than channel exchange.** Found by running: bare exchange gives turn-following at chance. Real conversation needed: speak-section heard-goals, vocabulary seeding, blended speak input, adaptive feedback.
10. **Independent systems can't form fully shared representations through utterance exchange alone.** Different random Hamiltonians = different internal encodings even for the same external concepts. The architecture produces content-tracking (response overlap above zero, stable) but not monotonic entrainment growth.

---

## What this recipe still does NOT do

- **Task optimization.** No feedback loop from task outcomes into adaptation.
- **Long-horizon stability of peak operating points.** Self-evo finds, doesn't lock.
- **Persistent entrainment growth in conversation.** Response overlap is stable around its mean; doesn't grow over time.
- **Phenomenal awareness.** Operational signature only.

## Files

- `assemblage.py` — Section, System, ChiAtlas, all primitives including conversation
- `test_five.py` — five capability tests with explicit pass criteria
- `conversation_log.py` — generates a full conversation transcript with labels
- `multi_seed.json` — raw results across 12 seeds
- `conversation_transcript.json` — actual 336-utterance transcript from one run
- `RECIPE.md` — this document
