# Binary Search
def BinarySearch_343(arr, target):
    low_343 = 0
    high_343 = len(arr) - 1

    while low_343 <= high_343:
        mid_343 = (low_343 + high_343) // 2
        if arr[mid_343] == target:
            return mid_343
        elif arr[mid_343] < target:
            low_343 = mid_343 + 1
        else:
            high_343 = mid_343 - 1
    return -1