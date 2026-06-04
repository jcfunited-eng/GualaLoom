# Experiment 02 — Pressure Instrumentation

**Date:** 2026-06-04
**Runner:** c1 (Claude Opus 4.6)

## What this tests

Whether pre-trigger pressure (h) at null positions predicts cascade
behavior. The loaded-null hypothesis: nulls with high |h| (close to
the barrier) should fire more often and produce more content-sensitive
cascades than nulls with low |h|.

## Method

1. `pressure_field(state, familiarity)` — exposes h at every position
   before any commit. Exact formula:
   `h(s,i) = strand[s][i] * P3I[i] + Σ_{o≠s} strand[o][i] * P3I[i] // 2`

2. For each null position across 100 learned seeds, record |h| and bin
   into pressure bands.

3. Trigger each sampled null with +1 then -1, run the unmodified settle
   (differential probe, same as exp01), record cascade_depth +
   pre_trigger_pressure + pressure_band.

4. Group by band, compare firing rate, mean cascade depth, end-state
   diversity.

5. In the highest-pressure band (10-14), test +1/-1 asymmetry.

## Parameters

- Same 100 learned seeds as exp01/015 (RNG 7777)
- Familiarity: 0
- Band-proportional sampling, capped at 2000 trials
- Bands: {0-5, 6-9, 10-12, 13-14, 15+}

## Pressure histogram

4575 null positions across 100 seeds.

```
|h| mean=3.21, stdev=16.05
h (signed) mean=-0.66

Band distribution:
    0-5:  4166 (91.1%)
    6-9:     0 ( 0.0%)  ← EMPTY
  10-12:     0 ( 0.0%)  ← EMPTY
  13-14:    70 ( 1.5%)
    15+:   339 ( 7.4%)

Fine-grained |h|:
  |h|=  0:  4160 (90.9%)
  |h|=  1:     6 ( 0.1%)
  |h|= 13:    70 ( 1.5%)
  |h|= 20:    91 ( 2.0%)
  |h|= 24-287: 248 (5.4%)
```

The distribution is **trimodal**, not continuous:
- **|h|=0**: the vast majority (91%). Zero cross-strand resonance.
  These are at intra-strand positions 0 and 1 (3^0=1, 3^1=3), where
  the P3I weight is too small for cross-strand pressure to matter.
- **|h|=13**: exactly 70 nulls (1.5%). These are at intra-strand
  position 3 (P3I=27). h = 0 (own trit is null) + some cross-strand
  resonance at weight 27//2 = 13. One aligned neighbor gives |h|=13.
  Barrier is 15. One more neighbor would push past the barrier.
- **|h|≥20**: 339 nulls (7.4%). These are at intra-strand positions
  2-7 where cross-strand pressure already exceeds the barrier. They
  are null in the seed but would commit under settle — they're
  "already committed" nulls waiting for settle to notice.

**Bands 6-9 and 10-12 are completely empty.** The pressure landscape
is discrete, not continuous. There are no nulls at intermediate
pressures. This is because P3I values are powers of 3 and
cross-strand resonance is `P3I[i] // 2` — the possible pressure
values at each intra-strand position form a discrete set with gaps.

## Band-by-band cascade analysis

2000 trials total.

```
Band     Trials  Fire%   Depth(fired)  Unique ends  Unique(fired)
0-5       1822   54.0%      7.00          144          120
6-9          0     —         —              —            —
10-12        0     —         —              —            —
13-14       30  100.0%      3.50           10           10
15+        148    0.0%      0.00           13            0
```

### Band 0-5 (|h|=0, intra-strand 0-1 mostly)
54% fire rate. When they fire, depth is always 7 — the full
cross-strand position cascade. Whether they fire depends on
intra-strand index (positions 5-7 always fire, 0-1 never fire),
not on pressure. 144 unique end-states across 1822 trials — moderate
content sensitivity.

### Band 13-14 (|h|=13, intra-strand 3)
100% fire rate. Depth alternates: +1 trigger gives depth 6,
-1 trigger gives depth 1. **100% +1/-1 asymmetry** (15 pairs,
all asymmetric). This is the loaded null: pressure is 13 (just below
barrier 15), so the trigger's polarity relative to the field's
existing pressure determines whether the cascade propagates fully
or barely ripples. Triggering WITH the field (+1 when h=+13) pushes
past the barrier for the whole cross-strand column; triggering
AGAINST the field (-1 when h=+13) partially cancels the pressure.

### Band 15+ (|h|≥20, intra-strand 2-7 where settle already commits)
0% fire rate. These positions have pressure already exceeding the
barrier — settle commits them in the control re-settle. The trigger
can't change anything because the control already settled these
positions. The seed recorded them as null, but settle disagrees.
This confirms exp01's finding: learned motifs are not fixed points
of settle at familiarity=0.

## +1/-1 asymmetry

In bands 10-14: **15 asymmetric pairs, 0 symmetric pairs (100%).**

All 70 nulls at |h|=13 are at intra-strand position 3 (P3I=27).
The pressure h=+13 comes from exactly one cross-strand neighbor
at that position with trit=+1 (contributing 27//2 = 13). Triggering
+1 aligns with the existing pressure field: h goes from 13 to
13+27=40, well past the barrier, and the full cross-strand column
cascades. Triggering -1 opposes the field: h goes from 13 to
13-27=-14, which is within the barrier, so only the trigger position
itself changes.

This is the cleanest finding: the cascade is not just
position-dependent (exp01) but polarity-dependent at loaded nulls.
The DIRECTION of the trigger matters where pressure is close to the
barrier.

## Things noticed (for joint read)

1. The pressure landscape is discrete and trimodal, not continuous.
   The bands 6-9 and 10-12 are structurally impossible given the
   P3I weights and cross-strand resonance formula. The "pressure
   gradient" that would let nulls be loaded to different degrees
   doesn't exist at the current scale (8 trits, 8 strands).

2. Band 15+ nulls are an artifact: they're null in the stored motif
   but would commit under familiarity=0 re-settle. The seed motif
   was produced at a different familiarity during feeding, so its
   commit/null pattern doesn't match familiarity=0 settle. This is
   the same finding as exp01's control-re-settle observation.

3. Only intra-strand position 3 produces loaded nulls (|h|=13). This
   is because P3I[3]=27, and 27//2=13, which is just below the
   barrier of 15. P3I[2]=9 gives 9//2=4 (too far below), P3I[4]=81
   gives 81//2=40 (too far above). The "interesting" pressure band
   exists at exactly one intra-strand position.

4. At larger scale (more strands, wider context), more intra-strand
   positions could land in the loaded range, because more cross-strand
   terms would sum. At CONTEXT=8, only position 3 has the right
   arithmetic. This may be a scale limitation, not a substrate
   limitation.
