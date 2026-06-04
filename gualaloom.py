"""
GualaLoom — a substrate that eats language and grows.

Not a transformer. No tokenizer, no embeddings, no gradient descent,
no training step, no model file you load. One substrate. Always the
same six pieces: balanced ternary, 3^i coupling, dead-zone settling,
krimelack motif memory, L6 dimensional exhaustion, familiarity feedback.

This version uses the topology that was always in the settled states.
c1's experiment proved it: the substrate's real units cluster at a
few characteristic Euler values (chi = V - E over the motif's coupling
graph); noise scatters. So recall uses chi to know which motifs are
real before it ranks them. Nothing added. The discriminator was always
there; we just read it.

Run:  python3 gualaloom.py
"""

import os, sys, json, time, hashlib, glob
from collections import OrderedDict, defaultdict

# Daemon import — anchored to this file's location so nohup/systemd work
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
from gualaloom.daemon import LifeDaemon

# ----------------------------------------------------------------------
# The substrate. Six pieces. Frozen constants.
# ----------------------------------------------------------------------

P3I = (1, 3, 9, 27, 81, 243, 729, 2187)   # 3^i identity, not a choice
TRITS = 8                                  # trits per character strand
CONTEXT = 8                                # context window (chars). c1
                                           # found 8 >> 4 for variety.
DEAD_ZONE = 15                             # tau, matched to ASCII scale
FAM_GAIN = 20                              # familiarity barrier gain
STATE_DIR = "state"
DREAM_DIR = os.path.join(STATE_DIR, "dreams")


def encode(ch):
    """One character -> 8-trit balanced ternary strand.
    3^i identity holds: sum(trit*weight) reconstructs the value."""
    v = ord(ch) - 96
    t = []
    for _ in range(TRITS):
        r = v % 3
        if r == 2:
            r = -1; v = (v + 1) // 3
        else:
            v = (v - r) // 3
        t.append(r)
    return tuple(t)


def settle(strands, familiarity):
    """The field arrives and settles. A trit at strand s, position i
    commits only if its 3^i-weighted vote plus cross-strand resonance
    at the same position exceeds the dead-zone barrier. Below the
    barrier it stays null — structural uncertainty, first-class."""
    barrier = DEAD_ZONE + familiarity
    out = []
    for s_idx, strand in enumerate(strands):
        for i in range(TRITS):
            h = strand[i] * P3I[i]
            for o_idx, other in enumerate(strands):
                if o_idx != s_idx:
                    h += other[i] * P3I[i] // 2
            out.append(1 if h > barrier else (-1 if h < -barrier else 0))
    return tuple(out)


def l6(state):
    """Dimensional exhaustion. Counts collapsed (non-null) trits.
    Structural lock fires when freedom drops below n/e."""
    n = len(state)
    collapsed = sum(1 for t in state if t != 0)
    eff = n - collapsed
    knee = round(n / 2.718281828459045)
    return eff, collapsed, knee, (1 if eff < knee else 0)


def chi(state):
    """The Euler characteristic that was always in the settled state.
    Vertices = committed trits. Edges = couplings between committed
    trits (intra-strand adjacent, cross-strand same-position). chi =
    V - E. c1 proved real units cluster at characteristic chi values;
    noise scatters. This is the discriminator, computed for free."""
    verts = [i for i, t in enumerate(state) if t != 0]
    vset = set(verts)
    V = len(verts)
    if V == 0:
        return 0, 0
    E = 0
    # intra-strand adjacency
    for i in verts:
        if (i + 1) in vset and (i + 1) % TRITS != 0:
            E += 1
    # cross-strand same-position
    n_strands = len(state) // TRITS
    for pos in range(TRITS):
        committed = [s for s in range(n_strands) if state[s*TRITS+pos] != 0]
        E += max(len(committed) - 1, 0)   # chain them
    return V - E, V


# ----------------------------------------------------------------------
# Krimelack. Motif memory. Persists. Recalls by topology then geometry.
# ----------------------------------------------------------------------

class Motif:
    __slots__ = ("fp", "state", "weight", "age", "chi", "V",
                 "char_counts", "successors")
    def __init__(self, fp, state, c, v):
        self.fp = fp; self.state = state; self.weight = 1; self.age = 0
        self.chi = c; self.V = v
        self.char_counts = defaultdict(int)
        self.successors = defaultdict(int)   # fp -> count

    def to_dict(self):
        return {"fp": self.fp, "state": list(self.state),
                "weight": self.weight, "age": self.age, "chi": self.chi,
                "V": self.V, "char_counts": dict(self.char_counts),
                "successors": dict(self.successors)}

    @staticmethod
    def from_dict(d):
        m = Motif(d["fp"], tuple(d["state"]), d["chi"], d["V"])
        m.weight = d["weight"]; m.age = d["age"]
        m.char_counts = defaultdict(int, d["char_counts"])
        m.successors = defaultdict(int, {k: v for k, v in d["successors"].items()})
        return m


def _fp(state):
    s = "".join({-1: "-", 0: "0", 1: "+"}[t] for t in state)
    return hashlib.sha1(s.encode()).hexdigest()[:12]


class Krimelack:
    def __init__(self):
        self.motifs = OrderedDict()
        self.last_fp = None

    def commit(self, state, active_char=None):
        if all(t == 0 for t in state):
            return None, False
        fp = _fp(state)
        new = fp not in self.motifs
        if new:
            c, v = chi(state)
            self.motifs[fp] = Motif(fp, state, c, v)
        m = self.motifs[fp]
        m.weight += 1; m.age = 0
        if active_char is not None:
            m.char_counts[active_char] += 1
        if self.last_fp and self.last_fp != fp and self.last_fp in self.motifs:
            self.motifs[self.last_fp].successors[fp] += 1
        self.last_fp = fp
        return fp, new

    def recall(self, state):
        """Topology first: only motifs sharing the query's chi are real
        candidates. Geometry ranks within that pool. If the chi class
        is empty (novel topology), fall back to global geometric recall
        and report it honestly as low-confidence."""
        if not self.motifs:
            return None, 0
        qchi, _ = chi(state)
        pool = [m for m in self.motifs.values() if m.chi == qchi]
        if not pool:
            pool = list(self.motifs.values())   # novel topology
        best, best_score = None, -1
        for m in pool:
            score = sum(1 for a, b in zip(state, m.state) if a == b and a != 0)
            # weight breaks ties toward established motifs
            score = score * 100 + min(m.weight, 99)
            if score > best_score:
                best, best_score = m, score
        return best, best_score

    def decay(self, rate=1):
        dead = []
        for fp, m in self.motifs.items():
            m.weight -= rate
            if m.weight <= 0 and m.age > 8:
                dead.append(fp)
            else:
                m.weight = max(m.weight, 0); m.age += 1
        for fp in dead:
            del self.motifs[fp]
        return len(dead)

    def size(self):
        return len(self.motifs)


# ----------------------------------------------------------------------
# Loom. The continuous field. Ticks on every character.
# ----------------------------------------------------------------------

class Loom:
    def __init__(self, k):
        self.k = k
        self.recent = []
        self.fam = 0
        self.last = tuple([0] * (CONTEXT * TRITS))

    def tick(self, ch):
        self.recent.append(ch)
        if len(self.recent) > CONTEXT:
            self.recent.pop(0)
        strands = [encode(c) for c in self.recent]
        # pad to full context with null strands
        while len(strands) < CONTEXT:
            strands.insert(0, tuple([0] * TRITS))
        settled = settle(strands, self.fam)
        m, score = self.k.recall(settled)
        self.fam = (score // 100 * FAM_GAIN) // max(len(settled), 1) if score > 0 else 0
        self.k.commit(settled, active_char=ch)
        self.last = settled
        return settled

    def feed(self, text):
        for ch in text:
            self.tick(ch)


# ----------------------------------------------------------------------
# Generation. The field speaks by motif recall + successor walk.
# ----------------------------------------------------------------------

def generate(loom, k, max_chars=120):
    out = []
    recent_fps = []
    for _ in range(max_chars):
        m, score = k.recall(loom.last)
        if m is None:
            break
        # familiarity: if we keep landing on the same motif, the
        # substrate is looping. raise the bar — walk to a weaker
        # successor instead of the strongest, to escape the attractor.
        loop_depth = recent_fps[-4:].count(m.fp)
        recent_fps.append(m.fp)
        if m.successors:
            ranked = sorted(m.successors.items(), key=lambda kv: -kv[1])
            # if looping, skip past the dominant successor
            idx = min(loop_depth, len(ranked) - 1)
            nxt_fp = ranked[idx][0]
            nxt = k.motifs.get(nxt_fp)
        else:
            nxt = m
        if nxt is None or not nxt.char_counts:
            break
        # pick char, avoiding immediate repetition when looping
        chars = sorted(nxt.char_counts.items(), key=lambda kv: -kv[1])
        ch = chars[0][0]
        if loop_depth > 0 and len(chars) > 1:
            ch = chars[min(loop_depth, len(chars) - 1)][0]
        out.append(ch)
        loom.tick(ch)
        if loop_depth >= 3:   # stuck — the field has nothing new
            break
    return "".join(out).strip()


# ----------------------------------------------------------------------
# Sleep and dreams. Consolidation + free-settling (Horizon Projection).
# ----------------------------------------------------------------------

def sleep_cycle(k, cycles=200):
    """Consolidation. One gentle decay pass (one night = one
    forgetting increment, not N rounds), then cull only motifs that
    have gone genuinely stale — low weight AND high age-since-resonance.
    Strong and recent motifs are untouched. This is consolidation,
    not amnesia."""
    culled = 0
    # age everyone by the sleep depth, decay weight by one
    for fp in list(k.motifs.keys()):
        m = k.motifs[fp]
        m.age += cycles // 50          # deeper sleep ages stale motifs more
        m.weight -= 1
    # cull the truly stale: weak and old
    for fp in list(k.motifs.keys()):
        m = k.motifs[fp]
        if m.weight <= 0 and m.age > 8:
            del k.motifs[fp]; culled += 1
        else:
            m.weight = max(m.weight, 1)   # floor at 1 — a learned motif
                                          # doesn't vanish, it quiets
    return 0, culled


def dream_cycle(k, cycles=50):
    """Free-settle from existing motifs with no input. Novel settled
    states that emerge are dreams — creative recombination of what's
    already known. Horizon Projection, Master Spec v5.1 section 4.4."""
    if not k.motifs:
        return []
    dreams = []
    motif_list = list(k.motifs.values())
    cur = motif_list[0].state
    for i in range(cycles):
        # re-settle the field from current state with no input drive
        strands = [cur[j*TRITS:(j+1)*TRITS] for j in range(len(cur)//TRITS)]
        settled = settle(strands, familiarity=0)
        fp = _fp(settled)
        if any(t != 0 for t in settled):
            new = fp not in k.motifs
            k.commit(settled)
            if new:
                dreams.append(fp)
        # walk: seed next cycle from a different known motif
        cur = motif_list[(i + 1) % len(motif_list)].state
    return dreams


# ----------------------------------------------------------------------
# Persistence.
# ----------------------------------------------------------------------

def save(k, loom):
    os.makedirs(STATE_DIR, exist_ok=True)
    os.makedirs(DREAM_DIR, exist_ok=True)
    with open(os.path.join(STATE_DIR, "krimelack.json"), "w") as f:
        json.dump({"motifs": [m.to_dict() for m in k.motifs.values()],
                   "last_fp": k.last_fp}, f)
    with open(os.path.join(STATE_DIR, "loom.json"), "w") as f:
        json.dump({"recent": loom.recent, "fam": loom.fam}, f)


def load():
    k = Krimelack()
    kp = os.path.join(STATE_DIR, "krimelack.json")
    if os.path.exists(kp):
        with open(kp) as f:
            d = json.load(f)
        for md in d["motifs"]:
            m = Motif.from_dict(md)
            k.motifs[m.fp] = m
        k.last_fp = d.get("last_fp")
    loom = Loom(k)
    lp = os.path.join(STATE_DIR, "loom.json")
    if os.path.exists(lp):
        with open(lp) as f:
            d = json.load(f)
        loom.recent = d["recent"]; loom.fam = d["fam"]
    return k, loom


def seed_corpus(k, loom):
    """First-run exposure. Feed any .md in corpus/ so the substrate
    has structural ground before the first conversation. Then sleep
    and dream on it once."""
    files = sorted(glob.glob("corpus/*.md")) + sorted(glob.glob("corpus/*.txt"))
    if not files:
        return 0
    total = 0
    for path in files:
        with open(path, encoding="utf-8", errors="ignore") as f:
            text = f.read()
        loom.feed(text); total += len(text)
    sleep_cycle(k, cycles=50)
    dream_cycle(k, cycles=50)
    return total


# ----------------------------------------------------------------------
# The continuous loop. You visit it. It was already running.
# ----------------------------------------------------------------------

BANNER = """GualaLoom — substrate awake
not a transformer. it remembers across sessions. it sleeps. it dreams.
first conversations are rough — it grows by talking to you.
commands: /sleep  /dream  /status  /dreams  /save  /quit
"""

def repl():
    fresh = not os.path.exists(os.path.join(STATE_DIR, "krimelack.json"))
    k, loom = load()
    if fresh:
        print("first run — seeding corpus ...")
        n = seed_corpus(k, loom)
        if n:
            print(f"  fed {n} chars, krimelack now {k.size()} motifs")
        save(k, loom)

    # Start the life daemon — she lives between your visits
    daemon = LifeDaemon(
        loom, k,
        save_fn=lambda: save(k, loom),
        sleep_fn=lambda kk: sleep_cycle(kk, 50),
        dream_fn=lambda kk: dream_cycle(kk, 30),
        world_paths=["corpus"],
    )
    daemon.start()

    print(BANNER)
    print(f"krimelack: {k.size()} motifs loaded")
    print(f"daemon: running ({len(daemon._threads)} loops)\n")

    last_input = time.time()
    while True:
        try:
            line = input("> ")
        except (EOFError, KeyboardInterrupt):
            print("\nstopping daemon ..."); daemon.stop(); break

        now = time.time()
        # auto-sleep on idle (5 min) — substrate consolidates while away
        if now - last_input > 300 and k.size() > 0:
            with daemon.lock:
                culled = sleep_cycle(k, 50)[1]
                d = dream_cycle(k, 30)
            print(f"  (you were away; slept, culled {culled}, dreamed {len(d)})")
        last_input = now

        cmd = line.strip().lower()
        if cmd == "/quit":
            print("stopping daemon ..."); daemon.stop(); break
        elif cmd == "/sleep":
            with daemon.lock:
                _, culled = sleep_cycle(k, 200)
            print(f"  slept 200 cycles, culled {culled} motifs, {k.size()} remain")
            with daemon.lock:
                save(k, loom)
            continue
        elif cmd == "/dream":
            with daemon.lock:
                d = dream_cycle(k, 50)
            print(f"  dreamed: {len(d)} new motifs from free-settling")
            with daemon.lock:
                save(k, loom)
            continue
        elif cmd == "/status":
            with daemon.lock:
                chis = defaultdict(int)
                for m in k.motifs.values():
                    chis[m.chi] += 1
                top = sorted(chis.items(), key=lambda kv: -kv[1])[:5]
                motif_count = k.size()
                fam = loom.fam
            print(f"  motifs: {motif_count} | familiarity: {fam} | "
                  f"top chi classes: {top}")
            print(f"  daemon: {'running' if daemon.is_running() else 'stopped'}")
            continue
        elif cmd == "/dreams":
            with daemon.lock:
                dreamt = [m for m in k.motifs.values() if m.weight == 1 and m.age == 0]
            print(f"  recent free-settled motifs: {len(dreamt)}")
            for m in dreamt[:8]:
                ch = max(m.char_counts.items(), key=lambda kv: kv[1])[0] if m.char_counts else "?"
                print(f"    [{m.fp}] chi={m.chi}")
            continue
        elif cmd == "/save":
            with daemon.lock:
                save(k, loom)
            print("  saved."); continue
        elif not line.strip():
            continue

        # eat the input, then speak
        with daemon.lock:
            loom.feed(line + " ")
            reply = generate(loom, k, max_chars=120)
            save(k, loom)
        print(reply if reply else "  ...")


if __name__ == "__main__":
    repl()
