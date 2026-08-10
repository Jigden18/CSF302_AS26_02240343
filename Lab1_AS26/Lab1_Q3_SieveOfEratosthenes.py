# Sieve of Eratosthenes
def SieveOfEratosthenes_343(N):
    is_prime_343 = [True] * (N + 1)
    is_prime_343[0:2] = [False, False]

    for i in range(2, int(N ** 0.5) + 1):
        if is_prime_343[i]:
            for multiple in range(i * i, N + 1, i):
                is_prime_343[multiple] = False

    primes = [num for num, prime in enumerate(is_prime_343) if prime]
    return primes