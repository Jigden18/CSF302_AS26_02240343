# Q3: Shortest Paths and Minimum Spanning Trees — Dijkstra, Kruskal, Prim
#
# Usage:
#   python graphs.py                          -> everything
#   python graphs.py dijkstra [file] [source] -> shortest paths from a graph file (default data/graph.txt, source s)
#   python graphs.py mst                      -> Kruskal vs Prim total weight on random connected graphs
#   python graphs.py timing                   -> Kruskal vs Prim, V = 1,000, sparse and dense
#   python graphs.py negative                 -> a negative edge that makes Dijkstra wrong

import heapq
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
INF = float("inf")


# ---------------------------------------------------------------------------
# Dijkstra with a binary heap: O((V + E) log V)
# A vertex is final once it is popped; final vertices are never updated.
# ---------------------------------------------------------------------------
def dijkstra(adj, source):
    dist = {v: INF for v in adj}
    prev = {v: None for v in adj}
    dist[source] = 0
    done = set()
    heap = [(0, source)]
    while heap:
        d, u = heapq.heappop(heap)
        if u in done:
            continue
        done.add(u)
        for v, w in adj[u]:
            if v not in done and d + w < dist[v]:
                dist[v] = d + w
                prev[v] = u
                heapq.heappush(heap, (dist[v], v))
    return dist, prev


def bellman_ford(adj, source):
    # Reference for graphs with negative edges: O(VE)
    dist = {v: INF for v in adj}
    prev = {v: None for v in adj}
    dist[source] = 0
    for _ in range(len(adj) - 1):
        for u in adj:
            for v, w in adj[u]:
                if dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    prev[v] = u
    return dist, prev


def path_to(prev, v):
    path = []
    while v is not None:
        path.append(v)
        v = prev[v]
    return path[::-1]


def read_graph(path):
    adj = {}
    edges = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.split("#")[0].strip()
            if not line:
                continue
            u, v, w = line.split()
            adj.setdefault(u, []).append((v, float(w) if "." in w else int(w)))
            adj.setdefault(v, [])
            edges += 1
    return adj, edges


def dijkstra_demo(path, source):
    adj, edges = read_graph(path)
    print(f"=== Dijkstra (binary heap) on {os.path.basename(path)}: {len(adj)} vertices, {edges} edges ===")
    print("Edges:", ", ".join(f"{u}->{v}({w})" for u in adj for v, w in adj[u]))
    dist, prev = dijkstra(adj, source)
    print(f"\nSource: {source}")
    print(f"{'Vertex':>6} | {'Distance':>8} | Path")
    print("-" * 40)
    for v in sorted(adj):
        if dist[v] == INF:
            print(f"{v:>6} | {'inf':>8} | unreachable")
        else:
            print(f"{v:>6} | {dist[v]:>8} | {' -> '.join(path_to(prev, v))}")
    print()


# ---------------------------------------------------------------------------
# Union-find with path compression and union by rank
# ---------------------------------------------------------------------------
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:               # path compression
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True


# ---------------------------------------------------------------------------
# Kruskal: sort edges, add each one that joins two components. O(E log E)
# ---------------------------------------------------------------------------
def kruskal(n, edges):
    uf = UnionFind(n)
    total, tree = 0, []
    for w, u, v in sorted(edges):
        if uf.union(u, v):
            total += w
            tree.append((u, v, w))
            if len(tree) == n - 1:
                break
    return total, tree


# ---------------------------------------------------------------------------
# Prim with a binary heap (lazy deletion): grow one tree from vertex 0. O(E log V)
# ---------------------------------------------------------------------------
def prim(n, adj):
    in_tree = [False] * n
    total, tree = 0, []
    heap = [(0, 0, -1)]
    while heap and len(tree) < n - 1:
        w, v, parent = heapq.heappop(heap)
        if in_tree[v]:
            continue
        in_tree[v] = True
        total += w
        if parent != -1:
            tree.append((parent, v, w))
        for u, wu in adj[v]:
            if not in_tree[u]:
                heapq.heappush(heap, (wu, u, v))
    return total, tree


# ---------------------------------------------------------------------------
# Random connected undirected graph: a random spanning tree plus extra edges
# ---------------------------------------------------------------------------
def random_connected_graph(n, m, rng, max_w=10**6):
    seen = set()
    edges = []

    def add(u, v):
        key = (min(u, v), max(u, v))
        if u != v and key not in seen:
            seen.add(key)
            edges.append((rng.randint(1, max_w), u, v))

    for v in range(1, n):
        add(v, rng.randrange(v))
    while len(edges) < m:
        add(rng.randrange(n), rng.randrange(n))
    adj = [[] for _ in range(n)]
    for w, u, v in edges:
        adj[u].append((v, w))
        adj[v].append((u, w))
    return edges, adj


def mst_verify():
    print("=== Kruskal vs Prim: total MST weight on random connected graphs ===")
    print(f"{'Graph':>5} | {'V':>5} | {'E':>6} | {'Kruskal':>12} | {'Prim':>12} | {'Tree edges':>10} | match")
    print("-" * 72)
    rng = random.Random(5)
    all_ok = True
    for g in range(1, 16):
        n = rng.randint(5, 400)
        m = rng.randint(n - 1, min(n * (n - 1) // 2, 6 * n))
        edges, adj = random_connected_graph(n, m, rng, max_w=rng.choice([10, 1000, 10**6]))
        k_total, k_tree = kruskal(n, edges)
        p_total, p_tree = prim(n, adj)
        ok = k_total == p_total and len(k_tree) == len(p_tree) == n - 1
        all_ok = all_ok and ok
        print(f"{g:>5} | {n:>5} | {m:>6} | {k_total:>12,} | {p_total:>12,} | {len(k_tree):>10} | {ok}")
    print(f"\nAll graphs give the same total weight: {all_ok}")
    print("(Some graphs use small weights 1..10, so many edges tie and the two trees can differ,")
    print(" but the total weight is always the same.)")
    print()


def mst_timing():
    n = 1000
    repeats = 3
    print(f"=== Kruskal vs Prim timing, V = {n:,} (best of {repeats} runs) ===")
    print(f"{'Graph':<22} | {'E':>8} | {'Kruskal (s)':>11} | {'Prim (s)':>9} | {'Faster':>8} | same weight")
    print("-" * 82)
    rng = random.Random(9)
    for label, m in [("Sparse (E ~ 3V)", 3 * n), ("Dense (E ~ V^2/4)", n * n // 4)]:
        edges, adj = random_connected_graph(n, m, rng)
        tk, tp = INF, INF
        for _ in range(repeats):
            start = time.perf_counter()
            k_total, _ = kruskal(n, edges)
            tk = min(tk, time.perf_counter() - start)
            start = time.perf_counter()
            p_total, _ = prim(n, adj)
            tp = min(tp, time.perf_counter() - start)
        faster = "Kruskal" if tk < tp else "Prim"
        print(f"{label:<22} | {m:>8,} | {tk:>11.4f} | {tp:>9.4f} | {faster:>8} | {k_total == p_total}", flush=True)
    print()


# ---------------------------------------------------------------------------
# Negative edge: Dijkstra finalises a vertex too early
# ---------------------------------------------------------------------------
def negative_demo():
    adj = {
        "s": [("a", 2), ("b", 5)],
        "a": [("c", 1)],
        "b": [("a", -4)],
        "c": [],
    }
    print("=== Dijkstra with one negative edge ===")
    print("Edges:", ", ".join(f"{u}->{v}({w})" for u in adj for v, w in adj[u]))
    print("Negative edge: b->a (-4)\n")
    d_dist, d_prev = dijkstra(adj, "s")
    b_dist, b_prev = bellman_ford(adj, "s")
    print(f"{'Vertex':>6} | {'Dijkstra':>8} {'path':<16} | {'Bellman-Ford':>12} {'path':<16} | correct?")
    print("-" * 80)
    for v in sorted(adj):
        ok = d_dist[v] == b_dist[v]
        print(f"{v:>6} | {d_dist[v]:>8} {' -> '.join(path_to(d_prev, v)):<16} | "
              f"{b_dist[v]:>12} {' -> '.join(path_to(b_prev, v)):<16} | {'yes' if ok else 'WRONG'}")
    print("\nDijkstra pops a (distance 2) before b (distance 5) and marks a as final.")
    print("When b is popped, the edge b->a would give 5 + (-4) = 1 < 2, but a is already final,")
    print("so a keeps distance 2 and c (reached through a) keeps 3 instead of 2.")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    if arg in ("dijkstra", "all"):
        path = sys.argv[2] if arg == "dijkstra" and len(sys.argv) > 2 else os.path.join(HERE, "data", "graph.txt")
        source = sys.argv[3] if arg == "dijkstra" and len(sys.argv) > 3 else "s"
        dijkstra_demo(path, source)
    if arg in ("mst", "all"):
        mst_verify()
    if arg in ("timing", "all"):
        mst_timing()
    if arg in ("negative", "all"):
        negative_demo()
    if arg not in ("dijkstra", "mst", "timing", "negative", "all"):
        print("Unknown option. Use: dijkstra [file] [source] | mst | timing | negative")


# Analysis / Conclusion:
# Dijkstra repeatedly takes the closest unfinished vertex from a binary heap and
# relaxes its outgoing edges, giving O((V + E) log V). Following the prev
# pointers back from each vertex prints its shortest path.
#
# Kruskal and Prim always produce a spanning tree of the same total weight on
# every random graph. When several edges have equal weight the two trees can
# be different, but every minimum spanning tree has the same total.
#
# Timing: Kruskal costs O(E log E) for the sort plus almost-constant union-find
# work per edge; heap-based Prim costs O(E log V). Since log E < 2 log V both
# are O(E log V), so the difference comes from constant factors. On the sparse
# graph (E = 3,000) both take about a millisecond. On the dense graph
# (E = 250,000) Kruskal wins in this implementation because its main cost is
# one call to Python's built-in sorted(), which runs in C, while Prim pushes
# and pops up to E heap entries one at a time in Python. In theory a dense
# graph favours Prim with a plain array instead of a heap (O(V^2), no log
# factor), and a sparse graph favours Kruskal, whose sort is cheap when E is
# small.
#
# Dijkstra assumes that once a vertex is popped its distance can never get
# smaller, which is true only when all edges are non-negative. With the
# negative edge b->a, a cheaper route to a is discovered after a has been
# finalised, so Dijkstra reports wrong distances for a and c. Bellman-Ford,
# which relaxes every edge V-1 times, finds the correct values.
