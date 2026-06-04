# Experiment 1.5 — Cascade with Co-Commit Indexing

**Date:** 2026-06-04
**Runner:** c1 (Claude Opus 4.6)

## Method

Same differential probe as exp01 (control re-settle vs trigger re-settle,
learned seeds only) but with a modified settle that propagates commits
along two channels:

1. **Position channel** (existing): cross-strand same-position resonance
2. **Co-commit channel** (new): when position p commits, positions q that
   co-committed with p across stored motifs (above threshold) get their
   barrier math recomputed with co-commit pressure added

Co-commit pressure: for each committed co-commit neighbor r of position q,
add `state[r] * P3I[r % 8] // 2` to q's pressure (same attenuation as
cross-strand resonance). Propagates via BFS wavefront after the position
channel's settle pass.

The modified settle lives in `tools/` as a probe. The substrate proper
is unchanged.

## Threshold choice

Three thresholds swept: 500, 300, 100.

Co-commit pairs = positions p, q both non-null in the same stored motif,
summed across the 893-motif population. Threshold = minimum count to
qualify as neighbors.

| Threshold | Positions with neighbors | Mean neighbors |
|-----------|--------------------------|----------------|
| 500       | 16                       | 8.4            |
| 300       | 24                       | 17.8           |
| 100       | 40                       | 29.4           |

At 500, only intra-strand positions 3-4 (the high-frequency committers)
have co-commit neighbors. At 100, positions 2-7 all have neighbors.
Positions 0-1 never commit in any motif (0% commit rate across all
strands), so they have no co-commit neighbors at any threshold.

## Parameters

- **Settle:** gualaloom.py's settle() + co-commit wavefront
- **Population:** 64 trits (8 strands × 8 trits)
- **Seeds:** 100 learned motifs from krimelack (RNG 7777)
- **Triggers per seed:** 10 positions × 2 values = 20
- **Trials per threshold:** 2000
- **Total trials:** 6000
- **Step cap:** 50
- **Familiarity:** 0

## Reproducibility

50 trials × 2 runs at threshold=300: 0 control mismatches, 0 trigger
mismatches. Deterministic.

## Raw results

### threshold=500

```
cascade_depth: min=0 max=15 mean=3.46 median=0
depth=0: 1025 (51.2%), depth>0: 975 (48.8%)
depth distribution: {0: 1025, 1: 9, 6: 9, 7: 935, 14: 13, 15: 9}
via_position mean=3.38, via_cocommit mean=0.21, via_both mean=0.19
attribution identity holds: 1978/2000

by intra-strand index:
  idx=0:  396 trials, depth>0=  0 (0%)
  idx=1:  372 trials, depth>0=  0 (0%)
  idx=2:  200 trials, depth>0=  0 (0%)
  idx=3:   74 trials, depth>0= 18 (24%), mean_depth=1.28
  idx=4:   48 trials, depth>0= 47 (98%), mean_depth=9.58, via_cc=7.35
  idx=5:  378 trials, depth>0=378 (100%), mean_depth=7.00, via_cc=0.00
  idx=6:  258 trials, depth>0=258 (100%), mean_depth=7.00, via_cc=0.00
  idx=7:  274 trials, depth>0=274 (100%), mean_depth=7.00, via_cc=0.00
```

### threshold=300

```
cascade_depth: min=0 max=23 mean=3.38 median=0
depth=0: 1055 (52.8%), depth>0: 945 (47.2%)
depth distribution: {0: 1055, 1: 1, 6: 1, 7: 928, 8: 2, 15: 7, 22: 3, 23: 3}
via_position mean=3.30, via_cocommit mean=0.19, via_both mean=0.11
attribution identity holds: 1993/2000

by intra-strand index:
  idx=0:  396 trials, depth>0=  0 (0%)
  idx=1:  372 trials, depth>0=  0 (0%)
  idx=2:  200 trials, depth>0=  0 (0%)
  idx=3:   74 trials, depth>0=  8 (11%), mean_depth=0.69
  idx=4:   48 trials, depth>0= 27 (56%), mean_depth=7.04, via_cc=6.69
  idx=5:  378 trials, depth>0=378 (100%), mean_depth=7.00, via_cc=0.00
  idx=6:  258 trials, depth>0=258 (100%), mean_depth=7.00, via_cc=0.00
  idx=7:  274 trials, depth>0=274 (100%), mean_depth=7.00, via_cc=0.00
```

### threshold=100

```
cascade_depth: min=0 max=39 mean=5.09 median=0
depth=0: 1202 (60.1%), depth>0: 798 (39.9%)
depth distribution: {0: 1202, 1: 1, 7: 382, 15: 308, 22: 8, 23: 50, 30: 7, 31: 36, 38: 3, 39: 3}
via_position mean=2.79, via_cocommit mean=3.50, via_both mean=1.47
attribution identity holds: 1934/2000

by intra-strand index:
  idx=0:  396 trials, depth>0=  0 (0%)
  idx=1:  372 trials, depth>0=  0 (0%)
  idx=2:  200 trials, depth>0=  0 (0%)
  idx=3:   74 trials, depth>0=  6 (8%), mean_depth=0.69
  idx=4:   48 trials, depth>0= 27 (56%), mean_depth=16.04, via_cc=13.21
  idx=5:  378 trials, depth>0=378 (100%), mean_depth=7.00, via_cc=0.00
  idx=6:  258 trials, depth>0=188 (73%), mean_depth=12.91, via_cc=11.62
  idx=7:  274 trials, depth>0=199 (73%), mean_depth=12.33, via_cc=12.13
```

## Things noticed (for joint read, not interpreted)

1. **Co-commit channel is threshold-sensitive but real.** At 500/300, it
   barely fires (mean via_cc < 1). At 100, it becomes the dominant channel
   (mean via_cc=3.50 vs via_pos=2.79). This is not a gradual transition —
   it's a qualitative break between 300 and 100.

2. **Intra-strand positions 0, 1, 2 remain completely dead across all
   thresholds.** The co-commit channel does NOT extend cascade reach into
   positions where the position channel was silent. Those positions never
   commit in any motif (0% commit rate for idx 0-1; idx 2 commits at 44%
   but its co-commit pressure never crosses the barrier). The second
   indexing is not opening new territory.

3. **Intra-strand position 4 is where co-commit fires strongest.** At
   threshold=100, idx=4 trials reach mean depth 16.04 (vs 7.00 via
   position alone), with via_cc=13.21. But idx=4 is the 81% committer —
   the position channel already cascades there 98% of the time at
   threshold=500. The co-commit channel is deepening existing cascades,
   not reaching new positions.

4. **Indices 6 and 7 show something different at threshold=100.** At
   500/300, they cascade 100% of the time with depth=7, all via position.
   At 100, they cascade 73% of the time but with depth ~12.5. The firing
   RATE dropped but the depth increased. The co-commit channel is changing
   the settle dynamics, not just adding on top of them.

5. **Attribution identity breaks for some trials.** 1978/2000 at t=500,
   1934/2000 at t=100. The gap = positions that flipped but are NOT direct
   position or co-commit neighbors of the trigger. These are multi-hop
   cascade: trigger → neighbor → neighbor's neighbor. The co-commit
   wavefront propagates beyond the trigger's immediate neighborhood.

6. **Depth distribution remains bimodal but with new modes.** At t=100,
   the distribution is {0: 1202, 7: 382, 15: 308, 23: 50, 31: 36, 39: 3}.
   The modes are roughly at multiples of 7-8, suggesting the cascade fires
   in discrete bursts of cross-strand siblings. The co-commit channel
   appears to trigger additional bursts, not smooth propagation.

7. **Position 58 (intra-strand 2) at threshold=100 went from depth=0
   with 3 settle steps to depth=0 with 2 settle steps.** The co-commit
   channel changed the settle dynamics (fewer iterations) even though the
   end-state was identical. The channel is active but its pressure wasn't
   enough to flip any positions.
