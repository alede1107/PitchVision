MULTIPLIERS = {
    "Suspension": 0.85,
    "Injury": 0.88,
    "Manager": 0.92,
    "Weather": 0.90,
    "Morale": 1.08,
}


def predictScore(strength, factors):
    for factor in factors:
        strength *= MULTIPLIERS.get(factor, 1)
    return max(0, min(4, round(strength)))
