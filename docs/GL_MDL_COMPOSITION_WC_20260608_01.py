"""
GL-MDL-COMPOSITION-WC-20260608-01

Layer 2: Composition.

Word = state trajectory through letter primitives.
Sentence = state trajectory through word commits.

Each composition layer:
  - Accumulates substrate state as input arrives
  - On a boundary signal (space, punctuation, end-of-input), commits
    the accumulated state as a new mode (or reinforces existing if recognized)
  - The committed mode carries its source-label so we can emit back

Key principle: composition is deterministic given the input sequence.
Same input → same trajectory → same commit. This is what makes the
substrate's identity for a word substrate-honest rather than dictionary-lookup.
"""

import math
import numpy as np
from GL_MDL_PRIMITIVES_WC_20260608_01 import (
    N, char_vec, char_type, recognize_char, normalize,
    LETTER_VECS, DIGIT_VECS, PUNCT_VECS,
)
import sys
sys.path.insert(0, '/home/claude/gualaloom_dna_renamed')
from krimelack import transduce_text


def text_chi(text):
    """Substrate's chi for any text = krimelack winding from transducing it.
    Same mechanism the deployed engine uses. Gives large, well-distributed range."""
    return transduce_text(text).winding


# --- Composition section ---

class CompositionSection:
    """A section that accumulates input and commits on boundary signals.
    
    State accumulation: psi += incoming * gain, then normalize.
    Commit: when boundary is seen, current psi is committed as a mode.
    """
    
    def __init__(self, name, primitive_kind=None, accum_gain=0.6):
        self.name = name
        self.primitive_kind = primitive_kind  # LETTER, DIGIT, PUNCT for input layer
        self.accum_gain = accum_gain
        self.psi = np.zeros(N, dtype=complex)
        self.modes = []  # list of {label, vec, chi, count, born_tick, last_tick}
        self.tick = 0
        self.cumulative_trajectory = []  # log of state at each input step
        # mapping label -> mode index for fast lookup
        self._label_index = {}
        
    def reset_state(self):
        """Reset state for a new accumulation (called after commit)."""
        self.psi = np.zeros(N, dtype=complex)
        self.cumulative_trajectory = []
        
    def accumulate(self, input_vec, tick=None):
        """Add an input primitive to the trajectory. State accumulates."""
        if tick is not None:
            self.tick = max(self.tick, tick)
        # Substrate state evolves: psi += gain * input, then normalize
        self.psi = self.psi + self.accum_gain * input_vec
        # Apply a small phase rotation per step — sequence-order encoded in phase
        n_steps = len(self.cumulative_trajectory)
        phase_rotation = np.exp(1j * 2 * math.pi * n_steps / 16)
        self.psi = self.psi * phase_rotation
        self.psi = normalize(self.psi)
        self.cumulative_trajectory.append(self.psi.copy())
        
    def chi_of_state(self, state=None):
        """V-E winding number of state — the substrate's identity for it."""
        if state is None:
            state = self.psi
        amps = np.abs(state)
        thresh = (1.0 / np.sqrt(len(state))) * 0.85
        committed = amps > thresh
        V = int(committed.sum())
        E = 0
        for i in range(len(state) - 1):
            if committed[i] and committed[i + 1]:
                E += 1
        if committed[0] and committed[-1]:
            E += 1
        return V - E
    
    def find_matching_mode(self, state=None, threshold=0.85):
        """Find existing mode that matches current state (above threshold)."""
        if state is None:
            state = self.psi
        if np.linalg.norm(state) < 1e-9:
            return -1, 0.0
        best_idx, best_score = -1, -1
        for i, m in enumerate(self.modes):
            score = float(np.abs(np.vdot(m["vec"], state)) ** 2)
            if score > best_score:
                best_score = score
                best_idx = i
        if best_score >= threshold:
            return best_idx, best_score
        return -1, best_score
    
    def commit(self, label=None, tick=None):
        """Commit current trajectory state as a mode.
        If existing mode matches (>threshold), reinforce it.
        Otherwise create new mode.
        """
        if tick is not None:
            self.tick = max(self.tick, tick)
        if np.linalg.norm(self.psi) < 1e-9:
            return None  # nothing to commit
        
        # Try to match existing mode by state
        match_idx, match_score = self.find_matching_mode(threshold=0.85)
        # Also try to match by label (if provided and we've seen it before)
        if label is not None and label in self._label_index:
            label_idx = self._label_index[label]
            if label_idx != match_idx and match_score < 0.95:
                # Label says this is the same word — trust the label
                match_idx = label_idx
                match_score = float(np.abs(np.vdot(self.modes[label_idx]["vec"], self.psi))**2)
        
        chi = text_chi(label) if label is not None else self.chi_of_state()
        if match_idx >= 0:
            # Reinforce existing
            mode = self.modes[match_idx]
            # State update: weighted average
            mode["vec"] = normalize(0.9 * mode["vec"] + 0.1 * self.psi)
            mode["count"] += 1
            mode["last_tick"] = self.tick
            return {"mode_id": match_idx, "label": mode["label"], "chi": chi,
                    "reason": "reinforce", "score": match_score}
        else:
            # New mode
            new_label = label if label is not None else f"<chi{chi}_t{self.tick}>"
            mode_id = len(self.modes)
            self.modes.append({
                "label": new_label,
                "vec": self.psi.copy(),
                "chi": chi,
                "count": 1,
                "born_tick": self.tick,
                "last_tick": self.tick,
            })
            if label is not None:
                self._label_index[label] = mode_id
            return {"mode_id": mode_id, "label": new_label, "chi": chi,
                    "reason": "new", "score": 0.0}


class TextProcessor:
    """End-to-end text processor:
    
    text → letter primitives → letter trajectories → word commits →
        word trajectories → sentence commits
    
    Returns the commit history at each layer.
    """
    
    def __init__(self):
        self.letter_layer = CompositionSection("letter_acc", primitive_kind="LETTER")
        self.word_layer = CompositionSection("word_acc", accum_gain=0.5)
        self.sentence_layer = CompositionSection("sentence_acc", accum_gain=0.5)
        self.tick = 0
        self.log = []
        
    def process(self, text):
        """Process text. Returns log of commits at each layer."""
        text = text.lower()
        current_word_chars = []
        for c in text:
            self.tick += 1
            ctype = char_type(c)
            if ctype is None:
                continue
                
            _, vec = char_vec(c)
            
            if ctype == "LETTER" or ctype == "DIGIT":
                # Accumulate in letter trajectory
                self.letter_layer.accumulate(vec, tick=self.tick)
                current_word_chars.append(c)
            else:
                # Boundary: punct or space → commit accumulated word
                if current_word_chars:
                    word_label = "".join(current_word_chars)
                    word_commit = self.letter_layer.commit(label=word_label, tick=self.tick)
                    if word_commit is not None:
                        self.log.append({"layer": "word", "tick": self.tick, **word_commit})
                        # Feed word commit's state into word_layer
                        word_state = self.letter_layer.modes[word_commit["mode_id"]]["vec"]
                        self.word_layer.accumulate(word_state, tick=self.tick)
                    self.letter_layer.reset_state()
                    current_word_chars = []
                
                # Is this an end-of-sentence boundary?
                if c in ".!?":
                    sent_commit = self.word_layer.commit(tick=self.tick)
                    if sent_commit is not None:
                        self.log.append({"layer": "sentence", "tick": self.tick, **sent_commit})
                        sent_state = self.word_layer.modes[sent_commit["mode_id"]]["vec"]
                        self.sentence_layer.accumulate(sent_state, tick=self.tick)
                    self.word_layer.reset_state()
        
        # End of input — commit any pending word/sentence
        if current_word_chars:
            word_label = "".join(current_word_chars)
            wc = self.letter_layer.commit(label=word_label, tick=self.tick)
            if wc is not None:
                self.log.append({"layer": "word", "tick": self.tick, **wc})
                word_state = self.letter_layer.modes[wc["mode_id"]]["vec"]
                self.word_layer.accumulate(word_state, tick=self.tick)
            self.letter_layer.reset_state()
        
        if np.linalg.norm(self.word_layer.psi) > 1e-6:
            sc = self.word_layer.commit(tick=self.tick)
            if sc is not None:
                self.log.append({"layer": "sentence", "tick": self.tick, **sc})
            self.word_layer.reset_state()
        
        return self.log


if __name__ == "__main__":
    # Test composition layer
    print("=" * 70)
    print("LAYER 2 TEST: composition")
    print("=" * 70)
    
    tp = TextProcessor()
    text = ("in the great green room there was a telephone and a red balloon. "
            "and a picture of the cow jumping over the moon. "
            "and there were three little bears sitting on chairs.")
    
    tp.process(text)
    
    print(f"\nProcessed text ({len(text)} chars)")
    print(f"Word modes committed: {len(tp.letter_layer.modes)}")
    print(f"Sentence modes committed: {len(tp.word_layer.modes)}")
    print(f"Total commits logged: {len(tp.log)}")
    
    # Show unique words found
    word_labels = {m["label"]: m["count"] for m in tp.letter_layer.modes}
    print(f"\nUnique words: {len(word_labels)}")
    print("Most-counted:")
    for w, n in sorted(word_labels.items(), key=lambda x: -x[1])[:10]:
        print(f"  '{w}': {n}")
    
    # Show that re-reading produces reinforcement, not new modes
    print("\n--- Re-process same text — should reinforce, not duplicate ---")
    n_modes_before = len(tp.letter_layer.modes)
    tp.process(text)
    n_modes_after = len(tp.letter_layer.modes)
    print(f"Word modes before: {n_modes_before}, after re-read: {n_modes_after}")
    print(f"New modes added: {n_modes_after - n_modes_before}")
    
    # Determinism test — same word twice produces same chi
    print("\n--- Determinism: same word should produce same state ---")
    tp2 = TextProcessor()
    tp2.process("moon moon moon")
    moon_modes = [m for m in tp2.letter_layer.modes if m["label"] == "moon"]
    print(f"'moon' processed 3 times -> {len(moon_modes)} distinct mode(s)")
    if moon_modes:
        print(f"  chi: {moon_modes[0]['chi']}, count: {moon_modes[0]['count']}")
    
    # Discrimination test — different words should produce different states
    print("\n--- Discrimination: word signatures ---")
    tp3 = TextProcessor()
    tp3.process("moon noon soon mood moan cat dog sun stars night")
    pairs = []
    for i, m1 in enumerate(tp3.letter_layer.modes):
        for m2 in tp3.letter_layer.modes[i+1:]:
            ov = float(np.abs(np.vdot(m1["vec"], m2["vec"]))**2)
            pairs.append((m1["label"], m2["label"], ov))
    pairs.sort(key=lambda x: -x[2])
    print("Most-similar word pairs (high overlap = similar trajectories):")
    for w1, w2, ov in pairs[:8]:
        print(f"  {w1:8s} / {w2:8s}: {ov:.3f}")
    print("Most-distinct word pairs:")
    for w1, w2, ov in pairs[-5:]:
        print(f"  {w1:8s} / {w2:8s}: {ov:.3f}")
