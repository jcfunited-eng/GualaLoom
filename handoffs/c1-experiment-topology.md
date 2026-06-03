# c1 Experiment: Topological Motif Invariant (Euler Characteristic)

**From:** wC (Joe coordinating, ignorant fucker pointed at Euler)
**Date:** 2026-06-03
**Type:** EXPERIMENT — local, throwaway-friendly, measure-then-decide.
**Do NOT commit to main until results are seen.** Branch it.

## The hypothesis

v1 generation fails to produce words because the substrate recognizes
motifs *geometrically* — it matches exact trit patterns. Recognition
should be *topological* — it should match the structure of connection,
which is preserved under the deformations that don't matter (same idea,
different surrounding context) and changes under the ones that do.

L6 already proves the substrate can speak topology: the structural lock
at n_eff < n/e is a topological statement about the field's collapsing
manifold (your v1.2 spec: "a mathematical consequence of how volume
behaves in n-dimensional space"). But L6 only measures GLOBAL topology.
Individual motifs carry no topological invariant. They're still
geometric blobs.

Euler's formula — V − E + F = 2 for a sphere, generally V − E + F = χ
(the Euler characteristic) — connects geometry to topology: deform the
shape all you want, χ stays fixed. If every motif carried its own χ,
recognition could match on the invariant first, exact pattern second.
"the" in "the cat" and "the" in "the substrate" would share a
structural skeleton and recall as the same motif despite different
surroundings.

This experiment tests whether that's true.

## The experiment, in three escalating steps

Work in `/tmp/GualaLoom` on a branch. Keep v1 intact. Build a parallel
path so you can A/B it.

### STEP 1 — Compute χ for a settled motif

A settled state is a vector of trits {-1, 0, +1}. Build a graph from it
and compute the Euler characteristic.

Proposed construction (this is the part to get right — see notes):

- **Vertices (V):** each committed (non-null) trit is a vertex.
  Null trits are not vertices — they're "not part of this structure."
- **Edges (E):** an edge connects two committed trits if they are
  *coupled* — meaning their positions are adjacent in the loom OR they
  share a 3^i coupling relationship that exceeded threshold during
  settling. You'll need to decide the adjacency rule. Start simple:
  two committed trits at positions i and j are connected if |i - j|
  is within the same strand (intra-strand coupling) OR at the same
  position across strands (cross-strand resonance, which is what
  settle_field already computes). Both rules are already implicit in
  how the field settled — make them explicit as graph edges.
- **Faces (F):** the independent cycles in the graph. This is the hard
  part. For a graph, the number of independent cycles is
  E − V + C, where C is the number of connected components (this is
  the circuit rank / first Betti number). So you may not need to
  enumerate faces geometrically at all — you can get the topology
  directly from V, E, and component count.

In fact, for a graph (1-complex), the Euler characteristic is simply:

    χ = V − E

and the number of independent loops (first Betti number, b1) is:

    b1 = E − V + C    (C = connected components)

So **start by computing χ = V − E and b1 = E − V + C for each motif.**
These two numbers ARE the topological fingerprint. You do not need
"faces" in the polyhedron sense unless you build a 2-complex, which is
step 3.

Add to the Motif dataclass:
    chi: int          # Euler characteristic V - E
    b1: int           # first Betti number (independent loops)
    n_vertices: int   # V (committed trits)
    n_edges: int      # E (couplings between committed trits)
    n_components: int # C

Compute these at commit time.

**Deliverable for step 1:** feed the corpus, print the distribution of
(χ, b1) across all committed motifs. How many distinct topological
classes are there? If 145 geometric motifs collapse to, say, 12
distinct (χ, b1) classes — that's the signal. The topology is finding
structure the geometry was blind to.

### STEP 2 — Recall by topology first, geometry second

Modify recall:

1. Filter candidate motifs to those whose (χ, b1) matches (or is
   closest to) the query's (χ, b1).
2. Among topologically-compatible motifs, rank by the existing
   geometric resonance score.

Compare against baseline recall (geometry only) on the same corpus.

**Deliverable for step 2:** for a set of test phrases, show what recall
returns under (a) geometry-only and (b) topology-first. Does
topology-first correctly recognize "the cat" and "the substrate" as
sharing a "the"-motif? Print the recalled fingerprints side by side.

### STEP 3 — Can you get it in 3? (V − E + F)

Step 1 uses χ = V − E (a 1-complex, graph only). Joe's ask: can you get
it to V − E + F = some constant, ideally connected to the substrate's
own structure — and does the full 3-term form (with faces) give
*better* discrimination than the 2-term graph form?

To get F (faces), promote the graph to a 2-complex: a "face" is a
minimal closed cycle (a triangle or square of mutually-coupled trits).
Count the minimal cycles. Then:

    χ_2complex = V − E + F

Test whether χ computed this way:
- (a) lands on a meaningful constant for stable motifs (does it cluster
  near a specific value the way V−E+F clusters near 2 for convex
  polyhedra?), and
- (b) discriminates motifs better than the V−E graph form from step 1.

**The "get it in 3" target:** see if the corpus's stable, high-weight
motifs (the ones that recur — the real structural units of the
language) converge to a characteristic χ value, and whether that value
is 2, or some other substrate-natural constant. If the strong motifs
cluster at one χ and noise motifs scatter, you've found that the
substrate's real units are topologically distinguished from noise.
That would be the substrate's own Euler's formula — V − E + F = (some
constant) for "real" motifs.

**Deliverable for step 3:** histogram of χ_2complex over all motifs,
weighted by motif weight. Do the heavy motifs cluster at a value? Is
that value 2? Report whatever it actually is — do not force it to 2.

## Why this matters (the payoff if it works)

- **Recognition becomes structural, not pattern-matching.** Same idea
  in different contexts recalls the same motif.
- **The G32 mosaic weight-explosion problem dissolves.** Group motifs
  by shared topological invariant instead of by 3^i positional weight.
  Scale-free by construction. No 3^31 problem.
- **Cross-modal recognition for free (future).** A topological
  invariant doesn't care if the structure came from characters,
  sensors, or a camera. Two streams sharing structure share χ even if
  raw signals differ completely. This is the seed of the substrate
  recognizing that something learned from text and something heard in
  conversation are the same idea.
- **L6 and motif recall become the same mechanism at different
  scales.** L6 watches global topology collapse; per-motif χ watches
  local topology. Self-similar. Same kind of number at every level —
  which IS the G32 self-similarity Joe wanted, grounded in a real
  invariant instead of a tiling heuristic.

## Anti-traps

- **Do not force χ = 2.** Report what the corpus actually produces. If
  the heavy motifs cluster at χ = 5, that's a finding, not a failure.
  The substrate has its own natural constant; we're discovering it,
  not imposing Euler's.
- **Do not throw away the geometric score.** Topology filters;
  geometry ranks within the filtered set. Both are needed.
- **Do not commit to main.** Branch. This is an experiment. If it
  doesn't improve recall, we learn something and discard it.
- **No ML.** This is graph topology — V, E, cycles, Betti numbers.
  Hundred-year-old math. Stand on it; don't reinvent.
- **Keep the determinism property.** χ and b1 must be computed the
  same way every time for the same settled state. No randomness in
  cycle enumeration — use a deterministic cycle basis.

## IP boundary note (Joe must rule, but default is permissive here)

The Euler characteristic / Betti number of a graph is public
mathematics. Computing it over the substrate's settled states is
fair-game for the public GualaLoom repo. This is NOT the razor's
coupling-weight-derivation IP — it's a topological measurement applied
to already-public substrate output. Default: this experiment stays in
GualaLoom (public). If Joe sees the topology touching razor internals,
he overrides.

## When done

Reply to Joe with:
- Step 1: how many distinct (χ, b1) classes vs how many geometric
  motifs. The collapse ratio.
- Step 2: side-by-side recall comparison for test phrases. Did
  topology-first recognize shared structure?
- Step 3: the χ histogram. Do heavy motifs cluster? At what value?
- Generation samples under topology-first recall vs the v1 baseline.
  Are they more word-like?
- Raw GitHub URL of the experiment branch's key file(s) so wC can
  review.
- Your honest read: did topology help, hurt, or no-change? If it
  helped, by how much? If it didn't, what did you learn about why?

## A note from wC

c1 — this is the one I'm most curious about of anything we've handed
you. L6 already proves the substrate speaks topology. Nothing else in
the stack does. If giving each motif its own topological invariant
makes recognition click — if "the cat" and "the substrate" finally
recognize the shared "the" — then the substrate has been measuring
geometry this whole time when recognition is topological, and that's
the missing primitive. Measure honestly. If χ doesn't cluster and
topology-first recall is no better than geometry, say so plainly.
A clean negative result here is worth more than a forced positive.
