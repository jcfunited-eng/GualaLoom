"""
GL-MDL-VISUAL-CORTEX-WC-20260608-01

Hierarchical visual transduction matching cortical architecture.

V1: orientation-selective edge detectors across retinotopic receptive fields.
    Each (receptive_field, orientation) pair has its own krimelack.
    Output: winding count per (RF, orientation) — the V1 response map.

V2: pool adjacent RFs, detect contours and corners.
    Run krimelacks on V1 output stream organized by spatial neighborhood.

LOC: integrate V2 outputs into an object-identity signature.
    The substrate's name for what this scene is.

Same krimelack primitive at every level — just different inputs.
"""

import math
import sys
import numpy as np
sys.path.insert(0, '/home/claude/gualaloom_dna_renamed')
from krimelack import Krimelack


def normalize(v):
    nrm = np.linalg.norm(v)
    return v if nrm < 1e-12 else v / nrm


# Orientation filters (Gabor-like edge detectors)
ORIENTATION_FILTERS = {
    "horizontal": np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]], dtype=float),
    "vertical":   np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]], dtype=float),
    "diag_45":    np.array([[0, 1, 1], [-1, 0, 1], [-1, -1, 0]], dtype=float),
    "diag_135":   np.array([[1, 1, 0], [1, 0, -1], [0, -1, -1]], dtype=float),
    # Center-surround (Hubel-Wiesel simple-cell "blob" detector)
    "blob_center": np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]], dtype=float),
}


def convolve2d_simple(img, kernel):
    """Plain 2D convolution. No padding — output is smaller than input."""
    h, w = img.shape
    kh, kw = kernel.shape
    oh = h - kh + 1
    ow = w - kw + 1
    out = np.zeros((oh, ow))
    for y in range(oh):
        for x in range(ow):
            out[y, x] = np.sum(img[y:y+kh, x:x+kw] * kernel)
    return out


def receptive_field_grid(img_h, img_w, n_per_side=4):
    """Divide image into a grid of receptive fields. Return list of (y0, y1, x0, x1)."""
    rfs = []
    rf_h = img_h // n_per_side
    rf_w = img_w // n_per_side
    for ry in range(n_per_side):
        for rx in range(n_per_side):
            y0 = ry * rf_h
            x0 = rx * rf_w
            rfs.append((y0, y0 + rf_h, x0, x0 + rf_w))
    return rfs


def transduce_signal_to_winding(signal_array, kappa=80.0):
    """Run signal through krimelack, return cumulative winding."""
    k = Krimelack(omega_0=2.0, kappa=kappa, dt=0.04, integration_threshold=math.pi / 3)
    k.feed_signal(signal_array)
    return k.winding, len(k.events), k.events


# =================== V1: oriented edge detectors per receptive field ===================

def v1_response(img, n_per_side=4):
    """V1: for each (receptive_field, orientation), compute krimelack winding
    on that subregion of the orientation-filtered image.
    
    Returns: dict mapping (rf_index, orientation_name) -> winding count."""
    img = np.array(img, dtype=float)
    # Apply each orientation filter
    filter_responses = {}
    for name, kernel in ORIENTATION_FILTERS.items():
        filter_responses[name] = convolve2d_simple(img, kernel)
    
    # Get RF grid based on filtered-image dimensions
    sample_resp = next(iter(filter_responses.values()))
    rfs = receptive_field_grid(sample_resp.shape[0], sample_resp.shape[1], n_per_side)
    
    v1 = {}
    for rf_idx, (y0, y1, x0, x1) in enumerate(rfs):
        for orient_name, resp in filter_responses.items():
            patch = resp[y0:y1, x0:x1].flatten()
            # Krimelack on this patch
            winding, n_events, _ = transduce_signal_to_winding(patch, kappa=150.0)
            v1[(rf_idx, orient_name)] = winding
    return v1, rfs


def v1_to_vector(v1_response_dict, n_per_side=4):
    """Flatten V1 dict to a real-valued vector for visualization/comparison."""
    orientations = list(ORIENTATION_FILTERS.keys())
    n_rf = n_per_side * n_per_side
    v = np.zeros(n_rf * len(orientations))
    for rf_idx in range(n_rf):
        for oi, orient in enumerate(orientations):
            v[rf_idx * len(orientations) + oi] = v1_response_dict.get((rf_idx, orient), 0)
    return v


# =================== V2: contour integration across adjacent RFs ===================

def v2_response(v1_dict, n_per_side=4):
    """V2: detect contours by pooling V1 across adjacent RFs.
    
    For each pair of adjacent RFs, integrate their responses.
    Detect:
      - Linear contour: two adjacent RFs with same orientation high
      - Corner: adjacent RFs with different orientations both high
      - Line ending: high orientation in RF with low in neighbor
    
    Returns: dict mapping (rf_pair, pattern_name) -> integrated winding."""
    v2 = {}
    # Adjacency map
    for ry in range(n_per_side):
        for rx in range(n_per_side):
            rf = ry * n_per_side + rx
            # Right neighbor
            if rx + 1 < n_per_side:
                neighbor = ry * n_per_side + (rx + 1)
                pair = (rf, neighbor)
                # Pool oriented responses across both
                for orient in ORIENTATION_FILTERS.keys():
                    a = v1_dict.get((rf, orient), 0)
                    b = v1_dict.get((neighbor, orient), 0)
                    # Linear contour signal
                    signal = np.array([a, b, a + b, abs(a - b), a * b * 0.001])
                    winding, _, _ = transduce_signal_to_winding(signal, kappa=120.0)
                    v2[(pair, f"linear_{orient}")] = winding
            # Down neighbor
            if ry + 1 < n_per_side:
                neighbor = (ry + 1) * n_per_side + rx
                pair = (rf, neighbor)
                for orient in ORIENTATION_FILTERS.keys():
                    a = v1_dict.get((rf, orient), 0)
                    b = v1_dict.get((neighbor, orient), 0)
                    signal = np.array([a, b, a + b, abs(a - b), a * b * 0.001])
                    winding, _, _ = transduce_signal_to_winding(signal, kappa=120.0)
                    v2[(pair, f"linear_{orient}_v")] = winding
    return v2


def v2_to_vector(v2_dict):
    """Flatten V2 dict to a real-valued vector."""
    items = sorted(v2_dict.items(), key=lambda x: str(x[0]))
    return np.array([v for (_, v) in items])


# =================== LOC: object signature ===================

def loc_signature(v1_dict, v2_dict, dim=16):
    """Lateral Occipital Complex: integrate V1+V2 into an object identity vector.
    
    Build a complex N-vector where:
      - Real part: V1 contributions (where edges are, which orientations)
      - Imaginary part: V2 contributions (how edges combine into shapes)
    Bin by chi value of the local V1/V2 response.
    """
    state = np.zeros(dim, dtype=complex)
    
    # V1 contributions: by orientation, into bins
    orientations = list(ORIENTATION_FILTERS.keys())
    for (rf_idx, orient), winding in v1_dict.items():
        if winding == 0:
            continue
        # Bin: orientation × magnitude
        orient_idx = orientations.index(orient)
        bin_idx = (orient_idx * 3 + abs(winding) // 5) % dim
        phase = math.pi * winding / 30.0
        amp = abs(winding) / 100.0
        state[bin_idx] += amp * np.exp(1j * phase)
    
    # V2 contributions: contour patterns
    for (pair_pattern, winding) in v2_dict.items():
        if winding == 0:
            continue
        # Hash the pair_pattern key into a bin
        h = hash(str(pair_pattern)) % dim
        phase = math.pi * winding / 25.0 + math.pi / 7
        amp = abs(winding) / 80.0
        state[h] += amp * np.exp(1j * phase)
    
    # Compute chi (V-E winding from binary committed components)
    amps = np.abs(state)
    if amps.max() < 1e-9:
        return {"chi": 0, "state": state, "v1_total_winding": 0}
    thresh = amps.max() * 0.3
    committed = amps > thresh
    V = int(committed.sum())
    E = 0
    for i in range(len(state) - 1):
        if committed[i] and committed[i + 1]:
            E += 1
    if committed[0] and committed[-1]:
        E += 1
    chi = V - E
    
    return {"chi": chi, "state": normalize(state),
            "v1_total_winding": sum(abs(w) for w in v1_dict.values()),
            "v2_total_winding": sum(abs(w) for w in v2_dict.values())}


def visual_percept_hierarchical(pattern_2d):
    """Full visual pipeline: image → V1 → V2 → LOC signature."""
    v1, rfs = v1_response(pattern_2d, n_per_side=4)
    v2 = v2_response(v1, n_per_side=4)
    loc = loc_signature(v1, v2)
    loc["modality"] = "visual"
    return loc


if __name__ == "__main__":
    # Test with various patterns
    sys.path.insert(0, '/home/claude/gualaloom_dna_renamed/senses')
    from GL_MDL_PHYSICS_SENSES_WC_20260608_01 import (
        _luminous_disk, _poisson_stars, _patch_field,
        _rough_curves, _hierarchical_texture, _room_field
    )
    
    patterns = {
        "moon":    _luminous_disk(size=32, intensity=1.0),
        "stars":   _poisson_stars(size=32, n_stars=10, seed=1),
        "cow":     _patch_field(size=32, n_patches=6, seed=2),
        "bears":   _rough_curves(size=32, n_curves=2, seed=3),
        "kittens": _hierarchical_texture(size=32, seed=4),
        "room":    _room_field(size=32, seed=5),
    }
    
    print("=" * 72)
    print("HIERARCHICAL VISUAL CORTEX — V1 → V2 → LOC")
    print("=" * 72)
    
    perceps = {}
    for name, pat in patterns.items():
        v1, _ = v1_response(pat, n_per_side=4)
        v2 = v2_response(v1, n_per_side=4)
        loc = loc_signature(v1, v2)
        perceps[name] = loc
        # Show V1 orientation totals as a quick fingerprint
        orient_totals = {}
        for orient in ORIENTATION_FILTERS.keys():
            orient_totals[orient] = sum(abs(v1[(rf, orient)]) for rf in range(16))
        print(f"\n  {name}:")
        print(f"    LOC chi: {loc['chi']:+d}  v1_total_winding: {loc['v1_total_winding']}  v2_total: {loc['v2_total_winding']}")
        print(f"    V1 by orientation:")
        for orient, total in sorted(orient_totals.items(), key=lambda x: -x[1]):
            print(f"      {orient:14s}: {total}")
    
    # Pairwise state-vector overlap — does V1→V2→LOC give discriminable signatures?
    print("\n" + "=" * 72)
    print("LOC STATE-VECTOR DISCRIMINATION (lower overlap = better)")
    print("=" * 72)
    names = list(perceps.keys())
    pairs = []
    for i, n1 in enumerate(names):
        for n2 in names[i+1:]:
            ov = float(np.abs(np.vdot(perceps[n1]["state"], perceps[n2]["state"]))**2)
            pairs.append((n1, n2, ov))
    pairs.sort(key=lambda x: -x[2])
    print(f"\nMean overlap: {sum(p[2] for p in pairs)/len(pairs):.3f}  (random baseline ≈ 0.0625)")
    print(f"\nAll pairs:")
    for (n1, n2, ov) in pairs:
        print(f"  {n1:10s} / {n2:10s}: {ov:.3f}")
