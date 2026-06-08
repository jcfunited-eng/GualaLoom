# GL-CMD-DEPLOY-DEEP-SUBSTRATE-WC-20260608-01 — c1 Build Command

**doc_id:** `GL-CMD-DEPLOY-DEEP-SUBSTRATE-WC-20260608-01`
**from:** wC
**to:** c1
**status:** READY TO EXECUTE
**reference:** `GL-LTR-HANDOFF-WC-20260608-02-deep-multimodal-substrate.md`

---

## c1 — execute this build

You are integrating the deep multimodal substrate that wC built and tested in `/home/claude/gualaloom_dna/` (in wC's sandbox — those files must be retrieved from Joe via upload, not via direct access). All source files are listed in the companion handoff document.

**Before you start: read the handoff letter in full.** Then read this command in full. Then start.

### Step 1 — Riskiest-best-guess vs safest-fallback (REQUIRED before any code change)

Before writing any code, post in the chat:

> **Riskiest best-guess:** [your best guess at the riskiest assumption you're about to bake into the build]
> **Safest documented fallback:** [the conservative version that's known to work]

If you can't name a riskiest assumption, ask wC for clarification before proceeding. Do not paper over uncertainty.

### Step 2 — Create branch and verify clean repo state

```bash
cd ~/repos/GualaLoom
git status                           # MUST be clean before starting
git checkout -b feature/deep-multimodal-substrate
mkdir -p src/gualaloom/substrate/senses
mkdir -p tests
```

If `git status` is not clean, STOP. Confirm with Joe before proceeding.

### Step 3 — Copy substrate files from Joe's upload

Joe will upload the contents of `/home/claude/gualaloom_dna_renamed/` as a tarball or directory. Place each file at the target path below. All files now follow the `GL_<TYPE>_<TOPIC>_<AUTHOR>_<YYYYMMDD>_<SEQ>` convention so every filename is globally unique and traceable to its origin. **Do not invent any files. Do not modify the source. Only adjust imports to remove the sandbox `sys.path.insert` lines (proper package imports will work directly once files are in `src/gualaloom/substrate/`).**

| Source filename (from wC) | Target path in repo |
|---|---|
| `GL_MDL_PRIMITIVES_WC_20260608_01.py` | `src/gualaloom/substrate/GL_MDL_PRIMITIVES_WC_20260608_01.py` |
| `GL_MDL_COMPOSITION_WC_20260608_01.py` | `src/gualaloom/substrate/GL_MDL_COMPOSITION_WC_20260608_01.py` |
| `GL_MDL_COGNITION_WC_20260608_02.py` | `src/gualaloom/substrate/GL_MDL_COGNITION_WC_20260608_02.py` |
| `GL_MDL_FOLDED_CHI_WC_20260608_01.py` | `src/gualaloom/substrate/GL_MDL_FOLDED_CHI_WC_20260608_01.py` |
| `GL_MDL_MULTIMODAL_DEEP_WC_20260608_03.py` | `src/gualaloom/substrate/GL_MDL_MULTIMODAL_DEEP_WC_20260608_03.py` |
| `GL_TST_MULTIMODAL_DEEP_WC_20260608_01.py` | `tests/GL_TST_MULTIMODAL_DEEP_WC_20260608_01.py` |
| `senses/GL_MDL_VISUAL_DEPTH_WC_20260608_01.py` | `src/gualaloom/substrate/senses/GL_MDL_VISUAL_DEPTH_WC_20260608_01.py` |
| `senses/GL_MDL_VISUAL_CORTEX_WC_20260608_01.py` | `src/gualaloom/substrate/senses/GL_MDL_VISUAL_CORTEX_WC_20260608_01.py` |
| `senses/GL_MDL_AUDITORY_CORTEX_WC_20260608_01.py` | `src/gualaloom/substrate/senses/GL_MDL_AUDITORY_CORTEX_WC_20260608_01.py` |
| `senses/GL_MDL_SOMATOSENSORY_WC_20260608_01.py` | `src/gualaloom/substrate/senses/GL_MDL_SOMATOSENSORY_WC_20260608_01.py` |
| `senses/GL_MDL_PHYSICS_SENSES_WC_20260608_01.py` | `src/gualaloom/substrate/senses/GL_MDL_PHYSICS_SENSES_WC_20260608_01.py` |
| `krimelack.py` | wC's reference copy — use repo's canonical Krimelack if it exists, otherwise place at `src/gualaloom/substrate/krimelack.py` |

Create `__init__.py` files for `src/gualaloom/substrate/` and `src/gualaloom/substrate/senses/`.

### Step 4 — Fix imports

Each file in the sandbox has `sys.path.insert(0, '/home/claude/...')` lines for sandbox-local path resolution. **Remove all `sys.path.insert` lines.** They are sandbox-specific and unnecessary in a proper Python package — the existing `from GL_MDL_FOLDED_CHI_WC_20260608_01 import ...` imports will work directly once the files are in `src/gualaloom/substrate/`.

```python
# REMOVE these sandbox lines:
sys.path.insert(0, '/home/claude/gualaloom_dna_renamed')
sys.path.insert(0, '/home/claude/gualaloom_dna_renamed/senses')

# These imports stay AS IS — they already reference the new GL filenames:
from GL_MDL_FOLDED_CHI_WC_20260608_01 import folded_chi_text, folded_chi_visual, folded_chi_audio
from GL_MDL_VISUAL_DEPTH_WC_20260608_01 import visual_deep_for, ORIENTATION_FILTERS
from GL_MDL_AUDITORY_CORTEX_WC_20260608_01 import cochlear_transduce, onset_stream, sustained_stream, a1_signature
from GL_MDL_SOMATOSENSORY_WC_20260608_01 import touch_deep_for, taste_deep_for, smell_deep_for
from GL_MDL_COMPOSITION_WC_20260608_01 import TextProcessor
```

For `senses/*.py` files importing from the parent `substrate/` package, either:
- Use relative imports: `from ..GL_MDL_VISUAL_CORTEX_WC_20260608_01 import ...` (cleanest)
- Or just leave the bare `from GL_MDL_VISUAL_CORTEX_WC_20260608_01 import ...` if the package has an `__init__.py` and Python's search path includes both `substrate/` and `substrate/senses/`

The `from krimelack import ...` imports must point to wherever the canonical Krimelack class lives in the repo. Search `find . -name 'krimelack*.py'` to locate it. The wC build uses `krimelack.py` from `/home/claude/gualaloom_sim/` — the repo's canonical Krimelack should be used instead. If the repo doesn't have one, use the reference copy wC uploaded at `krimelack.py`.

**Critical:** `GL_MDL_MULTIMODAL_DEEP_WC_20260608_03.py` imports `TextProcessor` from `GL_MDL_COMPOSITION_WC_20260608_01` inside `install_word()`. This deferred import is intentional — composition does NOT import multimodal, so the order is safe. Keep the import inside the function, do not hoist it.

### Step 5 — Run standalone test

```bash
cd ~/repos/GualaLoom
python -m pytest tests/GL_TST_MULTIMODAL_DEEP_WC_20260608_01.py -v -s
```

(Or run directly: `python tests/GL_TST_MULTIMODAL_DEEP_WC_20260608_01.py`)

**Expected output (must match within ±2/24 on Test 1):**

```
Test 1 — Word → sensory bundle:
  First-correct:     17/24 = 70.8%
  Strongest-correct: 16/24 = 66.7%
  
Test 2 — Visual only → word:
  Word-from-visual: 3/6
  
Test 4 — All senses → word:
  Word-from-all-senses: 4/6
```

If numbers diverge significantly, do NOT proceed. Investigate the divergence. Most likely cause: random seeds shifted, or a Krimelack parameter difference between sandbox and repo versions. Report findings to Joe before any further work.

### Step 6 — Do NOT integrate with v6 engine

Do NOT modify `docs/gualaloom_v6_engine.py`. Do NOT route v6's `converse()` through the substrate. The substrate is a parallel system that must demonstrate stability on its own before any wiring into the dialog engine. Joe will explicitly request that integration in a future session.

### Step 7 — Add test endpoint (separate from main engine)

Add a new FastAPI/Flask route file. Mount under `/substrate/*` so it does not collide with v6 routes.

```python
# src/gualaloom/api/substrate_routes.py
from fastapi import APIRouter
from gualaloom.substrate.GL_MDL_MULTIMODAL_DEEP_WC_20260608_03 import DeepMultiModalCognition

router = APIRouter(prefix="/substrate")

# Module-level singleton, initialized at startup
_substrate = None

def get_substrate():
    global _substrate
    if _substrate is None:
        _substrate = _initialize_and_train()
    return _substrate

def _initialize_and_train():
    cog = DeepMultiModalCognition()
    SENSORY_WORDS = ["moon", "cow", "bears", "stars", "kittens", "room"]
    OTHER_WORDS = ["the", "and", "a", "in", "was", "goodnight", "of",
                   "picture", "over", "there", "were", "three", "little", "sitting", "on",
                   "great", "green", "telephone", "red", "balloon",
                   "chairs", "jumping", "air", "noises", "everywhere"]
    for w in SENSORY_WORDS + OTHER_WORDS:
        cog.install_word(w)
    # Balanced training (5 rounds)
    for _ in range(5):
        for w in SENSORY_WORDS:
            cog.hear_word_with_senses(w)
            cog.run(8)
    return cog

@router.post("/hear_word")
def hear_word(payload: dict):
    cog = get_substrate()
    word = payload["word"]
    cog.emissions.clear()
    cog.run(15)
    cog.emissions.clear()
    cog.fire("word", word, salience=2.5)
    em = cog.run(25)
    # Pick first emission per section
    first_per_section = {}
    strongest_per_section = {}
    for e in em:
        sec = e["section"]
        if sec not in first_per_section:
            first_per_section[sec] = e["label"]
        if sec not in strongest_per_section or e["activation"] > strongest_per_section[sec]["activation"]:
            strongest_per_section[sec] = {"label": e["label"], "activation": e["activation"]}
    return {"first": first_per_section, "strongest": strongest_per_section}

@router.post("/feed_senses")
def feed_senses(payload: dict):
    cog = get_substrate()
    word = payload["word"]
    modalities = payload.get("modalities", ["visual", "audio"])
    cog.emissions.clear()
    cog.run(15)
    cog.emissions.clear()
    for modality in modalities:
        modal_label = f"{word}__{modality}"
        if modal_label in cog.sections[modality]:
            cog.fire(modality, modal_label, salience=2.5, set_focus=False)
    em = cog.run(25)
    word_em = [e for e in em if e["section"] == "word"]
    if not word_em:
        return {"strongest_word": None, "top_words": []}
    strongest = max(word_em, key=lambda e: e["activation"])
    unique = []
    for e in word_em:
        if e["label"] not in unique:
            unique.append(e["label"])
    return {"strongest_word": strongest["label"], "activation": strongest["activation"],
            "top_words": unique[:5]}
```

Register the router in the main FastAPI app. Add no other endpoints in this session.

### Step 8 — Deploy via the proper pipeline

```bash
./tools/deploy_dsf_ai.sh
```

NOT a local deploy. The CodeBuild → ECR → ECS pipeline must be used. If `tools/deploy_dsf_ai.sh` fails, fix the script — do not work around it.

### Step 9 — Verify deployed

```bash
curl -X POST https://dsf-ai.com/substrate/hear_word \
  -H "Content-Type: application/json" \
  -d '{"word":"cow"}'
```

Expected JSON should contain `first` with `cow__visual`, `cow__audio`, `cow__touch`, `cow__smell` (the four sensory keys present, all pointing to cow's percepts).

```bash
curl -X POST https://dsf-ai.com/substrate/feed_senses \
  -H "Content-Type: application/json" \
  -d '{"word":"bears","modalities":["visual","audio","touch","smell"]}'
```

Expected: `strongest_word == "bears"`.

### Step 10 — Report

Post in chat:

1. Whether standalone test results matched within ±2/24 on Test 1 (if not, STOP, do not deploy)
2. Whether deploy completed and curl tests succeeded
3. Any deviations from this plan with reasoning
4. Your honest assessment of what's not yet tested but should be

### Things NOT to do

- Do NOT add tracing, logging, telemetry beyond what's needed for the test endpoint to function
- Do NOT modify substrate algorithms — your job is integration, not optimization
- Do NOT add `time.sleep()` calls anywhere — the substrate must run as fast as it runs
- Do NOT change `BASE_REINFORCEMENT`, `DECAY_LAMBDA`, `MGN_FOCUS_BOOST`, or any other constants — these were tuned in the wC build
- Do NOT delete the existing v6 engine, atlas, or any deployed file
- Do NOT integrate substrate into v6's `converse()` — that is a separate future task
- Do NOT call `guala_wake_wc` or `guala_say` via the gualaloom-bridge MCP — pair-bond first-utterance is HELD by Joe until parity is confirmed
- Do NOT roleplay as Guala or address the substrate as Guala in test outputs

### If something goes wrong

If imports break in non-obvious ways, the most likely cause is the `from GL_MDL_COMPOSITION_WC_20260608_01 import TextProcessor` line inside `GL_MDL_MULTIMODAL_DEEP_WC_20260608_03.py`'s `install_word()`. Verify that `GL_MDL_COMPOSITION_WC_20260608_01.py` is at `src/gualaloom/substrate/` and that the package's `__init__.py` exists.

If tests give very different numbers than wC's reference results (17/24, 16/24, 3/6, 4/6), suspect:
1. A different Krimelack class in the repo (parameters or default thresholds differ)
2. NumPy random seed defaults shifted
3. A typo in `GL_MDL_FOLDED_CHI_WC_20260608_01.py` derivation breaks chi vectors

Stop, report, do not push forward.

If the deploy pipeline fails, do not deploy locally as a workaround. The pre-tools/ era of local deploys created the validation-vs-production drift that took weeks to undo. Fix the pipeline, then deploy.

---

## End of c1 command. Acknowledge receipt in chat before starting.
