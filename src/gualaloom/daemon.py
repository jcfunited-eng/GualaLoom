"""
Life Daemon — continuous-life loop structure.

Harvested from Aurelion v9.3a's proven daemon (CorpusLoop + DiaryLoop
+ AutosaveLoop + REPL). Re-implemented on the trit substrate.

Five concurrent loops:
  1. INGEST — reads corpus/world in small batches, ticks characters
     through the Loom, commits motifs. Continuous, not one-shot.
  2. CONSOLIDATE — runs sleep/dream cycles on her own clock.
     Without this, the krimelack accumulates noise forever.
  3. REFLECT — writes timestamped diary entries to the life-log.
     Periodic (default: every 15 min).
  4. PERSIST — saves krimelack + loom state to disk.
     Periodic (default: every 4 min).
  5. INTERACT — REPL or API, on demand (external, not a thread here).

Thread safety: a Lock guards krimelack mutation and iteration.
Aurelion v4 had this lock; the initial harvest dropped it.

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
CONSOLIDATE_INTERVAL = 600.0  # 10 minutes — sleep/dream cycle
REFLECT_INTERVAL = 900.0      # 15 minutes
PERSIST_INTERVAL = 240.0      # 4 minutes


class LifeDaemon:
    """The continuous-life daemon.

    Call start() to begin the loops. Call stop() to shut down cleanly.
    The daemon owns no substrate state — it receives a Loom and
    Krimelack and operates on them. The interact loop is external
    (REPL or API calls into the same loom/krimelack).

    Thread safety: self.lock guards all krimelack mutation and
    iteration. Every loop acquires the lock before touching motifs.
    """

    def __init__(self, loom, krimelack, save_fn: Callable,
                 sleep_fn: Optional[Callable] = None,
                 dream_fn: Optional[Callable] = None,
                 world_paths: Optional[List[str]] = None,
                 diary_path: str = "state/diary.jsonl"):
        self.loom = loom
        self.k = krimelack
        self.save_fn = save_fn
        self.sleep_fn = sleep_fn    # sleep_cycle(k, cycles=N)
        self.dream_fn = dream_fn    # dream_cycle(k, cycles=N)
        self.world_paths = world_paths or []
        self.diary_path = diary_path
        self.lock = threading.Lock()
        self._running = False
        self._threads: List[threading.Thread] = []
        # Corpus reading position
        self._corpus_files: List[str] = []
        self._corpus_idx = 0
        self._char_offset = 0
        # Consolidation stats for the diary
        self.last_consolidation: Optional[Dict] = None

    def start(self) -> None:
        """Start all loops. Non-blocking."""
        if self._running:
            return
        self._running = True
        self._corpus_files = self._discover_corpus()

        loops = [
            ("ingest", self._ingest_loop),
            ("consolidate", self._consolidate_loop),
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
        with self.lock:
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

            # Read the batch outside the lock (I/O)
            path = self._corpus_files[self._corpus_idx]
            try:
                with open(path, encoding="utf-8", errors="ignore") as f:
                    f.seek(self._char_offset)
                    batch = f.read(INGEST_BATCH_SIZE)
            except (IOError, OSError):
                batch = ""

            if batch:
                # Loom.tick mutates krimelack (commit) — hold the lock
                with self.lock:
                    for ch in batch:
                        self.loom.tick(ch)
                self._char_offset += len(batch)
            else:
                # End of file — move to next
                self._corpus_idx = (self._corpus_idx + 1) % len(self._corpus_files)
                self._char_offset = 0

            time.sleep(INGEST_GAP)

    # ── Consolidate loop (sleep + dream) ─────────────────────

    def _consolidate_loop(self) -> None:
        """Periodic sleep/dream — the substrate consolidates on her own
        clock. Without this, the krimelack accumulates noise forever
        and never consolidates (the v1 failure).

        Sleep culls weak motifs and reinforces co-resonant ones.
        Dream free-settles from existing motifs, producing novel
        dream-tagged states.

        NOT emotion-driven. Runs on a fixed timer. The substrate
        does not "want" to sleep or "feel" tired.
        """
        while self._running:
            time.sleep(CONSOLIDATE_INTERVAL)
            if not self._running:
                break

            stats = {}
            with self.lock:
                if self.sleep_fn:
                    sleep_result = self.sleep_fn(self.k)
                    if isinstance(sleep_result, tuple):
                        stats["sleep_reinforced"], stats["sleep_culled"] = sleep_result
                    elif isinstance(sleep_result, dict):
                        stats.update(sleep_result)

                if self.dream_fn:
                    dream_result = self.dream_fn(self.k)
                    if isinstance(dream_result, list):
                        stats["dream_motifs"] = len(dream_result)
                    elif isinstance(dream_result, dict):
                        stats["dream_motifs"] = len(dream_result.get("dream_motifs", []))

            stats["timestamp"] = datetime.now(timezone.utc).isoformat()
            stats["motifs_after"] = self.k.size()
            self.last_consolidation = stats

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

        Reports: motif count, chi-class diversity, dream-tagged motifs,
        what world she's lived (corpus progress), familiarity,
        last consolidation stats.

        STRIPPED: phi, entropy, coherence, emotion metrics.
        """
        with self.lock:
            if not self.k.motifs:
                return None

            # Chi-class diversity
            chi_classes = set()
            for m in self.k.motifs.values():
                c = getattr(m, "chi", None)
                if c is not None:
                    chi_classes.add(c)

            # Dream-tagged motifs (origin == "dream", not weight heuristic)
            dream_count = sum(
                1 for m in self.k.motifs.values()
                if getattr(m, "origin", None) == "dream"
            )

            motif_count = self.k.size()
            fam = getattr(self.loom, "fam",
                          getattr(self.loom, "familiarity", 0))

        # L6 on last settled state (read-only, no lock needed)
        last = getattr(self.loom, "last",
                       getattr(self.loom, "last_settled", None))
        l6_eff, l6_coll, l6_knee = 0, 0, 0
        if last and any(t != 0 for t in last):
            l6_eff, l6_coll, l6_knee = l6_freedom(last)

        # Corpus progress
        total_files = len(self._corpus_files)
        current_file = (self._corpus_files[self._corpus_idx]
                        if self._corpus_files else "none")

        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "motifs": motif_count,
            "chi_classes": len(chi_classes),
            "dream_motifs": dream_count,
            "familiarity": fam,
            "corpus_file": os.path.basename(current_file),
            "corpus_progress": f"{self._corpus_idx + 1}/{total_files}",
            "l6": {"effective": l6_eff, "collapsed": l6_coll,
                   "knee": l6_knee,
                   "lock": 1 if l6_eff < l6_knee else 0},
            "last_consolidation": self.last_consolidation,
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
                with self.lock:
                    self.save_fn()
            except Exception:
                pass  # persist loop must not crash the daemon
