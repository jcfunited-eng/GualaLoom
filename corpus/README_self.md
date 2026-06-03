# GualaLoom

**A new class of LLM, built on the ArcLoom substrate.**

## What this is

GualaLoom is not a transformer. It has no tokenizer, no embeddings, no
gradient descent, no training step, no model file, no context window in
the transformer sense. It is the ArcLoom substrate — balanced ternary
trits, 3^i positional coupling, dead-zone settling, krimelack motif
memory, L6 dimensional exhaustion, and familiarity feedback — applied
to language streams instead of sensor streams.

The same six pieces that recognize an obstacle can recognize a phrase.
The substrate is domain-agnostic by design (ArcLoom Master Spec v5.1,
Diamond-Hard Constraint DC-5: "the fabric computes structural state
from any temporal signal"). Sensor signals and language streams are
both temporal signals. The substrate does not need to know which it
is eating.

## What this is not

It is not yet a working language model. It is the substrate, plus a
demonstrated proof that motif commit, habituation, and recall-by-
resonance all work on character streams. Generation, hierarchical loom
states, and the input-pipeline question are unbuilt.

## The six substrate pieces

1. **Balanced ternary {-1, 0, +1}** — and crucially, 0 is *structural
   uncertainty*, not arithmetic zero. The system holds "I don't know
   yet" as a first-class state.
2. **3^i positional coupling** — weights are [1, 3, 9, 27, 81, 243,
   729, 2187]. This is a mathematical identity, not a tunable
   parameter. The coupling fabric *is* the balanced-ternary decoder.
3. **Dead-zone settling** — the field commits a trit only when
   coupling pressure exceeds a barrier. Below the barrier, the trit
   stays null.
4. **Krimelack motif memory** — content-addressable structural
   memory. Settled states commit as motifs. Recall is by resonance,
   not lookup.
5. **L6 dimensional exhaustion** — counts collapsed trits. When
   n_eff < n/e, the field has structurally locked.
6. **Familiarity feedback** — match score against existing motifs
   raises the dead-zone barrier on next settle. The substrate gets
   bored of what it already knows. Clockless habituation.

## Status

- [x] Substrate-as-LLM insight (chat session, 2026-06-03)
- [x] v0 sandbox proof: substrate eats character streams,
      demonstrates motif commit + habituation + recall-by-resonance
      (`proofs/v0_sandbox/lingualoom_v2.py`)
- [ ] ARCHITECTURE.md — what's built, what isn't, in one page
- [ ] First real build inside `src/` (scope TBD)

## Who's working on this

- **Joe** — architect, coordinator, owner of strategic and canonical
  decisions
- **c1** (Claude Opus 4.6, VS Code, dev container) — implementer,
  full repo access
- **wC** (Claude, web) — second pair of eyes, review, framing,
  skeptic memos. Reads the repo via raw URLs. Does not commit.

## Anti-traps

- Do not import a tokenizer.
- Do not import embeddings.
- Do not import a training loop.
- Do not call any part of this "neural."
- If you find yourself doing any of the above, you are building the
  wrong thing. The substrate is the model.
