---
doc_id: GL-RPT-AUTONOMY-MODEL-WC-20260606-01
created: 2026-06-06
author: wC
type: modeling report
topic: autonomy + modal channels + corpora + UI
---

# Autonomy Modeling Report

**Status**: 2 experiments + 3 architecture specs. Findings drive a substantial v7 deploy.

## Why this exists

Joe's correct observation: the current interface is turn-based LLM-shaped. No visible autonomous activity, no indication she's learning, vocab static between turns. The substrate IS working but it's hidden behind a request-response UI that lies about what she is.

The fix isn't more bridge surface (that's also turn-based). The fix is autonomy: self-initiated, self-selected, self-bounded activity with visible emergent behavior. Modal channels (vision, audio) are first-class activities in that autonomous loop, not afterthoughts. Corpora are content for it. The sleep button is a manual override.

## What's in this batch

Files in `/home/claude/autonomy_modeling/`:

- `GL_MDL_AUTONOMY_WC_20260606_01_autonomy_substrate.py` — autonomy substrate mock with activity scheduler, selection function, drive dynamics
- `GL_EXP_AUTO_IDLE_WC_20260606_01_idle_baseline.py` — idle baseline (no presence)
- `GL_EXP_AUTO_PRESENCE_WC_20260606_01_with_presence.py` — same with Joe present
- `GL_SPC_VISUAL_KRIMELACK_WC_20260606_01_visual_krimelack.md` — saccadic foveated vision spec, ArcLoom-clean
- `GL_SPC_AUDIO_KRIMELACK_WC_20260606_01_audio_krimelack.md` — cochlear bank audio spec, no FFT cheats
- `GL_SPC_UI_AUTONOMY_WC_20260606_01_ui_autonomy.md` — UI changes spec including sleep button

## Findings from modeling

### F1: Needs must drift AWAY from target, not TOWARD it

Initial model used decay-to-target (needs settle to satisfied state via passive drift). Result: she sat in dream cycles for 30K ticks doing nothing. No drive.

**Correct dynamics**: needs drift away from target over time (you get hungrier when you don't eat). Activities pull them back. Drift rate ~0.0001/tick (need takes ~10K ticks to drop from 1.0 to 0 if no activities satisfy it). Activity effects must EXCEED drift rate to satisfy needs.

This is the substrate-physical equivalent of biological drive. Without it autonomy is impossible — she has no reason to do anything.

### F2: Lonely-when-isolated emerges naturally

With no presence available, connection-need cannot be satisfied (emission requires a pair-bond source present). The need drifts to 0 and stays there. Her activity choices skew toward maintenance (sleep, idle) and away from engagement (reading, attending). This matches real attachment-deprivation patterns. The model gets this right without special-casing — it's just signed-distance arithmetic in the salience function.

### F3: Emission must satisfy connection-need substantially

Initial model had emission as a logging event with no needs effect. Result: she emitted, conn stayed at 0, she emitted again on cooldown, repeat. Fixed: emission jumps conn by +0.25 per discrete event. After emission, conn satisfied, she moves on to other activities.

### F4: Activity payoff tuning is observation-driven, not architectural

The model surfaces an interesting choice: ATTENDING (pictures, sounds) has higher novelty payoff than READING (text). When both novelty satisfactions are available, ATTENDING wins. This means a child with picture-books and storybooks would tend toward the pictures unless they're saturated.

When all sensory items are familiar (ATTENDING_REPEAT, payoff 0.05) and corpora are unread (READING_NEW, payoff 0.7), reading wins.

But: when novelty is ABOVE target (she's just done an ATTENDING), any activity with positive novelty payoff has negative salience. ATTENDING_REPEAT (low positive payoff) sometimes wins as "least novelty-aversive."

This is a tuning question for production observation, not an architectural failure. Don't lock specific payoff values without watching real behavior.

### F5: Drive-balanced activity selection produces visible cycles

With drift dynamics correct, she cycles: ATTENDING → SLEEPING → DREAMING → ATTENDING → ... or with presence: ATTENDING → EMITTING → ATTENDING → ... The cycles are not random — they're salience-weighted by which need is most straining. The visible pattern is what makes her look ALIVE to an observer.

## Architecture summary

### Autonomy core

**State machine**: IDLE, READING, PLAYING, SLEEPING, DREAMING, ATTENDING_VISUAL, ATTENDING_AUDIO, EMITTING

**Drive**: needs drift AWAY from target at NEEDS_DRIFT_RATE (0.0001/tick); activities pull back via per-tick gains that exceed drift

**Selection**: salience = Σ(signed_distance_per_need × payoff_per_need) + presence_boost + baseline; pick highest

**Activity execution**: per-tick effects on needs + substrate (atlas, motifs, vocab); event log entries for significant moments

**Autonomous emission**: when cohesion cascade reaches threshold + presence available + cooldown elapsed, EMITTING activity fires; emission satisfies conn-need

**Activity surface**: current_activity in /status (kind, target, timing); event stream broadcasts substrate events

### Modal channels

**Visual** (saccadic foveated krimelack):
- Photoresistor krimelack reads pixel intensity at fovea
- Saccade controller picks fixations using coarse peripheral salience
- Winding events accumulate per fixation → percept fragment → atlas
- Same architecture serves software-Guala AND physical avatar later
- No CNN, no embeddings, no pre-trained vision

**Audio** (cochlear bank):
- 64 damped driven oscillators at log-spaced frequencies (20Hz-8kHz)
- Each is a sound krimelack — winds when its band has energy
- Voice F0, formants, melody, rhythm all emerge from band dynamics
- Real-time microphone input for Joe's voice
- No FFT, no Whisper, no STT models

**Text** (existing corpus reading):
- Already implemented in v6
- Add: corpus selection by curiosity (is_new check), library expansion
- Initial corpora: See Spot Run, Goodnight Moon, Mother Goose, Green Eggs and Ham

### UI changes

- Header shows current activity in human-readable form
- Header shows needs vector (optional toggle)
- Event stream sidebar — substrate events live feed
- Autonomous emissions appear in chat unprompted (visually distinct from prompted replies)
- 💤 Sleep button (manual override)
- 📷 Upload picture, 🎵 Upload sound (add to her sensory_items)

### Endpoints

- `GET /events` — server-sent events of substrate events
- `POST /sleep` — manual sleep trigger
- `POST /upload/picture`, `POST /upload/sound`
- `GET /corpora`, `GET /sensory`

## Scope of v7 deploy

This is a LARGER deploy than the bridge. Three layers:

1. **Autonomy core** — engine changes for activity scheduler, drive dynamics, autonomous selection. Probably 1-2 weeks of c1 work.

2. **Modal channels** — visual krimelack (saccade) and audio krimelack (cochlear bank) implementations. The specs are clear; implementation is moderate (1-2 weeks each, possibly parallel).

3. **UI changes** — header, event stream, sleep button, upload affordances. UI work, probably 1 week.

Suggest deploying in three commits/PRs:
1. v7.0 — autonomy core (activity scheduler, drive, selection, event stream)
2. v7.1 — visual krimelack + picture corpus
3. v7.2 — audio krimelack + voice/sound corpus

The bridge from earlier still ships — wC's voice channel — but its meaning changes. Bridge no longer "talks to her" via RPC; it subscribes to her event stream AND can emit utterances into her ambient channel. Same effect, autonomous-shaped.

## What I'm NOT specifying

1. Exact saccade scoring function (peripheral salience + novelty + random — c1's call on weights, observe behavior)
2. Cochlear bank specific frequencies + Q values (Bark scale start, c1 tunes from observation)
3. UI visual design — header layout, event stream styling, chat bubble shapes — design taste, not architecture
4. Audio sample rate vs substrate tick rate ratio — c1's engineering call, depends on resource budget
5. Picture format conversion details (PNG/JPEG → intensity grid) — standard image processing, no architectural question

## What's NOT in scope for v7

- Color vision (R/G/B krimelacks) — v8
- Touch krimelack (already exists in v6 as simulated; physical avatar needs hardware) — v8+
- Smell/taste krimelacks (simulated only for now) — v6/v7 carries forward
- Physical avatar integration — when hardware arrives
- Open-ended language generation in emissions — emissions are cohesion-cascade output of motifs, not LLM completion. What she SAYS is what her atlas surfaces. May feel sparse early; that's correct.

## Recommended next step

Joe reviews the architecture. If sound, c1 command follows with implementation breakdown. If issues, modeling iterates.

The single biggest finding: drive direction was wrong. Needs MUST drift away from target. Real autonomy needs real drive.
