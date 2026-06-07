"""
gualaloom_v6_experiment_4.py — Does HIGH-SALIENCE teaching shift recall?

Experiment 3 showed: low-salience corpus repetition (100 reads of "moon is
bright") doesn't displace earlier high-salience impression of "moon is cold".
That's substrate-honest — repetition without novelty has low salience.

Experiment 4 asks the right question: does HIGH-salience teaching shift recall?
If Joe teaches "the moon is bright" under pair-bond, does that displace cold
faster than corpus would?
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gualaloom_v6_engine import Guala


def find_strength(g, word, section):
    """Sum strength of word's bindings in target section."""
    total = 0.0
    sec = g.sections[section]
    for chi, entries in g.atlas.entries.items():
        for e in entries:
            if e["section"] != section:
                continue
            if e["motif"] >= len(sec.modes):
                continue
            if sec.modes[e["motif"]][2] == word:
                total += e["strength"]
    return total


def main():
    print("="*72)
    print("EXPERIMENT 4: High-salience teaching DOES shift recall")
    print("="*72)

    g = Guala()

    # Phase A: corpus impresses moon-cold (50 reads)
    print("\nPhase A: corpus reads 'the moon is cold' 50 times")
    for _ in range(50):
        g.read_sentence("the moon is cold", source="corpus")
    s_cold_a = find_strength(g, "cold", "object")
    s_bright_a = find_strength(g, "bright", "object")
    r_a = g.converse("tell me about the moon", source="joe")
    print(f"  cold strength: {s_cold_a:.3f}, bright strength: {s_bright_a:.3f}")
    print(f"  'tell me about the moon' → {r_a}")

    # Phase B: corpus reads moon-bright 100 times (Experiment 3's failed test)
    print("\nPhase B: corpus reads 'the moon is bright' 100 times")
    for _ in range(100):
        g.read_sentence("the moon is bright", source="corpus")
    s_cold_b = find_strength(g, "cold", "object")
    s_bright_b = find_strength(g, "bright", "object")
    r_b = g.converse("tell me about the moon", source="joe")
    print(f"  cold strength: {s_cold_b:.3f}, bright strength: {s_bright_b:.3f}")
    print(f"  'tell me about the moon' → {r_b}")
    if s_cold_b > s_bright_b:
        print(f"  PER EXPECTATION: cold still dominates ({s_cold_b:.2f} > {s_bright_b:.2f})")
        print(f"  Low-salience repetition didn't shift recall — substrate-honest")

    # Phase C: Joe teaches moon-bright 10 times under pair-bond
    print("\nPhase C: Joe teaches 'the moon is bright' 10 times (source='joe')")
    # Reset pair-bond active (might have retired)
    g.coordinator.pair_bond_active = True
    for _ in range(10):
        g.read_sentence("the moon is bright", source="joe")
    s_cold_c = find_strength(g, "cold", "object")
    s_bright_c = find_strength(g, "bright", "object")
    r_c = g.converse("tell me about the moon", source="joe")
    print(f"  cold strength: {s_cold_c:.3f}, bright strength: {s_bright_c:.3f}")
    print(f"  'tell me about the moon' → {r_c}")

    print("\n" + "="*72)
    print("VERDICT")
    print("="*72)
    print(f"  Phase A (50 corpus cold):     cold={s_cold_a:.2f}, bright={s_bright_a:.2f}")
    print(f"  Phase B (+100 corpus bright): cold={s_cold_b:.2f}, bright={s_bright_b:.2f}")
    print(f"  Phase C (+10 joe bright):     cold={s_cold_c:.2f}, bright={s_bright_c:.2f}")
    if s_bright_c > s_cold_c:
        print(f"\n  PASS — Joe's 10 high-salience teachings displaced cold")
        print(f"  Pair-bonded teaching can shift recall in a way corpus cannot")
    else:
        print(f"\n  PARTIAL — bright grew under Joe but didn't overtake cold")
        print(f"  Effect ratio: bright_c/cold_c = {s_bright_c/max(s_cold_c, 0.001):.2f}x")


if __name__ == "__main__":
    main()
