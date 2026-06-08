"""
GL-MDL-PHYSICS-SENSES-WC-20260608-01

Real-physics sensory generation. No more flat synthetic patterns.

Each sense has a physical essence that produces discriminable signal structure:

VISUAL: 2D fields with proper spatial frequency content. Each percept has a
  characteristic SPATIAL FREQUENCY SPECTRUM that distinguishes it from others
  the way real photographs do.
  - moon: low-frequency luminous disk (single dominant scale)
  - stars: poisson points (broadband high-frequency)
  - cow: piecewise constant patches with sharp edges (mid frequencies, edge content)
  - bears: rough textured curves (broadband with directional bias)
  - kittens: hierarchical fine texture (1/f spectrum, soft edges)
  - room: low-frequency uniformity with sparse edges
  
AUDIO: 1D waveforms with proper harmonic structure.
  - moon: ambient hum 50Hz with very low amplitude
  - cow moo: fundamental 150Hz + 300, 450, 600Hz harmonics
  - bears growl: 80Hz fundamental + broadband noise
  - stars chime: 800Hz + 1600Hz pure tones, decaying
  - kittens purr: 25Hz envelope on 200Hz carrier
  - room ambient: pink noise low amplitude

TOUCH: vibration frequency spectrum representing texture.
  - cow fur: 2-3Hz coarse texture, moderate amplitude
  - bears fur: 4-6Hz rough texture, high amplitude
  - kittens fur: 25-30Hz fine texture, low amplitude
  - room surface: <1Hz smooth, very low amplitude

TASTE: 5-dimensional profile (sweet/sour/salty/bitter/umami) with adaptation.
  - milk: (0.7, 0.0, 0.1, 0.0, 0.3) — sweet dairy
  - mush: (0.2, 0.0, 0.2, 0.0, 0.5) — savory blend

SMELL: breath-locked olfactory binding (oscillating intensity).
  - cow: strong barnyard, intensity 0.8
  - bears: musky strong, 0.9
  - kittens: mild fur, 0.3
  - room: neutral, 0.2
"""

import math
import sys
import numpy as np

sys.path.insert(0, '/home/claude/gualaloom_dna_renamed')
from krimelack import Krimelack


def normalize(v):
    nrm = np.linalg.norm(v)
    return v if nrm < 1e-12 else v / nrm


def transduce_signal(signal_array, omega_0=2.0, kappa=80.0, dt=0.04,
                      threshold=None, adapt_tau=0):
    if threshold is None:
        threshold = math.pi / 3
    k = Krimelack(omega_0=omega_0, kappa=kappa, dt=dt, integration_threshold=threshold)
    if adapt_tau > 0:
        running = 0.0
        for s in signal_array:
            running = 0.95 * running + 0.05 * abs(s)
            adapt_factor = 1.0 / (1.0 + running / 0.5)
            k.kappa = kappa * adapt_factor
            k.step(float(s))
    else:
        k.feed_signal(signal_array)
    return k


def events_to_state(events, dim=16):
    """Build complex state vector from event stream.
    
    Use event TIMING distribution (binned into dim buckets) and event SIGNAL
    VALUES to give a content-dependent vector. Different signal patterns →
    different event distributions → different state vectors.
    """
    v = np.zeros(dim, dtype=complex)
    if not events:
        return v
    t_max = max(e["t"] for e in events) + 1e-9
    for ev in events:
        # Time-bin index
        idx = min(dim - 1, int(ev["t"] / t_max * dim))
        # Use signal value AT the event for amplitude — high-amplitude
        # events contribute more
        amp = 0.5 + 0.5 * abs(ev["s"])
        # Phase encodes WHICH direction the winding went + signal sign
        sign = +1.0 if ev["dw"] > 0 else -1.0
        s_sign = +1.0 if ev["s"] > 0 else -1.0
        phase = math.pi * (sign * 0.3 + s_sign * 0.2 + (ev["t"] / t_max) * 2)
        v[idx] += amp * np.exp(1j * phase)
    return normalize(v) if np.linalg.norm(v) > 1e-12 else v


# =================== VISUAL — fractal/spatial-physics ===================

def _luminous_disk(size=64, radius=None, center=None, intensity=1.0):
    """Bright disk on dark — moon physics."""
    if radius is None:
        radius = size // 4
    if center is None:
        center = (size // 2, size // 2)
    img = np.zeros((size, size))
    y, x = np.ogrid[:size, :size]
    d = np.sqrt((x - center[1])**2 + (y - center[0])**2)
    # Soft falloff with edge — like real lunar limb
    img = intensity * np.exp(-d / (radius * 0.7)) * (d < radius * 1.5)
    return img


def _poisson_stars(size=64, n_stars=15, seed=0):
    """Sparse bright points — stars physics."""
    rng = np.random.default_rng(seed)
    img = np.zeros((size, size))
    for _ in range(n_stars):
        y = rng.integers(0, size)
        x = rng.integers(0, size)
        # Star has small bright core + halo
        img[y, x] = 1.0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if 0 <= y+dy < size and 0 <= x+dx < size:
                    img[y+dy, x+dx] = max(img[y+dy, x+dx], 0.4)
    # Dark sky background with very subtle noise
    img += rng.standard_normal((size, size)) * 0.02
    return np.clip(img, 0, 1)


def _patch_field(size=64, n_patches=8, seed=0, contrast=0.9):
    """Cow physics — piecewise constant patches with sharp edges."""
    rng = np.random.default_rng(seed)
    img = np.zeros((size, size))
    for _ in range(n_patches):
        y0 = rng.integers(0, size - 8)
        x0 = rng.integers(0, size - 8)
        h = rng.integers(4, 12)
        w = rng.integers(4, 12)
        value = contrast if rng.random() < 0.5 else 0.05
        img[y0:y0+h, x0:x0+w] = value
    return img


def _rough_curves(size=64, n_curves=4, seed=0):
    """Bears physics — rough textured curved shapes."""
    rng = np.random.default_rng(seed)
    img = np.ones((size, size)) * 0.4
    for _ in range(n_curves):
        cy = rng.integers(size // 4, 3 * size // 4)
        cx = rng.integers(size // 4, 3 * size // 4)
        r = rng.integers(5, 12)
        # Rough irregular boundary
        for theta_i in range(120):
            theta = 2 * math.pi * theta_i / 120
            r_eff = r + rng.standard_normal() * 1.5
            y = int(cy + r_eff * math.sin(theta))
            x = int(cx + r_eff * math.cos(theta))
            if 0 <= y < size and 0 <= x < size:
                # Dark, textured interior
                img[max(0,y-1):y+2, max(0,x-1):x+2] = 0.15
        # Fill interior with texture
        for ry in range(max(0, cy - r), min(size, cy + r)):
            for rx in range(max(0, cx - r), min(size, cx + r)):
                d = math.sqrt((rx - cx)**2 + (ry - cy)**2)
                if d < r - 1:
                    img[ry, rx] = 0.15 + rng.standard_normal() * 0.08
    return np.clip(img, 0, 1)


def _hierarchical_texture(size=64, seed=0, scales=(1, 4, 16)):
    """Kittens physics — soft fur with multi-scale 1/f spectrum."""
    rng = np.random.default_rng(seed)
    img = np.ones((size, size)) * 0.6
    for scale in scales:
        # Sample fine noise then upsample
        small = rng.standard_normal((size // scale + 1, size // scale + 1))
        # Repeat to upscale
        upscaled = np.kron(small, np.ones((scale, scale)))[:size, :size]
        img += upscaled * (1.0 / scale)
    img = (img - img.min()) / (img.max() - img.min() + 1e-6)
    # Add soft round shapes
    for cx, cy in [(size // 4, size // 2), (3 * size // 4, size // 2)]:
        for y in range(size):
            for x in range(size):
                d = math.sqrt((x - cx)**2 + (y - cy)**2)
                if d < size // 8:
                    img[y, x] = 0.3 * (1 - d / (size // 8)) + 0.7 * img[y, x]
    return img


def _room_field(size=64, seed=0):
    """Room physics — low-frequency uniformity with sparse linear edges."""
    rng = np.random.default_rng(seed)
    img = np.ones((size, size)) * 0.55
    # Add gradients (walls)
    for y in range(size):
        img[y, :] += (y - size/2) / size * 0.15
    # Add a few vertical edges (corners, furniture lines)
    for _ in range(3):
        x = rng.integers(size // 4, 3 * size // 4)
        img[:, x] -= 0.2
        if x > 0:
            img[:, x-1] -= 0.1
    img += rng.standard_normal((size, size)) * 0.03
    return np.clip(img, 0, 1)


# Visual primitive function — same pipeline for all
def visual_percept(pattern_2d):
    """Transduce 2D pattern through krimelack with proper visual physics."""
    sig = np.array(pattern_2d).flatten().astype(float)
    # Keep absolute brightness — don't zero-mean
    sig = sig * 2.0 - 1.0
    n = len(sig)
    # Spatial frequency encoding: position-modulation captures STRUCTURE
    # Real visual systems are sensitive to spatial frequency
    pos_mod = np.sin(2 * math.pi * np.arange(n) / 32) * 0.4
    sig = sig + pos_mod
    k = transduce_signal(sig, kappa=300.0, adapt_tau=0)
    return {"chi": k.winding, "state": events_to_state(k.events), "modality": "visual",
            "n_events": len(k.events)}


# Object → visual percept (programmed mapping)
def visual_for(name):
    """Hierarchical visual percept via V1 → V2 → LOC.
    Uses the cortical pipeline — orientation detectors per receptive field,
    contour pooling, LOC integration."""
    patterns = {
        "moon":    _luminous_disk(size=32, intensity=1.0),
        "stars":   _poisson_stars(size=32, n_stars=10, seed=1),
        "cow":     _patch_field(size=32, n_patches=6, seed=2),
        "bears":   _rough_curves(size=32, n_curves=2, seed=3),
        "kittens": _hierarchical_texture(size=32, seed=4),
        "room":    _room_field(size=32, seed=5),
    }
    if name not in patterns:
        return None
    from GL_MDL_VISUAL_CORTEX_WC_20260608_01 import visual_percept_hierarchical
    return visual_percept_hierarchical(patterns[name])


# =================== AUDIO — proper harmonics ===================

def _harmonic_signal(fundamental_hz, harmonics_amps, duration_s=2.0, sample_rate=200):
    """Synthesize harmonic-rich audio with proper acoustic physics.
    harmonics_amps: list of (harmonic_index, amplitude) pairs."""
    n = int(duration_s * sample_rate)
    t = np.arange(n) / sample_rate
    sig = np.zeros(n)
    for h, a in harmonics_amps:
        sig += a * np.sin(2 * math.pi * fundamental_hz * h * t)
    # Apply envelope
    envelope = np.exp(-t * 0.5) * np.minimum(1, t * 4)
    return sig * envelope


def _noise_band(center_hz, bandwidth_hz, amplitude=1.0, duration_s=2.0, sample_rate=200, seed=0):
    """Band-limited noise — natural sounds (growl, purr texture)."""
    rng = np.random.default_rng(seed)
    n = int(duration_s * sample_rate)
    t = np.arange(n) / sample_rate
    # Filtered noise via random phase modulation
    sig = np.zeros(n)
    for i in range(8):
        f = center_hz + rng.standard_normal() * bandwidth_hz / 4
        phase = rng.uniform(0, 2 * math.pi)
        amp = amplitude * rng.uniform(0.5, 1.5)
        sig += amp * np.sin(2 * math.pi * f * t + phase)
    return sig * np.exp(-t * 0.3)


def audio_percept(signal_1d):
    """Transduce 1D audio waveform via krimelack with audio-tuned params."""
    sig = np.asarray(signal_1d)
    sig = sig / (max(abs(sig).max(), 1e-6))  # normalize amplitude
    k = transduce_signal(sig, kappa=200.0, adapt_tau=0)
    return {"chi": k.winding, "state": events_to_state(k.events), "modality": "audio",
            "n_events": len(k.events)}


def audio_for(name):
    """Hierarchical auditory percept via cochlear → cochlear nucleus → A1.
    Each sound has dominant energy in different cochlear bands (substrate-native
    frequencies, not raw Hz)."""
    from GL_MDL_AUDITORY_CORTEX_WC_20260608_01 import audio_percept_hierarchical
    
    if name == "moon":
        # Quiet hum — energy in very_low band only
        n = 400
        t = np.arange(n) / 200
        sig = 0.1 * np.sin(2 * math.pi * 8 * t) + 0.03 * np.sin(2 * math.pi * 16 * t)
        return audio_percept_hierarchical(sig)
    if name == "cow":
        # Moo: low-mid fundamental + harmonics
        n = 400
        t = np.arange(n) / 200
        sig = (0.8 * np.sin(2 * math.pi * 18 * t) +
               0.4 * np.sin(2 * math.pi * 36 * t) +
               0.2 * np.sin(2 * math.pi * 54 * t))
        sig *= np.exp(-t * 0.5)
        return audio_percept_hierarchical(sig)
    if name == "bears":
        # Growl: low + broadband mid
        n = 400
        t = np.arange(n) / 200
        rng = np.random.default_rng(10)
        sig = 0.6 * np.sin(2 * math.pi * 8 * t) + 0.3 * np.sin(2 * math.pi * 18 * t)
        # Broadband noise centered on mid
        for _ in range(8):
            f = 35 + rng.standard_normal() * 10
            sig += 0.1 * np.sin(2 * math.pi * f * t + rng.uniform(0, 2 * math.pi))
        return audio_percept_hierarchical(sig)
    if name == "stars":
        # Chime: high frequencies
        n = 400
        t = np.arange(n) / 200
        sig = 0.5 * np.sin(2 * math.pi * 75 * t) + 0.4 * np.sin(2 * math.pi * 92 * t)
        sig *= np.exp(-t * 0.4)
        return audio_percept_hierarchical(sig)
    if name == "kittens":
        # Purr: low fundamental modulated at very_low (the 25Hz envelope)
        n = 400
        t = np.arange(n) / 200
        carrier = np.sin(2 * math.pi * 55 * t)  # mid carrier
        env = (1 + np.sin(2 * math.pi * 8 * t)) / 2  # very_low envelope
        sig = carrier * env * 0.5
        return audio_percept_hierarchical(sig)
    if name == "room":
        # Ambient low pink-ish noise — broadband low end
        rng = np.random.default_rng(20)
        n = 400
        t = np.arange(n) / 200
        sig = np.zeros(n)
        for f in [8, 12, 18, 25]:
            sig += 0.1 * np.sin(2 * math.pi * f * t + rng.uniform(0, 2 * math.pi))
        return audio_percept_hierarchical(sig)
    return None


# =================== TOUCH — vibration frequencies ===================

def touch_percept(vibration_hz, amplitude=0.5, duration_n=200, dt=0.04):
    """Touch as texture vibration. Adapting krimelack — receptors adapt to sustained input."""
    t = np.arange(duration_n) * dt
    sig = amplitude * np.sin(2 * math.pi * vibration_hz * t)
    # Add slight texture noise
    sig += np.random.default_rng(int(vibration_hz * 100)).standard_normal(duration_n) * 0.05
    k = transduce_signal(sig, kappa=80.0, adapt_tau=12.0)
    return {"chi": k.winding, "state": events_to_state(k.events), "modality": "touch",
            "n_events": len(k.events)}


def touch_for(name):
    profiles = {
        "cow":     (2.5, 0.5),
        "bears":   (5.0, 0.7),
        "kittens": (28.0, 0.3),
        "room":    (0.3, 0.2),
    }
    if name not in profiles:
        return None
    return touch_percept(*profiles[name])


# =================== TASTE — five basic dimensions ===================

def taste_percept(sweet, sour, salty, bitter, umami):
    """5-dim taste profile → adapting krimelack signal."""
    # Each receptor type → a frequency band
    # Sweet=1Hz, sour=2, salty=3, bitter=4, umami=5
    n = 100
    t = np.arange(n) * 0.04
    sig = (sweet * np.sin(2*math.pi*1*t) +
           sour * np.sin(2*math.pi*2*t) +
           salty * np.sin(2*math.pi*3*t) +
           bitter * np.sin(2*math.pi*4*t) +
           umami * np.sin(2*math.pi*5*t))
    sig = sig / (max(abs(sig).max(), 1e-6))
    k = transduce_signal(sig, kappa=90.0, adapt_tau=8.0)
    return {"chi": k.winding, "state": events_to_state(k.events), "modality": "taste",
            "n_events": len(k.events)}


def taste_for(name):
    profiles = {
        "milk":  (0.7, 0.0, 0.1, 0.0, 0.3),
        "mush":  (0.2, 0.0, 0.2, 0.0, 0.5),
    }
    if name not in profiles:
        return None
    return taste_percept(*profiles[name])


# =================== SMELL — breath-locked ===================

def smell_percept(intensity, breath_period=20, n_breaths=5):
    """Olfaction: intensity modulated by breath cycle. Adapts."""
    n = breath_period * n_breaths
    t = np.arange(n) / breath_period * 2 * math.pi
    breath = (np.sin(t) + 1) / 2
    sig = intensity * breath + 0.1 * intensity * np.sin(3 * t)
    k = transduce_signal(sig, kappa=60.0, adapt_tau=15.0)
    return {"chi": k.winding, "state": events_to_state(k.events), "modality": "smell",
            "n_events": len(k.events)}


def smell_for(name):
    intensities = {
        "cow":     0.8,
        "bears":   0.9,
        "kittens": 0.3,
        "room":    0.2,
        "milk":    0.4,
        "mush":    0.5,
    }
    if name not in intensities:
        return None
    return smell_percept(intensities[name])


# =================== Bundle assembly ===================

def percept_bundle_for(name):
    """Return the multi-modal sensory bundle from physics-based generators."""
    return {
        "visual": visual_for(name),
        "audio":  audio_for(name),
        "touch":  touch_for(name),
        "taste":  taste_for(name),
        "smell":  smell_for(name),
    }


# Sanity self-test
if __name__ == "__main__":
    print("=" * 72)
    print("PHYSICS-BASED SENSORY PRIMITIVES — chi values + state-vector distinctness")
    print("=" * 72)
    
    words = ["moon", "stars", "cow", "bears", "kittens", "room", "milk", "mush"]
    bundles = {w: percept_bundle_for(w) for w in words}
    
    # Show chi values per modality
    print(f"\n{'word':10s} {'visual':>10s} {'audio':>10s} {'touch':>10s} {'taste':>10s} {'smell':>10s}")
    for w in words:
        b = bundles[w]
        cells = []
        for mod in ["visual", "audio", "touch", "taste", "smell"]:
            p = b.get(mod)
            cell = f"{p['chi']:+d}" if p else "  ·"
            cells.append(f"{cell:>10s}")
        print(f"{w:10s} {''.join(cells)}")
    
    # Test STATE VECTOR DISCRIMINATION within each modality
    # — different objects should have low pairwise overlap
    print("\n--- Pairwise state-vector overlap within each modality ---")
    for mod in ["visual", "audio", "touch", "taste", "smell"]:
        # Get all bundles that have this modality
        present = [(w, b[mod]) for w, b in bundles.items() if b.get(mod) is not None]
        if len(present) < 2:
            continue
        overlaps = []
        for i, (w1, p1) in enumerate(present):
            for (w2, p2) in present[i+1:]:
                ov = float(np.abs(np.vdot(p1["state"], p2["state"]))**2)
                overlaps.append((w1, w2, ov))
        overlaps.sort(key=lambda x: -x[2])
        mean = sum(o[2] for o in overlaps) / len(overlaps)
        print(f"\n  [{mod}] mean overlap: {mean:.3f}  (random N=16 baseline ≈ 0.0625)")
        print(f"    most-similar:")
        for (w1, w2, ov) in overlaps[:3]:
            print(f"      {w1:8s}/{w2:8s}: {ov:.3f}")
        print(f"    most-distinct:")
        for (w1, w2, ov) in overlaps[-3:]:
            print(f"      {w1:8s}/{w2:8s}: {ov:.3f}")
