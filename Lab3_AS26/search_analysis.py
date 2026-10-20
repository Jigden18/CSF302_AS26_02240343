
# Simple Linear Congruential Generator (no imports needed)
_rng_state = 42  # seed

def next_rand():
    global _rng_state
    _rng_state = (1103515245 * _rng_state + 12345) % (2 ** 31)
    return _rng_state


def generate_sorted_array(n, low=1, high=10000):
    arr = []
    for _ in range(n):
        val = low + (next_rand() % (high - low + 1))
        arr.append(val)
    arr.sort()
    return arr


# Binary Search 
def binary_search(arr, key):
    low, high = 0, len(arr) - 1
    comparisons = 0
    while low <= high:
        mid = (low + high) // 2
        comparisons += 1
        if arr[mid] == key:
            return mid, comparisons
        elif arr[mid] < key:
            low = mid + 1
        else:
            high = mid - 1
    return -1, comparisons


# Ternary Search 
def ternary_search(arr, key):
    low, high = 0, len(arr) - 1
    comparisons = 0
    while low <= high:
        mid1 = low + (high - low) // 3
        mid2 = high - (high - low) // 3

        comparisons += 1
        if arr[mid1] == key:
            return mid1, comparisons

        comparisons += 1
        if arr[mid2] == key:
            return mid2, comparisons

        comparisons += 1
        if key < arr[mid1]:
            high = mid1 - 1
        elif key > arr[mid2]:
            low = mid2 + 1
        else:
            low = mid1 + 1
            high = mid2 - 1
    return -1, comparisons


# Best / Worst case helpers 
def best_case_binary(arr):
    # Best case: key is exactly the first element checked (the middle)
    mid = (0 + len(arr) - 1) // 2
    key = arr[mid]
    return binary_search(arr, key)


def best_case_ternary(arr):
    # Best case: key is exactly the first mid1 checked
    low, high = 0, len(arr) - 1
    mid1 = low + (high - low) // 3
    key = arr[mid1]
    return ternary_search(arr, key)


def worst_case_binary(arr):
    # Worst case: key absent, forces search to shrink to nothing
    key = arr[-1] + 999999
    return binary_search(arr, key)


def worst_case_ternary(arr):
    key = arr[-1] + 999999
    return ternary_search(arr, key)


# Comparison Table 
def comparison_table():
    sizes = [10, 50, 100, 500, 1000, 5000, 10000]
    print("\n{:<10}{:<20}{:<20}".format("n", "Binary (worst)", "Ternary (worst)"))
    print("-" * 50)
    rows = []
    for n in sizes:
        arr = generate_sorted_array(n)
        _, b_cmp = worst_case_binary(arr)
        _, t_cmp = worst_case_ternary(arr)
        rows.append((n, b_cmp, t_cmp))
        print("{:<10}{:<20}{:<20}".format(n, b_cmp, t_cmp))

    # simple text-based bar graph (no plotting libraries/imports required)
    print("\nText Graph (each '*' = 1 comparison)")
    for n, b_cmp, t_cmp in rows:
        print(f"n={n:<6} Binary : " + "*" * b_cmp + f" ({b_cmp})")
        print(f"n={n:<6} Ternary: " + "*" * t_cmp + f" ({t_cmp})")
        print()

    # Analysis / Conclusion
    # Binary Search recurrence: T(n) = T(n/2) + O(1)  -> O(log2 n)
    # Ternary Search recurrence: T(n) = T(n/3) + O(1)  -> O(log3 n), but each
    # level does up to 3 comparisons instead of 1.
    # Result: log2(n) < log3(n) * 3 for all n, so Binary Search consistently
    # performs fewer total comparisons than Ternary Search, even though
    # Ternary reduces the search space faster per level. Ternary Search's
    # extra comparisons per level (2-3 vs 1) outweigh the benefit of the
    # smaller branching factor.

    return rows


# Menu 
current_array = []

def display_array():
    if not current_array:
        print("Array is empty. Generate it first (Option 1).")
    else:
        print(current_array)


def menu():
    global current_array
    while True:
        print("\n===== Binary vs Ternary Search Menu =====")
        print("1. Generate n sorted random numbers -> Array")
        print("2. Display Array")
        print("3. Search for a key using Binary Search")
        print("4. Search for a key using Ternary Search")
        print("5. Step/frequency count - Best Case")
        print("6. Step/frequency count - Worst Case")
        print("7. Step/frequency count comparison table across increasing n")
        print("8. Exit")
        choice = input("Enter choice: ").strip()

        if choice == "1":
            n = int(input("Enter n: "))
            current_array = generate_sorted_array(n)
            print(f"Generated {n} sorted numbers.")

        elif choice == "2":
            display_array()

        elif choice == "3":
            if not current_array:
                print("Generate the array first (Option 1).")
                continue
            key = int(input("Enter key to search: "))
            idx, cmp_count = binary_search(current_array, key)
            if idx != -1:
                print(f"Found at index {idx}. Comparisons: {cmp_count}")
            else:
                print(f"Not found. Comparisons: {cmp_count}")

        elif choice == "4":
            if not current_array:
                print("Generate the array first (Option 1).")
                continue
            key = int(input("Enter key to search: "))
            idx, cmp_count = ternary_search(current_array, key)
            if idx != -1:
                print(f"Found at index {idx}. Comparisons: {cmp_count}")
            else:
                print(f"Not found. Comparisons: {cmp_count}")

        elif choice == "5":
            if not current_array:
                print("Generate the array first (Option 1).")
                continue
            _, b_cmp = best_case_binary(current_array)
            _, t_cmp = best_case_ternary(current_array)
            print(f"Best case Binary Search comparisons : {b_cmp}")
            print(f"Best case Ternary Search comparisons: {t_cmp}")

        elif choice == "6":
            if not current_array:
                print("Generate the array first (Option 1).")
                continue
            _, b_cmp = worst_case_binary(current_array)
            _, t_cmp = worst_case_ternary(current_array)
            print(f"Worst case Binary Search comparisons : {b_cmp}")
            print(f"Worst case Ternary Search comparisons: {t_cmp}")

        elif choice == "7":
            comparison_table()

        elif choice == "8":
            print("Exiting...")
            break

        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    menu()