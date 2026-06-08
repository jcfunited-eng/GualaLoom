"""
GL-MDL-MULTIMODAL-V3-DEEP-WC-20260608-01

Multimodal cognition with full depth on all five senses + folded chi +
bidirectional MGN (bottom-up perception + top-down expectation).

Compared to v2:
- Visual: V1 multi-scale bank + V2 contour + V4 color + LOC (in visual_depth.py)
- Touch: 4 mechanoreceptor types + S1 integration  
- Taste: 5 receptor channels + insular integration
- Smell: 8 olfactory channels + piriform integration
- Audio: cochlea + onset/sustained + A1 (unchanged from v2)
- Folded 4D chi atlas (unchanged from v2)
- Top-down MGN: coordinator's prior decisions bias sensory expectations
- Balanced training: each sensory word gets equal reinforcement
"""

import math
import sys
import numpy as np
from collections import defaultdict, deque, Counter

sys.path.insert(0, '/home/claude/gualaloom_dna_renamed')
sys.path.insert(0, '/home/claude/gualaloom_dna_renamed/senses')
sys.path.insert(0, '/home/claude/gualaloom_dna_renamed')

from krimelack import transduce_text
from GL_MDL_FOLDED_CHI_WC_20260608_01 import (folded_chi_text, folded_chi_visual, folded_chi_audio,
                         folded_chi_distance, chi_neighbors)
from GL_MDL_VISUAL_DEPTH_WC_20260608_01 import visual_deep_for, ORIENTATION_FILTERS
from GL_MDL_AUDITORY_CORTEX_WC_20260608_01 import cochlear_transduce, onset_stream, sustained_stream, a1_signature
from GL_MDL_SOMATOSENSORY_WC_20260608_01 import touch_deep_for, taste_deep_for, smell_deep_for


BASE_REINFORCEMENT = 0.10
DECAY_LAMBDA = 0.0005
FORGETTING_THRESHOLD = 0.02
STRENGTH_CAP = 1.0

ACT_DECAY = 0.55
CASCADE_GAIN = 0.30
COHESION_THRESHOLD = 0.30
EMISSION_REFRACTORY = 8
LATERAL_INHIBITION = 0.35
PERCEPTION_BOOST = 0.95
COFIRE_WINDOW_TICKS = 6

MGN_FOCUS_BOOST = 1.5     # was 2.0 — softer to reduce feedback runaway
MGN_OFF_FOCUS_SUPPRESS = 0.5  # was 0.4 — less aggressive suppression
TOP_DOWN_BOOST = 1.0      # disabled — was 1.5, but caused feedback loop with MGN

CHI_NEIGHBORHOOD_L1 = 1

MODAL_SECTIONS = ["word", "visual", "audio", "touch", "taste", "smell"]


def normalize(v):
    nrm = np.linalg.norm(v)
    return v if nrm < 1e-12 else v / nrm


class FoldedAtlas:
    def __init__(self):
        self.entries = defaultdict(list)
        self.tick = 0
    
    def record(self, section, motif, chi_vec, tick, salience=1.0):
        imp = BASE_REINFORCEMENT * max(0.2, min(3.0, salience))
        self.tick = max(self.tick, tick)
        chi_t = tuple(chi_vec)
        found = None
        for e in self.entries[chi_t]:
            if e["section"] == section and e["motif"] == motif:
                found = e
                break
        if found:
            found["strength"] = min(STRENGTH_CAP, found["strength"] + imp)
            found["last_tick"] = tick
        else:
            self.entries[chi_t].append({
                "section": section, "motif": motif, "chi": chi_t,
                "strength": min(STRENGTH_CAP, imp),
                "last_tick": tick, "born_tick": tick,
            })
    
    def at_chi(self, chi_vec, neighborhood=CHI_NEIGHBORHOOD_L1,
               exclude_section=None, exclude_motif=None):
        out = []
        for nb_chi in chi_neighbors(chi_vec, max_distance=neighborhood):
            for e in self.entries.get(nb_chi, []):
                if e["strength"] < FORGETTING_THRESHOLD:
                    continue
                if exclude_section and e["section"] == exclude_section and e["motif"] == exclude_motif:
                    continue
                out.append(e)
        return out
    
    def decay(self, tick):
        for entries in self.entries.values():
            for e in entries:
                dt = tick - e["last_tick"]
                if dt > 0:
                    e["strength"] *= math.exp(-DECAY_LAMBDA * dt)
                    e["last_tick"] = tick
    
    def prune(self):
        for chi_t in list(self.entries.keys()):
            survivors = [e for e in self.entries[chi_t] if e["strength"] >= FORGETTING_THRESHOLD]
            if survivors:
                self.entries[chi_t] = survivors
            else:
                del self.entries[chi_t]
    
    def live_count(self):
        return sum(1 for es in self.entries.values()
                   for e in es if e["strength"] >= FORGETTING_THRESHOLD)


def audio_deep_for(name):
    """Audio with folded chi from cochlear→CN→A1."""
    if name == "moon":
        n = 400; t = np.arange(n) / 200
        sig = 0.1 * np.sin(2 * math.pi * 8 * t) + 0.03 * np.sin(2 * math.pi * 16 * t)
    elif name == "cow":
        n = 400; t = np.arange(n) / 200
        sig = (0.8 * np.sin(2 * math.pi * 18 * t) + 0.4 * np.sin(2 * math.pi * 36 * t) +
               0.2 * np.sin(2 * math.pi * 54 * t))
        sig *= np.exp(-t * 0.5)
    elif name == "bears":
        n = 400; t = np.arange(n) / 200
        rng = np.random.default_rng(10)
        sig = 0.6 * np.sin(2 * math.pi * 8 * t) + 0.3 * np.sin(2 * math.pi * 18 * t)
        for _ in range(8):
            f = 35 + rng.standard_normal() * 10
            sig += 0.1 * np.sin(2 * math.pi * f * t + rng.uniform(0, 2 * math.pi))
    elif name == "stars":
        n = 400; t = np.arange(n) / 200
        sig = 0.5 * np.sin(2 * math.pi * 75 * t) + 0.4 * np.sin(2 * math.pi * 92 * t)
        sig *= np.exp(-t * 0.4)
    elif name == "kittens":
        n = 400; t = np.arange(n) / 200
        carrier = np.sin(2 * math.pi * 55 * t)
        env = (1 + np.sin(2 * math.pi * 8 * t)) / 2
        sig = carrier * env * 0.5
    elif name == "room":
        rng = np.random.default_rng(20)
        n = 400; t = np.arange(n) / 200
        sig = np.zeros(n)
        for f in [8, 12, 18, 25]:
            sig += 0.1 * np.sin(2 * math.pi * f * t + rng.uniform(0, 2 * math.pi))
    else:
        return None
    
    cochlear = cochlear_transduce(sig, sample_rate=200)
    onsets = onset_stream(cochlear)
    sustained = sustained_stream(cochlear)
    a1 = a1_signature(cochlear, onsets, sustained)
    a1["chi_folded"] = folded_chi_audio(cochlear, onsets, sustained, a1)
    a1["modality"] = "audio"
    return a1


def deep_bundle_for(name):
    """Build full deep multi-modal bundle with folded chi for all percepts."""
    bundle = {}
    v = visual_deep_for(name)
    if v is not None:
        # Build folded chi for deep visual from v1, v2, v4 stages
        v1 = v.get("v1", {})
        v2 = v.get("v2", {})
        v4 = v.get("v4", {})
        v1_total = sum(abs(w) for w in v1.values()) // 200
        v2_total = sum(abs(w) for w in v2.values()) // 1000
        v4_total = sum(abs(w) for w in v4.values()) // 100
        loc_chi = v.get("chi", 0)
        v["chi_folded"] = (int(v1_total), int(v2_total), int(v4_total), int(loc_chi))
        bundle["visual"] = v
    a = audio_deep_for(name)
    if a is not None:
        bundle["audio"] = a
    t = touch_deep_for(name)
    if t is not None:
        bundle["touch"] = t
    ta = taste_deep_for(name)
    if ta is not None:
        bundle["taste"] = ta
    sm = smell_deep_for(name)
    if sm is not None:
        bundle["smell"] = sm
    return bundle


class DeepMultiModalCognition:
    def __init__(self):
        self.tick = 0
        self.atlas = FoldedAtlas()
        self.sections = {s: {} for s in MODAL_SECTIONS}
        self.section_mid_to_label = {s: {} for s in MODAL_SECTIONS}
        self.next_mid = {s: 0 for s in MODAL_SECTIONS}
        self.recent_perceptions = deque(maxlen=20)
        self.emissions = []
        self.intro_log = []
        self.intro_top = Counter()
        self.coordinator_actions = []
        self.attention_focus = None
        self.expectation = None  # top-down — what cortex expects to perceive next
        self.ATTENTION_PERSIST_TICKS = 20
        self.EXPECTATION_PERSIST_TICKS = 10
    
    def install_mode(self, section, label, chi_folded, state=None):
        if label in self.sections[section]:
            return self.sections[section][label]["mid"]
        mid = self.next_mid[section]
        self.next_mid[section] += 1
        self.sections[section][label] = {
            "label": label, "mid": mid, "chi": tuple(chi_folded),
            "state": state if state is not None else np.zeros(16, dtype=complex),
            "activation": 0.0, "last_emit_tick": -9999,
            "install_tick": self.tick,
        }
        self.section_mid_to_label[section][mid] = label
        return mid
    
    def install_word(self, label):
        chi_v = folded_chi_text(label)
        from GL_MDL_COMPOSITION_WC_20260608_01 import TextProcessor
        tp = TextProcessor()
        tp.process(label)
        word_state = None
        for m in tp.letter_layer.modes:
            if m["label"] == label:
                word_state = m["vec"]
                break
        if word_state is None:
            word_state = np.zeros(16, dtype=complex)
        self.install_mode("word", label, chi_v, state=word_state)
        bundle = deep_bundle_for(label)
        for modality in ["visual", "audio", "touch", "taste", "smell"]:
            p = bundle.get(modality)
            if p is not None and "chi_folded" in p:
                modal_label = f"{label}__{modality}"
                self.install_mode(modality, modal_label, p["chi_folded"], state=p["state"])
    
    def fire(self, section, label, salience=1.5, set_focus=True):
        if label not in self.sections[section]:
            return False
        m = self.sections[section][label]
        m["activation"] = min(1.0, m["activation"] + PERCEPTION_BOOST)
        m["last_emit_tick"] = self.tick
        self.recent_perceptions.append((self.tick, section, m["mid"], m["chi"]))
        self.atlas.record(section, m["mid"], m["chi"], self.tick, salience=salience)
        if set_focus:
            self.attention_focus = (section, m["mid"], self.tick)
        return True
    
    def cofire_bind(self):
        recent = [(t, s, mid, chi) for (t, s, mid, chi) in self.recent_perceptions
                  if self.tick - t < COFIRE_WINDOW_TICKS]
        for i, (t1, s1, mid1, chi1) in enumerate(recent):
            for (t2, s2, mid2, chi2) in recent[i+1:]:
                if s1 == s2 and mid1 == mid2:
                    continue
                age = min(self.tick - t1, self.tick - t2)
                sal = max(0.3, 1.5 * (1.0 - age / COFIRE_WINDOW_TICKS))
                self.atlas.record(s1, mid1, chi2, self.tick, salience=sal)
                self.atlas.record(s2, mid2, chi1, self.tick, salience=sal)
    
    def cascade(self):
        incoming = defaultdict(float)
        for section, modes in self.sections.items():
            for label, m in modes.items():
                if m["activation"] < 0.08:
                    continue
                src_state = m.get("state")
                neighbors = self.atlas.at_chi(m["chi"], exclude_section=section, exclude_motif=m["mid"])
                for e in neighbors:
                    weight = 1.0
                    if e["section"] == section and src_state is not None:
                        target_label = self.section_mid_to_label[e["section"]].get(e["motif"])
                        if target_label:
                            target_state = self.sections[e["section"]][target_label].get("state")
                            if (target_state is not None and np.linalg.norm(target_state) > 1e-9
                                    and np.linalg.norm(src_state) > 1e-9):
                                weight = float(np.abs(np.vdot(src_state, target_state))**2)
                    propagated = m["activation"] * e["strength"] * CASCADE_GAIN * weight
                    if propagated > 0.01:
                        incoming[(e["section"], e["motif"])] += propagated
        for (sec, mid), inc in incoming.items():
            label = self.section_mid_to_label[sec].get(mid)
            if label and label in self.sections[sec]:
                m = self.sections[sec][label]
                m["activation"] = min(1.0, m["activation"] + inc)
    
    def mgn_gate(self):
        """Bottom-up MGN: amplify partners of current attention focus."""
        if self.attention_focus is None:
            return
        focus_sec, focus_mid, set_tick = self.attention_focus
        if self.tick - set_tick > self.ATTENTION_PERSIST_TICKS:
            self.attention_focus = None
            return
        focus_label = self.section_mid_to_label[focus_sec].get(focus_mid)
        if focus_label is None:
            return
        focus_m = self.sections[focus_sec][focus_label]
        focus_chi = focus_m["chi"]
        
        MIN_STRONG = 0.4
        partner_mids = set()
        for entry in self.atlas.at_chi(focus_chi):
            if entry["strength"] >= MIN_STRONG:
                partner_mids.add((entry["section"], entry["motif"]))
        for chi_t, entries in self.atlas.entries.items():
            focus_strong_here = any(
                (e["section"] == focus_sec and e["motif"] == focus_mid
                 and e["strength"] >= MIN_STRONG) for e in entries)
            if focus_strong_here:
                for e in entries:
                    if e["strength"] >= MIN_STRONG:
                        partner_mids.add((e["section"], e["motif"]))
        
        for section, modes in self.sections.items():
            for label, m in modes.items():
                mid_key = (section, m["mid"])
                if mid_key == (focus_sec, focus_mid):
                    continue
                if mid_key in partner_mids:
                    m["activation"] = min(1.0, m["activation"] * MGN_FOCUS_BOOST)
                else:
                    m["activation"] *= MGN_OFF_FOCUS_SUPPRESS
    
    def top_down_expectation(self):
        """Top-down MGN: coordinator's recent winner sets expectation for
        partner sensory inputs. When expected partners fire, they get boosted."""
        if self.expectation is None:
            return
        exp_sec, exp_mid, set_tick = self.expectation
        if self.tick - set_tick > self.EXPECTATION_PERSIST_TICKS:
            self.expectation = None
            return
        exp_label = self.section_mid_to_label[exp_sec].get(exp_mid)
        if exp_label is None:
            return
        exp_m = self.sections[exp_sec][exp_label]
        exp_chi = exp_m["chi"]
        
        # Find expected partners (similar to MGN partner lookup)
        MIN_STRONG = 0.3
        expected_mids = set()
        for entry in self.atlas.at_chi(exp_chi):
            if entry["strength"] >= MIN_STRONG:
                expected_mids.add((entry["section"], entry["motif"]))
        
        # Boost any expected partner currently above threshold
        for (sec, mid) in expected_mids:
            label = self.section_mid_to_label[sec].get(mid)
            if label:
                m = self.sections[sec][label]
                if m["activation"] > 0.1:
                    m["activation"] = min(1.0, m["activation"] * TOP_DOWN_BOOST)
    
    def coordinator(self):
        near = []
        for section, modes in self.sections.items():
            for label, m in modes.items():
                if m["activation"] >= COHESION_THRESHOLD * 0.8:
                    near.append((section, label, m["activation"]))
        if len(near) >= 2:
            near.sort(key=lambda x: -x[2])
            winner_sec, winner_lab, winner_act = near[0]
            losers = near[1:]
            self.sections[winner_sec][winner_lab]["activation"] = min(1.0, winner_act + 0.10)
            for (s, l, _) in losers:
                self.sections[s][l]["activation"] *= 0.6
            # Set top-down expectation from winner
            winner_m = self.sections[winner_sec][winner_lab]
            self.expectation = (winner_sec, winner_m["mid"], self.tick)
            self.coordinator_actions.append({"tick": self.tick, "winner": (winner_sec, winner_lab)})
    
    def step(self):
        self.tick += 1
        self.cofire_bind()
        self.cascade()
        self.mgn_gate()
        self.top_down_expectation()
        self.coordinator()
        emissions = []
        for section, modes in self.sections.items():
            ready = [(label, m) for label, m in modes.items()
                     if m["activation"] >= COHESION_THRESHOLD
                     and self.tick - m["last_emit_tick"] >= EMISSION_REFRACTORY]
            if not ready:
                continue
            ready.sort(key=lambda x: -x[1]["activation"])
            winner_label, winner_m = ready[0]
            emissions.append({
                "tick": self.tick, "section": section, "label": winner_label,
                "chi": winner_m["chi"], "activation": winner_m["activation"],
                "mid": winner_m["mid"],
            })
            winner_m["last_emit_tick"] = self.tick
            winner_m["activation"] = 0.1
            for other_label, other_m in modes.items():
                if other_label != winner_label:
                    other_m["activation"] *= 0.15
        self.emissions.extend(emissions)
        for modes in self.sections.values():
            for m in modes.values():
                m["activation"] *= ACT_DECAY
                if m["activation"] < 0.005:
                    m["activation"] = 0.0
        if self.tick % 10 == 0:
            self.atlas.decay(self.tick)
        if self.tick % 200 == 0:
            self.atlas.prune()
        return emissions
    
    def run(self, n_ticks):
        out = []
        for _ in range(n_ticks):
            out.extend(self.step())
        return out
    
    def hear_word_with_senses(self, word):
        if word not in self.sections["word"]:
            return False
        self.fire("word", word, salience=2.0)
        for modality in ["visual", "audio", "touch", "taste", "smell"]:
            modal_label = f"{word}__{modality}"
            if modal_label in self.sections[modality]:
                self.fire(modality, modal_label, salience=2.0, set_focus=False)
        return True
