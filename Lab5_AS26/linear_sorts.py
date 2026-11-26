# Q2: Counting Sort and Radix Sort vs Merge Sort (from Lab 1)
#
# Usage:
#   python linear_sorts.py              -> everything
#   python linear_sorts.py stable       -> stability demonstration
#   python linear_sorts.py counting     -> counting sort vs merge sort, n = 100,000, varying k
#   python linear_sorts.py radix        -> radix sort vs merge sort, k = 10^9, varying n

import os
import random
import sys
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Merge sort from Lab 1 (copied into merge_sort.py)
from merge_sort import MergeSort_343 as merge_sort

HERE = os.path.dirname(os.path.abspath(__file__))
PUBLIC = os.path.join(HERE, "public")


# ---------------------------------------------------------------------------
# 1. Stable counting sort for integers in the range 0..k: O(n + k)
#    key(x) extracts the integer key, so it also sorts (key, index) pairs.
# ---------------------------------------------------------------------------
def counting_sort(arr, k, key=lambda x: x):
    count = [0] * (k + 1)
    for x in arr:
        count[key(x)] += 1
    # prefix sums: count[v] = number of elements with key <= v
    for v in range(1, k + 1):
        count[v] += count[v - 1]
    output = [None] * len(arr)
    # walk backwards so equal keys keep their original order (stability)
    for x in reversed(arr):
        kx = key(x)
        count[kx] -= 1
        output[count[kx]] = x
    return output


# ---------------------------------------------------------------------------
# 2. LSD radix sort: stable counting sort on each digit, least significant first
#    O(d * (n + base)), d = number of digits of the maximum value in this base
# ---------------------------------------------------------------------------
def radix_sort(arr, base=10):
    if not arr:
        return []
    max_val = max(arr)
    exp = 1
    out = list(arr)
    while max_val // exp > 0:
        out = counting_sort(out, base - 1, key=lambda x: (x // exp) % base)
        exp *= base
    return out


# ---------------------------------------------------------------------------
# Stability demonstration
# ---------------------------------------------------------------------------
def stability_demo():
    print("=== Stability check: sorting (key, original index) pairs ===")
    rng = random.Random(7)
    keys = [rng.randint(0, 4) for _ in range(12)]
    pairs = [(key, i) for i, key in enumerate(keys)]
    print("Input  (key, index):", pairs)
    result = counting_sort(pairs, 4, key=lambda p: p[0])
    print("Sorted (key, index):", result)
    for v in range(5):
        print(f"  key {v}: indices {[p[1] for p in result if p[0] == v]}")
    stable = all(result[i][1] < result[i + 1][1]
                 for i in range(len(result) - 1) if result[i][0] == result[i + 1][0])
    print("Equal keys keep their original index order -> stable:", stable)

    big = [(rng.randint(0, 100), i) for i in range(10000)]
    print("10,000 random pairs, result equals Python's stable sorted():",
          counting_sort(big, 100, key=lambda p: p[0]) == sorted(big, key=lambda p: p[0]))
    print()


# ---------------------------------------------------------------------------
# Timing helpers
# ---------------------------------------------------------------------------
def timed(func, *args):
    start = time.perf_counter()
    result = func(*args)
    return result, time.perf_counter() - start


# ---------------------------------------------------------------------------
# Experiment 1: counting sort, n = 100,000, k = 10 .. 10^7
# ---------------------------------------------------------------------------
def counting_experiment():
    n = 100_000
    ks = [10, 10**3, 10**5, 10**7]
    print(f"=== Counting sort vs merge sort (n = {n:,}, values 0..k) ===")
    print(f"{'k':>12} | {'Counting (s)':>12} | {'Merge (s)':>10} | {'Faster':>9} | correct")
    print("-" * 62)
    rows = []
    for k in ks:
        rng = random.Random(k)
        arr = [rng.randint(0, k) for _ in range(n)]
        c_out, t_c = timed(counting_sort, arr, k)
        m_out, t_m = timed(merge_sort, arr)
        ok = c_out == m_out == sorted(arr)
        faster = "Counting" if t_c < t_m else "Merge"
        print(f"{k:>12,} | {t_c:>12.4f} | {t_m:>10.4f} | {faster:>9} | {ok}", flush=True)
        rows.append((k, t_c, t_m))

    plt.figure(figsize=(7, 4.5))
    plt.semilogx([r[0] for r in rows], [r[1] for r in rows], "o-", label="Counting sort  O(n + k)")
    plt.semilogx([r[0] for r in rows], [r[2] for r in rows], "s-", label="Merge sort  O(n log n)")
    plt.xlabel("Key range k"); plt.ylabel("Time (s)")
    plt.title(f"Counting sort vs merge sort, n = {n:,}")
    plt.grid(True, which="both", alpha=0.3); plt.legend(); plt.tight_layout()
    path = os.path.join(PUBLIC, "q2_counting_plot.png")
    plt.savefig(path, dpi=120); plt.close()
    print(f"Plot saved to public/{os.path.basename(path)}\n")


# ---------------------------------------------------------------------------
# Experiment 2: radix sort (base 10 and 256) vs merge sort, k = 10^9
# ---------------------------------------------------------------------------
def radix_experiment():
    k = 10**9
    ns = [10_000, 50_000, 100_000, 250_000, 500_000, 1_000_000]
    print(f"=== Radix sort vs merge sort (values 0..{k:,}) ===")
    print(f"{'n':>10} | {'Radix b=10 (s)':>14} | {'Radix b=256 (s)':>15} | {'Merge (s)':>10} | correct")
    print("-" * 70)
    rows = []
    for n in ns:
        rng = random.Random(n)
        arr = [rng.randint(0, k) for _ in range(n)]
        r10, t10 = timed(radix_sort, arr, 10)
        r256, t256 = timed(radix_sort, arr, 256)
        m, tm = timed(merge_sort, arr)
        ok = r10 == r256 == m
        print(f"{n:>10,} | {t10:>14.4f} | {t256:>15.4f} | {tm:>10.4f} | {ok}", flush=True)
        rows.append((n, t10, t256, tm))

    plt.figure(figsize=(7, 4.5))
    ns_ = [r[0] for r in rows]
    plt.plot(ns_, [r[1] for r in rows], "o-", label="Radix sort, base 10 (10 passes)")
    plt.plot(ns_, [r[2] for r in rows], "^-", label="Radix sort, base 256 (4 passes)")
    plt.plot(ns_, [r[3] for r in rows], "s-", label="Merge sort")
    plt.xlabel("n"); plt.ylabel("Time (s)")
    plt.title("Radix sort vs merge sort, values up to 10^9")
    plt.grid(True, alpha=0.3); plt.legend(); plt.tight_layout()
    path = os.path.join(PUBLIC, "q2_radix_plot.png")
    plt.savefig(path, dpi=120); plt.close()
    print(f"Plot saved to public/{os.path.basename(path)}\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    os.makedirs(PUBLIC, exist_ok=True)
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    if arg in ("stable", "all"):
        stability_demo()
    if arg in ("counting", "all"):
        counting_experiment()
    if arg in ("radix", "all"):
        radix_experiment()
    if arg not in ("stable", "counting", "radix", "all"):
        print("Unknown option. Use: stable | counting | radix")


# Analysis / Conclusion:
# Counting sort runs in O(n + k). With n fixed at 100,000 it is much faster
# than merge sort while k is small (k = 10 .. 10^5), because it never compares
# elements and just makes a few linear passes. When k grows far beyond n
# (k = 10^7) the O(k) work of allocating and prefix-summing the count array
# dominates, and it loses to merge sort's O(n log n).
#
# Radix sort keeps the count array small by sorting one digit at a time:
# O(d (n + b)). With base 10, values up to 10^9 need d = 10 passes; with
# base 256 they need only d = 4 passes over a 256-entry count array, so base
# 256 is roughly 2x faster than base 10. Both grow linearly in n, while merge
# sort grows as n log n. In pure Python, base-256 radix sort beats merge sort,
# while base-10 radix sort is closer because its 10 passes cost about as much
# as merge sort's log2(n) ~ 20 levels.
#
# Linear-time sorts win when keys are integers from a small range (counting
# sort) or have few digits relative to log n (radix sort). They lose when the
# key range is huge compared to n, when keys are not small integers, or when
# the number of digit passes approaches log n.
#
# The (key, index) demonstration shows that equal keys keep their original
# relative order, which is exactly why counting sort can be used inside radix
# sort: each pass must preserve the order produced by the previous digit.
