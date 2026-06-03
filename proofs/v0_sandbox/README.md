# v0 Sandbox

**Status:** Throwaway sketch. Not load-bearing. Reference only.

These files were built by wC in a sandbox session on 2026-06-03 as a
first-pass proof that the ArcLoom substrate can eat language streams
and produce motif-commit / habituation / recall behavior — the same
mechanism the SPPU uses on sensor streams.

They are not the real LinguaLoom build. The real build lives in
`src/` (currently empty) and will be done by c1 inside this repo,
with access to the real substrate modules.

These files are kept for three reasons:
1. They are the artifact that produced the substrate-as-LLM insight.
2. They demonstrate the dynamics work in software before c1 touches
   real code.
3. The bug history matters: v1 had a tuning bug that produced empty
   results dressed up as success. The diagnostic.py file exposed it.
   That's a documented pattern this project must not repeat.

## Files

- `lingualoom_v2.py` — the substrate eating character streams.
  Pure-Python, integer-only, no imports beyond stdlib.
- `diagnostic.py` — field-inspection tool. Shows the actual
  coupling pressure at each trit position for a sample context
  window. Useful when motifs are not committing and you need to
  see why.
- `output_run1.txt` — captured output from the canonical run on
  wC's sandbox. Compare against c1's run on the dev container to
  confirm determinism.

## How to run

```bash
cd proofs/v0_sandbox
python3 lingualoom_v2.py
python3 diagnostic.py
```

No dependencies beyond Python 3.

## What the canonical run shows

Test 1 (repeated pattern "the cat sat on the mat" x4):
- First quarter: 9 new motifs, 14 reinforcements
- Fourth quarter: 3 new motifs, 20 reinforcements
- Habituation is real: new-motif rate dropped 3x, reinforcements
  climbed, familiarity rose, match score climbed.

Test 2 (novel gibberish "xqz!vbnm pwlrtj@ zkfhge#"):
- Match score 5.9, lower than Test 1's late quarter (7.8).
- Substrate honestly reports lower recognition.

Test 3 (return to original pattern):
- Match score back to 7.8.
- Krimelack growth -4 (decay culled stale motifs, recall pulled
  live ones back into resonance).
- Recognition without "loading" anything.

If c1's run on the dev container produces meaningfully different
numbers, that's a finding (different Python version, hash ordering,
or a real determinism gap) and should be surfaced before any
further work.
