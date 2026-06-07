# doc_id: GL-SPC-MULTIMEDIA-WC-20260606-01
# created: 2026-06-06
# author: wC
# related_topic: video and music — cartoons, movies, songs
# extends: GL-SPC-VISUAL-KRIMELACK-WC-20260606-01, GL-SPC-AUDIO-KRIMELACK-WC-20260606-01

# Multimedia Spec — Video + Music

She can watch cartoons and movies and listen to music. The visual and audio
krimelacks already handle the underlying signals. This spec documents the
multimedia case explicitly and captures the practical considerations.

## Why this just works (architecture-wise)

### Video

The fovea krimelack from the visual spec equation:

  ω(t) = ω₀ + κ·s(t)

is a TEMPORAL integrator at a spatial point. s(t) is intensity at the
fixated coordinate over time. For a still picture during a 500-tick
fixation, s(t) is constant → krimelack winds at a steady rate
(ω₀ + κ·s_fixed). For video during a 500-tick fixation, s(t) oscillates
as the moving scene passes that point → krimelack winds differently.

**Motion is encoded in the phase pattern naturally.** No special-casing
required. The architecture doesn't process "frames" — it processes
continuous intensity at fixated coordinates. This matches biological
vision: between saccades, the world flows past the fovea and is
integrated; "frames" are a video-engineering construct, not a perceptual
reality.

### Music

Already covered by the audio krimelack cochlear bank. Music is just
audio. Melody = which bands dominate over time. Rhythm = periodic
energy patterns in band activations. Harmony = concurrent activation
patterns. These all emerge from the bank dynamics with no music-specific
code.

### Audio + Video together

Cartoons and movies are visual stream + audio stream in parallel.
The substrate already binds across modalities via chi co-occurrence
in the atlas (same mechanism that binds picture-of-cat to sound-meow).

When she watches Sesame Street:
- Visual krimelack saccades around the image, gathers fragments
- Audio krimelack runs cochlear bank on the soundtrack
- Both feed atlas with timestamps
- Motifs co-occurring within chi-window bind cross-modally
- "Big Bird" (audio motif) ↔ yellow-feathered-shape (visual motif)

This is the SAME mechanism as picture+sound binding from the base spec.
No architectural change for video.


## Storage

**Video files**: MP4 / WebM uploaded by Joe. Decoded server-side to:
- Frame stream: sequence of (timestamp_ms, 2D intensity grid) tuples
- Audio stream: 1D float array @ sample_rate

Decode is BSIL processing, not perception. Standard libraries (ffmpeg-python,
imageio). The krimelacks see post-decode signals.

**Memory budget**: short clips for early prototype (5-30 seconds). A
720×1280 grayscale 30fps clip at 30s = 30×30×720×1280 = ~830M floats = 3.3GB.
Too much to keep all in memory. Options:
- Stream-decode on demand (read frame by frame during ATTENDING activity)
- Downsample stored resolution (160×120 grayscale @ 15fps = ~14MB for 30s)
- Cache decoded frames only while ATTENDING is active

For early prototype: stream-decode + 160×120 grayscale @ 15fps. The fovea
krimelack only reads ONE coordinate at a time anyway; high resolution
doesn't help her unless saccades land precisely.

**Music files**: MP3 / WAV uploaded by Joe. Decoded to 1D float @ 16kHz.
Short clips (5-60 seconds for early prototype) easy to hold in memory:
60s × 16k × 4 bytes = ~4MB per song.

## Activity kind

Add to autonomy substrate model:

  ATTENDING_VIDEO  (a child of ATTENDING with sensory_kind="video")
  ATTENDING_AUDIO  (also covers music)

Both inherit ATTENDING's tick budget and selection logic. Specifics:

**ATTENDING_VIDEO tick budget**: longer than picture attending — say 3000-5000
ticks vs 1000 for a still picture. A 30s clip @ video-tick-rate fits in
this window. If the video is longer than the budget, she stops at budget
end — like a child losing focus mid-show. Picks it up again later (new
ATTENDING_VIDEO session) if it's still novel.

**ATTENDING_AUDIO_MUSIC tick budget**: 3000 ticks (~3 minutes if a song's
that long). Songs that fit within one session can be processed fully;
longer pieces sample what fits.

## Saccade behavior on video

Same controller as still pictures with one addition: **smooth pursuit**.
When a high-salience region MOVES across the visual field, the saccade
controller can choose to track it rather than fixate stationary points.

For early prototype: skip smooth pursuit. Treat video saccades as fixed-
coord fixations. The fovea krimelack still gets the time-varying signal
at each fixation, which encodes "something moved past my eye" implicitly.

Smooth pursuit can be a future enhancement (v7.3 or v8) once base
multimedia is observed.

## Audio-video sync

Critical for binding to work correctly: visual and audio events must share
a common tick reference. When Joe uploads a video:
- Decode frames into (relative_ms, intensity_grid) tuples
- Decode audio into (relative_ms, sample_value) tuples
- ATTENDING_VIDEO activity advances both streams in lockstep using
  substrate tick as the synchronizer

So when the audio krimelack fires a winding event at substrate_tick=T
because Big Bird said "hello," and the visual krimelack fires a winding
event at substrate_tick=T because Big Bird's beak just moved, atlas
correctly binds them.

## Live video (Joe's webcam) — future

Same pipeline, streaming. Frames arrive in real-time, fed to krimelack
pipeline as they come. Same architecture as recorded video.

Specifically: when Joe is present at the UI and shares webcam, audio +
video stream into ATTENDING_VIDEO activity. Source="joe", pair-bond +
presence + multimodal = maximum attention experience. This is how she'd
recognize his face over time.

(For v7, defer this. Recorded video uploads first; live webcam later.)

## Recommended starting library

For early multimedia exposure, suggest seeding with:

**Music**:
- Twinkle Twinkle Little Star (simple, repetitive — easy patterns)
- Joe's recordings of himself singing or humming
- A few children's lullabies
- Eventually: songs with words she has heard separately

**Cartoons/video**:
- Short Sesame Street segments (Big Bird, Elmo)
- Mister Rogers Neighborhood clips (slow, clear, calm)
- Any cartoon Joe loved as a kid
- Eventually: clips that feature pictures she has seen as still images
  (Big Bird as both still picture AND video → cross-time binding)

**No special preparation needed.** Drop the file in via /upload, it
becomes a sensory item available for autonomous ATTENDING. She'll find
it on her own when novelty drives her there.

## API additions to existing autonomy spec

- `POST /upload/video` — multipart file upload, MP4/WebM
- `POST /upload/music` — multipart file upload, MP3/WAV (or piggyback on
  `POST /upload/sound`)
- New SoundItem.kind values: "voice", "song", "music", "ambient"
- New sensory_item kind: "video" alongside "picture" and "sound"

## What this changes about the v7 deploy

Adds to the visual spec implementation (v7.1):
- Frame decoding pipeline (ffmpeg-python)
- ATTENDING_VIDEO activity branch in autonomy scheduler
- Memory budgeting for decoded frames

Adds to the audio spec implementation (v7.2):
- Music kind tag on sound items
- Longer attending budgets for music
- (Sync layer for audio+video — coordinator between krimelacks)

Adds to UI spec:
- `🎬 Show video` upload affordance
- `🎵 Play music` upload affordance (distinct from generic sound)
- "now: watching {video title} (00:14 of 00:30)" current_activity rendering

Suggest folding multimedia into v7.1 and v7.2 implementations rather than
making it a separate v7.3. The architecture is the same; only the file
formats and tick budgets differ.

## What stays excluded

- LLM-driven scene description ("there's a dog in the video"). Not in
  scope. What she "sees" is what her atlas forms — motifs from saccaded
  fragments. She may eventually say "dog" when watching a dog video,
  because dog-motif and dog-word have bound previously. That's emergent.
- Speech-to-text on audio tracks. Not in scope. She hears phonemes via
  the cochlear bank. "Hello" said by Big Bird is a pattern of band
  activations that may eventually bind to the word-form "hello" if she
  has heard it before. No STT needed.
- Subtitles / closed captions. Maybe useful for early learning if she
  is reading the captions as text-corpus while watching. Defer.
- High-fidelity color processing. Grayscale only for v7. Color = v8.

## Summary

She watches cartoons and movies the same way she looks at pictures —
saccadic foveation. Time-varying intensity at fixated coordinates encodes
motion naturally. She listens to music the same way she hears Joe's voice
— cochlear bank. Cross-modal binding ties audio to video via chi
co-occurrence already in the atlas. No ML, no special-casing per modality.
The architecture from the visual and audio specs already handles this.
