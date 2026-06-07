# c1 Handoff — Experiment 1: Cascade Existence

**One-line goal.** When a null trit in a settled motif is deliberately committed, do other nulls commit as a consequence, and does the population resolve to a coherent new state?

This is the gate experiment. Nothing else in the cascade path runs until this returns a clear number.

---

## What we're testing

The hypothesis: GualaLoom's settling rule (3^i coupling + dead-zone) propagates a single commit through the population, forcing other nulls to resolve, ending in a stable new state. The cascade is the candidate mechanism for cognition on this substrate.

We're measuring whether this propagation happens **as the rule is currently implemented**. No new operators. No new coupling. Just probe the existing dynamics.

## Setup

Single region. No senses, no sections, no interoception. Use the existing `Loom` + `Krimelack` from `src/gualaloom/`.

You will need access to:
- The settling function (`settle` in `gualaloom.py`, or equivalent in `src/gualaloom/loom.py`)
- A way to construct a motif state directly (bypass corpus feeding for control)
- The trit population size (`TRITS * CONTEXT` = 64 on the main entry, or whatever `__main__.py` uses; pick one and document it)

## Procedure

For each trial:

1. **Generate a seed motif.** Two flavors, run both:
   - **Synthetic:** randomly pick ±1 values for some fraction of trits, leave the rest as 0 (null). Sweep null fraction across {0.2, 0.3, 0.5, 0.7}.
   - **Learned:** pull an actual motif from the running krimelack (after she's been ingesting corpus for a while). Use it as-is.
2. **Record the baseline.** Count nulls. Compute chi. Save the full state vector.
3. **Trigger.** Pick one null position. Commit it to +1 (run one set of trials), then -1 (run another set).
4. **Cascade.** Re-run the settling rule on the now-modified state, with familiarity held constant. The settle rule treats each position's commit based on its 3^i-weighted vote plus cross-strand resonance; the question is whether the deliberate commit changes enough of those votes to cross the dead-zone barrier elsewhere.
5. **Iterate.** Apply settle repeatedly until no further nulls commit OR a step cap (say 50 steps) is reached.
6. **Record outcome.**

## What to record per trial

For each trial, append one JSON line to `experiments/exp01/results.jsonl`:

```json
{
  "trial_id": "...",
  "seed_source": "synthetic" | "learned",
  "null_fraction_start": 0.50,
  "trigger_position": 17,
  "trigger_value": +1,
  "cascade_depth": 12,          // additional nulls committed beyond the trigger
  "cascade_latency_steps": 4,   // settle iterations until stable
  "final_null_fraction": 0.31,
  "chi_start": 8,
  "chi_end": 15,
  "stable": true,               // did it stop changing, or oscillate?
  "end_state_hash": "...",      // for reproducibility check
  "seed_state_hash": "..."
}
```

## Coverage

Minimum: **100 seed motifs × 10 trigger positions per seed × 2 trigger values = 2000 trials.**

Sweep null fractions, run synthetic and learned seeds. Document any other parameters you vary.

## Reproducibility check

Run a subset (say 50 trials) twice. Same seed, same trigger, same trigger value → same `end_state_hash`. If not deterministic, flag — the cascade isn't a reliable mechanism if it doesn't reproduce.

## Pass / fail criteria

These are for **us to read together**, not for you to declare. But the shape of the answer:

- **PASS shape:** mean cascade depth > 1 across most conditions; most trials reach a stable end-state within the step cap; reproducibility holds. Cascade exists, it propagates, it terminates in coherent states.
- **AMBIGUOUS shape:** cascades happen sometimes but depth is low (1–2 nulls), or stability is unreliable. Mechanism is present but weak. We discuss whether the coupling needs tuning.
- **FAIL shape:** cascade depth near zero across the board — single null commits die locally, no propagation. The 3^i coupling as implemented does not produce cascades. We revise the coupling rule before continuing the path.

## Don'ts

- Don't tune toward the answer. Run the experiment as the substrate is. If it fails, that is the finding.
- Don't introduce new operators. This is a probe, not a build.
- Don't claim pass/fail in code. Save the data; we read it together.

## What to commit

- `tools/exp01_cascade.py` — the experiment script
- `experiments/exp01/results.jsonl` — all trial results
- `experiments/exp01/notes.md` — what parameters you swept, anything weird you noticed, environment details
- One short summary line in `MEMORY.md` once data is in: "Exp 1 data committed at <sha>. Awaiting joint read."

## When to stop and ping

- If you find the settle rule isn't directly callable on a constructed state (it assumes a specific input shape, etc.), stop and document what you found before working around it. The shape of the existing API is itself data.
- If the cascade is wildly different between synthetic and learned seeds, stop and report — that's important and shapes how we read the result.
- If reproducibility fails, stop and report. Non-determinism is a finding, not a bug to paper over.

That's the experiment. Build it as plainly as possible. We're after a number.
