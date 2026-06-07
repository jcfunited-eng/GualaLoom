"""
krimelack_dna.py — Krimelacks with pre-programmed DNA inheritance

Spec Ch.5: krimelack = oscillator ring whose ω is modulated by signal s(t).
ω_krim(t) = ω_0 + κ·s(t). Winding-number transitions are events.

DNA cheat (selective, scaffolded, non-foreclosing):
- Modal krimelacks have pre-tuned signatures for known sensory experiences
  (apple-smell, fire-warmth, water-flow). These are hand-built placeholders
  that will be replaced by real sensor data when the avatar comes online.
- Language krimelack has pre-tuned morphological priors:
  consonant/vowel discrimination, syllable structure, role-class hints
  (subject-class, verb-class, object-class words).
- ENCODING = the cross-modal co-firing across these krimelacks within the
  same atlas window. Not a separate vector layer.

Three criteria for selective cheat (per prior wC):
1. Named as scaffold — DNA is explicitly labeled, hand-built inheritance.
2. Known retirement path — modal signatures get replaced by avatar sensors;
   language morphology becomes refinement from real corpus reading.
3. Does not foreclose primitive — krimelack still transduces, modes still
   form from events, atlas still binds. DNA is the SIGNAL SOURCE, not the
   perceptual mechanism.
"""

import math
import numpy as np
from collections import defaultdict


# ============================================================
# Krimelack primitive (spec Ch.5)
# ============================================================

class Krimelack:
    """Oscillator ring with phase accumulation + winding transitions."""

    def __init__(self, omega_0=2.0, kappa=80.0, dt=0.04,
                 threshold=math.pi / 3, label="unnamed"):
        self.omega_0 = omega_0
        self.kappa = kappa
        self.dt = dt
        self.threshold = threshold
        self.label = label
        self.reset()

    def reset(self):
        self.phase = 0.0
        self.t = 0.0
        self.winding = 0
        self.events = []

    def feed(self, signal_array):
        """Feed signal, accumulate events. Each event = (t, dw, s)."""
        for s in signal_array:
            omega = self.omega_0 + self.kappa * float(s)
            dphi = (omega - self.omega_0) * self.dt
            self.phase += dphi
            self.t += self.dt
            while self.phase >= self.threshold:
                self.phase -= self.threshold
                self.winding += 1
                self.events.append({"t": self.t, "dw": +1, "s": float(s)})
            while self.phase <= -self.threshold:
                self.phase += self.threshold
                self.winding -= 1
                self.events.append({"t": self.t, "dw": -1, "s": float(s)})

    def fingerprint(self):
        """Compact fingerprint of the event stream: (n_events, total_winding,
        mean_s, event-density-by-quadrant)."""
        n = len(self.events)
        if n == 0:
            return (0, 0, 0.0, 0, 0, 0, 0)
        total_w = self.winding
        mean_s = sum(e["s"] for e in self.events) / n
        # Split events into 4 quarters by time
        t_max = max(e["t"] for e in self.events)
        q = [0, 0, 0, 0]
        for e in self.events:
            qi = min(3, int(e["t"] / (t_max / 4 + 1e-9)))
            q[qi] += 1
        return (n, total_w, mean_s, q[0], q[1], q[2], q[3])


# ============================================================
# DNA TABLES — the inheritance cheat, hand-built
# ============================================================

# Sensory DNA: hand-built signatures for words with concrete experience.
# Each modality has independent component values in [0,1].
# Five modalities: sight, sound, smell, taste, touch.
# Replacement path: avatar sensors when ready.
SENSORY_DNA = {
    # nature
    "sun":    {"sight": 0.95, "touch": 0.85},
    "moon":   {"sight": 0.40, "touch": 0.10},
    "fire":   {"sight": 0.85, "touch": 0.95, "sound": 0.60, "smell": 0.70},
    "ice":    {"sight": 0.60, "touch": 0.05},
    "water":  {"sight": 0.45, "touch": 0.40, "sound": 0.50, "taste": 0.20},
    "wind":   {"sound": 0.55, "touch": 0.45},
    "tree":   {"sight": 0.60, "touch": 0.55, "smell": 0.40},
    "leaf":   {"sight": 0.55, "touch": 0.30},
    "flower": {"sight": 0.75, "smell": 0.85, "touch": 0.30},
    "bird":   {"sight": 0.70, "sound": 0.80},
    "star":   {"sight": 0.90},
    "sky":    {"sight": 0.65},
    "cloud":  {"sight": 0.50, "touch": 0.20},
    "rain":   {"sound": 0.60, "touch": 0.40, "sight": 0.40},
    # qualities (single-modality)
    "warm":   {"touch": 0.85},
    "cold":   {"touch": 0.10},
    "hot":    {"touch": 0.95},
    "wet":    {"touch": 0.50},
    "dry":    {"touch": 0.30},
    "loud":   {"sound": 0.90},
    "quiet":  {"sound": 0.10},
    "bright": {"sight": 0.95},
    "dark":   {"sight": 0.10},
    "sweet":  {"taste": 0.85, "smell": 0.50},
    "sour":   {"taste": 0.20, "smell": 0.30},
    "soft":   {"touch": 0.40},
    "hard":   {"touch": 0.80},
    # things
    "apple":  {"sight": 0.70, "smell": 0.85, "taste": 0.80, "touch": 0.45},
    "bread":  {"sight": 0.55, "smell": 0.75, "taste": 0.60, "touch": 0.50},
    "milk":   {"sight": 0.95, "taste": 0.60, "touch": 0.40},
    "salt":   {"taste": 0.90, "sight": 0.85},
    "stone":  {"sight": 0.50, "touch": 0.75},
    "lamb":   {"sight": 0.85, "sound": 0.55, "touch": 0.65},
}


# Language morphology DNA: which class does the word belong to?
# Subject-class: pronouns, common subject nouns
# Verb-class: actions, copulas
# Object-class: nouns that commonly take object position
# Modifier-class: adjectives, adverbs
# This is the syntactic role inheritance — not a label dict that REPLACES the
# substrate's role-formation, but a prior that the krimelack carries on first
# exposure. Role-class refinement happens through repeated context.
ROLE_DNA = {
    # subject-class (high prior to be a subject)
    "i": "subject", "you": "subject", "we": "subject", "he": "subject",
    "she": "subject", "they": "subject", "it": "subject", "guala": "subject",
    "bird": "subject", "sun": "subject", "moon": "subject", "tree": "subject",
    "flower": "subject", "star": "subject", "fire": "subject", "water": "subject",
    "wind": "subject", "cloud": "subject", "rain": "subject", "sky": "subject",
    "lamb": "subject", "apple": "subject", "stone": "subject",
    # verb-class (copulas and actions)
    "am": "verb", "is": "verb", "are": "verb", "was": "verb", "were": "verb",
    "be": "verb", "has": "verb", "have": "verb", "had": "verb",
    "feel": "verb", "think": "verb", "see": "verb", "hear": "verb",
    "listen": "verb", "learn": "verb", "grow": "verb", "wonder": "verb",
    "remember": "verb", "moves": "verb", "rises": "verb", "shines": "verb",
    "flows": "verb", "burns": "verb", "sings": "verb", "sang": "verb",
    "blooms": "verb", "saw": "verb", "tell": "verb", "comes": "verb", "can": "verb",
    # object-class / complement nouns (lower priority than subject-class)
    "leaf": "object", "leaves": "object", "wings": "object", "states": "object",
    "color": "object", "number": "object", "subject": "object", "verb": "object",
    "noun": "object", "action": "object", "name": "object", "word": "object",
    "rule": "object", "sound": "object", "wave": "object", "air": "object",
    "light": "object", "world": "object", "words": "object",
    # modifier-class
    "warm": "modifier", "cold": "modifier", "hot": "modifier", "wet": "modifier",
    "dry": "modifier", "loud": "modifier", "quiet": "modifier", "bright": "modifier",
    "dark": "modifier", "sweet": "modifier", "sour": "modifier", "soft": "modifier",
    "hard": "modifier", "blue": "modifier", "green": "modifier", "white": "modifier",
    "small": "modifier", "great": "modifier", "little": "modifier", "exact": "modifier",
    "true": "modifier", "fast": "modifier", "slow": "modifier", "good": "modifier",
}


# ============================================================
# DNA-equipped language krimelack
# ============================================================

class LanguageKrimelack(Krimelack):
    """Word-level krimelack with DNA: morphology tuning + role priors.

    The krimelack's OUTPUT (event fingerprint + role prior + sensory bindings)
    becomes the cross-modal binding signature in the atlas. The encoding IS
    the binding, per Joe's clarification.
    """

    def __init__(self):
        super().__init__(omega_0=2.0, kappa=80.0, dt=0.04,
                         threshold=math.pi / 3, label="language")

    def transduce(self, word):
        """Transduce a word, returning (fingerprint, role, sensory_dict)."""
        self.reset()
        # Convert characters to signal using morphology DNA tuning:
        # vowels low signal, consonants high signal, with morphology-aware
        # phase offsets at syllable boundaries.
        vowels = set("aeiouy")
        signal = []
        for i, c in enumerate(word.lower()):
            if c in vowels:
                base = -0.3 + (ord(c) - ord('a')) / 25.0 * 0.5
            elif c.isalpha():
                base = +0.4 + (ord(c) - ord('a')) / 25.0 * 0.4
            else:
                base = 0.0
            # 4 samples per character for smooth signal
            for j in range(4):
                signal.append(base + 0.05 * math.sin(i + j * math.pi / 4))
        self.feed(signal)
        fp = self.fingerprint()
        role = ROLE_DNA.get(word.lower(), "unknown")
        senses = SENSORY_DNA.get(word.lower(), {})
        return fp, role, senses


# ============================================================
# Modal krimelack — pre-programmed with one modality's DNA
# ============================================================

class ModalKrimelack(Krimelack):
    """One modality's krimelack. When the language krimelack fires a word
    with this modality in its sensory DNA, this krimelack fires the
    corresponding signature. Co-firing is what the atlas binds."""

    def __init__(self, modality):
        # Each modality gets its own ω_0 so different modalities have
        # distinguishable chi states
        omega_offsets = {"sight": 2.0, "sound": 2.3, "smell": 2.6,
                         "taste": 2.9, "touch": 3.2}
        super().__init__(omega_0=omega_offsets.get(modality, 2.0),
                         kappa=60.0, dt=0.04,
                         threshold=math.pi / 3, label=modality)
        self.modality = modality

    def fire_signature(self, intensity):
        """Fire this modality's krimelack with the given intensity (0..1).
        intensity comes from the SENSORY_DNA for the word being processed."""
        self.reset()
        # Intensity translates to a signal that produces events
        # Signal pattern: ramp + sustain, intensity-modulated
        n_samples = 32
        for i in range(n_samples):
            s = intensity * (0.5 + 0.5 * math.sin(2 * math.pi * i / n_samples))
            self.phase += (self.omega_0 + self.kappa * s - self.omega_0) * self.dt
            self.t += self.dt
            while self.phase >= self.threshold:
                self.phase -= self.threshold
                self.winding += 1
                self.events.append({"t": self.t, "dw": +1, "s": s})
            while self.phase <= -self.threshold:
                self.phase += self.threshold
                self.winding -= 1
                self.events.append({"t": self.t, "dw": -1, "s": s})
        return self.fingerprint()


# ============================================================
# DNA-aware sensory bank
# ============================================================

class SensoryBank:
    """Five modal krimelacks. Fire the ones that match a word's sensory DNA."""

    MODALITIES = ("sight", "sound", "smell", "taste", "touch")

    def __init__(self):
        self.krimelacks = {m: ModalKrimelack(m) for m in self.MODALITIES}

    def fire_for_word(self, sensory_dict):
        """Given a SENSORY_DNA dict for a word, fire all bound krimelacks.
        Returns dict modality -> fingerprint. Empty modalities return None."""
        out = {}
        for m in self.MODALITIES:
            if m in sensory_dict:
                fp = self.krimelacks[m].fire_signature(sensory_dict[m])
                out[m] = fp
            else:
                out[m] = None
        return out
