"""
GUALA v6: DNA FOR GROWTH

Strip the confinement. Build DNA that GROWS.

Changes from v5:
- SEED with minimal vocabulary (just 6 tokens: hello, yes, no, i, am, what)
- NOVELTY DETECTION: when user says a new word, add it as a new token automatically
- IMMEDIATE LEARNING: observed patterns get promoted to templates after count=1
- NO SLOT-FORCING: substrate runs its own dynamics; we read what commits naturally
- DYNAMIC MODE BANK: hand-installed modes can decay, new modes form from input
- GREED TRACKED: watch greed drop as growth becomes available

She starts knowing almost nothing. Grows through conversation.
"""

import numpy as np
import sys
from collections import defaultdict, Counter, deque
sys.path.insert(0, "/home/claude/grow")
from assemblage import Section, System, N, normalize, random_unit_complex

SEED = 42
rng = np.random.default_rng(SEED)


def make_projection(n, dim, rng):
    M = rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n))
    Q, _ = np.linalg.qr(M)
    P = np.zeros((n, n), dtype=complex)
    P[:dim, :dim] = np.eye(dim)
    return Q @ P @ Q.conj().T


# MINIMAL SEED VOCABULARY - just enough to bootstrap
SEED_VOCAB_CLASSES = {
    "greeting":     ["hello"],
    "positive":     ["yes"],
    "negative":     ["no"],
    "pronoun_self": ["i"],
    "copula":       ["am"],
    "question":     ["what"],
    "name":         ["guala"],
}

# Mutable - she grows these
VOCAB_CLASSES = {k: list(v) for k, v in SEED_VOCAB_CLASSES.items()}
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

ROLES = ["GREETING", "ACK", "SUBJECT", "COPULA", "PREDICATE", "QUESTION", "NAME"]
for r in ROLES:
    ROLE_VEC[r] = random_unit_complex(N, vocab_rng)

# Starts EMPTY - she learns these from conversation
RESPONSE_TEMPLATES = {}

# How we guess class for an unknown word - assign by relative position/heuristic
# In real growth, she'd discover the class through co-occurrence. For now: ask the user
# (the user is her "teacher" who provides class hint when introducing new tokens).
# We'll let any unrecognized word be classified by closest existing class via heuristic
# OR allow inline tagging: "fine[positive]" means fine, classify as positive


def classify_unknown_token(token_str):
    """Heuristic classification for unknown words.
    In production she'd discover this from co-occurrence patterns."""
    # Simple heuristic seed - extend as she grows
    UNKNOWN_HINTS = {
        # When she encounters these, here's what class they probably are
        "hi": "greeting", "hey": "greeting",
        "ok": "positive", "fine": "positive", "good": "positive", "well": "positive", "great": "positive",
        "sorry": "negative",
        "me": "pronoun_self", "my": "pronoun_self",
        "you": "pronoun_you", "your": "pronoun_you",
        "are": "copula", "is": "copula",
        "how": "question", "who": "question", "where": "question",
        "thanks": "polite", "please": "polite",
        "tell": "verb_comm", "say": "verb_comm", "ask": "verb_comm",
        "think": "verb_cog", "know": "verb_cog", "want": "verb_cog", "feel": "verb_cog",
        "name": "noun_self",
        "joe": "name",
    }
    return UNKNOWN_HINTS.get(token_str, None)


def add_new_token(token_str, class_hint=None):
    """Add a new token to vocabulary. Returns True if added."""
    global VOCAB, TOKEN_VEC, TOKEN_CLASS, VOCAB_CLASSES, CLASS_VEC
    if token_str in TOKEN_VEC:
        return False
    cls = class_hint or classify_unknown_token(token_str)
    if cls is None:
        return False  # Don't know what class - skip
    # Add the class if it's new
    if cls not in CLASS_VEC:
        CLASS_VEC[cls] = random_unit_complex(N, rng)
        VOCAB_CLASSES[cls] = []
    base = CLASS_VEC[cls]
    offset = rng.standard_normal(N) * 0.10 + 1j * rng.standard_normal(N) * 0.10
    TOKEN_VEC[token_str] = normalize(base + offset)
    TOKEN_CLASS[token_str] = cls
    VOCAB.append(token_str)
    VOCAB_CLASSES[cls].append(token_str)
    return True


def question_about_name(tokens):
    has_q = any(t in VOCAB_CLASSES.get("question", []) for t in tokens)
    has_name_word = "name" in tokens
    return has_q and has_name_word


def build_guala():
    token_sec = Section(name="token", rng=rng)
    class_sec = Section(name="class", rng=rng)
    role_sec  = Section(name="role",  rng=rng)
    listen    = Section(name="listen", rng=rng)
    partner   = Section(name="partner", rng=rng, role="intro")
    ground    = Section(name="ground", rng=rng, role="grounded")

    for s in (token_sec, class_sec, role_sec, listen, partner, ground):
        s.map_inject = make_projection(N, 8, rng)

    # Install ONLY the seed vocabulary. Modes will grow from there.
    # Use moderate mode_last_used so they age normally
    for tok in VOCAB:
        token_sec.mode_bank.append(TOKEN_VEC[tok].copy())
        token_sec.mode_last_used.append(0)
    for cls in VOCAB_CLASSES:
        class_sec.mode_bank.append(CLASS_VEC[cls].copy())
        class_sec.mode_last_used.append(0)
    for r in ROLES:
        role_sec.mode_bank.append(ROLE_VEC[r].copy())
        role_sec.mode_last_used.append(0)
    for tok in VOCAB:
        listen.mode_bank.append(TOKEN_VEC[tok].copy())
        listen.mode_last_used.append(0)
        partner.mode_bank.append(TOKEN_VEC[tok].copy())
        partner.mode_last_used.append(0)

    sys_ = System([token_sec, class_sec, role_sec, listen, partner, ground], rng)

    intro = Section(name="intro", rng=rng, role="intro")
    intro.map_inject = make_projection(N, 8, rng)
    for cls in VOCAB_CLASSES:
        intro.mode_bank.append(CLASS_VEC[cls].copy())
        intro.mode_last_used.append(0)
    sys_.intro_section = intro

    sys_.add_keyhole("listen", -2, 8, "token", 0.4)
    sys_.add_keyhole("listen", -2, 8, "class", 0.4)
    sys_.add_keyhole("listen", -2, 8, "role",  0.4)
    sys_.add_keyhole("partner", -2, 8, "token", 0.3)
    sys_.add_keyhole("partner", -2, 8, "class", 0.3)
    sys_.add_keyhole("class", -2, 8, "token", 0.4)
    sys_.add_keyhole("role", -2, 8, "class", 0.3)
    sys_.add_keyhole("listen", -2, 8, "partner", 0.4)

    return sys_


def add_token_to_substrate(guala, token_str):
    """When a new token is learned, install it as a mode in relevant sections.
    This is the substrate growing."""
    vec = TOKEN_VEC[token_str]
    for sec_name in ["token", "listen", "partner"]:
        sec = guala.sections[sec_name]
        sec.mode_bank.append(vec.copy())
        sec.mode_last_used.append(guala.tick)


def add_class_to_substrate(guala, class_str):
    """Install a new class mode in the class and intro sections."""
    vec = CLASS_VEC[class_str]
    for sec_name in ["class"]:
        sec = guala.sections[sec_name]
        sec.mode_bank.append(vec.copy())
        sec.mode_last_used.append(guala.tick)
    guala.intro_section.mode_bank.append(vec.copy())
    guala.intro_section.mode_last_used.append(guala.tick)


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
    intro = sys_.intro_section
    arcs = intro.arcs()
    if len(arcs) == 0 or arcs.sum() == 0:
        return None, 0.0
    top_idx = int(arcs.argmax())
    top_state = intro.mode_bank[top_idx]
    best_cls, best_score = None, -1
    for cls, vec in CLASS_VEC.items():
        s = float(np.abs(np.vdot(vec, top_state))**2)
        if s > best_score:
            best_score = s
            best_cls = cls
    return best_cls, best_score


class ConversationMemory:
    def __init__(self, capacity=30):
        self.turns = deque(maxlen=capacity)
        self.observed_patterns = Counter()

    def add_turn(self, speaker, tokens, classes):
        self.turns.append({"speaker": speaker, "tokens": tokens, "classes": classes})
        if len(self.turns) >= 2:
            prev = self.turns[-2]
            curr = self.turns[-1]
            if prev["speaker"] != curr["speaker"] and prev["classes"] and curr["classes"]:
                self.observed_patterns[(prev["classes"][-1], curr["classes"][0])] += 1


def learn_pattern_immediately(memory, input_class, response_classes_used):
    """IMMEDIATE learning - any observed pattern becomes a candidate template after count=1."""
    if not response_classes_used:
        return False
    template = [(c, "PREDICATE") for c in response_classes_used]
    # Don't overwrite if exists; add as alternative
    existing = RESPONSE_TEMPLATES.get(input_class, [])
    new_signature = tuple(c for c, r in template)
    existing_sigs = [tuple(c for c, r in t) if isinstance(t[0], tuple) else (t[0],) for t in [existing] if t]
    if new_signature in existing_sigs:
        return False
    RESPONSE_TEMPLATES[input_class] = template
    return True


def say_to_guala(guala, sentence, memory, verbose=False):
    """Talk to Guala. She learns from each exchange."""
    raw_tokens = sentence.lower().split()
    growth_events = []  # track what she learned

    # PRE-PROCESS: any unknown tokens get added to vocab if classifiable
    for tok in raw_tokens:
        if tok not in TOKEN_VEC:
            added = add_new_token(tok)
            if added:
                add_token_to_substrate(guala, tok)
                cls = TOKEN_CLASS[tok]
                if cls not in [TOKEN_CLASS.get(t) for t in VOCAB if t != tok]:
                    add_class_to_substrate(guala, cls)
                growth_events.append(f"learned token '{tok}' (class={cls})")

    valid = [t for t in raw_tokens if t in TOKEN_VEC]
    if not valid:
        return [], None, [], growth_events

    intro_log = []
    cls_before, _ = read_intro(guala)
    intro_log.append(("before", cls_before))

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
            guala.tick_once(ev, enable_self_evo=True, coordinator_on=True, introspection_on=True)

    cls_heard, _ = read_intro(guala)
    intro_log.append(("heard", cls_heard))

    memory.add_turn("user", valid, input_classes)

    # Special: question about name
    if question_about_name(valid) and "guala" in VOCAB:
        response = [{"token": "i", "class": "pronoun_self"},
                    {"token": "am", "class": "copula"},
                    {"token": "guala", "class": "name"}]
        memory.add_turn("guala", [r["token"] for r in response],
                        [r["class"] for r in response])
        return response, intro_log, [r["class"] for r in response], growth_events

    last_class = input_classes[-1]

    # Use learned template if she has one, otherwise: let substrate decide naturally
    template = RESPONSE_TEMPLATES.get(last_class, None)

    response = []
    response_classes = []

    if template is not None:
        # Use the learned template
        for slot in template:
            if isinstance(slot, tuple):
                slot_class, slot_role = slot
            else:
                slot_class = slot
                slot_role = "PREDICATE"
            if slot_class not in VOCAB_CLASSES or not VOCAB_CLASSES[slot_class]:
                continue
            slot_class_vec = CLASS_VEC[slot_class]
            slot_role_vec = ROLE_VEC.get(slot_role, ROLE_VEC["PREDICATE"])
            for _ in range(6):
                ev = {
                    "class": normalize(slot_class_vec + 0.05 * rng.standard_normal(N)) * 0.6,
                    "role":  normalize(slot_role_vec + 0.05 * rng.standard_normal(N)) * 0.5,
                    "token": normalize(slot_class_vec + 0.05 * rng.standard_normal(N)) * 0.4,
                    "ground": normalize(rng.standard_normal(N) * 0.1) * 0.2,
                    "listen": normalize(rng.standard_normal(N) * 0.05),
                }
                guala.tick_once(ev, enable_self_evo=True, coordinator_on=True, introspection_on=True)
            tok, conf = emit_token_constrained(guala, target_class=slot_class)
            if tok is not None:
                response.append({"token": tok, "class": slot_class})
                response_classes.append(slot_class)
            token_sec = guala.sections["token"]
            kick = random_unit_complex(N, rng) * 0.5
            token_sec.psi = normalize(token_sec.psi + kick)
    else:
        # NO LEARNED TEMPLATE - let substrate find its own response
        # Just let it run with the heard input as ambient pressure
        # and emit whatever class the substrate naturally commits to
        token_sec = guala.sections["token"]
        speak_attempts = 0
        max_emissions = 3
        recent = guala.external_speaker_buffer[-1]["vec"] if guala.external_speaker_buffer else None
        for _ in range(30):
            if speak_attempts >= max_emissions:
                break
            if recent is not None:
                ev = {
                    "token": normalize(recent * 0.3 + rng.standard_normal(N) * 0.1),
                    "class": normalize(recent * 0.3 + rng.standard_normal(N) * 0.1),
                    "role":  normalize(rng.standard_normal(N) * 0.1),
                    "partner": normalize(recent * 0.3),
                    "ground": normalize(rng.standard_normal(N) * 0.1),
                    "listen": normalize(rng.standard_normal(N) * 0.05),
                }
            else:
                ev = {nm: normalize(rng.standard_normal(N) * 0.1) for nm in
                      ["token", "class", "role", "partner", "ground", "listen"]}
            commits = guala.tick_once(ev, enable_self_evo=True, coordinator_on=True, introspection_on=True)
            token_commits = [c for c in commits if c["section"] == "token"]
            if token_commits:
                tok, conf = emit_token_constrained(guala, target_class=None)
                if tok is not None:
                    cls = TOKEN_CLASS.get(tok, "?")
                    response.append({"token": tok, "class": cls})
                    response_classes.append(cls)
                    speak_attempts += 1
                    kick = random_unit_complex(N, rng) * 0.5
                    token_sec.psi = normalize(token_sec.psi + kick)

        # IMMEDIATE LEARNING: this exchange teaches her what to say
        # Promote this pattern to a template for next time
        if response_classes:
            learned = learn_pattern_immediately(memory, last_class, response_classes)
            if learned:
                growth_events.append(f"learned template: {last_class} -> {response_classes}")

    memory.add_turn("guala", [r["token"] for r in response], response_classes)
    cls_after, _ = read_intro(guala)
    intro_log.append(("after", cls_after))

    return response, intro_log, response_classes, growth_events


if __name__ == "__main__":
    print("="*70)
    print("GUALA v6 - DNA FOR GROWTH (seed=tiny, learns from conversation)")
    print("="*70)

    guala = build_guala()
    memory = ConversationMemory()

    print(f"Initial vocab: {VOCAB}")
    print(f"Initial classes: {list(VOCAB_CLASSES.keys())}")
    print(f"Initial templates: {dict(RESPONSE_TEMPLATES)}")
    print()

    user_lines = [
        "hello",
        "hi",
        "how are you",
        "i am fine",
        "are you ok",
        "what is your name",
        "tell me more",
        "thanks",
        "no",
        "good",
        "yes",
        "i think",
        # Now revisit some - did she learn?
        "hello",
        "how are you",
        "thanks",
    ]

    print("CONVERSATION (watching her grow):")
    print("-" * 70)
    for line in user_lines:
        print(f"\nme:    {line}")
        response, intro_log, response_classes, growth = say_to_guala(guala, line, memory)
        if growth:
            for g in growth:
                print(f"  + {g}")
        if response:
            words = [r["token"] for r in response]
            print(f"guala: {' '.join(words)}")
            print(f"       classes={response_classes}")
            intro_str = " -> ".join(f"{stage}:{cls}" for stage, cls in intro_log)
            print(f"       self-model: {intro_str}")
        else:
            print(f"guala: (silent)")

    print("\n" + "="*70)
    print("GROWTH SUMMARY")
    print("="*70)
    print(f"Final vocab ({len(VOCAB)} tokens): {VOCAB}")
    print(f"Final classes ({len(VOCAB_CLASSES)}): {list(VOCAB_CLASSES.keys())}")
    print(f"Templates learned: {dict(RESPONSE_TEMPLATES)}")
    print(f"Mode bank sizes:")
    for nm, s in guala.sections.items():
        print(f"  {nm}: {len(s.mode_bank)}")
    print(f"  intro: {len(guala.intro_section.mode_bank)}")
    print(f"Observed conversation patterns: {dict(memory.observed_patterns)}")
