import fastf1
from fastapi import HTTPException
from datetime import datetime

SEASONS = list(range(2018, 2027))


def list_seasons() -> list:
    return SEASONS


def list_races(year: int):
    if year not in SEASONS:
        raise HTTPException(
            status_code=404,
            detail=f"Invalid year: {year}. Please use a season from {SEASONS}",
        )

    schedule = fastf1.get_event_schedule(year)
    now = datetime.now()
    past = schedule[schedule["Session5DateUtc"] <= now]
    races = past["EventName"].tolist()

    return races


def list_sessions(year: int, round_number: int) -> list:
    if year not in SEASONS:
        raise HTTPException(
            status_code=404,
            detail=f"Invalid year: {year}. Please use a season from {SEASONS}",
        )

    schedule = fastf1.get_event_schedule(year)
    last_round = int(schedule.iloc[-1]["RoundNumber"])

    if round_number > last_round or round_number < 1:
        raise HTTPException(
            status_code=404,
            detail=f"Round {round_number} does not exist for {year}. Valid range: 1-{last_round}.",
        )

    matches = schedule[schedule["RoundNumber"] == round_number]

    event = matches.iloc[0]
    now = datetime.now()

    sessions = []
    for i in range(1, 6):
        name = event.get(f"Session{i}")
        date = event.get(f"Session{i}DateUtc")
        if name and date is not None and date <= now:
            sessions.append(name)

    return sessions


def get_event_name_for_round_number(year: int, round_number: int) -> str:
    schedule = fastf1.get_event_schedule(year)
    matches = schedule[schedule["RoundNumber"] == round_number]
    grand_prix = matches["EventName"].iloc[0]

    return grand_prix
