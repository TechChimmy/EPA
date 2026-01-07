class CUSUM:
    def __init__(self, drift=0.1, threshold=1.5):
        self.sum = 0
        self.drift = drift
        self.threshold = threshold

    def update(self, value):
        self.sum = max(0, self.sum + value - self.drift)
        return self.sum > self.threshold
