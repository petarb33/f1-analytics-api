from fastapi import APIRouter, Depends
from app.services.fetch import (
    list_seasons,
    list_races,
    list_sessions,
    get_event_name_for_round_number,
)
from app.schemas.session import SeasonParams, SeasonRoundParams

router = APIRouter()


@router.get("")
def seasons():
    return {"seasons": list_seasons()}


@router.get("/{year}/races")
def season(params: SeasonParams = Depends()):
    return {f"races for season {params.year}": list_races(params.year)}


@router.get("/{year}/{round_number}/sessions")
def get_completed_sessions(params: SeasonRoundParams = Depends()):
    sessions = list_sessions(params.year, params.round_number)

    return {
        f"Sessions for {get_event_name_for_round_number(params.year, params.round_number)}": sessions
    }
