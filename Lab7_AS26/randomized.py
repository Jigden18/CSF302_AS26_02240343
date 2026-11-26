# Q4: Randomized Algorithms — quickselect, Miller-Rabin primality test, Carmichael number 561
#
# Usage:
#   python randomized.py                -> everything
#   python randomized.py quickselect    -> quickselect vs sort-and-index, n = 10^4 .. 10^6
#   python randomized.py primes         -> Miller-Rabin vs trial division on 20 random 12-digit numbers
#   python randomized.py carmichael     -> Miller-Rabin (1 round) on 561, 1,000 times

import math
import random
import sys
import time

rng = random.Random(2024)


# ---------------------------------------------------------------------------
# 1. Randomized quickselect: k-th smallest (k = 0-based), expected O(n)
#    Random pivot, split into < pivot, == pivot, > pivot, keep only one side.
# ---------------------------------------------------------------------------
def quickselect(arr, k):
    if not 0 <= k < len(arr):
        raise IndexError("k out of range")
    while True:
        pivot = arr[rng.randrange(len(arr))]
        lows = [x for x in arr if x < pivot]
        highs = [x for x in arr if x > pivot]
        n_equal = len(arr) - len(lows) - len(highs)
        if k < len(lows):
            arr = lows
        elif k < len(lows) + n_equal:
            return pivot
        else:
            k -= len(lows) + n_equal
            arr = highs


def sort_select(arr, k):
    return sorted(arr)[k]


def quickselect_demo():
    print("=== Randomized quickselect vs sorting and indexing (k = n/2, the median) ===")
    print(f"{'n':>10} | {'Quickselect (s)':>15} | {'Sort + index (s)':>16} | {'Faster':>11} | same answer")
    print("-" * 75)
    data_rng = random.Random(1)
    for n in [10_000, 30_000, 100_000, 300_000, 1_000_000]:
        arr = [data_rng.randint(0, 10**9) for _ in range(n)]
        k = n // 2
        repeats = 5 if n <= 100_000 else 3
        tq = ts = float("inf")
        for _ in range(repeats):
            start = time.perf_counter()
            q = quickselect(arr, k)
            tq = min(tq, time.perf_counter() - start)
            start = time.perf_counter()
            s = sort_select(arr, k)
            ts = min(ts, time.perf_counter() - start)
        faster = "Quickselect" if tq < ts else "Sort"
        print(f"{n:>10,} | {tq:>15.4f} | {ts:>16.4f} | {faster:>11} | {q == s}", flush=True)
    print("\nOther ranks at n = 100,000 (k = 0, 1,000, 99,999):", end=" ")
    arr = [data_rng.randint(0, 10**9) for _ in range(100_000)]
    print(all(quickselect(arr, k) == sorted(arr)[k] for k in (0, 1000, 99_999)))
    print()


# ---------------------------------------------------------------------------
# 2. Miller-Rabin primality test (probabilistic)
#    n - 1 = d * 2^s with d odd. A base a is a witness that n is composite if
#    a^d != 1 and a^(d*2^r) != -1 (mod n) for every r < s.
# ---------------------------------------------------------------------------
def miller_rabin_round(n, a):
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    x = pow(a, d, n)
    if x == 1 or x == n - 1:
        return True                         # "probably prime" for this base
    for _ in range(s - 1):
        x = x * x % n
        if x == n - 1:
            return True
    return False                            # a is a witness: n is composite


def miller_rabin(n, rounds=20, r=rng):
    if n < 2:
        return False
    for p in (2, 3, 5, 7):
        if n % p == 0:
            return n == p
    for _ in range(rounds):
        a = r.randint(2, n - 2)
        if not miller_rabin_round(n, a):
            return False
    return True


# ---------------------------------------------------------------------------
# 3. Trial division up to sqrt(n): deterministic, O(sqrt n)
# ---------------------------------------------------------------------------
def trial_division(n):
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    for i in range(3, math.isqrt(n) + 1, 2):
        if n % i == 0:
            return False
    return True


def primes_demo():
    print("=== Miller-Rabin (20 rounds) vs trial division on 20 random 12-digit numbers ===")
    num_rng = random.Random(12)
    numbers = []
    for i in range(20):
        n = num_rng.randint(10**11, 10**12 - 1)
        if i % 2 == 1:                          # every second number: next prime after a random start,
            while not miller_rabin(n):          # so that both answers ("prime"/"composite") appear
                n += 1
        numbers.append(n)
    print(f"{'#':>2} | {'Number':>13} | {'Miller-Rabin':>12} {'time (s)':>9} | {'Trial division':>14} {'time (s)':>9} | agree")
    print("-" * 82)
    total_mr = total_td = 0.0
    all_agree = True
    for i, n in enumerate(numbers, 1):
        start = time.perf_counter()
        mr = miller_rabin(n)
        t_mr = time.perf_counter() - start
        start = time.perf_counter()
        td = trial_division(n)
        t_td = time.perf_counter() - start
        total_mr += t_mr
        total_td += t_td
        all_agree = all_agree and mr == td
        word = lambda b: "prime" if b else "composite"
        print(f"{i:>2} | {n:>13} | {word(mr):>12} {t_mr:>9.6f} | {word(td):>14} {t_td:>9.6f} | {mr == td}", flush=True)
    print(f"\nTotal time: Miller-Rabin {total_mr:.4f} s, trial division {total_td:.4f} s")
    print(f"Both tests agree on all 20 numbers: {all_agree}")
    print()


# ---------------------------------------------------------------------------
# 4. Carmichael number 561 = 3 * 11 * 17
# ---------------------------------------------------------------------------
def carmichael_demo():
    n, trials = 561, 1000
    print(f"=== Miller-Rabin with 1 round on the Carmichael number {n} = 3 x 11 x 17, {trials:,} runs ===")
    run_rng = random.Random(561)
    says_prime = 0
    fermat_prime = 0
    for _ in range(trials):
        a = run_rng.randint(2, n - 2)
        if miller_rabin_round(n, a):
            says_prime += 1
        if pow(a, n - 1, n) == 1:               # Fermat test with the same base, for comparison
            fermat_prime += 1
    liars = [a for a in range(2, n - 1) if miller_rabin_round(n, a)]
    fermat_liars = sum(1 for a in range(2, n - 1) if pow(a, n - 1, n) == 1)
    print(f"Miller-Rabin answered 'prime'    : {says_prime} / {trials}  ({says_prime / trials * 100:.1f}%)")
    print(f"Fermat test answered 'prime'     : {fermat_prime} / {trials}  ({fermat_prime / trials * 100:.1f}%)")
    print(f"\nBases a in 2..{n - 2} that fool one Miller-Rabin round: {len(liars)} of {n - 3} "
          f"({len(liars) / (n - 3) * 100:.2f}%) -> {liars}")
    print(f"Bases that fool the Fermat test: {fermat_liars} of {n - 3} ({fermat_liars / (n - 3) * 100:.1f}%)")
    print(f"With 20 rounds the chance of answering 'prime' is at most "
          f"({len(liars)}/{n - 3})^20 = {(len(liars) / (n - 3)) ** 20:.1e}")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    if arg in ("quickselect", "all"):
        quickselect_demo()
    if arg in ("primes", "all"):
        primes_demo()
    if arg in ("carmichael", "all"):
        carmichael_demo()
    if arg not in ("quickselect", "primes", "carmichael", "all"):
        print("Unknown option. Use: quickselect | primes | carmichael")


# Analysis / Conclusion:
# Quickselect always returns the same element as sorting and indexing. With a
# random pivot each round keeps on average about half of the list, so the
# expected work is n + n/2 + n/4 + ... = O(n), compared with O(n log n) for
# sorting. In the measurements, though, the two are very close and each wins
# at some sizes: Python's sorted() is written in C, while quickselect builds its
# partitions in Python. The O(n) vs O(n log n) advantage (a factor of about
# log n ~ 20) is cancelled out by that constant-factor difference at these
# sizes. Implemented in the same language, quickselect would be clearly faster.
#
# Miller-Rabin and trial division agree on all 20 numbers. Trial division must
# try up to sqrt(n) ~ 10^6 divisors to prove a 12-digit number prime, while
# Miller-Rabin does 20 rounds of modular exponentiation (about 40 squarings
# each), so on primes it is roughly 50-150 times faster in these runs. On
# composites with a small factor both answer almost instantly.
#
# 561 is a Carmichael number: a^560 = 1 (mod 561) for every a coprime to 561,
# so the Fermat test is fooled by more than half of all bases. Miller-Rabin
# also checks the square roots of 1 along the way, which exposes 561 for all
# but 8 bases, so one round answers "prime" only about 1.4% of the time
# (never more than 1/4 for any composite). Repeating the test with independent
# random bases makes the error probability shrink exponentially.
