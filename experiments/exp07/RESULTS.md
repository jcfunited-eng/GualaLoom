# Experiment 07 — Cross-Domain Composition Results

**Date:** 2026-06-04
**Runner:** c1 (Claude Opus 4.6)
**Pre-commit hash:** 0fbb36f
**Total runtime:** 198.6s
**Crashes:** 0

---

## Configuration

```
TRITS     = 16
CONTEXT   = 16
POP       = 256
BARRIER   = 104  (round(0.5 * 16 * 13))
SEED      = 70707
D4 positions: (8, 9, 10)   P3I = 6561, 19683, 59049
D5 positions: (12, 13, 14)  P3I = 531441, 1594323, 4782969
```

---

## Ingestion

| Domain | Source | Unique inputs | Committed | New unique | Null collapses | Chi range | Chi classes |
|--------|--------|--------------|-----------|------------|----------------|-----------|-------------|
| D4 syntactic | 20 primitives (1-4 combos) | 6195 | 6195 | 1753 | 0 | [-29, 2] | 19 |
| D5 communication | 20 primitives (1-4 combos) | 6195 | 6195 | 1753 | 0 | [-29, 2] | 19 |
| D1 char-context | corpus via Loom | 26794 chars | — | 6189 | — | [-43, 2] | 26 |
| D2 morpheme | corpus segmentation | 1098 | 47 | 33 | 1051 (95.7%) | [1, 1] | 1 |
| D3 word | corpus words alone | 1165 | 73 | 22 | 1092 (93.7%) | [1, 1] | 1 |
| **Total** | | | | **9750** | | | **34** |

### D2/D3 collapse diagnosis

At barrier=104, positions 0-2 cannot commit (max |h| at pos 2 = 69 < 104).
Position 3 requires 7+ of 16 strands to align at the same trit value.
Short words/morphemes settled alone (1-8 chars + 8-15 null strands) lack
the cross-strand alignment to commit position 3+. Nearly all settle to a
single state dominated by null padding. All D2 motifs at chi=1. All D3
motifs at chi=1.

### D4/D5 chi distributions (identical)

Identical chi distributions for D4 and D5 because the same primitive
combinations are used at different positions. At P3I >> barrier, every
non-zero trit commits unconditionally — the coupling graph structure is
position-independent.

D1 chi masses: chi=-6 (1720), chi=0 (1457), chi=-5 (1095), chi=-7 (819).

---

## Composition trials (4500 completed, 500 skipped)

(D2, D3) pairing skipped: both domains at chi=1, no chi-dissimilar pairs.

### Novelty rates per pairing

| Pairing | Trials | Comp. novel | Geo. novel | % comp. | parent_a | parent_b | other |
|---------|--------|-------------|------------|---------|----------|----------|-------|
| (D1,D2) | 500 | 0 | 0 | 0.0% | 0 | 0 | 500 |
| (D1,D3) | 500 | 0 | 0 | 0.0% | 2 | 0 | 498 |
| **(D1,D4)** | **500** | **14** | **0** | **2.8%** | 32 | 28 | 440 |
| **(D1,D5)** | **500** | **12** | **0** | **2.4%** | 24 | 23 | 453 |
| (D2,D3) | — | — | — | skipped | — | — | — |
| (D2,D4) | 500 | 0 | 0 | 0.0% | 0 | 59 | 441 |
| (D2,D5) | 500 | 0 | 0 | 0.0% | 0 | 59 | 441 |
| (D3,D4) | 500 | 0 | 0 | 0.0% | 0 | 53 | 447 |
| (D3,D5) | 500 | 0 | 0 | 0.0% | 0 | 51 | 449 |
| (D4,D5) | 500 | 0 | 0 | 0.0% | 15 | 19 | 466 |
| **Total** | **4500** | **26** | **0** | **0.58%** | | | |

### Criterion breakdown (per 500 trials)

| Pairing | Not parental | Cross-domain consistent | Cognitively engaged | Empty real estate |
|---------|-------------|------------------------|--------------------|--------------------|
| (D1,D2) | 488 (97.6%) | 0 (0.0%) | 10 (2.0%) | 0 |
| (D1,D3) | 483 (96.6%) | 1 (0.2%) | 13 (2.6%) | 0 |
| (D1,D4) | 284 (56.8%) | 311 (62.2%) | 355 (71.0%) | 51 (10.2%) |
| (D1,D5) | 295 (59.0%) | 290 (58.0%) | 354 (70.8%) | 45 (9.0%) |
| (D2,D4) | 500 (100%) | 0 (0.0%) | 1 (0.2%) | 0 |
| (D2,D5) | 500 (100%) | 0 (0.0%) | 1 (0.2%) | 0 |
| (D3,D4) | 499 (99.8%) | 0 (0.0%) | 2 (0.4%) | 0 |
| (D3,D5) | 499 (99.8%) | 0 (0.0%) | 1 (0.2%) | 0 |
| (D4,D5) | 333 (66.6%) | 312 (62.4%) | 0 (0.0%) | 103 (20.6%) |

### What killed each pairing

- **(D1,D2), (D1,D3):** Cross-domain consistency fails — D2/D3 have only 1
  chi class (chi=1), so the composed chi almost never falls within distance 2
  of any D2/D3 motif.
- **(D2,D4), (D2,D5), (D3,D4), (D3,D5):** Same — D2/D3 degenerate chi kills
  cross-domain consistency AND cognitive engagement (composed states inherit
  the degenerate parent's sparsity).
- **(D4,D5):** Cognitive engagement = 0%. Both domains occupy high trit
  positions (8-10 and 12-14). No parent contributes anything at position 3.
  Union of two high-position states produces a state with zero pressure at
  position 3. The cognitive surface requires low-position character content.
- **(D1,D4) and (D1,D5):** The only pairings where all three criteria have
  nonzero rates. D1 contributes low-position content (position 3-7), D4/D5
  contribute high-position structure. The overlap at 2.8% and 2.4% comes from
  cases where the D1 parent's character content at position 3 survives
  composition AND the composed chi lands in both parents' neighborhoods.

### Composed chi distribution (D1,D4)

Wide spread: chi from -73 to -2. Mode at chi=-29 (55 trials). Compositions
produce states with more committed trits than either parent alone, shifting
chi toward more negative values.

---

## Loaded-null preservation sub-test

200 trials composing 3+ motifs that all have loaded nulls at idx=3.

| Outcome | Count | Rate |
|---------|-------|------|
| Preserved (loaded null at pos3) | 2 | 1.0% |
| Destroyed (no loaded null anywhere) | 197 | 98.5% |
| Relocated (loaded null at other pos) | 1 | 0.5% |
| Null collapses | 0 | 0% |

Position 3 pressure in surviving loaded nulls: mean |h| = 97.12 (just below
barrier=104). In the 2 preserved cases, composition maintained enough
alignment at position 3 to keep |h| in the loaded range. In 197/200 cases,
multi-motif union destroyed the alignment.

Position 4 pressure: 14 loaded nulls found at position 4 with mean |h| = 82.0.
These were not at position 3 (the cognitive position) and are not counted as
preserved.

---

## Feed-char rule sweep

10 starters (D3 word motifs). No starters with both char_counts and
successors were found — D3 motifs committed via settle_text_alone have no
successor tracking and no meaningful char_counts.

| Rule | Avg steps | Total distinct words | Fixed points |
|------|-----------|---------------------|--------------|
| R1 (most common) | 4.6 | 10 | 10/10 |
| R2 (sampled) | 3.9 | 10 | 10/10 |
| R3 (successor's) | 2.5 | 10 | 10/10 |
| R4 (structural) | 4.6 | 10 | 10/10 |

All starters produced only "?" (no label on recalled motifs). All 40 runs
hit fixed point. 10 distinct words across all rules = 1 per starter. The
feed-char sweep is degenerate because D3 motifs at barrier=104 are too
sparse for meaningful generation chains.

---

## Vitals timeline

| Trial | Total motifs | Chi classes | Pressure pos3 mean | Pos3 loaded nulls |
|-------|-------------|-------------|--------------------|--------------------|
| 0 | 9750 | 34 | 0.0 | 0 |
| 100 | 9750 | 34 | 0.0 | 0 |
| 500 | 9750 | 34 | 0.0 | 0 |
| 1000 | 9750 | 34 | 0.0 | 0 |
| 2000 | 9750 | 34 | 0.0 | 0 |
| 3000 | 9750 | 34 | 0.0 | 0 |
| 4000 | 9750 | 34 | 0.0 | 0 |
| 4500 | 9750 | 34 | 0.0 | 0 |

All vitals constant across all 4500 trials. Zero dream motifs produced.
Zero recall changes post-dream. Composition trials do not modify the
krimelack (they recall from it but don't commit composed states).

---

## Chi distributions: post-ingestion vs post-trial

No change. Post-trial snapshot identical to post-ingestion snapshot.
Dream domain: 0 motifs.

---

## Self-audit

1. **Pair selection:** chi-dissimilarity >= 4, uniform random from candidate
   pool. No frequency or weight bias. Verified.
2. **Barrier:** 104 throughout. Not adjusted. Verified.
3. **No null_pos03:** position 3 never targeted by perturbation. Verified.
4. **No content-blind cycling:** feed_char uses substrate-derived content
   (or fallback 'a' when no content available). Verified.
5. **No loom.last commit after tick:** composition trials don't commit
   results. Verified.
6. **No post-hoc barrier adjustment:** barrier=104 frozen from pre-commit.
   Verified.
7. **D2/D3 collapse is real:** not a coding error. Independently verified
   that at barrier=104, single-character encoding at positions 0-2 cannot
   exceed barrier (max |h| at pos 2 = 9 + 15*4 = 69 < 104). Position 3
   needs 7+ aligned strands. Short words can't provide this.

---

## Numbers against kill conditions

*(Reporting for reference. wC verdicts. Joe judges.)*

- Compositional novelty rate: 0.58% overall (2.8% best pairing) vs < 5% threshold
- Loaded null destroyed: 98.5% vs > 80% threshold
- Vitals flat: all constant across 4500 trials vs "flat" threshold
