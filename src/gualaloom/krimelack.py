"""
Krimelack — content-addressable structural memory.

Motifs are settled loom states. Commit by settling, recall by resonance.
Successor tracking: when motif A commits at time t and motif B commits
at t+1, A records B as a successor. This is the generation mechanism —
given a recalled motif, its most common successor predicts the next
committed state.

Persistence is handled by persist.py; this module owns the data
structure and in-memory operations.
"""

import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple


def compute_chi(state: Tuple[int, ...], trits_per_strand: int = 8) -> int:
    """Euler characteristic V - E over the motif's coupling graph.
    Inlined from topology.py — avoids cross-branch dependency.
    Vertices = committed trits, edges = adjacent-in-strand + same-pos-cross-strand."""
    verts = [i for i, t in enumerate(state) if t != 0]
    vset = set(verts)
    V = len(verts)
    if V == 0:
        return 0
    E = 0
    for v in verts:
        neighbor = v + 1
        if neighbor in vset and neighbor // trits_per_strand == v // trits_per_strand:
            E += 1
        cross = v + trits_per_strand
        if cross in vset:
            E += 1
    return V - E


class Motif:
    __slots__ = ("fingerprint", "state", "weight", "age",
                 "first_seen", "last_resonated", "successors",
                 "char_counts", "origin", "chi")

    def __init__(self, fingerprint: str, state: Tuple[int, ...],
                 weight: int = 1, age: int = 0,
                 first_seen: Optional[str] = None,
                 last_resonated: Optional[str] = None,
                 successors: Optional[Dict[str, int]] = None,
                 char_counts: Optional[Dict[str, int]] = None,
                 origin: str = "commit",
                 chi: Optional[int] = None):
        self.fingerprint = fingerprint
        self.state = state
        self.weight = weight
        self.age = age
        now = datetime.now(timezone.utc).isoformat()
        self.first_seen = first_seen or now
        self.last_resonated = last_resonated or now
        self.successors = successors or {}
        self.char_counts = char_counts or {}
        self.origin = origin
        self.chi = chi if chi is not None else compute_chi(state)

    def to_dict(self) -> dict:
        return {
            "fingerprint": self.fingerprint,
            "state": list(self.state),
            "weight": self.weight,
            "age": self.age,
            "first_seen": self.first_seen,
            "last_resonated": self.last_resonated,
            "successors": self.successors,
            "char_counts": self.char_counts,
            "origin": self.origin,
            "chi": self.chi,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Motif":
        return cls(
            fingerprint=d["fingerprint"],
            state=tuple(d["state"]),
            weight=d.get("weight", 1),
            age=d.get("age", 0),
            first_seen=d.get("first_seen"),
            last_resonated=d.get("last_resonated"),
            successors=d.get("successors", {}),
            char_counts=d.get("char_counts", {}),
            origin=d.get("origin", "commit"),
            chi=d.get("chi"),
        )


def fingerprint(state: Tuple[int, ...]) -> str:
    """SHA-1 prefix of the trit string. Deterministic."""
    s = "".join({-1: "-", 0: "0", 1: "+"}[t] for t in state)
    return hashlib.sha1(s.encode("ascii")).hexdigest()[:12]


DECAY_RATE = 1


class Krimelack:
    def __init__(self) -> None:
        self.motifs: Dict[str, Motif] = {}
        self._last_committed_fp: Optional[str] = None

    def commit(self, state: Tuple[int, ...],
               origin: str = "commit",
               active_char: Optional[str] = None) -> Tuple[str, bool]:
        """Commit a settled state. Returns (fingerprint, was_new).

        If the motif already exists, reinforce it. If new, create it.
        Records successor linkage from the previously committed motif.
        active_char: the character being fed when this commit happens.
        """
        if all(t == 0 for t in state):
            return ("null", False)

        fp = fingerprint(state)
        now = datetime.now(timezone.utc).isoformat()
        was_new = False

        if fp in self.motifs:
            m = self.motifs[fp]
            m.weight += 1
            m.last_resonated = now
        else:
            self.motifs[fp] = Motif(fingerprint=fp, state=state,
                                    origin=origin)
            was_new = True

        # Record which character was active at commit time
        if active_char and fp in self.motifs:
            m = self.motifs[fp]
            m.char_counts[active_char] = m.char_counts.get(active_char, 0) + 1

        # Successor linkage: previous motif -> this motif
        if self._last_committed_fp and self._last_committed_fp in self.motifs:
            prev = self.motifs[self._last_committed_fp]
            prev.successors[fp] = prev.successors.get(fp, 0) + 1

        self._last_committed_fp = fp
        return (fp, was_new)

    def recall(self, current: Tuple[int, ...]) -> Tuple[Optional[str], int, int]:
        """Topology-first recall: chi filters, geometry ranks.

        Only motifs sharing the query's chi are real candidates.
        Geometry ranks within that pool. Weight breaks ties toward
        established motifs (but capped at 99 so a 12,000-weight
        motif can't dominate purely by mass).

        If the chi class is empty (novel topology), fall back to
        global geometric recall — honestly low-confidence.

        Returns (fingerprint, match_score, weight).
        """
        if not self.motifs:
            return (None, 0, 0)

        qchi = compute_chi(current)

        # Chi-first: filter to topologically compatible motifs
        pool = [m for m in self.motifs.values() if m.chi == qchi]
        if not pool:
            pool = list(self.motifs.values())  # novel topology

        best_fp: Optional[str] = None
        best_score = -1
        best_weight = 0

        for m in pool:
            score = sum(1 for a, b in zip(current, m.state)
                        if a == b and a != 0)
            # Weight breaks ties, capped so mass can't dominate
            combined = score * 100 + min(m.weight, 99)
            if combined > best_score:
                best_fp = m.fingerprint
                best_score = combined
                best_weight = m.weight

        # Return the geometric score (not the combined), for threshold checks
        geo_score = best_score // 100 if best_score >= 0 else 0
        return (best_fp, geo_score, best_weight)

    def successor_of(self, fp: str) -> Optional[str]:
        """Return the most common successor fingerprint of a motif."""
        if fp not in self.motifs:
            return None
        succs = self.motifs[fp].successors
        if not succs:
            return None
        return max(succs, key=succs.get)

    def most_common_char(self, fp: str) -> Optional[str]:
        """Return the most common character associated with a motif."""
        if fp not in self.motifs:
            return None
        cc = self.motifs[fp].char_counts
        if not cc:
            return None
        return max(cc, key=cc.get)

    def decay(self, rate: int = DECAY_RATE) -> int:
        """Age all motifs. Cull those with zero weight and age > 8.
        Returns number culled."""
        dead = []
        for fp, m in self.motifs.items():
            m.weight = max(m.weight - rate, 0)
            m.age += 1
            if m.weight <= 0 and m.age > 8:
                dead.append(fp)
        for fp in dead:
            del self.motifs[fp]
        return len(dead)

    def size(self) -> int:
        return len(self.motifs)

    def all_fingerprints(self) -> List[str]:
        return list(self.motifs.keys())

    def get_motif(self, fp: str) -> Optional[Motif]:
        return self.motifs.get(fp)
