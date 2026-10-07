from typing import Any

import pandas as pd
import numpy as np
from fastf1.core import Session
from numpy import dtype, ndarray
from app.services.plots.processing.race_pace import fill_missing_laps
from app.services.plots.processing.laps import pick_fast_laps


def get_lap_time_consistency(
    data: Session, drivers: list[str], mode: str = "race"
) -> ndarray[tuple[int, int], dtype[Any]]:
    """Build a driver-by-lap matrix of lap times for a consistency heatmap.

    Missing lap times are reconstructed from sector times when all three
    sectors are available.

    Args:
        data: A loaded FastF1 race session.
        drivers: Driver abbreviations to include. The row order of the
            result follows this list.
        mode: Which laps to keep:
            - ``"race"``: representative laps only. Leaves out laps with
              a pit entry or exit, lap 1, and Safety Car, VSC and
              red-flag laps.
            - ``"quick"``: laps selected by ``pick_fast_laps``.
            - ``"all"``: every lap.

    Returns:
        An array of shape ``(len(drivers), n_laps)`` holding lap times in
        seconds, where ``n_laps`` is the highest lap number in the session
        and column ``i`` is lap ``i + 1``. Cells without a lap time are
        ``NaN``.

    Raises:
        ValueError: If ``mode`` is not one of the values above.
    """
    if mode == "race":
        laps = data.laps.pick_wo_box()
    elif mode == "quick":
        laps = pick_fast_laps(data)
    elif mode == "all":
        laps = data.laps
    else:
        raise ValueError(f"Unknown mode: {mode!r}")

    laps = laps.pick_drivers(drivers).copy()
    laps["LapTime (s)"] = laps["LapTime"].dt.total_seconds()
    laps = fill_missing_laps(laps)
    laps = laps[laps["LapNumber"] != 1]

    if mode == "race":
        laps = laps[~laps["TrackStatus"].str.contains(r"[4567]", na=False)]

    laps = laps.dropna(subset=["LapNumber"])
    n_laps = int(data.laps["LapNumber"].max())
    matrix = np.full((len(drivers), n_laps), np.nan)

    row_of = {driver: i for i, driver in enumerate(drivers)}
    rows = laps["Driver"].map(row_of).to_numpy()
    cols = laps["LapNumber"].astype(int).to_numpy() - 1
    matrix[rows, cols] = laps["LapTime (s)"].to_numpy()

    return matrix


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
