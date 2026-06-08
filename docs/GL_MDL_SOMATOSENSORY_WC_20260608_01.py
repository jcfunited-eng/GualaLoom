"""
GL-MDL-SOMATOSENSORY-WC-20260608-01

Hierarchical touch, taste, smell — matching real cortical organization.

TOUCH (somatosensory):
  Four mechanoreceptor types — Merkel (slow-adapting, pressure/edges),
  Meissner (fast-adapting, low-freq vibration), Pacinian (high-freq vibration),
  Ruffini (sustained skin stretch). Each is a krimelack with distinct kappa/adaptation.
  
  S1: somatotopic integration (like A1's tonotopic).

TASTE (gustatory):
  Five basic taste receptors — sweet (T1R2/T1R3), salty (ENaC), sour (PKD2L1),
  bitter (T2R), umami (T1R1/T1R3). Each receptor is its own krimelack.
  
  Insular cortex: integrate 5-channel response into taste signature.

SMELL (olfactory):
  Many olfactory receptors → 8-channel simplified glomerulus model.
  Each channel responds to different molecular feature.
  
  Piriform cortex: integrate channel pattern into odor identity.
"""

import math
import sys
import numpy as np
sys.path.insert(0, '/home/claude/gualaloom_dna_renamed')
from krimelack import Krimelack


def normalize(v):
    nrm = np.linalg.norm(v)
    return v if nrm < 1e-12 else v / nrm


def _krimelack_run(signal, kappa, adapt_tau=0, threshold=None):
    if threshold is None:
        threshold = math.pi / 3
    k = Krimelack(omega_0=2.0, kappa=kappa, dt=0.04, integration_threshold=threshold)
    if adapt_tau > 0:
        running = 0.0
        for s in signal:
            running = 0.95 * running + 0.05 * abs(s)
            k.kappa = kappa / (1.0 + running / 0.5)
            k.step(float(s))
    else:
        k.feed_signal(signal)
    return k.winding, len(k.events), k.events


def _events_to_state(events, dim=16, offset_phase=0):
    v = np.zeros(dim, dtype=complex)
    if not events:
        return v
    t_max = max(e["t"] for e in events) + 1e-9
    for ev in events:
        idx = min(dim - 1, int(ev["t"] / t_max * dim))
        amp = 0.5 + 0.5 * abs(ev["s"])
        sign = +1.0 if ev["dw"] > 0 else -1.0
        s_sign = +1.0 if ev["s"] > 0 else -1.0
        phase = offset_phase + math.pi * (sign * 0.3 + s_sign * 0.2 + (ev["t"] / t_max) * 2)
        v[idx] += amp * np.exp(1j * phase)
    return normalize(v) if np.linalg.norm(v) > 1e-12 else v


# =================== TOUCH: 4 mechanoreceptor types ===================

MECHANORECEPTORS = [
    {"name": "merkel",   "kappa": 40,  "adapt_tau": 0,    "freq_pref": 1.0,  "phase": 0},
    {"name": "meissner", "kappa": 80,  "adapt_tau": 15,   "freq_pref": 5.0,  "phase": math.pi/4},
    {"name": "pacinian", "kappa": 150, "adapt_tau": 5,    "freq_pref": 30.0, "phase": math.pi/2},
    {"name": "ruffini",  "kappa": 35,  "adapt_tau": 0,    "freq_pref": 0.5,  "phase": 3*math.pi/4},
]


def touch_hierarchical(vibration_hz, amplitude=0.5, duration_n=200, dt=0.04):
    """Touch via 4 mechanoreceptor types in parallel.
    Each receptor responds best to its preferred frequency."""
    t = np.arange(duration_n) * dt
    base_sig = amplitude * np.sin(2 * math.pi * vibration_hz * t)
    base_sig += np.random.default_rng(int(vibration_hz * 100)).standard_normal(duration_n) * 0.05
    
    receptor_outputs = {}
    for receptor in MECHANORECEPTORS:
        # Receptor sensitivity: higher response when vibration matches preferred freq
        freq_match = math.exp(-((math.log(vibration_hz + 0.1) - math.log(receptor["freq_pref"]))**2) / 2)
        weighted_sig = base_sig * (0.3 + 0.7 * freq_match)
        winding, n_events, events = _krimelack_run(
            weighted_sig, receptor["kappa"], adapt_tau=receptor["adapt_tau"])
        receptor_outputs[receptor["name"]] = {
            "winding": winding, "n_events": n_events,
            "freq_match": freq_match, "events": events,
        }
    
    # S1: integrate receptor responses
    state = np.zeros(16, dtype=complex)
    for receptor in MECHANORECEPTORS:
        r = receptor_outputs[receptor["name"]]
        partial = _events_to_state(r["events"], dim=16, offset_phase=receptor["phase"])
        state += partial * (r["n_events"] / 100.0)
    state = normalize(state) if np.linalg.norm(state) > 1e-9 else state
    
    # Chi vector for folded chi
    chi_folded = (
        int(receptor_outputs["merkel"]["n_events"] // 10),
        int(receptor_outputs["meissner"]["n_events"] // 10),
        int(receptor_outputs["pacinian"]["n_events"] // 10),
        int(receptor_outputs["ruffini"]["n_events"] // 10),
    )
    
    return {
        "chi": chi_folded[0] - chi_folded[2],  # single chi for legacy
        "chi_folded": chi_folded,
        "state": state,
        "modality": "touch",
        "receptor_pattern": {r["name"]: receptor_outputs[r["name"]]["n_events"]
                             for r in MECHANORECEPTORS},
    }


def touch_deep_for(name):
    profiles = {
        "cow":     (2.5, 0.5),
        "bears":   (5.0, 0.7),
        "kittens": (28.0, 0.3),
        "room":    (0.3, 0.2),
        "milk":    (0.5, 0.3),
    }
    if name not in profiles:
        return None
    return touch_hierarchical(*profiles[name])


# =================== TASTE: 5 receptor channels ===================

TASTE_RECEPTORS = [
    {"name": "sweet",  "kappa": 70,  "freq": 1.0, "phase": 0},
    {"name": "salty",  "kappa": 85,  "freq": 2.0, "phase": math.pi/3},
    {"name": "sour",   "kappa": 100, "freq": 3.0, "phase": 2*math.pi/3},
    {"name": "bitter", "kappa": 120, "freq": 4.0, "phase": math.pi},
    {"name": "umami",  "kappa": 60,  "freq": 5.0, "phase": 4*math.pi/3},
]


def taste_hierarchical(sweet, salty, sour, bitter, umami):
    """Five receptor types, each with own krimelack.
    Insular cortex integrates."""
    levels = [sweet, salty, sour, bitter, umami]
    n = 100
    t = np.arange(n) * 0.04
    
    receptor_outputs = {}
    for receptor, level in zip(TASTE_RECEPTORS, levels):
        if level < 0.01:
            receptor_outputs[receptor["name"]] = {"winding": 0, "n_events": 0, "events": []}
            continue
        # Each receptor sees its own signal modulated by its level
        sig = level * np.sin(2 * math.pi * receptor["freq"] * t)
        # Add adaptation
        winding, n_events, events = _krimelack_run(
            sig, receptor["kappa"], adapt_tau=8.0)
        receptor_outputs[receptor["name"]] = {
            "winding": winding, "n_events": n_events, "events": events, "level": level,
        }
    
    # Insular cortex: integrate
    state = np.zeros(16, dtype=complex)
    for receptor in TASTE_RECEPTORS:
        r = receptor_outputs[receptor["name"]]
        partial = _events_to_state(r["events"], dim=16, offset_phase=receptor["phase"])
        state += partial * (r["n_events"] / 50.0)
    state = normalize(state) if np.linalg.norm(state) > 1e-9 else state
    
    chi_folded = (
        int(receptor_outputs["sweet"]["n_events"] // 5),
        int(receptor_outputs["salty"]["n_events"] // 5),
        int(receptor_outputs["sour"]["n_events"] // 5),
        int(receptor_outputs["umami"]["n_events"] // 5),
    )
    
    return {
        "chi": sum(chi_folded) // 4,
        "chi_folded": chi_folded,
        "state": state,
        "modality": "taste",
        "receptor_pattern": {r["name"]: receptor_outputs[r["name"]]["n_events"]
                             for r in TASTE_RECEPTORS},
    }


def taste_deep_for(name):
    profiles = {
        "milk":  (0.7, 0.1, 0.0, 0.0, 0.3),
        "mush":  (0.2, 0.2, 0.0, 0.0, 0.5),
    }
    if name not in profiles:
        return None
    return taste_hierarchical(*profiles[name])


# =================== SMELL: 8 olfactory channels ===================

OLFACTORY_CHANNELS = [
    {"name": "musky",     "kappa": 50,  "feature_freq": 1.5, "phase": 0},
    {"name": "floral",    "kappa": 60,  "feature_freq": 2.5, "phase": math.pi/4},
    {"name": "minty",     "kappa": 70,  "feature_freq": 3.5, "phase": math.pi/2},
    {"name": "pungent",   "kappa": 80,  "feature_freq": 4.5, "phase": 3*math.pi/4},
    {"name": "ethereal",  "kappa": 55,  "feature_freq": 1.0, "phase": math.pi},
    {"name": "camphor",   "kappa": 65,  "feature_freq": 2.0, "phase": 5*math.pi/4},
    {"name": "putrid",    "kappa": 90,  "feature_freq": 5.5, "phase": 3*math.pi/2},
    {"name": "barnyard",  "kappa": 75,  "feature_freq": 4.0, "phase": 7*math.pi/4},
]


def smell_hierarchical(molecule_profile, breath_period=20, n_breaths=5):
    """Olfaction: 8 receptor types, each sees the molecule profile
    weighted by its receptor preference. Breath-locked modulation."""
    # molecule_profile: dict mapping channel_name -> intensity
    n = breath_period * n_breaths
    t = np.arange(n) / breath_period * 2 * math.pi
    breath = (np.sin(t) + 1) / 2
    
    receptor_outputs = {}
    for channel in OLFACTORY_CHANNELS:
        intensity = molecule_profile.get(channel["name"], 0)
        if intensity < 0.01:
            receptor_outputs[channel["name"]] = {"winding": 0, "n_events": 0, "events": []}
            continue
        sig = intensity * breath + 0.1 * intensity * np.sin(channel["feature_freq"] * t)
        winding, n_events, events = _krimelack_run(
            sig, channel["kappa"], adapt_tau=15.0)
        receptor_outputs[channel["name"]] = {
            "winding": winding, "n_events": n_events, "events": events,
        }
    
    # Piriform cortex: integrate
    state = np.zeros(16, dtype=complex)
    for channel in OLFACTORY_CHANNELS:
        r = receptor_outputs[channel["name"]]
        partial = _events_to_state(r["events"], dim=16, offset_phase=channel["phase"])
        state += partial * (r["n_events"] / 30.0)
    state = normalize(state) if np.linalg.norm(state) > 1e-9 else state
    
    chi_folded = tuple(int(receptor_outputs[c["name"]]["n_events"] // 5) 
                       for c in OLFACTORY_CHANNELS[:4])
    
    return {
        "chi": sum(chi_folded) // 4,
        "chi_folded": chi_folded,
        "state": state,
        "modality": "smell",
        "receptor_pattern": {c["name"]: receptor_outputs[c["name"]]["n_events"]
                             for c in OLFACTORY_CHANNELS},
    }


def smell_deep_for(name):
    """Each thing has a distinct molecular profile."""
    profiles = {
        "cow":     {"barnyard": 0.8, "musky": 0.4, "pungent": 0.3},
        "bears":   {"musky": 0.9, "barnyard": 0.3, "pungent": 0.4, "putrid": 0.2},
        "kittens": {"musky": 0.3, "ethereal": 0.2},
        "room":    {"ethereal": 0.2, "camphor": 0.1},
        "milk":    {"ethereal": 0.4, "floral": 0.1},
        "mush":    {"barnyard": 0.5, "pungent": 0.3, "musky": 0.2},
    }
    if name not in profiles:
        return None
    return smell_hierarchical(profiles[name])


# Self-test
if __name__ == "__main__":
    print("=" * 72)
    print("HIERARCHICAL TOUCH (4 mechanoreceptors)")
    print("=" * 72)
    names = ["cow", "bears", "kittens", "room"]
    perceps = {n: touch_deep_for(n) for n in names}
    print(f"\n{'name':10s} {'Merkel':>8s} {'Meissn':>8s} {'Pacin':>8s} {'Ruff':>8s}")
    for n, p in perceps.items():
        rp = p["receptor_pattern"]
        print(f"  {n:10s} {rp['merkel']:>8d} {rp['meissner']:>8d} {rp['pacinian']:>8d} {rp['ruffini']:>8d}")
    
    pairs = []
    for i, n1 in enumerate(names):
        for n2 in names[i+1:]:
            ov = float(np.abs(np.vdot(perceps[n1]["state"], perceps[n2]["state"]))**2)
            pairs.append((n1, n2, ov))
    pairs.sort(key=lambda x: -x[2])
    print(f"\nMean state overlap: {sum(p[2] for p in pairs)/len(pairs):.3f}")
    
    print("\n" + "=" * 72)
    print("HIERARCHICAL TASTE (5 receptors)")
    print("=" * 72)
    names = ["milk", "mush"]
    perceps = {n: taste_deep_for(n) for n in names}
    print(f"\n{'name':10s} {'sweet':>8s} {'salty':>8s} {'sour':>8s} {'bitter':>8s} {'umami':>8s}")
    for n, p in perceps.items():
        rp = p["receptor_pattern"]
        print(f"  {n:10s} {rp['sweet']:>8d} {rp['salty']:>8d} {rp['sour']:>8d} {rp['bitter']:>8d} {rp['umami']:>8d}")
    
    print("\n" + "=" * 72)
    print("HIERARCHICAL SMELL (8 channels)")
    print("=" * 72)
    names = ["cow", "bears", "kittens", "room"]
    perceps = {n: smell_deep_for(n) for n in names}
    print(f"\n{'name':10s} musky floral minty pung ether camph putr barn")
    for n, p in perceps.items():
        rp = p["receptor_pattern"]
        print(f"  {n:10s} {rp['musky']:>5d} {rp['floral']:>5d} {rp['minty']:>5d} {rp['pungent']:>5d} {rp['ethereal']:>5d} {rp['camphor']:>5d} {rp['putrid']:>5d} {rp['barnyard']:>5d}")
    
    pairs = []
    for i, n1 in enumerate(names):
        for n2 in names[i+1:]:
            ov = float(np.abs(np.vdot(perceps[n1]["state"], perceps[n2]["state"]))**2)
            pairs.append((n1, n2, ov))
    pairs.sort(key=lambda x: -x[2])
    print(f"\nMean smell state overlap: {sum(p[2] for p in pairs)/len(pairs):.3f}")
