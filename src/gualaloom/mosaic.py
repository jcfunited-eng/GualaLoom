"""
G32 mosaic-of-mosaics — hierarchical loom settling.

Level 0: character-level (what v1 does now)
  - 4 character strands × 8 trits = 32 trit positions
  - settles to one state per tick

Level 1: word/phrase mosaic
  - Accumulates 8 consecutive level-0 settled states as "tiles"
  - At each trit position, computes cross-tile coupling using 3^i
    weights on the tile index (tile 0 = weight 1, tile 7 = weight 2187)
  - Dead-zone thresholds to produce a mosaic-level settled state
  - Mosaic motifs committed to krimelack with level=1 tag

The 3^i coupling is self-similar: same weights at both levels.
At level 0, they weight trit positions within a strand.
At level 1, they weight tiles within a mosaic.
The substrate doesn't know what level it's at. Same mechanism.

Level 2 (mosaic of mosaics) would take 8 level-1 settled states
and do it again. Not built here — testing level 1 first.
"""

from typing import Dict, List, Optional, Tuple

from .substrate import POSITIONAL_3I, DEAD_ZONE_BASE, l6_freedom
from .krimelack import Krimelack, fingerprint

# Mosaic parameters
MOSAIC_WIDTH = 8           # tiles per mosaic (matches 3^i weight count)
MOSAIC_DEAD_ZONE = 100     # higher barrier — mosaic-level structure is
                           # rarer and more meaningful than char-level


def settle_mosaic(tiles: List[Tuple[int, ...]],
                  familiarity: int = 0) -> Tuple[int, ...]:
    """Settle a mosaic of level-0 states into a level-1 state.

    Each tile is a level-0 settled state (32 trits for 4-char context).
    At each trit position, the mosaic computes cross-tile coupling:
      h[pos] = sum over tiles t: tile_t[pos] * 3^t

    Same 3^i identity, applied to tiles instead of trits.
    Structure that persists across tiles commits; structure that
    doesn't stays null — same as level 0.
    """
    if not tiles:
        return ()

    barrier = MOSAIC_DEAD_ZONE + familiarity
    n_positions = len(tiles[0])

    settled = []
    for pos in range(n_positions):
        h = 0
        for t_idx, tile in enumerate(tiles):
            if t_idx >= len(POSITIONAL_3I):
                break
            if pos < len(tile):
                h += tile[pos] * POSITIONAL_3I[t_idx]

        if h > barrier:
            settled.append(1)
        elif h < -barrier:
            settled.append(-1)
        else:
            settled.append(0)

    return tuple(settled)


class MosaicLoom:
    """Accumulates level-0 states and produces level-1 mosaic motifs."""

    def __init__(self, krimelack: Krimelack):
        self.k = krimelack
        self.tiles: List[Tuple[int, ...]] = []
        self.mosaic_familiarity: int = 0
        self.last_mosaic_settled: Optional[Tuple[int, ...]] = None
        self.mosaic_count: int = 0

    def push_tile(self, level0_settled: Tuple[int, ...],
                  active_char: Optional[str] = None) -> Optional[Dict]:
        """Push a level-0 settled state as a tile.

        When MOSAIC_WIDTH tiles accumulate, settle the mosaic and
        commit the result. Returns mosaic stats if a mosaic was
        produced, None otherwise.
        """
        if not level0_settled or all(t == 0 for t in level0_settled):
            return None

        self.tiles.append(level0_settled)

        if len(self.tiles) < MOSAIC_WIDTH:
            return None

        # Settle the mosaic
        mosaic_state = settle_mosaic(self.tiles, self.mosaic_familiarity)
        eff, coll, knee = l6_freedom(mosaic_state)

        # Recall at mosaic level
        fp, score, weight = self.k.recall(mosaic_state)

        # Update mosaic familiarity
        max_possible = max(len(mosaic_state), 1)
        self.mosaic_familiarity = (
            (score * 20) // max_possible if score > 0 else 0
        )

        # Commit if anything collapsed
        committed_fp = None
        was_new = False
        if coll > 0:
            committed_fp, was_new = self.k.commit(
                mosaic_state, origin="mosaic",
                active_char=active_char,
            )

        self.last_mosaic_settled = mosaic_state
        self.mosaic_count += 1

        # Slide window: keep last 4 tiles for overlap
        self.tiles = self.tiles[MOSAIC_WIDTH // 2:]

        result = {
            "mosaic_num": self.mosaic_count,
            "effective": eff, "collapsed": coll, "knee": knee,
            "lock": 1 if eff < knee else 0,
            "match": score, "match_fp": fp,
            "committed": committed_fp, "new_motif": was_new,
            "mosaic_fam": self.mosaic_familiarity,
        }
        return result
