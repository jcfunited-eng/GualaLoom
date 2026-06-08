"""
GL-MDL-FOLDED-CHI-WC-20260608-01

Folded chi: instead of single integer winding, build chi VECTOR from
multiple krimelacks applied to different transformations of the signal.

Self-application principle from substrate: the krimelack mechanism applied
to different views of the same signal yields different windings. The
ensemble of windings is the folded chi.

For TEXT:
  fold_1: krimelack on raw character sequence (original chi)
  fold_2: krimelack on character pair-differences (transitions)
  fold_3: krimelack on character squared (energy)
  fold_4: krimelack on running-mean filtered (smoothed)

For VISUAL:
  fold_1: V1 total winding
  fold_2: V2 total winding
  fold_3: LOC committed-mode count
  fold_4: orientation-balance metric

For AUDIO:
  fold_1: total event count across cochlea
  fold_2: peak-band index (which band dominates)
  fold_3: onset total
  fold_4: sustained total

Atlas indexed by N-D chi vector. Collisions in 4D are rare.
"""

import math
import sys
import numpy as np
sys.path.insert(0, '/home/claude/gualaloom_dna_renamed')
from krimelack import Krimelack, transduce_text


def _krimelack_winding(signal, kappa=80.0, dt=0.04):
    k = Krimelack(omega_0=2.0, kappa=kappa, dt=dt, integration_threshold=math.pi / 3)
    k.feed_signal(signal)
    return k.winding, len(k.events)


def folded_chi_text(text):
    """Build folded chi vector from text.
    Each dimension = krimelack winding on a different transformation of
    the character sequence."""
    chars = [ord(c) % 64 for c in text.lower()]
    if len(chars) < 2:
        chars = chars + [0]
    arr = np.array(chars, dtype=float)
    # Normalize roughly to [-1, 1] range
    sig = (arr - arr.mean()) / (arr.std() + 1e-6)
    
    # Fold 1: raw sequence
    w1, _ = _krimelack_winding(sig, kappa=80)
    # Fold 2: pair-differences (captures transitions)
    diffs = np.diff(sig)
    w2, _ = _krimelack_winding(diffs, kappa=80) if len(diffs) > 0 else (0, 0)
    # Fold 3: squared signal (energy)
    sq = sig ** 2
    sq = sq - sq.mean()
    w3, _ = _krimelack_winding(sq, kappa=80)
    # Fold 4: running mean filtered (smoothed)
    if len(sig) >= 3:
        smoothed = np.convolve(sig, np.ones(3)/3, mode='valid')
        w4, _ = _krimelack_winding(smoothed, kappa=80)
    else:
        w4 = 0
    
    return (w1, w2, w3, w4)


def folded_chi_visual(v1_dict, v2_dict, loc):
    """Build folded chi vector for visual from V1/V2/LOC outputs."""
    # Fold 1: total V1 winding
    w1 = sum(abs(w) for w in v1_dict.values()) // 50  # quantize for binning
    # Fold 2: total V2 winding
    w2 = sum(abs(w) for w in v2_dict.values()) // 50
    # Fold 3: dominant orientation index
    from GL_MDL_VISUAL_CORTEX_WC_20260608_01 import ORIENTATION_FILTERS
    orient_totals = {}
    for orient in ORIENTATION_FILTERS.keys():
        orient_totals[orient] = sum(abs(v1_dict.get((rf, orient), 0)) for rf in range(16))
    dominant = max(orient_totals.items(), key=lambda x: x[1])[0]
    orient_idx = list(ORIENTATION_FILTERS.keys()).index(dominant)
    # Fold 4: LOC chi from the existing computation
    w4 = loc.get("chi", 0)
    return (int(w1), int(w2), int(orient_idx), int(w4))


def folded_chi_audio(cochlear_dict, onsets_dict, sustained_dict, a1):
    """Build folded chi for audio from cochlear/CN/A1 outputs."""
    # Fold 1: total events across cochlea (quantized)
    total_events = sum(c["n_events"] for c in cochlear_dict.values())
    w1 = total_events // 100
    # Fold 2: peak-band index
    band_events = [(name, c["n_events"]) for name, c in cochlear_dict.items()]
    band_events.sort(key=lambda x: -x[1])
    peak_band = band_events[0][0]
    from GL_MDL_AUDITORY_CORTEX_WC_20260608_01 import COCHLEAR_BANDS
    band_idx = next(i for i, b in enumerate(COCHLEAR_BANDS) if b["name"] == peak_band)
    # Fold 3: onset total (quantized)
    w3 = sum(onsets_dict.values()) // 20
    # Fold 4: sustained total (quantized)
    w4 = sum(s["duration_samples"] for s in sustained_dict.values()) // 200
    return (int(w1), int(band_idx), int(w3), int(w4))


def folded_chi_distance(chi_a, chi_b):
    """L1 distance in folded chi space. Used for fuzzy atlas lookup."""
    if len(chi_a) != len(chi_b):
        return float('inf')
    return sum(abs(a - b) for a, b in zip(chi_a, chi_b))


def chi_neighbors(chi, max_distance=2):
    """Generate all chi vectors within L1 distance max_distance.
    Used for atlas band-lookup in folded space."""
    n_dims = len(chi)
    # Generate combinations of (-d, +d) per dimension that sum to <= max_distance
    def gen(remaining_distance, dim_idx, current):
        if dim_idx >= n_dims:
            yield tuple(current)
            return
        for d in range(-remaining_distance, remaining_distance + 1):
            current.append(chi[dim_idx] + d)
            yield from gen(remaining_distance - abs(d), dim_idx + 1, current)
            current.pop()
    yield from gen(max_distance, 0, [])


# Sanity self-test
if __name__ == "__main__":
    print("=" * 72)
    print("FOLDED CHI — text words")
    print("=" * 72)
    
    words = ["moon", "cow", "bears", "stars", "kittens", "room",
             "goodnight", "the", "and", "a", "you", "foot", "moan", "noon"]
    print(f"\n{'word':12s} {'fold_1':>8s} {'fold_2':>8s} {'fold_3':>8s} {'fold_4':>8s}")
    chis = {}
    for w in words:
        chi = folded_chi_text(w)
        chis[w] = chi
        print(f"{w:12s} {chi[0]:>+8d} {chi[1]:>+8d} {chi[2]:>+8d} {chi[3]:>+8d}")
    
    print("\n--- Single-fold collision check (fold_1 only, like old chi) ---")
    fold1_counts = {}
    for w, chi in chis.items():
        fold1_counts.setdefault(chi[0], []).append(w)
    collisions_1d = sum(1 for v in fold1_counts.values() if len(v) > 1)
    print(f"chi values with collisions (1D): {collisions_1d}")
    for chi_val, ws in fold1_counts.items():
        if len(ws) > 1:
            print(f"  chi={chi_val}: {ws}")
    
    print("\n--- Folded 4-D chi collision check ---")
    full_counts = {}
    for w, chi in chis.items():
        full_counts.setdefault(chi, []).append(w)
    collisions_4d = sum(1 for v in full_counts.values() if len(v) > 1)
    print(f"chi positions with collisions (4D): {collisions_4d}")
    for chi_val, ws in full_counts.items():
        if len(ws) > 1:
            print(f"  chi={chi_val}: {ws}")
    
    # Test neighbor lookup
    print("\n--- Neighbors of moon's chi within L1=2 ---")
    n = list(chi_neighbors(chis["moon"], max_distance=2))
    print(f"Neighbors count: {len(n)}")
    # Show how many distinct word-chi are within L1=2 of moon
    nearby = []
    for w, chi in chis.items():
        if w == "moon":
            continue
        d = folded_chi_distance(chis["moon"], chi)
        if d <= 4:  # show within a larger radius for context
            nearby.append((w, chi, d))
    nearby.sort(key=lambda x: x[2])
    print(f"Words within L1=4 of moon:")
    for (w, chi, d) in nearby:
        print(f"  {w:10s} {chi}  L1-dist={d}")
