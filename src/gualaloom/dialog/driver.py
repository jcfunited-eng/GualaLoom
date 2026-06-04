"""
Dialog driver — say_to_guala() and REPL.

Ported from gualaloom_guala_v6_growth.py. This is the conversation loop.
"""

import numpy as np

from ..dna.assemblage import N, normalize, random_unit_complex
from .composer import (
    VocabManager, build_guala, add_token_to_substrate, add_class_to_substrate,
    emit_token, read_intro, question_about_name,
)
from .memory import ConversationMemory
from .learning_bridge import learn_pattern_immediately


def say_to_guala(guala, sentence, vocab, memory, rng, verbose=False):
    """Talk to Guala. She learns from each exchange."""
    raw_tokens = sentence.lower().split()
    growth_events = []

    # Pre-process: unknown tokens get added if classifiable
    for tok in raw_tokens:
        if tok not in vocab.token_vec:
            added = vocab.add_token(tok, rng=rng)
            if added:
                add_token_to_substrate(guala, vocab, tok)
                cls = vocab.token_class[tok]
                existing_classes = set(vocab.token_class[t] for t in vocab.vocab if t != tok)
                if cls not in existing_classes:
                    add_class_to_substrate(guala, vocab, cls)
                growth_events.append(f"learned token '{tok}' (class={cls})")

    valid = [t for t in raw_tokens if t in vocab.token_vec]
    if not valid:
        return [], None, [], growth_events

    intro_log = []
    cls_before, _ = read_intro(guala, vocab)
    intro_log.append(("before", cls_before))

    input_classes = []
    for tok in valid:
        vec = vocab.token_vec[tok]
        guala.hear_speaker(vec, "listen", "token")
        input_classes.append(vocab.token_class[tok])
        for _ in range(3):
            noisy = normalize(vec + 0.05 * rng.standard_normal(N))
            class_vec = vocab.class_vec[vocab.token_class[tok]]
            ev = {
                "listen": noisy,
                "partner": noisy * 0.7,
                "class": normalize(class_vec + 0.1 * rng.standard_normal(N)) * 0.6,
                "ground": noisy * 0.3,
            }
            guala.tick_once(ev, enable_self_evo=True,
                            coordinator_on=True, introspection_on=True)

    cls_heard, _ = read_intro(guala, vocab)
    intro_log.append(("heard", cls_heard))

    memory.add_turn("user", valid, input_classes)

    # Special: question about name
    if question_about_name(valid, vocab) and "guala" in vocab.vocab:
        response = [{"token": "i", "class": "pronoun_self"},
                    {"token": "am", "class": "copula"},
                    {"token": "guala", "class": "name"}]
        memory.add_turn("guala", [r["token"] for r in response],
                        [r["class"] for r in response])
        return response, intro_log, [r["class"] for r in response], growth_events

    last_class = input_classes[-1]
    template = vocab.response_templates.get(last_class, None)
    response = []
    response_classes = []

    if template is not None:
        for slot in template:
            if isinstance(slot, tuple):
                slot_class, slot_role = slot
            else:
                slot_class = slot
                slot_role = "PREDICATE"
            if slot_class not in vocab.vocab_classes or not vocab.vocab_classes[slot_class]:
                continue
            slot_class_vec = vocab.class_vec[slot_class]
            slot_role_vec = vocab.role_vec.get(slot_role, vocab.role_vec["PREDICATE"])
            for _ in range(6):
                ev = {
                    "class": normalize(slot_class_vec + 0.05 * rng.standard_normal(N)) * 0.6,
                    "role": normalize(slot_role_vec + 0.05 * rng.standard_normal(N)) * 0.5,
                    "token": normalize(slot_class_vec + 0.05 * rng.standard_normal(N)) * 0.4,
                    "ground": normalize(rng.standard_normal(N) * 0.1) * 0.2,
                    "listen": normalize(rng.standard_normal(N) * 0.05),
                }
                guala.tick_once(ev, enable_self_evo=True,
                                coordinator_on=True, introspection_on=True)
            tok, conf = emit_token(guala, vocab, target_class=slot_class)
            if tok is not None:
                response.append({"token": tok, "class": slot_class})
                response_classes.append(slot_class)
            token_sec = guala.sections["token"]
            kick = random_unit_complex(N, rng) * 0.5
            token_sec.psi = normalize(token_sec.psi + kick)
    else:
        # NO LEARNED TEMPLATE — let substrate find its own response
        token_sec = guala.sections["token"]
        speak_attempts = 0
        max_emissions = 3
        recent = (guala.external_speaker_buffer[-1]["vec"]
                  if guala.external_speaker_buffer else None)
        for _ in range(30):
            if speak_attempts >= max_emissions:
                break
            if recent is not None:
                ev = {
                    "token": normalize(recent * 0.3 + rng.standard_normal(N) * 0.1),
                    "class": normalize(recent * 0.3 + rng.standard_normal(N) * 0.1),
                    "role": normalize(rng.standard_normal(N) * 0.1),
                    "partner": normalize(recent * 0.3),
                    "ground": normalize(rng.standard_normal(N) * 0.1),
                    "listen": normalize(rng.standard_normal(N) * 0.05),
                }
            else:
                ev = {nm: normalize(rng.standard_normal(N) * 0.1)
                      for nm in ["token", "class", "role", "partner", "ground", "listen"]}
            commits = guala.tick_once(ev, enable_self_evo=True,
                                      coordinator_on=True, introspection_on=True)
            token_commits = [c for c in commits if c["section"] == "token"]
            if token_commits:
                tok, conf = emit_token(guala, vocab, target_class=None)
                if tok is not None:
                    cls = vocab.token_class.get(tok, "?")
                    response.append({"token": tok, "class": cls})
                    response_classes.append(cls)
                    speak_attempts += 1
                    kick = random_unit_complex(N, rng) * 0.5
                    token_sec.psi = normalize(token_sec.psi + kick)

        # IMMEDIATE LEARNING: promote this pattern to a template
        if response_classes:
            learned = learn_pattern_immediately(
                vocab.response_templates, last_class, response_classes)
            if learned:
                growth_events.append(
                    f"learned template: {last_class} -> {response_classes}")

    memory.add_turn("guala", [r["token"] for r in response], response_classes)
    cls_after, _ = read_intro(guala, vocab)
    intro_log.append(("after", cls_after))

    return response, intro_log, response_classes, growth_events
