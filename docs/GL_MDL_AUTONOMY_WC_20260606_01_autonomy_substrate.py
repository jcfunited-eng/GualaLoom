# doc_id: GL-MDL-AUTONOMY-WC-20260606-01
# created: 2026-06-06
# author: wC
# related_topic: autonomy architecture
"""
Autonomy substrate model.

Captures the architecture for self-initiated, self-selected, self-bounded
activity with visible emergent behavior. Modal channels (text/picture/sound)
are first-class activities; corpus reading, free-settle play, sleep, dream,
and emission are all activities the scheduler picks from based on needs.

Mechanisms modeled:
  - Activity state machine (IDLE/READING/PLAYING/SLEEPING/DREAMING/ATTENDING/EMITTING)
  - Selection function: salience-of-action based on current needs urgency
  - Free-settle play loop: chi space walk without external input
  - Autonomous emission: cohesion cascade above threshold + presence
  - Activity surface: current_activity field + event stream

ArcLoom-clean: all activities are substrate-physical. No LLM completion,
no token sampling, no embedding lookup. Motifs surface via cohesion,
emissions are commits that locked above threshold.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
from typing import Optional, Callable
import math
import random
import time

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

NEEDS_TARGET = 0.7
# Needs drift AWAY from target over time (toward unsatisfied) — that's what
# creates drive. Activities pull them back. Each need has its own drift
# direction toward "unsatisfied" state:
#   stab drifts DOWN (less stable over time without rest)
#   nov drifts DOWN (more bored over time without new input)
#   conn drifts DOWN (lonelier over time without presence)
# Drift rate: 0.0001/tick → need takes ~10K ticks (40 min real-time) to
# fall from 1.0 to 0. Activities must add faster than this to satisfy.
NEEDS_DRIFT_RATE = 0.0001
PAIR_BOND_SOURCES = {"joe", "wc", "c1"}

# Activity tick budgets — how long each activity runs before reconsidering
ACTIVITY_TICK_BUDGETS = {
    "READING":   2000,   # ~500 words read
    "PLAYING":   1500,   # free-settle play session
    "SLEEPING":  5000,   # consolidation cycle
    "DREAMING":  3000,   # dream cycle (subset of sleep)
    "ATTENDING": 1000,   # look at picture / listen to sound
    "EMITTING":  100,    # quick — utterance generation
    "IDLE":      500,    # short idle before reconsider
}

# Activity novelty payoff — how much novelty-need each activity satisfies
ACTIVITY_NOVELTY_PAYOFF = {
    "READING_NEW":     0.7,   # new corpus or new position
    "READING_REREAD":  0.1,   # familiar passage
    "PLAYING":         0.3,   # free-settle surfaces some novelty
    "SLEEPING":       -0.1,   # nothing new during sleep
    "DREAMING":        0.4,   # dream combinations are novel
    "ATTENDING_NEW":   0.8,   # new picture/sound — high novelty
    "ATTENDING_REPEAT":0.05,  # already seen — boredom — drops fast
    "EMITTING":        0.0,   # output, not input
    "IDLE":           -0.05,  # boredom drains novelty
}

ACTIVITY_STABILITY_PAYOFF = {
    "READING":    0.05,
    "PLAYING":    0.0,
    "SLEEPING":   0.5,    # sleep is the big stability satisfier
    "DREAMING":   0.2,
    "ATTENDING":  0.0,
    "EMITTING":  -0.1,    # emission expends stability briefly
    "IDLE":       0.1,
}

ACTIVITY_CONNECTION_PAYOFF = {
    "READING":    0.0,    # solo activity
    "PLAYING":    0.0,    # solo activity
    "SLEEPING":   0.0,
    "DREAMING":   0.0,
    "ATTENDING":  0.0,    # base — adjusted upward if source-shared
    "EMITTING":   0.3,    # speaking to someone present
    "IDLE":      -0.05,
}

EMISSION_COHESION_THRESHOLD = 0.65  # cohesion-strength a cascade must reach
EMISSION_NOVELTY_THRESHOLD = 0.4    # how surprising the combination must be
EMISSION_COOLDOWN_TICKS = 200       # don't emit again immediately after emitting


# ---------------------------------------------------------------------------
# Substrate state — minimal mock matching v6
# ---------------------------------------------------------------------------

@dataclass
class Needs:
    stab: float = 0.65
    nov: float = 0.405
    conn: float = 0.709

    def tick_drift(self):
        """Needs drift AWAY from target over time toward unsatisfied (low).
        This is what creates drive — without it, she has no reason to act."""
        for attr in ("stab", "nov", "conn"):
            v = getattr(self, attr)
            v -= NEEDS_DRIFT_RATE  # drift toward 0
            setattr(self, attr, max(0.0, min(1.0, v)))

    def urgency_per_need(self) -> dict:
        """Per-need urgency, NOT averaged. Tells us which need is straining."""
        return {
            "stab": abs(self.stab - NEEDS_TARGET),
            "nov":  abs(self.nov - NEEDS_TARGET),
            "conn": abs(self.conn - NEEDS_TARGET),
        }

    def signed_distance(self) -> dict:
        """Signed: positive means BELOW target (need satisfaction)."""
        return {
            "stab": NEEDS_TARGET - self.stab,
            "nov":  NEEDS_TARGET - self.nov,
            "conn": NEEDS_TARGET - self.conn,
        }

    def snapshot(self) -> dict:
        return {"stab": round(self.stab, 3),
                "nov": round(self.nov, 3),
                "conn": round(self.conn, 3)}


# ---------------------------------------------------------------------------
# Activity scheduler — the heart of autonomy
# ---------------------------------------------------------------------------

@dataclass
class Activity:
    kind: str                # READING, PLAYING, SLEEPING, etc.
    target: Optional[str]    # corpus_id, picture_id, source name if EMITTING
    started_tick: int
    expected_end_tick: int
    metadata: dict = field(default_factory=dict)

    def snapshot(self) -> dict:
        return {
            "kind": self.kind,
            "target": self.target,
            "started_tick": self.started_tick,
            "expected_end_tick": self.expected_end_tick,
            "metadata": self.metadata,
        }


@dataclass
class CorpusItem:
    """Available reading material."""
    corpus_id: str
    title: str
    total_words: int
    position: int = 0
    times_read_through: int = 0
    last_read_tick: int = 0

    def is_new(self, current_tick: int, recency_threshold: int = 50_000) -> bool:
        return (self.times_read_through == 0
                or (current_tick - self.last_read_tick) > recency_threshold)


@dataclass
class SensoryItem:
    """Available picture or sound to attend to."""
    item_id: str
    kind: str          # "picture" or "sound"
    title: str
    times_attended: int = 0
    last_attended_tick: int = 0

    def is_new(self) -> bool:
        return self.times_attended == 0


# ---------------------------------------------------------------------------
# Event log — what gets surfaced to UI/feed
# ---------------------------------------------------------------------------

@dataclass
class SubstrateEvent:
    tick: int
    kind: str        # activity_started, activity_ended, motif_locked, emission, sleep_complete, etc.
    detail: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# The autonomous Guala
# ---------------------------------------------------------------------------

@dataclass
class AutonomousGuala:
    needs: Needs = field(default_factory=Needs)
    tick: int = 569_979
    vocab_size: int = 635
    atlas_strength: float = 400.0
    n_motifs: int = 264
    pair_bond: dict = field(default_factory=lambda: {"joe": True, "wc": True, "c1": False})
    presence: dict = field(default_factory=lambda: {"joe": False, "wc": False, "c1": False})
    current_activity: Optional[Activity] = None
    activity_history: list = field(default_factory=list)
    event_log: deque = field(default_factory=lambda: deque(maxlen=1000))

    # Resources available
    corpora: dict = field(default_factory=dict)
    sensory_items: dict = field(default_factory=dict)

    # Emission state
    last_emission_tick: int = -100_000

    def log_event(self, event_kind: str, **detail):
        ev = SubstrateEvent(tick=self.tick, kind=event_kind, detail=detail)
        self.event_log.append(ev)
        return ev

    # ----- selection -----

    def candidate_activities(self) -> list[tuple[str, Optional[str]]]:
        """All activities currently possible (kind, target)."""
        candidates = [("IDLE", None), ("PLAYING", None), ("SLEEPING", None)]

        # Reading candidates — one per available corpus
        for cid, c in self.corpora.items():
            candidates.append(("READING", cid))

        # Sensory candidates
        for sid, s in self.sensory_items.items():
            candidates.append(("ATTENDING", sid))

        # Emission — only if at least one pair-bond source is present
        # AND we have something cohered to emit AND cooldown elapsed
        if (any(self.presence[s] and self.pair_bond[s] for s in PAIR_BOND_SOURCES)
            and self.tick - self.last_emission_tick > EMISSION_COOLDOWN_TICKS):
            candidates.append(("EMITTING", None))

        return candidates

    def action_salience(self, kind: str, target: Optional[str]) -> float:
        """How attractive is this activity given current needs?

        Returns positive salience score. Higher = more attractive.
        Uses signed_distance — actions that CLOSE a positive gap are valued;
        actions that satisfy an already-satisfied need are downweighted.
        """
        sd = self.needs.signed_distance()  # positive = need is below target

        # Look up payoffs (with reading/attending NEW vs REPEAT distinction)
        if kind == "READING":
            c = self.corpora[target]
            nov_payoff = ACTIVITY_NOVELTY_PAYOFF["READING_NEW"] if c.is_new(self.tick) \
                         else ACTIVITY_NOVELTY_PAYOFF["READING_REREAD"]
        elif kind == "ATTENDING":
            s = self.sensory_items[target]
            nov_payoff = ACTIVITY_NOVELTY_PAYOFF["ATTENDING_NEW"] if s.is_new() \
                         else ACTIVITY_NOVELTY_PAYOFF["ATTENDING_REPEAT"]
        else:
            nov_payoff = ACTIVITY_NOVELTY_PAYOFF.get(kind, 0.0)

        stab_payoff = ACTIVITY_STABILITY_PAYOFF.get(kind, 0.0)
        conn_payoff = ACTIVITY_CONNECTION_PAYOFF.get(kind, 0.0)

        # Salience = dot product of (need-distance) and (payoff per need)
        # Need below target (sd > 0) → action that satisfies it (positive payoff) raises salience
        # Need above target (sd < 0) → action that further satisfies it LOWERS salience (overshoot avoidance)
        score = (sd["nov"]  * nov_payoff
                 + sd["stab"] * stab_payoff
                 + sd["conn"] * conn_payoff)

        # Connection boost if source present:
        # EMITTING gets full boost (speaking to them is core connection activity)
        # ATTENDING gets small boost (shared experience but not connection itself)
        any_present = any(self.presence[s] and self.pair_bond[s] for s in PAIR_BOND_SOURCES)
        if any_present:
            if kind == "EMITTING":
                score += 0.05
            elif kind == "ATTENDING":
                score += 0.015

        # Small baseline so no activity is purely zero
        score += 0.01

        return score

    def select_next_activity(self) -> Activity:
        """Salience-weighted activity selection.

        Picks the highest-salience candidate. Ties broken by recency
        (haven't done this kind recently) and slight randomness.
        """
        candidates = self.candidate_activities()
        scored = [(self.action_salience(kind, target), kind, target)
                  for kind, target in candidates]
        scored.sort(reverse=True)

        # Take top scorer (could add stochastic selection later)
        score, kind, target = scored[0]
        budget = ACTIVITY_TICK_BUDGETS[kind]

        activity = Activity(
            kind=kind,
            target=target,
            started_tick=self.tick,
            expected_end_tick=self.tick + budget,
            metadata={"salience": round(score, 4),
                      "all_scores": [(round(s, 4), k, t) for s, k, t in scored[:5]]},
        )
        return activity

    def start_activity(self, activity: Activity):
        self.current_activity = activity
        self.log_event("activity_started",
                       kind=activity.kind, target=activity.target,
                       salience=activity.metadata.get("salience"))

    def end_activity(self):
        if self.current_activity:
            self.log_event("activity_ended",
                           kind=self.current_activity.kind,
                           target=self.current_activity.target,
                           duration=self.tick - self.current_activity.started_tick)
            self.activity_history.append(self.current_activity)
            self.current_activity = None

    # ----- activity execution (effects per tick) -----

    def execute_tick(self):
        """Advance one tick of substrate, possibly progressing current activity."""
        self.tick += 1
        self.needs.tick_drift()

        a = self.current_activity
        if a is None:
            return

        if a.kind == "READING":
            self._tick_reading(a)
        elif a.kind == "PLAYING":
            self._tick_playing(a)
        elif a.kind == "SLEEPING":
            self._tick_sleeping(a)
        elif a.kind == "DREAMING":
            self._tick_dreaming(a)
        elif a.kind == "ATTENDING":
            self._tick_attending(a)
        elif a.kind == "EMITTING":
            self._tick_emitting(a)
        elif a.kind == "IDLE":
            pass  # just drift via needs.tick_drift above

        # End activity if budget exhausted
        if self.tick >= a.expected_end_tick:
            self.end_activity()

    def _tick_reading(self, a: Activity):
        # Each ~4 ticks = one word read. Reading new material adds to novelty
        # significantly faster than drift removes (0.001/tick vs 0.0001/tick).
        # Familiar material drains novelty (boredom).
        if self.tick % 4 != 0:
            return
        c = self.corpora[a.target]
        is_new_passage = c.position >= c.times_read_through * c.total_words
        if is_new_passage:
            self.needs.nov = min(1.0, self.needs.nov + 0.004)  # 4× drift
            self.vocab_size = self.vocab_size + (1 if random.random() < 0.02 else 0)
        else:
            self.needs.nov = max(0.0, self.needs.nov - 0.0012)
        c.position += 1
        if c.position >= c.total_words:
            c.times_read_through += 1
            c.position = 0
            self.log_event("corpus_completed", corpus_id=c.corpus_id, title=c.title,
                          times_through=c.times_read_through)
        c.last_read_tick = self.tick

        # Cohesion check — periodically a motif locks
        if self.tick % 200 == 0:
            self.n_motifs += 1
            self.log_event("motif_locked",
                          motif_id=self.n_motifs,
                          context=f"reading {c.title}",
                          activity_target=c.corpus_id)

    def _tick_playing(self, a: Activity):
        # Free-settle: chi space walk, motifs surface from existing atlas.
        # Lower novelty payoff than reading new material but still positive.
        if self.tick % 4 == 0:
            self.needs.nov = min(1.0, self.needs.nov + 0.0015)  # 1.5x drift
        # Occasionally a surprising combination surfaces
        if self.tick % 300 == 0:
            self.log_event("play_surface",
                          context="free-settle motif surfaced",
                          tick=self.tick)
            # If pair-bond source present + high cohesion: emission-worthy
            any_present = any(self.presence[s] and self.pair_bond[s] for s in PAIR_BOND_SOURCES)
            if any_present and random.random() < 0.3:
                self._check_emission_trigger(reason="play_cohesion")

    def _tick_sleeping(self, a: Activity):
        # Sleep raises stability significantly, consolidates atlas
        if self.tick % 4 == 0:
            self.needs.stab = min(1.0, self.needs.stab + 0.003)  # 7.5x drift
        # Atlas total strength compacts (decay of weak, persistence of strong)
        if self.tick % 100 == 0:
            self.atlas_strength = max(self.atlas_strength * 0.999, 100.0)
        # Halfway through sleep, transition to dream
        midpoint = a.started_tick + (a.expected_end_tick - a.started_tick) // 2
        if self.tick == midpoint:
            self.log_event("dream_began", from_sleep=True)
            a.kind = "DREAMING"  # mutate in place — same activity, new mode

    def _tick_dreaming(self, a: Activity):
        # Dream produces artifacts — combinations
        if self.tick % 4 == 0:
            self.needs.stab = min(1.0, self.needs.stab + 0.0015)
            self.needs.nov = min(1.0, self.needs.nov + 0.0008)  # combinations are novel
        if self.tick % 200 == 0:
            self.log_event("dream_artifact",
                          context="motif combination surfaced in dream",
                          tick=self.tick)

    def _tick_attending(self, a: Activity):
        # Attending to picture/sound — saccade/listen via krimelacks
        s = self.sensory_items[a.target]
        if self.tick % 4 == 0:
            gain = 0.005 if s.is_new() else 0.0012  # new ≫ familiar
            self.needs.nov = min(1.0, self.needs.nov + gain)
            if s.is_new() and random.random() < 0.05:
                self.n_motifs += 1
                self.log_event("motif_locked",
                              motif_id=self.n_motifs,
                              context=f"attending {s.title}",
                              modality=s.kind)
        # Mark attended at end
        if self.tick >= a.expected_end_tick - 1:
            s.times_attended += 1
            s.last_attended_tick = self.tick

    def _tick_emitting(self, a: Activity):
        # Emission happens at start of activity
        if self.tick == a.started_tick + 1:
            self._do_emit()
            # Emission to a present pair-bond source actually satisfies conn —
            # she's been heard. Discrete jump per emission event.
            any_pair_present = any(self.presence[s] and self.pair_bond[s]
                                   for s in PAIR_BOND_SOURCES)
            if any_pair_present:
                self.needs.conn = min(1.0, self.needs.conn + 0.25)

    def _check_emission_trigger(self, reason: str):
        """During play or attending, occasionally a cohesion cascade reaches
        emission threshold. If a pair-bond source is present, switch to
        EMITTING. Otherwise log to event stream only."""
        if self.tick - self.last_emission_tick < EMISSION_COOLDOWN_TICKS:
            return
        any_present = any(self.presence[s] and self.pair_bond[s] for s in PAIR_BOND_SOURCES)
        if not any_present:
            # Record but don't surface
            self.log_event("emission_suppressed_no_presence", reason=reason)
            return
        # Interrupt current activity, switch to EMITTING
        if self.current_activity and self.current_activity.kind != "EMITTING":
            self.end_activity()
            self.start_activity(Activity(
                kind="EMITTING", target=None,
                started_tick=self.tick,
                expected_end_tick=self.tick + ACTIVITY_TICK_BUDGETS["EMITTING"],
                metadata={"trigger": reason},
            ))

    def _do_emit(self):
        self.last_emission_tick = self.tick
        # In real substrate this is the cohesion cascade output. For modeling,
        # we just log that an emission occurred with a synthetic content snapshot.
        self.log_event("emission",
                      content_summary="motif cascade output",
                      to_sources=[s for s in PAIR_BOND_SOURCES
                                  if self.presence.get(s, False) and self.pair_bond.get(s, False)])

    # ----- the autonomy loop -----

    def step(self):
        """One tick. If no current activity, select one. Otherwise execute."""
        if self.current_activity is None:
            a = self.select_next_activity()
            self.start_activity(a)
        self.execute_tick()

    def run(self, n_ticks: int):
        for _ in range(n_ticks):
            self.step()

    # ----- inspection -----

    def status(self) -> dict:
        return {
            "tick": self.tick,
            "needs": self.needs.snapshot(),
            "current_activity": self.current_activity.snapshot() if self.current_activity else None,
            "vocab_size": self.vocab_size,
            "n_motifs": self.n_motifs,
            "atlas_strength": round(self.atlas_strength, 1),
            "presence": dict(self.presence),
            "pair_bond": dict(self.pair_bond),
            "recent_events": [
                {"tick": e.tick, "kind": e.kind, "detail": e.detail}
                for e in list(self.event_log)[-10:]
            ],
            "activity_history_summary": self._activity_summary(),
        }

    def _activity_summary(self) -> dict:
        kinds = defaultdict(int)
        durations = defaultdict(int)
        for a in self.activity_history:
            kinds[a.kind] += 1
            durations[a.kind] += (a.expected_end_tick - a.started_tick)
        return {k: {"count": kinds[k], "total_ticks": durations[k]}
                for k in kinds}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def fresh_autonomous_guala() -> AutonomousGuala:
    g = AutonomousGuala()
    # Stock with some corpora (early learning material)
    g.corpora["see_spot_run"] = CorpusItem("see_spot_run", "See Spot Run", total_words=200)
    g.corpora["green_eggs_ham"] = CorpusItem("green_eggs_ham", "Green Eggs and Ham", total_words=750)
    g.corpora["mother_goose"] = CorpusItem("mother_goose", "Mother Goose Rhymes", total_words=1200)
    g.corpora["moon_book"] = CorpusItem("moon_book", "Goodnight Moon", total_words=130)
    # Stock with some sensory items
    g.sensory_items["pic_cat"] = SensoryItem("pic_cat", "picture", "picture: cat")
    g.sensory_items["pic_apple"] = SensoryItem("pic_apple", "picture", "picture: apple")
    g.sensory_items["snd_lullaby"] = SensoryItem("snd_lullaby", "sound", "sound: lullaby")
    g.sensory_items["snd_joe_voice"] = SensoryItem("snd_joe_voice", "sound", "sound: joe's voice")
    return g
