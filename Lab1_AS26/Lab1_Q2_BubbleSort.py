# Bubble Sort
def BubbleSort_343(arr):
    a_343 = arr.copy()
    n_343 = len(a_343)
    for i in range(n_343 - 1):
        swapped = False
        for j in range(n_343 - 1 - i):
            if a_343[j] > a_343[j + 1]:
                a_343[j], a_343[j + 1] = a_343[j + 1], a_343[j]
                swapped = True
        if not swapped:
            break
    return a_343