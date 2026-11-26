"""
booking.py
CSF302 Assignment 4: Booking the Hall (Part A)

A community hall in Paro receives booking requests. Each request is a tuple
(start, finish, fee). Only one event may use the hall at a time. Two requests
fit together when one finishes no later than the other starts, so an event
ending at 12 and an event starting at 12 are compatible.

Every function returns a pair (total_fee, chosen) where
    total_fee is the sum of the fees of the accepted requests, and
    chosen    is the list of ORIGINAL indices of the accepted requests,
              sorted in ascending order.

Functions
    greedy_earliest_finish(requests)  greedy, accept the earliest finishing request that fits
    greedy_highest_fee(requests)      greedy, accept the most expensive request that fits
    best_schedule(requests)           dynamic programming (weighted interval scheduling)
    brute_force(requests)             tries every subset, only for checking (n <= 15)

Assumptions
    start <= finish for every request and every fee is non negative.
    Times and fees may be integers or floats.
"""

from bisect import bisect_right

# The brute force search grows as 2^n, so it is limited to small inputs.
BRUTE_FORCE_LIMIT = 15


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def validate(requests):
    """Raise ValueError if any request is malformed.

    A request must have finish >= start and a fee that is not negative.
    Checking this once at the start keeps the algorithms themselves simple.
    """
    for i, (start, finish, fee) in enumerate(requests):
        if finish < start:
            raise ValueError(f"request {i} finishes ({finish}) before it starts ({start})")
        if fee < 0:
            raise ValueError(f"request {i} has a negative fee ({fee})")


def fits(a, b):
    """Return True if requests a and b can both use the hall.

    They are compatible when one finishes no later than the other starts.
    Each argument is a (start, finish, fee) tuple.
    """
    return a[1] <= b[0] or b[1] <= a[0]


def is_feasible(requests, chosen):
    """Return True if no two chosen requests overlap.

    Sorting the chosen requests by finish time means we only need to compare
    each request with the one immediately before it.
    """
    ordered = sorted(chosen, key=lambda i: (requests[i][1], requests[i][0]))
    for prev, cur in zip(ordered, ordered[1:]):
        if requests[prev][1] > requests[cur][0]:
            return False
    return True


def total_fee(requests, chosen):
    """Sum of the fees of the chosen requests."""
    return sum(requests[i][2] for i in chosen)


# ---------------------------------------------------------------------------
# Greedy rule 1: earliest finish first (the manager's current rule)
# ---------------------------------------------------------------------------

def greedy_earliest_finish(requests):
    """Sort by finish time and accept each request that fits.

    Because requests are visited in order of finish time, a new request only
    has to start at or after the finish time of the last accepted request.

    Time complexity: O(n log n) for the sort plus O(n) for the scan.
    """
    validate(requests)

    # Visit indices in order of finish time. Ties are broken by start time and
    # then by index so the result is deterministic.
    order = sorted(range(len(requests)),
                   key=lambda i: (requests[i][1], requests[i][0], i))

    chosen = []
    last_finish = float("-inf")  # nothing booked yet, so anything fits
    for i in order:
        start, finish, _fee = requests[i]
        if start >= last_finish:      # fits after the last accepted event
            chosen.append(i)
            last_finish = finish

    chosen.sort()
    return total_fee(requests, chosen), chosen


# ---------------------------------------------------------------------------
# Greedy rule 2: highest fee first
# ---------------------------------------------------------------------------

def greedy_highest_fee(requests):
    """Sort by fee (highest first) and accept each request that fits.

    Requests are no longer visited in time order, so a new request has to be
    compared with every request already accepted.

    Time complexity: O(n log n) for the sort plus O(n * k) for the checks,
    where k is the number accepted so far. In the worst case k grows to n,
    giving O(n^2) overall.
    """
    validate(requests)

    # Highest fee first. Ties go to the earlier finish, then to the lower index.
    order = sorted(range(len(requests)),
                   key=lambda i: (-requests[i][2], requests[i][1], i))

    chosen = []
    for i in order:
        # Accept only if it is compatible with every request already accepted.
        if all(fits(requests[i], requests[j]) for j in chosen):
            chosen.append(i)

    chosen.sort()
    return total_fee(requests, chosen), chosen


# ---------------------------------------------------------------------------
# Dynamic programming: the optimal schedule
# ---------------------------------------------------------------------------

def best_schedule(requests):
    """Weighted interval scheduling by dynamic programming.

    Sort the requests by finish time and number them 1..n in that order.
    p(j) is the largest i < j whose request finishes no later than request j
    starts (0 if there is none). The recurrence is

        OPT(0) = 0
        OPT(j) = max( OPT(j - 1),              # request j is rejected
                      fee_j + OPT(p(j)) )      # request j is accepted

    OPT(n) is the best total. The chosen requests are recovered by walking
    backwards from j = n and repeating the same comparison.

    Time complexity: O(n log n). The sort is O(n log n), each p(j) is found by
    binary search in O(log n), the table is filled in O(n) and the
    reconstruction is O(n).
    """
    validate(requests)
    n = len(requests)

    # order[k] is the original index of the (k + 1)-th request by finish time.
    order = sorted(range(n), key=lambda i: (requests[i][1], requests[i][0], i))
    starts = [requests[i][0] for i in order]
    finishes = [requests[i][1] for i in order]
    fees = [requests[i][2] for i in order]

    # p[j] for j = 1..n (p[0] is unused). bisect_right counts how many of the
    # first j - 1 requests finish at or before the start of request j, which is
    # exactly the 1-based position of the last compatible request.
    p = [0] * (n + 1)
    for j in range(1, n + 1):
        p[j] = bisect_right(finishes, starts[j - 1], 0, j - 1)

    # Fill the table bottom up.
    opt = [0] * (n + 1)
    for j in range(1, n + 1):
        take = fees[j - 1] + opt[p[j]]
        skip = opt[j - 1]
        opt[j] = max(take, skip)

    # Reconstruct the accepted requests by retracing the decisions.
    chosen = []
    j = n
    while j > 0:
        if fees[j - 1] + opt[p[j]] >= opt[j - 1]:   # taking j was (one of) the best
            chosen.append(order[j - 1])
            j = p[j]                                 # jump to last compatible request
        else:
            j -= 1                                   # j was rejected

    chosen.sort()
    return opt[n], chosen


# ---------------------------------------------------------------------------
# Brute force: try every subset (for checking only)
# ---------------------------------------------------------------------------

def brute_force(requests):
    """Try all 2^n subsets and keep the best feasible one.

    This is far too slow for real use but is clearly correct, which makes it
    a reliable reference for testing the other functions.

    Time complexity: O(2^n * n log n), since every subset is sorted and
    checked. Limited to n <= 15.
    """
    validate(requests)
    n = len(requests)
    if n > BRUTE_FORCE_LIMIT:
        raise ValueError(f"brute_force is limited to {BRUTE_FORCE_LIMIT} requests, got {n}")

    best_total, best_chosen = 0, []
    # Each integer mask from 0 to 2^n - 1 represents one subset:
    # bit i is set when request i is in the subset.
    for mask in range(1 << n):
        subset = [i for i in range(n) if mask & (1 << i)]
        if is_feasible(requests, subset):
            value = total_fee(requests, subset)
            if value > best_total:
                best_total, best_chosen = value, subset

    return best_total, best_chosen


# ---------------------------------------------------------------------------
# Demonstration with the example from the assignment brief
# ---------------------------------------------------------------------------

def _show(name, requests, result):
    """Print one result in a readable form."""
    total, chosen = result
    print(f"{name:<24} total = Nu. {total:>6}   chosen = {chosen}")
    for i in chosen:
        s, f, fee = requests[i]
        print(f"{'':<26}request {i}: {s:>2}:00 to {f:>2}:00, fee Nu. {fee}")


if __name__ == "__main__":
    example = [(9, 12, 3000), (10, 16, 8000), (13, 17, 4000),
               (12, 14, 2500), (16, 18, 2000)]

    print("Booking requests (index: start, finish, fee)")
    for idx, req in enumerate(example):
        print(f"  {idx}: {req}")
    print()

    _show("greedy_earliest_finish", example, greedy_earliest_finish(example))
    _show("greedy_highest_fee", example, greedy_highest_fee(example))
    _show("best_schedule (DP)", example, best_schedule(example))
    _show("brute_force", example, brute_force(example))
