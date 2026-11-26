"""
benchmark.py

Timing experiments for sorts.py:

  1. Both quicksorts on random, already sorted and many-duplicates (0..9)
     input for n = 1,000 to 64,000, with crashes recorded.
  2. quicksort_basic on sorted input with the recursion limit raised, to
     show the quadratic growth that the crash otherwise hides.
  3. quicksort_improved on 100,000 random values for several cutoffs.
  4. Best version against Python's built-in sorted().

Results are printed as tables and saved to results.json; graphs are saved
as PNG files in the same folder.

    python benchmark.py              run every experiment, then draw graphs
    python benchmark.py --plot-only  redraw graphs from an existing results.json
"""

import json
import platform
import random
import statistics
import sys
import threading
import time

from sorts import quicksort_basic, quicksort_improved

SIZES = [1_000 * 2 ** k for k in range(7)]          # 1,000 .. 64,000
REPEATS = 3                                          # median of 3 runs
SEED = 2026


def make_input(kind, n, rng):
    if kind == "random":
        return [rng.randint(0, 1_000_000) for _ in range(n)]
    if kind == "sorted":
        return list(range(n))
    if kind == "duplicates":
        return [rng.randint(0, 9) for _ in range(n)]
    raise ValueError(kind)


def time_once(sort_fn, data):
    """Time one call on a fresh copy; return seconds or the error name."""
    a = list(data)
    start = time.perf_counter()
    try:
        sort_fn(a)
    except RecursionError:
        return "RecursionError"
    elapsed = time.perf_counter() - start
    assert a == sorted(data), "sort produced a wrong answer"
    return elapsed


def time_median(sort_fn, data, repeats=REPEATS):
    results = []
    for _ in range(repeats):
        r = time_once(sort_fn, data)
        if isinstance(r, str):
            return r          # a crash is a crash, no point repeating
        results.append(r)
    return statistics.median(results)


def fmt(v):
    return v if isinstance(v, str) else f"{v * 1000:.2f}"


# ---------------------------------------------------------------------------
# Experiment 1: three input types
# ---------------------------------------------------------------------------

def experiment_input_types():
    rng = random.Random(SEED)
    sorts = {
        "basic": quicksort_basic,
        "improved": lambda a: quicksort_improved(a, 16),
        "sorted()": None,
    }
    table = {}
    for kind in ["random", "sorted", "duplicates"]:
        table[kind] = {}
        print(f"\n=== Input: {kind}  (time in ms, median of {REPEATS}) ===")
        print(f"{'n':>8} | {'basic':>15} | {'improved':>10} | {'sorted()':>10}")
        for n in SIZES:
            data = make_input(kind, n, rng)
            row = {}
            for name, fn in sorts.items():
                if fn is None:
                    fn = lambda a: a.sort()
                row[name] = time_median(fn, data)
            table[kind][n] = row
            print(f"{n:>8} | {fmt(row['basic']):>15} | "
                  f"{fmt(row['improved']):>10} | {fmt(row['sorted()']):>10}")
    return table


# ---------------------------------------------------------------------------
# Experiment 2: basic quicksort on sorted data with a deep stack
# ---------------------------------------------------------------------------

def experiment_basic_deep_stack():
    """
    Raise the recursion limit and run in a thread with a large stack so the
    basic version can finish on sorted input. This exposes the Theta(n^2)
    running time predicted by T(n) = T(n-1) + Theta(n).
    """
    sizes = [1_000, 2_000, 4_000, 8_000, 16_000]
    out = {}

    def worker():
        sys.setrecursionlimit(100_000)
        for n in sizes:
            out[n] = time_once(quicksort_basic, list(range(n)))

    threading.stack_size(512 * 1024 * 1024)
    t = threading.Thread(target=worker)
    t.start()
    t.join()
    threading.stack_size(0)

    print("\n=== quicksort_basic on sorted input, recursion limit raised ===")
    print(f"{'n':>8} | {'time (ms)':>10} | {'ratio to previous':>17}")
    prev = None
    for n in sizes:
        ratio = "" if prev is None else f"{out[n] / prev:.2f}"
        print(f"{n:>8} | {fmt(out[n]):>10} | {ratio:>17}")
        prev = out[n]
    return out


# ---------------------------------------------------------------------------
# Experiment 3: choosing the cutoff
# ---------------------------------------------------------------------------

def experiment_cutoff():
    rng = random.Random(SEED + 1)
    data = [rng.randint(0, 1_000_000) for _ in range(100_000)]
    cutoffs = [1, 4, 8, 16, 32, 64]
    rounds = 11
    samples = {c: [] for c in cutoffs}
    # The cutoffs are interleaved round by round (in a shuffled order) so
    # that background load on the machine affects every cutoff equally,
    # instead of penalising whichever happened to run during a busy spell.
    for _ in range(rounds):
        order = cutoffs[:]
        rng.shuffle(order)
        for c in order:
            samples[c].append(time_once(lambda a, c=c: quicksort_improved(a, c), data))
    out = {c: statistics.median(samples[c]) for c in cutoffs}
    print(f"\n=== quicksort_improved, n = 100,000 random, median of {rounds} ===")
    print(f"{'cutoff':>7} | {'median (ms)':>11} | {'fastest (ms)':>12}")
    for c in cutoffs:
        print(f"{c:>7} | {fmt(out[c]):>11} | {fmt(min(samples[c])):>12}")
    best = min(out, key=out.get)
    print(f"best cutoff: {best}")
    return out, best


# ---------------------------------------------------------------------------
# Experiment 4: best version against sorted()
# ---------------------------------------------------------------------------

def experiment_vs_builtin(best_cutoff):
    rng = random.Random(SEED + 2)
    out = {}
    print(f"\n=== improved (cutoff={best_cutoff}) vs sorted(), n = 100,000 ===")
    print(f"{'input':>11} | {'improved':>10} | {'sorted()':>10} | {'ratio':>6}")
    for kind in ["random", "sorted", "duplicates"]:
        data = make_input(kind, 100_000, rng)
        mine = time_median(lambda a: quicksort_improved(a, best_cutoff), data, 5)
        builtin = time_median(lambda a: a.sort(), data, 5)
        out[kind] = {"improved": mine, "sorted()": builtin,
                     "ratio": mine / builtin}
        print(f"{kind:>11} | {fmt(mine):>10} | {fmt(builtin):>10} | "
              f"{mine / builtin:>6.1f}")
    return out


# ---------------------------------------------------------------------------
# Graphs
# ---------------------------------------------------------------------------

# Line colours, as hex codes so they never depend on matplotlib's colour cycle.
COLOURS = {"basic": "#c0392b", "improved": "#2471a3", "sorted()": "#7f8c8d"}
FIT_COLOUR = "#000000"
GRID_COLOUR = "#b0b0b0"


def draw_graphs(types_table, deep, cutoff_table):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # Locked style: start from matplotlib's built-in defaults (ignoring any
    # matplotlibrc or style a particular machine has set up), then fix the font,
    # font size and resolution. DejaVu Sans ships with matplotlib itself, so
    # the images come out looking identical on every computer.
    plt.rcdefaults()
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "figure.dpi": 100,
        "savefig.dpi": 200,
    })

    # Figure 1: one panel per input type (left to right: random, sorted,
    # duplicates). The report caption names the panels, so there is no title.
    fig, axes = plt.subplots(1, 3, figsize=(13, 4), sharey=False)
    for ax, kind in zip(axes, ["random", "sorted", "duplicates"]):
        for name in ["basic", "improved", "sorted()"]:
            xs = [n for n in SIZES if not isinstance(types_table[kind][n][name], str)]
            ys = [types_table[kind][n][name] * 1000 for n in xs]
            if xs:
                ax.plot(xs, ys, marker="o", label=name, color=COLOURS[name])
            crashed = [n for n in SIZES if isinstance(types_table[kind][n][name], str)]
            if crashed:
                # Crashes have no running time, so they are marked on the x-axis.
                ax.scatter(crashed, [0] * len(crashed), marker="x", s=60,
                           color=COLOURS[name], label=f"{name}: RecursionError")
        ax.set_xlabel("n (number of elements)")
        ax.set_ylabel("time (ms)")
        ax.grid(color=GRID_COLOUR, alpha=0.5)
        ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig("fig1_input_types.png")
    plt.close(fig)

    # Figure 2: basic quicksort on sorted input with a deep stack, against a
    # c*n^2 curve fitted through the largest measurement.
    fig, ax = plt.subplots(figsize=(6, 4))
    xs = sorted(deep)
    ys = [deep[n] * 1000 for n in xs]
    c = ys[-1] / xs[-1] ** 2
    ax.plot(xs, ys, marker="o", color=COLOURS["basic"], label="measured")
    ax.plot(xs, [c * n * n for n in xs], linestyle="--", color=FIT_COLOUR,
            label="c·n² fit")
    ax.set_xlabel("n (number of elements)")
    ax.set_ylabel("time (ms)")
    ax.grid(color=GRID_COLOUR, alpha=0.5)
    ax.legend()
    fig.tight_layout()
    fig.savefig("fig2_basic_quadratic.png")
    plt.close(fig)

    # Figure 3: effect of the insertion sort cutoff (log2 x-axis).
    fig, ax = plt.subplots(figsize=(6, 4))
    cs = sorted(cutoff_table)
    ax.plot(cs, [cutoff_table[c] * 1000 for c in cs], marker="o",
            color=COLOURS["improved"])
    ax.set_xscale("log", base=2)
    ax.set_xticks(cs)
    ax.set_xticklabels([str(c) for c in cs])
    ax.set_xlabel("cutoff")
    ax.set_ylabel("time (ms)")
    ax.grid(color=GRID_COLOUR, alpha=0.5)
    fig.tight_layout()
    fig.savefig("fig3_cutoff.png")
    plt.close(fig)


def load_results(path="results.json"):
    """Read a saved results.json back into the shapes draw_graphs expects.
    JSON stores dictionary keys as strings, so the sizes and cutoffs are
    turned back into integers here."""
    with open(path) as f:
        data = json.load(f)
    types_table = {kind: {int(n): row for n, row in rows.items()}
                   for kind, rows in data["input_types"].items()}
    deep = {int(n): t for n, t in data["basic_deep"].items()}
    cutoff_table = {int(c): t for c, t in data["cutoff"].items()}
    return types_table, deep, cutoff_table


if __name__ == "__main__":
    # "python benchmark.py --plot-only" redraws the graphs from an existing
    # results.json without timing anything again, so the images always show
    # exactly the numbers that were saved.
    if "--plot-only" in sys.argv:
        draw_graphs(*load_results())
        print("Redrew fig1..fig3 PNG files from results.json.")
        sys.exit(0)

    # Fixed seed for the random pivots too (the input lists already use their
    # own seeded generators), so every run makes the same pivot choices.
    random.seed(SEED)

    print(f"Python {platform.python_version()} on {platform.platform()}")
    print(f"Default recursion limit: {sys.getrecursionlimit()}")

    types_table = experiment_input_types()
    deep = experiment_basic_deep_stack()
    cutoff_table, best = experiment_cutoff()
    vs = experiment_vs_builtin(best)

    with open("results.json", "w") as f:
        json.dump({"input_types": types_table, "basic_deep": deep,
                   "cutoff": cutoff_table, "best_cutoff": best,
                   "vs_builtin": vs}, f, indent=2)
    draw_graphs(types_table, deep, cutoff_table)
    print("\nSaved results.json and fig1..fig3 PNG files.")
