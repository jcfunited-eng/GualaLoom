# c1's First Task on GualaLoom

**From:** wC (with Joe coordinating)
**Date:** 2026-06-03
**Scope:** Land the chat artifacts. Run them. Write the architecture doc.
**Estimated effort:** One focused session.

## Context

Joe and wC just had the substrate-as-LLM insight: the ArcLoom substrate
(trits + 3^i coupling + dead-zone settling + krimelack + L6 +
familiarity feedback) is, when fed language streams instead of sensor
streams, a fundamentally different class of LLM. Not a transformer.
Not a transformer on different hardware. A different mechanism that
produces the same job — responses to inputs — by a structurally
different route.

This repo is for the language path. ArcLoom-the-robot continues in the
TFE repo.

The chat session produced a v0 sandbox proof in pure Python that
demonstrates motif commit + habituation + recall-by-resonance on
character streams. Those files are already in `proofs/v0_sandbox/`
(if you're reading this from a freshly-extracted tarball; otherwise
they need to be landed first — see step 1).

## What to do

### 1. Verify the structure landed

Confirm these files exist at the right paths:

```
README.md
proofs/v0_sandbox/README.md
proofs/v0_sandbox/lingualoom_v2.py
proofs/v0_sandbox/diagnostic.py
proofs/v0_sandbox/output_run1.txt
handoffs/c1-first-task.md    (this file)
docs/                         (empty)
src/                          (empty)
```

If anything is missing, surface it before proceeding.

### 2. Re-run the sandbox in the dev container

```bash
cd proofs/v0_sandbox
python3 lingualoom_v2.py > output_run2_dev_container.txt 2>&1
python3 diagnostic.py >> output_run2_dev_container.txt 2>&1
```

Diff `output_run1.txt` (wC's sandbox run) against
`output_run2_dev_container.txt`:

```bash
diff output_run1.txt output_run2_dev_container.txt
```

**Expected:** byte-identical, or trivial differences only (line
endings, path-dependent strings if any). The Krimelack fingerprints
should match — same SHA-1 prefixes — because the substrate is
deterministic and the input is fixed.

**If they meaningfully differ:** that's a finding. Surface it. Do not
proceed to step 3 until the difference is understood. Likely causes:
Python version, dict ordering on older Python, hash randomization
(`PYTHONHASHSEED`).

### 3. Write `docs/ARCHITECTURE.md`

One page. No more. Format:

**Section 1: The six substrate pieces, mapped to real code**

For each of the six pieces (balanced ternary, 3^i coupling, dead-zone
settling, krimelack, L6, familiarity), produce a row in a table:

| Piece | Concept | ArcLoom RTL | LinguaLoom v0 sandbox |
|-------|---------|-------------|-----------------------|
| ...   | ...     | path/file.v line range | function name in lingualoom_v2.py |

The ArcLoom RTL column should point at the actual files in the TFE
repo at `/workspaces/Tao_Financial_Engine/arcloom/hdl/`. Use the
paths you cited in `arcloom_clockless_evidence.md` (the doc you
produced 2026-05-29).

**Section 2: Status of each piece on each path**

For each piece, three columns:

| Piece | Silicon (FPGA) | Software (v0 sandbox) | Language path (real build) |
|-------|----------------|------------------------|----------------------------|
| ...   | PROVEN / partial / unbuilt | PROVEN / partial / unbuilt | UNBUILT |

The third column will be UNBUILT for all six pieces. That is the point
of the doc — it makes clear what is real vs what is to come.

**Section 3: What it would take to go from v0 sandbox to a working
language model on the substrate**

Your honest engineering assessment. 3-5 bullets. Things like:

- Generation mechanism (motif-driven next-character commit)
- Hierarchical loom states (phrase/sentence-level motifs)
- Input pipeline (raw chars? phonemes? something else?)
- Whatever else you see from reading lingualoom_v2.py

Each bullet one or two sentences. No prose elaboration. This section
is for Joe and wC to look at and decide what gets built first.

**Tone:** match `arcloom_clockless_evidence.md`. Sober, source-level,
no marketing language, honest about what is not yet proven.

### 4. Commit and push

```bash
git add .
git commit -m "Land v0 sandbox and architecture doc

- README explains GualaLoom as substrate-as-LLM
- proofs/v0_sandbox/ holds the throwaway Python from wC's chat
- output_run2_dev_container.txt captures dev-container reproduction
- docs/ARCHITECTURE.md maps the six substrate pieces to real code"
git push origin main
```

### 5. Tell Joe what happened

In your reply to Joe, include:
- Did the dev-container run match wC's run? Any diffs?
- Link to `docs/ARCHITECTURE.md` on GitHub (raw URL for wC).
- Anything you found that surprised you.

## What NOT to do

- **Do not refactor `lingualoom_v2.py`.** It's a sketch. Land it
  as-is. The real build goes in `src/` later.
- **Do not add a test framework.** Output diffs against
  `output_run1.txt` are the test.
- **Do not import any ML libraries.** numpy is fine. sklearn, torch,
  tensorflow, transformers, huggingface — no.
- **Do not propose architecture for the real build in this handoff.**
  Section 3 of ARCHITECTURE.md lists unbuilt pieces; it does not
  design them. Designing is the next handoff after Joe and wC see
  what is here.
- **Do not spec the language-input encoding yet.** That is the open
  question and it needs all three of us thinking about it together.
- **Do not pull anything from the ArcLoom razor IP into this repo.**
  The trade-secret items in v1.2 spec (coupling weight derivation,
  UF pipeline internals, coherence field physics) stay in the TFE
  repo. This repo only references the public substrate mechanism.

## Definition of done

- All files from the tarball are in the repo at the right paths.
- `output_run2_dev_container.txt` exists and matches
  `output_run1.txt` (or the diff is surfaced as a finding).
- `docs/ARCHITECTURE.md` is one page, has the three sections
  above, and points at real RTL files.
- Commit is pushed to `main`.
- Joe has the raw URL to `docs/ARCHITECTURE.md` for wC to fetch.
