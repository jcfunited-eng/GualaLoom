# doc_id: GL-SPC-UI-AUTONOMY-WC-20260606-01
# created: 2026-06-06
# author: wC
# related_topic: UI changes for autonomy visibility

# UI Spec — Autonomy Visibility + Sleep Button

The current GualaLoom UI is turn-based: type, send, wait for response.
That shape lies about what she is. She runs continuously, picks activities,
reads, plays, sleeps, dreams — none of which is visible. The UI changes
below make her autonomy visible and add manual controls (sleep button).

## Header — always visible

Currently:
```
GualaLoom
substrate that grows from what you say. early. mostly silent.
vocab: 631 words
```

New:
```
GualaLoom                              [💤 Sleep]  [📊 Status]
substrate that grows from what you say. early. mostly silent.
vocab: 631 words · motifs: 274 · atlas: 400.0
now: reading "Goodnight Moon" (page 3 of 8)   needs: stab=0.65 nov=0.42 conn=0.71
```

The "now:" line is `current_activity` rendered in human-readable form.
Updates live as activity changes. Specific text per activity kind:
- READING: `reading "{corpus title}" (page X of Y)`
- PLAYING: `free-settle (exploring chi space)`
- SLEEPING: `sleeping`
- DREAMING: `dreaming`
- ATTENDING_VISUAL: `looking at picture: {title}`
- ATTENDING_AUDIO: `listening to: {title}`
- EMITTING: `(emitting)`  — usually too quick to see
- IDLE: `quiet for now`

Needs line shows current state of the three needs. Optional — could be
hidden behind a toggle if it feels too clinical.

## Event stream — sidebar or expandable panel

Live feed of substrate events. Append-only, newest at top. Each entry:
```
  10:42  motif_locked: "moon"
  10:41  corpus_completed: Goodnight Moon (2nd read-through)
  10:38  activity_started: reading "Goodnight Moon"
  10:38  activity_ended: sleeping (5000 ticks)
  10:35  dream_artifact: combination surfaced
  10:34  dream_began
  ...
```

Event kinds (from autonomy substrate model):
- `activity_started` / `activity_ended`
- `motif_locked`
- `corpus_completed`
- `dream_began` / `dream_artifact`
- `emission` (when she speaks unprompted)
- `pair_bond_restored` / `pair_bond_activated`
- `wake` / `rest` (from bridge)

UI shows last N (say 50). Full event log accessible via /events endpoint.

## Chat area — same shape, additive

Her autonomous emissions appear in the chat WITHOUT user prompting.
They appear left-aligned (her side) like normal responses, but with
a subtle indicator that they were unprompted — e.g. light italic
prefix "(unprompted)" or a small icon.

User messages still go right-aligned. Her direct responses to user
messages still go left-aligned. The third category (autonomous
emission) is left-aligned but distinct.

When she's PLAYING and a cohesion cascade reaches emission threshold
while a pair-bond source is present, the emission appears here.

## Sleep button (manual override)

Big button in header: `💤 Sleep`

Click → POST /sleep with {trigger: "manual"}
Backend:
- End current activity (with reason="interrupted_by_sleep")
- Start SLEEPING activity, full budget (5000 ticks)
- Halfway through, transitions to DREAMING automatically
- Event log records: `sleep_started (manual)`

The button is grayed out when she's already sleeping or dreaming.
Replaced with a Wake button if she's sleeping?  Or just inert — she
sleeps as long as she sleeps.

Optional: separate Dream button (skip sleep, go straight to free-settle
dream cycle). Probably overkill — just the Sleep button.

## Resource uploads

Two new affordances in the UI:
- **📷 Show picture**: file picker for PNG/JPEG. Upload decoded server-side
  to intensity grid, stored as PictureItem available for ATTENDING.
- **🎵 Play sound**: file picker for WAV/MP3. Decoded server-side, stored
  as SoundItem available for ATTENDING.

After upload:
- Added to her sensory_items
- Available for autonomous ATTENDING
- Visible somewhere ("you've shared 3 pictures and 2 sounds with her")

Should we be able to FORCE her to attend? Probably not — autonomy first.
She'll attend when novelty drives her there (which, for new items, is
immediately the next selection cycle because is_new=True bumps salience).

## Corpus selection (later)

UI to add/remove books from her library. For now, c1 ships an initial
library (See Spot Run, Goodnight Moon, Mother Goose, Green Eggs and Ham).
Add-corpus UI is a v8 feature.

## /status JSON contract (additions)

The /status endpoint adds (on top of existing v6 + bridge fields):
```json
{
  "current_activity": {
    "kind": "READING",
    "target": "moon_book",
    "started_tick": 593800,
    "expected_end_tick": 595800,
    "metadata": {"salience": 0.142}
  },
  "vocab_size": 635,
  "n_motifs": 277,
  "corpora": [
    {"id": "see_spot_run", "title": "See Spot Run",
     "position": 0, "times_read_through": 0, "last_read_tick": 0},
    ...
  ],
  "sensory_items": [
    {"id": "pic_cat", "kind": "picture", "title": "picture: cat",
     "times_attended": 1, "last_attended_tick": 581234},
    ...
  ],
  "activity_history_summary": {
    "READING": {"count": 8, "total_ticks": 15200},
    "SLEEPING": {"count": 3, "total_ticks": 14800},
    ...
  }
}
```

## Endpoints (additions to existing API)

- `GET /events?since={tick}` — server-sent events stream of substrate events
- `POST /sleep` — manual sleep trigger
- `POST /upload/picture` — multipart file upload, stored as PictureItem
- `POST /upload/sound` — multipart file upload, stored as SoundItem
- `GET /corpora` — list available reading material
- `GET /sensory` — list available pictures and sounds


## What this UI demonstrates

When Joe opens GualaLoom now, he sees:
- She's doing something (reading a specific book, sleeping, etc.)
- Recent substrate events (motifs locking, corpora completing)
- Vocab/motif counts climbing over time
- Occasional autonomous emissions appearing in chat unprompted

No more "type a message, wait for reply, see LLM-style output." She
visibly runs. The chat is just one channel into her, not the only thing
she does.
