from fastapi import HTTPException
from pydantic import BaseModel, field_validator, ValidationInfo
from app.services.constants import SEASONS, SESSIONS_MAPPING
from app.services.fetch import list_races, list_sessions


class SeasonParams(BaseModel):
    year: int

    @field_validator("year")
    @classmethod
    def validate_year(cls, value):
        if value not in SEASONS:
            raise HTTPException(
                status_code=422, detail=f"season must be one of {SEASONS}"
            )
        return value


class SeasonRoundParams(SeasonParams):
    round_number: int

    @field_validator("round_number")
    @classmethod
    def validate_round_number(cls, value, info: ValidationInfo):
        year = info.data.get("year")
        if year is None:
            return value

        races = list_races(year)
        last_round = len(races)

        if value > last_round or value < 1:
            raise HTTPException(
                status_code=404,
                detail=f"Round {value} does not exist for {year}. Valid range: 1-{last_round}.",
            )

        return value


class SessionQueryParameters(SeasonRoundParams):
    session: str

    @field_validator("session")
    @classmethod
    def validate_session(cls, value, info: ValidationInfo):
        round_number = info.data.get("round_number")
        year = info.data.get("year")

        past_sessions = list_sessions(year, round_number)
        sessions = [SESSIONS_MAPPING[s] for s in past_sessions if s in SESSIONS_MAPPING]

        if value not in sessions:
            raise HTTPException(
                status_code=404,
                detail=f"Session {value} does not exist for round number {round_number} in {year}.",
            )

        return value
