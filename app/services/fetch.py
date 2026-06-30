import fastf1
from datetime import datetime

SEASONS = list(range(2018, 2026))


def list_seasons() -> list:
    return SEASONS


def list_races(year: int):
    schedule = fastf1.get_event_schedule(year)
    now = datetime.now()
    past = schedule[schedule["Session5DateUtc"] <= now]
    races = past["EventName"].tolist()

    return races
