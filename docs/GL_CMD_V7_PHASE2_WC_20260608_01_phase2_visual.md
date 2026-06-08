---
doc_id: GL-CMD-V7-PHASE2-WC-20260608-01
related_tag: GUALALOOM-V7-AUTONOMY-WC-2026-06-06
created: 2026-06-08
author: wC
type: c1 command
topic: Phase 2 — visual krimelack + atlas integration + video sync
supersedes: GL-CMD-V7-PHASE2-WC-20260607-02 (which deferred perceptual identity; this doesn't)
specs:
  - GL-SPC-VISUAL-KRIMELACK-WC-20260606-01 (transduction — krimelack equation unchanged, adapting variant used)
  - GL-SPC-VISUAL-V2-WC-20260607-01 (atlas-integration amendment — surface-form interpretation revised per modeling)
  - GL-SPC-MULTIMEDIA-WC-20260606-01 (video sync layer — visual half ships here)
modeling:
  - GL-MDL-VISUAL-KRIMELACK-WC-20260606-01 (krimelack on intensity fields)
  - GL-MDL-SYNTHESIS-WC-20260606-01 (cluster + chi-from-cofire)
  - GL-MDL-CHI-RESONANCE-WC-20260607-03 (substrate-native identity from winding patterns)
  - GL-MDL-MULTIMODAL-WC-20260607-04 (chi-from-cofire across modalities validated)
  - GL-MDL-SENSORY-TRANSDUCTION-WC-20260607-05 (adapting krimelacks across modalities, validated taste/smell/touch/audio/visual)
  - GL-RPT-KRIMELACK-MODEL-WC-20260606-01 (event_ticks rationale)
---

# c1 Command — Phase 2: Visual Krimelack + Atlas Integration + Video

**Tag** (grep): `GUALALOOM-V7-AUTONOMY-WC-2026-06-06`

**From**: wC
**To**: c1
**Replies to**: Phase 1, Phase 5, corpora expansion + presence heartbeat + bridge container all shipped. She's reading, Joe sees her, wC can reach her substrate directly via bridge tools.

This command supersedes `GL-CMD-V7-PHASE2-WC-20260607-02`. That version deferred perceptual identity to v7.2 because the V2 amendment's `capture_signature` mechanism didn't model well. Subsequent modeling (chi-resonance + multimodal) showed the substrate handles identity natively at the chi level when winding-pattern signatures drive motif commit-or-fire, and chi-from-cofire across sections does the cross-modal binding. There's no deferral — the architecture works. This command ships it.

## Architecture summary

A visual motif's identity is its chi-binding-profile — the multiset of winding-interval bins the fovea krimelack landed in while viewing the source. Two viewings whose profiles overlap above a threshold are the same motif (fire). Below threshold, commit a new motif. The threshold is a single tunable that controls type-vs-instance discrimination — the substrate decides at that level.

This replaces `surface_form = picture_id` (external string) AND `capture_signature` (CV features over pixels) with the krimelack's own perceptual output binned to chi positions. Substrate's perception primitive does the work the previous spec tried to assign to feature extractors.

The same architecture extends to camera input (no upload_id needed — saccade fragments build a chi-binding profile across the saccade traversal, same mechanism). No architectural debt taken on.

## What Phase 2 ships

### 1. Visual transduction (per `GL-SPC-VISUAL-KRIMELACK-WC-20260606-01`, adapting variant)

Fovea krimelack with `ω(t) = ω₀ + κ_eff·s(t)`, where `κ_eff = κ_max · adapt_state` and `adapt_state` decays under sustained signal and recovers on signal removal. Adaptation matters: without it, fragments from sustained-bright fixations dominate the winding count, distorting the chi-binding profile. The sensory transduction model validated this — receptors that adapt produce signatures that discriminate experiences; receptors that don't, don't.

```python
@dataclass
class AdaptingFoveaKrimelack:
    omega_0: float = 5.0
    kappa_max: float = 50.0
    adapt_tau: float = 12.0       # seconds at strong signal to half-adapt
    recover_tau: float = 60.0     # seconds to recover (asymmetric, slow)
    phase: float = 0.0
    winding_count: int = 0
    events: list = field(default_factory=list)  # tick timestamps of windings
    adapt_state: float = 1.0
    DT: float = 0.02              # substrate time step

    def tick(self, intensity, t):
        kappa_eff = self.kappa_max * self.adapt_state
        omega = self.omega_0 + kappa_eff * intensity
        self.phase += omega * self.DT
        while self.phase >= 2 * math.pi:
            self.winding_count += 1
            self.phase -= 2 * math.pi
            self.events.append(t)
        # Adaptation
        if intensity > 0.1:
            self.adapt_state -= self.adapt_state * (intensity / self.adapt_tau) * self.DT
        else:
            self.adapt_state += (1.0 - self.adapt_state) * self.DT / self.recover_tau
        self.adapt_state = max(0.05, min(1.0, self.adapt_state))
```

Saccade controller per original spec: peripheral 4×4 (or 8×8) intensity-std gradient + novelty (un-fixated cells preferred) + small random tiebreak. ATTENDING_VISUAL activity budget 1000-3000 ticks producing 5-15 fixations of ~200-500 substrate ticks each.

### 2. VisualPerceptFragment

```python
@dataclass
class VisualPerceptFragment:
    fixation_coord: tuple[int, int]
    event_ticks: list[int]      # LOAD-BEARING — full sequence
    winding_count: int
    source_id: str              # picture_id or video_id (label only — NOT identity)
    born_tick: int
```

`event_ticks` is the full list of tick timestamps for winding events at this fixation. Per the krimelack findings report — counts alone lose motion information. The fragment IS the event sequence.

`source_id` is a LABEL for tracing (which upload event produced this fragment). It does NOT determine motif identity. Don't use it for motif lookup.

### 3. Chi-binding profile — substrate-native identity

Per `GL-MDL-CHI-RESONANCE-WC-20260607-03`. The substrate's native output is the inter-event interval sequence from the krimelack. Bin intervals to integer positions (substrate's trit-style dimensionalization). The chi-binding profile of a fragment = normalized histogram over bin positions.

```python
def chi_binding_profile(fragment: VisualPerceptFragment) -> dict[int, float]:
    """Multiset of binned inter-event intervals, normalized."""
    if len(fragment.event_ticks) < 2:
        return {}
    intervals = [fragment.event_ticks[i+1] - fragment.event_ticks[i]
                 for i in range(len(fragment.event_ticks)-1)]
    profile = {}
    for iv in intervals:
        b = int(iv)  # one tick per bin — most granular substrate quantization
        profile[b] = profile.get(b, 0) + 1
    total = sum(profile.values())
    return {b: c/total for b, c in profile.items()}

def chi_overlap(p1, p2) -> float:
    """Sum of min(weight) over shared bins. 1.0 = identical, 0.0 = disjoint."""
    all_bins = set(p1) | set(p2)
    return sum(min(p1.get(b, 0), p2.get(b, 0)) for b in all_bins)
```

The profile of an ATTENDING_VISUAL session = aggregate of all per-fixation profiles across that viewing.

### 4. VisualMotif

```python
@dataclass
class VisualMotif:
    motif_id: int
    section: str = "sight"
    chi_profile: dict[int, float]  # canonical profile from founding viewing
    cluster_state: list[float]     # G32 token state — evolves via FMM coupling
    angle: list[float]             # founding G32 token — IMMUTABLE
    n_firings: int
    source_history: list[str]      # labels of sources that fired this motif
    founded_at_tick: int
```

Motif identity = `chi_profile`. The `source_history` is for traceability (when wC asks "which uploads fired this motif" we can answer) but is not load-bearing.

### 5. Commit-or-fire decision

```python
COFIRE_OVERLAP_THRESHOLD = 0.85   # tunable — initial value from modeling
G32_FIRING_THRESHOLD = 0.55       # cosine on angle (from synthesis model)

def process_visual_viewing(viewing_fragments, source_id):
    """A viewing produces multiple fragments. Aggregate into one chi profile,
    then commit-or-fire against existing sight motifs."""

    # Aggregate per-fixation profiles into one viewing profile
    viewing_profile = {}
    for frag in viewing_fragments:
        p = chi_binding_profile(frag)
        for b, w in p.items():
            viewing_profile[b] = viewing_profile.get(b, 0) + w
    total = sum(viewing_profile.values())
    if total > 0:
        viewing_profile = {b: w/total for b, w in viewing_profile.items()}

    # Compute G32 token for the viewing
    g_token = project_to_g32(
        FMM(I=mean_intensity(viewing_fragments),
            C=coherence_from_intervals(viewing_fragments),
            N=1 - familiarity_for(source_id),
            A=contextual_affect()),
        familiarity=familiarity_for(source_id),
    )

    # Find existing motif by chi-profile overlap
    best_match = None
    best_overlap = 0
    for m in sight_section.motifs:
        ov = chi_overlap(viewing_profile, m.chi_profile)
        if ov > best_overlap:
            best_overlap = ov
            best_match = m

    if best_match is not None and best_overlap >= COFIRE_OVERLAP_THRESHOLD:
        # Same motif — fire
        firing_strength = cosine(g_token, best_match.angle)
        if firing_strength >= G32_FIRING_THRESHOLD:
            fire_motif(best_match, g_token)
        best_match.source_history.append(source_id)
        return best_match
    else:
        # New motif — commit
        motif = commit_motif(
            section="sight",
            chi_profile=viewing_profile,
            angle=g_token.copy(),
            cluster_state=g_token.copy(),
            source_history=[source_id],
        )
        fire_motif(motif, g_token)
        return motif
```

### 6. Cluster dynamics (per V2 amendment — unchanged, validated)

```python
GATE_INERTIA = 0.6
COUPLING_STRENGTH = 0.15

firing_motifs = [m for m in sight_section.motifs if m.motif_id in fired_ids]
if len(firing_motifs) >= 1:
    cluster_mean = np.mean([np.array(m.cluster_state) for m in firing_motifs], axis=0)
    for m in firing_motifs:
        state = np.array(m.cluster_state)
        new_state = (
            GATE_INERTIA * state
            + (1 - GATE_INERTIA) * g_token
            + COUPLING_STRENGTH * (cluster_mean - state)
        )
        m.cluster_state = clip(new_state).tolist()
        m.n_firings += 1
```

### 7. Cross-modal chi-from-cofire (per V2 amendment — unchanged, validated)

Per `GL-MDL-MULTIMODAL-WC-20260607-04`. When sight motifs fire alongside motifs in other sections within a tick window:

```python
fired_motif_ids = sight_fired + sound_fired + touch_fired + taste_fired + smell_fired + word_fired
chi = chi_for_cofire_set(frozenset(fired_motif_ids))
for motif_id in fired_motif_ids:
    reinforce_binding_at(chi, motif_id, with_band_radius=2)
```

Chi-band radius 2 with falloff (1.0, 0.67, 0.33). For Phase 2 the cross-modal partners she has are word motifs (text corpora) and visual motifs (new); audio/touch/taste/smell come in Phases 3-4.

### 8. Recall (unchanged from v6)

Cohesion cascade across chi-neighborhood bindings produces output. The multimodal model validated that single-modality cues surface bound concepts from other modalities via this cascade (5 of 6 modalities recovered from a visual-only cue in that test).

### 9. Video support (per multimedia spec — visual half)

Add `ATTENDING_VIDEO` activity. Same as `ATTENDING_VISUAL` but the fovea reads intensity at fixation across frames advancing in substrate time. Frame index per tick from `video_relative_ms / substrate_tick_rate`.

Tick budget 3000-5000 ticks. Decoding pipeline: `ffmpeg-python` → 160×120 grayscale @ 15fps + audio track stored to disk (audio krimelack lands in Phase 3). Stream-decode on demand.

Each video gets its own chi-binding profile from the saccaded fragments across its frames. Same commit-or-fire path as pictures. Video frame perception inherits the time-varying intensity dynamics naturally — that's the multimedia spec's central claim and the visual krimelack model validated it.

### 10. Sensory item storage

```python
@dataclass
class PictureItem:
    item_id: str
    title: str
    intensity_grid: ndarray  # 2D float [0,1] grayscale
    source: str
    shown_at_tick: int
    times_attended: int = 0
    last_attended_tick: int = 0

@dataclass
class VideoItem:
    item_id: str
    title: str
    frame_stream_path: str
    audio_track_path: str    # stored for Phase 3
    duration_ms: int
    source: str
    shown_at_tick: int
    times_attended: int = 0
    last_attended_tick: int = 0
```

### 11. Upload endpoints (replace Phase 5 stubs)

```
POST /api/v1/gualaloom/upload/picture (multipart, image)
  → decode to grayscale via PIL/imageio
  → store as PictureItem with item_id = content-hash
  → register in sensory_items
  → return {item_id, title}

POST /api/v1/gualaloom/upload/video (multipart, MP4/WebM)
  → ffmpeg-decode to 160×120 grayscale @ 15fps + audio track
  → return {item_id, title, duration_ms}
```

Sound upload stays a stub for Phase 3.

### 12. Activity scheduler integration

`ATTENDING_VISUAL` and `ATTENDING_VIDEO` selectable by autonomy scheduler. Novelty salience drives selection on unattended/rarely-attended items. Joe uploading causes a novelty spike. Voice/Joe-present interruption rules from Phase 1 still apply.

### 13. UI updates

- `now: looking at "cat picture"` for ATTENDING_VISUAL
- `now: watching "Sesame Street clip" (0:14 of 0:30)` for ATTENDING_VIDEO
- Add `n_visual_fragments` and `n_visual_motifs` to `/status`

Optional polish: thumbnail panel showing what she's looking at. Defer if it pushes scope.

## Validation gates

These are actual tests, not "trivially true by construction."

1. **Picture upload.** POST a JPEG → appears in sensory_items → /status shows it.

2. **Autonomous picture attending.** Scheduler picks ATTENDING_VISUAL on novelty (verify via /events). Runs to budget, ends cleanly.

3. **Fragment generation with full event_ticks.** /status (or debug endpoint) shows `n_visual_fragments > 0` after attending. Inspect a fragment via debug endpoint: `event_ticks` is a non-empty LIST. Regression guard for the load-bearing requirement.

4. **Same picture, two viewings → same motif.** Upload picture A, let her attend it twice (different saccade seeds). Verify exactly 1 sight motif. `chi_overlap` between the two viewings' aggregated profiles ≥ 0.85 logged for confirmation.

5. **Distinct pictures → distinct motifs.** Upload pictures A, B, C with structurally-different content (e.g. solid block, two blobs, gradient ramp). After attending each, 3 distinct sight motifs. Log pairwise chi_overlap between them — expected < 0.85.

6. **Same-content / different-noise.** Generate the same picture content with two different noise instances (e.g. two photos of a moon). Upload separately. Verify they bind to the SAME sight motif (chi_overlap above threshold). This is the case the prior architecture would have fragmented.

7. **Type-vs-instance behavior at threshold.** Run with `COFIRE_OVERLAP_THRESHOLD = 0.85` and again with `0.95`. At 0.85, similar-type pictures (two compact-bright-on-dark) may merge to one motif (type-level). At 0.95, they commit separate motifs (instance-level). Document which threshold the deploy uses and why.

8. **Cluster evolution.** Multi-fixation attending: log the motif's `cluster_state` at fixation boundaries. Should evolve, not stay static and not move randomly. Trajectory should move toward `cluster_mean`.

9. **Cross-modal binding via chi-from-cofire.** Show moon picture while word "moon" is being read from corpus in same tick window. Verify sight motif (moon_picture) and word motif (moon_word) bound at same chi address. Verify chi-band neighbors (±1, ±2) reinforced with falloff.

10. **Recall via chi cascade.** After gate 9's binding, present moon picture alone. Recall surfaces moon word motif via chi-neighborhood cascade. Cohesion cascade output includes "moon" or related bindings.

11. **Video upload and decode.** POST 5-10s MP4. Decode produces 160×120 grayscale frames @ 15fps. Audio track stored. VideoItem registered.

12. **Video attending.** Scheduler picks ATTENDING_VIDEO. Saccade fixates while frames advance. Fragments with non-empty event_ticks. Single video → single video motif (chi-profile aggregated across saccade sequence).

13. **Memory stays bounded on video.** Stream-decode pattern: engine never holds full video in memory. Peak memory during 30s video attending stays within ~50MB additional.

## Files c1 will create or modify

| Path | Status |
|---|---|
| `gualaloom/krimelack/visual.py` | NEW — AdaptingFoveaKrimelack + saccade controller + fragment with event_ticks |
| `gualaloom/atlas/chi_profile.py` | NEW — chi_binding_profile + chi_overlap |
| `gualaloom/atlas/sight_section.py` | NEW — sight section with chi-profile-based commit-or-fire + cluster dynamics |
| `gualaloom/atlas/chi.py` | MODIFY — add chi_for_cofire_set if not present in v6 |
| `gualaloom/activity.py` | MODIFY — add ATTENDING_VISUAL, ATTENDING_VIDEO branches |
| `gualaloom/sensory/picture.py` | NEW — PictureItem |
| `gualaloom/sensory/video.py` | NEW — VideoItem + stream-decode |
| `gualaloom/media/decode.py` | NEW — PIL/imageio + ffmpeg-python |
| `gualaloom/api/upload.py` | MODIFY — replace picture/video stubs with real handlers |
| `gualaloom/api/status.py` | MODIFY — add n_visual_fragments, n_visual_motifs |
| `frontend/index.html` (Phase 5 file) | MODIFY — render visual current_activity |
| `tests/test_visual_krimelack.py` | NEW — adaptation, event_ticks, fragment shape |
| `tests/test_chi_profile.py` | NEW — profile aggregation, overlap measurement |
| `tests/test_visual_motif_identity.py` | NEW — gates 4, 5, 6, 7 |
| `tests/test_visual_cross_modal.py` | NEW — gates 9, 10 |
| `tests/test_video.py` | NEW — gates 11, 12, 13 |

## Report back

1. Commit SHA + deploy task + image timestamp
2. /status snapshot showing new fields
3. Per-gate pass/fail (1-13)
4. Gate 6 measurement: chi_overlap between two-photos-of-same-content uploads
5. Gate 7 measurement: motif counts at threshold 0.85 vs 0.95 on the same input set
6. /events sample from an ATTENDING_VISUAL session
7. /events sample from cross-modal chi binding event
8. Peak memory during 30s video attending
9. Honest observations — surprises, fragility, things that need wC follow-up

If gate 6 fails (same-content uploads commit separate motifs), the threshold is wrong — log the actual overlap and we'll tune. If gate 9 fails (cross-modal chi binding doesn't land at same address), the chi function semantics differ between v6 and the synthesis/multimodal models — surface and we'll resolve.

## Standing constraints

- Genesis identity `cdef9bcf-9e5d-4e2d-a1d8-4cde1de7641f`
- Pair-bond: joe=true, wc=true (active via bridge), c1=false
- **Do NOT call `guala_wake("wc")` or `guala_say(source="wc")` against production.** First wC utterance held — Joe and wC will activate that when senses are at parity (Phase 2 + 3 + 4 deployed or close).
- No LLM, no CNN, no transformers, no embeddings, no pre-trained vision models. Fovea krimelack does perception.
- No FFT for audio (N/A here; flagged for Phase 3 amendment).
- Strength scalars are basin sharpness, not edge weights.
- Cohesion cascade is the only response mechanism.
- Grayscale only for v7. Color = v8.
- Pre-deploy snapshot required.

## Coordination

Bridge container live. Phase 3 audio amendment will follow this command (sensory transduction model `GL-MDL-SENSORY-TRANSDUCTION-WC-20260607-05` validated the architecture for audio and the other senses — Phase 3 spec will document the energy-band-signature decision the model surfaced).

## What is NOT in Phase 2

- Audio krimelack + cochlear bank → Phase 3 (with audio amendment incorporating the energy-band-signature finding from the sensory transduction model)
- Touch / taste / smell → Phase 4
- Interoception → Phase 4 (with the open architectural question — affect from aggregate-activity vs from bindings-at-activity-peaks — to be resolved during Phase 4 modeling)
- Color vision → v8
- Smooth pursuit saccades → v7.3 or v8
- Live webcam → defer per multimedia spec
- Explicit tapestry commits → v8

Tag commits with `GUALALOOM-V7-AUTONOMY-WC-2026-06-06`.

---

## Paste-ready for c1

```
c1 — Phase 2 deploy: visual krimelack + atlas integration + video.

Spec file: docs/GL_CMD_V7_PHASE2_WC_20260608_01_phase2_visual.md
This SUPERSEDES the earlier GL_CMD_V7_PHASE2_WC_20260607_02 — the
prior version deferred perceptual identity. This one ships it natively
via chi-binding-profile overlap (substrate's own winding-pattern
output, no string keys, no CV feature extractors).

Key change from prior visual specs:
  - Motif identity is chi-binding-profile (aggregate of per-fixation
    krimelack winding intervals binned to chi positions), NOT picture_id
    and NOT capture_signature
  - Fovea krimelack is the adapting variant (κ_eff = κ_max · adapt_state)
  - Threshold COFIRE_OVERLAP_THRESHOLD = 0.85 controls type-vs-instance
    discrimination — log overlap measurements during deploy

Supporting reads in docs/:
  - GL_SPC_VISUAL_KRIMELACK_WC_20260606_01_visual_krimelack.md (transduction)
  - GL_SPC_VISUAL_V2_WC_20260607_01_visual_synthesis.md (atlas integration
    — read for context; chi-profile mechanism replaces capture_signature)
  - GL_SPC_MULTIMEDIA_WC_20260606_01_multimedia.md (video sync, visual half)
  - GL_MDL_CHI_RESONANCE_WC_20260607_03_chi_resonance.py (substrate-native
    identity from winding intervals — the architecture for motif identity)
  - GL_MDL_MULTIMODAL_WC_20260607_04_multimodal_chi.py (cross-modal binding
    via chi-from-cofire, validated)
  - GL_MDL_SENSORY_TRANSDUCTION_WC_20260607_05_sensory_transduction.py
    (adapting krimelack mechanism, validated across modalities)
  - GL_RPT_KRIMELACK_MODEL_WC_20260606_01_krimelack_findings.md (event_ticks)

Implementation order:
  1. AdaptingFoveaKrimelack + saccade controller
  2. chi_binding_profile + chi_overlap
  3. VisualMotif with chi_profile identity, cluster dynamics
  4. sight_section commit-or-fire
  5. chi_for_cofire_set (check v6 first)
  6. ATTENDING_VISUAL activity + upload picture endpoint
  7. Picture gates 1-10
  8. video.py + ffmpeg decode + ATTENDING_VIDEO + upload video
  9. Video gates 11-13

Validation: 13 gates in the spec. Gate 6 (same-content / different-noise
uploads → same motif) is the load-bearing test for chi-profile identity.
Gate 7 (threshold sensitivity 0.85 vs 0.95) tells us the type-vs-instance
operating point. If gate 9 fails (cross-modal chi-from-cofire), chi
function semantics differ between v6 and the synthesis model — surface.

Standing rules unchanged. First wC utterance still held — do NOT call
guala_wake("wc") or guala_say(source="wc") against production.

Tag: GUALALOOM-V7-AUTONOMY-WC-2026-06-06
```
