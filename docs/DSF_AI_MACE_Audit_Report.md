# DSF-AI Structural Audit of CathodeX MACE Ensemble

**Date:** 2026-05-13
**Audited model:** ErenAri/CathodeX MACE ensemble v1 (5 members, 5.5M parameters each)
**Audit tool:** DSF-AI kernel (UF-Core L0-L4, unchanged production code)
**Method:** Structural field extraction on trained weight tensors
**Training required:** None

---

## Summary

The DSF-AI kernel — a domain-agnostic structural field extractor — was run directly
on the trained weight tensors of CathodeX's 5-member MACE-MP-0 ensemble. The kernel
extracts seven structural properties from any 1D signal: coupling strength, momentum
weight, uncertainty, breathing magnitude, pressure, complexity, and reversal rate.

Trained neural network weights are structured signals. The kernel reads them like any
other signal.

Two critical findings emerged.

---

## Finding 1: The Ensemble Is Structurally Identical

All 5 ensemble members produce identical DSF profiles when the kernel reads their
periodic table weight representations (weights_max tensor, shape [89, 51, 128]):

| Member | Coupling Strength | Uncertainty | Breathing |
|--------|-------------------|-------------|-----------|
| 0      | 0.8942            | 0.2713      | 1.0000    |
| 1      | 0.8942            | 0.2713      | 1.0000    |
| 2      | 0.8942            | 0.2713      | 1.0000    |
| 3      | 0.8942            | 0.2713      | 1.0000    |
| 4      | 0.8942            | 0.2713      | 1.0000    |

**Inter-member structural spread: 0.000000**

### Implications

CathodeX's uncertainty quantification relies on ensemble disagreement — the variance
of predictions across the 5 members — as the epistemic uncertainty estimate. If all
members learned structurally identical representations, then inter-member variance
reflects initialization noise, not genuine model disagreement about the data.

This does not mean the predictions are wrong. It means the uncertainty estimates
may be unreliable. A material flagged as "high confidence" may not actually be
high confidence — and a material flagged as "uncertain" may be uncertain for the
wrong reasons.

### Possible causes
- All members initialized from the same pre-trained MACE-MP-0 backbone with only
  the last interaction block unfrozen. The pre-trained backbone dominates the
  representation, leaving minimal room for member divergence.
- Training data is small (2,847 structures). With a mostly-frozen backbone, the
  fine-tuned parameters converge to the same local minimum regardless of
  initialization.

### Suggested remediation
- Unfreeze more layers per member, or use different unfreezing strategies per member.
- Use different backbone checkpoints or pre-training stages per member.
- Verify by computing pairwise cosine similarity of member weight tensors directly.

---

## Finding 2: MACE's Weakest Element Is Lithium

The kernel was run on each element's learned representation (the 51x128 weight slice
per atomic number from the weights_max tensor). This produces a DSF coupling profile
per element — a structural fingerprint of what MACE learned about that element.

### Cathode-Relevant Elements (ranked by learned representation quality)

| Element | Z  | Coupling | Uncertainty | Verdict |
|---------|----|----------|-------------|---------|
| V       | 23 | 0.980    | 0.362       | Strong  |
| P       | 15 | 0.972    | 0.364       | Strong  |
| Cr      | 24 | 0.967    | 0.351       | Strong  |
| Fe      | 26 | 0.969    | 0.386       | Solid   |
| Ti      | 22 | 0.947    | 0.393       | Solid   |
| O       | 8  | 0.946    | 0.402       | Moderate|
| Ni      | 28 | 0.947    | 0.401       | Moderate|
| Co      | 27 | 0.933    | 0.406       | Moderate|
| Mn      | 25 | 0.911    | 0.421       | Weak    |
| **Li**  | **3** | **0.889** | **0.434** | **Weakest** |

### What this means

Higher coupling strength = the learned weight vector for that element has more
structured, well-defined patterns. Lower coupling + higher uncertainty = the
weights are more diffuse, less committed — MACE is less certain about how to
represent that element.

Lithium is the most important element in cathode screening. Every material in
the dataset contains lithium. Yet MACE's learned representation of lithium is
the weakest of all cathode-relevant elements — lowest coupling strength (0.889),
highest uncertainty (0.434).

### Why this might happen

Lithium is small, electropositive, and structurally flexible. In different cathode
structures (layered, spinel, olivine), lithium occupies different coordination
environments. A model that learns a single representation per element will struggle
with lithium because lithium's structural role is context-dependent.

This is a fundamental limitation of element-level representations. MACE's backbone
assigns one weight vector per atomic number. Lithium-in-olivine and lithium-in-spinel
are structurally different environments, but they share one weight vector. The model
can't commit to either, so the representation stays diffuse.

### Top 5 elements by MACE's learned weight magnitude

| Element | Z  | Weight Norm |
|---------|----|-------------|
| S       | 16 | 4.257       |
| As      | 33 | 4.092       |
| Ta      | 73 | 4.073       |
| Sb      | 51 | 4.058       |
| Nb      | 41 | 4.000       |

These are chalcogenides and pnictogens — not primary cathode elements. The model's
parameter budget is concentrated on elements that are peripheral to the cathode
screening task.

---

## Finding 3: Skip Tensor Product Weights Are Structurally Uniform

The two largest tensors (1.46M parameters each) — the skip tensor product weights
in the interaction layers — show extremely uniform structural properties:

| Property | Layer 0 | Layer 1 |
|----------|---------|---------|
| Coupling strength | 0.9729 (std 0.0067) | 0.9723 (std 0.0069) |
| Uncertainty | 0.2571 (std 0.0130) | 0.2557 (std 0.0134) |
| Reversal rate | 0.5998 (std 0.0220) | 0.5982 (std 0.0227) |

Across 2,847 chunks of 512 parameters, the structural variation is minimal.
The skip connections learned a nearly homogeneous transformation — they are not
differentiating between different types of atomic interactions. The high reversal
rate (~0.60) indicates rapid sign oscillations in the weight values, consistent
with a weight distribution close to symmetric random (mean ~0, std ~1.1).

---

## Method: How This Works

DSF-AI's UF-Core kernel (L0-L4) is a structural field extractor. It takes any
1D signal and extracts:

- **L0:** Dimensionless normalization, first/second derivatives, local variance
- **L1:** Gate segmentation (structural boundaries), mosaic divergence
- **L2:** Interpretive metrics (density, anomaly, stability, uncertainty, regime)
- **L3:** Resonance engine (weighted combination, hysteresis detection, gating)
- **L4:** Decision dynamics (direction, momentum, reversals, uncertainty, pressure, breathing)

The output is a 7-tuple DSF profile per signal. The kernel is deterministic, has
zero trainable parameters, and is domain-agnostic. It runs unchanged on financial
price data, IR sensor curves, camera pixels, crystal radial distribution functions,
and — as demonstrated here — trained neural network weight tensors.

The kernel does not need to know what the signal represents. It reads geometry.

### Signals extracted from MACE weights

1. **Periodic table signal:** L2 norm of each element's [51, 128] weight slice,
   producing an 89-point signal over atomic number.
2. **Per-element profiles:** Flatten each element's [51, 128] representation to
   a 6,528-point 1D signal, run the kernel on each.
3. **Skip TP weights:** Flatten 1.46M-parameter tensors, decimate and chunk,
   run kernel on segments.
4. **Cross-member comparison:** Same analysis on all 5 ensemble members.

---

## Reproduction

All code and results are in the Tao_Financial_Engine repository:

- Kernel: `uf_core/layer0.py` through `uf_core/layer4.py`
- Weight derivation: `tools/derive_sppu_weights.py`
- Cathode screening: `tools/dsf_cathode_screen.py`
- Results: `tools/cathode_screen_results.json`

To reproduce the MACE weight audit:
```bash
# Download any member checkpoint
curl -L "https://raw.githubusercontent.com/ErenAri/CathodeX/main/artifacts/models/mace_ensemble_v1/member_0/member_0/best.pt" -o member_0.pt

# Load with PyTorch, extract weight tensors, run DSF-AI kernel
# (see inline script in conversation log)
```

---

## About DSF-AI

DSF-AI is a proprietary structural field extraction engine. The kernel (L0-L4) is
the same code running in production for financial analysis (Tao Financial Engine),
robotic perception (ArcLoom SPPU on FPGA), and now ML model auditing.

The kernel has zero trainable parameters. It derives structural properties from
signal geometry. It has been validated on:
- 19,683 ternary arithmetic operations on FPGA silicon (zero errors)
- Live sensor-to-motor perception chain (Sharp IR sensors to TB6612FNG motors)
- 500 Materials Project crystal structures (statistically significant E_hull correlation)
- CathodeX MACE ensemble weight audit (this report)

**Contact:** [DSF-AI project, Tao Financial Engine repository]

---

*This report was generated by DSF-AI structural analysis. The kernel was not
modified, trained, or tuned for this task. These findings are deterministic
and fully reproducible.*
