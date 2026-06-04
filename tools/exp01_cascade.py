"""
Experiment 01 — Cascade Existence (revised)

Two-step differential probe: for each learned motif and trigger,
re-settle the unmodified seed (control) and re-settle with one null
committed (trigger). Cascade depth = positions where the two end-states
differ, minus the trigger position itself.

Learned seeds only. Synthetic seeds dropped — settle recomputes from
strands, so random states that were never produced by settle dissolve
on re-evaluation. That's a property of the rule, not a bug.

Uses gualaloom.py's settle() directly. No new operators. No tuning.

Usage:
    python3 tools/exp01_cascade.py                # full run
    python3 tools/exp01_cascade.py --dry-run 10   # schema sanity check
    python3 tools/exp01_cascade.py --repro-only    # reproducibility only
"""

import os, sys, json, hashlib, random, argparse

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(REPO)
sys.path.insert(0, REPO)

import importlib.util
_spec = importlib.util.spec_from_file_location("gualaloom", os.path.join(REPO, "gualaloom.py"))
gl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gl)

settle = gl.settle
TRITS = gl.TRITS      # 8
CONTEXT = gl.CONTEXT   # 8
POP = TRITS * CONTEXT  # 64

STEP_CAP = 50
RESULTS_DIR = os.path.join(REPO, "experiments", "exp01")
RESULTS_FILE = os.path.join(RESULTS_DIR, "results.jsonl")


def state_hash(state):
    s = "".join({-1: "-", 0: "0", 1: "+"}[t] for t in state)
    return hashlib.sha1(s.encode()).hexdigest()[:12]


def to_strands(state):
    return [state[j * TRITS:(j + 1) * TRITS] for j in range(CONTEXT)]


def count_nulls(state):
    return sum(1 for t in state if t == 0)


def chi(state):
    return gl.chi(state)


def settle_to_equilibrium(state, familiarity=0):
    """Iterate settle until stable or step cap. Returns (end_state, steps, stable)."""
    for step in range(STEP_CAP):
        strands = to_strands(state)
        new_state = settle(strands, familiarity)
        if new_state == state:
            return state, step + 1, True
        state = new_state
    return state, STEP_CAP, False


def run_trial(seed_state, trigger_pos, trigger_val, familiarity=0):
    """Two-step differential probe.

    1. Control: re-settle the unmodified seed to its natural equilibrium.
    2. Trigger: commit one null in the seed, then re-settle.
    3. Cascade depth = positions where trigger end-state differs from
       control end-state, minus the trigger position itself.
    """
    if seed_state[trigger_pos] != 0:
        return None

    # Step 1: control re-settle
    control_end, control_steps, control_stable = settle_to_equilibrium(
        seed_state, familiarity)

    # Step 2: apply trigger, then re-settle
    triggered = list(seed_state)
    triggered[trigger_pos] = trigger_val
    triggered = tuple(triggered)
    trigger_end, trigger_steps, trigger_stable = settle_to_equilibrium(
        triggered, familiarity)

    # Cascade depth: positions that differ between control and trigger
    # end-states, minus the trigger position itself
    diffs = [i for i in range(POP) if control_end[i] != trigger_end[i]]
    # Remove the trigger position from the diff count if it differs
    # (it should, since we forced it — but if settle happened to
    # produce the same value at that position anyway, don't subtract)
    trigger_in_diff = trigger_pos in diffs
    cascade_depth = len(diffs) - (1 if trigger_in_diff else 0)

    chi_start, _ = chi(seed_state)
    chi_control, _ = chi(control_end)
    chi_trigger, _ = chi(trigger_end)

    return {
        "trial_id": None,  # filled by caller
        "seed_source": "learned",
        "null_fraction_start": round(count_nulls(seed_state) / POP, 4),
        "trigger_position": trigger_pos,
        "trigger_value": trigger_val,
        "cascade_depth": cascade_depth,
        "cascade_latency_steps": trigger_steps,
        "control_latency_steps": control_steps,
        "final_null_fraction": round(count_nulls(trigger_end) / POP, 4),
        "control_null_fraction": round(count_nulls(control_end) / POP, 4),
        "chi_start": chi_start,
        "chi_control": chi_control,
        "chi_trigger": chi_trigger,
        "stable": trigger_stable,
        "control_stable": control_stable,
        "end_state_hash": state_hash(trigger_end),
        "control_end_state_hash": state_hash(control_end),
        "seed_state_hash": state_hash(seed_state),
        "diff_positions": diffs,
    }


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
    return [m.state for m in k.motifs.values()]


def run_all_trials(max_trials=None):
    learned_states = load_learned_seeds()
    print(f"  Loaded {len(learned_states)} motifs from krimelack")

    rng = random.Random(7777)
    if len(learned_states) > 100:
        seeds = rng.sample(learned_states, 100)
    else:
        seeds = list(learned_states)

    results = []
    for seed_idx, seed_state in enumerate(seeds):
        null_positions = get_null_positions(seed_state)
        if not null_positions:
            continue
        trigger_positions = pick_trigger_positions(null_positions, 10, rng)
        for trig_pos in trigger_positions:
            for trig_val in [1, -1]:
                r = run_trial(seed_state, trig_pos, trig_val)
                if r is None:
                    continue
                r["trial_id"] = f"learned_s{seed_idx}_p{trig_pos}_v{trig_val}"
                results.append(r)
                if max_trials and len(results) >= max_trials:
                    return results
    return results


def run_reproducibility_check():
    """Run 50 trials twice, verify both control and trigger hashes match."""
    learned_states = load_learned_seeds()
    rng_a = random.Random(8888)
    rng_b = random.Random(8888)

    subset_a = rng_a.sample(learned_states, min(25, len(learned_states)))
    subset_b = rng_b.sample(learned_states, min(25, len(learned_states)))

    pairs = []
    for sa, sb in zip(subset_a, subset_b):
        null_pos = get_null_positions(sa)
        if not null_pos:
            continue
        trig_pos = null_pos[0]
        for trig_val in [1, -1]:
            ra = run_trial(sa, trig_pos, trig_val)
            rb = run_trial(sb, trig_pos, trig_val)
            if ra and rb:
                pairs.append({
                    "control_match": ra["control_end_state_hash"] == rb["control_end_state_hash"],
                    "trigger_match": ra["end_state_hash"] == rb["end_state_hash"],
                })

    control_mismatches = sum(1 for p in pairs if not p["control_match"])
    trigger_mismatches = sum(1 for p in pairs if not p["trigger_match"])
    return len(pairs), control_mismatches, trigger_mismatches


def print_summary(results):
    if not results:
        print("  No results.")
        return

    depths = [r["cascade_depth"] for r in results]
    stables = [r["stable"] for r in results]
    ctrl_stables = [r["control_stable"] for r in results]
    steps = [r["cascade_latency_steps"] for r in results]

    # How many seeds had nulls to trigger at all
    seeds_with_nulls = len(set(r["seed_state_hash"] for r in results))

    # Null fraction distribution of the seeds
    nf_starts = [r["null_fraction_start"] for r in results]

    print(f"\nlearned ({len(results)} trials from {seeds_with_nulls} seeds):")
    print(f"  cascade_depth: min={min(depths)} max={max(depths)} "
          f"mean={sum(depths)/len(depths):.2f} "
          f"median={sorted(depths)[len(depths)//2]}")
    print(f"  depth=0: {sum(1 for d in depths if d == 0)} "
          f"({100*sum(1 for d in depths if d == 0)/len(depths):.1f}%)")
    print(f"  depth>0: {sum(1 for d in depths if d > 0)} "
          f"({100*sum(1 for d in depths if d > 0)/len(depths):.1f}%)")
    print(f"  trigger stable: {sum(stables)}/{len(stables)} "
          f"({100*sum(stables)/len(stables):.1f}%)")
    print(f"  control stable: {sum(ctrl_stables)}/{len(ctrl_stables)} "
          f"({100*sum(ctrl_stables)/len(ctrl_stables):.1f}%)")
    print(f"  trigger steps: min={min(steps)} max={max(steps)} "
          f"mean={sum(steps)/len(steps):.2f}")
    print(f"  null_fraction_start: min={min(nf_starts):.4f} "
          f"max={max(nf_starts):.4f} mean={sum(nf_starts)/len(nf_starts):.4f}")

    # Depth distribution
    from collections import Counter
    depth_dist = Counter(depths)
    print(f"  depth distribution: {dict(sorted(depth_dist.items()))}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", type=int, default=0,
                        help="Run N trials and dump to terminal for schema check")
    parser.add_argument("--repro-only", action="store_true")
    args = parser.parse_args()

    os.makedirs(RESULTS_DIR, exist_ok=True)

    if args.repro_only:
        total, ctrl_mm, trig_mm = run_reproducibility_check()
        print(f"Reproducibility: {total} trials")
        print(f"  control mismatches: {ctrl_mm}")
        print(f"  trigger mismatches: {trig_mm}")
        return

    if args.dry_run > 0:
        print(f"=== Dry run: {args.dry_run} trials ===\n")
        results = run_all_trials(max_trials=args.dry_run)
        for r in results:
            # Print without diff_positions for readability
            display = {k: v for k, v in r.items() if k != "diff_positions"}
            display["n_diff_positions"] = len(r["diff_positions"])
            print(json.dumps(display, indent=2))
        print(f"\n--- {len(results)} trials ---")
        return

    # Full run
    print("=== Reproducibility check ===")
    total, ctrl_mm, trig_mm = run_reproducibility_check()
    print(f"  {total} trials, control mismatches: {ctrl_mm}, "
          f"trigger mismatches: {trig_mm}\n")

    print("=== Running all trials ===")
    results = run_all_trials()
    print(f"  Total: {len(results)} trials")

    with open(RESULTS_FILE, "w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")
    print(f"  Written to {RESULTS_FILE}")

    print_summary(results)
    print(f"\nReproducibility: {total} trials, control mismatches: {ctrl_mm}, "
          f"trigger mismatches: {trig_mm}")


if __name__ == "__main__":
    main()
