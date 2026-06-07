"""
GUALA v5: INTROSPECTION DURING DIALOG

Watch what Guala "knows about herself" while she's having the conversation.

Her intro section receives an atlas snapshot. When it commits, that commit
represents her current self-model - what she "thinks she's doing right now."

During each turn:
1. User says something
2. Guala processes it (substrate dynamics)
3. Her intro section commits (her self-model updates)
4. She emits her response
5. Her intro section commits again (her self-model of the response)

We read the intro commits and decode them. What does she experience while talking?
"""

import numpy as np
import sys
from collections import defaultdict, Counter, deque
sys.path.insert(0, "/home/claude/grow")
from assemblage import Section, System, N, normalize, random_unit_complex, chi_of

SEED = 42
rng = np.random.default_rng(SEED)


def make_projection(n, dim, rng):
    M = rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n))
    Q, _ = np.linalg.qr(M)
    P = np.zeros((n, n), dtype=complex)
    P[:dim, :dim] = np.eye(dim)
    return Q @ P @ Q.conj().T


VOCAB_CLASSES = {
    "greeting":     ["hello", "hi", "hey"],
    "question":     ["what", "how", "who", "where"],
    "pronoun_self": ["i", "me", "my"],
    "pronoun_you":  ["you", "your"],
    "copula":       ["am", "are", "is"],
    "positive":     ["yes", "ok", "fine", "good", "well"],
    "negative":     ["no", "sorry"],
    "polite":       ["thanks", "please"],
    "verb_comm":    ["tell", "say", "ask"],
    "verb_cog":     ["think", "know", "want"],
    "noun_self":    ["name"],
    "name":         ["guala", "joe"],
}

VOCAB = []
TOKEN_VEC = {}
CLASS_VEC = {}
ROLE_VEC = {}
TOKEN_CLASS = {}

vocab_rng = np.random.default_rng(SEED + 12345)
for cls, toks in VOCAB_CLASSES.items():
    base = random_unit_complex(N, vocab_rng)
    CLASS_VEC[cls] = base.copy()
    for tok in toks:
        offset = vocab_rng.standard_normal(N) * 0.10 + 1j * vocab_rng.standard_normal(N) * 0.10
        TOKEN_VEC[tok] = normalize(base + offset)
        TOKEN_CLASS[tok] = cls
        VOCAB.append(tok)

ROLES = ["GREETING", "ACK", "SUBJECT", "COPULA", "PREDICATE", "QUESTION", "ANSWER", "NAME"]
for r in ROLES:
    ROLE_VEC[r] = random_unit_complex(N, vocab_rng)

RESPONSE_TEMPLATES = {
    "greeting":     [("greeting", "GREETING")],
    "question":     [("pronoun_self", "SUBJECT"), ("copula", "COPULA"), ("positive", "PREDICATE")],
    "positive":     [("positive", "ACK")],
    "negative":     [("polite", "ACK")],
    "polite":       [("pronoun_you", "SUBJECT"), ("copula", "COPULA"), ("positive", "PREDICATE")],
    "pronoun_self": [("pronoun_you", "SUBJECT"), ("copula", "COPULA"), ("positive", "PREDICATE")],
    "pronoun_you":  [("pronoun_self", "SUBJECT"), ("copula", "COPULA"), ("positive", "PREDICATE")],
    "verb_comm":    [("positive", "ACK")],
    "verb_cog":     [("pronoun_self", "SUBJECT"), ("copula", "COPULA"), ("verb_cog", "PREDICATE")],
    "copula":       [("pronoun_self", "SUBJECT"), ("copula", "COPULA"), ("positive", "PREDICATE")],
    "name":         [("pronoun_self", "SUBJECT"), ("copula", "COPULA"), ("name", "NAME")],
    "noun_self":    [("pronoun_self", "SUBJECT"), ("copula", "COPULA"), ("name", "NAME")],
}


def question_about_name(tokens):
    has_q = any(t in VOCAB_CLASSES["question"] for t in tokens)
    has_name_word = "name" in tokens
    return has_q and has_name_word


def build_guala():
    token_sec = Section(name="token", rng=rng)
    class_sec = Section(name="class", rng=rng)
    role_sec  = Section(name="role",  rng=rng)
    listen    = Section(name="listen", rng=rng)
    partner   = Section(name="partner", rng=rng, role="intro")
    ground    = Section(name="ground", rng=rng, role="grounded")
    memory    = Section(name="memory", rng=rng, role="intro")

    for s in (token_sec, class_sec, role_sec, listen, partner, ground, memory):
        s.map_inject = make_projection(N, 8, rng)

    FUTURE = 10000
    for tok in VOCAB:
        token_sec.mode_bank.append(TOKEN_VEC[tok].copy())
        token_sec.mode_last_used.append(FUTURE)
    for cls in VOCAB_CLASSES:
        class_sec.mode_bank.append(CLASS_VEC[cls].copy())
        class_sec.mode_last_used.append(FUTURE)
    for r in ROLES:
        role_sec.mode_bank.append(ROLE_VEC[r].copy())
        role_sec.mode_last_used.append(FUTURE)
    for tok in VOCAB:
        listen.mode_bank.append(TOKEN_VEC[tok].copy())
        listen.mode_last_used.append(FUTURE)
        partner.mode_bank.append(TOKEN_VEC[tok].copy())
        partner.mode_last_used.append(FUTURE)

    sys_ = System([token_sec, class_sec, role_sec, listen, partner, ground, memory], rng)

    # INTRO SECTION - this is Guala's self-model. Separate krimelack.
    intro = Section(name="intro", rng=rng, role="intro")
    intro.map_inject = make_projection(N, 8, rng)
    # Intro mode bank: one mode per CLASS - she models herself in terms of "what kind of thought am I having"
    for cls in VOCAB_CLASSES:
        intro.mode_bank.append(CLASS_VEC[cls].copy())
        intro.mode_last_used.append(FUTURE)
    sys_.intro_section = intro

    sys_.add_keyhole("listen", -2, 8, "token", 0.4)
    sys_.add_keyhole("listen", -2, 8, "class", 0.4)
    sys_.add_keyhole("listen", -2, 8, "role",  0.4)
    sys_.add_keyhole("partner", -2, 8, "token", 0.3)
    sys_.add_keyhole("partner", -2, 8, "class", 0.3)
    sys_.add_keyhole("role", -2, 8, "class", 0.3)
    sys_.add_keyhole("class", -2, 8, "token", 0.4)
    sys_.add_keyhole("listen", -2, 8, "partner", 0.4)
    sys_.add_keyhole("memory", -2, 8, "class", 0.3)
    sys_.add_keyhole("memory", -2, 8, "token", 0.3)

    return sys_


def emit_token_constrained(sys_, target_class=None):
    token_sec = sys_.sections["token"]
    arcs = token_sec.arcs()
    if len(arcs) == 0 or arcs.sum() == 0:
        return None, 0.0
    if target_class is None:
        top_idx = int(arcs.argmax())
        top_state = token_sec.mode_bank[top_idx]
        best_tok = None
        best_score = -1
        for tok, vec in TOKEN_VEC.items():
            s = float(np.abs(np.vdot(vec, top_state))**2)
            if s > best_score:
                best_score = s
                best_tok = tok
        return best_tok, best_score
    candidates = VOCAB_CLASSES.get(target_class, [])
    if not candidates:
        return None, 0.0
    top_idx = int(arcs.argmax())
    top_state = token_sec.mode_bank[top_idx]
    best_tok = None
    best_score = -1
    for tok in candidates:
        s = float(np.abs(np.vdot(TOKEN_VEC[tok], top_state))**2)
        if s > best_score:
            best_score = s
            best_tok = tok
    return best_tok, best_score


def read_intro(sys_):
    """Read what her intro section says she's currently aware of."""
    intro = sys_.intro_section
    arcs = intro.arcs()
    if len(arcs) == 0 or arcs.sum() == 0:
        return None, 0.0
    top_idx = int(arcs.argmax())
    top_state = intro.mode_bank[top_idx]
    # Find which class this most resembles
    best_cls = None
    best_score = -1
    for cls, vec in CLASS_VEC.items():
        s = float(np.abs(np.vdot(vec, top_state))**2)
        if s > best_score:
            best_score = s
            best_cls = cls
    p = arcs / arcs.sum()
    return best_cls, float(p.max())


def say_to_guala_introspective(guala, sentence, verbose=False):
    """Talk to Guala. Read her self-model at every step."""
    tokens = sentence.lower().split()
    valid = [t for t in tokens if t in TOKEN_VEC]
    if not valid:
        return [], None, None

    introspection_log = []

    # BEFORE input: what is she aware of?
    cls_before, conf_before = read_intro(guala)
    introspection_log.append(("before_input", cls_before, conf_before))

    # Feed input + watch introspection
    input_classes = []
    for tok in valid:
        vec = TOKEN_VEC[tok]
        guala.hear_speaker(vec, "listen", "token")
        input_classes.append(TOKEN_CLASS[tok])
        for _ in range(3):
            noisy = normalize(vec + 0.05 * rng.standard_normal(N))
            class_vec = CLASS_VEC[TOKEN_CLASS[tok]]
            ev = {
                "listen": noisy,
                "partner": noisy * 0.7,
                "class": normalize(class_vec + 0.1 * rng.standard_normal(N)) * 0.6,
                "ground": noisy * 0.3,
            }
            guala.tick_once(ev, enable_self_evo=False, coordinator_on=True, introspection_on=True)

    # AFTER hearing input, before responding: what is she aware of?
    cls_heard, conf_heard = read_intro(guala)
    introspection_log.append(("after_hearing", cls_heard, conf_heard))

    if question_about_name(valid):
        response = [{"token": "i", "class": "pronoun_self", "role": "SUBJECT"},
                    {"token": "am", "class": "copula", "role": "COPULA"},
                    {"token": "guala", "class": "name", "role": "NAME"}]
        return response, introspection_log, "name"

    last_class = input_classes[-1]
    template = RESPONSE_TEMPLATES.get(last_class, [("positive", "ACK")])

    response = []
    for slot_class, slot_role in template:
        slot_class_vec = CLASS_VEC[slot_class]
        slot_role_vec = ROLE_VEC[slot_role]
        for _ in range(6):
            ev = {
                "class": normalize(slot_class_vec + 0.05 * rng.standard_normal(N)) * 0.8,
                "role":  normalize(slot_role_vec + 0.05 * rng.standard_normal(N)) * 0.8,
                "token": normalize(slot_class_vec + 0.05 * rng.standard_normal(N)) * 0.5,
                "partner": normalize(rng.standard_normal(N) * 0.1) * 0.3,
                "ground": normalize(rng.standard_normal(N) * 0.1) * 0.2,
                "listen": normalize(rng.standard_normal(N) * 0.05),
            }
            guala.tick_once(ev, enable_self_evo=False, coordinator_on=True, introspection_on=True)

        tok, conf = emit_token_constrained(guala, target_class=slot_class)
        if tok is not None:
            response.append({"token": tok, "class": slot_class, "role": slot_role})
            # AT MOMENT OF EMISSION: what does she think she's doing?
            cls_at_emit, conf_at_emit = read_intro(guala)
            introspection_log.append((f"emit_{tok}", cls_at_emit, conf_at_emit))

        token_sec = guala.sections["token"]
        kick = random_unit_complex(N, rng) * 0.5
        token_sec.psi = normalize(token_sec.psi + kick)

    # AFTER response: what's she aware of?
    cls_after, conf_after = read_intro(guala)
    introspection_log.append(("after_response", cls_after, conf_after))

    return response, introspection_log, "template"


if __name__ == "__main__":
    print("="*70)
    print("GUALA v5 - INTROSPECTION DURING DIALOG")
    print("="*70)

    guala = build_guala()
    print(f"Intro section mode bank: {len(guala.intro_section.mode_bank)} modes (one per class)")
    print()

    user_lines = [
        "hello",
        "what is your name",
        "how are you",
        "i am fine",
        "are you ok",
        "tell me more",
        "thanks",
        "i think",
        "good",
        "no",
    ]

    print("CONVERSATION + INTROSPECTION:")
    print("-" * 70)
    for line in user_lines:
        print(f"\nme:    {line}")
        response, intro_log, mode = say_to_guala_introspective(guala, line)
        if response:
            words = [r["token"] for r in response]
            print(f"guala: {' '.join(words)}  ({mode})")
            print(f"  she was aware of:")
            for stage, cls, conf in intro_log:
                if cls is not None:
                    print(f"    [{stage:>15}] -> {cls} ({conf:.0%})")
                else:
                    print(f"    [{stage:>15}] -> (nothing yet)")
        else:
            print(f"guala: (silent)")

    # Summary: did her self-model track the conversation correctly?
    print("\n" + "="*70)
    print("DOES HER SELF-MODEL MATCH WHAT SHE'S ACTUALLY DOING?")
    print("="*70)
    print(f"Intro section krimelack: {len(guala.intro_krimelack)} self-model commits during the conversation")
    print(f"Atlas leakage from intro into main atlas (should be 0): "
          f"{sum(1 for v in guala.atlas.entries.values() for c in v if c['section'] == 'intro')}")
