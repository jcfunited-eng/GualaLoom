"""
GL-MDL-PRIMITIVES-WC-20260608-01

Layer 1: Programmed substrate primitives.

Letters, digits, special chars are PROGRAMMED as orthogonal trit-encoded
modes in their respective sections. Not learned. Installed.

Each primitive has:
  - A unique sparse ternary vector (trit pattern)
  - A chi value (from krimelack transduction of the character)
  - Lives in a typed section (LETTER, DIGIT, PUNCT)

These primitives are the substrate's alphabet. Everything above composes
from them.
"""

import math
import numpy as np
import string


N = 16  # substrate state dimension
LETTER_SPARSITY = 5  # number of non-zero trits per letter (more = more discriminable)
DIGIT_SPARSITY = 5
PUNCT_SPARSITY = 6


def normalize(v):
    nrm = np.linalg.norm(v)
    return v if nrm < 1e-12 else v / nrm


def make_trit_vec(seed, sparsity, n=N):
    """Build orthogonal-ish sparse ternary vector deterministically from seed."""
    rng = np.random.default_rng(seed)
    v = np.zeros(n, dtype=complex)
    positions = rng.choice(n, size=sparsity, replace=False)
    # Real and imaginary trits independently for richer encoding
    re_signs = rng.choice([-1, 1], size=sparsity)
    im_signs = rng.choice([-1, 1], size=sparsity)
    for i, p in enumerate(positions):
        v[p] = re_signs[i] + 1j * im_signs[i]
    return normalize(v)


# --- Build primitive sections ---

LETTER_VECS = {}
LETTER_CHIS = {}
for i, c in enumerate(string.ascii_lowercase):
    LETTER_VECS[c] = make_trit_vec(1000 + i, LETTER_SPARSITY)

DIGIT_VECS = {}
for i, c in enumerate("0123456789"):
    DIGIT_VECS[c] = make_trit_vec(2000 + i, DIGIT_SPARSITY)

PUNCT_CHARS = " .,!?'-:;()"
PUNCT_VECS = {}
for i, c in enumerate(PUNCT_CHARS):
    PUNCT_VECS[c] = make_trit_vec(3000 + i, PUNCT_SPARSITY)


def char_vec(c):
    """Get the trit-encoded primitive vector for any character."""
    c = c.lower()
    if c in LETTER_VECS:
        return ("LETTER", LETTER_VECS[c])
    if c in DIGIT_VECS:
        return ("DIGIT", DIGIT_VECS[c])
    if c in PUNCT_VECS:
        return ("PUNCT", PUNCT_VECS[c])
    return (None, None)


def char_type(c):
    c = c.lower()
    if c in LETTER_VECS:
        return "LETTER"
    if c in DIGIT_VECS:
        return "DIGIT"
    if c in PUNCT_VECS:
        return "PUNCT"
    return None


def recognize_char(input_vec, kind=None):
    """Direct overlap recognition — return the character whose primitive
    best matches input. Optionally restrict to a kind (LETTER/DIGIT/PUNCT)."""
    bank = {}
    if kind == "LETTER" or kind is None:
        bank.update({c: v for c, v in LETTER_VECS.items()})
    if kind == "DIGIT" or kind is None:
        bank.update({c: v for c, v in DIGIT_VECS.items()})
    if kind == "PUNCT" or kind is None:
        bank.update({c: v for c, v in PUNCT_VECS.items()})
    if not bank:
        return None, 0.0
    best, score = None, -1
    for c, v in bank.items():
        s = float(np.abs(np.vdot(v, input_vec)) ** 2)
        if s > score:
            score, best = s, c
    return best, score


# --- Self-test ---
if __name__ == "__main__":
    # Check pairwise orthogonality
    def pairs_stats(d):
        items = list(d.items())
        ovs = []
        for i, (k1, v1) in enumerate(items):
            for (k2, v2) in items[i+1:]:
                ovs.append(float(np.abs(np.vdot(v1, v2))**2))
        return {
            "n": len(ovs),
            "mean": sum(ovs) / max(len(ovs), 1),
            "max": max(ovs) if ovs else 0,
            "min": min(ovs) if ovs else 0,
        }

    print("Letter primitive overlap:", pairs_stats(LETTER_VECS))
    print("Digit primitive overlap:", pairs_stats(DIGIT_VECS))
    print("Punct primitive overlap:", pairs_stats(PUNCT_VECS))

    # Test recognition
    print("\nDirect recognition test:")
    test = "hello world 123 it's me!"
    correct = 0
    total = 0
    for c in test:
        kind = char_type(c)
        if kind is None:
            continue
        _, vec = char_vec(c)
        rec, score = recognize_char(vec, kind=kind)
        ok = "✓" if rec == c else "✗"
        if rec == c:
            correct += 1
        total += 1
        print(f"  {ok} '{c}' ({kind}) -> '{rec}' (score={score:.3f})")
    print(f"\nRecognition: {correct}/{total} = {correct/max(total,1):.1%}")
