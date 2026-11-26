# Q1: Activity Selection and Knapsack — greedy rules, counterexamples, fractional and 0/1 knapsack
#
# Usage:
#   python greedy.py                    -> everything
#   python greedy.py select [file]      -> earliest-finish activity selection (default data/activities.txt)
#   python greedy.py counter            -> random search for inputs where the other two rules lose
#   python greedy.py fractional         -> fractional knapsack
#   python greedy.py knapsack01         -> greedy vs DP on 0/1 knapsack

import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------------------
# Activity selection
# ---------------------------------------------------------------------------
def read_activities(path):
    acts = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.split("#")[0].strip()
            if line:
                s, t = line.replace(",", " ").split()
                acts.append((int(s), int(t)))
    return acts


def compatible(a, b):
    # half-open intervals [s, f): touching end-to-start is allowed
    return a[1] <= b[0] or b[1] <= a[0]


def greedy_select(acts, key):
    # Consider activities in the order given by key; keep each one that is
    # compatible with everything selected so far. Returns activity indices.
    order = sorted(range(len(acts)), key=lambda i: key(acts[i]))
    chosen = []
    for i in order:
        if all(compatible(acts[i], acts[j]) for j in chosen):
            chosen.append(i)
    return sorted(chosen, key=lambda i: acts[i])


def earliest_finish(acts):
    # Classic O(n log n) version: sort by finish, keep if start >= last finish
    order = sorted(range(len(acts)), key=lambda i: acts[i][1])
    chosen, last_finish = [], float("-inf")
    for i in order:
        if acts[i][0] >= last_finish:
            chosen.append(i)
            last_finish = acts[i][1]
    return chosen


def earliest_start(acts):
    return greedy_select(acts, key=lambda a: a[0])


def shortest_duration(acts):
    return greedy_select(acts, key=lambda a: a[1] - a[0])


RULES = [("Earliest finish", earliest_finish),
         ("Earliest start", earliest_start),
         ("Shortest duration", shortest_duration)]


def show_selection(acts, chosen):
    return ", ".join(f"a{i + 1}{acts[i]}" for i in chosen)


def select_demo(path):
    acts = read_activities(path)
    print(f"=== Activity selection (earliest finish time) from {os.path.basename(path)} ===")
    print("Activities (start, finish):")
    for i, a in enumerate(acts):
        print(f"  a{i + 1:<3} {a}")
    chosen = earliest_finish(acts)
    print(f"\nSelected {len(chosen)} activities: {show_selection(acts, chosen)}")
    for name, rule in RULES[1:]:
        c = rule(acts)
        print(f"({name} would select {len(c)}: {show_selection(acts, c)})")
    print()


def counterexamples():
    print("=== Random search: inputs where another greedy rule selects fewer activities ===")
    rng = random.Random(7)
    for name, rule in RULES[1:]:
        found, tried = None, 0
        for n in range(2, 10):                      # smallest n first
            for _ in range(5000):
                tried += 1
                acts = []
                for _ in range(n):
                    s = rng.randint(0, 10)
                    acts.append((s, s + rng.randint(1, 8)))
                if len(rule(acts)) < len(earliest_finish(acts)):
                    found = acts
                    break
            if found:
                break
        print(f"\n{name}: counterexample found after {tried:,} random inputs (n = {len(found)})")
        for i, a in enumerate(found):
            print(f"  a{i + 1} {a}")
        ef, other = earliest_finish(found), rule(found)
        print(f"  Earliest finish selects {len(ef)}: {show_selection(found, ef)}")
        print(f"  {name:<15} selects {len(other)}: {show_selection(found, other)}")
    print()


# ---------------------------------------------------------------------------
# Fractional knapsack: highest value/weight ratio first, O(n log n)
# ---------------------------------------------------------------------------
def fractional_knapsack(items, capacity):
    order = sorted(range(len(items)), key=lambda i: items[i][0] / items[i][1], reverse=True)
    total, taken, remaining = 0.0, [], capacity
    for i in order:
        if remaining == 0:
            break
        v, w = items[i]
        amount = min(w, remaining)
        total += v * amount / w
        taken.append((i, amount / w))
        remaining -= amount
    return total, taken


def fractional_demo():
    print("=== Fractional knapsack (highest value/weight ratio first) ===")
    items = [(60, 10), (100, 20), (120, 30), (40, 8), (30, 15)]
    capacity = 50
    print(f"Capacity W = {capacity}")
    print(f"{'Item':>5} | {'Value':>5} | {'Weight':>6} | {'Ratio':>5}")
    print("-" * 31)
    for i, (v, w) in enumerate(items):
        print(f"{i + 1:>5} | {v:>5} | {w:>6} | {v / w:>5.2f}")
    total, taken = fractional_knapsack(items, capacity)
    print("\nTaken (in ratio order):")
    for i, frac in taken:
        v, w = items[i]
        print(f"  item {i + 1}: {frac * 100:6.2f}% of it -> weight {frac * w:5.1f}, value {frac * v:6.1f}")
    print(f"Maximum total value = {total:.2f}")
    print()


# ---------------------------------------------------------------------------
# 0/1 knapsack: same greedy rule (whole items only) vs DP, O(nW)
# ---------------------------------------------------------------------------
def greedy_01(items, capacity):
    order = sorted(range(len(items)), key=lambda i: items[i][0] / items[i][1], reverse=True)
    total, chosen, remaining = 0, [], capacity
    for i in order:
        v, w = items[i]
        if w <= remaining:
            chosen.append(i)
            total += v
            remaining -= w
    return total, sorted(chosen)


def dp_01(items, capacity):
    n = len(items)
    K = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        v, w = items[i - 1]
        for c in range(capacity + 1):
            K[i][c] = K[i - 1][c]
            if w <= c and K[i - 1][c - w] + v > K[i][c]:
                K[i][c] = K[i - 1][c - w] + v
    chosen, c = [], capacity
    for i in range(n, 0, -1):
        if K[i][c] != K[i - 1][c]:
            chosen.append(i - 1)
            c -= items[i - 1][1]
    return K[n][capacity], sorted(chosen)


def knapsack01_demo():
    trials = 5000
    print(f"=== 0/1 knapsack: greedy by ratio vs DP ({trials:,} random inputs) ===")
    rng = random.Random(11)
    worst, worst_case = 1.0, None
    optimal_count, ratio_sum = 0, 0.0
    for _ in range(trials):
        n = rng.randint(2, 10)
        items = [(rng.randint(1, 60), rng.randint(1, 30)) for _ in range(n)]
        capacity = rng.randint(5, 60)
        g, _ = greedy_01(items, capacity)
        d, _ = dp_01(items, capacity)
        ratio = g / d if d else 1.0
        ratio_sum += ratio
        optimal_count += ratio == 1.0
        if ratio < worst:
            worst, worst_case = ratio, (items, capacity)
    print(f"Greedy was optimal in {optimal_count:,} of {trials:,} inputs ({optimal_count / trials * 100:.1f}%)")
    print(f"Average greedy/optimal ratio: {ratio_sum / trials:.4f}")
    print(f"Worst greedy/optimal ratio found: {worst:.4f}")

    items, capacity = worst_case
    g, gc = greedy_01(items, capacity)
    d, dc = dp_01(items, capacity)
    print(f"\nWorst input (W = {capacity}):")
    print(f"{'Item':>5} | {'Value':>5} | {'Weight':>6} | {'Ratio':>5}")
    print("-" * 31)
    for i, (v, w) in enumerate(items):
        print(f"{i + 1:>5} | {v:>5} | {w:>6} | {v / w:>5.2f}")
    print(f"Greedy picks items {[i + 1 for i in gc]} -> value {g}")
    print(f"DP picks items     {[i + 1 for i in dc]} -> value {d}")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    if arg in ("select", "all"):
        path = sys.argv[2] if arg == "select" and len(sys.argv) > 2 else os.path.join(HERE, "data", "activities.txt")
        select_demo(path)
    if arg in ("counter", "all"):
        counterexamples()
    if arg in ("fractional", "all"):
        fractional_demo()
    if arg in ("knapsack01", "all"):
        knapsack01_demo()
    if arg not in ("select", "counter", "fractional", "knapsack01", "all"):
        print("Unknown option. Use: select [file] | counter | fractional | knapsack01")


# Analysis / Conclusion:
# Earliest finish time is optimal: the activity that finishes first leaves the
# most room for the rest, and any optimal schedule can swap its first activity
# for it without losing anything. The other two rules have no such guarantee.
# Earliest start fails when one long activity starts first and blocks several
# short ones. Shortest duration fails when a short activity overlaps the end of
# one activity and the start of another, so choosing it blocks two.
#
# Fractional knapsack is solved exactly by taking items in decreasing
# value/weight order, because any leftover capacity can be filled with a
# fraction of the next best item.
#
# For 0/1 knapsack the same rule is not optimal: items cannot be split, so
# taking a high-ratio item can leave unusable capacity that a lower-ratio but
# heavier item would have filled. Greedy is usually close to optimal on random
# inputs, but the worst case found is well below 1, and in general the ratio can
# be made arbitrarily small (e.g. a tiny item with a slightly better ratio
# blocks one item that fills the whole knapsack). The DP solves it exactly in
# O(nW).
