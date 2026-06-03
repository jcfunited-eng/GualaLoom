"""
The loom state — context window of strands, current settled state,
the tick() method that advances one step.

Familiarity feedback is computed here: match score from krimelack
recall raises the dead-zone barrier on the next settle.
"""

from typing import Dict, List, Optional, Tuple

from .substrate import (
    FAMILIARITY_GAIN, encode_to_strand, settle_field, l6_freedom,
)
from .krimelack import Krimelack


class Loom:
    def __init__(self, krimelack: Krimelack, context_chars: int = 4):
        self.k = krimelack
        self.ctx = context_chars
        self.familiarity: int = 0
        self.recent: List[int] = []
        self.last_settled: Optional[Tuple[int, ...]] = None

    def tick(self, ch: str) -> Dict:
        """Advance the substrate by one character.

        Encodes the character, settles the field across the context
        window, recalls against krimelack, updates familiarity,
        commits the settled state, decays stale motifs.

        Returns a record of everything that happened this step.
        """
        centered = ord(ch) - 96
        self.recent.append(centered)
        if len(self.recent) > self.ctx:
            self.recent.pop(0)

        strands = [encode_to_strand(c) for c in self.recent]
        settled = settle_field(strands, self.familiarity)
        eff, coll, knee = l6_freedom(settled)

        # Recall — does this settled state match anything?
        fp, score, weight = self.k.recall(settled)

        # Familiarity rises with match score (substrate habituates)
        max_possible = max(len(settled), 1)
        self.familiarity = (score * FAMILIARITY_GAIN) // max_possible if score > 0 else 0

        # Structural lock
        lock = 1 if eff < knee else 0

        # Commit any meaningfully settled state
        committed_fp = None
        was_new = False
        if coll > 0:
            committed_fp, was_new = self.k.commit(settled, active_char=ch)

        # No decay during active feeding. Decay is a sleep function —
        # during waking, motifs only grow. Sleep culls the weak ones.

        self.last_settled = settled

        return {
            "ch": ch, "centered": centered,
            "settled": settled,
            "effective": eff, "collapsed": coll, "knee": knee,
            "lock": lock, "fam": self.familiarity,
            "match": score, "match_fp": fp,
            "committed": committed_fp, "new_motif": was_new,
            "krimelack_size": self.k.size(),
        }

    def feed(self, text: str) -> List[Dict]:
        """Feed a string character by character. Returns all records."""
        return [self.tick(ch) for ch in text]

    def restore(self, recent: List[int], familiarity: int,
                last_settled: Optional[Tuple[int, ...]]) -> None:
        """Restore loom state from persisted data."""
        self.recent = recent
        self.familiarity = familiarity
        self.last_settled = last_settled
