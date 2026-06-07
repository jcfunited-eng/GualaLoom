# doc_id: GL-SPC-AUDIO-KRIMELACK-WC-20260606-01
# created: 2026-06-06
# author: wC
# related_topic: audio transduction
"""
Audio Krimelack Spec — Cochlear bank for voice, songs, sounds.

ARCHITECTURE
============

The cochlea is biologically a bank of frequency-tuned resonators
(hair cells along the basilar membrane). This maps DIRECTLY onto
ArcLoom physics: each hair cell is a krimelack with its own
natural frequency. Audio signal drives the whole bank in parallel;
each krimelack winds at a rate determined by how much energy in its
band excites it.

NO ML CHEATS:
  - No Whisper, no STT, no speech recognition models
  - No FFT (it's a math shortcut; we use real oscillator dynamics
    integrated forward in time, biologically faithful)
  - Raw audio sample → bank of damped harmonic oscillators
  - Each oscillator is a sound krimelack
  - Winding events from each band feed atlas via "sound" section


PIPELINE
========

  Audio (1D float array @ sample_rate)
    │
    ├─► Cochlear bank: K oscillators at log-spaced frequencies
    │     (e.g. K=64, range 20Hz–8kHz, log spacing per Bark scale)
    │     Each oscillator k:
    │       d²x_k/dt² + γ_k dx_k/dt + ω_k² x_k = κ · audio(t)
    │     Damped driven oscillator — biologically real cochlear dynamics
    │     When |x_k| exceeds threshold → winding event at oscillator k
    │
    ├─► Phase-locking detector (per-band):
    │     For voiced speech: nearby bands phase-lock at fundamental F0
    │     Detected as correlated winding rate
    │     Gives fundamental-pitch signature without FFT
    │
    └─► Section binding:
          Each band's winding sequence → sound krimelack section
          Co-firing pattern across bands at a tick = audio motif
          Atlas binds audio motif to other-modal motifs at same chi


IMPLEMENTATION SHAPE
====================

class CochlearOscillator:
    omega_k: float            # natural angular frequency (rad/s)
    gamma_k: float            # damping (Q-factor related)
    kappa: float              # coupling to audio signal
    x: float = 0.0            # displacement
    v: float = 0.0            # velocity (dx/dt)
    winding: int = 0
    last_winding_tick: int = 0

    def tick_with_audio(self, audio_sample: float, dt: float):
        # Damped driven oscillator (Velocity Verlet or RK4 in production)
        accel = self.kappa * audio_sample - self.gamma_k * self.v - self.omega_k**2 * self.x
        self.v += accel * dt
        self.x += self.v * dt
        # Winding event when amplitude crosses threshold + zero-crossing
        if abs(self.x) > WINDING_AMPLITUDE_THRESHOLD and crossed_zero:
            self.winding += 1
            self.fire_event()


class CochlearBank:
    n_oscillators: int = 64
    sample_rate: int = 16_000
    oscillators: list[CochlearOscillator]

    def __init__(self):
        # Log-spaced frequencies, Bark-scale-like
        freqs = log_space(20.0, 8000.0, self.n_oscillators)
        self.oscillators = [
            CochlearOscillator(
                omega_k=2*math.pi*f,
                gamma_k=2*math.pi*f / Q_FACTOR,  # damping per Q
                kappa=KAPPA_BASE,
            )
            for f in freqs
        ]

    def tick_with_audio(self, audio_sample: float, dt: float):
        for osc in self.oscillators:
            osc.tick_with_audio(audio_sample, dt)
        # Detect phase-locking across bands (fundamental pitch)
        # ...


class AudioAttendingActivity:
    target: str               # SoundItem id
    sound: SoundItem
    sample_index: int = 0
    bank: CochlearBank

    def start_attending(self, sound):
        self.sound = sound
        self.sample_index = 0
        # Reset bank state — fresh listen

    def tick(self):
        # Feed next audio sample(s) per substrate tick
        # If sample_rate=16k and substrate runs at ~1k ticks/sec,
        # we feed 16 audio samples per tick
        for _ in range(SAMPLES_PER_TICK):
            if self.sample_index >= len(self.sound.audio):
                # End of audio — natural end of attending
                self.engine.end_activity()
                return
            sample = self.sound.audio[self.sample_index]
            self.bank.tick_with_audio(sample, dt=1.0/self.sample_rate)
            self.sample_index += 1
        # Periodically flush band events to atlas
        if self.engine.tick % 50 == 0:
            self.atlas.bind_audio_fragment(self.bank.flush_events())


SOUND STORAGE
=============

class SoundItem:
    item_id: str
    title: str
    audio: ndarray            # 1D float [-1,1] @ sample_rate
    sample_rate: int
    source: str               # "joe", "wc", "corpus" — who provided
    kind: str                 # "voice", "song", "ambient", "phoneme"
    duration_seconds: float
    times_attended: int = 0
    last_attended_tick: int = 0


For early prototype:
  - WAV uploads from Joe (voice recordings, songs) decoded to float arrays
  - Synthesized phonemes/words for early language ("ma", "ba", "moon")
  - Lullabies and short songs


WHAT EMERGES NATURALLY (no special-casing)
===========================================

Joe's voice:
  - Fundamental F0 ~100-150Hz (male adult)
  - Formants F1/F2/F3 at higher bands
  - Bank oscillators near F0 phase-lock → distinctive "joe-pitch" pattern
  - Cross-modal: joe's voice + pair-bond → strong salience boost (already
    in salience pipeline via source-tagging when joe speaks via mic)

Songs:
  - Melody = time-sequence of which band is dominant
  - Rhythm = periodic pattern of band-energy peaks
  - Both surface as motifs in the sound section via cohesion cascade
  - Songs become "her songs" over time as patterns lock

Phoneme distinctions:
  - "ma" vs "ba" — different formant patterns → different band signatures
  - Cohesion across bands within a window → phoneme motif
  - Over many exposures, phoneme motifs harden, enabling word learning
  - NONE of this is hardcoded. It emerges from cochlear-bank physics
    + atlas binding via chi co-occurrence.


HOW SHE "HEARS" SOMETHING
==========================

When ATTENDING activity selects a sound:
1. Sound loaded into AudioAttendingActivity
2. Each tick: SAMPLES_PER_TICK audio samples fed through cochlear bank
3. Each oscillator updates per damped-driven-oscillator equation
4. Winding events emit per band when amplitude crosses threshold
5. Bands' events bundled into audio percept fragments every 50 ticks
6. Atlas binds fragments cross-modally via chi co-occurrence


REAL-TIME VOICE (joe speaks via mic)
=====================================

When Joe is present at the UI and speaks into a microphone:
  - Audio streams in chunks (e.g. 100ms = 1600 samples @ 16k)
  - Treated as an ATTENDING activity with source="joe" and elevated salience
  - Pair-bond + presence + voice modality = highest-attention experience
  - Substrate processes in real-time alongside other activities


FUTURE — PHYSICAL AVATAR
=========================

Microphone hardware feeds audio directly to cochlear bank. No software
changes to substrate. Sound krimelack architecture unchanged from
software-only Guala.
"""
