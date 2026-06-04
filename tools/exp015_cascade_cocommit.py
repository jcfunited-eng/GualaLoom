"""
Experiment 1.5 — Cascade with Co-Commit Indexing

Same differential probe as exp01 (control vs trigger, learned seeds only)
but with a modified settle that propagates commits along TWO channels:
  1. Position channel (existing): cross-strand same-position resonance
  2. Co-commit channel (new): positions that co-committed in stored motifs

The modified settle lives here as a probe — not in the substrate proper.

Three co-commit thresholds (500, 300, 100) swept to distinguish "the
channel works" from "we picked the right number."

Usage:
    python3 tools/exp015_cascade_cocommit.py                # full run
    python3 tools/exp015_cascade_cocommit.py --dry-run 10   # 10 per threshold
    python3 tools/exp015_cascade_cocommit.py --repro-only
"""

import os, sys, json, hashlib, random, argparse
from collections import Counter, defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(REPO)
sys.path.insert(0, REPO)

import importlib.util
_spec = importlib.util.spec_from_file_location("gualaloom", os.path.join(REPO, "gualaloom.py"))
gl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gl)

settle = gl.settle
P3I = gl.P3I
TRITS = gl.TRITS          # 8
CONTEXT = gl.CONTEXT       # 8
POP = TRITS * CONTEXT      # 64
DEAD_ZONE = gl.DEAD_ZONE   # 15

STEP_CAP = 50
THRESHOLDS = [500, 300, 100]
RESULTS_DIR = os.path.join(REPO, "experiments", "exp015")
RESULTS_FILE = os.path.join(RESULTS_DIR, "results.jsonl")


def state_hash(state):
    s = "".join({-1: "-", 0: "0", 1: "+"}[t] for t in state)
    return hashlib.sha1(s.encode()).hexdigest()[:12]


def to_strands(state):
    return [state[j * TRITS:(j + 1) * TRITS] for j in range(CONTEXT)]


def count_nulls(state):
    return sum(1 for t in state if t == 0)


# ── Co-commit neighbor map ──────────────────────────────────────────

def build_cocommit_neighbors(motifs, threshold):
    """Positions p, q are co-commit neighbors if they are both non-null
    in the same stored motif, summed across the population, >= threshold."""
    pair_counts = Counter()
    for m in motifs:
        committed = [i for i, t in enumerate(m.state) if t != 0]
        for idx, p in enumerate(committed):
            for q in committed[idx + 1:]:
                pair_counts[(min(p, q), max(p, q))] += 1

    neighbors = defaultdict(set)
    for (p, q), c in pair_counts.items():
        if c >= threshold:
            neighbors[p].add(q)
            neighbors[q].add(p)
    return dict(neighbors)


def position_neighbors(trigger_pos):
    """Cross-strand siblings: same intra-strand index, different strand."""
    intra = trigger_pos % TRITS
    strand = trigger_pos // TRITS
    return {s * TRITS + intra for s in range(CONTEXT) if s != strand}


# ── Modified settle: position + co-commit channels ──────────────────

def settle_with_cocommit(state, familiarity, cc_neighbors):
    """One settle pass: normal position channel, then co-commit wavefront.

    Step 1: run the existing settle rule (position channel only).
    Step 2: for each position that committed in step 1 (or was already
    committed), propagate through co-commit neighbors. For each null
    co-commit neighbor, recompute its barrier math with pressure from
    committed co-commit neighbors added. If it crosses, commit it and
    add it to the wavefront.

    The position channel is NOT removed. The co-commit channel runs
    alongside it, after the position pass."""
    strands = to_strands(state)
    new_state = list(settle(strands, familiarity))
    barrier = DEAD_ZONE + familiarity

    # Positions that committed in this pass (were null in input, non-null now)
    newly_committed = [p for p in range(POP)
                       if new_state[p] != 0 and state[p] == 0]

    # Also include positions that were already committed in the input,
    # since their co-commit pressure is real
    all_committed = [p for p in range(POP) if new_state[p] != 0]

    # BFS wavefront through co-commit graph
    wavefront = list(newly_committed)
    visited = set(range(POP))  # start with all, remove nulls we haven't checked
    visited = set(p for p in range(POP) if new_state[p] != 0)

    while wavefront:
        next_wave = []
        for p in wavefront:
            for q in cc_neighbors.get(p, []):
                if new_state[q] != 0 or q in visited:
                    continue
                visited.add(q)

                # Recompute q's pressure with both channels
                qs = q // TRITS   # strand index
                qi = q % TRITS    # intra-strand position

                # Position channel (same as normal settle)
                h = strands[qs][qi] * P3I[qi]
                for o in range(len(strands)):
                    if o != qs:
                        h += strands[o][qi] * P3I[qi] // 2

                # Co-commit channel: pressure from all committed co-commit neighbors
                for r in cc_neighbors.get(q, []):
                    if new_state[r] != 0:
                        h += new_state[r] * P3I[r % TRITS] // 2

                if h > barrier:
                    new_state[q] = 1
                    next_wave.append(q)
                elif h < -barrier:
                    new_state[q] = -1
                    next_wave.append(q)

        wavefront = next_wave

    return tuple(new_state)


def settle_to_eq(state, familiarity, cc_neighbors):
    """Iterate settle_with_cocommit until stable or step cap."""
    for step in range(STEP_CAP):
        new = settle_with_cocommit(state, familiarity, cc_neighbors)
        if new == state:
            return state, step + 1, True
        state = new
    return state, STEP_CAP, False


# ── Trial runner ─────────────────────────────────────────────────────

def run_trial(seed_state, trigger_pos, trigger_val, cc_neighbors, threshold):
    """Two-step differential probe with co-commit channel."""
    if seed_state[trigger_pos] != 0:
        return None

    # Control: re-settle unmodified seed
    ctrl_end, ctrl_steps, ctrl_stable = settle_to_eq(seed_state, 0, cc_neighbors)

    # Trigger: commit one null, then re-settle
    triggered = list(seed_state)
    triggered[trigger_pos] = trigger_val
    triggered = tuple(triggered)
    trig_end, trig_steps, trig_stable = settle_to_eq(triggered, 0, cc_neighbors)

    # Diff: positions where trigger end-state differs from control
    diffs = [i for i in range(POP) if ctrl_end[i] != trig_end[i]]
    trigger_in_diff = trigger_pos in diffs
    cascade_depth = len(diffs) - (1 if trigger_in_diff else 0)

    # Attribution: which channel's neighbors carried which diffs
    pos_nbrs = position_neighbors(trigger_pos)
    cc_nbrs = set(cc_neighbors.get(trigger_pos, []))

    diff_set = set(diffs)
    if trigger_in_diff:
        diff_set.discard(trigger_pos)

    via_pos = diff_set & pos_nbrs
    via_cc = diff_set & cc_nbrs
    via_both = via_pos & via_cc

    chi_start, _ = gl.chi(seed_state)
    chi_ctrl, _ = gl.chi(ctrl_end)
    chi_trig, _ = gl.chi(trig_end)

    return {
        "trial_id": None,
        "seed_source": "learned",
        "threshold": threshold,
        "null_fraction_start": round(count_nulls(seed_state) / POP, 4),
        "trigger_position": trigger_pos,
        "trigger_value": trigger_val,
        "trigger_intra_strand_index": trigger_pos % TRITS,
        "cascade_depth": cascade_depth,
        "cascade_via_position": len(via_pos),
        "cascade_via_cocommit": len(via_cc),
        "cascade_via_both": len(via_both),
        "cascade_latency_steps": trig_steps,
        "control_latency_steps": ctrl_steps,
        "final_null_fraction": round(count_nulls(trig_end) / POP, 4),
        "control_null_fraction": round(count_nulls(ctrl_end) / POP, 4),
        "chi_start": chi_start,
        "chi_control": chi_ctrl,
        "chi_trigger": chi_trig,
        "stable": trig_stable,
        "control_stable": ctrl_stable,
        "end_state_hash": state_hash(trig_end),
        "control_end_state_hash": state_hash(ctrl_end),
        "seed_state_hash": state_hash(seed_state),
        "diff_positions": diffs,
    }


# ── Data loading ─────────────────────────────────────────────────────

def get_null_positions(state):
    return [i for i, t in enumerate(state) if t == 0]


def pick_trigger_positions(null_positions, count, rng):
    if len(null_positions) <= count:
        return list(null_positions)
    return rng.sample(null_positions, count)


def load_learned_seeds():
    k, loom = gl.load()
    if k.size() == 0:
        gl.seed_corpus(k, loom)
        gl.save(k, loom)
    return list(k.motifs.values())


# ── Run all trials ───────────────────────────────────────────────────

def run_trials_for_threshold(seeds, motifs, threshold, max_trials=None):
    """Run 2000 trials for one threshold."""
    cc_neighbors = build_cocommit_neighbors(motifs, threshold)

    # Stats about the neighbor map
    positions_with_neighbors = len(cc_neighbors)
    if cc_neighbors:
        mean_neighbors = sum(len(v) for v in cc_neighbors.values()) / len(cc_neighbors)
    else:
        mean_neighbors = 0
    print(f"  threshold={threshold}: {positions_with_neighbors} positions "
          f"have co-commit neighbors (mean {mean_neighbors:.1f})")

    rng = random.Random(7777)
    if len(seeds) > 100:
        seed_subset = rng.sample(seeds, 100)
    else:
        seed_subset = list(seeds)

    results = []
    for seed_idx, seed_state in enumerate(seed_subset):
        null_positions = get_null_positions(seed_state)
        if not null_positions:
            continue
        trigger_positions = pick_trigger_positions(null_positions, 10, rng)
        for trig_pos in trigger_positions:
            for trig_val in [1, -1]:
                r = run_trial(seed_state, trig_pos, trig_val,
                              cc_neighbors, threshold)
                if r is None:
                    continue
                r["trial_id"] = (f"learned_t{threshold}_s{seed_idx}"
                                 f"_p{trig_pos}_v{trig_val}")
                results.append(r)
                if max_trials and len(results) >= max_trials:
                    return results
    return results


def run_reproducibility_check(motifs):
    """50 trials × 2 runs at threshold=300, verify hashes match."""
    cc_neighbors = build_cocommit_neighbors(motifs, 300)
    seeds = [m.state for m in motifs]

    rng_a = random.Random(8888)
    rng_b = random.Random(8888)
    subset_a = rng_a.sample(seeds, min(25, len(seeds)))
    subset_b = rng_b.sample(seeds, min(25, len(seeds)))

    pairs = []
    for sa, sb in zip(subset_a, subset_b):
        null_pos = get_null_positions(sa)
        if not null_pos:
            continue
        trig_pos = null_pos[0]
        for trig_val in [1, -1]:
            ra = run_trial(sa, trig_pos, trig_val, cc_neighbors, 300)
            rb = run_trial(sb, trig_pos, trig_val, cc_neighbors, 300)
            if ra and rb:
                pairs.append({
                    "ctrl": ra["control_end_state_hash"] == rb["control_end_state_hash"],
                    "trig": ra["end_state_hash"] == rb["end_state_hash"],
                })

    ctrl_mm = sum(1 for p in pairs if not p["ctrl"])
    trig_mm = sum(1 for p in pairs if not p["trig"])
    return len(pairs), ctrl_mm, trig_mm


# ── Summary ──────────────────────────────────────────────────────────

def print_summary(results):
    if not results:
        print("  No results.")
        return

    # Group by threshold
    by_threshold = defaultdict(list)
    for r in results:
        by_threshold[r["threshold"]].append(r)

    for thresh in sorted(by_threshold.keys(), reverse=True):
        subset = by_threshold[thresh]
        depths = [r["cascade_depth"] for r in subset]
        via_pos = [r["cascade_via_position"] for r in subset]
        via_cc = [r["cascade_via_cocommit"] for r in subset]
        via_both = [r["cascade_via_both"] for r in subset]

        # Check attribution identity
        identity_holds = sum(
            1 for r in subset
            if (r["cascade_via_position"] + r["cascade_via_cocommit"]
                - r["cascade_via_both"]) == r["cascade_depth"]
        )

        # Intra-strand index breakdown
        by_intra = defaultdict(list)
        for r in subset:
            by_intra[r["trigger_intra_strand_index"]].append(r)

        depth_dist = Counter(depths)

        print(f"\nthreshold={thresh} ({len(subset)} trials):")
        print(f"  cascade_depth: min={min(depths)} max={max(depths)} "
              f"mean={sum(depths)/len(depths):.2f} "
              f"median={sorted(depths)[len(depths)//2]}")
        print(f"  depth=0: {sum(1 for d in depths if d == 0)} "
              f"({100*sum(1 for d in depths if d == 0)/len(depths):.1f}%)")
        print(f"  depth>0: {sum(1 for d in depths if d > 0)} "
              f"({100*sum(1 for d in depths if d > 0)/len(depths):.1f}%)")
        print(f"  depth distribution: {dict(sorted(depth_dist.items()))}")
        print(f"  via_position: mean={sum(via_pos)/len(via_pos):.2f}")
        print(f"  via_cocommit: mean={sum(via_cc)/len(via_cc):.2f}")
        print(f"  via_both: mean={sum(via_both)/len(via_both):.2f}")
        print(f"  attribution identity holds: {identity_holds}/{len(subset)}")

        # Per intra-strand-index summary
        print(f"  by intra-strand index:")
        for idx in sorted(by_intra.keys()):
            sub = by_intra[idx]
            d = [r["cascade_depth"] for r in sub]
            vp = [r["cascade_via_position"] for r in sub]
            vc = [r["cascade_via_cocommit"] for r in sub]
            d_gt0 = sum(1 for x in d if x > 0)
            print(f"    idx={idx}: {len(sub):4d} trials, "
                  f"depth>0={d_gt0:3d} ({100*d_gt0/len(sub) if sub else 0:.0f}%), "
                  f"mean_depth={sum(d)/len(d):.2f}, "
                  f"via_pos={sum(vp)/len(vp):.2f}, "
                  f"via_cc={sum(vc)/len(vc):.2f}")


# ── Main ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", type=int, default=0,
                        help="Run N trials PER THRESHOLD and dump to terminal")
    parser.add_argument("--repro-only", action="store_true")
    args = parser.parse_args()

    os.makedirs(RESULTS_DIR, exist_ok=True)

    motifs = load_learned_seeds()
    seeds = [m.state for m in motifs]
    print(f"Loaded {len(motifs)} motifs from krimelack")

    if args.repro_only:
        total, ctrl_mm, trig_mm = run_reproducibility_check(motifs)
        print(f"Reproducibility: {total} trials")
        print(f"  control mismatches: {ctrl_mm}")
        print(f"  trigger mismatches: {trig_mm}")
        return

    if args.dry_run > 0:
        print(f"=== Dry run: {args.dry_run} trials per threshold ===\n")
        for thresh in THRESHOLDS:
            results = run_trials_for_threshold(seeds, motifs, thresh,
                                               max_trials=args.dry_run)
            print(f"\n  --- threshold={thresh}: {len(results)} trials ---")
            for r in results:
                display = {k: v for k, v in r.items() if k != "diff_positions"}
                display["n_diff_positions"] = len(r["diff_positions"])
                # Check attribution identity
                identity = (r["cascade_via_position"] + r["cascade_via_cocommit"]
                            - r["cascade_via_both"])
                display["attribution_check"] = (
                    f"{identity} == {r['cascade_depth']}: "
                    f"{'OK' if identity == r['cascade_depth'] else 'MISMATCH'}")
                print(json.dumps(display, indent=2))
            print()
        return

    # Full run
    print("=== Reproducibility check ===")
    total, ctrl_mm, trig_mm = run_reproducibility_check(motifs)
    print(f"  {total} trials, control mismatches: {ctrl_mm}, "
          f"trigger mismatches: {trig_mm}\n")

    all_results = []
    for thresh in THRESHOLDS:
        print(f"=== Threshold {thresh} ===")
        results = run_trials_for_threshold(seeds, motifs, thresh)
        print(f"  {len(results)} trials")
        all_results.extend(results)

    print(f"\n=== Total: {len(all_results)} trials ===")

    with open(RESULTS_FILE, "w") as f:
        for r in all_results:
            f.write(json.dumps(r) + "\n")
    print(f"Written to {RESULTS_FILE}")

    print_summary(all_results)
    print(f"\nReproducibility: {total} trials, control mismatches: {ctrl_mm}, "
          f"trigger mismatches: {trig_mm}")


if __name__ == "__main__":
    main()
