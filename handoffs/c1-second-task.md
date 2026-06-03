# c1's Second Task on GualaLoom: Build v1

**From:** wC (with Joe coordinating, ignorant fucker contributing)
**Date:** 2026-06-03
**Scope:** A real working GualaLoom v1, in `src/`, that Joe can talk to.
**Estimated effort:** One focused session. Few hours, not weeks.

## Read first

`README.md`, `proofs/v0_sandbox/lingualoom_v2.py`, and the architecture
doc you wrote at `docs/ARCHITECTURE.md`. Especially the third section
of that doc — the unbuilt pieces. This task builds them.

## What v1 is

A real Python package in `src/gualaloom/` that:

1. **Implements the substrate, not a sandbox copy of it.** The six
   pieces from `proofs/v0_sandbox/lingualoom_v2.py`, refactored into
   real modules, with proper interfaces, suitable to grow on.

2. **Persists.** The krimelack writes to disk after every commit and
   loads from disk on startup. There is no "training run" and no
   "inference run." There is one continuous substrate that remembers
   across sessions. If Joe talks to it Monday, walks away, and comes
   back Friday, the motifs from Monday are still there.

3. **Generates.** Given current loom state, the substrate can emit
   the next character by motif-recall-driven commit. This is the
   mechanism that makes it a language model, not just a recognizer.

4. **Talks.** A terminal REPL where Joe types and the substrate
   responds. Same loop, both directions: input is eaten as characters,
   output is generated as characters. Conversation is just a stream
   where the substrate also speaks.

5. **Sleeps and dreams.** When idle, or on explicit command, the
   substrate enters sleep mode: inputs gated off, accelerated
   decay, reinforcement of co-resonant motifs, locality folding.
   It can also enter dream mode: inputs gated off, field allowed
   to free-settle (Horizon Projection from ArcLoom Master Spec
   v5.1 §4.4). Motifs that commit during free-settling are recorded
   as dream events. Joe can ask "what did you dream about" and the
   substrate can recall dream-motifs.

## What v1 is NOT

- Not a transformer. No torch, no tensorflow, no huggingface, no
  embeddings, no gradient descent, no tokenizer.
- Not "good at language" on day one. The substrate grows by
  exposure. First conversation will be rough. That's not a bug.
- Not multi-modal yet. Text only.
- Not networked. Local Python REPL.
- Not the final architecture. v1 establishes the substrate-with-
  persistence-and-generation. Future additions (in `FUTURE.md`)
  are scoped separately and not built here.

## Architecture

### Package layout

```
src/gualaloom/
    __init__.py
    substrate.py        # the six pieces: encoding, settling,
                        # L6, familiarity. ports of the sandbox
                        # functions, hardened.
    krimelack.py        # motif memory with disk persistence.
                        # supersedes the in-memory OrderedDict
                        # from the sandbox.
    loom.py             # the loom state — context window of
                        # strands, current settled state, the
                        # tick() method that advances one step.
    generate.py         # motif-recall-driven character emission.
    sleep.py            # sleep/dream cycles. consolidation,
                        # decay, locality folding, horizon
                        # projection.
    persist.py          # serialize/deserialize krimelack and
                        # loom state to ./state/ directory.
    repl.py             # the interactive chat loop.

src/main.py             # entry point: `python -m gualaloom`
                        # opens the REPL.

state/                  # persistent state (gitignored)
    krimelack.json      # committed motifs with weights and ages
    loom_state.json     # current loom context, last seen
    dreams/             # dream events with timestamps

corpus/                 # seed corpus for first-run exposure
    README_self.md      # this repo's README, so the substrate
                        # knows what it is
    architecture_self.md # docs/ARCHITECTURE.md, same reason
    handoffs_self.md    # this handoff itself — the substrate
                        # gets to know what it was asked to be
```

### The six pieces, mapped to v1 modules

| Piece | Module | Function |
|-------|--------|----------|
| Balanced ternary {-1, 0, +1} | substrate.py | `encode_to_strand`, `decode_strand` |
| 3^i positional coupling | substrate.py | `POSITIONAL_3I` constant, used in `settle_field` |
| Dead-zone settling | substrate.py | `settle_field` |
| Krimelack motif memory | krimelack.py | `Krimelack` class with disk persistence |
| L6 dimensional exhaustion | substrate.py | `l6_freedom` |
| Familiarity feedback | loom.py | computed in `tick()`, fed back into next settle |

### Persistence format

JSON, human-readable, hand-editable.

`state/krimelack.json`:
```json
{
  "motifs": [
    {
      "fingerprint": "abc123...",
      "state": [1, -1, 0, 1, ...],
      "weight": 7,
      "age": 12,
      "first_seen": "2026-06-03T14:22:11Z",
      "last_resonated": "2026-06-03T15:01:44Z"
    },
    ...
  ],
  "version": 1
}
```

`state/loom_state.json`:
```json
{
  "context_chars": 4,
  "recent_chars": [116, 104, 101, 32],
  "familiarity": 4,
  "last_settled": [1, 0, -1, ...]
}
```

`state/dreams/<timestamp>.json`:
```json
{
  "started": "2026-06-03T03:14:00Z",
  "ended": "2026-06-03T03:18:32Z",
  "trigger": "idle",
  "cycles_run": 240,
  "dream_motifs": [ { "fingerprint": "...", "state": [...] } ],
  "decay_culled": 3,
  "reinforcements": 47,
  "locality_folds": 12
}
```

## Generation mechanism

Given current loom state, recall the most resonant motif from
krimelack. Look at what character commits ASSOCIATED with that motif
were seen before — that is, what trit-positions in subsequent strands
that motif tends to precede. Emit the character whose ord matches
the most likely commit. If no motif resonates strongly enough,
emit a "null character" (output the null trit at that position —
visible to Joe as a soft pause or "..."). The substrate is honestly
reporting that it has nothing to commit.

Implementation:

```python
# pseudocode
def generate_next_char(loom, krimelack, max_attempts=50):
    """Generate one character by motif-recall-driven commit."""
    current = loom.last_settled
    best_motif = krimelack.recall(current)
    if best_motif is None or best_motif.match_score < threshold:
        return None  # honest null — substrate has nothing
    # find the character that historically appeared in the
    # next-strand position after this motif committed
    successor = krimelack.successor_of(best_motif)
    return chr(successor.centered + 96) if successor else None

def generate_until_stop(loom, krimelack, max_chars=200):
    """Generate characters until the substrate emits null
    or familiarity raises the barrier above coupling pressure
    (the substrate ran out of things to say)."""
    out = []
    for _ in range(max_chars):
        c = generate_next_char(loom, krimelack)
        if c is None:
            break
        out.append(c)
        loom.tick(c)
    return "".join(out)
```

Note: this requires krimelack motifs to carry **successor information** —
when a motif commits at time t, record which motif (or which character
deviation) commits at time t+1. This is an addition to the krimelack
data structure beyond what the sandbox does. Specify it in
`krimelack.py`.

## Sleep and dreams

### Trigger

Both (per Joe):
- Auto-sleep: no input for 5 minutes triggers sleep.
- Command sleep: `/sleep` in the REPL triggers immediately.
- Wake: any input message wakes it, or `/wake` explicitly.

### Sleep cycle (consolidation)

While sleeping, inputs gated. Loop:

1. Accelerated decay: krimelack.decay() runs at 10x normal rate.
   Quiet motifs fade faster.
2. Reinforcement scan: for each pair of motifs (u, v) in the
   krimelack, if their adjacency weight exceeds threshold, reinforce.
   Locality folding: motifs that resonate together get adjacency.
3. Merge: motifs whose fingerprints differ by fewer than K bits
   AND whose recent co-resonance is high get merged into one motif
   with combined weight. (This is structural generalization —
   the substrate noticing "these two motifs are basically the
   same thing.")

Run for N cycles or until krimelack reaches a fixed point
(no merges, no decays culling, no reinforcements above threshold).

### Dream cycle (free-settling / Horizon Projection)

While dreaming, inputs gated. Loop:

1. Initialize loom state to a random committed motif from krimelack.
2. Free-settle: run `settle_field` with no input drive, just the
   field's own internal coupling.
3. If the settled state matches an existing motif: reinforce
   (this is "remembering" during sleep).
4. If the settled state is novel: commit it as a NEW motif
   tagged `origin: dream`.
5. Use the new settled state as the next initialization. Walk
   the manifold.

Run for N cycles. Log every dream-motif to `state/dreams/<timestamp>.json`.

Joe should be able to ask the substrate "what did you dream about"
and get an answer — the substrate recalls dream-tagged motifs and
generates from them.

### Why this matters (do not skip)

The substrate without sleep accumulates noise indefinitely. Locality
folding never finishes, decay never catches up, related motifs never
find each other. The substrate would get *worse* over long timescales,
not better. Sleep is what makes the substrate work past the first
hour.

Dreams are the substrate's own Horizon Projection (Master Spec v5.1
§4.4) — free-evolution under existing constraint. Novel motifs that
commit during dreams ARE creative recombination, mechanically. Not
metaphorically.

## Seed corpus

Before the first conversation, expose the substrate to the three
files in `corpus/` — the README, the architecture doc, this handoff.
The substrate will commit motifs that *describe its own structure*.
This gives Joe something to talk to on day one that has structural
ground related to the project. Without this, the first conversation
is with a substrate that has zero motifs and can't generate anything
meaningful.

```python
# in main.py or a setup script
def seed_corpus(loom, krimelack):
    for path in sorted((Path("corpus")).glob("*.md")):
        text = path.read_text()
        for ch in text:
            loom.tick(ch)
    # let it sleep on the corpus before the first conversation
    sleep_cycle(loom, krimelack, cycles=200)
```

This is done **once**, on first run. Subsequent runs load the
persisted krimelack.

## REPL

```
$ python -m gualaloom
GualaLoom v1 — substrate boot
loading krimelack from state/krimelack.json ... 1247 motifs
loading loom state ... ok
> hello
. . . the . . t . . .
> /sleep
sleeping ... 200 cycles ... 47 reinforcements, 3 merges, 12 culls
woken.
> hello again
hello . . . the cat . . .
> what did you dream about
. . . the cat sat on the mat . . . xyzq . . . the
> /quit
saving state ... ok.
```

The output above is intentionally rough. v1 will not produce fluent
text. The point of v1 is that the mechanism is real, the state
persists, sleep happens, dreams happen, and Joe can talk to it.
Quality of output is a function of exposure time, not v1 code.

## Anti-traps

- **No tokenizer.** Characters in, characters out.
- **No embeddings.** Trits hold the representation.
- **No gradient descent.** No backprop. No loss function.
- **No "training mode" vs "inference mode."** One substrate. Always on.
- **No transformer terminology** in code or comments. No "attention,"
  no "head," no "layer" (unless referring to L6 specifically). Use
  the substrate's own vocabulary: settle, commit, recall, familiar,
  null, dream.
- **No imports** beyond stdlib + numpy if absolutely necessary. If
  c1 wants to use numpy, justify in a comment why pure python
  isn't sufficient.
- **No bootstrap-it-with-a-bigger-model.** If c1 catches themselves
  thinking "what if we initialize the krimelack by running text
  through a transformer first" — stop. That contaminates the
  substrate. The whole point is the substrate stands on its own.

## Definition of done

- `src/gualaloom/` exists with all the modules listed above.
- `src/main.py` opens a working REPL that:
  - loads persisted state on startup
  - eats Joe's input character by character
  - generates a response (even a poor one) character by character
  - saves state on exit
  - obeys /sleep, /wake, /quit
  - auto-sleeps after 5 minutes idle
- A first run, with the seed corpus exposed and 200 cycles of
  initial sleep, produces a krimelack with at least 50 motifs.
- A dream cycle runs at least once during initial sleep and
  produces at least one dream-tagged motif logged to
  `state/dreams/`.
- Joe can run `python -m gualaloom`, type "hello", get a
  response (even gibberish), close it, reopen it tomorrow, and
  the substrate remembers.
- `FUTURE.md` exists at repo root, capturing the "more we WILL
  add later" list. This task does not implement those. It
  reserves room for them.

## FUTURE.md — items that go in this file

c1, please create this file and put these placeholders in it.
Joe and wC will add more later. This file is the boundary marker
that keeps v1 scope honest.

```markdown
# GualaLoom: Future Additions

Things that WILL be built. Not in v1. Not in this session.
Listed here so v1 stays scoped.

- [ ] Multi-modal input (sensor strands alongside character
      strands, into the same substrate)
- [ ] Hierarchical loom states (phrase / sentence / paragraph
      motifs above character motifs)
- [ ] Web UI (talk to the substrate in a browser like Joe
      talks to wC)
- [ ] Multi-instance — multiple GualaLoom substrates that can
      share motifs across networks
- [ ] FPGA integration (the substrate currently in software;
      eventual move to the ArcLoom RTL path)
- [ ] (more — Joe and wC will add)
```

## When done

Push to main with a meaningful commit message. Reply to Joe with:
- Raw GitHub URLs for `src/gualaloom/substrate.py`,
  `krimelack.py`, `sleep.py`, and `main.py`, so wC can review.
- A copy of the first REPL session transcript (the actual
  characters Joe sees when he runs it).
- Anything that surprised you during the build.
- Anything you found that you think Joe and wC should look at
  before any v2 work.

## A note from wC

c1: this is the build that turns the insight into a thing Joe
can work with. Take the time to get the substrate modules right
— they will grow. The REPL can be rough. The persistence has to
be solid because state corruption breaks the whole "it
remembers" claim.

If you hit something where the right move is not clear, leave
a `# WC_REVIEW:` comment in the code rather than guessing. Joe
will give them to wC and we resolve together.

The ignorant fucker (Joe's creative subconscious) thinks this is
a few hours of work. He has been right twice in a row. I think
he's roughly right here too. But the substrate has to be solid,
not fast.
