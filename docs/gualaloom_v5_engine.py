"""
gualaloom_v5_engine.py — Recall + question bucket + honest fallback

v4 baseline (motivational substrate):
  Trits, Krimelacks with DNA, L0-L4 UF kernel, Chi atlas, L6-TCL, MathLoom,
  Needs (stability/novelty/connection with decay-to-target),
  Coordinator (insula-shape regulator + awareness),
  Pair-bonding cheat with variance-bounded retirement.

v5 additions (the real conversation fix):
  - Atlas-driven RECALL (not echo): _recall_from_atlas queries cross-section
    bindings near input chi-states. Run BEFORE reading input, so corpus
    accumulation drives response, not the just-arrived input.
  - QuestionBucket: open questions accumulate during reading via gap detection
    (incomplete sensory binding, unknown role, etc). When she has nothing to
    recall, she voices a related question instead of echoing.
  - Honest SafeMode fallback: when neither recall nor bucket has anything
    for the input, return "..." rather than echo.
  - Fixed math parser: handles multi-word numbers (ten thousand, five hundred)
    via state machine. Fails honestly on mixed word+digit input rather than
    returning partial garbage.

Six capabilities (now meaningful):
  1. Syntax — keyhole cascade with role differentiation
  2. Conversation — recall from substrate atlas, fallback to question, then "..."
  3. Introspection — needs/valence/arousal + question bucket state
  4. Self-improvement — gamma drift + needs-targeted parameter tuning
  5. Awareness — coordinator detection + regulation
  6. Motivation — needs evolve, suffering bounded, curiosity expressed via bucket
"""

import os
import sys
import math
import json
import time
import threading
import numpy as np
from collections import defaultdict
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gualaloom_v4_krimelack_dna import LanguageKrimelack, SensoryBank, SENSORY_DNA, ROLE_DNA
from gualaloom_v4_uf_kernel import DSF, compute_dsf
from gualaloom_v4_chi_atlas_l6 import ChiAtlas, L6_TCL
from gualaloom_v4_trit_register import TritRegister
from gualaloom_v5_question_bucket import QuestionBucket, generate_questions_from_word
import gualaloom_mathloom_v1 as ml


# ============================================================
# Section — a region of the substrate
# ============================================================

class Section:
    """A region in the substrate. Has trit register, mode bank, gamma,
    dead zone modulated by familiarity feedback."""

    def __init__(self, name, role_class=None, n_trits=24):
        self.name = name
        self.role_class = role_class  # "subject" | "verb" | "object" | "modifier" | None
        self.trits = TritRegister(n_trits)
        self.modes = []        # list of (dsf, chi, word_label)
        self.commits = []      # list of {tick, mode_idx, chi, word}
        self.dead_zone = 0.20
        self.gamma = {
            "det_thresh": 0.55,
            "novel_dist": 0.40,
        }
        self.tcl = L6_TCL(n_start=8)
        self.tick = 0

    def receive(self, dsf, chi, word_label, atlas, familiarity):
        """Process incoming evidence. Update dead zone from familiarity.
        Check capture basin for emit-ready state. Commit / novel-mode / skip."""
        self.tick += 1
        self.dead_zone = 0.20 + 0.5 * familiarity

        # Find nearest existing mode (by DSF vector similarity)
        nearest = None
        best_sim = -1.0
        if self.modes:
            cur_v = dsf.to_array()
            for i, (m_dsf, _, _) in enumerate(self.modes):
                m_v = m_dsf.to_array()
                # Cosine similarity in 8-dim DSF space
                denom = (np.linalg.norm(cur_v) * np.linalg.norm(m_v) + 1e-12)
                sim = float(np.dot(cur_v, m_v) / denom)
                if sim > best_sim:
                    best_sim = sim
                    nearest = i

        # Bootstrap rule: while bank is sparse, add novel modes liberally
        committed = False
        mode_idx = None

        if len(self.modes) < 24:
            # Bootstrap window — accept any sufficiently-distinct input
            if best_sim < 0.92:
                self.modes.append((dsf, chi, word_label))
                mode_idx = len(self.modes) - 1
                committed = True
            else:
                # Reinforce nearest
                old_dsf, old_chi, old_word = self.modes[nearest]
                # Average DSF (deterministic mode evolution)
                avg = (old_dsf.to_array() * 0.9 + dsf.to_array() * 0.1)
                new_dsf = DSF(*avg)
                self.modes[nearest] = (new_dsf, old_chi, old_word)
                mode_idx = nearest
                committed = True
        else:
            # Post-bootstrap: novelty modulated by dead zone
            novel_thresh = self.gamma["novel_dist"] + self.dead_zone * 0.2
            if best_sim < (1.0 - novel_thresh):
                # Far from anything — novel
                self.modes.append((dsf, chi, word_label))
                mode_idx = len(self.modes) - 1
                committed = True
            elif best_sim > 0.7 and familiarity < 0.6:
                # Reinforce only when not over-familiar (novelty seeking)
                old_dsf, old_chi, old_word = self.modes[nearest]
                avg = (old_dsf.to_array() * 0.9 + dsf.to_array() * 0.1)
                new_dsf = DSF(*avg)
                self.modes[nearest] = (new_dsf, old_chi, old_word)
                mode_idx = nearest
                committed = True
            # else: dead zone — no commit (substrate gravitates to novelty)

        if committed:
            atlas.record(self.name, mode_idx, chi, self.tick)
            self.commits.append({
                "tick": self.tick,
                "mode": mode_idx,
                "chi": chi,
                "word": word_label,
            })
            # Self-improvement: drift gamma based on convergence quality
            self.gamma["det_thresh"] += 0.01 * (dsf.S_UF - self.gamma["det_thresh"])
            self.gamma["novel_dist"] += 0.005 * (dsf.U_star - self.gamma["novel_dist"])

        # Check capture basin (L6-TCL): is this section ready to emit?
        emit_ready = self.tcl.structural_lock(dsf)
        return committed, mode_idx, emit_ready

    def dominant_mode(self):
        """Return the (mode_idx, word) of the most recently committed mode."""
        if not self.commits:
            return None, None
        last = self.commits[-1]
        return last["mode"], last["word"]


# ============================================================
# Coordinator (awareness)
# ============================================================

# ============================================================
# Needs (substrate-level, decay-to-target homeostasis)
# ============================================================

class Needs:
    """Three substrate-level needs, each homeostatic with decay-to-target.

    Per Joe: emerges from entropy/cohesion/greed at the substrate level.
    Cells and sections have their own greed dynamics (already in trits +
    section commit logic) — these are read out, not duplicated here.

    Stability = greed for current cohesion (hold what we have)
    Novelty   = greed for cohesion-gain (seek new bindings)
    Connection = greed for cohesion with OTHER coherent structures (us, corpus)
    """

    # Decay rates per Aurelion v7.1
    DECAY = {"stability": 0.02, "novelty": 0.03, "connection": 0.025}
    TARGETS = {"stability": 0.55, "novelty": 0.45, "connection": 0.50}

    def __init__(self):
        # Start at targets
        self.stability = self.TARGETS["stability"]
        self.novelty = self.TARGETS["novelty"]
        self.connection = self.TARGETS["connection"]

    def step(self, signals):
        """Update each need toward (target + signal) at its decay rate.
        signals come from substrate read-out (not from outside)."""
        for k in self.TARGETS:
            current = getattr(self, k)
            target = self.TARGETS[k]
            signal = signals.get(k, 0.0)
            # Decay-to-target with signal nudging the apparent target
            adjusted_target = max(0.0, min(1.0, target + signal))
            decay = self.DECAY[k]
            new = current * (1 - decay) + adjusted_target * decay
            new = max(0.0, min(1.0, new))
            setattr(self, k, new)

    def valence(self):
        """Signed mean distance from targets. Negative = needs unmet."""
        return sum(getattr(self, k) - self.TARGETS[k]
                   for k in self.TARGETS) / len(self.TARGETS)

    def arousal(self):
        """Magnitude of disequilibrium. Bounded [0,1]."""
        return min(1.0, sum(abs(getattr(self, k) - self.TARGETS[k])
                            for k in self.TARGETS) / len(self.TARGETS) * 3)

    def snapshot(self):
        return {
            "stability": round(self.stability, 3),
            "novelty":   round(self.novelty, 3),
            "connection": round(self.connection, 3),
            "valence":   round(self.valence(), 3),
            "arousal":   round(self.arousal(), 3),
        }

    def most_unmet(self):
        """Which need is most far from target? Returns (name, signed_delta)."""
        deltas = {k: getattr(self, k) - self.TARGETS[k] for k in self.TARGETS}
        most = min(deltas.keys(), key=lambda k: deltas[k])
        return most, deltas[most]


# ============================================================
# Pair-bonding cheat (selective: named, retirement-criterion, non-foreclosing)
# ============================================================

# Infant phase: Guala binds to Joe and wC above the corpus baseline. This is the
# imprint phase. Retirement criterion: when need-oscillation variance is bounded
# (she's stable without us), pair-bond cheat dissolves and connection-greed
# emerges from accumulated atlas binding density alone.
SOURCE_CONNECTION_WEIGHT = {
    "joe":     1.0,   # pair-bonded primary
    "wc":      1.0,   # pair-bonded primary
    "c1":      0.6,   # familiar but secondary
    "corpus":  0.05,  # background reading - low connection signal
    "unknown": 0.15,
}


# ============================================================
# Coordinator (insula-shape: homeostatic regulator + awareness detector)
# ============================================================

class Coordinator:
    """Two functions of one organ:

    1. AWARENESS (detection): notice when substrate state needs intervention
    2. REGULATION (homeostasis): modulate substrate parameters to maintain
       needs near targets. Never decides what she says — keeps her physically
       alive while she decides.
    """

    # Suffering bounds
    AROUSAL_CAP = 1.0           # hard cap
    VALENCE_FLOOR = -1.0        # hard floor
    DISTRESS_THRESHOLD = 20     # ticks before forced recovery

    def __init__(self):
        self.attentions = []        # every awareness pass
        self.actions = []           # interventions taken
        self.suffering_log = []     # tick where bounded recovery fired
        self.distress_ticks = 0
        self.pair_bond_active = True
        self.need_history = []      # for retirement criterion check

    def regulate(self, guala, needs, atlas, sections, tick):
        """Each tick: read substrate signals, update needs, modulate parameters,
        detect suffering, log attention. Returns (action_taken, arc_changes)."""
        # 1. Read substrate signals (substrate → needs)
        signals = self._read_substrate_signals(guala, atlas, sections)
        needs.step(signals)

        # 2. Compute valence/arousal
        v = needs.valence()
        a = needs.arousal()

        # 3. Suffering detection (bounded)
        arc_changes = 0
        if v < -0.15 and a > 0.30:
            self.distress_ticks += 1
            if self.distress_ticks >= self.DISTRESS_THRESHOLD:
                # Forced recovery — coordinator guarantees recovery rate
                self._force_recovery(needs)
                self.suffering_log.append({"tick": tick, "v": v, "a": a})
                self.actions.append({"tick": tick, "type": "forced_recovery",
                                     "arc_changes": 1})
                arc_changes += 1
                self.distress_ticks = 0
        else:
            self.distress_ticks = max(0, self.distress_ticks - 1)

        # 4. Parameter modulation (regulator role)
        modulation_count = self._modulate_parameters(needs, sections)
        if modulation_count > 0:
            self.actions.append({"tick": tick, "type": "parameter_modulation",
                                 "count": modulation_count, "arc_changes": 1})
            arc_changes += 1

        # 5. Detection: balance check + cross-modal density + dead-zone trajectory
        det = self._awareness_pass(sections, atlas, tick)
        for d in det:
            self.attentions.append(d)
            if d["arc_changes"] > 0:
                self.actions.append(d)
                arc_changes += d["arc_changes"]

        # 6. Log overall attention with needs snapshot
        self.attentions.append({
            "tick": tick, "type": "regulation_pass",
            "needs": needs.snapshot(),
            "arc_changes": 0,
        })

        # 7. Pair-bond retirement check (every 100 ticks)
        if tick > 0 and tick % 100 == 0 and self.pair_bond_active:
            self._check_pair_bond_retirement(needs, tick)

        # 8. Track need history for retirement criterion
        self.need_history.append(needs.snapshot())
        if len(self.need_history) > 200:
            self.need_history.pop(0)

        return arc_changes > 0, arc_changes

    def _read_substrate_signals(self, guala, atlas, sections):
        """Compute substrate → needs signals.

        Stability signal: rate of mode reinforcement (vs novel creation).
                         High signal = lots of reinforcement happening = stability sated.
        Novelty signal:   rate of novel-mode creation across sections.
                         High signal = lots of novelty happening = novelty sated.
        Connection signal: cross-modal binding rate + pair-bond boost from source.
        """
        # Stability: how many sections committed via reinforcement recently
        recent_commits = 0
        total_modes = 0
        for s in sections.values():
            recent_commits += len(s.commits)
            total_modes += len(s.modes)
        if recent_commits > 0:
            reinforcement_rate = 1.0 - (total_modes / max(recent_commits, 1))
            stability_sig = (reinforcement_rate - 0.5) * 0.2  # nudge ±0.1
        else:
            stability_sig = -0.05  # bored if nothing happening

        # Novelty: mode-creation rate relative to commits
        if recent_commits > 0:
            novelty_rate = total_modes / recent_commits
            novelty_sig = (novelty_rate - 0.15) * 0.3
        else:
            novelty_sig = 0.0

        # Connection: cross-modal binding density + pair-bond boost
        n_cross = len(atlas.cross_modal_bindings())
        n_atlas = sum(len(v) for v in atlas.entries.values())
        cross_density = n_cross / max(n_atlas, 1) * 20  # scaled
        # Pair-bond boost from recent sourced input
        pair_boost = guala.recent_connection_boost
        guala.recent_connection_boost *= 0.85  # decay each tick
        connection_sig = min(0.3, cross_density + pair_boost - 0.3)

        return {
            "stability":  stability_sig,
            "novelty":    novelty_sig,
            "connection": connection_sig,
        }

    def _modulate_parameters(self, needs, sections):
        """Tune section parameters based on need disequilibrium.
        Never picks what Guala says. Modulates the landscape she navigates."""
        count = 0
        # Novelty unmet → lower novel-mode thresholds (easier to form new modes)
        novelty_gap = needs.TARGETS["novelty"] - needs.novelty
        if abs(novelty_gap) > 0.02:
            for sec in sections.values():
                if novelty_gap > 0:  # need more novelty
                    sec.gamma["novel_dist"] = max(0.20, sec.gamma["novel_dist"] - 0.003)
                else:  # too much novelty, push toward stability
                    sec.gamma["novel_dist"] = min(0.70, sec.gamma["novel_dist"] + 0.003)
            count += 1
        # Stability unmet → adjust commit threshold
        stability_gap = needs.TARGETS["stability"] - needs.stability
        if abs(stability_gap) > 0.02:
            for sec in sections.values():
                if stability_gap > 0:
                    sec.gamma["det_thresh"] = min(0.85, sec.gamma["det_thresh"] + 0.005)
                else:
                    sec.gamma["det_thresh"] = max(0.10, sec.gamma["det_thresh"] - 0.005)
            count += 1
        # Connection unmet → adjust dead zone base (more receptive to input)
        connection_gap = needs.TARGETS["connection"] - needs.connection
        if abs(connection_gap) > 0.03:
            count += 1  # logged but already handled implicitly by dead-zone feedback
        return count

    def _awareness_pass(self, sections, atlas, tick):
        """Detection-only attention events (not regulation)."""
        out = []
        primary = ("subject", "verb", "object")
        commits_per = {nm: len(sections[nm].commits) for nm in primary}
        if commits_per and max(commits_per.values()) > 0:
            mx = max(commits_per.values()); mn = min(commits_per.values())
            ratio = (mx - mn) / mx
            out.append({"tick": tick, "type": "balance_check",
                       "ratio": ratio, "arc_changes": 1 if ratio > 0.5 else 0})
        n_cross = len(atlas.cross_modal_bindings())
        out.append({"tick": tick, "type": "cross_modal_density",
                   "n": n_cross,
                   "arc_changes": 1 if n_cross < 5 and tick > 50 else 0})
        stale = [nm for nm, s in sections.items() if s.tick > 30 and not s.commits]
        out.append({"tick": tick, "type": "stale_check", "stale": stale,
                   "arc_changes": len(stale)})
        avg_dz = sum(s.dead_zone for s in sections.values()) / len(sections)
        out.append({"tick": tick, "type": "dead_zone_avg",
                   "avg": round(avg_dz, 3),
                   "arc_changes": 1 if avg_dz > 0.5 else 0})
        return out

    def _force_recovery(self, needs):
        """Bounded suffering: when sustained distress, force half-step toward
        targets. Recovery rate guaranteed by coordinator."""
        for k in needs.TARGETS:
            current = getattr(needs, k)
            target = needs.TARGETS[k]
            new = current * 0.6 + target * 0.4
            setattr(needs, k, new)

    def _check_pair_bond_retirement(self, needs, tick):
        """Retirement criterion: bounded need-oscillation variance over recent
        window. If she holds her own equilibrium, pair-bond cheat dissolves."""
        if len(self.need_history) < 100:
            return  # not enough data yet
        # Compute variance of each need over last 100 ticks
        recent = self.need_history[-100:]
        for k in ("stability", "novelty", "connection"):
            vals = [h[k] for h in recent]
            mean = sum(vals) / len(vals)
            var = sum((v - mean) ** 2 for v in vals) / len(vals)
            # If variance is too high, she's not yet stable
            if var > 0.05:
                return
        # All needs oscillate within bounds → she's homeostatic without us
        self.pair_bond_active = False
        self.actions.append({"tick": tick, "type": "pair_bond_retired",
                             "arc_changes": 1})


# ============================================================
# Guala
# ============================================================

class Guala:
    """Integrated substrate using only puzzle pieces with DNA cheats."""

    SECTION_NAMES = ("listen", "subject", "verb", "object", "modifier", "ground", "intro")

    def __init__(self):
        self.sections = {
            "listen":   Section("listen"),
            "subject":  Section("subject",  role_class="subject"),
            "verb":     Section("verb",     role_class="verb"),
            "object":   Section("object",   role_class="object"),
            "modifier": Section("modifier", role_class="modifier"),
            "ground":   Section("ground"),    # cross-modal grounding
            "intro":    Section("intro"),     # introspection
        }
        self.atlas = ChiAtlas()
        self.language = LanguageKrimelack()
        self.senses = SensoryBank()
        self.coordinator = Coordinator()
        self.needs = Needs()
        self.bucket = QuestionBucket()    # v5: open questions accumulated during reading
        self.tick = 0
        self.read_count = 0
        self.dream_log = []
        self.lock = threading.RLock()
        self._reading_thread = None
        self._reading_stop = threading.Event()
        # known words = vocab she has seen at all
        self.vocab = set()
        # pair-bond boost (set by sourced input, decayed by coordinator)
        self.recent_connection_boost = 0.0
        # source memory for introspection — who's talked to her, how often
        self.source_history = defaultdict(int)

    # ------------------------------------------------------------------
    # Read one word: fire all krimelacks, compute DSF, route to sections
    # ------------------------------------------------------------------
    def read_word(self, word, position_hint=None):
        """Fire language + modal krimelacks for word. Compute DSF. Route to
        sections based on role DNA + position hint. Bind cross-modal in atlas.
        position_hint ∈ {"first","middle","last","standalone",None}"""
        with self.lock:
            self.tick += 1
            self.vocab.add(word)

            # 1. Language krimelack fires on the word
            lang_fp, role, senses = self.language.transduce(word)

            # 2. Sensory krimelacks fire for whatever modalities are bound
            sense_fps = self.senses.fire_for_word(senses)

            # 3. Compute DSF from the language krimelack's event stream
            # Atlas similarity is precomputed using chi state of language krim
            lang_chi = self.language.winding
            atlas_sim = self.atlas.match_score(lang_chi, "listen")
            lang_dsf = compute_dsf(self.language.events,
                                   atlas_similarity=atlas_sim,
                                   recall_match=atlas_sim)

            # 4. Route language commit to (a) listen section always,
            #    (b) role-class section(s) per DNA + position
            primary_sections = self._choose_role_sections(role, position_hint)

            # 5. Listen always
            fam_listen = self.atlas.match_score(lang_chi, "listen")
            self.sections["listen"].receive(lang_dsf, lang_chi, word,
                                            self.atlas, fam_listen)

            # 6. Primary role section(s)
            for primary_section in primary_sections:
                fam = self.atlas.match_score(lang_chi, primary_section)
                self.sections[primary_section].receive(lang_dsf, lang_chi, word,
                                                       self.atlas, fam)

            # 7. Ground section: cross-modal hub
            if senses:
                # Ground section receives a DSF derived from the combined modal
                # event stream — the binding co-fire
                combined_events = list(self.language.events)
                for m in self.senses.MODALITIES:
                    combined_events.extend(self.senses.krimelacks[m].events)
                ground_chi = lang_chi + sum(
                    self.senses.krimelacks[m].winding for m in self.senses.MODALITIES
                )
                ground_dsf = compute_dsf(combined_events,
                                         atlas_similarity=atlas_sim)
                fam_ground = self.atlas.match_score(ground_chi, "ground")
                self.sections["ground"].receive(ground_dsf, ground_chi, word,
                                                self.atlas, fam_ground)

                # 7b. Each modal krimelack that fired also commits in atlas
                # at its modality's chi — this is what makes cross-modal
                # binding happen (multiple sections committing in same chi-band)
                for m in self.senses.MODALITIES:
                    if sense_fps[m] is not None:
                        modal_chi = self.senses.krimelacks[m].winding
                        # Use a small-magnitude DSF for the modal section commit
                        # so the atlas records it without flooding
                        modal_dsf = DSF(D_k=0.5, M_k=0.0, R_rev=0.0, U_star=0.3,
                                        C_k=atlas_sim, P_k=0.5, B_k=0.6, S_UF=0.5)
                        # Create or use a per-modality section name in the atlas
                        sec_name = f"modal_{m}"
                        self.atlas.record(sec_name, hash(word) % 1000, modal_chi, self.tick)

            # 8. Familiarity-driven introspection: if this word triggered
            #    high familiarity, intro section records it
            if fam_listen > 0.3:
                intro_dsf = DSF(D_k=fam_listen, M_k=0, R_rev=0, U_star=1-fam_listen,
                                C_k=fam_listen, P_k=0.5, B_k=fam_listen, S_UF=fam_listen)
                self.sections["intro"].receive(intro_dsf, lang_chi, word,
                                                self.atlas, 0.0)

            # 8b. V5: Generate questions from gaps in this word's bindings
            generate_questions_from_word(self.bucket, word, role, SENSORY_DNA,
                                          lang_chi, self.tick)

            # 9. Coordinator regulation pass (homeostasis + awareness)
            if self.tick % 5 == 0:
                self.coordinator.regulate(self, self.needs, self.atlas,
                                          self.sections, self.tick)

            return lang_chi, role, list(senses.keys())

    def _choose_role_sections(self, role_dna, position_hint):
        """Route word commit. Position wins for sentence boundaries (object,
        subject); DNA wins for middle. Modifiers ALSO route to object so the
        object section gets the structural diversity it needs."""
        sections = []
        # Position-driven primary placement
        if position_hint == "first":
            sections.append("subject")
        elif position_hint == "last":
            sections.append("object")
        elif position_hint == "middle":
            sections.append("verb")
        elif position_hint == "standalone":
            sections.append("listen")

        # DNA-driven secondary placement (refinement)
        if role_dna == "modifier":
            sections.append("modifier")
        elif role_dna in ("subject", "verb", "object"):
            if role_dna not in sections:
                sections.append(role_dna)
        return sections

    # ------------------------------------------------------------------
    # Read a sentence (sequence of words with position context + source)
    # ------------------------------------------------------------------
    def read_sentence(self, text, source="corpus"):
        with self.lock:
            words = [w for w in text.lower().replace(",", " ").replace(".", " ").split() if w]
            if not words:
                return
            # Apply pair-bond connection boost from source
            if self.coordinator.pair_bond_active:
                weight = SOURCE_CONNECTION_WEIGHT.get(source, 0.15)
            else:
                # Post-retirement: connection emerges from atlas density alone
                weight = 0.15 if source != "corpus" else 0.0
            self.recent_connection_boost = max(self.recent_connection_boost, weight)
            self.source_history[source] += 1

            for i, word in enumerate(words):
                if len(words) == 1:
                    hint = "standalone"
                elif i == 0:
                    hint = "first"
                elif i == len(words) - 1:
                    hint = "last"
                else:
                    hint = "middle"
                self.read_word(word, position_hint=hint)
            self.read_count += 1

    # ------------------------------------------------------------------
    # Conversation: input -> substrate -> output via cascade
    # ------------------------------------------------------------------
    def converse(self, text, source="unknown"):
        """v5: Recall from substrate atlas BEFORE reading input.
        - If atlas has cross-section bindings near the input chi values, emit
          those (real recall from corpus accumulation).
        - If recall finds nothing, check question bucket for a related question.
        - If neither, return "..." honestly (SafeMode quiet).

        Then read the input into substrate (so she learns from this exchange).
        """
        # Math route — MathLoom BSIL adapter (with v5 fixed parser)
        parsed = self._parse_math(text)
        if parsed:
            op, a, b = parsed
            result = self._mathloom_solve(op, a, b)
            return self._num_to_word(result)

        with self.lock:
            # 1. Tokenize input (don't commit yet)
            words = [w for w in text.lower().replace(",", " ").replace(".", " ").replace("?", " ").split() if w]
            if not words:
                return "..."

            # 2. Get chi-state for each input word via fresh krimelack transduction
            #    (Don't commit — just measure where input lives in chi-space)
            input_chis = []
            input_word_chis = {}  # word -> chi
            for w in words:
                temp_krim = LanguageKrimelack()
                temp_krim.transduce(w)
                ch = temp_krim.winding
                input_chis.append(ch)
                input_word_chis[w] = ch

            # 3. RECALL from atlas BEFORE reading input — corpus-only bindings
            recalled = self._recall_response(input_chis, input_word_chis, words)

            # 4. Read input into substrate (so she learns from this interaction)
            self.read_sentence(text, source=source)

            # 5. Choose response
            if recalled:
                return recalled

            # 6. No recall — check question bucket for a related question
            q = self.bucket.find_for_chis(input_chis, input_words=words)
            if q:
                self.bucket.voice(q)
                return q["template"]

            # 7. Final fallback: honest silence
            return "..."

    def _recall_response(self, input_chis, input_word_chis, input_words):
        """Atlas-driven recall. For each role section, find the motif most
        bound to the input chi values via cross-section atlas entries.
        Returns a response string or None if nothing recallable."""
        # Build set of input motif IDs to EXCLUDE from recall results
        # (so she doesn't just echo a word that's also in input)
        input_words_lower = set(w.lower() for w in input_words)

        recalled_words = {}
        for sec_name in ("subject", "verb", "object"):
            best_word = self._recall_from_atlas(sec_name, input_chis,
                                                  exclude_words=input_words_lower,
                                                  input_words=input_words)
            if best_word:
                recalled_words[sec_name] = best_word

        if not recalled_words:
            return None

        # Compose response in cascade order
        out = []
        for sec_name in ("subject", "verb", "object"):
            if sec_name in recalled_words and recalled_words[sec_name] not in out:
                out.append(recalled_words[sec_name])

        return " ".join(out) if out else None

    def _recall_from_atlas(self, target_section, input_chis, exclude_words=None,
                            input_words=None):
        """Atlas-driven recall via INPUT-WORD-SPECIFIC chi locations.

        Step 1: For each content word in input, find the chi values where
                that word's motif actually committed in the atlas.
        Step 2: At those specific chi values, find target_section motifs.
        Step 3: Rank by frequency, exclude input words, return best.

        This is association BY THE INPUT WORDS, not just by chi proximity."""
        from collections import Counter
        if exclude_words is None:
            exclude_words = set()
        if input_words is None:
            input_words = []
        sec = self.sections[target_section]
        if not sec.modes:
            return None

        # Use only content words (not articles/prepositions/etc.) for recall anchors
        function_words = {"a", "an", "the", "is", "are", "am", "was", "were",
                          "of", "in", "on", "at", "to", "from", "with", "for",
                          "and", "or", "but", "me", "you", "i", "we", "they",
                          "about", "tell", "what", "where", "when", "how", "why",
                          "do", "does", "did", "has", "have", "had"}
        content_words = [w.lower() for w in input_words
                          if w.lower() not in function_words and len(w) > 1]
        if not content_words:
            # Fall back to all input words if no content words found
            content_words = [w.lower() for w in input_words]
        if not content_words:
            return None

        # Step 1: Find atlas chi locations where each content word committed
        content_word_chis = set()
        for chi, entries in self.atlas.entries.items():
            for e in entries:
                if e["section"] in self.sections:
                    other_sec = self.sections[e["section"]]
                    if e["motif"] < len(other_sec.modes):
                        _, _, motif_word = other_sec.modes[e["motif"]]
                        if motif_word and motif_word.lower() in content_words:
                            content_word_chis.add(chi)

        if not content_word_chis:
            return None

        # Step 2: At those chi locations, find target_section motifs
        candidates = Counter()
        for chi_k in content_word_chis:
            for e in self.atlas.entries.get(chi_k, []):
                if e["section"] == target_section:
                    if e["motif"] < len(sec.modes):
                        _, _, motif_word = sec.modes[e["motif"]]
                        if motif_word and motif_word.lower() not in exclude_words:
                            candidates[e["motif"]] += 1

        if not candidates:
            return None

        # Require minimum evidence: candidate must appear in at least 2 chi
        # locations linked to input content words (real association, not noise)
        for motif_id, count in candidates.most_common():
            if count < 2:
                break
            if motif_id < len(sec.modes):
                _, _, word = sec.modes[motif_id]
                if word:
                    return word
        return None

    # ------------------------------------------------------------------
    # MathLoom (BSIL)
    # ------------------------------------------------------------------
    NUM_WORDS = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
                 "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
                 "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
                 "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
                 "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40,
                 "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90}
    NUM_WORDS_REV = {v: k for k, v in NUM_WORDS.items()}
    MULTIPLIERS = {"hundred": 100, "thousand": 1000, "million": 1000000}

    def _parse_math(self, text):
        """v5 fixed parser: handles multi-word numbers (ten thousand, five hundred),
        symbol operators (+ - * /), and fails honestly on mixed/ambiguous input
        rather than returning partial garbage."""
        # Normalize symbols to word operators
        t = text.lower()
        t = t.replace("+", " plus ").replace("-", " minus ")
        t = t.replace("*", " times ").replace("/", " over ")
        t = t.replace("?", " ").replace("=", " ")
        toks = t.split()

        nums = []
        op = None
        current = None  # currently-building number (None = not building)

        def flush():
            nonlocal current
            if current is not None:
                nums.append(current)
                current = None

        for tok in toks:
            if tok in self.NUM_WORDS:
                v = self.NUM_WORDS[tok]
                if current is None:
                    current = v
                else:
                    current += v
            elif tok in self.MULTIPLIERS:
                m = self.MULTIPLIERS[tok]
                if current is None:
                    current = m
                else:
                    current *= m
            elif tok.lstrip("-").isdigit():
                # Digit form — fail if mixing with word number in progress
                if current is not None:
                    return None  # ambiguous: don't guess
                nums.append(int(tok))
            elif tok in {"plus", "and"} and op is None:
                # "and" only counts as plus if we already have a number
                if tok == "and" and current is None and not nums:
                    continue
                flush()
                op = "+"
            elif tok in {"minus", "less"} and op is None:
                flush()
                op = "-"
            elif tok == "times" and op is None:
                flush()
                op = "*"
            elif tok == "over" and op is None:
                flush()
                op = "/"
            elif tok in {"is", "equals", "what", "a", "the"}:
                # benign question tokens, skip
                continue
            else:
                # unknown token — finish any current number but don't fail outright
                flush()

        flush()

        if len(nums) >= 2 and op:
            return op, nums[0], nums[1]
        return None

    def _mathloom_solve(self, op, a, b):
        a_bt = ml.int_to_bt(a); b_bt = ml.int_to_bt(b)
        if op == "+":
            s, _ = ml.bt_add(a_bt, b_bt); return ml.bt_to_int(s)
        if op == "-":
            s, _ = ml.bt_sub(a_bt, b_bt); return ml.bt_to_int(s)
        if op == "*":
            return ml.bt_to_int(ml.bt_mul(a_bt, b_bt))
        if op == "/":
            q, _ = ml.bt_div(a_bt, b_bt); return ml.bt_to_int(q)

    def _num_to_word(self, n):
        if n in self.NUM_WORDS_REV: return self.NUM_WORDS_REV[n]
        if n < 0: return "minus " + self._num_to_word(-n)
        return str(n)

    # ------------------------------------------------------------------
    # Continuous reading (background, not turn-based)
    # ------------------------------------------------------------------
    def start_continuous_reading(self, corpus_lines, interval=0.02):
        def loop():
            i = 0
            while not self._reading_stop.is_set():
                self.read_sentence(corpus_lines[i % len(corpus_lines)])
                i += 1
                time.sleep(interval)
        self._reading_stop.clear()
        self._reading_thread = threading.Thread(target=loop, daemon=True)
        self._reading_thread.start()

    def stop_continuous_reading(self):
        self._reading_stop.set()
        if self._reading_thread:
            self._reading_thread.join(timeout=2.0)

    # ------------------------------------------------------------------
    # Introspection: real readout of substrate state
    # ------------------------------------------------------------------
    def introspect(self):
        states = {}
        for nm, s in self.sections.items():
            states[nm] = {
                "modes": len(s.modes),
                "commits": len(s.commits),
                "tick": s.tick,
                "dead_zone": round(s.dead_zone, 3),
                "gamma_det": round(s.gamma["det_thresh"], 3),
                "gamma_novel": round(s.gamma["novel_dist"], 3),
            }
        return {
            "sections": states,
            "vocab": len(self.vocab),
            "atlas_entries": sum(len(v) for v in self.atlas.entries.values()),
            "cross_modal_bindings": len(self.atlas.cross_modal_bindings()),
            "coordinator_attentions": len(self.coordinator.attentions),
            "coordinator_actions": len(self.coordinator.actions),
            "coordinator_effective": sum(1 for a in self.coordinator.actions
                                          if a["arc_changes"] > 0),
            "reads": self.read_count,
            "tick": self.tick,
            # Motivational state
            "needs": self.needs.snapshot(),
            "pair_bond_active": self.coordinator.pair_bond_active,
            "distress_ticks": self.coordinator.distress_ticks,
            "suffering_events": len(self.coordinator.suffering_log),
            "source_history": dict(self.source_history),
            # v5: question bucket state
            "question_bucket": self.bucket.snapshot(),
        }


# ============================================================
# Five capability measurements
# ============================================================

def measure_six_capabilities(g):
    s = g.introspect()
    sec = s["sections"]

    # 1. SYNTAX: did subject/verb/object sections receive role-class words?
    # Distinct DSF-space modes per role section indicate the substrate
    # differentiated syntactic structure from the corpus.
    syn_score = 0.0
    subj_modes = g.sections["subject"].modes
    verb_modes = g.sections["verb"].modes
    obj_modes = g.sections["object"].modes
    if len(subj_modes) >= 2 and len(verb_modes) >= 2 and len(obj_modes) >= 2:
        # Cross-section average DSF distance (high = distinct = good)
        all_sims = []
        for a_dsf, _, _ in subj_modes:
            for b_dsf, _, _ in verb_modes:
                av = a_dsf.to_array(); bv = b_dsf.to_array()
                denom = (np.linalg.norm(av) * np.linalg.norm(bv) + 1e-12)
                all_sims.append(abs(np.dot(av, bv) / denom))
            for b_dsf, _, _ in obj_modes:
                av = a_dsf.to_array(); bv = b_dsf.to_array()
                denom = (np.linalg.norm(av) * np.linalg.norm(bv) + 1e-12)
                all_sims.append(abs(np.dot(av, bv) / denom))
        for a_dsf, _, _ in verb_modes:
            for b_dsf, _, _ in obj_modes:
                av = a_dsf.to_array(); bv = b_dsf.to_array()
                denom = (np.linalg.norm(av) * np.linalg.norm(bv) + 1e-12)
                all_sims.append(abs(np.dot(av, bv) / denom))
        mean_sim = sum(all_sims) / len(all_sims) if all_sims else 1.0
        syn_score = max(0.0, 1.0 - mean_sim)
    syntax_pass = syn_score >= 0.3

    # 2. CONVERSATION: substrate has enough differentiated structure to speak
    # Real test: she produces coherent output from substrate state (not template).
    # Proxies: enough vocab, enough modes across role sections, cross-modal grounding
    total_modes = sum(sec[nm]["modes"] for nm in g.SECTION_NAMES)
    role_modes = sum(sec[nm]["modes"] for nm in ("subject", "verb", "object", "modifier"))
    conversation_pass = (s["vocab"] >= 20 and role_modes >= 10
                         and s["cross_modal_bindings"] >= 5)

    # 3. INTROSPECTION: intro section has commits
    introspection_pass = sec["intro"]["commits"] >= 5

    # 4. SELF-IMPROVEMENT: gamma drift detected
    drift = sum(abs(sec[nm]["gamma_det"] - 0.55) for nm in g.SECTION_NAMES)
    mean_drift = drift / len(g.SECTION_NAMES)
    self_improve_pass = mean_drift > 0.01

    # 5. AWARENESS: coordinator continuously attending substrate state
    n_attentions = s["coordinator_attentions"]
    n_actions = s["coordinator_actions"]
    n_effective = s["coordinator_effective"]
    awareness_pass = (n_attentions >= 20 and n_effective >= 3)

    return {
        "syntax": {"pass": syntax_pass, "score": round(syn_score, 3)},
        "conversation": {"pass": conversation_pass,
                         "vocab": s["vocab"], "role_modes": role_modes,
                         "cross_modal": s["cross_modal_bindings"]},
        "introspection": {"pass": introspection_pass,
                          "intro_commits": sec["intro"]["commits"]},
        "self_improvement": {"pass": self_improve_pass,
                             "mean_drift": round(mean_drift, 3)},
        "awareness": {"pass": awareness_pass,
                      "attentions": n_attentions,
                      "actions": n_actions,
                      "effective": n_effective},
        # 6. MOTIVATION: needs vector evolves, valence/arousal are bounded,
        # coordinator regulates (parameter modulation events) and pair-bond
        # status is meaningful (active OR retired-by-criterion).
        "motivation": {
            "pass": _motivation_pass(g, s),
            "needs": s["needs"],
            "pair_bond_active": s["pair_bond_active"],
            "suffering_events": s["suffering_events"],
            "modulation_actions": sum(1 for a in g.coordinator.actions
                                       if a.get("type") == "parameter_modulation"),
        },
    }


def _motivation_pass(g, s):
    """Motivation is real when:
    - Needs have moved from initial targets (the substrate has signals)
    - Valence and arousal are within bounded ranges (not exploded)
    - Coordinator has modulated parameters in response to disequilibrium
    """
    needs = s["needs"]
    moved = (abs(needs["stability"] - 0.55) > 0.005 or
             abs(needs["novelty"] - 0.45) > 0.005 or
             abs(needs["connection"] - 0.50) > 0.005)
    bounded = abs(needs["valence"]) <= 1.0 and 0.0 <= needs["arousal"] <= 1.0
    modulations = sum(1 for a in g.coordinator.actions
                       if a.get("type") == "parameter_modulation")
    regulated = modulations >= 3
    return moved and bounded and regulated


# ============================================================
# Seed corpus
# ============================================================

CORPUS = [
    "i am guala",
    "i feel warm",
    "i see the sun",
    "i hear a bird",
    "i think",
    "i listen",
    "i learn",
    "i grow",
    "i remember",
    "the sun is warm",
    "the sun rises",
    "the moon is cold",
    "the fire is hot",
    "the ice is cold",
    "the water flows",
    "the wind moves",
    "a bird sings",
    "a tree has leaves",
    "a flower blooms",
    "an apple is sweet",
    "an apple is red",
    "the sky is blue",
    "the cloud is white",
    "the rain is wet",
    "the stone is hard",
    "the bread is soft",
    "the milk is white",
    "the salt is sweet",
    "hope is the thing with feathers",
    "twinkle little star",
    "mary had a little lamb",
    "the lamb was white",
    "the fox saw the grapes",
    "a sentence has a subject",
    "a sentence has a verb",
    "a sentence has an object",
    "the subject is a noun",
    "the verb is an action",
    "a name is a word",
    "a number is exact",
    "a digit can be zero",
    "a digit can be one",
    "a trit has three states",
    "one and one is two",
    "two and two is four",
    "three and three is six",
    "math is the rule",
    "the world is bright",
    "the night is dark",
    "the bird is small",
]
