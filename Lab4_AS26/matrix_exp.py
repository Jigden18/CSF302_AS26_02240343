# Part B: Efficient Matrix Modular Exponentiation — naive vs binary (repeated squaring)
#
# Usage:
#   python matrix_exp.py              -> everything
#   python matrix_exp.py compare      -> naive vs binary on different matrices
#   python matrix_exp.py fibonacci    -> Fibonacci mod m + counting walks in a graph
#   python matrix_exp.py benchmark    -> timing table (also saves public/partB_benchmark_chart.png)

import os
import sys
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PUBLIC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")

MOD = 10**9 + 7


# ---------------------------------------------------------------------------
# Basic matrix helpers
# ---------------------------------------------------------------------------
def validate_matrix(A, m):
    if m < 1:
        raise ValueError(f"Invalid modulus m={m}: modulus must be >= 1")
    n = len(A)
    if n == 0 or any(len(row) != n for row in A):
        raise ValueError("Matrix must be square and non-empty")


def identity_matrix(d):
    return [[1 if i == j else 0 for j in range(d)] for i in range(d)]


def mat_mult_mod(A, B, m):
    # C[i][j] = sum_k A[i][k] * B[k][j]  (mod m)
    d = len(A)
    B_cols = list(zip(*B))          # columns of B for faster access
    C = [[0] * d for _ in range(d)]
    for i in range(d):
        row = A[i]
        for j in range(d):
            col = B_cols[j]
            total = 0
            for k in range(d):
                total += row[k] * col[k]
            C[i][j] = total % m
    return C


def reduce_matrix(A, m):
    return [[x % m for x in row] for row in A]


# ---------------------------------------------------------------------------
# 1. Naive Matrix Exponentiation: n multiplications -> O(n * d^3)
# ---------------------------------------------------------------------------
def naive_matrix_exp(A, n, m):
    validate_matrix(A, m)
    if n < 0:
        raise ValueError("Negative exponent is not supported")
    d = len(A)
    A = reduce_matrix(A, m)
    result = reduce_matrix(identity_matrix(d), m)   # A^0 = I (mod m)
    for _ in range(n):
        result = mat_mult_mod(result, A, m)
    return result


# ---------------------------------------------------------------------------
# 2. Binary Matrix Exponentiation (repeated squaring): O(log n * d^3)
# ---------------------------------------------------------------------------
def binary_matrix_exp(A, n, m):
    validate_matrix(A, m)
    if n < 0:
        raise ValueError("Negative exponent is not supported")
    d = len(A)
    base = reduce_matrix(A, m)
    result = reduce_matrix(identity_matrix(d), m)
    while n:
        if n & 1:
            result = mat_mult_mod(result, base, m)
        base = mat_mult_mod(base, base, m)
        n >>= 1
    return result


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
_seed = 2024

def _next_rand():
    global _seed
    _seed = (1103515245 * _seed + 12345) % (2 ** 31)
    return _seed


def random_matrix(d, low=0, high=9):
    return [[low + _next_rand() % (high - low + 1) for _ in range(d)] for _ in range(d)]


def print_matrix(M, label=""):
    if label:
        print(label)
    for row in M:
        print("  ", row)


# ---------------------------------------------------------------------------
# Comparison of naive vs binary
# ---------------------------------------------------------------------------
def compare_outputs():
    print("=== Output comparison: naive vs binary matrix exponentiation ===")
    cases = [
        ([[1, 1], [1, 0]], 10, 1000),
        ([[2, 3], [1, 4]], 25, 97),
        ([[1, 2, 3], [4, 5, 6], [7, 8, 9]], 50, 10**9 + 7),
        ([[-1, 2], [3, -4]], 7, 13),          # negative entries
        ([[5, 7], [9, 11]], 0, 17),           # zero exponent -> identity
        (random_matrix(4), 100, 1009),
    ]
    for A, n, m in cases:
        naive = naive_matrix_exp(A, n, m)
        binary = binary_matrix_exp(A, n, m)
        print(f"\nA = {A}, n = {n}, m = {m}")
        print_matrix(binary, "  A^n mod m:")
        print("  Results match:", naive == binary)


# ---------------------------------------------------------------------------
# Fibonacci via matrix exponentiation
#   [[1, 1], [1, 0]]^n = [[F(n+1), F(n)], [F(n), F(n-1)]]
# ---------------------------------------------------------------------------
def fibonacci_mod(n, m):
    if n < 0:
        raise ValueError("n must be non-negative")
    Q = [[1, 1], [1, 0]]
    return binary_matrix_exp(Q, n, m)[0][1]


def fibonacci_iterative_mod(n, m):
    # Reference check for small n only
    a, b = 0, 1
    for _ in range(n):
        a, b = b, (a + b) % m
    return a % m


def fibonacci_demo():
    print("\n=== Fibonacci numbers modulo m using matrix exponentiation ===")
    print("First 15 Fibonacci numbers:", [fibonacci_mod(i, MOD) for i in range(15)])
    for n, m in [(50, 10**9 + 7), (1000, 1000), (10000, 10**9 + 7)]:
        f = fibonacci_mod(n, m)
        ref = fibonacci_iterative_mod(n, m)
        print(f"F({n}) mod {m} = {f}  (iterative check: {ref}, match={f == ref})")

    n = 10**18
    start = time.perf_counter()
    f = fibonacci_mod(n, MOD)
    elapsed = time.perf_counter() - start
    print(f"\nF(10^18) mod (10^9 + 7) = {f}   [computed in {elapsed:.6f} s,"
          f" only ~{n.bit_length()} squarings]")


# ---------------------------------------------------------------------------
# Counting walks of exactly k edges in a directed graph
#   (A^k)[u][v] = number of walks of length k from u to v
# ---------------------------------------------------------------------------
def count_walks(adj, u, v, k, m):
    return binary_matrix_exp(adj, k, m)[u][v]


def walks_demo():
    print("\n=== Counting walks of exactly k edges in a directed graph ===")
    # Directed graph: 0->1, 0->2, 1->2, 2->0, 2->3, 3->1
    adj = [
        [0, 1, 1, 0],
        [0, 0, 1, 0],
        [1, 0, 0, 1],
        [0, 1, 0, 0],
    ]
    print_matrix(adj, "Adjacency matrix (edges 0->1, 0->2, 1->2, 2->0, 2->3, 3->1):")
    for u, v, k in [(0, 3, 2), (0, 0, 3), (0, 2, 5), (1, 3, 10)]:
        fast = count_walks(adj, u, v, k, MOD)
        slow = naive_matrix_exp(adj, k, MOD)[u][v]
        print(f"Walks of length {k:>2} from {u} to {v}: {fast}  (naive check: {slow})")
    k = 10**12
    print(f"Walks of length 10^12 from 0 to 3 (mod 10^9+7): {count_walks(adj, 0, 3, k, MOD)}")


# ---------------------------------------------------------------------------
# Benchmark: dimensions d = 2..32, exponents n = 2^4..2^12
# ---------------------------------------------------------------------------
def time_once(func, A, n, m):
    start = time.perf_counter()
    func(A, n, m)
    return time.perf_counter() - start


def benchmark():
    print("\n=== Benchmark: naive vs binary matrix exponentiation (m = 10^9+7) ===")
    dims = [2, 4, 8, 16, 32]
    exps = [2 ** p for p in range(4, 13)]
    print(f"{'d':>4} {'n':>6} | {'Naive (s)':>12} | {'Binary (s)':>12} | {'Speedup':>9}")
    print("-" * 54)
    data = {}
    for d in dims:
        A = random_matrix(d)
        for n in exps:
            t_naive = time_once(naive_matrix_exp, A, n, MOD)
            t_bin = time_once(binary_matrix_exp, A, n, MOD)
            print(f"{d:>4} {n:>6} | {t_naive:>12.6f} | {t_bin:>12.6f} | {t_naive / t_bin:>8.1f}x",
                  flush=True)
            data.setdefault(d, []).append((n, t_naive, t_bin))
        print("-" * 54)
    plot_benchmark(data)


def plot_benchmark(data):
    os.makedirs(PUBLIC, exist_ok=True)
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
    for d, pts in data.items():
        ns = [p[0] for p in pts]
        line, = ax[0].loglog(ns, [p[1] for p in pts], "o-", label=f"naive d={d}")
        ax[0].loglog(ns, [p[2] for p in pts], "s--", color=line.get_color(), label=f"binary d={d}")
        ax[1].semilogx(ns, [p[1] / p[2] for p in pts], "o-", base=2, label=f"d={d}")
    ax[0].set_xscale("log", base=2)
    ax[0].set_xlabel("Exponent n"); ax[0].set_ylabel("Time (s)")
    ax[0].set_title("Matrix exponentiation time"); ax[0].grid(True, which="both", alpha=0.3)
    ax[0].legend(fontsize=7, ncol=2)
    ax[1].set_xlabel("Exponent n"); ax[1].set_ylabel("Speedup (naive / binary)")
    ax[1].set_title("Speedup of binary over naive"); ax[1].grid(True, alpha=0.3); ax[1].legend()
    plt.tight_layout()
    plt.savefig(os.path.join(PUBLIC, "partB_benchmark_chart.png"), dpi=120); plt.close()
    print("Plot saved to public/partB_benchmark_chart.png")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    if arg in ("compare", "all"):
        compare_outputs()
    if arg in ("fibonacci", "all"):
        fibonacci_demo()
        walks_demo()
    if arg in ("benchmark", "all"):
        benchmark()
    if arg not in ("compare", "fibonacci", "benchmark", "all"):
        print("Unknown option. Use: compare | fibonacci | benchmark")


# Analysis / Conclusion:
# Naive and binary matrix exponentiation give identical matrices for every
# test case. One d x d multiplication costs O(d^3), so the naive method costs
# O(n * d^3) while repeated squaring costs O(log n * d^3). For a power of two
# n = 2^p, binary exponentiation needs only about p squarings, so in the
# benchmark the binary time grows by a constant step each time n doubles,
# while the naive time doubles. The speedup is roughly n / (2 log2 n) and is
# independent of d, while both methods grow by about 8x each time d doubles.
# Repeated squaring makes otherwise impossible computations practical:
# F(10^18) mod (10^9 + 7) is obtained from about 60 squarings of a 2 x 2
# matrix, and the number of length-k walks in a graph is read straight from
# A^k without enumerating any walks.
