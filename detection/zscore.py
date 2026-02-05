def is_anomaly(current, mean, std, threshold=3.0):
    z = abs((current - mean) / std)
    return z >= threshold

