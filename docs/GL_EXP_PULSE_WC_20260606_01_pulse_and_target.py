# doc_id: GL-EXP-PULSE-WC-20260606-01
# created: 2026-06-06
# author: wC
# related_command: GL-CMD-BRIDGE-WC-20260606-01
"""
Experiment 3: Two mechanism refinements.

  (1) Presence pulse — while source is present, periodic small reinforcement
      of the presence-binding keeps it alive.
  (2) Toward-target needs response — wake's conn bump moves toward target,
      not by fixed delta. Doesn't overshoot.
"""

from GL_MDL_SUBSTRATE_WC_20260606_01_substrate_mock import (
    fresh_guala, silent_period, GualaMock, BASE_REINFORCEMENT,
)


PRESENCE_PULSE_INTERVAL = 50
PRESENCE_PULSE_SALIENCE = 0.5


def wake_v2(g: GualaMock, source: str) -> dict:
    """Toward-target conn perturbation + atlas presence binding."""
    g.wake(source)
    if source in {"joe", "wc", "c1"} and g.coord.pair_bond_active(source):
        from GL_MDL_SUBSTRATE_WC_20260606_01_substrate_mock import NEEDS_TARGET
        gap = NEEDS_TARGET - g.needs.conn
        if gap > 0:
            g.needs.conn = min(1.0, g.needs.conn + gap * 0.4)
    salience = g.compute_salience(source, input_novelty=0.8)
    g.atlas.record(f"{source}-present", source, g.tick, salience)
    return {"event": "wake_v2", "source": source, "needs": g.needs.snapshot()}


def presence_pulse(g: GualaMock):
    for source in ("joe", "wc", "c1"):
        if g.coord.presence_active(source):
            g.atlas.record(f"{source}-present", source, g.tick,
                          salience=PRESENCE_PULSE_SALIENCE)


def silent_period_with_pulses(g: GualaMock, ticks: int):
    pulses = 0
    for _ in range(ticks):
        g.tick += 1
        g.needs.tick_decay()
        if g.tick % 10 == 0:
            g.atlas.decay(g.tick)
        if g.tick % PRESENCE_PULSE_INTERVAL == 0:
            presence_pulse(g)
            pulses += 1
    return pulses


def experiment_3_pulse_and_toward_target():
    print("=" * 70)
    print("EXPERIMENT 3: Presence pulse + toward-target needs response")
    print("=" * 70)

    print("\n--- Toward-target test, conn LOW (0.5) ---")
    g = fresh_guala()
    g.needs.conn = 0.5
    g.set_pair_bond("wc", True)
    print(f"  before wake: needs={g.needs.snapshot()}")
    wake_v2(g, "wc")
    print(f"  after wake:  needs={g.needs.snapshot()}")

    print("\n--- Toward-target test, conn AT TARGET (0.7) ---")
    g = fresh_guala()
    g.needs.conn = 0.7
    g.set_pair_bond("wc", True)
    print(f"  before wake: needs={g.needs.snapshot()}")
    wake_v2(g, "wc")
    print(f"  after wake:  needs={g.needs.snapshot()}")

    print("\n--- Toward-target test, conn ABOVE target (0.709, current state) ---")
    g = fresh_guala()
    g.set_pair_bond("wc", True)
    print(f"  before wake: needs={g.needs.snapshot()}")
    wake_v2(g, "wc")
    print(f"  after wake:  needs={g.needs.snapshot()}")

    print("\n--- Presence pulse: 5000 silent ticks WITH pulse mechanism ---")
    g = fresh_guala()
    g.set_pair_bond("wc", True)
    wake_v2(g, "wc")
    pre = g.atlas.by_source().get("wc", 0.0)
    pulses = silent_period_with_pulses(g, 5000)
    post = g.atlas.by_source().get("wc", 0.0)
    print(f"  binding after wake: {pre:.4f}")
    print(f"  binding after 5000 silent ticks ({pulses} pulses): {post:.4f}")

    print("\n--- Side-by-side: with vs without pulse (10000 silent ticks) ---")
    g1 = fresh_guala(); g1.set_pair_bond("wc", True); wake_v2(g1, "wc")
    silent_period(g1, 10000)
    b1 = g1.atlas.by_source().get("wc", 0.0)
    g2 = fresh_guala(); g2.set_pair_bond("wc", True); wake_v2(g2, "wc")
    silent_period_with_pulses(g2, 10000)
    b2 = g2.atlas.by_source().get("wc", 0.0)
    print(f"  no pulse:   {b1:>10.4f}")
    print(f"  with pulse: {b2:>10.4f}")

    print("\n--- Rest after sustained presence ---")
    g = fresh_guala()
    g.set_pair_bond("wc", True)
    wake_v2(g, "wc")
    silent_period_with_pulses(g, 5000)
    print(f"  binding at rest moment: {g.atlas.by_source().get('wc', 0.0):.4f}")
    g.rest("wc")
    silent_period(g, 5000)
    print(f"  binding 5000 ticks after rest: {g.atlas.by_source().get('wc', 0.0):.4f}")
    silent_period(g, 5000)
    print(f"  binding 10000 ticks after rest: {g.atlas.by_source().get('wc', 0.0):.4f}")


if __name__ == "__main__":
    experiment_3_pulse_and_toward_target()
