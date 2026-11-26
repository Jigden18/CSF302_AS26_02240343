"""
analysis.py
CSF302 Assignment 4: Booking the Hall (Part C support script)

Produces the numbers used in the report:
    1. the counterexamples, checked with brute force
    2. greedy to optimal revenue ratios on 1,000 random inputs of 50 requests
    3. running times for growing n, to support the complexity claims
    4. two figures (ratio distribution and running time)

Run with:  python analysis.py
"""

import random
import statistics
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Lock the look of the graphs so they are identical on any computer.
# rcdefaults() ignores any personal matplotlib settings, and DejaVu Sans is
# the font that ships inside matplotlib itself, so every machine has it.
plt.rcdefaults()
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "figure.dpi": 100,
    "savefig.dpi": 200,
})
LINE_COLOURS = {
    "greedy_earliest_finish": "#2a6f97",
    "greedy_highest_fee": "#e07a5f",
    "best_schedule": "#3a7d44",
}

from booking import best_schedule, brute_force, greedy_earliest_finish, greedy_highest_fee

SEED = 2026
TRIALS = 1000
N_REQUESTS = 50
OPEN, CLOSE = 6, 22          # the hall is open from 06:00 to 22:00


# ---------------------------------------------------------------------------
# Random input generators
# ---------------------------------------------------------------------------

def independent_fees(rng, n=N_REQUESTS):
    """Start on the hour between 06:00 and 21:00, last 1 to 6 hours (closing
    at 22:00 at the latest) and pay a fee from Nu. 1,000 to Nu. 10,000 in steps
    of 500 that does not depend on the length of the event."""
    reqs = []
    for _ in range(n):
        start = rng.randint(OPEN, CLOSE - 1)
        finish = min(CLOSE, start + rng.randint(1, 6))
        fee = rng.randrange(1000, 10001, 500)
        reqs.append((start, finish, fee))
    return reqs


def length_based_fees(rng, n=N_REQUESTS):
    """Same times, but the fee is about Nu. 1,500 per hour with +/- 30% noise,
    which is closer to how a hall is usually priced."""
    reqs = []
    for start, finish, _ in independent_fees(rng, n):
        hours = finish - start
        fee = round(1500 * hours * rng.uniform(0.7, 1.3), -1)
        reqs.append((start, finish, fee))
    return reqs


def equal_fees(rng, n=N_REQUESTS):
    """Same times, every event pays Nu. 3,000."""
    return [(s, f, 3000) for s, f, _ in independent_fees(rng, n)]


# ---------------------------------------------------------------------------
# Part C.1 Counterexamples
# ---------------------------------------------------------------------------

def show_counterexamples():
    examples = {
        "Earliest finish fails": [(9, 11, 1000), (10, 17, 9000)],
        "Highest fee fails": [(9, 17, 5000), (9, 13, 3000), (13, 17, 3000)],
        "Both rules fail": [(9, 11, 1000), (10, 12, 4000), (12, 14, 4000), (9, 14, 6000)],
    }
    print("=" * 72)
    print("PART C.1  COUNTEREXAMPLES (optimum confirmed by brute force)")
    print("=" * 72)
    for name, reqs in examples.items():
        print(f"\n{name}: {reqs}")
        for func in (greedy_earliest_finish, greedy_highest_fee, best_schedule, brute_force):
            total, chosen = func(reqs)
            print(f"  {func.__name__:<24} Nu. {total:>6}  chosen {chosen}")


# ---------------------------------------------------------------------------
# Part C.3 Revenue ratios
# ---------------------------------------------------------------------------

def ratio_experiment(generator, label, rng):
    ef_ratios, hf_ratios = [], []
    for _ in range(TRIALS):
        reqs = generator(rng)
        opt = best_schedule(reqs)[0]
        ef_ratios.append(greedy_earliest_finish(reqs)[0] / opt)
        hf_ratios.append(greedy_highest_fee(reqs)[0] / opt)

    rows = []
    for rule, ratios in (("Earliest finish", ef_ratios), ("Highest fee", hf_ratios)):
        rows.append({
            "scenario": label,
            "rule": rule,
            "mean": statistics.mean(ratios),
            "worst": min(ratios),
            "best": max(ratios),
            "optimal_pct": 100 * sum(abs(r - 1) < 1e-12 for r in ratios) / TRIALS,
        })
    return rows, ef_ratios, hf_ratios


def print_ratio_table(rows):
    print("\n" + "=" * 72)
    print(f"PART C.3  GREEDY / OPTIMAL REVENUE, {TRIALS} inputs of {N_REQUESTS} requests")
    print("=" * 72)
    print(f"{'Scenario':<22}{'Rule':<17}{'Average':>9}{'Worst':>9}{'Best':>9}{'% optimal':>11}")
    for r in rows:
        print(f"{r['scenario']:<22}{r['rule']:<17}{r['mean']:>9.4f}{r['worst']:>9.4f}"
              f"{r['best']:>9.4f}{r['optimal_pct']:>10.1f}%")


# ---------------------------------------------------------------------------
# Part C.4 Running times
# ---------------------------------------------------------------------------

def timing_experiment():
    rng = random.Random(SEED + 7)
    sizes = [250, 500, 1000, 2000, 4000, 8000]
    results = {f.__name__: [] for f in (greedy_earliest_finish, greedy_highest_fee, best_schedule)}
    print("\n" + "=" * 72)
    print("PART C.4  RUNNING TIME IN MILLISECONDS (mean of 5 runs)")
    print("=" * 72)
    print(f"{'n':>6}" + "".join(f"{name:>26}" for name in results))
    for n in sizes:
        # Spread events over a long horizon so many are accepted, which is the
        # expensive case for greedy_highest_fee.
        reqs = []
        for _ in range(n):
            s = rng.randint(0, 4 * n)
            reqs.append((s, s + rng.randint(1, 8), rng.randint(1, 100)))
        line = f"{n:>6}"
        for func in (greedy_earliest_finish, greedy_highest_fee, best_schedule):
            t0 = time.perf_counter()
            for _ in range(5):
                func(reqs)
            ms = (time.perf_counter() - t0) / 5 * 1000
            results[func.__name__].append(ms)
            line += f"{ms:>26.2f}"
        print(line)

    # Brute force grows as 2^n, so show it separately on small sizes.
    print(f"\n{'n':>6}{'brute_force (ms)':>20}")
    bf = []
    for n in (8, 10, 12, 14):
        reqs = [(s, s + rng.randint(1, 4), rng.randint(1, 100))
                for s in (rng.randint(0, 20) for _ in range(n))]
        t0 = time.perf_counter()
        brute_force(reqs)
        ms = (time.perf_counter() - t0) * 1000
        bf.append((n, ms))
        print(f"{n:>6}{ms:>20.1f}")
    return sizes, results, bf


# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------

def plot_ratios(ef, hf, path):
    fig, ax = plt.subplots(figsize=(7, 3.6))
    bins = [0.36 + 0.02 * i for i in range(33)]
    ax.hist(ef, bins=bins, alpha=0.75, label="Earliest finish", color="#2a6f97")
    ax.hist(hf, bins=bins, alpha=0.75, label="Highest fee", color="#e07a5f")
    ax.set_xlabel("Greedy revenue / optimal revenue")
    ax.set_ylabel("Number of inputs (of 1,000)")
    ax.legend(frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=200)


def plot_timing(sizes, results, path):
    fig, ax = plt.subplots(figsize=(7, 3.6))
    for name, ms in results.items():
        ax.plot(sizes, ms, marker="o", label=name, color=LINE_COLOURS[name])
    ax.set_xlabel("Number of requests n")
    ax.set_ylabel("Time (ms)")
    ax.legend(frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=200)


if __name__ == "__main__":
    show_counterexamples()

    rng = random.Random(SEED)
    all_rows = []
    rows, ef_ind, hf_ind = ratio_experiment(independent_fees, "Independent fees", rng)
    all_rows += rows
    rows, _, _ = ratio_experiment(length_based_fees, "Fee by length", rng)
    all_rows += rows
    rows, _, _ = ratio_experiment(equal_fees, "Equal fees", rng)
    all_rows += rows
    print_ratio_table(all_rows)

    sizes, results, _ = timing_experiment()
    plot_ratios(ef_ind, hf_ind, "fig_ratio_histogram.png")
    plot_timing(sizes, results, "fig_running_time.png")
    print("\nSaved fig_ratio_histogram.png and fig_running_time.png")
