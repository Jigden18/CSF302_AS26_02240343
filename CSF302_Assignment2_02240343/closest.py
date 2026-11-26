"""
closest.py
==========
CSF302 Algorithm Design and Analysis, Assignment 2: Closest Camera Traps
Student : Jigden Shakya (02240343)

Camera traps in Jigme Dorji National Park sit on a map grid. Two traps that
are very close record the same animals, so the field team wants the closest
pair of traps in order to move one of them.

This module gives two solutions to the closest pair problem:

    closest_pair_brute(points)  checks every pair             Theta(n^2)
    closest_pair(points)        divide and conquer            Theta(n log n)

Both functions take a list of n >= 2 points (x, y) and return a tuple
(d, i, j) where d is the smallest distance and i < j are the indices of the
two points in the ORIGINAL list.

Example (from the assignment brief):

    >>> points = [(2, 3), (12, 30), (40, 50), (5, 1), (12, 10), (3, 4)]
    >>> closest_pair(points)
    (1.4142135623730951, 0, 5)

Design notes
------------
* Distances are compared as SQUARED distances (dx*dx + dy*dy). This avoids
  calling sqrt for every pair and gives exactly the same ordering, because
  sqrt is increasing. The square root is taken once, at the very end.
* Both functions use the same squared distance arithmetic, so the timing
  comparison in Part C is fair.
* If several pairs share the smallest distance, both functions return a
  correct pair, but not necessarily the same pair. The tests therefore check
  that the distance matches and that (i, j) really is a pair at that distance.
"""

import math

# Subproblems of this size or smaller are solved by brute force inside the
# recursion. Three is the textbook choice: with 2 or 3 points a split would
# leave a half with a single point, which has no pair at all.
BASE_CASE_SIZE = 3


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _check_input(points):
    """Raise ValueError if there are fewer than two points (no pair exists)."""
    if len(points) < 2:
        raise ValueError("closest pair needs at least 2 points, got %d" % len(points))


def _ordered(d_sq, a, b):
    """Return the result tuple (d_sq, i, j) with the smaller index first."""
    return (d_sq, a, b) if a < b else (d_sq, b, a)


# ---------------------------------------------------------------------------
# Part A (1): brute force, Theta(n^2)
# ---------------------------------------------------------------------------

def closest_pair_brute(points):
    """Return (d, i, j) by comparing every one of the n(n-1)/2 pairs.

    The loop structure is fixed: for every i, j runs over all later points,
    so the number of distance computations is exactly n(n-1)/2 whatever the
    input looks like. That is why the running time is Theta(n^2), not just
    O(n^2).
    """
    _check_input(points)
    n = len(points)

    best_sq = math.inf          # smallest squared distance seen so far
    best_i, best_j = 0, 1       # indices of that pair

    for i in range(n - 1):
        xi, yi = points[i]
        for j in range(i + 1, n):
            dx = xi - points[j][0]
            dy = yi - points[j][1]
            d_sq = dx * dx + dy * dy
            if d_sq < best_sq:      # strict '<' keeps the first pair found on ties
                best_sq = d_sq
                best_i, best_j = i, j

    return (math.sqrt(best_sq), best_i, best_j)


# ---------------------------------------------------------------------------
# Part A (2): divide and conquer, Theta(n log n)
# ---------------------------------------------------------------------------

def closest_pair(points):
    """Return (d, i, j) using divide and conquer.

    Steps
    -----
    1. Tag every point with its original index and sort by x once.
    2. Recursively:
         DIVIDE   split the x-sorted points at the middle index;
         CONQUER  solve the left half and the right half;
         COMBINE  let delta be the better of the two answers, then look only
                  at points within delta of the dividing line (the strip of
                  width 2*delta) for a pair that crosses the line.
    3. Take the square root of the best squared distance.

    To keep the COMBINE step linear, each recursive call also returns its
    points sorted by y. The two y-sorted halves are merged exactly as in merge
    sort, so we never have to re-sort the strip. This is what makes the
    recurrence T(n) = 2T(n/2) + Theta(n) instead of 2T(n/2) + Theta(n log n).
    """
    _check_input(points)

    # Each entry is (x, y, original_index). Sorting tuples sorts by x first,
    # then y, then index, which gives a fixed, repeatable order.
    px = sorted((p[0], p[1], idx) for idx, p in enumerate(points))

    (best_sq, i, j), _ = _closest_recursive(px, 0, len(px))
    return (math.sqrt(best_sq), i, j)


def _brute_small(px, lo, hi):
    """Base case: brute force on px[lo:hi] (at most BASE_CASE_SIZE points).

    Returns (best, by_y) where best = (d_sq, i, j) uses original indices and
    by_y is the same points sorted by y, ready for merging by the caller.
    """
    best = (math.inf, -1, -1)
    for a in range(lo, hi - 1):
        xa, ya, ia = px[a]
        for b in range(a + 1, hi):
            xb, yb, ib = px[b]
            dx = xa - xb
            dy = ya - yb
            d_sq = dx * dx + dy * dy
            if d_sq < best[0]:
                best = _ordered(d_sq, ia, ib)
    by_y = sorted(px[lo:hi], key=lambda p: p[1])
    return best, by_y


def _merge_by_y(left, right):
    """Merge two lists that are already sorted by y into one sorted list.

    This is the merge step of merge sort and costs Theta(len(left) + len(right)).
    """
    merged = []
    a = b = 0
    while a < len(left) and b < len(right):
        if left[a][1] <= right[b][1]:
            merged.append(left[a])
            a += 1
        else:
            merged.append(right[b])
            b += 1
    # One of the two lists is used up, so copy whatever remains of the other.
    merged.extend(left[a:])
    merged.extend(right[b:])
    return merged


def _closest_recursive(px, lo, hi):
    """Solve the closest pair problem for px[lo:hi] (px is sorted by x).

    Index bounds lo and hi are passed instead of slicing, so that the divide
    step costs Theta(1) and no copies of the x-sorted list are made.

    Returns (best, by_y):
        best  = (d_sq, i, j), smallest squared distance and original indices
        by_y  = the points of px[lo:hi] sorted by y
    """
    n = hi - lo

    # ---- Base case -------------------------------------------------------
    if n <= BASE_CASE_SIZE:
        return _brute_small(px, lo, hi)

    # ---- Divide ----------------------------------------------------------
    mid = (lo + hi) // 2
    mid_x = px[mid][0]          # x coordinate of the dividing vertical line

    # ---- Conquer ---------------------------------------------------------
    best_left, left_y = _closest_recursive(px, lo, mid)
    best_right, right_y = _closest_recursive(px, mid, hi)

    # Tuple comparison: smaller distance wins; on a tie the smaller indices win.
    best = min(best_left, best_right)

    # ---- Combine ---------------------------------------------------------
    by_y = _merge_by_y(left_y, right_y)

    best_sq = best[0]
    if best_sq == 0:
        # Two identical points were already found. Nothing can beat a
        # distance of 0, so the strip does not need to be checked.
        return best, by_y

    # The strip holds every point whose horizontal distance to the dividing
    # line is less than delta = sqrt(best_sq). Only such points can be part
    # of a crossing pair that is closer than delta. Because by_y is sorted by
    # y, the strip comes out sorted by y as well.
    strip = [p for p in by_y if (p[0] - mid_x) * (p[0] - mid_x) < best_sq]

    # Compare each strip point with the points just above it. As soon as the
    # vertical gap reaches delta, no later point can be closer, so we break.
    # A packing argument shows this inner loop runs at most 7 times per
    # point, so the whole strip scan is Theta(n).
    for k in range(len(strip)):
        xk, yk, ik = strip[k]
        for m in range(k + 1, len(strip)):
            xm, ym, im = strip[m]
            dy = ym - yk
            if dy * dy >= best_sq:
                break
            dx = xm - xk
            d_sq = dx * dx + dy * dy
            if d_sq < best_sq:
                best_sq = d_sq
                best = _ordered(d_sq, ik, im)

    return best, by_y


# ---------------------------------------------------------------------------
# Small demonstration when the file is run directly: python closest.py
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    demo = [(2, 3), (12, 30), (40, 50), (5, 1), (12, 10), (3, 4)]
    print("Closest Camera Traps: demonstration")
    print("Input points :", demo)

    d1, i1, j1 = closest_pair_brute(demo)
    d2, i2, j2 = closest_pair(demo)

    print("Brute force  : d = %.6f between index %d %s and index %d %s"
          % (d1, i1, demo[i1], j1, demo[j1]))
    print("Divide & conq: d = %.6f between index %d %s and index %d %s"
          % (d2, i2, demo[i2], j2, demo[j2]))
    print("Expected     : (1.414..., 0, 5)")
    print("Both agree   :", (d1, i1, j1) == (d2, i2, j2))
