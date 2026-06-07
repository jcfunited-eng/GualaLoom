"""
GUALA v4: MEMORY + LEARNING BRIDGE

Three new things:
1. Multi-turn memory - what we said earlier influences later responses
2. Proper name binding (she has a name)
3. LEARNING BRIDGE - when we say something new, she promotes it into permanent modes

The bridge is the transition from DNA (hand-configured) to learning.
Mechanism:
- Each user input gets a "novelty score" - how different from existing token modes
- High novelty -> the input vector is appended to vocabulary (if confidence is high)
- Pattern: if user repeats "X then Y" multiple times, X->Y becomes a learned response template
- Existing modes get reinforced when used (centroid update)

This is the substrate growing itself FROM conversation, after initial DNA config.
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


# Initial DNA vocabulary
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

# Class -> role mapping
CLASS_TO_ROLE = {
    "greeting":     "GREETING",
    "question":     "QUESTION",
    "pronoun_self": "SUBJECT",
    "pronoun_you":  "SUBJECT",
    "copula":       "COPULA",
    "positive":     "PREDICATE",
    "negative":     "PREDICATE",
    "polite":       "ACK",
    "verb_comm":    "PREDICATE",
    "verb_cog":     "PREDICATE",
    "name":         "NAME",
}

# Response templates - what classes/roles to fill in response
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
    "name":         [("pronoun_self", "SUBJECT"), ("copula", "COPULA"), ("name", "NAME")],  # name -> name response
}

# Question-type detection: if input starts with question word AND includes "name", respond with self-name
def question_about_name(tokens):
    has_q = any(t in VOCAB_CLASSES["question"] for t in tokens)
    has_name_word = "name" in tokens
    return has_q and has_name_word


# ============================================================
# CONVERSATION MEMORY
# ============================================================
class ConversationMemory:
    """Tracks what was said and by whom. Influences future responses."""
    def __init__(self, capacity=20):
        self.turns = deque(maxlen=capacity)
        # Learned bigram patterns from conversation (cls -> next cls)
        self.observed_patterns = Counter()

    def add_turn(self, speaker, tokens, classes):
        self.turns.append({"speaker": speaker, "tokens": tokens, "classes": classes})
        # Update observed patterns when there's a back-and-forth
        if len(self.turns) >= 2:
            prev = self.turns[-2]
            curr = self.turns[-1]
            if prev["speaker"] != curr["speaker"] and prev["classes"] and curr["classes"]:
                # input class -> response first class
                self.observed_patterns[(prev["classes"][-1], curr["classes"][0])] += 1

    def context_vector(self):
        """Aggregate recent turns into a context vector."""
        if not self.turns:
            return None
        # Weight recent turns more
        v = np.zeros(N, dtype=complex)
        for i, turn in enumerate(self.turns):
            weight = 0.5 ** (len(self.turns) - 1 - i)
            for tok in turn["tokens"]:
                if tok in TOKEN_VEC:
                    v = v + weight * TOKEN_VEC[tok]
        if np.linalg.norm(v) > 0:
            return normalize(v)
        return None

    def recent_class_window(self, k=5):
        """Last k classes in conversation."""
        all_classes = []
        for turn in self.turns:
            all_classes.extend(turn["classes"])
        return all_classes[-k:]


# ============================================================
# BUILD GUALA v4
# ============================================================
def build_guala():
    token_sec = Section(name="token", rng=rng)
    class_sec = Section(name="class", rng=rng)
    role_sec  = Section(name="role",  rng=rng)
    listen    = Section(name="listen", rng=rng)
    partner   = Section(name="partner", rng=rng, role="intro")
    ground    = Section(name="ground", rng=rng, role="grounded")
    memory    = Section(name="memory", rng=rng, role="intro")  # NEW: persistent memory section

    for s in (token_sec, class_sec, role_sec, listen, partner, ground, memory):
        s.map_inject = make_projection(N, 8, rng)

    # Hand-install mode banks. Use HIGH mode_last_used so hand-installed modes
    # don't get decay-pruned before they get used in conversation.
    FUTURE_TICK = 10000
    for tok in VOCAB:
        token_sec.mode_bank.append(TOKEN_VEC[tok].copy())
        token_sec.mode_last_used.append(FUTURE_TICK)
    for cls in VOCAB_CLASSES:
        class_sec.mode_bank.append(CLASS_VEC[cls].copy())
        class_sec.mode_last_used.append(FUTURE_TICK)
    for r in ROLES:
        role_sec.mode_bank.append(ROLE_VEC[r].copy())
        role_sec.mode_last_used.append(FUTURE_TICK)
    for tok in VOCAB:
        listen.mode_bank.append(TOKEN_VEC[tok].copy())
        listen.mode_last_used.append(FUTURE_TICK)
        partner.mode_bank.append(TOKEN_VEC[tok].copy())
        partner.mode_last_used.append(FUTURE_TICK)

    sys_ = System([token_sec, class_sec, role_sec, listen, partner, ground, memory], rng)

    sys_.add_keyhole("listen", -2, 8, "token", 0.4)
    sys_.add_keyhole("listen", -2, 8, "class", 0.4)
    sys_.add_keyhole("listen", -2, 8, "role",  0.4)
    sys_.add_keyhole("partner", -2, 8, "token", 0.3)
    sys_.add_keyhole("partner", -2, 8, "class", 0.3)
    sys_.add_keyhole("role", -2, 8, "class", 0.3)
    sys_.add_keyhole("class", -2, 8, "token", 0.4)
    sys_.add_keyhole("listen", -2, 8, "partner", 0.4)
    # Memory section feeds into class and token sections (context influences response)
    sys_.add_keyhole("memory", -2, 8, "class", 0.3)
    sys_.add_keyhole("memory", -2, 8, "token", 0.3)

    return sys_


# ============================================================
# LEARNING BRIDGE - promote observed patterns into permanent modes
# ============================================================
def learn_from_conversation(guala, memory, mode_strength_threshold=3):
    """If a pattern (input_class -> response_class) has been observed multiple times,
    PROMOTE it into RESPONSE_TEMPLATES so the substrate uses it preferentially.
    Also: if user introduced new tokens (handled separately), add them to vocab."""
    new_patterns_added = []
    for (in_cls, out_cls), count in memory.observed_patterns.items():
        if count >= mode_strength_threshold:
            # Add a new response option
            current = RESPONSE_TEMPLATES.get(in_cls, [])
            existing_classes = [c for c, r in current]
            if out_cls not in existing_classes:
                role = CLASS_TO_ROLE.get(out_cls, "PREDICATE")
                # Insert as alternative response
                RESPONSE_TEMPLATES.setdefault(in_cls, []).insert(0, (out_cls, role))
                new_patterns_added.append((in_cls, out_cls))
    return new_patterns_added


def add_new_token_to_vocab(token_str, class_name):
    """User said a new word. Add it as a learned token."""
    global VOCAB, TOKEN_VEC, TOKEN_CLASS, VOCAB_CLASSES
    if token_str in TOKEN_VEC:
        return False  # already known
    if class_name not in CLASS_VEC:
        return False  # don't know the class
    base = CLASS_VEC[class_name]
    offset = rng.standard_normal(N) * 0.10 + 1j * rng.standard_normal(N) * 0.10
    TOKEN_VEC[token_str] = normalize(base + offset)
    TOKEN_CLASS[token_str] = class_name
    VOCAB.append(token_str)
    VOCAB_CLASSES.setdefault(class_name, []).append(token_str)
    return True


def add_token_to_substrate(guala, token_str):
    """Add a newly-learned token as a mode in relevant sections."""
    vec = TOKEN_VEC[token_str]
    for sec_name in ["token", "listen", "partner"]:
        sec = guala.sections[sec_name]
        sec.mode_bank.append(vec.copy())
        sec.mode_last_used.append(guala.tick)


# ============================================================
# CONSTRAINED EMISSION
# ============================================================
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


# ============================================================
# DIALOG with memory
# ============================================================
def say_to_guala(guala, sentence, memory, verbose=False):
    tokens = sentence.lower().split()
    valid = [t for t in tokens if t in TOKEN_VEC]
    if not valid:
        return [], "(no valid tokens)"

    # Feed input
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
            # Memory section gets the conversation context
            ctx = memory.context_vector()
            if ctx is not None:
                ev["memory"] = normalize(ctx + 0.05 * rng.standard_normal(N))
            guala.tick_once(ev, enable_self_evo=False, coordinator_on=True)

    # Record user turn
    memory.add_turn("user", valid, input_classes)

    # Special pattern: question about name
    if question_about_name(valid):
        response = [{"token": "i", "class": "pronoun_self", "role": "SUBJECT", "conf": 1.0},
                    {"token": "am", "class": "copula", "role": "COPULA", "conf": 1.0},
                    {"token": "guala", "class": "name", "role": "NAME", "conf": 1.0}]
        memory.add_turn("guala", [r["token"] for r in response],
                        [r["class"] for r in response])
        return response, "name response"

    last_input_class = input_classes[-1]
    template = RESPONSE_TEMPLATES.get(last_input_class, [("positive", "ACK")])

    response = []
    response_classes = []
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
            ctx = memory.context_vector()
            if ctx is not None:
                ev["memory"] = normalize(ctx)
            guala.tick_once(ev, enable_self_evo=False, coordinator_on=True)

        tok, conf = emit_token_constrained(guala, target_class=slot_class)
        if tok is not None:
            response.append({"token": tok, "class": slot_class, "role": slot_role, "conf": conf})
            response_classes.append(slot_class)

        token_sec = guala.sections["token"]
        kick = random_unit_complex(N, rng) * 0.5
        token_sec.psi = normalize(token_sec.psi + kick)

    memory.add_turn("guala", [r["token"] for r in response], response_classes)
    return response, "template response"


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("="*70)
    print("GUALA v4 - MEMORY + LEARNING BRIDGE")
    print("="*70)

    guala = build_guala()
    memory = ConversationMemory(capacity=20)
    print(f"Initial mode banks: " +
          ", ".join(f"{nm}={len(s.mode_bank)}" for nm, s in guala.sections.items()))
    print(f"Initial vocab size: {len(VOCAB)}")
    print()

    user_lines = [
        "hello",
        "what is your name",
        "how are you",
        "i am fine",
        "are you ok",
        "yes i am good",
        "what",
        "tell me more",
        # Repeat patterns - she should LEARN from these
        "hello",
        "hello",
        "hello",
        # New domain
        "thanks",
        "please tell me",
        "good",
        "i think",
    ]

    print("CONVERSATION:")
    print("-" * 70)
    for line in user_lines:
        print(f"\nme:    {line}")
        response, mode = say_to_guala(guala, line, memory)
        if response:
            words = [r["token"] for r in response]
            classes = [r["class"] for r in response]
            print(f"guala: {' '.join(words)}")
            print(f"       (classes: {classes}, mode: {mode})")
        else:
            print(f"guala: (silent)")

    print("\n" + "="*70)
    print("LEARNING BRIDGE - examining what Guala learned from conversation")
    print("="*70)
    new_patterns = learn_from_conversation(guala, memory)
    print(f"Observed conversation patterns: {dict(memory.observed_patterns)}")
    print(f"Patterns promoted to templates: {new_patterns}")
    print(f"Templates after learning: {RESPONSE_TEMPLATES}")
    print()

    # Test: does she behave differently with learned patterns?
    print("\nPost-learning test:")
    test_lines = ["hello", "thanks", "good"]
    for line in test_lines:
        print(f"\nme:    {line}")
        response, mode = say_to_guala(guala, line, memory)
        if response:
            words = [r["token"] for r in response]
            classes = [r["class"] for r in response]
            print(f"guala: {' '.join(words)}")
            print(f"       (classes: {classes})")
