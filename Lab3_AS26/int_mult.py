_seed = 12345

def _next_rand():
    global _seed
    _seed = (1103515245 * _seed + 12345) % (2 ** 31)
    return _seed

def random_digit(low, high):
    return low + (_next_rand() % (high - low + 1))

def random_digit_string(num_digits):
    if num_digits <= 0:
        return '0'
    first = str(random_digit(1, 9))
    rest = ''.join(str(random_digit(0, 9)) for _ in range(num_digits - 1))
    return first + rest


op_count = 0

def reset_ops():
    global op_count
    op_count = 0


def add_strings(a, b):
    a, b = a[::-1], b[::-1]
    n = max(len(a), len(b))
    result = []
    carry = 0
    for i in range(n):
        da = int(a[i]) if i < len(a) else 0
        db = int(b[i]) if i < len(b) else 0
        total = da + db + carry
        result.append(str(total % 10))
        carry = total // 10
    if carry:
        result.append(str(carry))
    return ''.join(result[::-1]).lstrip('0') or '0'


def subtract_strings(a, b):
    a, b = a[::-1], b[::-1]
    result = []
    borrow = 0
    for i in range(len(a)):
        da = int(a[i]) - borrow
        db = int(b[i]) if i < len(b) else 0
        if da < db:
            da += 10
            borrow = 1
        else:
            borrow = 0
        result.append(str(da - db))
    return ''.join(result[::-1]).lstrip('0') or '0'


def shift_left(s, zeros):
    return '0' if s == '0' else s + '0' * zeros


def traditional_multiply(a, b):
    global op_count
    a = a.lstrip('0') or '0'
    b = b.lstrip('0') or '0'
    if a == '0' or b == '0':
        return '0'
    n, m = len(a), len(b)
    result = [0] * (n + m)
    for i in range(n - 1, -1, -1):
        da = int(a[i])
        carry = 0
        for j in range(m - 1, -1, -1):
            db = int(b[j])
            op_count += 1
            pos = i + j + 1
            total = da * db + result[pos] + carry
            result[pos] = total % 10
            carry = total // 10
        result[i] += carry
    return ''.join(map(str, result)).lstrip('0') or '0'


CUTOFF = 32

def karatsuba_multiply(a, b):
    a = a.lstrip('0') or '0'
    b = b.lstrip('0') or '0'
    if a == '0' or b == '0':
        return '0'
    if len(a) <= CUTOFF or len(b) <= CUTOFF:
        return traditional_multiply(a, b)

    n = max(len(a), len(b))
    power = 1
    while power < n:
        power *= 2
    a = a.zfill(power)
    b = b.zfill(power)
    m = power // 2

    x1, x0 = a[:m], a[m:]
    y1, y0 = b[:m], b[m:]

    z2 = karatsuba_multiply(x1, y1)
    z0 = karatsuba_multiply(x0, y0)
    z1_full = karatsuba_multiply(add_strings(x1, x0), add_strings(y1, y0))
    z1 = subtract_strings(subtract_strings(z1_full, z2), z0)

    return add_strings(add_strings(shift_left(z2, 2 * m), shift_left(z1, m)), z0)


def verify(a, b):
    t = traditional_multiply(a, b)
    k = karatsuba_multiply(a, b)
    # Both implementations are string-based, so verification also works for
    # inputs much larger than the host language's native integer range.
    return t == k, t, k


def benchmark(sizes):
    print(f"{'Digits':>8} | {'Traditional ops':>16} | {'Karatsuba ops':>14} | {'Ratio':>8}")
    print("-" * 56)
    for n in sizes:
        a = random_digit_string(n)
        b = random_digit_string(n)

        reset_ops()
        traditional_multiply(a, b)
        trad_ops = op_count

        reset_ops()
        karatsuba_multiply(a, b)
        kara_ops = op_count

        ratio = trad_ops / kara_ops if kara_ops else float('inf')
        print(f"{n:>8} | {trad_ops:>16} | {kara_ops:>14} | {ratio:>7.2f}x")


if __name__ == "__main__":
    print("=== Correctness check (manual cases) ===")
    manual_tests = [
        ("12345", "6789"),
        ("999999", "999999"),
        ("123456789123456789", "987654321987654321"),
    ]
    for a, b in manual_tests:
        ok, t, k = verify(a, b)
        print(f"{a} * {b} -> match={ok}")

    print("\n=== Correctness check (random cases) ===")
    all_ok = True
    for _ in range(15):
        da = random_digit(1, 60)
        db = random_digit(1, 60)
        a = random_digit_string(da)
        b = random_digit_string(db)
        ok, t, k = verify(a, b)
        all_ok = all_ok and ok
        if not ok:
            print(f"  MISMATCH: {a} * {b}")
    print("All random cases passed:", all_ok)

    print("\n=== Performance comparison (operation counts) ===")
    benchmark([8, 16, 32, 64, 128, 256, 512, 1024])


# Analysis / Conclusion:
# Karatsuba uses three recursive products instead of four, giving
# O(n^log2(3)) complexity versus O(n^2) for grade-school multiplication.
# The cutoff uses the traditional method for small pieces, which avoids
# recursion overhead while preserving correctness for arbitrarily long strings.