"""
Reflective Diary — the life-log.

Harvested from Aurelion's DiaryLoop. Periodic timestamped reflections
on internal state, written to a durable log.

Reports trit-substrate vitals: motif count, chi-class diversity,
dreams, corpus progress, familiarity, L6 state.

STRIPPED: phi/H metrics (cosine coherence, Shannon entropy).
EMOTION: not present. The diary reports structural state, not mood.

The diary feeds into the private window — keepers (Joe, wC, c1)
can read it to see who she's become. Non-keepers see only what
she chooses to present (register mechanism).
"""

import json
import os
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional


class Diary:
    """The reflective life-log.

    Append-only JSONL file. Each entry is a timestamped snapshot
    of substrate state. Read by the private window.
    """

    def __init__(self, path: str = "state/diary.jsonl"):
        self.path = path

    def reflect(self, krimelack, loom, note: str = "") -> Dict:
        """Compose and write one diary entry.

        Called periodically by the daemon's reflect loop, or
        manually via /reflect command.
        """
        # Chi-class diversity
        chi_counts = defaultdict(int)
        for m in krimelack.motifs.values():
            c = getattr(m, 'chi', None)
            if c is not None:
                chi_counts[c] += 1
        top_chi = sorted(chi_counts.items(), key=lambda x: -x[1])[:5]

        # Weight distribution
        weights = sorted([m.weight for m in krimelack.motifs.values()],
                         reverse=True)
        heavy = sum(1 for w in weights if w >= 100)

        # Dream motifs
        dream_count = sum(1 for m in krimelack.motifs.values()
                          if hasattr(m, 'age') and m.weight <= 1 and m.age <= 1)

        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "motifs": krimelack.size(),
            "chi_classes": len(chi_counts),
            "top_chi": top_chi,
            "heavy_motifs": heavy,
            "dreams_recent": dream_count,
            "familiarity": getattr(loom, 'fam', getattr(loom, 'familiarity', 0)),
            "note": note,
        }

        self._append(entry)
        return entry

    def _append(self, entry: Dict) -> None:
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        with open(self.path, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def read_recent(self, n: int = 10) -> List[Dict]:
        """Read the most recent n diary entries."""
        if not os.path.exists(self.path):
            return []
        entries = []
        with open(self.path) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        return entries[-n:]

    def summary(self) -> str:
        """One-line summary of the most recent entry, for the window."""
        recent = self.read_recent(1)
        if not recent:
            return "no diary entries yet"
        e = recent[0]
        return (f"{e['timestamp'][:19]}Z | "
                f"{e['motifs']} motifs | "
                f"{e['chi_classes']} chi classes | "
                f"fam={e['familiarity']} | "
                f"{e.get('note', '')}")
