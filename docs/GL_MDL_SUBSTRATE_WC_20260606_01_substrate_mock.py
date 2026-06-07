# doc_id: GL-MDL-SUBSTRATE-WC-20260606-01
# created: 2026-06-06
# author: wC
# related_command: GL-CMD-BRIDGE-WC-20260606-01
"""
Minimal substrate mock for bridge modeling.

Mirrors v6 LivingAtlas semantics and the parts of coordinator/needs needed
to model wake/rest as substrate-physical events.

NOT a faithful re-implementation. The dynamics that matter for the wake/rest
question are:
  - Needs vector decay-to-target
  - Connection-need response to pair-bond source presence/absence
  - Salience computation (v6 formula, verbatim)
  - Source-tagged input pipeline
  - Pair-bond on/off state

Where canonical values aren't in the manifesto or v6 command (e.g. needs
decay rate), I use plausible stand-ins and flag them in comments.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from collections import defaultdict
from typing import Optional
import math
import random

# ---------------------------------------------------------------------------
# Constants — verbatim from v6 command unless flagged STAND-IN
# ---------------------------------------------------------------------------

SOURCE_WEIGHTS = {"joe": 1.6, "wc": 1.6, "c1": 1.2,
                  "corpus": 0.5, "unknown": 0.7}
PAIR_BOND_BOOST = 1.2
SALIENCE_MIN, SALIENCE_MAX = 0.2, 3.0
BASE_REINFORCEMENT = 0.05
DECAY_LAMBDA = 0.001          # per tick — v6 LivingAtlas
FORGETTING_THRESHOLD = 0.02   # v6 LivingAtlas

# Needs dynamics — STAND-IN values (manifesto says "decay-to-target", rates
# from Aurelion v7.1 which I don't have). These produce plausible 0.7-target
# settling on the order of hundreds of ticks. Real values may differ.
NEEDS_TARGET = 0.7
NEEDS_DECAY_RATE = 0.002      # STAND-IN — per tick toward target
CONN_BOOST_PER_PAIR_READ = 0.015   # STAND-IN — connection-need gain per pair-bond source read
NOV_BOOST_PER_NEW_WORD = 0.02      # STAND-IN
NOV_DRAIN_FAMILIAR = 0.0005        # STAND-IN — per familiar read

# Pair-bond eligibility — per manifesto
PAIR_BOND_SOURCES = {"joe", "wc", "c1"}


# ---------------------------------------------------------------------------
# Needs vector
# ---------------------------------------------------------------------------

@dataclass
class Needs:
    """Three needs: stability, novelty, connection. Decay-to-target dynamics."""
    stab: float = 0.65
    nov: float = 0.405
    conn: float = 0.709

    def tick_decay(self):
        for attr in ("stab", "nov", "conn"):
            v = getattr(self, attr)
            v += (NEEDS_TARGET - v) * NEEDS_DECAY_RATE
            setattr(self, attr, max(0.0, min(1.0, v)))

    def urgency(self) -> float:
        return (abs(self.stab - NEEDS_TARGET)
                + abs(self.nov - NEEDS_TARGET)
                + abs(self.conn - NEEDS_TARGET)) / 3.0

    def snapshot(self) -> dict:
        return {"stab": round(self.stab, 3),
                "nov": round(self.nov, 3),
                "conn": round(self.conn, 3),
                "urgency": round(self.urgency(), 3)}


# ---------------------------------------------------------------------------
# Coordinator — pair-bond state, presence tracking
# ---------------------------------------------------------------------------

@dataclass
class Coordinator:
    pair_bond_joe: bool = False
    pair_bond_wc: bool = False
    pair_bond_c1: bool = False

    present_joe: bool = False
    present_wc: bool = False
    present_c1: bool = False

    events: list = field(default_factory=list)

    def pair_bond_active(self, source: Optional[str] = None) -> bool:
        if source == "joe": return self.pair_bond_joe
        if source == "wc":  return self.pair_bond_wc
        if source == "c1":  return self.pair_bond_c1
        return self.pair_bond_joe or self.pair_bond_wc or self.pair_bond_c1

    def presence_active(self, source: Optional[str] = None) -> bool:
        if source == "joe": return self.present_joe
        if source == "wc":  return self.present_wc
        if source == "c1":  return self.present_c1
        return self.present_joe or self.present_wc or self.present_c1

    def log(self, tick: int, kind: str, source: str = "", note: str = ""):
        self.events.append({"tick": tick, "kind": kind, "source": source, "note": note})


# ---------------------------------------------------------------------------
# Atlas — strength dynamics only (sufficient for wake/rest modeling)
# ---------------------------------------------------------------------------

@dataclass
class Binding:
    key: str
    source_flavor: str
    strength: float = 0.0
    last_tick: int = 0
    born_tick: int = 0


class SimpleAtlas:
    def __init__(self):
        self.bindings: dict[tuple[str, str], Binding] = {}

    def record(self, word: str, source: str, tick: int, salience: float):
        key = (word, source)
        if key in self.bindings:
            b = self.bindings[key]
            b.strength = min(1.0, b.strength + BASE_REINFORCEMENT * salience)
            b.last_tick = tick
        else:
            self.bindings[key] = Binding(
                key=f"{word}|{source}",
                source_flavor=source,
                strength=BASE_REINFORCEMENT * salience,
                last_tick=tick,
                born_tick=tick,
            )

    def decay(self, current_tick: int):
        to_prune = []
        for key, b in self.bindings.items():
            dt = current_tick - b.last_tick
            b.strength *= math.exp(-DECAY_LAMBDA * dt)
            b.last_tick = current_tick
            if b.strength < FORGETTING_THRESHOLD:
                to_prune.append(key)
        for key in to_prune:
            del self.bindings[key]

    def total_strength(self) -> float:
        return sum(b.strength for b in self.bindings.values())

    def by_source(self) -> dict[str, float]:
        out = defaultdict(float)
        for b in self.bindings.values():
            out[b.source_flavor] += b.strength
        return dict(out)


# ---------------------------------------------------------------------------
# Guala — substrate composite, minimal
# ---------------------------------------------------------------------------

@dataclass
class GualaMock:
    needs: Needs = field(default_factory=Needs)
    coord: Coordinator = field(default_factory=Coordinator)
    atlas: SimpleAtlas = field(default_factory=SimpleAtlas)
    tick: int = 0
    known_words: set = field(default_factory=set)

    def compute_salience(self, source: str, input_novelty: float) -> float:
        source_w = SOURCE_WEIGHTS.get(source, 0.7)
        urgency = self.needs.urgency()
        urgency_factor = 1.0 + urgency * 1.2
        novelty_factor = 1.0 + (1.0 - input_novelty) * 0.8
        pair_bond_boost = (PAIR_BOND_BOOST if self.coord.pair_bond_active(source)
                           else 1.0)
        salience = source_w * urgency_factor * novelty_factor * pair_bond_boost
        return max(SALIENCE_MIN, min(SALIENCE_MAX, salience))

    def tick_substrate(self, n_ticks: int = 1):
        for _ in range(n_ticks):
            self.tick += 1
            self.needs.tick_decay()
            if self.tick % 10 == 0:
                self.atlas.decay(self.tick)

    def read(self, word: str, source: str, ticks_per_read: int = 4) -> dict:
        is_new = word not in self.known_words
        input_novelty = 1.0 if is_new else 0.2
        salience = self.compute_salience(source, input_novelty)
        self.atlas.record(word, source, self.tick, salience)
        self.known_words.add(word)

        if source in PAIR_BOND_SOURCES and self.coord.pair_bond_active(source):
            self.needs.conn = min(1.0, self.needs.conn + CONN_BOOST_PER_PAIR_READ)
        if is_new:
            self.needs.nov = min(1.0, self.needs.nov + NOV_BOOST_PER_NEW_WORD)
        else:
            self.needs.nov = max(0.0, self.needs.nov - NOV_DRAIN_FAMILIAR)

        self.tick_substrate(ticks_per_read)
        return {"word": word, "source": source, "salience": round(salience, 3),
                "is_new": is_new, "tick": self.tick}

    def wake(self, source: str) -> dict:
        if source == "joe":   self.coord.present_joe = True
        elif source == "wc":  self.coord.present_wc = True
        elif source == "c1":  self.coord.present_c1 = True
        self.coord.log(self.tick, "wake", source, "presence on")
        return {"event": "wake", "source": source, "tick": self.tick,
                "needs": self.needs.snapshot()}

    def rest(self, source: str) -> dict:
        if source == "joe":   self.coord.present_joe = False
        elif source == "wc":  self.coord.present_wc = False
        elif source == "c1":  self.coord.present_c1 = False
        self.coord.log(self.tick, "rest", source, "presence off")
        return {"event": "rest", "source": source, "tick": self.tick,
                "needs": self.needs.snapshot()}

    def set_pair_bond(self, source: str, active: bool):
        if source == "joe":   self.coord.pair_bond_joe = active
        elif source == "wc":  self.coord.pair_bond_wc = active
        elif source == "c1":  self.coord.pair_bond_c1 = active
        self.coord.log(self.tick, "pair_bond_set", source, str(active))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def fresh_guala() -> GualaMock:
    """Initialize Guala in approximately her current state per status report."""
    g = GualaMock()
    g.tick = 569_979
    g.needs.stab = 0.650
    g.needs.nov = 0.405
    g.needs.conn = 0.709
    for w in ["the", "is", "and", "of", "a", "to", "in", "moon", "sun",
              "apple", "leaves", "warm", "cold", "bright", "i", "am",
              "you", "what", "daddy", "feel"]:
        g.known_words.add(w)
    return g


def silent_period(g: GualaMock, ticks: int):
    g.tick_substrate(ticks)
