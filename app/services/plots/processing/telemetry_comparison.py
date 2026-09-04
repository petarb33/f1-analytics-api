import pandas as pd
import fastf1.utils
from fastf1.core import Session, Lap, Telemetry
from app.core.exceptions import AnalysisDataError
from app.services.constants import QUALIFYING_SESSIONS


def parse_lap_picks(raw_picks: list[str]) -> list[tuple[str, str]]:
    parsed = []
    for pick in raw_picks:
        driver, _, ident = pick.partition(":")
        if not driver or not ident:
            raise ValueError(
                f"Invalid pick '{pick}', expected 'DRIVER:lapnumber', "
                f"'DRIVER:fastest' or 'DRIVER:grid'"
            )
        parsed.append((driver, ident))
    return parsed


def resolve_grid_lap(session_data: Session, session: str, driver: str) -> Lap:
    if session not in QUALIFYING_SESSIONS:
        raise AnalysisDataError(
            "'grid' pick is only valid for qualifying-type sessions"
        )

    q1, q2, q3 = session_data.laps.split_qualifying_sessions()
    driver_number = session_data.get_driver(driver)["DriverNumber"]
    row = session_data.results.loc[driver_number]

    for segment, column in ((q3, "Q3"), (q2, "Q2"), (q1, "Q1")):
        if segment is not None and pd.notna(row[column]):
            lap = segment.pick_drivers(driver).pick_fastest()
            if lap is not None:
                return lap

    raise AnalysisDataError(f"No qualifying time found for driver '{driver}'")


def resolve_lap(session_data: Session, session: str, driver: str, ident: str) -> Lap:
    if ident == "fastest":
        lap = session_data.laps.pick_drivers(driver).pick_fastest()
    elif ident == "grid":
        lap = resolve_grid_lap(session_data, session, driver)
    else:
        try:
            lap_number = int(ident)
        except ValueError:
            raise ValueError(
                f"Invalid lap identifier '{ident}', expected a lap number, "
                f"'fastest' or 'grid'"
            )
        driver_laps = session_data.laps.pick_drivers(driver)
        matching = driver_laps[driver_laps["LapNumber"] == lap_number]
        lap = matching.pick_fastest(only_by_time=True) if not matching.empty else None

    if lap is None:
        raise AnalysisDataError(f"No lap found for '{driver}:{ident}'")
    return lap


def compute_delta(faster_lap: Lap, slower_lap: Lap) -> tuple[pd.Series, Telemetry]:
    delta, ref_tel, _ = fastf1.utils.delta_time(faster_lap, slower_lap)
    return delta, ref_tel
