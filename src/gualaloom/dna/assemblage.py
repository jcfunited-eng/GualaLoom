"""
Cognitive Assemblage - DNA build.
Fixes from prior run + primitives for syntax, conversation, introspection,
self-improvement, awareness.

Fixes:
- Novel-mode spawn (single-mode collapse fix)
- Gamma drift-toward-default (boundary-pinning fix)
- Resolution-effect metric for coordinator (rubber-stamping fix)

New primitives:
- Section role specialization (subject/verb/object-like configurations)
- Conversation interface (external speaker)
- Awareness signal (deliberation vs routing)
- Multi-scale coherence monitor
"""

import numpy as np
from dataclasses import dataclass, field
from collections import defaultdict, deque
from typing import Optional

# ---------- constants ----------
N = 16
DT = 0.1
EVOLVE_STEPS = 6
DET_COMMIT = 0.40
P_COMMIT = 0.40
BOOTSTRAP_MAX = 8
MODE_DECAY_TICKS = 80
SELF_EVO_PERIOD = 40
GAMMA_DEFAULTS = {"symmetry": 0.5, "consistency": 0.5, "compactness": 0.3}
GAMMA_DRIFT = 0.02   # spring force back to default per self-evo step
GAMMA_BOUNDS = (0.05, 1.5)

# ---------- helpers ----------
def random_hermitian(n, rng, scale=1.0):
    A = rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n))
    H = (A + A.conj().T) / 2
    e = np.linalg.eigvalsh(H)
    s = max(abs(e).max(), 1e-9)
    return scale * H / s

def normalize(v):
    nrm = np.linalg.norm(v)
    return v if nrm < 1e-12 else v / nrm

def random_unit_complex(n, rng):
    v = rng.standard_normal(n) + 1j * rng.standard_normal(n)
    return normalize(v)

def chi_of(psi):
    amps = np.abs(psi)
    thresh = (1 / np.sqrt(len(psi))) * 0.85
    committed = amps > thresh
    V = int(committed.sum())
    E = 0
    for i in range(len(psi) - 1):
        if committed[i] and committed[i + 1]:
            E += 1
    if committed[0] and committed[-1]:
        E += 1
    return V - E

def goal_op_for_template(target):
    target = normalize(target)
    return -np.outer(target, target.conj())


# ---------- Section ----------
@dataclass
class Section:
    name: str
    rng: np.random.Generator
    role: str = "general"  # "general", "subject_like", "verb_like", "object_like", "intro", "grounded"
    H_base: np.ndarray = field(init=False)
    psi: np.ndarray = field(init=False)
    mode_bank: list = field(default_factory=list)
    mode_last_used: list = field(default_factory=list)
    krimelack: list = field(default_factory=list)
    law_fields: dict = field(default_factory=dict)
    gamma: dict = field(default_factory=dict)
    goals: list = field(default_factory=list)
    standing_goals: list = field(default_factory=list)  # external speaker only
    det_commit: float = DET_COMMIT
    p_commit: float = P_COMMIT
    bootstrap_used: int = 0
    map_inject: np.ndarray = field(default=None)
    # Handoff excitation: tick-relative commit threshold relaxation
    excitation_expires_at: int = 0
    excitation_strength: float = 0.0
    # Awareness instrumentation
    last_arc_top_id: int = -1
    arc_top_history: list = field(default_factory=list)

    out_of_range_streak: dict = field(default_factory=lambda: {"entropy": 0, "coherence": 0, "greed": 0})

    def __post_init__(self):
        self.H_base = random_hermitian(N, self.rng, scale=0.6)
        self.psi = normalize(random_unit_complex(N, self.rng) * 0.3
                             + normalize(np.ones(N, dtype=complex)) * 0.7)
        self.law_fields = {
            "symmetry":    random_hermitian(N, self.rng, scale=0.5),
            "consistency": random_hermitian(N, self.rng, scale=0.5),
            "compactness": np.diag(np.linspace(-1, 1, N)).astype(complex) * 0.5,
        }
        self.gamma = dict(GAMMA_DEFAULTS)

    def effective_det_commit(self, current_tick):
        """Excitation pulse lowers commit threshold."""
        if current_tick < self.excitation_expires_at:
            return max(0.10, self.det_commit - self.excitation_strength)
        return self.det_commit

    def effective_p_commit(self, current_tick):
        if current_tick < self.excitation_expires_at:
            return max(0.20, self.p_commit - self.excitation_strength * 0.5)
        return self.p_commit

    def H_total(self):
        H = self.H_base.copy()
        for name, L in self.law_fields.items():
            H = H + self.gamma[name] * L
        for (gn, op, eta, source) in self.goals:
            H = H + eta * op
        for (gn, op, eta, source) in self.standing_goals:
            H = H + eta * op
        return H

    def step(self, J=None):
        H = self.H_total()
        I = np.eye(N, dtype=complex)
        A = I + 1j * H * DT / 2
        B = I - 1j * H * DT / 2
        try:
            self.psi = np.linalg.solve(A, B @ self.psi)
        except np.linalg.LinAlgError:
            pass
        if J is not None and np.linalg.norm(J) > 0:
            self.psi = self.psi + J * DT
        self.psi = normalize(self.psi)

    def evolve(self, J=None, steps=EVOLVE_STEPS):
        for i in range(steps):
            self.step(J=J if i == 0 else None)

    def arcs(self):
        if not self.mode_bank:
            return np.array([])
        return np.array([np.abs(np.vdot(m, self.psi)) ** 2 for m in self.mode_bank])

    def entropy_det(self):
        a = self.arcs()
        if len(a) == 0 or a.sum() < 1e-12:
            return 0.0, 0.0
        p = a / a.sum()
        p_nz = p[p > 1e-12]
        H_k = -float(np.sum(p_nz * np.log(p_nz)))
        H_0 = np.log(len(self.mode_bank)) if len(self.mode_bank) > 1 else 1.0
        Det_k = 1.0 - H_k / max(H_0, 1e-9)
        return H_k, Det_k

    def commit_check(self, evidence_pressure=0.0, current_tick=0):
        a = self.arcs()
        if len(self.mode_bank) < 2 or a.sum() < 1e-9:
            if self.bootstrap_used < BOOTSTRAP_MAX and evidence_pressure > 0.20:
                return True, "bootstrap"
            return False, None
        # Sections need genuine evidence pressure to commit.
        # Excitation does NOT substitute for evidence - it only lowers thresholds.
        if evidence_pressure < 0.15:
            return False, None
        p = a / a.sum()
        p_max = float(p.max())
        H_k, Det_k = self.entropy_det()
        max_overlap = float(a.max())
        novel_thresh = 0.30 / (1.0 + 0.05 * max(0, len(self.mode_bank) - 5))
        if max_overlap < novel_thresh and evidence_pressure > 0.25:
            return True, "novel_mode"
        det_th = self.effective_det_commit(current_tick)
        p_th = self.effective_p_commit(current_tick)
        if Det_k >= det_th and p_max >= p_th:
            return True, "entropic_flip"
        return False, None

    def commit(self, tick, reason):
        state = self.psi.copy()
        c = chi_of(state)
        a = self.arcs()
        mode_id = -1
        if reason in ("bootstrap", "novel_mode"):
            self.mode_bank.append(state.copy())
            self.mode_last_used.append(tick)
            mode_id = len(self.mode_bank) - 1
            if reason == "bootstrap":
                self.bootstrap_used += 1
        else:
            p = a / a.sum() if a.sum() > 0 else a
            mode_id = int(p.argmax())
            self.mode_bank[mode_id] = normalize(0.92 * self.mode_bank[mode_id] + 0.08 * state)
            self.mode_last_used[mode_id] = tick
        self.krimelack.append({"state": state, "chi": c, "tick": tick,
                               "mode_id": mode_id, "reason": reason})
        # arc-top history for resolution-effect metric
        if len(a) > 0:
            top = int(a.argmax())
            self.arc_top_history.append((tick, top))
            self.last_arc_top_id = top
        return c, mode_id, state

    def decay_modes(self, tick):
        new_bank, new_last = [], []
        pruned = 0
        for m, t_last in zip(self.mode_bank, self.mode_last_used):
            age = tick - t_last
            if age <= MODE_DECAY_TICKS:
                new_bank.append(m)
                new_last.append(t_last)
            else:
                shrink = max(0.0, 1.0 - 0.05 * (age - MODE_DECAY_TICKS) / 10)
                if shrink < 0.2:
                    pruned += 1
                    continue
                new_bank.append(m * shrink)
                new_last.append(t_last)
        self.mode_bank = new_bank
        self.mode_last_used = new_last
        return pruned

    def three_axis(self):
        a = self.arcs()
        if len(a) > 0 and a.sum() > 0:
            p = a / a.sum()
            p_nz = p[p > 1e-12]
            ent = float(-np.sum(p_nz * np.log(p_nz)))
            ent_norm = ent / max(np.log(len(a)), 1e-9) if len(a) > 1 else 0.0
            greed = float((a / a.sum()).max())
        else:
            ent_norm = 0.0
            greed = 0.0
        amps = np.abs(self.psi)
        coh = float(np.linalg.norm(amps - np.mean(amps)))
        coh_norm = min(1.0, coh / 1.0)
        return {"entropy": ent_norm, "coherence": coh_norm, "greed": greed}


# ---------- Atlas ----------
class ChiAtlas:
    def __init__(self):
        self.entries = defaultdict(list)
        self.merges = []
        self.deferrals = []
        self.requested_keyholes = []

    def add_claim(self, chi, section_name, mode_id, tick):
        self.entries[chi].append({"section": section_name, "mode_id": mode_id, "tick": tick})

    def conflicts(self):
        out = []
        for chi, claims in self.entries.items():
            sections = {c["section"] for c in claims}
            if len(sections) > 1:
                out.append((chi, claims))
        return out

    def density(self):
        if not self.entries:
            return 0.0
        ds = []
        for chi, claims in self.entries.items():
            ds.append(len({c["section"] for c in claims}))
        return float(np.mean(ds))


# ---------- System ----------
class System:
    def __init__(self, sections, rng):
        self.sections = {s.name: s for s in sections}
        self.atlas = ChiAtlas()
        self.tick = 0
        self.keyholes = []
        self.pending_goals = defaultdict(list)
        self.coordinator_fires = []
        self.deferred_conflicts = {}
        self.rng = rng
        self.system_log = defaultdict(list)
        self.section_self_evo_log = defaultdict(list)
        self.intro_krimelack = []
        self.intro_section = None
        # Awareness instrumentation
        self.deliberation_ticks = []
        self.routing_ticks = []
        self.coordinator_actions_log = []
        # External speaker (for conversation)
        self.external_speaker_buffer = deque(maxlen=20)
        self.grounding_section = None
        # Coherence-feedback (for conversation): track match rate between own utterances
        # and partner's recent utterances. Used to adapt heard-speaker goal strength.
        self.utterance_match_log = deque(maxlen=30)  # 1 = matched, 0 = didn't
        self.heard_speaker_strength = 0.70  # adaptive, stronger baseline

    def add_keyhole(self, sender, chi_lo, chi_hi, receiver, goal_strength=0.4):
        self.keyholes.append({"sender": sender, "chi_lo": chi_lo, "chi_hi": chi_hi,
                              "receiver": receiver, "goal_strength": goal_strength})

    def project_into(self, section, evidence):
        if section.map_inject is None or evidence is None:
            return None
        J = section.map_inject @ evidence
        nrm = np.linalg.norm(J)
        if nrm > 0:
            J = J * min(1.0, 0.5 / nrm) * 0.5
        return J

    def hear_speaker(self, utterance_template_vector, target_section_name, speak_section_name=None):
        """External speaker says something.
        - Becomes a goal in target (listen) section
        - Also becomes a goal in speak section (so response is biased to same template)
        - Seeds a mode in listener's bank if no similar mode exists
        """
        target = normalize(utterance_template_vector)
        op = goal_op_for_template(target)
        sec = self.sections[target_section_name]
        sec.standing_goals.append((f"heard_t{self.tick}", op, self.heard_speaker_strength, "external"))
        self.external_speaker_buffer.append({"tick": self.tick, "vec": target.copy()})
        # Also bias the speak section toward responding on the same template - STRONG
        if speak_section_name and speak_section_name in self.sections:
            sp = self.sections[speak_section_name]
            sp.standing_goals.append((f"heard_t{self.tick}", op, 1.0, "external"))
        # Seed mode in listener if novel
        if sec.mode_bank:
            overlaps = [np.abs(np.vdot(m, target))**2 for m in sec.mode_bank]
            if max(overlaps) < 0.40:
                sec.mode_bank.append(target.copy())
                sec.mode_last_used.append(self.tick)
        else:
            sec.mode_bank.append(target.copy())
            sec.mode_last_used.append(self.tick)

    def record_utterance_match(self, matched: bool):
        """Track utterance match rate, adapt heard-speaker strength."""
        self.utterance_match_log.append(1 if matched else 0)
        if len(self.utterance_match_log) >= 8:
            recent_rate = sum(self.utterance_match_log) / len(self.utterance_match_log)
            # Wider range: 0.30 (high match, light touch) to 1.10 (low match, force alignment)
            target = 0.30 + (1.10 - 0.30) * (1.0 - recent_rate)
            self.heard_speaker_strength = 0.85 * self.heard_speaker_strength + 0.15 * target

    def expire_standing_goals(self, heard_lifetime=35, handoff_lifetime=5, coord_lifetime=3):
        for sec in self.sections.values():
            kept = []
            for g in sec.standing_goals:
                gn = g[0]
                if gn.startswith("heard_t"):
                    age = self.tick - int(gn.split("_t")[1])
                    if age < heard_lifetime:
                        kept.append(g)
                elif gn.startswith("coord_displace_t"):
                    age = self.tick - int(gn.split("_t")[1])
                    if age < coord_lifetime:
                        kept.append(g)
                elif gn.startswith("hf_") and "_t" in gn:
                    try:
                        t_str = gn.rsplit("_t", 1)[1]
                        age = self.tick - int(t_str)
                        if age < handoff_lifetime:
                            kept.append(g)
                    except (ValueError, IndexError):
                        kept.append(g)
                else:
                    kept.append(g)
            sec.standing_goals = kept

    def tick_once(self, evidence_per_section, enable_self_evo=False,
                  coordinator_on=False, introspection_on=False, allow_rewiring=False):
        self.tick += 1
        # Snapshot arc-tops before evolution this tick (current arcs, not last committed)
        prev_arc_tops = {}
        for nm, sec in self.sections.items():
            a = sec.arcs()
            prev_arc_tops[nm] = int(a.argmax()) if len(a) > 0 else -1

        commits_this_tick = []
        for name, sec in self.sections.items():
            ev = evidence_per_section.get(name, None)
            J = self.project_into(sec, ev) if ev is not None else None
            evidence_pressure = float(np.linalg.norm(J)) if J is not None else 0.0
            for g in self.pending_goals.get(name, []):
                sec.goals.append(g)
            _, det_before = sec.entropy_det()
            sec.evolve(J=J)
            do_commit, reason = sec.commit_check(evidence_pressure=evidence_pressure,
                                                  current_tick=self.tick)
            committed_info = None
            if do_commit:
                chi, mode_id, state = sec.commit(self.tick, reason)
                self.atlas.add_claim(chi, name, mode_id, self.tick)
                committed_info = {"section": name, "chi": chi, "mode_id": mode_id,
                                   "reason": reason,
                                   "det_before": det_before,
                                   "det_after": sec.entropy_det()[1]}
                commits_this_tick.append(committed_info)
            sec.goals = [g for g in sec.goals if g[3] == "permanent"]
        self.pending_goals.clear()

        # Keyhole handoffs - EXCITATION PULSES (not content goals)
        # Sender's commit fires a temporary commit-threshold relaxation in receiver.
        # Receiver decides WHAT to commit based on its OWN evidence + state.
        # This is the corrected handoff mechanism.
        for c in commits_this_tick:
            sender = c["section"]
            chi = c["chi"]
            det_rose = c["det_after"] > c["det_before"] + 0.01
            if not det_rose and c["reason"] == "entropic_flip":
                self.system_log["weak_commits"].append((self.tick, sender, chi))
                continue
            if c["reason"] in ("bootstrap", "novel_mode"):
                continue
            for kh in self.keyholes:
                if kh["sender"] != sender:
                    continue
                if kh["chi_lo"] <= chi <= kh["chi_hi"]:
                    receiver = kh["receiver"]
                    rec_sec = self.sections[receiver]
                    # Set excitation in receiver
                    rec_sec.excitation_expires_at = self.tick + 8  # ~one phase
                    rec_sec.excitation_strength = kh["goal_strength"]

        # Coordinator
        coordinator_fired_this_tick = False
        if coordinator_on:
            conflicts = self.atlas.conflicts()
            unresolved = []
            for (chi, claims) in conflicts:
                key = (chi, frozenset(c["section"] for c in claims))
                if key in self.deferred_conflicts and self.deferred_conflicts[key] > self.tick:
                    continue
                unresolved.append((chi, claims))
            for (chi, claims) in unresolved:
                sec_names = {c["section"] for c in claims}
                self.coordinator_fires.append({"tick": self.tick, "chi": chi,
                                                "n_claims": len(claims),
                                                "sections": list(sec_names)})
                coordinator_fired_this_tick = True
                connected = any(kh["sender"] in sec_names and kh["receiver"] in sec_names
                                for kh in self.keyholes)
                if connected:
                    self.atlas.merges.append({"tick": self.tick, "chi": chi,
                                               "sections": list(sec_names)})
                    self.deferred_conflicts[(chi, frozenset(sec_names))] = self.tick + 30
                    # Strong displacement: inject orthogonal kick into conflicting sections' psi
                    for sn in sec_names:
                        if sn in self.sections:
                            sec_obj = self.sections[sn]
                            kick = random_unit_complex(N, self.rng) * 0.45
                            sec_obj.psi = normalize(sec_obj.psi + kick)
                            sec_obj.excitation_expires_at = max(sec_obj.excitation_expires_at,
                                                                  self.tick - 1)
                    self.coordinator_actions_log.append({"tick": self.tick, "action": "merge",
                                                          "sections": list(sec_names)})
                else:
                    if allow_rewiring:
                        sec_list = list(sec_names)
                        shared = 0
                        for c2, ent in self.atlas.entries.items():
                            secs2 = {e["section"] for e in ent}
                            if set(sec_list).issubset(secs2):
                                shared += 1
                        if shared >= 2:
                            self.atlas.requested_keyholes.append({"tick": self.tick,
                                                                   "sections": sec_list, "chi": chi})
                            a, b = sec_list[0], sec_list[1]
                            self.add_keyhole(a, chi - 1, chi + 1, b, 0.3)
                            self.add_keyhole(b, chi - 1, chi + 1, a, 0.3)
                            self.coordinator_actions_log.append({"tick": self.tick, "action": "rewire",
                                                                  "sections": list(sec_names)})
                    self.atlas.deferrals.append({"tick": self.tick, "chi": chi,
                                                  "sections": list(sec_names)})
                    self.deferred_conflicts[(chi, frozenset(sec_names))] = self.tick + 20

        # Awareness instrumentation: deliberation vs routing
        if coordinator_fired_this_tick:
            self.deliberation_ticks.append(self.tick)
        elif commits_this_tick:
            self.routing_ticks.append(self.tick)

        # Introspection
        if introspection_on and self.intro_section is not None:
            snap = self._atlas_snapshot()
            self.intro_section.evolve(J=snap)
            do_commit, reason = self.intro_section.commit_check(evidence_pressure=float(np.linalg.norm(snap)))
            if do_commit:
                chi, mode_id, state = self.intro_section.commit(self.tick, reason)
                self.intro_krimelack.append({"state": state, "chi": chi, "tick": self.tick,
                                              "mode_id": mode_id, "reason": reason,
                                              "atlas_snapshot": snap.copy()})

        # Mode decay
        for sec in self.sections.values():
            sec.decay_modes(self.tick)

        # Self-evolution with gamma drift-toward-default
        # Conservative: require persistent out-of-range and use moderate learning rate
        if enable_self_evo and self.tick % SELF_EVO_PERIOD == 0:
            for sec in self.sections.values():
                ax = sec.three_axis()
                sec.out_of_range_streak["entropy"] = sec.out_of_range_streak["entropy"] + 1 if ax["entropy"] < 0.3 else 0
                sec.out_of_range_streak["coherence"] = sec.out_of_range_streak["coherence"] + 1 if ax["coherence"] < 0.3 else 0
                sec.out_of_range_streak["greed"] = sec.out_of_range_streak["greed"] + 1 if ax["greed"] > 0.7 else 0
                eta = 0.04
                dgamma = {"symmetry": 0.0, "consistency": 0.0, "compactness": 0.0}
                if sec.out_of_range_streak["entropy"] >= 2:
                    dgamma["symmetry"] -= eta
                    dgamma["consistency"] -= eta
                if sec.out_of_range_streak["coherence"] >= 2:
                    dgamma["consistency"] += eta
                if sec.out_of_range_streak["greed"] >= 2:
                    dgamma["compactness"] += eta
                for k in dgamma:
                    drift = (GAMMA_DEFAULTS[k] - sec.gamma[k]) * GAMMA_DRIFT
                    dgamma[k] += drift
                for k, dv in dgamma.items():
                    sec.gamma[k] = float(np.clip(sec.gamma[k] + dv, *GAMMA_BOUNDS))
                self.section_self_evo_log[sec.name].append({
                    "tick": self.tick, "three_axis": ax, "gamma": dict(sec.gamma)})

        # Resolution-effect: did arc-tops in conflict sections change after a coordinator action?
        # (Measured by looking at arc-tops BEFORE the action vs after.
        # Arc-top updates happen on commits. The displacement kick gives some psi rotation
        # which alters arcs immediately — record the pre-action arcs vs current arcs.)
        if coordinator_fired_this_tick and self.coordinator_actions_log:
            last_action = self.coordinator_actions_log[-1]
            if last_action["tick"] == self.tick:
                # Record arc-tops AFTER for sections involved
                # We compare against arc *snapshots* taken pre-action (prev_arc_tops captured at start of tick)
                arc_changes = 0
                for nm in last_action["sections"]:
                    if nm not in self.sections:
                        continue
                    sec_obj = self.sections[nm]
                    if len(sec_obj.mode_bank) == 0:
                        continue
                    current_arcs = sec_obj.arcs()
                    current_top = int(current_arcs.argmax()) if len(current_arcs) > 0 else -1
                    if current_top != prev_arc_tops.get(nm, -1):
                        arc_changes += 1
                last_action["arc_changes"] = arc_changes
                last_action["arc_targets"] = len(last_action["sections"])

        # Expire standing goals
        self.expire_standing_goals()

        # Log
        self.system_log["tick"].append(self.tick)
        self.system_log["n_commits"].append(len(commits_this_tick))
        self.system_log["atlas_size"].append(sum(len(v) for v in self.atlas.entries.values()))
        self.system_log["atlas_chi_classes"].append(len(self.atlas.entries))
        self.system_log["atlas_density"].append(self.atlas.density())
        self.system_log["n_conflicts"].append(len(self.atlas.conflicts()))
        self.system_log["coordinator_fired"].append(1 if coordinator_fired_this_tick else 0)
        all_ax = [s.three_axis() for s in self.sections.values()]
        for k in ("entropy", "coherence", "greed"):
            self.system_log[f"system_{k}"].append(float(np.mean([a[k] for a in all_ax])))

        return commits_this_tick

    def _atlas_snapshot(self):
        """Compress current atlas + section three-axis into a complex N-vector for introspection."""
        v = np.zeros(N, dtype=complex)
        # Atlas component: chi values weighted by section diversity
        section_to_idx = {nm: i % N for i, nm in enumerate(sorted(self.sections.keys()))}
        for chi, claims in self.atlas.entries.items():
            # Each claim contributes at index = (chi + section_idx) mod N
            for c in claims[-5:]:  # last 5 claims weighted most
                sec_idx = section_to_idx.get(c["section"], 0)
                idx = (chi + sec_idx) % N
                v[idx] += np.exp(1j * (chi / N) * 2 * np.pi)
        # Three-axis component: encode each section's current state
        for nm, sec in self.sections.items():
            ax = sec.three_axis()
            sec_idx = section_to_idx[nm]
            v[sec_idx] += ax["entropy"] * np.exp(1j * 0.5 * np.pi)
            v[(sec_idx + 1) % N] += ax["coherence"] * np.exp(1j * 1.0 * np.pi)
            v[(sec_idx + 2) % N] += ax["greed"] * np.exp(1j * 1.5 * np.pi)
        if np.linalg.norm(v) > 0:
            v = normalize(v)
        return v

    def coordinator_resolution_effect(self):
        """How often did coordinator actions actually change arc-tops?"""
        actions_with_change = [a for a in self.coordinator_actions_log if a.get("arc_changes", 0) > 0]
        if not self.coordinator_actions_log:
            return 0.0
        return len(actions_with_change) / len(self.coordinator_actions_log)
