from pydantic import BaseModel, field_validator, ValidationInfo
from app.services.constants import SEASONS, SESSIONS_MAPPING, RACE_SESSIONS
from app.services.fetch import list_races, list_sessions


def get_race_count(year: int) -> int:
    return len(list_races(year))


def get_valid_sessions(year: int, round_number: int) -> tuple[str, ...]:
    past_sessions = list_sessions(year, round_number)
    return tuple(SESSIONS_MAPPING[s] for s in past_sessions if s in SESSIONS_MAPPING)


class SeasonParams(BaseModel):
    year: int

    @field_validator("year")
    @classmethod
    def validate_year(cls, value: int) -> int:
        if value not in SEASONS:
            raise ValueError(f"year must be one of {sorted(SEASONS)}")
        return value


class SeasonRoundParams(SeasonParams):
    round_number: int

    @field_validator("round_number")
    @classmethod
    def validate_round_number(cls, value: int, info: ValidationInfo):
        year = info.data.get("year")
        if year is None:
            return value

        last_round = get_race_count(year)
        if not 1 <= value <= last_round:
            raise ValueError(
                f"Round {value} does not exist for {year}. "
                f"Valid range: 1-{last_round}."
            )
        return value


class SessionParameters(SeasonRoundParams):
    session: str

    @field_validator("session")
    @classmethod
    def validate_session(cls, value, info: ValidationInfo):
        year = info.data.get("year")
        round_number = info.data.get("round_number")
        if year is None or round_number is None:
            return value

        valid = get_valid_sessions(year, round_number)
        if value not in valid:
            raise ValueError(
                f"Session '{value}' does not exist for round {round_number} "
                f"in {year}. Valid sessions: {list(valid)}."
            )
        return value


class RaceSessionParameters(SessionParameters):
    @field_validator("session")
    @classmethod
    def validate_race_session(cls, value, info: ValidationInfo):
        if value not in RACE_SESSIONS:
            raise ValueError(
                f"Session '{value}' is not supported here — only Race ('R') "
                f"and Sprint ('S') sessions are allowed."
            )
        return value
