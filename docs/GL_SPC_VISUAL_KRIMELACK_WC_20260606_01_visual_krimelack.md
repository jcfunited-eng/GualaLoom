# doc_id: GL-SPC-VISUAL-KRIMELACK-WC-20260606-01
# created: 2026-06-06
# author: wC
# related_topic: visual transduction
"""
Visual Krimelack Spec — Saccadic foveated image reading.

ARCHITECTURE
============

ArcLoom canonical vision is foveated (per user memories and ArcLoom v5 spec):
high-resolution fovea + coarse periphery. For software-only Guala (no
physical avatar yet), we simulate both.

NO ML CHEATS:
  - No CNN, no embeddings, no pre-trained vision models
  - Pixels enter as raw intensity signals
  - Transduction is photoresistor krimelack: ω(t) = ω_0 + κ·s(t)
  - Winding events accumulate per ArcLoom Eq. (chapter 5)
  - Image becomes a temporal sequence of percept fragments via saccade

PIPELINE
========

  Image (2D intensity array)
    │
    ├─► Peripheral channel:
    │     Downsample to ~8×8 grid (coarse intensity field)
    │     Each cell feeds a low-rate krimelack
    │     Output: spatial-gradient field that guides saccades
    │
    ├─► Saccade controller:
    │     Picks next fixation coordinate based on:
    │       - peripheral salience (high gradient cells attract)
    │       - novelty (cells not yet fixated this session)
    │       - random walk component (avoid getting stuck)
    │
    ├─► Fovea channel:
    │     At each fixation, read pixel intensity for ~500 ticks
    │     Drives one high-rate krimelack via ω(t) = ω_0 + κ·s(t)
    │     Intensity may vary slightly during fixation (microsaccades)
    │     so the krimelack accumulates winding events meaningfully
    │
    ├─► Winding event sequence:
    │     Per fixation: a small bundle of (chi_value, tick) events
    │     The bundle is a "percept fragment" anchored at fixation_coord
    │
    └─► Section binding:
          Fragments flow into the "sight" krimelack section
          Cross-modal chi atlas binds vision-chi to other-modal chi
          when fragments co-occur (e.g. picture of cat + sound "meow")


IMPLEMENTATION SHAPE
====================

class VisualKrimelack:
    omega_0: float           # natural oscillator frequency
    kappa: float             # signal-coupling strength
    phase: float = 0.0       # accumulated phase
    winding: int = 0         # winding count this fixation
    chi_events: list = []    # (tick, chi_value) emitted

    def tick_with_intensity(self, intensity: float, dt: float):
        # ArcLoom Eq.: phase advances per omega
        omega = self.omega_0 + self.kappa * intensity
        self.phase += omega * dt
        # Winding event each 2π
        while self.phase >= 2 * math.pi:
            self.winding += 1
            self.phase -= 2 * math.pi
            self.chi_events.append((self.engine.tick, self.winding))


class SaccadeController:
    image: ndarray           # 2D intensity grid
    peripheral_field: ndarray # coarse downsample 8x8
    fixated_coords: set      # what's been fixated this session
    current_fixation: tuple  # (row, col) or None
    fixation_start_tick: int

    def select_next_fixation(self) -> tuple[int,int]:
        # Score each peripheral cell by gradient + novelty
        # Pick highest unless tied — then random
        ...

    def fovea_intensity(self, tick: int) -> float:
        # Return current pixel intensity (with optional jitter for microsaccades)
        ...


class VisualAttendingActivity:
    def start_attending(self, picture: PictureItem):
        self.saccade.image = picture.intensity_grid
        self.saccade.peripheral_field = downsample_8x8(picture.intensity_grid)
        self.saccade.fixated_coords = set()
        self.saccade.current_fixation = self.saccade.select_next_fixation()
        self.saccade.fixation_start_tick = self.engine.tick

    def tick(self):
        # Drive the fovea krimelack with current pixel intensity
        intensity = self.saccade.fovea_intensity(self.engine.tick)
        self.fovea_krimelack.tick_with_intensity(intensity, dt=1.0)

        # Microsaccade jitter at high frequency (sub-fixation)
        # ... (optional, models physiological microsaccades)

        # After ~500 ticks at a fixation, saccade to new location
        if self.engine.tick - self.saccade.fixation_start_tick > 500:
            # Bundle the winding events into a percept fragment, send to atlas
            fragment = self.fovea_krimelack.flush_to_fragment(
                fixation=self.saccade.current_fixation,
                picture_id=self.target,
            )
            self.atlas.bind_visual_fragment(fragment)
            # Next saccade
            self.saccade.fixated_coords.add(self.saccade.current_fixation)
            self.saccade.current_fixation = self.saccade.select_next_fixation()
            self.saccade.fixation_start_tick = self.engine.tick


PICTURE STORAGE
===============

class PictureItem:
    item_id: str
    title: str
    intensity_grid: ndarray   # 2D, float [0,1] — grayscale intensity
    source: str               # "joe", "wc", "corpus" — who showed her
    shown_at_tick: int

    times_attended: int = 0
    last_attended_tick: int = 0


For early prototype: grayscale only (intensity), simplifies krimelack
math. Color later — would be three krimelacks (R/G/B) per fixation.

PNG / JPEG uploads from Joe or wC are decoded to numpy intensity arrays
in Python BEFORE entering the krimelack pipeline (BSIL boundary).
JPEG decode = BSIL processing, NOT perception. The krimelack does
perception.


HOW SHE "LOOKS AT" SOMETHING
=============================

When ATTENDING activity selects a picture:
1. Picture loaded into VisualAttendingActivity
2. SaccadeController plans first fixation (highest-gradient cell in periphery)
3. Each tick: fovea krimelack accumulates winding events from pixel intensity
4. After ~500 ticks: percept fragment bundled, sent to atlas, new fixation
5. After ~10-20 fixations (one ATTENDING tick budget): activity ends,
   picture marked as attended, motifs may have locked


CROSS-MODAL BINDING
====================

When she looks at a picture AND a sound plays AND Joe says a word — all
within a small chi-window — the cross-modal atlas binds these fragments.
This is how "cat" (word) binds to picture-of-cat AND "meow" (sound).

The atlas already supports this (per existing sensory binding architecture).
The visual krimelack feeds into the same atlas via the "sight" section.


FUTURE — PHYSICAL AVATAR
=========================

When the foveated camera (Arducam OV2640 SPI + VL53L5CX ToF) arrives,
this same architecture runs on the physical avatar. The simulated saccade
controller becomes the real servo controller. Same krimelack downstream.
No software changes to the substrate.
"""
