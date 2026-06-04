# Experiment 07 — Riskiest Best-Guess and Safest Fallback

**Date:** 2026-06-04
**Runner:** c1 (Claude Opus 4.6)
**Committed BEFORE any experiment code runs.**

---

## RISKIEST BEST-GUESS

The substrate produces genuine compositional novelty at 10-20% rate for
cross-domain pairings involving at least one pre-loaded primitive domain
(D4 or D5), because the chi-orthogonal placement puts primitive structure
at positions the character-derived domains can never reach, and composition
via union-with-conflict-nulling creates states that inherit structural
opinions from both parents without collapsing to either.

Specifically:
- **(D1,D4), (D2,D4), (D3,D4)** and the D5 equivalents show the highest
  novelty rates because char/morpheme/word motifs occupy low trit positions
  while primitives occupy high trit positions — union has minimal conflict,
  and the settled composite is structurally novel (committed trits at both
  low and high positions, a chi value achievable by neither parent alone).
- **(D4,D5)** shows near-zero novelty because both domains occupy high
  positions and conflict-null each other extensively.
- **(D1,D2), (D1,D3), (D2,D3)** show low novelty (<5%) because all three
  occupy the same low trit positions and union produces heavy conflict.
- **Loaded nulls survive 3+ composition** in 40-60% of trials because the
  idx=3 position (P3I=27) has enough pressure from multi-motif alignment to
  stay in the loaded band even after union.
- **Vitals shift measurably** — familiarity rises during same-domain
  composition (substrate recognizing parental territory) and drops during
  cross-domain composition (novel territory).
- **feed_char rule R4** (structural-similarity recall) outperforms R1-R3
  because it reads the substrate's state rather than riding corpus statistics.

Why this is risky: it assumes the chi-orthogonal separation actually creates
complementary structure rather than just non-interfering garbage. If the
high-position primitives don't couple with low-position character content
during settling, the composition is just concatenation — no structural
interaction, no real novelty.

## SAFEST FALLBACK

Same trial structure, but if **ingestion mechanically fails** — defined as:
- Any domain produces < 50 non-null committed motifs after settling, OR
- Barrier 104 produces 100% null collapse on settle (all states all-null)

Then fall back to:
- barrier = 52 (half the computed value)
- Document why, re-run ingestion only, continue with same trial structure

The fallback exists ONLY for mechanical failure (the substrate literally
can't commit anything at this barrier). If the barrier works but results
are disappointing (low novelty, flat vitals), that is DATA, not failure.
Run the full experiment and report the numbers.

## WHAT I EXPECT TO LEARN EITHER WAY

If the risky version succeeds: chi-orthogonal primitive placement is the
engineering tool for multi-domain substrate architecture. The coupling
positions matter more than the content. This is directly applicable to
ArcLoom's multi-sensor sections.

If the risky version fails (low novelty, destroyed loaded nulls, flat
vitals): the substrate's compositional mechanism requires structural
overlap at the same trit positions, not orthogonal placement. Composition
is fundamentally about conflict resolution, not territory union. The next
experiment would need to test same-position multi-domain encoding (which
means domain identity must come from something other than position).
