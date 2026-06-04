# Experiment 07 — DNA Five Capabilities, Multi-Seed Validation

**Date:** 2026-06-04
**Runner:** c1 (Claude Opus 4.6)

## Result: 11/12 seeds pass all 5 capabilities. Conversation passes 12/12.

Matches reference result count. The failing seed differs (99 vs reference's
1234) due to RNG path sensitivity in homeostatic self-improvement — documented
architectural limitation, not a divergence.

## Per-capability results

| Capability | Pass/12 | Reference |
|---|---|---|
| Syntax | 12/12 | 12/12 |
| Conversation | 12/12 | 12/12 |
| Introspection | 12/12 | 12/12 |
| Self-improvement | 11/12 | 11/12 |
| Awareness | 12/12 | 12/12 |

## Per-seed comparison to reference

| Seed | Mine | Reference | Match? |
|---|---|---|---|
| 42 | ALL PASS | ALL PASS | MATCH |
| 7 | ALL PASS | ALL PASS | MATCH |
| 99 | self_improvement FAIL | ALL PASS | seed-swap |
| 23 | ALL PASS | ALL PASS | MATCH |
| 156 | ALL PASS | ALL PASS | MATCH |
| 311 | ALL PASS | ALL PASS | MATCH |
| 8888 | ALL PASS | ALL PASS | MATCH |
| 1 | ALL PASS | ALL PASS | MATCH |
| 2024 | ALL PASS | ALL PASS | MATCH |
| 17 | ALL PASS | ALL PASS | MATCH |
| 555 | ALL PASS | ALL PASS | MATCH |
| 1234 | ALL PASS | self_improvement FAIL | seed-swap |

10/12 exact match. 2 seeds swapped which one fails self-improvement.

## Why the failing seed swapped

Self-improvement tests homeostatic adaptation: does gamma move from defaults
without pinning at boundaries, and does adaptation not cause catastrophic
degradation (mean_with >= mean_without - 0.12)?

Seed 99 this run: mean_with=0.427, mean_without=0.579 — gap of 0.152 exceeds
the 0.12 tolerance. Adaptation made things worse.

Seed 1234 this run: mean_with=0.423, mean_without=0.296 — adaptation helped.
Reference had it the other way.

This is the documented limitation: "homeostatic adaptation ≠ task optimization."
The substrate adjusts gamma based on internal three-axis health, not task
outcomes. Whether that incidentally helps or hurts is RNG-path-dependent.
The RATE of failure (1/12) and the MECHANISM match the reference exactly.

## Hardcoded protections verified

- Bootstrap mechanism: hardcoded at max 8
- Coordinator action space: {merge, defer, request_keyhole} — no delete
- Atlas: append-only
- Intro krimelack: isolated (0 leakage across all 12 seeds)
- Evidence-pressure requirement: >= 0.15 for any commit

## Documented limitations preserved

- ~40% of sentences silently fail (sections don't all commit)
- No persistent entrainment growth in conversation
- Self-improvement is homeostatic, not task-optimizing
- Awareness is operational signature, not phenomenal

## Files

- `src/gualaloom/dna/assemblage.py` — Section, System, ChiAtlas, all primitives
- `src/gualaloom/dna/test_five.py` — five capability tests
- `src/gualaloom/dna/conversation_log.py` — conversation transcript generator
- `experiments/exp07/multi_seed_results.json` — raw results across 12 seeds
- `experiments/exp07/reference_results.json` — wC's reference results
- `experiments/exp07/RECIPE.md` — the recipe specification
