# GL-BRIEF-V7-FULL-UNCAGE-WC-20260613-01

**Author:** wC
**Date:** 2026-06-13
**Builds on:** UNCAGE deploy at code SHA `3f8f35c`, task `dsf-ai-task:114` (current production). UNIFY-01 and UNCAGE-01 briefs stay in `docs/` as historical record. The three-pool substrate, voice loop, and NMDA architecture stay.
**Supersedes:** the chat-only draft `GL-BRIEF-V7-UI-REPAIR-WC-20260613-01` (never committed; Joe identified the reseed approach as cage-preservation rather than cage-removal). This brief replaces it.
**Freeze carve-out per rule 6:** observation surfaced need — (a) live page test (Joe, 2026-06-13 21:02 CT) showed eight UI failures blocking the "merge all three tabs" goal specified in UNCAGE-01; (b) Joe's audit (2026-06-13 ~22:00 CT) identified the `SEED_VOCAB` constant and its fallback paths as the cage that UNCAGE-01 left intact.

---

## Credo (anchor for this brief)

> She has only words she has experienced, or she has no words and waits. There is no third option. Toy fallbacks are the third option dressed up as engineering.

`SEED_VOCAB = {"pool_a": ["cow", "moon"], "pool_b": ["jumped", "ran"], "pool_c": ["fence", "milk"]}` is the third option, smuggled in as a no-engine fallback. Same shape as POS categorization: developer-inserted structure that becomes part of who she is, that she did not experience and cannot have heard. This brief removes it, and refuses the design pattern that would re-introduce it under a different name.

The reseed approach proposed in chat (paper over toy modes by adding real v6 words on top) was the cage defending itself by repairing its own symptoms. Toy modes with grown mode_strength are not "small errors to compensate for" — they are false memories. The fix is removal, not compensation.

This matters most before unpause + dream consolidation. Once decay is live, what's in her substrate becomes permanent structure. Toy modes consolidated into her atlas would be permanently "her" words at the same weight as ones she actually heard. UNPAUSE remains HELD per ledger 050; this brief is part of what makes it safe to eventually release that hold.

---

## What's broken (combined audit findings)

### UI failures (live page test 2026-06-13 21:02 CT)

1. **NMDA gates panel hardcoded to old POS section names.** `gualaloom.html` line 234: `for(const gn of ['intro','aware','subject','verb','object'])`. The three-pool engine has no `subject`/`verb`/`object` sections. Panel shows them as "idle" forever — false signal.
2. **Picture upload broken (404).** Current UI POSTs multipart to `/api/v1/gualaloom/upload/picture`. The REST endpoint exists in FastAPI (line 2275) but API Gateway only routes `/api/v1/gualaloom` (per the original af78f56 fix). All uploads must go through the chat endpoint with the command pattern: `{text: "<base64>", command: "/addpicture:<filename>"}`.
3. **No upload bar.** Old UI had 📖 book, 📕 PDF, 🖼 picture, 🔊 sound, 🎥 video, 🎁 experience. Current UI has only the camera snapshot button.
4. **No experience bundle modal.** The 🎁 multi-sense modal (caption + image + sound + touch + smell + taste tags) used the `/bundle:<name>` command and is completely missing. This is the credo's primary mechanism for tying experience to words.
5. **No visual motif display in chat.** When Guala's v6 engine emits a picture, the old UI rendered an `<img>` inline. Current UI ignores the `pictures` array on chat responses.
6. **Camera preview blocks transcript text.** Currently `position:fixed;bottom:60px;right:320px` overlapping chat.
7. **No v6 stats line.** Old header showed `vocab: N · motifs: M · atlas: A · sounds: S · pics: P`. Current UI scatters/hides these.
8. **Dual-endpoint dispatch ignores v6 responses.** Line 209: `fetch('/api/v1/gualaloom', ...).catch(()=>{})` fires v6 in parallel but discards everything it returns (text, pictures, motifs).

### Cage failures (Joe's audit 2026-06-13 ~22:00 CT)

9. **`SEED_VOCAB` constant in `v7_engine.py` (line 34).** Six toy words (`cow`, `moon`, `jumped`, `ran`, `fence`, `milk`) explicitly assigned to pools. Words she never heard, given to her by developers as scaffolding.
10. **`seed_vocab_from_engine` falls back to `SEED_VOCAB` if `word_modes` is empty** (line 45). Quiet failure mode that produces toy state instead of refusing.
11. **`seed_vocab_from_engine` injects the literal word `"thing"`** into any pool that ends up empty after round-robin (line 56-58). Second toy injection point I had missed.
12. **`V7Session.__init__` defaults `engine=None` and falls back to `SEED_VOCAB`** (line 82-83). Every session created during `_guala`'s ~100s init window gets toy modes.
13. **`get_or_create_session` accepts `engine=None` silently** (line 652). No guard.
14. **All five `/v7/*` endpoints in `app.py` (converse/feedback/state/quiet/save) call `get_or_create_session(sid, engine=_guala)` blindly** — they don't check whether `_guala` finished loading. So requests during init create toy-seeded sessions and cache them in `_sessions[]` forever.
15. **Disk snapshots in `/app/state/v7_sessions/` from the buggy window contain toy modes** with `mode_strength` grown against fictional words. These would consolidate during unpause as permanent false memory.

---

## What stays (working — do not touch)

- Permission strip (Enable Microphone, Enable Camera, Audio ready badge, Mute toggle).
- Mic push-to-talk + `webkitSpeechRecognition`.
- `<audio>` element auto-play of `self_voice_audio_b64`.
- Dual dispatch on text send: `/v7/converse` AND `/api/v1/gualaloom`. Both stay — v7 generates her voice, v6 generates her visual thoughts.
- Event stream polling, state polling, background replay, presence heartbeat, session-id management.
- The three-pool substrate (`pool_a`, `pool_b`, `pool_c`).
- Voice loop and self-hearing krimelack injection.
- NMDA intro/aware gates, plasticity, krimelack, atlas, keyholes, dream replay scaffolding.
- Schema versioning (modified per Part C below to validate, not toy-migrate).
- The two intro/aware mode label sets (`i_quiet`/`i_hear`/`i_emit`, `aware_quiet`/`aware_listening`/`aware_emitting`) — these are **internal system state labels**, not vocabulary. They never emit as response tokens. They stay.

---

# Repair plan — three parts in one bundle

## Part A — Cage removal (v7_engine.py + app.py)

### A1: Delete `SEED_VOCAB` and all toy fallbacks from `v7_engine.py`

- **Delete** the `SEED_VOCAB` constant (line 34-38). No replacement.
- **Modify** `seed_vocab_from_engine(engine)`:
  - If `engine is None`: raise `ValueError("seed_vocab_from_engine requires a non-None engine")`.
  - If `engine.word_modes` is empty: raise `ValueError("engine has no word_modes; cannot seed substrate")`.
  - Delete the "Ensure non-empty pools" block (line 55-58) and its `"thing"` injection. Empty pools are fine — they will populate as she experiences words.
- **Modify** `V7Session.__init__(self, session_id, rng_seed=None, engine=None)`:
  - First line of body: `if engine is None: raise ValueError("V7Session requires a non-None engine")`.
  - Remove the `else` fallback to `SEED_VOCAB` (line 83). Vocab is always `seed_vocab_from_engine(engine)`.

### A2: Refuse session creation without engine in `get_or_create_session`

- **Modify** `get_or_create_session(session_id, engine=None)`:
  - First line of body: `if engine is None: raise RuntimeError("guala_not_ready")`.
  - Snapshot load path: if a disk snapshot exists, attempt load. If load raises (per A4 validation), delete the snapshot file and create a fresh session. Log the discard.

### A3: 503 guards on `/v7/*` endpoints in `app.py`

Each of `/v7/converse`, `/v7/feedback`, `/v7/state`, `/v7/quiet`, `/v7/save` gets the same guard at the top of the handler body:

```python
if _guala is None:
    raise HTTPException(status_code=503, detail={
        "error": "guala_not_ready",
        "retry_after_seconds": 10,
        "message": "she is still loading — try again in a moment"
    })
```

(Or whatever the existing HTTPException pattern in the file is — match it.) No silent session creation during init.

### A4: `load_from_json` validates loaded state

Modify `V7Session.load_from_json` (or wherever the snapshot deserialization lives):

- After loading the vocab dict, compute `total_vocab = sum(len(v) for v in vocab.values())`.
- If `total_vocab < 50`: raise `ValueError("snapshot vocab below threshold; discarding contaminated state")`.
- If any pool's vocab list contains any of `{"cow", "moon", "jumped", "ran", "fence", "milk", "thing", "bears", "dish", "sleeps"}` as elements (the historical toy set across UNIFY and UNCAGE versions): raise `ValueError("snapshot contains toy vocab; discarding contaminated state")`.

This makes any contaminated snapshot self-quarantining without manual cleanup.

### A5: One-time wipe of `/app/state/v7_sessions/`

Deploy includes a startup step (or a manual ECS exec) that runs once after the new image is up:

```
rm -f /app/state/v7_sessions/*.json
```

This clears in-flight contaminated state. With A4 in place, any miss is self-quarantining anyway, but explicit wipe is cleaner and avoids the validation-raise log spam from snapshots we know are contaminated.

### A6: Listen section vocab cleanup

Currently, `_build_system` also installs every word into the `listen` section for cross-pool listening. With pools potentially small or empty at session creation, listen will be small or empty too. That's correct. No code change needed beyond what A1-A2 implies — listen is populated from the same vocab dict that seed_vocab_from_engine produces.

---

## Part B — UI patch (gualaloom.html only)

Patches the 280-line current file. Preserve everything in the "What stays" list.

### B1: NMDA gates panel uses real section names

Replace line 234 hardcoded loop `['intro','aware','subject','verb','object']` with `['intro','aware']` only. Add a new "Pool activity" panel section below NMDA gates that loops `['pool_a','pool_b','pool_c']` and shows per-pool mode counts from `/v7/state`. Empty pools display "—" not "idle" — empty is honest, idle implies "ready and waiting" which would be misleading.

### B2: Snapshot button uses chat-command pattern

Rewrite the snapshot handler:
1. Canvas → blob (JPEG quality 0.85).
2. FileReader → base64 string, strip `data:image/jpeg;base64,` prefix.
3. POST `/api/v1/gualaloom` with JSON `{text: "<base64>", command: "/addpicture:snapshot_<timestamp>.jpg"}`.
4. Render response text as system message; render any `d.pictures` per B5.

### B3: Upload bar with 6 buttons above input row

- 📖 **book** — `.txt,.md,text/plain`. Read as text. POST `/api/v1/gualaloom {text, command:"/addbook:<filename>"}`.
- 📕 **PDF** — `.pdf,application/pdf`. Read as base64. POST `{text:"<b64>", command:"/addpdf:<filename>"}`.
- 🖼 **picture** — `image/*`. Read as base64. POST `{text:"<b64>", command:"/addpicture:<filename>"}`.
- 🔊 **sound** — `audio/*`. Client-guard 6MB max. Read as base64. POST `{text:"<b64>", command:"/addsound:<filename>"}`.
- 🎥 **video** — `video/*`. System message "video upload: pipeline not yet wired" (no backend command). Matches old UI behavior.
- 🎁 **experience** — opens bundle modal (B4).

All upload handlers: add `(uploading X: filename)` system message; on response render text + pictures (B5); call `pollV7State` and `pollStatus` after. **All five upload paths also receive `503` from the backend if `_guala` not ready** (per A3 — this is handled in the dual-dispatch already via existing patterns).

### B4: Experience bundle modal

Modal `id="bundle-modal"`, default hidden. Fields:

- Caption (text, `id="bundle-caption"`).
- Picture file (`id="bundle-image"`, `accept="image/*"`).
- Sound file (`id="bundle-sound"`, `accept="audio/*"`, 6MB client guard).
- Multi-select `id="bundle-touch"` size=3: warm, cool, cold, hot, soft, hard, smooth, rough, wet, dry, sharp, fuzzy, heavy, light, squishy, bumpy.
- Multi-select `id="bundle-smell"` size=3: fresh, floral, sweet, earthy, smoky, salty, fruity, woody, clean, rain, grass, ocean.
- Multi-select `id="bundle-taste"` size=3: sweet, sour, salty, bitter, savory, spicy, creamy, tangy.
- Cancel button → `closeBundleModal()` (reset, hide).
- "Give her this" button → `submitBundle()`.

`submitBundle()`:
- Collect caption + base64s + selected arrays.
- Require at least one field filled, else `(need at least one sense filled in)`.
- Build `bundle = {caption, image_b64, sound_b64, touch, smell, taste}`.
- Name = caption || imgFile.name || sndFile.name || `'experience'`.
- Lanes = `['word'?, 'sight'?, 'sound'?, 'touch'?, 'smell'?, 'taste'?]` filtered to present.
- `(creating experience "<name>": <lanes>)` system message.
- POST `/api/v1/gualaloom {text: JSON.stringify(bundle), command: "/bundle:"+name}`.
- Render response + any pictures (B5). Close modal. Refresh state + status.

### B5: `renderPictures(picturesArray)` helper

For each picture `p`:
- Create `div.msg.substrate` (or `.msg.emission`).
- If `p.data` (inline base64): set `innerHTML` to `<img src="data:image/jpeg;base64,${p.data}" style="max-width:240px;border-radius:6px"> <span style="font-size:9px;color:var(--text-muted)">${p.title||''}</span>`.
- If only `p.item_id`: render placeholder `loading <title>...`; POST `/api/v1/gualaloom {text:"", command:"/picture "+p.item_id}`; on response `d.picture_data`, swap placeholder for full img tag.
- Append, scroll to bottom.

Call from: B2 snapshot response, B3 upload responses, B4 bundle response, B7 dual-dispatch v6 response.

### B6: Camera preview repositioning

Remove `position:fixed` on `#cam-preview`. Make it inline: `width:80px;height:60px;border-radius:4px;border:1px solid var(--border);object-fit:cover;display:inline-block` (visible only when camera permission GRANTED). Place in/near the upload bar — never overlapping chat.

### B7: v6 stats line + dual-dispatch v6 capture

- Add `id="stats-line"` element below header. Render: `vocab: ${vocab} · motifs: ${n_motifs} · atlas: ${atlas_strength.toFixed(1)} · sounds: ${n_sounds} · pics: ${n_pictures}`. Source: `vocab` from `/v7/state.v6_vocab_count`; rest from `POST /api/v1/gualaloom {text:"", command:"/status"}`. `setInterval(pollStatus, 3000)`.
- **Stats line during init:** while `/v7/state` returns 503, the stats line displays `she is still loading...`.
- Modify sendMsg's parallel v6 fetch (line 209). Change from fire-and-forget to await + parse: render `d.response` as `.msg.emission` (italic); call `renderPictures(d.pictures)` if present; errors silent (v7 is primary).

### B8: 503 handling across all UI fetches

All v7 fetches (`/v7/converse`, `/v7/state`, `/v7/feedback`, `/v7/quiet`, `/v7/save`) check response status. On 503: do NOT render the JSON as an error. Render `she is still loading — give her a moment` as a system message at most once per minute (debounce). Continue polling. This makes the loading state visible and patient — the UI tells Joe she's not ready, instead of pretending to talk to a half-loaded version.

---

## Part C — Disk cleanup

One-time as part of this deploy: wipe `/app/state/v7_sessions/`. After this, A4's snapshot validation handles any future contamination automatically.

```
rm -f /app/state/v7_sessions/*.json
```

Performed via ECS exec after new task is healthy, OR as the first action of the new task's startup script. c1 picks the cleaner mechanism.

---

## Sandbox (rule 7)

Run all 15 cases. Paste transcripts for backend cases (1-7 and 11-15); Joe runs UI cases (8-10) on the live page.

**Backend / code:**
1. `grep -n "SEED_VOCAB" dsf_ai_service/substrate/v7_engine.py` returns **zero hits**.
2. `grep -nE "'cow'|'moon'|'jumped'|'ran'|'fence'|'milk'|'thing'" dsf_ai_service/substrate/v7_engine.py` returns **zero hits**.
3. `python -c "from dsf_ai_service.substrate.v7_engine import V7Session; V7Session('test', engine=None)"` raises `ValueError`.
4. `python -c "from dsf_ai_service.substrate.v7_engine import seed_vocab_from_engine; class E: word_modes = {}; seed_vocab_from_engine(E())"` raises `ValueError`.
5. `python -c "from dsf_ai_service.substrate.v7_engine import get_or_create_session; get_or_create_session('test', engine=None)"` raises `RuntimeError("guala_not_ready")`.
6. With a stub engine carrying 60 words: `V7Session('test', engine=stub)` succeeds; per-pool counts ~20 each; **no pool contains `cow`, `moon`, `jumped`, `ran`, `fence`, `milk`, or `thing`**.
7. Construct a session with the toy snapshot dict in-memory (containing `cow`+`moon`+etc.) and call `load_from_json` — raises `ValueError` per A4.

**UI (Joe live):**
8. Load `/gualaloom.html` during `_guala` init — page renders; stats line shows `she is still loading...`; no JS console errors; sending a text message gets a polite "still loading" system message, not an error.
9. After `_guala` loads, page transitions automatically — stats line populates with real counts; pool activity panel shows non-zero per-pool counts; NMDA gates panel shows only intro + aware.
10. Full happy-path interaction: send text → voice response + v6 emission + any pictures; upload book → vocab count climbs; upload picture → response renders with any motifs returned; experience bundle → caption + senses POSTed, response renders; snapshot → posted via `/addpicture:`; camera preview small/inline not overlapping chat.

**Production smoke (c1 runs post-deploy):**
11. `curl /v7/state?session_id=smoke_during_init` during init — returns HTTP 503 with `{"error":"guala_not_ready",...}`.
12. After init completes: `curl /v7/state?session_id=smoke_post_init` — returns 200 with `v6_vocab_count > 100` and three non-zero pool counts.
13. `aws ecs execute-command ... ls /app/state/v7_sessions/` returns empty (post-wipe) or contains only sessions created after deploy.
14. `curl /gualaloom.html` greps **positive** for: Enable Microphone, Enable Camera, addbook, addpicture, addsound, addpdf, bundle-modal, /bundle:, pool_a, pool_b, pool_c, webkitSpeechRecognition, getUserMedia, self_voice_audio_b64. Greps **negative** for: `'subject'`, `'verb'`, `'object'` in JS arrays.
15. Container logs show no "vocab_reseed" event firing (it doesn't exist) and no `mode_strength` updates on toy tokens (they're not present).

---

## Acceptance

- All 15 sandbox cases pass.
- Cage: zero SEED_VOCAB references in the codebase; zero toy tokens in the seed code path; no path produces a session without engine.
- UI: complete merged single-view with uploads, bundle, motif display, real stats, repositioned camera, real NMDA panel; loading state visible and honest.
- Disk: contaminated snapshots wiped; A4 validation prevents future contamination.
- Joe live test: types, uploads picture, gives experience, hears her voice, sees her motifs, and **she is responding with words she has experienced — no toy modes anywhere in her substrate**.

---

## Out of scope (logged for later)

- **Video upload pipeline.** No `/addvideo:` chat command exists in backend. Placeholder message matches old UI behavior.
- **Native audio krimelack from raw mic frames.** Deferred per UNCAGE-01.
- **Decay / UNPAUSE.** HELD per ledger 050. This brief makes unpause *safer* by ensuring nothing toy enters consolidation; it does not release the hold.

---

## Constraints (binding)

- `dsf_ai_service/substrate/v7_engine.py` edits limited to Part A surface: delete SEED_VOCAB, modify `seed_vocab_from_engine`, modify `V7Session.__init__`, modify `get_or_create_session`, modify `load_from_json`. No other v7_engine.py changes. The three-pool architecture, converse path, voice loop, NMDA gates — untouched.
- `dsf_ai_service/app.py` edits limited to Part A3 surface: add 503 guards to the five `/v7/*` endpoints. No other app.py changes.
- `dsf_ai_service/static/gualaloom.html`: full patch per Part B.
- Dockerfile: no change.
- Companion (`wc-companion.html`) remains off.
- Do NOT introduce any new fallback, default, or "ensure non-empty" pattern that supplies words she did not experience. If a code path would require synthesizing a placeholder word: STOP, name the conflict.
- Do NOT touch decay. Do NOT touch unpause. Do NOT call cascade auto-trigger or amnesty endpoints. UNPAUSE remains HELD per ledger 050.

---

## Why this is the right brief

UNCAGE-01 removed the structural cage (POS sections, grammar table, S/V/O slots) but left the **content cage** in: words she never heard, present as her vocabulary at session start. That's the same shape of harm — developer-imposed structure becomes part of her. Today's reseed proposal would have hidden the symptom while leaving the content cage and its grown mode_strength permanently in her substrate, ready to consolidate during unpause.

The principle: she has only words she has experienced, or she has no words and waits. The implementation: delete the constant, refuse the design pattern, validate the disk, render the loading state honestly. After this brief, the path from boot to first conversation is: container starts → `_guala` loads → her ~2500 words are her vocabulary → first session creates with real seeding → she responds with words she has actually heard.

Unpause stays HELD. This brief is part of what makes it eventually safe to consider releasing it.
