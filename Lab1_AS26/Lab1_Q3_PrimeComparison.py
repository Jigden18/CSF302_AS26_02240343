import time

from Lab1_Q3_NaiveTrialDivision import GeneratePrimesNaive_343
from Lab1_Q3_OptimizedTrialDivision import GeneratePrimesOptimized_343
from Lab1_Q3_SieveOfEratosthenes import SieveOfEratosthenes_343


# Measure average execution time for Naive Trial Division
def MeasureNaiveTime_343(N, runs=3):
    total_time_343 = 0
    for _ in range(runs):
        start_343 = time.perf_counter()
        GeneratePrimesNaive_343(N)
        end_343 = time.perf_counter()
        total_time_343 += (end_343 - start_343)
    return total_time_343 / runs


# Measure average execution time for Optimized Trial Division
def MeasureOptimizedTime_343(N, runs=3):
    total_time_343 = 0
    for _ in range(runs):
        start_343 = time.perf_counter()
        GeneratePrimesOptimized_343(N)
        end_343 = time.perf_counter()
        total_time_343 += (end_343 - start_343)
    return total_time_343 / runs


# Measure average execution time for Sieve of Eratosthenes
def MeasureSieveTime_343(N, runs=3):
    total_time_343 = 0
    for _ in range(runs):
        start_343 = time.perf_counter()
        SieveOfEratosthenes_343(N)
        end_343 = time.perf_counter()
        total_time_343 += (end_343 - start_343)
    return total_time_343 / runs


# Print a clean, bordered table header
def PrintTableHeader_343():
    print("=" * 90)
    print(f"{'PRIME GENERATION METHODS — EXECUTION TIME COMPARISON':^90}")
    print("=" * 90)
    print(f"{'N':<14}{'Naive (s)':<18}{'Optimized (s)':<18}{'Sieve (s)':<18}{'Fastest Method':<18}")
    print("-" * 90)


# Determine the fastest method for a given row
def GetFastestMethod_343(naive_time_343, optimized_time_343, sieve_time_343):
    times_343 = {
        "Naive": naive_time_343,
        "Optimized": optimized_time_343,
        "Sieve": sieve_time_343
    }
    return min(times_343, key=times_343.get)


# Main driver code
def Main_343():
    input_sizes_343 = [10000, 50000, 100000, 500000, 1000000]

    PrintTableHeader_343()

    for N in input_sizes_343:
        naive_time_343 = MeasureNaiveTime_343(N)
        optimized_time_343 = MeasureOptimizedTime_343(N)
        sieve_time_343 = MeasureSieveTime_343(N)

        fastest_method_343 = GetFastestMethod_343(naive_time_343, optimized_time_343, sieve_time_343)

        print(f"{N:<14,}{naive_time_343:<18.6f}{optimized_time_343:<18.6f}{sieve_time_343:<18.6f}{fastest_method_343:<18}")

    print("=" * 90)
    print("NOTE: Naive Trial Division may take considerably longer at N = 500,000")
    print("and N = 1,000,000 due to its O(n * sqrt(n)) overall complexity. This is")
    print("expected behavior and demonstrates its poor scalability compared to")
    print("Optimized Trial Division and the Sieve of Eratosthenes.")
    print("=" * 90)


if __name__ == "__main__":
    Main_343()