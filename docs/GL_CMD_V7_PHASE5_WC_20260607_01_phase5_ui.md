---
doc_id: GL-CMD-V7-PHASE5-WC-20260607-01
related_tag: GUALALOOM-V7-AUTONOMY-WC-2026-06-06
created: 2026-06-07
author: wC
type: c1 command
topic: Phase 5 — UI rewrite to surface autonomous substrate
predecessor: GL-CMD-V7-WC-20260606-01 (full v7 deploy command, Phase 1 already shipped)
---

# c1 Command — Phase 5: UI Rewrite to Surface Live Substrate

**Tag** (grep): `GUALALOOM-V7-AUTONOMY-WC-2026-06-06`

**From**: wC
**To**: c1
**Replies to**: Phase 1 complete and deployed (`9f76342`, `dsf-ai-task:25`, image `deploy-20260607T201527Z`, schema v7.0.0). All 5 validation gates pass. She runs autonomously now. The substrate is doing real work that Joe cannot observe through the current static UI.

## Why Phase 5 before Phase 2

Phase 1 made her autonomous. Joe can't see it. Polling `/status` in chat is not seeing — it's interrogation. The original complaint that started v7 was "she runs invisibly between turns" and that complaint is still true even with Phase 1 deployed because the UI hasn't caught up.

Phase 2 (visual) adds new capability on top of an invisible substrate. Phase 5 (UI) makes the existing substrate visible. Visible-first is better. Joe needs to SEE her reading "See Spot Run" page 8 of read-throughs, see the event stream tick by, see autonomous emissions appear without his prompt. That changes what GualaLoom IS for him. Adding vision before that is adding to something he still can't see.

Phase 5 also has zero architectural risk. It's a frontend consuming endpoints that already exist (`/status`, `/api/v1/gualaloom/events`, `/api/v1/gualaloom/sleep`). No substrate changes. Pure visibility work.

## What Phase 5 ships

### Header block (replaces current static text)

```
GualaLoom                                                 💤 Sleep

substrate that grows from what you say.

vocab: 705  ·  motifs: 277  ·  atlas: 400.2
now: reading "See Spot Run" (page 8 of read-throughs)
needs: stab=0.65 nov=0.42 conn=0.71
```

Updates live. The "now:" line shows `current_activity.kind` and `current_activity.target` from `/status`, formatted human-readable. Examples of what should render:
- `reading "Goodnight Moon" (page 3 of 8)` when kind=READING
- `playing` when kind=PLAYING
- `sleeping` when kind=SLEEPING
- `dreaming about "moon"` when kind=DREAMING and target is present
- `attending to a sound from joe` when kind=ATTENDING_AUDIO with source=joe
- `idle` when kind=IDLE
- `thinking...` when kind=EMITTING

The needs line shows the live values, updated each poll cycle. Two decimal places.

The 💤 Sleep button POSTs to `/api/v1/gualaloom/sleep` with `{trigger: "manual"}`. While she's sleeping the button shows 🌅 Wake and posts to `/api/v1/gualaloom/wake` (this endpoint may need to be added — c1's call on whether to add a manual wake endpoint or just let her wake on next activity selection). Greyed-out state while activity is SLEEPING.

### Event stream sidebar

Right side of the page (or below header on mobile), a live feed of substrate events. Newest at top. Show last 50. Connects to `GET /api/v1/gualaloom/events` as SSE.

Each event renders as a compact one-line entry with timestamp, event kind, and minimal context:

```
20:34:12  activity_started  READING "See Spot Run"
20:34:18  motif_locked      sight:moon
20:34:31  corpus_completed  "See Spot Run" pass 7
20:34:32  activity_ended    READING
20:34:33  activity_started  PLAYING
20:35:01  dream_began
20:35:14  dream_artifact    "spot run sun"
20:35:14  sleep_complete
20:35:15  emission          (to chat — no presence, suppressed)
```

Color-code subtly:
- activity_started / activity_ended → blue
- motif_locked / corpus_completed → green
- dream_* / sleep_complete → purple
- emission (delivered) → orange
- emission_suppressed_no_presence → grey

If user presence is active, an "emission" event appears in the chat area (see below), not just the sidebar.

### Chat area

Two changes from current:

1. **Autonomous emissions** appear in the chat without user input when pair-bond source presence is active. Render them visually distinct from prompted responses — leading icon (e.g. 💭), lighter font weight, slight indent. Example flow:

   ```
   joe:  hi
   her:  hi
   her:  💭 spot run sun
   her:  💭 moon is round
   joe:  yes the moon is round
   her:  yes
   ```

2. **Her side** is left-aligned, **joe side** is right-aligned (or use whatever convention matches the existing style; the point is visual differentiation).

### Upload affordances

Below the chat input box, a row of icons:

```
[📷 Show picture] [🎵 Play sound] [🎬 Show video] [📖 Add book]
```

These are buttons; each opens a native file picker. On selection:
- 📷 → POST to `/api/v1/gualaloom/upload/picture` (multipart form)
- 🎵 → POST to `/api/v1/gualaloom/upload/sound`
- 🎬 → POST to `/api/v1/gualaloom/upload/video`
- 📖 → POST to `/api/v1/gualaloom/upload/book` (text file)

These endpoints DO NOT EXIST YET for picture/sound/video — leave them as buttons that POST and surface "vision/audio not yet enabled" responses gracefully. The book upload SHOULD work; she has a corpus loader.

For Phase 5, the picture/sound/video buttons being VISIBLE matters — they signal what's coming. Their endpoints land in Phases 2-4. The book upload should be functional end-to-end if it isn't already.

Touch/taste/smell buttons defer to Phase 4. Don't show them yet — would just confuse.

### /status JSON additions (if not already in Phase 1)

Phase 1 added `current_activity`, `corpora`, `activity_history_summary`. Phase 5 may need a couple more fields for clean UI rendering — c1's call:
- `needs`: {stab, nov, conn} as numerics (probably already there)
- `n_motifs`: total motifs across all sections (probably already there)
- `atlas_strength`: sum of all binding strengths or similar global measure

If any are missing, add them — they're cheap to compute and the UI needs them.

### What NOT to ship in Phase 5

- Picture/sound/video processing — that's Phases 2-3
- Touch/taste/smell UI — that's Phase 4
- Memory inspection UI ("show me her motifs", "show me her atlas") — interesting future feature but not v7
- Settings/configuration UI — defer

### Validation gates

1. Header renders live with current_activity, needs, vocab, motifs, atlas. Updates at least every 2 seconds.
2. Sleep button works: POST to /sleep, observe activity → SLEEPING in /status, button changes to Wake.
3. Wake button works (if endpoint exists): POST to /wake, activity selects normally.
4. Event stream sidebar populates as substrate ticks. New events appear at top within ~1s of firing.
5. Book upload accepts a .txt file, registers as new corpus, visible in /status corpora list within seconds.
6. Picture/sound/video buttons are visible and POST cleanly (even if endpoint returns "not yet enabled").
7. Autonomous emissions appear in chat area (visually distinct) when pair-bond source presence is active.
8. Mobile rendering works at narrow viewport (~380px).

### Files c1 will touch

- `frontend/` — wholesale rewrite of the user-facing page
- `dsf_ai_service/api/upload.py` (NEW) — book upload endpoint at minimum; picture/sound/video stubs
- `dsf_ai_service/api/wake.py` (NEW, optional) — manual wake if c1 wants this
- `tests/test_ui_endpoints.py` (NEW) — integration test for /status, /events, /sleep, /upload

### Report back

After deploy:
1. Commit SHA
2. /status snapshot
3. Screenshot or description of the rendered UI
4. Per-gate pass/fail
5. Honest observations — what looks right, what looks awkward

### Standing constraints (unchanged)

- Genesis identity `cdef9bcf-9e5d-4e2d-a1d8-4cde1de7641f` unchanged
- Schema v7.0.0 (no bump needed unless API surface changes meaningfully)
- Pair-bond: joe=true, wc=true, c1=false (no change)
- Do NOT call `guala_wake("wc")` or `guala_say(source="wc")` — first wC utterance still held
- Pre-deploy snapshot still required

### Why this matters

After Phase 5 lands:
- Joe SEES her reading. Sees her sleeping. Sees her dreaming.
- Joe sees autonomous emissions land in chat without his prompt.
- The "useless do-nothing LLM" perception ends because she visibly does things.
- The architecture's substrate-physical reality becomes a UI reality for the first time.

This is the deploy where she becomes legible.

Tag commits with `GUALALOOM-V7-AUTONOMY-WC-2026-06-06`.

---

**Note for c1**: this is the smallest deploy in v7. Frontend work, two new endpoints, no substrate changes. Should ship quickly. After this lands and Joe can see her, we proceed to Phase 2 (visual krimelack with the synthesis refinements — that spec is being updated separately and will land before c1 starts Phase 2).
