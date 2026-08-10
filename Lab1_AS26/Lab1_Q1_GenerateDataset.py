import random

# Generate random dataset
def GenerateDataset_343(size):
    return [random.randint(0, size * 10) for _ in range(size)]