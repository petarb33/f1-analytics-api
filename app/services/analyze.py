from app.services.plots.analyzers.overtakes import Overtakes
from app.services.plots.analyzers.sector_times import DriverSectorTimes, TeamSectorTimes
from app.services.plots.analyzers.strategy import Strategy
from app.services.plots.analyzers.race_pace import TeamsRacePace, DriversRacePace
from app.services.plots.analyzers.lap_by_lap_race_pace import LapByLapRacePace
from app.services.plots.analyzers.gap_to_pole import GapToPole

SECTOR_ANALYZERS = {
    "drivers": DriverSectorTimes,
    "teams": TeamSectorTimes,
}

PACE_ANALYZERS = {
    "drivers": DriversRacePace,
    "teams": TeamsRacePace,
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


def run_race_pace(year: int, round_number: int, session: str, group: str):
    analyzer_class = PACE_ANALYZERS[group]
    analyzer = analyzer_class(year=year, round_number=round_number, session=session)
    return analyzer.run()


def run_strategy(year: int, round_number: int, session: str):
    strategy = Strategy(year=year, round_number=round_number, session=session)
    return strategy.run()


def run_lap_by_lap_pace(year: int, round_number: int, session: str):
    pace = LapByLapRacePace(year=year, round_number=round_number, session=session)
    return pace.run()


def run_gap_to_pole(year: int, round_number: int, session: str):
    gap_to_pole = GapToPole(year=year, round_number=round_number, session=session)
    return gap_to_pole.run()
