"""
Motif-recall-driven character generation.

Ported from wC's v1 single-file gualaloom.py generate() which has
the loop-breaker that the package was missing.

The key mechanism: if we keep landing on the same motif, the substrate
is looping. Raise the bar — walk to a weaker successor instead of
the strongest, to escape the attractor. If stuck for 3+ consecutive
hits on the same motif, stop honestly (the field has nothing new).
"""

from typing import List, Optional

from .krimelack import Krimelack
from .loom import Loom


def generate_response(loom: Loom, krimelack: Krimelack,
                      max_chars: int = 120) -> str:
    """Generate characters by motif-recall + successor walk.

    Each generated character is fed back through tick() so the loom
    state evolves — the substrate hears itself speak.

    Loop-breaker: tracks recent recalled motif fingerprints. When the
    same motif appears repeatedly in the last 4 steps, generation
    skips past the dominant successor to a weaker one. This is the
    familiarity-raises-the-bar escape from wC's v1, applied at the
    generation level.
    """
    out: List[str] = []
    recent_fps: List[str] = []

    for _ in range(max_chars):
        if loom.last_settled is None:
            break

        best_fp, score, weight = krimelack.recall(loom.last_settled)
        if best_fp is None:
            break

        m = krimelack.get_motif(best_fp)
        if m is None:
            break

        # Loop detection: how many times has this motif appeared
        # in the last 4 generation steps?
        loop_depth = recent_fps[-4:].count(best_fp)
        recent_fps.append(best_fp)

        # Follow successor chain. If looping, skip past the dominant
        # successor to a weaker one — escape the attractor.
        nxt = None
        if m.successors:
            ranked = sorted(m.successors.items(), key=lambda kv: -kv[1])
            # Skip self-loops AND skip past dominant successor when looping
            candidates = [(fp, cnt) for fp, cnt in ranked
                          if fp != best_fp and krimelack.get_motif(fp) is not None]
            if candidates:
                idx = min(loop_depth, len(candidates) - 1)
                nxt_fp = candidates[idx][0]
                nxt = krimelack.get_motif(nxt_fp)

        # Fall back to the recalled motif itself if no successor
        if nxt is None:
            nxt = m

        if not nxt.char_counts:
            break

        # Pick character. If looping, skip past the dominant character
        # to a less common one — vary the output.
        chars = sorted(nxt.char_counts.items(), key=lambda kv: -kv[1])
        # Filter out newlines
        chars = [(ch, cnt) for ch, cnt in chars if ch != "\n"]
        if not chars:
            break

        ch = chars[0][0]
        if loop_depth > 0 and len(chars) > 1:
            idx = min(loop_depth, len(chars) - 1)
            ch = chars[idx][0]

        out.append(ch)
        loom.tick(ch)

        # Stuck — the field has nothing new to say. Stop honestly.
        if loop_depth >= 3:
            break

    return "".join(out).strip()
