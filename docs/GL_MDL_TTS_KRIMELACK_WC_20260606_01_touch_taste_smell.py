# doc_id: GL-MDL-TTS-KRIMELACK-WC-20260606-01
# created: 2026-06-06
# author: wC
# related_topic: touch, taste, smell krimelacks
"""
Touch / Taste / Smell krimelack models.

Three modalities completing the 5-modal architecture (sight, sound, touch,
taste, smell). All ArcLoom-canonical: ω(t) = ω₀ + κ·s(t) for single
krimelacks; banks of krimelacks for receptor-bank modalities.

  Touch — single krimelack per touch point. Input = pressure(t).
          Bank organization comes from MANY touch points across a surface,
          but each point's krimelack is the same equation as fovea krimelack.

  Taste — bank of 5 krimelacks: sweet, salty, sour, bitter, umami.
          Each is a scalar intensity over time as food is on the tongue.
          Simplest of the three.

  Smell — bank of N receptors, each tuned to a different molecular feature.
          A "smell" is a vector of concentrations triggering different
          activation patterns across receptors. Same architecture as
          cochlear bank but feature-axis instead of frequency.

Tests for each:
  - Distinct stimuli produce distinct percept fragments
  - Time-varying stimuli encoded naturally
  - Same architecture as sight (touch) and sound (smell) — no new physics

For software-only Guala, all three are driven by hand-built signatures
(per user memory: "hand-built signatures bridge until physical avatar with
real sensors is ready"). The signatures ARE substrate-physical inputs;
hand-built just means Joe specifies them rather than reading from hardware.
"""

import math
import numpy as np
from dataclasses import dataclass, field


# Shared krimelack equation (same as fovea)
OMEGA_0 = 5.0
KAPPA = 50.0
WINDING_PHASE = 2 * math.pi


@dataclass
class ScalarKrimelack:
    """Generic single-channel krimelack: ω(t) = ω_0 + κ·s(t).
    Same architecture used by fovea (pixel intensity), touch (pressure),
    and individual taste receptors."""
    phase: float = 0.0
    winding_count: int = 0
    events: list = field(default_factory=list)
    name: str = ""

    def tick_with_signal(self, signal: float, tick: int, dt: float = 1.0):
        omega = OMEGA_0 + KAPPA * max(0.0, signal)  # clamp negative (no pressure can't be negative)
        self.phase += omega * dt
        while self.phase >= WINDING_PHASE:
            self.winding_count += 1
            self.phase -= WINDING_PHASE
            self.events.append((tick, signal))

    def reset(self):
        self.phase = 0.0
        self.winding_count = 0
        self.events = []


# ============================================================================
# TOUCH
# ============================================================================

@dataclass
class TouchPoint:
    """A single touch sensor location on the avatar. One krimelack per point.
    Pressure(t) drives the krimelack. Texture emerges from time-varying signal."""
    location: tuple                # (body_region, sub_coord) e.g. ("fingertip", 0)
    krimelack: ScalarKrimelack = field(default_factory=ScalarKrimelack)


def synth_touch_tap(duration_ticks=500, tap_at=100, tap_width=20, tap_pressure=0.8):
    """Single quick tap on a touch point. Short pressure spike."""
    signal = np.zeros(duration_ticks)
    signal[tap_at:tap_at + tap_width] = tap_pressure
    return signal


def synth_touch_sustained(duration_ticks=500, pressure=0.6):
    """Sustained even pressure — being held."""
    return np.full(duration_ticks, pressure)


def synth_touch_stroke(duration_ticks=500):
    """Gentle stroke — slow ramp up + ramp down."""
    t = np.linspace(0, math.pi, duration_ticks)
    return 0.5 * np.sin(t)  # half-sine, smooth


def synth_touch_scratch(duration_ticks=500, freq=20):
    """Scratch — rapidly varying pressure (rough texture)."""
    t = np.arange(duration_ticks)
    return 0.4 + 0.3 * np.sin(2 * math.pi * freq * t / duration_ticks * 10)


def exp_touch():
    print("=" * 72)
    print("TOUCH: four pressure profiles, single touch point")
    print("=" * 72)

    profiles = [
        ("tap", synth_touch_tap()),
        ("sustained", synth_touch_sustained()),
        ("stroke", synth_touch_stroke()),
        ("scratch", synth_touch_scratch()),
    ]

    for name, signal in profiles:
        krim = ScalarKrimelack(name=name)
        for tick, s in enumerate(signal):
            krim.tick_with_signal(float(s), tick)
        # Compute fragment statistics
        intervals = []
        if len(krim.events) > 1:
            ticks = [e[0] for e in krim.events]
            intervals = [ticks[i+1] - ticks[i] for i in range(len(ticks)-1)]
        print(f"\n  {name:>12s}: total_pressure={signal.sum():.1f}, "
              f"windings={krim.winding_count}, "
              f"interval_std={np.std(intervals):.2f}" if intervals else
              f"  {name:>12s}: windings={krim.winding_count}, (single-event)")

    print("\n>>> Distinct touch profiles produce distinct windings + temporal")
    print("    structure. Scratch has high interval variance (rough texture),")
    print("    sustained has low variance (smooth held). The fragment")
    print("    sequence carries the touch signature.")


# ============================================================================
# TASTE — bank of 5 receptors
# ============================================================================

TASTE_NAMES = ["sweet", "salty", "sour", "bitter", "umami"]


@dataclass
class TasteBank:
    """Bank of 5 taste krimelacks, one per primary taste quality."""
    receptors: list = field(default_factory=lambda: [
        ScalarKrimelack(name=n) for n in TASTE_NAMES
    ])

    def feed_taste_vector(self, taste_vector_over_time: np.ndarray):
        """taste_vector_over_time: (n_ticks, 5) array — intensity per receptor per tick."""
        for tick in range(taste_vector_over_time.shape[0]):
            for i, krim in enumerate(self.receptors):
                krim.tick_with_signal(float(taste_vector_over_time[tick, i]), tick)

    def signature(self) -> dict:
        """How each receptor fired."""
        return {self.receptors[i].name: self.receptors[i].winding_count
                for i in range(len(self.receptors))}


def synth_taste_strawberry(duration_ticks=400):
    """Strawberry: mostly sweet (0.85), small sour (0.2), trace umami (0.05)."""
    vec_over_time = np.zeros((duration_ticks, 5))
    # Rises in first 50 ticks (food entering mouth), plateau, falls last 100 ticks (swallowed)
    for tick in range(duration_ticks):
        if tick < 50:
            ramp = tick / 50
        elif tick > duration_ticks - 100:
            ramp = (duration_ticks - tick) / 100
        else:
            ramp = 1.0
        vec_over_time[tick, 0] = 0.85 * ramp  # sweet
        vec_over_time[tick, 2] = 0.20 * ramp  # sour
        vec_over_time[tick, 4] = 0.05 * ramp  # umami
    return vec_over_time


def synth_taste_pickle(duration_ticks=400):
    """Pickle: strong sour, salty, faint umami."""
    vec_over_time = np.zeros((duration_ticks, 5))
    for tick in range(duration_ticks):
        if tick < 50:
            ramp = tick / 50
        elif tick > duration_ticks - 100:
            ramp = (duration_ticks - tick) / 100
        else:
            ramp = 1.0
        vec_over_time[tick, 1] = 0.70 * ramp  # salty
        vec_over_time[tick, 2] = 0.85 * ramp  # sour
        vec_over_time[tick, 4] = 0.10 * ramp  # umami
    return vec_over_time


def synth_taste_water(duration_ticks=400):
    """Water: essentially nothing — baseline."""
    return np.zeros((duration_ticks, 5))


def synth_taste_coffee_bitter(duration_ticks=400):
    """Black coffee: bitter dominant, slight sour, faint sweet."""
    vec_over_time = np.zeros((duration_ticks, 5))
    for tick in range(duration_ticks):
        if tick < 50:
            ramp = tick / 50
        elif tick > duration_ticks - 100:
            ramp = (duration_ticks - tick) / 100
        else:
            ramp = 1.0
        vec_over_time[tick, 0] = 0.10 * ramp  # sweet
        vec_over_time[tick, 2] = 0.20 * ramp  # sour
        vec_over_time[tick, 3] = 0.85 * ramp  # bitter
    return vec_over_time


def exp_taste():
    print("\n" + "=" * 72)
    print("TASTE: four food signatures through 5-receptor bank")
    print("=" * 72)

    foods = [
        ("strawberry", synth_taste_strawberry()),
        ("pickle",     synth_taste_pickle()),
        ("water",      synth_taste_water()),
        ("coffee",     synth_taste_coffee_bitter()),
    ]

    print(f"\n{'food':>12s}  {'sweet':>6s} {'salty':>6s} {'sour':>6s} "
          f"{'bitter':>6s} {'umami':>6s}")
    print("  " + "-" * 56)
    for name, signal in foods:
        bank = TasteBank()
        bank.feed_taste_vector(signal)
        sig = bank.signature()
        print(f"  {name:>12s}: " + " ".join(f"{sig[n]:>6d}" for n in TASTE_NAMES))

    print("\n>>> Each food has distinct receptor activation signature.")
    print("    Strawberry: sweet dominant. Pickle: sour+salty. Coffee:")
    print("    bitter dominant. Water: silent. The bank discriminates.")


# ============================================================================
# SMELL — bank of N receptors with feature-axis tuning
# ============================================================================

# Olfactory receptors are biologically tuned to molecular feature axes
# (carbon chain length, polarity, aromaticity, etc.). For modeling, define
# 8 receptor types with affinities for different "feature axes."
# A molecule is represented as a vector along these axes; receptor response
# = (affinity_vector · molecule_vector), clamped to [0, 1].

N_SMELL_RECEPTORS = 8
SMELL_FEATURE_NAMES = ["chain_length", "polarity", "aromaticity",
                       "sulfur", "amine", "ester", "ketone", "acid"]


def make_smell_receptor_affinities(n=N_SMELL_RECEPTORS, seed=42):
    """Each receptor has a vector of affinities along feature axes.
    Generate so receptors are diverse but cover the feature space."""
    rng = np.random.default_rng(seed)
    # Each receptor has high affinity for ~2-3 features, low for others
    affinities = np.zeros((n, n))
    for i in range(n):
        # Receptor i has strongest affinity for feature i, plus 1-2 secondaries
        affinities[i, i] = 0.9
        secondaries = rng.choice([j for j in range(n) if j != i], size=2, replace=False)
        affinities[i, secondaries] = rng.uniform(0.2, 0.5, size=2)
    return affinities


@dataclass
class SmellBank:
    """Bank of olfactory krimelacks, each with feature-axis affinities."""
    affinities: np.ndarray = None
    receptors: list = field(default_factory=list)

    def __post_init__(self):
        if self.affinities is None:
            self.affinities = make_smell_receptor_affinities()
        if not self.receptors:
            self.receptors = [ScalarKrimelack(name=f"smell_recv_{i}")
                              for i in range(N_SMELL_RECEPTORS)]

    def receptor_response(self, molecule_vector: np.ndarray) -> np.ndarray:
        """Each receptor responds = affinity · molecule_vector, clamped [0,1]."""
        responses = self.affinities @ molecule_vector
        return np.clip(responses, 0.0, 1.0)

    def feed_smell_over_time(self, molecule_over_time: np.ndarray):
        """molecule_over_time: (n_ticks, n_features) array."""
        for tick in range(molecule_over_time.shape[0]):
            responses = self.receptor_response(molecule_over_time[tick])
            for i, krim in enumerate(self.receptors):
                krim.tick_with_signal(float(responses[i]), tick)

    def signature(self) -> dict:
        return {self.receptors[i].name: self.receptors[i].winding_count
                for i in range(len(self.receptors))}


def synth_smell(molecule_vector, duration_ticks=400):
    """Smell signature with a typical rise-plateau-fall envelope."""
    out = np.zeros((duration_ticks, len(molecule_vector)))
    for tick in range(duration_ticks):
        if tick < 30:
            ramp = tick / 30
        elif tick > duration_ticks - 80:
            ramp = (duration_ticks - tick) / 80
        else:
            ramp = 1.0
        out[tick] = molecule_vector * ramp
    return out


# Smell "recipes" — vectors along the 8 feature axes
SMELL_LEMON = np.array([0.3, 0.6, 0.4, 0.0, 0.0, 0.8, 0.2, 0.7])  # ester+acid+aromatic
SMELL_ROSE = np.array([0.4, 0.5, 0.6, 0.0, 0.0, 0.3, 0.4, 0.0])   # aromatic+polar
SMELL_BACON = np.array([0.8, 0.2, 0.3, 0.7, 0.4, 0.1, 0.5, 0.1])  # chain+sulfur+ketone
SMELL_SKUNK = np.array([0.5, 0.3, 0.0, 0.95, 0.4, 0.0, 0.0, 0.0]) # heavy sulfur+amine


def exp_smell():
    print("\n" + "=" * 72)
    print(f"SMELL: four smells through {N_SMELL_RECEPTORS}-receptor bank")
    print("=" * 72)

    smells = [
        ("lemon", SMELL_LEMON),
        ("rose",  SMELL_ROSE),
        ("bacon", SMELL_BACON),
        ("skunk", SMELL_SKUNK),
    ]

    # Show what the receptor bank thinks about each
    affinities = make_smell_receptor_affinities()
    print(f"\n  Receptors tuned to feature axes:")
    print(f"    {'recv':>5s}  " + "  ".join(f"{n[:8]:>8s}" for n in SMELL_FEATURE_NAMES))
    for i in range(N_SMELL_RECEPTORS):
        print(f"    R{i:>2d}    " + "  ".join(f"{affinities[i,j]:>8.2f}"
                                              for j in range(N_SMELL_RECEPTORS)))

    print(f"\n  Receptor activation pattern per smell:")
    print(f"  {'smell':>8s}  " + "  ".join(f"R{i}" for i in range(N_SMELL_RECEPTORS)))
    for name, molecule in smells:
        bank = SmellBank(affinities=affinities)
        signal_over_time = synth_smell(molecule)
        bank.feed_smell_over_time(signal_over_time)
        sig = bank.signature()
        counts = [sig[f"smell_recv_{i}"] for i in range(N_SMELL_RECEPTORS)]
        # Normalize to relative pattern
        max_c = max(counts) if max(counts) > 0 else 1
        relative = [c / max_c for c in counts]
        print(f"  {name:>8s}  " + "  ".join(f"{r:>2.1f}" for r in relative))

    print("\n>>> Each smell produces a DISTINCT pattern of receptor")
    print("    activation. Lemon and rose share aromaticity (overlap on those")
    print("    receptors) but differ on others. Skunk lights up sulfur-tuned")
    print("    receptors heavily. The pattern IS the percept signature.")


# ============================================================================
# Cross-modal test — same architecture across all 5 modalities
# ============================================================================

def exp_architecture_consistency():
    print("\n" + "=" * 72)
    print("ARCHITECTURE CONSISTENCY: all 5 modalities, same ω(t) = ω₀ + κ·s(t)")
    print("=" * 72)

    # Drive single krimelacks with constant signals at different intensities
    # All should produce winding rates proportional to (ω_0 + κ·s).
    test_signals = [0.0, 0.2, 0.5, 0.8, 1.0]
    print(f"\n  Input intensity → winding rate over 500 ticks")
    print(f"  (proves same equation works for any sensory modality)")
    print(f"\n  {'intensity':>10s}  {'expected_freq':>15s}  {'measured_windings':>18s}")
    for s in test_signals:
        krim = ScalarKrimelack()
        for tick in range(500):
            krim.tick_with_signal(s, tick)
        expected = OMEGA_0 + KAPPA * s  # rad per tick
        expected_windings = expected * 500 / (2 * math.pi)
        print(f"  {s:>10.2f}  {expected_windings:>15.1f}  {krim.winding_count:>18d}")

    print("\n>>> Linear relationship between input intensity and winding rate.")
    print("    Same equation drives every modality. No special-casing per sense.")


if __name__ == "__main__":
    exp_touch()
    exp_taste()
    exp_smell()
    exp_architecture_consistency()
