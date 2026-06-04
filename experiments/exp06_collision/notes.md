# Experiment 06 — Three-Layer Collision

**Date:** 2026-06-04
**Runner:** c1 (Claude Opus 4.6)

## What this is

Deliberate stress test: stack CONTEXT=16, folding composition, and
word-mosaic ingestion. Best-guess everything, no tuning. Capture what
breaks.

## Configuration

```
TRITS=16, CONTEXT=16, POP=256
DEAD_ZONE=15 (unchanged)
P3I = (1, 3, 9, 27, 81, 243, 729, 2187, 6561, 19683, 59049, 177147,
       531441, 1594323, 4782969, 14348907)
```

## (1) What completed and what didn't

**Everything completed. Zero crashes.**

- Word-mosaic ingestion: 4008 words → 437 unique motifs in 1.1s
- Folding composition: 50/50 pairs produced stable motifs, 0 null collapses
- Generation: all 10 starting words produced output

This was surprising. The three-layer stack ran without mechanical
failure.

## (2) The 10 generation outputs verbatim

```
[0] start='gualaloom' (w=2918, chi=-29)
    gualaloom descent, gualaloom substrate gualaloom — gualaloom —
    descent, gualaloom substrate gualaloom substrate — gualaloom

[1] start='descent,' (w=389, chi=-14)
    descent, gualaloom descent, architecture gualaloom substrate
    gualaloom substrate — gualaloom substrate — descent, gualaloom

[2] start='—' (w=89, chi=-58)
    — gualaloom descent, gualaloom substrate gualaloom — gualaloom —
    descent, gualaloom substrate gualaloom substrate — gualaloom

[3] start='substrate' (w=52, chi=-14)
    substrate gualaloom descent, gualaloom substrate — gualaloom
    substrate — descent, gualaloom substrate — descent, architecture

[4] start='architecture' (w=40, chi=1)
    architecture gualaloom descent, gualaloom substrate gualaloom —
    gualaloom — descent, gualaloom substrate gualaloom substrate

[5] start='motif' (w=17, chi=-29)
    motif descent, gualaloom descent, architecture gualaloom substrate
    gualaloom substrate — gualaloom substrate — descent,

[6] start='#' (w=16, chi=-28)
    # gualaloom descent, gualaloom substrate gualaloom — gualaloom —
    descent, gualaloom substrate gualaloom substrate — gualaloom

[7] start='feedback' (w=9, chi=-14)
    feedback | gualaloom descent, gualaloom substrate gualaloom —
    gualaloom — descent, gualaloom substrate gualaloom substrate

[8] start='→' (w=7, chi=-58)
    → gualaloom descent, gualaloom substrate gualaloom — gualaloom —
    descent, gualaloom substrate gualaloom substrate — gualaloom

[9] start='ternary' (w=6, chi=-26)
    ternary gualaloom descent, gualaloom substrate gualaloom —
    gualaloom — descent, gualaloom substrate gualaloom substrate
```

## (3) The first thing that broke

**Nothing mechanically broke.** The first FAILURE is the attractor
collapse in generation. "gualaloom" (weight=2918) dominates every
output within 1-2 steps. Every generation run converges to the same
~5 word orbit: {gualaloom, descent, substrate, —, architecture}.
This is the exp01 attractor problem at word scale.

## (4) The most interesting failure mode

**The pressure landscape at CONTEXT=16 is WORSE than CONTEXT=8.**

```
CONTEXT=8 pressure bands:       CONTEXT=16 pressure bands:
  0-5:   91.1%                    0-5:   97.7%
  6-9:    0.0%                    6-9:    0.0%
10-12:    0.0%                   10-12:   0.0%
13-14:    1.5%                   13-14:   0.0%   ← GONE
  15+:    7.4%                    15+:    2.3%
```

At CONTEXT=16, the loaded band (13-14) is **completely empty**. The
one cognitive position (intra-strand 3, |h|=13 from 7 cross-strand
neighbors each contributing P3I[3]//2=13) now has 15 cross-strand
neighbors each contributing 13, giving |h|=195 for any position
where neighbors agree. The pressure jumps from the inert zone
straight to the already-committed zone, skipping the loaded band
entirely.

**Wider context DESTROYED the loaded-null mechanism.** More
cross-strand terms don't smooth the pressure landscape — they amplify
it. The barrier of 15 is overwhelmed by 15 cross-strand votes at
P3I[3]//2=13 each. Every position that has any cross-strand resonance
blows past the barrier immediately. The loaded zone between "inert"
and "committed" doesn't exist at this scale.

This means: the cognitive surface area finding from exp02-04 is
BARRIER-DEPENDENT and CONTEXT-DEPENDENT in a non-obvious way.
Doubling context doesn't double the cognitive surface — it can
collapse it to zero.

## (5) What surprised me in the wreckage

1. **Zero mechanical failures.** The entire stack ran in 1.1s.
   The substrate's computational properties (integer ternary, no
   floating point, deterministic) mean it doesn't crash on scale
   change. The MATH is wrong at scale, but the CODE is fine.

2. **Folding composition succeeded at 100%.** All 50 merges produced
   stable motifs, zero null collapses. "agree-keep, disagree-null"
   is a robust merge rule. The composed motifs recall to their parents
   (every composition recalled to one of its source motifs). This
   suggests folding composition at CONTEXT=16 is mechanically sound
   even if the pressure landscape is broken.

3. **437 motifs from 4008 words (1676 unique) = 26% motif-to-word
   ratio.** Many distinct words collapse to the same motif. This is
   expected — the context window means similar character sequences
   settle to the same state — but the ratio tells us something:
   word-mosaic at CONTEXT=16 provides about 4x compression of the
   vocabulary into structural equivalence classes.

4. **Chi distribution shifted dramatically.** CONTEXT=8 chi range:
   [-19, +2]. CONTEXT=16 chi range: [-58, +1]. The wider state
   allows much more negative chi (more edges in the coupling graph
   relative to vertices). The chi landscape is richer at CONTEXT=16,
   even though the pressure landscape is poorer.

5. **The attractor is even worse at word scale.** At character scale,
   the loop-breaker managed 11 distinct outputs for 16 inputs. At
   word scale, "gualaloom" (w=2918) has 7x the weight of "descent,"
   (w=389) and 50x the weight of everything else. The successor graph
   is a star topology centered on "gualaloom". The loop-breaker can't
   escape because there are no alternative paths — every word leads
   back to "gualaloom" within 1-2 hops.

## The key finding

**The barrier must scale with context.** At CONTEXT=8, barrier=15
creates a loaded zone at position 3 because 7 cross-strand terms at
P3I[3]//2=13 can't all push past 15 unless they agree. At CONTEXT=16,
15 cross-strand terms at P3I[3]//2=13 sum to 195, which overwhelms
barrier=15 completely. The barrier needs to be proportional to
(CONTEXT - 1) × P3I[loaded_position] // 2, or approximately
barrier ≈ 0.5 × CONTEXT × 13 ≈ 104 at CONTEXT=16 for position 3 to
remain in the loaded zone.

This is not a tuning recommendation — it's a structural observation
about what broke and why. The barrier-to-context relationship is the
first thing to investigate if wider context is the path forward.
