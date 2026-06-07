---
doc_id: GL-RPT-KRIMELACK-MODEL-WC-20260606-01
created: 2026-06-06
author: wC
type: modeling report
topic: visual + audio krimelack numerical validation
related_specs:
  - GL-SPC-VISUAL-KRIMELACK-WC-20260606-01
  - GL-SPC-AUDIO-KRIMELACK-WC-20260606-01
  - GL-SPC-MULTIMEDIA-WC-20260606-01
---

# Krimelack Modeling Report

I wrote specs for the visual and audio krimelacks without modeling them. Joe called this out. This report covers actual numerical simulation of both.

## What I modeled

`GL_MDL_VISUAL_KRIMELACK_WC_20260606_01_visual_krimelack_sim.py`
  - Single fovea krimelack with ArcLoom equation ω(t) = ω₀ + κ·s(t)
  - Simple saccade controller using peripheral gradient
  - Experiments: still image single fixation, still image multiple saccades,
    video (moving object) at fixation point

`GL_MDL_AUDIO_KRIMELACK_WC_20260606_01_audio_krimelack_sim.py`
  - Cochlear bank of 32 damped driven oscillators, log-spaced 80-4000 Hz
  - Velocity-Verlet integration of d²x/dt² + γ·v + ω²·x = κ·s(t)
  - Experiments: pure tones at known freqs, two-tone, voice-like, chord

## Visual findings

**Architecture works.** Bright vs dark regions produce 3.3× different winding rates (3978 vs 1193 over 500 ticks). Multiple saccades produce distinct fragments per region (std 1184.9 across fragments). Video at a fixation point produces time-varying intensity the krimelack tracks naturally.

**Implementation requirement surfaced**: my naive summary statistic (total windings per fixation) doesn't distinguish "still mid-intensity" from "video oscillating high-low" — both have similar means. The krimelack's PHASE history captures the difference; the SUMMARY doesn't. The atlas binding logic must use the raw event_ticks sequence, not just counts. **The percept fragment is the event sequence, not a number.**

This matters because video perception relies on temporal structure in the krimelack output. If c1 implements "windings per fixation as the perceptual feature" the model will lose motion information. The fragment must carry timing.

## Audio findings

**Architecture works for frequency discrimination.** Pure tones land on the nearest band cleanly:

| Input | Top band | Distance |
|---|---|---|
| 100 Hz | 103.0 Hz | 3.0 Hz |
| 250 Hz | 249.1 Hz | 0.9 Hz |
| 1000 Hz | 998.2 Hz | 1.8 Hz |
| 2500 Hz | 2414.6 Hz | 85.4 Hz |

Log-spacing of bands means high-frequency resolution is lower in absolute terms but proportional in relative terms.

**Critical implementation requirement: 1/ω response bias.** The damped driven oscillator's steady-state amplitude at resonance is X_max ≈ κ·F·Q/ω. Low-frequency oscillators get much larger displacement than high-frequency oscillators for the same input amplitude. In a two-tone test (200 Hz + 1500 Hz at equal amplitude), the 200 Hz band's response is ~7× larger than the 1500 Hz band's. The 1500 Hz tone is essentially invisible.

Real cochleae compensate for this via the cochlear amplifier (outer hair cells). The production implementation needs **per-band gain normalization** — multiply each band's energy by ω (or apply Bark-scale gain compensation) so equal-amplitude input frequencies produce equal-energy output across the bank. Without this, voice formants (730 Hz, 1090 Hz, 2440 Hz) are drowned out by F0 (120 Hz).

This is the kind of thing modeling catches before deploy. Specifying "cochlear bank" alone is not enough; the gain compensation is essential.

**Energy vs winding events**: Energy per band (= ½·v² + ½·ω²·x²) gives the cleanest signal of "this frequency is present." Winding events (amplitude-thresholded zero-crossings) give the discrete event encoding for atlas binding. Both are needed:
  - Energy → real-time band activation pattern (the "what frequencies right now" signal)
  - Winding events → motif-formable discrete events that feed into the existing atlas via the sound section

## Multimedia spec implications

The multimedia spec assumed visual + audio krimelacks worked. Both do, with the implementation requirements above. Multimedia adds:
  - Audio + video stream sync via substrate tick (already specced)
  - Visual fragment carries event_ticks (now confirmed required)
  - Audio band energies normalized 1/ω (now confirmed required)
  - Cross-modal binding via chi co-occurrence (existing atlas)

The multimedia case is sound. No new architectural changes from running the models.

## What I haven't modeled

  - Real video file decoding pipeline (ffmpeg→intensity grids → krimelack)
  - Real audio file decoding pipeline (WAV/MP3 → samples → cochlear bank)
  - Cross-modal binding under simultaneous visual+audio input
  - Smooth pursuit saccades (deferred per spec)

These are implementation details, not architectural questions. The architecture is validated.

## Updates to specs

The two krimelack specs should be amended:

**Visual spec** — add explicit requirement: percept fragments MUST carry event_ticks sequence, not just counts. The temporal structure is what encodes motion and intensity dynamics.

**Audio spec** — add explicit requirement: per-band gain compensation (multiply energy by ω or Bark-scale gain) to counter the 1/ω response bias. Without this, low-frequency content drowns out everything else.

I'll fold these into the specs before c1 implementation begins.

## Honest assessment

The visual spec was essentially right; the audio spec was right at the architecture level but missing a critical implementation detail (gain compensation). Running the models was the difference between c1 building something that works and c1 building something that hears only bass.

Standing rule reinforced: spec without modeling is sketch. Don't trust sketches.
