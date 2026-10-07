from typing import Any

import pandas as pd
import numpy as np
from fastf1.core import Session
from numpy import dtype, ndarray
from app.services.plots.processing.race_pace import fill_missing_laps


def get_lap_time_consistency(
    data: Session, drivers: list[str] | None = None, mode: str = "race"
) -> ndarray[tuple[int, int], dtype[Any]]:
    """Build a driver-by-lap matrix of lap times for a consistency heatmap.

    Missing lap times are reconstructed from sector times when all three
    sectors are available. In ``"race"`` mode only representative laps
    are kept: laps with a pit entry or exit, lap 1, and Safety Car, VSC
    and red-flag laps are left out.

    Args:
        data: A loaded FastF1 race session.
        drivers: Driver abbreviations to include. Must be provided; the
            row order of the result follows this list.
        mode: ``"race"`` to keep only representative laps, or ``"all"``
            to keep every lap.

    Returns:
        An array of shape ``(len(drivers), data.total_laps)`` holding lap
        times in seconds, where column ``i`` is lap ``i + 1``. Cells
        without a lap time are ``NaN``.
    """
    max_laps = data.total_laps
    lap_time_matrix = np.full((len(drivers), max_laps), np.nan)

    laps_source = data.laps.pick_wo_box() if mode == "race" else data.laps

    for idx, driver in enumerate(drivers):
        driver_laps = laps_source.pick_drivers(driver).copy()
        driver_laps["LapTime (s)"] = driver_laps["LapTime"].dt.total_seconds()
        driver_laps = fill_missing_laps(driver_laps)

        if mode == "race":
            driver_laps = driver_laps.loc[driver_laps["LapNumber"] != 1]
            driver_laps = driver_laps[
                ~driver_laps["TrackStatus"].str.contains(r"[4567]", na=False)
            ]

        for _, lap in driver_laps.iterrows():
            lap_num = int(lap["LapNumber"]) - 1
            if 0 <= lap_num < max_laps:
                lap_time_matrix[idx, lap_num] = lap["LapTime (s)"]

    return lap_time_matrix


def order_by_finishing_position(data: Session, drivers: list[str]) -> list[str]:
    """Sort drivers by their finishing position in the session.

    Drivers that are missing from the results or have no classified
    position are placed last, keeping their relative input order.

    Args:
        data: A loaded FastF1 session.
        drivers: Driver abbreviations to sort.

    Returns:
        The driver abbreviations ordered from first to last place.
    """
    finishing_order = data.results.set_index("Abbreviation")["Position"]

    def position_key(driver: str) -> float:
        """Return the driver's position, or infinity if they have none."""
        pos = finishing_order.get(driver, float("inf"))
        return float("inf") if pd.isna(pos) else pos

    return sorted(drivers, key=position_key)
