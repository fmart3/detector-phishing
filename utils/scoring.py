## mapeos de valores si fuese necesario
## envio a modelo

def score_big5_apertura(responses):
    keys = ["AE01", "AE02", "AE03", "AE06", "AE07", "AE10"]
    return sum(responses[k] for k in keys) / len(keys)