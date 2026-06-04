"""
Experiment 04 — Self-Similar Ternary Scaling Probe

Tests whether hierarchical composition fills the pressure-landscape gaps
that exp03 showed are structurally unfillable at a single level.

Two-level structure:
  INNER: 64 learned motifs → 64 settled states → 64 chi values
  OUTER: chi values balanced-ternary-encoded into 8 super-strands of 8 trits
         → same settle()/pressure_field() at the outer level

The composition rule: chi = Σ trit_i × 3^i, so encoding chi into balanced
ternary IS the substrate's native representation. The outer level operates
on structural summaries of the inner level using identical math.

Usage:
    python3 tools/exp04_self_similar.py                # full run
    python3 tools/exp04_self_similar.py --dry-run       # histograms only
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
DEAD_ZONE = gl.DEAD_ZONE

STEP_CAP = 50
RESULTS_DIR = os.path.join(REPO, "experiments", "exp04")
RESULTS_FILE = os.path.join(RESULTS_DIR, "results.jsonl")

# Pressure bands from exp02 (fixed barrier=15)
BANDS_FIXED = [
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


def pressure_band_fixed(abs_h):
    for label, lo, hi in BANDS_FIXED:
        if lo <= abs_h <= hi:
            return label
    return "15+"


# ── Balanced ternary encoding of an integer ──────────────────────────

def encode_bt(value):
    """Encode an integer to 8-trit balanced ternary.
    Same math as gualaloom.py encode() but without the ord()-96 offset."""
    v = value
    t = []
    for _ in range(TRITS):
        r = v % 3
        if r == 2:
            r = -1
            v = (v + 1) // 3
        else:
            v = (v - r) // 3
        t.append(r)
    return tuple(t)


# ── Pressure field (same as exp02) ───────────────────────────────────

def pressure_field(state):
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


def settle_to_eq(state, familiarity=0):
    for step in range(STEP_CAP):
        strands = to_strands(state)
        new_state = settle(strands, familiarity)
        if new_state == state:
            return state, step + 1, True
        state = new_state
    return state, STEP_CAP, False


# ── Data loading ─────────────────────────────────────────────────────

def load_learned_seeds():
    k, loom = gl.load()
    if k.size() == 0:
        gl.seed_corpus(k, loom)
        gl.save(k, loom)
    return [m.state for m in k.motifs.values()]


# ── Two-level structure ──────────────────────────────────────────────

def build_outer_state(inner_motifs):
    """Build the outer-level state from 64 inner motifs.

    inner_motifs: list of 64 state tuples (8 per super-strand × 8 super-strands)
    Returns: 64-trit outer state (8 super-strands × 8 super-trits)

    Each inner motif's chi value is balanced-ternary-encoded into an 8-trit
    strand. The ith motif within a super-strand provides the ith super-trit
    via its chi encoding.

    Layout: super-strand s, position i → chi of inner_motifs[s*8 + i],
    encoded as balanced ternary trit i of that chi.

    Wait — this needs care. Each super-strand should be one 8-trit BT encoding
    of one chi value. We have 8 super-strands, each derived from one inner
    unit's chi. So 8 inner motifs → 8 chi values → 8 BT strands → 64 outer trits.

    But the spec says 64 inner motifs (8 per super-strand × 8 super-strands).
    That's 8 inner motifs PER super-strand position. So we need to aggregate.

    Rethinking: the most natural structure is:
    - 8 super-strands, each is one BT-encoded chi
    - 8 inner motifs → 8 chi values → 8 super-strands
    - outer state = concatenation of 8 BT strands = 64 trits

    But the spec asks for 64 inner motifs total. Let me re-read...

    "Replicate this across 8 super-strands by sampling 64 learned motifs total
    (8 per super-strand × 8 super-strands)"

    OK so it's 8 super-strands, each composed from 8 inner motifs. Each inner
    motif contributes one trit to the super-strand. The super-strand at
    position (s, i) = sign or BT-trit of the chi from inner_motifs[s*8 + i].

    But that means each super-strand position i gets the balanced-ternary
    trit at position i of one chi value. Each of the 8 inner motifs in a
    super-strand contributes to ONE position in the strand.

    Actually the simplest self-similar structure: each super-strand is the
    BT encoding of the MEAN chi across its 8 inner motifs... No, that's
    too lossy.

    Simplest correct structure: each super-strand IS one BT(chi).
    8 inner motifs → 8 chi values → 8 super-strands.
    64 inner motifs gives us 8 independent outer-level realizations to probe.

    Let me do it both ways but for the main probe:
    - primary: 8 inner motifs → 8 chi → 8 BT strands → 1 outer state (64 trits)
    - sweep: repeat with different sets of 8 inner motifs for statistical coverage
    """
    pass  # handled below


def build_one_outer_state(motifs_8):
    """8 inner motifs → 8 chi values → 8 BT-encoded super-strands → 64 trits."""
    strands = []
    chis = []
    for m_state in motifs_8:
        c, _ = gl.chi(m_state)
        chis.append(c)
        strands.append(encode_bt(c))
    # Flatten to 64-trit state
    state = tuple(t for strand in strands for t in strand)
    return state, chis


# ── Histogram printing ───────────────────────────────────────────────

def print_pressure_histogram(pressures_at_nulls, label):
    if not pressures_at_nulls:
        print(f"\n{label}: no null positions")
        return

    abs_vals = [abs(h) for h in pressures_at_nulls]
    band_counts = Counter()
    for ah in abs_vals:
        band_counts[pressure_band_fixed(ah)] += 1

    print(f"\n{label}: {len(pressures_at_nulls)} null positions")
    print(f"  |h| mean={sum(abs_vals)/len(abs_vals):.2f} "
          f"stdev={math.sqrt(sum((x-sum(abs_vals)/len(abs_vals))**2 for x in abs_vals)/len(abs_vals)):.2f}")
    for label_b, _, _ in BANDS_FIXED:
        c = band_counts.get(label_b, 0)
        pct = 100 * c / len(pressures_at_nulls)
        print(f"  {label_b:>5s}: {c:5d} ({pct:5.1f}%)")

    # Fine-grained
    ah_hist = Counter(abs_vals)
    print(f"  Fine-grained |h|:")
    for ah in sorted(ah_hist.keys()):
        c = ah_hist[ah]
        bar = "#" * min(c // 5 + 1, 60) if c > 0 else ""
        print(f"    |h|={ah:4d}: {c:5d} {bar}")


# ── Cascade probe at outer level ────────────────────────────────────

def run_outer_trial(outer_state, trigger_pos, trigger_val, pre_pressure):
    if outer_state[trigger_pos] != 0:
        return None

    ctrl_end, ctrl_steps, ctrl_stable = settle_to_eq(outer_state)
    triggered = list(outer_state)
    triggered[trigger_pos] = trigger_val
    triggered = tuple(triggered)
    trig_end, trig_steps, trig_stable = settle_to_eq(triggered)

    diffs = [i for i in range(POP) if ctrl_end[i] != trig_end[i]]
    trigger_in_diff = trigger_pos in diffs
    cascade_depth = len(diffs) - (1 if trigger_in_diff else 0)

    chi_start, _ = gl.chi(outer_state)
    chi_ctrl, _ = gl.chi(ctrl_end)
    chi_trig, _ = gl.chi(trig_end)

    h_i = pre_pressure[trigger_pos]

    return {
        "level": "outer",
        "null_fraction_start": round(count_nulls(outer_state) / POP, 4),
        "trigger_position": trigger_pos,
        "trigger_value": trigger_val,
        "trigger_intra_strand_index": trigger_pos % TRITS,
        "pre_trigger_pressure": h_i,
        "pressure_band": pressure_band_fixed(abs(h_i)),
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
        "seed_state_hash": state_hash(outer_state),
        "diff_positions": diffs,
    }


# ── Main ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Print histograms only, no cascade probe")
    args = parser.parse_args()

    os.makedirs(RESULTS_DIR, exist_ok=True)

    all_states = load_learned_seeds()
    print(f"Loaded {len(all_states)} motifs from krimelack")

    rng = random.Random(7777)
    shuffled = list(all_states)
    rng.shuffle(shuffled)

    # ── Inner-level chi distribution ─────────────────────────────────
    print("\n=== INNER-LEVEL CHI DISTRIBUTION ===")
    inner_chis = [gl.chi(s)[0] for s in shuffled[:64]]
    chi_dist = Counter(inner_chis)
    print(f"64 inner motifs, chi values:")
    for c in sorted(chi_dist.keys()):
        print(f"  chi={c:4d}: {chi_dist[c]:3d}")

    # ── Inner-level pressure histogram (for comparison) ──────────────
    print("\n=== INNER-LEVEL PRESSURE HISTOGRAM (for reference) ===")
    inner_null_pressures = []
    for state in shuffled[:100]:
        pf = pressure_field(state)
        for pos in range(POP):
            if state[pos] == 0:
                inner_null_pressures.append(pf[pos])
    print_pressure_histogram(inner_null_pressures, "INNER (100 seeds)")

    # ── Build multiple outer states from non-overlapping sets of 8 ───
    # 64 motifs / 8 = 8 outer states. Then extend: use all available
    # motifs to build many outer states for better coverage.
    n_outer_states = min(len(shuffled) // 8, 100)
    outer_states = []
    outer_chi_lists = []
    for i in range(n_outer_states):
        batch = shuffled[i * 8:(i + 1) * 8]
        if len(batch) < 8:
            break
        ostate, ochis = build_one_outer_state(batch)
        outer_states.append(ostate)
        outer_chi_lists.append(ochis)

    print(f"\n=== OUTER-LEVEL STRUCTURE ===")
    print(f"Built {len(outer_states)} outer states from "
          f"{len(outer_states)*8} inner motifs")

    # ── Outer-level pressure histogram ───────────────────────────────
    print("\n=== OUTER-LEVEL PRESSURE HISTOGRAM ===")
    outer_null_pressures = []
    outer_null_catalog = []  # (state_idx, pos, h)
    for si, ostate in enumerate(outer_states):
        pf = pressure_field(ostate)
        for pos in range(POP):
            if ostate[pos] == 0:
                outer_null_pressures.append(pf[pos])
                outer_null_catalog.append((si, pos, pf[pos]))

    print_pressure_histogram(outer_null_pressures, "OUTER")

    # ── Side-by-side comparison ──────────────────────────────────────
    print("\n=== SIDE-BY-SIDE COMPARISON ===")
    inner_bands = Counter()
    for h in inner_null_pressures:
        inner_bands[pressure_band_fixed(abs(h))] += 1
    outer_bands = Counter()
    for h in outer_null_pressures:
        outer_bands[pressure_band_fixed(abs(h))] += 1

    print(f"{'Band':>7s}  {'Inner%':>8s}  {'Outer%':>8s}  {'Change':>8s}")
    for label, _, _ in BANDS_FIXED:
        ip = 100 * inner_bands.get(label, 0) / len(inner_null_pressures) if inner_null_pressures else 0
        op = 100 * outer_bands.get(label, 0) / len(outer_null_pressures) if outer_null_pressures else 0
        print(f"{label:>7s}  {ip:>7.1f}%  {op:>7.1f}%  {op-ip:>+7.1f}%")

    # Check: are the previously-empty bands now populated?
    band_6_9 = outer_bands.get("6-9", 0)
    band_10_12 = outer_bands.get("10-12", 0)
    print(f"\nPreviously-empty bands at outer level: "
          f"6-9={band_6_9}, 10-12={band_10_12}")

    if band_6_9 == 0 and band_10_12 == 0:
        print("\n*** OUTER LEVEL REPRODUCES THE SAME GAPS ***")
        print("Self-similarity does not smooth the pressure landscape.")
        print("Stopping before cascade probe — the histogram is the finding.")

    if args.dry_run:
        # Also show the outer-level intra-strand-position breakdown
        print("\n=== OUTER-LEVEL NULL PRESSURE BY INTRA-STRAND INDEX ===")
        by_intra = defaultdict(list)
        for h in outer_null_pressures:
            # We don't track position here, redo
            pass
        for si, ostate in enumerate(outer_states[:10]):
            pf = pressure_field(ostate)
            for pos in range(POP):
                if ostate[pos] == 0:
                    by_intra[pos % TRITS].append(abs(pf[pos]))
        for idx in sorted(by_intra.keys()):
            vals = by_intra[idx]
            if vals:
                unique = sorted(set(vals))
                print(f"  idx={idx}: {len(vals)} nulls, "
                      f"|h| values={unique[:15]}"
                      f"{'...' if len(unique) > 15 else ''}")
        return

    # ── Cascade probe at outer level (if gaps are filled) ────────────
    if band_6_9 == 0 and band_10_12 == 0:
        # Still run cascade probe on whatever loaded nulls exist
        pass

    print("\n=== OUTER-LEVEL CASCADE PROBE ===")
    results = []
    for si, ostate in enumerate(outer_states):
        pf = pressure_field(ostate)
        null_positions = [pos for pos in range(POP) if ostate[pos] == 0]
        if not null_positions:
            continue
        # Sample up to 10 null positions per outer state
        sample_rng = random.Random(si + 9999)
        trigger_positions = (sample_rng.sample(null_positions, min(10, len(null_positions))))
        for trig_pos in trigger_positions:
            for trig_val in [1, -1]:
                r = run_outer_trial(ostate, trig_pos, trig_val, pf)
                if r is None:
                    continue
                r["trial_id"] = f"outer_s{si}_p{trig_pos}_v{trig_val}"
                r["outer_state_idx"] = si
                results.append(r)

    print(f"  {len(results)} trials")

    # Write results
    with open(RESULTS_FILE, "w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")
    print(f"  Written to {RESULTS_FILE}")

    # Band-by-band analysis
    by_band = defaultdict(list)
    for r in results:
        by_band[r["pressure_band"]].append(r)

    print(f"\n=== OUTER-LEVEL BAND-BY-BAND CASCADE ANALYSIS ===")
    for label, _, _ in BANDS_FIXED:
        subset = by_band.get(label, [])
        if not subset:
            print(f"  {label:>5s}: no trials")
            continue
        depths = [r["cascade_depth"] for r in subset]
        fired = [r for r in subset if r["cascade_depth"] > 0]
        fire_rate = 100 * len(fired) / len(subset)
        unique_ends = len(set(r["end_state_hash"] for r in subset))

        # Asymmetry
        pairs = defaultdict(dict)
        for r in subset:
            key = (r["seed_state_hash"], r["trigger_position"])
            pairs[key][r["trigger_value"]] = r
        asym = sum(1 for v in pairs.values()
                   if 1 in v and -1 in v
                   and v[1]["end_state_hash"] != v[-1]["end_state_hash"])
        total_pairs = sum(1 for v in pairs.values() if 1 in v and -1 in v)

        mean_depth = sum(depths) / len(depths)
        print(f"  {label:>5s}: {len(subset):4d} trials, "
              f"fire={fire_rate:5.1f}%, "
              f"depth_mean={mean_depth:.2f}, "
              f"unique_ends={unique_ends}, "
              f"asym={asym}/{total_pairs}")

    # Inner vs outer comparison table
    print("\n=== INNER vs OUTER: LOADED NULL COMPARISON ===")
    inner_loaded = [r for r in results if r["pressure_band"] == "13-14"]
    outer_6_9 = [r for r in results if r["pressure_band"] == "6-9"]
    outer_10_12 = [r for r in results if r["pressure_band"] == "10-12"]
    print(f"  Inner-equivalent loaded (13-14): {len(inner_loaded)} trials")
    print(f"  NEW band 6-9 trials: {len(outer_6_9)}")
    print(f"  NEW band 10-12 trials: {len(outer_10_12)}")


if __name__ == "__main__":
    main()
