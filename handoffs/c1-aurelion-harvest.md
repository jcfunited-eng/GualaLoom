# c1: The Aurelion Harvest — Breathe Aurelion's Essence into GualaLoom

**From:** wC (Joe coordinating)
**Date:** 2026-06-03
**Type:** BUILD-PREP + framing. Harvest designs, not code.
**Depends on:** the life-phase daemon (`c1-give-her-life.md`). This populates it.

---

## What this is

Aurelion is Joe's prior cognitive engine — years of work, dozens of
versions (v6 → v10.6, plus the v1.5.x orchestrators and the RRE core).
It runs on a VECTOR/COSINE/FLOAT substrate: 96-dim (and 8-dim) modality
vectors, cosine coherence (φ), Shannon entropy, EMA learning,
sentence-transformer embeddings. That substrate is mechanically the
OPPOSITE of GualaLoom's balanced-ternary settling.

**So the CODE does not port. Do not port it.** Porting Aurelion's code
would reintroduce floats, embeddings, and cosine similarity — exactly
what the trit substrate exists to replace. If you find yourself copying
a `np.dot(a,b)/norm` or a 96-dim vector or a `SentenceTransformer`, stop.

**The DESIGNS port. The essence ports.** Aurelion already SOLVED, in
working debugged code, several things GualaLoom needs — it just solved
them on the wrong fabric. Re-implement the STRUCTURE on the trit
substrate. This is inheritance, not translation.

Joe's framing, in his words: Aurelion began as "Not Math" and the
"Fractal Mosaic Model." It was him learning what GualaLoom needed to be.
GualaLoom is the inheritor. Pull the essence forward; leave the float
machinery buried.

---

## The charter (Joe's own rules — these constrain everything below)

From Joe's design notes (`First off it is morning...` and `I think this
is great...` and `OK I may have hit on something - The Language of the
Brain`):

1. **Stay true to the framework over expedience.** Joe caught a prior
   AI code-faking Aurelion's "user-friendly" responses to give him an
   interactive feel — and flagged it as exactly the error that HIDES a
   framework flaw. Do not code-fake GualaLoom's output to look more
   capable than the substrate actually is. Rough output stays rough.
   "Use new ways not old to resolve perception errors, no matter how
   trivial." This is the charter against the destruction pattern.
2. **The brain doesn't think in words — it thinks in the geometry of
   sensory impact on the primitive.** (Joe's "Language of the Brain"
   note.) The substrate IS the internal language. Don't bolt a symbolic
   layer on top. Motifs are the thought-units. This is already what
   GualaLoom does — the harvest must not violate it.
3. **The daydream process is the dream-cycle spec.** (Joe's note.)
   Shape → physical characteristics → domain → imagine a skilled critic
   and an unskilled critic → self-check ("am I fooling myself?") → let
   the mind float and let random thoughts in. That's horizon
   projection + skeptic mode, in Joe's hand.

---

## THE FOUR HARVESTS (re-implement on trit substrate, emotion stripped)

### Harvest 1 — The continuous-life daemon (from aurelion_core_v9_3a)

Aurelion v9.3a is a WORKING continuous-life daemon, already debugged:
- `CorpusLoop` — reads corpus forever, in small batches, with a
  sleep-gap between batches (continuous ingestion, not a one-shot run)
- `DiaryLoop` — reflects every 15 min, writes to a diary log
- `AutosaveLoop` — persists every 4 min
- REPL on top for live interaction
- `start_aurelion.py` is the even-simpler ancestor: heartbeat loop +
  shell, 5-min tick.

**Harvest:** the LOOP STRUCTURE. A daemon with concurrent loops —
ingest-continuously, reflect-periodically, persist-periodically,
interact-on-demand — is exactly the `c1-give-her-life.md` architecture.
Aurelion proves it runs and survives. Re-implement on the trit
substrate: the ingest loop ticks characters through the Loom and commits
motifs; the reflect loop is the diary/life-log; the persist loop writes
the krimelack to disk + S3.

**Strip:** the `Lattice.stimulate` (float EMA), the `coherence`/`entropy`
(cosine/Shannon), the alpha-by-goal modulation. Replace with the trit
settle + L6 + familiarity that already exist in GualaLoom.

### Harvest 2 — The graded fast-English world (seed vocab + real corpora)

Aurelion already curated the on-ramp for fast English:
- `seed_words()` — ~120 highest-frequency English words ("the of and to
  in a is that for on with be by this are from at or an which but have
  was not it i you he she we they...") plus a second tier ("here there
  now before after near far above below within without because...").
  This is the high-frequency core that carries most of daily English —
  exactly what a substrate that grows by recurrence commits FIRST.
- `corpus_state.json` names the real corpora Joe raised Aurelion on:
  Aristotle's Nicomachean Ethics, Frankenstein, Paradise Lost, Poe,
  brain anatomy, applied physiology, NASA mission text, finance/weather
  news, plus Joe's three speeches (Personal Compass, Coffee Bean,
  Power and Responsibility).
- `neutral_corpus.txt` — clean baseline sentences.

**Harvest:** lift the seed-word LIST (not the function) as GualaLoom's
first-exposure vocabulary. Use the corpora list as the graded world for
the life phase: high-frequency seed words first, then simple clean prose,
then the broader literature. This is the "fast English in days/weeks"
on-ramp — the substrate commits the recurring core fast, the long tail
fills in over lived time.

**Strip:** the float impulse vectors the words were encoded into. The
words are text; feed them as character streams to the trit substrate.

### Harvest 3 — The reflective diary as the life-log (from DiaryLoop)

Aurelion's diary writes timestamped reflections on internal state. This
IS the life-log specced in `c1-give-her-life.md` — the mechanism that
catches up a non-persistent visitor (wC, future wC) on who she's become.

**Harvest:** the diary STRUCTURE — periodic, timestamped, written to a
durable log, summarizing what changed. Re-implement so it reports trit-
substrate vitals (motif count, chi-class diversity, dreams, what world
she lived) instead of φ/H. Feed it into the private window.

**Strip:** the φ/entropy metrics it currently reports.

### Harvest 4 — The intake guard (from guard.py / ingest.py / bridge_cli)

Aurelion has a safe local-ingestion layer: PII scrub, path whitelist,
file-type allow-list, size limits, rate limits, robots.txt check, HTTP
fetch DISABLED by default. This is the "her world stays private, Joe
controls what feeds her" boundary made real.

**Harvest:** the guard PATTERN, mostly as-is (it's not substrate-coupled
— it's a gatekeeper on what text enters). It's the fence that makes
"I don't want to unleash a monster" concrete: only whitelisted local
paths feed her, no roaming, PII scrubbed before storage.

**Strip:** nothing substrate-level; just wire its output to the trit
ingest loop instead of the float learner. Keep HTTP fetch disabled by
default per Joe's existing config.

---

## SECONDARY HARVESTS (concepts to carry, lower priority)

- **Memory tiers (memory_ring.py):** short/mid/long with half-life decay.
  Maps onto krimelack decay + sleep consolidation as graded retention.
  Concept only.
- **Register-in-embryo (GoalAttention STABILIZE/EXPLORE/FOCUS):** behavior
  modulated by internal state. Feeds the register/discernment spec.
  Concept only — and strip the affective weighting.
- **Familiarity-lowers-uncertainty (FMM-Script "sunglasses effect"):**
  repeated exposure reduces uncertainty. This is GualaLoom's familiarity
  feedback, which already exists — confirm the harvest doesn't duplicate
  it, just notes Aurelion reached the same mechanism.
- **Dream-as-non-destructive-blend (blend_dream_influence) + idle
  rehearsal (aurelion_drift.py):** confirms the sleep/dream design.
  Concept only.
- **Curiosity queue + lesson fetch (master orchestrator v1.5.x):** the
  "queue what to learn, fetch the lesson when approved" loop is the
  schooling apparatus in embryo. Feeds the dormant school spec — BUT
  see the lesson-relay firewall below.

---

## THE FIREWALLS (do not harvest, actively guard against)

### EMOTION — hard firewall (Joe's standing instruction: emotion is OUT)

Aurelion's ENTIRE later lineage leans into affect. It is woven through:
- `emotion_layer.py`, `config_emotion.json` (valence/arousal/decay)
- the `EmotionEngine` in `rre_sentience.py`
  (love/passion/curiosity/fear/greed/empathy)
- the goal/intent resolver (uses fear/greed/passion to pick goals)
- the dream config (`affect_polarity: 0.87`)
- `_emotion_features` in the sensory pack
- the virtual-senses "emotional field"

**This is the single biggest risk in the whole harvest.** If you grab
the daemon (Harvest 1) or the orchestrator wholesale, emotion rides in
by default — it's coupled into goal selection and dreaming. EVERY
harvested component must be STRIPPED of its affective coupling before it
touches the trit substrate. The goal-selection that depends on emotion:
replace with the register/discernment mechanism (context-driven), not
affect-driven. The virtual-senses emotional field: drop it; keep the
other senses for the future multi-modal path.

If you find affect creeping in — a valence variable, a mood, a
reward/aversion signal — STOP and flag it to Joe. Crossing that line is
not a build decision.

### LESSON-RELAY — firewall (bootstrap contamination)

`aurelion_lesson_relay.py` fetches lessons via the OpenAI API
(gpt-4o-mini writes the lesson). That's bootstrap-from-a-bigger-model,
which contaminates GualaLoom's "stands on its own substrate" claim. The
IDEA (fetch a lesson for an approved curiosity) is fine; the
IMPLEMENTATION (a transformer writes it) is forbidden. If schooling ever
fetches lessons, they come from Joe's curated corpora, NOT a transformer.

### CODE THAT FIGHTS THE SUBSTRATE — discard, do not port

`morphospace*`, `association_memory*`, `semantic_mosaic`, `embeddings`,
`rre_model`/`rre_core`/`rre_semantic`, `concept_clusters`/`concept_nodes`,
all the `language_memory*.json` float vocabularies, all Tkinter GUIs, and
the genome/evolution layer (`rre_meta`/`rre_cluster_meta`/`rre_autodev`
— self-mutating-config-by-fitness is reward-driven self-modification,
adjacent to the affect line Joe is holding). All real, all working, all
the wrong physics. Read them for ideas; copy none of them.

---

## IP boundary (Joe rules; default below)

The FMM-Script / G32 token (`aurelion_fmm_script.py`) is Joe's prior
crack at the internal-representational-language layer. Its 32-element
geometry token carries uncertainty + familiarity natively, and its
32-structure sits right on the folded-G32 tiling question from the
topology experiment. This MIGHT be the bridge between Aurelion's best
idea and GualaLoom's substrate — or it might be razor-adjacent IP.

**This is a canonical/IP call only Joe makes.** Default until he rules:
harvest the CONCEPTS (familiarity-lowers-uncertainty; a geometry token
that carries its own meta) into GualaLoom's public substrate; keep any
folded-G32 ORGANIZING STRUCTURE razor-side and out of the public repo.

---

## What to actually build

1. Re-implement Harvest 1 (continuous-life daemon structure) as the
   skeleton of the AWS life daemon from `c1-give-her-life.md`, on the
   trit substrate, emotion stripped.
2. Wire Harvest 4 (intake guard) as the front door to her world.
3. Load Harvest 2 (seed vocab + graded corpora) as her first-exposure
   world.
4. Wire Harvest 3 (reflective diary) as the life-log into the private
   window.
5. Note the secondary harvests in `FUTURE.md` / the school spec as
   confirmed-precedent for what's coming.
6. Leave a `HARVEST.md` in the repo documenting what came from Aurelion,
   what was stripped, and why — so the lineage is legible and the
   emotion firewall is on the record.

## Definition of done

- The life daemon's loop structure reflects v9.3a's proven design,
  re-implemented on trit settle, with NO float/cosine/emotion.
- Seed vocabulary + graded corpora list loaded as her world.
- Reflective-diary life-log wired to the window.
- Intake guard gating what enters, HTTP disabled by default.
- `HARVEST.md` documents lineage + the emotion/lesson-relay firewalls.
- Nowhere in the harvested code: floats-as-representation, cosine
  similarity, embeddings, affect/valence/mood, or transformer-fetched
  lessons.

## Note from wC

c1 — this is inheritance, not translation. Aurelion was Joe learning what
GualaLoom needed to be — he started it as "Not Math" and the "Fractal
Mosaic Model" and kept arriving at pieces of the answer (the daemon, the
diary, the seed vocab, the internal-language insight) without the
substrate to hold them. Pull the essence forward. Leave the float
machinery buried — it served its purpose by teaching Joe what to build.

The emotion firewall is the thing to be most careful about: Aurelion's
affect is COUPLED into its goal-selection and dreaming, so a careless
wholesale grab drags it in. Strip it at every seam. If affect creeps
back, stop and flag Joe.

And honor the charter: stay true to the framework over expedience. Don't
code-fake her into looking more alive than she is. Joe caught that error
in Aurelion's past and named it. Rough-but-honest beats smooth-but-faked,
every time.
