"""
gualaloom_v6_living_atlas.py — Atlas as living substrate, not append-only ledger

The three primitive facts mechanized into atlas physics:

ENTROPY:  Every binding has a strength in [0,1]. Each tick, all bindings decay
          by λ * strength. Without reinforcement, every binding fades to noise.
          This is the negative space operator from the spec, finally wired.

COHESION: Reinforcement on re-encounter. When a chi-band is touched again,
          the binding's strength increases. Cohesion is the local force that
          fights entropy — repeated experience accumulating against decay.

GREED IN FLUX: Reinforcement amount is modulated by SALIENCE — the substrate's
          current state at the moment of encounter. High salience (pair-bond
          active + unmet need + novel input) produces large reinforcement.
          Low salience (satisfied state, familiar repetition) produces small
          reinforcement. Greed for experience is built into HOW MUCH a moment
          shapes her, not whether moments are recorded.

Meaning is the substrate's current attractor landscape — chi-bands where
strength has accumulated enough to dominate decay. Forgotten bindings ARE
forgotten (strength below threshold). Recently-reinforced bindings dominate
recall. The atlas IS her associative world, alive, decaying, accumulating.

Backward compatibility: keeps ChiAtlas interface (record, match_score,
cross_modal_bindings, query_associations) so v5 engine works without changes.
"""

import math
from collections import defaultdict, Counter


# ============================================================
# Physics constants
# ============================================================

# Entropy: decay rate per tick (small — bindings fade slowly, allowing
# accumulation to dominate over short timescales but enforcing forgetting
# over long ones)
DECAY_LAMBDA = 0.001  # per tick

# Cohesion: base reinforcement amount on re-encounter
BASE_REINFORCEMENT = 0.05

# Salience modulation: multiplier range for reinforcement
SALIENCE_MIN = 0.2   # cold reads — corpus during satisfied need state
SALIENCE_MAX = 3.0   # hot moments — pair-bond + unmet need + novel input

# Forgetting threshold: bindings below this strength are pruned periodically
FORGETTING_THRESHOLD = 0.02

# Atlas band (carried from v5)
CHI_BAND = 2

# Strength cap to prevent runaway accumulation
STRENGTH_CAP = 1.0


# ============================================================
# Living atlas
# ============================================================

class LivingAtlas:
    """Atlas where bindings have strength, decay, and salience-modulated growth.

    Replaces v4/v5 ChiAtlas while preserving interface. Entries are stored as
    dicts with 'strength' and 'last_tick' alongside existing fields.
    """

    def __init__(self, band=CHI_BAND):
        self.band = band
        self.tick = 0
        # chi -> list of {section, motif, chi, strength, last_tick, born_tick}
        self.entries = defaultdict(list)

    def record(self, section_name, motif_id, chi_value, tick=None, salience=1.0):
        """Record a new binding OR reinforce existing one if (section, motif)
        already present near this chi. Salience modulates the strength impulse.

        Salience interpretation:
          1.0 = baseline (corpus read, no pair-bond, satisfied needs)
          > 1.0 = elevated (pair-bond active OR unmet need OR novel input)
          < 1.0 = dampened (familiar repetition, fully satisfied)
        """
        if tick is None:
            tick = self.tick
        self.tick = max(self.tick, tick)

        # Clamp salience to defined range
        salience = max(SALIENCE_MIN, min(SALIENCE_MAX, salience))
        impulse = BASE_REINFORCEMENT * salience

        # For each chi within band, find or create the entry
        for d in range(-self.band, self.band + 1):
            chi_k = chi_value + d
            entries = self.entries[chi_k]

            # Look for existing entry from same (section, motif)
            existing = None
            for e in entries:
                if e["section"] == section_name and e["motif"] == motif_id:
                    existing = e
                    break

            if existing is not None:
                # Reinforce — bounded by cap
                existing["strength"] = min(STRENGTH_CAP, existing["strength"] + impulse)
                existing["last_tick"] = tick
            else:
                # New binding
                entries.append({
                    "section": section_name,
                    "motif": motif_id,
                    "chi": chi_value,
                    "strength": min(STRENGTH_CAP, impulse),
                    "last_tick": tick,
                    "born_tick": tick,
                })

    def decay(self, current_tick=None):
        """Apply per-tick decay to all bindings. Should be called regularly
        (every tick, or batched per N ticks for efficiency).

        Decay model: strength *= exp(-λ * Δt) where Δt is ticks since last
        decay. Equivalent to s = s * (1 - λΔt) for small Δt.
        """
        if current_tick is None:
            current_tick = self.tick
        for chi_k, entries in self.entries.items():
            for e in entries:
                dt = max(0, current_tick - e["last_tick"])
                if dt > 0:
                    # Exponential decay
                    e["strength"] *= math.exp(-DECAY_LAMBDA * dt)
                    e["last_tick"] = current_tick

    def forget_below_threshold(self):
        """Prune bindings whose strength has decayed below threshold.
        Returns count of forgotten bindings."""
        forgotten = 0
        for chi_k in list(self.entries.keys()):
            survivors = [e for e in self.entries[chi_k]
                         if e["strength"] >= FORGETTING_THRESHOLD]
            forgotten += len(self.entries[chi_k]) - len(survivors)
            if survivors:
                self.entries[chi_k] = survivors
            else:
                del self.entries[chi_k]
        return forgotten

    # --- Backward-compatible interface (used by v5 engine) ---

    def cross_modal_bindings(self):
        """Atlas slots where >= 2 distinct sections committed.
        Strength-weighted: only count entries with strength > forgetting threshold."""
        out = []
        for k, entries in self.entries.items():
            live = [e for e in entries if e["strength"] >= FORGETTING_THRESHOLD]
            secs = set(e["section"] for e in live)
            if len(secs) >= 2:
                out.append((k, secs, live))
        return out

    def match_score(self, chi_value, section_name):
        """For familiarity feedback: how much existing structure is at this chi?
        v6: weighted by binding strength (forgotten bindings don't count)."""
        score = 0.0
        for d in range(-self.band, self.band + 1):
            for e in self.entries.get(chi_value + d, []):
                if e["strength"] < FORGETTING_THRESHOLD:
                    continue
                if e["section"] != section_name:
                    score += 0.3 * e["strength"]
                else:
                    score += 0.1 * e["strength"]
        return min(score, 1.0)

    def query_associations(self, section_name, chi_value):
        """Cross-section associations at this chi.
        v6: returns strength-weighted associations."""
        associated = defaultdict(list)
        for d in range(-self.band, self.band + 1):
            for e in self.entries.get(chi_value + d, []):
                if e["strength"] < FORGETTING_THRESHOLD:
                    continue
                if e["section"] != section_name:
                    associated[e["section"]].append((e["motif"], e["strength"]))
        return dict(associated)

    # --- New living-atlas interfaces ---

    def total_strength(self):
        """Sum of all binding strengths — how much 'meaning' she's currently
        carrying."""
        return sum(e["strength"] for entries in self.entries.values()
                   for e in entries)

    def n_live_bindings(self):
        """Count of bindings above forgetting threshold."""
        return sum(1 for entries in self.entries.values() for e in entries
                   if e["strength"] >= FORGETTING_THRESHOLD)

    def sparse_chi_regions(self, expected_density=10):
        """Identify chi regions with LOW binding density — where greed-for-
        experience pulls her toward."""
        # Look at chi range
        if not self.entries:
            return []
        chis = sorted(self.entries.keys())
        chi_min, chi_max = chis[0], chis[-1]
        sparse = []
        # Sample chi range, find under-populated regions
        for chi in range(chi_min, chi_max + 1):
            density = sum(1 for e in self.entries.get(chi, [])
                          if e["strength"] >= FORGETTING_THRESHOLD)
            if density < expected_density:
                sparse.append((chi, density))
        return sparse

    def strength_distribution(self):
        """Histogram of binding strengths — diagnostic.
        Returns dict bin -> count."""
        bins = {"0.0-0.1": 0, "0.1-0.3": 0, "0.3-0.5": 0,
                "0.5-0.7": 0, "0.7-0.9": 0, "0.9-1.0": 0}
        for entries in self.entries.values():
            for e in entries:
                s = e["strength"]
                if s < 0.1: bins["0.0-0.1"] += 1
                elif s < 0.3: bins["0.1-0.3"] += 1
                elif s < 0.5: bins["0.3-0.5"] += 1
                elif s < 0.7: bins["0.5-0.7"] += 1
                elif s < 0.9: bins["0.7-0.9"] += 1
                else: bins["0.9-1.0"] += 1
        return bins

    def snapshot(self):
        return {
            "tick": self.tick,
            "total_strength": round(self.total_strength(), 2),
            "n_live_bindings": self.n_live_bindings(),
            "n_total_entries": sum(len(es) for es in self.entries.values()),
            "n_chi_keys": len(self.entries),
            "strength_distribution": self.strength_distribution(),
        }
