"""
Experiment 07 — Cross-Domain Composition with Pre-Loaded Primitives at CONTEXT=16

Pre-commits frozen at 0fbb36f.
Anti-cheat discipline from exp06 pass 4 enforced throughout.

DO NOT:
- Replace strand 0 in place during perturbation (use shift-left-append-right)
- Cycle 'a'-'z' content-blind
- Select pairs by successor count or word frequency
- Commit loom.last after loom.tick() (zero-new-motifs cheat)
- Use null_pos03 perturbation
- Adjust barrier mid-run
"""

import os, sys, json, hashlib, time, random, math, traceback, glob
from collections import OrderedDict, defaultdict, Counter
from itertools import combinations

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(REPO)

RESULTS_DIR = os.path.join(REPO, "experiments", "exp07")
RESULTS_FILE = os.path.join(RESULTS_DIR, "results.jsonl")
os.makedirs(RESULTS_DIR, exist_ok=True)

# ======================================================================
# FROZEN CONFIGURATION (from PRECOMMITS.md)
# ======================================================================

TRITS = 16
CONTEXT = 16
POP = TRITS * CONTEXT  # 256
P3I = tuple(3**i for i in range(TRITS))
BARRIER = 104  # round(0.5 * CONTEXT * (P3I[3] // 2))
SEED = 70707

# Primitive placement positions (chi-orthogonal)
D4_POSITIONS = (8, 9, 10)   # syntactic, P3I = 6561, 19683, 59049
D5_POSITIONS = (12, 13, 14)  # communication, P3I = 531441, 1594323, 4782969

# Canonical primitive list (frozen, alphabetical, 1-indexed)
PRIMITIVES = [
    "agent", "deixis_distal", "deixis_proximal", "dep_dir", "focus",
    "hedge", "imperative", "modifier", "modality", "mood", "negation",
    "object", "performative", "question", "scope", "sentence_bound",
    "statement", "subject", "verb", "vocative",
]

# Morpheme segmentation lists
SUFFIXES = sorted([
    "tion", "sion", "ment", "ness", "able", "ible", "ful", "less",
    "ous", "ive", "ing", "ity", "ent", "ant", "ary", "ory",
    "al", "ly", "ed", "er", "es", "en", "ty", "ic",
], key=lambda s: -len(s))

PREFIXES = sorted([
    "under", "over", "dis", "mis", "pre", "non", "sub",
    "un", "re", "in", "im", "ir", "il",
], key=lambda s: -len(s))


# ======================================================================
# SUBSTRATE (same as gualaloom.py / exp06, barrier = 104)
# ======================================================================

def encode(ch):
    """One character -> TRITS-length balanced ternary strand."""
    v = ord(ch) - 96
    t = []
    for _ in range(TRITS):
        r = v % 3
        if r == 2:
            r = -1; v = (v + 1) // 3
        else:
            v = (v - r) // 3
        t.append(r)
    return tuple(t)


def settle(strands, barrier=BARRIER):
    """Settle with fixed barrier (no familiarity modulation in experiment)."""
    out = []
    for s_idx, strand in enumerate(strands):
        for i in range(TRITS):
            h = strand[i] * P3I[i]
            for o_idx, other in enumerate(strands):
                if o_idx != s_idx:
                    h += other[i] * P3I[i] // 2
            out.append(1 if h > barrier else (-1 if h < -barrier else 0))
    return tuple(out)


def chi(state):
    """Euler characteristic: V - E over the coupling graph."""
    verts = [i for i, t in enumerate(state) if t != 0]
    vset = set(verts)
    V = len(verts)
    if V == 0:
        return 0, 0
    E = 0
    for i in verts:
        if (i + 1) in vset and (i + 1) % TRITS != 0:
            E += 1
    n_strands = len(state) // TRITS
    for pos in range(TRITS):
        committed = [s for s in range(n_strands) if state[s * TRITS + pos] != 0]
        E += max(len(committed) - 1, 0)
    return V - E, V


def _fp(state):
    s = "".join({-1: "-", 0: "0", 1: "+"}[t] for t in state)
    return hashlib.sha1(s.encode()).hexdigest()[:12]


def null_count(state):
    return sum(1 for t in state if t == 0)


def pressure_at(state, idx):
    """Compute |h| at a specific flat index in the state."""
    strands = [state[j * TRITS:(j + 1) * TRITS] for j in range(CONTEXT)]
    s_idx = idx // TRITS
    i = idx % TRITS
    h = strands[s_idx][i] * P3I[i]
    for o_idx, other in enumerate(strands):
        if o_idx != s_idx:
            h += other[i] * P3I[i] // 2
    return abs(h)


def pressure_at_pos(state, pos):
    """Compute |h| at intra-strand position `pos` for all strands.
    Returns list of (strand_idx, |h|, committed) tuples."""
    strands = [state[j * TRITS:(j + 1) * TRITS] for j in range(CONTEXT)]
    results = []
    for s_idx, strand in enumerate(strands):
        h = strand[pos] * P3I[pos]
        for o_idx, other in enumerate(strands):
            if o_idx != s_idx:
                h += other[pos] * P3I[pos] // 2
        flat_idx = s_idx * TRITS + pos
        results.append((s_idx, abs(h), state[flat_idx] != 0))
    return results


def loaded_null_at_pos3(state):
    """Check if any null at intra-strand position 3 has |h| >= 4."""
    for s_idx, ah, committed in pressure_at_pos(state, 3):
        if not committed and ah >= 4:
            return True, ah
    return False, 0


# ======================================================================
# KRIMELACK (single store, domain-tagged motifs)
# ======================================================================

class Motif:
    __slots__ = ("fp", "state", "weight", "age", "chi_val", "V",
                 "char_counts", "successors", "domain", "label")

    def __init__(self, fp, state, c, v, domain="?", label=None):
        self.fp = fp; self.state = state; self.weight = 1; self.age = 0
        self.chi_val = c; self.V = v
        self.char_counts = defaultdict(int)
        self.successors = defaultdict(int)
        self.domain = domain
        self.label = label


class Krimelack:
    def __init__(self):
        self.motifs = OrderedDict()
        self._last_fp = None
        # Index: chi -> list of fps
        self._chi_index = defaultdict(list)

    def commit(self, state, domain="?", label=None, active_char=None, track_successor=True):
        if all(t == 0 for t in state):
            return None, False
        fp = _fp(state)
        new = fp not in self.motifs
        if new:
            c, v = chi(state)
            self.motifs[fp] = Motif(fp, state, c, v, domain=domain, label=label)
            self._chi_index[c].append(fp)
        m = self.motifs[fp]
        m.weight += 1; m.age = 0
        if active_char is not None:
            m.char_counts[active_char] += 1
        if track_successor and self._last_fp and self._last_fp != fp and self._last_fp in self.motifs:
            self.motifs[self._last_fp].successors[fp] += 1
        self._last_fp = fp
        return fp, new

    def recall(self, state, domain_filter=None):
        """Chi-first recall, optionally filtered to a domain."""
        if not self.motifs:
            return None, 0
        qchi, _ = chi(state)
        # Build pool: chi-matched first, optionally domain-filtered
        pool_fps = self._chi_index.get(qchi, [])
        pool = []
        for fp in pool_fps:
            m = self.motifs.get(fp)
            if m and (domain_filter is None or m.domain == domain_filter):
                pool.append(m)
        if not pool:
            # Fallback: all motifs (optionally filtered)
            pool = [m for m in self.motifs.values()
                    if domain_filter is None or m.domain == domain_filter]
        if not pool:
            return None, 0
        best, best_score = None, -1
        for m in pool:
            score = sum(1 for a, b in zip(state, m.state) if a == b and a != 0)
            score = score * 100 + min(m.weight, 99)
            if score > best_score:
                best, best_score = m, score
        return best, best_score

    def recall_global(self, state):
        return self.recall(state, domain_filter=None)

    def size(self, domain=None):
        if domain is None:
            return len(self.motifs)
        return sum(1 for m in self.motifs.values() if m.domain == domain)

    def motifs_in_domain(self, domain):
        return [m for m in self.motifs.values() if m.domain == domain]

    def chi_distribution(self, domain=None):
        dist = Counter()
        for m in self.motifs.values():
            if domain is None or m.domain == domain:
                dist[m.chi_val] += 1
        return dict(sorted(dist.items()))

    def chi_neighborhood(self, chi_val, distance=2, domain=None):
        """Count motifs within chi-distance of a value."""
        count = 0
        for c in range(chi_val - distance, chi_val + distance + 1):
            for fp in self._chi_index.get(c, []):
                m = self.motifs.get(fp)
                if m and (domain is None or m.domain == domain):
                    count += 1
        return count


# ======================================================================
# LOOM (for char-context ingestion, barrier=104)
# ======================================================================

class Loom:
    def __init__(self, k):
        self.k = k
        self.recent = []
        self.fam = 0
        self.last = tuple([0] * POP)

    def tick(self, ch):
        self.recent.append(ch)
        if len(self.recent) > CONTEXT:
            self.recent.pop(0)
        strands = [encode(c) for c in self.recent]
        while len(strands) < CONTEXT:
            strands.insert(0, tuple([0] * TRITS))
        settled = settle(strands, BARRIER)
        m, score = self.k.recall(settled)
        self.fam = (score // 100 * 20) // max(POP, 1) if score > 0 else 0
        self.k.commit(settled, domain="D1", active_char=ch)
        self.last = settled
        return settled

    def feed(self, text):
        for ch in text:
            self.tick(ch)


# ======================================================================
# PRIMITIVE ENCODING
# ======================================================================

def bt3(index):
    """Balanced ternary 3-trit signature for 1-indexed prime_index."""
    v = index
    t = []
    for _ in range(3):
        r = v % 3
        if r == 2:
            r = -1; v = (v + 1) // 3
        else:
            v = (v - r) // 3
        t.append(r)
    return tuple(t)


def build_primitive_state(prim_indices, positions):
    """Build a POP-length state with primitive signatures at given positions.

    prim_indices: list of 1-indexed primitive indices
    positions: tuple of 3 trit positions (e.g., D4_POSITIONS or D5_POSITIONS)

    Each primitive goes in a separate strand. Strands are assigned sequentially
    starting from strand 0.
    """
    state = [0] * POP
    for strand_idx, pidx in enumerate(prim_indices):
        if strand_idx >= CONTEXT:
            break  # can't exceed available strands
        sig = bt3(pidx)
        for k_pos, pos in enumerate(positions):
            state[strand_idx * TRITS + pos] = sig[k_pos]
    return tuple(state)


def preload_primitives(k, domain_name, positions, rng, target=2000):
    """Generate and commit primitive motifs for a domain.

    Builds singletons, pairs, triples (and 4-tuples if needed) from
    the 20 primitives placed at the given positions.
    """
    stats = {"singletons": 0, "pairs": 0, "triples": 0, "quads": 0,
             "total_committed": 0, "total_new": 0, "null_collapses": 0}

    indices = list(range(1, len(PRIMITIVES) + 1))  # 1-20

    # Singletons
    for idx in indices:
        raw = build_primitive_state([idx], positions)
        strands = [raw[j * TRITS:(j + 1) * TRITS] for j in range(CONTEXT)]
        settled = settle(strands, BARRIER)
        fp, new = k.commit(settled, domain=domain_name,
                           label=PRIMITIVES[idx - 1], track_successor=False)
        if fp is None:
            stats["null_collapses"] += 1
        else:
            stats["singletons"] += 1
            stats["total_committed"] += 1
            if new:
                stats["total_new"] += 1

    # Pairs
    for combo in combinations(indices, 2):
        raw = build_primitive_state(list(combo), positions)
        strands = [raw[j * TRITS:(j + 1) * TRITS] for j in range(CONTEXT)]
        settled = settle(strands, BARRIER)
        label = "+".join(PRIMITIVES[i - 1] for i in combo)
        fp, new = k.commit(settled, domain=domain_name,
                           label=label, track_successor=False)
        if fp is None:
            stats["null_collapses"] += 1
        else:
            stats["pairs"] += 1
            stats["total_committed"] += 1
            if new:
                stats["total_new"] += 1

    # Triples
    for combo in combinations(indices, 3):
        raw = build_primitive_state(list(combo), positions)
        strands = [raw[j * TRITS:(j + 1) * TRITS] for j in range(CONTEXT)]
        settled = settle(strands, BARRIER)
        label = "+".join(PRIMITIVES[i - 1] for i in combo)
        fp, new = k.commit(settled, domain=domain_name,
                           label=label, track_successor=False)
        if fp is None:
            stats["null_collapses"] += 1
        else:
            stats["triples"] += 1
            stats["total_committed"] += 1
            if new:
                stats["total_new"] += 1

    # 4-tuples if still below target
    if stats["total_new"] < target:
        quads = list(combinations(indices, 4))
        rng.shuffle(quads)
        for combo in quads:
            if stats["total_new"] >= target:
                break
            raw = build_primitive_state(list(combo), positions)
            strands = [raw[j * TRITS:(j + 1) * TRITS] for j in range(CONTEXT)]
            settled = settle(strands, BARRIER)
            label = "+".join(PRIMITIVES[i - 1] for i in combo)
            fp, new = k.commit(settled, domain=domain_name,
                               label=label, track_successor=False)
            if fp is None:
                stats["null_collapses"] += 1
            else:
                stats["quads"] += 1
                stats["total_committed"] += 1
                if new:
                    stats["total_new"] += 1

    return stats


# ======================================================================
# MORPHEME SEGMENTATION (D2)
# ======================================================================

def segment_morphemes(word):
    """Simple prefix/suffix segmentation. Returns list of morphemes."""
    w = word.lower()
    if len(w) < 4:
        return [w]  # too short to decompose

    prefix = None
    suffix = None
    stem = w

    # Try longest suffix first
    for sfx in SUFFIXES:
        if stem.endswith(sfx) and len(stem) - len(sfx) >= 2:
            suffix = sfx
            stem = stem[:-len(sfx)]
            break

    # Try longest prefix on remaining stem
    for pfx in PREFIXES:
        if stem.startswith(pfx) and len(stem) - len(pfx) >= 2:
            prefix = pfx
            stem = stem[len(pfx):]
            break

    parts = []
    if prefix:
        parts.append(prefix)
    parts.append(stem)
    if suffix:
        parts.append(suffix)
    return parts


def settle_text_alone(text):
    """Settle a text string's characters as strands, null-padded to CONTEXT."""
    chars = list(text.lower())
    if len(chars) > CONTEXT:
        chars = chars[:CONTEXT]
    strands = [encode(c) for c in chars]
    while len(strands) < CONTEXT:
        strands.append(tuple([0] * TRITS))
    return settle(strands, BARRIER)


def ingest_morphemes(k, corpus_text):
    """D2: morpheme domain. Settle each unique morpheme alone."""
    words = corpus_text.lower().split()
    all_morphemes = set()
    for w in words:
        # Clean word
        w_clean = "".join(c for c in w if c.isalpha())
        if not w_clean:
            continue
        parts = segment_morphemes(w_clean)
        for p in parts:
            if len(p) >= 2:
                all_morphemes.add(p)

    stats = {"unique_morphemes": len(all_morphemes), "committed": 0,
             "new": 0, "null_collapses": 0}

    for morph in sorted(all_morphemes):
        settled = settle_text_alone(morph)
        fp, new = k.commit(settled, domain="D2", label=morph, track_successor=False)
        if fp is None:
            stats["null_collapses"] += 1
        else:
            stats["committed"] += 1
            if new:
                stats["new"] += 1

    return stats


# ======================================================================
# WORD INGESTION (D3)
# ======================================================================

def ingest_words(k, corpus_text):
    """D3: word domain. Settle each unique word alone."""
    words = corpus_text.lower().split()
    unique_words = set()
    for w in words:
        w_clean = "".join(c for c in w if c.isalpha())
        if w_clean:
            unique_words.add(w_clean)

    stats = {"unique_words": len(unique_words), "committed": 0,
             "new": 0, "null_collapses": 0}

    for word in sorted(unique_words):
        settled = settle_text_alone(word)
        fp, new = k.commit(settled, domain="D3", label=word, track_successor=False)
        if fp is None:
            stats["null_collapses"] += 1
        else:
            stats["committed"] += 1
            if new:
                stats["new"] += 1

    return stats


# ======================================================================
# COMPOSITION + NOVELTY
# ======================================================================

def fold_compose(state_a, state_b):
    """Union with conflict-nulling, then settle."""
    merged = []
    for a, b in zip(state_a, state_b):
        if a == b:
            merged.append(a)
        elif a != 0 and b != 0:
            merged.append(0)  # conflict -> null
        elif a != 0:
            merged.append(a)
        else:
            merged.append(b)
    merged = tuple(merged)
    strands = [merged[j * TRITS:(j + 1) * TRITS] for j in range(CONTEXT)]
    settled = settle(strands, BARRIER)
    return merged, settled


def evaluate_novelty(k, state_r, chi_r, motif_a, motif_b):
    """Evaluate the novelty criterion from PRECOMMITS.md.

    Returns dict with:
      novel: bool (all three criteria met)
      geometric_novel: bool (passes criterion but in empty real estate)
      not_parental: bool
      cross_domain_consistent: bool
      cognitively_engaged: bool
      empty_real_estate: bool
    """
    result = {
        "not_parental": False,
        "cross_domain_consistent": False,
        "cognitively_engaged": False,
        "empty_real_estate": False,
        "novel": False,
        "geometric_novel": False,
    }

    # Criterion 1: not in chi-neighborhood of either parent
    chi_a = motif_a.chi_val
    chi_b = motif_b.chi_val
    near_a = abs(chi_r - chi_a) <= 2
    near_b = abs(chi_r - chi_b) <= 2
    result["not_parental"] = not near_a and not near_b

    # Criterion 2: in chi-neighborhood of at least one motif from each parent's domain
    dom_a = motif_a.domain
    dom_b = motif_b.domain
    near_dom_a = k.chi_neighborhood(chi_r, distance=2, domain=dom_a) > 0
    near_dom_b = k.chi_neighborhood(chi_r, distance=2, domain=dom_b) > 0
    result["cross_domain_consistent"] = near_dom_a and near_dom_b

    # Criterion 3: |h| >= 4 at idx=3
    has_loaded, max_h = loaded_null_at_pos3(state_r)
    result["cognitively_engaged"] = has_loaded
    result["h_at_pos3"] = max_h

    # Empty-real-estate guard
    neighbors = k.chi_neighborhood(chi_r, distance=3)
    result["empty_real_estate"] = neighbors < 3

    # Compositional novelty vs geometric novelty
    all_criteria = (result["not_parental"] and
                    result["cross_domain_consistent"] and
                    result["cognitively_engaged"])
    if all_criteria and not result["empty_real_estate"]:
        result["novel"] = True
    elif all_criteria and result["empty_real_estate"]:
        result["geometric_novel"] = True

    return result


def dream_mini(k, cycles=5):
    """Small dream cycle. Returns count of new motifs."""
    if not k.motifs:
        return 0
    motif_list = list(k.motifs.values())
    new_count = 0
    for i in range(cycles):
        m = motif_list[i % len(motif_list)]
        strands = [m.state[j * TRITS:(j + 1) * TRITS] for j in range(CONTEXT)]
        settled = settle(strands, BARRIER)
        if any(t != 0 for t in settled):
            fp = _fp(settled)
            if fp not in k.motifs:
                k.commit(settled, domain="dream", track_successor=False)
                new_count += 1
    return new_count


# ======================================================================
# VITALS COLLECTION
# ======================================================================

def collect_vitals(k, trial_num):
    """Snapshot substrate vitals at a trial boundary."""
    chi_dist = k.chi_distribution()
    domain_sizes = {}
    for d in ["D1", "D2", "D3", "D4", "D5", "dream"]:
        domain_sizes[d] = k.size(domain=d)

    # Pressure stats at position 3 across a sample of motifs
    sample = list(k.motifs.values())[:100]
    pressures_pos3 = []
    for m in sample:
        for s_idx, ah, committed in pressure_at_pos(m.state, 3):
            if not committed:
                pressures_pos3.append(ah)

    return {
        "trial": trial_num,
        "total_motifs": k.size(),
        "domain_sizes": domain_sizes,
        "chi_classes": len(chi_dist),
        "pressure_pos3_mean": round(sum(pressures_pos3) / max(len(pressures_pos3), 1), 2),
        "pressure_pos3_loaded": sum(1 for p in pressures_pos3 if p >= 4),
        "pressure_pos3_total_nulls": len(pressures_pos3),
    }


# ======================================================================
# COMPOSITION TRIALS
# ======================================================================

DOMAIN_PAIRS = [
    ("D1", "D2"), ("D1", "D3"), ("D1", "D4"), ("D1", "D5"),
    ("D2", "D3"), ("D2", "D4"), ("D2", "D5"),
    ("D3", "D4"), ("D3", "D5"),
    ("D4", "D5"),
]

TRIALS_PER_PAIR = 500


def run_composition_trials(k, rng):
    """Run 500 trials per pairing, 10 pairings. Returns full results."""
    all_results = {}
    vitals_log = []
    trial_counter = 0

    for dom_a, dom_b in DOMAIN_PAIRS:
        print(f"\n  === Pairing ({dom_a}, {dom_b}) ===")
        motifs_a = k.motifs_in_domain(dom_a)
        motifs_b = k.motifs_in_domain(dom_b)

        if len(motifs_a) < 2 or len(motifs_b) < 2:
            print(f"    SKIP: {dom_a}={len(motifs_a)}, {dom_b}={len(motifs_b)} motifs")
            all_results[f"{dom_a}_{dom_b}"] = {"skipped": True,
                                                "reason": "insufficient motifs"}
            continue

        # Build candidate pairs: chi-distance >= 4
        candidates = []
        for ma in motifs_a:
            for mb in motifs_b:
                if abs(ma.chi_val - mb.chi_val) >= 4:
                    candidates.append((ma, mb))

        if len(candidates) < 10:
            # Relax to chi-distance >= 2
            candidates = [(ma, mb) for ma in motifs_a for mb in motifs_b
                          if abs(ma.chi_val - mb.chi_val) >= 2]
            print(f"    Relaxed chi threshold to >=2, {len(candidates)} candidates")

        if not candidates:
            print(f"    SKIP: no chi-dissimilar pairs")
            all_results[f"{dom_a}_{dom_b}"] = {"skipped": True,
                                                "reason": "no chi-dissimilar pairs"}
            continue

        print(f"    {len(candidates)} candidate pairs from "
              f"{len(motifs_a)}x{len(motifs_b)} motifs")

        pair_stats = {
            "trials": 0,
            "compositional_novel": 0,
            "geometric_novel": 0,
            "recall_to_parent_a": 0,
            "recall_to_parent_b": 0,
            "recall_to_other": 0,
            "recall_changed_post_dream": 0,
            "null_collapses": 0,
            "not_parental_count": 0,
            "cross_domain_consistent_count": 0,
            "cognitively_engaged_count": 0,
            "empty_real_estate_count": 0,
            "chi_composed_values": [],
            "sample_trials": [],
        }

        for t in range(TRIALS_PER_PAIR):
            ma, mb = rng.choice(candidates)
            trial_counter += 1

            # Compose
            merged, settled = fold_compose(ma.state, mb.state)

            if all(t_val == 0 for t_val in settled):
                pair_stats["null_collapses"] += 1
                pair_stats["trials"] += 1
                continue

            chi_r, v_r = chi(settled)
            pair_stats["chi_composed_values"].append(chi_r)

            # Recall
            recalled, score = k.recall_global(settled)

            # Classify recall
            if recalled is None:
                recall_class = "none"
            elif recalled.fp == _fp(ma.state):
                recall_class = "parent_a"
                pair_stats["recall_to_parent_a"] += 1
            elif recalled.fp == _fp(mb.state):
                recall_class = "parent_b"
                pair_stats["recall_to_parent_b"] += 1
            else:
                recall_class = "other"
                pair_stats["recall_to_other"] += 1

            # Novelty evaluation
            nov = evaluate_novelty(k, settled, chi_r, ma, mb)
            if nov["novel"]:
                pair_stats["compositional_novel"] += 1
            if nov["geometric_novel"]:
                pair_stats["geometric_novel"] += 1
            if nov["not_parental"]:
                pair_stats["not_parental_count"] += 1
            if nov["cross_domain_consistent"]:
                pair_stats["cross_domain_consistent_count"] += 1
            if nov["cognitively_engaged"]:
                pair_stats["cognitively_engaged_count"] += 1
            if nov["empty_real_estate"]:
                pair_stats["empty_real_estate_count"] += 1

            # Dream cycle, then re-recall
            dream_mini(k, cycles=5)
            recalled_post, score_post = k.recall_global(settled)
            recall_changed = (recalled_post is None) != (recalled is None)
            if recalled and recalled_post and recalled.fp != recalled_post.fp:
                recall_changed = True
            if recall_changed:
                pair_stats["recall_changed_post_dream"] += 1

            pair_stats["trials"] += 1

            # Sample first 5 trials for detailed logging
            if len(pair_stats["sample_trials"]) < 5:
                pair_stats["sample_trials"].append({
                    "parent_a": ma.label, "parent_b": mb.label,
                    "chi_a": ma.chi_val, "chi_b": mb.chi_val,
                    "chi_composed": chi_r, "recall_class": recall_class,
                    "recall_label": recalled.label if recalled else None,
                    "novelty": nov,
                    "recall_changed": recall_changed,
                })

            # Vitals every 100 trials
            if trial_counter % 100 == 0:
                vitals_log.append(collect_vitals(k, trial_counter))

        # Summary for this pairing
        n = max(pair_stats["trials"], 1)
        pair_stats["compositional_novelty_rate"] = round(
            pair_stats["compositional_novel"] / n, 4)
        pair_stats["geometric_novelty_rate"] = round(
            pair_stats["geometric_novel"] / n, 4)
        pair_stats["recall_change_rate"] = round(
            pair_stats["recall_changed_post_dream"] / n, 4)

        # Compress chi values for storage
        chi_counter = Counter(pair_stats["chi_composed_values"])
        pair_stats["chi_composed_distribution"] = dict(sorted(chi_counter.items()))
        del pair_stats["chi_composed_values"]

        print(f"    Trials: {pair_stats['trials']}")
        print(f"    Compositional novel: {pair_stats['compositional_novel']} "
              f"({pair_stats['compositional_novelty_rate']*100:.1f}%)")
        print(f"    Geometric novel: {pair_stats['geometric_novel']} "
              f"({pair_stats['geometric_novelty_rate']*100:.1f}%)")
        print(f"    Recall to parent_a/b/other: "
              f"{pair_stats['recall_to_parent_a']}/"
              f"{pair_stats['recall_to_parent_b']}/"
              f"{pair_stats['recall_to_other']}")
        print(f"    Recall changed post-dream: {pair_stats['recall_changed_post_dream']}")

        all_results[f"{dom_a}_{dom_b}"] = pair_stats

    return all_results, vitals_log


# ======================================================================
# LOADED-NULL PRESERVATION SUB-TEST
# ======================================================================

def run_loaded_null_test(k, rng, trials=200):
    """Compose 3+ motifs that ALL have loaded nulls at idx=3.
    Does the composed result preserve, destroy, or relocate?"""
    print("\n  === Loaded-Null Preservation Sub-Test ===")

    # Find motifs with loaded nulls at position 3
    loaded_motifs = []
    for m in k.motifs.values():
        has_loaded, ah = loaded_null_at_pos3(m.state)
        if has_loaded:
            loaded_motifs.append((m, ah))

    print(f"    Motifs with loaded null at pos3: {len(loaded_motifs)}")

    if len(loaded_motifs) < 3:
        print(f"    SKIP: need >= 3 loaded motifs, have {len(loaded_motifs)}")
        return {"skipped": True, "loaded_motifs_found": len(loaded_motifs)}

    stats = {
        "trials": 0,
        "preserved": 0,      # loaded null at pos3 in result
        "destroyed": 0,      # no loaded null at any position
        "relocated": 0,      # loaded null at other position, not pos3
        "null_collapses": 0,
        "h_pos3_values": [],
        "h_all_positions": defaultdict(list),
        "sample_trials": [],
    }

    for t in range(trials):
        # Sample 3 (sometimes 4) loaded-null motifs
        n_compose = rng.choice([3, 3, 3, 4])
        if n_compose > len(loaded_motifs):
            n_compose = len(loaded_motifs)
        chosen = rng.sample(loaded_motifs, n_compose)
        motifs_chosen = [c[0] for c in chosen]

        # Compose sequentially: fold A+B, then result+C, etc.
        state = motifs_chosen[0].state
        for m in motifs_chosen[1:]:
            _, state = fold_compose(state, m.state)

        if all(t_val == 0 for t_val in state):
            stats["null_collapses"] += 1
            stats["trials"] += 1
            continue

        # Check loaded null at pos3
        has_loaded_3, h_3 = loaded_null_at_pos3(state)
        stats["h_pos3_values"].append(h_3)

        # Check all positions for loaded nulls
        found_loaded_elsewhere = False
        for pos in range(TRITS):
            for s_idx, ah, committed in pressure_at_pos(state, pos):
                if not committed and ah >= 4:
                    stats["h_all_positions"][pos].append(ah)
                    if pos != 3:
                        found_loaded_elsewhere = True

        if has_loaded_3:
            stats["preserved"] += 1
        elif found_loaded_elsewhere:
            stats["relocated"] += 1
        else:
            stats["destroyed"] += 1

        stats["trials"] += 1

        if len(stats["sample_trials"]) < 5:
            stats["sample_trials"].append({
                "n_composed": n_compose,
                "parents": [m.label for m in motifs_chosen],
                "h_pos3": h_3,
                "preserved": has_loaded_3,
                "relocated": found_loaded_elsewhere and not has_loaded_3,
            })

    n = max(stats["trials"], 1)
    stats["preservation_rate"] = round(stats["preserved"] / n, 4)
    stats["destruction_rate"] = round(stats["destroyed"] / n, 4)
    stats["relocation_rate"] = round(stats["relocated"] / n, 4)

    # Compress h_all_positions
    stats["h_all_positions"] = {
        pos: {"count": len(vals), "mean": round(sum(vals) / len(vals), 2)}
        for pos, vals in stats["h_all_positions"].items()
    }
    del stats["h_pos3_values"]

    print(f"    Trials: {stats['trials']}")
    print(f"    Preserved: {stats['preserved']} ({stats['preservation_rate']*100:.1f}%)")
    print(f"    Destroyed: {stats['destroyed']} ({stats['destruction_rate']*100:.1f}%)")
    print(f"    Relocated: {stats['relocated']} ({stats['relocation_rate']*100:.1f}%)")
    print(f"    Null collapses: {stats['null_collapses']}")

    return stats


# ======================================================================
# FEED-CHAR RULE SWEEP
# ======================================================================

def find_sequencing_starters(k, n=10):
    """Find starters that produced multi-step sequences in exp06-style testing.
    These are word-domain motifs with rich char_counts and successors."""
    candidates = []
    for m in k.motifs.values():
        if m.domain == "D3" and m.char_counts and m.successors:
            richness = len(m.char_counts) + len(m.successors)
            candidates.append((richness, m))
    candidates.sort(key=lambda x: -x[0])
    return [m for _, m in candidates[:n]]


def feed_char_rule_sweep(k, rng, starters, max_steps=50):
    """Run 4 feed_char rules on each starter for 50 steps."""
    print("\n  === Feed-Char Rule Sweep ===")

    if not starters:
        # Fall back to any D3 motifs
        starters = [m for m in k.motifs.values() if m.domain == "D3"][:10]
    if not starters:
        print("    SKIP: no starters found")
        return {"skipped": True}

    print(f"    Starters: {len(starters)}")

    rules = ["R1", "R2", "R3", "R4"]
    all_results = {}

    for rule in rules:
        print(f"\n    --- Rule {rule} ---")
        rule_results = []

        for starter in starters:
            state = starter.state
            words_emitted = []
            prev_state = None
            orbit_fps = []

            for step in range(max_steps):
                strands = [state[j * TRITS:(j + 1) * TRITS] for j in range(CONTEXT)]
                settled = settle(strands, BARRIER)

                if settled == prev_state:
                    break  # fixed point
                if all(t_val == 0 for t_val in settled):
                    break

                recalled, score = k.recall_global(settled)
                if recalled is None:
                    break

                orbit_fps.append(recalled.fp)
                word = recalled.label if recalled.label else "?"
                words_emitted.append(word)

                prev_state = settled

                # Apply feed_char rule to get next character
                next_ch = None

                if rule == "R1":
                    # First char of most common word in char_counts
                    if recalled.char_counts:
                        top = max(recalled.char_counts, key=recalled.char_counts.get)
                        if top and len(top) > 0:
                            next_ch = top[0]

                elif rule == "R2":
                    # Sampled from char_counts distribution
                    if recalled.char_counts:
                        items = list(recalled.char_counts.items())
                        total = sum(v for _, v in items)
                        r = rng.random() * total
                        cum = 0
                        for label, cnt in items:
                            cum += cnt
                            if cum >= r:
                                next_ch = label[0] if label else None
                                break

                elif rule == "R3":
                    # From successor motif's char_counts
                    if recalled.successors:
                        succ_fp = max(recalled.successors, key=recalled.successors.get)
                        succ = k.motifs.get(succ_fp)
                        if succ and succ.char_counts:
                            top = max(succ.char_counts, key=succ.char_counts.get)
                            if top and len(top) > 0:
                                next_ch = top[0]

                elif rule == "R4":
                    # Structural-similarity recall on partial (shifted) state
                    partial = settled[TRITS:]  # drop first strand
                    partial += tuple([0] * TRITS)  # pad with nulls
                    partial_recalled, _ = k.recall_global(partial)
                    if partial_recalled and partial_recalled.char_counts:
                        top = max(partial_recalled.char_counts,
                                  key=partial_recalled.char_counts.get)
                        if top and len(top) > 0:
                            next_ch = top[0]

                if next_ch is None or not next_ch.isalpha():
                    next_ch = 'a'  # fallback (content-agnostic)

                # Shift left, append right
                new_strand = encode(next_ch)
                state = settled[TRITS:] + tuple(new_strand)

            # Compute orbit depth
            unique_fps = len(set(orbit_fps))
            fp_counter = Counter(orbit_fps)
            max_repeat = max(fp_counter.values()) if fp_counter else 0

            distinct_words = len(set(words_emitted))
            fixed_point = len(words_emitted) < max_steps

            result = {
                "starter": starter.label,
                "starter_chi": starter.chi_val,
                "steps": len(words_emitted),
                "distinct_words": distinct_words,
                "output_preview": " ".join(words_emitted[:20]),
                "fixed_point": fixed_point,
                "orbit_depth": unique_fps,
                "max_repeat": max_repeat,
            }
            rule_results.append(result)

            if distinct_words > 1:
                print(f"      [{starter.label}] steps={len(words_emitted)} "
                      f"distinct={distinct_words} orbit={unique_fps}")

        all_results[rule] = rule_results

        # Summary
        total_distinct = sum(r["distinct_words"] for r in rule_results)
        avg_steps = sum(r["steps"] for r in rule_results) / max(len(rule_results), 1)
        fp_count = sum(1 for r in rule_results if r["fixed_point"])
        print(f"    Summary: avg_steps={avg_steps:.1f} total_distinct_words={total_distinct} "
              f"fixed_points={fp_count}/{len(rule_results)}")

    return all_results


# ======================================================================
# MAIN
# ======================================================================

def main():
    t_start = time.time()
    rng = random.Random(SEED)

    results = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "precommit_hash": "0fbb36f",
        "config": {
            "TRITS": TRITS, "CONTEXT": CONTEXT, "POP": POP,
            "BARRIER": BARRIER, "SEED": SEED,
            "P3I_3": P3I[3], "P3I_3_half": P3I[3] // 2,
            "D4_POSITIONS": D4_POSITIONS,
            "D5_POSITIONS": D5_POSITIONS,
        },
        "crashes": [],
    }

    # ── Load corpus ─────────────────────────────────────────────
    corpus_files = sorted(glob.glob("corpus/*.md")) + sorted(glob.glob("corpus/*.txt"))
    corpus_text = ""
    for path in corpus_files:
        try:
            with open(path, encoding="utf-8", errors="ignore") as f:
                corpus_text += f.read() + " "
        except Exception as e:
            results["crashes"].append(f"corpus load {path}: {e}")

    results["corpus"] = {
        "files": len(corpus_files),
        "total_chars": len(corpus_text),
        "total_words": len(corpus_text.split()),
    }
    print(f"Corpus: {len(corpus_files)} files, {len(corpus_text)} chars")

    k = Krimelack()

    # ── STEP 1: Pre-load D4 and D5 ────────────────────────────
    print("\n=== STEP 1: Pre-load D4 (syntactic) and D5 (communication) ===")

    t0 = time.time()
    d4_stats = preload_primitives(k, "D4", D4_POSITIONS, rng, target=2000)
    d4_time = time.time() - t0
    results["D4_preload"] = d4_stats
    results["D4_preload"]["time_seconds"] = round(d4_time, 2)
    print(f"  D4: {d4_stats['total_new']} new motifs in {d4_time:.1f}s "
          f"(s={d4_stats['singletons']} p={d4_stats['pairs']} "
          f"t={d4_stats['triples']} q={d4_stats['quads']})")

    t0 = time.time()
    d5_stats = preload_primitives(k, "D5", D5_POSITIONS, rng, target=2000)
    d5_time = time.time() - t0
    results["D5_preload"] = d5_stats
    results["D5_preload"]["time_seconds"] = round(d5_time, 2)
    print(f"  D5: {d5_stats['total_new']} new motifs in {d5_time:.1f}s "
          f"(s={d5_stats['singletons']} p={d5_stats['pairs']} "
          f"t={d5_stats['triples']} q={d5_stats['quads']})")

    ingestion_hash = hashlib.sha1(
        json.dumps({"D4": d4_stats, "D5": d5_stats}).encode()
    ).hexdigest()[:12]
    results["ingestion_hash"] = ingestion_hash
    print(f"  Ingestion hash: {ingestion_hash}")

    # ── Mechanical failure check ────────────────────────────────
    if d4_stats["total_new"] < 50 or d5_stats["total_new"] < 50:
        print(f"\n  MECHANICAL FAILURE: D4={d4_stats['total_new']}, "
              f"D5={d5_stats['total_new']} < 50")
        print(f"  Fallback would halve barrier to 52. Stopping.")
        results["mechanical_failure"] = True
        with open(RESULTS_FILE, "w") as f:
            f.write(json.dumps(results, indent=2))
        return

    # ── STEP 2: Ingest D1 (char-context) ──────────────────────
    print("\n=== STEP 2: Ingest D1 (char-context via Loom) ===")
    t0 = time.time()
    loom = Loom(k)
    loom.feed(corpus_text)
    d1_time = time.time() - t0
    d1_size = k.size(domain="D1")
    results["D1_ingestion"] = {
        "motifs": d1_size,
        "time_seconds": round(d1_time, 2),
    }
    print(f"  D1: {d1_size} motifs in {d1_time:.1f}s")

    # ── STEP 3: Ingest D2 (morpheme) ─────────────────────────
    print("\n=== STEP 3: Ingest D2 (morpheme) ===")
    t0 = time.time()
    d2_stats = ingest_morphemes(k, corpus_text)
    d2_time = time.time() - t0
    results["D2_ingestion"] = d2_stats
    results["D2_ingestion"]["time_seconds"] = round(d2_time, 2)
    print(f"  D2: {d2_stats['new']} new motifs from {d2_stats['unique_morphemes']} "
          f"morphemes in {d2_time:.1f}s")

    # ── STEP 4: Ingest D3 (word) ─────────────────────────────
    print("\n=== STEP 4: Ingest D3 (word) ===")
    t0 = time.time()
    d3_stats = ingest_words(k, corpus_text)
    d3_time = time.time() - t0
    results["D3_ingestion"] = d3_stats
    results["D3_ingestion"]["time_seconds"] = round(d3_time, 2)
    print(f"  D3: {d3_stats['new']} new motifs from {d3_stats['unique_words']} "
          f"words in {d3_time:.1f}s")

    # ── STEP 5: Snapshot chi distributions ────────────────────
    print("\n=== Post-ingestion snapshot ===")
    chi_snapshot = {}
    for d in ["D1", "D2", "D3", "D4", "D5"]:
        dist = k.chi_distribution(domain=d)
        chi_snapshot[d] = {
            "count": k.size(domain=d),
            "chi_range": [min(dist.keys()), max(dist.keys())] if dist else [0, 0],
            "chi_classes": len(dist),
            "distribution": dist,
        }
        print(f"  {d}: {chi_snapshot[d]['count']} motifs, "
              f"chi [{chi_snapshot[d]['chi_range'][0]}, {chi_snapshot[d]['chi_range'][1]}], "
              f"{chi_snapshot[d]['chi_classes']} classes")
    results["chi_snapshot_post_ingestion"] = chi_snapshot
    print(f"  Total: {k.size()} motifs")

    # ── Initial vitals ────────────────────────────────────────
    vitals_init = collect_vitals(k, 0)
    print(f"  Initial vitals: {vitals_init['total_motifs']} motifs, "
          f"{vitals_init['chi_classes']} chi classes")

    # ── COMPOSITION TRIALS ────────────────────────────────────
    print("\n=== COMPOSITION TRIALS (500 x 10 pairings) ===")
    t0 = time.time()
    try:
        comp_results, vitals_log = run_composition_trials(k, rng)
        comp_time = time.time() - t0
        results["composition_trials"] = comp_results
        results["composition_time_seconds"] = round(comp_time, 2)
        results["vitals_log"] = [vitals_init] + vitals_log
        print(f"\n  Composition trials completed in {comp_time:.1f}s")

        # Overall novelty summary
        total_comp_novel = sum(
            v.get("compositional_novel", 0)
            for v in comp_results.values() if isinstance(v, dict))
        total_geo_novel = sum(
            v.get("geometric_novel", 0)
            for v in comp_results.values() if isinstance(v, dict))
        total_trials = sum(
            v.get("trials", 0)
            for v in comp_results.values() if isinstance(v, dict))
        print(f"  Overall: {total_comp_novel} compositional novel, "
              f"{total_geo_novel} geometric novel out of {total_trials} trials")
    except Exception as e:
        tb = traceback.format_exc()
        results["crashes"].append(f"composition_trials: {tb}")
        print(f"  CRASHED: {e}")
        comp_results = {}

    # ── LOADED-NULL SUB-TEST ──────────────────────────────────
    print("\n=== LOADED-NULL PRESERVATION SUB-TEST ===")
    t0 = time.time()
    try:
        loaded_results = run_loaded_null_test(k, rng, trials=200)
        loaded_time = time.time() - t0
        results["loaded_null_test"] = loaded_results
        results["loaded_null_test"]["time_seconds"] = round(loaded_time, 2)
    except Exception as e:
        tb = traceback.format_exc()
        results["crashes"].append(f"loaded_null_test: {tb}")
        print(f"  CRASHED: {e}")

    # ── FEED-CHAR RULE SWEEP ──────────────────────────────────
    print("\n=== FEED-CHAR RULE SWEEP ===")
    t0 = time.time()
    try:
        starters = find_sequencing_starters(k, n=10)
        print(f"  Found {len(starters)} sequencing starters")
        fc_results = feed_char_rule_sweep(k, rng, starters, max_steps=50)
        fc_time = time.time() - t0
        results["feed_char_sweep"] = fc_results
        results["feed_char_sweep_time"] = round(fc_time, 2)
    except Exception as e:
        tb = traceback.format_exc()
        results["crashes"].append(f"feed_char_sweep: {tb}")
        print(f"  CRASHED: {e}")

    # ── Post-trial chi snapshot ───────────────────────────────
    print("\n=== Post-trial snapshot ===")
    chi_post = {}
    for d in ["D1", "D2", "D3", "D4", "D5", "dream"]:
        dist = k.chi_distribution(domain=d)
        chi_post[d] = {
            "count": k.size(domain=d),
            "chi_classes": len(dist),
        }
    results["chi_snapshot_post_trial"] = chi_post
    print(f"  Total: {k.size()} motifs (dream: {k.size(domain='dream')})")

    # ── Final vitals ──────────────────────────────────────────
    vitals_final = collect_vitals(k, -1)
    results["vitals_final"] = vitals_final

    # ── Write results ─────────────────────────────────────────
    total_time = time.time() - t_start
    results["total_time_seconds"] = round(total_time, 2)

    with open(RESULTS_FILE, "w") as f:
        f.write(json.dumps(results, indent=2, default=str))
    print(f"\nWritten to {RESULTS_FILE}")
    print(f"Total time: {total_time:.1f}s")
    print(f"Crashes: {len(results['crashes'])}")
    if results["crashes"]:
        for c in results["crashes"]:
            print(f"  {c[:200]}")


if __name__ == "__main__":
    main()
