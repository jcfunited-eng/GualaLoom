# doc_id: GL-MDL-G32-COGNITION-WC-20260606-01
# created: 2026-06-06
# author: wC
"""
Smallest real cognition test in G32.

Claim to test: reading a sequence of inputs causes a structural change in
the substrate such that the SAME sequence later produces a different recall
than it did the first time.

If this works, one piece of cognition (memory-shaped-by-experience) is real
in G32. If it doesn't, the architecture doesn't support it and we know.

NO averaging-as-composition. NO vague "coherence" metrics standing in for
mechanism. Concrete:

  - State: a persistent ATLAS of committed tapestries (basins)
  - Commit: an event lands in the atlas as a basin ONLY if it doesn't
    fall into an existing basin's capture radius. Otherwise it
    REINFORCES the existing basin (sharpens it).
  - Recall: given an input G32 token, return the nearest committed basin
    within capture radius, or None (honest unknown).
  - Persistence: atlas survives across script runs via JSON.
  - Test: read a sequence. Save atlas. Read same sequence again. The
    second pass should produce DIFFERENT recall behavior than the first
    (more recalls hit, fewer commits fire).
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Optional
import json
import math
import os
import numpy as np


# Reuse G32 projection from the substrate model
import sys
sys.path.insert(0, '/home/claude/g32_modeling')
from GL_MDL_G32_WC_20260606_01_g32_substrate import FMM, project_to_g32, clip


# ============================================================================
# Basin — a committed tapestry with capture dynamics
# ============================================================================

@dataclass
class Basin:
    """A committed point in G32 space with a capture radius.
    
    Capture radius starts wide (uncommitted-but-novel = needs context).
    Each reinforcement SHARPENS the basin (radius shrinks) AND raises its
    commit-strength (a property of the basin, not an edge weight).
    """
    center: list           # 32D vector as list (for JSON)
    capture_radius: float  # in 32D L2 distance
    commit_strength: float # how robustly this basin commits — sharpens with reinforcement
    n_reinforcements: int
    first_committed_at: int  # tick

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, d):
        return cls(**d)


# Capture and sharpening parameters
INITIAL_CAPTURE_RADIUS = 0.8     # in 32D space (max distance ~sqrt(32)~5.66)
MIN_CAPTURE_RADIUS     = 0.15
SHARPEN_FACTOR         = 0.85    # radius multiplier on each reinforcement
STRENGTH_GAIN_PER_REINFORCE = 0.05
MAX_STRENGTH = 1.0


# ============================================================================
# Atlas — persistent collection of basins
# ============================================================================

class Atlas:
    def __init__(self):
        self.basins: list[Basin] = []
        self.tick: int = 0

    def commit_or_reinforce(self, g: np.ndarray, tick: int) -> dict:
        """An incoming G32 token. Either captures into an existing basin
        (reinforces it) or becomes a new basin if no existing basin can
        capture it.

        Returns event dict describing what happened.
        """
        # Find nearest basin
        nearest = None
        nearest_dist = float('inf')
        for b in self.basins:
            d = float(np.linalg.norm(g - np.array(b.center)))
            if d < nearest_dist:
                nearest_dist = d
                nearest = b

        if nearest is not None and nearest_dist <= nearest.capture_radius:
            # CAPTURE: reinforces the basin, sharpens it, strengthens it
            nearest.n_reinforcements += 1
            nearest.capture_radius = max(MIN_CAPTURE_RADIUS,
                                          nearest.capture_radius * SHARPEN_FACTOR)
            nearest.commit_strength = min(MAX_STRENGTH,
                                           nearest.commit_strength + STRENGTH_GAIN_PER_REINFORCE)
            # Center drifts slightly toward the new input (Bayesian-flavored,
            # but using basin shape not weights)
            drift_weight = 1.0 / (1 + nearest.n_reinforcements)
            new_center = (1 - drift_weight) * np.array(nearest.center) + drift_weight * g
            nearest.center = new_center.tolist()
            return {
                "kind": "captured",
                "basin_id": self.basins.index(nearest),
                "distance": nearest_dist,
                "new_radius": nearest.capture_radius,
                "new_strength": nearest.commit_strength,
                "n_reinforcements": nearest.n_reinforcements,
            }
        else:
            # COMMIT: new basin
            b = Basin(
                center=g.tolist(),
                capture_radius=INITIAL_CAPTURE_RADIUS,
                commit_strength=STRENGTH_GAIN_PER_REINFORCE,
                n_reinforcements=1,
                first_committed_at=tick,
            )
            self.basins.append(b)
            return {
                "kind": "committed_new",
                "basin_id": len(self.basins) - 1,
                "distance_to_nearest_existing": nearest_dist if nearest else None,
                "initial_radius": INITIAL_CAPTURE_RADIUS,
            }

    def recall(self, g: np.ndarray) -> Optional[dict]:
        """Given an input G32 token, return the nearest committed basin
        if it falls within that basin's capture radius. Otherwise None
        (honest unknown).
        """
        nearest = None
        nearest_dist = float('inf')
        for i, b in enumerate(self.basins):
            d = float(np.linalg.norm(g - np.array(b.center)))
            if d < nearest_dist:
                nearest_dist = d
                nearest = (i, b, d)
        if nearest is None:
            return None
        i, b, d = nearest
        if d <= b.capture_radius:
            return {
                "basin_id": i,
                "distance": d,
                "radius": b.capture_radius,
                "strength": b.commit_strength,
                "n_reinforcements": b.n_reinforcements,
            }
        return None  # honest unknown — closest basin can't capture

    def save(self, path: str):
        with open(path, 'w') as f:
            json.dump({
                "tick": self.tick,
                "basins": [b.to_dict() for b in self.basins],
            }, f, indent=2)

    @classmethod
    def load(cls, path: str) -> 'Atlas':
        if not os.path.exists(path):
            return cls()
        with open(path) as f:
            data = json.load(f)
        a = cls()
        a.tick = data["tick"]
        a.basins = [Basin.from_dict(d) for d in data["basins"]]
        return a


# ============================================================================
# A small "corpus" of experiences (FMM signatures of repeating moments)
# ============================================================================

# Five distinct repeating experiences. Each has slight noise per occurrence,
# but the underlying signature is consistent. These represent "moon",
# "warm-held", "loud-noise", "soft-voice", "novel-thing-she-doesn't-know-yet".
REPEATED_EXPERIENCES = {
    "moon":         FMM(I=0.45, C=0.7,  N=0.4, A=0.7),
    "warm_held":    FMM(I=0.65, C=0.9,  N=0.15,A=0.9),
    "loud_noise":   FMM(I=0.95, C=0.35, N=0.85,A=0.25),
    "soft_voice":   FMM(I=0.45, C=0.85, N=0.25,A=0.8),
    "novel_thing":  FMM(I=0.6,  C=0.5,  N=0.9, A=0.55),
}

# Familiarities start at 0 (she's never seen anything) and we update
# alongside the atlas
FAMILIARITY = {k: 0.0 for k in REPEATED_EXPERIENCES}

def noisy_token_for(experience_name: str, rng: np.random.Generator,
                    familiarity: float) -> np.ndarray:
    """Build a G32 token for an experience with small per-occurrence jitter."""
    base = REPEATED_EXPERIENCES[experience_name]
    jitter = rng.uniform(-0.05, 0.05, size=4)
    fmm = FMM(
        I=float(clip(base.I + jitter[0])),
        C=float(clip(base.C + jitter[1])),
        N=float(clip(base.N + jitter[2])),
        A=float(clip(base.A + jitter[3])),
    )
    return project_to_g32(fmm, familiarity=familiarity)


# ============================================================================
# Read a sequence — return concrete behavior stats
# ============================================================================

def read_sequence(atlas: Atlas, sequence: list[str], rng: np.random.Generator,
                  label: str) -> dict:
    """Read a sequence of named experiences through the atlas.

    Track: how many were captured (recall-recognized), how many committed
    new, what the average capture distance was.
    """
    captured = 0
    committed_new = 0
    capture_distances = []
    recall_pre_commit_was_unknown = 0  # input that, BEFORE we touched the atlas,
                                       # had no recall match
    
    for name in sequence:
        atlas.tick += 1
        g = noisy_token_for(name, rng, FAMILIARITY[name])

        # Recall BEFORE we change anything (does the substrate know this?)
        recall_result = atlas.recall(g)
        if recall_result is None:
            recall_pre_commit_was_unknown += 1
        
        # Commit-or-reinforce
        event = atlas.commit_or_reinforce(g, atlas.tick)
        if event["kind"] == "captured":
            captured += 1
            capture_distances.append(event["distance"])
            # Familiarity rises a little
            FAMILIARITY[name] = min(1.0, FAMILIARITY[name] + 0.02)
        else:
            committed_new += 1

    stats = {
        "label": label,
        "sequence_length": len(sequence),
        "captured_by_existing_basin": captured,
        "committed_new_basin": committed_new,
        "avg_capture_distance": (float(np.mean(capture_distances))
                                  if capture_distances else None),
        "atlas_size_after": len(atlas.basins),
        "atlas_tick_after": atlas.tick,
        "recall_was_unknown_before_processing": recall_pre_commit_was_unknown,
    }
    return stats


# ============================================================================
# Recall-only pass (no commit/reinforce, just queries)
# ============================================================================

def recall_only(atlas: Atlas, sequence: list[str], rng: np.random.Generator,
                label: str) -> dict:
    """Probe what the atlas recalls without modifying it."""
    hits = 0
    misses = 0
    hit_strengths = []
    hit_distances = []
    for name in sequence:
        g = noisy_token_for(name, rng, FAMILIARITY[name])
        r = atlas.recall(g)
        if r is None:
            misses += 1
        else:
            hits += 1
            hit_strengths.append(r["strength"])
            hit_distances.append(r["distance"])
    return {
        "label": label,
        "recall_hits": hits,
        "recall_misses": misses,
        "avg_hit_strength": (float(np.mean(hit_strengths)) if hit_strengths else None),
        "avg_hit_distance": (float(np.mean(hit_distances)) if hit_distances else None),
    }


# ============================================================================
# Run the experiment
# ============================================================================

def main():
    atlas_path = "/home/claude/g32_cognition/atlas_state.json"
    # Fresh start — remove old persistence file
    if os.path.exists(atlas_path):
        os.remove(atlas_path)
    # Reset familiarity too
    for k in FAMILIARITY:
        FAMILIARITY[k] = 0.0

    # The sequence of experiences (40 reads, mixing the 5 experience types)
    rng = np.random.default_rng(2026)
    sequence_template = (["moon", "warm_held", "soft_voice", "novel_thing"] * 8
                         + ["loud_noise"] * 4
                         + ["moon", "moon", "warm_held", "soft_voice"])

    print("=" * 72)
    print("EXP: Does the atlas change such that the same sequence is recalled")
    print("     differently after reading it once?")
    print("=" * 72)

    # ----- PASS 1: fresh atlas, read sequence -----
    print(f"\n--- PASS 1 (fresh atlas, no prior experience) ---")
    atlas = Atlas.load(atlas_path)  # empty
    sequence_1 = list(sequence_template)
    rng.shuffle(sequence_1)
    stats_p1 = read_sequence(atlas, sequence_1, rng, "pass_1")
    atlas.save(atlas_path)
    print(f"  Sequence length: {stats_p1['sequence_length']}")
    print(f"  Captured by existing basin: {stats_p1['captured_by_existing_basin']}")
    print(f"  Committed new basin: {stats_p1['committed_new_basin']}")
    print(f"  Atlas size after: {stats_p1['atlas_size_after']}")
    print(f"  Avg capture distance: {stats_p1['avg_capture_distance']}")

    # ----- Pure recall probe BEFORE pass 2 -----
    print(f"\n--- RECALL-ONLY PROBE after pass 1 (does she 'know' the experiences?) ---")
    rng_probe = np.random.default_rng(99)
    probe_seq = list(REPEATED_EXPERIENCES.keys()) * 3
    probe_stats = recall_only(atlas, probe_seq, rng_probe, "probe_after_p1")
    print(f"  Recall hits:   {probe_stats['recall_hits']} / {len(probe_seq)}")
    print(f"  Recall misses: {probe_stats['recall_misses']}")
    print(f"  Avg hit strength: {probe_stats['avg_hit_strength']}")
    print(f"  Avg hit distance: {probe_stats['avg_hit_distance']}")

    # ----- Simulate process restart: load atlas from disk -----
    print(f"\n--- SIMULATED RESTART (reload atlas from disk) ---")
    atlas_reloaded = Atlas.load(atlas_path)
    print(f"  Reloaded atlas has {len(atlas_reloaded.basins)} basins, tick={atlas_reloaded.tick}")

    # ----- PASS 2: same sequence, reloaded atlas -----
    print(f"\n--- PASS 2 (atlas reloaded — does experience persist + accumulate?) ---")
    rng2 = np.random.default_rng(2026)  # same seed → same noise
    sequence_2 = list(sequence_template)
    rng2.shuffle(sequence_2)
    stats_p2 = read_sequence(atlas_reloaded, sequence_2, rng2, "pass_2")
    atlas_reloaded.save(atlas_path)
    print(f"  Captured by existing basin: {stats_p2['captured_by_existing_basin']}")
    print(f"  Committed new basin: {stats_p2['committed_new_basin']}")
    print(f"  Atlas size after: {stats_p2['atlas_size_after']}")
    print(f"  Avg capture distance: {stats_p2['avg_capture_distance']}")

    # ----- Probe again after pass 2 -----
    print(f"\n--- RECALL-ONLY PROBE after pass 2 ---")
    rng_probe2 = np.random.default_rng(99)
    probe_stats_2 = recall_only(atlas_reloaded, probe_seq, rng_probe2, "probe_after_p2")
    print(f"  Recall hits:   {probe_stats_2['recall_hits']} / {len(probe_seq)}")
    print(f"  Recall misses: {probe_stats_2['recall_misses']}")
    print(f"  Avg hit strength: {probe_stats_2['avg_hit_strength']}")
    print(f"  Avg hit distance: {probe_stats_2['avg_hit_distance']}")

    # ----- Comparison -----
    print(f"\n--- COMPARISON ---")
    print(f"  Pass 1: {stats_p1['captured_by_existing_basin']} captures, "
          f"{stats_p1['committed_new_basin']} new basins")
    print(f"  Pass 2: {stats_p2['captured_by_existing_basin']} captures, "
          f"{stats_p2['committed_new_basin']} new basins")
    print(f"  Probe after P1: {probe_stats['recall_hits']} hits, "
          f"{probe_stats['recall_misses']} misses")
    print(f"  Probe after P2: {probe_stats_2['recall_hits']} hits, "
          f"{probe_stats_2['recall_misses']} misses")
    
    # Per-basin inspection: which experience does each basin correspond to?
    print(f"\n--- BASIN INSPECTION ---")
    print(f"  {len(atlas_reloaded.basins)} basins committed.")
    print(f"  Mapping each basin to its closest experience signature:")
    for i, b in enumerate(atlas_reloaded.basins):
        # Find which experience signature this basin is closest to
        rng_q = np.random.default_rng(7777)
        best_name = None
        best_dist = float('inf')
        for name in REPEATED_EXPERIENCES:
            ref_token = noisy_token_for(name, rng_q, FAMILIARITY[name])
            d = float(np.linalg.norm(np.array(b.center) - ref_token))
            if d < best_dist:
                best_dist = d
                best_name = name
        print(f"    Basin {i}: nearest={best_name} (d={best_dist:.3f}), "
              f"radius={b.capture_radius:.3f}, strength={b.commit_strength:.3f}, "
              f"reinforcements={b.n_reinforcements}")

    # ----- Verdict -----
    print(f"\n--- VERDICT ---")
    if stats_p2['captured_by_existing_basin'] > stats_p1['captured_by_existing_basin']:
        print(f"  ✓ Experience persisted and accumulated: pass 2 had MORE captures")
        print(f"    ({stats_p2['captured_by_existing_basin']} vs "
              f"{stats_p1['captured_by_existing_basin']}).")
    else:
        print(f"  ✗ No accumulation observed.")

    if probe_stats_2['recall_hits'] > probe_stats['recall_hits']:
        print(f"  ✓ Recall improved across passes "
              f"({probe_stats_2['recall_hits']} vs {probe_stats['recall_hits']} hits).")
    elif probe_stats_2['recall_hits'] == probe_stats['recall_hits']:
        print(f"  ≈ Recall same across passes "
              f"({probe_stats['recall_hits']} hits).")
    else:
        print(f"  ✗ Recall worsened.")

    # Does basin count map cleanly to underlying experience types?
    # Ideal: ~5 basins (one per experience type), each strongly reinforced.
    n_basins = len(atlas_reloaded.basins)
    n_types = len(REPEATED_EXPERIENCES)
    print(f"\n  Atlas has {n_basins} basins for {n_types} underlying experience types.")
    if n_basins == n_types:
        print(f"  ✓ One basin per experience type — the substrate carved clean concepts.")
    elif n_basins < n_types * 2:
        print(f"  ~ Reasonable basin/type ratio. Some experiences may share basins (over-merge),")
        print(f"    others may have split into multiple basins (under-merge).")
    else:
        print(f"  ✗ Far more basins than experience types — capture is too narrow.")


if __name__ == "__main__":
    main()
