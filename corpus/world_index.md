# GualaLoom World — Graded Corpora Index

Harvested from Aurelion's corpus_state.json. These are the texts Joe
raised Aurelion on, graded from simple to complex. The substrate
commits recurring structure first, so high-frequency seed words come
before literature.

## Phase 1 — Seed vocabulary (first exposure)
- `seed_vocab.txt` — ~200 highest-frequency English words
- `seed.md` — the substrate's self-description

## Phase 2 — Simple clean prose (after seed commits)
- Neutral corpus: simple declarative sentences
- Joe's speeches: Personal Compass, Coffee Bean, Power and Responsibility

## Phase 3 — Broader literature (after simple prose commits)
- Aristotle's Nicomachean Ethics
- Mary Shelley's Frankenstein
- John Milton's Paradise Lost
- Edgar Allan Poe (selected works)

## Phase 4 — Domain knowledge (after literature)
- Brain anatomy texts
- Applied physiology
- NASA mission transcripts
- Finance/weather news

## Notes
- Phases are exposure order, not hard gates. The substrate decides
  what commits via reinforcement-by-recurrence.
- All text enters through the intake guard (PII scrubbed, whitelisted).
- Lessons come from these corpora, NEVER from a transformer.
  (Aurelion's lesson-relay fetched lessons from GPT — that is firewalled.)
- Joe controls what feeds her. The guard enforces this.
