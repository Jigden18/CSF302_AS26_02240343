import time

from Lab1_Q1_LinearSearch import LinearSearch_343
from Lab1_Q1_BinarySearch import BinarySearch_343
from Lab1_Q1_GenerateDataset import GenerateDataset_343


# Measure average execution time for Linear Search
def MeasureLinearSearchTime_343(arr, target, runs=5):
    total_time_343 = 0
    for _ in range(runs):
        start_343 = time.perf_counter()
        LinearSearch_343(arr, target)
        end_343 = time.perf_counter()
        total_time_343 += (end_343 - start_343)
    return total_time_343 / runs


# Measure average execution time for Binary Search
def MeasureBinarySearchTime_343(arr, target, runs=5):
    total_time_343 = 0
    for _ in range(runs):
        start_343 = time.perf_counter()
        BinarySearch_343(arr, target)
        end_343 = time.perf_counter()
        total_time_343 += (end_343 - start_343)
    return total_time_343 / runs


# Print a clean, bordered table header
def PrintTableHeader_343():
    print("=" * 78)
    print(f"{'LINEAR SEARCH vs BINARY SEARCH — EXECUTION TIME COMPARISON':^78}")
    print("=" * 78)
    print(f"{'Input Size':<15}{'Linear Search (s)':<22}{'Binary Search (s)':<22}{'Performance Ratio (x)':<19}")
    print("-" * 78)


# Main driver code
def Main_343():
    input_sizes_343 = [1000, 5000, 10000, 50000, 100000, 500000, 1000000]

    PrintTableHeader_343()

    for size in input_sizes_343:
        dataset_343 = GenerateDataset_343(size)
        target_343 = dataset_343[-1]  # worst-case target for linear search

        # Linear Search on unsorted dataset
        linear_time_343 = MeasureLinearSearchTime_343(dataset_343, target_343)

        # Sort dataset before Binary Search
        sorted_dataset_343 = sorted(dataset_343)

        # Binary Search on sorted dataset
        binary_time_343 = MeasureBinarySearchTime_343(sorted_dataset_343, target_343)

        # Avoid division by zero if binary_time is extremely small
        performance_ratio_343 = linear_time_343 / binary_time_343 if binary_time_343 > 0 else float("inf")

        print(f"{size:<15,}{linear_time_343:<22.6f}{binary_time_343:<22.6f}{performance_ratio_343:<19.2f}")

    print("=" * 78)


if __name__ == "__main__":
    Main_343()