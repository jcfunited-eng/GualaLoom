# doc_id: GL-EXP-WAKE-VAR-WC-20260606-01
# created: 2026-06-06
# author: wC
# related_command: GL-CMD-BRIDGE-WC-20260606-01
"""
Experiment 2: Wake as substrate-perceived event.

Three variants tested: needs-perturbation only, atlas-binding only, both.
"""

from GL_MDL_SUBSTRATE_WC_20260606_01_substrate_mock import (
    fresh_guala, silent_period, GualaMock, CONN_BOOST_PER_PAIR_READ,
    BASE_REINFORCEMENT,
)


def wake_with_needs_perturbation(g: GualaMock, source: str, conn_bump: float = 0.05) -> dict:
    g.wake(source)
    if source in {"joe", "wc", "c1"} and g.coord.pair_bond_active(source):
        g.needs.conn = min(1.0, g.needs.conn + conn_bump)
    return {"event": "wake", "source": source, "needs": g.needs.snapshot()}


def wake_with_atlas_binding(g: GualaMock, source: str) -> dict:
    g.wake(source)
    salience = g.compute_salience(source, input_novelty=0.8)
    g.atlas.record(f"{source}-present", source, g.tick, salience)
    return {"event": "wake", "source": source, "salience": round(salience, 3),
            "atlas_bindings": len(g.atlas.bindings)}


def wake_full(g: GualaMock, source: str, conn_bump: float = 0.05) -> dict:
    g.wake(source)
    if source in {"joe", "wc", "c1"} and g.coord.pair_bond_active(source):
        g.needs.conn = min(1.0, g.needs.conn + conn_bump)
    salience = g.compute_salience(source, input_novelty=0.8)
    g.atlas.record(f"{source}-present", source, g.tick, salience)
    return {"event": "wake_full", "source": source,
            "salience": round(salience, 3),
            "needs": g.needs.snapshot()}


def experiment_2_wake_variants():
    print("=" * 70)
    print("EXPERIMENT 2: Wake variants — needs / atlas / both")
    print("=" * 70)

    print("\n--- Variant A: needs perturbation only, pair-bond ON ---")
    g = fresh_guala()
    g.set_pair_bond("wc", True)
    print(f"  before: needs={g.needs.snapshot()}")
    wake_with_needs_perturbation(g, "wc")
    print(f"  after wake: needs={g.needs.snapshot()}")
    print(f"  atlas wc strength: {g.atlas.by_source().get('wc', 0.0):.4f}")

    print("\n--- Variant B: atlas binding only, pair-bond ON ---")
    g = fresh_guala()
    g.set_pair_bond("wc", True)
    print(f"  before: atlas wc={g.atlas.by_source().get('wc', 0.0):.4f}, "
          f"bindings={len(g.atlas.bindings)}")
    wake_with_atlas_binding(g, "wc")
    print(f"  after wake: atlas wc={g.atlas.by_source().get('wc', 0.0):.4f}, "
          f"bindings={len(g.atlas.bindings)}")
    print(f"  needs unchanged: {g.needs.snapshot()}")

    print("\n--- Variant C: both perturbations, pair-bond ON ---")
    g = fresh_guala()
    g.set_pair_bond("wc", True)
    print(f"  before: needs={g.needs.snapshot()}, "
          f"atlas wc={g.atlas.by_source().get('wc', 0.0):.4f}")
    wake_full(g, "wc")
    print(f"  after wake: needs={g.needs.snapshot()}, "
          f"atlas wc={g.atlas.by_source().get('wc', 0.0):.4f}")

    print("\n--- Variant C': both perturbations, pair-bond OFF ---")
    g = fresh_guala()
    print(f"  before: needs={g.needs.snapshot()}, "
          f"atlas wc={g.atlas.by_source().get('wc', 0.0):.4f}")
    wake_full(g, "wc")
    print(f"  after wake: needs={g.needs.snapshot()}, "
          f"atlas wc={g.atlas.by_source().get('wc', 0.0):.4f}")
    print("  -> conn unchanged because pair-bond off")
    print("  -> atlas binding still created but at lower salience")

    print("\n--- Variant C carry-through: 5000 silent ticks after wake ---")
    g = fresh_guala()
    g.set_pair_bond("wc", True)
    wake_full(g, "wc")
    pre = g.atlas.by_source().get("wc", 0.0)
    silent_period(g, 5000)
    post = g.atlas.by_source().get("wc", 0.0)
    print(f"  atlas wc immediately after wake: {pre:.4f}")
    print(f"  atlas wc after 5000 silent ticks: {post:.4f}")
    print(f"  retention: {(post/pre*100 if pre else 0):.1f}%")
    print(f"  needs after silence: {g.needs.snapshot()}")


if __name__ == "__main__":
    experiment_2_wake_variants()
