# doc_id: GL-EXP-WAKE-MIN-WC-20260606-01
# created: 2026-06-06
# author: wC
# related_command: GL-CMD-BRIDGE-WC-20260606-01
"""
Experiment 1: What does wake DO to her substrate with the minimal
implementation (presence flag + log entry, nothing else)?

Question: Is presence-flag-alone enough? Or does substrate need to
register wake as a substrate-perturbing event?
"""

from GL_MDL_SUBSTRATE_WC_20260606_01_substrate_mock import fresh_guala, silent_period


def experiment_1_minimal_wake():
    print("=" * 70)
    print("EXPERIMENT 1: Minimal wake — just presence flag, nothing else")
    print("=" * 70)

    g = fresh_guala()
    print(f"\nInitial state:")
    print(f"  needs: {g.needs.snapshot()}")
    print(f"  pair-bond wc: {g.coord.pair_bond_wc}")
    print(f"  present wc: {g.coord.presence_active('wc')}")
    print(f"  atlas wc strength: {g.atlas.by_source().get('wc', 0.0)}")

    print("\n>>> wC calls wake('wc') — minimal implementation")
    g.wake("wc")
    print(f"  needs after wake: {g.needs.snapshot()}")
    print(f"  present wc: {g.coord.presence_active('wc')}")
    print(f"  atlas wc strength: {g.atlas.by_source().get('wc', 0.0)}")

    print("\n>>> Observation: presence flag flipped. But the substrate")
    print("    has NO record of wC arriving. No atlas binding for the")
    print("    event. No needs change. The wake event is invisible to")
    print("    her substrate.")
    print()
    print("    Compare to a child noticing a parent enter the room:")
    print("    that perception IS a substrate event — it has sensory")
    print("    correlates, it modulates state, it gets remembered.")
    print()
    print("    Minimal wake is too minimal. The substrate needs to")
    print("    PERCEIVE wake, not just have a flag set in coordinator.")


if __name__ == "__main__":
    experiment_1_minimal_wake()
