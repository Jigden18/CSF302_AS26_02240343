"""
test_sorts.py

Correctness tests for sorts.py. Run with either:

    python -m pytest -v test_sorts.py
    python test_sorts.py

sorted() is used only as the reference answer, never inside the sorts.
"""

import random
import sys
import unittest

from sorts import quicksort_basic, quicksort_improved


# A few cutoffs are checked so that both the insertion sort path and the
# partitioning path of quicksort_improved get exercised.
CUTOFFS = [1, 4, 16, 64]


def run_basic(data):
    a = list(data)
    quicksort_basic(a)
    return a


def run_improved(data, cutoff=16):
    a = list(data)
    quicksort_improved(a, cutoff)
    return a


class TestRandomLists(unittest.TestCase):
    """Brute-force check against sorted() on many random lists."""

    NUM_LISTS = 500

    def setUp(self):
        # Fixed seed so a failure can be reproduced exactly.
        self.rng = random.Random(302)

    def _random_list(self):
        n = self.rng.randint(0, 300)
        # Mix of narrow and wide value ranges so some lists have many
        # duplicates and others have almost none.
        spread = self.rng.choice([5, 100, 10_000])
        return [self.rng.randint(-spread, spread) for _ in range(n)]

    def test_basic_matches_sorted(self):
        for trial in range(self.NUM_LISTS):
            data = self._random_list()
            with self.subTest(trial=trial, n=len(data)):
                self.assertEqual(run_basic(data), sorted(data))

    def test_improved_matches_sorted(self):
        for trial in range(self.NUM_LISTS):
            data = self._random_list()
            cutoff = CUTOFFS[trial % len(CUTOFFS)]
            with self.subTest(trial=trial, n=len(data), cutoff=cutoff):
                self.assertEqual(run_improved(data, cutoff), sorted(data))


class TestEdgeCases(unittest.TestCase):
    """The specific inputs listed in Part B, run through both sorts."""

    CASES = {
        "empty": [],
        "one element": [42],
        "two elements reversed": [2, 1],
        "all equal": [7] * 200,
        "already sorted": list(range(200)),
        "reverse sorted": list(range(200, 0, -1)),
        "negative numbers": [-3, -1, -7, 0, 5, -2, -100, 4, -1],
        "all negative": list(range(-1, -150, -1)),
    }

    def test_basic_edge_cases(self):
        for name, data in self.CASES.items():
            with self.subTest(case=name):
                self.assertEqual(run_basic(data), sorted(data))

    def test_improved_edge_cases(self):
        for name, data in self.CASES.items():
            for cutoff in CUTOFFS:
                with self.subTest(case=name, cutoff=cutoff):
                    self.assertEqual(run_improved(data, cutoff), sorted(data))


class TestBehaviour(unittest.TestCase):
    """Properties beyond plain correctness."""

    def test_sorts_in_place_and_returns_none(self):
        a = [3, 1, 2]
        self.assertIsNone(quicksort_basic(a))
        self.assertEqual(a, [1, 2, 3])

        b = [3, 1, 2]
        self.assertIsNone(quicksort_improved(b))
        self.assertEqual(b, [1, 2, 3])

    def test_improved_handles_large_sorted_input(self):
        # 50,000 sorted elements would overflow the default recursion limit
        # with the basic version. The improved version must cope easily.
        data = list(range(50_000))
        self.assertEqual(run_improved(data), data)

    def test_improved_handles_large_input_with_duplicates(self):
        rng = random.Random(1)
        data = [rng.randint(0, 9) for _ in range(20_000)]
        self.assertEqual(run_improved(data), sorted(data))

    def test_improved_recursion_depth_is_logarithmic(self):
        # Allow only ~60 extra stack frames beyond what the test runner is
        # already using. log2(100,000) is about 17, so a correct
        # smaller-side-first implementation fits comfortably, while any
        # O(n) depth would fail immediately.
        data = list(range(100_000))
        old_limit = sys.getrecursionlimit()
        current_depth = len(__import__("inspect").stack())
        sys.setrecursionlimit(current_depth + 60)
        try:
            quicksort_improved(data, cutoff=1)
        finally:
            sys.setrecursionlimit(old_limit)
        self.assertEqual(data, list(range(100_000)))

    def test_basic_fails_on_large_sorted_input(self):
        # Documents the known weakness rather than hiding it: with the
        # default recursion limit, sorted input of this size cannot be
        # handled by the last-element pivot.
        data = list(range(5 * sys.getrecursionlimit()))
        with self.assertRaises(RecursionError):
            quicksort_basic(data)

    def test_invalid_cutoff_rejected(self):
        with self.assertRaises(ValueError):
            quicksort_improved([3, 2, 1], cutoff=0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
