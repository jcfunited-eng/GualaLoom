"""
GL-MDL-VISUAL-DEPTH-WC-20260608-01

Visual cortex with full depth:
- COLOR: 3-channel RGB processing, V4 color-opponent detection
- MULTI-SCALE V1: bank of 3 krimelacks per (RF, orientation) at different scales
- V4: color constancy + form integration
- LOC: ventral "what" stream matching against installed prototypes

Each level expands dimensionality and preconditions for next stage.
"""

import math
import sys
import numpy as np
sys.path.insert(0, '/home/claude/gualaloom_dna_renamed')
sys.path.insert(0, '/home/claude/gualaloom_dna_renamed/senses')
from krimelack import Krimelack
from GL_MDL_VISUAL_CORTEX_WC_20260608_01 import (ORIENTATION_FILTERS, convolve2d_simple,
                            receptive_field_grid)


def normalize(v):
    nrm = np.linalg.norm(v)
    return v if nrm < 1e-12 else v / nrm


# Multi-scale parallel krimelack bank for V1
V1_KRIMELACK_BANK = [
    {"kappa": 80,  "threshold": math.pi / 3},   # coarse
    {"kappa": 150, "threshold": math.pi / 4},   # medium
    {"kappa": 250, "threshold": math.pi / 5},   # fine
]


def v1_bank_response(img_channel, n_per_side=4):
    """V1 with parallel krimelack bank per (RF, orientation).
    Returns dict mapping (rf_idx, orientation, scale_idx) -> winding."""
    img = np.array(img_channel, dtype=float)
    filter_responses = {}
    for name, kernel in ORIENTATION_FILTERS.items():
        filter_responses[name] = convolve2d_simple(img, kernel)
    
    sample = next(iter(filter_responses.values()))
    rfs = receptive_field_grid(sample.shape[0], sample.shape[1], n_per_side)
    
    v1 = {}
    for rf_idx, (y0, y1, x0, x1) in enumerate(rfs):
        for orient_name, resp in filter_responses.items():
            patch = resp[y0:y1, x0:x1].flatten()
            # Run all krimelacks in the bank on this patch
            for scale_idx, params in enumerate(V1_KRIMELACK_BANK):
                k = Krimelack(omega_0=2.0, kappa=params["kappa"], dt=0.04,
                              integration_threshold=params["threshold"])
                k.feed_signal(patch)
                v1[(rf_idx, orient_name, scale_idx)] = k.winding
    return v1, rfs


# =================== COLOR — V4 color-opponent ===================

COLOR_OPPONENT_CHANNELS = ["red_green", "blue_yellow", "luminance"]


def to_color_opponent(rgb_img):
    """Convert RGB image to color-opponent representation.
    
    Real V4 uses red-green and blue-yellow opponency from cone responses.
    
    rgb_img: shape (H, W, 3) with R, G, B channels in [0, 1]
    Returns: dict with 'red_green', 'blue_yellow', 'luminance' channels
    """
    r = rgb_img[..., 0]
    g = rgb_img[..., 1]
    b = rgb_img[..., 2]
    return {
        "red_green":   r - g,
        "blue_yellow": b - (r + g) / 2,
        "luminance":   (r + g + b) / 3,
    }


def v4_response(rgb_img, n_per_side=4):
    """V4: color-opponent + form processing.
    Each color-opponent channel gets V1-style processing."""
    channels = to_color_opponent(rgb_img)
    v4 = {}
    for chan_name, chan_data in channels.items():
        # Edge-detect on this color channel
        v1_chan, _ = v1_bank_response(chan_data, n_per_side=n_per_side)
        # Aggregate per orientation across RFs and scales
        for orient in ORIENTATION_FILTERS.keys():
            for scale_idx in range(len(V1_KRIMELACK_BANK)):
                total = sum(abs(v1_chan.get((rf, orient, scale_idx), 0))
                            for rf in range(n_per_side * n_per_side))
                v4[(chan_name, orient, scale_idx)] = total
    return v4


# =================== LOC ventral "what" stream ===================

def loc_signature_color(v1_luminance, v2_dict, v4_dict, dim=16):
    """Lateral Occipital Complex: integrate V1 (multi-scale), V2 (contour), 
    V4 (color) into object signature."""
    state = np.zeros(dim, dtype=complex)
    
    # V1 luminance contributions
    orientations = list(ORIENTATION_FILTERS.keys())
    for (rf_idx, orient, scale_idx), winding in v1_luminance.items():
        if winding == 0:
            continue
        orient_idx = orientations.index(orient)
        bin_idx = (orient_idx * 3 + scale_idx) % dim
        phase = math.pi * winding / 30.0 + scale_idx * math.pi / 4
        amp = abs(winding) / (80.0 * (scale_idx + 1))
        state[bin_idx] += amp * np.exp(1j * phase)
    
    # V2 contour contributions
    for (pair_pattern, winding) in v2_dict.items():
        if winding == 0:
            continue
        h = hash(str(pair_pattern)) % dim
        phase = math.pi * winding / 25.0 + math.pi / 7
        amp = abs(winding) / 80.0
        state[h] += amp * np.exp(1j * phase)
    
    # V4 color contributions  
    chan_to_phase_offset = {"red_green": 0, "blue_yellow": math.pi / 2, "luminance": math.pi}
    for (chan, orient, scale_idx), total in v4_dict.items():
        if total == 0:
            continue
        orient_idx = orientations.index(orient)
        bin_idx = (orient_idx * 2 + scale_idx + 5) % dim
        phase = chan_to_phase_offset[chan] + scale_idx * math.pi / 6
        amp = total / 1000.0
        state[bin_idx] += amp * np.exp(1j * phase)
    
    amps = np.abs(state)
    if amps.max() < 1e-9:
        return {"chi": 0, "state": state}
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
            "v1_total": sum(abs(w) for w in v1_luminance.values()),
            "v2_total": sum(abs(w) for w in v2_dict.values()),
            "v4_total": sum(abs(w) for w in v4_dict.values())}


def v2_response_bank(v1_dict, n_per_side=4):
    """V2 contour pooling — works on V1 bank output.
    Sums across scales for each (RF, orientation) and then does pair-wise integration."""
    # Collapse scales into single per-RF-per-orientation winding
    v1_collapsed = {}
    for (rf, orient, scale_idx), w in v1_dict.items():
        key = (rf, orient)
        v1_collapsed[key] = v1_collapsed.get(key, 0) + w
    
    v2 = {}
    for ry in range(n_per_side):
        for rx in range(n_per_side):
            rf = ry * n_per_side + rx
            if rx + 1 < n_per_side:
                neighbor = ry * n_per_side + (rx + 1)
                pair = (rf, neighbor)
                for orient in ORIENTATION_FILTERS.keys():
                    a = v1_collapsed.get((rf, orient), 0)
                    b = v1_collapsed.get((neighbor, orient), 0)
                    signal = np.array([a, b, a + b, abs(a - b), a * b * 0.001])
                    k = Krimelack(omega_0=2.0, kappa=120, dt=0.04,
                                  integration_threshold=math.pi / 3)
                    k.feed_signal(signal)
                    v2[(pair, f"linear_{orient}")] = k.winding
            if ry + 1 < n_per_side:
                neighbor = (ry + 1) * n_per_side + rx
                pair = (rf, neighbor)
                for orient in ORIENTATION_FILTERS.keys():
                    a = v1_collapsed.get((rf, orient), 0)
                    b = v1_collapsed.get((neighbor, orient), 0)
                    signal = np.array([a, b, a + b, abs(a - b), a * b * 0.001])
                    k = Krimelack(omega_0=2.0, kappa=120, dt=0.04,
                                  integration_threshold=math.pi / 3)
                    k.feed_signal(signal)
                    v2[(pair, f"linear_{orient}_v")] = k.winding
    return v2


def visual_percept_deep(rgb_img):
    """Full deep visual pipeline: RGB → V1 bank (lum) → V2 → V4 (color) → LOC."""
    luminance = (rgb_img[..., 0] + rgb_img[..., 1] + rgb_img[..., 2]) / 3
    v1_lum, _ = v1_bank_response(luminance, n_per_side=4)
    v2 = v2_response_bank(v1_lum, n_per_side=4)
    v4 = v4_response(rgb_img, n_per_side=4)
    loc = loc_signature_color(v1_lum, v2, v4)
    loc["modality"] = "visual"
    return loc, v1_lum, v2, v4


# =================== Colored patterns ===================

def make_moon_rgb(size=32):
    """Moon: bright cream-colored disk on dark blue sky."""
    img = np.zeros((size, size, 3))
    img[..., 2] = 0.05  # very dark blue background
    cx = cy = size // 2
    r = size // 4
    for y in range(size):
        for x in range(size):
            d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            if d < r * 1.5:
                fall = max(0, 1 - d / (r * 1.5))
                img[y, x, 0] = fall * 0.95   # cream
                img[y, x, 1] = fall * 0.90
                img[y, x, 2] = fall * 0.70
    return img


def make_stars_rgb(size=32):
    """Stars: blue-white points on dark sky."""
    rng = np.random.default_rng(123)
    img = np.zeros((size, size, 3))
    img[..., 2] = 0.05  # dark blue
    for _ in range(10):
        y = rng.integers(0, size)
        x = rng.integers(0, size)
        img[y, x] = [0.95, 0.95, 1.0]  # blue-white
        # Halo
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if 0 <= y+dy < size and 0 <= x+dx < size:
                    img[y+dy, x+dx] = np.maximum(img[y+dy, x+dx], [0.3, 0.3, 0.4])
    return img


def make_cow_rgb(size=32):
    """Cow: black-and-white patches on green grass."""
    rng = np.random.default_rng(42)
    img = np.zeros((size, size, 3))
    img[..., 1] = 0.4   # green grass background
    img[..., 0] = 0.15
    # Patches of cow
    for _ in range(8):
        y0 = rng.integers(0, size - 4)
        x0 = rng.integers(0, size - 4)
        h = rng.integers(2, 5)
        w = rng.integers(2, 5)
        if rng.random() < 0.5:
            img[y0:y0+h, x0:x0+w] = [0.95, 0.95, 0.95]  # white patch
        else:
            img[y0:y0+h, x0:x0+w] = [0.05, 0.05, 0.05]  # black patch
    return img


def make_bears_rgb(size=32):
    """Bears: brown rough curves on lighter brown background."""
    rng = np.random.default_rng(3)
    img = np.ones((size, size, 3)) * 0.55
    img[..., 0] = 0.65   # tan
    img[..., 1] = 0.5
    img[..., 2] = 0.35
    for cx, cy in [(8, 10), (16, 18), (24, 10)]:
        r = 4
        for y in range(size):
            for x in range(size):
                d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
                if d < r:
                    img[y, x] = [0.3, 0.2, 0.1]  # brown bear
    return img


def make_kittens_rgb(size=32):
    """Kittens: gray-white furry texture."""
    rng = np.random.default_rng(99)
    img = np.ones((size, size, 3)) * 0.8
    # Soft round kitten shapes
    for cx, cy in [(8, 16), (20, 18)]:
        r = 4
        for y in range(size):
            for x in range(size):
                d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
                if d < r:
                    fall = 1 - d / r
                    img[y, x] = [0.4 + rng.standard_normal()*0.1,
                                 0.4 + rng.standard_normal()*0.1,
                                 0.45 + rng.standard_normal()*0.1]
    # Soft texture noise
    img += rng.standard_normal((size, size, 3)) * 0.03
    return np.clip(img, 0, 1)


def make_room_rgb(size=32):
    """Room: warm cream walls with edges."""
    rng = np.random.default_rng(7)
    img = np.ones((size, size, 3)) * 0.75
    img[..., 0] = 0.85   # cream/warm
    img[..., 1] = 0.78
    img[..., 2] = 0.65
    # Wall edges
    for _ in range(3):
        x = rng.integers(size // 4, 3 * size // 4)
        img[:, x] *= 0.7
        if x > 0:
            img[:, x-1] *= 0.85
    img += rng.standard_normal((size, size, 3)) * 0.02
    return np.clip(img, 0, 1)


def colored_pattern_for(name):
    patterns = {
        "moon":    make_moon_rgb,
        "stars":   make_stars_rgb,
        "cow":     make_cow_rgb,
        "bears":   make_bears_rgb,
        "kittens": make_kittens_rgb,
        "room":    make_room_rgb,
    }
    if name in patterns:
        return patterns[name]()
    return None


def visual_deep_for(name):
    pat = colored_pattern_for(name)
    if pat is None:
        return None
    loc, v1, v2, v4 = visual_percept_deep(pat)
    loc["v1"] = v1
    loc["v2"] = v2
    loc["v4"] = v4
    return loc


if __name__ == "__main__":
    print("=" * 72)
    print("VISUAL DEPTH — color V4 + multi-scale V1 bank + LOC")
    print("=" * 72)
    
    names = ["moon", "stars", "cow", "bears", "kittens", "room"]
    perceps = {n: visual_deep_for(n) for n in names}
    
    print(f"\n{'name':10s} {'LOC chi':>8s} {'V1 total':>10s} {'V2 total':>10s} {'V4 total':>10s}")
    for n, p in perceps.items():
        print(f"  {n:10s} {p['chi']:>+8d} {p['v1_total']:>10d} {p['v2_total']:>10d} {p['v4_total']:>10d}")
    
    print("\nPairwise LOC state-vector overlap:")
    pairs = []
    for i, n1 in enumerate(names):
        for n2 in names[i+1:]:
            ov = float(np.abs(np.vdot(perceps[n1]["state"], perceps[n2]["state"]))**2)
            pairs.append((n1, n2, ov))
    pairs.sort(key=lambda x: -x[2])
    print(f"Mean overlap: {sum(p[2] for p in pairs)/len(pairs):.3f}")
    for (n1, n2, ov) in pairs:
        print(f"  {n1:10s} / {n2:10s}: {ov:.3f}")
