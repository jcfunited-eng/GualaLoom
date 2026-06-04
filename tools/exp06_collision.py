"""
Experiment 06 — Three-Layer Collision Build (pass 4)

Fixes seven cheats from pass 3:
  1. Word/char fingerprint domains separated
  2. Word motifs settled from word chars alone (no context contamination)
  3. Composition pairs selected by chi dissimilarity, not co-commit count
  4. feed_char sequences by shift-left append-right
  5. feed_char draws next char from recalled motif's char_counts
  6. null_pos03 replaced with null_high (positions 13-15)
  7. Starters sampled across chi distribution, not by weight
"""

import os, sys, json, hashlib, time, traceback, glob, random
from collections import OrderedDict, defaultdict, Counter

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(REPO)

RESULTS_DIR = os.path.join(REPO, "experiments", "exp06_collision")
RESULTS_FILE = os.path.join(RESULTS_DIR, "results.jsonl")
os.makedirs(RESULTS_DIR, exist_ok=True)

TRITS = 16
CONTEXT = 16
POP = TRITS * CONTEXT  # 256
DEAD_ZONE = 15

P3I = tuple(3**i for i in range(TRITS))


def encode(ch):
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


def settle(strands, familiarity):
    barrier = DEAD_ZONE + familiarity
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


def _state_string(state):
    return "".join({-1: "-", 0: "0", 1: "+"}[t] for t in state)


def _fp_char(state):
    """Fingerprint in the character domain."""
    return hashlib.sha1(("C:" + _state_string(state)).encode()).hexdigest()[:12]


def _fp_word(state):
    """Fingerprint in the word domain."""
    return hashlib.sha1(("W:" + _state_string(state)).encode()).hexdigest()[:12]


def _fp_raw(state):
    """Raw fingerprint (no domain prefix) for cross-domain collision check."""
    return _state_string(state)


def count_nulls(state):
    return sum(1 for t in state if t == 0)


# ======================================================================
# Krimelack with separate char and word motif stores
# ======================================================================

class Motif:
    __slots__ = ("fp", "state", "weight", "age", "chi", "V",
                 "char_counts", "successors", "word", "domain")
    def __init__(self, fp, state, c, v, domain="char"):
        self.fp = fp; self.state = state; self.weight = 1; self.age = 0
        self.chi = c; self.V = v
        self.char_counts = defaultdict(int)
        self.successors = defaultdict(int)
        self.word = None
        self.domain = domain

    def to_dict(self):
        return {"fp": self.fp, "state": list(self.state),
                "weight": self.weight, "age": self.age, "chi": self.chi,
                "V": self.V, "char_counts": dict(self.char_counts),
                "successors": dict(self.successors),
                "word": self.word, "domain": self.domain}


class Krimelack:
    def __init__(self):
        self.char_motifs = OrderedDict()
        self.word_motifs = OrderedDict()
        self._last_char_fp = None
        self._last_word_fp = None

    def commit_char(self, state, active_char=None):
        if all(t == 0 for t in state):
            return None, False
        fp = _fp_char(state)
        new = fp not in self.char_motifs
        if new:
            c, v = chi(state)
            self.char_motifs[fp] = Motif(fp, state, c, v, domain="char")
        m = self.char_motifs[fp]
        m.weight += 1; m.age = 0
        if active_char is not None:
            m.char_counts[active_char] += 1
        if self._last_char_fp and self._last_char_fp != fp and self._last_char_fp in self.char_motifs:
            self.char_motifs[self._last_char_fp].successors[fp] += 1
        self._last_char_fp = fp
        return fp, new

    def commit_word(self, state, word=None):
        if all(t == 0 for t in state):
            return None, False
        fp = _fp_word(state)
        new = fp not in self.word_motifs
        if new:
            c, v = chi(state)
            self.word_motifs[fp] = Motif(fp, state, c, v, domain="word")
        m = self.word_motifs[fp]
        m.weight += 1; m.age = 0
        if word is not None:
            if m.word is None:
                m.word = word
            # Track all words that map here
            m.char_counts[word] = m.char_counts.get(word, 0) + 1
        if self._last_word_fp and self._last_word_fp != fp and self._last_word_fp in self.word_motifs:
            self.word_motifs[self._last_word_fp].successors[fp] += 1
        self._last_word_fp = fp
        return fp, new

    def recall_from(self, state, motif_store):
        """Recall from a specific motif store (char_motifs or word_motifs)."""
        if not motif_store:
            return None, 0
        qchi, _ = chi(state)
        pool = [m for m in motif_store.values() if m.chi == qchi]
        if not pool:
            pool = list(motif_store.values())
        best, best_score = None, -1
        for m in pool:
            score = sum(1 for a, b in zip(state, m.state) if a == b and a != 0)
            score = score * 100 + min(m.weight, 99)
            if score > best_score:
                best, best_score = m, score
        return best, best_score

    def recall_word(self, state):
        return self.recall_from(state, self.word_motifs)

    def recall_char(self, state):
        return self.recall_from(state, self.char_motifs)

    def char_size(self):
        return len(self.char_motifs)

    def word_size(self):
        return len(self.word_motifs)


# ======================================================================
# Loom at CONTEXT=16 (commits to char domain only)
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
        settled = settle(strands, self.fam)
        m, score = self.k.recall_from(settled, self.k.char_motifs)
        self.fam = (score // 100 * 20) // max(len(settled), 1) if score > 0 else 0
        self.k.commit_char(settled, active_char=ch)
        self.last = settled
        return settled

    def feed(self, text):
        for ch in text:
            self.tick(ch)


# ======================================================================
# LAYER 3 — Word-Mosaic (word chars settled alone, no context)
# ======================================================================

def settle_word_alone(word):
    """Settle a word's characters as strands with no context window.
    Words shorter than CONTEXT get null-strand padding.
    Words longer than CONTEXT use the FIRST CONTEXT chars."""
    chars = list(word.lower())
    if len(chars) > CONTEXT:
        chars = chars[:CONTEXT]
    strands = [encode(c) for c in chars]
    while len(strands) < CONTEXT:
        strands.append(tuple([0] * TRITS))
    return settle(strands, 0)


def word_mosaic_ingest(k, corpus_text):
    """Run character Loom normally. At whitespace boundaries, ALSO settle
    the completed word alone (no context) and commit to the word domain."""

    stats = {
        "total_words": 0,
        "unique_words": set(),
        "word_motifs_committed": 0,
        "word_motifs_new": 0,
        "word_null_collapses": 0,
        "char_motifs_total": 0,
        "errors": [],
    }

    loom = Loom(k)
    current_word_chars = []

    for ch in corpus_text:
        if ch in (' ', '\t', '\n', '\r'):
            if current_word_chars:
                word = "".join(current_word_chars).lower()
                stats["total_words"] += 1
                stats["unique_words"].add(word)

                # Settle the word ALONE — no context contamination
                word_state = settle_word_alone(word)
                if all(t == 0 for t in word_state):
                    stats["word_null_collapses"] += 1
                else:
                    fp, new = k.commit_word(word_state, word=word)
                    if fp is not None:
                        stats["word_motifs_committed"] += 1
                        if new:
                            stats["word_motifs_new"] += 1

                current_word_chars = []

            loom.tick(ch)
            stats["char_motifs_total"] += 1
        else:
            current_word_chars.append(ch)
            loom.tick(ch)
            stats["char_motifs_total"] += 1

    if current_word_chars:
        word = "".join(current_word_chars).lower()
        stats["total_words"] += 1
        stats["unique_words"].add(word)
        word_state = settle_word_alone(word)
        if not all(t == 0 for t in word_state):
            fp, new = k.commit_word(word_state, word=word)
            if fp is not None:
                stats["word_motifs_committed"] += 1
                if new:
                    stats["word_motifs_new"] += 1

    stats["unique_words"] = len(stats["unique_words"])
    return stats, loom


# ======================================================================
# Cross-domain collision analysis (cheat 1 diagnostic)
# ======================================================================

def cross_domain_analysis(k):
    """How many word states exactly match char states?"""
    char_raw = {_state_string(m.state) for m in k.char_motifs.values()}
    word_raw = {}
    for m in k.word_motifs.values():
        word_raw[_state_string(m.state)] = m

    collisions = 0
    unique_to_word = 0
    for raw, m in word_raw.items():
        if raw in char_raw:
            collisions += 1
        else:
            unique_to_word += 1

    return {
        "total_word_motifs": len(word_raw),
        "total_char_motifs": len(char_raw),
        "word_states_matching_char_states": collisions,
        "word_states_unique_to_word_domain": unique_to_word,
        "collision_rate": round(collisions / max(len(word_raw), 1), 4),
    }


def word_stability_analysis(k, corpus_text):
    """For words appearing multiple times, how many distinct word motif
    states does each get?"""
    words = corpus_text.lower().split()
    word_counts = Counter(words)
    multi_words = [w for w, c in word_counts.items() if c >= 3][:50]

    results = {}
    for word in multi_words:
        state = settle_word_alone(word)
        fp = _fp_word(state)
        # Word settled alone is deterministic — same word always produces
        # same state (no context). So the question is: does settle_word_alone
        # produce the same state every time for the same word?
        # (It must, since encode and settle are deterministic.)
        # The real question is: do DIFFERENT words produce different states?
        results[word] = {
            "count_in_corpus": word_counts[word],
            "fp": fp,
            "null_fraction": round(count_nulls(state) / POP, 4),
        }

    # Group by fp to find words sharing a motif
    fp_groups = defaultdict(list)
    for word, info in results.items():
        fp_groups[info["fp"]].append(word)
    shared = {fp: words for fp, words in fp_groups.items() if len(words) > 1}

    return {
        "words_sampled": len(multi_words),
        "distinct_fps": len(fp_groups),
        "fps_shared_by_multiple_words": len(shared),
        "shared_examples": {fp: words[:10] for fp, words in list(shared.items())[:10]},
    }


# ======================================================================
# LAYER 2 — Folding Composition (chi-dissimilar pairs from word domain)
# ======================================================================

def fold_compose(state_a, state_b):
    """Union with conflict-nulling."""
    merged = []
    for a, b in zip(state_a, state_b):
        if a == b:
            merged.append(a)
        elif a != 0 and b != 0:
            merged.append(0)
        elif a != 0:
            merged.append(a)
        else:
            merged.append(b)
    merged = tuple(merged)

    strands = [merged[j * TRITS:(j + 1) * TRITS] for j in range(CONTEXT)]
    settled = settle(strands, 0)
    return merged, settled


def run_folding_composition(k):
    """Compose 50 pairs of word motifs selected for chi dissimilarity."""
    stats = {
        "pairs_attempted": 0,
        "stable_compositions": 0,
        "collapsed_to_null": 0,
        "recalls_to_parent_a": 0,
        "recalls_to_parent_b": 0,
        "recalls_to_novel": 0,
        "recalls_to_other_existing": 0,
        "errors": [],
        "compositions": [],
    }

    # Group word motifs by chi
    by_chi = defaultdict(list)
    for fp, m in k.word_motifs.items():
        by_chi[m.chi].append(m)

    chi_bins = sorted(by_chi.keys())
    if len(chi_bins) < 2:
        stats["errors"].append("fewer than 2 chi bins in word motifs")
        return stats

    # Build pairs: maximize chi spread between parents
    pairs = []
    rng = random.Random(6666)
    for i, chi_a in enumerate(chi_bins):
        for chi_b in chi_bins[i+1:]:
            if abs(chi_a - chi_b) >= 3:  # minimum spread
                ma = rng.choice(by_chi[chi_a])
                mb = rng.choice(by_chi[chi_b])
                pairs.append((abs(chi_a - chi_b), ma.fp, mb.fp, ma, mb))

    pairs.sort(key=lambda x: -x[0])  # highest spread first
    pairs = pairs[:50]

    for spread, _fpa, _fpb, ma, mb in pairs:
        stats["pairs_attempted"] += 1
        try:
            merged, settled = fold_compose(ma.state, mb.state)
            all_null = all(t == 0 for t in settled)

            comp = {
                "parent_a_fp": ma.fp,
                "parent_b_fp": mb.fp,
                "parent_a_word": ma.word,
                "parent_b_word": mb.word,
                "chi_spread": spread,
                "chi_a": ma.chi,
                "chi_b": mb.chi,
                "parent_a_null_fraction": round(count_nulls(ma.state) / POP, 4),
                "parent_b_null_fraction": round(count_nulls(mb.state) / POP, 4),
                "merged_null_fraction": round(count_nulls(merged) / POP, 4),
                "settled_null_fraction": round(count_nulls(settled) / POP, 4),
                "collapsed_to_null": all_null,
            }

            if all_null:
                stats["collapsed_to_null"] += 1
                comp["chi_composed"] = 0
            else:
                c, v = chi(settled)
                comp["chi_composed"] = c
                comp["settled_fp"] = _fp_word(settled)

                # Recall from word motifs
                best, score = k.recall_word(settled)
                comp["recalls_to_fp"] = best.fp if best else None
                comp["recalls_to_word"] = best.word if best else None

                if best is None:
                    comp["recall_class"] = "none"
                elif best.fp == ma.fp:
                    comp["recall_class"] = "parent_a"
                    stats["recalls_to_parent_a"] += 1
                elif best.fp == mb.fp:
                    comp["recall_class"] = "parent_b"
                    stats["recalls_to_parent_b"] += 1
                else:
                    # Is the recalled motif a KNOWN word motif?
                    if best.fp in k.word_motifs:
                        comp["recall_class"] = "other_existing"
                        stats["recalls_to_other_existing"] += 1
                    else:
                        comp["recall_class"] = "novel"
                        stats["recalls_to_novel"] += 1

                # Does chi_composed fall between parents?
                chi_lo = min(ma.chi, mb.chi)
                chi_hi = max(ma.chi, mb.chi)
                comp["chi_between_parents"] = chi_lo <= c <= chi_hi

                stats["stable_compositions"] += 1

            stats["compositions"].append(comp)
        except Exception as e:
            stats["errors"].append(f"{ma.fp}+{mb.fp}: {str(e)}")

    return stats


# ======================================================================
# Generation — three honest perturbation strategies
# ======================================================================

def generate_settle(k, start_fp, perturb_mode, max_steps=50):
    """Faithful cascade-based generation from word motifs.

    perturb_mode:
      "null_pos0" — null only position 0 in each strand (6%)
      "null_high" — null positions 13-15 in each strand (~19%)
      "feed_char" — shift-left, append-right with substrate-derived char
    """
    out = []
    trace = []

    m = k.word_motifs.get(start_fp)
    if m is None:
        return "", []

    state = m.state
    prev_state = None

    for step in range(max_steps):
        strands = [state[j * TRITS:(j + 1) * TRITS] for j in range(CONTEXT)]
        settled = settle(strands, 0)

        if settled == prev_state:
            trace.append({"step": step, "event": "fixed_point",
                          "null_fraction": round(count_nulls(settled) / POP, 4)})
            break

        if all(t == 0 for t in settled):
            trace.append({"step": step, "event": "all_null_collapse"})
            break

        # Recall from word motifs
        recalled, score = k.recall_word(settled)
        if recalled is None:
            trace.append({"step": step, "event": "recall_failed"})
            out.append("?")
        else:
            word = recalled.word if recalled.word else "?"
            out.append(word)
            trace.append({
                "step": step, "event": "emit",
                "word": word, "fp": recalled.fp,
                "chi": recalled.chi, "score": score,
                "null_fraction": round(count_nulls(settled) / POP, 4),
            })

        prev_state = settled

        # Perturbation
        if perturb_mode == "null_pos0":
            perturbed = list(settled)
            for s in range(CONTEXT):
                perturbed[s * TRITS + 0] = 0
            state = tuple(perturbed)

        elif perturb_mode == "null_high":
            perturbed = list(settled)
            for s in range(CONTEXT):
                for i in range(13, 16):  # positions 13, 14, 15
                    perturbed[s * TRITS + i] = 0
            state = tuple(perturbed)

        elif perturb_mode == "feed_char":
            # Determine next char from the substrate's own state
            next_ch = '?'
            if recalled is not None and recalled.char_counts:
                # char_counts on word motifs stores word→count, not char→count
                # So use the first char of the most common word
                top_word = max(recalled.char_counts, key=recalled.char_counts.get)
                if top_word and len(top_word) > 0:
                    next_ch = top_word[0]
            new_strand = encode(next_ch)
            # Shift left, append right (architectural sequencing)
            state = settled[TRITS:] + tuple(new_strand)

        if all(t == 0 for t in state):
            trace.append({"step": step + 1, "event": "perturbation_collapsed"})
            break

    return " ".join(out), trace


# ======================================================================
# Starter selection by chi distribution (cheat 7 fix)
# ======================================================================

def select_starters_by_chi(k, n=10):
    """Pick one word motif from each of the n most-populated chi bins."""
    by_chi = defaultdict(list)
    for m in k.word_motifs.values():
        by_chi[m.chi].append(m)

    # Sort bins by population, take top n
    bins = sorted(by_chi.items(), key=lambda kv: -len(kv[1]))[:n]

    rng = random.Random(1234)
    starters = []
    for chi_val, motifs in bins:
        starters.append(rng.choice(motifs))
    return starters


# ======================================================================
# MAIN
# ======================================================================

def main():
    results = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "pass": "fourth",
        "config": {
            "TRITS": TRITS, "CONTEXT": CONTEXT, "POP": POP,
            "DEAD_ZONE": DEAD_ZONE,
        },
        "crashes": [],
    }

    # ── Load corpus ──────────────────────────────────────────────────
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
    print(f"Corpus: {len(corpus_files)} files, {len(corpus_text)} chars, "
          f"{len(corpus_text.split())} words")

    # ── LAYER 3: Word-mosaic ────────────────────────────────────────
    print("\n=== LAYER 3: Word-mosaic (word settled alone, separate domain) ===")
    k = Krimelack()
    t0 = time.time()
    try:
        ingest_stats, loom = word_mosaic_ingest(k, corpus_text)
        ingest_time = time.time() - t0
        ingest_stats["time_seconds"] = round(ingest_time, 2)
        results["word_mosaic_ingestion"] = ingest_stats
        print(f"  Completed in {ingest_time:.1f}s")
        print(f"  Words: {ingest_stats['total_words']} "
              f"(unique: {ingest_stats['unique_words']})")
        print(f"  Word motifs: {ingest_stats['word_motifs_committed']} committed, "
              f"{ingest_stats['word_motifs_new']} new")
        print(f"  Word null collapses: {ingest_stats['word_null_collapses']}")
        print(f"  Char motifs: {k.char_size()} unique")
    except Exception as e:
        tb = traceback.format_exc()
        results["crashes"].append(f"word_mosaic_ingestion: {tb}")
        print(f"  CRASHED: {e}")
        loom = None

    # ── Cross-domain analysis ────────────────────────────────────────
    if k.word_size() > 0 and k.char_size() > 0:
        print("\n=== Cross-domain collision analysis ===")
        xd = cross_domain_analysis(k)
        results["cross_domain"] = xd
        print(f"  Word motifs: {xd['total_word_motifs']}")
        print(f"  Char motifs: {xd['total_char_motifs']}")
        print(f"  Word states matching char states: {xd['word_states_matching_char_states']} "
              f"({xd['collision_rate']*100:.1f}%)")
        print(f"  Word states unique to word domain: {xd['word_states_unique_to_word_domain']}")

    # ── Word stability analysis ──────────────────────────────────────
    if k.word_size() > 0:
        print("\n=== Word stability analysis ===")
        ws = word_stability_analysis(k, corpus_text)
        results["word_stability"] = ws
        print(f"  Words sampled: {ws['words_sampled']}")
        print(f"  Distinct fps: {ws['distinct_fps']}")
        print(f"  FPs shared by multiple words: {ws['fps_shared_by_multiple_words']}")
        if ws["shared_examples"]:
            for fp, words in list(ws["shared_examples"].items())[:5]:
                print(f"    {fp}: {words}")

    # ── Motif analysis ───────────────────────────────────────────────
    if k.word_size() > 0:
        print(f"\n=== Word motif analysis ===")
        chi_dist_w = Counter()
        for m in k.word_motifs.values():
            chi_dist_w[m.chi] += 1
        chi_dist_c = Counter()
        for m in k.char_motifs.values():
            chi_dist_c[m.chi] += 1
        results["chi_distribution_word"] = dict(sorted(chi_dist_w.items()))
        results["chi_distribution_char"] = dict(sorted(chi_dist_c.items()))
        print(f"  Word motifs: {k.word_size()}, chi range "
              f"[{min(chi_dist_w.keys())}, {max(chi_dist_w.keys())}]")
        print(f"  Char motifs: {k.char_size()}, chi range "
              f"[{min(chi_dist_c.keys())}, {max(chi_dist_c.keys())}]")

        nf_w = [count_nulls(m.state) / POP for m in k.word_motifs.values()]
        nf_c = [count_nulls(m.state) / POP for m in k.char_motifs.values()]
        results["null_fraction_word"] = {
            "mean": round(sum(nf_w) / len(nf_w), 4),
            "min": round(min(nf_w), 4), "max": round(max(nf_w), 4),
        }
        results["null_fraction_char"] = {
            "mean": round(sum(nf_c) / len(nf_c), 4),
            "min": round(min(nf_c), 4), "max": round(max(nf_c), 4),
        }
        print(f"  Word null fraction: mean={results['null_fraction_word']['mean']:.4f}")
        print(f"  Char null fraction: mean={results['null_fraction_char']['mean']:.4f}")

        print(f"  Word chi distribution (top):")
        for c in sorted(chi_dist_w.keys()):
            if chi_dist_w[c] >= 5:
                print(f"    chi={c:4d}: {chi_dist_w[c]:4d}")

    # ── Pressure landscape ───────────────────────────────────────────
    if k.word_size() > 0:
        print("\n=== Pressure landscape (word motifs) ===")
        sample = list(k.word_motifs.values())[:20]
        null_pressures = []
        for m in sample:
            strands = [m.state[j*TRITS:(j+1)*TRITS] for j in range(CONTEXT)]
            for s_idx, strand in enumerate(strands):
                for i in range(TRITS):
                    if m.state[s_idx * TRITS + i] == 0:
                        h = strand[i] * P3I[i]
                        for o_idx, other in enumerate(strands):
                            if o_idx != s_idx:
                                h += other[i] * P3I[i] // 2
                        null_pressures.append(abs(h))
        if null_pressures:
            bands = Counter()
            for ah in null_pressures:
                if ah <= 5: bands["0-5"] += 1
                elif ah <= 9: bands["6-9"] += 1
                elif ah <= 12: bands["10-12"] += 1
                elif ah <= 14: bands["13-14"] += 1
                else: bands["15+"] += 1
            results["pressure_word"] = {"n": len(null_pressures), "bands": dict(bands)}
            for band in ["0-5", "6-9", "10-12", "13-14", "15+"]:
                c = bands.get(band, 0)
                print(f"  {band}: {c} ({100*c/len(null_pressures):.1f}%)")

    # ── LAYER 2: Folding composition ─────────────────────────────────
    print("\n=== LAYER 2: Folding (chi-dissimilar word pairs) ===")
    if k.word_size() > 1:
        t0 = time.time()
        try:
            fold_stats = run_folding_composition(k)
            fold_time = time.time() - t0
            results["folding_composition"] = {
                k2: v2 for k2, v2 in fold_stats.items()
                if k2 != "compositions"
            }
            results["folding_composition"]["sample_compositions"] = (
                fold_stats["compositions"][:10])
            print(f"  Completed in {fold_time:.1f}s")
            print(f"  Pairs: {fold_stats['pairs_attempted']}")
            print(f"  Stable: {fold_stats['stable_compositions']}")
            print(f"  Collapsed: {fold_stats['collapsed_to_null']}")
            print(f"  Recalls to parent_a: {fold_stats['recalls_to_parent_a']}")
            print(f"  Recalls to parent_b: {fold_stats['recalls_to_parent_b']}")
            print(f"  Recalls to other existing: {fold_stats['recalls_to_other_existing']}")
            print(f"  Recalls to novel: {fold_stats['recalls_to_novel']}")

            for comp in fold_stats["compositions"][:8]:
                print(f"    {comp.get('parent_a_word','?')} (chi={comp['chi_a']}) + "
                      f"{comp.get('parent_b_word','?')} (chi={comp['chi_b']}): "
                      f"merged_null={comp['merged_null_fraction']:.2f} "
                      f"settled_null={comp['settled_null_fraction']:.2f} "
                      f"chi_composed={comp.get('chi_composed','null')} "
                      f"between={comp.get('chi_between_parents','?')} "
                      f"recall={comp.get('recall_class','?')} "
                      f"({comp.get('recalls_to_word','?')})")

        except Exception as e:
            tb = traceback.format_exc()
            results["crashes"].append(f"folding: {tb}")
            print(f"  CRASHED: {e}")

    # ── Generation ───────────────────────────────────────────────────
    print("\n=== Generation (settle-based, chi-distributed starters) ===")
    if k.word_size() > 0:
        starters = select_starters_by_chi(k, n=10)

        all_gen = {}
        for mode in ["null_pos0", "null_high", "feed_char"]:
            print(f"\n  --- mode: {mode} ---")
            gen_results = []
            for i, m in enumerate(starters):
                try:
                    output, trace = generate_settle(k, m.fp, mode, max_steps=50)
                    gen = {
                        "starter_fp": m.fp, "starter_word": m.word,
                        "starter_chi": m.chi, "starter_weight": m.weight,
                        "perturb_mode": mode,
                        "output": output,
                        "output_words": len(output.split()) if output else 0,
                        "steps": len(trace),
                        "termination": trace[-1]["event"] if trace else "no_steps",
                        "trace": trace,
                    }
                    gen_results.append(gen)
                    print(f"  [{i}] '{m.word}' (chi={m.chi}) "
                          f"-> {output[:100] if output else '(empty)'}")
                    print(f"       steps={len(trace)} "
                          f"end={trace[-1]['event'] if trace else '?'}")
                except Exception as e:
                    gen_results.append({
                        "starter_fp": m.fp, "starter_word": m.word,
                        "perturb_mode": mode, "crashed": True, "error": str(e),
                    })
                    print(f"  [{i}] CRASHED: {e}")
            all_gen[mode] = gen_results
        results["generation"] = all_gen

    # ── Write ────────────────────────────────────────────────────────
    with open(RESULTS_FILE, "w") as f:
        f.write(json.dumps(results, indent=2))
    print(f"\nWritten to {RESULTS_FILE}")
    print(f"Crashes: {len(results['crashes'])}")


if __name__ == "__main__":
    main()
