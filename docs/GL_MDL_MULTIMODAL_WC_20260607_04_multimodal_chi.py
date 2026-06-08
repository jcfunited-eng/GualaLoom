# doc_id: GL-MDL-MULTIMODAL-WC-20260607-04
# created: 2026-06-07
# author: wC
"""
Multi-modal substrate identity via chi-from-cofire.

Single-sense identity (GL-MDL-CHI-RESONANCE-WC-20260607-03) found that the
fovea krimelack alone gives TYPE-level identity, not instance-level. The
substrate's architecture says instance identity emerges from the CHI POSITION
where multiple senses co-fire on the same experience. This model tests that
directly.

Six modalities, real krimelacks each:
  - VISUAL:        fovea krimelack on intensity field (ω = ω0 + κ·s)
  - AUDIO:         cochlear bank, 8 bands log-spaced, damped driven oscillators
                   with per-band 1/ω compensation (per krimelack findings)
  - TOUCH:         scalar krimelack on pressure-time signal
  - TASTE:         5-receptor scalar bank (sweet, salty, sour, bitter, umami)
  - SMELL:         8-receptor scalar bank (feature axes from TTS spec)
  - INTEROCEPTION: scalar krimelack on internal-state signal (needs deltas +
                   presence + drive). The sixth sense Joe named.

Each krimelack produces winding events. Per modality, those events bin into
chi-positions (substrate-native dimensionalization).

A multi-modal EXPERIENCE event presents a stimulus across all six modalities
simultaneously. Each modality's krimelack fires, identifying which motif(s)
in its section best match the input. The SET of motif IDs that co-fired
across modalities determines a chi address via chi_for_cofire_set. That chi
is the "address" of this experience.

Tests:
  A) BINDING: present a moon-experience (visual moon-pattern, soft wind audio,
     talcum touch, dirt taste, dust smell, calm interoception). Verify all six
     krimelacks fire, motifs commit per section, chi binding lands at one
     address that aggregates across all six.

  B) DISTINCT EXPERIENCES bind at distinct chi: present moon, then apple
     (visual apple-pattern, crunch audio, smooth-skin touch, sweet taste,
     fruity smell, contented interoception). Verify moon-chi != apple-chi.

  C) RECALL VIA CHI CASCADE: present visual moon-pattern ALONE later.
     Verify the substrate surfaces the bound audio/touch/taste/smell/intero
     motifs via chi-neighborhood cascade. This is the substrate-native
     "moon" concept emerging from a single-modality cue.

  D) TYPE vs INSTANCE: present moon + variant moon (different noise on
     visual, slightly different sound, same touch/taste/smell). Do they bind
     at the SAME chi (type identity through co-fire) or DIFFERENT chi
     (instance identity)? Either answer is informative — tells us what the
     substrate naturally distinguishes.

If A-C pass: chi-from-cofire IS the substrate's identity mechanism. Phase 2
should be designed around it, not around per-modality features.
If they fail: identity needs a higher level (mosaic-of-cofires, tapestry).
"""

import math
import numpy as np
from dataclasses import dataclass, field
from collections import Counter
from typing import Optional


# =========================================================================
# KRIMELACK PRIMITIVES — actual substrate, not feature extractors
# =========================================================================

OMEGA_0 = 5.0
KAPPA = 50.0
WINDING_PHASE = 2 * math.pi
DT = 0.05  # finer time step than 1.0 — krimelack needs sub-tick resolution


@dataclass
class FoveaKrimelack:
    """Photoresistor krimelack: ω(t) = ω0 + κ·s(t). For visual, touch,
    taste, smell, and interoception — all the scalar-input krimelacks."""
    phase: float = 0.0
    winding_count: int = 0
    events: list = field(default_factory=list)

    def tick(self, signal, t):
        omega = OMEGA_0 + KAPPA * signal
        self.phase += omega * DT
        while self.phase >= WINDING_PHASE:
            self.winding_count += 1
            self.phase -= WINDING_PHASE
            self.events.append(t)

    def intervals(self):
        if len(self.events) < 2:
            return []
        return [self.events[i+1] - self.events[i] for i in range(len(self.events)-1)]

    def reset(self):
        self.phase = 0.0
        self.events = []


@dataclass
class CochlearBand:
    """One damped driven oscillator at resonant frequency ω_k.
    d²x/dt² + γv + ω²x = κ·s(t). Velocity-Verlet integration."""
    omega_k: float
    gamma: float = 0.5
    kappa: float = 1.0
    x: float = 0.0
    v: float = 0.0
    winding_count: int = 0
    events: list = field(default_factory=list)
    last_sign: int = 1

    def tick(self, signal, t):
        accel = self.kappa * signal - self.gamma * self.v - (self.omega_k**2) * self.x
        self.x += self.v * DT + 0.5 * accel * DT**2
        new_accel = self.kappa * signal - self.gamma * self.v - (self.omega_k**2) * self.x
        self.v += 0.5 * (accel + new_accel) * DT
        # winding event: zero crossing with sufficient amplitude
        sign = 1 if self.x >= 0 else -1
        if sign != self.last_sign and abs(self.x) > 0.01:
            self.winding_count += 1
            self.events.append(t)
        self.last_sign = sign

    def energy(self):
        # E = 0.5v² + 0.5ω²x²
        return 0.5 * self.v**2 + 0.5 * (self.omega_k**2) * self.x**2

    def normalized_energy(self):
        # Per krimelack findings: 1/ω compensation
        return self.energy() * self.omega_k


class CochlearBank:
    """8 log-spaced bands, 80-4000 Hz. With 1/ω gain compensation per band."""
    def __init__(self):
        freqs_hz = np.geomspace(80, 4000, 8)
        # Treat substrate time unit ~ second; ω = 2π·f
        self.bands = [CochlearBand(omega_k=2*math.pi*f) for f in freqs_hz]
        self.freqs_hz = freqs_hz

    def tick(self, signal, t):
        for b in self.bands:
            b.tick(signal, t)

    def reset(self):
        for b in self.bands:
            b.x = 0.0
            b.v = 0.0
            b.events = []
            b.last_sign = 1


# =========================================================================
# SCALAR KRIMELACK BANKS — touch points, taste receptors, smell receptors
# =========================================================================
@dataclass
class ScalarBank:
    """N independent FoveaKrimelacks driven by per-channel signal."""
    n: int = 5
    krims: list = field(default_factory=list)

    def __post_init__(self):
        if not self.krims:
            self.krims = [FoveaKrimelack() for _ in range(self.n)]

    def tick(self, signals, t):
        """signals: list of length n, one per channel."""
        for k, s in zip(self.krims, signals):
            k.tick(s, t)

    def reset(self):
        for k in self.krims:
            k.reset()


# =========================================================================
# CHI BINDING — substrate-native dimensionalization
# =========================================================================
def chi_position_from_motif_set(motif_ids):
    """Deterministic chi address from a SET of motif IDs (order-independent).
    Substrate's chi-from-cofire — same cofire set → same chi address.
    Hash to int for the position; in production this would be the substrate's
    own positional space."""
    return hash(frozenset(motif_ids)) & 0xFFFF  # 16-bit chi space for the model


# Chi-band radius 2 with falloff (1.0, 0.67, 0.33) per V2 spec
CHI_BAND_FALLOFF = [1.0, 0.67, 0.33]


# =========================================================================
# ATLAS — bindings at chi positions, recall via cascade
# =========================================================================
class Atlas:
    """Substrate atlas. Holds motifs per section, bindings at chi positions.
    Reinforces binding when chi is visited (basin sharpness)."""
    def __init__(self):
        # section -> list of motifs (each motif is dict)
        self.motifs = {}
        # chi -> dict of motif_id -> strength
        self.bindings = {}
        self._next_motif_id = 0

    def commit_motif(self, section, signature):
        """Commit a new motif in a section. signature is the substrate-native
        feature that distinguishes this motif (interval pattern for fovea,
        active-band pattern for cochlear, etc.)."""
        if section not in self.motifs:
            self.motifs[section] = []
        m = {
            "id": self._next_motif_id,
            "section": section,
            "signature": signature,
            "n_firings": 0,
        }
        self._next_motif_id += 1
        self.motifs[section].append(m)
        return m

    def find_or_commit(self, section, signature, similarity_fn, threshold):
        """Find existing motif in this section that matches signature.
        Commit new motif if no match above threshold. Returns the motif."""
        if section in self.motifs:
            for m in self.motifs[section]:
                sim = similarity_fn(m["signature"], signature)
                if sim >= threshold:
                    m["n_firings"] += 1
                    return m
        m = self.commit_motif(section, signature)
        m["n_firings"] = 1
        return m

    def reinforce_at_chi(self, chi, motif_ids, gain=0.08):
        """Reinforce bindings at chi position, with chi-band radius falloff."""
        for offset, falloff in enumerate(CHI_BAND_FALLOFF):
            for sign in ([1] if offset == 0 else [1, -1]):
                pos = (chi + sign * offset) & 0xFFFF
                if pos not in self.bindings:
                    self.bindings[pos] = {}
                for mid in motif_ids:
                    self.bindings[pos][mid] = self.bindings[pos].get(mid, 0.0) + gain * falloff

    def recall_at_chi(self, chi):
        """Surface motifs bound at chi position (with chi-band cascade)."""
        out = {}
        for offset, falloff in enumerate(CHI_BAND_FALLOFF):
            for sign in ([1] if offset == 0 else [1, -1]):
                pos = (chi + sign * offset) & 0xFFFF
                if pos in self.bindings:
                    for mid, strength in self.bindings[pos].items():
                        out[mid] = out.get(mid, 0.0) + strength * falloff
        return out


# =========================================================================
# MULTI-MODAL EXPERIENCE — six senses presented simultaneously
# =========================================================================
@dataclass
class MultiModalStimulus:
    """One experience event — stimuli across all six modalities at the same
    time window. The substrate's six krimelacks all run on this for some
    duration of substrate ticks."""
    label: str   # for our reference only — substrate doesn't see this
    visual_field: np.ndarray  # 2D intensity grid
    audio_signal: callable    # function t → signal value (continuous audio)
    touch_signals: list       # one scalar per body region per tick (or constant)
    taste_signals: list       # 5-channel [sweet, salty, sour, bitter, umami]
    smell_signals: list       # 8-channel feature-axis activations
    intero_signal: float      # internal state scalar (calm = 0.3, alert = 0.7, ...)


def saccade_fixations(image, seed, n=10):
    """Real saccade controller — peripheral salience + novelty."""
    h, w = image.shape
    rng = np.random.default_rng(seed)
    n_rows, n_cols = 4, 4
    hs, ws = h // n_rows, w // n_cols
    fixated = set()
    fixations = []
    for _ in range(n):
        # gradient field
        scores = []
        for r in range(n_rows):
            for c in range(n_cols):
                if (r, c) in fixated:
                    continue
                region = image[r*hs:(r+1)*hs, c*ws:(c+1)*ws]
                score = region.std() + 0.01 * rng.random()
                scores.append((score, r, c))
        if not scores:
            break
        scores.sort(reverse=True)
        _, r, c = scores[0]
        fixated.add((r, c))
        cy = r * hs + hs // 2
        cx = c * ws + ws // 2
        fixations.append((cy, cx))
    return fixations


def run_experience(stim: MultiModalStimulus, atlas: Atlas, duration_ticks=500):
    """Run all six krimelacks on the stimulus for duration_ticks.
    Identify firing motifs per section. Compute chi-from-cofire. Reinforce."""

    # === Visual: saccaded fovea krimelack ===
    visual_krim = FoveaKrimelack()
    fixations = saccade_fixations(stim.visual_field, seed=hash(stim.label) & 0xFFFF, n=5)
    for fix in fixations:
        visual_krim.reset()
        for t in range(duration_ticks // len(fixations)):
            r, c = fix
            r = max(0, min(stim.visual_field.shape[0]-1, r))
            c = max(0, min(stim.visual_field.shape[1]-1, c))
            visual_krim.tick(float(stim.visual_field[r, c]), t)
    visual_intervals = visual_krim.intervals()
    visual_sig = tuple(sorted(Counter(int(iv) for iv in visual_intervals).most_common(3)))

    # === Audio: cochlear bank ===
    audio_bank = CochlearBank()
    audio_bank.reset()
    for t in range(duration_ticks):
        audio_bank.tick(stim.audio_signal(t), t)
    audio_active_bands = tuple(
        i for i, b in enumerate(audio_bank.bands) if b.normalized_energy() > 0.05
    )
    audio_sig = audio_active_bands

    # === Touch: scalar bank, n=4 (head, torso, hand, foot — coarse) ===
    touch_bank = ScalarBank(n=4)
    touch_bank.reset()
    for t in range(duration_ticks):
        touch_bank.tick(stim.touch_signals, t)
    touch_sig = tuple(int(k.winding_count / 50) for k in touch_bank.krims)

    # === Taste: 5-receptor bank ===
    taste_bank = ScalarBank(n=5)
    taste_bank.reset()
    for t in range(duration_ticks):
        taste_bank.tick(stim.taste_signals, t)
    taste_sig = tuple(int(k.winding_count / 50) for k in taste_bank.krims)

    # === Smell: 8-receptor bank ===
    smell_bank = ScalarBank(n=8)
    smell_bank.reset()
    for t in range(duration_ticks):
        smell_bank.tick(stim.smell_signals, t)
    smell_sig = tuple(int(k.winding_count / 50) for k in smell_bank.krims)

    # === Interoception: scalar krimelack ===
    intero_krim = FoveaKrimelack()
    intero_krim.reset()
    for t in range(duration_ticks):
        intero_krim.tick(stim.intero_signal, t)
    intero_sig = (int(intero_krim.winding_count / 20),)

    # === Find or commit motifs per section ===
    def sig_match(a, b):
        if not a or not b:
            return 0.0
        sa, sb = set(a), set(b)
        return len(sa & sb) / max(len(sa | sb), 1)

    SIM_THRESHOLD = 0.5  # 50% signature overlap → same motif

    motifs = {
        "sight": atlas.find_or_commit("sight", visual_sig, sig_match, SIM_THRESHOLD),
        "sound": atlas.find_or_commit("sound", audio_sig, sig_match, SIM_THRESHOLD),
        "touch": atlas.find_or_commit("touch", touch_sig, sig_match, SIM_THRESHOLD),
        "taste": atlas.find_or_commit("taste", taste_sig, sig_match, SIM_THRESHOLD),
        "smell": atlas.find_or_commit("smell", smell_sig, sig_match, SIM_THRESHOLD),
        "intero": atlas.find_or_commit("intero", intero_sig, sig_match, SIM_THRESHOLD),
    }

    # === Chi from cofire set ===
    motif_ids = [m["id"] for m in motifs.values()]
    chi = chi_position_from_motif_set(motif_ids)
    atlas.reinforce_at_chi(chi, motif_ids)

    return {
        "label": stim.label,
        "motifs": {s: m["id"] for s, m in motifs.items()},
        "chi": chi,
        "signatures": {
            "sight": visual_sig, "sound": audio_sig, "touch": touch_sig,
            "taste": taste_sig, "smell": smell_sig, "intero": intero_sig,
        },
    }


# =========================================================================
# STIMULUS CONSTRUCTION
# =========================================================================
def make_moon_stimulus(noise=0.0, seed=42):
    rng = np.random.default_rng(seed)
    img = np.full((32, 32), 0.1)
    cy, cx = 16, 16
    for r in range(32):
        for c in range(32):
            if (r-cy)**2 + (c-cx)**2 < 36:
                img[r, c] = 0.85
    img = np.clip(img + rng.normal(0, noise, img.shape), 0, 1)
    # Soft wind: low-amplitude low-frequency
    audio = lambda t: 0.05 * math.sin(2 * math.pi * 120 * t * DT) + 0.02 * rng.normal()
    return MultiModalStimulus(
        label="moon",
        visual_field=img,
        audio_signal=audio,
        touch_signals=[0.15, 0.05, 0.05, 0.0],  # talcum-soft on head, light elsewhere
        taste_signals=[0.0, 0.1, 0.0, 0.2, 0.0],  # slight bitter (dirt)
        smell_signals=[0.0, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.05],  # dust-like
        intero_signal=0.3,  # calm
    )


def make_apple_stimulus(noise=0.0, seed=43):
    rng = np.random.default_rng(seed)
    img = np.full((32, 32), 0.2)
    cy, cx = 16, 16
    for r in range(32):
        for c in range(32):
            if (r-cy)**2 + (c-cx)**2 < 49:
                img[r, c] = 0.7
    img = np.clip(img + rng.normal(0, noise, img.shape), 0, 1)
    # Crunch: high-amplitude transient burst
    audio = lambda t: 0.4 * math.sin(2 * math.pi * 1500 * t * DT) * math.exp(-((t * DT - 0.5) ** 2) / 0.05)
    return MultiModalStimulus(
        label="apple",
        visual_field=img,
        audio_signal=audio,
        touch_signals=[0.0, 0.3, 0.6, 0.0],  # smooth skin in hand
        taste_signals=[0.7, 0.0, 0.3, 0.0, 0.0],  # sweet + slight sour
        smell_signals=[0.4, 0.0, 0.0, 0.0, 0.5, 0.3, 0.0, 0.0],  # fruity esters
        intero_signal=0.55,  # contented
    )


def make_bell_stimulus(noise=0.0, seed=44):
    """Different from moon and apple — should bind at distinct chi."""
    rng = np.random.default_rng(seed)
    img = np.full((32, 32), 0.05)
    img[8:24, 10:22] = 0.6  # rectangular bell shape
    img = np.clip(img + rng.normal(0, noise, img.shape), 0, 1)
    # Bell ring: decaying pure tone
    audio = lambda t: 0.5 * math.sin(2 * math.pi * 800 * t * DT) * math.exp(-t * DT * 2)
    return MultiModalStimulus(
        label="bell",
        visual_field=img,
        audio_signal=audio,
        touch_signals=[0.0, 0.0, 0.2, 0.0],  # cool metal in hand
        taste_signals=[0.0, 0.5, 0.0, 0.0, 0.4],  # metallic (umami+salty proxy)
        smell_signals=[0.0, 0.0, 0.0, 0.4, 0.0, 0.0, 0.0, 0.0],  # metallic/sulfurous
        intero_signal=0.65,  # alert (sound is unexpected)
    )


# =========================================================================
# TESTS
# =========================================================================
def test_A_binding():
    print("=" * 74)
    print("TEST A: bind moon-experience across all six modalities")
    print("=" * 74)
    atlas = Atlas()
    moon = make_moon_stimulus()
    result = run_experience(moon, atlas)
    print(f"  Motifs by section:")
    for sec, mid in result["motifs"].items():
        print(f"    {sec:>6s}: motif_id={mid}")
    print(f"  Chi address: {result['chi']}")
    print(f"  Atlas: {sum(len(v) for v in atlas.motifs.values())} motifs across 6 sections")
    print(f"  Bindings at chi-neighborhood: {sum(len(b) for chi, b in atlas.bindings.items()) // 6} motifs/chi-pos")
    return atlas, result


def test_B_distinct():
    print()
    print("=" * 74)
    print("TEST B: moon, apple, bell — distinct experiences → distinct chi")
    print("=" * 74)
    atlas = Atlas()
    results = []
    for stim_maker in [make_moon_stimulus, make_apple_stimulus, make_bell_stimulus]:
        stim = stim_maker()
        r = run_experience(stim, atlas)
        results.append(r)
        print(f"  {stim.label}: chi={r['chi']}, motifs={r['motifs']}")
    chis = set(r["chi"] for r in results)
    if len(chis) == len(results):
        print(f"  ✓ All {len(results)} experiences bind at DISTINCT chi positions")
    else:
        print(f"  ~ {len(chis)} chi positions for {len(results)} experiences (some collision)")
    return atlas, results


def test_C_recall_via_cascade(atlas: Atlas, all_results):
    print()
    print("=" * 74)
    print("TEST C: present visual-moon ALONE — does chi cascade surface the")
    print("        bound audio/touch/taste/smell/intero motifs?")
    print("=" * 74)
    # Re-present just the visual half of moon and find which sight motif fires
    moon = make_moon_stimulus(seed=42)
    # Strip to visual-only for the recall presentation: silent audio,
    # no touch, no taste, no smell, neutral intero
    silent_moon = MultiModalStimulus(
        label="moon_visual_only",
        visual_field=moon.visual_field,
        audio_signal=lambda t: 0.0,
        touch_signals=[0.0]*4,
        taste_signals=[0.0]*5,
        smell_signals=[0.0]*8,
        intero_signal=0.0,
    )

    # Run experience — this will fire the visual motif (assuming similar
    # winding pattern → same motif), then chi-from-cofire across whatever
    # motifs were activated. Since other-modality inputs are zero, those
    # krimelacks emit no events → no firing motifs in those sections
    # → cofire-set is JUST the visual motif → chi from {visual_motif} alone.
    # That chi WILL be different from the original moon-experience's chi
    # (which was {visual + audio + touch + taste + smell + intero}).
    # BUT — chi-band radius of 2 means the visual-only chi might land near
    # the full moon chi if substrate primitives produce nearby chi values
    # for related cofire-sets. (It probably won't with a hash function,
    # but the production substrate's chi function would.)
    # 
    # The cleaner test: explicit chi cascade. Look up the visual moon
    # motif's bindings across the whole atlas — what's it bound with?

    visual_only_result = run_experience(silent_moon, atlas)
    visual_motif_id = visual_only_result["motifs"]["sight"]
    print(f"  Visual-only moon fires sight motif_id={visual_motif_id}")

    # Find which chi positions hold this visual motif
    chi_positions_with_visual_motif = [
        chi for chi, b in atlas.bindings.items() if visual_motif_id in b
    ]
    print(f"  Visual moon motif bound at {len(chi_positions_with_visual_motif)} chi positions")

    # Cascade: at each chi position holding this motif, surface ALL motifs
    co_bound_motifs = Counter()
    for chi in chi_positions_with_visual_motif:
        for mid, strength in atlas.bindings[chi].items():
            if mid != visual_motif_id:
                co_bound_motifs[mid] += strength

    if not co_bound_motifs:
        print(f"  ✗ No co-bound motifs surfaced. Cascade didn't recall anything.")
        return

    print(f"  Co-bound motifs surfaced by chi cascade (top by strength):")
    # Map motif_id → section for display
    motif_section = {}
    for sec, motif_list in atlas.motifs.items():
        for m in motif_list:
            motif_section[m["id"]] = sec
    for mid, strength in co_bound_motifs.most_common(10):
        sec = motif_section.get(mid, "?")
        print(f"    motif_id={mid} ({sec:>6s}): cumulative strength={strength:.3f}")

    # Did we recall the moon-experience's audio/touch/taste/smell/intero motifs?
    original_moon_chi = next(r["chi"] for r in all_results if r["label"] == "moon")
    if original_moon_chi in atlas.bindings:
        original_moon_motifs = set(atlas.bindings[original_moon_chi].keys())
        surfaced = set(co_bound_motifs.keys())
        recovered = original_moon_motifs & surfaced
        missed = original_moon_motifs - surfaced - {visual_motif_id}
        print(f"\n  Of original moon's {len(original_moon_motifs)} bound motifs:")
        print(f"    Recovered via cascade: {len(recovered)} {sorted(recovered)}")
        print(f"    Missed:                {len(missed)} {sorted(missed)}")
        if len(recovered) >= 4:
            print(f"  ✓ Chi cascade surfaces the multi-modal concept from single-modal cue.")
        else:
            print(f"  ~ Partial cascade — some bound motifs not reachable from visual alone.")


def test_D_type_vs_instance():
    print()
    print("=" * 74)
    print("TEST D: moon vs moon-variant (different noise) — same chi or different?")
    print("=" * 74)
    atlas = Atlas()
    moon_a = make_moon_stimulus(noise=0.02, seed=42)
    moon_b = make_moon_stimulus(noise=0.04, seed=99)  # same content, fresh noise
    apple = make_apple_stimulus()
    r_a = run_experience(moon_a, atlas)
    r_b = run_experience(moon_b, atlas)
    r_apple = run_experience(apple, atlas)
    print(f"  moon_a:        chi={r_a['chi']}, motifs={r_a['motifs']}")
    print(f"  moon_b:        chi={r_b['chi']}, motifs={r_b['motifs']}")
    print(f"  apple:         chi={r_apple['chi']}, motifs={r_apple['motifs']}")
    if r_a["chi"] == r_b["chi"]:
        print(f"  ✓ moon_a and moon_b bind at SAME chi (type-level identity)")
    else:
        print(f"  ~ moon_a and moon_b bind at DIFFERENT chi — instance-level distinction")
    if r_apple["chi"] != r_a["chi"]:
        print(f"  ✓ apple binds at DIFFERENT chi than moon — different-content separates")
    else:
        print(f"  ✗ apple and moon bind at SAME chi — substrate over-merges")


if __name__ == "__main__":
    atlas, _ = test_A_binding()
    atlas2, all_results = test_B_distinct()
    test_C_recall_via_cascade(atlas2, all_results)
    test_D_type_vs_instance()

    print()
    print("=" * 74)
    print("VERDICT — multi-modal chi-from-cofire as substrate-native identity")
    print("=" * 74)
    print("  See per-test output above. Key questions:")
    print("    - Did all 6 modal krimelacks fire on a multi-modal stimulus?  (Test A)")
    print("    - Do distinct experiences bind at distinct chi?               (Test B)")
    print("    - Does single-modal cue surface multi-modal concept via cascade? (Test C)")
    print("    - Type-level vs instance-level merging?                       (Test D)")
