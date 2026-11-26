# Part A: Efficient Modular Exponentiation — naive vs binary (square-and-multiply)
#
# Usage:
#   python mod_exp.py              -> everything
#   python mod_exp.py outputs      -> output comparison + input validation
#   python mod_exp.py timing       -> timing table (also saves public/partA_timing_chart.png)

import os
import sys
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PUBLIC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")


# ---------------------------------------------------------------------------
# Input validation (shared by every version)
# ---------------------------------------------------------------------------
def validate(a, b, m):
    if m < 1:
        raise ValueError(f"Invalid modulus m={m}: modulus must be >= 1")
    if b < 0:
        raise ValueError(f"Negative exponent b={b} is not supported")
    # Negative base: reduce into the range [0, m) first
    return a % m


# ---------------------------------------------------------------------------
# 1. Naive Modular Exponentiation: O(b) multiplications
# ---------------------------------------------------------------------------
def naive_mod_exp(a, b, m):
    a = validate(a, b, m)
    result = 1 % m          # zero exponent -> 1 mod m (0 when m == 1)
    for _ in range(b):
        result = (result * a) % m
    return result


# ---------------------------------------------------------------------------
# 2. Binary Exponentiation (square-and-multiply, arithmetic version): O(log b)
# ---------------------------------------------------------------------------
def binary_mod_exp(a, b, m):
    a = validate(a, b, m)
    result = 1 % m
    while b > 0:
        if b % 2 == 1:              # odd exponent -> multiply result by base
            result = (result * a) % m
        a = (a * a) % m             # square the base
        b = b // 2                  # halve the exponent
    return result


# ---------------------------------------------------------------------------
# 3. Binary Exponentiation using bitwise operations
# ---------------------------------------------------------------------------
def binary_mod_exp_bitwise(a, b, m):
    a = validate(a, b, m)
    result = 1 % m
    while b:
        if b & 1:                   # lowest bit set -> exponent is odd
            result = (result * a) % m
        a = (a * a) % m
        b >>= 1                     # shift right -> halve the exponent
    return result


# ---------------------------------------------------------------------------
# Comparison of outputs
# ---------------------------------------------------------------------------
def compare_outputs():
    print("=== Output comparison: naive vs binary vs bitwise ===")
    cases = [
        (2, 10, 1000),
        (3, 200, 13),
        (7, 0, 5),          # zero exponent
        (-5, 3, 7),         # negative base
        (10, 5, 1),         # m = 1 -> everything is 0
        (123456789, 1000, 1000000007),
        (2, 12345, 998244353),
        (17, 9999, 97),
    ]
    print(f"{'a':>10} {'b':>6} {'m':>11} | {'naive':>10} {'binary':>10} {'bitwise':>10} {'pow()':>10} | match")
    print("-" * 90)
    for a, b, m in cases:
        n = naive_mod_exp(a, b, m)
        bi = binary_mod_exp(a, b, m)
        bw = binary_mod_exp_bitwise(a, b, m)
        ref = pow(a, b, m)
        ok = n == bi == bw == ref
        print(f"{a:>10} {b:>6} {m:>11} | {n:>10} {bi:>10} {bw:>10} {ref:>10} | {ok}")


def test_validation():
    print("\n=== Input validation ===")
    print("7^0 mod 5       =", binary_mod_exp_bitwise(7, 0, 5))
    print("(-5)^3 mod 7    =", binary_mod_exp_bitwise(-5, 3, 7), "(expected", (-125) % 7, ")")
    for a, b, m, label in [(2, -3, 5, "negative exponent"),
                           (2, 3, 0, "modulus 0"),
                           (2, 3, -4, "negative modulus")]:
        try:
            binary_mod_exp_bitwise(a, b, m)
            print(f"{label:<18}: no error raised (unexpected)")
        except ValueError as e:
            print(f"{label:<18}: ValueError -> {e}")


# ---------------------------------------------------------------------------
# Timing benchmark
# ---------------------------------------------------------------------------
def time_it(func, a, b, m, repeats):
    start = time.perf_counter()
    for _ in range(repeats):
        func(a, b, m)
    return (time.perf_counter() - start) / repeats


def benchmark():
    print("\n=== Execution time: naive vs binary (a=123456789, m=10^9+7) ===")
    a, m = 123456789, 10**9 + 7
    print(f"{'b':>10} | {'Naive (s)':>12} | {'Binary (s)':>12} | {'Bitwise (s)':>12} | {'Speedup':>10}")
    print("-" * 70)
    rows = []
    for k in range(1, 7):
        b = 10 ** k
        naive_repeats = max(1, 10000 // b)
        t_naive = time_it(naive_mod_exp, a, b, m, naive_repeats)
        t_bin = time_it(binary_mod_exp, a, b, m, 1000)
        t_bit = time_it(binary_mod_exp_bitwise, a, b, m, 1000)
        print(f"{b:>10} | {t_naive:>12.6f} | {t_bin:>12.8f} | {t_bit:>12.8f} | {t_naive / t_bit:>9.1f}x",
              flush=True)
        rows.append((b, t_naive, t_bin, t_bit))
    plot_timing(rows)


def plot_timing(rows):
    os.makedirs(PUBLIC, exist_ok=True)
    bs = [r[0] for r in rows]
    plt.figure(figsize=(7, 4.5))
    plt.loglog(bs, [r[1] for r in rows], "o-", label="Naive  O(b)")
    plt.loglog(bs, [r[2] for r in rows], "s-", label="Binary  O(log b)")
    plt.loglog(bs, [r[3] for r in rows], "^-", label="Binary (bitwise)")
    plt.xlabel("Exponent b"); plt.ylabel("Time (s)")
    plt.title("Modular exponentiation: naive vs binary")
    plt.grid(True, which="both", alpha=0.3); plt.legend(); plt.tight_layout()
    plt.savefig(os.path.join(PUBLIC, "partA_timing_chart.png"), dpi=120); plt.close()
    print("Plot saved to public/partA_timing_chart.png")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    if arg in ("outputs", "all"):
        compare_outputs()
        test_validation()
    if arg in ("timing", "all"):
        benchmark()
    if arg not in ("outputs", "timing", "all"):
        print("Unknown option. Use: outputs | timing")


# Analysis / Conclusion:
# All three versions return identical results (also matching Python's built-in
# pow(a, b, m)). The naive method performs b multiplications, so its running
# time grows linearly: each 10x increase in b makes it about 10x slower.
# Square-and-multiply performs about log2(b) squarings and at most log2(b)
# extra multiplications, so going from b = 10 to b = 10^6 only raises the loop
# count from 4 to 20 iterations and the time barely changes. Using b & 1 and
# b >>= 1 instead of % 2 and // 2 gives the same result with slightly cheaper
# operations. Reducing every intermediate product modulo m keeps the numbers
# small, so each multiplication stays constant-time.
