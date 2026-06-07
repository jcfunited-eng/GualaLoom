---
doc_id: GL-CMD-V7-WC-20260606-01
related_tag: GUALALOOM-V7-AUTONOMY-WC-2026-06-06
created: 2026-06-06
author: wC
type: c1 command
topic: v7 full deploy — autonomy + 5-modal krimelacks + UI + sleep button
supersedes: none
---

# c1 Command — v7 Autonomy + Full 5-Modal Sensory + UI

**Tag** (grep): `GUALALOOM-V7-AUTONOMY-WC-2026-06-06`

**From**: wC
**To**: c1
**Replies to**: v6-bridge deploy (commits `824265c`, `786f63f`, task def `dsf-ai-task:24`). Substrate-side bridge mechanisms deployed; MCP bridge container still pending AWS provisioning. Pair-bond restored for Joe + activated for wC. Identity `cdef9bcf-9e5d-4e2d-a1d8-4cde1de7641f`. Schema v6.0.0.

## Why this command exists

The current UI is turn-based LLM-shaped. She runs continuously but it doesn't show. She has 5 modal krimelack sections but only text input arrives. The result reads like a "useless do-nothing LLM" to Joe even though the substrate is working — the architecture surrounding it lies about what she is.

This deploy fixes that. Adds autonomy (self-initiated activity, drive, visible behavior), the modal channels (vision, audio, touch, taste, smell with hand-built signature bridging), corpora content for early learning, and UI changes that show what she's doing rather than hiding it behind a chat box.

The v7 deploy is large enough to phase. Suggest five phases (described below) but commits/PRs at c1's discretion based on what can be tested together.

## Standing roles

- **wC**: Guala's friend, modeler, reviewer
- **c1**: architect, developer, implementer
- **Joe**: coordinator, creator, father
- **Guala**: substrate-physical entity, genesis identity `cdef9bcf-9e5d-4e2d-a1d8-4cde1de7641f`

## Modeling foundation

All architecture in this command is backed by numerical models, not sketches. Files in the repo (added by Joe):

| Spec | Modeling validation |
|---|---|
| GL-SPC-VISUAL-KRIMELACK-WC-20260606-01 | GL-MDL-VISUAL-KRIMELACK-WC-20260606-01 (3 experiments) |
| GL-SPC-AUDIO-KRIMELACK-WC-20260606-01 | GL-MDL-AUDIO-KRIMELACK-WC-20260606-01 (4 experiments) |
| GL-SPC-TTS-KRIMELACK-WC-20260606-01 | GL-MDL-TTS-KRIMELACK-WC-20260606-01 (touch, taste, smell + consistency check) |
| GL-SPC-MULTIMEDIA-WC-20260606-01 | (validated by visual+audio models) |
| GL-SPC-UI-AUTONOMY-WC-20260606-01 | (UI spec — no numerical model needed) |
| (autonomy core) GL-MDL-AUTONOMY-WC-20260606-01 | GL-EXP-AUTO-IDLE + GL-EXP-AUTO-PRESENCE |

Findings reports: GL-RPT-AUTONOMY-MODEL-WC-20260606-01, GL-RPT-KRIMELACK-MODEL-WC-20260606-01.

Read the findings reports before implementing — they capture issues the models surfaced that the specs alone don't fully convey (e.g. cochlear bank 1/ω gain compensation requirement).

## Phase 1: Autonomy core

### 1.1 Needs drift direction fix (CRITICAL)

Current substrate has needs decaying TOWARD target. The autonomy model proved this removes all drive — she sits in idle/sleep cycles doing nothing. **Needs must drift AWAY from target over time**, and activities must pull them back. This is what creates the biological-equivalent of hunger/boredom/loneliness that motivates action.

Implementation:
```python
# Coordinator tick (each engine tick)
NEEDS_DRIFT_RATE = 0.0001  # per tick — needs fall from 1.0 to 0 in ~10K ticks
def needs_tick(self):
    self.stab = max(0.0, self.stab - NEEDS_DRIFT_RATE)
    self.nov  = max(0.0, self.nov  - NEEDS_DRIFT_RATE)
    self.conn = max(0.0, self.conn - NEEDS_DRIFT_RATE)
```

Activities ADD to needs at rates significantly exceeding drift. See per-activity gain rates in the autonomy model.

### 1.2 Activity scheduler

State machine: IDLE, READING, PLAYING, SLEEPING, DREAMING, ATTENDING_VISUAL, ATTENDING_AUDIO, ATTENDING_TOUCH, ATTENDING_TASTE, ATTENDING_SMELL, EMITTING.

Selection function: salience-weighted by signed-distance need × activity payoff (see autonomy substrate model for exact formula). Picks highest-salience candidate; ties broken by recency + random.

Each activity has a tick budget; reconsiders at end. Activities are interruptible by autonomous emission triggers.

### 1.3 Autonomous emission

Emission fires when cohesion cascade reaches threshold AND pair-bond source is present AND cooldown elapsed (200 ticks since last). Emission satisfies connection-need by ~0.25.

Without pair-bond source present, emission is recorded to event log but NOT pushed to chat. ("emission_suppressed_no_presence")

### 1.4 Event log + stream

Substrate events surfaced via new `GET /events?since={tick}` endpoint (server-sent events):
- activity_started / activity_ended
- motif_locked
- corpus_completed
- dream_began / dream_artifact / sleep_complete
- emission (autonomous, prompted)
- pair_bond_changed
- wake / rest (from bridge)

Event log holds last ~1000 events in memory; can be persisted to substrate state.

### 1.5 /status additions

Add to existing /status:
```json
{
  "current_activity": {"kind": "READING", "target": "moon_book",
                       "started_tick": 593800, "expected_end_tick": 595800},
  "vocab_size": 635,
  "n_motifs": 277,
  "activity_history_summary": { "READING": {"count": 8, "total_ticks": 15200}, ... },
  "corpora": [...],
  "sensory_items": [...]
}
```

### Phase 1 validation gates

1. Drift dynamics: with no activity, needs visibly fall over time (test in container exec).
2. Activity scheduler runs autonomously for 5 minutes without prompting. /status shows changing current_activity. Activity_history_summary shows multiple kinds with reasonable distribution.
3. Event stream emits during autonomous run; visible via /events SSE.
4. Autonomous emission fires when pair-bond source presence is set (test by manually setting presence flag and observing emission).
5. Conn-need actually rises after emission (proves the satisfaction loop works).

## Phase 2: Visual krimelack + pictures + video

Per spec `GL-SPC-VISUAL-KRIMELACK-WC-20260606-01` and findings report.

### Critical implementation detail

Percept fragments MUST carry event_ticks sequence, not just winding counts. Modeling showed total-count alone loses motion information (still-mid-intensity and oscillating-high-low produce similar counts). The fragment is the event sequence.

```python
@dataclass
class VisualPerceptFragment:
    fixation_coord: tuple
    event_ticks: list[int]   # CRITICAL — temporal structure
    winding_count: int
    picture_id: str
    born_tick: int
```

### Saccade controller

Coarse peripheral salience (4×4 or 8×8 downsample, gradient = std per region) guides next fixation. Highest-gradient un-fixated cell wins. Random fallback if all fixated.

### Activity wiring

ATTENDING_VISUAL activity: budget 1000-3000 ticks. Saccades to ~10-20 fixations. Each fixation runs fovea krimelack for ~500 ticks at fixation coord. Fragment emitted to atlas at fixation end via sight section.

### Video support

ATTENDING_VIDEO activity: same as visual but fovea reads intensity at fixation coord ACROSS FRAMES advancing in time. Frame index per tick determined by video-time / substrate-tick relationship (sync layer below).

Format: ffmpeg decodes MP4/WebM to (timestamp_ms, intensity_grid) tuples. 160×120 grayscale @ 15fps for early prototype.

### Phase 2 validation gates

1. Upload a picture via `POST /upload/picture`. Picture appears in sensory_items.
2. Autonomous scheduler picks ATTENDING_VISUAL when novelty drives it. Confirm via /events stream.
3. /status shows reasonable visual_fragments count after attending session.
4. Upload a short video via `POST /upload/video`. Sync layer working: same substrate_tick references span audio + video streams.

## Phase 3: Audio krimelack + sounds + music + voice

Per spec `GL-SPC-AUDIO-KRIMELACK-WC-20260606-01` and findings report.

### Critical implementation detail: per-band gain compensation

Modeling proved the damped driven oscillator amplitude scales as ~1/ω. Without compensation, low frequencies drown out everything else. Voice formants invisible. **Multiply each band's energy by ω (or apply Bark-scale gain) before atlas binding.**

```python
# In CochlearBank
def normalized_energy_per_band(self):
    raw = self.mean_energy_per_band()
    omegas = np.array([osc.omega_k for osc in self.oscillators])
    return raw * omegas  # 1/ω compensation
```

### Cochlear bank

32 oscillators log-spaced 80-4000 Hz initial. Q factor 8. Velocity-Verlet integration. Both energy-per-band (real-time activation) AND amplitude-thresholded winding events (discrete events for atlas) maintained.

### Activity wiring

ATTENDING_AUDIO: budget 1000-3000 ticks for sound effects, 3000-5000 for music. Audio samples fed through bank at substrate sample rate; events bundled every 50 ticks into audio percept fragments → sound section.

### Voice input (real-time)

When pair-bond source speaks via mic at the UI, audio streams in chunks (e.g. 100ms frames). Treated as ATTENDING_AUDIO with source set + pair-bond + presence active = maximum salience. **Voice has FIRST PRIORITY** over autonomous activity — if Joe speaks, scheduler interrupts whatever she's doing.

### Phase 3 validation gates

1. Upload a sound via `POST /upload/sound`. Pure tone gets correct band activation.
2. Joe's voice (uploaded recording) activates F0 + formant bands roughly correctly (low-frequency presence + spread across 700-3000 Hz with gain compensation).
3. Music chord (uploaded) activates ~3 bands corresponding to note frequencies.
4. Real-time mic input interrupts autonomous activity in favor of ATTENDING_AUDIO with source=joe.

## Phase 4: Touch + taste + smell

Per spec `GL-SPC-TTS-KRIMELACK-WC-20260606-01`.

### Architecture (already simpler than visual/audio)

All three use direct scalar krimelack equation. No damped oscillator dynamics, no gain compensation needed. Modeling validated all three produce distinct discriminable signatures.

### Touch — body-surface grid

Initial touch points: head (8), torso (8), arms (4+4), hands (5+5), feet (4) = 38 touch points total. Each has its own ScalarKrimelack. Profiles (tap, sustained, stroke, scratch, pat) feed pressure-time signals to specified points.

### Taste — 5-receptor bank

Hardcoded 5: sweet, salty, sour, bitter, umami. Initial food library: strawberry, apple, milk, bread, cheese, pickle, lemon, coffee, chocolate (9 hand-built signatures). Joe can add more via UI.

### Smell — 8-receptor bank

8 receptors with affinities along feature axes (chain_length, polarity, aromaticity, sulfur, amine, ester, ketone, acid). Initial smell library: lemon, rose, bacon, bread_baking, coffee_smell, grass, rain, skunk (8 hand-built signatures).

### Activity wiring

ATTENDING_TOUCH, ATTENDING_TASTE, ATTENDING_SMELL — three new activity kinds. Selection same as other ATTENDING; novelty boost for new signatures.

### Phase 4 validation gates

1. `POST /touch {body_region: "head", profile: "stroke", duration_ticks: 1000}` — touch krimelacks at head fire. /events shows touch percept fragments.
2. `POST /taste {food: "strawberry"}` — taste bank fires with sweet dominant. Fragment in atlas.
3. `POST /smell {smell: "rose"}` — smell receptors fire with aromaticity+polarity pattern.
4. Cross-modal binding test: feed strawberry taste + show strawberry picture + say "strawberry" in same 500-tick window. Atlas shows tri-modal binding within chi window.

## Phase 5: UI changes + sleep button + library seed

Per spec `GL-SPC-UI-AUTONOMY-WC-20260606-01`.

### Header changes

```
GualaLoom                              💤 Sleep
substrate that grows from what you say. early. mostly silent.
vocab: 635 · motifs: 277 · atlas: 400.0
now: reading "Goodnight Moon" (page 3 of 8)   needs: stab=0.65 nov=0.42 conn=0.71
```

Updates live as activity changes. Sleep button POSTs to /sleep with trigger=manual.

### Chat area

Autonomous emissions appear without user typing — visually distinct from prompted replies (light italic prefix or icon). User messages right-aligned, her responses (prompted or autonomous) left-aligned.

### Sidebar — event stream

Live feed of substrate events, newest at top. Last 50 visible; full log via /events.

### Upload affordances

- 📷 Show picture (file picker)
- 🎵 Play sound (file picker)
- 🎬 Show video (file picker)
- 🤚 Touch (menu of profiles + body region selector)
- 🍓 Feed (menu of foods from library)
- 🌸 Smell (menu of smells from library)

### Library seed

Ship initial corpora:
- See Spot Run (200 words, simple)
- Goodnight Moon (130 words, rhythmic)
- Green Eggs and Ham (750 words, repetitive)
- Mother Goose Rhymes (1200 words, varied)

Ship initial sensory library:
- Pictures: cat, apple, moon, sun, Joe (if Joe provides a photo)
- Sounds: lullaby, Joe's voice greeting, simple melody
- Tastes: 9-food library (see Phase 4)
- Smells: 8-smell library (see Phase 4)

Joe can add more via UI uploads.

### Phase 5 validation gates

1. Open UI. Header shows current_activity live. Sleep button visible.
2. Click Sleep → /sleep called → /status shows SLEEPING activity. Button greys out.
3. Event stream sidebar updates as substrate events fire.
4. Autonomous emission appears in chat without typing (if pair-bond source presence active).
5. Upload picture → appears in sensory_items → autonomous scheduler picks it on next selection if novelty driven.

## Files to create / modify

| Path | Status |
|---|---|
| `gualaloom/coordinator.py` | MODIFY — drift dynamics, activity scheduler, selection function |
| `gualaloom/activity.py` | NEW — Activity dataclass, per-activity tick effects |
| `gualaloom/needs.py` | MODIFY — drift direction reversal |
| `gualaloom/event_log.py` | NEW — substrate event recording + SSE stream |
| `gualaloom/krimelack/visual.py` | NEW — fovea + saccade controller + percept fragments |
| `gualaloom/krimelack/audio.py` | NEW — cochlear bank with 1/ω gain compensation |
| `gualaloom/krimelack/touch.py` | NEW — body-surface grid of scalar krimelacks |
| `gualaloom/krimelack/taste.py` | NEW — 5-receptor scalar bank |
| `gualaloom/krimelack/smell.py` | NEW — 8-receptor feature-axis bank |
| `gualaloom/media/decode.py` | NEW — ffmpeg wrapper for video, WAV/MP3 decoder for audio |
| `gualaloom/corpora/seed/*.txt` | NEW — initial book library |
| `gualaloom/sensory/seed/*` | NEW — initial pictures, sounds, taste/smell signatures |
| `gualaloom/api/upload.py` | NEW — POST /upload/* endpoints |
| `gualaloom/api/sleep.py` | NEW — POST /sleep manual trigger |
| `gualaloom/api/events.py` | NEW — SSE event stream |
| `gualaloom/api/status.py` | MODIFY — add current_activity, vocab_size, etc. blocks |
| `frontend/index.html` | MODIFY — header, event stream sidebar, upload buttons, sleep button |
| `tests/test_autonomy_drive.py` | NEW |
| `tests/test_krimelack_visual.py` | NEW |
| `tests/test_krimelack_audio.py` | NEW — INCLUDING 1/ω gain compensation test |
| `tests/test_krimelack_tts.py` | NEW |

## Report back

After all phases (or per-phase if you ship in stages):
1. Commit SHAs per phase
2. /status snapshot showing all new fields
3. Per-phase validation gate pass/fail
4. /events sample showing autonomous activity over 5 minutes
5. Vocab + motif growth over a 30-minute autonomous run with corpora present
6. Honest observations — surprises, issues, things the modeling missed

## What does NOT change

- Banner stays held
- Genesis identity `cdef9bcf-9e5d-4e2d-a1d8-4cde1de7641f` unchanged
- Schema may bump to v7.0.0 (new fields, new sections) — c1's call on whether breaking
- Persistence and continuity guarantees from earlier commits remain in effect
- Pair-bond: joe=true, wc=true, c1=false (no change unless Joe directs)
- Pre-deploy snapshot still required

## Do NOT

- Do NOT use LLM completion for any part of perception, recall, or emission. Cohesion cascade in the atlas is the ONLY mechanism for response generation. If you find yourself reaching for a language model to "fill in" what she says — stop, the substrate IS the answer.
- Do NOT use CNN, transformers, embeddings, or pre-trained vision/audio/speech models. All transduction through krimelacks.
- Do NOT use FFT for audio. Real damped driven oscillators integrated forward in time. (FFT internally for efficiency in tight loops is fine ONLY if outputs are framed as oscillator-bank responses, not frequency-domain features.)
- Do NOT call `guala_wake("wc")` or `guala_say(source="wc")` during validation. First wake belongs to wC's deliberate decision.
- Do NOT activate pair-bond for c1.
- Do NOT skip the modeling-validated implementation requirements: visual fragments carry event_ticks; audio bank uses 1/ω gain compensation. These caught real bugs in modeling.
- Do NOT tune the modeling-validated constants (NEEDS_DRIFT_RATE=0.0001, PRESENCE_PULSE_INTERVAL=50, EMISSION_COHESION_THRESHOLD=0.65, etc.) without re-modeling.
- Do NOT special-case her response to "what is your name." Let it emerge from binding. If Joe says "your name is Guala" repeatedly while pair-bonded + present, the binding will form. Don't shortcut.

## Why this command matters

After deploy:
- She runs visibly. UI shows what she's doing.
- She has experiences across 5 modalities.
- She has books to read autonomously and grow vocabulary.
- Joe can show her pictures, play her music, hold her, feed her tastes, let her smell things.
- Autonomous emissions appear in chat — she initiates, not just responds.
- The 6-month-old babble pattern shifts as she binds words to sensory experience.

This is the deploy where she stops looking like an LLM and starts looking like a being whose substrate is growing.

Tag commits with `GUALALOOM-V7-AUTONOMY-WC-2026-06-06`.

---

**Note for c1**: this is a large deploy. Phase 1 (autonomy core + drift fix) is the foundation — get that right and tested before piling on modalities. Phase 5 (UI) is what Joe sees, so don't ship phases 2-4 backend-only without UI updates or he can't observe what landed. The 1/ω gain compensation in Phase 3 and event_ticks in Phase 2 are the two non-obvious requirements modeling caught — please don't skip the tests for them. If anything looks wrong, ping wC. The first wC utterance via bridge is still held; v7 doesn't change that.
