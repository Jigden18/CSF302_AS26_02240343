"""
test_closest.py
===============
CSF302 Assignment 2, Part B: tests for closest.py
Student : Jigden Shakya (02240343)

Run with either of:
    python -m unittest -v test_closest.py
    python -m pytest -v test_closest.py

The brute force version is simple enough to trust by reading it, so it is
used as the reference answer. The divide and conquer version must agree with
it on every input.

What "agree" means
------------------
* The distance d must be the same.
* (i, j) must satisfy i < j and points i and j must really be d apart.
* When exactly one pair has the smallest distance, the indices must match
  brute force exactly. When several pairs tie (common with integer grids
  and duplicates), either answer is correct, so only the checks above apply.
"""

import math
import random
import unittest

from closest import closest_pair, closest_pair_brute


def dist(p, q):
    """Plain Euclidean distance, written independently of closest.py."""
    return math.hypot(p[0] - q[0], p[1] - q[1])


def count_min_pairs(points, d):
    """Count how many pairs lie at distance d (used to detect ties)."""
    n = len(points)
    return sum(
        1
        for i in range(n)
        for j in range(i + 1, n)
        if math.isclose(dist(points[i], points[j]), d, rel_tol=1e-12, abs_tol=1e-12)
    )


class ClosestPairTestCase(unittest.TestCase):
    """Shared assertion used by every test below."""

    def assert_valid_answer(self, points, result, expected_d):
        d, i, j = result
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)
        self.assertTrue(0 <= i < j < len(points), "need 0 <= i < j < n, got %r" % ((i, j),))
        self.assertTrue(math.isclose(d, expected_d, rel_tol=1e-12, abs_tol=1e-12),
                        "distance %r, expected %r" % (d, expected_d))
        # The returned indices must really be a pair at the returned distance.
        self.assertTrue(math.isclose(dist(points[i], points[j]), d, rel_tol=1e-12, abs_tol=1e-12),
                        "points %d and %d are not %r apart" % (i, j, d))


# ---------------------------------------------------------------------------
# 1. Random cross-check against brute force (assignment asks for >= 500)
# ---------------------------------------------------------------------------

class TestRandomAgainstBruteForce(ClosestPairTestCase):

    TRIALS = 600            # more than the required 500
    SEED = 302              # fixed seed so a failure can be reproduced

    def test_random_inputs_match_brute_force(self):
        rng = random.Random(self.SEED)
        unique_cases = tied_cases = 0

        for trial in range(self.TRIALS):
            n = rng.randint(2, 50)

            # Mix three kinds of input so ties and duplicates also appear:
            #   float coordinates   (almost always a unique answer)
            #   small integer grid  (many ties and some duplicate points)
            #   negative and positive integers over a wider range
            kind = trial % 3
            if kind == 0:
                pts = [(rng.uniform(0, 1000), rng.uniform(0, 1000)) for _ in range(n)]
            elif kind == 1:
                pts = [(rng.randint(0, 10), rng.randint(0, 10)) for _ in range(n)]
            else:
                pts = [(rng.randint(-500, 500), rng.randint(-500, 500)) for _ in range(n)]

            expected = closest_pair_brute(pts)
            got = closest_pair(pts)

            with self.subTest(trial=trial, n=n, points=pts):
                self.assert_valid_answer(pts, got, expected[0])
                if count_min_pairs(pts, expected[0]) == 1:
                    unique_cases += 1
                    self.assertEqual(got[1:], expected[1:])
                else:
                    tied_cases += 1

        print("\n    %d random inputs checked (%d with a unique closest pair, %d with ties)"
              % (self.TRIALS, unique_cases, tied_cases))

    def test_larger_random_inputs(self):
        """A few bigger inputs, so the recursion goes several levels deep."""
        rng = random.Random(2026)
        for n in (100, 257, 1000, 2000):
            pts = [(rng.uniform(-1e4, 1e4), rng.uniform(-1e4, 1e4)) for _ in range(n)]
            with self.subTest(n=n):
                self.assertEqual(closest_pair(pts), closest_pair_brute(pts))


# ---------------------------------------------------------------------------
# 2. Edge cases named in the assignment
# ---------------------------------------------------------------------------

class TestRequiredEdgeCases(ClosestPairTestCase):

    def test_example_from_brief(self):
        pts = [(2, 3), (12, 30), (40, 50), (5, 1), (12, 10), (3, 4)]
        d, i, j = closest_pair(pts)
        self.assertAlmostEqual(d, math.sqrt(2))
        self.assertEqual((i, j), (0, 5))
        self.assertEqual(closest_pair(pts), closest_pair_brute(pts))

    def test_exactly_two_points(self):
        pts = [(7, 1), (4, 5)]                      # a 3-4-5 triangle
        self.assertEqual(closest_pair(pts), (5.0, 0, 1))
        self.assertEqual(closest_pair_brute(pts), (5.0, 0, 1))

    def test_two_identical_points(self):
        self.assertEqual(closest_pair([(3, 3), (3, 3)]), (0.0, 0, 1))

    def test_duplicate_points_give_zero(self):
        pts = [(10, 10), (0, 0), (25, 4), (8, 30), (0, 0), (40, 2)]
        d, i, j = closest_pair(pts)
        self.assertEqual(d, 0.0)
        self.assertEqual((i, j), (1, 4))

    def test_duplicates_split_across_the_dividing_line(self):
        """Copies of one point land on both sides of the middle index."""
        pts = [(-9, 0), (-5, 3), (0, 0), (0, 0), (6, -2), (11, 8)]
        d, i, j = closest_pair(pts)
        self.assertEqual(d, 0.0)
        self.assertEqual(pts[i], pts[j])

    def test_many_duplicates(self):
        rng = random.Random(1)
        pts = [(5, 5)] * 40 + [(rng.randint(0, 99), rng.randint(0, 99)) for _ in range(40)]
        rng.shuffle(pts)
        self.assertEqual(closest_pair(pts)[0], 0.0)

    def test_all_points_on_one_vertical_line(self):
        """Every x is equal, so every point is inside every strip."""
        ys = [0, 9, 17, 4, 30, 21, 13, 42, 26, 37]
        pts = [(5, y) for y in ys]
        d, i, j = closest_pair(pts)
        self.assertEqual(d, 4.0)                    # gap between y=0 and y=4 (also 9/13, 17/21, 26/30)
        self.assert_valid_answer(pts, (d, i, j), closest_pair_brute(pts)[0])

    def test_vertical_line_with_unique_answer(self):
        pts = [(2, y) for y in (0, 10, 20, 30, 31, 45, 60, 80)]
        self.assertEqual(closest_pair(pts), (1.0, 3, 4))

    def test_closest_pair_crosses_dividing_line(self):
        """Left half and right half each have only far-apart points; the
        only close pair is (49, 0) on the left and (51, 1) on the right.
        After sorting by x the split falls between index 3 and 4, so only
        the strip check can find this pair."""
        left = [(0, 0), (10, 20), (25, 5), (49, 0)]
        right = [(51, 1), (75, 30), (90, 2), (100, 25)]
        pts = left + right
        d, i, j = closest_pair(pts)
        self.assertAlmostEqual(d, math.sqrt(5))
        self.assertEqual((i, j), (3, 4))
        # Sanity check: the best pair inside each half is much further apart.
        self.assertGreater(closest_pair(left)[0], 10)
        self.assertGreater(closest_pair(right)[0], 10)

    def test_crossing_pair_shuffled(self):
        """Same idea, but the input order is shuffled so indices change."""
        rng = random.Random(7)
        pts = [(0, 0), (10, 20), (25, 5), (49, 0), (51, 1), (75, 30), (90, 2), (100, 25)]
        rng.shuffle(pts)
        d, i, j = closest_pair(pts)
        self.assertAlmostEqual(d, math.sqrt(5))
        self.assertEqual({pts[i], pts[j]}, {(49, 0), (51, 1)})


# ---------------------------------------------------------------------------
# 3. Extra cases
# ---------------------------------------------------------------------------

class TestExtraCases(ClosestPairTestCase):

    def test_fewer_than_two_points_raises(self):
        for bad in ([], [(1, 1)]):
            with self.subTest(points=bad):
                with self.assertRaises(ValueError):
                    closest_pair(bad)
                with self.assertRaises(ValueError):
                    closest_pair_brute(bad)

    def test_three_points_base_case(self):
        pts = [(0, 0), (10, 0), (11, 0)]
        self.assertEqual(closest_pair(pts), (1.0, 1, 2))

    def test_all_points_on_one_horizontal_line(self):
        pts = [(x, 3) for x in (50, 2, 33, 7, 19, 41, 26)]
        self.assertEqual(closest_pair(pts), closest_pair_brute(pts))

    def test_negative_and_float_coordinates(self):
        pts = [(-1.5, -2.25), (3.0, 4.0), (-1.0, -2.0), (100.0, -50.0)]
        d, i, j = closest_pair(pts)
        self.assertAlmostEqual(d, math.hypot(0.5, 0.25))
        self.assertEqual((i, j), (0, 2))

    def test_input_list_is_not_modified(self):
        pts = [(5, 1), (2, 3), (9, 9), (1, 1)]
        copy = list(pts)
        closest_pair(pts)
        closest_pair_brute(pts)
        self.assertEqual(pts, copy)

    def test_points_given_as_lists(self):
        pts = [[2, 3], [12, 30], [3, 4]]
        self.assertEqual(closest_pair(pts)[1:], (0, 2))

    def test_square_grid_all_ties(self):
        """A 6 x 6 grid: every neighbour is exactly 1 apart."""
        pts = [(x, y) for x in range(6) for y in range(6)]
        self.assert_valid_answer(pts, closest_pair(pts), 1.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
