# Q1: Quicksort Variants — Lomuto, Hoare, Randomised and Three-way (Dutch national flag)
#
# Usage:
#   python quicksort_variants.py              -> correctness check + all four tables
#   python quicksort_variants.py check        -> correctness check only
#   python quicksort_variants.py random       -> table for random input
#   python quicksort_variants.py sorted       -> table for already sorted input
#   python quicksort_variants.py reverse      -> table for reverse sorted input
#   python quicksort_variants.py duplicates   -> table for many duplicates (0..9)

import random
import sys
import time

rng = random.Random(42)
comparisons = 0


# ---------------------------------------------------------------------------
# 1. Lomuto partition (last element as pivot)
# ---------------------------------------------------------------------------
def lomuto_partition(arr, lo, hi):
    global comparisons
    pivot = arr[hi]
    i = lo - 1
    for j in range(lo, hi):
        comparisons += 1
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[hi] = arr[hi], arr[i + 1]
    return i + 1


def quicksort_lomuto(arr, lo=0, hi=None):
    if hi is None:
        hi = len(arr) - 1
    while lo < hi:
        p = lomuto_partition(arr, lo, hi)
        # Recurse on the smaller part, loop on the larger part
        if p - lo < hi - p:
            quicksort_lomuto(arr, lo, p - 1)
            lo = p + 1
        else:
            quicksort_lomuto(arr, p + 1, hi)
            hi = p - 1


# ---------------------------------------------------------------------------
# 2. Hoare partition (first element as pivot)
# ---------------------------------------------------------------------------
def hoare_partition(arr, lo, hi):
    global comparisons
    pivot = arr[lo]
    i, j = lo - 1, hi + 1
    while True:
        i += 1
        comparisons += 1
        while arr[i] < pivot:
            i += 1
            comparisons += 1
        j -= 1
        comparisons += 1
        while arr[j] > pivot:
            j -= 1
            comparisons += 1
        if i >= j:
            return j
        arr[i], arr[j] = arr[j], arr[i]


def quicksort_hoare(arr, lo=0, hi=None):
    if hi is None:
        hi = len(arr) - 1
    while lo < hi:
        p = hoare_partition(arr, lo, hi)     # splits into [lo..p] and [p+1..hi]
        if p - lo < hi - p:
            quicksort_hoare(arr, lo, p)
            lo = p + 1
        else:
            quicksort_hoare(arr, p + 1, hi)
            hi = p


# ---------------------------------------------------------------------------
# 3. Randomised quicksort (random pivot swapped to the end, then Lomuto)
# ---------------------------------------------------------------------------
def quicksort_randomised(arr, lo=0, hi=None):
    if hi is None:
        hi = len(arr) - 1
    while lo < hi:
        r = rng.randint(lo, hi)
        arr[r], arr[hi] = arr[hi], arr[r]
        p = lomuto_partition(arr, lo, hi)
        if p - lo < hi - p:
            quicksort_randomised(arr, lo, p - 1)
            lo = p + 1
        else:
            quicksort_randomised(arr, p + 1, hi)
            hi = p - 1


# ---------------------------------------------------------------------------
# 4. Three-way quicksort (Dutch national flag), random pivot
#    arr[lo..lt-1] < pivot, arr[lt..gt] == pivot, arr[gt+1..hi] > pivot
# ---------------------------------------------------------------------------
def three_way_partition(arr, lo, hi):
    global comparisons
    r = rng.randint(lo, hi)
    pivot = arr[r]
    lt, i, gt = lo, lo, hi
    while i <= gt:
        comparisons += 1
        if arr[i] < pivot:
            arr[lt], arr[i] = arr[i], arr[lt]
            lt += 1
            i += 1
        else:
            comparisons += 1
            if arr[i] > pivot:
                arr[i], arr[gt] = arr[gt], arr[i]
                gt -= 1
            else:
                i += 1
    return lt, gt


def quicksort_three_way(arr, lo=0, hi=None):
    if hi is None:
        hi = len(arr) - 1
    while lo < hi:
        lt, gt = three_way_partition(arr, lo, hi)
        if lt - lo < hi - gt:
            quicksort_three_way(arr, lo, lt - 1)
            lo = gt + 1
        else:
            quicksort_three_way(arr, gt + 1, hi)
            hi = lt - 1


VARIANTS = [
    ("Lomuto", quicksort_lomuto),
    ("Hoare", quicksort_hoare),
    ("Randomised", quicksort_randomised),
    ("Three-way", quicksort_three_way),
]


# ---------------------------------------------------------------------------
# Input generators
# ---------------------------------------------------------------------------
def make_input(kind, n):
    data_rng = random.Random(n)            # same data for every variant
    if kind == "random":
        return [data_rng.randint(0, 10**6) for _ in range(n)]
    if kind == "sorted":
        return list(range(n))
    if kind == "reverse":
        return list(range(n, 0, -1))
    if kind == "duplicates":
        return [data_rng.randint(0, 9) for _ in range(n)]
    raise ValueError(kind)


INPUT_TYPES = {
    "random": "Random",
    "sorted": "Already sorted",
    "reverse": "Reverse sorted",
    "duplicates": "Many duplicates (0..9)",
}
SIZES = [1000, 2000, 4000, 8000, 16000]


# ---------------------------------------------------------------------------
# Correctness check
# ---------------------------------------------------------------------------
def correctness_check():
    print("=== Correctness check (each variant vs Python sorted()) ===")
    for name, sort in VARIANTS:
        ok = True
        for kind in INPUT_TYPES:
            for n in [0, 1, 2, 10, 500]:
                arr = make_input(kind, n)
                expected = sorted(arr)
                sort(arr)
                ok = ok and arr == expected
        print(f"{name:<12}: {'all inputs sorted correctly' if ok else 'FAILED'}")
    print()


# ---------------------------------------------------------------------------
# Benchmark table for one input type
# ---------------------------------------------------------------------------
def run_table(kind):
    global comparisons
    print(f"=== Input type: {INPUT_TYPES[kind]} ===")
    header = f"{'n':>7} |" + "|".join(f"{name:^24}" for name, _ in VARIANTS)
    sub = f"{'':>7} |" + "|".join(f"{'comparisons':>13} {'time (s)':>9} " for _ in VARIANTS)
    print(header)
    print(sub)
    print("-" * len(sub))
    for n in SIZES:
        row = f"{n:>7} |"
        cells = []
        for name, sort in VARIANTS:
            arr = make_input(kind, n)
            comparisons = 0
            start = time.perf_counter()
            sort(arr)
            elapsed = time.perf_counter() - start
            cells.append(f"{comparisons:>13,} {elapsed:>9.4f} ")
        print(row + "|".join(cells), flush=True)
    # n^2/2 reference, to spot quadratic behaviour
    print(f"Reference: n^2/2 at n=16000 = {16000 * 16000 // 2:,}   n*log2(n) at n=16000 = {int(16000 * 13.97):,}")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    if arg == "check":
        correctness_check()
    elif arg in INPUT_TYPES:
        run_table(arg)
    elif arg == "all":
        correctness_check()
        for kind in INPUT_TYPES:
            run_table(kind)
    else:
        print("Unknown option. Use: check | random | sorted | reverse | duplicates")


# Analysis / Conclusion:
# Every variant recurses only on the smaller side and loops on the larger
# side, so the recursion depth stays O(log n) even when a partition is
# completely unbalanced, and sorted inputs never hit the recursion limit.
#
# Random input: all four variants take Theta(n log n) comparisons.
#
# Lomuto (last element pivot) degrades to Theta(n^2) on sorted and reverse
# sorted input, because the pivot is always the max (or min), so one side of
# every partition is empty. It also degrades on many duplicates: elements
# equal to the pivot all go to the left side (arr[j] <= pivot), so a run of
# equal values is split off one element at a time.
#
# Hoare (first element pivot) degrades to Theta(n^2) on sorted and reverse
# sorted input for the same reason (the pivot is the min or max). It handles
# duplicates well, because both scans stop on elements equal to the pivot
# and swap them, which splits a run of equal values in the middle.
#
# Randomised quicksort fixes the sorted and reverse cases (expected
# Theta(n log n) on any order), but it still uses Lomuto, so on many
# duplicates it is still Theta(n^2): a random pivot cannot help when most
# elements are equal to it.
#
# Three-way quicksort groups everything equal to the pivot in the middle and
# never touches it again. With only 10 distinct values it needs about 10
# partition levels, so it is the fastest on duplicates and stays
# Theta(n log n) on every input type.
