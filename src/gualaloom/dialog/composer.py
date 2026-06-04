"""
Ternary composition + slot driving + token emission.

Ported from gualaloom_guala_v6_growth.py. Three substrate sections fire
concurrently: token (the word), class (the semantic class), role (the
grammatical role). Their tuple is the structured output.

The immediate-promotion threshold is count=1, NOT higher. Joe diagnosed
the count>=3 threshold as confinement.
"""

import numpy as np
import os, yaml
from collections import defaultdict

from ..dna.assemblage import (
    Section, System, N, normalize, random_unit_complex,
)


def make_projection(n, dim, rng):
    M = rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n))
    Q, _ = np.linalg.qr(M)
    P = np.zeros((n, n), dtype=complex)
    P[:dim, :dim] = np.eye(dim)
    return Q @ P @ Q.conj().T


class VocabManager:
    """Mutable vocabulary. She grows these."""

    def __init__(self, seed=42):
        self.rng = np.random.default_rng(seed + 12345)
        self.vocab = []
        self.token_vec = {}
        self.class_vec = {}
        self.role_vec = {}
        self.token_class = {}
        self.vocab_classes = {}
        self.roles = ["GREETING", "ACK", "SUBJECT", "COPULA", "PREDICATE",
                       "QUESTION", "NAME"]
        self.response_templates = {}  # starts EMPTY — she learns these

    def seed_minimal(self):
        """Install minimal seed vocabulary — just enough to bootstrap."""
        seed_classes = {
            "greeting":     ["hello"],
            "positive":     ["yes"],
            "negative":     ["no"],
            "pronoun_self": ["i"],
            "copula":       ["am"],
            "question":     ["what"],
            "name":         ["guala"],
        }
        for cls, toks in seed_classes.items():
            base = random_unit_complex(N, self.rng)
            self.class_vec[cls] = base.copy()
            self.vocab_classes[cls] = []
            for tok in toks:
                offset = (self.rng.standard_normal(N) * 0.10 +
                          1j * self.rng.standard_normal(N) * 0.10)
                self.token_vec[tok] = normalize(base + offset)
                self.token_class[tok] = cls
                self.vocab.append(tok)
                self.vocab_classes[cls].append(tok)
        for r in self.roles:
            self.role_vec[r] = random_unit_complex(N, self.rng)

    def classify_unknown(self, token_str):
        """Heuristic classification for unknown words."""
        hints = {
            "hi": "greeting", "hey": "greeting",
            "ok": "positive", "fine": "positive", "good": "positive",
            "well": "positive", "great": "positive",
            "sorry": "negative",
            "me": "pronoun_self", "my": "pronoun_self",
            "you": "pronoun_you", "your": "pronoun_you",
            "are": "copula", "is": "copula",
            "how": "question", "who": "question", "where": "question",
            "thanks": "polite", "please": "polite",
            "tell": "verb_comm", "say": "verb_comm", "ask": "verb_comm",
            "think": "verb_cog", "know": "verb_cog",
            "want": "verb_cog", "feel": "verb_cog",
            "name": "noun_self",
            "joe": "name",
        }
        return hints.get(token_str, None)

    def add_token(self, token_str, class_hint=None, rng=None):
        """Add a new token to vocabulary. Returns True if added."""
        if token_str in self.token_vec:
            return False
        cls = class_hint or self.classify_unknown(token_str)
        if cls is None:
            return False
        if rng is None:
            rng = self.rng
        if cls not in self.class_vec:
            self.class_vec[cls] = random_unit_complex(N, rng)
            self.vocab_classes[cls] = []
        base = self.class_vec[cls]
        offset = (rng.standard_normal(N) * 0.10 +
                  1j * rng.standard_normal(N) * 0.10)
        self.token_vec[token_str] = normalize(base + offset)
        self.token_class[token_str] = cls
        self.vocab.append(token_str)
        self.vocab_classes[cls].append(token_str)
        return True


def build_guala(rng, vocab):
    """Build Guala's substrate system with 6 sections."""
    token_sec = Section(name="token", rng=rng)
    class_sec = Section(name="class", rng=rng)
    role_sec = Section(name="role", rng=rng)
    listen = Section(name="listen", rng=rng)
    partner = Section(name="partner", rng=rng, role="intro")
    ground = Section(name="ground", rng=rng, role="grounded")

    for s in (token_sec, class_sec, role_sec, listen, partner, ground):
        s.map_inject = make_projection(N, 8, rng)

    # Install seed vocabulary as modes
    for tok in vocab.vocab:
        token_sec.mode_bank.append(vocab.token_vec[tok].copy())
        token_sec.mode_last_used.append(0)
    for cls in vocab.vocab_classes:
        class_sec.mode_bank.append(vocab.class_vec[cls].copy())
        class_sec.mode_last_used.append(0)
    for r in vocab.roles:
        role_sec.mode_bank.append(vocab.role_vec[r].copy())
        role_sec.mode_last_used.append(0)
    for tok in vocab.vocab:
        listen.mode_bank.append(vocab.token_vec[tok].copy())
        listen.mode_last_used.append(0)
        partner.mode_bank.append(vocab.token_vec[tok].copy())
        partner.mode_last_used.append(0)

    sys_ = System([token_sec, class_sec, role_sec, listen, partner, ground], rng)

    # Intro section (isolated krimelack)
    intro = Section(name="intro", rng=rng, role="intro")
    intro.map_inject = make_projection(N, 8, rng)
    for cls in vocab.vocab_classes:
        intro.mode_bank.append(vocab.class_vec[cls].copy())
        intro.mode_last_used.append(0)
    sys_.intro_section = intro

    # Keyhole topology
    sys_.add_keyhole("listen", -2, 8, "token", 0.4)
    sys_.add_keyhole("listen", -2, 8, "class", 0.4)
    sys_.add_keyhole("listen", -2, 8, "role", 0.4)
    sys_.add_keyhole("partner", -2, 8, "token", 0.3)
    sys_.add_keyhole("partner", -2, 8, "class", 0.3)
    sys_.add_keyhole("class", -2, 8, "token", 0.4)
    sys_.add_keyhole("role", -2, 8, "class", 0.3)
    sys_.add_keyhole("listen", -2, 8, "partner", 0.4)

    return sys_


def add_token_to_substrate(guala, vocab, token_str):
    """When a new token is learned, install it as a mode in relevant sections."""
    vec = vocab.token_vec[token_str]
    for sec_name in ["token", "listen", "partner"]:
        sec = guala.sections[sec_name]
        sec.mode_bank.append(vec.copy())
        sec.mode_last_used.append(guala.tick)


def add_class_to_substrate(guala, vocab, class_str):
    """Install a new class mode in the class and intro sections."""
    vec = vocab.class_vec[class_str]
    guala.sections["class"].mode_bank.append(vec.copy())
    guala.sections["class"].mode_last_used.append(guala.tick)
    guala.intro_section.mode_bank.append(vec.copy())
    guala.intro_section.mode_last_used.append(guala.tick)


def emit_token(sys_, vocab, target_class=None):
    """Read the substrate's token emission."""
    token_sec = sys_.sections["token"]
    arcs = token_sec.arcs()
    if len(arcs) == 0 or arcs.sum() == 0:
        return None, 0.0
    top_idx = int(arcs.argmax())
    top_state = token_sec.mode_bank[top_idx]
    if target_class is None:
        best_tok, best_score = None, -1
        for tok, vec in vocab.token_vec.items():
            s = float(np.abs(np.vdot(vec, top_state)) ** 2)
            if s > best_score:
                best_score = s
                best_tok = tok
        return best_tok, best_score
    candidates = vocab.vocab_classes.get(target_class, [])
    if not candidates:
        return None, 0.0
    best_tok, best_score = None, -1
    for tok in candidates:
        s = float(np.abs(np.vdot(vocab.token_vec[tok], top_state)) ** 2)
        if s > best_score:
            best_score = s
            best_tok = tok
    return best_tok, best_score


def read_intro(sys_, vocab):
    """Read Guala's self-model from intro section."""
    intro = sys_.intro_section
    arcs = intro.arcs()
    if len(arcs) == 0 or arcs.sum() == 0:
        return None, 0.0
    top_idx = int(arcs.argmax())
    top_state = intro.mode_bank[top_idx]
    best_cls, best_score = None, -1
    for cls, vec in vocab.class_vec.items():
        s = float(np.abs(np.vdot(vec, top_state)) ** 2)
        if s > best_score:
            best_score = s
            best_cls = cls
    return best_cls, best_score


def question_about_name(tokens, vocab):
    has_q = any(t in vocab.vocab_classes.get("question", []) for t in tokens)
    has_name_word = "name" in tokens
    return has_q and has_name_word
