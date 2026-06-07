# ArcLoom SPPU — Competitive Landscape Analysis

**Date:** 2026-05-13
**Version:** 1.0
**Classification:** Internal — DARPA/Patent Preparation
**Author:** Joseph Forrester / DSF-AI Architecture

---

## Purpose

This document surveys all known ternary computing systems, clockless perception
hardware, structural memory architectures, and related work. Its purpose is to
establish that ArcLoom occupies a unique position in the landscape and to prepare
clear distinctions for DARPA pitch, Efabless submission, and patent prosecution.

---

## 1. Ternary Computing Hardware

### 1.1 Huawei Ternary Logic Gate (2025)

- **What:** Patent CN119652311A for ternary logic gates using threshold voltage
  layering on CNTFET. Claims 40% fewer transistors, 60% less power.
- **Ternary type:** Standard (0, 1, 2) — NOT balanced.
- **Hardware status:** Patent filing. Unclear if silicon exists.
- **Computing model:** Sequential instruction execution with 3-state gates.
- **ArcLoom distinction:** Huawei improved the transistor. The computing model
  is unchanged — fetch/decode/execute with a clock. Standard ternary (0,1,2)
  lacks the symmetric negation property of balanced ternary (-1,0,+1). The
  SPPU's combinational settling through signed coupling is architecturally
  impossible in Huawei's number system. (See ASIC Spec v1.2, Section 10.2.1.)

### 1.2 5500FP Ternary RISC Processor (2026)

- **What:** 24-trit balanced ternary RISC processor on Efinix Trion T120F484
  FPGA. 120-instruction ISA. Open hardware.
- **Ternary type:** Balanced (-1, 0, +1).
- **Hardware status:** Running on FPGA. No custom silicon.
- **Computing model:** Von Neumann RISC — fetch, decode, execute, store.
- **ArcLoom distinction:** The 5500FP treats trits as numbers in registers.
  ArcLoom treats them as coupled physical states in a field. The null trit
  in 5500FP is arithmetic zero. In SPPU, it is structural uncertainty — the
  system's admission that coupling pressure is insufficient to commit this
  dimension. The 5500FP validates that balanced ternary works on FPGA; ArcLoom
  builds a different computational model on top of it.
  (See ASIC Spec v1.2, Section 10.2.2.)

### 1.3 Microsoft BitNet b1.58 (2024-2026)

- **What:** LLM with ternary weight quantization {-1, 0, +1}. 2B parameter
  model. Open-source inference engine.
- **Ternary type:** Ternary VALUES on binary HARDWARE. Not ternary computing.
- **Hardware status:** Runs on standard x86 CPUs. No custom hardware.
- **Computing model:** Trained neural network inference.
- **ArcLoom distinction:** BitNet uses ternary as a compression trick —
  reducing model weight storage from 16-bit floats to 1.58-bit trits. The
  processor is entirely binary. The computation is still matrix multiplication
  (simplified to add/subtract). ArcLoom uses balanced ternary as the native
  computational substrate. The coupling fabric IS the computation. No matrix
  multiplication. No training. No inference.

### 1.4 TCN-CUTIE / CUTIE (ETH Zurich, 2022)

- **What:** Fabricated ASIC (GlobalFoundries 22nm) for ternary neural network
  acceleration. 1,036 TOp/s/W efficiency.
- **Ternary type:** Ternary weights, binary logic. The chip is a binary
  accelerator optimized for ternary-quantized weight matrices.
- **Hardware status:** Real silicon. Production-grade.
- **ArcLoom distinction:** TCN-CUTIE is a binary chip that processes ternary
  data. ArcLoom is a ternary chip that perceives through coupling. TCN-CUTIE
  requires trained neural network weights. ArcLoom derives weights from sensor
  physics with zero training.

### 1.5 TerEffic (2025)

- **What:** FPGA architecture for ternary LLM inference. 16,300 tokens/second.
- **Ternary type:** Ternary weight encoding on binary FPGA.
- **ArcLoom distinction:** Same as BitNet — ternary data, binary hardware,
  trained model. ArcLoom is native ternary logic, no training.

### 1.6 Tiny Tapeout Balanced Ternary Calculator (USN Group)

- **What:** 2-trit balanced ternary calculator (add/subtract/multiply) taped
  out on Skywater 130nm through Tiny Tapeout 03. Follow-up REBEL-2 ALU on TT05.
- **Ternary type:** Balanced (-1, 0, +1). Binary-Encoded Ternary on CMOS.
- **Hardware status:** Real silicon (Tiny Tapeout shuttle).
- **ArcLoom distinction:** REBEL-2 does add/sub/mul. MathLoom does all of those
  PLUS folding division (41,430 tests, zero errors) with native free rounding
  via truncation. Nobody else has verified balanced ternary division on hardware.
  More fundamentally, REBEL-2 is a standalone ALU. MathLoom exists only at I/O
  boundaries of the SPPU — the perception path has no ALU at all.

### 1.7 Carbon Nanotube Ternary Logic (Science Advances, Jan 2025)

- **What:** CNT source-gating transistors with native 3-state switching.
  Ternary inverters, NMIN/NMAX gates, ternary SRAM, ternary neural network.
- **Hardware status:** Lab-scale fabricated devices. Not a system.
- **ArcLoom distinction:** Individual ternary gates, not an architecture.
  Their ternary neural network is trained. ArcLoom is a complete perception
  system from sensor to motor, training-free.

### 1.8 USN Ternary Research Group (University of South-Eastern Norway)

- **What:** Academic research group building EDA tools for ternary VLSI.
  Mixed Radix Circuit Synthesizer (MRCS). Founded 2019.
- **Hardware status:** EDA tools and simulation. No fabricated chips.
- **ArcLoom distinction:** USN builds the tools to design ternary chips.
  ArcLoom IS a ternary chip (on FPGA, ASIC spec'd). Complementary, not
  competing. Potential collaboration for ArcLoom-256 tape-out.

### 1.9 Historical: Setun (Moscow State University, 1958)

- **What:** First and only mass-produced balanced ternary computer. ~50 units.
- **ArcLoom distinction:** Setun was a general-purpose computer that happened
  to use balanced ternary. It validated the number system. It did not explore
  coupling, perception, or the null trit as structural uncertainty. Discontinued
  for political reasons, not technical ones.

### 1.10 TCAM (Cisco, Broadcom — Production)

- **What:** Ternary Content-Addressable Memory in network routers. Three states:
  0, 1, X (don't care). Massively deployed.
- **ArcLoom distinction:** TCAM's third state is a wildcard mask for pattern
  matching, not a computational state. TCAM does lookup, not logic. The
  "ternary" in TCAM has nothing in common with balanced ternary computing.

---

## 2. Clockless / Asynchronous Perception Hardware

### 2.1 Intel Loihi 2

- **What:** 128 asynchronous neuron cores on Intel 4 process. Spiking neural
  network processor. Sensor fusion demonstrated (radar, vision, lidar).
- **ArcLoom distinction:** Loihi runs trained spiking neural networks on async
  hardware. The hardware is clockless; the computation is ML. SPPU is
  combinational — no spikes, no neurons, no training, no iteration. The answer
  settles through wire propagation in ~5 ns.

### 2.2 BrainChip Akida (AKD1500)

- **What:** Event-driven digital processor. 800 GOPS at <300mW. Gesture
  recognition demonstrated with Prophesee event camera.
- **ArcLoom distinction:** Akida runs Temporal Event-based Neural Networks
  (TENNs). Event-driven hardware, ML algorithms. SPPU has no neural network
  of any kind.

### 2.3 SpiNNaker2 (TU Dresden)

- **What:** 153 ARM cores with async event routing. 22nm FDSOI. Deployed at
  Sandia National Labs.
- **ArcLoom distinction:** SpiNNaker2 is a massively parallel ARM cluster for
  spiking neural network simulation. It has 153 clocked ARM cores connected
  by async routing. SPPU has zero clocked cores and zero neural networks.

### 2.4 Prophesee GenX320 (Event Camera)

- **What:** 320x320 event camera where each pixel fires independently and
  asynchronously. 10,000 FPS equivalent. >140dB dynamic range.
- **ArcLoom distinction:** Prophesee is an async sensor, not an async
  processor. Interesting as a future BSIL input source — event-driven pixels
  feeding directly into the SPPU's combinational fabric. Complementary.

### 2.5 Gap Analysis

Every existing clockless/async processor runs trained neural networks. The
async fabric is the delivery mechanism; the computation is still ML.

Nobody has: purely combinational perception where the answer settles through
coupling constraints with no spikes, no neurons, no weights learned from data,
and no iteration. The SPPU is unique in this category.

---

## 3. Content-Addressable Structural Memory (Krimelack)

### 3.1 Existing CAM Technology

All deployed CAMs (TCAM in routers, memristor CAMs, ferroelectric CAMs) do
bit-level or weight-level matching. They store addresses, keys, or feature
vectors. None store structural motifs — coupled multi-field patterns that
represent a settled loom state.

### 3.2 Memristor Habituation (Nature Communications, 2025)

- **What:** Third-order memristor (HfO2+TiOx) with physical habituation.
  Robot arm ignores 71% of familiar stimuli while responding to threats.
  Non-volatile habituation survives power loss.
- **ArcLoom distinction:** This is the closest existing work to Krimelack's
  habituation mechanism. The difference: memristor habituation is analog,
  per-synapse, and embedded in a trained SNN. Krimelack habituation is digital,
  pattern-level (full loom state), and operates through combinational dead-zone
  feedback. The memristor habituates individual connections. Krimelack
  habituates entire structural experiences.

### 3.3 Gap Analysis

No existing hardware combines: (a) content-addressable structural motif storage,
(b) cue-based recall from partial signatures, (c) pattern-level habituation via
dead-zone feedback, and (d) autonomous commit gating based on dimensional
exhaustion (L6 structural lock). Each piece exists in isolation somewhere.
The combination is unique to Krimelack.

---

## 4. Balanced Ternary Arithmetic (MathLoom)

### 4.1 REBEL-2 (USN Group, Tiny Tapeout 05)

- **What:** Balanced ternary ALU with MIN, MAX, ADD, SUB, MUL, CMP, SHFT.
  Submitted for ASIC fabrication on Skywater 130nm.
- **MathLoom distinction:** REBEL-2 does not implement division. MathLoom's
  folding division — verified with 41,430 tests (integer, complex, matrix,
  polynomial) at zero errors — has no equivalent in any balanced ternary
  hardware. The native free rounding property (truncation = rounding in
  balanced ternary) is exploited as a design feature in MathLoom but is not
  used in REBEL-2's operations.

### 4.2 Georgia Tech Discrete ALU (Louis Duret-Robert)

- **What:** 2-trit balanced ternary ALU from discrete CD4007 CMOS chips.
- **MathLoom distinction:** Proof of concept on discrete components. Not
  integrated. No division. No verification suite.

### 4.3 Gap Analysis

MathLoom's unique claims:
1. Folding division with native free rounding — no prior art
2. Exact 1/3 representation exploited as design feature — no prior art
3. Computational completeness proven (complex, matrix, polynomial, trig)
4. 41,430 verification tests + 18 silicon tests at zero errors
5. Positioned as I/O boundary arithmetic, not central ALU

---

## 5. Structural Perception Without ML

### 5.1 Hyperdimensional Computing (UC San Diego, UC Berkeley, ETH Zurich)

- **What:** Encodes sensor data into high-dimensional binary vectors. Does
  similarity matching via dot products. HyperSense (2024) does real-time
  raw sensor processing on FPGA. GraspHD (2024) does robotic grasping.
- **ArcLoom distinction:** HDC encodes deterministically but classifies with
  a trained model. The encoding is training-free; the decision is not. SPPU
  is training-free end-to-end — from sensor to motor. HDC operates in
  high-dimensional binary space. SPPU operates in low-dimensional balanced
  ternary space where the null state is a first-class computational primitive.

### 5.2 Ternary Spike-Based SNN (Neural Networks journal, 2025)

- **What:** Threshold-adaptive encoding converts analog to ternary spikes.
  QT-SNN processes with quantized ternary weights. Speech and EEG recognition.
- **ArcLoom distinction:** Trained spiking neural network with ternary encoding.
  Not structural perception. Not combinational. Not training-free.

### 5.3 Gap Analysis

The following concepts return zero results in the literature:
- "Coupling weights" as a perception mechanism
- "Dimensional exhaustion" as a detection principle
- "Geometric inevitability" in hardware
- Perception that settles via coupling constraints without iteration or training
- 3^i positional weights as structural decoders in a perception fabric

ArcLoom's computational model — combinational settling through signed ternary
coupling with dead-zone thresholding — has no prior art.

---

## 6. Dead Zone / Null State Computing

### 6.1 Three-Valued Logic

Kleene and Lukasiewicz three-valued logics are well-established in formal logic.
Hardware implementations exist (TDDFET gates, memristive circuits, Huawei patent).
In all cases, the third state represents "unknown" or "high-impedance" — a
failure to resolve.

### 6.2 ArcLoom Distinction

In the SPPU, the null trit is not "unknown." It is "the coupling field has
insufficient energy to collapse this dimension." This is an active computational
state with specific consequences:

- It contributes zero to downstream coupling (multiplicative silence)
- It can be created by habituation (Krimelack dead-zone feedback)
- It can be created by insufficient input (sensor ambiguity)
- It is counted by L6 to detect dimensional exhaustion
- It can flip to committed (+1 or -1) when coupling pressure increases

No prior ternary architecture treats the null state as structural uncertainty
with these computational properties.

---

## 7. Summary: What ArcLoom Has That Nobody Else Has

| Capability | Nearest Prior Art | Gap |
|---|---|---|
| Combinational ternary perception | Loihi 2 (async SNN) | No ML, no spikes, no clock |
| 3^i positional coupling weights | None | No prior art |
| Null trit as structural uncertainty | Three-valued logic | Not used as active computation |
| Krimelack structural motif memory | Memristor habituation | Not CAM, not pattern-level, not combinational |
| Folding division with native rounding | REBEL-2 (add/sub/mul only) | No division anywhere |
| L6 dimensional exhaustion detection | None | No prior art |
| Clockless habituation via dead-zone feedback | None | No prior art |
| Sensor-to-motor ternary perception chain | None | No prior art |
| Training-free embodied cognition | HDC (trains classifier) | End-to-end training-free |
| Autonomous obstacle navigation on ternary hardware | None | No prior art |

---

## 8. Potential Allies / Collaborators

| Entity | What They Have | How They Help ArcLoom |
|---|---|---|
| USN Ternary Research Group | EDA tools (MRCS) | Synthesis and verification for tape-out |
| Prophesee | Event cameras (GenX320) | Async sensor input for SPPU |
| Efabless | Shuttle runs (Skywater 130nm, GF180) | ArcLoom-256 fabrication |
| Caltech/Yale async groups | ACT async design tools | Async BSIL timing verification |

---

## 9. Anticipated Objections and Responses

**"Isn't this just another ternary computer?"**
No. The 5500FP is a ternary computer — fetch, decode, execute. ArcLoom has no
instruction set. The answer settles through wire propagation. Different
computational model entirely.

**"How is this different from BitNet?"**
BitNet uses ternary values on binary hardware. ArcLoom uses ternary logic as the
native substrate. BitNet is a compression trick for trained LLMs. ArcLoom is a
perception architecture that requires zero training.

**"Huawei already made a ternary chip."**
Huawei patented ternary gates using standard ternary (0,1,2). ArcLoom uses
balanced ternary (-1,0,+1) which has the symmetric negation property required
for signed coupling. Huawei's chip (if it exists) runs sequential instructions.
ArcLoom settles combinationally. Different number system, different architecture.

**"Neural accelerators already do low-power perception."**
Neural accelerators require trained models, clocks, and sequential matrix
multiplication. SPPU requires no training, no clock, and no multiplication in
the decision path. Power is 10^9x lower than ARM Cortex-M0 for equivalent
perception.

**"How do you know it works?"**
19,683 arithmetic operations verified on FPGA silicon. 41,430 division tests at
zero errors. Live sensor-to-motor chain demonstrated. 351-sample autonomous
obstacle navigation with camera. Camera-sensor ambiguity correctly perceived.
See ASIC Spec v1.2, Section 12 (Validation Status).

**"What about Loihi / Akida / SpiNNaker?"**
All three run trained spiking neural networks on async hardware. The hardware
is clockless; the computation is ML. SPPU is purely combinational — no spikes,
no neurons, no weights learned from data.

---

*This document is confidential and for internal use only. The competitive
landscape analysis is based on publicly available information as of May 2026.
All ArcLoom claims reference validated demonstrations documented in the ASIC
Architecture Specification v1.2.*
