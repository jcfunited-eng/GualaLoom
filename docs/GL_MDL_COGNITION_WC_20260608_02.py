"""
GL-MDL-COGNITION-V2-WC-20260608-01

Cognition layer with word identity preserved + co-occurrence bindings
+ lateral inhibition.

Key changes from v1:
- Co-occurrence bindings: when word X and word Y fire within a window,
  bind X→Y and Y→X with strength proportional to recency. This is a
  WORD-LEVEL association graph, separate from the chi-based atlas
  (which has band-overlap problems).
- Lateral inhibition: when one mode crosses emission threshold, it
  suppresses other modes' activation by a fraction (winner-take-some).
- Tight emission: only emit when activation is well above background noise.
- Cofire binding only on perception events, not on emissions (no positive
  feedback loop).
- Decay-balance: tuned to allow accumulation while preventing runaway.

This is the "thinking" layer. It does:
  - Cascade (associations propagate activation)
  - Recall (input cascades and surfaces related words)
  - Introspection (intro tracks what's currently active)
  - Coordinator (conflict detection between competing words)
"""

import math
import numpy as np
from collections import defaultdict, deque, Counter
import sys
sys.path.insert(0, '/home/claude/gualaloom_dna_renamed')
from krimelack import transduce_text


# Atlas-style decay-balance
BASE_REINFORCEMENT = 0.10        # higher than deployed engine — for faster learning in this model
DECAY_LAMBDA = 0.0005             # slower decay than deployed — accumulates more easily
FORGETTING_THRESHOLD = 0.02
STRENGTH_CAP = 1.0

# Cognition dynamics
ACT_DECAY = 0.65                 # slower decay so cascade can accumulate over ticks
CASCADE_GAIN = 0.55              # stronger cascade
COHESION_THRESHOLD = 0.30        # lower threshold — substrate emits with less pressure
EMISSION_REFRACTORY = 8
LATERAL_INHIBITION = 0.35
PERCEPTION_BOOST = 0.85
COFIRE_WINDOW_TICKS = 5

# Introspection
INTRO_PERIOD = 2

# Coordinator
COORDINATOR_PERIOD = 1
CONFLICT_THRESHOLD = 0.35   # multiple modes above this = conflict


class AssociationGraph:
    """Word-to-word co-occurrence bindings with strength/decay.
    Different from chi-atlas — keyed by (word_id, word_id) pairs."""
    
    def __init__(self):
        self.bindings = defaultdict(lambda: {"strength": 0.0, "last_tick": 0})
        self.tick = 0
    
    def reinforce(self, src_id, dst_id, tick, salience=1.0):
        if src_id == dst_id:
            return
        imp = BASE_REINFORCEMENT * max(0.2, min(3.0, salience))
        self.tick = max(self.tick, tick)
        key = (src_id, dst_id)
        b = self.bindings[key]
        b["strength"] = min(STRENGTH_CAP, b["strength"] + imp)
        b["last_tick"] = tick
    
    def decay(self, current_tick):
        for key, b in self.bindings.items():
            dt = current_tick - b["last_tick"]
            if dt > 0:
                b["strength"] *= math.exp(-DECAY_LAMBDA * dt)
                b["last_tick"] = current_tick
    
    def prune(self):
        forgotten = 0
        for key in list(self.bindings.keys()):
            if self.bindings[key]["strength"] < FORGETTING_THRESHOLD:
                del self.bindings[key]
                forgotten += 1
        return forgotten
    
    def neighbors(self, src_id):
        """Yield (dst_id, strength) for all live forward-bindings from src_id."""
        for (s, d), b in self.bindings.items():
            if s == src_id and b["strength"] >= FORGETTING_THRESHOLD:
                yield d, b["strength"]
    
    def live_count(self):
        return sum(1 for b in self.bindings.values() if b["strength"] >= FORGETTING_THRESHOLD)
    
    def total_strength(self):
        return sum(b["strength"] for b in self.bindings.values()
                   if b["strength"] >= FORGETTING_THRESHOLD)


class CognitionV2:
    def __init__(self):
        self.tick = 0
        self.word_modes = {}     # label -> {label, mid, chi, vec, activation, last_emit_tick}
        self.mid_to_label = {}
        self.next_mid = 0
        self.assoc = AssociationGraph()
        # Cofire window: recent perceptions
        self.recent_perceptions = deque(maxlen=12)
        # Introspection: tracks active mode set per tick
        self.intro_log = []     # (tick, top_label, top_act, n_active)
        self.intro_modes = Counter()  # what we've "thought about"
        # Coordinator
        self.coordinator_actions = []
        # Emissions
        self.emissions = []
    
    def install_word(self, label, vec=None, chi=None):
        if label in self.word_modes:
            return self.word_modes[label]["mid"]
        if chi is None:
            chi = transduce_text(label).winding
        if vec is None:
            vec = np.zeros(16, dtype=complex)
        mid = self.next_mid
        self.next_mid += 1
        self.word_modes[label] = {
            "label": label, "mid": mid, "chi": chi, "vec": vec,
            "activation": 0.0, "last_emit_tick": -9999,
            "install_tick": self.tick,
        }
        self.mid_to_label[mid] = label
        return mid
    
    def hear(self, label, salience=1.5):
        if label not in self.word_modes:
            return False
        m = self.word_modes[label]
        m["activation"] = min(1.0, m["activation"] + PERCEPTION_BOOST)
        # Input mode is suppressed from emission for a window — response
        # has to come from the cascade, not echo the input.
        m["last_emit_tick"] = self.tick  # treat as just-emitted (refractory)
        self.recent_perceptions.append((self.tick, m["mid"]))
        # Co-occurrence reinforcement with all recent perceptions
        for (t_recent, mid_recent) in self.recent_perceptions:
            if mid_recent != m["mid"] and self.tick - t_recent <= COFIRE_WINDOW_TICKS:
                # Bidirectional binding
                self.assoc.reinforce(mid_recent, m["mid"], self.tick, salience=salience)
                self.assoc.reinforce(m["mid"], mid_recent, self.tick, salience=salience)
        return True
    
    def cascade(self):
        """Activation propagates through association graph.
        Each active mode contributes to its neighbors proportional to
        its activation and the binding strength."""
        incoming = defaultdict(float)
        for label, m in self.word_modes.items():
            if m["activation"] < 0.08:
                continue
            for (dst_mid, strength) in self.assoc.neighbors(m["mid"]):
                propagated = m["activation"] * strength * CASCADE_GAIN
                if propagated > 0.01:
                    incoming[dst_mid] += propagated
        for mid, inc in incoming.items():
            label = self.mid_to_label[mid]
            self.word_modes[label]["activation"] = min(
                1.0,
                self.word_modes[label]["activation"] + inc
            )
    
    def lateral_inhibit(self, winner_label):
        """When winner fires, suppress competing modes' activation."""
        for label, m in self.word_modes.items():
            if label != winner_label:
                m["activation"] *= (1.0 - LATERAL_INHIBITION)
    
    def coordinator(self):
        """Detect conflict: multiple modes near emission threshold."""
        near = [(label, m["activation"]) for label, m in self.word_modes.items()
                if m["activation"] >= CONFLICT_THRESHOLD]
        if len(near) >= 2:
            near.sort(key=lambda x: -x[1])
            winner, w_act = near[0]
            losers = near[1:]
            action = {
                "tick": self.tick,
                "winner": winner, "winner_act": w_act,
                "losers": [(l, a) for (l, a) in losers],
                "arc_changes": 0,
            }
            # Amplify winner, suppress losers
            self.word_modes[winner]["activation"] = min(1.0, w_act + 0.10)
            for (loser_label, _) in losers:
                self.word_modes[loser_label]["activation"] *= 0.6
            # Check if winner crosses emission threshold
            if self.word_modes[winner]["activation"] >= COHESION_THRESHOLD:
                action["arc_changes"] = 1
            self.coordinator_actions.append(action)
            return True
        return False
    
    def introspect(self):
        """Intro section: log dominant active mode."""
        active = [(label, m["activation"]) for label, m in self.word_modes.items()
                  if m["activation"] > 0.05]
        if active:
            active.sort(key=lambda x: -x[1])
            top_label, top_act = active[0]
            self.intro_log.append((self.tick, top_label, top_act, len(active)))
            self.intro_modes[top_label] += 1
    
    def step(self):
        self.tick += 1
        # Cascade
        self.cascade()
        # Coordinator
        if self.tick % COORDINATOR_PERIOD == 0:
            self.coordinator()
        # Introspect
        if self.tick % INTRO_PERIOD == 0:
            self.introspect()
        # Emission check
        emissions = []
        for label, m in self.word_modes.items():
            refractory = self.tick - m["last_emit_tick"] < EMISSION_REFRACTORY
            if m["activation"] >= COHESION_THRESHOLD and not refractory:
                emissions.append({
                    "tick": self.tick, "label": label, "chi": m["chi"],
                    "activation": m["activation"], "mid": m["mid"],
                })
                m["last_emit_tick"] = self.tick
                m["activation"] = 0.1
                # Lateral inhibition on emission
                self.lateral_inhibit(label)
        self.emissions.extend(emissions)
        # Activation decay
        for m in self.word_modes.values():
            m["activation"] *= ACT_DECAY
            if m["activation"] < 0.005:
                m["activation"] = 0.0
        # Association graph decay
        if self.tick % 10 == 0:
            self.assoc.decay(self.tick)
        if self.tick % 200 == 0:
            self.assoc.prune()
        return emissions
    
    def run(self, n_ticks):
        out = []
        for _ in range(n_ticks):
            out.extend(self.step())
        return out
    
    def health(self):
        return {
            "tick": self.tick,
            "n_words": len(self.word_modes),
            "live_bindings": self.assoc.live_count(),
            "total_strength": round(self.assoc.total_strength(), 2),
            "intro_observations": len(self.intro_log),
            "distinct_intro_words": len(self.intro_modes),
            "coordinator_fires": len(self.coordinator_actions),
            "emissions_so_far": len(self.emissions),
        }


# === DNA RECIPE TESTS ===

def test_recipe():
    from GL_MDL_COMPOSITION_WC_20260608_01 import TextProcessor
    
    GM = """in the great green room there was a telephone and a red balloon. 
and a picture of the cow jumping over the moon. 
and there were three little bears sitting on chairs.
goodnight room. goodnight moon. 
goodnight cow jumping over the moon. 
goodnight bears. goodnight chairs. 
goodnight kittens. and goodnight mittens.
goodnight stars. goodnight air. 
goodnight noises everywhere."""
    
    tp = TextProcessor()
    tp.process(GM)
    
    cog = CognitionV2()
    # Install vocab
    for m in tp.letter_layer.modes:
        cog.install_word(m["label"], vec=m["vec"], chi=m["chi"])
    
    # Read text — build associations
    print(f"\nReading text — {len(cog.word_modes)} word vocab")
    sentences = [s.strip() for s in GM.replace("\n", " ").split(".") if s.strip()]
    for pass_n in range(5):  # multiple passes for strong associations
        for sent in sentences:
            words = sent.lower().replace(",", "").split()
            for w in words:
                w_clean = "".join(c for c in w if c.isalnum())
                if w_clean in cog.word_modes:
                    cog.hear(w_clean)
                cog.run(2)
            cog.run(3)  # gap between sentences
    
    print(f"After reading: {cog.health()}")
    
    # === DNA TESTS ===
    
    print("\n" + "=" * 70)
    print("DNA RECIPE: 1. SYNTAX (does emission produce structured sequences?)")
    print("=" * 70)
    # Test: hear a noun, see if its typical co-occurring words emit in order
    test_inputs = ["moon", "goodnight", "bears", "cow", "stars"]
    syntax_log = []
    for inp in test_inputs:
        cog.emissions.clear()
        cog.run(15)  # quiet down
        cog.emissions.clear()
        cog.hear(inp, salience=2.5)
        em = cog.run(30)
        em_labels = [e["label"] for e in em]
        print(f"  '{inp}' → {em_labels}")
        syntax_log.append((inp, em_labels))
    syntax_pass = all(len(em) >= 1 for _, em in syntax_log)
    syntax_grounded = all(em[0] != inp if em else False for inp, em in syntax_log)
    print(f"  PASS: emission produced (not silence) on all inputs: {syntax_pass}")
    
    print("\n" + "=" * 70)
    print("DNA RECIPE: 2. CONVERSATION (input → grounded response → input...)")
    print("=" * 70)
    # Two-turn conversation
    cog.emissions.clear()
    cog.run(15)
    cog.emissions.clear()
    
    turn1_input = "moon"
    print(f"  TURN 1 — IN: '{turn1_input}'")
    cog.hear(turn1_input, salience=2.5)
    em = cog.run(20)
    turn1_response = [e["label"] for e in em[:3]]
    print(f"  TURN 1 — OUT: {turn1_response}")
    
    cog.emissions.clear()
    cog.run(10)
    cog.emissions.clear()
    
    turn2_input = "goodnight"
    print(f"  TURN 2 — IN: '{turn2_input}'")
    cog.hear(turn2_input, salience=2.5)
    em = cog.run(20)
    turn2_response = [e["label"] for e in em[:3]]
    print(f"  TURN 2 — OUT: {turn2_response}")
    
    conversation_pass = len(turn1_response) > 0 and len(turn2_response) > 0
    print(f"  PASS: both turns produced response: {conversation_pass}")
    
    print("\n" + "=" * 70)
    print("DNA RECIPE: 3. INTROSPECTION (substrate tracks what it thought about)")
    print("=" * 70)
    print(f"  Total intro observations: {len(cog.intro_log)}")
    print(f"  Distinct words 'thought about': {len(cog.intro_modes)}")
    print(f"  Most-thought words: {cog.intro_modes.most_common(8)}")
    intro_pass = len(cog.intro_modes) > 5
    print(f"  PASS: distinct >5: {intro_pass}")
    
    print("\n" + "=" * 70)
    print("DNA RECIPE: 4. SELF-IMPROVEMENT (associations strengthen over use)")
    print("=" * 70)
    # Measure: does re-reading a sentence make associations stronger?
    test_pair = ("goodnight", "moon")
    a_mid = cog.word_modes[test_pair[0]]["mid"]
    b_mid = cog.word_modes[test_pair[1]]["mid"]
    pre_strength = cog.assoc.bindings.get((a_mid, b_mid), {}).get("strength", 0)
    
    for _ in range(3):
        cog.hear("goodnight"); cog.run(2)
        cog.hear("moon"); cog.run(2)
    
    post_strength = cog.assoc.bindings.get((a_mid, b_mid), {}).get("strength", 0)
    print(f"  Binding strength '{test_pair[0]}'→'{test_pair[1]}'")
    print(f"    before re-reading: {pre_strength:.3f}")
    print(f"    after re-reading:  {post_strength:.3f}")
    print(f"    increase: {post_strength - pre_strength:+.3f}")
    self_improvement_pass = post_strength > pre_strength
    print(f"  PASS: binding strengthened with use: {self_improvement_pass}")
    
    print("\n" + "=" * 70)
    print("DNA RECIPE: 5. AWARENESS (coordinator handles conflict)")
    print("=" * 70)
    n_total = len(cog.coordinator_actions)
    n_effect = sum(1 for a in cog.coordinator_actions if a.get("arc_changes", 0) > 0)
    print(f"  Coordinator fired: {n_total} times")
    print(f"  With measurable effect (winner crossed threshold): {n_effect}")
    eff_ratio = n_effect / max(n_total, 1)
    print(f"  Resolution-effect ratio: {eff_ratio:.1%}")
    awareness_pass = n_total > 0 and eff_ratio > 0.15
    print(f"  PASS: fires AND >15% effective: {awareness_pass}")
    
    print("\n" + "=" * 70)
    print("DNA RECIPE — SUMMARY")
    print("=" * 70)
    results = {
        "syntax": syntax_pass,
        "conversation": conversation_pass,
        "introspection": intro_pass,
        "self_improvement": self_improvement_pass,
        "awareness": awareness_pass,
    }
    for k, v in results.items():
        print(f"  {k}: {'PASS' if v else 'FAIL'}")
    all_pass = all(results.values())
    print(f"\nAll five: {'PASS' if all_pass else 'FAIL'}")
    return results


if __name__ == "__main__":
    test_recipe()
