# doc_id: GL-MDL-SYNTHESIS-WC-20260606-01
# created: 2026-06-06
# author: wC
"""
Synthesis: G32 + chi-address + FMM-cluster dynamics.

Architecture:
  - Sections (subject, verb, object, listen, ...) each hold a CLUSTER of motifs.
  - A motif is a fractal gate with angle θ set at commit-time from the G32 of
    the founding event.
  - An event at time t: krimelack → FMM(I,C,N,A) → G32 token.
  - Each motif's "fire score" = alignment(g_token, motif.angle_signature)
  - Top-firing motifs in each section are the active motifs at t.
  - Co-firing motifs (across sections) get bound at a chi-position.
  - Chi-positions are integer addresses; chi-band locality of ±2 means
    a binding at chi=K reinforces chi-positions K-2..K+2 with falloff.
  - Cluster dynamics: the firing motifs' interpretive state evolves via
    FMM coupling — no learning rule, only geometric evolution.
  - Stored at each (chi-pos, motif_id) binding: list of G32 tokens that
    co-fired here, a strength scalar that tracks "how reliably this binds."

Recall:
  - Input event → fires motifs → for each fired motif, fetch chi-neighborhood
    of bindings → cohesion cascade across bound motifs' G32 tokens →
    surface the strongest motif in each section as the recall content.

Test:
  1. Read variants of 5 repeated experiences (same as basin experiment)
  2. Verify: same experience clusters at SAME chi-address, not fragmented
  3. Recall by input similarity returns correct experience signature
  4. Persistence across reload works
  5. (Stretch) Read a tiny Guala-style dialog and observe basic binding
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from collections import defaultdict
from typing import Optional
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, '/home/claude/g32_modeling')
from GL_MDL_G32_WC_20260606_01_g32_substrate import FMM, project_to_g32, clip


# ============================================================================
# Constants
# ============================================================================

CHI_BAND_RADIUS = 2          # locality of reinforcement
COFIRE_THRESHOLD = 0.55      # motif fires if alignment >= this
ALIGNMENT_TOP_K = 2          # how many top motifs per section can fire at once
STRENGTH_GAIN_PER_BINDING = 0.08
DECAY_PER_TICK = 0.0008      # gentle decay of unused bindings
FORGETTING_THRESHOLD = 0.05
COMMIT_NOVELTY_THRESHOLD = 0.5  # how novel an event has to be to commit a NEW motif

# FMM cluster coupling
COUPLING_STRENGTH = 0.15     # α — how much other gates' state affects mine
GATE_INERTIA = 0.6           # how much of prior state persists


# ============================================================================
# Motif (= fractal gate with angle)
# ============================================================================

@dataclass
class Motif:
    """A gate in a section's cluster. Has an interpretive angle, set at commit
    time from the founding G32 token. Fires when inputs align with that angle.
    The cluster state evolves but the angle is fixed (committed identity)."""
    motif_id: int
    section: str
    angle: list                 # the 32D angle (founding G32 token) — IMMUTABLE
    cluster_state: list         # current dynamic state — evolves via coupling
    n_firings: int = 0
    founded_at_tick: int = 0

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, d):
        return cls(**d)

    def alignment(self, g_token: np.ndarray) -> float:
        """How well does this input token align with this motif's angle?
        Use cosine similarity on the normalized angle/token (treated as vectors
        in [0,1]^32)."""
        a = np.array(self.angle)
        denom = (np.linalg.norm(a) * np.linalg.norm(g_token))
        if denom < 1e-9:
            return 0.0
        return float(np.dot(a, g_token) / denom)


# ============================================================================
# Binding — what's stored at (chi_position, motif_id) in the atlas
# ============================================================================

@dataclass
class Binding:
    chi_position: int
    motif_id: int
    section: str
    strength: float
    n_reinforcements: int
    g_token_centroid: list       # running mean of G32 tokens that co-fired here
    last_tick: int

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, d):
        return cls(**d)


# ============================================================================
# Atlas — sections, motifs, bindings, chi-addressing
# ============================================================================

SECTIONS = ["listen", "subject", "verb", "object", "modifier", "ground", "intro"]


class SynthesisAtlas:
    def __init__(self):
        self.motifs: dict[str, list[Motif]] = {s: [] for s in SECTIONS}
        self.bindings: dict[tuple[int, int], Binding] = {}  # (chi, motif_id) → Binding
        self.next_motif_id = 0
        self.tick = 0
        # Chi-position counter — auto-assigns new chi-positions as needed.
        # In production, chi-position would be determined by motif co-firing
        # context. For this model, we use a deterministic hash of the co-firing
        # set as the chi address.
        self.chi_address_map: dict[frozenset, int] = {}
        self.next_chi = 0

    def _chi_for_cofire_set(self, fired_motif_ids: list[int]) -> int:
        """Determine the chi-position from a set of co-firing motif IDs.
        Same co-firing set → same chi-position (deterministic). This is what
        makes 'similar experiences land at the same address.'"""
        key = frozenset(fired_motif_ids)
        if key not in self.chi_address_map:
            self.chi_address_map[key] = self.next_chi
            self.next_chi += 1
        return self.chi_address_map[key]

    def _fire_motifs_in_section(self, section: str, g_token: np.ndarray,
                                familiarity: float) -> list[int]:
        """Compute which motifs in a section fire for this input.
        Returns list of motif_ids that fired (above threshold)."""
        section_motifs = self.motifs[section]
        if not section_motifs:
            return []
        alignments = [(m.motif_id, m.alignment(g_token)) for m in section_motifs]
        alignments.sort(key=lambda x: x[1], reverse=True)
        # Top-k motifs whose alignment exceeds threshold
        fired = []
        for motif_id, align in alignments[:ALIGNMENT_TOP_K]:
            if align >= COFIRE_THRESHOLD:
                fired.append(motif_id)
        return fired

    def _maybe_commit_new_motif(self, section: str, g_token: np.ndarray,
                                novelty: float, fired_in_section: list[int]) -> Optional[int]:
        """If this event is novel enough AND no motif in this section already
        fires strongly for it, commit a new motif here."""
        if fired_in_section:
            return None  # existing motif handles this input
        if novelty < COMMIT_NOVELTY_THRESHOLD:
            return None  # not novel enough to warrant a new motif
        motif_id = self.next_motif_id
        self.next_motif_id += 1
        motif = Motif(
            motif_id=motif_id,
            section=section,
            angle=g_token.tolist(),
            cluster_state=g_token.tolist(),
            n_firings=1,
            founded_at_tick=self.tick,
        )
        self.motifs[section].append(motif)
        return motif_id

    def _reinforce_or_create_binding(self, chi: int, motif_id: int,
                                     section: str, g_token: np.ndarray):
        """Strengthen the binding at (chi, motif_id), or create if new.
        Also reinforces chi-band neighborhood with falloff."""
        for offset in range(-CHI_BAND_RADIUS, CHI_BAND_RADIUS + 1):
            neighbor_chi = chi + offset
            if neighbor_chi < 0:
                continue
            falloff = 1.0 - (abs(offset) / (CHI_BAND_RADIUS + 1))
            gain = STRENGTH_GAIN_PER_BINDING * falloff
            key = (neighbor_chi, motif_id)
            if key in self.bindings:
                b = self.bindings[key]
                b.strength = min(1.0, b.strength + gain)
                b.n_reinforcements += 1
                # Update G32 centroid (running mean)
                w = 1.0 / b.n_reinforcements
                old = np.array(b.g_token_centroid)
                new = (1 - w) * old + w * g_token
                b.g_token_centroid = new.tolist()
                b.last_tick = self.tick
            elif offset == 0:  # only create on direct hit, not neighborhood
                self.bindings[key] = Binding(
                    chi_position=neighbor_chi,
                    motif_id=motif_id,
                    section=section,
                    strength=gain,
                    n_reinforcements=1,
                    g_token_centroid=g_token.tolist(),
                    last_tick=self.tick,
                )

    def _evolve_cluster_state(self, section: str, fired_motif_ids: list[int],
                              g_token: np.ndarray):
        """FMM cluster dynamics: motifs that fired evolve their state via
        coupling to other firing motifs in the same section."""
        if len(fired_motif_ids) < 1:
            return
        # Compute mean state of firing motifs (proxy for cluster influence)
        firing_motifs = [m for m in self.motifs[section] if m.motif_id in fired_motif_ids]
        if not firing_motifs:
            return
        cluster_mean = np.mean([np.array(m.cluster_state) for m in firing_motifs], axis=0)
        for m in firing_motifs:
            state = np.array(m.cluster_state)
            # s_{t+1} = tanh-like update, but bounded to [0,1]
            # input drive: g_token; other-gate coupling: cluster_mean; inertia: prior state
            new_state = (GATE_INERTIA * state
                         + (1 - GATE_INERTIA) * g_token
                         + COUPLING_STRENGTH * (cluster_mean - state))
            m.cluster_state = clip(new_state).tolist()
            m.n_firings += 1

    def decay(self):
        """Gentle decay of all bindings; prune below threshold."""
        to_prune = []
        for key, b in self.bindings.items():
            b.strength = max(0.0, b.strength - DECAY_PER_TICK)
            if b.strength < FORGETTING_THRESHOLD:
                to_prune.append(key)
        for key in to_prune:
            del self.bindings[key]

    def process_event(self, g_token: np.ndarray, novelty: float,
                      familiarity: float, section_focus: Optional[str] = None) -> dict:
        """Main event-processing pipeline.

        section_focus is an optional hint about which section is being targeted
        (e.g. 'subject' for a name word). If None, fire across all sections."""
        self.tick += 1
        result = {"tick": self.tick, "fired": {}, "committed_new": {}, "bound_at_chi": []}

        # Determine sections to engage
        sections_to_process = [section_focus] if section_focus else SECTIONS

        # Phase 1: Fire motifs in each section
        all_fired = []
        for section in sections_to_process:
            fired = self._fire_motifs_in_section(section, g_token, familiarity)
            # Maybe commit new motif if nothing fired and event is novel
            new_id = self._maybe_commit_new_motif(section, g_token, novelty, fired)
            if new_id is not None:
                fired.append(new_id)
                result["committed_new"][section] = new_id
            result["fired"][section] = fired
            all_fired.extend(fired)

        # Phase 2: Determine chi-position from co-firing set
        if all_fired:
            chi = self._chi_for_cofire_set(all_fired)
            result["bound_at_chi"] = chi
            # Bind each fired motif at this chi-position
            for section in sections_to_process:
                for motif_id in result["fired"][section]:
                    self._reinforce_or_create_binding(chi, motif_id, section, g_token)
            # Phase 3: Cluster dynamics in each section
            for section in sections_to_process:
                self._evolve_cluster_state(section, result["fired"][section], g_token)

        # Phase 4: Decay
        self.decay()
        return result

    def recall(self, g_token: np.ndarray, section_focus: Optional[str] = None) -> dict:
        """Given an input token, fire motifs and surface the cohesion cascade
        across their chi-neighborhood bindings."""
        sections_to_process = [section_focus] if section_focus else SECTIONS
        all_fired = []
        for section in sections_to_process:
            fired = self._fire_motifs_in_section(section, g_token, familiarity=0.5)
            all_fired.extend(fired)

        if not all_fired:
            return {"recall": None, "reason": "no_motifs_fired"}

        chi = self._chi_for_cofire_set(all_fired) if frozenset(all_fired) in self.chi_address_map else None
        if chi is None:
            return {"recall": None, "reason": "novel_cofire_combination", "fired": all_fired}

        # Fetch chi-neighborhood bindings, surface the strongest per section
        recalled_by_section = {s: [] for s in SECTIONS}
        for offset in range(-CHI_BAND_RADIUS, CHI_BAND_RADIUS + 1):
            neighbor_chi = chi + offset
            for (chi_pos, mid), b in self.bindings.items():
                if chi_pos == neighbor_chi:
                    recalled_by_section[b.section].append((b, abs(offset)))

        # Surface strongest per section with chi-distance penalty
        result = {}
        for section, bs in recalled_by_section.items():
            if not bs:
                continue
            scored = [(b.strength * (1.0 - 0.1 * dist), b) for b, dist in bs]
            scored.sort(key=lambda x: x[0], reverse=True)
            result[section] = {
                "motif_id": scored[0][1].motif_id,
                "strength": scored[0][1].strength,
                "n_reinforcements": scored[0][1].n_reinforcements,
            }
        return {"recall": result, "chi": chi, "fired": all_fired}

    def save(self, path: str):
        with open(path, 'w') as f:
            json.dump({
                "tick": self.tick,
                "next_motif_id": self.next_motif_id,
                "next_chi": self.next_chi,
                "motifs": {s: [m.to_dict() for m in motifs]
                          for s, motifs in self.motifs.items()},
                "bindings": [
                    {"key": list(k), "value": v.to_dict()}
                    for k, v in self.bindings.items()
                ],
                "chi_address_map": [
                    {"cofire_set": list(k), "chi": v}
                    for k, v in self.chi_address_map.items()
                ],
            }, f, indent=2)

    @classmethod
    def load(cls, path: str) -> 'SynthesisAtlas':
        if not os.path.exists(path):
            return cls()
        with open(path) as f:
            data = json.load(f)
        a = cls()
        a.tick = data["tick"]
        a.next_motif_id = data["next_motif_id"]
        a.next_chi = data["next_chi"]
        a.motifs = {s: [Motif.from_dict(m) for m in ms]
                   for s, ms in data["motifs"].items()}
        a.bindings = {tuple(b["key"]): Binding.from_dict(b["value"])
                     for b in data["bindings"]}
        a.chi_address_map = {frozenset(e["cofire_set"]): e["chi"]
                            for e in data["chi_address_map"]}
        return a


# ============================================================================
# Experience signatures (same as basin experiment for direct comparison)
# ============================================================================

REPEATED_EXPERIENCES = {
    "moon":         (FMM(I=0.45, C=0.7,  N=0.4, A=0.7), "object"),
    "warm_held":    (FMM(I=0.65, C=0.9,  N=0.15,A=0.9), "modifier"),
    "loud_noise":   (FMM(I=0.95, C=0.35, N=0.85,A=0.25),"listen"),
    "soft_voice":   (FMM(I=0.45, C=0.85, N=0.25,A=0.8), "listen"),
    "novel_thing":  (FMM(I=0.6,  C=0.5,  N=0.9, A=0.55),"object"),
}

FAMILIARITY = {k: 0.0 for k in REPEATED_EXPERIENCES}


def noisy_token_for(name: str, rng: np.random.Generator):
    base, section = REPEATED_EXPERIENCES[name]
    jitter = rng.uniform(-0.05, 0.05, size=4)
    fmm = FMM(
        I=float(clip(base.I + jitter[0])),
        C=float(clip(base.C + jitter[1])),
        N=float(clip(base.N + jitter[2])),
        A=float(clip(base.A + jitter[3])),
    )
    g = project_to_g32(fmm, familiarity=FAMILIARITY[name])
    return g, section, fmm.N


# ============================================================================
# Tests
# ============================================================================

def test_no_fragmentation_under_variance():
    print("=" * 72)
    print("TEST: Same experience under noise — does it cluster at one chi-address")
    print("      or fragment into many?")
    print("=" * 72)

    atlas_path = "/home/claude/synthesis/syn_atlas.json"
    if os.path.exists(atlas_path):
        os.remove(atlas_path)
    for k in FAMILIARITY:
        FAMILIARITY[k] = 0.0

    atlas = SynthesisAtlas()

    rng = np.random.default_rng(2026)
    sequence = (["moon", "warm_held", "soft_voice", "novel_thing"] * 8
                + ["loud_noise"] * 4
                + ["moon", "moon", "warm_held", "soft_voice"])
    rng.shuffle(sequence)

    # Track per-experience: which chi-addresses did variants land at?
    chi_addresses_per_exp = defaultdict(set)
    motifs_committed_per_exp = defaultdict(set)

    print(f"\n--- PASS 1 ({len(sequence)} reads) ---")
    for name in sequence:
        g, section, novelty = noisy_token_for(name, rng)
        FAMILIARITY[name] = min(1.0, FAMILIARITY[name] + 0.02)
        result = atlas.process_event(g, novelty, FAMILIARITY[name], section_focus=section)
        if result.get("bound_at_chi") is not None and result.get("bound_at_chi") != []:
            chi_addresses_per_exp[name].add(result["bound_at_chi"])
        for sec, mid in result["committed_new"].items():
            motifs_committed_per_exp[name].add((sec, mid))

    atlas.save(atlas_path)

    print(f"  After pass 1:")
    print(f"    Total motifs: {sum(len(ms) for ms in atlas.motifs.values())}")
    print(f"    Motifs by section: {[(s, len(ms)) for s, ms in atlas.motifs.items() if ms]}")
    print(f"    Total bindings: {len(atlas.bindings)}")
    print(f"    Total chi-addresses used: {len(atlas.chi_address_map)}")
    print(f"\n  Per-experience chi-fragmentation:")
    for name in REPEATED_EXPERIENCES:
        chis = chi_addresses_per_exp[name]
        motifs = motifs_committed_per_exp[name]
        print(f"    {name:>14s}: chi-addresses={sorted(chis)}, new motifs={sorted(motifs)}")

    # Compute the verdict
    print(f"\n  KEY METRIC: number of distinct chi-addresses per experience type.")
    print(f"  Ideal = 1 (all variants of one experience cluster at one address).")
    print(f"  Fragmentation = >1 (same experience splitting).")
    max_chi_per_exp = max(len(c) for c in chi_addresses_per_exp.values())
    if max_chi_per_exp <= 1:
        print(f"  ✓ All experiences cluster at single chi-addresses. NO fragmentation.")
    elif max_chi_per_exp <= 2:
        print(f"  ~ Light fragmentation (max {max_chi_per_exp} chi-addresses per experience).")
    else:
        print(f"  ✗ Heavy fragmentation (max {max_chi_per_exp} chi-addresses per experience).")

    # Pass 2 — does additional experience help or fragment further?
    print(f"\n--- PASS 2 (reload + read same sequence again) ---")
    atlas_reload = SynthesisAtlas.load(atlas_path)
    rng2 = np.random.default_rng(2026)
    sequence_2 = list(sequence)
    rng2.shuffle(sequence_2)

    chi_addresses_per_exp_2 = defaultdict(set)
    new_motifs_in_pass_2 = 0

    motifs_before_pass_2 = sum(len(ms) for ms in atlas_reload.motifs.values())
    for name in sequence_2:
        g, section, novelty = noisy_token_for(name, rng2)
        result = atlas_reload.process_event(g, novelty, FAMILIARITY[name],
                                            section_focus=section)
        if result.get("bound_at_chi") not in (None, []):
            chi_addresses_per_exp_2[name].add(result["bound_at_chi"])
        new_motifs_in_pass_2 += len(result["committed_new"])

    motifs_after_pass_2 = sum(len(ms) for ms in atlas_reload.motifs.values())
    atlas_reload.save(atlas_path)

    print(f"  Motifs before pass 2: {motifs_before_pass_2}")
    print(f"  Motifs after pass 2:  {motifs_after_pass_2}")
    print(f"  New motifs committed in pass 2: {new_motifs_in_pass_2}")
    print(f"  (0 new motifs in pass 2 = the substrate generalizes from experience)")

    print(f"\n  Pass 2 chi-addresses per experience:")
    for name in REPEATED_EXPERIENCES:
        prior = chi_addresses_per_exp[name]
        now = chi_addresses_per_exp_2[name]
        added = now - prior
        print(f"    {name:>14s}: prior={sorted(prior)}, "
              f"now={sorted(now)}, NEW_CHI={sorted(added) if added else 'none'}")

    # Compare to basin experiment
    print(f"\n--- COMPARISON TO BASIN EXPERIMENT ---")
    print(f"  Basin experiment: 5 → 9 basins for same data (concept fragmentation).")
    print(f"  Synthesis experiment: {motifs_before_pass_2} → {motifs_after_pass_2} motifs.")
    if motifs_after_pass_2 <= motifs_before_pass_2 + 1:
        print(f"  ✓ Synthesis architecture GENERALIZES under repeated experience.")
    else:
        print(f"  ~ Some new motifs in pass 2 — investigate why.")


def test_recall_after_learning():
    print("\n" + "=" * 72)
    print("TEST: Does the substrate recall correctly after learning?")
    print("=" * 72)

    atlas = SynthesisAtlas.load("/home/claude/synthesis/syn_atlas.json")
    rng = np.random.default_rng(99)
    hits = 0
    misses = 0
    correct_section = 0
    for name in REPEATED_EXPERIENCES:
        for _ in range(3):
            g, section, _ = noisy_token_for(name, rng)
            result = atlas.recall(g, section_focus=section)
            if result["recall"] is None:
                misses += 1
            else:
                hits += 1
                if section in result["recall"]:
                    correct_section += 1
    print(f"  Recall hits: {hits}/15")
    print(f"  Section-correct recalls: {correct_section}/15")
    print(f"  Misses (honest unknowns): {misses}/15")


def test_tiny_dialog_learning():
    """Read a small Guala-like dialog. Observe whether bindings form
    between subject + verb + modifier across turns."""
    print("\n" + "=" * 72)
    print("TEST: Tiny dialog — does substrate bind subject+verb+modifier")
    print("      across utterances?")
    print("=" * 72)

    atlas_path = "/home/claude/synthesis/syn_dialog_atlas.json"
    if os.path.exists(atlas_path):
        os.remove(atlas_path)
    atlas = SynthesisAtlas()
    rng = np.random.default_rng(42)

    # Tiny dialog modeled on Joe-Guala patterns:
    # Each "utterance" decomposes into word-events tagged with their section.
    # FMM signature reflects the affect/coherence of that utterance.
    utterances = [
        # Joe: "moon is hot" — wrong, teaching
        [("moon", "subject", 0.5, 0.7, 0.5, 0.6),
         ("is", "verb", 0.4, 0.85, 0.2, 0.6),
         ("hot", "modifier", 0.6, 0.6, 0.5, 0.7)],
        # Joe: "no moon is cold"
        [("no", "ground", 0.55, 0.85, 0.3, 0.4),
         ("moon", "subject", 0.5, 0.7, 0.2, 0.6),
         ("is", "verb", 0.4, 0.85, 0.1, 0.6),
         ("cold", "modifier", 0.55, 0.8, 0.4, 0.55)],
        # Guala-style read: "stone hard"
        [("stone", "subject", 0.55, 0.75, 0.6, 0.55),
         ("hard", "modifier", 0.6, 0.7, 0.5, 0.5)],
        # Joe: "stone soft like cotton"
        [("stone", "subject", 0.5, 0.85, 0.2, 0.6),
         ("soft", "modifier", 0.5, 0.8, 0.4, 0.7),
         ("cotton", "object", 0.5, 0.7, 0.7, 0.7)],
        # Joe: "stone hard like diamond"
        [("stone", "subject", 0.5, 0.85, 0.2, 0.6),
         ("hard", "modifier", 0.6, 0.75, 0.3, 0.6),
         ("diamond", "object", 0.55, 0.7, 0.7, 0.75)],
        # Joe: "moon is cold"
        [("moon", "subject", 0.5, 0.85, 0.1, 0.65),
         ("is", "verb", 0.4, 0.85, 0.05, 0.6),
         ("cold", "modifier", 0.55, 0.8, 0.2, 0.55)],
        # Joe: "moon is bright"
        [("moon", "subject", 0.5, 0.85, 0.1, 0.7),
         ("is", "verb", 0.4, 0.85, 0.05, 0.6),
         ("bright", "modifier", 0.6, 0.8, 0.4, 0.75)],
    ]

    fam_per_word = defaultdict(float)
    binding_history = []  # which words co-fired across utterances

    for utt_idx, utt in enumerate(utterances):
        for (word, section, I, C, N, A) in utt:
            fam = fam_per_word[word]
            fmm = FMM(I=I, C=C, N=N, A=A)
            g = project_to_g32(fmm, familiarity=fam)
            result = atlas.process_event(g, fmm.N, fam, section_focus=section)
            fam_per_word[word] = min(1.0, fam + 0.1)
            # Track what fired and what got committed
            binding_history.append((utt_idx, word, section, result.get("fired", {}),
                                    result.get("committed_new", {})))

    # Inspect: what's bound to "moon"?
    print(f"\n  Words observed: {sorted(fam_per_word.keys())}")
    print(f"  Total motifs: {sum(len(ms) for ms in atlas.motifs.values())}")
    print(f"  Motifs by section:")
    for s, ms in atlas.motifs.items():
        if ms:
            print(f"    {s}: {len(ms)}")
    print(f"  Total bindings: {len(atlas.bindings)}")
    print(f"  Distinct chi-addresses: {len(atlas.chi_address_map)}")

    # Recall: query with a "moon"-like input — what does the substrate surface?
    print(f"\n  RECALL TEST: input matches 'moon' subject signature")
    g_moon = project_to_g32(FMM(I=0.5, C=0.85, N=0.05, A=0.7), familiarity=0.5)
    recall_result = atlas.recall(g_moon, section_focus="subject")
    print(f"    {recall_result}")

    # Recall: query with input near "stone"
    print(f"\n  RECALL TEST: input matches 'stone' signature")
    g_stone = project_to_g32(FMM(I=0.55, C=0.8, N=0.2, A=0.6), familiarity=0.5)
    recall_result = atlas.recall(g_stone, section_focus="subject")
    print(f"    {recall_result}")


if __name__ == "__main__":
    test_no_fragmentation_under_variance()
    test_recall_after_learning()
    test_tiny_dialog_learning()
