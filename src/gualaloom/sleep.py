"""
Sleep and dream cycles.

Sleep (consolidation): accelerated decay, co-resonance reinforcement,
locality folding, motif merging.

Dream (horizon projection): free-settle from random committed motifs,
walk the manifold, record novel motifs as dream events.
"""

import random
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from .substrate import settle_field, l6_freedom, TRITS_PER_STRAND
from .krimelack import Krimelack, fingerprint


# --- Sleep parameters ---
SLEEP_DECAY_MULTIPLIER = 1
MERGE_HAMMING_THRESHOLD = 2   # max trit differences for merge candidates
CO_RESONANCE_THRESHOLD = 5    # min shared successors for reinforcement/merge

# --- Dream parameters ---
DREAM_CYCLES_DEFAULT = 50


def _hamming(a: Tuple[int, ...], b: Tuple[int, ...]) -> int:
    """Count positions where trits differ (ignoring null-vs-null)."""
    return sum(1 for x, y in zip(a, b) if x != y)


def _co_resonance(k: Krimelack, fp_a: str, fp_b: str) -> int:
    """Count shared successors between two motifs."""
    ma = k.get_motif(fp_a)
    mb = k.get_motif(fp_b)
    if ma is None or mb is None:
        return 0
    shared = set(ma.successors.keys()) & set(mb.successors.keys())
    return len(shared)


def sleep_cycle(k: Krimelack, cycles: int = 200) -> Dict:
    """Run consolidation. Returns stats."""
    total_culled = 0
    total_reinforced = 0
    total_merged = 0
    total_folds = 0

    for cycle_i in range(cycles):
        # 1. Decay — runs every 10th cycle, not every cycle.
        # This prevents over-culling while still clearing noise.
        culled = 0
        if cycle_i % 20 == 0:
            culled = k.decay(rate=SLEEP_DECAY_MULTIPLIER)
        total_culled += culled

        # 2. Co-resonance reinforcement + locality folding
        fps = k.all_fingerprints()
        for i, fp_a in enumerate(fps):
            for fp_b in fps[i+1:]:
                cr = _co_resonance(k, fp_a, fp_b)
                if cr >= CO_RESONANCE_THRESHOLD:
                    ma = k.get_motif(fp_a)
                    mb = k.get_motif(fp_b)
                    if ma and mb:
                        ma.weight += 1
                        mb.weight += 1
                        total_reinforced += 2
                        # Locality fold: cross-link as successors
                        ma.successors[fp_b] = ma.successors.get(fp_b, 0) + 1
                        mb.successors[fp_a] = mb.successors.get(fp_a, 0) + 1
                        total_folds += 1

        # 3. Merge near-duplicate motifs — only when states are
        # extremely close AND they share significant successor overlap.
        # WC_REVIEW: merging is conservative for now because trit density
        # is low (most positions null), making hamming distances small.
        # May need revisiting with hierarchical loom states.
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
                # Require very close states AND strong co-resonance
                if (_hamming(ma.state, mb.state) <= MERGE_HAMMING_THRESHOLD
                        and _co_resonance(k, fp_a, fp_b) >= CO_RESONANCE_THRESHOLD):
                    # Merge B into A
                    ma.weight += mb.weight
                    for sfp, cnt in mb.successors.items():
                        ma.successors[sfp] = ma.successors.get(sfp, 0) + cnt
                    for ch, cnt in mb.char_counts.items():
                        ma.char_counts[ch] = ma.char_counts.get(ch, 0) + cnt
                    del k.motifs[fp_b]
                    merged_this_cycle.add(fp_b)
                    total_merged += 1

        # Early termination: fixed point
        if culled == 0 and total_merged == 0 and total_reinforced == 0:
            break

    return {
        "cycles_run": cycles,
        "decay_culled": total_culled,
        "reinforcements": total_reinforced,
        "merges": total_merged,
        "locality_folds": total_folds,
    }


def dream_cycle(k: Krimelack,
                cycles: int = DREAM_CYCLES_DEFAULT) -> Dict:
    """Free-settle from random motifs (horizon projection).

    Walk the motif manifold: pick a motif, free-settle its state
    (no external input, just internal coupling), check if the result
    matches or is novel.

    Returns dream event data for persistence.
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

    for _ in range(cycles):
        if current_motif is None:
            break

        state = current_motif.state
        # Break state into strands for free-settling, with
        # random perturbation (dream noise). Flip 1-2 random trit
        # positions to allow novel states to emerge.
        perturbed = list(state)
        n_flips = random.randint(1, 2)
        for _ in range(n_flips):
            pos = random.randint(0, len(perturbed) - 1)
            perturbed[pos] = random.choice([-1, 0, 1])
        perturbed = tuple(perturbed)

        n_strands = max(len(perturbed) // TRITS_PER_STRAND, 1)
        strands = []
        for s in range(n_strands):
            start = s * TRITS_PER_STRAND
            end = start + TRITS_PER_STRAND
            strands.append(tuple(perturbed[start:end]))

        # Free-settle with zero familiarity (no external barrier)
        settled = settle_field(strands, familiarity=0)

        if all(t == 0 for t in settled):
            # Nothing settled — pick a new random starting point
            current_fp = random.choice(fps)
            current_motif = k.get_motif(current_fp)
            continue

        # Check if this settled state matches an existing motif
        match_fp, score, weight = k.recall(settled)
        fp = fingerprint(settled)

        if fp in k.motifs:
            # Reinforcement — "remembering" during sleep
            k.motifs[fp].weight += 1
            reinforcements += 1
            current_fp = fp
            current_motif = k.get_motif(fp)
        else:
            # Novel dream motif — commit with dream origin
            committed_fp, _ = k.commit(settled, origin="dream")
            dream_motifs.append({
                "fingerprint": committed_fp,
                "state": list(settled),
            })
            current_fp = committed_fp
            current_motif = k.get_motif(committed_fp)

        # Also try walking via successor
        succ = k.successor_of(current_fp) if current_fp else None
        if succ and k.get_motif(succ):
            current_fp = succ
            current_motif = k.get_motif(succ)

    ended = datetime.now(timezone.utc).isoformat()
    return {
        "started": started,
        "ended": ended,
        "trigger": "dream",
        "cycles_run": cycles,
        "dream_motifs": dream_motifs,
        "reinforcements": reinforcements,
    }
