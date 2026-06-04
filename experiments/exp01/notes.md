# Experiment 01 — Cascade Existence

**Date:** 2026-06-04
**Commit:** see git log
**Runner:** c1 (Claude Opus 4.6)

## Revised design

Initial spec assumed settle could be re-run on an arbitrary state as a
fixed-point operator. It cannot — settle recomputes commitments from
strands against the barrier, so any state not previously produced by
settle (random synthetic seeds) dissolves on re-evaluation. This is
correct behavior of the rule. The synthetic-seed half of the original
design was dropped; experiment proceeds with learned seeds only and a
control-vs-trigger differential probe.

## Method

Two-step differential probe per trial:
1. **Control:** re-settle the unmodified seed to its natural equilibrium.
2. **Trigger:** commit one null trit to ±1, then re-settle.
3. **Cascade depth** = positions where trigger end-state differs from
   control end-state, minus the trigger position itself.

This subtracts settle's own recomputation (baseline noise) from the
trigger's propagation effect.

## Parameters

- **Settle function:** `gualaloom.py` top-level `settle()` (same math
  as `src/gualaloom/substrate.py:settle_field()`, chosen because
  gualaloom.py is the canonical runtime)
- **Population:** TRITS=8 × CONTEXT=8 = 64 trits
- **Seeds:** 100 learned motifs sampled from krimelack after corpus
  ingestion (893 motifs available, RNG seed 7777)
- **Triggers per seed:** 10 null positions (sampled), × 2 values (+1, -1)
- **Total trials:** 2000
- **Step cap:** 50 settle iterations
- **Familiarity:** 0 (held constant)

## Reproducibility

50 trials run twice with identical inputs:
- Control end-state hash mismatches: **0**
- Trigger end-state hash mismatches: **0**

Settle is fully deterministic.

## Raw summary

```
cascade_depth: min=0 max=7 mean=3.38 median=0
depth=0:  1024 (51.2%)
depth>0:   976 (48.8%)
depth distribution: {0: 1024, 1: 9, 6: 13, 7: 954}

trigger stable:  2000/2000 (100.0%)
control stable:  2000/2000 (100.0%)
trigger steps: min=1 max=3 mean=2.01
null_fraction_start: min=0.3750 max=0.9844 mean=0.7148
```

## Things noticed (not interpreted — for the joint read)

1. The depth distribution is bimodal: 0 or 7, almost nothing in between
   (only 9 at depth=1, 13 at depth=6). The cascade is either silent or
   fires hard — no gradual propagation.

2. Every trial reaches stability within 3 settle steps. No oscillation
   observed at any trigger position or value. Step cap of 50 was never
   approached.

3. The control re-settle itself often shifts the seed state (chi_start
   differs from chi_control in the raw data). Learned motifs are not
   fixed points of settle — they were produced by settle during feeding,
   but feeding includes familiarity and context that differ from
   familiarity=0 re-settle. The differential probe handles this
   correctly.

4. +1 and -1 triggers at the same position sometimes produce the same
   end-state hash (e.g., position 58 in seed s0 — both reach
   c680745a5a4a with depth=0). Other positions produce different
   end-states for +1 vs -1 but the same cascade depth.

5. Mean null_fraction_start is 0.71 — most learned motifs are
   majority-null. Only ~29% of trits commit during normal feeding.
