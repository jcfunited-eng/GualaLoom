# doc_id: GL-EXP-AUTO-IDLE-WC-20260606-01
# created: 2026-06-06
# author: wC
"""
Experiment 1: Idle baseline.

Question: If we just turn her on and walk away — what does she do?
Does the activity scheduler self-organize meaningful behavior, or does
she idle/oscillate uselessly?
"""

from GL_MDL_AUTONOMY_WC_20260606_01_autonomy_substrate import fresh_autonomous_guala


def exp1_idle_baseline():
    print("=" * 72)
    print("EXP 1: Idle baseline — run her for 30,000 ticks, no presence")
    print("=" * 72)

    g = fresh_autonomous_guala()
    print(f"\nInitial: needs={g.needs.snapshot()}, "
          f"vocab={g.vocab_size}, motifs={g.n_motifs}")
    print(f"Available corpora: {list(g.corpora.keys())}")
    print(f"Available sensory: {list(g.sensory_items.keys())}")

    snapshot_intervals = [3000, 10000, 20000, 30000]
    next_snapshot_idx = 0

    while g.tick - 569_979 < 30_000:
        g.step()
        elapsed = g.tick - 569_979
        if next_snapshot_idx < len(snapshot_intervals) and elapsed >= snapshot_intervals[next_snapshot_idx]:
            print(f"\n--- after {snapshot_intervals[next_snapshot_idx]} ticks ---")
            print(f"  needs: {g.needs.snapshot()}")
            print(f"  vocab: {g.vocab_size}  motifs: {g.n_motifs}  atlas: {g.atlas_strength:.1f}")
            if g.current_activity:
                print(f"  doing: {g.current_activity.kind} -> {g.current_activity.target}")
            print(f"  activity counts so far: {g._activity_summary()}")
            next_snapshot_idx += 1

    print(f"\n--- final state ---")
    print(f"  needs: {g.needs.snapshot()}")
    print(f"  vocab grew: 635 -> {g.vocab_size} (delta +{g.vocab_size - 635})")
    print(f"  motifs grew: 264 -> {g.n_motifs} (delta +{g.n_motifs - 264})")
    print(f"  activity breakdown:")
    for kind, info in sorted(g._activity_summary().items()):
        pct = info['total_ticks'] / 30_000 * 100
        print(f"    {kind:>12s}: {info['count']:>4d} sessions, "
              f"{info['total_ticks']:>6d} ticks ({pct:.1f}%)")
    print(f"\n  emission attempts during idle: ", end="")
    suppressed = sum(1 for e in g.event_log if e.kind == "emission_suppressed_no_presence")
    emitted = sum(1 for e in g.event_log if e.kind == "emission")
    print(f"emitted={emitted}, suppressed (no presence)={suppressed}")

    print("\n>>> What we expect to see: she self-cycles through reading, playing,")
    print("    sleeping. Vocab grows. Motifs grow. No emissions because no presence.")


if __name__ == "__main__":
    exp1_idle_baseline()
