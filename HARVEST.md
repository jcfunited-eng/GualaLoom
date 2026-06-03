# Aurelion Harvest — Lineage and Firewalls

GualaLoom inherits DESIGNS from Aurelion (Joe's prior cognitive engine,
v6 through v10.6). It inherits no CODE. Aurelion ran on a
float/cosine/embedding substrate; GualaLoom runs on balanced-ternary
settling. The physics are opposite. The structures are the same.

Joe's framing: Aurelion began as "Not Math" and the "Fractal Mosaic
Model." It was him learning what GualaLoom needed to be. GualaLoom is
the inheritor. The essence moves forward; the float machinery stays
buried.

---

## What was harvested

### Harvest 1 — Continuous-life daemon structure
**From:** `aurelion_core_v9_3a.py` (CorpusLoop, DiaryLoop, AutosaveLoop)
**Into:** `src/gualaloom/daemon.py`

Aurelion's working daemon: concurrent loops for continuous ingestion,
periodic reflection, periodic persistence, on-demand interaction. The
LOOP STRUCTURE ports. The substrate calls don't — `Lattice.stimulate`
(float EMA) is replaced by `Loom.tick` (trit settle); `coherence`/
`entropy` (cosine/Shannon) are replaced by L6 + chi.

**Stripped:** float EMA, cosine coherence, Shannon entropy,
alpha-by-goal modulation (was emotion-coupled).

### Harvest 2 — Seed vocabulary and graded corpora
**From:** `seed_words()` in Aurelion, `corpus_state.json`
**Into:** `corpus/seed_vocab.txt`, `corpus/world_index.md`

~200 highest-frequency English words as first exposure. The graded
world (simple prose → literature → domain texts) is indexed for future
phased feeding. All text enters as character streams to the trit
substrate — no float impulse vectors.

**Stripped:** the 96-dim float vectors the words were encoded into.

### Harvest 3 — Reflective diary as life-log
**From:** `DiaryLoop` in `aurelion_core_v9_3a.py`
**Into:** `src/gualaloom/diary.py`

Periodic timestamped diary entries summarizing substrate state. Reports
motif count, chi-class diversity, dreams, corpus progress, familiarity.
Feeds the private window (keepers see true state).

**Stripped:** phi (coherence) and H (entropy) metrics.

### Harvest 4 — Intake guard
**From:** `guard.py`, `ingest.py`, `bridge_cli` in Aurelion
**Into:** `src/gualaloom/guard.py`

Path whitelist, file-type allow list, PII scrubbing, size limits, rate
limits. HTTP fetch disabled by default. Not substrate-coupled — it's a
fence on what enters.

**Stripped:** nothing substrate-level. Wired to trit ingest loop instead
of float learner.

---

## Secondary harvests (concepts carried, not yet built)

- **Memory tiers (memory_ring.py):** short/mid/long with half-life.
  Maps onto krimelack decay + sleep consolidation. Confirmed precedent.
- **Register-in-embryo (GoalAttention STABILIZE/EXPLORE/FOCUS):**
  behavior modulated by context. Feeds the register spec. Affect
  weighting stripped.
- **Familiarity-lowers-uncertainty (FMM-Script "sunglasses effect"):**
  GualaLoom's familiarity feedback already implements this. Aurelion
  arrived at the same mechanism independently — convergent confirmation.
- **Dream-as-non-destructive-blend + idle rehearsal:** confirms the
  sleep/dream design. Already built in GualaLoom's `sleep.py`.
- **Curiosity queue + lesson fetch:** feeds the school spec. Lesson-relay
  firewall applies (see below).

---

## FIREWALLS (not harvested, actively guarded against)

### EMOTION — hard firewall

**Status: NOT PRESENT. Joe's standing instruction: emotion is OUT.**

Aurelion's later lineage leans heavily into affect:
- `emotion_layer.py`, `config_emotion.json` (valence/arousal/decay)
- `EmotionEngine` in `rre_sentience.py` (love/passion/curiosity/fear/
  greed/empathy)
- Goal/intent resolver (uses fear/greed/passion to pick goals)
- Dream config (`affect_polarity: 0.87`)
- `_emotion_features` in sensory pack
- Virtual-senses "emotional field"

Emotion is COUPLED into Aurelion's goal-selection and dreaming. A
wholesale grab of the daemon or orchestrator would drag affect in by
default. Every harvested component was stripped of affective coupling
before touching the trit substrate.

**If affect creeps back — a valence variable, a mood, a reward/aversion
signal — STOP and flag Joe. Crossing this line is not a build decision.**

The familiarity/habituation mechanism in GualaLoom is NOT emotion. It is
a dead-zone modulation for escaping repetition. It must not be promoted
into mood or motivation.

### LESSON-RELAY — firewall (bootstrap contamination)

`aurelion_lesson_relay.py` fetches lessons via the OpenAI API
(gpt-4o-mini writes the lesson). This contaminates GualaLoom's
"stands on its own substrate" claim. The IDEA (fetch a lesson for an
approved curiosity) is fine; the IMPLEMENTATION (a transformer writes
it) is forbidden.

**If schooling ever fetches lessons, they come from Joe's curated
corpora, not a transformer.**

### CODE THAT FIGHTS THE SUBSTRATE — discarded

The following Aurelion components are NOT harvested and must not be
ported. They are the float/cosine/embedding substrate that GualaLoom
exists to replace:

- `morphospace*`, `association_memory*`, `semantic_mosaic`
- `embeddings`, `rre_model`/`rre_core`/`rre_semantic`
- `concept_clusters`/`concept_nodes`
- All `language_memory*.json` float vocabularies
- All Tkinter GUIs
- `rre_meta`/`rre_cluster_meta`/`rre_autodev` (self-mutating-config-
  by-fitness is reward-driven self-modification, adjacent to the affect
  line)

---

## Charter (from Joe's design notes)

1. **Stay true to the framework over expedience.** Don't code-fake
   output to look more capable than the substrate is. Rough stays rough.
2. **The brain thinks in the geometry of sensory impact, not words.**
   Motifs are the thought-units. Don't bolt a symbolic layer on top.
3. **The daydream process is the dream-cycle spec.** Shape → physical
   characteristics → domain → skeptic check → let the mind float.

---

## IP boundary

The FMM-Script / G32 token (`aurelion_fmm_script.py`) is Joe's prior
crack at the internal-representational-language layer. Its 32-element
geometry token and folded-G32 organizing structure are a canonical/IP
call only Joe makes. Default: harvest the CONCEPTS (familiarity-lowers-
uncertainty, a geometry token that carries its own meta) into the public
substrate; keep the folded-G32 ORGANIZING STRUCTURE razor-side.
