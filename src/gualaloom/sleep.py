"""
Sleep and dream cycles.

Sleep (consolidation): weight rebalancing (compress over-dominant motifs),
gentle decay, co-resonance reinforcement, locality folding, motif merging.

The key fix: a motif with weight 12,000 while everything else is single
digits is pathological — sleep compresses that. Without weight rebalancing,
the dominant attractor absorbs every query and generation can't escape it.

Dream (horizon projection): free-settle from random committed motifs,
walk the manifold, record novel motifs as dream events.
"""

import math
import random
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from .substrate import settle_field, l6_freedom, TRITS_PER_STRAND
from .krimelack import Krimelack, fingerprint


# --- Sleep parameters ---
WEIGHT_CAP = 500              # max weight any single motif can hold
MERGE_HAMMING_THRESHOLD = 2
CO_RESONANCE_THRESHOLD = 5

# --- Dream parameters ---
DREAM_CYCLES_DEFAULT = 50


def _hamming(a: Tuple[int, ...], b: Tuple[int, ...]) -> int:
    return sum(1 for x, y in zip(a, b) if x != y)


def _co_resonance(k: Krimelack, fp_a: str, fp_b: str) -> int:
    ma = k.get_motif(fp_a)
    mb = k.get_motif(fp_b)
    if ma is None or mb is None:
        return 0
    shared = set(ma.successors.keys()) & set(mb.successors.keys())
    return len(shared)


def sleep_cycle(k: Krimelack, cycles: int = 200) -> Dict:
    """Consolidation. Matches wC's v1 design:
    one gentle decay pass, weight rebalancing, then cull the truly stale.

    The weight rebalancing is the critical fix: log-compress any motif
    whose weight exceeds the cap. A motif at 12,000 becomes ~log(12000)
    scaled to the cap. This breaks the black hole without destroying the
    relative ordering — heavy motifs stay heavier, but not by 1000x.
    """
    total_culled = 0
    total_compressed = 0
    total_reinforced = 0
    total_merged = 0

    # ── Phase 1: Weight rebalancing (the attractor fix) ──────
    # Log-compress any motif above the cap. This runs ONCE per sleep,
    # not per cycle — it's a rebalancing step, not iterative decay.
    for fp, m in k.motifs.items():
        if m.weight > WEIGHT_CAP:
            # Log-compress: weight → cap + log2(excess). A 12,000-weight
            # motif becomes ~514 (500 + log2(24) ≈ 500 + 4.6). This
            # preserves ordering but crushes the black hole.
            excess = m.weight / WEIGHT_CAP
            m.weight = WEIGHT_CAP + int(math.log2(max(excess, 1)))
            total_compressed += 1

    # ── Phase 2: Age everyone, gentle decay ──────────────────
    # One decay pass per sleep (not N rounds). Matches wC's v1:
    # "one night = one forgetting increment, not N rounds."
    for fp in list(k.motifs.keys()):
        m = k.motifs[fp]
        m.age += max(cycles // 50, 1)
        m.weight -= 1

    # ── Phase 3: Cull the truly stale ────────────────────────
    for fp in list(k.motifs.keys()):
        m = k.motifs[fp]
        if m.weight <= 0 and m.age > 8:
            del k.motifs[fp]
            total_culled += 1
        else:
            # Floor at 1 — a learned motif doesn't vanish, it quiets
            m.weight = max(m.weight, 1)

    # ── Phase 4: Co-resonance reinforcement (one pass only) ──
    # One pass, and only reinforce motifs below the cap — prevents
    # reinforcement from rebuilding the attractor we just compressed.
    fps = k.all_fingerprints()
    for i, fp_a in enumerate(fps):
        for fp_b in fps[i+1:]:
            cr = _co_resonance(k, fp_a, fp_b)
            if cr >= CO_RESONANCE_THRESHOLD:
                ma = k.get_motif(fp_a)
                mb = k.get_motif(fp_b)
                if ma and mb and ma.weight < WEIGHT_CAP and mb.weight < WEIGHT_CAP:
                    ma.weight += 1
                    mb.weight += 1
                    total_reinforced += 2
                    ma.successors[fp_b] = ma.successors.get(fp_b, 0) + 1
                    mb.successors[fp_a] = mb.successors.get(fp_a, 0) + 1

    # ── Phase 5: Merge near-duplicates ───────────────────────
    fps = k.all_fingerprints()
    merged_this_cycle = set()
    for i, fp_a in enumerate(fps):
        if fp_a in merged_this_cycle:
            continue
        ma = k.get_motif(fp_a)
        if ma is None:
            continue
        for fp_b in fps[i+1:]:
            if fp_b in merged_this_cycle:
                continue
            mb = k.get_motif(fp_b)
            if mb is None:
                continue
            if (_hamming(ma.state, mb.state) <= MERGE_HAMMING_THRESHOLD
                    and _co_resonance(k, fp_a, fp_b) >= CO_RESONANCE_THRESHOLD):
                ma.weight += mb.weight
                for sfp, cnt in mb.successors.items():
                    ma.successors[sfp] = ma.successors.get(sfp, 0) + cnt
                for ch, cnt in getattr(mb, 'char_counts', {}).items():
                    ma.char_counts[ch] = ma.char_counts.get(ch, 0) + cnt
                del k.motifs[fp_b]
                merged_this_cycle.add(fp_b)
                total_merged += 1

    return {
        "cycles_run": cycles,
        "weight_compressed": total_compressed,
        "decay_culled": total_culled,
        "reinforcements": total_reinforced,
        "merges": total_merged,
    }


def dream_cycle(k: Krimelack,
                cycles: int = DREAM_CYCLES_DEFAULT) -> Dict:
    """Free-settle from random motifs (horizon projection).

    Walk the motif manifold: pick a motif, free-settle its state
    (no external input, just internal coupling), check if the result
    matches or is novel.
    """
    started = datetime.now(timezone.utc).isoformat()
    dream_motifs: List[Dict] = []
    reinforcements = 0

    fps = k.all_fingerprints()
    if not fps:
        return {
            "started": started,
            "ended": datetime.now(timezone.utc).isoformat(),
            "trigger": "dream",
            "cycles_run": 0,
            "dream_motifs": [],
            "reinforcements": 0,
        }

    # Start from a random motif
    current_fp = random.choice(fps)
    current_motif = k.get_motif(current_fp)

    for i in range(cycles):
        if current_motif is None:
            break

        state = current_motif.state
        # Dream noise: flip 1-2 random trit positions
        perturbed = list(state)
        for _ in range(random.randint(1, 2)):
            pos = random.randint(0, len(perturbed) - 1)
            perturbed[pos] = random.choice([-1, 0, 1])
        perturbed = tuple(perturbed)

        n_strands = max(len(perturbed) // TRITS_PER_STRAND, 1)
        strands = [tuple(perturbed[s*TRITS_PER_STRAND:(s+1)*TRITS_PER_STRAND])
                   for s in range(n_strands)]

        settled = settle_field(strands, familiarity=0)

        if all(t == 0 for t in settled):
            current_fp = random.choice(fps)
            current_motif = k.get_motif(current_fp)
            continue

        fp = fingerprint(settled)

        if fp in k.motifs:
            k.motifs[fp].weight += 1
            reinforcements += 1
            current_fp = fp
            current_motif = k.get_motif(fp)
        else:
            committed_fp, _ = k.commit(settled, origin="dream")
            dream_motifs.append({
                "fingerprint": committed_fp,
                "state": list(settled),
            })
            current_fp = committed_fp
            current_motif = k.get_motif(committed_fp)

        # Walk via successor, or jump to a different motif
        succ = k.successor_of(current_fp) if current_fp else None
        if succ and k.get_motif(succ):
            current_fp = succ
            current_motif = k.get_motif(succ)
        else:
            # Jump to a different known motif (wC's design: walk the manifold)
            motif_list = list(k.motifs.values())
            current_motif = motif_list[(i + 1) % len(motif_list)]
            current_fp = current_motif.fingerprint

    ended = datetime.now(timezone.utc).isoformat()
    return {
        "started": started,
        "ended": ended,
        "trigger": "dream",
        "cycles_run": cycles,
        "dream_motifs": dream_motifs,
        "reinforcements": reinforcements,
    }
