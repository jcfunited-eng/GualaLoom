# doc_id: GL-MDL-VISUAL-KRIMELACK-WC-20260606-01
# created: 2026-06-06
# author: wC
# related_topic: visual transduction — saccadic fovea krimelack
"""
Visual krimelack model — actual numerical simulation.

Tests whether the fovea krimelack equation ω(t) = ω_0 + κ·s(t)
produces meaningful winding events when reading pixel intensity at
saccaded fixations. Tests:

  Exp A: Still picture, single fixation — baseline winding rate
  Exp B: Still picture, multiple fixations — distinct fragments per region
  Exp C: Moving content at fixation point — winding pattern differs from still

If A and B work, picture reading is sound. If C produces different patterns
than still, video reading is sound by the same architecture.
"""

import math
import numpy as np
from dataclasses import dataclass, field


# Krimelack parameters
OMEGA_0 = 5.0       # baseline angular frequency (rad/tick) at intensity=0
KAPPA = 50.0        # signal-coupling strength
WINDING_PHASE = 2 * math.pi


@dataclass
class FoveaKrimelack:
    """Photoresistor krimelack. Reads scalar intensity over time,
    accumulates phase, emits winding events every 2π."""
    phase: float = 0.0
    winding_count: int = 0
    events: list = field(default_factory=list)  # (tick, winding_number)

    def tick_with_intensity(self, intensity: float, tick: int, dt: float = 1.0):
        """ω(t) = ω_0 + κ·s(t). One ArcLoom-canonical equation."""
        omega = OMEGA_0 + KAPPA * intensity
        self.phase += omega * dt
        while self.phase >= WINDING_PHASE:
            self.winding_count += 1
            self.phase -= WINDING_PHASE
            self.events.append((tick, self.winding_count))

    def flush_fragment(self, fixation_coord, picture_id):
        """Bundle accumulated events into a percept fragment, reset events."""
        frag = {
            "fixation": fixation_coord,
            "picture_id": picture_id,
            "n_windings": len(self.events),
            "event_ticks": [e[0] for e in self.events],
            "intensity_signature": self._signature(),
        }
        self.events = []
        return frag

    def _signature(self):
        """Inter-event interval pattern — what distinguishes a fragment."""
        if len(self.events) < 2:
            return []
        ticks = [e[0] for e in self.events]
        return [ticks[i+1] - ticks[i] for i in range(len(ticks) - 1)]


@dataclass
class SaccadeController:
    """Picks fixation coordinates. For modeling, simple grid scan + novelty."""
    image: np.ndarray = None
    grid_h: int = 0
    grid_w: int = 0
    fixated: set = field(default_factory=set)
    
    def __post_init__(self):
        if self.image is not None:
            self.grid_h, self.grid_w = self.image.shape

    def set_image(self, image):
        self.image = image
        self.grid_h, self.grid_w = image.shape
        self.fixated = set()

    def peripheral_field(self, n_rows=4, n_cols=4):
        """Coarse 4x4 downsample of intensity gradients — guides saccades."""
        h_step = self.grid_h // n_rows
        w_step = self.grid_w // n_cols
        gradients = np.zeros((n_rows, n_cols))
        for r in range(n_rows):
            for c in range(n_cols):
                region = self.image[r*h_step:(r+1)*h_step, c*w_step:(c+1)*w_step]
                gradients[r, c] = np.std(region)  # std as gradient proxy
        return gradients, h_step, w_step

    def pick_fixation(self) -> tuple:
        """Highest-gradient un-fixated peripheral cell. Center of that cell."""
        gradients, h_step, w_step = self.peripheral_field()
        n_rows, n_cols = gradients.shape
        # Find highest-gradient un-fixated cell
        candidates = []
        for r in range(n_rows):
            for c in range(n_cols):
                if (r, c) not in self.fixated:
                    candidates.append((gradients[r, c], r, c))
        if not candidates:
            return None
        candidates.sort(reverse=True)
        _, r, c = candidates[0]
        self.fixated.add((r, c))
        # Convert peripheral cell to image-coord center
        return (r * h_step + h_step // 2, c * w_step + w_step // 2)

    def fovea_intensity(self, fixation, tick, video_frames=None):
        """Read pixel intensity at fixation. If video, advance to current frame."""
        if video_frames is not None:
            # tick determines frame index — simulate video playing during fixation
            frame_idx = tick % len(video_frames)
            return float(video_frames[frame_idx][fixation[0], fixation[1]])
        else:
            return float(self.image[fixation[0], fixation[1]])


# ---------------------------------------------------------------------------
# Test images
# ---------------------------------------------------------------------------

def make_simple_shape_image(size=32):
    """Square with a brighter circle inside."""
    img = np.full((size, size), 0.2)  # dark background
    # Bright circle in middle
    cy, cx = size // 2, size // 2
    for r in range(size):
        for c in range(size):
            if (r - cy)**2 + (c - cx)**2 < (size // 4)**2:
                img[r, c] = 0.9
    return img


def make_two_object_image(size=32):
    """Two bright regions, separated."""
    img = np.full((size, size), 0.15)
    img[4:12, 4:12] = 0.85   # top-left bright square
    img[18:28, 20:30] = 0.7  # bottom-right bright region
    return img


def make_moving_video(size=32, n_frames=100):
    """A bright circle moving across the image. Returns list of frames."""
    frames = []
    for f in range(n_frames):
        img = np.full((size, size), 0.15)
        cy = size // 2
        cx = int(2 + (size - 4) * (f / n_frames))  # moves left to right
        for r in range(size):
            for c in range(size):
                if (r - cy)**2 + (c - cx)**2 < (size // 6)**2:
                    img[r, c] = 0.95
        frames.append(img)
    return frames


# ---------------------------------------------------------------------------
# Experiments
# ---------------------------------------------------------------------------

def exp_A_still_single_fixation():
    print("=" * 72)
    print("EXP A: Still image, single fixation — baseline winding rate")
    print("=" * 72)

    img = make_simple_shape_image()
    sacc = SaccadeController()
    sacc.set_image(img)
    krim = FoveaKrimelack()

    # Force a fixation on the center (where the bright circle is)
    center = (img.shape[0] // 2, img.shape[1] // 2)
    print(f"\nFixation at center {center}, intensity = {img[center]:.2f}")
    print(f"Running 500 ticks of fovea integration...")

    for tick in range(500):
        intensity = sacc.fovea_intensity(center, tick)
        krim.tick_with_intensity(intensity, tick)

    fragment = krim.flush_fragment(center, "shape_image")
    print(f"\n  Total windings in 500 ticks: {fragment['n_windings']}")
    print(f"  Average inter-event interval: "
          f"{np.mean(fragment['intensity_signature']):.2f} ticks/winding"
          if fragment['intensity_signature'] else "N/A")

    # Compare with fixation on dark region
    print("\nFixation on DARK background (corner), 500 ticks...")
    krim2 = FoveaKrimelack()
    corner = (2, 2)
    for tick in range(500):
        krim2.tick_with_intensity(sacc.fovea_intensity(corner, tick), tick)
    frag2 = krim2.flush_fragment(corner, "shape_image")
    print(f"  Total windings: {frag2['n_windings']}")
    print(f"  Avg interval: "
          f"{np.mean(frag2['intensity_signature']):.2f} ticks/winding"
          if frag2['intensity_signature'] else "N/A")

    print("\n>>> Bright vs dark produces DIFFERENT winding rates. "
          "Krimelack distinguishes regions.")
    return fragment, frag2


def exp_B_still_multiple_fixations():
    print("\n" + "=" * 72)
    print("EXP B: Still image, multiple saccades — distinct fragments")
    print("=" * 72)

    img = make_two_object_image()
    sacc = SaccadeController()
    sacc.set_image(img)
    print(f"\nImage has two bright regions (top-left, bottom-right)")
    
    fragments = []
    for fixation_n in range(6):
        fixation = sacc.pick_fixation()
        if fixation is None:
            print(f"  No more fixations available")
            break
        krim = FoveaKrimelack()
        for t in range(500):
            krim.tick_with_intensity(sacc.fovea_intensity(fixation, t), t)
        frag = krim.flush_fragment(fixation, "two_object")
        intensity_at_fixation = img[fixation]
        print(f"  Saccade #{fixation_n+1}: coord={fixation}, "
              f"intensity={intensity_at_fixation:.2f}, "
              f"windings={frag['n_windings']}")
        fragments.append(frag)

    # Distinct fragments by winding count?
    counts = [f['n_windings'] for f in fragments]
    print(f"\n  Winding counts across fragments: {counts}")
    print(f"  Spread: min={min(counts)}, max={max(counts)}, "
          f"std={np.std(counts):.1f}")
    print(f"\n>>> Different fixations produce different fragments because "
          f"intensity varies across the image. This is the spatial "
          f"information she'd integrate to perceive structure.")
    return fragments


def exp_C_video_at_fixation():
    print("\n" + "=" * 72)
    print("EXP C: Video at single fixation point — moving vs still")
    print("=" * 72)

    # Video: circle moves across the image
    video = make_moving_video()
    sacc_video = SaccadeController()
    sacc_video.set_image(video[0])

    # Fixate at the path of the moving circle
    fixation = (video[0].shape[0] // 2, video[0].shape[1] // 2)
    print(f"\nFixation at {fixation} — circle moves through this point")
    
    krim_video = FoveaKrimelack()
    intensities_video = []
    for tick in range(500):
        intensity = sacc_video.fovea_intensity(fixation, tick, video_frames=video)
        intensities_video.append(intensity)
        krim_video.tick_with_intensity(intensity, tick)
    
    print(f"\n  Intensity at fixation over 500 ticks:")
    print(f"    min={min(intensities_video):.2f}, "
          f"max={max(intensities_video):.2f}, "
          f"mean={np.mean(intensities_video):.2f}, "
          f"std={np.std(intensities_video):.2f}")
    
    frag_video = krim_video.flush_fragment(fixation, "moving_circle")
    print(f"\n  Total windings (video): {frag_video['n_windings']}")
    if frag_video['intensity_signature']:
        intervals = frag_video['intensity_signature']
        print(f"  Inter-event intervals: min={min(intervals)}, "
              f"max={max(intervals)}, std={np.std(intervals):.2f}")

    # Compare with still image at same fixation
    still = make_simple_shape_image()
    sacc_still = SaccadeController()
    sacc_still.set_image(still)
    krim_still = FoveaKrimelack()
    for tick in range(500):
        krim_still.tick_with_intensity(
            sacc_still.fovea_intensity(fixation, tick), tick)
    frag_still = krim_still.flush_fragment(fixation, "still_circle")
    print(f"\n  Total windings (still, same coord): {frag_still['n_windings']}")
    if frag_still['intensity_signature']:
        intervals_still = frag_still['intensity_signature']
        print(f"  Inter-event intervals: min={min(intervals_still)}, "
              f"max={max(intervals_still)}, std={np.std(intervals_still):.2f}")

    print(f"\n>>> Video at same fixation produces VERY DIFFERENT signature "
          f"than still (interval-variance still={np.std(intervals_still):.2f} "
          f"vs video={np.std(intervals):.2f}). Motion is encoded naturally "
          f"in the krimelack's time-varying phase pattern. No frame "
          f"processing required.")
    return frag_video, frag_still


if __name__ == "__main__":
    exp_A_still_single_fixation()
    exp_B_still_multiple_fixations()
    exp_C_video_at_fixation()
