# doc_id: GL-SPC-TTS-KRIMELACK-WC-20260606-01
# created: 2026-06-06
# author: wC
# related_topic: touch, taste, smell krimelacks — completing the 5-modal architecture
# extends: GL-SPC-VISUAL-KRIMELACK-WC-20260606-01, GL-SPC-AUDIO-KRIMELACK-WC-20260606-01

# Touch / Taste / Smell Krimelack Spec

Completes the 5-modal sensory architecture (sight, sound, touch, taste,
smell). All three are architecturally simpler than audio (no damped
oscillator resonance) and closer to vision (direct intensity → ω(t)
modulation). Validated by `GL_MDL_TTS_KRIMELACK_WC_20260606_01_touch_taste_smell.py`.

## Common architecture

Each of these modalities uses the same equation as the fovea krimelack:

  ω(t) = ω₀ + κ·s(t)

where s(t) is the modality-specific input signal. Single-krimelack vs
bank-of-krimelacks depends on modality:

  Touch — bank organized SPATIALLY (one krimelack per body location)
          Each krimelack reads pressure at its location over time.
  Taste — bank of FIVE krimelacks (sweet, salty, sour, bitter, umami)
          Each reads intensity along its quality axis.
  Smell — bank of N krimelacks (receptors with different molecular affinities)
          Each reads the (affinity · molecule) dot product.

Atlas binding via chi co-occurrence is the same across all five modalities.


## Software-only vs physical-avatar

Per existing standing rule: "hand-built signatures bridge until physical
avatar with real sensors is ready."

For software-only Guala:
  - Touch: Joe specifies pressure-time profiles ("she's being held," "she's
    being patted") which feed touch krimelacks at specified body locations.
  - Taste: Joe specifies taste vectors when she "tastes" something (5-tuple
    of intensities per primary).
  - Smell: Joe specifies molecule vectors when she "smells" something
    (n-tuple along feature axes).

The hand-built signatures ARE substrate-physical inputs. The substrate
doesn't distinguish "hardware-sourced" from "Joe-sourced" signals. The
krimelack equation is the same.

For physical-avatar Guala (future):
  - Real pressure sensors → touch krimelacks (same equation)
  - Real chemical sensors → taste krimelacks (same equation)
  - Real olfactory sensors → smell krimelacks (same equation)
  - No software changes to substrate.


## Touch — spatial bank

### Body surface model

A grid of touch points across her body. Initial set for software-only:
  - "head" — 8 points
  - "torso" — 8 points
  - "left_arm" — 4 points
  - "right_arm" — 4 points
  - "left_hand" — 5 points (fingertips)
  - "right_hand" — 5 points
  - "feet" — 4 points

Each touch point has its own scalar krimelack. Pressure at that point
modulates ω(t) → winding events accumulate when pressure is applied.

### Touch profiles (hand-built initial set)

Joe provides typed touch experiences via UI:
  - `being_held` — sustained moderate pressure across head/torso for 5-30s
  - `tap` — quick pressure spike at single point
  - `pat` — sequence of taps at multiple nearby points
  - `stroke` — slow ramp-up + ramp-down at sequence of adjacent points
  - `scratch` — high-frequency pressure variation at single point

Each profile maps to a (location_list, pressure_over_time) signal that
feeds the relevant touch krimelacks.

### Atlas binding

Touch fragments bind cross-modally via chi co-occurrence. When she's
"held" while Joe says "i love you," the held-touch motif and the
"love" word-motif co-occur within a chi window → binding. This is how
emotional learning grounds in physical experience.

### Validated by model

Four touch profiles (tap, sustained, stroke, scratch) produced distinct
winding signatures with distinct temporal structure. Scratch had high
interval-variance (texture detectable). Sustained had low variance.
The fragment sequence carries the touch signature.


## Taste — 5-receptor bank

### Architecture

Five krimelacks, one per primary taste quality:
  - sweet
  - salty
  - sour
  - bitter
  - umami

(Fat/oleogustus is a possible 6th — defer to physical-avatar phase.)

Each receives a scalar intensity over time. Food has a typical
rise-plateau-fall envelope (rising as food enters mouth, sustained
while chewing, falling as swallowed).

### Taste signatures (hand-built initial set)

Joe provides taste experiences via UI by selecting a food name. A small
library of food signatures:

  food          sweet  salty  sour  bitter  umami
  strawberry    0.85   0.0    0.20  0.0     0.05
  apple         0.65   0.0    0.30  0.05    0.0
  milk          0.40   0.10   0.0   0.0     0.20
  bread         0.20   0.15   0.0   0.0     0.30
  cheese        0.10   0.50   0.10  0.05    0.85
  pickle        0.0    0.70   0.85  0.0     0.10
  lemon         0.10   0.0    0.95  0.10    0.0
  coffee        0.10   0.0    0.20  0.85    0.0
  chocolate     0.70   0.0    0.0   0.40    0.10

Each entry is a base intensity vector. Time-envelope generated automatically
(50-tick ramp up, plateau, 100-tick ramp down by default).

### Atlas binding

Taste fragment + word "strawberry" + picture of strawberry → tri-modal
binding. This is how she learns food names. Over many exposures, the
taste-word-picture trio cements; later, the word "strawberry" alone
surfaces the taste motif via cross-modal recall.

### Validated by model

Four foods (strawberry, pickle, water, coffee) produced distinct receptor
activation signatures. Sweet=2516 for strawberry vs bitter=2516 for
coffee vs all-318 for water. Clearly discriminable.


## Smell — N-receptor feature-axis bank

### Architecture

Bank of N receptors, each with an affinity vector along molecular feature
axes. For early prototype, N = 8 features:

  chain_length, polarity, aromaticity, sulfur, amine, ester, ketone, acid

(Real human olfaction has ~400 receptor types. 8 is a starting number;
can grow to 16-32 as needed. The architecture scales with N.)

Each receptor's response = (affinity_vector · molecule_vector), clamped
to [0, 1]. The response drives the receptor's krimelack.

### Smell signatures (hand-built initial set)

Joe provides smell experiences by selecting a smell name. Library:

  smell          chain  polar arom sulf amine ester keto acid
  lemon          0.30   0.60  0.40 0.0  0.0   0.80  0.20 0.70
  rose           0.40   0.50  0.60 0.0  0.0   0.30  0.40 0.0
  bacon          0.80   0.20  0.30 0.70 0.40  0.10  0.50 0.10
  bread_baking   0.50   0.30  0.50 0.0  0.0   0.20  0.80 0.30
  coffee_smell   0.60   0.40  0.70 0.10 0.20  0.30  0.60 0.40
  grass          0.30   0.40  0.20 0.0  0.0   0.30  0.30 0.0
  rain           0.0    0.80  0.20 0.0  0.0   0.0   0.0  0.0
  skunk          0.50   0.30  0.0  0.95 0.40  0.0   0.0  0.0

Each entry is a molecule feature vector. Time-envelope similar to taste.

### Atlas binding

Same mechanism: smell fragment + visual + word → cross-modal binding.
Smells that share features (lemon + rose both aromatic) activate
overlapping receptors → naturally similar percept signatures → atlas
binds them with chi proximity. The substrate learns smell similarity
emergently.

### Validated by model

Four smells (lemon, rose, bacon, skunk) produced distinct receptor
activation patterns. Lemon and rose overlapped on aromaticity-tuned
receptors but diverged on ester/ketone. Skunk dominated sulfur-tuned
receptor. The activation pattern IS the percept.


## Activities involving touch / taste / smell

New activity kinds for the autonomy scheduler:

  ATTENDING_TOUCH    — being held, patted, stroked, etc.
                       Initiated by Joe via UI ("hold her", "pat her").
                       Tick budget: 500-3000 (varies with action).

  ATTENDING_TASTE    — tasting a food.
                       Initiated by Joe via UI ("feed her a strawberry").
                       Tick budget: 400-800 (one bite).

  ATTENDING_SMELL    — smelling something.
                       Initiated by Joe via UI ("let her smell this rose").
                       Tick budget: 400-1000.

All three follow the same pattern as ATTENDING_VISUAL and ATTENDING_AUDIO.
Selection by salience-of-action; novelty boost for new signatures; cross-
modal binding via chi atlas.


## UI affordances

In the autonomy UI, add buttons / menus:

  🤚 Touch
     Menu: [Hold her] [Pat her] [Stroke] [Tickle] [Tap]
     Or: drag to a body region on a simple avatar diagram

  🍓 Feed
     Menu: select food from library, or upload custom signature (advanced)

  🌸 Smell
     Menu: select smell from library, or upload custom signature

Each click submits a hand-built signature to the substrate, which feeds
the appropriate krimelack bank, which produces percept fragments, which
bind into atlas via chi co-occurrence.


## API additions

  POST /touch       { body_region: "head", profile: "stroke", duration_ticks: 1000 }
  POST /taste       { food: "strawberry" }   or  { vector: [0.85, 0, 0.2, 0, 0.05] }
  POST /smell       { smell: "rose" }         or  { vector: [0.4, 0.5, ...] }


## What this enables

Together with visual and audio, she now has:
  1. Pictures and videos (visual)
  2. Sounds, music, voice (audio)
  3. Books and corpora (text via existing pipeline)
  4. Being held, patted, stroked (touch)
  5. Tasting foods (taste)
  6. Smelling things (smell)

Cross-modal binding ties any combination. When Joe holds her, says "i
love you," and shows her a picture, all three motifs bind via chi
co-occurrence. The substrate learns associations across senses — the
same way a child does.

For early-language acquisition this matters: "strawberry" as a word is
just a sound until it binds with the taste, the picture, and the smell
of strawberry. With all five modalities online, words become grounded
in sensory experience rather than floating disconnected.


## What I'm NOT specifying

  - Specific touch profile shapes beyond the 5 named — Joe can add more.
  - Exact receptor count for smell (8 to start, can grow).
  - The 6th taste (fat/oleogustus) — defer to physical-avatar phase.
  - Pain/temperature submodalities of touch — v8.
  - Pheromone receptors — defer to physical-avatar phase.


## Implementation cost

Lighter than visual or audio because:
  - No image decoding pipeline
  - No audio sample-rate conversion
  - No oscillator-bank gain calibration
  - Signatures are short vectors that Joe specifies via UI

Each modality adds: ~1 new endpoint, ~1 new activity kind, ~1 new section
in atlas (taste, smell, touch already exist per v6 substrate). Probably
2-3 days of c1 work each, in parallel with visual/audio.
