"""
chi_atlas_l6.py — Chi Atlas (binding) + L6-TCL (dimensional grinder)

Spec L6-TCL: n_eff = n_start - Σ rank(C_i). When n_eff < n_start/e,
capture basin → SL-1 (structural lock) → emit.

Chi atlas: binds commits across krimelacks by chi-state co-occurrence
within band δ. Encoding = the cross-modal co-firing recorded here.
"""
import math
from collections import defaultdict


CHI_BAND = 2  # soft band width (δ)
N_START = 8   # initial dimensionality (matches DSF dim)


class ChiAtlas:
    """Binds events across modal + word + role krimelacks within chi-band δ."""

    def __init__(self, band=CHI_BAND):
        self.band = band
        # chi_value -> list of {section, motif_id, chi, tick}
        self.entries = defaultdict(list)
        self.tick = 0

    def record(self, section_name, motif_id, chi_value, tick=None):
        """Record a commit at chi_value. Replicate across band for soft binding."""
        if tick is None:
            tick = self.tick
        self.tick += 1
        for d in range(-self.band, self.band + 1):
            self.entries[chi_value + d].append({
                "section": section_name,
                "motif": motif_id,
                "chi": chi_value,
                "tick": tick,
            })

    def cross_modal_bindings(self):
        """Atlas entries where >= 2 distinct sections committed in same band."""
        out = []
        for k, entries in self.entries.items():
            secs = set(e["section"] for e in entries)
            if len(secs) >= 2:
                out.append((k, secs, entries))
        return out

    def match_score(self, chi_value, section_name):
        """Familiarity feedback hook: how much existing structure is in this band?
        Returns score ∈ [0,1]. Spec Ch.21: this raises the dead zone."""
        score = 0.0
        for d in range(-self.band, self.band + 1):
            for e in self.entries.get(chi_value + d, []):
                if e["section"] != section_name:
                    score += 0.3  # cross-modal evidence weighted heavier
                else:
                    score += 0.1
        return min(score, 1.0)

    def query_associations(self, section_name, chi_value):
        """For introspection / recall: what other sections bound at this chi?"""
        associated = defaultdict(list)
        for d in range(-self.band, self.band + 1):
            for e in self.entries.get(chi_value + d, []):
                if e["section"] != section_name:
                    associated[e["section"]].append(e["motif"])
        return dict(associated)


class L6_TCL:
    """L6 Topological Constraint Layer / Dimensional Grinder.

    As constraints from the kernel restrict the coupling matrix, effective
    dimensionality reduces: n_eff = n_start - Σ rank(C_i).
    When n_eff < n_start/e ≈ n_start * 0.368, fabric enters capture basin
    → SL-1 (Structural Lock Level 1) → emit.
    """

    def __init__(self, n_start=N_START):
        self.n_start = n_start
        self.capture_threshold = n_start / math.e

    def n_eff(self, dsf):
        """Effective dimension given current DSF. Each high-magnitude DSF
        component is a constraint that reduces dimensionality."""
        constraints = 0
        # Each DSF component above 0.5 magnitude is a rank-1 constraint
        for v in (dsf.D_k, dsf.M_k, dsf.R_rev, dsf.U_star,
                  dsf.C_k, dsf.P_k, dsf.B_k, dsf.S_UF):
            if abs(v) > 0.5:
                constraints += 1
        return self.n_start - constraints

    def captured(self, dsf):
        """Return True if capture basin reached → emit ready."""
        return self.n_eff(dsf) < self.capture_threshold

    def structural_lock(self, dsf):
        """SL-1 fires when captured AND conviction is high AND freedom is low."""
        return (self.captured(dsf) and dsf.B_k > 0.5 and dsf.U_star < 0.4
                and dsf.S_UF > 0.4)
