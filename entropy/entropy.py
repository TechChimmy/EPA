import math
from collections import Counter

def shannon_entropy(data: bytes) -> float:
    if not data:
        return 0.0

    freq = Counter(data)
    length = len(data)

    return -sum((c/length) * math.log2(c/length) for c in freq.values())
