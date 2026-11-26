"""
benchmark.py
============
CSF302 Assignment 2, Part C: timing experiments for closest.py
Student : Jigden Shakya (02240343)

What it does
------------
1. Times closest_pair_brute and closest_pair for n = 1,000, 2,000, 4,000, ...,
   64,000 random camera trap positions. Both functions get the SAME points.
   Brute force runs in a separate process and is stopped after 60 seconds;
   once it has been stopped, larger n are skipped (they would only be slower).
2. Prints a table with times, doubling ratios t(2n)/t(n) and checks that both
   functions agree whenever both finished.
3. Estimates the growth exponent k in t ~ n^k from the log-log slope.
4. Searches small n (2 to 150) for the crossover point where divide and
   conquer becomes faster than brute force.
5. Saves timings.csv, crossover.csv and loglog.png (needs matplotlib).

Run:  python benchmark.py            (full run, a few minutes)
      python benchmark.py --quick    (smaller sizes, for a fast check)
      python benchmark.py --plot-only (redraw loglog.png from timings.csv)
"""

import csv
import math
import multiprocessing as mp
import platform
import random
import sys
import time
import timeit

from closest import closest_pair, closest_pair_brute

TIME_LIMIT = 60.0           # seconds allowed for one brute force run
SEED = 2240343              # fixed seed (student number) so runs repeat
MAP_SIZE = 100_000.0        # traps placed on a 100 km x 100 km grid, in metres


def make_points(n, seed=SEED):
    """n random trap positions; the same (n, seed) always gives the same list."""
    rng = random.Random(seed + n)
    return [(rng.uniform(0, MAP_SIZE), rng.uniform(0, MAP_SIZE)) for _ in range(n)]


# ---------------------------------------------------------------------------
# Large n timing
# ---------------------------------------------------------------------------

def _brute_worker(n, queue):
    """Child process: rebuild the same points, time brute force, report back."""
    pts = make_points(n)
    start = time.perf_counter()
    result = closest_pair_brute(pts)
    queue.put((time.perf_counter() - start, result))


def time_brute_with_limit(n):
    """Return (seconds, result), or (None, None) if it passed TIME_LIMIT."""
    queue = mp.Queue()
    proc = mp.Process(target=_brute_worker, args=(n, queue))
    proc.start()
    proc.join(TIME_LIMIT)
    if proc.is_alive():                 # still running after 60 s: stop it
        proc.terminate()
        proc.join()
        return None, None
    return queue.get()


def time_dc(n, repeats=5):
    """Best of `repeats` runs of divide and conquer (the minimum is the run
    least disturbed by other programs on the machine)."""
    pts = make_points(n)
    best, result = math.inf, None
    for _ in range(repeats):
        start = time.perf_counter()
        result = closest_pair(pts)
        best = min(best, time.perf_counter() - start)
    return best, result


def loglog_slope(ns, ts):
    """Least squares slope of log(t) against log(n): the k in t ~ n^k."""
    xs = [math.log(n) for n in ns]
    ys = [math.log(t) for t in ts]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = sum((x - mx) ** 2 for x in xs)
    return num / den


def fmt(t):
    return "%.4f" % t if t is not None else "> 60 (stopped)"


def large_n_experiment(sizes):
    rows = []
    brute_stopped = False
    prev_b = prev_d = None

    print("\nPart C timing: n from %d to %d (brute force limit %d s)\n" % (sizes[0], sizes[-1], TIME_LIMIT))
    header = "%8s | %16s | %8s | %12s | %8s | %10s | %s" % (
        "n", "brute (s)", "ratio", "D&C (s)", "ratio", "speed-up", "same d?")
    print(header)
    print("-" * len(header))

    for n in sizes:
        t_d, res_d = time_dc(n)

        if brute_stopped:
            t_b, res_b, status = None, None, "skipped"
        else:
            t_b, res_b = time_brute_with_limit(n)
            status = "ok" if t_b is not None else "stopped"
            if t_b is None:
                brute_stopped = True

        ratio_b = t_b / prev_b if (t_b and prev_b) else None
        ratio_d = t_d / prev_d if prev_d else None
        speedup = t_b / t_d if t_b else None
        agree = (math.isclose(res_b[0], res_d[0], rel_tol=1e-12) if res_b else None)

        print("%8d | %16s | %8s | %12.4f | %8s | %10s | %s" % (
            n,
            fmt(t_b) if status != "skipped" else "skipped",
            "%.2f" % ratio_b if ratio_b else "-",
            t_d,
            "%.2f" % ratio_d if ratio_d else "-",
            "%.0fx" % speedup if speedup else "-",
            {True: "yes", False: "NO", None: "-"}[agree]))

        rows.append({"n": n, "brute_s": t_b, "brute_status": status,
                     "dc_s": t_d, "brute_ratio": ratio_b, "dc_ratio": ratio_d,
                     "speedup": speedup, "agree": agree, "closest_d_m": res_d[0]})
        prev_b, prev_d = t_b, t_d

    done_b = [(r["n"], r["brute_s"]) for r in rows if r["brute_s"]]
    k_b = loglog_slope(*zip(*done_b)) if len(done_b) >= 2 else float("nan")
    k_d = loglog_slope([r["n"] for r in rows], [r["dc_s"] for r in rows])
    print("\nLog-log slope (t ~ n^k): brute force k = %.2f, divide and conquer k = %.2f" % (k_b, k_d))
    print("Theory: brute force k = 2; n log n gives k a little above 1 over this range.")
    return rows, k_b, k_d


# ---------------------------------------------------------------------------
# Crossover search for small n
# ---------------------------------------------------------------------------

def time_small(func, pts, repeats=5, target=0.02):
    """Seconds per call, best of `repeats`. One call on a few points takes
    microseconds, far below the clock resolution, so each repeat runs the
    function many times in a loop (about `target` seconds) and divides."""
    timer = timeit.Timer(lambda: func(pts))
    one = timer.timeit(number=10) / 10
    loops = max(10, int(target / max(one, 1e-9)))
    return min(timer.repeat(repeat=repeats, number=loops)) / loops


def crossover_experiment(max_n=150, sets_per_n=3):
    """Time both functions for every n from 2 to max_n. Each n uses several
    different random point sets and the times are averaged, so one lucky
    layout does not decide the answer."""
    print("\nCrossover search: n = 2 .. %d (%d point sets per n)" % (max_n, sets_per_n))
    rows = []
    for n in range(2, max_n + 1):
        tb = td = 0.0
        for s in range(sets_per_n):
            pts = make_points(n, seed=SEED + 1000 * s)
            tb += time_small(closest_pair_brute, pts)
            td += time_small(closest_pair, pts)
        rows.append({"n": n, "brute_us": tb / sets_per_n * 1e6, "dc_us": td / sets_per_n * 1e6})

    first_faster = next((r["n"] for r in rows if r["dc_us"] < r["brute_us"]), None)
    # "Stays faster": smallest n such that D&C wins at n and at every larger n tested.
    stays_faster = None
    for k in range(len(rows)):
        if all(r["dc_us"] < r["brute_us"] for r in rows[k:]):
            stays_faster = rows[k]["n"]
            break

    print("\n%6s | %12s | %12s | %s" % ("n", "brute (us)", "D&C (us)", "faster"))
    for r in rows:
        if r["n"] <= 12 or r["n"] % 10 == 0 or (stays_faster and abs(r["n"] - stays_faster) <= 4):
            print("%6d | %12.2f | %12.2f | %s" % (r["n"], r["brute_us"], r["dc_us"],
                                                   "D&C" if r["dc_us"] < r["brute_us"] else "brute"))
    print("\nFirst n where D&C is faster          :", first_faster)
    print("Smallest n where D&C stays faster    :", stays_faster)
    return rows, first_faster, stays_faster


# ---------------------------------------------------------------------------
# Output files
# ---------------------------------------------------------------------------

def save_csv(path, rows):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print("Saved", path)


def save_loglog(path, rows):
    """Draw the log-log graph of running time against n and save it as a PNG.

    The plotted values come from `rows` (the measured timings), so no random
    data is generated here; the points themselves were made with the fixed
    SEED in make_points(), which keeps the whole pipeline repeatable.
    """
    try:
        import matplotlib
        matplotlib.use("Agg")               # draw to a file, no window needed
        import matplotlib.pyplot as plt
        plt.rcdefaults()
    except ImportError:
        print("matplotlib not installed, skipping", path)
        return

    # Style lock: matplotlib reads personal settings (matplotlibrc files, style
    # sheets, installed fonts) that differ between computers. Resetting to the
    # defaults above and fixing the font, sizes and resolution here makes the
    # saved image look exactly the same on any machine. DejaVu Sans ships with
    # matplotlib itself, so every installation has it.
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "figure.dpi": 100,
        "savefig.dpi": 200,
    })

    # Every mark gets an explicit hex colour instead of the default colour cycle.
    blue, orange, ink, muted, grid = "#257de0", "#f47230", "#1f1f1f", "#6b6b6b", "#e3e3e3"
    nb = [r["n"] for r in rows if r["brute_s"]]
    tb = [r["brute_s"] for r in rows if r["brute_s"]]
    nd = [r["n"] for r in rows]
    td = [r["dc_s"] for r in rows]

    # No title inside the graph: the report caption names the figure.
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    ax.loglog(nb, tb, "-o", color=blue, lw=2, ms=6, label="Brute force, Θ(n²)")
    ax.loglog(nd, td, "-s", color=orange, lw=2, ms=6, label="Divide and conquer, Θ(n log n)")
    ax.axhline(TIME_LIMIT, color=muted, lw=1, ls=":")
    ax.text(nd[0], TIME_LIMIT / 1.7, "60 s limit for brute force", color=muted, fontsize=9)

    # Direct labels at the last point of each line (text stays in ink colours).
    ax.annotate("brute force", (nb[-1], tb[-1]), xytext=(10, -4), textcoords="offset points",
                color=ink, fontsize=9)
    ax.annotate("divide and conquer", (nd[-1], td[-1]), xytext=(-30, -30), textcoords="offset points",
                color=ink, fontsize=9, ha="center")

    ax.set_xlabel("Number of camera traps, n (log scale)")
    ax.set_ylabel("Running time in seconds (log scale)")
    ax.set_xticks(nd)
    ax.set_xticklabels(["%dk" % (n // 1000) for n in nd])
    ax.minorticks_off()
    ax.grid(True, which="major", color=grid, lw=0.8)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(0, 0.93))
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
    print("Saved", path)


def load_timings(path="timings.csv"):
    """Read timings.csv back in (used by --plot-only)."""
    rows = []
    with open(path) as f:
        for r in csv.DictReader(f):
            rows.append({"n": int(r["n"]), "dc_s": float(r["dc_s"]),
                         "brute_s": float(r["brute_s"]) if r["brute_s"] else None})
    return rows


def main():
    if "--plot-only" in sys.argv:          # redraw the graph from saved timings
        save_loglog("loglog.png", load_timings())
        return

    quick = "--quick" in sys.argv
    sizes = [1000 * 2 ** k for k in range(7)]          # 1k, 2k, 4k, ..., 64k
    if quick:
        sizes = sizes[:3]

    print("Machine : %s, Python %s" % (platform.platform(), platform.python_version()))
    print("Processor:", platform.processor() or platform.machine())

    rows, k_b, k_d = large_n_experiment(sizes)
    save_csv("timings.csv", rows)
    save_loglog("loglog.png", rows)

    small_rows, first, stays = crossover_experiment(max_n=60 if quick else 150)
    save_csv("crossover.csv", small_rows)


if __name__ == "__main__":
    main()
