"""
The six substrate pieces, minus krimelack (which gets its own module).

1. Balanced ternary {-1, 0, +1}
2. 3^i positional coupling
3. Dead-zone settling
4. (Krimelack — see krimelack.py)
5. L6 dimensional exhaustion
6. (Familiarity feedback — computed in loom.py tick())

No imports beyond stdlib.
"""

from typing import List, Tuple

# Mathematical identity. Not tunable.
POSITIONAL_3I: Tuple[int, ...] = (1, 3, 9, 27, 81, 243, 729, 2187)
TRITS_PER_STRAND: int = 8

# Dead-zone base barrier. Tuned for ASCII character context in the v0
# sandbox. Mid-position weights (27, 81) carry the structure; barrier
# admits those when context aligns, rejects when it doesn't.
DEAD_ZONE_BASE: int = 15

# Familiarity gain per unit of match score.
FAMILIARITY_GAIN: int = 20


def encode_to_strand(value: int) -> Tuple[int, ...]:
    """Convert an integer to balanced ternary strand of TRITS_PER_STRAND trits.

    Each trit is -1, 0, or +1. The encoding satisfies:
        value == sum(trit * 3^i for i, trit in enumerate(strand))
    """
    v = value
    trits = []
    for _ in range(TRITS_PER_STRAND):
        r = v % 3
        if r == 2:
            r = -1
            v = (v + 1) // 3
        else:
            v = (v - r) // 3
        trits.append(r)
    return tuple(trits)


def decode_strand(strand: Tuple[int, ...]) -> int:
    """Inverse of encode_to_strand. Reconstructs the integer from trits."""
    return sum(t * w for t, w in zip(strand, POSITIONAL_3I))


def settle_field(input_strands: List[Tuple[int, ...]],
                 familiarity: int) -> Tuple[int, ...]:
    """Settle the full loom state across the context window.

    Each position's pressure = its own trit * 3^i weight, plus
    cross-strand resonance from the same position in other strands.
    If pressure exceeds the barrier (dead zone + familiarity), the
    position commits +1 or -1. Otherwise it stays null (0).

    Returns the full settled state: n_strands * TRITS_PER_STRAND trits.
    This is what L6 evaluates and krimelack stores as a motif.
    """
    barrier = DEAD_ZONE_BASE + familiarity
    if not input_strands:
        return ()

    settled = []
    for s_idx, strand in enumerate(input_strands):
        for i in range(TRITS_PER_STRAND):
            # Local pressure: this trit's own weighted vote
            h = strand[i] * POSITIONAL_3I[i]
            # Cross-strand resonance: other strands reinforce or oppose
            for other_idx, other in enumerate(input_strands):
                if other_idx == s_idx:
                    continue
                h += other[i] * POSITIONAL_3I[i] // 2
            if h > barrier:
                settled.append(1)
            elif h < -barrier:
                settled.append(-1)
            else:
                settled.append(0)
    return tuple(settled)


def l6_freedom(state: Tuple[int, ...]) -> Tuple[int, int, int]:
    """L6 dimensional exhaustion.

    Returns (n_effective, n_collapsed, knee).
    Structural lock fires when n_effective < knee (= n / e).
    """
    n = len(state)
    if n == 0:
        return (0, 0, 0)
    collapsed = sum(1 for t in state if t != 0)
    effective = n - collapsed
    knee = round(n / 2.718281828459045)
    return (effective, collapsed, knee)
