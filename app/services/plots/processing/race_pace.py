import pandas as pd
from fastf1.core import Session
from pandas import DataFrame
from app.core.logging import logger

EXCLUDED_STATUS = {"W", "N", "F", "E", "D"}
SC_VSC_RED = r"[4567]"
QUICKLAP_THRESHOLD = 1.07
MIN_LAPS = 5


def get_race_pace_boxplot(
    data: Session, group_by: str
) -> tuple[DataFrame, list[str], pd.Series | None]:
    """Prepare representative race laps for a race pace boxplot.

    Starts from laps without pit entry or exit, then excludes lap 1,
    drivers with an excluded classification (withdrawn, not classified,
    failed to qualify, excluded, disqualified), Safety Car, VSC and
    red-flag laps, and laps slower than 107% of the fastest remaining
    lap. Missing lap times are reconstructed from sector times when all
    three sectors are available. Groups with fewer than ``MIN_LAPS``
    laps are dropped so every group can be drawn as a box.

    Args:
        data: A loaded FastF1 race session.
        group_by: Laps column to group on, either ``"Driver"`` or ``"Team"``.

    Returns:
        A tuple of:
            - laps: Filtered laps with an added ``"LapTime (s)"`` column.
            - order: Group names sorted by mean lap time, fastest first,
              for use as the plot's x-axis order.
            - mean_laptimes: One row per group with its mean lap time in
              seconds, rounded to 3 decimals and sorted fastest first.
    """
    laps = data.laps.pick_wo_box()
    laps = laps.loc[laps["LapNumber"] != 1].copy()

    sector_sum = laps["Sector1Time"] + laps["Sector2Time"] + laps["Sector3Time"]
    filled = laps["LapTime"].isna() & sector_sum.notna()
    if filled.any():
        logger.info("lap_times_filled", count=int(filled.sum()))
    laps["LapTime (s)"] = laps["LapTime"].fillna(sector_sum).dt.total_seconds()

    laps = laps[~laps["TrackStatus"].str.contains(SC_VSC_RED, na=False)]
    laps = laps.dropna(subset=["LapTime (s)"])

    threshold = laps["LapTime (s)"].min() * QUICKLAP_THRESHOLD
    laps = laps[laps["LapTime (s)"] <= threshold]

    counts = laps.groupby(group_by)["LapTime (s)"].transform("size")
    laps = laps[counts >= MIN_LAPS]

    mean_laptimes = (
        laps.groupby(group_by, as_index=False)["LapTime (s)"]
        .mean()
        .round(3)
        .sort_values("LapTime (s)")
    )
    order = mean_laptimes[group_by].tolist()

    return laps, order, mean_laptimes


def fill_missing_laps(laps: pd.DataFrame) -> pd.DataFrame:
    for index, lap in laps.iterrows():
        if pd.isna(lap["LapTime"]):
            s1, s2, s3 = lap["Sector1Time"], lap["Sector2Time"], lap["Sector3Time"]
            if all(pd.notna([s1, s2, s3])):
                laptime = s1.total_seconds() + s2.total_seconds() + s3.total_seconds()
                laps.at[index, "LapTime (s)"] = laptime
                logger.info(
                    "lap_time_filled",
                    lap=lap["LapNumber"],
                    driver=lap["Driver"],
                    laptime=laptime,
                )
    return laps
