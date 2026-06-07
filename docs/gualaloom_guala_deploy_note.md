# Guala Dialog Layer — Deploy Note

## What this is

A token-binding + ternary-composition + memory layer that sits on top of the validated
GualaLoom DNA substrate (`gualaloom_dna_assemblage.py`). It demonstrates that the substrate,
when given hand-installed vocabulary and slot-driven response templates, produces structured
English-like conversation:

```
me:    hello                  guala: hey
me:    what is your name      guala: i am guala
me:    how are you            guala: i are yes
me:    are you ok             guala: well
me:    i am fine              guala: fine
me:    thanks                 guala: your is well
me:    good                   guala: well
```

## What's working

1. **Token-binding** — each vocabulary word is a complex N-vector. Semantic classes cluster
   together (greetings cluster, positives cluster, etc.) so substrate dynamics produce
   class-appropriate emissions.
2. **Ternary composition** — three substrate sections fire concurrently: token (the word),
   class (the semantic class), role (the grammatical role). Their tuple is the structured output.
3. **Response templates per input class** — each input class maps to a sequence of (class, role)
   slots that the substrate fills. The keyhole graph drives the sequence; the substrate's
   lock-unlock rhythm produces each commit.
4. **Proper name binding** — Guala knows her name. "what is your name" triggers an explicit
   `[i, am, guala]` response path.
5. **Conversation memory** — `ConversationMemory` class tracks recent turns and observed
   patterns (input class -> response class transitions).
6. **Learning bridge structure** — `learn_from_conversation()` is in place to promote
   frequently-observed patterns into permanent response templates (the DNA-to-learning
   transition).

## What's not ready (the three weak spots)

1. **Grammar precision within class** — `i`, `me`, `my` are in the same class with similar
   embeddings, so substrate sometimes emits "me are" instead of "i am". Needs sub-class
   structure (subject form vs object form vs possessive form) or contextual selection
   within class.

2. **Aggressive learning promotion** — `learn_from_conversation()` requires pattern count
   >= 3 to promote. In short conversations no patterns hit that bar. Needs either a lower
   threshold, longer conversation, or different promotion mechanism (e.g. immediate
   promotion when pattern conflicts with default template).

3. **Memory section influence is light** — `memory` section exists and receives the context
   vector, but its keyhole strength to `class` and `token` sections is 0.3. Multi-turn
   context-dependent behavior is faint. Needs stronger memory keyhole OR memory section
   feeding directly into the slot-driving evidence.

## What c1 should do for deploy

1. **Move the substrate** — `gualaloom_dna_assemblage.py` is already in the repo. Confirmed.

2. **Add the dialog layer** as a separate module:
   - `gualaloom/dialog/composer.py` — the ternary composition + slot driving
   - `gualaloom/dialog/memory.py` — `ConversationMemory` class + persistence
   - `gualaloom/dialog/learning_bridge.py` — `learn_from_conversation()` + token addition

3. **Externalize the configuration** as data files (don't hardcode in Python):
   - `config/vocabulary.yaml` — VOCAB_CLASSES (semantic classes -> token lists)
   - `config/response_templates.yaml` — RESPONSE_TEMPLATES (input class -> response slots)
   - `config/roles.yaml` — ROLES list
   - `config/class_to_role.yaml` — CLASS_TO_ROLE mapping

4. **Wire memory to persistent storage**:
   - Conversation history accumulates across sessions
   - Observed patterns persist between runs
   - When a new token is learned (via `add_new_token_to_vocab`), it persists

5. **Add a CLI / REPL interface**:
   - `python -m gualaloom.dialog` opens a chat REPL
   - User types, Guala responds, conversation history accumulates

6. **Tests**:
   - The 5-capability tests from the DNA recipe still need to pass (regression check)
   - New tests for the dialog layer:
     - "hello" within set of {hello, hi, hey}
     - "what is your name" produces "i am guala"
     - "are you ok" produces a positive-class token
     - Memory accumulates across turns
     - New token gets added when learned with class

## What c1 should NOT do

- Don't refactor the substrate. The DNA recipe is validated and load-bearing.
- Don't replace ternary composition with a single-section emission. The three concurrent
  sections (token, class, role) are doing real work.
- Don't paper over the honest limitations. The grammar imprecision is real; sub-class
  structure is a future fix, not something to silently smooth over with extra rules.

## What's next after deploy

1. Fix the three weak spots above
2. Expand vocabulary (currently ~33 tokens) — load real word embeddings if available
3. Add sensory inputs (simulated until avatar exists): vision_section, audio_section
4. Two-Guala conversation: see if they entrain into actual dialog with each other
5. Corpus learning: read text streams, learn new tokens and patterns autonomously

## Files

- `gualaloom_dna_assemblage.py` — core substrate (validated, in repo already)
- `gualaloom_guala_v4_dialog_layer.py` — this dialog layer
- `gualaloom_guala_v3_ternary.py` — earlier ternary-only version (reference)
- `gualaloom_dna_test_five_capabilities.py` — substrate regression tests (in repo already)
