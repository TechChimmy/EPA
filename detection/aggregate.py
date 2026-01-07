from collections import defaultdict

class ProcessAggregator:
    def __init__(self):
        self.counts = defaultdict(int)

    def update(self, pid):
        self.counts[pid] += 1
        return self.counts[pid]
