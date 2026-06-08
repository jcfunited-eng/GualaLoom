"""
GL-MDL-AUDITORY-CORTEX-WC-20260608-01

Hierarchical auditory transduction matching cortical architecture.

COCHLEA: tonotopic bandpass filter bank, each band followed by a
  krimelack tuned to that frequency. Equivalent to V1's orientation bank
  but in frequency space instead of orientation space.

COCHLEAR NUCLEUS: two parallel streams from cochlear output:
  - ONSET stream: fires at energy onset (transient detection)
  - SUSTAINED stream: tracks sustained activity per band

A1: tonotopic preservation + pitch/loudness/timbre/duration integration.
  Each band's onset + sustained pattern contributes to the A1 state vector.

The "what" stream then matches A1 against installed sound primitives.

Same krimelack primitive at every level. Tonotopic structure replaces
retinotopic for vision.
"""

import math
import sys
import numpy as np

sys.path.insert(0, '/home/claude/gualaloom_dna_renamed')
from krimelack import Krimelack


def normalize(v):
    nrm = np.linalg.norm(v)
    return v if nrm < 1e-12 else v / nrm


# Cochlear tonotopic frequency bands — within substrate Nyquist (signal sample_rate=200)
# Different sounds will activate different bands based on their dominant frequencies
COCHLEAR_BANDS = [
    {"name": "very_low",  "freq": 8,   "bandwidth": 4},
    {"name": "low",       "freq": 18,  "bandwidth": 8},
    {"name": "low_mid",   "freq": 35,  "bandwidth": 15},
    {"name": "mid",       "freq": 55,  "bandwidth": 20},
    {"name": "mid_high",  "freq": 75,  "bandwidth": 20},
    {"name": "high",      "freq": 92,  "bandwidth": 15},
]


def bandpass_filter(signal, center_hz, bandwidth_hz, sample_rate=200):
    """Simple resonant bandpass via biquad-like filtering. Implements
    cochlear band selectivity — only frequencies near center pass through."""
    n = len(signal)
    dt = 1.0 / sample_rate
    # Resonant filter: y[k] = a*x[k] + b*y[k-1] + c*y[k-2]
    omega = 2 * math.pi * center_hz / sample_rate
    Q = center_hz / max(bandwidth_hz, 1)
    # Biquad coefficients (resonance bandpass)
    alpha = math.sin(omega) / (2 * Q)
    b0 = alpha
    b1 = 0
    b2 = -alpha
    a0 = 1 + alpha
    a1 = -2 * math.cos(omega)
    a2 = 1 - alpha
    # Normalize
    b0, b1, b2 = b0 / a0, b1 / a0, b2 / a0
    a1, a2 = a1 / a0, a2 / a0
    
    y = np.zeros(n)
    x1 = x2 = y1 = y2 = 0.0
    for i in range(n):
        x = signal[i]
        y[i] = b0 * x + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
        x2 = x1
        x1 = x
        y2 = y1
        y1 = y[i]
    return y


def cochlear_transduce(signal_1d, sample_rate=200):
    """Cochlea: split signal into tonotopic bands.
    Each band: bandpass filter, then krimelack to count events.
    Returns: dict mapping band_name -> (winding, n_events, filtered_signal)
    """
    cochlear = {}
    for band in COCHLEAR_BANDS:
        filtered = bandpass_filter(signal_1d, band["freq"], band["bandwidth"], sample_rate)
        # Normalize filtered signal
        norm = abs(filtered).max()
        if norm > 1e-9:
            filtered = filtered / norm
        # Krimelack on this band — frequency-tuned via kappa
        # Higher freq bands get more kappa to be sensitive to their range
        kappa = 100.0 + (math.log10(band["freq"] / 50) * 80)
        k = Krimelack(omega_0=2.0, kappa=kappa, dt=0.04,
                      integration_threshold=math.pi / 3)
        k.feed_signal(filtered)
        cochlear[band["name"]] = {
            "winding": k.winding,
            "n_events": len(k.events),
            "filtered": filtered,
            "events": k.events,
        }
    return cochlear


# =================== COCHLEAR NUCLEUS: two streams ===================

def onset_stream(cochlear_output):
    """Onset choppers — fire at transients (sound onset).
    For each band, look at the derivative of filtered signal and detect rises."""
    onsets = {}
    for band_name, c in cochlear_output.items():
        filtered = c["filtered"]
        # Detect onset: first derivative > threshold
        if len(filtered) < 2:
            onsets[band_name] = 0
            continue
        deriv = np.diff(np.abs(filtered))
        # Count onset events (large positive derivatives)
        threshold = np.std(deriv) * 1.5
        n_onsets = int(np.sum(deriv > threshold))
        onsets[band_name] = n_onsets
    return onsets


def sustained_stream(cochlear_output):
    """Sustained responders — track energy duration per band."""
    sustained = {}
    for band_name, c in cochlear_output.items():
        filtered = c["filtered"]
        # Energy in this band
        energy = float(np.mean(filtered ** 2))
        # Duration above threshold (how long was band active)
        threshold = abs(filtered).max() * 0.3
        active_samples = int(np.sum(np.abs(filtered) > threshold))
        sustained[band_name] = {
            "energy": energy,
            "duration_samples": active_samples,
            "winding": c["winding"],
        }
    return sustained


# =================== A1: integrate cochlear + onset + sustained ===================

def a1_signature(cochlear, onsets, sustained, dim=16):
    """A1: build complex state vector preserving tonotopic organization.
    Uses RELATIVE band activation (each sound's signature is its profile)."""
    state = np.zeros(dim, dtype=complex)
    
    n_bands = len(COCHLEAR_BANDS)
    dims_per_band = max(1, dim // n_bands)
    
    # Compute total events for normalization
    total_events = sum(c["n_events"] for c in cochlear.values()) + 1
    total_onsets = sum(onsets.values()) + 1
    
    for bi, band in enumerate(COCHLEAR_BANDS):
        name = band["name"]
        c = cochlear[name]
        sus = sustained[name]
        onset_count = onsets.get(name, 0)
        
        # RELATIVE share of this band — what fraction of activity is here
        events_share = c["n_events"] / total_events
        onset_share = onset_count / total_onsets
        sustained_norm = sus["energy"] * 50.0
        
        # Amplitude proportional to relative share
        amp = events_share * 10.0 + sustained_norm + onset_share * 5.0
        
        # Phase encodes onset vs sustained ratio
        if events_share > 0:
            onset_to_event_ratio = onset_share / max(events_share, 1e-6)
            phase = math.pi * (bi / n_bands) * 2 + math.pi * onset_to_event_ratio * 0.5
        else:
            phase = math.pi * (bi / n_bands) * 2
        
        for d in range(dims_per_band):
            target = (bi * dims_per_band + d) % dim
            state[target] += amp * np.exp(1j * (phase + d * math.pi / 5))
    
    # Compute chi from V-E winding
    amps = np.abs(state)
    if amps.max() < 1e-9:
        return {"chi": 0, "state": state, "band_pattern": {}}
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
    
    band_pattern = {name: cochlear[name]["n_events"] for name in cochlear}
    return {"chi": chi, "state": normalize(state), "band_pattern": band_pattern,
            "onset_total": sum(onsets.values()),
            "sustained_total": sum(s["duration_samples"] for s in sustained.values())}


def audio_percept_hierarchical(signal_1d, sample_rate=200):
    """Full auditory pipeline: signal → cochlear bands → CN streams → A1 signature."""
    cochlear = cochlear_transduce(signal_1d, sample_rate)
    onsets = onset_stream(cochlear)
    sustained = sustained_stream(cochlear)
    a1 = a1_signature(cochlear, onsets, sustained)
    a1["modality"] = "audio"
    return a1


# =================== Self-test ===================

if __name__ == "__main__":
    sample_rate = 200
    
    def harmonic_sig(f0, harmonics, duration_s=2.0):
        n = int(duration_s * sample_rate)
        t = np.arange(n) / sample_rate
        sig = np.zeros(n)
        for h, a in harmonics:
            sig += a * np.sin(2 * math.pi * f0 * h * t)
        env = np.exp(-t * 0.5) * np.minimum(1, t * 4)
        return sig * env
    
    def noise_band(center, bw, amp=1.0, duration_s=2.0, seed=0):
        rng = np.random.default_rng(seed)
        n = int(duration_s * sample_rate)
        t = np.arange(n) / sample_rate
        sig = np.zeros(n)
        for _ in range(8):
            f = center + rng.standard_normal() * bw / 4
            phase = rng.uniform(0, 2 * math.pi)
            sig += amp * np.sin(2 * math.pi * f * t + phase)
        return sig * np.exp(-t * 0.3)
    
    # The sound primitives from GL_MDL_PHYSICS_SENSES_WC_20260608_01
    sounds = {
        "moon (hum)":     harmonic_sig(50, [(1, 0.1), (2, 0.03)]),
        "cow (moo)":      harmonic_sig(150, [(1, 0.8), (2, 0.4), (3, 0.2), (4, 0.1)]),
        "bears (growl)":  harmonic_sig(80, [(1, 0.6), (2, 0.3), (3, 0.15)]) + noise_band(200, 100, 0.4, seed=10),
        "stars (chime)":  harmonic_sig(800, [(1, 0.5)]) + harmonic_sig(1200, [(1, 0.4)]),
        "kittens (purr)": (lambda: (lambda t: 0.5 * np.sin(2*math.pi*200*t) * (1 + np.sin(2*math.pi*25*t))/2)(np.arange(400)/sample_rate))(),
        "room (ambient)": noise_band(60, 40, 0.1, seed=20),
    }
    
    print("=" * 72)
    print("HIERARCHICAL AUDITORY CORTEX — COCHLEA → CN → A1")
    print("=" * 72)
    
    sigs = {}
    for name, signal in sounds.items():
        a1 = audio_percept_hierarchical(signal)
        sigs[name] = a1
        print(f"\n  {name}:")
        print(f"    A1 chi: {a1['chi']:+d}  onsets: {a1['onset_total']}  sustained: {a1['sustained_total']}")
        print(f"    Band activations (tonotopic pattern):")
        for band in COCHLEAR_BANDS:
            w = a1['band_pattern'][band['name']]
            bar = "█" * min(40, int(abs(w) / 5))
            print(f"      {band['name']:10s} ({band['freq']:>4}Hz): {w:>4d}  {bar}")
    
    # Pairwise state-vector overlap — A1 signature discrimination
    print("\n" + "=" * 72)
    print("A1 STATE-VECTOR DISCRIMINATION (lower = better)")
    print("=" * 72)
    names = list(sigs.keys())
    pairs = []
    for i, n1 in enumerate(names):
        for n2 in names[i+1:]:
            ov = float(np.abs(np.vdot(sigs[n1]["state"], sigs[n2]["state"]))**2)
            pairs.append((n1, n2, ov))
    pairs.sort(key=lambda x: -x[2])
    print(f"\nMean overlap: {sum(p[2] for p in pairs)/len(pairs):.3f}  (random N=16 baseline ≈ 0.0625)")
    print("\nAll pairs:")
    for (n1, n2, ov) in pairs:
        print(f"  {n1:18s} / {n2:18s}: {ov:.3f}")
