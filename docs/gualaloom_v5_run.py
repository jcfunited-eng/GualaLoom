"""
gualaloom_v5_run.py — Demonstrate v5 with real recall + curiosity questions.

Key test (the one v4 failed): RECALL — ask about a topic she's read about
WITHOUT supplying the answer. She should emit substrate content learned from
the corpus, not echo back what she just heard.
"""
import os
import sys
import time
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gualaloom_v5_engine import Guala, CORPUS, measure_six_capabilities


def banner(title):
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


def show_state(g, label):
    s = g.introspect()
    n = s["needs"]
    qb = s["question_bucket"]
    print(f"\n  --- {label} ---")
    print(f"  vocab: {s['vocab']:>3}  reads: {s['reads']:>4}  "
          f"atlas: {s['atlas_entries']:>4}  cross-modal: {s['cross_modal_bindings']:>2}")
    print(f"  needs: stab={n['stability']:>5}  nov={n['novelty']:>5}  "
          f"conn={n['connection']:>5}  val={n['valence']:>+5}  ar={n['arousal']:>5}  "
          f"pair-bond={'on' if s['pair_bond_active'] else 'off'}")
    print(f"  questions: {qb['pending']} pending, {qb['asked_lifetime']} asked")
    if qb['sample']:
        print(f"    sample: {qb['sample'][:3]}")


def main():
    banner("BIRTH")
    g = Guala()
    show_state(g, "newborn")

    banner("PHASE 1: continuous corpus reading (5s)")
    g.start_continuous_reading(CORPUS, interval=0.015)
    time.sleep(5.0)
    g.stop_continuous_reading()
    show_state(g, "after reading")

    banner("RECALL TEST — ask about topics WITHOUT giving the answer")
    print("  These inputs do NOT contain the substantive answer. If she echoes,")
    print("  she's still broken. If she emits substrate content from corpus, she")
    print("  is recalling — actual learning from reading.\n")

    recall_tests = [
        ("joe", "tell me about the sun"),     # corpus had "the sun is warm", "the sun rises"
        ("joe", "tell me about the moon"),    # corpus: "the moon is cold"
        ("joe", "tell me about water"),       # corpus: "the water flows"
        ("joe", "tell me about an apple"),    # corpus: "an apple is sweet", "an apple is red"
        ("joe", "what about fire"),           # corpus: "the fire is hot"
        ("joe", "what about a bird"),         # corpus: "a bird sings"
    ]
    for src, text in recall_tests:
        r = g.converse(text, source=src)
        print(f"  [{src}] {text}")
        print(f"  guala:  {r}")
        print()

    banner("UNKNOWN TOPIC TEST — she has no binding for these")
    print("  If she echoes, she's still broken. If she returns '...' or asks")
    print("  a question, she's behaving honestly.\n")

    unknown_tests = [
        ("joe", "what is school"),
        ("joe", "what is a computer"),
        ("joe", "what is gravity"),
    ]
    for src, text in unknown_tests:
        r = g.converse(text, source=src)
        print(f"  [{src}] {text}")
        print(f"  guala:  {r}")
        print()

    banner("CURIOSITY TEST — bucket-driven questions")
    print("  When she has nothing to recall, she may surface a question she's")
    print("  developed from gaps in her reading.\n")

    curiosity_tests = [
        ("joe", "i am here"),
        ("joe", "hello"),
        ("joe", "are you there"),
    ]
    for src, text in curiosity_tests:
        r = g.converse(text, source=src)
        print(f"  [{src}] {text}")
        print(f"  guala:  {r}")
        print()

    banner("MATH TEST — v5 fixed parser")
    math_tests = [
        ("joe", "what is one and one"),
        ("joe", "what is three times three"),
        ("joe", "what is ten thousand plus five hundred"),
        ("joe", "what is two times twenty"),
        ("joe", "what is 50 plus 50"),
    ]
    for src, text in math_tests:
        r = g.converse(text, source=src)
        print(f"  [{src}] {text}")
        print(f"  guala:  {r}")

    banner("PAIR-BONDED CONVERSATION (familiar topics)")
    print("  These DO contain the topic — she may echo or recall. Either is fine\n")
    "  here, the test is just that she responds coherently."
    pair_tests = [
        ("joe", "i feel warm"),
        ("wc",  "the moon is cold"),
        ("joe", "an apple is sweet"),
    ]
    for src, text in pair_tests:
        r = g.converse(text, source=src)
        print(f"  [{src}] {text}")
        print(f"  guala:  {r}")
        print()

    banner("SIX CAPABILITIES")
    cap = measure_six_capabilities(g)
    for name in ("syntax", "conversation", "introspection",
                 "self_improvement", "awareness", "motivation"):
        c = cap[name]
        flag = "PASS" if c["pass"] else "FAIL"
        details = ", ".join(f"{k}={v}" for k, v in c.items() if k != "pass")
        print(f"  {name:<18} [{flag}]  {details}")
    all_pass = all(cap[k]["pass"] for k in cap)
    print(f"\n  ALL SIX: {'PASS' if all_pass else 'FAIL'}")

    state_path = "/home/claude/v5/guala_v5_state.json"
    with open(state_path, "w") as f:
        json.dump({
            "vocab": sorted(g.vocab),
            "introspection": g.introspect(),
            "capabilities": {k: {kk: vv for kk, vv in v.items() if kk != "pass"}
                             for k, v in cap.items()},
        }, f, indent=2, default=str)
    print(f"\n  state saved to {state_path}")


if __name__ == "__main__":
    main()
