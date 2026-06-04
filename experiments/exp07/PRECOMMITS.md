# Experiment 07 — Pre-Commits

**Date:** 2026-06-04
**Runner:** c1 (Claude Opus 4.6)
**Committed BEFORE any experiment code runs.**

---

## 1. NOVELTY CRITERION

Composition (A, B) -> R is NOVEL iff ALL THREE hold:

1. **Not parental:** R is not in the chi-neighborhood (chi-distance <= 2) of A or B
2. **Cross-domain consistent:** R is in the chi-neighborhood (chi-distance <= 2) of
   at least one motif from A's domain AND at least one motif from B's domain
3. **Cognitively engaged:** R has |h| >= 4 at idx=3 (loaded-null surface, not flat)

All three conditions must hold simultaneously. A result that passes (1) but fails
(2) is geometric displacement, not compositional novelty. A result that passes (1)
and (2) but fails (3) is structurally inert.

---

## 2. PRIMITIVE ENCODING SCHEME

### Canonical list (frozen, alphabetical)

```
 #  Name              3-trit signature    prime_index
 1  agent             (+1,  0,  0)        1
 2  deixis_distal     (-1, +1,  0)        2
 3  deixis_proximal   ( 0, +1,  0)        3
 4  dep_dir           (+1, +1,  0)        4
 5  focus             (-1, -1, +1)        5
 6  hedge             ( 0, -1, +1)        6
 7  imperative        (+1, -1, +1)        7
 8  modifier          (-1,  0, +1)        8
 9  modality          ( 0,  0, +1)        9
10  mood              (+1,  0, +1)       10
11  negation          (-1, +1, +1)       11
12  object            ( 0, +1, +1)       12
13  performative      (+1, +1, +1)       13
14  question          (-1, -1, -1)       14
15  scope             ( 0, -1, -1)       15
16  sentence_bound    (+1, -1, -1)       16
17  statement         (-1,  0, -1)       17
18  subject           ( 0,  0, -1)       18
19  verb              (+1,  0, -1)       19
20  vocative          (-1, +1, -1)       20
```

### Derivation rule

`signature = balanced_ternary_3trit(prime_index)` where:
- prime_index = 1-indexed alphabetical position in the frozen list above
- 1-indexed to avoid the all-null (0,0,0) signature at index 0
- Balanced ternary encoding: standard {-1, 0, +1} with carry, 3 trits
- All 20 signatures verified unique

### Chi-orthogonal placement

- **D4 (syntactic):** signature placed at trit positions 8, 9, 10 within each strand
  (P3I values: 6561, 19683, 59049 — unreachable from character input at barrier=104)
- **D5 (communication):** signature placed at trit positions 12, 13, 14 within each strand
  (P3I values: 531441, 1594323, 4782969 — unreachable from character input)
- D4 and D5 occupy non-overlapping position ranges, guaranteeing chi-orthogonality
- Character-derived domains (D1-D3) commit only at low positions (0-4), no interference

### Motif generation (to reach ~2000 per domain)

Each primitive is a 256-trit state with the 3-trit signature at the designated
positions in ONE strand, rest null. To reach ~2000 motifs per domain:
- All singletons (20)
- All ordered pairs settled together (20*19 = 380)
- All ordered triples settled together (20*19*18 / 6 = 1140)
- Continue with 4-tuples if needed to reach ~2000

The settle step is applied to the combined strands, so composite primitives
interact through the coupling rule, producing genuine settled states (not
concatenation).

### Freeze

No primitive encoding may be modified after this file's commit hash is recorded.

---

## 3. EMPTY-REAL-ESTATE GUARD

A composition result R lands in "empty real estate" iff:

```
count(motifs M in krimelack where |chi(M) - chi(R)| <= 3) < 3
```

Empty-real-estate landings are reported separately as **geometric novelty**.
They DO NOT count as **compositional novelty** even if they pass the novelty
criterion above. The distinction matters because:
- Compositional novelty = the substrate found a state consistent with both
  parent domains in occupied territory (the composition added real structure)
- Geometric novelty = the composition landed somewhere nobody has been
  (may be noise, may be real — can't tell without population)

---

## 4. CONFIGURATION (computed, frozen)

```
CONTEXT   = 16
TRITS     = 16
POP       = 256  (CONTEXT * TRITS)
P3I[3]    = 27
P3I[3]//2 = 13
barrier   = round(0.5 * CONTEXT * (P3I[3] // 2))
          = round(0.5 * 16 * 13)
          = 104
```

Note: the formula `round(0.5 * CONTEXT * P3I[3] // 2)` has ambiguous precedence.
The parenthesized form `round(0.5 * CONTEXT * (P3I[3] // 2))` = 104 matches the
semantic intent: scale half the context by the loaded-null pressure value from exp02.
The left-to-right evaluation gives 108. Using 104.

barrier = 104, frozen for the entire run.
