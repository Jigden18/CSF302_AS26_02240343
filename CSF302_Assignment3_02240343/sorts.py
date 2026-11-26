"""
sorts.py

Two in-place quicksort implementations for lists of integers.

quicksort_basic     Lomuto partition, last element as pivot, plain recursion.
quicksort_improved  Random pivot, three-way partition, insertion sort for
                    small ranges, and recursion only on the smaller side so
                    the call stack stays O(log n) deep.

Both functions modify the list they are given and return None, in the same
way that list.sort() does.
"""

import random


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _lomuto_partition(a, lo, hi):
    """
    Partition a[lo..hi] around the pivot stored at a[hi].

    After the loop, every element in a[lo..i] is <= pivot and every element
    in a[i+1..hi-1] is > pivot. The pivot is then swapped into position i+1,
    which is its final sorted position, and that index is returned.

    Note that elements equal to the pivot all go to the left side. When the
    whole range is equal, the split is therefore n-1 versus 0, which is the
    reason the basic version degrades on inputs with many duplicates.
    """
    pivot = a[hi]
    i = lo - 1
    for j in range(lo, hi):
        if a[j] <= pivot:
            i += 1
            a[i], a[j] = a[j], a[i]
    a[i + 1], a[hi] = a[hi], a[i + 1]
    return i + 1


def _three_way_partition(a, lo, hi):
    """
    Partition a[lo..hi] around the pivot stored at a[hi] into three bands:

        a[lo..lt-1]  < pivot
        a[lt..gt]   == pivot
        a[gt+1..hi]  > pivot

    and return (lt, gt). This is Dijkstra's "Dutch national flag" scheme.

    The equal band is already in its final place, so it is excluded from
    both recursive calls. With many repeated keys (for example only the
    values 0 to 9) this is what keeps the sort at O(n log n); a two-way
    Lomuto split would keep re-partitioning the same equal values.
    """
    pivot = a[hi]
    lt = lo        # next free slot for a value < pivot
    i = lo         # current element being examined
    gt = hi        # a[gt+1..hi] already holds values > pivot
    while i <= gt:
        if a[i] < pivot:
            a[lt], a[i] = a[i], a[lt]
            lt += 1
            i += 1
        elif a[i] > pivot:
            # The value swapped in from gt has not been examined yet,
            # so i is deliberately not advanced here.
            a[i], a[gt] = a[gt], a[i]
            gt -= 1
        else:
            i += 1
    return lt, gt


def _insertion_sort(a, lo, hi):
    """
    Sort a[lo..hi] (inclusive) in place with insertion sort.

    Each element is lifted out and the larger elements to its left are
    shifted one place right until the gap is where it belongs. On short
    ranges this has very little overhead compared with further partitioning.
    """
    for k in range(lo + 1, hi + 1):
        key = a[k]
        j = k - 1
        while j >= lo and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key


# ---------------------------------------------------------------------------
# Part A (1): textbook quicksort
# ---------------------------------------------------------------------------

def quicksort_basic(a):
    """
    Sort list a in place using textbook quicksort.

    The pivot is always the last element. On already sorted input that pivot
    is the maximum, so each call peels off only one element and the recursion
    goes n levels deep. For large n this raises RecursionError, which is left
    to propagate so the caller can record it.
    """
    _quicksort_basic(a, 0, len(a) - 1)


def _quicksort_basic(a, lo, hi):
    if lo < hi:
        p = _lomuto_partition(a, lo, hi)
        _quicksort_basic(a, lo, p - 1)
        _quicksort_basic(a, p + 1, hi)


# ---------------------------------------------------------------------------
# Part A (2): improved quicksort
# ---------------------------------------------------------------------------

def quicksort_improved(a, cutoff=16):
    """
    Sort list a in place using an improved quicksort.

    Changes compared with quicksort_basic:

    1. Random pivot. A random index is swapped into a[hi] before
       partitioning, so no fixed input order (sorted, reversed, and so on)
       can force the worst case. The expected running time is O(n log n)
       for every input of distinct keys.

    2. Insertion sort cutoff. Ranges with at most `cutoff` elements are
       finished with insertion sort, which avoids many tiny recursive calls.

    3. Smaller side first. After partitioning, the function recurses into
       the smaller part and then continues the while loop on the larger part.
       Each recursive call therefore handles at most half of the current
       range, so the depth of the call stack is at most about log2(n).

    4. Three-way partition. Keys equal to the pivot are gathered in the
       middle and never touched again. A random pivot on its own does not
       help when the data has only a handful of distinct values, because
       every pivot choice is then one of those repeated values.
    """
    if cutoff < 1:
        raise ValueError("cutoff must be at least 1")
    _quicksort_improved(a, 0, len(a) - 1, cutoff)


def _quicksort_improved(a, lo, hi, cutoff):
    while hi - lo + 1 > cutoff:
        r = random.randint(lo, hi)
        a[r], a[hi] = a[hi], a[r]
        lt, gt = _three_way_partition(a, lo, hi)

        # Left part is a[lo..lt-1], right part is a[gt+1..hi].
        if lt - lo < hi - gt:
            _quicksort_improved(a, lo, lt - 1, cutoff)
            lo = gt + 1
        else:
            _quicksort_improved(a, gt + 1, hi, cutoff)
            hi = lt - 1

    # Whatever is left (size <= cutoff) is small enough for insertion sort.
    if lo < hi:
        _insertion_sort(a, lo, hi)


if __name__ == "__main__":
    demo = [5, 3, 8, 1, 9, 2, 7, 3, 3, -4]
    x = demo[:]
    quicksort_basic(x)
    y = demo[:]
    quicksort_improved(y, cutoff=4)
    print("input              :", demo)
    print("quicksort_basic    :", x)
    print("quicksort_improved :", y)
    print("matches sorted()   :", x == sorted(demo) and y == sorted(demo))
