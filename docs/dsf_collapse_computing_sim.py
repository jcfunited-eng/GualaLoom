#!/usr/bin/env python3
"""
DSF-AI Collapse-Based Quantum Computing — Simulation
=====================================================

THE QUESTION:
  Can you skip sequential gates entirely?
  Encode the problem in geometry. Prepare superposition. Measure.
  Does the correct answer have higher probability than random?

TEST METHODOLOGY:
  1. Set up coupled NV qubits with geometric Hamiltonian
  2. Prepare all qubits in equal superposition (no gates)
  3. Let system evolve under lattice coupling ONLY
  4. Measure — does geometry direct collapse toward the answer?

If yes: collapse-based computing works.
If no: we're stuck with gate-based.

HONEST ASSESSMENT. No hand-waving.

Classification: TRADE SECRET — DSF-AI
"""

import numpy as np
import qutip as qt
import time as timer

# Basics
I2 = qt.qeye(2)
sx = qt.sigmax()
sy = qt.sigmay()
sz = qt.sigmaz()
s0 = qt.basis(2, 0)
s1 = qt.basis(2, 1)
H_had = qt.Qobj([[1, 1], [1, -1]]) / np.sqrt(2)

DIPOLAR_CONST = 52.0  # MHz·nm³


def make_dipolar_H(n_qubits, couplings):
    """
    Build full secular dipolar Hamiltonian for n qubits.
    couplings: list of (i, j, g_MHz) tuples.
    H = sum_ij g_ij * (Sz_i Sz_j - (Sx_i Sx_j + Sy_i Sy_j)/2)
    """
    H = 0
    for i, j, g in couplings:
        for pauli, factor in [(sz, 1.0), (sx, -0.5), (sy, -0.5)]:
            ops = [I2] * n_qubits
            ops[i] = pauli
            ops[j] = pauli
            H = H + g * factor * qt.tensor(ops)
    return H


def equal_superposition(n_qubits):
    """Prepare |+⟩^n — equal superposition of all states."""
    plus = (s0 + s1).unit()
    state = plus
    for _ in range(n_qubits - 1):
        state = qt.tensor(state, plus)
    return state


def measure_probabilities(psi, n_qubits):
    """Get measurement probabilities for all basis states."""
    n_states = 2**n_qubits
    probs = []
    for k in range(n_states):
        bits = format(k, f'0{n_qubits}b')
        basis = qt.tensor([s0 if b == '0' else s1 for b in bits])
        overlap = basis.dag() * psi
        if hasattr(overlap, 'full'):
            p = float(abs(overlap.full().flatten()[0])**2)
        else:
            p = float(abs(overlap)**2)
        probs.append(p)
    return np.array(probs)


# ===========================================================================
# TEST A: SIMPLE 2-QUBIT — DOES COUPLING BIAS COLLAPSE?
# ===========================================================================
def test_collapse_2q():
    """
    2 qubits coupled along [111].
    Prepare |+⟩|+⟩. Evolve under coupling. Measure.
    Does geometry bias toward specific outcomes?
    """
    print("=" * 70)
    print("TEST A: 2-QUBIT COLLAPSE BIAS")
    print("=" * 70)
    print("  Setup: 2 NVs along [111], 10nm apart")
    print("  Initial state: |+⟩|+⟩ (equal superposition)")
    print("  No gates applied. Just coupling and time.")

    g = DIPOLAR_CONST / 10**3 * 2  # 10nm, Gamma=2
    H = make_dipolar_H(2, [(0, 1, g)])
    psi0 = equal_superposition(2)

    # Sweep evolution time
    random_prob = 0.25  # 1/4 for each of 4 states
    t_max = 2 * np.pi / g
    times = np.linspace(0, t_max, 500)
    result = qt.sesolve(H, psi0, times)

    print(f"\n  Coupling: {g:.4f} MHz")
    print(f"  Period: {t_max:.2f} μs")
    print(f"  Random baseline: 25% per state")

    # Track max bias over time
    best_bias = 0
    best_t = 0
    best_probs = None

    for i, psi_t in enumerate(result.states):
        probs = measure_probabilities(psi_t, 2)
        bias = max(probs) - random_prob
        if bias > best_bias:
            best_bias = bias
            best_t = times[i]
            best_probs = probs

    labels = ['|00⟩', '|01⟩', '|10⟩', '|11⟩']
    print(f"\n  Peak bias at t = {best_t*1000:.1f} ns:")
    for label, p in zip(labels, best_probs):
        bar = '█' * int(p * 60)
        marker = ' ← ENHANCED' if p > random_prob + 0.05 else ''
        print(f"    {label}: {p:.4f}  {bar}{marker}")

    print(f"\n  Max probability: {max(best_probs):.4f} (random = 0.2500)")
    print(f"  Bias: {best_bias:.4f} ({best_bias/random_prob*100:.1f}% above random)")

    # The ground state of H = g*(SzSz - (SxSx+SySy)/2) is the singlet
    # (|01⟩-|10⟩)/√2 with eigenvalue -3g/2
    # But we're looking at whether measurement probabilities are biased
    # The coupling should favor aligned or anti-aligned states

    if best_bias > 0.05:
        print(f"\n  ✓ COUPLING BIASES COLLAPSE — geometry directs the outcome")
    else:
        print(f"\n  ✗ No significant bias — coupling alone doesn't direct collapse")

    return best_bias, best_probs


# ===========================================================================
# TEST B: 4-QUBIT OPTIMIZATION — FIND THE GROUND STATE
# ===========================================================================
def test_collapse_optimization():
    """
    Encode an optimization problem in the coupling geometry.
    Can the system find the optimal solution through collapse alone?

    Problem: 4 qubits, find bit string that minimizes energy.
    Couplings set so that |1010⟩ is the unique ground state.
    """
    print(f"\n{'=' * 70}")
    print("TEST B: 4-QUBIT OPTIMIZATION VIA COLLAPSE")
    print("=" * 70)
    print("  Problem: find lowest-energy bit string")
    print("  Target ground state: |1010⟩")
    print("  Approach: superposition → evolve under H → measure")

    n = 4
    g = 0.1  # MHz, representative coupling

    # Design couplings so |1010⟩ is ground state
    # Antiferromagnetic coupling (negative g) favors anti-aligned neighbors
    # In a chain: qubit 0-1, 1-2, 2-3 all antiferromagnetic
    # Ground states: |0101⟩ and |1010⟩ (degenerate for pure AFM chain)
    # Add asymmetry: weak field-like term to break degeneracy
    couplings = [
        (0, 1, -g),   # AFM
        (1, 2, -g),   # AFM
        (2, 3, -g),   # AFM
    ]
    H = make_dipolar_H(n, couplings)

    # Add weak bias to prefer |1⟩ on qubit 0 (breaks degeneracy)
    ops = [I2] * n
    ops[0] = sz
    H = H - 0.02 * g * qt.tensor(ops)  # tiny bias, barely breaks symmetry

    # Find actual ground state of H
    eigenvalues, eigenstates = H.eigenstates()
    gs = eigenstates[0]
    gs_probs = measure_probabilities(gs, n)
    gs_label_idx = np.argmax(gs_probs)
    gs_label = format(gs_label_idx, f'0{n}b')
    print(f"\n  Actual ground state: |{gs_label}⟩ (probability {gs_probs[gs_label_idx]:.4f})")
    print(f"  Ground energy: {eigenvalues[0]:.6f} MHz")

    # Now: prepare superposition and evolve
    psi0 = equal_superposition(n)
    random_prob = 1.0 / (2**n)  # 1/16 = 0.0625

    # Evolve for various times
    t_max = 4 * np.pi / g
    times = np.linspace(0, t_max, 500)
    result = qt.sesolve(H, psi0, times)

    best_gs_prob = 0
    best_t = 0
    best_probs = None

    for i, psi_t in enumerate(result.states):
        probs = measure_probabilities(psi_t, n)
        gs_prob = probs[gs_label_idx]
        if gs_prob > best_gs_prob:
            best_gs_prob = gs_prob
            best_t = times[i]
            best_probs = probs

    print(f"\n  Peak ground-state probability at t = {best_t*1000:.0f} ns:")
    print(f"  Random baseline: {random_prob:.4f} (1/{2**n})")
    print(f"  Achieved: {best_gs_prob:.4f}")
    print(f"  Enhancement: {best_gs_prob/random_prob:.1f}x over random")

    # Show top 4 states
    sorted_idx = np.argsort(best_probs)[::-1]
    print(f"\n  Top states at peak time:")
    for rank, idx in enumerate(sorted_idx[:6]):
        label = format(idx, f'0{n}b')
        p = best_probs[idx]
        bar = '█' * int(p * 60)
        gs_mark = ' ← GROUND STATE' if idx == gs_label_idx else ''
        print(f"    |{label}⟩: {p:.4f}  {bar}{gs_mark}")

    if best_gs_prob > 2 * random_prob:
        print(f"\n  ✓ COLLAPSE FINDS OPTIMUM — {best_gs_prob/random_prob:.1f}x above random")
        print(f"  ✓ No gates needed — geometry encodes the problem")
    else:
        print(f"\n  ✗ Insufficient bias toward ground state")

    return best_gs_prob, random_prob


# ===========================================================================
# TEST C: COLLAPSE SPEED — HOW FAST DOES THE ANSWER EMERGE?
# ===========================================================================
def test_collapse_speed():
    """
    How quickly does the probability bias build up?
    Is it fast enough to be practical?
    """
    print(f"\n{'=' * 70}")
    print("TEST C: COLLAPSE SPEED — HOW FAST DOES THE ANSWER EMERGE?")
    print("=" * 70)

    n = 3
    g = 0.1  # MHz

    # Simple problem: 3-qubit AFM chain, ground state |010⟩ or |101⟩
    couplings = [(0, 1, -g), (1, 2, -g)]
    H = make_dipolar_H(n, couplings)
    # Small bias to select |101⟩
    ops = [I2]*n; ops[0] = sz
    H = H - 0.01 * g * qt.tensor(ops)

    eigenvalues, eigenstates = H.eigenstates()
    gs = eigenstates[0]
    gs_probs = measure_probabilities(gs, n)
    gs_idx = np.argmax(gs_probs)
    gs_label = format(gs_idx, f'0{n}b')

    psi0 = equal_superposition(n)
    random_prob = 1.0 / (2**n)

    # Fine time resolution to see speed
    t_max = 10 * np.pi / g
    n_times = 1000
    times = np.linspace(0, t_max, n_times)
    result = qt.sesolve(H, psi0, times)

    print(f"  Target ground state: |{gs_label}⟩")
    print(f"  Random probability: {random_prob:.4f}")
    print(f"  Coupling: {g} MHz = {g*1000:.0f} kHz")
    print(f"\n  Time evolution of ground-state probability:")

    # Track probability over time
    gs_prob_vs_time = []
    for psi_t in result.states:
        probs = measure_probabilities(psi_t, n)
        gs_prob_vs_time.append(probs[gs_idx])

    gs_prob_vs_time = np.array(gs_prob_vs_time)

    # Report at key time points
    checkpoints_ns = [1, 10, 100, 1000, 5000, 10000, 50000, 100000]
    print(f"\n  {'Time':>12} {'P(ground)':>12} {'vs Random':>12} {'Status':>20}")
    print(f"  {'-'*58}")

    first_useful = None
    for t_ns in checkpoints_ns:
        t_us = t_ns / 1000.0
        if t_us > t_max:
            break
        idx = int(t_us / t_max * (n_times - 1))
        idx = min(idx, n_times - 1)
        p = gs_prob_vs_time[idx]
        ratio = p / random_prob
        status = ""
        if ratio > 1.5 and first_useful is None:
            status = "← USEFUL BIAS"
            first_useful = t_ns
        elif ratio > 2:
            status = "← STRONG BIAS"
        elif ratio > 3:
            status = "← DOMINANT"

        if t_ns >= 1000:
            t_str = f"{t_ns/1000:.1f} μs"
        else:
            t_str = f"{t_ns} ns"
        print(f"  {t_str:>12} {p:>12.4f} {ratio:>11.1f}x {status:>20}")

    # Find peak and time to reach it
    peak_idx = np.argmax(gs_prob_vs_time)
    peak_prob = gs_prob_vs_time[peak_idx]
    peak_time = times[peak_idx]

    print(f"\n  Peak: P = {peak_prob:.4f} ({peak_prob/random_prob:.1f}x random) "
          f"at t = {peak_time*1000:.0f} ns")

    # Find time to first exceed 2x random
    threshold = 2 * random_prob
    exceed_idx = np.where(gs_prob_vs_time > threshold)[0]
    if len(exceed_idx) > 0:
        t_exceed = times[exceed_idx[0]]
        print(f"  Time to 2x random: {t_exceed*1000:.0f} ns")
        print(f"  Time to 2x random: {t_exceed:.4f} μs")
    else:
        print(f"  Never reached 2x random in simulation window")

    # Compare to gate-based time
    gate_time = np.pi / (4 * g)  # single gate time
    n_gates_equiv = 5  # roughly what you'd need for this problem gate-based
    gate_total = gate_time * n_gates_equiv

    if len(exceed_idx) > 0:
        print(f"\n  Gate-based equivalent: ~{n_gates_equiv} gates × {gate_time*1000:.0f} ns = "
              f"{gate_total*1000:.0f} ns")
        print(f"  Collapse-based: {t_exceed*1000:.0f} ns to useful bias")
        speedup = gate_total / t_exceed if t_exceed > 0 else float('inf')
        if speedup > 1:
            print(f"  Speedup: {speedup:.1f}x faster than gate-based")
        else:
            print(f"  Slowdown: {1/speedup:.1f}x slower than gate-based")

    return peak_prob, random_prob


# ===========================================================================
# TEST D: 5-QUBIT CONSTRAINT SATISFACTION
# ===========================================================================
def test_constraint_satisfaction():
    """
    Can geometric coupling solve a constraint satisfaction problem?

    Problem: 5 variables, find assignment satisfying:
      - Qubit 0 and 1 must differ (AFM coupling)
      - Qubit 1 and 2 must differ
      - Qubit 2 and 3 must differ
      - Qubit 3 and 4 must differ
      - Qubit 4 and 0 must differ (ring constraint!)

    This is graph coloring on a 5-cycle. Only possible with odd cycle.
    Solutions: |01010⟩, |10101⟩ (and ONLY these).
    The geometry must find 2 out of 32 states = 6.25%
    """
    print(f"\n{'=' * 70}")
    print("TEST D: 5-QUBIT CONSTRAINT SATISFACTION (RING)")
    print("=" * 70)
    print("  Problem: 5-node ring, each pair of neighbors must differ")
    print("  Solutions: |01010⟩ and |10101⟩ only (2 out of 32)")

    n = 5
    g = 0.1  # MHz

    # Ring of AFM couplings
    couplings = [(i, (i+1) % n, -g) for i in range(n)]
    H = make_dipolar_H(n, couplings)

    psi0 = equal_superposition(n)
    random_prob = 1.0 / (2**n)

    # Find ground states
    eigenvalues, eigenstates = H.eigenstates()
    print(f"\n  Lowest 4 eigenvalues:")
    for i in range(min(4, len(eigenvalues))):
        probs = measure_probabilities(eigenstates[i], n)
        top_idx = np.argmax(probs)
        label = format(top_idx, f'0{n}b')
        print(f"    E_{i} = {eigenvalues[i]:+.6f}  dominant: |{label}⟩ ({probs[top_idx]:.4f})")

    # Evolve and check
    t_max = 4 * np.pi / g
    times = np.linspace(0, t_max, 500)
    result = qt.sesolve(H, psi0, times)

    # Track probability of the two correct solutions
    idx_01010 = int('01010', 2)
    idx_10101 = int('10101', 2)

    best_solution_prob = 0
    best_t = 0

    for i, psi_t in enumerate(result.states):
        probs = measure_probabilities(psi_t, n)
        solution_prob = probs[idx_01010] + probs[idx_10101]
        if solution_prob > best_solution_prob:
            best_solution_prob = solution_prob
            best_t = times[i]
            best_all_probs = probs

    print(f"\n  Peak solution probability at t = {best_t*1000:.0f} ns:")
    print(f"  P(|01010⟩) = {best_all_probs[idx_01010]:.4f}")
    print(f"  P(|10101⟩) = {best_all_probs[idx_10101]:.4f}")
    print(f"  P(solution) = {best_solution_prob:.4f}")
    print(f"  Random baseline: {2*random_prob:.4f} (2/{2**n})")
    print(f"  Enhancement: {best_solution_prob/(2*random_prob):.1f}x over random")

    # Show what the wrong answers look like
    sorted_idx = np.argsort(best_all_probs)[::-1]
    print(f"\n  Top 8 states at peak time:")
    for rank, idx in enumerate(sorted_idx[:8]):
        label = format(idx, f'0{n}b')
        p = best_all_probs[idx]
        bar = '█' * int(p * 60)
        is_solution = ' ← SOLUTION' if idx in [idx_01010, idx_10101] else ''
        print(f"    |{label}⟩: {p:.4f}  {bar}{is_solution}")

    if best_solution_prob > 4 * random_prob:
        print(f"\n  ✓ COLLAPSE SOLVES CONSTRAINT PROBLEM")
        print(f"  ✓ Solutions found at {best_solution_prob/(2*random_prob):.1f}x above random")
        print(f"  ✓ No gates, no oracle, no sequential operations")
    elif best_solution_prob > 2 * random_prob:
        print(f"\n  ~ PARTIAL: some bias toward solutions but not dominant")
    else:
        print(f"\n  ✗ No useful bias toward solutions")

    return best_solution_prob, 2 * random_prob


# ===========================================================================
# TEST E: SCALING — DOES IT GET BETTER OR WORSE WITH MORE QUBITS?
# ===========================================================================
def test_scaling():
    """
    Run the AFM chain problem at different qubit counts.
    Does collapse-based bias improve or degrade with scale?
    """
    print(f"\n{'=' * 70}")
    print("TEST E: SCALING — DOES COLLAPSE BIAS SCALE?")
    print("=" * 70)
    print("  Problem: AFM chain at various lengths")
    print("  Question: does the ground-state bias improve with more qubits?")

    g = 0.1
    results = []

    for n in [2, 3, 4, 5, 6, 7]:
        couplings = [(i, i+1, -g) for i in range(n-1)]
        H = make_dipolar_H(n, couplings)
        # Small bias on qubit 0
        ops = [I2]*n; ops[0] = sz
        H = H - 0.01 * g * qt.tensor(ops)

        eigenvalues, eigenstates = H.eigenstates()
        gs_probs = measure_probabilities(eigenstates[0], n)
        gs_idx = np.argmax(gs_probs)

        psi0 = equal_superposition(n)
        random_prob = 1.0 / (2**n)

        t_max = 4 * np.pi / g
        times = np.linspace(0, t_max, 300)
        result = qt.sesolve(H, psi0, times)

        best_prob = 0
        for psi_t in result.states:
            probs = measure_probabilities(psi_t, n)
            p = probs[gs_idx]
            if p > best_prob:
                best_prob = p

        enhancement = best_prob / random_prob
        results.append((n, best_prob, random_prob, enhancement))

        gs_label = format(gs_idx, f'0{n}b')
        print(f"  n={n}: ground=|{gs_label}⟩  "
              f"P_random={random_prob:.4f}  P_peak={best_prob:.4f}  "
              f"enhancement={enhancement:.1f}x")

    # Check scaling trend
    enhancements = [r[3] for r in results]
    improving = all(enhancements[i] <= enhancements[i+1]
                    for i in range(len(enhancements)-1))
    degrading = all(enhancements[i] >= enhancements[i+1]
                    for i in range(len(enhancements)-1))

    print(f"\n  Enhancement trend: ", end="")
    if improving:
        print("IMPROVING with scale ✓")
        print("  → More qubits = more geometric constraint = better collapse direction")
    elif degrading:
        print("DEGRADING with scale ✗")
        print("  → More qubits = more noise = weaker bias")
    else:
        print("NON-MONOTONIC")
        print("  → Complex relationship with qubit count")
        # Find if generally improving
        if enhancements[-1] > enhancements[0]:
            print("  → But overall trend is positive (larger > smaller)")
        else:
            print("  → Overall trend is negative")

    return results


# ===========================================================================
# RUN ALL TESTS
# ===========================================================================
if __name__ == "__main__":
    print()
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║  DSF-AI COLLAPSE-BASED QUANTUM COMPUTING — CAN IT WORK?            ║")
    print("║  No gates. No sequences. Geometry → Collapse → Answer.             ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    print()

    t0 = timer.time()

    bias, probs = test_collapse_2q()
    gs_prob, rand_prob = test_collapse_optimization()
    peak_prob, rand_prob_3 = test_collapse_speed()
    sol_prob, rand_sol = test_constraint_satisfaction()
    scaling = test_scaling()

    elapsed = timer.time() - t0

    print(f"\n{'=' * 70}")
    print("VERDICT: IS COLLAPSE-BASED COMPUTING VIABLE?")
    print("=" * 70)

    tests_passed = 0
    tests_total = 5

    if bias > 0.05:
        print(f"  A. 2-qubit collapse bias:        YES  (bias = {bias:.4f})")
        tests_passed += 1
    else:
        print(f"  A. 2-qubit collapse bias:        NO   (bias = {bias:.4f})")

    if gs_prob > 2 * rand_prob:
        print(f"  B. 4-qubit optimization:         YES  ({gs_prob/rand_prob:.1f}x random)")
        tests_passed += 1
    else:
        print(f"  B. 4-qubit optimization:         NO   ({gs_prob/rand_prob:.1f}x random)")

    if peak_prob > 2 * rand_prob_3:
        print(f"  C. Collapse speed:               YES  ({peak_prob/rand_prob_3:.1f}x random)")
        tests_passed += 1
    else:
        print(f"  C. Collapse speed:               NO   ({peak_prob/rand_prob_3:.1f}x random)")

    if sol_prob > 2 * rand_sol:
        print(f"  D. Constraint satisfaction:       YES  ({sol_prob/rand_sol:.1f}x random)")
        tests_passed += 1
    else:
        print(f"  D. Constraint satisfaction:       NO   ({sol_prob/rand_sol:.1f}x random)")

    enhancements = [r[3] for r in scaling]
    if enhancements[-1] > enhancements[0]:
        print(f"  E. Scaling trend:                POSITIVE")
        tests_passed += 1
    else:
        print(f"  E. Scaling trend:                NEGATIVE")

    print(f"\n  RESULT: {tests_passed}/{tests_total} tests passed")
    print(f"  Time: {elapsed:.2f} seconds")

    if tests_passed >= 4:
        print(f"\n  COLLAPSE-BASED COMPUTING IS VIABLE.")
        print(f"  Geometry directs collapse. No gates needed.")
        print(f"  The directed ion storm is real.")
    elif tests_passed >= 2:
        print(f"\n  PARTIALLY VIABLE.")
        print(f"  Some problems benefit, others don't.")
        print(f"  May need hybrid: collapse for structure, gates for precision.")
    else:
        print(f"\n  NOT VIABLE IN PURE FORM.")
        print(f"  Gate-based approach is necessary.")
        print(f"  Collapse alone doesn't reliably direct outcomes.")

    print()
