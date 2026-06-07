"""
trit_register.py — Spec Ch.6 Physical Geometry: Triple-Node Resonant Ring

A single trit = three nonlinear oscillators (A, B, C) in equilateral arrangement.
States: w ∈ {-1, 0, +1} = {CCW flow, quiescent, CW flow}
Energy barrier between adjacent states: ΔE = J*(1 + 3α/4)*1.5 ≈ 2.37 for J=1, α=37/64.

Software approximation of the TSAC cell: phase-only state with topological
parity. Hardware version is ferroelectric tri-stable; in software we represent
the winding state w and the phases (φ_A, φ_B, φ_C).
"""
import math
import numpy as np

# Spec frozen constants (DC-1)
J_COUPLING = 1.0
ALPHA = 37.0 / 64.0
DELTA_E = J_COUPLING * (1.0 + 3.0 * ALPHA / 4.0) * 1.5  # ≈ 2.37


class Trit:
    """Single tri-stable cell with three nodes A, B, C."""

    def __init__(self, w=0):
        self.w = w                  # winding state ∈ {-1, 0, +1}
        self.phi_A = 0.0
        self._set_phases_from_w(w)

    def _set_phases_from_w(self, w):
        if w == 0:
            self.phi_B = self.phi_A
            self.phi_C = self.phi_A
        elif w == +1:  # CW: B = A + 2π/3, C = B + 2π/3
            self.phi_B = self.phi_A + 2 * math.pi / 3
            self.phi_C = self.phi_B + 2 * math.pi / 3
        else:          # CCW: C = A + 2π/3, B = C + 2π/3
            self.phi_C = self.phi_A + 2 * math.pi / 3
            self.phi_B = self.phi_C + 2 * math.pi / 3

    def settle_to(self, target_w):
        """Move trit toward target_w. Energy barrier ΔE between adjacent states.
        Software: if coupling pressure exceeds barrier, transition fires."""
        if target_w == self.w:
            return False
        # Adjacent state check (can only transition to adjacent state in one step)
        if abs(target_w - self.w) > 1 and not (self.w == -1 and target_w == +1):
            # Two-step transition required
            intermediate = 0 if self.w * target_w < 0 else (self.w + target_w) // 2
            self.w = intermediate
            self._set_phases_from_w(intermediate)
            return True
        self.w = target_w
        self._set_phases_from_w(target_w)
        return True

    def coupling_pressure_to(self, target_w, J_eff):
        """Pressure to transition. Compared against ΔE for tristate decision."""
        if target_w == self.w:
            return 0.0
        return J_eff * abs(target_w - self.w)


class TritRegister:
    """N-trit register with parity chains for geometric error correction.
    Parity chain: P=5 trits whose w must sum to topological constant K."""

    def __init__(self, n_trits, parity_K=0):
        self.trits = [Trit() for _ in range(n_trits)]
        self.n = n_trits
        self.parity_K = parity_K
        self.lambda_parity = 0.1

    def state(self):
        return np.array([t.w for t in self.trits], dtype=int)

    def set_state(self, ws):
        for t, w in zip(self.trits, ws):
            t.w = int(w)
            t._set_phases_from_w(int(w))

    def parity_violation(self):
        """For parity chains of P=5, ∑w_i should equal K. Return restoring force."""
        violations = []
        for i in range(0, self.n - 4, 5):
            chunk = sum(t.w for t in self.trits[i:i+5])
            violations.append((i, chunk - self.parity_K))
        return violations

    def restore_parity(self):
        """Apply restoring force to bring chains back to topological constant."""
        viols = self.parity_violation()
        for chunk_start, delta in viols:
            if delta == 0:
                continue
            # Push the leftmost non-extreme trit toward correction
            for j in range(chunk_start, chunk_start + 5):
                t = self.trits[j]
                if delta > 0 and t.w > -1:
                    t.settle_to(t.w - 1)
                    delta -= 1
                    if delta == 0:
                        break
                elif delta < 0 and t.w < +1:
                    t.settle_to(t.w + 1)
                    delta += 1
                    if delta == 0:
                        break

    def winding_signature(self):
        """Topological invariant of the whole register."""
        return int(np.sum(self.state()))

    def chi_state(self):
        """Chi state — used by atlas for binding. Sum of winding numbers
        carries the topological information."""
        return int(np.sum(self.state()))
