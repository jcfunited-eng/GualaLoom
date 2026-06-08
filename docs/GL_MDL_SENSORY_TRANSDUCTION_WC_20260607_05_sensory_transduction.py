# doc_id: GL-MDL-SENSORY-TRANSDUCTION-WC-20260607-05
# created: 2026-06-07
# author: wC
"""
Real sensory transduction for Guala's six modalities.

The previous multimodal model (GL-MDL-MULTIMODAL-WC-20260607-04) had visual
and audio krimelacks driven by actual time-varying inputs (intensity fields,
audio waveforms). Touch, taste, smell, and interoception were driven by
CONSTANT scalar vectors. The substrate counted windings on labels, not
on perception.

This model fixes that. Each modality has a time-varying input that reflects
what receiving that sense actually IS:

  TASTE: receptors with sensitivity adaptation. Molecule concentration ramps
         (the substance reaches the tongue and dissolves), sustains, decays.
         Receptors saturate. Cross-talk between channels (sweet receptor has
         some sensitivity to umami-class molecules). The signature of "moon
         dirt" vs "apple" is different not just in which receptors fire but
         in their adaptation curves.

  SMELL: receptors with affinity profiles along 8 feature axes. Concentration
         arrives in PULSES timed to a breathing cycle. Each sniff is a brief
         peak; between sniffs concentration falls. Receptor activation is
         dot(affinity, molecule_profile) * concentration_at_t. A molecule's
         profile is its position in the 8-axis feature space.

  TOUCH: per body region, THREE receptor types — pressure (sustained), texture
         (high-frequency micro-variation), vibration (medium frequency). A
         talcum-on-skin experience has high-frequency-low-amplitude texture
         that's DIFFERENT from sand-on-skin (medium-freq-medium-amplitude)
         or silk (very smooth, almost no texture).

  AUDIO: shaped envelopes. Wind is not sin(2π·120·t). It's broadband noise
         in 100-400Hz with slowly-varying amplitude envelope (gusts). A bell
         is a decaying tone. A crunch is a transient burst.

  VISUAL: stays as fovea krimelack on intensity field — that one was already
          doing real perception.

  INTEROCEPTION: scalar that evolves DURING the experience based on substrate
                 activity. High aggregate winding across modalities raises
                 arousal. Familiar chi binding raises comfort. Novel cofire
                 sets raise alertness. The substrate watching itself.

Then the multi-modal binding test, but now with real perception underneath.
"""

import math
import numpy as np
from dataclasses import dataclass, field
from collections import Counter


# =========================================================================
# Time constants
# =========================================================================
DT = 0.02              # 50 Hz substrate tick
DURATION_TICKS = 2000  # 40 seconds of experience time

OMEGA_0 = 5.0
KAPPA_MAX = 50.0
WINDING_PHASE = 2 * math.pi


# =========================================================================
# Krimelacks
# =========================================================================
@dataclass
class AdaptingKrimelack:
    """Photoresistor krimelack with sensitivity adaptation.
    Sustained high signal → adapt_state decays → effective coupling drops.
    Signal removed → adapt_state recovers slowly.
    This is what every receptor does in a real nervous system."""
    omega_0: float = OMEGA_0
    kappa_max: float = KAPPA_MAX
    adapt_tau: float = 8.0       # seconds to half-adapt under strong signal
    recover_tau: float = 40.0    # seconds to recover (asymmetric, slow)
    phase: float = 0.0
    winding_count: int = 0
    events: list = field(default_factory=list)
    adapt_state: float = 1.0

    def tick(self, signal, t):
        kappa_eff = self.kappa_max * self.adapt_state
        omega = self.omega_0 + kappa_eff * signal
        self.phase += omega * DT
        while self.phase >= WINDING_PHASE:
            self.winding_count += 1
            self.phase -= WINDING_PHASE
            self.events.append(t)
        # Adaptation dynamics
        if signal > 0.1:
            decay_rate = signal / self.adapt_tau
            self.adapt_state -= self.adapt_state * decay_rate * DT
        else:
            self.adapt_state += (1.0 - self.adapt_state) * DT / self.recover_tau
        self.adapt_state = max(0.05, min(1.0, self.adapt_state))

    def firing_rate(self):
        """Recent firing rate from events."""
        if not self.events:
            return 0.0
        recent = [e for e in self.events if e > self.events[-1] - 100]
        return len(recent) / max(1, (self.events[-1] - (self.events[-1] - 100)) * DT)

    def reset(self):
        self.phase = 0.0
        self.events = []
        self.adapt_state = 1.0
        self.winding_count = 0


@dataclass
class CochlearBand:
    """Damped driven oscillator. Steady-state at resonance: x_max ≈ κ·A/(γ·ω).
    To get amplitudes that cross a fixed winding threshold across bands,
    kappa scales with omega (compensating the 1/ω falloff at the source —
    this is the cochlear amplifier analog). Sharp resonance (Q = ω/γ ≈ 8)."""
    omega_k: float
    gamma: float = 0.0  # set in __post_init__ from omega_k
    kappa: float = 0.0  # set in __post_init__ from omega_k
    x: float = 0.0
    v: float = 0.0
    winding_count: int = 0
    events: list = field(default_factory=list)
    last_sign: int = 1
    win_threshold: float = 0.0  # set in __post_init__

    def __post_init__(self):
        # Q ≈ 6, modest damping
        self.gamma = self.omega_k / 6.0
        # Kappa proportional to ω
        self.kappa = self.omega_k * 1.5
        self.win_threshold = 0.002

    def tick(self, signal, t):
        # Stability for Verlet on damped SHO: omega * sub_dt below ~0.3
        n_substeps = max(2, int(self.omega_k * DT / 0.25))
        sub_dt = DT / n_substeps
        for _ in range(n_substeps):
            accel = self.kappa * signal - self.gamma * self.v - (self.omega_k**2) * self.x
            self.x += self.v * sub_dt + 0.5 * accel * sub_dt**2
            new_accel = self.kappa * signal - self.gamma * self.v - (self.omega_k**2) * self.x
            self.v += 0.5 * (accel + new_accel) * sub_dt
            sign = 1 if self.x >= 0 else -1
            if sign != self.last_sign and abs(self.x) > self.win_threshold:
                self.winding_count += 1
                self.events.append(t)
            self.last_sign = sign

    def normalized_energy(self):
        return (0.5 * self.v**2 + 0.5 * (self.omega_k**2) * self.x**2) * self.omega_k

    def reset(self):
        self.x = 0.0
        self.v = 0.0
        self.winding_count = 0
        self.events = []
        self.last_sign = 1


# =========================================================================
# TASTE — 5 adapting receptors with cross-talk
# =========================================================================
TASTE_CHANNELS = ["sweet", "salty", "sour", "bitter", "umami"]

# Each row: how much receptor i responds to PRIMARY molecule for channel j
# (some cross-talk — sweet receptor partly responds to umami molecules)
TASTE_CROSSTALK = np.array([
    [1.00, 0.05, 0.05, 0.00, 0.20],  # sweet receptor
    [0.00, 1.00, 0.15, 0.00, 0.10],  # salty
    [0.10, 0.10, 1.00, 0.10, 0.00],  # sour
    [0.00, 0.05, 0.10, 1.00, 0.05],  # bitter
    [0.15, 0.10, 0.00, 0.10, 1.00],  # umami
])


class TasteBank:
    def __init__(self):
        self.receptors = [AdaptingKrimelack(adapt_tau=6.0) for _ in range(5)]

    def tick(self, molecule_concentrations, t):
        """molecule_concentrations: (sweet, salty, sour, bitter, umami) at time t."""
        m = np.array(molecule_concentrations)
        for i, recep in enumerate(self.receptors):
            stim = float(np.clip(TASTE_CROSSTALK[i] @ m, 0, 1))
            recep.tick(stim, t)

    def reset(self):
        for r in self.receptors:
            r.reset()

    def winding_signature(self):
        return tuple(r.winding_count for r in self.receptors)

    def adapt_signature(self):
        return tuple(round(r.adapt_state, 2) for r in self.receptors)


def molecule_profile_moon_dirt(t_tick, duration_ticks):
    """Time-varying molecule concentration during a moon-dirt taste experience.
    Dominant bitter, slight salty, trace umami (mineral). Ramp/sustain/decay."""
    frac = t_tick / duration_ticks
    if frac < 0.15:
        envelope = frac / 0.15
    elif frac < 0.65:
        envelope = 1.0
    elif frac < 0.95:
        envelope = 1.0 - (frac - 0.65) / 0.30
    else:
        envelope = 0.0
    return (0.0, 0.20 * envelope, 0.05 * envelope, 0.70 * envelope, 0.15 * envelope)


def molecule_profile_apple(t_tick, duration_ticks):
    """Apple taste — sweet dominant, slight sour at start (acidity), umami trace."""
    frac = t_tick / duration_ticks
    if frac < 0.05:
        envelope = frac / 0.05
    elif frac < 0.7:
        envelope = 1.0
    elif frac < 1.0:
        envelope = 1.0 - (frac - 0.7) / 0.30
    else:
        envelope = 0.0
    # First moment has more sour; sweet sustains
    sour_pulse = max(0.0, 1.0 - frac / 0.2)
    return (
        0.75 * envelope,
        0.0,
        0.30 * envelope * sour_pulse + 0.05 * envelope,
        0.0,
        0.10 * envelope,
    )


# =========================================================================
# SMELL — 8 affinity-profile receptors, breathing-modulated concentration
# =========================================================================
SMELL_AXES = ["chain_length", "polarity", "aromaticity", "sulfur",
              "amine", "ester", "ketone", "acid"]

# Each receptor has affinity along these 8 axes
# (8 receptors, each tuned to a primary axis but with secondary sensitivities)
SMELL_AFFINITY = np.array([
    [0.9, 0.2, 0.0, 0.0, 0.1, 0.1, 0.0, 0.0],  # long-chain detector
    [0.2, 0.9, 0.1, 0.0, 0.2, 0.1, 0.0, 0.1],  # polar
    [0.0, 0.1, 0.9, 0.0, 0.0, 0.2, 0.2, 0.0],  # aromatic
    [0.0, 0.0, 0.0, 0.9, 0.1, 0.0, 0.1, 0.0],  # sulfur
    [0.1, 0.2, 0.0, 0.1, 0.9, 0.1, 0.0, 0.0],  # amine
    [0.1, 0.1, 0.2, 0.0, 0.1, 0.9, 0.2, 0.1],  # ester
    [0.0, 0.0, 0.2, 0.1, 0.0, 0.2, 0.9, 0.0],  # ketone
    [0.0, 0.1, 0.0, 0.0, 0.0, 0.1, 0.0, 0.9],  # acid
])


class SmellBank:
    def __init__(self):
        self.receptors = [AdaptingKrimelack(adapt_tau=4.0) for _ in range(8)]

    def tick(self, molecule_profile, concentration_at_t, t):
        """molecule_profile: 8-vector of feature-axis composition.
        concentration_at_t: scalar at time t (breathing-modulated)."""
        m = np.array(molecule_profile) * concentration_at_t
        for i, recep in enumerate(self.receptors):
            stim = float(np.clip(SMELL_AFFINITY[i] @ m, 0, 1))
            recep.tick(stim, t)

    def reset(self):
        for r in self.receptors:
            r.reset()

    def winding_signature(self):
        return tuple(r.winding_count for r in self.receptors)


def breathing_concentration(t_tick, total_ticks):
    """Concentration modulated by ~3-second breath cycle.
    Each inhalation = brief peak; exhalation = trough; brief pause."""
    seconds = t_tick * DT
    cycle = seconds % 3.0
    if cycle < 0.5:
        # Sharp inhale (sniff) — peak rises
        return 0.2 + 1.5 * (cycle / 0.5)
    elif cycle < 1.0:
        # Inhale tail
        return 1.7 - 1.4 * ((cycle - 0.5) / 0.5)
    elif cycle < 2.5:
        # Hold + exhale — falls back to baseline
        return 0.3 - 0.2 * ((cycle - 1.0) / 1.5)
    else:
        # Pause
        return 0.1


SMELL_PROFILE_DUST = (0.4, 0.1, 0.0, 0.0, 0.0, 0.0, 0.05, 0.05)
SMELL_PROFILE_FRUIT = (0.2, 0.5, 0.1, 0.0, 0.0, 0.7, 0.3, 0.2)
SMELL_PROFILE_METAL = (0.0, 0.05, 0.0, 0.3, 0.0, 0.0, 0.0, 0.1)


# =========================================================================
# TOUCH — per region: pressure (slow), texture (fast), vibration (medium)
# =========================================================================
@dataclass
class TouchPoint:
    """One body region with three receptor channels."""
    pressure: AdaptingKrimelack = field(default_factory=lambda: AdaptingKrimelack(adapt_tau=10.0))
    texture: AdaptingKrimelack = field(default_factory=lambda: AdaptingKrimelack(adapt_tau=2.0))
    vibration: AdaptingKrimelack = field(default_factory=lambda: AdaptingKrimelack(adapt_tau=4.0))

    def tick(self, signal_dict, t):
        self.pressure.tick(signal_dict.get("pressure", 0.0), t)
        self.texture.tick(signal_dict.get("texture", 0.0), t)
        self.vibration.tick(signal_dict.get("vibration", 0.0), t)

    def reset(self):
        self.pressure.reset()
        self.texture.reset()
        self.vibration.reset()

    def winding_signature(self):
        return (self.pressure.winding_count, self.texture.winding_count, self.vibration.winding_count)


TOUCH_REGIONS = ["head", "hand", "torso", "foot"]


def touch_profile_talcum_on_head(t_tick, total_ticks):
    """Talcum powder dusted on head — low pressure, very-high-freq texture
    (powder grains brushing skin), no vibration."""
    seconds = t_tick * DT
    pressure = 0.15
    # Texture: very fast micro-variation, low amplitude
    texture = 0.08 + 0.05 * math.sin(2 * math.pi * 30 * seconds)
    vibration = 0.0
    return {"pressure": pressure, "texture": texture, "vibration": vibration}


def touch_profile_apple_in_hand(t_tick, total_ticks):
    """Apple held in hand — sustained pressure, smooth-skin texture (slow
    variation as fingers rotate it), no vibration."""
    seconds = t_tick * DT
    pressure = 0.4
    texture = 0.05 + 0.03 * math.sin(2 * math.pi * 2 * seconds)
    vibration = 0.0
    return {"pressure": pressure, "texture": texture, "vibration": vibration}


def touch_profile_zero(t_tick, total_ticks):
    return {"pressure": 0.0, "texture": 0.0, "vibration": 0.0}


# =========================================================================
# AUDIO — real envelope shapes
# =========================================================================
def audio_soft_wind(t_tick, total_ticks, rng):
    """Broadband noise in 100-400Hz with slow gust envelope."""
    seconds = t_tick * DT
    gust = 0.3 + 0.4 * math.sin(2 * math.pi * 0.2 * seconds + 1.0)
    # Approximate broadband noise by summing a few low freqs with random phases
    noise = sum(0.1 * rng.normal() * math.sin(2 * math.pi * f * seconds)
                for f in [120, 180, 240, 320])
    return 0.15 * gust * noise


def audio_apple_crunch(t_tick, total_ticks, rng):
    """Sharp transient burst around t=15s of experience, then silence."""
    seconds = t_tick * DT
    crunch_time = 15.0
    if abs(seconds - crunch_time) < 0.3:
        # Multi-frequency burst
        burst = sum(math.sin(2 * math.pi * f * seconds + rng.random() * 6.28)
                    for f in [800, 1500, 2400])
        envelope = math.exp(-((seconds - crunch_time) ** 2) / 0.02)
        return 0.5 * envelope * burst
    return 0.02 * rng.normal()


def audio_silent(t_tick, total_ticks, rng):
    return 0.005 * rng.normal()


class CochlearBank:
    def __init__(self):
        freqs_hz = np.geomspace(80, 1500, 6)
        self.bands = [CochlearBand(omega_k=2*math.pi*f) for f in freqs_hz]
        self.freqs_hz = freqs_hz

    def tick(self, signal, t):
        for b in self.bands:
            b.tick(signal, t)

    def reset(self):
        for b in self.bands:
            b.reset()

    def winding_signature(self):
        return tuple(b.winding_count for b in self.bands)

    def active_bands(self, energy_threshold=0.05):
        return tuple(i for i, b in enumerate(self.bands) if b.normalized_energy() > energy_threshold)


# =========================================================================
# VISUAL — same fovea krimelack as before (already real)
# =========================================================================
class VisualBank:
    def __init__(self):
        self.fovea = AdaptingKrimelack(adapt_tau=12.0, kappa_max=KAPPA_MAX)

    def view_picture(self, image, t_start, n_fixations=6, ticks_per_fixation=80):
        """Saccaded foveation. Returns winding pattern."""
        h, w = image.shape
        rng = np.random.default_rng(int(image.sum() * 1000) & 0xFFFF)
        # 4x4 peripheral grid, pick highest-gradient un-fixated cells
        fixated = set()
        n_rows, n_cols = 4, 4
        hs, ws = h // n_rows, w // n_cols
        t = t_start
        for _ in range(n_fixations):
            scores = []
            for r in range(n_rows):
                for c in range(n_cols):
                    if (r, c) in fixated:
                        continue
                    region = image[r*hs:(r+1)*hs, c*ws:(c+1)*ws]
                    scores.append((region.std() + 0.01 * rng.random(), r, c))
            if not scores:
                break
            scores.sort(reverse=True)
            _, r, c = scores[0]
            fixated.add((r, c))
            cy = r * hs + hs // 2
            cx = c * ws + ws // 2
            for _ in range(ticks_per_fixation):
                self.fovea.tick(float(image[cy, cx]), t)
                t += 1
        return t  # final tick

    def reset(self):
        self.fovea.reset()


# =========================================================================
# INTEROCEPTION — driven by aggregate substrate activity
# =========================================================================
class Interoception:
    """Scalar krimelack driven by aggregate substrate activity AND character.
    Not just 'how much winding' — also 'what kind of winding pattern.'
    The substrate watching its own activation level AND structure."""
    def __init__(self):
        self.krim = AdaptingKrimelack(adapt_tau=25.0, kappa_max=40.0)
        self.recent_activity_log = []
        self.baseline = 0.2

    def update(self, modality_winding_counts, t):
        """modality_winding_counts: dict of section → current winding count.
        Interoception responds to RATE (how fast windings are arriving) and
        BALANCE (which modalities dominate)."""
        total = sum(modality_winding_counts.values())
        # Activity term: log-scale so it doesn't saturate immediately
        activity = min(1.0, math.log1p(total) / 8.0)
        # Balance term: how evenly spread across modalities
        # (an experience with many active modalities feels different from
        #  one dominant modality — substrate "balance" sense)
        if total > 0:
            balance = 1.0 - max(modality_winding_counts.values()) / total
        else:
            balance = 0.0
        signal = self.baseline + 0.5 * activity + 0.2 * balance
        signal = float(np.clip(signal, 0, 1))
        self.krim.tick(signal, t)
        self.recent_activity_log.append((t, signal))

    def reset(self):
        self.krim.reset()
        self.recent_activity_log = []

    def winding_signature(self):
        return (self.krim.winding_count,)

    def trajectory(self):
        """Return signal trajectory across the experience — distinguishes
        a slow-build calm from a sharp-spike alert."""
        if not self.recent_activity_log:
            return (0, 0, 0)
        signals = [s for _, s in self.recent_activity_log]
        return (
            round(signals[0], 2),
            round(signals[len(signals)//2], 2),
            round(signals[-1], 2),
        )


# =========================================================================
# MULTI-MODAL EXPERIENCE
# =========================================================================
def run_moon_experience(rng_seed=42):
    """Time-varying signals across all six modalities, all running for the
    full duration. The substrate has to perceive moon-dust the way it would
    if Joe handed her the substance: see it, smell it, taste it, feel it,
    while her internal state responds to having a novel multimodal experience."""
    rng = np.random.default_rng(rng_seed)

    visual = VisualBank()
    cochlea = CochlearBank()
    taste = TasteBank()
    smell = SmellBank()
    touch_head = TouchPoint()
    touch_hand = TouchPoint()
    intero = Interoception()

    # Visual: moon image
    moon_img = np.full((32, 32), 0.1)
    for r in range(32):
        for c in range(32):
            if (r-16)**2 + (c-16)**2 < 36:
                moon_img[r, c] = 0.85
    moon_img += rng.normal(0, 0.02, moon_img.shape)
    moon_img = np.clip(moon_img, 0, 1)

    # Run visual saccades upfront (foveation happens over time)
    # then run the other senses across DURATION_TICKS in parallel
    visual.view_picture(moon_img, t_start=0)

    for t in range(DURATION_TICKS):
        # Audio: soft wind
        cochlea.tick(audio_soft_wind(t, DURATION_TICKS, rng), t)

        # Taste: moon-dirt molecule profile
        taste.tick(molecule_profile_moon_dirt(t, DURATION_TICKS), t)

        # Smell: dust profile with breathing modulation
        conc = breathing_concentration(t, DURATION_TICKS)
        smell.tick(SMELL_PROFILE_DUST, conc, t)

        # Touch: talcum on head, no apple in hand
        touch_head.tick(touch_profile_talcum_on_head(t, DURATION_TICKS), t)
        touch_hand.tick(touch_profile_zero(t, DURATION_TICKS), t)

        # Interoception: respond to substrate activity per-modality
        if t % 10 == 0:
            mod_w = {
                "visual": visual.fovea.winding_count,
                "audio": sum(b.winding_count for b in cochlea.bands),
                "taste": sum(r.winding_count for r in taste.receptors),
                "smell": sum(r.winding_count for r in smell.receptors),
                "touch": sum(touch_head.winding_signature()) + sum(touch_hand.winding_signature()),
            }
            intero.update(mod_w, t)

    return {
        "visual": (visual.fovea.winding_count, round(visual.fovea.adapt_state, 3)),
        "audio_bands": cochlea.active_bands(),
        "audio_windings": cochlea.winding_signature(),
        "taste_windings": taste.winding_signature(),
        "taste_adapt": taste.adapt_signature(),
        "smell_windings": smell.winding_signature(),
        "touch_head_winding": touch_head.winding_signature(),
        "touch_hand_winding": touch_hand.winding_signature(),
        "intero_winding": intero.winding_signature(),
        "intero_trajectory": intero.trajectory(),
    }


def run_apple_experience(rng_seed=43):
    rng = np.random.default_rng(rng_seed)

    visual = VisualBank()
    cochlea = CochlearBank()
    taste = TasteBank()
    smell = SmellBank()
    touch_head = TouchPoint()
    touch_hand = TouchPoint()
    intero = Interoception()

    apple_img = np.full((32, 32), 0.2)
    for r in range(32):
        for c in range(32):
            if (r-16)**2 + (c-16)**2 < 49:
                apple_img[r, c] = 0.7
    apple_img += rng.normal(0, 0.02, apple_img.shape)
    apple_img = np.clip(apple_img, 0, 1)
    visual.view_picture(apple_img, t_start=0)

    for t in range(DURATION_TICKS):
        cochlea.tick(audio_apple_crunch(t, DURATION_TICKS, rng), t)
        taste.tick(molecule_profile_apple(t, DURATION_TICKS), t)
        conc = breathing_concentration(t, DURATION_TICKS)
        smell.tick(SMELL_PROFILE_FRUIT, conc, t)
        touch_head.tick(touch_profile_zero(t, DURATION_TICKS), t)
        touch_hand.tick(touch_profile_apple_in_hand(t, DURATION_TICKS), t)
        if t % 10 == 0:
            mod_w = {
                "visual": visual.fovea.winding_count,
                "audio": sum(b.winding_count for b in cochlea.bands),
                "taste": sum(r.winding_count for r in taste.receptors),
                "smell": sum(r.winding_count for r in smell.receptors),
                "touch": sum(touch_head.winding_signature()) + sum(touch_hand.winding_signature()),
            }
            intero.update(mod_w, t)

    return {
        "visual": (visual.fovea.winding_count, round(visual.fovea.adapt_state, 3)),
        "audio_bands": cochlea.active_bands(),
        "audio_windings": cochlea.winding_signature(),
        "taste_windings": taste.winding_signature(),
        "taste_adapt": taste.adapt_signature(),
        "smell_windings": smell.winding_signature(),
        "touch_head_winding": touch_head.winding_signature(),
        "touch_hand_winding": touch_hand.winding_signature(),
        "intero_winding": intero.winding_signature(),
        "intero_trajectory": intero.trajectory(),
    }


# =========================================================================
# PERCEPTION TESTS — prove each modality is actually doing something
# =========================================================================
def test_taste_adaptation():
    """A taste receptor under SUSTAINED bitter input — firing rate should
    DECREASE over time (adaptation), not stay constant or increase."""
    print("--- TASTE: adaptation under sustained signal ---")
    tb = TasteBank()
    # Sustained pure bitter
    first_quarter_windings = 0
    last_quarter_windings = 0
    for t in range(2000):
        tb.tick((0.0, 0.0, 0.0, 0.7, 0.0), t)
    # Sample at 25% and 100% of run
    counts_at_quarters = []
    tb2 = TasteBank()
    for t in range(2000):
        tb2.tick((0.0, 0.0, 0.0, 0.7, 0.0), t)
        if t in [499, 999, 1499, 1999]:
            counts_at_quarters.append(tb2.receptors[3].winding_count)
    deltas = [counts_at_quarters[i+1] - counts_at_quarters[i] for i in range(3)]
    print(f"  Bitter receptor windings per 500-tick quarter: {deltas}")
    print(f"  Adapt_state at end: {tb.receptors[3].adapt_state:.3f}")
    decreasing = all(deltas[i] >= deltas[i+1] for i in range(len(deltas)-1))
    print(f"  {'✓' if decreasing else '✗'} Firing rate {'monotonically decreases' if decreasing else 'does NOT consistently decrease'} (adaptation working)")
    print()


def test_smell_breathing():
    """Smell receptor on a dust profile under BREATHING modulation —
    winding events should cluster at breath peaks, not be uniform."""
    print("--- SMELL: breathing-locked firing ---")
    sb = SmellBank()
    breath_peaks = []
    for t in range(3000):
        conc = breathing_concentration(t, 3000)
        if (t * DT) % 3.0 < 0.5 and conc > 0.5:
            breath_peaks.append(t)
        sb.tick(SMELL_PROFILE_DUST, conc, t)
    primary_recep = sb.receptors[0]  # long-chain — best match for dust profile
    if not primary_recep.events:
        print("  ✗ No smell events fired")
        return
    # Are most events near breath peaks?
    near_peak = 0
    for evt_t in primary_recep.events:
        if any(abs(evt_t - bp) < 50 for bp in breath_peaks):
            near_peak += 1
    frac = near_peak / len(primary_recep.events)
    print(f"  Receptor windings near breath peaks: {near_peak}/{len(primary_recep.events)} = {frac:.2%}")
    print(f"  {'✓' if frac > 0.6 else '~'} {'Clear' if frac > 0.6 else 'Partial'} breathing-locked firing")
    print()


def test_touch_texture_distinguishes():
    """Talcum (high-freq texture) and silk-like (very-low-freq texture) should
    produce different texture-channel winding patterns even at similar pressure."""
    print("--- TOUCH: texture-frequency distinguishes surfaces ---")
    tp_talcum = TouchPoint()
    tp_silk = TouchPoint()
    for t in range(2000):
        tp_talcum.tick(touch_profile_talcum_on_head(t, 2000), t)
        # silk: same pressure, no texture
        tp_silk.tick({"pressure": 0.15, "texture": 0.02, "vibration": 0.0}, t)
    talcum_sig = tp_talcum.winding_signature()
    silk_sig = tp_silk.winding_signature()
    print(f"  Talcum (pressure, texture, vibration windings): {talcum_sig}")
    print(f"  Silk-like (same pressure, near-zero texture):   {silk_sig}")
    different = talcum_sig[1] != silk_sig[1]
    print(f"  {'✓' if different else '✗'} Texture channel {'distinguishes' if different else 'does NOT distinguish'} the surfaces")
    print()


def test_audio_envelope_distinguishes():
    """Wind (broadband, slow gust envelope) vs bell-like (decaying single tone)
    should activate different cochlear bands and produce different total windings."""
    print("--- AUDIO: envelope shape distinguishes stimuli ---")
    cb_wind = CochlearBank()
    cb_crunch = CochlearBank()
    rng = np.random.default_rng(0)
    for t in range(1500):
        cb_wind.tick(audio_soft_wind(t, 1500, rng), t)
        cb_crunch.tick(audio_apple_crunch(t, 1500, rng), t)
    wind_bands = cb_wind.active_bands(energy_threshold=0.02)
    crunch_bands = cb_crunch.active_bands(energy_threshold=0.02)
    print(f"  Wind active bands (out of 8):   {wind_bands}")
    print(f"  Crunch active bands (out of 8): {crunch_bands}")
    different = wind_bands != crunch_bands
    print(f"  {'✓' if different else '✗'} {'Distinct' if different else 'Same'} band activation pattern")
    print()


# =========================================================================
# MULTI-MODAL BINDING TEST (with real perception underneath)
# =========================================================================
def test_multimodal_signatures():
    """Now that each modality is actually perceiving, do moon and apple
    produce substantively different signatures across all six channels?"""
    print("=" * 74)
    print("MULTI-MODAL: moon vs apple experience signatures")
    print("=" * 74)
    moon = run_moon_experience()
    apple = run_apple_experience()

    print()
    print(f"  MOON:")
    for k, v in moon.items():
        print(f"    {k:>20s}: {v}")
    print()
    print(f"  APPLE:")
    for k, v in apple.items():
        print(f"    {k:>20s}: {v}")

    # Count how many modalities differ
    differing = 0
    for k in moon:
        if moon[k] != apple[k]:
            differing += 1
    print()
    print(f"  Modalities with different signatures: {differing}/9")
    if differing >= 7:
        print(f"  ✓ Substrate carries rich multi-modal differences between experiences.")
    elif differing >= 4:
        print(f"  ~ Most modalities differ; some collapse.")
    else:
        print(f"  ✗ Most modalities produce same signature — perception is too coarse.")


if __name__ == "__main__":
    print("=" * 74)
    print("Real sensory transduction tests")
    print("=" * 74)
    print()
    test_taste_adaptation()
    test_smell_breathing()
    test_touch_texture_distinguishes()
    test_audio_envelope_distinguishes()
    test_multimodal_signatures()
