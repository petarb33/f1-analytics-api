SEASONS = list(range(2018, 2027))

SESSIONS_MAPPING = {
    "Practice 1": "FP1",
    "Practice 2": "FP2",
    "Practice 3": "FP3",
    "Sprint Qualifying": "SQ",
    "Sprint Shootout": "SS",
    "Sprint": "S",
    "Qualifying": "Q",
    "Race": "R",
}

SESSIONS_MAPPING_REVERSED = {v: k for k, v in SESSIONS_MAPPING.items()}

RACE_SESSIONS = ("R", "S")

CONDITION_COLORS = {"VSC": "tan", "SC": "sienna", "RF": "red"}

SESSION_COLORS = {"Q1": "#b2df8a", "Q2": "#66c2a5", "Q3": "#1b7837"}
