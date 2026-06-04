"""
Guala dialog REPL.

    python -m gualaloom.dialog
"""

import numpy as np
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from gualaloom.dialog.composer import VocabManager, build_guala
from gualaloom.dialog.memory import ConversationMemory
from gualaloom.dialog.driver import say_to_guala

SEED = 42


def main():
    rng = np.random.default_rng(SEED)
    vocab = VocabManager(seed=SEED)
    vocab.seed_minimal()

    guala = build_guala(rng, vocab)
    memory = ConversationMemory()

    # Load persisted memory if it exists
    state_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "..", "..", "..", "state")
    mem_path = os.path.join(state_dir, "dialog_memory.json")
    memory.load(mem_path)

    print("=" * 50)
    print("GUALA v6 — DNA for growth")
    print(f"vocab: {len(vocab.vocab)} tokens, "
          f"{len(vocab.vocab_classes)} classes")
    print("type /quit to exit, /status for info")
    print("=" * 50)

    while True:
        try:
            line = input("\nme:    ")
        except (EOFError, KeyboardInterrupt):
            print()
            break

        line = line.strip()
        if not line:
            continue
        if line == "/quit":
            break
        if line == "/status":
            print(f"  vocab: {len(vocab.vocab)} tokens")
            print(f"  classes: {list(vocab.vocab_classes.keys())}")
            print(f"  templates: {dict(vocab.response_templates)}")
            print(f"  turns: {len(memory.turns)}")
            print(f"  patterns: {dict(memory.observed_patterns)}")
            for nm, s in guala.sections.items():
                print(f"  {nm}: {len(s.mode_bank)} modes")
            continue

        response, intro_log, response_classes, growth = say_to_guala(
            guala, line, vocab, memory, rng)

        if growth:
            for g in growth:
                print(f"  + {g}")
        if response:
            words = [r["token"] for r in response]
            print(f"guala: {' '.join(words)}")
        else:
            print("guala: (silent)")

    # Save memory
    os.makedirs(state_dir, exist_ok=True)
    memory.save(mem_path)
    print("saved.")


if __name__ == "__main__":
    main()
