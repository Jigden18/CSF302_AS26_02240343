# Q2: Matrix Chain Multiplication — bottom-up DP vs brute-force recursive search
#
# Usage:
#   python matrix_chain.py              -> everything
#   python matrix_chain.py fixed        -> the two given chains
#   python matrix_chain.py random       -> 5 random chains

import random
import sys


# ---------------------------------------------------------------------------
# 1. Bottom-up DP: m[i][j] = min cost of A_i..A_j, s[i][j] = best split k
#    Matrix A_i has dimensions p[i-1] x p[i]. O(n^3) time, O(n^2) space.
# ---------------------------------------------------------------------------
def matrix_chain_order(p):
    n = len(p) - 1
    m = [[0] * (n + 1) for _ in range(n + 1)]
    s = [[0] * (n + 1) for _ in range(n + 1)]
    for length in range(2, n + 1):              # chain length
        for i in range(1, n - length + 2):
            j = i + length - 1
            m[i][j] = float("inf")
            for k in range(i, j):
                cost = m[i][k] + m[k + 1][j] + p[i - 1] * p[k] * p[j]
                if cost < m[i][j]:
                    m[i][j] = cost
                    s[i][j] = k
    return m, s


def parenthesise(s, i, j):
    if i == j:
        return f"A{i}"
    k = s[i][j]
    return "(" + parenthesise(s, i, k) + parenthesise(s, k + 1, j) + ")"


# ---------------------------------------------------------------------------
# 2. Brute-force recursive search: tries every split, no memoization
#    (exponential: the number of parenthesisations is a Catalan number)
# ---------------------------------------------------------------------------
def brute_force(p, i, j):
    if i == j:
        return 0, f"A{i}"
    best_cost, best_paren = float("inf"), ""
    for k in range(i, j):
        left_cost, left_paren = brute_force(p, i, k)
        right_cost, right_paren = brute_force(p, k + 1, j)
        cost = left_cost + right_cost + p[i - 1] * p[k] * p[j]
        if cost < best_cost:
            best_cost, best_paren = cost, "(" + left_paren + right_paren + ")"
    return best_cost, best_paren


# ---------------------------------------------------------------------------
# Left-to-right order ((((A1A2)A3)A4)...): the running product is p0 x p[i-1]
# ---------------------------------------------------------------------------
def left_to_right_cost(p):
    n = len(p) - 1
    return sum(p[0] * p[i - 1] * p[i] for i in range(2, n + 1))


def left_to_right_paren(n):
    expr = "A1"
    for i in range(2, n + 1):
        expr = f"({expr}A{i})"
    return expr


# ---------------------------------------------------------------------------
# Report for one chain
# ---------------------------------------------------------------------------
def report(p, label):
    n = len(p) - 1
    m, s = matrix_chain_order(p)
    optimal = m[1][n]
    paren = parenthesise(s, 1, n)
    print(f"{label}: dimensions <{', '.join(map(str, p))}>  ({n} matrices)")
    print(f"  Optimal cost (DP)        : {optimal:,}")
    print(f"  Optimal parenthesisation : {paren}")
    if n <= 8:
        bf_cost, bf_paren = brute_force(p, 1, n)
        print(f"  Brute-force cost         : {bf_cost:,}   match: {bf_cost == optimal}")
    ltr = left_to_right_cost(p)
    print(f"  Left-to-right cost       : {ltr:,}   {left_to_right_paren(n)}")
    print(f"  Left-to-right / optimal  : {ltr / optimal:.2f}x")
    print()
    return optimal


def fixed_chains():
    print("=== Matrix chain multiplication: given chains ===\n")
    c1 = report([30, 35, 15, 5, 10, 20, 25], "Chain 1")
    print(f"  Expected minimum 15,125 -> {'correct' if c1 == 15125 else 'WRONG'}\n")
    report([5, 4, 6, 2, 7], "Chain 2")


def random_chains():
    print("=== Matrix chain multiplication: 5 random chains (verified by brute force) ===\n")
    rng = random.Random(6)
    for t in range(1, 6):
        n = rng.randint(4, 8)
        p = [rng.randint(2, 50) for _ in range(n + 1)]
        report(p, f"Random chain {t}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    if arg in ("fixed", "all"):
        fixed_chains()
    if arg in ("random", "all"):
        random_chains()
    if arg not in ("fixed", "random", "all"):
        print("Unknown option. Use: fixed | random")


# Analysis / Conclusion:
# The bottom-up DP fills m[i][j] for chains of increasing length, trying
# every split point k, in O(n^3) time. Storing the best k in s[i][j] lets us
# rebuild the optimal parenthesisation recursively.
#
# For <30, 35, 15, 5, 10, 20, 25> the DP gives 15,125 multiplications with
# ((A1(A2A3))((A4A5)A6)), matching the expected answer. The brute-force
# search tries every parenthesisation (a Catalan number of them) and finds
# the same minimum for every chain of up to 8 matrices, which confirms the DP.
#
# The left-to-right order can be several times more expensive than the
# optimal order, so choosing the parenthesisation matters even though every
# order gives the same product matrix.
