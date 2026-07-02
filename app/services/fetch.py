import fastf1
from datetime import datetime
from app.services.constants import SEASONS


def list_seasons() -> list:
    return SEASONS


def list_races(year: int):
    schedule = fastf1.get_event_schedule(year)
    now = datetime.now()
    past = schedule[schedule["Session1DateUtc"] <= now]
    races = past["EventName"].tolist()

    return races


def list_sessions(year: int, round_number: int) -> list:
    schedule = fastf1.get_event_schedule(year)

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


def load_session(params):
    session = fastf1.get_session(
        params["season"], params["round_number"], params["session"]
    )
    session.load()

    return session


def get_drivers(data) -> list[str]:
    return list(data.results["Abbreviation"])
