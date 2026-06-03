"""
Topological invariants for settled motif states.

Given a settled state (vector of trits {-1, 0, +1}), build a graph
from committed (non-null) trits and compute:
  - V: vertex count (committed trits)
  - E: edge count (couplings between committed trits)
  - C: connected components
  - chi = V - E (Euler characteristic for 1-complex)
  - b1 = E - V + C (first Betti number: independent loops)
  - F: face count (minimal cycles of length 3 for 2-complex)
  - chi2 = V - E + F (Euler characteristic for 2-complex)

Edge rule: two committed trits at positions i and j are connected if:
  (a) they are in the same strand and adjacent: |i - j| == 1
      AND both in the same strand (i // trits_per_strand == j // trits_per_strand)
  (b) they are at the same position across strands:
      i % trits_per_strand == j % trits_per_strand
      AND they are in adjacent strands: |i // tps - j // tps| == 1

Both rules make the implicit coupling in settle_field explicit.
"""

from typing import Dict, List, Set, Tuple

from .substrate import TRITS_PER_STRAND


def _build_graph(state: Tuple[int, ...],
                 trits_per_strand: int = TRITS_PER_STRAND
                 ) -> Tuple[List[int], List[Tuple[int, int]]]:
    """Build vertex list and edge list from a settled state.

    Vertices: indices of committed (non-null) trits.
    Edges: coupled pairs per the adjacency rules.
    """
    vertices = [i for i, t in enumerate(state) if t != 0]
    v_set = set(vertices)

    edges = []
    for v in vertices:
        strand_v = v // trits_per_strand
        pos_v = v % trits_per_strand

        # Intra-strand: next position in same strand
        neighbor = v + 1
        if (neighbor in v_set
                and neighbor // trits_per_strand == strand_v):
            edges.append((v, neighbor))

        # Cross-strand: same position in next strand
        cross = v + trits_per_strand
        if cross in v_set:
            edges.append((v, cross))

    return vertices, edges


def _connected_components(vertices: List[int],
                          edges: List[Tuple[int, int]]) -> int:
    """Count connected components via union-find."""
    if not vertices:
        return 0

    parent = {v: v for v in vertices}

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for a, b in edges:
        union(a, b)

    roots = set(find(v) for v in vertices)
    return len(roots)


def _count_triangles(vertices: List[int],
                     edges: List[Tuple[int, int]]) -> int:
    """Count triangles (3-cycles) in the graph. Each triangle = 1 face."""
    adj: Dict[int, Set[int]] = {v: set() for v in vertices}
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)

    triangles = 0
    v_list = sorted(vertices)
    for i, u in enumerate(v_list):
        for j in range(i + 1, len(v_list)):
            v = v_list[j]
            if v not in adj[u]:
                continue
            for k in range(j + 1, len(v_list)):
                w = v_list[k]
                if w in adj[u] and w in adj[v]:
                    triangles += 1
    return triangles


def compute_topology(state: Tuple[int, ...]) -> Dict:
    """Compute all topological invariants for a settled state.

    Returns dict with V, E, C, chi, b1, F, chi2.
    """
    vertices, edges = _build_graph(state)
    V = len(vertices)
    E = len(edges)
    C = _connected_components(vertices, edges)
    chi = V - E
    b1 = E - V + C  # independent loops

    F = _count_triangles(vertices, edges)
    chi2 = V - E + F

    return {
        "V": V, "E": E, "C": C,
        "chi": chi, "b1": b1,
        "F": F, "chi2": chi2,
    }
