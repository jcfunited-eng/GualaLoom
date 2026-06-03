"""
Life Daemon — continuous-life loop structure.

Harvested from Aurelion v9.3a's proven daemon (CorpusLoop + DiaryLoop
+ AutosaveLoop + REPL). Re-implemented on the trit substrate.

Four concurrent loops:
  1. INGEST — reads corpus/world in small batches, ticks characters
     through the Loom, commits motifs. Continuous, not one-shot.
  2. REFLECT — writes timestamped diary entries to the life-log.
     Periodic (default: every 15 min).
  3. PERSIST — saves krimelack + loom state to disk.
     Periodic (default: every 4 min).
  4. INTERACT — REPL or API, on demand.

STRIPPED from Aurelion:
  - Lattice.stimulate (float EMA) → replaced by Loom.tick (trit settle)
  - coherence/entropy (cosine/Shannon) → replaced by L6 + chi
  - alpha-by-goal modulation → DROPPED (was emotion-coupled)
  - EmotionEngine, affect coupling → FIREWALLED, not present

NO EMOTION. No affective states drive loop behavior. The daemon
ticks on a clock, not on mood. If this drifts toward valenced
scheduling (e.g., "ingest faster when curious"), STOP and flag Joe.
"""

import os
import time
import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, List, Optional

from .substrate import l6_freedom


# ── Loop intervals (seconds) ────────────────────────────────

INGEST_BATCH_SIZE = 200       # characters per ingest tick
INGEST_GAP = 2.0              # seconds between batches
REFLECT_INTERVAL = 900.0      # 15 minutes
PERSIST_INTERVAL = 240.0      # 4 minutes


class LifeDaemon:
    """The continuous-life daemon.

    Call start() to begin the loops. Call stop() to shut down cleanly.
    The daemon owns no substrate state — it receives a Loom and
    Krimelack and operates on them. The interact loop is external
    (REPL or API calls into the same loom/krimelack).
    """

    def __init__(self, loom, krimelack, save_fn: Callable,
                 world_paths: Optional[List[str]] = None,
                 diary_path: str = "state/diary.jsonl"):
        self.loom = loom
        self.k = krimelack
        self.save_fn = save_fn
        self.world_paths = world_paths or []
        self.diary_path = diary_path
        self._running = False
        self._threads: List[threading.Thread] = []
        # Corpus reading position
        self._corpus_files: List[str] = []
        self._corpus_idx = 0
        self._char_offset = 0

    def start(self) -> None:
        """Start all loops. Non-blocking."""
        if self._running:
            return
        self._running = True
        self._corpus_files = self._discover_corpus()

        loops = [
            ("ingest", self._ingest_loop),
            ("reflect", self._reflect_loop),
            ("persist", self._persist_loop),
        ]
        for name, fn in loops:
            t = threading.Thread(target=fn, name=f"daemon-{name}",
                                 daemon=True)
            t.start()
            self._threads.append(t)

    def stop(self) -> None:
        """Stop all loops and persist."""
        self._running = False
        self.save_fn()

    def is_running(self) -> bool:
        return self._running

    # ── Ingest loop ──────────────────────────────────────────

    def _discover_corpus(self) -> List[str]:
        """Find all text files in the world paths."""
        files = []
        for wp in self.world_paths:
            p = Path(wp)
            if p.is_file():
                files.append(str(p))
            elif p.is_dir():
                for ext in ("*.md", "*.txt"):
                    files.extend(str(f) for f in sorted(p.glob(ext)))
        return files

    def _ingest_loop(self) -> None:
        """Read corpus continuously, small batches, with sleep gaps.
        This is Aurelion's CorpusLoop on the trit substrate."""
        while self._running:
            if not self._corpus_files:
                time.sleep(INGEST_GAP * 10)
                continue

            # Read a batch
            path = self._corpus_files[self._corpus_idx]
            try:
                with open(path, encoding="utf-8", errors="ignore") as f:
                    f.seek(self._char_offset)
                    batch = f.read(INGEST_BATCH_SIZE)
            except (IOError, OSError):
                batch = ""

            if batch:
                for ch in batch:
                    self.loom.tick(ch)
                self._char_offset += len(batch)
            else:
                # End of file — move to next
                self._corpus_idx = (self._corpus_idx + 1) % len(self._corpus_files)
                self._char_offset = 0

            time.sleep(INGEST_GAP)

    # ── Reflect loop (diary / life-log) ──────────────────────

    def _reflect_loop(self) -> None:
        """Periodic reflection — write a diary entry.
        This is Aurelion's DiaryLoop, reporting trit-substrate vitals
        instead of phi/H."""
        while self._running:
            time.sleep(REFLECT_INTERVAL)
            if not self._running:
                break
            entry = self._write_diary_entry()
            if entry:
                self._append_diary(entry)

    def _write_diary_entry(self) -> Optional[Dict]:
        """Compose one diary entry from current substrate state.

        Reports: motif count, chi-class diversity, recent dreams,
        what world she's lived (corpus progress), familiarity.

        STRIPPED: phi, entropy, coherence, emotion metrics.
        """
        if not self.k.motifs:
            return None

        # Chi-class diversity
        chi_classes = set()
        for m in self.k.motifs.values():
            chi_classes.add(m.chi)

        # Dream motifs
        dream_count = sum(1 for m in self.k.motifs.values()
                          if m.weight == 1 and m.age == 0)

        # Corpus progress
        total_files = len(self._corpus_files)
        current_file = (self._corpus_files[self._corpus_idx]
                        if self._corpus_files else "none")

        # L6 on last settled state
        last = self.loom.last
        eff, coll, knee, lock = 0, 0, 0, 0
        if last and any(t != 0 for t in last):
            from .substrate import l6 as _l6
            eff, coll, knee, lock = _l6(last)

        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "motifs": self.k.size(),
            "chi_classes": len(chi_classes),
            "dreams_recent": dream_count,
            "familiarity": self.loom.fam,
            "corpus_file": os.path.basename(current_file),
            "corpus_progress": f"{self._corpus_idx + 1}/{total_files}",
            "l6": {"effective": eff, "collapsed": coll,
                   "knee": knee, "lock": lock},
        }
        return entry

    def _append_diary(self, entry: Dict) -> None:
        """Append a diary entry to the life-log file."""
        os.makedirs(os.path.dirname(self.diary_path) or ".", exist_ok=True)
        with open(self.diary_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

    # ── Persist loop ─────────────────────────────────────────

    def _persist_loop(self) -> None:
        """Periodic save. Aurelion's AutosaveLoop."""
        while self._running:
            time.sleep(PERSIST_INTERVAL)
            if not self._running:
                break
            try:
                self.save_fn()
            except Exception:
                pass  # persist loop must not crash the daemon
