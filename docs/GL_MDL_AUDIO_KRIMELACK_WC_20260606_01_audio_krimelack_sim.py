# doc_id: GL-MDL-AUDIO-KRIMELACK-WC-20260606-01
# created: 2026-06-06
# author: wC
# related_topic: audio transduction — cochlear bank
"""
Audio krimelack model — cochlear bank, actual numerical simulation.

Bank of damped driven oscillators per ArcLoom spec. Each oscillator k:
   d²x_k/dt² + γ_k dx_k/dt + ω_k² x_k = κ · audio(t)

Tests:
  Exp A: Pure tone at known frequency — only matching band fires
  Exp B: Two pure tones — corresponding bands fire independently
  Exp C: Voice-like signal (F0 + formants) — band activation matches
  Exp D: Music (chord) — multiple bands fire concurrently
"""

import math
import numpy as np
from dataclasses import dataclass, field


SAMPLE_RATE = 16000  # Hz — standard speech rate
N_OSCILLATORS = 32   # log-spaced cochlear bank
FREQ_LOW = 80.0      # Hz — lowest band (covers male voice F0)
FREQ_HIGH = 4000.0   # Hz — highest band (covers most speech)

# Per-oscillator parameters
Q_FACTOR = 8.0       # quality factor — higher = sharper band selectivity
KAPPA = 1.0          # input coupling
WINDING_AMPLITUDE_THRESHOLD = 1e-5  # only count windings when oscillator is actively driven


@dataclass
class CochlearOscillator:
    """Damped driven oscillator. One band in the cochlear bank."""
    omega_k: float            # natural angular frequency (rad/s)
    gamma_k: float            # damping coefficient
    x: float = 0.0            # displacement
    v: float = 0.0            # velocity
    winding_count: int = 0
    last_zero_cross_sign: int = 0  # for winding detection
    events: list = field(default_factory=list)
    energy_history: list = field(default_factory=list)

    def step(self, audio_sample: float, dt: float, tick: int,
             record_energy: bool = True):
        """Velocity-Verlet integration of d²x/dt² + γ·v + ω²·x = κ·s(t)"""
        accel = KAPPA * audio_sample - self.gamma_k * self.v - self.omega_k**2 * self.x
        self.v += accel * dt
        self.x += self.v * dt

        # Winding events: fire ONLY when amplitude exceeds threshold AND
        # we cross zero with positive velocity. Sub-threshold oscillations
        # (off-resonance bands) produce no winding events. This is what
        # actual cochlear hair cells do — fire only when their resonant
        # frequency has energy in the signal.
        cur_sign = 1 if self.x >= 0 else -1
        if (self.last_zero_cross_sign == -1 and cur_sign == 1 and self.v > 0
                and abs(self.x) > WINDING_AMPLITUDE_THRESHOLD):
            self.winding_count += 1
            self.events.append(tick)
        self.last_zero_cross_sign = cur_sign

        # Energy = (1/2)(v² + ω²·x²) — proportional to amplitude of oscillation
        # at this band. This is the cleanest measure of "this frequency present."
        if record_energy:
            self.energy_history.append(0.5 * (self.v**2 + self.omega_k**2 * self.x**2))


class CochlearBank:
    """Bank of N oscillators at log-spaced frequencies."""

    def __init__(self, n=N_OSCILLATORS, freq_low=FREQ_LOW, freq_high=FREQ_HIGH):
        self.frequencies_hz = np.geomspace(freq_low, freq_high, n)
        self.oscillators = []
        for f_hz in self.frequencies_hz:
            omega = 2 * math.pi * f_hz
            gamma = omega / Q_FACTOR
            self.oscillators.append(CochlearOscillator(omega_k=omega, gamma_k=gamma))

    def feed_audio(self, audio: np.ndarray, record_energy: bool = True):
        """Run the audio signal through the bank."""
        dt = 1.0 / SAMPLE_RATE
        for tick, sample in enumerate(audio):
            for osc in self.oscillators:
                osc.step(sample, dt, tick, record_energy=record_energy)

    def winding_counts(self):
        return np.array([osc.winding_count for osc in self.oscillators])

    def mean_energy_per_band(self):
        return np.array([
            np.mean(osc.energy_history) if osc.energy_history else 0.0
            for osc in self.oscillators
        ])


# ---------------------------------------------------------------------------
# Test signals
# ---------------------------------------------------------------------------

def pure_tone(freq_hz: float, duration_s: float = 0.5, amplitude: float = 1.0):
    """Pure sine wave."""
    t = np.linspace(0, duration_s, int(SAMPLE_RATE * duration_s), endpoint=False)
    return amplitude * np.sin(2 * math.pi * freq_hz * t)


def two_tones(f1: float, f2: float, duration_s: float = 0.5):
    """Two pure tones summed."""
    t = np.linspace(0, duration_s, int(SAMPLE_RATE * duration_s), endpoint=False)
    return 0.5 * np.sin(2 * math.pi * f1 * t) + 0.5 * np.sin(2 * math.pi * f2 * t)


def voice_like(f0_hz: float = 120.0, duration_s: float = 0.5):
    """Voice-like: F0 fundamental plus harmonics at typical formant frequencies.
    Mimics 'ah' vowel: F0=120, F1=730, F2=1090, F3=2440 for male adult."""
    t = np.linspace(0, duration_s, int(SAMPLE_RATE * duration_s), endpoint=False)
    sig = np.zeros_like(t)
    # F0 + harmonics (a glottal pulse train has many harmonics; vocal tract
    # filters them so formants stand out)
    for harmonic_n in range(1, 25):
        f = f0_hz * harmonic_n
        # Amplitude shaped by formants — peaks at F1, F2, F3
        amp = 1.0 / harmonic_n  # natural rolloff
        # Boost near formants
        for formant, gain in [(730, 1.5), (1090, 1.0), (2440, 0.8)]:
            if abs(f - formant) < 150:
                amp *= gain
        sig += amp * np.sin(2 * math.pi * f * t)
    return sig / np.max(np.abs(sig))  # normalize


def chord(notes_hz: list, duration_s: float = 0.5):
    """Musical chord — multiple frequencies summed (with harmonics)."""
    t = np.linspace(0, duration_s, int(SAMPLE_RATE * duration_s), endpoint=False)
    sig = np.zeros_like(t)
    for note in notes_hz:
        for h in range(1, 4):
            sig += (1.0/h) * np.sin(2 * math.pi * note * h * t)
    return sig / np.max(np.abs(sig))


# ---------------------------------------------------------------------------
# Experiments
# ---------------------------------------------------------------------------

def exp_A_pure_tone(freq_hz):
    print(f"\n--- pure tone at {freq_hz} Hz ---")
    bank = CochlearBank()
    audio = pure_tone(freq_hz, duration_s=0.3)
    bank.feed_audio(audio, record_energy=True)

    energies = bank.mean_energy_per_band()
    counts = bank.winding_counts()

    # The strongly-resonating band — highest energy
    top_idx = np.argmax(energies)
    top_freq = bank.frequencies_hz[top_idx]
    print(f"  Top energy band: {top_freq:.1f} Hz (energy={energies[top_idx]:.4f})")
    print(f"  Target was {freq_hz} Hz — distance to nearest band: "
          f"{abs(top_freq - freq_hz):.1f} Hz")
    print(f"  Neighbor energies: ", end="")
    for i in range(max(0, top_idx-1), min(len(energies), top_idx+2)):
        print(f"{bank.frequencies_hz[i]:.0f}Hz={energies[i]:.4f} ", end="")
    print()
    print(f"  Windings at top band: {counts[top_idx]} "
          f"(amplitude-thresholded — fires only when actively driven)")
    return bank


def exp_B_two_tones():
    print("\n--- two simultaneous tones (200 Hz + 1500 Hz) ---")
    bank = CochlearBank()
    audio = two_tones(200, 1500, duration_s=0.3)
    bank.feed_audio(audio, record_energy=True)
    energies = bank.mean_energy_per_band()

    sorted_idx = np.argsort(energies)[::-1]
    print(f"  Top 5 energy bands:")
    for i in sorted_idx[:5]:
        print(f"    {bank.frequencies_hz[i]:.1f} Hz: energy={energies[i]:.4f}")
    print(f"\n  Both ~200 Hz and ~1500 Hz bands should be top energy.")


def exp_C_voice_like():
    print("\n--- voice-like signal: F0=120 Hz with formant structure ---")
    bank = CochlearBank()
    audio = voice_like(f0_hz=120, duration_s=0.3)
    bank.feed_audio(audio, record_energy=True)
    energies = bank.mean_energy_per_band()

    sorted_idx = np.argsort(energies)[::-1]
    print(f"  Top 8 energy bands (should cluster near 120, 730, 1090, 2440 Hz):")
    for i in sorted_idx[:8]:
        print(f"    {bank.frequencies_hz[i]:.1f} Hz: energy={energies[i]:.4f}")


def exp_D_chord():
    print("\n--- musical chord: C major (262, 330, 392 Hz) ---")
    bank = CochlearBank()
    audio = chord([262, 330, 392], duration_s=0.3)
    bank.feed_audio(audio, record_energy=True)
    energies = bank.mean_energy_per_band()

    sorted_idx = np.argsort(energies)[::-1]
    print(f"  Top 6 energy bands (should include ~262, 330, 392 Hz):")
    for i in sorted_idx[:6]:
        print(f"    {bank.frequencies_hz[i]:.1f} Hz: energy={energies[i]:.4f}")


if __name__ == "__main__":
    print("=" * 72)
    print("Cochlear bank experiments")
    print(f"  Bank: {N_OSCILLATORS} oscillators, {FREQ_LOW}-{FREQ_HIGH} Hz log-spaced")
    print(f"  Q factor: {Q_FACTOR}")
    print("=" * 72)
    
    print("\n=== EXP A: Pure tones at known frequencies ===")
    for freq in [100, 250, 1000, 2500]:
        exp_A_pure_tone(freq)
    
    print("\n\n=== EXP B: Two simultaneous tones ===")
    exp_B_two_tones()
    
    print("\n\n=== EXP C: Voice-like (F0 + formants) ===")
    exp_C_voice_like()
    
    print("\n\n=== EXP D: Musical chord ===")
    exp_D_chord()
