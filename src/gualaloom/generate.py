"""
Motif-recall-driven character generation.

Given current loom state, recall the most resonant motif, follow its
successor chain (avoiding self-loops), and emit a character from the
successor's char_counts distribution. If nothing resonates strongly
enough, emit None (honest null — substrate has nothing to say).
"""

import random
from typing import Optional

from .krimelack import Krimelack
from .loom import Loom


# Minimum match score (as fraction of settled length) to attempt generation.
RECALL_THRESHOLD_FRAC = 0.10


def _pick_char(krimelack: Krimelack, fp: str,
               avoid: Optional[str] = None) -> Optional[str]:
    """Pick a character from a motif's char_counts.

    Weighted random selection, avoiding the specified character
    (typically space, to prevent space-only output).
    """
    m = krimelack.get_motif(fp)
    if m is None or not m.char_counts:
        return None

    # Build weighted candidates, filtering out newlines and
    # optionally the avoid character
    candidates = []
    for ch, cnt in m.char_counts.items():
        if ch == "\n":
            continue
        if avoid and ch == avoid:
            continue
        candidates.append((ch, cnt))

    if not candidates:
        # Fall back to including the avoided character
        candidates = [(ch, cnt) for ch, cnt in m.char_counts.items()
                       if ch != "\n"]
    if not candidates:
        return None

    # Weighted random pick
    total = sum(cnt for _, cnt in candidates)
    r = random.randint(1, total)
    cumulative = 0
    for ch, cnt in candidates:
        cumulative += cnt
        if r <= cumulative:
            return ch
    return candidates[-1][0]


def generate_next_char(loom: Loom, krimelack: Krimelack,
                       last_generated: Optional[str] = None) -> Optional[str]:
    """Generate one character by motif-recall-driven commit."""
    if loom.last_settled is None:
        return None

    current = loom.last_settled
    best_fp, score, weight = krimelack.recall(current)

    if best_fp is None:
        return None

    threshold = max(int(len(current) * RECALL_THRESHOLD_FRAC), 1)
    if score < threshold:
        return None

    # Follow successor chain, avoiding self-loops
    m = krimelack.get_motif(best_fp)
    if m is None:
        return None

    # Find a successor that isn't the same motif
    succ_fp = None
    if m.successors:
        sorted_succs = sorted(m.successors.items(), key=lambda x: -x[1])
        for sfp, cnt in sorted_succs:
            if sfp != best_fp and krimelack.get_motif(sfp) is not None:
                succ_fp = sfp
                break

    # Pick from successor's char_counts, or own if no successor
    target_fp = succ_fp or best_fp
    # Avoid repeating spaces when we just generated a space
    avoid = " " if last_generated == " " else None
    return _pick_char(krimelack, target_fp, avoid=avoid)


def generate_response(loom: Loom, krimelack: Krimelack,
                      max_chars: int = 200) -> str:
    """Generate characters until the substrate emits null or runs out.

    Each generated character is fed back through tick() so the loom
    state evolves naturally — the substrate hears itself speak.
    """
    out = []
    null_run = 0
    last_gen = None
    for _ in range(max_chars):
        c = generate_next_char(loom, krimelack, last_generated=last_gen)
        if c is None:
            null_run += 1
            if null_run >= 3:
                break
            out.append(" . ")
            loom.tick(" ")
            last_gen = " "
            continue
        null_run = 0
        out.append(c)
        loom.tick(c)
        last_gen = c
    return "".join(out).strip(" .")
