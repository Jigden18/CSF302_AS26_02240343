# Naive Prime Checking using Trial Division
def IsPrimeNaive_343(n):
    if n < 2:
        return False
    for i in range(2, n):
        if n % i == 0:
            return False
    return True


def GeneratePrimesNaive_343(N):
    primes_343 = []
    for num in range(2, N + 1):
        if IsPrimeNaive_343(num):
            primes_343.append(num)
    return primes_343