"""
Experiment 03 — Barrier Sweep on Pressure-and-Cascade Probe

Same 100 learned seeds, same pressure_field() from exp02.
Sweeps DEAD_ZONE barrier across {15, 13, 11, 9, 7, 5}.
Tests whether lowering the barrier brings new intra-strand positions
into the loaded-null zone, expanding the substrate's cognitive surface.

Uses a probe-settle with explicit barrier parameter — does NOT modify
the real substrate.

Usage:
    python3 tools/exp03_barrier_sweep.py                # full run
    python3 tools/exp03_barrier_sweep.py --dry-run 20   # 20 per barrier
"""

import os, sys, json, hashlib, random, argparse, math
from collections import Counter, defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(REPO)
sys.path.insert(0, REPO)

import importlib.util
_spec = importlib.util.spec_from_file_location("gualaloom", os.path.join(REPO, "gualaloom.py"))
gl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gl)

P3I = gl.P3I
TRITS = gl.TRITS
CONTEXT = gl.CONTEXT
POP = TRITS * CONTEXT

STEP_CAP = 50
BARRIERS = [15, 13, 11, 9, 7, 5]
RESULTS_DIR = os.path.join(REPO, "experiments", "exp03")
RESULTS_FILE = os.path.join(RESULTS_DIR, "results.jsonl")


def state_hash(state):
    s = "".join({-1: "-", 0: "0", 1: "+"}[t] for t in state)
    return hashlib.sha1(s.encode()).hexdigest()[:12]


def to_strands(state):
    return [state[j * TRITS:(j + 1) * TRITS] for j in range(CONTEXT)]


def count_nulls(state):
    return sum(1 for t in state if t == 0)


# ── Probe-settle: identical math, barrier as parameter ───────────────

def settle_probe(strands, barrier):
    """Identical to gualaloom.py settle(), except barrier is explicit."""
    out = []
    for s_idx, strand in enumerate(strands):
        for i in range(TRITS):
            h = strand[i] * P3I[i]
            for o_idx, other in enumerate(strands):
                if o_idx != s_idx:
                    h += other[i] * P3I[i] // 2
            out.append(1 if h > barrier else (-1 if h < -barrier else 0))
    return tuple(out)


def settle_to_eq(state, barrier):
    """Iterate settle_probe until stable or step cap."""
    for step in range(STEP_CAP):
        strands = to_strands(state)
        new_state = settle_probe(strands, barrier)
        if new_state == state:
            return state, step + 1, True
        state = new_state
    return state, STEP_CAP, False


# ── Pressure field (same as exp02, barrier-independent) ──────────────

def pressure_field(state):
    """Raw h at every position. Independent of barrier."""
    strands = to_strands(state)
    pressures = []
    for s_idx, strand in enumerate(strands):
        for i in range(TRITS):
            h = strand[i] * P3I[i]
            for o_idx, other in enumerate(strands):
                if o_idx != s_idx:
                    h += other[i] * P3I[i] // 2
            pressures.append(h)
    return pressures


# ── Dynamic banding relative to barrier ──────────────────────────────

def classify_null(abs_h, barrier):
    """Classify a null position relative to the current barrier.
    - loaded: |h| in [barrier-2, barrier-1] — one nudge from committing
    - primed: |h| in [barrier/3, barrier-3]
    - inert:  |h| < barrier/3
    - already: |h| >= barrier — would commit under this barrier
    """
    if abs_h >= barrier:
        return "already"
    if abs_h >= barrier - 2:
        return "loaded"
    if abs_h >= barrier // 3:
        return "primed"
    return "inert"


# ── Trial runner ─────────────────────────────────────────────────────

def run_trial(seed_state, trigger_pos, trigger_val, pre_pressure, barrier):
    if seed_state[trigger_pos] != 0:
        return None

    ctrl_end, ctrl_steps, ctrl_stable = settle_to_eq(seed_state, barrier)
    triggered = list(seed_state)
    triggered[trigger_pos] = trigger_val
    triggered = tuple(triggered)
    trig_end, trig_steps, trig_stable = settle_to_eq(triggered, barrier)

    diffs = [i for i in range(POP) if ctrl_end[i] != trig_end[i]]
    trigger_in_diff = trigger_pos in diffs
    cascade_depth = len(diffs) - (1 if trigger_in_diff else 0)

    chi_start, _ = gl.chi(seed_state)
    chi_ctrl, _ = gl.chi(ctrl_end)
    chi_trig, _ = gl.chi(trig_end)

    h_i = pre_pressure[trigger_pos]

    return {
        "trial_id": None,
        "seed_source": "learned",
        "barrier_used": barrier,
        "null_fraction_start": round(count_nulls(seed_state) / POP, 4),
        "trigger_position": trigger_pos,
        "trigger_value": trigger_val,
        "trigger_intra_strand_index": trigger_pos % TRITS,
        "pre_trigger_pressure": h_i,
        "pressure_band": classify_null(abs(h_i), barrier),
        "cascade_depth": cascade_depth,
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

def load_learned_seeds():
    k, loom = gl.load()
    if k.size() == 0:
        gl.seed_corpus(k, loom)
        gl.save(k, loom)
    return [m.state for m in k.motifs.values()]


# ── Per-barrier analysis ─────────────────────────────────────────────

def analyze_pressure_for_barrier(seeds, barrier):
    """Compute pressure histogram and null classification for one barrier."""
    null_catalog = []  # (seed_idx, pos, h, abs_h, band, intra_idx)
    band_counts = Counter()
    intra_by_band = defaultdict(Counter)

    for seed_idx, state in enumerate(seeds):
        pf = pressure_field(state)
        for pos in range(POP):
            if state[pos] == 0:
                h = pf[pos]
                ah = abs(h)
                band = classify_null(ah, barrier)
                intra = pos % TRITS
                null_catalog.append((seed_idx, pos, h, ah, band, intra))
                band_counts[band] += 1
                intra_by_band[band][intra] += 1

    return null_catalog, band_counts, intra_by_band


def run_trials_for_barrier(seeds, barrier, max_trials=1500,
                           dry_run_per_band=0):
    """Run cascade probe for one barrier value."""
    null_catalog, band_counts, intra_by_band = analyze_pressure_for_barrier(
        seeds, barrier)

    # Pre-compute pressure fields
    pressure_cache = {}
    for seed_idx, state in enumerate(seeds):
        pressure_cache[seed_idx] = pressure_field(state)

    # Group by band
    by_band = defaultdict(list)
    for entry in null_catalog:
        by_band[entry[4]].append(entry)

    rng = random.Random(4242 + barrier)

    if dry_run_per_band > 0:
        sampled = []
        for band in ["loaded", "primed", "inert", "already"]:
            pool = by_band.get(band, [])
            if not pool:
                continue
            n = min(dry_run_per_band, len(pool))
            sampled.extend(rng.sample(pool, n))
    else:
        max_nulls = max_trials // 2
        total_nulls = len(null_catalog)
        sampled = []
        for band in ["loaded", "primed", "inert", "already"]:
            pool = by_band.get(band, [])
            if not pool:
                continue
            proportion = len(pool) / total_nulls if total_nulls > 0 else 0
            n = max(10, round(proportion * max_nulls))
            n = min(n, len(pool))
            sampled.extend(rng.sample(pool, n))
        if len(sampled) > max_nulls:
            sampled = rng.sample(sampled, max_nulls)

    results = []
    for seed_idx, pos, h, ah, band, intra in sampled:
        state = seeds[seed_idx]
        pf = pressure_cache[seed_idx]
        for trig_val in [1, -1]:
            r = run_trial(state, pos, trig_val, pf, barrier)
            if r is None:
                continue
            r["trial_id"] = f"b{barrier}_s{seed_idx}_p{pos}_v{trig_val}"
            results.append(r)

    return results, band_counts, intra_by_band


# ── Summary printing ─────────────────────────────────────────────────

def print_barrier_histogram(barrier, band_counts, intra_by_band, total_nulls):
    loaded = band_counts.get("loaded", 0)
    primed = band_counts.get("primed", 0)
    inert = band_counts.get("inert", 0)
    already = band_counts.get("already", 0)

    print(f"\n  barrier={barrier}: {total_nulls} nulls")
    print(f"    loaded  [{barrier-2}-{barrier-1}]: {loaded:5d} "
          f"({100*loaded/total_nulls:.1f}%) "
          f"intra={dict(sorted(intra_by_band.get('loaded', {}).items()))}")
    print(f"    primed  [{barrier//3}-{barrier-3}]: {primed:5d} "
          f"({100*primed/total_nulls:.1f}%) "
          f"intra={dict(sorted(intra_by_band.get('primed', {}).items()))}")
    print(f"    inert   [0-{barrier//3 - 1}]:    {inert:5d} "
          f"({100*inert/total_nulls:.1f}%)")
    print(f"    already [>={barrier}]:  {already:5d} "
          f"({100*already/total_nulls:.1f}%)")


def print_band_analysis(results, barrier):
    by_band = defaultdict(list)
    for r in results:
        by_band[r["pressure_band"]].append(r)

    print(f"\n  barrier={barrier} cascade analysis ({len(results)} trials):")
    for band in ["loaded", "primed", "inert", "already"]:
        subset = by_band.get(band, [])
        if not subset:
            print(f"    {band:>8s}: no trials")
            continue

        depths = [r["cascade_depth"] for r in subset]
        fired = [r for r in subset if r["cascade_depth"] > 0]
        fire_rate = 100 * len(fired) / len(subset)
        unique_ends = len(set(r["end_state_hash"] for r in subset))

        # +1/-1 asymmetry
        pairs = defaultdict(dict)
        for r in subset:
            key = (r["seed_state_hash"], r["trigger_position"])
            pairs[key][r["trigger_value"]] = r
        asym = sum(1 for v in pairs.values()
                   if 1 in v and -1 in v
                   and v[1]["end_state_hash"] != v[-1]["end_state_hash"])
        total_pairs = sum(1 for v in pairs.values() if 1 in v and -1 in v)

        # Intra-strand breakdown
        intra_fired = Counter()
        intra_total = Counter()
        for r in subset:
            idx = r["trigger_intra_strand_index"]
            intra_total[idx] += 1
            if r["cascade_depth"] > 0:
                intra_fired[idx] += 1

        mean_depth = sum(depths) / len(depths)
        mean_fired = (sum(r["cascade_depth"] for r in fired) / len(fired)
                     if fired else 0)

        print(f"    {band:>8s}: {len(subset):4d} trials, "
              f"fire={fire_rate:5.1f}%, "
              f"depth={mean_depth:.2f} (fired:{mean_fired:.2f}), "
              f"unique_ends={unique_ends}, "
              f"asym={asym}/{total_pairs}")
        # Per intra-strand index for loaded band
        if band == "loaded":
            for idx in sorted(intra_total.keys()):
                f = intra_fired.get(idx, 0)
                t = intra_total[idx]
                print(f"      idx={idx}: {t} trials, "
                      f"fired={f} ({100*f/t:.0f}%)")


def print_comparison_table(all_band_counts, all_intra_by_band,
                           all_results_by_barrier):
    """Final comparison table across all barriers."""
    print("\n" + "=" * 70)
    print("COMPARISON TABLE")
    print("=" * 70)
    print(f"{'barrier':>7s}  {'loaded%':>7s}  {'loaded_n':>8s}  "
          f"{'fire%':>6s}  {'depth':>6s}  {'asym%':>6s}  "
          f"{'loaded_intra_positions':>30s}")

    for barrier in BARRIERS:
        bc = all_band_counts[barrier]
        total = sum(bc.values())
        loaded_n = bc.get("loaded", 0)
        loaded_pct = 100 * loaded_n / total if total else 0

        # Loaded intra positions
        loaded_intra = all_intra_by_band[barrier].get("loaded", {})
        intra_str = ",".join(f"{k}" for k in sorted(loaded_intra.keys()))

        # Fire rate and depth at loaded nulls
        results = all_results_by_barrier.get(barrier, [])
        loaded_trials = [r for r in results if r["pressure_band"] == "loaded"]
        if loaded_trials:
            fired = [r for r in loaded_trials if r["cascade_depth"] > 0]
            fire_pct = 100 * len(fired) / len(loaded_trials)
            mean_depth = (sum(r["cascade_depth"] for r in fired) / len(fired)
                         if fired else 0)
            # Asymmetry
            pairs = defaultdict(dict)
            for r in loaded_trials:
                key = (r["seed_state_hash"], r["trigger_position"])
                pairs[key][r["trigger_value"]] = r
            asym = sum(1 for v in pairs.values()
                       if 1 in v and -1 in v
                       and v[1]["end_state_hash"] != v[-1]["end_state_hash"])
            total_pairs = sum(1 for v in pairs.values()
                             if 1 in v and -1 in v)
            asym_pct = 100 * asym / total_pairs if total_pairs else 0
        else:
            fire_pct = 0
            mean_depth = 0
            asym_pct = 0

        print(f"{barrier:>7d}  {loaded_pct:>6.1f}%  {loaded_n:>8d}  "
              f"{fire_pct:>5.1f}%  {mean_depth:>6.2f}  {asym_pct:>5.1f}%  "
              f"  idx={intra_str if intra_str else 'none'}")

    # Also print the P3I//2 arithmetic for reference
    print(f"\nP3I//2 values: ", end="")
    for i in range(TRITS):
        print(f"idx{i}={P3I[i]//2}", end="  ")
    print()
    print("Loaded range at each barrier: [barrier-2, barrier-1]")
    for barrier in BARRIERS:
        lo, hi = barrier - 2, barrier - 1
        matching = [i for i in range(TRITS) if lo <= P3I[i] // 2 <= hi]
        print(f"  barrier={barrier}: range=[{lo},{hi}], "
              f"P3I//2 matches idx={matching}")


# ── Main ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", type=int, default=0,
                        help="Run N trials per barrier and dump to terminal")
    args = parser.parse_args()

    os.makedirs(RESULTS_DIR, exist_ok=True)

    all_states = load_learned_seeds()
    print(f"Loaded {len(all_states)} motifs from krimelack")

    rng = random.Random(7777)
    if len(all_states) > 100:
        seeds = rng.sample(all_states, 100)
    else:
        seeds = list(all_states)

    all_band_counts = {}
    all_intra_by_band = {}
    all_results_by_barrier = {}
    all_results = []

    if args.dry_run > 0:
        print(f"=== Dry run: {args.dry_run} trials per barrier ===")
        for barrier in BARRIERS:
            print(f"\n--- barrier={barrier} ---")
            null_cat, bc, ibb = analyze_pressure_for_barrier(seeds, barrier)
            total_nulls = sum(bc.values())
            print_barrier_histogram(barrier, bc, ibb, total_nulls)

            results, _, _ = run_trials_for_barrier(
                seeds, barrier, dry_run_per_band=args.dry_run // 4 + 1)
            for r in results[:args.dry_run]:
                display = {k: v for k, v in r.items() if k != "diff_positions"}
                display["n_diff_positions"] = len(r["diff_positions"])
                print(json.dumps(display, indent=2))
            print(f"  ({len(results)} trials)")
        return

    # Full run
    for barrier in BARRIERS:
        print(f"\n=== Barrier {barrier} ===")
        null_cat, bc, ibb = analyze_pressure_for_barrier(seeds, barrier)
        total_nulls = sum(bc.values())
        print_barrier_histogram(barrier, bc, ibb, total_nulls)
        all_band_counts[barrier] = bc
        all_intra_by_band[barrier] = ibb

        results, _, _ = run_trials_for_barrier(seeds, barrier, max_trials=1500)
        print(f"  {len(results)} trials")
        print_band_analysis(results, barrier)
        all_results_by_barrier[barrier] = results
        all_results.extend(results)

    # Write results
    with open(RESULTS_FILE, "w") as f:
        for r in all_results:
            f.write(json.dumps(r) + "\n")
    print(f"\nWritten {len(all_results)} trials to {RESULTS_FILE}")

    # Comparison table
    print_comparison_table(all_band_counts, all_intra_by_band,
                           all_results_by_barrier)


if __name__ == "__main__":
    main()
