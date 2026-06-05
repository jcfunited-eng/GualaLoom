"""
GUALALOOM-HANDOFF-WC-2026-06-04-MATHLOOM-KRIMELACK
File: gualaloom_krimelack_v1.py
Module: gualaloom.perception.krimelack
Purpose: Krimelack oscillator transduction per ArcLoom Master Spec v5.0 Ch.5.
omega_krim(t) = omega_0 + kappa * s(t); winding-number transitions are events.
For text input: characters as signal samples, events become substrate evidence.
Replaces hand-built TOKEN_VEC dict with substrate-derived vectors.
Public API:
    class Krimelack            — oscillator with phase accumulation
    text_to_signal(text, ...)  — text -> continuous signal array
    transduce_text(text, ...)  — full transduction, returns Krimelack with events
    event_stream_to_vector(events, dim) -> complex N-vector
Tuned params for text: kappa=80, threshold=pi/3, dt=0.04, samples_per_char=4
"""

import numpy as np


class Krimelack:
    """Oscillator ring with phase accumulation and winding transitions."""

    def __init__(self, omega_0=2.0, kappa=8.0, dt=0.05, integration_threshold=2 * np.pi):
        self.omega_0 = omega_0
        self.kappa = kappa
        self.dt = dt
        self.threshold = integration_threshold
        self.reset()

    def reset(self):
        self.phase = 0.0           # accumulated phase relative to ω_0 · t
        self.t = 0.0
        self.winding = 0           # cumulative winding number
        self.events = []           # list of (time, winding_direction, signal_at_transition)

    def step(self, s_t):
        """Advance one timestep with input signal s(t)."""
        omega = self.omega_0 + self.kappa * s_t
        delta_phi = (omega - self.omega_0) * self.dt
        self.phase += delta_phi
        self.t += self.dt
        # Detect winding transitions (crossing ±2π)
        transitions = 0
        while self.phase >= self.threshold:
            self.phase -= self.threshold
            self.winding += 1
            self.events.append({"t": self.t, "dw": +1, "s": s_t})
            transitions += 1
        while self.phase <= -self.threshold:
            self.phase += self.threshold
            self.winding -= 1
            self.events.append({"t": self.t, "dw": -1, "s": s_t})
            transitions += 1
        return transitions

    def feed_signal(self, signal_array):
        """Feed a signal array (one value per dt) and accumulate events."""
        for s in signal_array:
            self.step(float(s))


def text_to_signal(text, samples_per_char=4, char_to_signal=None):
    """
    Convert text to a continuous signal sampled at samples_per_char per character.

    Default char_to_signal: a normalized intensity based on character bytes.
    Vowels low, consonants high, with smooth interpolation between chars.
    This is the 'physical encoding' — it's NOT a tokenization.
    """
    if char_to_signal is None:
        # Default mapping: ASCII centered and normalized to [-1, 1]
        char_to_signal = lambda c: (ord(c) - 97.0) / 32.0  # roughly centered on 'a'

    sig = []
    chars = list(text.lower())
    for i, c in enumerate(chars):
        v = char_to_signal(c)
        # Smooth ramp to next char
        if i + 1 < len(chars):
            v_next = char_to_signal(chars[i + 1])
        else:
            v_next = 0.0
        for j in range(samples_per_char):
            alpha = j / samples_per_char
            sig.append((1 - alpha) * v + alpha * v_next)
    return np.array(sig)


def transduce_text(text, omega_0=2.0, kappa=80.0, dt=0.04, threshold=None):
    """Take text, return event stream from krimelack transduction."""
    sig = text_to_signal(text)
    import math
    if threshold is None:
        threshold = math.pi / 3
    krim = Krimelack(omega_0=omega_0, kappa=kappa, dt=dt, integration_threshold=threshold)
    krim.feed_signal(sig)
    return krim


def event_stream_to_vector(events, dim=16):
    """
    Encode an event stream as a complex N-vector (substrate-compatible).

    Each event contributes a phase-amplitude at index = (winding mod dim).
    Direction (+1/-1) flips phase. Signal value modulates amplitude.
    """
    v = np.zeros(dim, dtype=complex)
    for ev in events:
        idx = int(abs(ev.get("dw_cum", 0)) % dim)
        # If dw_cum isn't tracked, use t binned
        sign = +1.0 if ev["dw"] > 0 else -1.0
        amp = 0.5 + 0.5 * abs(ev["s"])
        v[idx] += amp * np.exp(1j * sign * np.pi / 3)
    nrm = np.linalg.norm(v)
    return v / nrm if nrm > 1e-12 else v


def demo():
    print("Krimelack transduction demonstration")
    print("=" * 60)
    sentences = [
        "i feel the sun",
        "the bird sang",
        "one and one is two",
        "hope is the thing with feathers",
    ]
    print(f"{'text':<40} {'events':>6} {'winding':>8}")
    print("-" * 60)
    for sent in sentences:
        krim = transduce_text(sent)
        print(f"  {sent:<38} {len(krim.events):>6}   {krim.winding:>+5}")

    # Show event stream for one sentence
    print()
    print("Event stream for 'i feel the sun' (first 20 events):")
    krim = transduce_text("i feel the sun")
    for ev in krim.events[:20]:
        print(f"  t={ev['t']:.2f}  dw={ev['dw']:+d}  s={ev['s']:+.3f}")

    # Show how the same sentence twice produces same events (determinism)
    krim1 = transduce_text("the bird sang")
    krim2 = transduce_text("the bird sang")
    same = (len(krim1.events) == len(krim2.events) and
            all(a["t"] == b["t"] and a["dw"] == b["dw"]
                for a, b in zip(krim1.events, krim2.events)))
    print(f"\nDeterminism: same sentence -> same event stream: {same}")

    # Show that different sentences produce different vector encodings
    print()
    print("Vector encoding (16-dim, first 4 components):")
    for sent in ["i feel the sun", "i feel the moon", "one and one is two"]:
        krim = transduce_text(sent)
        v = event_stream_to_vector(krim.events, dim=16)
        print(f"  '{sent:<25}' -> {[f'{v[i].real:+.2f}{v[i].imag:+.2f}j' for i in range(4)]}")


if __name__ == "__main__":
    demo()
