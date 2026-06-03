"""
Topology experiment — Steps 1, 2, 3.

Run from repo root:
    PYTHONPATH=src python experiments/topology_experiment.py
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from collections import Counter, defaultdict
from pathlib import Path

from gualaloom.krimelack import Krimelack
from gualaloom.loom import Loom
from gualaloom.topology import compute_topology
from gualaloom.generate import generate_response


def step1(k: Krimelack) -> dict:
    """Compute (chi, b1) distribution across all motifs."""
    print("=" * 72)
    print("STEP 1 — Topological invariants for all motifs")
    print("=" * 72)

    topo_map = {}  # fp -> topology dict
    chi_b1_counter = Counter()
    chi2_counter = Counter()

    for fp, m in k.motifs.items():
        t = compute_topology(m.state)
        topo_map[fp] = t
        chi_b1_counter[(t["chi"], t["b1"])] += 1
        chi2_counter[t["chi2"]] += 1

    print(f"\nGeometric motifs: {k.size()}")
    print(f"Distinct (chi, b1) classes: {len(chi_b1_counter)}")
    print(f"Collapse ratio: {k.size()} geometric -> "
          f"{len(chi_b1_counter)} topological "
          f"({k.size() / max(len(chi_b1_counter), 1):.1f}x)")

    print(f"\n(chi, b1) distribution:")
    for (chi, b1), count in sorted(chi_b1_counter.items(),
                                     key=lambda x: -x[1]):
        print(f"  chi={chi:+3d}, b1={b1:2d}: {count:3d} motifs")

    print(f"\nchi_2complex (V-E+F) distribution:")
    for chi2, count in sorted(chi2_counter.items(), key=lambda x: -x[1]):
        print(f"  chi2={chi2:+3d}: {count:3d} motifs")

    # Weight-stratified: heavy vs light motifs
    heavy = [(fp, m) for fp, m in k.motifs.items() if m.weight >= 100]
    light = [(fp, m) for fp, m in k.motifs.items() if m.weight < 10]
    print(f"\nWeight stratification:")
    print(f"  Heavy (w>=100): {len(heavy)} motifs")
    if heavy:
        heavy_classes = Counter()
        for fp, m in heavy:
            t = topo_map[fp]
            heavy_classes[(t["chi"], t["b1"])] += 1
        for (chi, b1), count in sorted(heavy_classes.items(),
                                         key=lambda x: -x[1]):
            print(f"    chi={chi:+3d}, b1={b1:2d}: {count} motifs")

    print(f"  Light (w<10): {len(light)} motifs")
    if light:
        light_classes = Counter()
        for fp, m in light:
            t = topo_map[fp]
            light_classes[(t["chi"], t["b1"])] += 1
        for (chi, b1), count in sorted(light_classes.items(),
                                         key=lambda x: -x[1])[:10]:
            print(f"    chi={chi:+3d}, b1={b1:2d}: {count} motifs")
        if len(light_classes) > 10:
            print(f"    ... and {len(light_classes) - 10} more classes")

    return topo_map


def step2(k: Krimelack, loom: Loom, topo_map: dict):
    """Compare geometry-only vs topology-first recall."""
    print("\n" + "=" * 72)
    print("STEP 2 — Topology-first vs geometry-only recall")
    print("=" * 72)

    test_phrases = [
        "the cat ",
        "the substrate ",
        "the ",
        "settled ",
        "motif ",
        "commit ",
        "hello ",
        "coupling ",
    ]

    for phrase in test_phrases:
        # Feed phrase and get settled state
        loom_copy_recent = list(loom.recent)
        loom_copy_fam = loom.familiarity

        for ch in phrase:
            loom.tick(ch)

        current = loom.last_settled
        if current is None:
            continue

        query_topo = compute_topology(current)
        query_key = (query_topo["chi"], query_topo["b1"])

        # --- Geometry-only recall (baseline) ---
        geo_fp, geo_score, geo_weight = k.recall(current)

        # --- Topology-first recall ---
        # Step A: filter to topologically compatible motifs
        compatible = []
        for fp, m in k.motifs.items():
            t = topo_map.get(fp)
            if t and (t["chi"], t["b1"]) == query_key:
                compatible.append((fp, m))

        # If no exact match, find closest chi
        if not compatible:
            best_dist = float("inf")
            for fp, m in k.motifs.items():
                t = topo_map.get(fp)
                if t:
                    dist = abs(t["chi"] - query_key[0]) + abs(t["b1"] - query_key[1])
                    if dist < best_dist:
                        best_dist = dist
                        compatible = [(fp, m)]
                    elif dist == best_dist:
                        compatible.append((fp, m))

        # Step B: rank by geometric resonance within compatible set
        topo_fp, topo_score, topo_weight = None, -1, 0
        for fp, m in compatible:
            score = sum(1 for a, b in zip(current, m.state)
                        if a == b and a != 0)
            if score > topo_score:
                topo_fp, topo_score, topo_weight = fp, score, m.weight

        # Report
        same = "SAME" if geo_fp == topo_fp else "DIFF"
        geo_origin = k.get_motif(geo_fp).origin if geo_fp and k.get_motif(geo_fp) else "?"
        topo_origin = k.get_motif(topo_fp).origin if topo_fp and k.get_motif(topo_fp) else "?"

        print(f"\n  '{phrase.strip()}'  query_topo=({query_key[0]:+d}, {query_key[1]})")
        print(f"    geo:  [{(geo_fp or '?')[:8]}] score={geo_score:2d} w={geo_weight:5d} origin={geo_origin}")
        print(f"    topo: [{(topo_fp or '?')[:8]}] score={topo_score:2d} w={topo_weight:5d} origin={topo_origin}  [{same}]")
        print(f"    compatible pool: {len(compatible)} motifs")

        # Restore loom state for next phrase
        loom.recent = loom_copy_recent
        loom.familiarity = loom_copy_fam


def step3(k: Krimelack, topo_map: dict):
    """chi2 = V - E + F histogram, weighted by motif weight."""
    print("\n" + "=" * 72)
    print("STEP 3 — V - E + F: do heavy motifs cluster?")
    print("=" * 72)

    # Weight-weighted chi2 histogram
    chi2_weight = defaultdict(int)
    chi2_count = defaultdict(int)
    for fp, m in k.motifs.items():
        t = topo_map.get(fp)
        if t:
            chi2_weight[t["chi2"]] += m.weight
            chi2_count[t["chi2"]] += 1

    print(f"\nchi2 = V - E + F, weighted by motif weight:")
    total_weight = sum(chi2_weight.values())
    for chi2, w in sorted(chi2_weight.items(), key=lambda x: -x[1]):
        pct = 100 * w / total_weight if total_weight else 0
        n = chi2_count[chi2]
        print(f"  chi2={chi2:+3d}: weight={w:6d} ({pct:5.1f}%)  "
              f"motifs={n}")

    # Specifically: what chi2 do the top-10 heaviest motifs have?
    print(f"\nTop 10 heaviest motifs:")
    by_weight = sorted(k.motifs.items(), key=lambda x: -x[1].weight)[:10]
    for fp, m in by_weight:
        t = topo_map.get(fp, {})
        print(f"  [{fp[:8]}] w={m.weight:5d}  "
              f"V={t.get('V',0):2d} E={t.get('E',0):2d} "
              f"F={t.get('F',0):2d} "
              f"chi2={t.get('chi2',0):+3d}  "
              f"(chi={t.get('chi',0):+3d}, b1={t.get('b1',0):2d}, "
              f"C={t.get('C',0):2d})")

    # Do heavy motifs cluster at a value?
    if by_weight:
        heavy_chi2 = [topo_map[fp]["chi2"] for fp, m in by_weight
                      if fp in topo_map]
        if heavy_chi2:
            from collections import Counter as C2
            mode = C2(heavy_chi2).most_common(1)[0]
            print(f"\n  Heavy-motif chi2 mode: {mode[0]:+d} "
                  f"({mode[1]}/{len(heavy_chi2)} of top 10)")


def generation_comparison(k_baseline: Krimelack, loom_baseline: Loom,
                          k_topo: Krimelack, loom_topo: Loom,
                          topo_map: dict):
    """Compare generation output: baseline vs topology-first."""
    print("\n" + "=" * 72)
    print("GENERATION COMPARISON — baseline vs topology-first")
    print("=" * 72)

    prompts = ["hello", "the substrate", "what is this"]

    for prompt in prompts:
        # Baseline
        for ch in prompt + " ":
            loom_baseline.tick(ch)
        resp_base = generate_response(loom_baseline, k_baseline, max_chars=60)

        # Topology (same krimelack, generation uses whatever recall finds)
        for ch in prompt + " ":
            loom_topo.tick(ch)
        resp_topo = generate_response(loom_topo, k_topo, max_chars=60)

        print(f"\n  > {prompt}")
        print(f"    baseline: {resp_base}")
        print(f"    topo:     {resp_topo}")


def main():
    print("GualaLoom Topology Experiment")
    print("Hypothesis: topological invariants improve motif recognition")
    print()

    # --- Feed corpus (context=8 for richer structure) ---
    k = Krimelack()
    loom = Loom(k, context_chars=8)

    for path in sorted(Path("corpus").glob("*.md")):
        text = path.read_text()
        print(f"Feeding {path.name} ({len(text)} chars)...", end=" ",
              flush=True)
        loom.feed(text)
        print(f"done. motifs={k.size()}")

    print(f"\nTotal: {k.size()} motifs from corpus\n")

    # --- Step 1 ---
    topo_map = step1(k)

    # --- Step 2 ---
    step2(k, loom, topo_map)

    # --- Step 3 ---
    step3(k, topo_map)

    # --- Generation comparison ---
    # Create a second identical loom for baseline comparison
    k2 = Krimelack()
    loom2 = Loom(k2, context_chars=8)
    for path in sorted(Path("corpus").glob("*.md")):
        loom2.feed(path.read_text())

    generation_comparison(k2, loom2, k, loom, topo_map)


if __name__ == "__main__":
    main()
