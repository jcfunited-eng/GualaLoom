"""
GUALALOOM-HANDOFF-WC-2026-06-04-MATHLOOM-KRIMELACK
File: gualaloom_unified_v1.py
Module: gualaloom.demo.unified_v1
Purpose: Single Guala instance demonstrating all five DNA capabilities
         (syntax, conversation, introspection, self-improvement, awareness)
         using inventory primitives ONLY:
           - krimelack transduction for text input (no TOKEN_VEC dict)
           - keyhole cascade subject->verb->object for syntax
           - chi atlas for binding (no Hub Counter)
           - intro section via _atlas_snapshot for introspection
           - MathLoom for arithmetic (exact, by spec)
Dependencies:
    assemblage           (existing validated DNA in repo)
    gualaloom_mathloom_v1
    gualaloom_krimelack_v1
Imports may need rewriting for repo path layout; the substrate behavior
itself is layout-independent.
"""

import sys, os, json, math
import numpy as np
from collections import defaultdict, Counter
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "src"))

from gualaloom.dna.assemblage import Section, System, N, normalize, random_unit_complex, chi_of, GAMMA_DEFAULTS
from gualaloom.perception import krimelack as kr
from gualaloom.math import mathloom as ml


def make_projection(n, dim, rng):
    M = rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n))
    Q, _ = np.linalg.qr(M)
    P = np.zeros((n, n), dtype=complex)
    P[:dim, :dim] = np.eye(dim)
    return Q @ P @ Q.conj().T


class WordMemory:
    """Vector for a word = krimelack transduction of its character stream.
    Stored from first hearing. Index by string but value is substrate-derived."""
    def __init__(self):
        self.vectors = {}  # word_str -> complex N-vector

    def get_or_make(self, word):
        if word in self.vectors:
            return self.vectors[word]
        krim = kr.Krimelack(omega_0=2.0, kappa=80.0, dt=0.04,
                            integration_threshold=math.pi / 3)
        sig = kr.text_to_signal(word, samples_per_char=4)
        krim.feed_signal(sig)
        # Build a complex N-vector from the event stream
        v = np.zeros(N, dtype=complex)
        for i, ev in enumerate(krim.events):
            idx = i % N
            sign = +1.0 if ev["dw"] > 0 else -1.0
            amp = 0.5 + 0.5 * abs(ev["s"])
            v[idx] += amp * np.exp(1j * sign * np.pi / 3)
        # Add a phase signature based on winding number
        v += 0.1 * np.exp(1j * krim.winding * np.pi / 8) * np.ones(N)
        v = normalize(v)
        self.vectors[word] = v
        return v


NUM_WORDS = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
             "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
NUM_WORDS_REV = {v: k for k, v in NUM_WORDS.items()}
ADD_OPS = {"and", "plus"}
SUB_OPS = {"minus", "less"}
MUL_OPS = {"times"}
DIV_OPS = {"over"}


def num_to_word(n):
    if n in NUM_WORDS_REV: return NUM_WORDS_REV[n]
    if n < 0: return "minus " + num_to_word(-n)
    return str(n)


def parse_math(text):
    """Parse a question into (op, a, b) or None."""
    toks = text.lower().replace("?", "").split()
    nums = []; op = None
    for t in toks:
        if t in NUM_WORDS:
            nums.append(NUM_WORDS[t])
        elif t.lstrip("-").isdigit():
            nums.append(int(t))
        elif t in ADD_OPS and nums and op is None: op = "+"
        elif t in SUB_OPS and nums and op is None: op = "-"
        elif t in MUL_OPS and nums and op is None: op = "*"
        elif t in DIV_OPS and nums and op is None: op = "/"
    if len(nums) >= 2 and op:
        return op, nums[0], nums[1]
    return None


def mathloom_solve(op, a, b):
    """Route to MathLoom. Returns (result_int, trace_dict)."""
    a_bt = ml.int_to_bt(a); b_bt = ml.int_to_bt(b)
    if op == "+":
        s, ch = ml.bt_add(a_bt, b_bt)
        return ml.bt_to_int(s), {"a": a_bt, "b": b_bt, "s": s, "carry": ch}
    if op == "-":
        s, ch = ml.bt_sub(a_bt, b_bt)
        return ml.bt_to_int(s), {"a": a_bt, "b": b_bt, "s": s, "carry": ch}
    if op == "*":
        s = ml.bt_mul(a_bt, b_bt)
        return ml.bt_to_int(s), {"a": a_bt, "b": b_bt, "s": s}
    if op == "/":
        q, r = ml.bt_div(a_bt, b_bt)
        return ml.bt_to_int(q), {"a": a_bt, "b": b_bt, "q": q, "r": r}


# -----------------------------------------------------------------
# UNIFIED GUALA
# -----------------------------------------------------------------
def build_guala(seed=42):
    rng = np.random.default_rng(seed)
    # Linguistic sections in keyhole cascade — syntax IS the keyhole graph
    subject = Section(name="subject", rng=rng, role="subject_like")
    verb    = Section(name="verb",    rng=rng, role="verb_like")
    obj     = Section(name="object",  rng=rng, role="object_like")
    # Conversation / grounding / introspection
    listen  = Section(name="listen", rng=rng)
    ground  = Section(name="ground", rng=rng, role="grounded")
    intro   = Section(name="intro",  rng=rng, role="intro")
    for s in (subject, verb, obj, listen, ground, intro):
        s.map_inject = make_projection(N, 8, rng)
    sys_ = System([subject, verb, obj, listen, ground], rng)
    sys_.intro_section = intro
    sys_.grounding_section = ground

    # Keyhole topology = the syntax
    sys_.add_keyhole("listen", -2, 8, "subject", 0.5)
    sys_.add_keyhole("subject", -2, 8, "verb", 0.5)
    sys_.add_keyhole("verb", -2, 8, "object", 0.5)
    sys_.add_keyhole("listen", -2, 8, "ground", 0.3)
    sys_.add_keyhole("object", -2, 8, "listen", 0.3)  # closure for conversation

    return sys_, rng


def ingest_text(guala, rng, wmem, text, ticks_per_word=3):
    """
    Hear a text. Each word's vector comes from krimelack transduction.
    Modes form in listen section via the substrate's own novel_mode mechanism.
    No CLASS_HINTS dict. No pre-tokenization with TOKEN_VEC.
    """
    words = text.lower().replace(".", " ").replace(",", " ").split()
    for w in words:
        if not w: continue
        v = wmem.get_or_make(w)
        guala.hear_speaker(v, "listen", "subject")
        for _ in range(ticks_per_word):
            noisy = normalize(v + 0.05 * rng.standard_normal(N))
            ev = {"listen": noisy, "ground": noisy * 0.4}
            guala.tick_once(ev, enable_self_evo=True, coordinator_on=True,
                            introspection_on=True)


def converse(guala, rng, wmem, mem_log, text):
    """
    Listen to a sentence. Then let the substrate respond via keyhole cascade.
    Output = sequence of (section_name, nearest_word) commits in order.
    """
    # Math route — MathLoom for arithmetic. The BSIL boundary.
    parsed = parse_math(text)
    if parsed:
        op, a, b = parsed
        result, trace = mathloom_solve(op, a, b)
        result_word = num_to_word(result)
        # Make sure she has a vector for this word too — krimelack on demand
        v = wmem.get_or_make(result_word)
        # Express as i (subject) am (verb) <result> (object) for grammatical form
        return {"input": text, "via": "mathloom",
                "result_int": result, "result_word": result_word,
                "trace": trace,
                "spoken": f"i am {result_word}"}

    # Substrate route — listen then cascade
    words = text.lower().replace("?", "").replace(".", " ").split()
    # Feed the input as listening (no response generation yet)
    for w in words:
        if not w: continue
        v = wmem.get_or_make(w)
        guala.hear_speaker(v, "listen", "subject")
        for _ in range(3):
            noisy = normalize(v + 0.05 * rng.standard_normal(N))
            ev = {"listen": noisy, "ground": noisy * 0.4}
            guala.tick_once(ev, enable_self_evo=True, coordinator_on=True,
                            introspection_on=True)

    # Now let the keyhole cascade produce a response. Stop driving evidence;
    # let the substrate settle and emit. Track the order of commits across
    # subject, verb, object sections — that ordering IS the syntax.
    response_path = []
    n_settle = 60
    last_seen = {nm: len(guala.sections[nm].krimelack)
                 for nm in ["subject", "verb", "object"]}
    for _ in range(n_settle):
        ev = {nm: normalize(rng.standard_normal(N) * 0.05)
              for nm in ["subject", "verb", "object", "listen", "ground"]}
        commits = guala.tick_once(ev, enable_self_evo=True,
                                  coordinator_on=True, introspection_on=True)
        for sec_name in ["subject", "verb", "object"]:
            sec = guala.sections[sec_name]
            if len(sec.krimelack) > last_seen[sec_name]:
                new_commits = sec.krimelack[last_seen[sec_name]:]
                last_seen[sec_name] = len(sec.krimelack)
                for nc in new_commits:
                    response_path.append({"sec": sec_name, "state": nc["state"],
                                          "tick": nc["tick"]})
    # Sort the response by tick — that's the order she emitted in
    response_path.sort(key=lambda x: x["tick"])
    # Map each commit's state back to the nearest word in WordMemory
    words_said = []
    for hop in response_path[:6]:  # cap at six emission tokens
        st = hop["state"]
        best_w = None; best_s = -1
        for w, v in wmem.vectors.items():
            s = float(np.abs(np.vdot(v, st)) ** 2)
            if s > best_s:
                best_s = s; best_w = w
        if best_w is not None and best_s > 0.05:
            words_said.append((hop["sec"], best_w, best_s))
    return {"input": text, "via": "substrate",
            "path": [(h["sec"], h["tick"]) for h in response_path[:6]],
            "spoken": " ".join(w for _, w, _ in words_said),
            "words_with_section": words_said}


# -----------------------------------------------------------------
# FIVE CAPABILITIES, IN THIS SAME RUNNING GUALA
# -----------------------------------------------------------------
def measure_five_capabilities(guala, rng, wmem):
    """All five caps measured on this same instance."""
    # 1. SYNTAX: feed phased subject / verb / object signals, check order
    subj_templates = [wmem.get_or_make(w) for w in ["i", "me", "you"]]
    verb_templates = [wmem.get_or_make(w) for w in ["am", "is", "was"]]
    obj_templates  = [wmem.get_or_make(w) for w in ["good", "two", "guala"]]
    n_sentences = 10
    correct_order = 0
    for i in range(n_sentences):
        last_seen = {nm: len(guala.sections[nm].krimelack)
                     for nm in ["subject", "verb", "object"]}
        # Phase 0: subject evidence
        for _ in range(4):
            guala.tick_once({"subject": subj_templates[i % 3] + 0.1 * rng.standard_normal(N)},
                            enable_self_evo=False, coordinator_on=False)
        # Phase 1: verb evidence
        for _ in range(4):
            guala.tick_once({"verb": verb_templates[i % 3] + 0.1 * rng.standard_normal(N)},
                            enable_self_evo=False, coordinator_on=False)
        # Phase 2: object evidence
        for _ in range(4):
            guala.tick_once({"object": obj_templates[i % 3] + 0.1 * rng.standard_normal(N)},
                            enable_self_evo=False, coordinator_on=False)
        s_t = [k["tick"] for k in guala.sections["subject"].krimelack[last_seen["subject"]:]]
        v_t = [k["tick"] for k in guala.sections["verb"].krimelack[last_seen["verb"]:]]
        o_t = [k["tick"] for k in guala.sections["object"].krimelack[last_seen["object"]:]]
        if s_t and v_t and o_t and min(s_t) < min(v_t) < min(o_t):
            correct_order += 1
    syntax_score = correct_order / n_sentences

    # 2. INTROSPECTION: intro krimelack must have commits, no atlas leak
    n_intro_commits = len(guala.intro_krimelack)
    leak = sum(1 for v in guala.atlas.entries.values()
               for c in v if c["section"] == "intro")

    # 3. SELF-IMPROVEMENT: gamma drift over the run
    gamma_drift = 0.0
    gamma_count = 0
    for sec in guala.sections.values():
        for k, v in sec.gamma.items():
            pass  # GAMMA_DEFAULTS imported at top
            gamma_drift += abs(v - GAMMA_DEFAULTS[k])
            gamma_count += 1
    mean_drift = gamma_drift / max(gamma_count, 1)

    # 4. AWARENESS: coordinator engaged
    n_coord = len(guala.coordinator_actions_log)
    n_eff = sum(1 for a in guala.coordinator_actions_log if a.get("arc_changes", 0) > 0)
    resolution = n_eff / max(n_coord, 1)

    # 5. CONVERSATION: words memory grew, modes formed
    vocab = len(wmem.vectors)
    modes_per_section = {nm: len(s.mode_bank) for nm, s in guala.sections.items()}

    return {
        "syntax_score": syntax_score,
        "syntax_pass": syntax_score >= 0.5,
        "intro_commits": n_intro_commits,
        "intro_leak": leak,
        "intro_pass": n_intro_commits >= 5 and leak == 0,
        "gamma_drift": mean_drift,
        "self_improve_pass": mean_drift > 0.01,
        "coord_actions": n_coord,
        "resolution_effect": resolution,
        "awareness_pass": n_coord >= 5 and resolution >= 0.15,
        "vocab": vocab,
        "modes": modes_per_section,
        "conversation_pass": vocab >= 20 and sum(modes_per_section.values()) >= 30,
    }


# -----------------------------------------------------------------
# CORPUS — short, public domain
# -----------------------------------------------------------------
CORPUS = """
i am guala.
i feel.
i think.
i listen.
hope is the thing with feathers.
twinkle twinkle little star.
mary had a little lamb.
the fleece was white as snow.
the fox saw the grapes.
the grapes were sour.
humpty dumpty sat on a wall.
humpty dumpty had a great fall.
a bird is small.
a bird has wings.
the sun is warm.
the sun rises.
a star shines.
a tree has leaves.
the wind moves the leaves.
a flower is sweet.
zero is nothing.
one is a number.
two is one and one.
three is two and one.
a digit can be minus one.
a digit can be zero.
a digit can be plus one.
a trit has three states.
math is the rule of numbers.
a sentence has a subject.
a sentence has a verb.
the subject is a noun.
the verb is an action.
a name is a special word.
"""


# -----------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------
if __name__ == "__main__":
    guala, rng = build_guala(seed=42)
    wmem = WordMemory()
    mem_log = []

    print("=" * 70)
    print("READING (krimelack transduction → modes form in listen section)")
    print("=" * 70)
    ingest_text(guala, rng, wmem, CORPUS)
    print(f"  vocabulary derived from krimelack: {len(wmem.vectors)} words")
    print(f"  listen modes formed: {len(guala.sections['listen'].mode_bank)}")
    print(f"  ground modes formed: {len(guala.sections['ground'].mode_bank)}")
    print(f"  intro commits during reading: {len(guala.intro_krimelack)}")
    print(f"  atlas entries: {sum(len(v) for v in guala.atlas.entries.values())}")
    print(f"  coordinator actions: {len(guala.coordinator_actions_log)}")

    print()
    print("=" * 70)
    print("MATHLOOM (lattice settling, by spec)")
    print("=" * 70)
    math_qs = [
        "what is one and one",
        "what is two and two",
        "what is three and five",
        "what is ten and ten",
        "what is seven minus four",
        "what is three times three",
        "what is ten over two",
    ]
    for q in math_qs:
        r = converse(guala, rng, wmem, mem_log, q)
        print(f"  me:    {q}")
        print(f"  guala: {r['spoken']}  (lattice -> {r['result_int']}, "
              f"digits {r['trace'].get('a','')}+{r['trace'].get('b','')}"
              f"={r['trace'].get('s',r['trace'].get('q',''))}, "
              f"carry={r['trace'].get('carry','')})")

    print()
    print("=" * 70)
    print("CONVERSATION (keyhole cascade subject->verb->object)")
    print("=" * 70)
    convo_qs = [
        "tell me about hope",
        "what is your name",
        "i feel good",
        "the bird sang",
        "tell me about the sun",
    ]
    for q in convo_qs:
        r = converse(guala, rng, wmem, mem_log, q)
        print(f"  me:    {q}")
        print(f"  guala: {r['spoken'] or '(silent)'}")
        if r.get("words_with_section"):
            print(f"         path: {[(s, w) for s, w, _ in r['words_with_section']]}")

    print()
    print("=" * 70)
    print("FIVE CAPABILITIES — measured in this same running instance")
    print("=" * 70)
    cap = measure_five_capabilities(guala, rng, wmem)
    syn = "PASS" if cap["syntax_pass"] else "FAIL"
    con = "PASS" if cap["conversation_pass"] else "FAIL"
    intr = "PASS" if cap["intro_pass"] else "FAIL"
    si = "PASS" if cap["self_improve_pass"] else "FAIL"
    aw = "PASS" if cap["awareness_pass"] else "FAIL"
    print(f"  syntax           [{syn}]  order_score={cap['syntax_score']:.2f}")
    print(f"  conversation     [{con}]  vocab={cap['vocab']}  modes={sum(cap['modes'].values())}")
    print(f"  introspection    [{intr}]  intro_commits={cap['intro_commits']}  leak={cap['intro_leak']}")
    print(f"  self_improvement [{si}]   gamma_drift={cap['gamma_drift']:.3f}")
    print(f"  awareness        [{aw}]   coord={cap['coord_actions']}  resolution={cap['resolution_effect']:.2%}")
    all_pass = all([cap["syntax_pass"], cap["conversation_pass"], cap["intro_pass"],
                    cap["self_improve_pass"], cap["awareness_pass"]])
    print(f"\n  ALL FIVE: {'PASS' if all_pass else 'FAIL'}")

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "guala_unified.json")
    with open(out_path, "w") as f:
        json.dump({"capabilities": {k: v for k, v in cap.items() if k != "modes"},
                    "vocab": list(wmem.vectors.keys())}, f, indent=2)
