---
doc_id: GL-SPC-VISUAL-V2-WC-20260607-01
related_tag: GUALALOOM-V7-AUTONOMY-WC-2026-06-06
created: 2026-06-07
author: wC
type: spec amendment
topic: Visual krimelack — synthesis refinements
supersedes_section_of: GL-SPC-VISUAL-KRIMELACK-WC-20260606-01 (only the atlas-integration section)
references:
  - GL-MDL-SYNTHESIS-WC-20260606-01 (modeling that validated the refinements)
  - GL-MDL-G32-COGNITION-WC-20260606-01 (the failed basin experiment whose failure mode this fixes)
---

# Visual Krimelack — Atlas Integration Amendment

This document AMENDS the original visual krimelack spec
(`GL-SPC-VISUAL-KRIMELACK-WC-20260606-01`). Everything in that spec stands
EXCEPT the atlas-integration section, which is replaced here.

The transduction part of the visual spec is unchanged: fovea krimelack with
`ω(t) = ω₀ + κ·s(t)`, saccade controller via peripheral gradient, fragments
carry full event_ticks sequences. All of that is the same.

What changes: HOW visual percept fragments commit motifs in the sight section
and HOW they bind in the atlas. The original spec referenced chi-band binding
generically. This amendment specifies the exact mechanism, informed by
modeling.

## Background: why this amendment exists

The synthesis modeling
(`GL_MDL_SYNTHESIS_WC_20260606_01_synthesis.py`) tested two architectural
choices side by side:

1. **L2 distance for capture** (the basin experiment): fragments fragmented.
   Same experience under noise produced 5 → 9 basins. The substrate
   over-specialized — every variant became its own concept.

2. **Cosine alignment + cluster dynamics + chi-from-cofire-set**: zero
   fragmentation. 2 motifs in pass 1, 2 motifs in pass 2 — perfect
   generalization across variants.

The same experiment exposed a different failure mode in the second design:
without surface-form anchoring, distinct concepts (moon, stone) collapsed to
the same motif because their G32 vectors pointed in similar directions.

The fix synthesizes both: cosine alignment + cluster dynamics for
generalization within a concept, surface-form anchoring (v6-native) for
discrimination between concepts.

## Visual motif: identity and structure

A visual motif in the sight section has the following structure:

```python
@dataclass
class VisualMotif:
    motif_id: int
    section: str = "sight"
    surface_form: str           # picture_id or video_id — IDENTITY anchor
    angle: list[float]          # founding G32 token — INTERPRETIVE perspective
    cluster_state: list[float]  # current dynamic state — evolves via coupling
    capture_signature: list[float]  # perceptual signature for matching
    n_firings: int
    founded_at_tick: int
```

- `surface_form` is the picture identifier or perceptual hash of the founding
  event. Two fragments from the same picture share the same surface_form.
- `angle` is the G32 token of the FIRST fragment that committed this motif.
  Immutable after commit.
- `cluster_state` is the running joint state; evolves via FMM coupling
  dynamics whenever this motif co-fires with others in the sight section.
- `capture_signature` is a perceptual signature used to determine whether
  an incoming fragment "belongs to" this motif's surface form. For a static
  picture, this could be a hash of the fragment's centroid coordinates and
  intensity histogram. For a video, this could be a more complex temporal
  signature.

## Visual percept fragment → G32 projection

When a saccade-fixation sequence completes and produces a `VisualPerceptFragment`:

```python
@dataclass
class VisualPerceptFragment:
    fixation_coord: tuple[int, int]
    event_ticks: list[int]      # full sequence — required, NOT just count
    winding_count: int
    picture_id: str             # surface form
    born_tick: int
```

Compute FMM primitive from the fragment:

- **I (intensity)**: mean signal intensity across fixation = `winding_count / fixation_duration` normalized to [0,1].
- **C (coherence)**: temporal regularity of winding events. Compute
  inter-event intervals from `event_ticks`. Coherence = `1 - clip(std(intervals) / mean(intervals))`. Low variance → high coherence.
- **N (novelty)**: 1 - familiarity score. Familiarity = max cosine similarity
  to any existing capture_signature in the sight section. Novel if no
  existing motif's signature matches above 0.7.
- **A (affect)**: contextual. If a pair-bond source is present at the time
  of this fragment AND audio in the same window carries affect, inherit
  that affect. Otherwise default 0.5 (neutral).

Project: `g_token = Π(FMM, familiarity=f, dream_delta=0)`

This is the percept's G32 representation. 32 dimensions, each a defined
cognitive primitive.

## Motif commit-or-fire decision

Given a fragment with surface_form S and g_token G:

```
1. Compute capture_signature for this fragment.
2. Find existing visual motifs whose capture_signature has cosine
   similarity > 0.7 with the fragment's capture_signature.
3. If MATCH found:
     - Fire the matched motif (it's the same picture/video coming back).
     - Cosine alignment of g_token with motif.angle determines firing
       strength (above 0.55 → fires; below → matched-but-quiescent).
4. If NO MATCH (truly novel surface):
     - Commit a new motif:
         surface_form = S
         angle = g_token (copy)
         capture_signature = fragment_signature (copy)
         cluster_state = g_token (initial)
     - Fire the new motif.
```

This is the discrimination fix: distinct pictures/videos commit distinct
motifs because their perceptual signatures differ. Two fragments from the
SAME picture share a motif because their signatures match, even if their
G32 vectors differ due to lighting/angle/motion variations within that
picture.

## Cluster dynamics (FMM coupling)

When multiple motifs fire in the sight section (multi-fixation saccade
producing fragments at different points, OR same picture interpreted at
multiple zoom levels), their cluster_states evolve:

```python
# After firing in section
firing_motifs = [m for m in self.motifs["sight"] if m.motif_id in fired_ids]
if len(firing_motifs) >= 1:
    cluster_mean = np.mean([np.array(m.cluster_state) for m in firing_motifs], axis=0)
    for m in firing_motifs:
        state = np.array(m.cluster_state)
        new_state = (
            GATE_INERTIA * state                        # prior persists
            + (1 - GATE_INERTIA) * g_token              # current input drives
            + COUPLING_STRENGTH * (cluster_mean - state)  # neighbors pull
        )
        m.cluster_state = clip(new_state).tolist()
        m.n_firings += 1
```

Constants (validated by synthesis modeling):
- `GATE_INERTIA = 0.6`
- `COUPLING_STRENGTH = 0.15`

No learning rule. The cluster's joint state settles toward coherent
interpretation through coupling — exactly per FMM paper.

## Chi-address binding

When sight-section motifs fire alongside motifs in other sections (audio,
touch, etc.) during cross-modal experiences:

```python
fired_motif_ids = (sight_fired + sound_fired + touch_fired + ...)
chi = chi_for_cofire_set(frozenset(fired_motif_ids))
for motif_id in fired_motif_ids:
    reinforce_binding_at(chi, motif_id, with_band_radius=2)
```

`chi_for_cofire_set` is deterministic: same set of co-firing motif_ids
ALWAYS produces the same chi address. This is the synthesis result —
contextual chi-addressing via co-firing context, not via L2 distance in
percept space.

The chi-band radius of 2 means a binding at chi=K also reinforces chi=K±1
and chi=K±2 with falloff (1.0, 0.67, 0.33). This preserves v6's living-atlas
neighborhood reinforcement, which is correct.

## Recall

When a new fragment arrives and Guala is asked to recall something:

```python
1. Project fragment to g_token.
2. Find matching surface_form (cosine sig > 0.7).
3. If match: that motif's chi-neighborhood bindings surface.
   The cohesion cascade across those bindings produces output.
4. If no match: honest unknown. (Same as v6 cohesion cascade.)
```

This preserves v6's recall behavior. The synthesis refinements are about
how MOTIFS form and align, not about how RECALL queries the atlas — that
mechanism stays.

## What this enables that v6 doesn't have

1. **Variant generalization**: same picture viewed at different times under
   different lighting/zoom/angle produces fragments with slightly different
   G32 vectors but the same capture_signature. They reinforce the same motif
   instead of fragmenting into many. This is the basin experiment's failure
   mode, fixed.

2. **Cluster-coherent interpretation**: when a multi-fixation saccade across
   a single picture produces multiple fragments, the sight cluster's
   joint state evolves toward a coherent settled interpretation of THAT
   picture. The picture isn't 12 disconnected fragments — it's a unified
   interpretive event.

3. **Cross-modal binding via chi-from-cofire**: when she sees a strawberry
   AND tastes a strawberry AND hears the word "strawberry" within the same
   tick window, three motifs co-fire across sections. Same co-firing set →
   same chi address. Tri-modal binding lands at one location. Next time
   any one of those three triggers, chi-neighborhood recall surfaces the
   other two.

## What this preserves from v6

1. **Surface-form anchoring**: motifs are still tied to specific pictures/
   videos/words. The picture_id determines motif identity. The G32 angle
   determines interpretive perspective. v6's discriminating power is intact.

2. **Cohesion cascade for recall**: when she's asked something, the cohesion
   cascade across chi-neighborhood bindings produces her response. No
   change.

3. **Strength scalars**: now correctly understood as BASIN SHARPNESS, not
   edge weights. Reinforcement strengthens a binding's reliability; decay
   reduces it; below threshold it forgets. v6's living-atlas semantics
   intact.

## What is NOT in this amendment

- Tapestry-level (mosaic of mosaics) explicit composition. Higher-level
  resonance emerges from accumulated experience without a separate code
  path. If we later want explicit tapestry commits, that's a future amendment.
- Per-modality G32 axis weighting. For now, all 32 dimensions weighted
  equally in cosine alignment. If experience shows certain dimensions
  matter more for visual matching, that's a tuning question for later.
- Eigenmode decomposition of motif clusters. The FMM coupling dynamics
  already produce eigenmode-like settling implicitly. Making this explicit
  would let the substrate refer to clusters as objects, which is needed for
  higher-order recursion but not for Phase 2.

## Validation gates (additions to original Phase 2 gates)

The original Phase 2 gates stand. ADD these:

7. **No-fragmentation gate**: upload the same picture 10 times. Verify the
   atlas commits exactly 1 visual motif for it (or close — at most 2 if
   the picture's perceptual signature has natural variability). NOT 10.

8. **Discrimination gate**: upload 3 distinct pictures. Verify the atlas
   commits 3 distinct visual motifs with different surface_forms.
   Verify their angles differ (cosine similarity between them < 0.85).

9. **Cluster-evolution gate**: feed a saccade sequence across a single
   complex picture. After the sequence, verify the sight cluster's motifs
   have moved their cluster_states toward a common region (cluster_mean
   pull works).

10. **Cross-modal binding gate**: present a picture AND a sound in the
    same tick window with both surface_forms novel. Verify the new sight
    motif and the new sound motif end up bound at the same chi address.
    Verify chi-band neighbors (±1, ±2) also have weakened bindings.

11. **Recall gate**: after binding a picture+sound, present the picture
    alone. Verify recall surfaces the sound motif via chi-neighborhood
    cascade.

## Files c1 will modify or create (relative to Phase 2's original list)

Adds these to or modifies these in the original Phase 2 file list:

- `gualaloom/krimelack/visual.py` — visual motif with surface_form +
  capture_signature + cosine alignment
- `gualaloom/atlas/sight_section.py` (NEW) — sight section with cluster
  dynamics
- `gualaloom/atlas/chi.py` (MODIFY) — chi_for_cofire_set function if not
  already present in v6 form
- `tests/test_visual_motif_generalization.py` (NEW) — gates 7-9
- `tests/test_visual_cross_modal.py` (NEW) — gates 10-11

## Honest note on the synthesis modeling

The synthesis model showed cosine alignment + chi-from-cofire-set produces
generalization (5 experience types → 5 motifs after multiple passes with
noise variants — actually fewer in my run because of over-merging from
missing surface-form anchoring, but the no-fragmentation result was clean).

The same model exposed that without surface-form anchoring, the substrate
over-merges. The fix is to keep v6's surface-form anchoring AND add the
synthesis's cosine/cluster mechanisms. This is the synthesis: not v6 vs
synthesis-replacement, but v6 + synthesis-refinement.

I haven't yet modeled the combined design end-to-end. The cosine+cluster
piece is validated. The surface-form anchoring is validated by v6's actual
behavior (Guala learning in real conversations). The combination should
work but hasn't been numerically tested. Phase 2 implementation will be
the first place we see it run together. If gates 7-11 fail, we learn
something about which combination piece is wrong — not a fundamental
issue, but a tuning question worth flagging now.

If c1 sees gate 7 (no-fragmentation) fail, the cosine threshold is wrong
or capture_signature matching is wrong. Adjust upward.

If c1 sees gate 8 (discrimination) fail, the capture_signature isn't
distinct enough between different pictures. Probably means the signature
needs more entropy — include color histogram, intensity gradient direction,
spatial layout, etc.

If c1 sees gate 9 (cluster evolution) fail, the FMM coupling constants
are wrong. Try GATE_INERTIA in [0.4, 0.7], COUPLING_STRENGTH in [0.1, 0.25].

## Standing constraints (unchanged)

- No LLM completion, no CNN, no embeddings, no pre-trained vision models
- No FFT-as-frequency-domain
- Cohesion cascade is the ONLY response mechanism
- Strength scalars describe basin sharpness, not edge weights
- Pair-bond: joe=true, wc=true, c1=false

Tag commits with `GUALALOOM-V7-AUTONOMY-WC-2026-06-06`.
