# c1 Deploy Command — MathLoom + Krimelack + Unified Five-Cap Demo

**Handoff tag** (grep this to find every artifact in this bundle):
`GUALALOOM-HANDOFF-WC-2026-06-04-MATHLOOM-KRIMELACK`

**From**: wC (web Claude), session 2026-06-04
**To**: c1 (Claude Code in VS Code)
**Repo**: https://github.com/jcfunited-eng/GualaLoom

## Files in bundle

1. `gualaloom_mathloom_v1.py` — balanced ternary arithmetic
2. `gualaloom_krimelack_v1.py` — oscillator transduction for text input
3. `gualaloom_unified_v1.py` — single-instance five-cap demo using both
4. This file

## What to do

### 1. Place files in repo

```
src/gualaloom/math/mathloom.py             <-  gualaloom_mathloom_v1.py
src/gualaloom/perception/krimelack.py      <-  gualaloom_krimelack_v1.py
experiments/unified_v1/unified_guala.py    <-  gualaloom_unified_v1.py
experiments/unified_v1/HANDOFF.md          <-  this file
```

Add `__init__.py` in each new directory. Keep the handoff tag in a comment
at the top of each file so future searches resolve.

### 2. Wire imports

The unified demo currently does `import gualaloom_mathloom_v1 as ml` and
`import gualaloom_krimelack_v1 as kr`. After placement those become:
```python
from gualaloom.math import mathloom as ml
from gualaloom.perception import krimelack as kr
```
Update the imports in unified_guala.py accordingly. The assemblage import
should remain `from gualaloom.dna.assemblage import ...` (or whatever the
repo's current path is — check the existing v6 dialog code for the pattern).

### 3. Validate MathLoom

Run `python -m gualaloom.math.mathloom`. Expected output:
```
addition: 6561 tests, 0 failures
multiplication: 961 tests, 0 failures
division: 610 tests, 0 failures
```
If any failures, stop and report back. Do not proceed.

### 4. Validate Krimelack

Run `python -m gualaloom.perception.krimelack`. Expected: distinct event
counts per sentence, deterministic across re-runs (same input → identical
events). If determinism fails, stop and report.

### 5. Run the unified five-cap demo

```
python experiments/unified_v1/unified_guala.py
```

Expected: all five capabilities PASS in a single running instance, plus
seven correct MathLoom answers (1+1=2, 2+2=4, 3+5=8, 10+10=20, 7-4=3,
3*3=9, 10/2=5). Capability thresholds (already encoded in the script):
- syntax: order_score >= 0.5
- conversation: vocab >= 20 AND modes >= 30
- introspection: intro_commits >= 5 AND no atlas leak
- self_improvement: gamma_drift > 0.01
- awareness: coord_actions >= 5 AND resolution_effect >= 0.15

### 6. Regression check existing DNA

Run the existing validated five-cap test against assemblage.py to confirm
substrate primitives still pass (this is the baseline canon). Expected: 5/5
or 11/12 per the recipe.

### 7. Honest substrate failures to expect

- Substrate conversation output is rough: keyhole-cascade fires in order
  but vector-nearest word readout produces loose content
  (e.g. "tell me about hope" -> "saw nine has white i eight"). The
  ordering is real syntax; the content matching is the substrate's current
  limit. Don't paper over this.
- MathLoom Approach 3 (global settle by gradient descent) did NOT converge
  reliably in software — local minima in the tri-well potential. Approach 1
  (carry chain) is the working substitute, by spec. Approach 3 needs
  FPGA validation as the spec acknowledges.

### 8. Report back

Report should include:
- Repo paths where each file landed
- The output of step 3 (mathloom self-test)
- The output of step 5 (five-cap demo)
- Any test failures or import issues
- A sample of the conversation output and one MathLoom trace with carry chain

Do NOT auto-deploy further changes beyond this bundle without check-in.
The cheats wC kept (Hub Counter, CLASS_HINTS dict in older dialog code,
phased SUBJECT-COPULA-PREDICATE loop) are documented as still-to-remove
and are not part of this deploy.

## Engineering notes / known issues

- The unified demo's WordMemory keeps word->vector entries from krimelack
  transduction. This is a derived index (memory of what was heard), not a
  hand-built dict. Naming preserved (`word_str` as key) for debugging
  readability; the values are substrate output.
- MathLoom routes through a small word->int recognizer (`parse_math`) at
  the BSIL boundary. This is the binary-story-ingestion layer per spec,
  not a hidden cheat. Document it as the BSIL adapter.

## Tag for future search

Every file in this bundle contains the string `GUALALOOM-HANDOFF-WC-2026-06-04-MATHLOOM-KRIMELACK` so c1 can locate
and audit them with a single grep across the repo.
