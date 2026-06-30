from fastapi import APIRouter
from app.services.fetch import (
    list_seasons,
    list_races,
    list_sessions,
    get_event_name_for_round_number,
)

router = APIRouter()


@router.get("/")
def root():
    return {"message": "Hello World"}


@router.get("/seasons")
def seasons():
    return {"seasons": list_seasons()}


@router.get("/seasons/{year}/races")
def season(year: int):
    return {f"races for season {year}": list_races(year)}


@router.get("/seasons/{year}/{round_number}/sessions")
def get_completed_sessions(year: int, round_number: int):
    sessions = list_sessions(year, round_number)

    return {
        f"Sessions for {get_event_name_for_round_number(year, round_number)}": sessions
    }
