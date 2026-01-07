from collections import defaultdict, deque

# entropy history per file
entropy_history = defaultdict(lambda: deque(maxlen=50))

# alerts list
alerts = []

# optional host risk score
risk_score = 0
