"""
Experiment 06 — Three-Layer Collision Build

Deliberate stress test: stack CONTEXT=16, folding composition, and
word-mosaic ingestion. Build once with best-guess parameters. No
tuning. No iteration. Capture everything that breaks.

NOT a build to ship. We are reading the wreckage.
"""

import os, sys, json, hashlib, time, traceback, glob
from collections import OrderedDict, defaultdict, Counter

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(REPO)

RESULTS_DIR = os.path.join(REPO, "experiments", "exp06_collision")
RESULTS_FILE = os.path.join(RESULTS_DIR, "results.jsonl")
os.makedirs(RESULTS_DIR, exist_ok=True)

# ======================================================================
# LAYER 1 — CONTEXT=16, 256-trit population
# ======================================================================

TRITS = 16
CONTEXT = 16
POP = TRITS * CONTEXT  # 256
DEAD_ZONE = 15  # unchanged, best-guess

# Extended P3I to 16 elements
P3I = tuple(3**i for i in range(TRITS))
# P3I = (1, 3, 9, 27, 81, 243, 729, 2187, 6561, 19683, 59049, 177147,
#         531441, 1594323, 4782969, 14348907)


def encode(ch):
    """Character -> 16-trit balanced ternary strand."""
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
    """Same settle math, CONTEXT=16 × TRITS=16."""
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
    """Euler characteristic, generalized for TRITS=16."""
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


def count_nulls(state):
    return sum(1 for t in state if t == 0)


# ======================================================================
# Krimelack (same structure, wider state)
# ======================================================================

class Motif:
    __slots__ = ("fp", "state", "weight", "age", "chi", "V",
                 "char_counts", "successors", "word")
    def __init__(self, fp, state, c, v):
        self.fp = fp; self.state = state; self.weight = 1; self.age = 0
        self.chi = c; self.V = v
        self.char_counts = defaultdict(int)
        self.successors = defaultdict(int)
        self.word = None  # for word-mosaic: the word that produced this motif

    def to_dict(self):
        return {"fp": self.fp, "state": list(self.state),
                "weight": self.weight, "age": self.age, "chi": self.chi,
                "V": self.V, "char_counts": dict(self.char_counts),
                "successors": dict(self.successors),
                "word": self.word}


class Krimelack:
    def __init__(self):
        self.motifs = OrderedDict()
        self.last_fp = None

    def commit(self, state, active_char=None, word=None):
        if all(t == 0 for t in state):
            return None, False
        fp = _fp(state)
        new = fp not in self.motifs
        if new:
            c, v = chi(state)
            self.motifs[fp] = Motif(fp, state, c, v)
        m = self.motifs[fp]
        m.weight += 1; m.age = 0
        if active_char is not None:
            m.char_counts[active_char] += 1
        if word is not None and m.word is None:
            m.word = word
        if self.last_fp and self.last_fp != fp and self.last_fp in self.motifs:
            self.motifs[self.last_fp].successors[fp] += 1
        self.last_fp = fp
        return fp, new

    def recall(self, state):
        if not self.motifs:
            return None, 0
        qchi, _ = chi(state)
        pool = [m for m in self.motifs.values() if m.chi == qchi]
        if not pool:
            pool = list(self.motifs.values())
        best, best_score = None, -1
        for m in pool:
            score = sum(1 for a, b in zip(state, m.state) if a == b and a != 0)
            score = score * 100 + min(m.weight, 99)
            if score > best_score:
                best, best_score = m, score
        return best, best_score

    def size(self):
        return len(self.motifs)


# ======================================================================
# Loom at CONTEXT=16
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
        m, score = self.k.recall(settled)
        self.fam = (score // 100 * 20) // max(len(settled), 1) if score > 0 else 0
        self.k.commit(settled, active_char=ch)
        self.last = settled
        return settled

    def feed(self, text):
        for ch in text:
            self.tick(ch)


# ======================================================================
# LAYER 3 — Word-Mosaic Ingestion
# ======================================================================

def word_mosaic_ingest(k, corpus_text):
    """Ingest corpus word-by-word instead of char-by-char.
    Accumulate characters until whitespace, then commit the whole
    word's character sequence as ONE motif.

    Best-guess: words > CONTEXT chars → truncate to rightmost CONTEXT.
    Words < CONTEXT → pad with previous word's tail.
    """
    stats = {
        "total_words": 0,
        "unique_words": set(),
        "motifs_committed": 0,
        "new_motifs": 0,
        "null_collapses": 0,
        "words_truncated": 0,
        "errors": [],
    }

    words = corpus_text.split()
    prev_tail = []  # previous word's character list for padding

    for word in words:
        stats["total_words"] += 1
        stats["unique_words"].add(word.lower())

        # Build character list for this word
        chars = list(word.lower())

        # Truncate if too long
        if len(chars) > CONTEXT:
            chars = chars[-CONTEXT:]
            stats["words_truncated"] += 1

        # Pad with previous word's tail if too short
        if len(chars) < CONTEXT and prev_tail:
            needed = CONTEXT - len(chars)
            padding = prev_tail[-needed:]
            chars = padding + chars

        # Still might be short on first word
        while len(chars) < CONTEXT:
            chars.insert(0, ' ')

        prev_tail = list(word.lower())

        # Encode all chars into strands
        try:
            strands = [encode(c) for c in chars[-CONTEXT:]]
            settled = settle(strands, 0)

            fp, new = k.commit(settled, word=word.lower())
            if fp is None:
                stats["null_collapses"] += 1
            else:
                stats["motifs_committed"] += 1
                if new:
                    stats["new_motifs"] += 1
        except Exception as e:
            stats["errors"].append(f"word={word}: {str(e)}")
            if len(stats["errors"]) > 20:
                stats["errors"].append("... (truncated)")
                break

    stats["unique_words"] = len(stats["unique_words"])
    return stats


# ======================================================================
# LAYER 2 — Folding Composition
# ======================================================================

def fold_compose(state_a, state_b):
    """Merge two motifs:
    - agree (same sign) → keep
    - disagree (different signs, or one null one committed) → null
    - both null → null
    Then settle the result."""
    merged = []
    for a, b in zip(state_a, state_b):
        if a == b:
            merged.append(a)
        elif a != 0 and b != 0 and a != b:
            merged.append(0)  # disagree
        elif a != 0 and b == 0:
            merged.append(0)  # one null
        elif a == 0 and b != 0:
            merged.append(0)  # one null
        else:
            merged.append(0)  # both null
    merged = tuple(merged)

    # Settle the merged state
    strands = [merged[j * TRITS:(j + 1) * TRITS] for j in range(CONTEXT)]
    settled = settle(strands, 0)
    return merged, settled


def run_folding_composition(k):
    """Find the highest co-commit pairs and compose them."""
    stats = {
        "pairs_attempted": 0,
        "stable_compositions": 0,
        "collapsed_to_null": 0,
        "scattered": 0,
        "errors": [],
        "compositions": [],
    }

    # Find top co-commit pairs from successors
    pairs = []
    for fp, m in k.motifs.items():
        for succ_fp, count in m.successors.items():
            if succ_fp in k.motifs:
                pairs.append((count, fp, succ_fp))
    pairs.sort(reverse=True)

    # Compose top 50 pairs
    for count, fp_a, fp_b in pairs[:50]:
        stats["pairs_attempted"] += 1
        try:
            ma = k.motifs[fp_a]
            mb = k.motifs[fp_b]
            merged, settled = fold_compose(ma.state, mb.state)

            merged_nulls = count_nulls(merged)
            settled_nulls = count_nulls(settled)
            all_null = all(t == 0 for t in settled)

            comp = {
                "parent_a": fp_a,
                "parent_b": fp_b,
                "co_commit_count": count,
                "merged_null_fraction": round(merged_nulls / POP, 4),
                "settled_null_fraction": round(settled_nulls / POP, 4),
                "collapsed_to_null": all_null,
                "chi_a": ma.chi,
                "chi_b": mb.chi,
            }

            if all_null:
                stats["collapsed_to_null"] += 1
                comp["chi_composed"] = 0
            else:
                c, v = chi(settled)
                comp["chi_composed"] = c
                comp["settled_fp"] = _fp(settled)

                # Check if parents are recoverable
                # (does the composed motif recall back to either parent?)
                best, score = k.recall(settled)
                comp["recalls_to"] = best.fp if best else None
                comp["recalls_to_parent"] = (
                    best.fp in (fp_a, fp_b) if best else False)

                stats["stable_compositions"] += 1

            stats["compositions"].append(comp)

        except Exception as e:
            stats["errors"].append(f"{fp_a}+{fp_b}: {str(e)}")

    return stats


# ======================================================================
# Generation from word motifs
# ======================================================================

def generate_from_word(k, start_fp, max_steps=50):
    """Faithful cascade-based generation. No successor walking.

    1. Start from the starting motif's full state.
    2. Each step: settle the current state at familiarity=0.
    3. Recall the settled state from krimelack. Emit the recalled motif's word.
    4. Perturb: null out the lowest-weight intra-strand positions (positions
       0-3 in each strand, since P3I[0..3] carry the least structural weight)
       to give the substrate room to move. Best-guess: null positions 0-3
       across all strands (64 of 256 trits = 25%).
    5. Repeat until fixed point, all-null, or max_steps.

    The successor counter is NOT referenced. This is settle dynamics only.
    """
    import random as _rng
    out = []
    trace = []  # detailed trace per step

    m = k.motifs.get(start_fp)
    if m is None:
        return "", []

    state = m.state
    prev_state = None

    for step in range(max_steps):
        # Settle the current state
        strands = [state[j * TRITS:(j + 1) * TRITS] for j in range(CONTEXT)]
        settled = settle(strands, 0)

        # Check for fixed point
        if settled == prev_state:
            trace.append({"step": step, "event": "fixed_point",
                          "null_fraction": round(count_nulls(settled) / POP, 4)})
            break

        # Check for all-null collapse
        if all(t == 0 for t in settled):
            trace.append({"step": step, "event": "all_null_collapse"})
            break

        # Recall from krimelack
        recalled, score = k.recall(settled)
        if recalled is None:
            trace.append({"step": step, "event": "recall_failed"})
            out.append("?")
        else:
            word = recalled.word if recalled.word else "?"
            out.append(word)
            trace.append({
                "step": step, "event": "emit",
                "word": word, "fp": recalled.fp,
                "chi": recalled.chi,
                "score": score,
                "null_fraction": round(count_nulls(settled) / POP, 4),
            })

        prev_state = settled

        # Perturb: null out positions 0-3 in each strand to give the
        # substrate room to move to a different state next step.
        # Best-guess: null the lowest-weight trit positions (0-3).
        perturbed = list(settled)
        for s in range(CONTEXT):
            for i in range(4):  # positions 0-3 (P3I = 1, 3, 9, 27)
                perturbed[s * TRITS + i] = 0
        state = tuple(perturbed)

        # Check if perturbation collapsed everything
        if all(t == 0 for t in state):
            trace.append({"step": step + 1, "event": "perturbation_collapsed"})
            break

    return " ".join(out), trace


# ======================================================================
# MAIN — Stack all three, capture everything
# ======================================================================

def main():
    results = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "config": {
            "TRITS": TRITS, "CONTEXT": CONTEXT, "POP": POP,
            "DEAD_ZONE": DEAD_ZONE,
            "P3I": list(P3I),
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

    # ── LAYER 3: Word-mosaic ingestion at CONTEXT=16 ─────────────────
    print("\n=== LAYER 3: Word-mosaic ingestion at CONTEXT=16 ===")
    k = Krimelack()
    t0 = time.time()
    try:
        ingest_stats = word_mosaic_ingest(k, corpus_text)
        ingest_time = time.time() - t0
        ingest_stats["time_seconds"] = round(ingest_time, 2)
        results["word_mosaic_ingestion"] = ingest_stats
        print(f"  Completed in {ingest_time:.1f}s")
        print(f"  Words processed: {ingest_stats['total_words']}")
        print(f"  Unique words: {ingest_stats['unique_words']}")
        print(f"  Motifs committed: {ingest_stats['motifs_committed']}")
        print(f"  New motifs: {ingest_stats['new_motifs']}")
        print(f"  Null collapses: {ingest_stats['null_collapses']}")
        print(f"  Truncated words: {ingest_stats['words_truncated']}")
        if ingest_stats["errors"]:
            print(f"  Errors: {ingest_stats['errors'][:5]}")
    except Exception as e:
        tb = traceback.format_exc()
        results["crashes"].append(f"word_mosaic_ingestion: {tb}")
        results["word_mosaic_ingestion"] = {"crashed": True, "error": str(e)}
        print(f"  CRASHED: {e}")

    # ── Chi distribution of word motifs ──────────────────────────────
    if k.size() > 0:
        chi_dist = Counter()
        for m in k.motifs.values():
            chi_dist[m.chi] += 1
        results["chi_distribution"] = dict(sorted(chi_dist.items()))
        print(f"\n  Chi distribution ({k.size()} motifs):")
        for c in sorted(chi_dist.keys()):
            if chi_dist[c] >= 5:
                print(f"    chi={c:4d}: {chi_dist[c]:4d}")

        # Null fraction distribution
        nf = [count_nulls(m.state) / POP for m in k.motifs.values()]
        results["null_fraction"] = {
            "mean": round(sum(nf) / len(nf), 4),
            "min": round(min(nf), 4),
            "max": round(max(nf), 4),
        }
        print(f"  Null fraction: mean={results['null_fraction']['mean']:.4f} "
              f"min={results['null_fraction']['min']:.4f} "
              f"max={results['null_fraction']['max']:.4f}")

        # Words with motifs
        words_with_motifs = sum(1 for m in k.motifs.values() if m.word)
        results["words_with_motifs"] = words_with_motifs
        print(f"  Motifs with word labels: {words_with_motifs}/{k.size()}")

        # Successor stats
        motifs_with_succs = sum(1 for m in k.motifs.values() if m.successors)
        total_links = sum(len(m.successors) for m in k.motifs.values())
        results["successor_stats"] = {
            "motifs_with_successors": motifs_with_succs,
            "total_links": total_links,
        }
        print(f"  Successors: {motifs_with_succs} motifs have them, "
              f"{total_links} total links")

    # ── Pressure field at CONTEXT=16 ─────────────────────────────────
    if k.size() > 0:
        print("\n=== Pressure landscape at CONTEXT=16 ===")
        sample_motifs = list(k.motifs.values())[:20]
        all_null_pressures = []
        for m in sample_motifs:
            strands = [m.state[j*TRITS:(j+1)*TRITS] for j in range(CONTEXT)]
            for s_idx, strand in enumerate(strands):
                for i in range(TRITS):
                    if m.state[s_idx * TRITS + i] == 0:
                        h = strand[i] * P3I[i]
                        for o_idx, other in enumerate(strands):
                            if o_idx != s_idx:
                                h += other[i] * P3I[i] // 2
                        all_null_pressures.append(abs(h))

        if all_null_pressures:
            band_counts = Counter()
            for ah in all_null_pressures:
                if ah <= 5: band_counts["0-5"] += 1
                elif ah <= 9: band_counts["6-9"] += 1
                elif ah <= 12: band_counts["10-12"] += 1
                elif ah <= 14: band_counts["13-14"] += 1
                else: band_counts["15+"] += 1

            results["pressure_landscape_16"] = {
                "null_positions_sampled": len(all_null_pressures),
                "bands": dict(band_counts),
            }
            print(f"  Sampled {len(all_null_pressures)} null positions:")
            for band in ["0-5", "6-9", "10-12", "13-14", "15+"]:
                c = band_counts.get(band, 0)
                pct = 100 * c / len(all_null_pressures)
                print(f"    {band}: {c} ({pct:.1f}%)")

    # ── LAYER 2: Folding composition ─────────────────────────────────
    print("\n=== LAYER 2: Folding composition ===")
    if k.size() > 1:
        t0 = time.time()
        try:
            fold_stats = run_folding_composition(k)
            fold_time = time.time() - t0
            fold_stats["time_seconds"] = round(fold_time, 2)
            # Don't serialize full compositions list to results.jsonl
            results["folding_composition"] = {
                k2: v2 for k2, v2 in fold_stats.items()
                if k2 != "compositions"
            }
            results["folding_composition"]["sample_compositions"] = (
                fold_stats["compositions"][:10])
            print(f"  Completed in {fold_time:.1f}s")
            print(f"  Pairs attempted: {fold_stats['pairs_attempted']}")
            print(f"  Stable: {fold_stats['stable_compositions']}")
            print(f"  Collapsed to null: {fold_stats['collapsed_to_null']}")
            if fold_stats["errors"]:
                print(f"  Errors: {fold_stats['errors'][:5]}")

            # Print some compositions
            for comp in fold_stats["compositions"][:5]:
                parent_a_word = k.motifs.get(comp["parent_a"])
                parent_b_word = k.motifs.get(comp["parent_b"])
                wa = parent_a_word.word if parent_a_word else "?"
                wb = parent_b_word.word if parent_b_word else "?"
                print(f"    {wa} + {wb}: null={comp['settled_null_fraction']:.2f} "
                      f"chi={comp.get('chi_composed', 'null')} "
                      f"recalls_to_parent={comp.get('recalls_to_parent', 'n/a')}")

        except Exception as e:
            tb = traceback.format_exc()
            results["crashes"].append(f"folding_composition: {tb}")
            results["folding_composition"] = {"crashed": True, "error": str(e)}
            print(f"  CRASHED: {e}")
    else:
        results["folding_composition"] = {"skipped": True,
                                           "reason": "fewer than 2 motifs"}
        print("  Skipped (fewer than 2 motifs)")

    # ── Generation (faithful: settle-based, no successor walking) ────
    print("\n=== Generation from word motifs (settle-based) ===")
    if k.size() > 0:
        # Pick 10 starting motifs: top by weight (note: weight is corpus
        # frequency — this biases toward attractor, documented not hidden)
        by_weight = sorted(k.motifs.values(), key=lambda m: -m.weight)
        starters = by_weight[:10]

        generation_results = []
        for i, m in enumerate(starters):
            try:
                output, trace = generate_from_word(k, m.fp, max_steps=50)
                gen = {
                    "starter_fp": m.fp,
                    "starter_word": m.word,
                    "starter_chi": m.chi,
                    "starter_weight": m.weight,
                    "output": output,
                    "output_words": len(output.split()) if output else 0,
                    "steps": len(trace),
                    "termination": trace[-1]["event"] if trace else "no_steps",
                    "trace": trace,
                }
                generation_results.append(gen)
                print(f"  [{i}] start='{m.word}' (w={m.weight}, chi={m.chi})")
                print(f"      -> {output[:120] if output else '(empty)'}")
                print(f"      steps={len(trace)}, "
                      f"ended={trace[-1]['event'] if trace else 'no_steps'}")
            except Exception as e:
                tb = traceback.format_exc()
                generation_results.append({
                    "starter_fp": m.fp, "starter_word": m.word,
                    "crashed": True, "error": str(e),
                })
                print(f"  [{i}] CRASHED: {e}")

        results["generation"] = generation_results
    else:
        results["generation"] = {"skipped": True}
        print("  Skipped (no motifs)")

    # ── Write results ────────────────────────────────────────────────
    with open(RESULTS_FILE, "w") as f:
        f.write(json.dumps(results, indent=2))
    print(f"\nResults written to {RESULTS_FILE}")
    print(f"Crashes: {len(results['crashes'])}")
    if results["crashes"]:
        for c in results["crashes"][:5]:
            print(f"  {c[:200]}")


if __name__ == "__main__":
    main()
