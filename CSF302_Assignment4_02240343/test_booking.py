"""
test_booking.py
CSF302 Assignment 4: Booking the Hall (Part B)

Run with either of these commands:
    python test_booking.py           (unittest, verbose output)
    python -m pytest -v -s test_booking.py

Every test checks two things about a schedule:
    1. it is feasible (no two accepted events overlap), and
    2. the reported total really is the sum of the accepted fees.
Optimality is checked against brute_force, which tries every subset.
"""

import random
import unittest

from booking import (
    best_schedule,
    brute_force,
    greedy_earliest_finish,
    greedy_highest_fee,
    is_feasible,
    total_fee,
)

# Fixed seed so that every run tests exactly the same random inputs.
SEED = 302
RANDOM_CASES = 600          # the brief asks for at least 500
ALL_FUNCTIONS = [greedy_earliest_finish, greedy_highest_fee, best_schedule, brute_force]


def random_requests(rng, n, max_time=20, max_len=8, fee_range=(1, 10)):
    """Build n random requests (start, finish, fee) with integer values.

    A short time range and small fees are used on purpose: they produce many
    overlaps, many back to back pairs and many ties, which are the cases most
    likely to expose mistakes.
    """
    requests = []
    for _ in range(n):
        start = rng.randint(0, max_time)
        finish = start + rng.randint(1, max_len)
        fee = rng.randint(*fee_range)
        requests.append((start, finish, fee))
    return requests


class ScheduleChecks(unittest.TestCase):
    """Shared assertions used by all the test classes."""

    def assert_valid(self, requests, result, label=""):
        """The schedule must be feasible and its total must be correct."""
        total, chosen = result
        self.assertTrue(is_feasible(requests, chosen),
                        f"{label}: overlapping events chosen {chosen} for {requests}")
        self.assertEqual(total, total_fee(requests, chosen),
                         f"{label}: total {total} does not match chosen {chosen}")
        self.assertEqual(len(chosen), len(set(chosen)), f"{label}: duplicate index")
        self.assertEqual(chosen, sorted(chosen), f"{label}: indices not sorted")


# ---------------------------------------------------------------------------
# 1. The worked example from the assignment brief
# ---------------------------------------------------------------------------

class TestBriefExample(ScheduleChecks):
    REQUESTS = [(9, 12, 3000), (10, 16, 8000), (13, 17, 4000),
                (12, 14, 2500), (16, 18, 2000)]

    def test_greedy_earliest_finish(self):
        self.assertEqual(greedy_earliest_finish(self.REQUESTS), (7500, [0, 3, 4]))

    def test_best_schedule(self):
        self.assertEqual(best_schedule(self.REQUESTS), (10000, [1, 4]))

    def test_brute_force_agrees(self):
        self.assertEqual(brute_force(self.REQUESTS)[0], 10000)


# ---------------------------------------------------------------------------
# 2. DP against brute force on random inputs
# ---------------------------------------------------------------------------

class TestRandomAgainstBruteForce(ScheduleChecks):

    def test_dp_matches_brute_force(self):
        """best_schedule must equal brute_force on 600 random inputs of 0 to 10 requests."""
        rng = random.Random(SEED)
        sizes_seen = set()
        greedy_ef_optimal = greedy_hf_optimal = 0

        for case in range(RANDOM_CASES):
            n = rng.randint(0, 10)
            sizes_seen.add(n)
            requests = random_requests(rng, n)

            expected_total = brute_force(requests)[0]
            dp = best_schedule(requests)
            self.assert_valid(requests, dp, f"case {case} DP")
            self.assertEqual(dp[0], expected_total,
                             f"case {case}: DP {dp[0]} != brute force {expected_total} for {requests}")

            # The greedy rules must always be valid and never beat the optimum.
            for func in (greedy_earliest_finish, greedy_highest_fee):
                result = func(requests)
                self.assert_valid(requests, result, f"case {case} {func.__name__}")
                self.assertLessEqual(result[0], expected_total)
            greedy_ef_optimal += greedy_earliest_finish(requests)[0] == expected_total
            greedy_hf_optimal += greedy_highest_fee(requests)[0] == expected_total

        self.assertEqual(sizes_seen, set(range(11)), "every size from 0 to 10 should appear")
        print(f"\n    {RANDOM_CASES} random inputs (0 to 10 requests): "
              f"best_schedule matched brute_force in all {RANDOM_CASES}")
        print(f"    greedy_earliest_finish was optimal in {greedy_ef_optimal}/{RANDOM_CASES}")
        print(f"    greedy_highest_fee     was optimal in {greedy_hf_optimal}/{RANDOM_CASES}")


# ---------------------------------------------------------------------------
# 3. Edge cases named in the brief
# ---------------------------------------------------------------------------

class TestEdgeCases(ScheduleChecks):

    def check_all(self, requests, expected_total, expected_dp_chosen=None):
        """Run every function, check validity, and check the optimal total."""
        for func in ALL_FUNCTIONS:
            self.assert_valid(requests, func(requests), func.__name__)
        self.assertEqual(best_schedule(requests)[0], expected_total)
        self.assertEqual(brute_force(requests)[0], expected_total)
        if expected_dp_chosen is not None:
            self.assertEqual(best_schedule(requests)[1], expected_dp_chosen)

    def test_no_requests(self):
        for func in ALL_FUNCTIONS:
            self.assertEqual(func([]), (0, []), func.__name__)

    def test_one_request(self):
        requests = [(9, 17, 5000)]
        for func in ALL_FUNCTIONS:
            self.assertEqual(func(requests), (5000, [0]), func.__name__)

    def test_all_overlapping(self):
        # Every request covers 12:00, so only one can be accepted.
        requests = [(9, 13, 3000), (11, 15, 7000), (10, 14, 4000), (12, 16, 2000)]
        self.check_all(requests, 7000, [1])
        self.assertEqual(greedy_highest_fee(requests), (7000, [1]))
        self.assertEqual(greedy_earliest_finish(requests), (3000, [0]))

    def test_none_overlapping(self):
        # Gaps between all events: every request should be accepted by every function.
        requests = [(15, 16, 1000), (8, 9, 2000), (10, 12, 3000), (13, 14, 4000)]
        for func in ALL_FUNCTIONS:
            self.assertEqual(func(requests), (10000, [0, 1, 2, 3]), func.__name__)

    def test_back_to_back(self):
        # Each event starts exactly when the previous one ends. These must fit.
        requests = [(8, 10, 1000), (10, 12, 2000), (12, 14, 3000), (14, 16, 4000)]
        for func in ALL_FUNCTIONS:
            self.assertEqual(func(requests), (10000, [0, 1, 2, 3]), func.__name__)

    def test_one_hour_overlap_is_not_back_to_back(self):
        # Finishing at 12 and starting at 11 is a real clash.
        requests = [(9, 12, 1000), (11, 14, 1000)]
        self.check_all(requests, 1000)

    def test_identical_requests(self):
        requests = [(10, 12, 500)] * 3
        self.check_all(requests, 500)

    def test_invalid_input_rejected(self):
        for bad in ([(12, 10, 100)], [(9, 10, -5)]):
            for func in ALL_FUNCTIONS:
                with self.assertRaises(ValueError):
                    func(bad)

    def test_brute_force_size_limit(self):
        with self.assertRaises(ValueError):
            brute_force([(i, i + 1, 1) for i in range(16)])


# ---------------------------------------------------------------------------
# 4. Equal fees: earliest finish must be optimal
# ---------------------------------------------------------------------------

class TestEqualFees(ScheduleChecks):

    def test_earliest_finish_optimal_when_fees_equal(self):
        """With equal fees, maximising revenue means maximising the number of events,
        and earliest finish is the classic optimal rule for that."""
        rng = random.Random(SEED + 1)
        cases = 500
        for case in range(cases):
            n = rng.randint(0, 12)
            fee = rng.choice([1, 500, 2500])
            requests = [(s, f, fee) for s, f, _ in random_requests(rng, n)]
            greedy = greedy_earliest_finish(requests)
            self.assert_valid(requests, greedy, f"equal fee case {case}")
            self.assertEqual(greedy[0], brute_force(requests)[0],
                             f"case {case}: greedy not optimal for {requests}")
            self.assertEqual(greedy[0], best_schedule(requests)[0])
        print(f"\n    {cases} equal fee inputs: greedy_earliest_finish was optimal in all {cases}")


# ---------------------------------------------------------------------------
# 5. Counterexamples used in the report (Part C)
# ---------------------------------------------------------------------------

class TestCounterexamples(ScheduleChecks):

    def test_earliest_finish_counterexample(self):
        requests = [(9, 11, 1000), (10, 17, 9000)]
        self.assertEqual(greedy_earliest_finish(requests), (1000, [0]))
        self.assertEqual(best_schedule(requests), (9000, [1]))

    def test_highest_fee_counterexample(self):
        requests = [(9, 17, 5000), (9, 13, 3000), (13, 17, 3000)]
        self.assertEqual(greedy_highest_fee(requests), (5000, [0]))
        self.assertEqual(best_schedule(requests), (6000, [1, 2]))

    def test_both_rules_fail_together(self):
        requests = [(9, 11, 1000), (10, 12, 4000), (12, 14, 4000), (9, 14, 6000)]
        self.assertEqual(greedy_earliest_finish(requests), (5000, [0, 2]))
        self.assertEqual(greedy_highest_fee(requests), (6000, [3]))
        self.assertEqual(best_schedule(requests), (8000, [1, 2]))
        self.assertEqual(brute_force(requests)[0], 8000)


if __name__ == "__main__":
    unittest.main(verbosity=2)
