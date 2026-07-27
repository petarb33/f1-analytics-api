from app.services.plots.analyzers.overtakes import Overtakes
from app.services.plots.analyzers.sector_times import DriverSectorTimes, TeamSectorTimes

SECTOR_ANALYZERS = {
    "drivers": DriverSectorTimes,
    "teams": TeamSectorTimes,
}


def run_overtakes(year: int, round_number: int, session: str):
    overtakes = Overtakes(year=year, round_number=round_number, session=session)
    return overtakes.run()


def run_sector_analysis(
    year: int, round_number: int, session: str, group: str, display: str, basis: str
):
    analyzer_class = SECTOR_ANALYZERS[group]
    analyzer = analyzer_class(
        year=year,
        round_number=round_number,
        session=session,
        display=display,
        basis=basis,
    )
    return analyzer.run()
