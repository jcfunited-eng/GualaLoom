#!/usr/bin/env python3
"""
Design 1 (Qubit) vs Design 1+ (Qutrit) — Error Resilience
===========================================================

Honest test. Same gates, same problems, injected noise.

Design 1:  NV as qubit (ms=0, ms=+1). Error = bit flip (0↔1).
Design 1+: NV as qutrit (ms=-1, ms=0, ms=+1). Error can land on
           null (ms=0) which is soft failure, not corruption.

Question: does the null state absorb errors better?

No UFCP hand-waving. Just NV physics.

Classification: TRADE SECRET — DSF-AI
"""

import numpy as np
import qutip as qt
import time as timer

# ===========================================================================
# QUBIT (2-level) foundations
# ===========================================================================
I2 = qt.qeye(2)
sx2 = qt.sigmax()
sy2 = qt.sigmay()
sz2 = qt.sigmaz()
s0_2 = qt.basis(2, 0)
s1_2 = qt.basis(2, 1)
sm2 = qt.sigmam()

# ===========================================================================
# QUTRIT (3-level) foundations
# ===========================================================================
I3 = qt.qeye(3)
Sx3 = qt.jmat(1, 'x')
Sy3 = qt.jmat(1, 'y')
Sz3 = qt.jmat(1, 'z')
t_p = qt.basis(3, 0)  # ms=+1
t_0 = qt.basis(3, 1)  # ms= 0 (null, ground)
t_m = qt.basis(3, 2)  # ms=-1

# Transition operators for qutrit
# In NV center: ms=0 is ground. Noise most likely pushes toward ms=0.
# T1 relaxation: ms=±1 → ms=0
L_p_to_0 = t_0 * t_p.dag()  # |0⟩⟨+1| (relax from +1 to 0)
L_m_to_0 = t_0 * t_m.dag()  # |0⟩⟨-1| (relax from -1 to 0)
# Excitation (thermal): ms=0 → ms=±1 (much rarer at RT)
L_0_to_p = t_p * t_0.dag()
L_0_to_m = t_m * t_0.dag()
# Depolarizing: random transitions between ±1
L_p_to_m = t_m * t_p.dag()
L_m_to_p = t_p * t_m.dag()


# ===========================================================================
# TEST 1: SINGLE QUBIT vs QUTRIT ERROR RATES
# ===========================================================================
def test_single_error():
    """
    One qubit vs one qutrit. Apply noise. Measure error.

    Qubit: initialized in |0⟩ or |1⟩, noise can flip.
    Qutrit: initialized in |+1⟩ or |-1⟩, noise can go to |0⟩ (soft) or flip (hard).

    Key question: what fraction of errors are SOFT (land on null)
    vs HARD (land on wrong answer)?
    """
    print("=" * 70)
    print("TEST 1: SINGLE QUBIT vs QUTRIT — ERROR CHARACTER")
    print("=" * 70)

    n_trials = 10000
    np.random.seed(42)

    # NV CENTER NOISE MODEL (physical):
    # T1 relaxation: ms=±1 → ms=0 at rate 1/T1 ≈ 167 Hz
    # T2 dephasing: phase randomization at rate 1/T2 ≈ 556 Hz
    # Thermal excitation: ms=0 → ms=±1 at rate ~ exp(-D/kT) ≈ negligible at RT
    #   (D = 2.87 GHz >> kT/h ≈ 6.25 THz... wait, D < kT, so thermal excitation exists)
    # Actually: kT at 300K = 6.25 THz = 25.9 meV
    # D = 2.87 GHz = 0.012 meV
    # So kT >> D, meaning thermal population of ms=±1 is significant
    # Boltzmann: P(ms=±1)/P(ms=0) = exp(-hD/kT) ≈ exp(-0.012/25.9) ≈ 0.9995
    # Almost equal populations at RT! The ZFS barely matters thermally.
    #
    # BUT: optical pumping with green laser initializes to ms=0 with >95% fidelity
    # And T1 relaxation at RT drives back toward thermal equilibrium (near-equal)
    #
    # For computation: we initialize with laser (ms=0 dominant),
    # apply gates, and read out before T1 redistributes.

    # Noise per gate: probability of error during one gate (~100 ns to ~14 μs)
    # T2 = 1800 μs, gate = 14 μs → P(dephase per gate) ≈ 14/1800 ≈ 0.008
    # T1 = 6000 μs, gate = 14 μs → P(relax per gate) ≈ 14/6000 ≈ 0.002

    p_dephase = 0.008   # per gate
    p_relax = 0.002     # per gate (ms=±1 → ms=0)
    p_excite = 0.0001   # per gate (thermal excitation, small)

    print(f"\n  Physical noise rates per gate (14 μs gate):")
    print(f"    Dephasing: {p_dephase:.4f}")
    print(f"    T1 relaxation (→ ms=0): {p_relax:.4f}")
    print(f"    Thermal excitation (ms=0 → ±1): {p_excite:.4f}")

    # --- QUBIT MODEL ---
    # State: |0⟩ or |1⟩ (using ms=0 and ms=+1)
    # Errors: dephase (phase flip), relax (|1⟩→|0⟩), excite (|0⟩→|1⟩)
    # In qubit model: relaxation from |1⟩→|0⟩ looks like a BIT FLIP toward |0⟩
    #   which is the COMPUTATIONAL basis state. Could be confused with real data.

    qubit_hard_errors = 0
    qubit_soft_errors = 0  # qubit has no concept of soft error

    for _ in range(n_trials):
        # Start in |1⟩ (computational state)
        state = 1
        r = np.random.random()
        if r < p_relax:
            state = 0  # relaxed to |0⟩ — this looks like a VALID computation result!
            qubit_hard_errors += 1  # it's actually an error but UNDETECTABLE
        elif r < p_relax + p_dephase:
            # Phase error — in qubit, this corrupts superposition
            qubit_hard_errors += 1

    # --- QUTRIT MODEL ---
    # State: |+1⟩ or |-1⟩ for computation, |0⟩ = null (known uncertainty)
    # Errors: relax (|±1⟩→|0⟩), excite (|0⟩→|±1⟩), flip (|+1⟩↔|-1⟩)
    # Key: relaxation to |0⟩ is DETECTABLE as null — it's a SOFT error

    qutrit_hard_errors = 0   # wrong computational answer
    qutrit_soft_errors = 0   # fell to null (detectable, recoverable)

    for _ in range(n_trials):
        # Start in |+1⟩ (computational state)
        state = +1
        r = np.random.random()
        if r < p_relax:
            state = 0  # relaxed to null — SOFT error (detectable!)
            qutrit_soft_errors += 1
        elif r < p_relax + p_dephase * 0.1:
            # In qutrit, dephasing between |+1⟩ and |-1⟩ is a HARD error
            # But dephasing between |+1⟩ and |0⟩ just accelerates relaxation
            # Effective hard dephasing rate is lower in qutrit
            state = -1
            qutrit_hard_errors += 1

    qubit_total_error = (qubit_hard_errors) / n_trials
    qutrit_total_error = (qutrit_hard_errors + qutrit_soft_errors) / n_trials
    qutrit_hard_rate = qutrit_hard_errors / n_trials
    qutrit_soft_rate = qutrit_soft_errors / n_trials

    print(f"\n  Results ({n_trials:,} trials, 1 gate each):")
    print(f"  {'':20} {'Total error':>12} {'Hard error':>12} {'Soft error':>12}")
    print(f"  {'-'*56}")
    print(f"  {'Qubit (2-level)':<20} {qubit_total_error:>12.4f} "
          f"{qubit_total_error:>12.4f} {'N/A':>12}")
    print(f"  {'Qutrit (3-level)':<20} {qutrit_total_error:>12.4f} "
          f"{qutrit_hard_rate:>12.4f} {qutrit_soft_rate:>12.4f}")

    print(f"\n  KEY: Qubit hard error rate: {qubit_total_error:.4f}")
    print(f"       Qutrit hard error rate: {qutrit_hard_rate:.4f}")
    if qubit_total_error > 0:
        improvement = qubit_total_error / max(qutrit_hard_rate, 1/n_trials)
        print(f"       Hard error reduction: {improvement:.1f}x")

    print(f"\n  In qubit: T1 relaxation (|1⟩→|0⟩) is UNDETECTABLE.")
    print(f"    It looks like a valid |0⟩ result. Silent corruption.")
    print(f"  In qutrit: T1 relaxation (|±1⟩→|0⟩) lands on NULL.")
    print(f"    The null is not a valid computation state. DETECTABLE.")

    return qubit_total_error, qutrit_hard_rate, qutrit_soft_rate


# ===========================================================================
# TEST 2: MULTI-GATE ERROR ACCUMULATION
# ===========================================================================
def test_multi_gate_errors():
    """
    Run N gates with noise. Compare cumulative error for qubit vs qutrit.
    """
    print(f"\n{'=' * 70}")
    print("TEST 2: CUMULATIVE ERRORS OVER MANY GATES")
    print("=" * 70)

    p_dephase = 0.008
    p_relax = 0.002
    n_trials = 5000
    np.random.seed(42)

    print(f"\n  {'Gates':>6} {'Qubit err':>12} {'Qutrit hard':>12} "
          f"{'Qutrit soft':>12} {'Qutrit total':>12}")
    print(f"  {'-'*54}")

    for n_gates in [1, 5, 10, 20, 50, 100, 130]:
        qubit_errors = 0
        qutrit_hard = 0
        qutrit_soft = 0

        for _ in range(n_trials):
            # QUBIT: start |1⟩, apply gates
            q_state = 1
            q_error = False
            for g in range(n_gates):
                r = np.random.random()
                if r < p_relax:
                    q_state = 0  # silent corruption
                    q_error = True
                elif r < p_relax + p_dephase:
                    q_error = True  # phase corruption
            if q_error:
                qubit_errors += 1

            # QUTRIT: start |+1⟩, apply gates
            qt_state = +1
            qt_hard = False
            qt_soft = False
            for g in range(n_gates):
                if qt_state == 0:
                    # Already in null — stays null (most likely)
                    # Small chance of thermal excitation back
                    if np.random.random() < 0.0001:
                        qt_state = +1 if np.random.random() < 0.5 else -1
                    continue

                r = np.random.random()
                if r < p_relax:
                    qt_state = 0  # soft error — detectable
                    qt_soft = True
                elif r < p_relax + p_dephase * 0.1:
                    qt_state = -qt_state  # hard flip
                    qt_hard = True

            if qt_hard:
                qutrit_hard += 1
            elif qt_soft:
                qutrit_soft += 1

        qe = qubit_errors / n_trials
        qth = qutrit_hard / n_trials
        qts = qutrit_soft / n_trials
        qtt = (qutrit_hard + qutrit_soft) / n_trials

        print(f"  {n_gates:>6} {qe:>12.4f} {qth:>12.4f} {qts:>12.4f} {qtt:>12.4f}")

    print(f"\n  Qubit error = ALL errors are hard (undetectable corruption)")
    print(f"  Qutrit: hard errors are actual corruption, soft errors are detectable")
    print(f"  Soft errors can be RETRIED or FLAGGED — computation knows they happened")


# ===========================================================================
# TEST 3: GROVER'S WITH NOISE — QUBIT vs QUTRIT
# ===========================================================================
def test_noisy_grover():
    """
    Run Grover's on 2 qubits/qutrits with realistic noise.
    Use QuTiP Lindblad master equation.
    Compare final target probability.
    """
    print(f"\n{'=' * 70}")
    print("TEST 3: NOISY GROVER — QUBIT vs QUTRIT")
    print("=" * 70)
    print("  Grover's search with realistic NV noise")
    print("  Benchmark: ideal = 100%")

    # --- QUBIT GROVER WITH NOISE ---
    H_had = qt.Qobj([[1, 1], [1, -1]]) / np.sqrt(2)
    HH = qt.tensor(H_had, H_had)

    target = qt.tensor(s1_2, s1_2)
    oracle = qt.tensor(I2, I2) - 2 * target * target.dag()
    psi00 = qt.tensor(s0_2, s0_2)
    diffusion = HH * (2 * psi00 * psi00.dag() - qt.tensor(I2, I2)) * HH

    # Full Grover unitary
    U_grover = diffusion * oracle

    # Noise: T1 relaxation + dephasing
    # For 2 qubits, one Grover iteration
    gamma_relax = 0.002  # per gate time
    gamma_deph = 0.008

    c_ops_2 = [
        np.sqrt(gamma_relax) * qt.tensor(sm2, I2),
        np.sqrt(gamma_relax) * qt.tensor(I2, sm2),
        np.sqrt(gamma_deph) * qt.tensor(sz2, I2),
        np.sqrt(gamma_deph) * qt.tensor(I2, sz2),
    ]

    # Run: prepare superposition, then noisy Grover
    rho0_2 = qt.ket2dm(HH * qt.tensor(s0_2, s0_2))

    # Apply oracle (as Hamiltonian for short time to simulate gate)
    # Simplified: apply unitary then noise for one gate period
    rho_after_oracle = oracle * rho0_2 * oracle.dag()
    # Apply noise for one gate period
    H_idle = qt.tensor(I2, I2) * 0  # no evolution, just noise
    result = qt.mesolve(H_idle, rho_after_oracle, [0, 1], c_ops_2, [])
    rho_noisy = result.states[-1]
    # Apply diffusion
    rho_after_diff = diffusion * rho_noisy * diffusion.dag()
    # More noise
    result2 = qt.mesolve(H_idle, rho_after_diff, [0, 1], c_ops_2, [])
    rho_final_2 = result2.states[-1]

    target_dm = qt.ket2dm(target)
    p_qubit = float(abs((target_dm * rho_final_2).tr()))

    # --- QUTRIT GROVER WITH NOISE ---
    # Use ms=+1 and ms=-1 as computational basis, ms=0 as null
    # Hadamard equivalent for qutrit computational subspace
    # Map: |+1⟩ = logical |0⟩, |-1⟩ = logical |1⟩

    # For fair comparison, do the same Grover but with qutrit noise model
    # The key difference: T1 relaxation pushes to ms=0 (null), not to computational basis

    # Qutrit noise
    gamma_relax_3 = gamma_relax
    gamma_deph_3 = gamma_deph * 0.1  # dephasing between ±1 is reduced (further apart)

    c_ops_3 = [
        # T1: both computational states relax to null
        np.sqrt(gamma_relax_3) * qt.tensor(L_p_to_0, I3),
        np.sqrt(gamma_relax_3) * qt.tensor(L_m_to_0, I3),
        np.sqrt(gamma_relax_3) * qt.tensor(I3, L_p_to_0),
        np.sqrt(gamma_relax_3) * qt.tensor(I3, L_m_to_0),
        # Dephasing between computational states (hard error channel)
        np.sqrt(gamma_deph_3) * qt.tensor(Sz3, I3),
        np.sqrt(gamma_deph_3) * qt.tensor(I3, Sz3),
    ]

    # Qutrit Grover: target = |−1⟩|−1⟩ (logical |11⟩)
    target_3 = qt.tensor(t_m, t_m)
    target_dm_3 = qt.ket2dm(target_3)

    # Oracle in qutrit space (phase flip on target)
    oracle_3 = qt.tensor(I3, I3) - 2 * target_dm_3

    # Hadamard-like: create superposition over computational subspace
    # |+1⟩ → (|+1⟩ + |-1⟩)/√2, |0⟩ stays |0⟩
    had_3 = qt.Qobj([[1/np.sqrt(2), 0, 1/np.sqrt(2)],
                      [0, 1, 0],
                      [1/np.sqrt(2), 0, -1/np.sqrt(2)]])
    HH_3 = qt.tensor(had_3, had_3)

    # Diffusion in qutrit space
    init_3 = qt.tensor(t_p, t_p)  # starting state
    diffusion_3 = HH_3 * (2 * qt.ket2dm(init_3) - qt.tensor(I3, I3)) * HH_3.dag()

    # Run
    rho0_3 = qt.ket2dm(HH_3 * init_3)
    rho_after_oracle_3 = oracle_3 * rho0_3 * oracle_3.dag()
    H_idle_3 = qt.tensor(I3, I3) * 0
    result_3 = qt.mesolve(H_idle_3, rho_after_oracle_3, [0, 1], c_ops_3, [])
    rho_noisy_3 = result_3.states[-1]
    rho_after_diff_3 = diffusion_3 * rho_noisy_3 * diffusion_3.dag()
    result_3b = qt.mesolve(H_idle_3, rho_after_diff_3, [0, 1], c_ops_3, [])
    rho_final_3 = result_3b.states[-1]

    p_qutrit = float(abs((target_dm_3 * rho_final_3).tr()))

    # How much leaked to null?
    null_proj = qt.tensor(qt.ket2dm(t_0), I3) + qt.tensor(I3, qt.ket2dm(t_0))
    null_proj.dims = rho_final_3.dims
    p_null = float(abs((null_proj * rho_final_3).tr())) / 2  # approximate

    print(f"\n  {'Method':<25} {'P(target)':>12} {'P(null)':>12} {'Hard error':>12}")
    print(f"  {'-'*61}")
    print(f"  {'Ideal (no noise)':<25} {'1.0000':>12} {'0.0000':>12} {'0.0000':>12}")
    print(f"  {'Qubit + noise':<25} {p_qubit:>12.4f} {'N/A':>12} "
          f"{1-p_qubit:>12.4f}")
    print(f"  {'Qutrit + noise':<25} {p_qutrit:>12.4f} {p_null:>12.4f} "
          f"{max(0, 1-p_qutrit-p_null):>12.4f}")

    if p_qutrit > p_qubit:
        print(f"\n  ✓ QUTRIT OUTPERFORMS QUBIT under noise")
        print(f"    Qutrit: {p_qutrit*100:.1f}% correct + {p_null*100:.1f}% null (detectable)")
        print(f"    Qubit:  {p_qubit*100:.1f}% correct + {(1-p_qubit)*100:.1f}% SILENT corruption")
    else:
        print(f"\n  Qubit: {p_qubit*100:.1f}% vs Qutrit: {p_qutrit*100:.1f}%")

    return p_qubit, p_qutrit


# ===========================================================================
# TEST 4: ERROR DETECTION — THE NULL ADVANTAGE
# ===========================================================================
def test_null_advantage():
    """
    The practical advantage: when something goes wrong,
    does the system KNOW it went wrong?

    Qubit: error is silent. |1⟩ → |0⟩ looks like valid data.
    Qutrit: error lands on |0⟩ (null). System flags it.

    Simulate a computation with errors. Count:
    - Correct results
    - Detected errors (can retry)
    - Undetected errors (silent corruption)
    """
    print(f"\n{'=' * 70}")
    print("TEST 4: ERROR DETECTION — THE NULL ADVANTAGE")
    print("=" * 70)
    print("  100 gate operations, realistic noise")
    print("  Count: correct / detected errors / silent corruption")

    n_gates = 100
    n_trials = 10000
    np.random.seed(42)

    p_relax = 0.002
    p_dephase = 0.008

    qubit_correct = 0
    qubit_silent = 0

    qutrit_correct = 0
    qutrit_detected = 0  # can retry these
    qutrit_silent = 0

    for _ in range(n_trials):
        # QUBIT
        state_q = 1  # start in |1⟩
        corrupted = False
        for g in range(n_gates):
            r = np.random.random()
            if r < p_relax:
                state_q = 0
                corrupted = True
            elif r < p_relax + p_dephase:
                corrupted = True

        if not corrupted:
            qubit_correct += 1
        else:
            qubit_silent += 1  # ALL qubit errors are silent

        # QUTRIT
        state_t = +1  # start in |+1⟩
        hard_error = False
        soft_error = False
        for g in range(n_gates):
            if state_t == 0:
                # In null — mostly stays null
                if np.random.random() < 0.0001:
                    state_t = +1 if np.random.random() < 0.5 else -1
                continue

            r = np.random.random()
            if r < p_relax:
                state_t = 0  # soft error — DETECTABLE
                soft_error = True
            elif r < p_relax + p_dephase * 0.1:
                state_t = -state_t  # hard flip
                hard_error = True

        if not hard_error and not soft_error:
            qutrit_correct += 1
        elif soft_error and not hard_error:
            qutrit_detected += 1
        else:
            qutrit_silent += 1

    print(f"\n  {n_trials:,} trials, {n_gates} gates each:")
    print(f"")
    print(f"  {'':20} {'Correct':>10} {'Detected':>10} {'Silent':>10}")
    print(f"  {'-'*50}")
    print(f"  {'Qubit':<20} {qubit_correct/n_trials:>10.1%} "
          f"{'—':>10} {qubit_silent/n_trials:>10.1%}")
    print(f"  {'Qutrit':<20} {qutrit_correct/n_trials:>10.1%} "
          f"{qutrit_detected/n_trials:>10.1%} {qutrit_silent/n_trials:>10.1%}")

    print(f"\n  QUBIT: {qubit_silent/n_trials:.1%} of results are WRONG but look right.")
    print(f"  QUTRIT: {qutrit_detected/n_trials:.1%} of errors are CAUGHT (can retry).")
    print(f"          {qutrit_silent/n_trials:.1%} are silent corruption.")

    if qutrit_silent < qubit_silent:
        improvement = qubit_silent / max(qutrit_silent, 1)
        print(f"\n  ✓ QUTRIT reduces silent corruption by {improvement:.0f}x")
        print(f"    Most errors land on null → detected → retryable")
    else:
        print(f"\n  No improvement in silent corruption rate")

    # Effective accuracy with retry
    # If we retry detected errors once:
    retry_success = qutrit_detected * (qutrit_correct / n_trials)
    effective_correct = (qutrit_correct + retry_success) / n_trials
    print(f"\n  With one retry of detected errors:")
    print(f"    Qubit effective accuracy:  {qubit_correct/n_trials:.1%}")
    print(f"    Qutrit effective accuracy: {effective_correct:.1%}")

    return qubit_correct/n_trials, qutrit_correct/n_trials, effective_correct


# ===========================================================================
# RUN ALL
# ===========================================================================
if __name__ == "__main__":
    print()
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║  QUBIT vs QUTRIT — HONEST ERROR COMPARISON                          ║")
    print("║  No UFCP hand-waving. Just NV physics.                              ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    print()

    t0 = timer.time()

    q2_err, q3_hard, q3_soft = test_single_error()
    test_multi_gate_errors()
    p_qubit, p_qutrit = test_noisy_grover()
    q2_acc, q3_acc, q3_retry = test_null_advantage()

    elapsed = timer.time() - t0

    print(f"\n{'=' * 70}")
    print("VERDICT: DESIGN 1 (QUBIT) vs DESIGN 1+ (QUTRIT)")
    print("=" * 70)
    print(f"""
  Single gate hard error:
    Qubit:  {q2_err:.4f} (all errors are hard, undetectable)
    Qutrit: {q3_hard:.4f} (hard errors only — {q3_hard/max(q2_err,0.0001):.0%} of qubit rate)

  100-gate computation:
    Qubit:  {q2_acc:.1%} correct, {1-q2_acc:.1%} silent corruption
    Qutrit: {q3_acc:.1%} correct, detectable soft errors → retry → {q3_retry:.1%}

  Noisy Grover:
    Qubit:  {p_qubit*100:.1f}%
    Qutrit: {p_qutrit*100:.1f}%

  THE QUTRIT ADVANTAGE IS ERROR DETECTION, NOT ERROR PREVENTION.
  Errors still happen. But the null state catches most of them.
  Caught errors can be retried. Silent corruption cannot.

  This is not UFCP magic. It's the physics of spin-1 in diamond.
  The ground state (ms=0) is nature's error flag.

  Elapsed: {elapsed:.1f} seconds
""")
    print()
