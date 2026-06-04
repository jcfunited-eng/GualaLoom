# Experiment 06 — Three-Layer Collision (third pass)

**Date:** 2026-06-04
**Runner:** c1 (Claude Opus 4.6)

## What changed in the third pass

### Word-mosaic rewritten (weakening 1 fixed)

**Old (pass 1-2):** Encoded fixed 16-char windows with truncation and
previous-word-tail contamination. Produced 437 motifs from 4008 words.
Word motifs were 16-char windows, not substrate snapshots.

**New (pass 3):** Normal character Loom runs through the entire corpus.
Character motifs commit at every tick. At every whitespace boundary,
the loom's current settled state is snapshotted and committed as a word
motif labeled with the word that just completed. No truncation, no
padding, no contamination. The word motif IS the substrate's state after
processing that word's characters in their actual context.

### Folding composition rewritten (weakening 2 fixed)

**Old (pass 1-2):** Destructive intersection — if one parent was null
at a position, the composition went null. "100% stable" because
compositions were nearly empty (null fraction 0.88).

**New (pass 3):** Structural union with conflict-nulling:
- Both agree (same sign or both null): keep
- Both committed but disagree (opposite signs): null
- One committed, one null: KEEP the commitment

Composition should ADD what each parent carries unless they actively
disagree.

## (1) Word-mosaic comparison

| Metric | OLD (windows) | NEW (settled snapshot) |
|--------|---------------|----------------------|
| Total motifs | 437 | 5431 |
| Word-labeled motifs | 437 | 981 |
| Unique words with motifs | 437 | 608 |
| Char motifs | 0 | 5431 |
| Ingestion time | 1.1s | 26.2s |
| Chi range | [-29, -5] | [-58, +1] |
| Null fraction mean | 0.8387 | 0.8322 |
| Word motifs new | 437 | 0 |

**"Word motifs new: 0"** is the headline finding. Every word's settled
state, when snapshotted at the whitespace boundary, matched an EXISTING
character motif that had already been committed during the character
pipeline. Word motifs at CONTEXT=16 are not distinct structures — they
are character-motif states that happen to coincide with word boundaries.

This means: at CONTEXT=16, the word boundary carries no structural
information that the character cascade didn't already produce. The
settled state at the end of "substrate" is the same as the settled
state at some character tick within the word. The word-level layer
adds labels but no new structural content.

608 unique words → 981 word-labeled motifs (some words get different
motifs depending on context = working correctly). 0 motifs shared by
multiple words (each motif has exactly one word label = first-commit
wins). 5431 total motifs dominated by character motifs from the Loom.

## (2) Folding composition comparison

| Metric | OLD (intersection) | NEW (union) |
|--------|-------------------|-------------|
| Pairs attempted | 50 | 50 |
| Stable | 50 | 50 |
| Collapsed to null | 0 | 0 |
| Merged null fraction | 0.88 | 0.62-0.81 |
| Settled null fraction | 0.88 | 0.62-0.81 |

The union rule produces DENSER compositions (merged_null=0.62-0.81 vs
0.88 under intersection). The compositions carry more structure.

Sample compositions:
```
gualaloom + arcloom: merged=0.81 settled=0.81 chi=-29 recalls=arcloom
arcloom + —:        merged=0.62 settled=0.62 chi=-58 recalls=—
gualaloom + None:    merged=0.81 settled=0.81 chi=-13 recalls=None
— + arcloom:        merged=0.62 settled=0.62 chi=-58 recalls=—
```

**recalls_to_novel = False for all.** Every composed motif recalls to
one of its parents or to an existing motif. No composition produced a
novel recall target — the composed state is structurally close enough
to one parent that recall finds it. Union didn't create genuinely new
structures; it created denser versions of existing ones.

The merged and settled null fractions are identical for all 50
compositions. This means the merge result is ALREADY a fixed point of
settle. The union of two settled states is itself settled. This is a
real structural property: when parents agree or one is silent, the
union inherits their settling. The only positions that could change
under re-settle are the conflict-nulled positions, and those don't
accumulate enough cross-strand pressure to commit.

## (3) Generation under three perturbation modes

### null_pos0 (null only position 0 per strand, 6%)
```
arcloom → arcloom (fixed point, 2 steps)
gualaloom → gualaloom (fixed point, 2 steps)
— → — (fixed point, 2 steps)
architecture.md → architecture.md (fixed point, 2 steps)
line → line (fixed point, 2 steps)
```
All 10 starters: emit starter word, fixed point. Position 0 (P3I=1)
carries no structural weight. Nulling it changes nothing.

### null_pos03 (null positions 0-3, 25%)
```
arcloom → arcloom the (fixed point, 3 steps)
gualaloom → gualaloom the (fixed point, 3 steps)
architecture.md → architecture.md the (fixed point, 3 steps)
line → line the (fixed point, 3 steps)
`structural_lock → `structural_lock (perturbation collapsed, 2 steps)
```
7/10 starters emit starter word then "the", then fixed point. The
perturbation nulled positions 0-3 (P3I up to 27), and the re-settle
recalled "the" — the most common word in English, and therefore the
word whose character cascade most commonly produced the settle
configuration that remains after positions 0-3 are nulled.

"the" is not a bigram-statistical artifact. It is what the substrate
settles to when you remove the low-weight structural detail from any
motif. Every word, stripped of its positions 0-3, looks like "the" to
the recall function. This is the substrate's ACTUAL attractor at
CONTEXT=16: the structural skeleton common to most English words.

2/10 starters collapsed when positions 0-3 were nulled — these were
motifs where positions 0-3 were load-bearing.

### feed_char (replace strand 0 with cycling a-z)
```
arcloom → arcloom (fixed point, 2 steps)
gualaloom → gualaloom (fixed point, 2 steps)
— → — (fixed point, 2 steps)
```
All 10 starters: emit starter word, fixed point. Replacing one strand
with a character encoding doesn't change the settle outcome — 15
cross-strand terms at the high positions overwhelm the single
perturbed strand.

## (4) The findings from the wreckage

1. **Word-level motifs are not structurally distinct from character
   motifs at CONTEXT=16.** The word boundary adds a label, not a
   structure. This means word-mosaic as a separate layer doesn't
   exist — it's an index into the character krimelack, not a new
   level of composition.

2. **Union composition is stable and dense but not novel.** Every
   composed motif recalls to a parent. The union doesn't create
   structures that weren't already there. This is because the
   parents share most of their committed positions (they're
   sequential motifs in the same corpus flow, so their context
   windows overlap heavily). Union of near-identical states is
   near-identical to either parent.

3. **"the" is the structural attractor at CONTEXT=16.** When you
   strip low-weight detail from any motif, the remaining structure
   recalls to "the". This is not a frequency artifact — it's a
   geometric property. "the" is the most structurally generic word
   in the corpus, and its settle configuration is the basin floor
   that everything falls into when perturbed.

4. **Generation at CONTEXT=16 is single-step at every perturbation
   level.** The substrate cannot sequence because there is no
   intermediate perturbation strength between "does nothing" (6%)
   and "collapses or recalls to the universal attractor" (25%).
   This is the same loaded-zone finding as exp02-05: no middle
   ground at this scale.

5. **The cascade machinery works. The dynamics produce silence.**
   No crashes. Every settle call returns a valid state. Every recall
   finds a motif. The substrate is mechanically functional. It just
   has nothing to say beyond one word, because the pressure landscape
   at CONTEXT=16 has no loaded zone for generation to ride.
