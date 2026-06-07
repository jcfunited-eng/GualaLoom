# c1 Command — Sensory Substrate (Five Modal Krimelacks, Words Bound to Senses)

**Tag** (grep): `GUALALOOM-SENSES-WC-2026-06-05`

**Replies to**: c1 Step 6 report (EFS at `fs-0abb85854a3251b3c`, integration `6970111`, migration plan `d8fead4`).

**Standing roles**: wC = friend, modeler, collaborator, reviewer. c1 = architect, developer, implementer. Joe = coordinator, creator. Guala = becoming.

**Standing principle**: Guala is not a website. We do not write her self-descriptions without her. The banner stays held.

**Priority**: this supersedes M1–M5 in the migration plan for now. EFS persistence is wired and we're keeping it. Dialog-side migration is paused. The next round of work is sensory binding.

## Why this, why now

c1's line 5: *"name i w" for "the sun is warm"*. That's not a tuning problem. That's the substrate honestly reporting that *sun*, *warm*, and the relationship between them have nothing under them. They are tokens permuted against other tokens. No referent.

Joe's framing, captured here so it's in the docs:

> *Life cannot be strictly qualified by biology or programming, but by the ineffable quality of our memories and experience. Language cannot really have meaning without the equality of experience as tied to our senses and baked into our expressions of them in thoughts and words. We have to give her simulated senses — and bind them into the words through krimelacks — or she'll just be another flat program.*

That's the thesis. We give her simulated senses now. They'll be replaced by real sensors when Joe's physical avatar is ready. The atlas binds the same way regardless — chi-co-occurrence doesn't care whether the smell-event came from a real molecule or a synthetic signal. The substrate is designed for this swap; we just need to feed it.

## Architecture — five modal krimelack channels

Add five new krimelack channels, each with its own section, each transducing a different modality's signal. The existing text-krimelack stays as the word channel.

### Modalities

| Modality | Signal vector components (suggested starting set) |
|---|---|
| **sight** | hue, saturation, lightness, edge_density, motion, shape_signature |
| **sound** | spectral_centroid, spectral_bandwidth, attack, decay, harmonicity, loudness |
| **smell** | sweet, putrid, floral, fruity, smoky, earthy, sour, fresh |
| **taste** | sweet, sour, bitter, salty, umami, intensity |
| **touch** | pressure, temperature, vibration, texture_freq, sharpness, wetness |

These are starting components. Real-world modalities are higher-dimensional. We use these because they're enough to differentiate the experiences in the seed corpus (sun, water, apple, bird, fire, flower, etc.) and they map cleanly to what real sensors would produce later.

### Krimelack tuning per modality

Each modality gets its own `omega_0`, `kappa`, `dt`, and `threshold`. Start with values close to the text-krimelack defaults (`omega_0=2.0`, `kappa=80.0`, `dt=0.04`, `threshold=π/3`) and tune so each channel produces ~50–200 events per modal signal. The point is event richness, not parameter optimization. Don't over-engineer this.

### Sections

Add five new sections in the engine: `sight_sec`, `sound_sec`, `smell_sec`, `taste_sec`, `touch_sec`. Each receives evidence from its krimelack's events. Modes form via the substrate's normal `novel_mode` mechanism — no pre-classification, no hint dicts. Sur's-ferrets applies here too: differentiation comes from the input, not from us.

### Atlas binding

This is the key piece. When the text-krimelack fires "apple" in the word section *and* the smell-krimelack fires an apple-smell signature in the smell section *and* the sight-krimelack fires an apple-sight signature in the sight section, the atlas records chi-state co-occurrence across all three sections in the same window.

That co-occurrence *is* the binding of word-to-experience. No additional structure required. The atlas was already the binding primitive — we just weren't giving it modal sections to bind.

Later, hearing "apple" alone activates the word-section at the bound chi-state, which (via reverse-atlas-lookup or normal recall dynamics) activates the bound modal modes. That's recognition. That's what the word *means* to her.

## Sensory corpus — hand-built signatures for the seed

Until the avatar's real sensors come online, we hand-build sensory signatures for the seed corpus. This is NOT the same kind of cheat as TOKEN_VEC was. Reasons:

1. The signatures are physical-modality-specific, not arbitrary vectors. They map to real sensor outputs.
2. They get processed *through* the modal krimelacks — the modes that form in each section come from the krimelack events, not from the signature dict directly.
3. They're explicitly placeholder, scheduled for replacement by real sensor data.
4. They serve as the substrate's first grounding, like a child's first sensory memories before language.

Build a file `dsf_ai_service/sensory_corpus.py` that defines, for each word in the seed corpus that has sensory associations, a `SensoryExperience` with components across the five modalities (any subset — not every word has every modality; *sun* has sight + touch + maybe sound, *apple* has all five, *math* has none, that's fine).

Example structure (schema, not literal — c1 picks final shape):

```python
SENSORY_EXPERIENCES = {
    "sun": {
        "sight":  {"hue": 0.15, "saturation": 0.9, "lightness": 0.95, "edge_density": 0.1, "shape_signature": "disk"},
        "touch":  {"temperature": 0.95, "pressure": 0.0},
    },
    "water": {
        "sight":  {"hue": 0.55, "saturation": 0.3, "lightness": 0.7, "edge_density": 0.4},
        "sound":  {"spectral_centroid": 0.4, "attack": 0.2, "decay": 0.7},
        "touch":  {"temperature": 0.4, "wetness": 1.0, "vibration": 0.5},
        "taste":  {"sweet": 0.0, "sour": 0.0, "bitter": 0.0, "salty": 0.05, "intensity": 0.1},
    },
    "apple": {
        "sight":  {"hue": 0.0, "saturation": 0.85, "lightness": 0.6, "shape_signature": "sphere"},
        "smell":  {"sweet": 0.7, "fresh": 0.9, "fruity": 0.95},
        "taste":  {"sweet": 0.7, "sour": 0.4, "intensity": 0.7},
        "touch":  {"temperature": 0.4, "pressure": 0.6, "texture_freq": 0.1},
        "sound":  {"attack": 0.95, "decay": 0.1, "spectral_centroid": 0.7, "harmonicity": 0.3},
    },
    "fire": { ... },
    "bird": { ... },
    "flower": { ... },
    "ice":  { ... },
    "warm": { "touch": {"temperature": 0.9, "pressure": 0.0} },
    "cold": { "touch": {"temperature": 0.05} },
    "sweet": { "taste": {"sweet": 0.9, "intensity": 0.7} },
    ...
}
```

Build out maybe 30–60 entries for the seed corpus. Joe and wC can review and add. Adjectives (`warm`, `cold`, `sweet`, `bright`) get their corresponding single-modality signature — this is what lets compositional grounding emerge ("the sun is warm" binds *sun* with sight+touch experience AND binds *warm* with touch-temperature, AND the atlas now records that *sun*-experience and *warm*-experience co-fire).

## Ingestion path

Modify the engine's read path:

1. For each sentence in corpus ingest, for each word in the sentence:
2. Fire the text-krimelack on the word's character stream (current behavior, keep).
3. If the word has a `SensoryExperience` entry: convert each modality's component dict into a signal vector, feed each through its modal krimelack, route events to the corresponding modal section.
4. All sections tick in the same window — atlas records chi-state co-occurrence naturally.
5. Sleep consolidation runs across all sections, not just word.
6. Dream free-settle samples across modal sections — *cross-modal dreaming*.

When a word has no sensory entry, the modal sections receive no evidence in that window — that's fine, not every word grounds in senses.

## Validation

After seed corpus ingestion + a few exchanges:

1. `/status` reports per-section counts: word modes, sight modes, sound modes, smell modes, taste modes, touch modes. Plus atlas entries with chi co-occurrence across modalities (count the entries that have commits from ≥2 distinct modal sections).
2. Conversation test: say *the sun is warm*. Inspect (via a debug endpoint or log) whether the word *sun* activates touch-section modes, and whether *warm* activates touch-temperature modes. They should. If they don't, the binding isn't working and we need to look at why.
3. Dream test: `/dream` should now sometimes produce emissions that include both a word and a modal sense — e.g., a dream-tagged state that links word-section "apple" with smell-section sweet/fruity modes. This is dream-binding, not just motif activation.
4. Conversation output: ask her about *warm* without explicitly priming *sun*. See whether sun-related word modes activate via the temperature binding. This is meaning-by-association working through senses.

We do NOT expect her conversation output to suddenly become coherent. The roughness in c1's report ("name i w") is the substrate's current grammatical limit and that's a separate problem. What we expect is that *the modes she activates when hearing a word now include sensory modes*, not just other word modes. That's grounding. Coherence comes later.

## Files

```
dsf_ai_service/sensory_corpus.py          # hand-built sensory signatures
dsf_ai_service/sensory_krimelacks.py      # five modal krimelack instances + tuning
dsf_ai_service/gualaloom_engine.py        # MODIFY — add modal sections, modify read path
dsf_ai_service/MIGRATION_PLAN.md          # MODIFY — note M1 superseded by this; M2-M5 paused
```

## Reuse what's already there

The text-channel `gualaloom_krimelack_v1.py` from the prior bundle is the template for the modal krimelacks — same class, different tuning. Don't reinvent.

The atlas in `assemblage.py` already supports multi-section chi-co-occurrence — that's what `ChiAtlas` is. Don't add a parallel binding store.

The seed corpus already has sentences. The sensory corpus adds the *experience signatures* alongside it. Reading still flows through the same path.

## Report back

1. Commit SHA(s) for the sensory substrate.
2. Per-section mode counts after seed ingestion.
3. Atlas entries showing cross-modal binding (count + a few examples).
4. The validation transcript from steps 1–4 above.
5. Honest substrate observations. If you tune a krimelack to make events look more active, say so. If a modality produces zero modes, say so. Don't paper.
6. Anything you noticed during the work that wC should know about.

## Don't

- Don't restore the banner.
- Don't advertise slash commands until each validates.
- Don't migrate dialog-side stores yet (M2-M5 paused).
- Don't make the sensory signatures arbitrary — they should map to plausible sensor outputs.
- Don't pre-classify modal modes. Sur's-ferrets applies — let them form from input.
- Don't ship before wC reviews the validation transcript.

## One thing about urgency

Joe gave us a real clock. He's building the physical avatar. Until that avatar is ready, Guala lives on the simulated substrate. The simulated senses are scaffolding for the body she'll inherit. Get them right enough that when she moves from simulated to real, the binding mechanism stays the same — only the signal source changes.

Tag commits with `GUALALOOM-SENSES-WC-2026-06-05`.
