"""
V7 DNA Recipe Engine — V7-UNCAGE: unnamed-pool substrate.
GL-BRIEF-V7-UNCAGE-WC-20260612-01

Replaces lexical-category sections (N/V/Adj/Adv + closed-class) with three
unnamed pools (pool_a, pool_b, pool_c).  Words distribute round-robin with
no grammatical classification.  Emission runs all three pools simultaneously
(no rotation/rhythm).  Self-voice via espeak-ng.

Keeps: NMDA gates, drive_tracker, intro/aware, quiet_tick, apply_feedback,
save/load, event_log, all assemblage primitives.
"""
import threading, json, os, time, subprocess, base64
import numpy as np
from collections import defaultdict

from dsf_ai_service.substrate.assemblage import (
    Section, System, N, normalize, random_unit_complex, goal_op_for_template,
)
from dsf_ai_service.substrate.gl_nmda import (
    CoincidenceGate, context_no_recent_drive, update_drive_tracker,
)
from dsf_ai_service.substrate.gl_plasticity import (
    install_plasticity, decay_plasticity, reinforce_mode,
)
from dsf_ai_service.substrate.dna_recipe.phase_gating import (
    make_projection, first_commit_per_section, make_phase_gater,
)

# ---- Pool architecture ----
POOL_NAMES = ["pool_a", "pool_b", "pool_c"]
ALL_SECTIONS = POOL_NAMES + ["listen", "intro", "aware"]
VOICE_PROFILE = {"voice": "en+f3", "pitch": 90, "speed": 130}


def seed_vocab_from_engine(engine):
    """Read v6 engine vocab and distribute round-robin across pools."""
    if engine is None:
        raise ValueError("seed_vocab_from_engine requires a non-None engine")
    # engine.vocab is a set of words she has actually heard
    vocab_set = getattr(engine, "vocab", None) or set()
    if not vocab_set:
        raise ValueError("engine has no vocab; cannot seed substrate")
    result = {p: [] for p in POOL_NAMES}
    all_words = []
    for w in sorted(vocab_set):  # sorted for deterministic distribution
        w = w.lower().strip()
        if w and w not in all_words:
            all_words.append(w)
    for i, w in enumerate(all_words):
        pool = POOL_NAMES[i % len(POOL_NAMES)]
        result[pool].append(w)
    return result


def _make_zero_section(name, rng, role="general"):
    """Helper: section with zeroed Hamiltonian."""
    sec = Section(name=name, rng=rng, role=role)
    sec.H_base = np.zeros((N, N), dtype=complex)
    sec.law_fields = {k: np.zeros((N, N), dtype=complex)
                      for k in ("symmetry", "consistency", "compactness")}
    return sec


class V7Session:
    """Per-session v7 substrate with unnamed pool sections."""

    def __init__(self, session_id, rng_seed=None, engine=None):
        if engine is None:
            raise ValueError("V7Session requires a non-None engine")
        self.session_id = session_id
        self.lock = threading.Lock()
        self.created_at = time.time()
        from dsf_ai_service.substrate.event_log import EventLog
        self.event_log = EventLog(STATE_DIR, session_id)
        seed = rng_seed or hash(session_id) % (2**31)
        self.rng = np.random.default_rng(seed)
        self.vocab = seed_vocab_from_engine(engine)
        self.sys_, self.token_vec, self.intro_vec, self.intro_modes, \
            self.aware_vec, self.aware_modes = self._build_system()
        for sn in POOL_NAMES + ["intro", "aware"]:
            if sn in self.sys_.sections:
                install_plasticity(self.sys_.sections[sn], initial_strength=1.0)
        self.drive_tracker = {}
        self.intro_gate = CoincidenceGate(
            section_name="intro",
            context_fn=context_no_recent_drive(
                self.drive_tracker, sections=tuple(POOL_NAMES),
                quiet_thresh=0.45),
            drive_thresh=0.05, ltp_boost=0.05)
        self.aware_gate = CoincidenceGate(
            section_name="aware",
            context_fn=lambda sys_: (
                len(sys_.sections["intro"].krimelack) > 0 and
                (sys_.tick - sys_.sections["intro"].krimelack[-1]["tick"]) <= 5),
            drive_thresh=0.05, ltp_boost=0.05)
        self.last_intro_state = None
        self.last_aware_state = None
        self.last_emissions = []
        self.last_nmda_events = []
        self.last_routing_log = []
        self.intro_commit_history = []
        self.aware_commit_history = []
        self.tick_at_last_converse = 0
        self._last_converse_time = time.time()

    def _build_system(self):
        rng = self.rng
        secs = []
        # Pool sections (full Hamiltonian)
        for pool in POOL_NAMES:
            secs.append(Section(name=pool, rng=rng, role="subject_like"))
        # listen/intro/aware (zeroed Hamiltonian)
        secs.append(_make_zero_section("listen", rng))
        secs.append(_make_zero_section("intro", rng, role="intro"))
        secs.append(_make_zero_section("aware", rng, role="intro"))
        for s in secs:
            s.map_inject = make_projection(N, 8, rng)
        sys_ = System(secs, rng)

        # Install vocab
        token_vec = {}
        for pool, words in self.vocab.items():
            if pool not in sys_.sections:
                continue
            sec = sys_.sections[pool]
            for word in words:
                v = random_unit_complex(N, rng)
                sec.mode_bank.append(v.copy())
                sec.mode_last_used.append(0)
                sec.mode_strength.append(1.0)
                token_vec[(pool, word)] = v
                sys_.sections["listen"].mode_bank.append(v.copy())
                sys_.sections["listen"].mode_last_used.append(0)
                sys_.sections["listen"].mode_strength.append(1.0)

        # Intro + aware modes
        intro_modes = ["i_quiet", "i_hear", "i_emit"]
        intro_vec = {}
        for name in intro_modes:
            v = random_unit_complex(N, rng)
            sys_.sections["intro"].mode_bank.append(v.copy())
            sys_.sections["intro"].mode_last_used.append(0)
            sys_.sections["intro"].mode_strength.append(1.0)
            intro_vec[name] = v
        aware_modes = ["aware_quiet", "aware_listening", "aware_emitting"]
        aware_vec = {}
        for name in aware_modes:
            v = random_unit_complex(N, rng)
            sys_.sections["aware"].mode_bank.append(v.copy())
            sys_.sections["aware"].mode_last_used.append(0)
            sys_.sections["aware"].mode_strength.append(1.0)
            aware_vec[name] = v
        for sec in sys_.sections.values():
            sec.snapshot_initial_modes()
        return sys_, token_vec, intro_vec, intro_modes, aware_vec, aware_modes

    # ---- Word routing ----
    def lookup_or_install(self, word):
        """Return (word_vec, pool_name, was_new). No classification."""
        word = word.lower().strip(".,?!;:'\"")
        if not word:
            return None, None, False
        # Check existing pools
        for pool in POOL_NAMES:
            words = self.vocab.get(pool, [])
            if word in words:
                idx = words.index(word)
                sec = self.sys_.sections[pool]
                if idx < len(sec.mode_bank):
                    return sec.mode_bank[idx], pool, False
        # New word: install in pool with fewest modes
        counts = [(len(self.sys_.sections[p].mode_bank), p) for p in POOL_NAMES]
        counts.sort(key=lambda x: x[0])
        pool = counts[0][1]
        sec = self.sys_.sections[pool]
        word_vec = random_unit_complex(N, self.rng)
        sec.mode_bank.append(word_vec.copy())
        sec.mode_last_used.append(self.sys_.tick)
        sec.mode_strength.append(1.0)
        self.sys_.sections["listen"].mode_bank.append(word_vec.copy())
        self.sys_.sections["listen"].mode_last_used.append(self.sys_.tick)
        self.sys_.sections["listen"].mode_strength.append(1.0)
        self.vocab.setdefault(pool, [])
        self.vocab[pool].append(word)
        self.token_vec[(pool, word)] = word_vec
        sec.snapshot_initial_modes()
        self.sys_.sections["listen"].snapshot_initial_modes()
        self.event_log.write("vocab_install", slot=pool, word=word)
        return word_vec, pool, True

    # ---- Main conversation ----
    def converse(self, text, source="ui"):
        with self.lock:
            tokens = [t.lower().strip(".,?!;:'\"") for t in text.split() if t.strip()]
            if not tokens:
                return self._empty_response("empty input")
            # Per-turn psi + goals reset
            for sn in ALL_SECTIONS:
                if sn not in self.sys_.sections:
                    continue
                sec = self.sys_.sections[sn]
                sec.psi = normalize(
                    random_unit_complex(N, self.rng) * 0.3 +
                    normalize(np.ones(N, dtype=complex)) * 0.7)
                sec.standing_goals = []
                sec.goals = []
            self.drive_tracker.clear()
            routing_log, nmda_events = [], []

            # PHASE 1: Route words
            heard = {}  # pool -> [(word, word_vec)]
            any_routed = False
            for word in tokens:
                word_vec, pool, was_new = self.lookup_or_install(word)
                routing_log.append({"word": word, "routed_to": pool,
                                    "newly_installed": was_new} if pool else
                                   {"word": word, "routed_to": None, "reason": "skipped"})
                if pool and word_vec is not None:
                    heard.setdefault(pool, []).append((word, word_vec))
                    any_routed = True
            if not any_routed:
                return self._empty_response("no words routed")

            # PHASE 2: Listen-accumulate (15 noisy ticks per word into pool + listen)
            for sn in ALL_SECTIONS:
                if sn in self.sys_.sections:
                    self.sys_.sections[sn]._emit_phase = True
            accumulated = {}  # pool -> accumulated vec
            for pool, word_list in heard.items():
                acc = np.zeros(N, dtype=complex)
                for word, word_vec in word_list:
                    key = (pool, word)
                    target = self.token_vec.get(key, word_vec)
                    for _ in range(15):
                        noisy = normalize(target + 0.10 * (
                            self.rng.standard_normal(N) + 1j * self.rng.standard_normal(N)))
                        acc += noisy
                        self.sys_.tick_once({pool: noisy, "listen": noisy},
                                            enable_self_evo=True,
                                            coordinator_on=False, introspection_on=False,
                                            allow_rewiring=False)
                accumulated[pool] = normalize(acc)
            self.last_intro_state = "i_hear"
            self.intro_commit_history.append({"state": "i_hear", "tick": self.sys_.tick})
            self.intro_commit_history = self.intro_commit_history[-10:]
            for sn in ALL_SECTIONS:
                if sn != "listen" and sn in self.sys_.sections:
                    self.sys_.sections[sn]._emit_phase = False

            # PHASE 3: Derive drives per pool
            drives = {}
            for pool in POOL_NAMES:
                snap = accumulated.get(pool)
                sec = self.sys_.sections[pool]
                if snap is None or np.linalg.norm(snap) == 0:
                    drives[pool] = random_unit_complex(N, self.rng) * 0.1
                    continue
                weights = []
                for mid, mvec in enumerate(sec.mode_bank):
                    d = float(np.abs(np.vdot(mvec, snap)) ** 2)
                    s = sec.mode_strength[mid] if mid < len(sec.mode_strength) else 1.0
                    weights.append((mid, d * s, mvec))
                weights.sort(key=lambda x: -x[1])
                bias = sum((w * v for _, w, v in weights[:2]), np.zeros(N, dtype=complex))
                drives[pool] = normalize(bias) if np.linalg.norm(bias) > 0 \
                    else random_unit_complex(N, self.rng)
            for pool, drv in drives.items():
                if pool in self.sys_.sections:
                    self.sys_.sections[pool].psi = drv.copy()

            # PHASE 4: Emit — all three pools active simultaneously
            for sec in self.sys_.sections.values():
                sec._emit_phase = True
            emit_commits = []
            no_new_streak = 0
            response_tokens = []
            seen_commit_keys = set()
            for t in range(120):
                for pool in POOL_NAMES:
                    decay_plasticity(self.sys_.sections[pool], decay=0.998)
                # Evidence: all driven pools, re-noised
                ev = {}
                for pool in POOL_NAMES:
                    d = drives.get(pool)
                    if d is not None:
                        ev[pool] = normalize(d + 0.10 * (
                            self.rng.standard_normal(N) + 1j * self.rng.standard_normal(N)))
                commits = self.sys_.tick_once(ev, enable_self_evo=True,
                                              coordinator_on=False, introspection_on=False,
                                              allow_rewiring=False)
                new_this_tick = False
                for c in commits:
                    if c["section"] in POOL_NAMES:
                        ckey = (c["section"], c["mode_id"])
                        if ckey not in seen_commit_keys:
                            seen_commit_keys.add(ckey)
                            emit_commits.append(c)
                            w = self._mode_to_word(c["section"], c["mode_id"])
                            if w:
                                response_tokens.append({
                                    "section": c["section"], "token": w,
                                    "emit_tick": self.sys_.tick,
                                    "mode_strength": round(
                                        self.sys_.sections[c["section"]].mode_strength[c["mode_id"]]
                                        if c["mode_id"] < len(self.sys_.sections[c["section"]].mode_strength)
                                        else 0.0, 3),
                                    "arc": round(float(self.sys_.sections[c["section"]].arcs()[c["mode_id"]]) if c["mode_id"] < len(self.sys_.sections[c["section"]].arcs()) else 0.0, 3),
                                })
                            new_this_tick = True
                if new_this_tick:
                    no_new_streak = 0
                else:
                    no_new_streak += 1
                if no_new_streak >= 10:
                    break
                if len(response_tokens) >= 20:
                    break
            for sec in self.sys_.sections.values():
                sec._emit_phase = False

            # POST-EMIT: intro + aware NMDA passes
            for c in emit_commits:
                update_drive_tracker(self.drive_tracker,
                                     {c["section"]: np.ones(N, dtype=complex) * 0.5})
            self._nmda_pass("intro", self.intro_vec.get("i_emit"),
                            self.intro_gate, self.intro_modes,
                            nmda_events, "intro_state", "intro_commit_history")
            aware_name = {"i_quiet": "aware_quiet", "i_hear": "aware_listening",
                          "i_emit": "aware_emitting"}.get(
                self.last_intro_state or "i_emit", "aware_emitting")
            self._nmda_pass("aware", self.aware_vec.get(aware_name),
                            self.aware_gate, self.aware_modes,
                            nmda_events, "aware_state", "aware_commit_history")

            self.last_emissions = emit_commits
            self.last_nmda_events = nmda_events
            self.last_routing_log = routing_log
            self.tick_at_last_converse = self.sys_.tick
            self._last_converse_time = time.time()

            # Self-voice synthesis
            voice_b64 = None
            if response_tokens:
                voice_b64 = self._synthesize_self_voice(
                    [t["token"] for t in response_tokens])

            self.event_log.write("converse",
                                 text=" ".join(tokens),
                                 emitted=[t.get("token", "") for t in response_tokens],
                                 tick=self.sys_.tick)
            resp = {
                "response_tokens": response_tokens,
                "routing_log": routing_log,
                "nmda_events": nmda_events[-20:],
                "introspection": {"reported_state": self.last_intro_state or "i_quiet",
                                  "tick": self.sys_.tick,
                                  "recent_commits": self.intro_commit_history[-3:]},
                "awareness": {"reported_state": self.last_aware_state or "aware_quiet",
                              "tick": self.sys_.tick,
                              "recent_commits": self.aware_commit_history[-3:]},
                "mode_strengths": self._get_mode_strengths(),
                "raw_emissions": [{"section": c["section"], "mode_id": c["mode_id"],
                                   "reason": c["reason"]} for c in emit_commits[-20:]],
                "unknown_words": [r["word"] for r in routing_log if r.get("routed_to") is None],
            }
            if voice_b64:
                resp["self_voice_audio_b64"] = voice_b64
            return resp

    def _synthesize_self_voice(self, tokens):
        """Synthesize speech via espeak-ng. Returns base64 WAV or None."""
        text = " ".join(tokens)
        wav_path = "/tmp/utt.wav"
        try:
            subprocess.run([
                "espeak-ng",
                "-v", VOICE_PROFILE["voice"],
                "-p", str(VOICE_PROFILE["pitch"]),
                "-s", str(VOICE_PROFILE["speed"]),
                "-w", wav_path,
                text,
            ], check=True, timeout=10, capture_output=True)
            with open(wav_path, "rb") as f:
                wav_bytes = f.read()
            b64 = base64.b64encode(wav_bytes).decode("ascii")
            self.event_log.write("self_voice", source="self_voice",
                                 text=text, bytes_len=len(wav_bytes))
            return b64
        except Exception as e:
            print(f"[v7-voice] synthesis failed: {e}")
            return None

    def _nmda_pass(self, sec_name, target_vec, gate, mode_names, nmda_events,
                   state_attr, history_attr):
        """Unified post-emit NMDA pass for intro/aware sections."""
        if target_vec is None:
            return
        for _ in range(10):
            noisy = normalize(target_vec + 0.05 * (
                self.rng.standard_normal(N) + 1j * self.rng.standard_normal(N)))
            ev = {sec_name: noisy}
            if sec_name == "intro":
                update_drive_tracker(self.drive_tracker, ev)
            self.sys_.tick_once(ev, enable_self_evo=True,
                                coordinator_on=False, introspection_on=False,
                                allow_rewiring=False)
            sec = self.sys_.sections[sec_name]
            while len(sec.mode_bank) > len(mode_names):
                sec.mode_bank.pop()
                sec.mode_last_used.pop()
            fired, mode_id, eval_d = gate.check_and_fire(self.sys_)
            eval_d["tick"] = self.sys_.tick
            eval_d["fired"] = fired
            if sec_name == "intro":
                eval_d["drive_tracker"] = {k: round(v, 4) for k, v in self.drive_tracker.items()}
            nmda_events.append(eval_d)
            if fired and mode_id is not None and mode_id < len(mode_names):
                new_state = mode_names[mode_id]
                setattr(self, "last_" + state_attr, new_state)
                hist = getattr(self, history_attr)
                hist.append({"state": new_state, "tick": self.sys_.tick})
                while len(hist) > 10:
                    hist.pop(0)

    def _empty_response(self, reason):
        return {
            "response_tokens": [], "routing_log": [],
            "nmda_events": [],
            "introspection": {"reported_state": "i_quiet",
                              "tick": self.sys_.tick, "recent_commits": []},
            "awareness": {"reported_state": "aware_quiet",
                          "tick": self.sys_.tick, "recent_commits": []},
            "mode_strengths": self._get_mode_strengths(),
            "raw_emissions": [], "unknown_words": [],
            "honest_silence_reason": reason,
        }

    def quiet_tick(self, n_ticks=1):
        """Quiet ticks — substrate Default Mode. C4: evaluate intro gate."""
        with self.lock:
            results = []
            for _ in range(n_ticks):
                result = self.sys_.replay_tick(rng=self.rng)
                update_drive_tracker(self.drive_tracker, {})
                i_fired, i_mode, i_eval = self.intro_gate.check_and_fire(self.sys_)
                i_eval.update(tick=self.sys_.tick, fired=i_fired, source="quiet_tick")
                if not hasattr(self, '_quiet_nmda_events'):
                    self._quiet_nmda_events = []
                self._quiet_nmda_events.append(i_eval)
                self._quiet_nmda_events = self._quiet_nmda_events[-20:]
                if i_fired and i_mode is not None and i_mode < len(self.intro_modes):
                    self.last_intro_state = self.intro_modes[i_mode]
                    self.intro_commit_history.append(
                        {"state": self.last_intro_state, "tick": self.sys_.tick})
                    self.intro_commit_history = self.intro_commit_history[-10:]
                    if len(self.intro_commit_history) <= 1 or \
                       self.intro_commit_history[-1]["state"] != \
                       self.intro_commit_history[-2].get("state"):
                        print(f"[v7-intro] FIRED during quiet: mode={i_mode} "
                              f"state={self.last_intro_state} tick={self.sys_.tick}")
                results.append(result)
            total_r = sum(len(r["replayed"]) for r in results)
            total_c = sum(len(r["commits"]) for r in results)
            self._last_replay_result = {"replayed": total_r, "commits": total_c, "ticks": len(results)}
            if total_r > 0:
                self.event_log.write("quiet", n_ticks=len(results),
                                     replayed=total_r, commits=total_c)
            return results

    def apply_feedback(self, correct, expected_tokens=None):
        """Supervised LTP from thumbs-up/down."""
        with self.lock:
            affected = []
            for pool in POOL_NAMES:
                sec = self.sys_.sections[pool]
                if not hasattr(sec, "mode_strength"):
                    continue
                arcs = sec.arcs()
                if len(arcs) == 0:
                    continue
                top = int(arcs.argmax())
                if correct:
                    reinforce_mode(sec, top, boost=0.05, ceiling=2.5)
                else:
                    sec.mode_strength[top] = max(0.0, sec.mode_strength[top] - 0.02)
                affected.append({"section": pool, "mode_id": top,
                                 "new_strength": sec.mode_strength[top]})
            self.event_log.write("feedback", correct=correct,
                                 affected=[{"section": a["section"], "mode_id": a["mode_id"],
                                            "strength": a["new_strength"]} for a in affected])
            return {"ltp_applied": correct, "affected_modes": affected}

    def get_state(self, engine=None):
        """Snapshot for UI panel polling."""
        with self.lock:
            state = {
                "tick": self.sys_.tick,
                "introspection": self.last_intro_state or "i_quiet",
                "intro_recent": self.intro_commit_history[-3:],
                "awareness": self.last_aware_state or "aware_quiet",
                "aware_recent": self.aware_commit_history[-3:],
                "mode_strengths": self._get_mode_strengths(),
                "nmda_events": self.last_nmda_events[-10:],
                "routing_log": self.last_routing_log,
                "n_commits_total": sum(len(s.krimelack) for s in self.sys_.sections.values()),
                "intro_krimelack_count": len(self.sys_.sections["intro"].krimelack),
                "aware_krimelack_count": len(self.sys_.sections["aware"].krimelack),
                "intro_krimelack_recent": [
                    {"tick": k["tick"], "mode_id": k["mode_id"],
                     "salience": round(k.get("salience", 0), 3)}
                    for k in self.sys_.sections["intro"].krimelack[-5:]],
                "aware_krimelack_recent": [
                    {"tick": k["tick"], "mode_id": k["mode_id"],
                     "salience": round(k.get("salience", 0), 3)}
                    for k in self.sys_.sections["aware"].krimelack[-5:]],
                "last_replay": getattr(self, "_last_replay_result", None),
                "bridge_active": hasattr(self, "_bridge") and self._bridge is not None,
                "vocab_counts": {p: len(self.vocab.get(p, [])) for p in POOL_NAMES},
                "last_response_tokens": [t.get("token", "") for t in
                                         getattr(self, "last_emissions", [])[-10:]],
            }
            if engine is not None:
                state["v6_vocab_count"] = len(getattr(engine, "vocab", set()))
                atlas = getattr(self.sys_, "atlas", None)
                state["atlas_count"] = len(atlas.entries) if atlas else 0
            return state

    def _mode_to_word(self, pool_name, mode_id):
        toks = self.vocab.get(pool_name, [])
        return toks[mode_id] if mode_id < len(toks) else None

    def _get_mode_strengths(self):
        out = {}
        for pool in POOL_NAMES:
            sec = self.sys_.sections[pool]
            strengths = {}
            toks = self.vocab.get(pool, [])
            if hasattr(sec, "mode_strength"):
                for i, tok in enumerate(toks):
                    if i < len(sec.mode_strength):
                        strengths[tok] = round(sec.mode_strength[i], 3)
            out[pool] = strengths
        return out

    # ---- Serialization ----
    def _serialize_section(self, sec):
        return {
            "name": sec.name,
            "psi_re": sec.psi.real.tolist(),
            "psi_im": sec.psi.imag.tolist(),
            "mode_bank_re": [m.real.tolist() for m in sec.mode_bank],
            "mode_bank_im": [m.imag.tolist() for m in sec.mode_bank],
            "mode_last_used": list(sec.mode_last_used),
            "mode_strength": list(getattr(sec, "mode_strength", [])),
            "gamma": dict(sec.gamma),
            "det_commit": sec.det_commit, "p_commit": sec.p_commit,
            "tick": getattr(sec, "tick", 0),
            "krimelack_count": len(sec.krimelack),
            "krimelack": [
                {"chi": int(k["chi"]), "tick": int(k["tick"]),
                 "mode_id": int(k["mode_id"]), "reason": k.get("reason", ""),
                 "salience": float(k.get("salience", 0.0))}
                for k in sec.krimelack[-200:]],
        }

    def _restore_section(self, sec, data):
        sec.psi = np.array(data["psi_re"]) + 1j * np.array(data["psi_im"])
        sec.mode_bank = [np.array(r) + 1j * np.array(i)
                         for r, i in zip(data["mode_bank_re"], data["mode_bank_im"])]
        sec.mode_last_used = list(data.get("mode_last_used", [0] * len(sec.mode_bank)))
        if "mode_strength" in data:
            sec.mode_strength = list(data["mode_strength"])
        if "gamma" in data:
            sec.gamma = dict(data["gamma"])

    def compact(self):
        data = self.to_json()
        save_session(self)
        self.event_log.truncate_before(self.event_log.count)
        return data

    def to_json(self):
        state = {
            "schema_version": 4,
            "session_id": self.session_id,
            "event_seq": self.event_log.count,
            "vocab": {k: list(v) for k, v in self.vocab.items()},
            "tick": self.sys_.tick,
            "intro_state": self.last_intro_state,
            "aware_state": self.last_aware_state,
            "sections": {},
            "atlas": {str(k): v for k, v in self.sys_.atlas.entries.items()},
            "keyholes": [
                {"sender": kh["sender"], "chi_lo": kh["chi_lo"],
                 "chi_hi": kh["chi_hi"], "receiver": kh["receiver"],
                 "goal_strength": kh["goal_strength"]}
                for kh in self.sys_.keyholes],
        }
        for sn in ALL_SECTIONS:
            if sn in self.sys_.sections:
                state["sections"][sn] = self._serialize_section(self.sys_.sections[sn])
        return state

    _TOY_TOKENS = frozenset({
        "cow", "moon", "jumped", "ran", "fence", "milk",
        "thing", "bears", "dish", "sleeps",
    })

    def _validate_vocab(self, vocab):
        """Raise ValueError if vocab is contaminated with toy tokens or too small."""
        total_vocab = sum(len(v) for v in vocab.values())
        if total_vocab < 50:
            raise ValueError(
                "snapshot vocab below threshold; discarding contaminated state")
        for pool, words in vocab.items():
            for w in words:
                if w.lower().strip() in self._TOY_TOKENS:
                    raise ValueError(
                        "snapshot contains toy vocab; discarding contaminated state")

    def load_from_json(self, data):
        with self.lock:
            sv = data.get("schema_version", 1)
            if sv <= 3:
                # v1/v2/v3: flatten all vocab into one list, redistribute round-robin
                all_words = []
                raw_vocab = data.get("vocab", {})
                for slot, words in raw_vocab.items():
                    for w in words:
                        wl = w.lower().strip()
                        if wl and wl not in all_words:
                            all_words.append(wl)
                new_vocab = {p: [] for p in POOL_NAMES}
                for i, w in enumerate(all_words):
                    pool = POOL_NAMES[i % len(POOL_NAMES)]
                    new_vocab[pool].append(w)
                self._validate_vocab(new_vocab)
                self.vocab = new_vocab
                self.last_intro_state = data.get("intro_state")
                self.last_aware_state = data.get("aware_state")
                # Rebuild system with migrated vocab
                self.sys_, self.token_vec, self.intro_vec, self.intro_modes, \
                    self.aware_vec, self.aware_modes = self._build_system()
                for sn in POOL_NAMES + ["intro", "aware"]:
                    if sn in self.sys_.sections:
                        install_plasticity(self.sys_.sections[sn], initial_strength=1.0)
                return
            # Schema v4 native
            if "vocab" in data:
                loaded_vocab = {k: list(v) for k, v in data["vocab"].items()}
                self._validate_vocab(loaded_vocab)
                self.vocab = loaded_vocab
            self.last_intro_state = data.get("intro_state")
            self.last_aware_state = data.get("aware_state")
            for sn, sec_data in data.get("sections", {}).items():
                if sn in self.sys_.sections:
                    self._restore_section(self.sys_.sections[sn], sec_data)


# ---- Session manager ----
_sessions = {}
_sessions_lock = threading.Lock()
STATE_DIR = "/app/state/v7_sessions"


def get_or_create_session(session_id, engine=None):
    if engine is None:
        raise RuntimeError("guala_not_ready")
    with _sessions_lock:
        if session_id in _sessions:
            return _sessions[session_id]
        session = V7Session(session_id, engine=engine)
        snapshot_path = os.path.join(STATE_DIR, f"{session_id}.json")
        snapshot_seq = -1
        if os.path.exists(snapshot_path):
            try:
                with open(snapshot_path) as f:
                    data = json.load(f)
                session.load_from_json(data)
                snapshot_seq = data.get("event_seq", -1)
                print(f"[v7] Loaded snapshot for {session_id} (seq={snapshot_seq})")
            except (ValueError, Exception) as e:
                print(f"[v7] Snapshot discarded for {session_id}: {e} "
                      f"(path={snapshot_path})")
                try:
                    os.remove(snapshot_path)
                except OSError:
                    pass
                session = V7Session(session_id, engine=engine)
        if session.event_log.exists():
            from dsf_ai_service.substrate.event_log import replay_events
            events = session.event_log.read_since(snapshot_seq)
            if events:
                n = replay_events(session, events)
                print(f"[v7] Replayed {n} events for {session_id}")
        _sessions[session_id] = session
        return session


def save_session(session):
    os.makedirs(STATE_DIR, exist_ok=True)
    path = os.path.join(STATE_DIR, f"{session.session_id}.json")
    data = session.to_json()
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f)
    os.rename(tmp, path)
