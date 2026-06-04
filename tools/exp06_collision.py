"""
Experiment 06 — Three-Layer Collision Build (third pass)

Third pass fixes:
  - Word-mosaic: now snapshots loom settled state at whitespace boundaries
    instead of encoding fixed windows. Character pipeline runs normally;
    word motifs are the substrate's state AT the word boundary.
  - Folding composition: structural union with conflict-nulling instead of
    destructive intersection. Keeps commitments from either parent unless
    they actively disagree.
  - Generation: three perturbation strategies, all settle-based, no
    successor walking.

NOT a build to ship. We are reading the wreckage.
"""

import os, sys, json, hashlib, time, traceback, glob, random
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


def _fp(state):
    s = "".join({-1: "-", 0: "0", 1: "+"}[t] for t in state)
    return hashlib.sha1(s.encode()).hexdigest()[:12]


def count_nulls(state):
    return sum(1 for t in state if t == 0)


# ======================================================================
# Krimelack
# ======================================================================

class Motif:
    __slots__ = ("fp", "state", "weight", "age", "chi", "V",
                 "char_counts", "successors", "word")
    def __init__(self, fp, state, c, v):
        self.fp = fp; self.state = state; self.weight = 1; self.age = 0
        self.chi = c; self.V = v
        self.char_counts = defaultdict(int)
        self.successors = defaultdict(int)
        self.word = None

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
# LAYER 3 — Word-Mosaic (REWRITTEN: settled-state snapshot at whitespace)
# ======================================================================

def word_mosaic_ingest(k, corpus_text):
    """Run the normal character Loom through the corpus. At every whitespace
    boundary, snapshot the current settled state and commit it as a word motif
    labeled with the word that just completed. Character motifs commit at
    every tick (normal Loom behavior). Word motifs are an additional commit
    layer — the substrate's state AT the word boundary, reflecting the actual
    character cascade in context.

    No truncation. No padding. No contamination. The word motif IS what the
    substrate settled to after processing that word's characters."""

    stats = {
        "total_words": 0,
        "unique_words": set(),
        "word_motifs_committed": 0,
        "word_motifs_new": 0,
        "word_null_collapses": 0,
        "char_motifs_committed": 0,
        "errors": [],
    }

    loom = Loom(k)
    current_word_chars = []

    for ch in corpus_text:
        if ch in (' ', '\t', '\n', '\r'):
            # Whitespace boundary — snapshot the current settled state as a word motif
            if current_word_chars:
                word = "".join(current_word_chars).lower()
                stats["total_words"] += 1
                stats["unique_words"].add(word)

                # The loom's current settled state IS the word motif
                word_state = loom.last
                if all(t == 0 for t in word_state):
                    stats["word_null_collapses"] += 1
                else:
                    fp, new = k.commit(word_state, word=word)
                    if fp is not None:
                        stats["word_motifs_committed"] += 1
                        if new:
                            stats["word_motifs_new"] += 1

                current_word_chars = []

            # Feed whitespace through the loom too — it's a real character
            loom.tick(ch)
            stats["char_motifs_committed"] += 1
        else:
            current_word_chars.append(ch)
            loom.tick(ch)
            stats["char_motifs_committed"] += 1

    # Final word if corpus doesn't end with whitespace
    if current_word_chars:
        word = "".join(current_word_chars).lower()
        stats["total_words"] += 1
        stats["unique_words"].add(word)
        word_state = loom.last
        if not all(t == 0 for t in word_state):
            fp, new = k.commit(word_state, word=word)
            if fp is not None:
                stats["word_motifs_committed"] += 1
                if new:
                    stats["word_motifs_new"] += 1

    stats["unique_words"] = len(stats["unique_words"])
    return stats, loom


# ======================================================================
# LAYER 2 — Folding Composition (REWRITTEN: union with conflict-nulling)
# ======================================================================

def fold_compose(state_a, state_b):
    """Structural union with conflict-nulling.
    - a == b (both same, including both null): keep
    - a != 0 AND b != 0 AND a != b (opposite signs, actual conflict): null
    - one committed, one null (no conflict): KEEP the commitment
    Then settle the result."""
    merged = []
    for a, b in zip(state_a, state_b):
        if a == b:
            merged.append(a)        # agree or both null
        elif a != 0 and b != 0:
            merged.append(0)        # actual conflict: different signs
        elif a != 0:
            merged.append(a)        # a has something, b is silent: keep a
        else:
            merged.append(b)        # b has something, a is silent: keep b
    merged = tuple(merged)

    strands = [merged[j * TRITS:(j + 1) * TRITS] for j in range(CONTEXT)]
    settled = settle(strands, 0)
    return merged, settled


def run_folding_composition(k):
    """Compose top 50 co-commit pairs using union-with-conflict-nulling."""
    stats = {
        "pairs_attempted": 0,
        "stable_compositions": 0,
        "collapsed_to_null": 0,
        "errors": [],
        "compositions": [],
    }

    pairs = []
    for fp, m in k.motifs.items():
        for succ_fp, count in m.successors.items():
            if succ_fp in k.motifs:
                pairs.append((count, fp, succ_fp))
    pairs.sort(reverse=True)

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
                "parent_a_word": ma.word,
                "parent_b_word": mb.word,
                "co_commit_count": count,
                "merged_null_fraction": round(merged_nulls / POP, 4),
                "settled_null_fraction": round(settled_nulls / POP, 4),
                "collapsed_to_null": all_null,
                "chi_a": ma.chi,
                "chi_b": mb.chi,
                "parent_a_null_fraction": round(count_nulls(ma.state) / POP, 4),
                "parent_b_null_fraction": round(count_nulls(mb.state) / POP, 4),
            }

            if all_null:
                stats["collapsed_to_null"] += 1
                comp["chi_composed"] = 0
            else:
                c, v = chi(settled)
                comp["chi_composed"] = c
                comp["settled_fp"] = _fp(settled)

                # Does composed motif recall to either parent?
                best, score = k.recall(settled)
                comp["recalls_to"] = best.fp if best else None
                comp["recalls_to_parent_a"] = (best.fp == fp_a) if best else False
                comp["recalls_to_parent_b"] = (best.fp == fp_b) if best else False
                comp["recalls_to_word"] = best.word if best else None

                # Does it recall to something NEITHER parent?
                comp["recalls_to_novel"] = (
                    best is not None and best.fp != fp_a and best.fp != fp_b
                ) if best else False

                stats["stable_compositions"] += 1

            stats["compositions"].append(comp)
        except Exception as e:
            stats["errors"].append(f"{fp_a}+{fp_b}: {str(e)}")

    return stats


# ======================================================================
# Generation — three perturbation strategies, all settle-based
# ======================================================================

def generate_settle(k, start_fp, perturb_mode, max_steps=50):
    """Faithful cascade-based generation. No successor walking.

    perturb_mode:
      "null_pos0" — null only position 0 in each strand (minimal, 16/256 = 6%)
      "null_pos03" — null positions 0-3 in each strand (25%)
      "feed_char" — feed a fresh character through the loom to perturb
                     (uses encode+settle, not a frequency lookup)
    """
    out = []
    trace = []

    m = k.motifs.get(start_fp)
    if m is None:
        return "", []

    state = m.state
    prev_state = None
    # For feed_char mode: cycle through 'a'-'z'
    feed_idx = 0

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

        elif perturb_mode == "null_pos03":
            perturbed = list(settled)
            for s in range(CONTEXT):
                for i in range(4):
                    perturbed[s * TRITS + i] = 0
            state = tuple(perturbed)

        elif perturb_mode == "feed_char":
            # Inject a fresh character into the settled state by replacing
            # the first strand with the encoding of a cycling character.
            # This is real substrate perturbation: encode produces a trit
            # strand, which changes the cross-strand resonance for all
            # other strands on the next settle.
            ch = chr(ord('a') + (feed_idx % 26))
            feed_idx += 1
            new_strand = encode(ch)
            perturbed = list(settled)
            # Replace strand 0 with the fresh character encoding
            for i in range(TRITS):
                perturbed[i] = new_strand[i]
            state = tuple(perturbed)

        if all(t == 0 for t in state):
            trace.append({"step": step + 1, "event": "perturbation_collapsed"})
            break

    return " ".join(out), trace


# ======================================================================
# MAIN
# ======================================================================

def main():
    results = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "pass": "third",
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

    # ── LAYER 3: Word-mosaic (settled-state snapshot at whitespace) ───
    print("\n=== LAYER 3: Word-mosaic (settled-state snapshot) ===")
    k = Krimelack()
    t0 = time.time()
    try:
        ingest_stats, loom = word_mosaic_ingest(k, corpus_text)
        ingest_time = time.time() - t0
        ingest_stats["time_seconds"] = round(ingest_time, 2)
        results["word_mosaic_ingestion"] = ingest_stats
        print(f"  Completed in {ingest_time:.1f}s")
        print(f"  Words processed: {ingest_stats['total_words']}")
        print(f"  Unique words: {ingest_stats['unique_words']}")
        print(f"  Word motifs committed: {ingest_stats['word_motifs_committed']}")
        print(f"  Word motifs new: {ingest_stats['word_motifs_new']}")
        print(f"  Word null collapses: {ingest_stats['word_null_collapses']}")
        print(f"  Char motifs committed: {ingest_stats['char_motifs_committed']}")
        if ingest_stats["errors"]:
            print(f"  Errors: {ingest_stats['errors'][:5]}")
    except Exception as e:
        tb = traceback.format_exc()
        results["crashes"].append(f"word_mosaic_ingestion: {tb}")
        results["word_mosaic_ingestion"] = {"crashed": True, "error": str(e)}
        print(f"  CRASHED: {e}")
        loom = None

    # ── Motif analysis ───────────────────────────────────────────────
    if k.size() > 0:
        chi_dist = Counter()
        word_motifs = []
        for m in k.motifs.values():
            chi_dist[m.chi] += 1
            if m.word:
                word_motifs.append(m)
        results["chi_distribution"] = dict(sorted(chi_dist.items()))
        print(f"\n  Total motifs: {k.size()} (word-labeled: {len(word_motifs)})")
        print(f"  Chi distribution (top):")
        for c in sorted(chi_dist.keys()):
            if chi_dist[c] >= 5:
                print(f"    chi={c:4d}: {chi_dist[c]:4d}")

        nf = [count_nulls(m.state) / POP for m in k.motifs.values()]
        results["null_fraction"] = {
            "mean": round(sum(nf) / len(nf), 4),
            "min": round(min(nf), 4),
            "max": round(max(nf), 4),
        }
        print(f"  Null fraction: mean={results['null_fraction']['mean']:.4f} "
              f"min={results['null_fraction']['min']:.4f} "
              f"max={results['null_fraction']['max']:.4f}")

        # Words-with-distinct-motifs: how many unique words map to distinct fps?
        word_to_fps = defaultdict(set)
        for m in word_motifs:
            word_to_fps[m.word].add(m.fp)
        words_distinct = sum(1 for fps in word_to_fps.values() if len(fps) == 1)
        words_shared = sum(1 for fps in word_to_fps.values() if len(fps) > 1)
        results["word_distinctness"] = {
            "unique_words_with_motifs": len(word_to_fps),
            "words_with_one_motif": words_distinct,
            "words_with_multiple_motifs": words_shared,
        }
        # Actually: a word can only have one motif (first commit wins the label)
        # But multiple words can share a motif fp
        fp_to_words = defaultdict(set)
        for m in word_motifs:
            fp_to_words[m.fp].add(m.word)
        motifs_multi_word = {fp: words for fp, words in fp_to_words.items()
                             if len(words) > 1}
        results["word_distinctness"]["motifs_shared_by_multiple_words"] = len(motifs_multi_word)
        print(f"  Words with motifs: {len(word_to_fps)}")
        print(f"  Motifs shared by multiple words: {len(motifs_multi_word)}")
        if motifs_multi_word:
            for fp, words in list(motifs_multi_word.items())[:5]:
                print(f"    {fp}: {sorted(words)[:8]}")

        motifs_with_succs = sum(1 for m in k.motifs.values() if m.successors)
        total_links = sum(len(m.successors) for m in k.motifs.values())
        results["successor_stats"] = {
            "motifs_with_successors": motifs_with_succs,
            "total_links": total_links,
        }
        print(f"  Successors: {motifs_with_succs} motifs, {total_links} links")

    # ── Pressure landscape ───────────────────────────────────────────
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

    # ── LAYER 2: Folding composition (union with conflict-nulling) ───
    print("\n=== LAYER 2: Folding composition (union + conflict-null) ===")
    if k.size() > 1:
        t0 = time.time()
        try:
            fold_stats = run_folding_composition(k)
            fold_time = time.time() - t0
            fold_stats["time_seconds"] = round(fold_time, 2)
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

            for comp in fold_stats["compositions"][:5]:
                wa = comp.get("parent_a_word", "?")
                wb = comp.get("parent_b_word", "?")
                print(f"    {wa} + {wb}: "
                      f"merged_null={comp['merged_null_fraction']:.2f} "
                      f"settled_null={comp['settled_null_fraction']:.2f} "
                      f"chi={comp.get('chi_composed', 'null')} "
                      f"recalls={comp.get('recalls_to_word', '?')} "
                      f"novel={comp.get('recalls_to_novel', '?')}")

        except Exception as e:
            tb = traceback.format_exc()
            results["crashes"].append(f"folding_composition: {tb}")
            results["folding_composition"] = {"crashed": True, "error": str(e)}
            print(f"  CRASHED: {e}")
    else:
        results["folding_composition"] = {"skipped": True}
        print("  Skipped (fewer than 2 motifs)")

    # ── Generation (three perturbation modes) ────────────────────────
    print("\n=== Generation (settle-based, three perturbation modes) ===")
    if k.size() > 0:
        by_weight = sorted(k.motifs.values(), key=lambda m: -m.weight)
        starters = by_weight[:10]

        all_gen_results = {}
        for mode in ["null_pos0", "null_pos03", "feed_char"]:
            print(f"\n  --- mode: {mode} ---")
            gen_results = []
            for i, m in enumerate(starters):
                try:
                    output, trace = generate_settle(k, m.fp, mode, max_steps=50)
                    gen = {
                        "starter_fp": m.fp,
                        "starter_word": m.word,
                        "starter_chi": m.chi,
                        "starter_weight": m.weight,
                        "perturb_mode": mode,
                        "output": output,
                        "output_words": len(output.split()) if output else 0,
                        "steps": len(trace),
                        "termination": trace[-1]["event"] if trace else "no_steps",
                        "trace": trace,
                    }
                    gen_results.append(gen)
                    print(f"  [{i}] '{m.word}' -> {output[:100] if output else '(empty)'}")
                    print(f"       steps={len(trace)} end={trace[-1]['event'] if trace else '?'}")
                except Exception as e:
                    gen_results.append({
                        "starter_fp": m.fp, "starter_word": m.word,
                        "perturb_mode": mode,
                        "crashed": True, "error": str(e),
                    })
                    print(f"  [{i}] CRASHED: {e}")

            all_gen_results[mode] = gen_results

        results["generation"] = all_gen_results
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
