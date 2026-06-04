"""
Conversation transcript: log every utterance and response between A and B.
An 'utterance' = a speak-section commit's mode_id + chi + best-match-template.
"""

import numpy as np
import sys
from collections import defaultdict, Counter
from .assemblage import (
    Section, System, ChiAtlas, N, normalize, random_unit_complex, chi_of
)

def make_projection(n, dim, rng):
    M = rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n))
    Q, _ = np.linalg.qr(M)
    P = np.zeros((n, n), dtype=complex)
    P[:dim, :dim] = np.eye(dim)
    return Q @ P @ Q.conj().T

SEED = 42
rng = np.random.default_rng(SEED)

def build_system(prefix):
    listen = Section(name=f"{prefix}_listen", rng=rng)
    speak = Section(name=f"{prefix}_speak", rng=rng)
    ground = Section(name=f"{prefix}_ground", rng=rng, role="grounded")
    for s in (listen, speak, ground):
        s.map_inject = make_projection(N, 8, rng)
    sys_ = System([listen, speak, ground], rng)
    sys_.grounding_section = ground
    sys_.add_keyhole(f"{prefix}_listen", -2, 8, f"{prefix}_speak", 0.4)
    sys_.add_keyhole(f"{prefix}_speak", -2, 8, f"{prefix}_listen", 0.3)
    return sys_

sys_A = build_system("A")
sys_B = build_system("B")

# Shared "lexicon" - templates the world contains
rng_world = np.random.default_rng(SEED + 1000)
# 4 shared concepts both systems' environments draw from (so they CAN converge if they listen)
shared_templates = [random_unit_complex(N, rng_world) for _ in range(4)]
# Each system also has 1 private concept (its own environment)
private_A = random_unit_complex(N, rng_world)
private_B = random_unit_complex(N, rng_world)

def label_utterance(state, templates_shared, private):
    """Find which concept this utterance is closest to."""
    overlaps_shared = [float(np.abs(np.vdot(t, state))**2) for t in templates_shared]
    overlap_private = float(np.abs(np.vdot(private, state))**2)
    best_shared = max(range(len(overlaps_shared)), key=lambda i: overlaps_shared[i])
    if overlap_private > overlaps_shared[best_shared]:
        return "private", overlap_private
    return f"concept_{best_shared}", overlaps_shared[best_shared]

# Warmup: each system explores its own environment
print("=== WARMUP (each system alone) ===")
for warmup in range(100):
    # 80% shared concept, 20% private
    if warmup % 5 == 0:
        env_a = private_A + 0.1 * rng.standard_normal(N)
    else:
        env_a = shared_templates[warmup % 4] + 0.1 * rng.standard_normal(N)
    if warmup % 5 == 0:
        env_b = private_B + 0.1 * rng.standard_normal(N)
    else:
        env_b = shared_templates[(warmup + 1) % 4] + 0.1 * rng.standard_normal(N)
    g_a = env_a + 0.05 * rng.standard_normal(N)
    g_b = env_b + 0.05 * rng.standard_normal(N)
    # Speak gets a mix of env (what was just heard) for warmup
    sys_A.tick_once({"A_ground": g_a, "A_listen": env_a, "A_speak": env_a},
                    enable_self_evo=False, coordinator_on=True)
    sys_B.tick_once({"B_ground": g_b, "B_listen": env_b, "B_speak": env_b},
                    enable_self_evo=False, coordinator_on=True)

print(f"After warmup: A has {len(sys_A.sections['A_speak'].mode_bank)} speak-modes, "
      f"B has {len(sys_B.sections['B_speak'].mode_bank)} speak-modes")

# Conversation phase - log every speak commit as an utterance
print("\n=== CONVERSATION PHASE ===")
print("(turn-by-turn transcript - each line is a speak-section commit)\n")

transcript = []
T_conv = 400
last_a_speak_tick = -1
last_b_speak_tick = -1

for t in range(T_conv):
    # Each system gets fresh environment input (independent)
    if t % 7 == 0:
        env_a = private_A + 0.12 * rng.standard_normal(N)
    else:
        env_a = shared_templates[t % 4] + 0.12 * rng.standard_normal(N)
    if t % 7 == 3:
        env_b = private_B + 0.12 * rng.standard_normal(N)
    else:
        env_b = shared_templates[(t + 2) % 4] + 0.12 * rng.standard_normal(N)
    g_a = env_a + 0.05 * rng.standard_normal(N)
    g_b = env_b + 0.05 * rng.standard_normal(N)

    # A says to B
    new_a_speaks = [k for k in sys_A.sections["A_speak"].krimelack if k["tick"] > last_a_speak_tick]
    if new_a_speaks:
        utterance = new_a_speaks[-1]["state"]
        sys_B.hear_speaker(utterance, "B_listen", "B_speak")
        last_a_speak_tick = new_a_speaks[-1]["tick"]
        lbl_a, conf = label_utterance(utterance, shared_templates, private_A)
        transcript.append({
            "tick": sys_A.tick, "speaker": "A", "label": lbl_a, "confidence": conf,
            "chi": new_a_speaks[-1]["chi"], "mode_id": new_a_speaks[-1]["mode_id"]
        })
        recent_b = [u for u in transcript if u["speaker"] == "B" and u["tick"] >= sys_A.tick - 8]
        matched = any(u["label"] == lbl_a for u in recent_b[-3:]) if recent_b else False
        sys_A.record_utterance_match(matched)

    new_b_speaks = [k for k in sys_B.sections["B_speak"].krimelack if k["tick"] > last_b_speak_tick]
    if new_b_speaks:
        utterance = new_b_speaks[-1]["state"]
        sys_A.hear_speaker(utterance, "A_listen", "A_speak")
        last_b_speak_tick = new_b_speaks[-1]["tick"]
        lbl_b, conf = label_utterance(utterance, shared_templates, private_B)
        transcript.append({
            "tick": sys_B.tick, "speaker": "B", "label": lbl_b, "confidence": conf,
            "chi": new_b_speaks[-1]["chi"], "mode_id": new_b_speaks[-1]["mode_id"]
        })
        recent_a = [u for u in transcript if u["speaker"] == "A" and u["tick"] >= sys_B.tick - 8]
        matched = any(u["label"] == lbl_b for u in recent_a[-3:]) if recent_a else False
        sys_B.record_utterance_match(matched)

    # Speak input = mix of recent listen commit + recent ground commit + last heard from partner
    # ("what I'm going to say is about what I just heard, what I'm seeing, and what they said")
    def speak_input(sys_, listen_name, ground_name, heard_buffer):
        recent_listen = [k for k in sys_.sections[listen_name].krimelack
                          if k["tick"] >= sys_.tick - 5]
        recent_ground = [k for k in sys_.sections[ground_name].krimelack
                          if k["tick"] >= sys_.tick - 5]
        recent_heard = [h for h in heard_buffer if h["tick"] >= sys_.tick - 8]
        parts = []
        if recent_listen:
            parts.append((0.35, recent_listen[-1]["state"]))
        if recent_ground:
            parts.append((0.25, recent_ground[-1]["state"]))
        if recent_heard:
            # Use partner's most recent utterance as topic seed
            parts.append((0.40, recent_heard[-1]["vec"]))
        if not parts:
            return None
        combined = sum(w * v for w, v in parts)
        return normalize(combined)

    speak_a = speak_input(sys_A, "A_listen", "A_ground", sys_A.external_speaker_buffer)
    speak_b = speak_input(sys_B, "B_listen", "B_ground", sys_B.external_speaker_buffer)

    ev_a_dict = {"A_ground": g_a, "A_listen": env_a}
    if speak_a is not None:
        ev_a_dict["A_speak"] = speak_a
    ev_b_dict = {"B_ground": g_b, "B_listen": env_b}
    if speak_b is not None:
        ev_b_dict["B_speak"] = speak_b

    sys_A.tick_once(ev_a_dict, enable_self_evo=True, coordinator_on=True)
    sys_B.tick_once(ev_b_dict, enable_self_evo=True, coordinator_on=True)

# Print transcript (first 60 utterances)
print(f"Total utterances logged: {len(transcript)}\n")
print(f"{'tick':>5} {'who':>3}  {'concept':<12} {'conf':>6}  {'chi':>4}  {'mode':>4}")
print("-" * 50)
for u in transcript[:60]:
    print(f"{u['tick']:>5} {u['speaker']:>3}  {u['label']:<12} {u['confidence']:>6.2%}  {u['chi']:>4}  {u['mode_id']:>4}")
if len(transcript) > 60:
    print(f"... ({len(transcript) - 60} more)")
print()

# Last 20 utterances - look for convergence at end
print("LAST 20 UTTERANCES:")
print(f"{'tick':>5} {'who':>3}  {'concept':<12} {'conf':>6}  {'chi':>4}  {'mode':>4}")
print("-" * 50)
for u in transcript[-20:]:
    print(f"{u['tick']:>5} {u['speaker']:>3}  {u['label']:<12} {u['confidence']:>6.2%}  {u['chi']:>4}  {u['mode_id']:>4}")

# Analysis: are A and B talking about the same things?
def concept_distribution(transcript, speaker):
    counts = Counter(u["label"] for u in transcript if u["speaker"] == speaker)
    total = sum(counts.values())
    return {k: v / total for k, v in counts.items()} if total else {}

dist_A = concept_distribution(transcript, "A")
dist_B = concept_distribution(transcript, "B")
print(f"\nConcept distribution in A's utterances: {dist_A}")
print(f"Concept distribution in B's utterances: {dist_B}")

# Convergence over time: did the concepts each talks about shift toward each other?
early = transcript[:len(transcript)//3]
late = transcript[-len(transcript)//3:]
def overlap_score(t1, t2):
    a = concept_distribution(t1, "A")
    b = concept_distribution(t2, "B")
    keys = set(a) | set(b)
    return sum(min(a.get(k, 0), b.get(k, 0)) for k in keys)

early_overlap = overlap_score(early, early)
late_overlap = overlap_score(late, late)
print(f"\nConcept overlap A-B early: {early_overlap:.2%}")
print(f"Concept overlap A-B late:  {late_overlap:.2%}")

# Turn-by-turn: after A says X, does B respond with X (mimicry/convergence)?
matched_turns = 0
total_turns = 0
for i in range(1, len(transcript)):
    if transcript[i]["speaker"] != transcript[i-1]["speaker"]:
        total_turns += 1
        if transcript[i]["label"] == transcript[i-1]["label"]:
            matched_turns += 1
print(f"\nTurn-following (responder uses same concept label as previous speaker): {matched_turns}/{total_turns} = {matched_turns/max(total_turns,1):.2%}")
print(f"Random baseline (5 labels): {1/5:.2%}")

# Better metric: VECTOR-LEVEL response similarity. Did B's response state actually overlap
# with A's previous utterance state vector?
# To compute we need the state vectors, which we have via mode_bank lookup
def utterance_state(speaker_sys, u):
    sec = speaker_sys.sections[f"{u['speaker']}_speak"]
    if u["mode_id"] < len(sec.mode_bank):
        return sec.mode_bank[u["mode_id"]]
    return None

overlaps_responses = []
for i in range(1, len(transcript)):
    if transcript[i]["speaker"] != transcript[i-1]["speaker"]:
        u_prev = transcript[i-1]
        u_curr = transcript[i]
        prev_sys = sys_A if u_prev["speaker"] == "A" else sys_B
        curr_sys = sys_A if u_curr["speaker"] == "A" else sys_B
        v_prev = utterance_state(prev_sys, u_prev)
        v_curr = utterance_state(curr_sys, u_curr)
        if v_prev is not None and v_curr is not None:
            overlap = float(np.abs(np.vdot(v_prev, v_curr)) ** 2)
            overlaps_responses.append(overlap)

if overlaps_responses:
    mean_response_overlap = float(np.mean(overlaps_responses))
    # Compare to random baseline: overlap between random pairs from each system's bank
    random_overlaps = []
    for _ in range(200):
        i_a = rng.integers(0, max(1, len(sys_A.sections["A_speak"].mode_bank)))
        i_b = rng.integers(0, max(1, len(sys_B.sections["B_speak"].mode_bank)))
        ma = sys_A.sections["A_speak"].mode_bank[i_a] if i_a < len(sys_A.sections["A_speak"].mode_bank) else None
        mb = sys_B.sections["B_speak"].mode_bank[i_b] if i_b < len(sys_B.sections["B_speak"].mode_bank) else None
        if ma is not None and mb is not None:
            random_overlaps.append(float(np.abs(np.vdot(ma, mb)) ** 2))
    mean_random_overlap = float(np.mean(random_overlaps)) if random_overlaps else 0.0
    print(f"\nVector-level response overlap (B's reply to A): {mean_response_overlap:.2%}")
    print(f"Random pair baseline (any A-mode vs any B-mode): {mean_random_overlap:.2%}")
    print(f"Ratio: {mean_response_overlap / max(mean_random_overlap, 0.001):.2f}x baseline")

    # Time evolution of response overlap
    third = len(overlaps_responses) // 3
    early_ovr = float(np.mean(overlaps_responses[:third])) if third else 0
    late_ovr = float(np.mean(overlaps_responses[-third:])) if third else 0
    print(f"Response overlap early: {early_ovr:.2%}, late: {late_ovr:.2%}")

# Save transcript
import json
import os
_out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "..", "..", "..", "experiments", "exp07")
os.makedirs(_out_dir, exist_ok=True)
with open(os.path.join(_out_dir, "conversation_transcript.json"), "w") as f:
    json.dump({
        "transcript": transcript,
        "concept_dist_A": dist_A,
        "concept_dist_B": dist_B,
        "turn_following_rate": matched_turns/max(total_turns,1),
        "n_utterances": len(transcript)
    }, f, indent=2, default=str)
print("\nSaved: conversation_transcript.json")
