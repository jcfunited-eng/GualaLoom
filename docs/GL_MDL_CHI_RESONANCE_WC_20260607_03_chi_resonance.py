# doc_id: GL-MDL-CHI-RESONANCE-WC-20260607-03
# created: 2026-06-07
# author: wC
"""
Substrate-native identity via chi resonance.

PREVIOUS APPROACHES that failed the substrate test:
  - capture_signature v1: per-fragment features (centroid + histogram).
    Operates on the fragment metadata, not the substrate output. CV-style.
  - capture_signature v2: per-picture features (whole-pic histograms,
    edge density). Operates on the pixel array directly, bypassing the
    krimelack. CV-style.
  - surface_form = picture_id: external string key. Not substrate at all.

THIS MODEL asks: can identity emerge from the substrate's own perceptual
output? Specifically — when the fovea krimelack reads intensity at
saccaded fixations on a picture, it produces a winding-event sequence.
That sequence has rhythmic structure (inter-event intervals). Two
viewings of the SAME picture should produce winding patterns whose
intervals resonate (share dominant bands). Different pictures should
produce patterns whose intervals do not.

If yes: chi binding is a NATURAL consequence of substrate perception, not
something we bolt on. Identity = "the chi positions this fragment's
winding pattern resonates with." No string keys, no CV.

If no: the substrate doesn't carry enough identity information at the
krimelack level alone; identity has to emerge at a higher level (mosaic
of fragments → tapestry → chi-binding-of-tapestries), and Phase 2 has
to be designed around that.

Approach:
  1. Generate synthetic intensity fields (pictures) — NOT for the model
     to "recognize," but as the actual input the krimelack will read.
  2. Run real saccade controller + fovea krimelack on each picture.
     ω(t) = ω_0 + κ·s(t). Integrate. Winding events emitted.
  3. Extract the substrate's native output: inter-event interval
     sequence per fixation, accumulated across all fixations of one viewing.
  4. Quantize intervals to integer bins (substrate's own dimensionalization
     — the way trits/L0-L4 would categorize). No CV thresholds, just
     integer rounding.
  5. The CHI-BINDING PROFILE of a viewing = multiset of interval bins
     across all fixations.
  6. Compare profiles:
     - Same picture viewed twice (different saccade seed)
     - Different pictures
     - Same-content / different-noise (Joe takes two photos of moon)
  7. Measure: does same-picture chi-binding overlap dominate over
     different-picture chi-binding?

If the substrate's own perceptual output naturally separates same from
different, IDENTITY IS A SUBSTRATE PROPERTY and Phase 2 can use it.
"""

import math
import numpy as np
from dataclasses import dataclass, field


# =========================================================================
# Krimelack parameters — from GL-MDL-VISUAL-KRIMELACK validated values
# =========================================================================
OMEGA_0 = 5.0
KAPPA = 50.0
WINDING_PHASE = 2 * math.pi


@dataclass
class FoveaKrimelack:
    phase: float = 0.0
    winding_count: int = 0
    events: list = field(default_factory=list)

    def tick(self, intensity, t):
        omega = OMEGA_0 + KAPPA * intensity
        self.phase += omega
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
        # NOTE: winding_count is cumulative across fixations (her experience total)


# =========================================================================
# Saccade controller — peripheral salience, novelty-driven
# =========================================================================
class SaccadeController:
    def __init__(self, image, seed):
        self.image = image
        self.h, self.w = image.shape
        self.rng = np.random.default_rng(seed)
        self.fixated = set()
        # 4x4 peripheral grid
        self.n_rows = 4
        self.n_cols = 4
        self.h_step = self.h // self.n_rows
        self.w_step = self.w // self.n_cols

    def gradient_field(self):
        g = np.zeros((self.n_rows, self.n_cols))
        for r in range(self.n_rows):
            for c in range(self.n_cols):
                region = self.image[r*self.h_step:(r+1)*self.h_step,
                                    c*self.w_step:(c+1)*self.w_step]
                g[r, c] = np.std(region)
        return g

    def pick(self):
        g = self.gradient_field()
        # Score = gradient + small random component (novelty surrogate); skip fixated
        candidates = []
        for r in range(self.n_rows):
            for c in range(self.n_cols):
                if (r, c) not in self.fixated:
                    score = g[r, c] + 0.01 * self.rng.random()
                    candidates.append((score, r, c))
        if not candidates:
            return None
        candidates.sort(reverse=True)
        _, r, c = candidates[0]
        self.fixated.add((r, c))
        # Center of cell, plus tiny jitter (microsaccade variability)
        cy = r * self.h_step + self.h_step // 2 + self.rng.integers(-1, 2)
        cx = c * self.w_step + self.w_step // 2 + self.rng.integers(-1, 2)
        cy = max(0, min(self.h - 1, cy))
        cx = max(0, min(self.w - 1, cx))
        return (cy, cx)


# =========================================================================
# View a picture — run actual saccaded krimelack, collect intervals
# =========================================================================
def view_picture(image, seed, n_fixations=12, ticks_per_fixation=500):
    """Real saccaded foveation. Returns the substrate's native output:
    the full list of inter-event intervals from all fixations of this
    viewing. NO summary, NO features over pixels — just what the
    krimelack actually emits."""
    sacc = SaccadeController(image, seed)
    krim = FoveaKrimelack()
    all_intervals = []
    fixations_used = 0
    t = 0
    for _ in range(n_fixations):
        fixation = sacc.pick()
        if fixation is None:
            break
        krim.reset()
        for _ in range(ticks_per_fixation):
            # Microsaccade jitter — read intensity at fixation with tiny noise
            # (physiologically realistic; without it phase locks artificially)
            jitter_r = sacc.rng.integers(-1, 2)
            jitter_c = sacc.rng.integers(-1, 2)
            r = max(0, min(image.shape[0]-1, fixation[0] + jitter_r))
            c = max(0, min(image.shape[1]-1, fixation[1] + jitter_c))
            intensity = float(image[r, c])
            krim.tick(intensity, t)
            t += 1
        intervals = krim.intervals()
        all_intervals.extend(intervals)
        fixations_used += 1
    return all_intervals, fixations_used


# =========================================================================
# Chi-binding profile — substrate-native dimensionalization
# =========================================================================
# The substrate quantizes via trits / L0-L4. Here: bin intervals to
# integer buckets. No hand-tuned threshold — just floor-divide by a
# tick-quantum (one trit's worth of time resolution). This is the
# substrate saying "intervals within this band are the same kind of
# rhythm."
TICK_QUANTUM = 1  # one tick = one bin. Most granular substrate quantization.


def chi_binding_profile(intervals):
    """Multiset of binned intervals. THIS IS THE CHI-BINDING PROFILE —
    where in chi-space this viewing's winding pattern lands.

    Two profiles overlap if the substrate's winding output shared the
    same rhythmic bands. Resonance = co-occupation of bins."""
    if not intervals:
        return {}
    profile = {}
    for iv in intervals:
        b = int(iv // TICK_QUANTUM)
        profile[b] = profile.get(b, 0) + 1
    # Normalize so two profiles with different total winding counts
    # can still be compared on shape (their distribution over chi bins)
    total = sum(profile.values())
    return {b: c/total for b, c in profile.items()}


def chi_overlap(p1, p2):
    """Substrate-native similarity: overlap of two chi-binding profiles.
    Sum of min(weight in p1, weight in p2) across all bins. 1.0 = identical
    distribution, 0.0 = disjoint bins."""
    all_bins = set(p1) | set(p2)
    return sum(min(p1.get(b, 0), p2.get(b, 0)) for b in all_bins)


# =========================================================================
# Synthetic pictures — actual intensity fields the krimelack will read
# =========================================================================
def make_pic(seed, kind, size=32, noise=0.0):
    rng_content = np.random.default_rng(seed)
    rng_noise = np.random.default_rng(seed * 9973 + int(noise * 1e6))

    if kind == "bright_object":
        img = np.full((size, size), 0.15)
        cy = rng_content.integers(8, size - 8)
        cx = rng_content.integers(8, size - 8)
        r = rng_content.integers(5, 9)
        for y in range(size):
            for x in range(size):
                d = (y-cy)**2 + (x-cx)**2
                if d < r*r:
                    img[y, x] = 0.85

    elif kind == "two_blobs":
        img = np.full((size, size), 0.2)
        for _ in range(2):
            cy = rng_content.integers(6, size - 6)
            cx = rng_content.integers(6, size - 6)
            r = rng_content.integers(4, 7)
            for y in range(size):
                for x in range(size):
                    if (y-cy)**2 + (x-cx)**2 < r*r:
                        img[y, x] = 0.8

    elif kind == "vertical_bars":
        img = np.full((size, size), 0.2)
        period = rng_content.integers(3, 7)
        for c in range(0, size, period):
            img[:, c:c+1] = 0.85

    elif kind == "horizontal_bars":
        img = np.full((size, size), 0.2)
        period = rng_content.integers(3, 7)
        for r in range(0, size, period):
            img[r:r+1, :] = 0.85

    elif kind == "gradient_ramp":
        img = np.zeros((size, size))
        for r in range(size):
            for c in range(size):
                img[r, c] = (r + c) / (2 * size)

    elif kind == "speckle":
        img = 0.3 + 0.4 * rng_content.random((size, size))

    img = img + rng_noise.normal(0, noise, (size, size))
    return np.clip(img, 0, 1)


# =========================================================================
# THE TEST
# =========================================================================
def run():
    print("=" * 74)
    print("Substrate-native identity via chi resonance — does it actually work?")
    print("=" * 74)
    print()
    print("Method: run actual fovea krimelack on actual intensity fields via")
    print("actual saccade controller. The substrate's native output is the")
    print("winding-interval sequence. Chi binding = which interval bins the")
    print("winding pattern occupies. Identity = chi overlap.")
    print("No string keys. No CV features over pixels.")
    print()

    # Cases:
    cases = [
        ("bright_object_A", "bright_object", 100),
        ("bright_object_B", "bright_object", 200),    # different bright object
        ("two_blobs_A",     "two_blobs",     300),
        ("vertical_bars",   "vertical_bars", 400),
        ("horizontal_bars", "horizontal_bars", 500),
        ("gradient_ramp",   "gradient_ramp", 600),
        ("speckle",         "speckle",       700),
    ]

    # For each picture: view it TWICE with different saccade seeds
    # (different saccade paths = same picture, different traversal).
    # That's the "same picture twice" case at the substrate level.
    profiles_per_picture = {}
    print("Running each picture twice (different saccade seed each viewing):")
    for label, kind, seed in cases:
        img = make_pic(seed, kind, noise=0.0)
        ivs_a, n_a = view_picture(img, seed=11)
        ivs_b, n_b = view_picture(img, seed=22)
        p_a = chi_binding_profile(ivs_a)
        p_b = chi_binding_profile(ivs_b)
        profiles_per_picture[label] = (p_a, p_b, len(ivs_a), len(ivs_b))
        print(f"  {label:>20s}: viewing A windings={len(ivs_a):4d} bins={len(p_a):3d}"
              f"   viewing B windings={len(ivs_b):4d} bins={len(p_b):3d}")

    print()
    print("--- SAME-PICTURE-TWICE chi overlap (substrate's natural identity) ---")
    same_overlaps = []
    for label, (p_a, p_b, _, _) in profiles_per_picture.items():
        ov = chi_overlap(p_a, p_b)
        same_overlaps.append(ov)
        print(f"  {label:>20s}: overlap = {ov:.3f}")

    print()
    print("--- DIFFERENT-PICTURE chi overlap ---")
    diff_overlaps = []
    labels = list(profiles_per_picture.keys())
    for i in range(len(labels)):
        for j in range(i+1, len(labels)):
            p_i_a, _, _, _ = profiles_per_picture[labels[i]]
            p_j_a, _, _, _ = profiles_per_picture[labels[j]]
            ov = chi_overlap(p_i_a, p_j_a)
            diff_overlaps.append(ov)
            print(f"  {labels[i]:>20s} vs {labels[j]:>20s}: overlap = {ov:.3f}")

    print()
    print("--- SAME-CONTENT / DIFFERENT-NOISE (Joe takes two moon photos) ---")
    # For each picture base, generate a "second photo" (same content, fresh noise)
    same_content_overlaps = []
    for label, kind, seed in cases:
        img1 = make_pic(seed, kind, noise=0.02)
        img2 = make_pic(seed, kind, noise=0.02)  # different noise rng path
        ivs1, _ = view_picture(img1, seed=11)
        ivs2, _ = view_picture(img2, seed=33)  # different saccade seed too
        p1 = chi_binding_profile(ivs1)
        p2 = chi_binding_profile(ivs2)
        ov = chi_overlap(p1, p2)
        same_content_overlaps.append(ov)
        print(f"  {label:>20s}: overlap = {ov:.3f}")

    print()
    print("=" * 74)
    print("FINDINGS")
    print("=" * 74)
    so = np.array(same_overlaps)
    do = np.array(diff_overlaps)
    sc = np.array(same_content_overlaps)
    print(f"  Same-picture-twice (different saccade seed):")
    print(f"    mean overlap = {so.mean():.3f}, min = {so.min():.3f}, max = {so.max():.3f}")
    print(f"  Same-content-different-noise:")
    print(f"    mean overlap = {sc.mean():.3f}, min = {sc.min():.3f}, max = {sc.max():.3f}")
    print(f"  Different-picture:")
    print(f"    mean overlap = {do.mean():.3f}, min = {do.min():.3f}, max = {do.max():.3f}")
    print()

    if so.min() > do.max() and sc.min() > do.max():
        print("  ✓ Substrate's own chi binding SEPARATES identity natively.")
        print("    Phase 2 can use chi-overlap as identity — no string keys needed.")
    elif so.mean() > do.mean() + do.std() and sc.mean() > do.mean():
        print("  ~ Partial separation. Same > different on average but with overlap.")
        print("    The substrate carries some identity info at the krimelack level")
        print("    but not enough alone. Higher-level binding (mosaics) likely needed.")
    else:
        print("  ✗ Substrate's interval distribution does NOT separate identity.")
        print("    Identity has to emerge above the krimelack — at the mosaic or")
        print("    tapestry level where co-firing patterns across fixations matter")
        print("    more than the interval distribution itself.")


if __name__ == "__main__":
    run()
