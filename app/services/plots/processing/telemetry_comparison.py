import pandas as pd
import fastf1.utils
from fastf1.core import Session, Lap, Telemetry
from app.core.exceptions import AnalysisDataError
from app.services.constants import QUALIFYING_SESSIONS


def parse_lap_picks(raw_picks: list[str]) -> list[tuple[str, str]]:
    """Split raw lap picks into driver and lap identifier pairs.

    Args:
        raw_picks: Picks in the form ``"DRIVER:ident"``, where ``ident``
            is a lap number, ``"fastest"`` or ``"grid"``.

    Returns:
        One ``(driver, ident)`` tuple per pick, in input order. The
        identifier is not validated here; see ``resolve_lap``.

    Raises:
        ValueError: If a pick has no ``":"`` separator, or an empty
            driver or identifier.
    """
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
    """Get the qualifying lap that set a driver's grid time.

    The lap is the driver's fastest lap from the last qualifying segment
    they set a time in: Q3 if they reached it, otherwise Q2, otherwise
    Q1.

    Args:
        session_data: A loaded FastF1 qualifying session.
        session: Session identifier, used to check that the session is a
            qualifying-type session.
        driver: Driver abbreviation.

    Returns:
        The driver's fastest lap from their last qualifying segment.

    Raises:
        AnalysisDataError: If the session is not a qualifying-type
            session, or the driver set no qualifying time.
    """
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
    """Resolve a lap identifier to a driver's lap.

    Args:
        session_data: A loaded FastF1 session.
        session: Session identifier, needed to resolve ``"grid"`` picks.
        driver: Driver abbreviation.
        ident: ``"fastest"`` for the driver's fastest lap, ``"grid"`` for
            the lap that set their qualifying time, or a lap number.

    Returns:
        The matching lap.

    Raises:
        ValueError: If ``ident`` is not ``"fastest"``, ``"grid"`` or a
            lap number.
        AnalysisDataError: If no matching lap exists for the driver, or
            ``"grid"`` is used outside a qualifying-type session.
    """
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
    """Compute the time delta between two laps over the lap distance.

    Args:
        faster_lap: Lap used as the reference.
        slower_lap: Lap compared against the reference.

    Returns:
        A tuple of:
            - delta: Time gap in seconds of ``slower_lap`` to
              ``faster_lap`` at each reference telemetry sample.
            - ref_tel: Telemetry of ``faster_lap``, whose ``Distance``
              column the delta is aligned to.
    """
    delta, ref_tel, _ = fastf1.utils.delta_time(faster_lap, slower_lap)
    return delta, ref_tel
