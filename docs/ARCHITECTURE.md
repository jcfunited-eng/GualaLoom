# GualaLoom Architecture

**Date:** 2026-06-03
**Scope:** What is built, what is not, where the code lives.

---

## 1. The Six Substrate Pieces: Code Map

| # | Piece | Concept | ArcLoom RTL | LinguaLoom v0 sandbox |
|---|-------|---------|-------------|-----------------------|
| 1 | Balanced ternary | {-1, 0, +1} encoding; 0 = structural uncertainty | `arcloom_ternary_loom.v` lines 27-54 (`arcloom_trit`, `arcloom_trit_mult`); `arcloom_bsil_bt.v` encoder; SPPU uses 2-bit encoding: `2'b01`=+1, `2'b10`=-1, `2'b00`=null | `encode_to_strand()` (lines 39-50): balanced ternary conversion, `r=2 → r=-1` carry rule |
| 2 | 3^i positional coupling | Weights [1, 3, 9, 27, 81, 243, 729, 2187]; mathematical identity, not tunable | `arcloom_sppu.v` lines 31-40: hardcoded 3^i weights; `arcloom_local_field` (lines 60-92 of `arcloom_ternary_loom.v`): weighted sum via `weights[16*i +: 16]` | `POSITIONAL_3I = (1, 3, 9, 27, 81, 243, 729, 2187)` (line 27); used in `settle_field()` line 74, 80 |
| 3 | Dead-zone settling | Trit commits only when coupling pressure exceeds barrier; below barrier → null | `arcloom_ternary_loom.v` lines 85-89: `effective_dz = DEAD_ZONE + dead_zone_adj`; three-way compare against `±effective_dz` | `settle_field()` lines 65, 81-86: `barrier = DEAD_ZONE_BASE + familiarity`; same three-way compare |
| 4 | Krimelack motif memory | Content-addressable structural memory; commit by settling, recall by resonance | `arcloom_krimelack.v`: 32-slot motif store, hash-based duplicate detection (line 81), parallel match scoring (`match_score` output), clocked commit logic (line 106) | `Krimelack` class (lines 98-145): `commit()` fingerprints via SHA-1, `recall()` scores overlap of non-null trits, `decay()` culls stale motifs |
| 5 | L6 dimensional exhaustion | Counts collapsed trits; structural lock when n_eff < n/e | `arcloom_l6_tcl.v`: counts non-null trits (lines 56-62), `structural_lock = (n_eff < KNEE)` (line 85), KNEE = n/e rounded | `l6_freedom()` (lines 90-95): `knee = round(n / e)`, returns effective/collapsed/knee |
| 6 | Familiarity feedback | Match score raises dead-zone barrier; substrate habituates to known patterns | `arcloom_ternary_loom.v` lines 444-464: `damped_fam` register, Krimelack `match_score` feeds back into SPPU `familiarity` input | `LinguaLoom.step()` lines 173-175: `familiarity = (score * FAMILIARITY_GAIN) // max_possible_score`; fed into next `settle_field()` call |

RTL paths are relative to `/workspaces/Tao_Financial_Engine/arcloom/hdl/`.

---

## 2. Status of Each Piece on Each Path

| # | Piece | Silicon (FPGA) | Software (v0 sandbox) | Language path (real build) |
|---|-------|----------------|------------------------|----------------------------|
| 1 | Balanced ternary | PROVEN — BSIL-BT synthesized and running on PYNQ | PROVEN — `encode_to_strand()` matches BT identity | UNBUILT |
| 2 | 3^i positional coupling | PROVEN — hardcoded in SPPU, floor-tested May 8 | PROVEN — `POSITIONAL_3I` tuple, used in settling | UNBUILT |
| 3 | Dead-zone settling | PROVEN — `arcloom_local_field` confirmed combinational, robot navigates with it | PROVEN — `settle_field()` produces commit/null decisions | UNBUILT |
| 4 | Krimelack motif memory | PROVEN — 32-slot clocked memory, commit + recall working on silicon | PROVEN — motif commit, reinforcement, decay, recall-by-resonance all demonstrated | UNBUILT |
| 5 | L6 dimensional exhaustion | PROVEN — `arcloom_l6_tcl` synthesized, gates Krimelack commits | PROVEN — `l6_freedom()` reports effective/collapsed/knee | UNBUILT |
| 6 | Familiarity feedback | PROVEN — `damped_fam` register feeds SPPU, habituation observed on sensor streams | PROVEN — familiarity modulates barrier, habituation visible across repeated text | UNBUILT |

---

## 3. What It Would Take to Go From v0 Sandbox to a Working Language Model

- **Generation mechanism.** The v0 sandbox only ingests characters and commits motifs. It never produces output text. A generation path would need to: given a settled field state, find the highest-resonance motif in Krimelack, then decode the next trit-strand back to a character. This is motif-driven next-character commit — not token sampling.

- **Hierarchical loom states.** The v0 sandbox operates at a single scale: 4-character context windows → flat motifs. Real language has phrase, clause, and sentence structure. The substrate would need stacked loom layers where lower-level settled states become input strands for a higher-level loom. This is the same idea as the SPPU's context/momentum/decision field hierarchy, applied recursively.

- **Input pipeline.** The v0 sandbox uses `ord(ch) - 96` to center ASCII characters before BT encoding. This works for proof-of-concept but wastes most of the 8-trit range on ASCII codes that never appear. The encoding question — raw characters, phonemes, byte-pair chunks, or something else — is open and will shape what kinds of structure the coupling can find.

- **Scale.** The v0 sandbox uses 8 trits per strand and 4-strand context windows (32 total trit positions). The FPGA SPPU uses 12 strands × 8 trits (96 coupled positions per field, 9 fields). Language likely needs wider context and deeper coupling to capture longer-range dependencies. How wide and how deep is an empirical question the real build would answer.

- **Persistence across inputs.** Krimelack decay in the v0 sandbox is aggressive (weight decrements every step). For language, motifs representing common phrases need to survive long enough to be useful during generation. The decay schedule and reinforcement scaling need tuning for language timescales rather than sensor-loop timescales.
