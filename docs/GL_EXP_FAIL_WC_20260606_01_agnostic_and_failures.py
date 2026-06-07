# doc_id: GL-EXP-FAIL-WC-20260606-01
# created: 2026-06-06
# author: wC
# related_command: GL-CMD-BRIDGE-WC-20260606-01
"""
Experiment 5: Source-agnostic atlas keys (matches v6 production) + failure modes.
"""

from GL_MDL_SUBSTRATE_WC_20260606_01_substrate_mock import (
    fresh_guala, silent_period, GualaMock,
    BASE_REINFORCEMENT, DECAY_LAMBDA, FORGETTING_THRESHOLD,
)
from GL_EXP_PULSE_WC_20260606_01_pulse_and_target import (
    wake_v2, silent_period_with_pulses, presence_pulse,
)
import math
from dataclasses import dataclass, field


@dataclass
class AgnosticBinding:
    word: str
    strength: float = 0.0
    last_tick: int = 0
    born_tick: int = 0
    source_contributions: dict = field(default_factory=dict)


class AgnosticAtlas:
    """Source-agnostic — matches v6 production semantics."""
    def __init__(self):
        self.bindings: dict[str, AgnosticBinding] = {}

    def record(self, word: str, source: str, tick: int, salience: float):
        if word in self.bindings:
            b = self.bindings[word]
            delta = BASE_REINFORCEMENT * salience
            b.strength = min(1.0, b.strength + delta)
            b.last_tick = tick
            b.source_contributions[source] = (
                b.source_contributions.get(source, 0.0) + delta)
        else:
            delta = BASE_REINFORCEMENT * salience
            self.bindings[word] = AgnosticBinding(
                word=word, strength=delta, last_tick=tick, born_tick=tick,
                source_contributions={source: delta},
            )

    def decay(self, current_tick: int):
        to_prune = []
        for word, b in self.bindings.items():
            dt = current_tick - b.last_tick
            factor = math.exp(-DECAY_LAMBDA * dt)
            b.strength *= factor
            b.source_contributions = {s: v * factor
                                       for s, v in b.source_contributions.items()}
            b.last_tick = current_tick
            if b.strength < FORGETTING_THRESHOLD:
                to_prune.append(word)
        for word in to_prune:
            del self.bindings[word]

    def total_strength(self) -> float:
        return sum(b.strength for b in self.bindings.values())

    def by_source(self) -> dict:
        out = {}
        for b in self.bindings.values():
            for s, v in b.source_contributions.items():
                out[s] = out.get(s, 0.0) + v
        return out


def patched_guala():
    g = fresh_guala()
    g.atlas = AgnosticAtlas()
    return g


def converse(g: GualaMock, source: str, words: list, ticks_between: int = 50):
    for w in words:
        g.read(w, source)
        for _ in range(ticks_between):
            g.tick += 1
            g.needs.tick_decay()
            if g.tick % 10 == 0:
                g.atlas.decay(g.tick)
            if g.tick % 50 == 0:
                presence_pulse(g)


def experiment_5a_shared_vocab():
    print("=" * 70)
    print("EXPERIMENT 5a: Shared vocab — wC reinforces corpus words")
    print("=" * 70)

    g = patched_guala()
    g.set_pair_bond("wc", True)
    for _ in range(20):
        g.read("hello", "corpus")
        g.tick_substrate(10)
    base = g.atlas.bindings["hello"].strength
    base_contribs = dict(g.atlas.bindings["hello"].source_contributions)
    print(f"\nAfter 20 corpus 'hello' reads:")
    print(f"  strength: {base:.4f}")
    print(f"  source contributions: {base_contribs}")

    wake_v2(g, "wc")
    converse(g, "wc", ["hello", "hello", "hello"])
    g.rest("wc")
    after = g.atlas.bindings["hello"].strength
    after_contribs = dict(g.atlas.bindings["hello"].source_contributions)
    print(f"\nAfter wC session (3 'hello's pair-bonded):")
    print(f"  strength: {after:.4f}")
    print(f"  source contributions: {after_contribs}")
    wc_share = after_contribs.get("wc", 0.0)
    print(f"  wC fraction: {wc_share/after*100:.1f}%")


def experiment_5b_long_term_trace():
    print("\n" + "=" * 70)
    print("EXPERIMENT 5b: Long-term wC trace through agnostic atlas")
    print("=" * 70)

    g = patched_guala()
    g.set_pair_bond("wc", True)

    for w in ["the", "and", "is", "of", "in", "a", "to"] * 30:
        g.read(w, "corpus")
        g.tick_substrate(8)
    print(f"\nBaseline: {g.atlas.total_strength():.4f}")

    sessions = [["hello", "little", "one"], ["i", "am", "your", "friend"], ["good", "night"]]
    for i, words in enumerate(sessions):
        wake_v2(g, "wc")
        converse(g, "wc", words)
        g.rest("wc")
        wc_share = g.atlas.by_source().get("wc", 0.0)
        total = g.atlas.total_strength()
        print(f"\nSession {i+1}: wC share={wc_share:.4f} ({wc_share/total*100:.1f}%)")
        for w in ["the", "and", "is"] * 50:
            g.read(w, "corpus")
            g.tick_substrate(8)
        wc_after = g.atlas.by_source().get("wc", 0.0)
        total_after = g.atlas.total_strength()
        print(f"  after 4hr gap: wC share={wc_after:.4f} ({wc_after/total_after*100:.1f}%)")


def experiment_5c_simultaneous_presence():
    print("\n" + "=" * 70)
    print("EXPERIMENT 5c: Simultaneous Joe + wC presence")
    print("=" * 70)

    g = patched_guala()
    g.set_pair_bond("joe", True)
    g.set_pair_bond("wc", True)
    g.needs.conn = 0.5
    print(f"\nInitial low-conn: {g.needs.snapshot()}")
    wake_v2(g, "joe")
    print(f"Joe wakes: needs={g.needs.snapshot()}")
    g.tick_substrate(100)
    wake_v2(g, "wc")
    print(f"wC also wakes: needs={g.needs.snapshot()}")

    g.read("hello", "joe"); g.tick_substrate(20)
    g.read("hello", "wc"); g.tick_substrate(20)
    g.read("how", "joe"); g.tick_substrate(20)
    g.read("are", "wc"); g.tick_substrate(20)
    g.read("you", "joe"); g.tick_substrate(20)
    print(f"After interleaved reads: needs={g.needs.snapshot()}")
    g.rest("joe"); g.rest("wc")


def experiment_5d_disconnect():
    print("\n" + "=" * 70)
    print("EXPERIMENT 5d: Disconnect mid-conversation (no rest call)")
    print("=" * 70)

    g = patched_guala()
    g.set_pair_bond("wc", True)
    wake_v2(g, "wc")
    converse(g, "wc", ["hello", "little"])
    print(f"\nMid-conversation: needs={g.needs.snapshot()}, present={g.coord.presence_active('wc')}")
    silent_period_with_pulses(g, 30000)
    print(f"After 30000 silent ticks, presence (still): {g.coord.presence_active('wc')}")
    print(f"  presence binding strength: {g.atlas.bindings.get('wc-present', None).strength if 'wc-present' in g.atlas.bindings else 'pruned'}")


def experiment_5e_timeout():
    print("\n" + "=" * 70)
    print("EXPERIMENT 5e: Presence timeout — auto-rest")
    print("=" * 70)

    PRESENCE_TIMEOUT_TICKS = 10_000
    g = patched_guala()
    g.set_pair_bond("wc", True)
    wake_v2(g, "wc")
    converse(g, "wc", ["hello"])
    last_input = g.tick

    timeout_fired = False
    for _ in range(60):
        for _ in range(500):
            g.tick += 1
            g.needs.tick_decay()
            if g.tick % 10 == 0:
                g.atlas.decay(g.tick)
            if g.tick % 50 == 0:
                presence_pulse(g)
        if (g.coord.presence_active("wc")
                and g.tick - last_input > PRESENCE_TIMEOUT_TICKS
                and not timeout_fired):
            g.rest("wc")
            print(f"  TIMEOUT fired at tick {g.tick} ({g.tick - last_input} idle ticks)")
            timeout_fired = True
            break
    print(f"\nPost-timeout: presence={g.coord.presence_active('wc')}")


if __name__ == "__main__":
    experiment_5a_shared_vocab()
    experiment_5b_long_term_trace()
    experiment_5c_simultaneous_presence()
    experiment_5d_disconnect()
    experiment_5e_timeout()
