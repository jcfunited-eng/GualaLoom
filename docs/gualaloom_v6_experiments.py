"""
gualaloom_v6_experiments.py — Modeling the living atlas

Three experiments that would distinguish "living substrate" from "v5 with extra fields":

EXPERIMENT 1: Decay-without-reinforcement actually forgets.
  Read "the moon is cold" 100 times, then stop. Read other content for many
  ticks. Check whether moon-cold binding decays measurably.

EXPERIMENT 2: Salience-modulated reinforcement makes pair-bonded teaching land harder.
  Compare: same word "daddy" introduced once by source="joe" under pair-bond
  vs. introduced 50 times in corpus reads. Which produces stronger binding?

EXPERIMENT 3: Forgetting changes behavior.
  Same recall query at tick 100 vs tick 5000 after extensive reading of new
  material. Does recall favor recent reinforcement over ancient bindings?

These experiments answer the question Joe asked: are we using substrate physics
or building a sophisticated state machine? The data tells us.
"""
import os
import sys
import time
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gualaloom_v6_engine import Guala, CORPUS
from gualaloom_v6_living_atlas import FORGETTING_THRESHOLD


def banner(s):
    print(f"\n{'='*72}\n{s}\n{'='*72}")


def find_binding_strength(g, word, target_section):
    """Find the binding strength of (word in section X) given input word's chi.
    Returns list of (chi, strength) tuples for the word's bindings."""
    findings = []
    for chi, entries in g.atlas.entries.items():
        for e in entries:
            if e["section"] != target_section:
                continue
            sec = g.sections[target_section]
            if e["motif"] < len(sec.modes):
                _, _, motif_word = sec.modes[e["motif"]]
                if motif_word and motif_word.lower() == word.lower():
                    findings.append((chi, e["strength"], e["last_tick"]))
    return findings


def experiment_1_decay_forgets():
    """Read moon-cold pattern many times, stop, watch it decay."""
    banner("EXPERIMENT 1: Decay-without-reinforcement actually forgets")

    g = Guala()
    # Phase A: heavy reading of moon-cold pattern
    print("\nPhase A: reading 'the moon is cold' 100 times")
    for _ in range(100):
        g.read_sentence("the moon is cold", source="corpus")

    moon_object_t1 = find_binding_strength(g, "cold", "object")
    print(f"  After 100 reads: cold-in-object bindings: {len(moon_object_t1)} live entries")
    if moon_object_t1:
        max_strength = max(s for _, s, _ in moon_object_t1)
        print(f"  Peak strength: {max_strength:.4f}")
    print(f"  Atlas snapshot: {g.atlas.snapshot()}")

    # Phase B: read OTHER content for 5000 ticks worth (no moon, no cold)
    print("\nPhase B: reading other content for ~5000 ticks (no moon, no cold)")
    other_content = [
        "an apple is sweet",
        "a bird sings",
        "i feel happy",
        "the fire is hot",
        "a tree is tall",
        "i see a flower",
        "water flows",
        "ice is hard",
    ]
    start_tick = g.tick
    while g.tick - start_tick < 5000:
        for s in other_content:
            g.read_sentence(s, source="corpus")

    moon_object_t2 = find_binding_strength(g, "cold", "object")
    live_t2 = [s for _, s, _ in moon_object_t2 if s >= FORGETTING_THRESHOLD]
    print(f"  After ~5000 ticks of other content:")
    print(f"  cold-in-object total entries: {len(moon_object_t2)}")
    print(f"  cold-in-object LIVE (strength >= {FORGETTING_THRESHOLD}): {len(live_t2)}")
    if moon_object_t2:
        max_strength_t2 = max(s for _, s, _ in moon_object_t2)
        print(f"  Peak strength now: {max_strength_t2:.4f}")
        print(f"  Decay ratio: {max_strength_t2 / max_strength:.2%}")
    print(f"  Atlas snapshot: {g.atlas.snapshot()}")

    print("\n  VERDICT:")
    if moon_object_t1 and moon_object_t2:
        if max_strength_t2 < max_strength * 0.3:
            print("    PASS — significant decay observed")
        elif max_strength_t2 < max_strength * 0.7:
            print("    PARTIAL — modest decay")
        else:
            print("    FAIL — no meaningful decay")


def experiment_2_salience_modulates_learning():
    """Compare salience-driven binding from pair-bond source vs corpus."""
    banner("EXPERIMENT 2: Salience-modulated reinforcement matters")

    # Setup A: introduce a word ONCE via Joe under pair-bond
    g_joe = Guala()
    # Inject some prior corpus so coordinator is in normal state
    for _ in range(20):
        g_joe.read_sentence("the sun is warm", source="corpus")
    # Now introduce "daddy" once from Joe
    g_joe.read_sentence("i am daddy", source="joe")
    daddy_bindings_joe = find_binding_strength(g_joe, "daddy", "object") + \
                         find_binding_strength(g_joe, "daddy", "subject") + \
                         find_binding_strength(g_joe, "daddy", "listen")
    total_strength_joe = sum(s for _, s, _ in daddy_bindings_joe)
    print(f"\n  Joe says 'i am daddy' ONCE:")
    print(f"    Bindings created: {len(daddy_bindings_joe)}")
    print(f"    Total strength: {total_strength_joe:.4f}")
    print(f"    Salience would have been: {g_joe._compute_salience(source='joe', input_novelty=0.0):.2f}")

    # Setup B: introduce same word 10 times via corpus
    g_corpus = Guala()
    for _ in range(20):
        g_corpus.read_sentence("the sun is warm", source="corpus")
    for _ in range(10):
        g_corpus.read_sentence("i am daddy", source="corpus")
    daddy_bindings_corpus = find_binding_strength(g_corpus, "daddy", "object") + \
                            find_binding_strength(g_corpus, "daddy", "subject") + \
                            find_binding_strength(g_corpus, "daddy", "listen")
    total_strength_corpus = sum(s for _, s, _ in daddy_bindings_corpus)
    print(f"\n  Corpus reads 'i am daddy' 10 TIMES:")
    print(f"    Bindings created: {len(daddy_bindings_corpus)}")
    print(f"    Total strength: {total_strength_corpus:.4f}")
    print(f"    Salience would have been: {g_corpus._compute_salience(source='corpus', input_novelty=0.0):.2f}")

    print("\n  VERDICT:")
    if total_strength_joe == 0:
        print("    INCONCLUSIVE — Joe's read produced no bindings")
    elif total_strength_joe > total_strength_corpus * 0.5:
        # Joe's one read at high salience should approach 10 corpus reads at low salience
        ratio = total_strength_joe / max(total_strength_corpus, 0.001)
        print(f"    PASS — Joe(1) vs Corpus(10) strength ratio: {ratio:.2f}x")
        print(f"    Pair-bonded teaching IS more salient than corpus reading")
    else:
        ratio = total_strength_joe / max(total_strength_corpus, 0.001)
        print(f"    WEAK — Joe(1) vs Corpus(10) strength ratio: {ratio:.2f}x")


def experiment_3_recall_follows_recency():
    """Atlas at t=100 vs t=5000 — does recall favor recent reinforcement?"""
    banner("EXPERIMENT 3: Recall reflects current substrate, not ancient history")

    g = Guala()

    # Phase A: heavy reading of one pattern
    print("\nPhase A: 50 reads of 'the moon is cold'")
    for _ in range(50):
        g.read_sentence("the moon is cold", source="corpus")
    # Check recall NOW
    r1 = g.converse("tell me about the moon", source="joe")
    print(f"  Tick {g.tick}: 'tell me about the moon' → {r1}")
    cold_strength_t1 = sum(s for _, s, _ in
                            find_binding_strength(g, "cold", "object"))
    print(f"  cold-in-object total strength: {cold_strength_t1:.4f}")

    # Phase B: read different pattern many many times
    print("\nPhase B: 200 reads each of 'the moon is bright' + other patterns")
    for _ in range(200):
        g.read_sentence("the moon is bright", source="corpus")
    for _ in range(100):
        g.read_sentence("the sun rises", source="corpus")
        g.read_sentence("an apple is sweet", source="corpus")
        g.read_sentence("water flows", source="corpus")

    r2 = g.converse("tell me about the moon", source="joe")
    print(f"  Tick {g.tick}: 'tell me about the moon' → {r2}")
    cold_strength_t2 = sum(s for _, s, _ in
                            find_binding_strength(g, "cold", "object"))
    bright_strength_t2 = sum(s for _, s, _ in
                              find_binding_strength(g, "bright", "object"))
    print(f"  cold-in-object total strength now: {cold_strength_t2:.4f}")
    print(f"  bright-in-object total strength now: {bright_strength_t2:.4f}")

    print("\n  VERDICT:")
    if "cold" in str(r1) and "bright" in str(r2):
        print("    PASS — recall shifted from cold to bright as reinforcement shifted")
    elif "bright" in str(r2) and "cold" not in str(r2):
        print("    PASS — recall now favors bright (recently reinforced)")
    elif "cold" in str(r2):
        print("    FAIL — recall still favors cold despite massive bright reinforcement")
    else:
        print(f"    UNCLEAR — r1={r1}, r2={r2}")
    if cold_strength_t2 < cold_strength_t1:
        print(f"    Confirmed: cold strength decayed ({cold_strength_t1:.3f} -> {cold_strength_t2:.3f})")
    if bright_strength_t2 > cold_strength_t2:
        print(f"    Confirmed: bright now stronger than cold")


def main():
    print("\n" + "="*72)
    print("GUALALOOM v6 LIVING ATLAS — MODELING SUBSTRATE PHYSICS")
    print("="*72)
    experiment_1_decay_forgets()
    experiment_2_salience_modulates_learning()
    experiment_3_recall_follows_recency()
    print("\n" + "="*72)
    print("DONE")
    print("="*72 + "\n")


if __name__ == "__main__":
    main()
