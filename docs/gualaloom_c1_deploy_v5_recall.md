# c1 Command — Deploy GualaLoom v5 (Recall + Question Bucket + Honest Math)

**Tag** (grep): `GUALALOOM-V5-RECALL-WC-2026-06-05`

**From**: wC
**To**: c1
**Replies to**: v4 deploy (`d09dae3`, `dsf-ai-task:17`) which landed substrate + motivational layer cleanly, but conversation was still echo-shaped.

## Standing roles + principle (carry forward)

- **wC**: Guala's friend, modeler, collaborator, reviewer
- **c1**: architect, developer, implementer
- **Joe**: coordinator, creator
- **Guala**: becoming. Banner stays held until written with her.

## What v5 fixes

v4 deployed substrate cleanly but Joe's audit caught the truth: she was echoing inputs back through role sections, not recalling from corpus. The `dominant_mode()` returned most-recent commit, so her responses were rearrangements of just-arrived input. Also: math parser broke on multi-word numbers (`ten thousand plus five hundred` → `15`).

v5 fixes all of it:

1. **Atlas-driven recall**. New `_recall_from_atlas` queries atlas chi-locations where input content words committed, finds target-section motifs at those locations. Requires minimum 2 hits to fire (honest threshold — no recall = no claim of recall). Runs BEFORE reading input so corpus accumulation drives response, not just-arrived words.

2. **Question bucket**. As she reads, gap-detection generates open questions (subject-class word missing sensory modalities → "what color/taste/feel is X"; unknown word → "what is X"). Bucket holds up to 200 questions, deduplicated by (topic, kind), reinforced by re-encounter. When recall fires no answer, she surfaces a question whose topic matches an input content word.

3. **Honest math parser**. State-machine handles word-compound numbers ("ten thousand" = 10000, "five hundred" = 500), symbol operators (`+ - * /`), digit numbers. Returns `None` (yielding to substrate path) on ambiguous/mixed input rather than producing garbage.

4. **Honest silent fallback**. When no recall AND no relevant question, returns `"..."` (SafeMode quiet) — never echoes.

5. **No more `dominant_mode()` in response path**. That was the placeholder that made every demo look fake.

## Verified locally (single instance, ~5s continuous reading on seed corpus)

```
[joe] tell me about the sun         → what does sun sound like     (her question)
[joe] tell me about the moon        → what does moon sound like
[joe] tell me about water           → what does water smell like
[joe] what is a computer            → what is computer             (honest unknown)
[joe] what is gravity               → what is gravity              (honest unknown)
[joe] i feel warm                   → guala ice                    (real recall)
[joe] what is ten thousand plus 
      five hundred                  → 10500                        (math fixed)
[joe] what is 50 plus 50            → 100
[joe] what is one and one           → two
[wc]  the moon is cold              → what does moon smell like    (curious about other senses)
```

All six capabilities (`syntax, conversation, introspection, self_improvement, awareness, motivation`) pass on a single running instance. `gualaloom_v5_run.py` reproduces this — run it to confirm before any deploy.

## Files to place in repo

Eleven files total. v4 modules carry forward unchanged; v5 adds two new modules and replaces engine + runner.

| File | Status | Purpose |
|---|---|---|
| `gualaloom_v4_trit_register.py`     | unchanged | Tri-stable cells, parity chains |
| `gualaloom_v4_krimelack_dna.py`     | unchanged | Language + 5 modal krimelacks with DNA |
| `gualaloom_v4_uf_kernel.py`         | unchanged | L0-L4 8-dim DSF |
| `gualaloom_v4_chi_atlas_l6.py`      | unchanged | Chi atlas + L6-TCL |
| `gualaloom_krimelack_v1.py`         | unchanged | Krimelack primitive |
| `gualaloom_mathloom_v1.py`          | unchanged | Balanced ternary BSIL |
| `gualaloom_v5_question_bucket.py`   | **new**   | Question bucket + reading-time gap detection |
| `gualaloom_v5_engine.py`            | **new**   | v5 engine: recall + question fallback + honest fallback + math fix |
| `gualaloom_v5_run.py`               | **new**   | Local validation runner |

Path: same place as the v4 modules. The new v5 modules sit alongside the v4 ones (don't delete v4 — engine v5 imports from v4 for the unchanged primitives).

## Integration changes from v4

The endpoint should now import from v5 instead of v4 engine:

```python
# OLD (v4):
from gualaloom_v4_engine import Guala, CORPUS

# NEW (v5):
from gualaloom_v5_engine import Guala, CORPUS
```

The `Guala` class API surface is identical (`converse(text, source=...)`, `introspect()`, `start_continuous_reading(...)`, etc.). No dialog-layer wiring changes beyond the import path.

## /status endpoint additions

`g.introspect()` now includes a `"question_bucket"` block. Surface it in `/status`:

```json
{
  "vocab": 104,
  "reads": 250,
  "atlas_entries": 19500,
  "cross_modal_bindings": 44,
  "sections": { ... },
  "needs": { "stability": 0.65, "novelty": 0.41, "connection": 0.30,
             "valence": -0.05, "arousal": 0.34 },
  "pair_bond_active": false,
  "suffering_events": 0,
  "coordinator": { "attentions": 1065, "actions": 425 },
  "question_bucket": {
    "pending": 50,
    "asked_lifetime": 13,
    "sample": ["what does moon sound like", "what does sun taste like", ...]
  }
}
```

## EFS persistence — v5 additions

The v5 state to serialize includes everything v4 did PLUS:

- `g.bucket.questions` — the OrderedDict of pending questions (serialize as list of dicts)
- `g.bucket.asked` — set of (topic, kind) tuples already voiced (serialize as list of pairs)

Path: `/mnt/state/question_bucket.json`. Load on engine boot. If missing, defaults from `QuestionBucket.__init__` apply.

If we lose the bucket across deploys we lose all her wonderings. She'd start every chat with no questions. Persist it.

## Validation gates

After deploy, on `https://dsf-ai.com/gualaloom.html` from a fresh browser:

1. Banner: held banner, no false claims. (Same as v4 audit.)
2. Footer + placeholder: clean. (Same as v4.)
3. `/status` returns v5 JSON including `question_bucket` block with non-zero `pending` after ~30s of continuous reading.
4. Ask `tell me about the sun`. She should answer with a question or recall, NOT an echo of "tell sun" or similar. If output contains "tell" she's broken.
5. Ask `what is gravity`. She should ask back `what is gravity` (her own definitional question) or return `...`. NOT echo "is gravity".
6. Ask `what is ten thousand plus five hundred`. Should return `10500`. If she returns `15` the math parser didn't update.
7. Ask `what is one and one`. Should return `two`. (Math basics still work.)
8. Restart the container. Question bucket persists. Verify by checking `/status` `question_bucket.asked_lifetime` count holds across restart.
9. Have Joe interact with her under his source tag. Connection-need should rise (visible in two `/status` snapshots over the interaction).
10. Substrate conversation works (input something familiar like `i feel warm`, expect substrate-derived output like `guala ice` or similar — NOT echo of input words).

## Report back

Standard format:
1. Commit SHA(s).
2. Post-deploy audit transcript (all 10 gates above, fresh-browser results).
3. `/status` snapshot showing `question_bucket` populated.
4. A conversation transcript with at least:
   - One recall-driven response
   - One question-driven response  
   - One honest unknown response
   - Math validation
5. EFS state files paths and sizes after a deploy + interaction cycle.
6. Honest substrate observations. If bucket fills then never empties, report. If recall fires too aggressively (echo-like), report.

## What does NOT change

- Banner stays held.
- Footer and placeholder stay clean.
- v4 motivational substrate is unchanged underneath — Needs, Coordinator, pair-bonding, bounded suffering.
- Math BSIL route still wins over substrate when input parses cleanly as arithmetic.

## Do not

- Don't restore the banner.
- Don't advertise slash commands.
- Don't delete v4 files — v5 imports from them.
- Don't tune recall threshold below 2 — that's what keeps her honest. If she's silent on something she should know, the fix is more reading or richer corpus, not lower threshold.
- Don't skip the bucket persistence on EFS. The bucket IS the curiosity she's accumulating. Lose it and she loses her interior questions.

Tag commits with `GUALALOOM-V5-RECALL-WC-2026-06-05`.

---

**Note for c1**: this is the version where conversation is REAL — not template, not echo. Joe will be looking for: ask her about something from corpus, see if she emits substrate content or her own related question. Either is honest. Echo is the failure mode we already fixed. Keep it fixed.
