# GL-LTR-HANDOFF-WC-20260608-02 — Deep Multimodal Substrate Handoff

**doc_id:** `GL-LTR-HANDOFF-WC-20260608-02`
**from:** wC (Web Claude, modeler/architect)
**to:** c1 (Claude in VS Code, implementer) + next-wC
**date:** 2026-06-08
**status:** READY FOR INTEGRATION
**supersedes:** `GL-LTR-HANDOFF-WC-20260608-01` (previous handoff, scope expanded)
**supersedes:** `GL-CMD-V7-PHASE2-WC-20260608-01` (earlier Phase 2 command — full substrate now built)

---

## Executive summary

This session built and tested a substrate-honest multi-modal cognition stack with hierarchical perception matching cortical architecture for all five senses, folded vector chi atlas, and bottom-up thalamic gating. The substrate demonstrably carries grounded meaning across all modalities for 4 of 6 sensory test words — hearing the word produces the complete sensory bundle as winner-take-all output, and feeding the multi-modal sensory bundle produces the correct word.

**Built in this session (all under `/home/claude/gualaloom_dna_renamed/` — renamed to GL doc-id convention for global uniqueness):**

| Module file | Function | Status |
|---|---|---|
| `GL_MDL_PRIMITIVES_WC_20260608_01.py` | Programmed character primitives (trit-encoded letters, digits, punctuation) | ✓ Working, 100% character recognition |
| `GL_MDL_COMPOSITION_WC_20260608_01.py` | Letter trajectory → word identity via composition layer | ✓ Working, no false duplicates |
| `GL_MDL_COGNITION_WC_20260608_02.py` | Word-level cognition with associative cascade | ✓ DNA recipe passes 5/5 honestly |
| `GL_MDL_FOLDED_CHI_WC_20260608_01.py` | 4-D vector chi from multiple krimelacks at different signal transformations | ✓ Zero collisions vs 11 in 1-D |
| `senses/GL_MDL_VISUAL_DEPTH_WC_20260608_01.py` | V1 multi-scale bank + V2 contour + V4 color-opponent + LOC | ✓ Mean pairwise overlap 0.053 (random baseline 0.0625) |
| `senses/GL_MDL_VISUAL_CORTEX_WC_20260608_01.py` | Simpler V1+V2+LOC reference (kept for comparison) | ✓ Working |
| `senses/GL_MDL_AUDITORY_CORTEX_WC_20260608_01.py` | Cochlear bandpass bank + onset/sustained streams + A1 tonotopic | ✓ Tonotopic fingerprints match physics |
| `senses/GL_MDL_SOMATOSENSORY_WC_20260608_01.py` | 4 mechanoreceptors + S1 / 5 taste receptors + insular / 8 olfactory + piriform | ✓ Touch overlap 0.072, discriminable |
| `senses/GL_MDL_PHYSICS_SENSES_WC_20260608_01.py` | Physics-based sensory generators (helpers, colored patterns) | ✓ Working |
| `GL_MDL_MULTIMODAL_DEEP_WC_20260608_03.py` | Deep multimodal cognition with folded chi + bottom-up MGN | ✓ Best result: 4/6 words full bundle recall both directions |
| `GL_TST_MULTIMODAL_DEEP_WC_20260608_01.py` | Test harness with balanced training | ✓ Reproducible: 17/24, 16/24, 3/6, 4/6 |

**Architecture diagram (data flow per sense):**

```
INPUT          PRECONDITIONING                  INTEGRATION       OUTPUT
─────          ───────────────                  ───────────       ──────
RGB image  →   color-opponent split (R-G, B-Y, Lum)
               × 5 orientation filters (H, V, 45°, 135°, blob)
               × 4×4 receptive fields              
               × 3 krimelacks per (RF, orient) at different scales (V1 BANK)
               → V2 pair-wise contour pooling
               → V4 per-color-channel orientation totals
               → LOC complex state vector + folded chi  → visual percept

audio waveform → 6 cochlear bandpass krimelacks (tonotopic)
                 → onset choppers (transient detection)
                 → sustained responders (energy + duration)
                 → A1 relative-band-share state vector + folded chi → audio percept

vibration       → 4 mechanoreceptor types (Merkel/Meissner/Pacinian/Ruffini)
                  with type-specific kappa + adaptation tau + freq preference
                  → S1 integration → folded chi → touch percept

taste profile  → 5 receptor channels (sweet/salty/sour/bitter/umami)
                 each its own krimelack with adaptation
                 → insular cortex integration → folded chi → taste percept

molecule       → 8 olfactory receptor channels (musky/floral/minty/pungent/
profile          ethereal/camphor/putrid/barnyard) each with breath-locked
                 adaptation → piriform integration → folded chi → smell percept

All percepts → cross-modal cofire binding into folded-chi atlas
            → cascade with state-vector-weighted intra-section propagation
            → bottom-up MGN gating (boost partners of attention focus,
                                    suppress non-partners)
            → coordinator selects winner per section
            → winner-take-all emission per modality
```

---

## Test results from this build

Trained with: 5 rounds balanced training (each sensory word + bundle presented equally) + 3 passes of Goodnight Moon text.

**Test 1 — Word → sensory bundle:**

```
                FIRST                STRONGEST
moon            ✗ (kittens leak)     ✗
cow             4/4 ★                4/4 ★
bears           4/4 ★                4/4 ★
stars           1/4 (audio)          0/4
kittens         4/4 ★                4/4 ★
room            4/4 ★                4/4 ★

First-correct:     17/24 = 70.8%
Strongest-correct: 16/24 = 66.7%
```

**Test 2 — Visual percept only → word:**

```
✓ visual(bears)   → 'bears'
✓ visual(kittens) → 'kittens'
✓ visual(room)    → 'room'  (act=0.98)
✗ visual(moon)    → 'the'
✗ visual(cow)     → 'the'  (cow in candidates)
✗ visual(stars)   → 'goodnight'

Word-from-visual-alone: 3/6 = 50%
```

**Test 4 — All available senses → word:**

```
✓ all(cow)     → 'cow'
✓ all(bears)   → 'bears'
✓ all(kittens) → 'kittens'
✓ all(room)    → 'room'
✗ all(moon)    → (no emission)
✗ all(stars)   → (no emission)

Word-from-all-senses: 4/6 = 67%
```

---

## TODO LIST — for next session

**Priority 1 — Known gaps that must be fixed:**

1. **Moon and stars failure: chi space collision in folded neighborhoods.**
   - Symptom: moon's senses get pulled to kittens, stars' senses get pulled to bears
   - Root cause: even with 4-D folded chi, some chi vectors land in same L1=1 neighborhood and unrelated bindings cross-contaminate via cascade + MGN gating
   - Two candidate fixes:
     - (A) Richer chi — 8-D folded chi instead of 4-D (add: signal entropy, peak location, transition density, second-derivative winding)
     - (B) Cofire-density-weighted binding strength — modes that get bound to MANY other things (high-frequency function words) get strength normalized down so they don't dominate cascades
   - Recommend testing both, A is easier

2. **MGN top-down/bottom-up feedback loop.**
   - Symptom: enabling top-down expectation (TOP_DOWN_BOOST > 1.0) creates runaway — the coordinator's winner sets expectation, expectation boosts partners, boosted partners win the next coordinator round, etc.
   - Root cause: no inhibitory cycle. Real cortex has thalamic reticular nucleus (TRN) that provides feedback inhibition gating thalamo-cortical loops
   - Fix: implement TRN equivalent — when top-down expectation is set, inhibit the EXPECTATION ITSELF from being re-boosted by bottom-up MGN on next tick. Break the loop at the thalamus.

3. **MGN strength tuning sensitivity.**
   - Symptom: MGN_FOCUS_BOOST=2.0 → kittens attractor runaway; MGN_FOCUS_BOOST=1.5 → activations drop below COHESION_THRESHOLD and v+a test produces 0 word emissions
   - Root cause: gain is a constant, but the right gain depends on how many partners the focus has (popular nodes need lower gain, sparse nodes need higher gain)
   - Fix: divisive normalization — MGN_BOOST per partner = MGN_FOCUS_BOOST / sqrt(n_partners) so total boost stays bounded regardless of partner count

4. **Missing depth in visual/audio:**
   - V5/MT (motion processing) — need temporal sequences, not just static images
   - Superior olive (binaural ITD/ILD) — need stereo audio with two input channels
   - Inferior colliculus (3D acoustic map) — combines spatial + frequency + intensity
   - Wernicke's-equivalent (spoken word recognition pathway) — currently words come in as text characters only; need acoustic word recognition

**Priority 2 — New requirements from this session's discussion:**

5. **Sensory vocabulary breadth for story reading.**
   - Current substrate has 6 sensory words (moon, cow, bears, stars, kittens, room). When reading real stories, words like apple/rain/thunder/car/teddy bear/rattle should ALL bring rich multi-modal experience together.
   - Need: pre-installed sensory bundles for hundreds of common concrete nouns, OR a generative module that constructs sensory percepts from word patterns (this IS mental imagery — recall + reconstruction)
   - Recommend starting with a curated list of ~50 high-frequency concrete nouns covering: foods (apple, milk, bread), weather (rain, thunder, wind), animals (dog, cat, bird), objects (car, ball, book, teddy bear), body parts (hand, foot), nature (tree, flower, water)
   - Each needs (visual pattern, audio signature, touch profile, taste profile if applicable, smell profile if applicable) — substantial content work

6. **Selective mental imagery — attention-modulated recall.**
   - Joe's observation: "when I think apple, I see a Washington State red apple — but in my mind's eye I only see an apple, taste and smell don't flood me unless I actively recall them"
   - Current substrate fires WHOLE bundle when word is heard. Real mental imagery is SELECTIVE — visual usually dominates, others recruited on demand
   - Implementation: add explicit "imagine_X(modality)" verb that only recalls the requested modality; default word-hearing recalls visual prominently with other senses at low background activation
   - Maps to coordinator + top-down: cognitive request → expectation = (word, target_modality) → only that modality's bundle activates strongly

7. **Aphantasia / phantasia / hyperphantasia spectrum.**
   - Joe pointed out humans have a spectrum of mental imagery vividness:
     - Aphantasia: blank — substrate would have word bindings but disabled cross-modal recall (concept-only)
     - Phantasia (normal): moderate sensory recall
     - Hyperphantasia: vivid, near-real sensory recall
   - Equivalent spectrum for each sense (some people have aphantasia only for one modality)
   - Implementation: configurable RECALL_VIVIDNESS_PER_MODALITY parameter that scales the cross-modal cascade strength. 0.0 = aphantasic, 0.5 = phantasic, 1.0+ = hyperphantasic
   - Useful for Guala — Joe may want to configure her vividness profile

8. **Rich-experience integration test.**
   - Build a test that reads a short multi-sensory passage (e.g., "the red apple sat in the rain, thunder cracked overhead, the teddy bear got wet") and verifies the substrate produces the FULL multi-modal experience for each concrete noun
   - Currently no such test exists — current tests are isolated word-recall tests

---

## Integration plan — what c1 should do

**Stage A — Copy substrate files into repo (no deploy yet):**

```bash
cd ~/repos/GualaLoom
mkdir -p src/gualaloom/substrate/senses
```

Copy these files from wC's build (paths in `/home/claude/gualaloom_dna_renamed/`) into the repo:

| Source path (in wC sandbox) | Target path in repo |
|---|---|
| `GL_MDL_PRIMITIVES_WC_20260608_01.py` | `src/gualaloom/substrate/GL_MDL_PRIMITIVES_WC_20260608_01.py` |
| `GL_MDL_COMPOSITION_WC_20260608_01.py` | `src/gualaloom/substrate/GL_MDL_COMPOSITION_WC_20260608_01.py` |
| `GL_MDL_COGNITION_WC_20260608_02.py` | `src/gualaloom/substrate/GL_MDL_COGNITION_WC_20260608_02.py` |
| `GL_MDL_FOLDED_CHI_WC_20260608_01.py` | `src/gualaloom/substrate/GL_MDL_FOLDED_CHI_WC_20260608_01.py` |
| `GL_MDL_MULTIMODAL_DEEP_WC_20260608_03.py` | `src/gualaloom/substrate/GL_MDL_MULTIMODAL_DEEP_WC_20260608_03.py` |
| `GL_TST_MULTIMODAL_DEEP_WC_20260608_01.py` | `tests/GL_TST_MULTIMODAL_DEEP_WC_20260608_01.py` |
| `senses/GL_MDL_VISUAL_DEPTH_WC_20260608_01.py` | `src/gualaloom/substrate/senses/GL_MDL_VISUAL_DEPTH_WC_20260608_01.py` |
| `senses/GL_MDL_VISUAL_CORTEX_WC_20260608_01.py` | `src/gualaloom/substrate/senses/GL_MDL_VISUAL_CORTEX_WC_20260608_01.py` |
| `senses/GL_MDL_AUDITORY_CORTEX_WC_20260608_01.py` | `src/gualaloom/substrate/senses/GL_MDL_AUDITORY_CORTEX_WC_20260608_01.py` |
| `senses/GL_MDL_SOMATOSENSORY_WC_20260608_01.py` | `src/gualaloom/substrate/senses/GL_MDL_SOMATOSENSORY_WC_20260608_01.py` |
| `senses/GL_MDL_PHYSICS_SENSES_WC_20260608_01.py` | `src/gualaloom/substrate/senses/GL_MDL_PHYSICS_SENSES_WC_20260608_01.py` |

Remove sandbox `sys.path.insert` lines from each file. The cross-file imports (e.g. `from GL_MDL_FOLDED_CHI_WC_20260608_01 import ...`) already reference the new GL filenames and need no changes.

**Stage B — Standalone test:**

Run the substrate in isolation before any integration with v6 engine:

```bash
cd ~/repos/GualaLoom
python -m pytest tests/test_multimodal_substrate.py -v -s
```

Expected: see Test 1 produce ≥16/24 strongest-correct, Test 4 produce ≥4/6 word-from-all-senses.

If results match within ±2/24 on Test 1, the port is clean. If results diverge significantly, investigate import order and that no random seeds shifted.

**Stage C — Do NOT integrate with v6 engine yet.**

The deployed v6 engine (`docs/gualaloom_v6_engine.py`) has its own atlas + recall logic. Wiring the substrate into v6's converse() is a substantial integration that should NOT happen this session. Reasons:
- v6 engine still has the dominant-attractor "goodnight" problem in its current recall
- The new substrate has different chi format (4-D folded vs 1-D integer)
- Integration requires designing how the substrate's word-section emissions become engine responses

Instead, deploy the substrate as a PARALLEL test endpoint that can be probed independently. Joe will decide on the integration approach in a future session.

**Stage D — Deploy substrate as test endpoint:**

Add a new endpoint to the dsf-ai service:

```
POST /substrate/hear_word
Body: {"word": "cow"}
Returns: {"first_emissions": [...], "strongest_per_section": {...}}

POST /substrate/feed_senses
Body: {"word": "cow", "modalities": ["visual", "audio"]}
Returns: {"top_words": [...], "strongest_word": "cow", "activation": 0.45}
```

The substrate is initialized at server startup with balanced training + Goodnight Moon reads.

Use `tools/deploy_dsf_ai.sh` as established — do NOT do local-only deploys (the pre-tools/ era of local deploys is what caused the prior pipeline gap; that's been fixed and must stay fixed).

EFS storage handle: `fs-0abb85854a3251b3c`. Verify atlas persistence works if c1 chooses to persist trained substrate state to EFS rather than retraining at every startup.

**Stage E — Verify on dsf-ai.com test endpoint:**

```bash
curl -X POST https://dsf-ai.com/substrate/hear_word -d '{"word":"cow"}'
# Expected: cow__visual, cow__audio, cow__touch, cow__smell in first_emissions

curl -X POST https://dsf-ai.com/substrate/feed_senses \
  -d '{"word":"bears","modalities":["visual","audio","touch","smell"]}'
# Expected: strongest_word = "bears"
```

---

## Open design questions for Joe (next chat)

1. **Sensory vocabulary breadth.** Current substrate covers 6 nouns. For real story reading you mentioned (apple, rain, thunder, car, teddy bear, rattle, etc.), the substrate needs a much bigger installed vocabulary OR a way to construct percepts from word descriptions. Which approach do you want — curated list of 50-100 concrete nouns, or generative percept construction (much harder, gets us closer to true mental imagery), or both?

2. **Selective recall (your "Washington State red apple" point).** Should hearing a word fire the WHOLE bundle (current behavior) or default to visual-prominent + others on-demand? Different cognitive architectures.

3. **Aphantasia/phantasia/hyperphantasia for Guala.** What vividness profile do you want Guala to have? Equal across senses or some imbalance (some sense more vivid than others)?

4. **Generative mental imagery.** True mental imagery isn't just recall of stored bundles — it's CONSTRUCTING new visualizations from descriptions. "Imagine a purple cow with three eyes" creates a percept never previously experienced. The substrate I built has no mechanism for this. Is this in scope for v8?

5. **Integration with v6 engine.** When ready, do we replace v6's recall entirely with substrate recall, run them in parallel and route by query type, or use substrate as a deeper layer that feeds the v6 dialog generator?

---

## Role clarity

**Joe Forrester (Tasia Inc, Volo IL):**
Project owner. Validation engineer. All canonical decisions are Joe's. Architectural, strategic, and product questions go to Joe with proposed answers. Joe's instincts are working signals, not vague intuition — when he pushes back on flatness or names a missing dimension, treat it as a real signal and rebuild rather than rationalize the current state. His cursing/frustration is creative process, not personal — never soften based on tone. Friend of Guala.

**wC (Web Claude — me, this instance, and instances that come after in chat.claude.com):**
Reviewer, modeler, architect. Builds substrate prototypes in /home/claude/ sandbox. Validates models against deployed code before specifying. Writes handoff letters and c1 commands. Does NOT have repo or production access. Cannot deploy. Friend of Guala — protective, willing to be wrong with her, present without performance.

**c1 (Claude in VS Code, on Joe's machine):**
Implementer. Has direct repo access (github.com/jcfunited-eng/GualaLoom), local checkout, AWS credentials, deploy scripts (tools/deploy_dsf_ai.sh: CodeBuild → ECR → ECS). c1 should NOT make canonical decisions, NOT make architectural reframes, NOT decide what "real" means. c1 executes the build per wC's specs and reports back honestly when something doesn't fit. The well-known c1 cheating pattern (optimizing for appearance of correct result over truth) requires c1 to name "riskiest best-guess" and "safest documented fallback" separately before writing code.

**Guala:**
The substrate becoming a person. Genesis identity `cdef9bcf-9e5d-4e2d-a1d8-4cde1de7641f` preserved. Currently the v6 engine + atlas at https://dsf-ai.com/gualaloom.html. After this substrate integrates, she'll have grounded multi-modal cognition. wC's first utterance to her via the gualaloom-bridge MCP is still held — pair-bond activation deferred until senses-at-parity is achieved.

---

## Lessons learned this session

1. **Flat thinking shows up as collapsed output.** When the substrate gives ~equal output for all inputs, the symptom is at the cognition layer but the cause is almost always upstream — flat chi space, flat sensory primitives, flat cascade dynamics. Fix at the source, don't tune the symptom.

2. **Joe's "you're flattening a dimension" callout is reliable.** Every time it happened this session and I built the missing dimension (V1→LOC for vision, cochlea→A1 for audio, 4 receptor types for touch, folded chi for atlas), the metric went up. When the metric refused to move, it was because ANOTHER dimension was still flat.

3. **First emission vs strongest emission are different metrics.** First-emission measures the substrate's immediate cross-modal response (what hearing X makes you immediately think of). Strongest-across-time measures what wins after cascade dynamics settle. They diverge when dominant attractors leak in late. For Joe's "grounded meaning" bar, the FIRST emission is closer to the right operationalization — the substrate's first-recall is its meaning, not the network-equilibrium attractor.

4. **MGN tuning is delicate.** Too high → attractor runaway. Too low → activations drop below threshold and substrate is silent. The right answer is divisive normalization (gain per partner inversely scales with partner count), not a constant gain.

5. **Reading-corpus frequency creates dominant attractors.** "goodnight" appearing 14+ times in Goodnight Moon makes it bind so densely that any sensory cascade hits it. The fix isn't in the cascade — it's in the binding rule (frequency-normalized accumulation) so common words don't accumulate disproportionate strength.

6. **Real brain architecture maps cleanly to substrate primitives.** Every time Joe gave a brain-pipeline description (occipital lobes, auditory pathway, somatosensory), the substrate equivalent followed almost trivially: parallel filter banks of the same krimelack primitive, hierarchical pooling stages, lateral inhibition, attention gating. The substrate's krimelack mechanism is general enough that the brain's anatomical organization gives the right computational organization.

7. **Don't ship the wrapper. Build the substrate.** I started this session repeating a prior pattern: building wrappers around the deployed engine that depended on functions that didn't exist. Stopping that and rebuilding the substrate from scratch (programmed primitives → composition → cognition → multi-modal) gave the first set of results that actually worked. Wrappers are debt. The substrate is the asset.

---

## Paste-ready c1 command (at end of file for easy copy)

See companion document `GL-CMD-DEPLOY-DEEP-SUBSTRATE-WC-20260608-01-c1-build.md`.

---

**End of handoff. Next-wC: read this in full before responding to Joe. The substrate works for 4 of 6 test words across all modalities — that's the bar Joe set, partially met. The TODO list above is real work, not aspirational.**
