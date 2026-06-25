# Mock World Cup standings for the demo.
# There are no live World Cup games during the lecture, so the app falls back
# on these fixed numbers and the prediction still works offline, every time.

MOCK_STATS = {
    "Spain":     {"form": "WWDWL", "goalsFor": 9,  "goalsAgainst": 4, "games": 5},
    "Brazil":    {"form": "WWWDW", "goalsFor": 11, "goalsAgainst": 3, "games": 5},
    "France":    {"form": "WDWWL", "goalsFor": 8,  "goalsAgainst": 5, "games": 5},
    "Argentina": {"form": "WWWWD", "goalsFor": 10, "goalsAgainst": 2, "games": 5},
    "England":   {"form": "WDDWL", "goalsFor": 7,  "goalsAgainst": 5, "games": 5},
    "Germany":   {"form": "LWDWW", "goalsFor": 8,  "goalsAgainst": 6, "games": 5},
}


def mockStrength(team):
    stats = MOCK_STATS.get(team)
    if stats is None:
        return 1.0
    points = stats["form"].count("W") * 3 + stats["form"].count("D")
    games = stats["games"]
    return points / games + (stats["goalsFor"] - stats["goalsAgainst"]) / games
