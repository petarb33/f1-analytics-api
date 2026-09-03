from fastf1.core import Session
from app.core.exceptions import AnalysisDataError


def validate_drivers(data: Session, drivers: list[str]) -> None:
    valid_drivers = set(data.results["Abbreviation"])
    unknown = set(drivers) - valid_drivers
    if unknown:
        raise AnalysisDataError(
            f"Driver(s) not in this session: {', '.join(sorted(unknown))}"
        )
