# Q1: Rod Cutting — naive recursion vs top-down memoization vs bottom-up tabulation
#
# Usage:
#   python rod_cutting.py              -> everything
#   python rod_cutting.py revenue      -> maximum revenue and pieces for n = 1..10
#   python rod_cutting.py calls        -> call counts and timing for n = 5..25

import sys
import time

BASE_PRICES = [1, 5, 8, 9, 10, 17, 17, 20, 24, 30]


def make_prices(n):
    # p[0] = 0, p[1..10] from the table, p[i] = 3*i for i > 10
    p = [0] + BASE_PRICES[:]
    for i in range(11, n + 1):
        p.append(3 * i)
    return p


calls = 0


# ---------------------------------------------------------------------------
# 1. Naive recursive solution: tries every first cut, recomputes subproblems
#    T(n) = 1 + sum_{j<n} T(j) = 2^n calls
# ---------------------------------------------------------------------------
def cut_rod_naive(p, n):
    global calls
    calls += 1
    if n == 0:
        return 0
    q = float("-inf")
    for i in range(1, n + 1):
        q = max(q, p[i] + cut_rod_naive(p, n - i))
    return q


# ---------------------------------------------------------------------------
# 2. Top-down memoized solution: each subproblem is solved once
# ---------------------------------------------------------------------------
def cut_rod_memo(p, n):
    memo = [None] * (n + 1)
    return _memo_aux(p, n, memo)


def _memo_aux(p, n, memo):
    global calls
    calls += 1
    if memo[n] is not None:
        return memo[n]
    if n == 0:
        q = 0
    else:
        q = float("-inf")
        for i in range(1, n + 1):
            q = max(q, p[i] + _memo_aux(p, n - i, memo))
    memo[n] = q
    return q


# ---------------------------------------------------------------------------
# 3. Bottom-up tabulated solution (no recursion), also records the first cut
#    so the list of pieces can be rebuilt
# ---------------------------------------------------------------------------
loop_steps = 0


def cut_rod_bottom_up(p, n):
    global loop_steps
    r = [0] * (n + 1)          # r[j] = best revenue for length j
    s = [0] * (n + 1)          # s[j] = size of the first piece in an optimal cut
    for j in range(1, n + 1):
        q = float("-inf")
        for i in range(1, j + 1):
            loop_steps += 1
            if p[i] + r[j - i] > q:
                q = p[i] + r[j - i]
                s[j] = i
        r[j] = q
    return r, s


def pieces(s, n):
    result = []
    while n > 0:
        result.append(s[n])
        n -= s[n]
    return result


# ---------------------------------------------------------------------------
# Maximum revenue and pieces for n = 1..10
# ---------------------------------------------------------------------------
def revenue_table():
    global calls
    p = make_prices(10)
    print("=== Rod cutting: maximum revenue for n = 1..10 ===")
    print("Prices:", ", ".join(f"p{i}={p[i]}" for i in range(1, 11)))
    print()
    print(f"{'n':>3} | {'Naive':>5} | {'Memo':>5} | {'Bottom-up':>9} | Pieces")
    print("-" * 50)
    r, s = cut_rod_bottom_up(p, 10)
    for n in range(1, 11):
        calls = 0
        naive = cut_rod_naive(p, n)
        memo = cut_rod_memo(p, n)
        print(f"{n:>3} | {naive:>5} | {memo:>5} | {r[n]:>9} | {pieces(s, n)}")
    print()


# ---------------------------------------------------------------------------
# Call counts and execution time for n = 5, 10, 15, 20, 25
# ---------------------------------------------------------------------------
def calls_table():
    global calls, loop_steps
    print("=== Recursive calls and execution time (p[i] = 3*i for i > 10) ===")
    print(f"{'n':>3} | {'Revenue':>7} | {'Naive calls':>12} {'time (s)':>9} | "
          f"{'Memo calls':>10} {'time (s)':>9} | {'Bottom-up calls':>15} {'loop steps':>10} {'time (s)':>9}")
    print("-" * 104)
    for n in [5, 10, 15, 20, 25]:
        p = make_prices(n)

        calls = 0
        start = time.perf_counter()
        naive = cut_rod_naive(p, n)
        t_naive = time.perf_counter() - start
        naive_calls = calls

        calls = 0
        start = time.perf_counter()
        memo = cut_rod_memo(p, n)
        t_memo = time.perf_counter() - start
        memo_calls = calls

        loop_steps = 0
        start = time.perf_counter()
        r, _ = cut_rod_bottom_up(p, n)
        t_bu = time.perf_counter() - start

        assert naive == memo == r[n]
        print(f"{n:>3} | {naive:>7} | {naive_calls:>12,} {t_naive:>9.4f} | "
              f"{memo_calls:>10,} {t_memo:>9.6f} | {0:>15} {loop_steps:>10,} {t_bu:>9.6f}", flush=True)
    print()
    print("Naive calls = 2^n;  memo calls = 1 + n(n+1)/2;  bottom-up loop steps = n(n+1)/2")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    if arg in ("revenue", "all"):
        revenue_table()
    if arg in ("calls", "all"):
        calls_table()
    if arg not in ("revenue", "calls", "all"):
        print("Unknown option. Use: revenue | calls")


# Analysis / Conclusion:
# All three versions return the same maximum revenue for every n.
#
# The naive recursion solves the same subproblems again and again: a rod of
# length n calls itself on every length n-1, n-2, ..., 0, so the number of
# calls satisfies T(n) = 1 + T(0) + ... + T(n-1) = 2^n. Going from n = 20 to
# n = 25 multiplies the work by 32, and n = 25 already needs over 33 million
# calls.
#
# The memoized version stores each answer the first time it is computed.
# Each of the n+1 subproblems does its loop once, and every other call is a
# table lookup, so it makes only 1 + n(n+1)/2 calls (326 for n = 25): Theta(n^2).
#
# The bottom-up version makes no recursive calls at all. It fills r[1..n] in
# increasing order with the same n(n+1)/2 loop steps, so it has the same
# Theta(n^2) cost as memoization without the function-call overhead, and it
# is the fastest of the three.
