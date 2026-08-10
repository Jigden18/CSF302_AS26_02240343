import math

# Optimized Trial Division (checking up to sqrt(n))
def IsPrimeOptimized_343(n):
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False

    limit_343 = int(math.sqrt(n)) + 1
    for i in range(3, limit_343, 2):
        if n % i == 0:
            return False
    return True


def GeneratePrimesOptimized_343(N):
    primes_343 = []
    for num in range(2, N + 1):
        if IsPrimeOptimized_343(num):
            primes_343.append(num)
    return primes_343