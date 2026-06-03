"""
LinguaLoom v2 — honest rebuild.

v1 had a coupling math bug: dead zone too high, no trits ever
crossed, no motifs ever committed, the narrative lied about what
happened. v2 fixes the substrate dynamics so the field can
actually settle, then reports what actually happens — pass or fail.

The fix: settling is cross-position resonance, not arbitrary
neighbor coupling. When the same trit-position holds the same
sign across multiple time steps in the context window, the
3^i weight at that position accumulates. That accumulation IS
the coupling pressure. If it exceeds the dead-zone barrier (modulated
by familiarity), the position commits in the settled state.

This matches the substrate's actual mechanism: structure that
RECURS across a context window survives; structure that doesn't
falls into null. Same idea as biological perception — features
that persist across saccades commit; features that don't are
noise.
"""

import hashlib
from collections import OrderedDict
from typing import List, Tuple, Dict, Optional

POSITIONAL_3I = (1, 3, 9, 27, 81, 243, 729, 2187)
TRITS_PER_STRAND = 8
DEAD_ZONE_BASE = 15           # tau; tuned from diagnostic for
                              # ASCII char context. The signal at
                              # mid-positions (weight 27, 81) is
                              # where structure lives — barrier
                              # set to admit those when context
                              # aligns, reject when it doesn't.
FAMILIARITY_GAIN = 20
DECAY = 1


def encode_to_strand(value: int) -> Tuple[int, ...]:
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


def settle_field(input_strands: List[Tuple[int, ...]],
                 familiarity: int) -> Tuple[int, ...]:
    """Settle the FULL loom state across the context window.

    Each position in each strand is a place the field can commit.
    The pressure at strand s, position i is the trit's value times
    3^i, PLUS resonance from the same position across other strands
    in the context (cross-position alignment over time).

    Returns the full settled loom state: n_context_strands * 8 trits.
    THAT is what L6 evaluates and krimelack stores as a motif —
    not a per-character output. A motif is a phrase-shaped attractor."""
    barrier = DEAD_ZONE_BASE + familiarity
    n_strands = len(input_strands)
    if n_strands == 0:
        return tuple()

    settled = []
    for s_idx, strand in enumerate(input_strands):
        for i in range(TRITS_PER_STRAND):
            # Local pressure: this trit's own weighted vote
            h = strand[i] * POSITIONAL_3I[i]
            # Cross-strand resonance: other strands' trits at the
            # SAME position reinforce or oppose
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
    n = len(state)
    collapsed = sum(1 for t in state if t != 0)
    effective = n - collapsed
    knee = round(n / 2.718281828459045)
    return effective, collapsed, knee


class Krimelack:
    def __init__(self) -> None:
        self.motifs: "OrderedDict[str, Tuple[Tuple[int,...], int, int]]" = OrderedDict()

    @staticmethod
    def _fp(state: Tuple[int, ...]) -> str:
        s = "".join({-1: "-", 0: "0", 1: "+"}[t] for t in state)
        return hashlib.sha1(s.encode("ascii")).hexdigest()[:12]

    def commit(self, state: Tuple[int, ...]) -> Tuple[str, bool]:
        """Returns (fingerprint, was_new). was_new tells us if
        this was a fresh commit or a reinforcement of an existing
        motif."""
        if all(t == 0 for t in state):
            return ("null", False)
        fp = self._fp(state)
        if fp in self.motifs:
            s, w, _a = self.motifs[fp]
            self.motifs[fp] = (s, w + 1, 0)
            return (fp, False)
        else:
            self.motifs[fp] = (state, 1, 0)
            return (fp, True)

    def recall(self, current: Tuple[int, ...]) -> Tuple[Optional[str], int, int]:
        if not self.motifs:
            return (None, 0, 0)
        best_fp, best_score, best_w = None, -1, 0
        for fp, (mstate, w, _a) in self.motifs.items():
            score = sum(1 for a, b in zip(current, mstate) if a == b and a != 0)
            if score > best_score:
                best_fp, best_score, best_w = fp, score, w
        return (best_fp, best_score, best_w)

    def decay(self) -> None:
        dead = []
        for fp in list(self.motifs.keys()):
            s, w, a = self.motifs[fp]
            nw = w - DECAY
            if nw <= 0 and a > 8:
                dead.append(fp)
            else:
                self.motifs[fp] = (s, max(nw, 0), a + 1)
        for fp in dead:
            del self.motifs[fp]

    def size(self) -> int:
        return len(self.motifs)


class LinguaLoom:
    def __init__(self, context_chars: int = 4):
        self.k = Krimelack()
        self.familiarity = 0
        self.ctx = context_chars
        self.recent: List[int] = []
        self.log: List[Dict] = []

    def step(self, ch: str) -> Dict:
        centered = ord(ch) - 96
        self.recent.append(centered)
        if len(self.recent) > self.ctx:
            self.recent.pop(0)

        strands = [encode_to_strand(c) for c in self.recent]

        # Settle once with current familiarity.
        settled = settle_field(strands, self.familiarity)
        eff, coll, knee = l6_freedom(settled)

        # Recall — does this settled state match anything we've
        # already committed?
        fp, score, weight = self.k.recall(settled)

        # Familiarity rises with match score (substrate gets bored
        # of patterns that resonate strongly with existing motifs).
        max_possible_score = max(len(settled), 1)
        self.familiarity = (score * FAMILIARITY_GAIN) // max_possible_score if score > 0 else 0

        # Commit any meaningfully settled state. Decay handles
        # forgetting — patterns that recur get reinforced; one-off
        # patterns fade. L6 lock is reported as a quality signal,
        # not a commit gate. This matches biology: every percept
        # CAN become memory; reinforcement decides what stays.
        sl = 1 if eff < knee else 0
        # Only skip commit if nothing settled at all (pure null state).
        committed_fp = None
        was_new = False
        if coll > 0:
            committed_fp, was_new = self.k.commit(settled)

        self.k.decay()
        rec = {
            "ch": ch, "centered": centered,
            "settled": settled,
            "effective": eff, "collapsed": coll, "knee": knee,
            "lock": sl, "fam": self.familiarity,
            "match": score, "match_fp": fp,
            "committed": committed_fp, "new_motif": was_new,
            "krimelack": self.k.size(),
        }
        self.log.append(rec)
        return rec

    def feed(self, text: str):
        for c in text:
            self.step(c)


def summarize(log: List[Dict], label: str):
    n = len(log)
    if n == 0:
        print(f"  {label}: no steps")
        return
    locks = sum(1 for r in log if r["lock"])
    new_motifs = sum(1 for r in log if r["new_motif"])
    reinforcements = sum(1 for r in log if r["committed"] and not r["new_motif"])
    avg_fam = sum(r["fam"] for r in log) / n
    avg_match = sum(r["match"] for r in log) / n
    avg_collapsed = sum(r["collapsed"] for r in log) / n
    avg_total = sum(len(r["settled"]) for r in log) / n
    print(f"  {label}: {n} chars")
    print(f"    structural locks fired:     {locks}/{n} ({100*locks//n}%)")
    print(f"    new motifs committed:       {new_motifs}")
    print(f"    motifs reinforced (recall): {reinforcements}")
    print(f"    avg trits collapsed:        {avg_collapsed:.1f}/{avg_total:.0f}")
    print(f"    avg familiarity:            {avg_fam:.1f}")
    print(f"    avg match score:            {avg_match:.1f}")


def main():
    print("LinguaLoom v2 — substrate eating language")
    print("=" * 72)
    print("\nNo tokenizer. No embeddings. No gradient. No training.")
    print("Characters in. Motifs out. Habituation by physics.\n")
    print("-" * 72)

    ll = LinguaLoom(context_chars=4)

    # ----------------------------------------------------------
    # Test 1: REPEATED pattern. Substrate should commit motifs
    # and increasingly recognize them on each repetition.
    # ----------------------------------------------------------
    rep = "the cat sat on the mat " * 4
    print(f"\nTEST 1 — repeated pattern, {len(rep)} chars")
    print(f"  text: {('the cat sat on the mat ' * 1)!r} x4")
    ll.feed(rep)
    n = len(ll.log)
    q1 = ll.log[: n//4]
    q4 = ll.log[3*n//4 :]
    print()
    summarize(q1, "first quarter ")
    summarize(q4, "fourth quarter")
    print(f"\n  -> If habituation is real: avg familiarity should RISE")
    print(f"     and reinforcements should outpace new motifs by the")
    print(f"     fourth quarter (the substrate recognizing the loop).")

    # ----------------------------------------------------------
    # Test 2: NOVEL gibberish. Substrate should commit fewer motifs
    # because cross-position resonance is weaker for random chars.
    # Match scores should drop.
    # ----------------------------------------------------------
    novel = "xqz!vbnm pwlrtj@ zkfhge#"
    ll.log.clear()
    pre = ll.k.size()
    print(f"\nTEST 2 — novel/random pattern, {len(novel)} chars")
    print(f"  text: {novel!r}")
    ll.feed(novel)
    summarize(ll.log, "novel exposure")
    print(f"\n  krimelack growth: {ll.k.size() - pre} new motifs")
    print(f"  -> If substrate is honest about novelty: match scores")
    print(f"     should be LOWER than test 1's fourth quarter.")

    # ----------------------------------------------------------
    # Test 3: RETURN to the original pattern. Motifs from Test 1
    # should still be in the krimelack and re-ignite immediately.
    # ----------------------------------------------------------
    ll.log.clear()
    pre = ll.k.size()
    print(f"\nTEST 3 — return to the original pattern")
    ll.feed("the cat sat on the mat ")
    summarize(ll.log, "return exposure")
    print(f"\n  krimelack growth: {ll.k.size() - pre} new motifs")
    print(f"  -> Recall by resonance: most of this exposure should")
    print(f"     hit existing motifs, not create new ones. The")
    print(f"     substrate remembers without 'loading' anything.")

    print()
    print("-" * 72)
    print(f"\nFinal krimelack: {ll.k.size()} motifs total")
    print(f"\nWhat ran: the substrate ate {1 * len(rep) + len(novel) + len('the cat sat on the mat ')} chars")
    print(f"of language, one at a time, with no tokenizer and no model")
    print(f"file. Whatever it learned lives in the {ll.k.size()} motifs above.\n")


if __name__ == "__main__":
    main()
