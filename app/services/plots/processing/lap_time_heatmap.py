from typing import Any

import pandas as pd
import numpy as np
from fastf1.core import Session
from numpy import dtype, ndarray
from app.services.plots.processing.race_pace import fill_missing_laps


def get_lap_time_consistency(
    data: Session, drivers: list[str] | None = None, mode: str = "race"
) -> ndarray[tuple[int, int], dtype[Any]]:
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
    finishing_order = data.results.set_index("Abbreviation")["Position"]

    def position_key(driver: str) -> float:
        pos = finishing_order.get(driver, float("inf"))
        return float("inf") if pd.isna(pos) else pos

    return sorted(drivers, key=position_key)


def validate_drivers(data: Session, drivers: list[str]) -> None:
    valid_drivers = set(data.results["Abbreviation"])
    unknown = set(drivers) - valid_drivers
    if unknown:
        raise ValueError(f"Driver(s) not in this session: {', '.join(sorted(unknown))}")
