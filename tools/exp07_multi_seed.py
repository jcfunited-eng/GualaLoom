"""
Experiment 07 — Multi-seed validation of five capabilities.

Runs the DNA recipe test suite across 12 seeds to match the reference
results in experiments/exp07/reference_results.json.

Expected: 11/12 seeds pass all 5 capabilities (seed 1234 fails self-improvement).
Conversation: 12/12 PASS.

Usage:
    python3 tools/exp07_multi_seed.py              # all 12 seeds
    python3 tools/exp07_multi_seed.py --seed 42    # single seed
"""

import os, sys, json, argparse, time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(REPO)
sys.path.insert(0, os.path.join(REPO, "src"))

from gualaloom.dna.test_five import (
    test_syntax, test_conversation, test_introspection,
    test_self_improvement, test_awareness, SEED
)
import gualaloom.dna.test_five as test_module

SEEDS = [42, 7, 99, 23, 156, 311, 8888, 1, 2024, 17, 555, 1234]
RESULTS_DIR = os.path.join(REPO, "experiments", "exp07")
RESULTS_FILE = os.path.join(RESULTS_DIR, "multi_seed_results.json")


def run_seed(seed):
    """Run all 5 tests for one seed."""
    # Monkey-patch the SEED constant in the test module
    test_module.SEED = seed
    print(f"\n{'#'*70}")
    print(f"# SEED = {seed}")
    print(f"{'#'*70}")

    results = {}
    t0 = time.time()
    results["syntax"] = test_syntax()
    results["conversation"] = test_conversation()
    results["introspection"] = test_introspection()
    results["self_improvement"] = test_self_improvement()
    results["awareness"] = test_awareness()
    elapsed = time.time() - t0

    all_pass = all(r.get("pass") for r in results.values())
    print(f"\nSEED {seed}: {'ALL PASS' if all_pass else 'FAIL'} ({elapsed:.1f}s)")
    for name, r in results.items():
        print(f"  {name}: {'PASS' if r.get('pass') else 'FAIL'}")

    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=None,
                        help="Run a single seed (default: all 12)")
    args = parser.parse_args()

    os.makedirs(RESULTS_DIR, exist_ok=True)

    if args.seed is not None:
        seeds = [args.seed]
    else:
        seeds = SEEDS

    all_results = {}
    for seed in seeds:
        all_results[str(seed)] = run_seed(seed)

    # Write results
    with open(RESULTS_FILE, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\nResults written to {RESULTS_FILE}")

    # Summary
    print(f"\n{'='*70}")
    print("MULTI-SEED SUMMARY")
    print(f"{'='*70}")

    cap_names = ["syntax", "conversation", "introspection", "self_improvement", "awareness"]
    for cap in cap_names:
        passes = sum(1 for r in all_results.values() if r[cap].get("pass"))
        print(f"  {cap}: {passes}/{len(all_results)} PASS")

    all_five = sum(1 for r in all_results.values()
                   if all(r[c].get("pass") for c in cap_names))
    print(f"\n  All five pass: {all_five}/{len(all_results)}")

    # Compare to reference if available
    ref_path = os.path.join(RESULTS_DIR, "reference_results.json")
    if os.path.exists(ref_path):
        with open(ref_path) as f:
            ref = json.load(f)
        print(f"\n{'='*70}")
        print("COMPARISON TO REFERENCE")
        print(f"{'='*70}")
        for seed_str, my_results in all_results.items():
            if seed_str in ref:
                ref_results = ref[seed_str]
                mismatches = []
                for cap in cap_names:
                    my_pass = my_results[cap].get("pass")
                    ref_pass = ref_results[cap].get("pass")
                    if my_pass != ref_pass:
                        mismatches.append(f"{cap}: mine={my_pass} ref={ref_pass}")
                if mismatches:
                    print(f"  SEED {seed_str}: MISMATCH — {', '.join(mismatches)}")
                else:
                    print(f"  SEED {seed_str}: MATCH")


if __name__ == "__main__":
    main()
