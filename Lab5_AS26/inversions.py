# Q3: Counting Inversions — brute force O(n^2) vs merge-sort-based O(n log n)
#
# Usage:
#   python inversions.py              -> verify + timing + Kendall tau
#   python inversions.py verify       -> brute force vs merge sort on random arrays (n <= 2,000)
#   python inversions.py timing       -> timing for n = 1,000 .. 1,000,000
#   python inversions.py kendall      -> Kendall tau distance between two users' movie rankings

import random
import sys
import time

TIME_LIMIT = 60.0      # seconds; brute force is abandoned after this


class TimeLimitExceeded(Exception):
    pass


# ---------------------------------------------------------------------------
# 1. Brute force: check every pair (i < j) -> O(n^2)
# ---------------------------------------------------------------------------
def count_inversions_brute(arr, time_limit=None):
    n = len(arr)
    start = time.perf_counter()
    count = 0
    for i in range(n):
        ai = arr[i]
        for j in range(i + 1, n):
            if ai > arr[j]:
                count += 1
        if time_limit is not None and time.perf_counter() - start > time_limit:
            raise TimeLimitExceeded
    return count


# ---------------------------------------------------------------------------
# 2. Merge-sort-based: count split inversions while merging -> O(n log n)
#    When right[j] is taken before left[i], it is smaller than every
#    remaining element of left, giving len(left) - i inversions at once.
# ---------------------------------------------------------------------------
def sort_and_count(arr):
    n = len(arr)
    if n <= 1:
        return list(arr), 0
    mid = n // 2
    left, inv_left = sort_and_count(arr[:mid])
    right, inv_right = sort_and_count(arr[mid:])

    merged = []
    i = j = 0
    split = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            split += len(left) - i
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged, inv_left + inv_right + split


def count_inversions_merge(arr):
    return sort_and_count(arr)[1]


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------
def verify():
    print("=== Verification: brute force vs merge sort (random arrays, n <= 2,000) ===")
    rng = random.Random(1)
    print(f"{'n':>6} | {'Brute force':>12} | {'Merge sort':>12} | match")
    print("-" * 45)
    all_ok = True
    for n in [0, 1, 2, 5, 10, 50, 100, 250, 500, 1000, 1500, 2000]:
        arr = [rng.randint(0, 1000) for _ in range(n)]
        b = count_inversions_brute(arr)
        m = count_inversions_merge(arr)
        all_ok = all_ok and b == m
        print(f"{n:>6} | {b:>12,} | {m:>12,} | {b == m}")
    extra_ok = True
    for _ in range(200):
        n = rng.randint(0, 2000)
        arr = [rng.randint(0, 50) for _ in range(n)]       # with duplicates
        extra_ok = extra_ok and count_inversions_brute(arr) == count_inversions_merge(arr)
    print(f"\n200 extra random arrays (sizes 0..2000, with duplicates) all match: {extra_ok}")
    print(f"Edge cases: sorted 1..2000 -> {count_inversions_merge(list(range(2000)))}, "
          f"reverse 2000..1 -> {count_inversions_merge(list(range(2000, 0, -1))):,} "
          f"(n(n-1)/2 = {2000 * 1999 // 2:,})")
    print("All verified:", all_ok and extra_ok)
    print()


# ---------------------------------------------------------------------------
# Timing
# ---------------------------------------------------------------------------
def timing():
    sizes = [1_000, 2_000, 5_000, 10_000, 20_000, 50_000, 100_000, 200_000, 500_000, 1_000_000]
    print(f"=== Timing: brute force vs merge sort (brute force stops after {TIME_LIMIT:.0f} s) ===")
    print(f"{'n':>10} | {'Inversions':>16} | {'Brute force (s)':>16} | {'Merge sort (s)':>15}")
    print("-" * 68)
    brute_stopped = False
    for n in sizes:
        rng = random.Random(n)
        arr = [rng.randint(0, 10**9) for _ in range(n)]

        start = time.perf_counter()
        inv = count_inversions_merge(arr)
        t_merge = time.perf_counter() - start

        if brute_stopped:
            brute_cell = "skipped"
        else:
            start = time.perf_counter()
            try:
                b = count_inversions_brute(arr, TIME_LIMIT)
                t_brute = time.perf_counter() - start
                brute_cell = f"{t_brute:.4f}" + ("" if b == inv else " MISMATCH")
            except TimeLimitExceeded:
                brute_stopped = True
                brute_cell = f"> {TIME_LIMIT:.0f} (stopped)"
        print(f"{n:>10,} | {inv:>16,} | {brute_cell:>16} | {t_merge:>15.4f}", flush=True)
    print()


# ---------------------------------------------------------------------------
# Kendall tau distance between two users' movie rankings
# ---------------------------------------------------------------------------
MOVIES = [
    "The Shawshank Redemption",
    "The Godfather",
    "The Dark Knight",
    "Pulp Fiction",
    "Forrest Gump",
    "Inception",
    "Fight Club",
    "The Matrix",
    "Interstellar",
    "Parasite",
]


def read_ranking(user):
    n = len(MOVIES)
    while True:
        raw = input(f"{user}, enter the {n} movie numbers from favourite to least favourite: ").split()
        try:
            ranking = [int(x) for x in raw]
        except ValueError:
            print("  Error: please enter numbers only.")
            continue
        if sorted(ranking) != list(range(1, n + 1)):
            print(f"  Error: enter each number from 1 to {n} exactly once.")
            continue
        return ranking


def kendall_tau_distance(rank_a, rank_b):
    # Position of each movie in user A's list, then rewrite user B's list as
    # A-positions. Every pair the two users order differently is an inversion.
    pos_in_a = {movie: i for i, movie in enumerate(rank_a)}
    seq = [pos_in_a[movie] for movie in rank_b]
    return count_inversions_merge(seq), count_inversions_brute(seq)


def kendall():
    print("=== Kendall tau distance between two users' movie rankings ===")
    for i, m in enumerate(MOVIES, 1):
        print(f"  {i:>2}. {m}")
    print()
    a = read_ranking("User 1")
    b = read_ranking("User 2")

    print("\n{:<5}{:<28}{:<28}".format("Rank", "User 1", "User 2"))
    for r in range(len(MOVIES)):
        print(f"{r + 1:<5}{MOVIES[a[r] - 1]:<28}{MOVIES[b[r] - 1]:<28}")

    d, d_brute = kendall_tau_distance(a, b)
    n = len(MOVIES)
    max_pairs = n * (n - 1) // 2
    similarity = 1 - d / max_pairs
    tau = 1 - 2 * d / max_pairs
    print(f"\nKendall tau distance (disagreeing pairs): {d} of {max_pairs}  (brute-force check: {d_brute})")
    print(f"Normalised distance: {d / max_pairs:.3f}")
    print(f"Similarity (1 - distance/{max_pairs}): {similarity:.3f}  ({similarity * 100:.1f}%)")
    print(f"Kendall tau correlation: {tau:+.3f}  (+1 identical, -1 completely reversed)")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    if arg in ("verify", "all"):
        verify()
    if arg in ("timing", "all"):
        timing()
    if arg in ("kendall", "all"):
        kendall()
    if arg not in ("verify", "timing", "kendall", "all"):
        print("Unknown option. Use: verify | timing | kendall")


# Analysis / Conclusion:
# Both methods return the same inversion count on every test array. The
# brute-force method checks all n(n-1)/2 pairs, so doubling n makes it about
# 4x slower and it passes the 60-second limit before n reaches 100,000. The
# merge-sort method counts all "split" inversions of a merge step at once
# (len(left) - i when an element from the right half is taken first), so it
# runs in O(n log n) and handles n = 1,000,000 in a few seconds.
#
# The Kendall tau distance between two rankings is the number of movie
# pairs the two users order differently. Rewriting user 2's ranking in terms
# of user 1's positions turns this into an inversion count: 0 means identical
# rankings, 45 (= 10*9/2) means one ranking is the exact reverse of the other.
