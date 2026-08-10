# Merge Sort
from turtle import right


def MergeSort_343(arr):
    if len(arr) <= 1:
        return arr

    mid_343 = len(arr) // 2
    left_343 = MergeSort_343(arr[:mid_343])
    right_343 = MergeSort_343(arr[mid_343:])

    return Merge_343(left_343, right_343)


def Merge_343(left_343, right_343):
    result = []
    i_343 = j_343 = 0

    while i_343 < len(left_343) and j_343 < len(right_343):
        if left_343[i_343] <= right_343[j_343]:
            result.append(left_343[i_343])
            i_343 += 1
        else:
            result.append(right_343[j_343])
            j_343 += 1

    result.extend(left_343[i_343:])
    result.extend(right_343[j_343:])
    return result