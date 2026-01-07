from collections import deque
import numpy as np

class RollingEntropy:
    def __init__(self, window=10):
        self.values = deque(maxlen=window)

    def add(self, value):
        self.values.append(value)

    def stats(self):
        if len(self.values) < 2:
            return None, None
        return float(np.mean(self.values)), float(np.std(self.values) + 1e-6)
