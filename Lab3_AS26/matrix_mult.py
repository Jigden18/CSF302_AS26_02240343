# Matrix Multiplication: Strassen's vs Traditional — manual input, no imports needed

# ---------------------------------------------------------------------------
# 1. Traditional Method: O(n^3)
# ---------------------------------------------------------------------------
def traditional_multiply(A, B):
    n = len(A)
    C = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            total = 0
            for k in range(n):
                total += A[i][k] * B[k][j]
            C[i][j] = total
    return C


# ---------------------------------------------------------------------------
# 2. Strassen's Algorithm: divide and conquer, 7 multiplications per split
# ---------------------------------------------------------------------------
def add_matrix(A, B):
    n = len(A)
    return [[A[i][j] + B[i][j] for j in range(n)] for i in range(n)]


def sub_matrix(A, B):
    n = len(A)
    return [[A[i][j] - B[i][j] for j in range(n)] for i in range(n)]


def split_matrix(M):
    n = len(M)
    mid = n // 2
    top_left = [row[:mid] for row in M[:mid]]
    top_right = [row[mid:] for row in M[:mid]]
    bottom_left = [row[:mid] for row in M[mid:]]
    bottom_right = [row[mid:] for row in M[mid:]]
    return top_left, top_right, bottom_left, bottom_right


def join_matrix(C11, C12, C21, C22):
    top = [c11_row + c12_row for c11_row, c12_row in zip(C11, C12)]
    bottom = [c21_row + c22_row for c21_row, c22_row in zip(C21, C22)]
    return top + bottom


def strassen_multiply(A, B):
    n = len(A)

    if n == 1:
        return [[A[0][0] * B[0][0]]]

    A11, A12, A21, A22 = split_matrix(A)
    B11, B12, B21, B22 = split_matrix(B)

    M1 = strassen_multiply(add_matrix(A11, A22), add_matrix(B11, B22))
    M2 = strassen_multiply(add_matrix(A21, A22), B11)
    M3 = strassen_multiply(A11, sub_matrix(B12, B22))
    M4 = strassen_multiply(A22, sub_matrix(B21, B11))
    M5 = strassen_multiply(add_matrix(A11, A12), B22)
    M6 = strassen_multiply(sub_matrix(A21, A11), add_matrix(B11, B12))
    M7 = strassen_multiply(sub_matrix(A12, A22), add_matrix(B21, B22))

    C11 = add_matrix(sub_matrix(add_matrix(M1, M4), M5), M7)
    C12 = add_matrix(M3, M5)
    C21 = add_matrix(M2, M4)
    C22 = add_matrix(sub_matrix(add_matrix(M1, M3), M2), M6)

    return join_matrix(C11, C12, C21, C22)


# ---------------------------------------------------------------------------
# Manual input helpers
# ---------------------------------------------------------------------------
def is_power_of_2(n):
    return n > 0 and (n & (n - 1)) == 0


def input_matrix(name, n):
    print(f"\nEnter matrix {name} ({n}x{n}), row by row.")
    print(f"Type {n} space-separated numbers per row, then press Enter.")
    M = []
    for i in range(n):
        while True:
            row_input = input(f"Row {i + 1}: ").split()
            if len(row_input) != n:
                print(f"  Error: expected {n} values, got {len(row_input)}. Try again.")
                continue
            try:
                row = [int(x) for x in row_input]
            except ValueError:
                print("  Error: please enter integers only. Try again.")
                continue
            M.append(row)
            break
    return M


def get_matrix_size():
    while True:
        try:
            n = int(input("Enter matrix size n (must be a power of 2, e.g. 2, 4, 8, 16): "))
        except ValueError:
            print("  Error: please enter an integer.")
            continue
        if not is_power_of_2(n):
            print("  Error: n must be a power of 2. Try again.")
            continue
        return n


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def print_matrix(M, label=""):
    if label:
        print(label)
    for row in M:
        print(row)
    print()


def matrices_equal(A, B):
    n = len(A)
    return all(A[i][j] == B[i][j] for i in range(n) for j in range(n))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    n = get_matrix_size()
    A = input_matrix("A", n)
    B = input_matrix("B", n)

    print_matrix(A, "\nMatrix A:")
    print_matrix(B, "Matrix B:")

    C_trad = traditional_multiply(A, B)
    C_strassen = strassen_multiply(A, B)

    print_matrix(C_trad, "Result (Traditional):")
    print_matrix(C_strassen, "Result (Strassen's):")

    print("Results match:", matrices_equal(C_trad, C_strassen))


# Analysis / Conclusion:
# Both methods produce the same matrix. Traditional multiplication performs
# O(n^3) scalar multiplications, while Strassen reduces recursive products to
# 7 per split and has complexity O(n^log2(7)); its extra additions and Python
# list allocation can make it slower for small matrices.