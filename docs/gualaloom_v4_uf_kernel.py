"""
uf_kernel.py — L0-L4 UF (Unified Framework) Kernel, 8-dim DSF output

Spec Ch.2/Ch.6: DSF = (D_k, M_k, R_rev_k, U*_k, C_k, P_k, B_k, S_UF)
8-dimensional structural perception field from kernel.

Inputs: krimelack event stream + atlas context.
Outputs: 8-dim DSF + auxiliary fields (TVR_k, ISF_k, URF_k, G_k).

For software approximation: derive each field from event-stream statistics
and atlas similarity. Each is bounded [0,1] except D_k which is signed [-1,1].
"""
import math
import numpy as np
from dataclasses import dataclass


@dataclass
class DSF:
    """Deterministic Structural Field — 8-dim output of L0-L4 kernel."""
    D_k: float       # Direction      ∈ [-1, +1]
    M_k: float       # Momentum       ∈ [-1, +1]
    R_rev: float     # Path-kill      ∈ [0, 1]
    U_star: float    # Freedom        ∈ [0, 1]
    C_k: float       # Binding        ∈ [0, 1]
    P_k: float       # Compression    ∈ [0, 1]
    B_k: float       # Conviction     ∈ [0, 1]
    S_UF: float      # Convergence    ∈ [0, 1]

    def to_array(self):
        return np.array([self.D_k, self.M_k, self.R_rev, self.U_star,
                         self.C_k, self.P_k, self.B_k, self.S_UF])

    def coupling_matrix_diag(self, J_base=1.0, J_max=2.0):
        """Per spec Ch.6 Table: derive J_ij from DSF outputs.
        Returns the diagonal of the coupling matrix (one J per kernel output)."""
        return {
            "direction":   self.D_k * J_base,
            "convergence": self.S_UF * J_base,
            "momentum":    abs(self.M_k) * J_base,
            "binding":     self.C_k / (1 + self.C_k) * J_base,
            "compression": self.P_k / (1 + self.P_k) * J_base,
            "conviction":  abs(self.B_k) * J_base,
            "freedom":     -(self.U_star) * J_base,
            "path_kill":   self.R_rev * J_max,
        }


def compute_dsf(events, atlas_similarity=0.0, recall_match=0.0):
    """Compute 8-dim DSF from krimelack event stream + atlas context.

    Args:
        events: list of {t, dw, s} from a krimelack
        atlas_similarity: max similarity to existing atlas entries [0,1]
        recall_match: motif recall match score [0,1] (familiarity feedback hook)
    """
    n = len(events)
    if n == 0:
        return DSF(0, 0, 0, 1, 0, 0, 0, 0)  # max freedom, no conviction

    # Winding direction (D_k): net direction
    dws = [e["dw"] for e in events]
    net_w = sum(dws)
    D_k = net_w / max(n, 1)
    D_k = max(-1.0, min(1.0, D_k))

    # Momentum (M_k): rate of change in signal magnitude over event sequence
    if n >= 2:
        s_vals = [e["s"] for e in events]
        diffs = [s_vals[i+1] - s_vals[i] for i in range(n-1)]
        M_k = sum(diffs) / len(diffs)
        M_k = max(-1.0, min(1.0, M_k * 2))  # scale into [-1,1]
    else:
        M_k = 0.0

    # Path-kill (R_rev): how often direction reverses
    reversals = sum(1 for i in range(n-1) if dws[i] * dws[i+1] < 0)
    R_rev = reversals / max(n - 1, 1)

    # Freedom (U*_k): event-position variance (high = underdetermined)
    if n >= 2:
        ts = [e["t"] for e in events]
        t_range = max(ts) - min(ts)
        if t_range > 0:
            expected_step = t_range / (n - 1)
            actual_steps = [ts[i+1] - ts[i] for i in range(n-1)]
            var = sum((a - expected_step) ** 2 for a in actual_steps) / len(actual_steps)
            U_star = min(1.0, math.sqrt(var) / expected_step)
        else:
            U_star = 0.0
    else:
        U_star = 1.0

    # Binding (C_k): atlas similarity (provided by caller)
    C_k = max(0.0, min(1.0, atlas_similarity))

    # Compression (P_k): event density per unit time
    if n >= 2:
        t_range = events[-1]["t"] - events[0]["t"]
        P_k = min(1.0, n / max(t_range * 50, 1.0))
    else:
        P_k = 0.0

    # Conviction (B_k): consistency of winding direction
    pos = sum(1 for d in dws if d > 0)
    neg = sum(1 for d in dws if d < 0)
    B_k = abs(pos - neg) / max(pos + neg, 1)

    # Convergence (S_UF): low U_star AND high B_k = converging on structure
    S_UF = (1.0 - U_star) * B_k

    return DSF(D_k=D_k, M_k=M_k, R_rev=R_rev, U_star=U_star,
               C_k=C_k, P_k=P_k, B_k=B_k, S_UF=S_UF)


def dsf_to_evidence_vector(dsf, n_dim=8):
    """Pack DSF + auxiliary fields into evidence vector for injection.
    Per spec: e_k = concat(norm(TVR_k), ISF_k, URF_k, DSF_k, N(G_k))
    For software: use DSF directly as 8-dim evidence."""
    return dsf.to_array()
