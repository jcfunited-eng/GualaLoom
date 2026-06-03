"""Entry point for `python -m gualaloom`."""

import sys
from pathlib import Path

from .krimelack import Krimelack
from .loom import Loom
from .persist import (
    load_krimelack, load_loom_state, save_krimelack, save_loom_state,
    save_dream, ensure_dirs,
)
from .sleep import sleep_cycle, dream_cycle
from .repl import run_repl


CORPUS_DIR = Path("corpus")
CONTEXT_CHARS = 4


def seed_corpus(loom: Loom, krimelack: Krimelack) -> None:
    """Feed the seed corpus on first run, then sleep on it."""
    if not CORPUS_DIR.exists():
        print("  no corpus/ directory found, skipping seed.")
        return

    files = sorted(CORPUS_DIR.glob("*.md"))
    if not files:
        print("  no .md files in corpus/, skipping seed.")
        return

    total_chars = 0
    for path in files:
        text = path.read_text()
        print(f"  feeding {path.name} ({len(text)} chars) ...", end=" ",
              flush=True)
        loom.feed(text)
        total_chars += len(text)
        print("done.")

    print(f"  total: {total_chars} chars fed, "
          f"{krimelack.size()} motifs committed")

    # Sleep on the corpus — consolidate (200 cycles per spec)
    print("  sleeping on corpus (200 cycles) ...", end=" ", flush=True)
    stats = sleep_cycle(krimelack, cycles=200)
    print(f"{stats['reinforcements']} reinforcements, "
          f"{stats['merges']} merges, {stats['decay_culled']} culls")

    # Dream — longer initial dream to seed creative motifs
    print("  dreaming (200 cycles) ...", end=" ", flush=True)
    dream = dream_cycle(krimelack, cycles=200)
    save_dream(dream)
    n_dream = len(dream.get("dream_motifs", []))
    print(f"{n_dream} dream motifs")

    # Save after seeding
    save_krimelack(krimelack)
    save_loom_state(
        context_chars=loom.ctx,
        recent=loom.recent,
        familiarity=loom.familiarity,
        last_settled=loom.last_settled,
    )
    print(f"  seed complete: {krimelack.size()} motifs persisted")


def main() -> None:
    ensure_dirs()

    # Load or initialize krimelack
    krimelack = load_krimelack()
    is_first_run = krimelack.size() == 0

    # Initialize loom
    loom = Loom(krimelack, context_chars=CONTEXT_CHARS)

    # Restore loom state if persisted
    saved = load_loom_state()
    if saved:
        loom.restore(
            recent=saved.get("recent_chars", []),
            familiarity=saved.get("familiarity", 0),
            last_settled=tuple(saved["last_settled"]) if saved.get("last_settled") else None,
        )

    # First run: seed corpus
    if is_first_run:
        print("first run — seeding corpus")
        seed_corpus(loom, krimelack)
        print()

    # Enter REPL
    run_repl(loom, krimelack)


if __name__ == "__main__":
    main()
