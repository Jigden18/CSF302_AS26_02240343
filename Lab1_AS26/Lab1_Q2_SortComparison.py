import time

from Lab1_Q2_BubbleSort import BubbleSort_343
from Lab1_Q2_MergeSort import MergeSort_343
from Lab1_Q2_GenerateDataset import GenerateDataset_343


# Measure average execution time for Bubble Sort
def MeasureBubbleSortTime_343(arr, runs=5):
    total_time_343 = 0
    for _ in range(runs):
        start_343 = time.perf_counter()
        BubbleSort_343(arr)
        end_343 = time.perf_counter()
        total_time_343 += (end_343 - start_343)
    return total_time_343 / runs


# Measure average execution time for Merge Sort
def MeasureMergeSortTime_343(arr, runs=5):
    total_time_343 = 0
    for _ in range(runs):
        start_343 = time.perf_counter()
        MergeSort_343(arr)
        end_343 = time.perf_counter()
        total_time_343 += (end_343 - start_343)
    return total_time_343 / runs


# Print a clean, bordered table header
def PrintTableHeader_343():
    print("=" * 78)
    print(f"{'BUBBLE SORT vs MERGE SORT — EXECUTION TIME COMPARISON':^78}")
    print("=" * 78)
    print(f"{'Input Size':<15}{'Bubble Sort (s)':<22}{'Merge Sort (s)':<22}{'Performance Ratio (x)':<19}")
    print("-" * 78)


# Main driver code
def Main_343():
    input_sizes_343 = [100, 500, 1000, 2000, 4000, 8000]

    PrintTableHeader_343()

    for size in input_sizes_343:
        dataset_343 = GenerateDataset_343(size)

        bubble_time_343 = MeasureBubbleSortTime_343(dataset_343)
        merge_time_343 = MeasureMergeSortTime_343(dataset_343)

        # Avoid division by zero if merge_time is extremely small
        performance_ratio_343 = bubble_time_343 / merge_time_343 if merge_time_343 > 0 else float("inf")

        print(f"{size:<15,}{bubble_time_343:<22.6f}{merge_time_343:<22.6f}{performance_ratio_343:<19.2f}")

    print("=" * 78)


if __name__ == "__main__":
    Main_343()