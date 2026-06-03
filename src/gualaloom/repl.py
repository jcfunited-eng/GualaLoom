"""
Interactive REPL — Joe types, substrate responds.

Commands:
  /sleep   — trigger sleep cycle immediately
  /dream   — trigger dream cycle immediately
  /wake    — (no-op unless sleeping, included for symmetry)
  /status  — show krimelack size, familiarity, last settled stats
  /dreams  — recall dream-tagged motifs
  /quit    — save and exit
"""

import sys
import time
import threading
from typing import Optional

from .loom import Loom
from .krimelack import Krimelack
from .generate import generate_response
from .sleep import sleep_cycle, dream_cycle
from .persist import save_krimelack, save_loom_state, save_dream


AUTO_SLEEP_SECONDS = 300  # 5 minutes


def _save_all(loom: Loom, krimelack: Krimelack) -> None:
    save_krimelack(krimelack)
    save_loom_state(
        context_chars=loom.ctx,
        recent=loom.recent,
        familiarity=loom.familiarity,
        last_settled=loom.last_settled,
    )


def _handle_command(cmd: str, loom: Loom, krimelack: Krimelack) -> Optional[str]:
    """Handle a /command. Returns response text, or None if not a command."""
    parts = cmd.strip().split()
    if not parts or not parts[0].startswith("/"):
        return None

    verb = parts[0].lower()

    if verb == "/quit":
        print("saving state ...", end=" ", flush=True)
        _save_all(loom, krimelack)
        print("ok.")
        sys.exit(0)

    elif verb == "/sleep":
        print("sleeping ...", end=" ", flush=True)
        stats = sleep_cycle(krimelack, cycles=200)
        _save_all(loom, krimelack)
        return (f"{stats['cycles_run']} cycles, "
                f"{stats['reinforcements']} reinforcements, "
                f"{stats['merges']} merges, "
                f"{stats['decay_culled']} culls")

    elif verb == "/dream":
        print("dreaming ...", end=" ", flush=True)
        dream = dream_cycle(krimelack, cycles=50)
        save_dream(dream)
        _save_all(loom, krimelack)
        n_dream = len(dream.get("dream_motifs", []))
        return (f"{dream['cycles_run']} cycles, "
                f"{n_dream} dream motifs, "
                f"{dream['reinforcements']} reinforcements")

    elif verb == "/wake":
        return "already awake."

    elif verb == "/status":
        settled_len = len(loom.last_settled) if loom.last_settled else 0
        coll = sum(1 for t in loom.last_settled if t != 0) if loom.last_settled else 0
        return (f"krimelack: {krimelack.size()} motifs | "
                f"familiarity: {loom.familiarity} | "
                f"last settled: {coll}/{settled_len} collapsed")

    elif verb == "/dreams":
        dream_motifs = [m for m in krimelack.motifs.values()
                        if m.origin == "dream"]
        if not dream_motifs:
            return "no dreams yet."
        # Recall from dream motifs by generating from them
        lines = []
        for dm in dream_motifs[:5]:
            fp_short = dm.fingerprint[:8]
            lines.append(f"  [{fp_short}] weight={dm.weight} age={dm.age}")
        return f"{len(dream_motifs)} dream motifs:\n" + "\n".join(lines)

    else:
        return f"unknown command: {verb}"


class AutoSleepTimer:
    """Triggers auto-sleep after idle timeout."""

    def __init__(self, loom: Loom, krimelack: Krimelack):
        self.loom = loom
        self.krimelack = krimelack
        self._timer: Optional[threading.Timer] = None

    def reset(self) -> None:
        if self._timer:
            self._timer.cancel()
        self._timer = threading.Timer(AUTO_SLEEP_SECONDS, self._fire)
        self._timer.daemon = True
        self._timer.start()

    def _fire(self) -> None:
        print("\n[auto-sleep: 5 min idle]")
        stats = sleep_cycle(self.krimelack, cycles=100)
        dream = dream_cycle(self.krimelack, cycles=25)
        save_dream(dream)
        _save_all(self.loom, self.krimelack)
        n_dream = len(dream.get("dream_motifs", []))
        print(f"  sleep: {stats['reinforcements']} reinforcements, "
              f"{stats['merges']} merges, {stats['decay_culled']} culls")
        print(f"  dream: {n_dream} dream motifs, "
              f"{dream['reinforcements']} reinforcements")
        print("> ", end="", flush=True)

    def stop(self) -> None:
        if self._timer:
            self._timer.cancel()


def run_repl(loom: Loom, krimelack: Krimelack) -> None:
    """Main REPL loop."""
    print(f"GualaLoom v1 — substrate boot")
    print(f"krimelack: {krimelack.size()} motifs loaded")
    print(f"commands: /sleep /dream /status /dreams /quit")
    print()

    auto_sleep = AutoSleepTimer(loom, krimelack)

    try:
        while True:
            auto_sleep.reset()
            try:
                line = input("> ")
            except EOFError:
                break

            if not line.strip():
                continue

            # Check for commands
            cmd_response = _handle_command(line, loom, krimelack)
            if cmd_response is not None:
                print(cmd_response)
                continue

            # Feed input to substrate character by character
            for ch in line:
                loom.tick(ch)
            # Feed the implicit newline/space boundary
            loom.tick(" ")

            # Generate response
            response = generate_response(loom, krimelack)
            if response:
                print(response)
            else:
                print(". . .")

            # Persist after each exchange
            _save_all(loom, krimelack)

    except KeyboardInterrupt:
        print()

    finally:
        auto_sleep.stop()
        print("saving state ...", end=" ", flush=True)
        _save_all(loom, krimelack)
        print("ok.")
