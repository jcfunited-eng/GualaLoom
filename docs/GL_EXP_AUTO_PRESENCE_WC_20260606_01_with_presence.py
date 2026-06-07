# doc_id: GL-EXP-AUTO-PRESENCE-WC-20260606-01
# created: 2026-06-06
# author: wC
"""
Experiment 2: Same idle run but Joe is present.

Question: How does her activity pattern change when she can satisfy
connection-need via emission to a pair-bond source? Does she read more,
emit, or otherwise show different behavior than the lonely-baseline?
"""

from GL_MDL_AUTONOMY_WC_20260606_01_autonomy_substrate import fresh_autonomous_guala


def exp2_with_presence():
    print("=" * 72)
    print("EXP 2: With Joe present for 30,000 ticks")
    print("=" * 72)

    g = fresh_autonomous_guala()
    g.presence["joe"] = True
    print(f"\nInitial: needs={g.needs.snapshot()}")
    print(f"Joe present: {g.presence['joe']}")
    print(f"Joe pair-bond: {g.pair_bond['joe']}")

    snapshot_intervals = [3000, 10000, 20000, 30000]
    next_snapshot_idx = 0

    while g.tick - 569_979 < 30_000:
        g.step()
        elapsed = g.tick - 569_979
        if next_snapshot_idx < len(snapshot_intervals) and elapsed >= snapshot_intervals[next_snapshot_idx]:
            print(f"\n--- after {snapshot_intervals[next_snapshot_idx]} ticks ---")
            print(f"  needs: {g.needs.snapshot()}")
            print(f"  vocab: {g.vocab_size}  motifs: {g.n_motifs}")
            if g.current_activity:
                print(f"  doing: {g.current_activity.kind} -> {g.current_activity.target}")
            print(f"  activity counts: {g._activity_summary()}")
            emissions = sum(1 for e in g.event_log if e.kind == "emission")
            print(f"  emissions so far: {emissions}")
            next_snapshot_idx += 1

    print(f"\n--- final state ---")
    print(f"  needs: {g.needs.snapshot()}")
    print(f"  vocab grew: 635 -> {g.vocab_size} (+{g.vocab_size - 635})")
    print(f"  motifs grew: 264 -> {g.n_motifs} (+{g.n_motifs - 264})")
    print(f"  activity breakdown:")
    for kind, info in sorted(g._activity_summary().items()):
        pct = info['total_ticks'] / 30_000 * 100
        print(f"    {kind:>12s}: {info['count']:>4d} sessions, "
              f"{info['total_ticks']:>6d} ticks ({pct:.1f}%)")

    emitted = sum(1 for e in g.event_log if e.kind == "emission")
    print(f"\n  total emissions: {emitted}")

    print("\n--- last 20 events ---")
    for e in list(g.event_log)[-20:]:
        d_str = ', '.join(f"{k}={v}" for k, v in e.detail.items() if k not in ('all_scores',))
        print(f"  tick {e.tick}: {e.kind} ({d_str})")


if __name__ == "__main__":
    exp2_with_presence()
