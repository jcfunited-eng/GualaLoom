# Experiment 05 — Chi-Keyhole Hypothesis

**Date:** 2026-06-04
**Runner:** c1 (Claude Opus 4.6)

## What this tests

Whether inner-level cascades whose end-state chi values fall in the
outer level's loaded-pressure zone selectively trigger outer-level
cascades, while inner cascades whose chi falls outside that zone leave
the outer level silent. This would be selective upward propagation —
vertical cognition.

## Result: the keyhole is degenerate at this scale

The experiment was stopped after step 1 (keyhole enumeration) because
the keyhole set is nearly the entire chi range, making the cascade
probe uninformative.

## Keyhole enumeration

For each chi value in the observed range [-19, +2], balanced-ternary
encoded and tested across 800 outer-level contexts (100 outer states
× 8 insertion positions). Checked whether any null trit position in
the inserted strand falls in the loaded zone (|h| ∈ [13, 14]).

```
  Chi  BT encoding               Loaded?  At position
  -19  [-1, 0, 1, -1, 0,0,0,0]  NO       —
  -18  [ 0, 0, 1, -1, 0,0,0,0]  NO       —
  -17  [ 1, 0, 1, -1, 0,0,0,0]  NO       —
  -16  [-1, 1, 1, -1, 0,0,0,0]  NO       —
  -15  [ 0, 1, 1, -1, 0,0,0,0]  NO       —
  -14  [ 1, 1, 1, -1, 0,0,0,0]  NO       —
  -13  [-1,-1,-1,  0, 0,0,0,0]  YES      pos 3 (31.9%)
  -12  [ 0,-1,-1,  0, 0,0,0,0]  YES      pos 3 (31.9%)
  ...  (all chi in [-13, +2])    YES      pos 3 (31.9%)
  ...
    2  [-1, 1, 0,  0, 0,0,0,0]  YES      pos 3 (31.9%)
```

**Keyhole set:** chi ∈ {-13, -12, -11, -10, -9, -8, -7, -6, -5, -4,
-3, -2, -1, 0, 1, 2} — **16 of 22 observed chi values (73%).**

**Non-keyhole set:** chi ∈ {-19, -18, -17, -16, -15, -14} — only 6
values, all with |chi| ≥ 14.

## Why the keyhole is degenerate

The loaded null is always at **outer position 3** (P3I[3]=27,
P3I[3]//2=13, loaded range [13,14] at barrier=15). Whether a chi
value produces a loaded null at position 3 depends solely on whether
**position 3 is null in the BT encoding of chi**.

Position 3 in balanced ternary represents the 27s place. Chi values
in [-13, +13] fit in 3 BT digits (positions 0-2), leaving position 3
as 0 (null). Chi values with |chi| ≥ 14 require the 27s place, so
position 3 is ±1 (committed, not null).

The "keyhole" is just: does |chi| < 14? That's not a narrow cognitive
filter — it's the vast majority of observed chi values. The selectivity
the experiment tests reduces to "does the chi encoding use 3 trits or
4 trits."

## What's actually happening

- Every chi value in [-13, +2] produces the same loaded null at the
  same position (outer pos 3) with the same |h|=13
- Every chi value in [-19, -14] commits position 3, so no loaded null
- The loaded-null rate is 31.9% across all keyhole chi values
  (identical — no variation within the keyhole)
- The loaded-null rate is 0% for all non-keyhole chi values
  (identical — no variation outside the keyhole)

There's no gradient, no partial selectivity, no interesting boundary
effects. It's a binary switch: chi fits in 3 digits → loaded; doesn't
→ not loaded.

## Why the keyhole would be non-degenerate at larger scale

At CONTEXT=8 with barrier=15, there is exactly ONE loaded position
(intra-strand 3) at both inner and outer levels. The keyhole can't
be selective because the loaded zone is a single point.

At larger scale, multiple positions could be loaded simultaneously,
and different chi values would activate different subsets of loaded
positions. The keyhole would become a multi-dimensional filter:

1. **More strands (CONTEXT > 8):** more cross-strand terms in the
   pressure sum. Intermediate |h| values become possible at more
   intra-strand positions (exp04 showed this at the outer level
   for positions 0-2).

2. **Lower barrier:** exp03 showed this doesn't help at single-level
   (discrete gaps), but exp04 showed hierarchical composition fills
   the gaps. A two-level structure with a lower outer barrier could
   have loaded nulls at positions 0, 1, and 2 — each with different
   BT-digit sensitivity, creating a genuinely selective keyhole.

3. **Three or more levels:** each additional level of composition
   shifts the trit-activity pattern. A chi-of-chi-of-chi encoding
   would distribute weight differently than chi-of-chi, potentially
   creating loaded positions that are unique to the deeper
   composition.

## What this means for the cascade path

The chi-keyhole hypothesis is correct in principle — inner-level
structural summaries CAN selectively trigger outer-level cascades —
but the selectivity is trivially binary at the current scale. The
experiment that would test genuine selectivity needs either wider
context, multi-level composition with tuned barriers, or both.

This is consistent with exp03's finding: the substrate at CONTEXT=8
has only one cognitive position per level. Expanding the cognitive
surface requires scaling, not tuning.
