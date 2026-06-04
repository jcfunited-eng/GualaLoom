"""
Experiment 02 — Pressure Instrumentation

Tests whether pre-trigger pressure (h) at null positions predicts
cascade behavior. The loaded-null hypothesis: nulls with high |h|
(close to the barrier) should fire more often and produce more
content-sensitive cascades than nulls with low |h|.

Step 1: pressure_field() — expose h at every position, no commit.
Step 2: population pressure histogram across all null positions.
Step 3: trigger each null, record cascade_depth + pressure band.
Step 4: group by pressure band, compare firing rate + end-state diversity.
Step 5: +1/-1 asymmetry in the highest-pressure band.

Usage:
    python3 tools/exp02_pressure.py                # full run
    python3 tools/exp02_pressure.py --dry-run 20   # 20 trials across bands
    python3 tools/exp02_pressure.py --histogram     # pressure histogram only
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

settle = gl.settle
P3I = gl.P3I
TRITS = gl.TRITS
CONTEXT = gl.CONTEXT
POP = TRITS * CONTEXT
DEAD_ZONE = gl.DEAD_ZONE  # 15

STEP_CAP = 50
RESULTS_DIR = os.path.join(REPO, "experiments", "exp02")
RESULTS_FILE = os.path.join(RESULTS_DIR, "results.jsonl")

# Pressure bands: |h| value ranges
BANDS = [
    ("0-5", 0, 5),
    ("6-9", 6, 9),
    ("10-12", 10, 12),
    ("13-14", 13, 14),
    ("15+", 15, 9999),
]


def state_hash(state):
    s = "".join({-1: "-", 0: "0", 1: "+"}[t] for t in state)
    return hashlib.sha1(s.encode()).hexdigest()[:12]


def to_strands(state):
    return [state[j * TRITS:(j + 1) * TRITS] for j in range(CONTEXT)]


def count_nulls(state):
    return sum(1 for t in state if t == 0)


# ── Step 1: pressure_field ──────────────────────────────────────────

def pressure_field(state, familiarity=0):
    """Compute h at every position — the raw pressure before any commit.

    Returns a 64-element list of ints. This is exactly the h that settle()
    computes internally, but exposed instead of fed into the barrier check.

    h(s, i) = strand[s][i] * P3I[i] + Σ_{o≠s} strand[o][i] * P3I[i] // 2
    """
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


def pressure_band(abs_h):
    """Classify |h| into a band label."""
    for label, lo, hi in BANDS:
        if lo <= abs_h <= hi:
            return label
    return "15+"


# ── Cascade probe (same as exp01) ───────────────────────────────────

def settle_to_eq(state, familiarity=0):
    for step in range(STEP_CAP):
        strands = to_strands(state)
        new_state = settle(strands, familiarity)
        if new_state == state:
            return state, step + 1, True
        state = new_state
    return state, STEP_CAP, False


def run_trial(seed_state, trigger_pos, trigger_val, pre_pressure,
              familiarity=0):
    """Differential probe: control vs trigger, with pressure annotation."""
    if seed_state[trigger_pos] != 0:
        return None

    # Control
    ctrl_end, ctrl_steps, ctrl_stable = settle_to_eq(seed_state, familiarity)

    # Trigger
    triggered = list(seed_state)
    triggered[trigger_pos] = trigger_val
    triggered = tuple(triggered)
    trig_end, trig_steps, trig_stable = settle_to_eq(triggered, familiarity)

    # Diff
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
        "null_fraction_start": round(count_nulls(seed_state) / POP, 4),
        "trigger_position": trigger_pos,
        "trigger_value": trigger_val,
        "trigger_intra_strand_index": trigger_pos % TRITS,
        "pre_trigger_pressure": h_i,
        "pressure_band": pressure_band(abs(h_i)),
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


# ── Step 2: pressure histogram ──────────────────────────────────────

def compute_pressure_histogram(seeds):
    """Compute |h| for every null position across all seeds."""
    all_pressures = []       # (seed_idx, pos, h, |h|, band)
    band_counts = Counter()

    for seed_idx, state in enumerate(seeds):
        pf = pressure_field(state, familiarity=0)
        for pos in range(POP):
            if state[pos] == 0:  # null position
                h = pf[pos]
                ah = abs(h)
                b = pressure_band(ah)
                all_pressures.append((seed_idx, pos, h, ah, b))
                band_counts[b] += 1

    return all_pressures, band_counts


def print_histogram(all_pressures, band_counts):
    abs_vals = [p[3] for p in all_pressures]
    signed_vals = [p[2] for p in all_pressures]

    print(f"\n=== Pressure histogram: {len(all_pressures)} null positions "
          f"across {len(set(p[0] for p in all_pressures))} seeds ===")
    print(f"  |h| mean={sum(abs_vals)/len(abs_vals):.2f} "
          f"stdev={math.sqrt(sum((x - sum(abs_vals)/len(abs_vals))**2 for x in abs_vals)/len(abs_vals)):.2f}")
    print(f"  h (signed) mean={sum(signed_vals)/len(signed_vals):.2f}")
    print(f"  Band distribution:")
    for label, _, _ in BANDS:
        c = band_counts.get(label, 0)
        pct = 100 * c / len(all_pressures) if all_pressures else 0
        print(f"    {label:>5s}: {c:5d} ({pct:5.1f}%)")

    # Fine-grained histogram of |h|
    ah_hist = Counter(p[3] for p in all_pressures)
    print(f"  Fine-grained |h| distribution:")
    for ah in sorted(ah_hist.keys()):
        c = ah_hist[ah]
        bar = "#" * min(c // 50, 60)
        print(f"    |h|={ah:4d}: {c:5d} {bar}")


# ── Step 3+4: trial runner with band-proportional sampling ──────────

def run_all_trials(seeds, max_trials=2000, dry_run_per_band=0):
    """Sample nulls proportionally by band so all bands are represented."""
    # First, collect all (seed_idx, pos, h, band) for null positions
    null_catalog = []
    for seed_idx, state in enumerate(seeds):
        pf = pressure_field(state, familiarity=0)
        for pos in range(POP):
            if state[pos] == 0:
                h = pf[pos]
                b = pressure_band(abs(h))
                null_catalog.append((seed_idx, pos, h, b))

    # Group by band
    by_band = defaultdict(list)
    for entry in null_catalog:
        by_band[entry[3]].append(entry)

    print(f"  Null positions by band:")
    for label, _, _ in BANDS:
        print(f"    {label}: {len(by_band.get(label, []))}")

    # Sample: proportional to band membership, but ensure at least
    # some from each non-empty band. Each null gets 2 trials (+1, -1).
    rng = random.Random(4242)

    if dry_run_per_band > 0:
        # Dry run: take up to dry_run_per_band from each band
        sampled = []
        for label, _, _ in BANDS:
            pool = by_band.get(label, [])
            if not pool:
                continue
            n = min(dry_run_per_band, len(pool))
            sampled.extend(rng.sample(pool, n))
    else:
        # Full run: max_trials total trials (each null = 2 trials)
        max_nulls = max_trials // 2
        total_nulls = len(null_catalog)

        sampled = []
        for label, _, _ in BANDS:
            pool = by_band.get(label, [])
            if not pool:
                continue
            # Proportional allocation, minimum 10 per band
            proportion = len(pool) / total_nulls
            n = max(10, round(proportion * max_nulls))
            n = min(n, len(pool))
            sampled.extend(rng.sample(pool, n))

        # Trim to max_nulls if overallocated
        if len(sampled) > max_nulls:
            sampled = rng.sample(sampled, max_nulls)

    # Run trials
    results = []
    for seed_idx, pos, h, band in sampled:
        state = seeds[seed_idx]
        pf = pressure_field(state, familiarity=0)
        for trig_val in [1, -1]:
            r = run_trial(state, pos, trig_val, pf)
            if r is None:
                continue
            r["trial_id"] = f"learned_s{seed_idx}_p{pos}_v{trig_val}"
            results.append(r)

    return results


# ── Step 5: +1/-1 asymmetry analysis ────────────────────────────────

def asymmetry_analysis(results):
    """In the highest-pressure band (10-14), do +1 and -1 produce
    different cascades?"""
    high_pressure = [r for r in results if r["pressure_band"] in ("10-12", "13-14")]

    # Group by (seed_state_hash, trigger_position)
    pairs = defaultdict(dict)
    for r in high_pressure:
        key = (r["seed_state_hash"], r["trigger_position"])
        pairs[key][r["trigger_value"]] = r

    asymmetric = 0
    symmetric = 0
    for key, vals in pairs.items():
        if 1 in vals and -1 in vals:
            if vals[1]["end_state_hash"] != vals[-1]["end_state_hash"]:
                asymmetric += 1
            else:
                symmetric += 1

    return asymmetric, symmetric


# ── Summary ──────────────────────────────────────────────────────────

def print_band_analysis(results):
    by_band = defaultdict(list)
    for r in results:
        by_band[r["pressure_band"]].append(r)

    print(f"\n=== Band-by-band cascade analysis ({len(results)} trials) ===")
    for label, _, _ in BANDS:
        subset = by_band.get(label, [])
        if not subset:
            print(f"  {label:>5s}: no trials")
            continue

        depths = [r["cascade_depth"] for r in subset]
        fired = [r for r in subset if r["cascade_depth"] > 0]
        fire_rate = len(fired) / len(subset) * 100

        unique_ends = len(set(r["end_state_hash"] for r in subset))
        unique_ends_fired = len(set(r["end_state_hash"] for r in fired)) if fired else 0

        mean_depth = sum(depths) / len(depths)
        mean_depth_fired = (sum(r["cascade_depth"] for r in fired) / len(fired)
                           if fired else 0)

        # Pressure stats within band
        pressures = [abs(r["pre_trigger_pressure"]) for r in subset]

        print(f"  {label:>5s}: {len(subset):4d} trials, "
              f"fire_rate={fire_rate:5.1f}%, "
              f"mean_depth={mean_depth:.2f} (fired: {mean_depth_fired:.2f}), "
              f"unique_ends={unique_ends} (fired: {unique_ends_fired}), "
              f"|h| range=[{min(pressures)}, {max(pressures)}]")

    # Asymmetry
    asym, sym = asymmetry_analysis(results)
    print(f"\n  +1/-1 asymmetry in bands 10-14: "
          f"{asym} asymmetric, {sym} symmetric pairs")
    if asym + sym > 0:
        print(f"  asymmetry rate: {100*asym/(asym+sym):.1f}%")


# ── Main ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", type=int, default=0,
                        help="Run N trials per band and dump to terminal")
    parser.add_argument("--histogram", action="store_true",
                        help="Print pressure histogram only, no trials")
    args = parser.parse_args()

    os.makedirs(RESULTS_DIR, exist_ok=True)

    all_states = load_learned_seeds()
    print(f"Loaded {len(all_states)} motifs from krimelack")

    # Use same 100 seeds as exp01/015
    rng = random.Random(7777)
    if len(all_states) > 100:
        seeds = rng.sample(all_states, 100)
    else:
        seeds = list(all_states)

    # Step 2: pressure histogram (always)
    all_pressures, band_counts = compute_pressure_histogram(seeds)
    print_histogram(all_pressures, band_counts)

    if args.histogram:
        return

    if args.dry_run > 0:
        print(f"\n=== Dry run: {args.dry_run} nulls per band ===")
        results = run_all_trials(seeds, dry_run_per_band=args.dry_run)
        for r in results:
            display = {k: v for k, v in r.items() if k != "diff_positions"}
            display["n_diff_positions"] = len(r["diff_positions"])
            print(json.dumps(display, indent=2))
        print(f"\n--- {len(results)} trials ---")
        print_band_analysis(results)
        return

    # Full run
    print(f"\n=== Running trials (target 2000) ===")
    results = run_all_trials(seeds, max_trials=2000)
    print(f"  Total: {len(results)} trials")

    with open(RESULTS_FILE, "w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")
    print(f"  Written to {RESULTS_FILE}")

    print_band_analysis(results)


if __name__ == "__main__":
    main()
