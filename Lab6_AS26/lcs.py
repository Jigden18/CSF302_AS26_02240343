# Q3: Longest Common Subsequence — DP table, reconstruction, space-optimised
# length, brute-force comparison and a line-by-line diff of two text files
#
# Usage:
#   python lcs.py              -> everything
#   python lcs.py table        -> LCS table for ABCBDAB / BDCABA + reconstruction + two-row version
#   python lcs.py timing       -> DP vs brute force for string lengths 5..18
#   python lcs.py diff         -> diff of old.txt and new.txt
#   python lcs.py diff A B     -> diff of files A and B

import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------------------
# 1. Bottom-up LCS table: c[i][j] = LCS length of X[:i] and Y[:j]
#    b[i][j] records which case was used: "\" diagonal, "^" up, "<" left
# ---------------------------------------------------------------------------
def lcs_table(X, Y):
    m, n = len(X), len(Y)
    c = [[0] * (n + 1) for _ in range(m + 1)]
    b = [[" "] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if X[i - 1] == Y[j - 1]:
                c[i][j] = c[i - 1][j - 1] + 1
                b[i][j] = "\\"
            elif c[i - 1][j] >= c[i][j - 1]:
                c[i][j] = c[i - 1][j]
                b[i][j] = "^"
            else:
                c[i][j] = c[i][j - 1]
                b[i][j] = "<"
    return c, b


# ---------------------------------------------------------------------------
# 2. Reconstruct one LCS by following the arrows back from c[m][n]
# ---------------------------------------------------------------------------
def reconstruct(b, X, i, j):
    result = []
    while i > 0 and j > 0:
        if b[i][j] == "\\":
            result.append(X[i - 1])
            i -= 1
            j -= 1
        elif b[i][j] == "^":
            i -= 1
        else:
            j -= 1
    return result[::-1]


# ---------------------------------------------------------------------------
# 3. Space-optimised length: only two rows of the table, O(min) extra space
# ---------------------------------------------------------------------------
def lcs_length_two_rows(X, Y):
    if len(Y) > len(X):
        X, Y = Y, X                         # keep the rows as short as possible
    prev = [0] * (len(Y) + 1)
    for i in range(1, len(X) + 1):
        curr = [0] * (len(Y) + 1)
        for j in range(1, len(Y) + 1):
            if X[i - 1] == Y[j - 1]:
                curr[j] = prev[j - 1] + 1
            else:
                curr[j] = max(prev[j], curr[j - 1])
        prev = curr
    return prev[len(Y)]


# ---------------------------------------------------------------------------
# 4. Brute force: try every subsequence of X (2^m of them) -> O(2^m * n)
# ---------------------------------------------------------------------------
def is_subsequence(s, Y):
    it = iter(Y)
    return all(ch in it for ch in s)


def lcs_brute_force(X, Y):
    m = len(X)
    best = ""
    for mask in range(1 << m):
        sub = "".join(X[i] for i in range(m) if mask >> i & 1)
        if len(sub) > len(best) and is_subsequence(sub, Y):
            best = sub
    return best


# ---------------------------------------------------------------------------
# Print the table for X = ABCBDAB, Y = BDCABA
# ---------------------------------------------------------------------------
def print_table(X, Y, c, b):
    print("      " + "".join(f"{'':>2}{y:>2}" for y in " " + Y))
    for i in range(len(X) + 1):
        label = X[i - 1] if i > 0 else " "
        row = "".join(f"{b[i][j]:>2}{c[i][j]:>2}" for j in range(len(Y) + 1))
        print(f"  {label:>2}  {row}")


def table_demo():
    X, Y = "ABCBDAB", "BDCABA"
    print(f"=== LCS table for X = {X}, Y = {Y} ===")
    print("(\\ = characters match, take diagonal + 1;  ^ = from above;  < = from the left)\n")
    c, b = lcs_table(X, Y)
    print_table(X, Y, c, b)
    lcs = "".join(reconstruct(b, X, len(X), len(Y)))
    print(f"\nLCS length (full table) : {c[len(X)][len(Y)]}")
    print(f"One LCS (reconstructed) : {lcs}")
    print(f"LCS length (two rows)   : {lcs_length_two_rows(X, Y)}")
    print(f"Brute-force check       : {lcs_brute_force(X, Y)} (length {len(lcs_brute_force(X, Y))})")
    print()


# ---------------------------------------------------------------------------
# DP vs brute force timing
# ---------------------------------------------------------------------------
def timing():
    print("=== Running time: DP vs brute force (random strings over A, B, C, D) ===")
    print(f"{'length':>6} | {'LCS':>3} | {'DP (s)':>10} | {'Brute force (s)':>15} | {'subsequences':>12} | match")
    print("-" * 70)
    rng = random.Random(3)
    for n in range(5, 19):
        X = "".join(rng.choice("ABCD") for _ in range(n))
        Y = "".join(rng.choice("ABCD") for _ in range(n))

        start = time.perf_counter()
        c, b = lcs_table(X, Y)
        dp_len = c[n][n]
        t_dp = time.perf_counter() - start

        start = time.perf_counter()
        bf = lcs_brute_force(X, Y)
        t_bf = time.perf_counter() - start

        print(f"{n:>6} | {dp_len:>3} | {t_dp:>10.6f} | {t_bf:>15.4f} | {2 ** n:>12,} | {len(bf) == dp_len}",
              flush=True)
    print()


# ---------------------------------------------------------------------------
# Line-by-line diff: lines in the LCS are unchanged, the rest removed/added
# ---------------------------------------------------------------------------
def diff(file_a, file_b):
    with open(file_a, encoding="utf-8") as f:
        A = f.read().splitlines()
    with open(file_b, encoding="utf-8") as f:
        B = f.read().splitlines()
    c, _ = lcs_table(A, B)

    # Walk the table from the start so lines come out in file order
    # (build it on reversed lists, so c_rev[i][j] = LCS of A[i:] and B[j:])
    c_rev, _ = lcs_table(A[::-1], B[::-1])
    m, n = len(A), len(B)
    suffix = lambda i, j: c_rev[m - i][n - j]

    print(f"=== Diff: {os.path.basename(file_a)} -> {os.path.basename(file_b)} ===")
    print(f"(LCS = {c[m][n]} unchanged lines;  '-' removed,  '+' added)\n")
    i = j = 0
    removed = added = 0
    while i < m or j < n:
        if i < m and j < n and A[i] == B[j]:
            print(f"   {A[i]}")
            i += 1
            j += 1
        elif i < m and (j == n or suffix(i + 1, j) >= suffix(i, j + 1)):
            print(f" - {A[i]}")
            removed += 1
            i += 1
        else:
            print(f" + {B[j]}")
            added += 1
            j += 1
    print(f"\n{c[m][n]} unchanged, {removed} removed, {added} added")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    if arg in ("table", "all"):
        table_demo()
    if arg in ("timing", "all"):
        timing()
    if arg in ("diff", "all"):
        if len(sys.argv) == 4:
            diff(sys.argv[2], sys.argv[3])
        else:
            diff(os.path.join(HERE, "old.txt"), os.path.join(HERE, "new.txt"))
    if arg not in ("table", "timing", "diff", "all"):
        print("Unknown option. Use: table | timing | diff [file1 file2]")


# Analysis / Conclusion:
# The DP fills an (m+1) x (n+1) table in O(mn) time. For ABCBDAB and BDCABA
# the LCS length is 4, and following the arrows back from the bottom-right
# corner gives BCBA. Only the previous row is ever read, so the length alone
# can be computed with two rows, using O(min(m, n)) space instead of O(mn).
#
# The brute force tries all 2^m subsequences of X and checks each one against
# Y, so its time doubles with every extra character: at length 18 it checks
# 262,144 subsequences and takes about a third of a second, while the DP
# still takes well under a millisecond. Both always give the same LCS length.
#
# Treating each line of a file as one "character", the LCS of two files is
# the largest set of lines that stayed in the same order. Lines in the LCS
# are printed as unchanged, lines only in the old file are removed (-) and
# lines only in the new file are added (+), which is how diff tools work.
