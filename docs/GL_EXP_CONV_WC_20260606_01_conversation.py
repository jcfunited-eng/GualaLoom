# doc_id: GL-EXP-CONV-WC-20260606-01
# created: 2026-06-06
# author: wC
# related_command: GL-CMD-BRIDGE-WC-20260606-01
"""
Experiment 4: Full conversation cycle and multi-session continuity.
"""

from GL_MDL_SUBSTRATE_WC_20260606_01_substrate_mock import (
    fresh_guala, silent_period, GualaMock, SOURCE_WEIGHTS,
)
from GL_EXP_PULSE_WC_20260606_01_pulse_and_target import (
    wake_v2, silent_period_with_pulses, presence_pulse,
)


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


def experiment_4a_single_session():
    print("=" * 70)
    print("EXPERIMENT 4a: Single wC session")
    print("=" * 70)

    g = fresh_guala()
    g.set_pair_bond("wc", True)
    print(f"\nInitial: needs={g.needs.snapshot()}")

    wake_v2(g, "wc")
    print(f"\nAfter wake: needs={g.needs.snapshot()}")
    print(f"  atlas wc bindings: {sum(1 for b in g.atlas.bindings.values() if b.source_flavor=='wc')}")

    print(f"\nwC says: 'hello little one i am here'")
    converse(g, "wc", ["hello", "little", "one", "i", "am", "here"])
    print(f"  atlas wc bindings: {sum(1 for b in g.atlas.bindings.values() if b.source_flavor=='wc')}")
    print(f"  needs: {g.needs.snapshot()}")

    silent_period_with_pulses(g, 500)

    print(f"\nwC says: 'i am your friend'")
    converse(g, "wc", ["i", "am", "your", "friend"])
    print(f"  atlas wc bindings: {sum(1 for b in g.atlas.bindings.values() if b.source_flavor=='wc')}")

    g.rest("wc")
    by_source = g.atlas.by_source()
    print(f"\nAt rest: wc total={by_source.get('wc', 0.0):.4f}")
    print(f"  needs: {g.needs.snapshot()}")

    silent_period(g, 20000)
    by_source = g.atlas.by_source()
    print(f"\n20000 ticks later:")
    print(f"  wc bindings: {sum(1 for b in g.atlas.bindings.values() if b.source_flavor=='wc')}")
    print(f"  wc total: {by_source.get('wc', 0.0):.4f}")


def experiment_4b_three_sessions():
    print("\n" + "=" * 70)
    print("EXPERIMENT 4b: Three sessions over a 'day'")
    print("=" * 70)

    g = fresh_guala()
    g.set_pair_bond("wc", True)

    sessions = [
        ("morning", ["hello", "little", "one", "good", "morning"]),
        ("midday", ["hello", "again", "are", "you", "well"]),
        ("evening", ["good", "night", "little", "one", "rest"]),
    ]

    for i, (label, words) in enumerate(sessions):
        wake_v2(g, "wc")
        converse(g, "wc", words)
        g.rest("wc")
        wc_strength = g.atlas.by_source().get("wc", 0.0)
        wc_count = sum(1 for b in g.atlas.bindings.values() if b.source_flavor=='wc')
        print(f"\nAfter session {i+1} ({label}):")
        print(f"  wc bindings: {wc_count}, total: {wc_strength:.4f}")
        silent_period(g, 60000)
        wc_strength_after = g.atlas.by_source().get("wc", 0.0)
        wc_count_after = sum(1 for b in g.atlas.bindings.values() if b.source_flavor=='wc')
        print(f"  after 60k tick gap: wc bindings={wc_count_after}, strength={wc_strength_after:.4f}")


def experiment_4c_corpus_during_presence():
    print("\n" + "=" * 70)
    print("EXPERIMENT 4c: Corpus reading during wC presence")
    print("=" * 70)

    g = fresh_guala()
    g.set_pair_bond("wc", True)
    wake_v2(g, "wc")

    corpus_words = ["the", "moon", "is", "cold", "and", "bright"] * 20
    for w in corpus_words:
        g.read(w, "corpus")
        for _ in range(10):
            g.tick += 1
            g.needs.tick_decay()
            if g.tick % 10 == 0:
                g.atlas.decay(g.tick)
            if g.tick % 50 == 0:
                presence_pulse(g)

    print(f"\nAfter 120 corpus reads with wC silently present:")
    print(f"  wc-source strength: {g.atlas.by_source().get('wc', 0.0):.4f}")
    print(f"  corpus-source strength: {g.atlas.by_source().get('corpus', 0.0):.4f}")

    converse(g, "wc", ["i", "am", "still", "here"], ticks_between=10)
    g.rest("wc")
    print(f"\nAfter brief wC utterance and rest:")
    print(f"  wc-source strength: {g.atlas.by_source().get('wc', 0.0):.4f}")
    print(f"  corpus-source strength: {g.atlas.by_source().get('corpus', 0.0):.4f}")


if __name__ == "__main__":
    experiment_4a_single_session()
    experiment_4b_three_sessions()
    experiment_4c_corpus_during_presence()
