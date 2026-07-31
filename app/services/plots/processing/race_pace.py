import pandas as pd
from fastf1.core import Session
from pandas import DataFrame


def get_race_pace_boxplot(
    data: Session, group_by: str
) -> tuple[DataFrame, list[str], pd.Series | None]:
    laps = data.laps.pick_wo_box()

    excluded_status = {"W", "N", "F", "E"}
    race_results = data.results["ClassifiedPosition"]
    race_results = race_results[~race_results.isin(excluded_status)]
    # TO CHECK

    transformed_laps = laps.copy()
    transformed_laps["LapTime (s)"] = transformed_laps["LapTime"].dt.total_seconds()
    transformed_laps = transformed_laps.loc[transformed_laps["LapNumber"] != 1]

    transformed_laps = fill_missing_laps(transformed_laps)

    transformed_laps = transformed_laps[
        ~transformed_laps["TrackStatus"].str.contains(r"[4567]", na=False)
    ]

    order = (
        transformed_laps.groupby(group_by)["LapTime (s)"]
        .mean()
        .sort_values()
        .index.tolist()
    )

    mean_laptimes = (
        transformed_laps.groupby(group_by, as_index=False)["LapTime (s)"]
        .mean()
        .round(3)
        .sort_values(by="LapTime (s)")
    )

    return transformed_laps, order, mean_laptimes


def fill_missing_laps(laps: pd.DataFrame) -> pd.DataFrame:
    for index, lap in laps.iterrows():
        if pd.isna(lap["LapTime"]):
            s1, s2, s3 = lap["Sector1Time"], lap["Sector2Time"], lap["Sector3Time"]
            if all(pd.notna([s1, s2, s3])):
                laptime = s1.total_seconds() + s2.total_seconds() + s3.total_seconds()
                laps.at[index, "LapTime (s)"] = laptime
                print(
                    f"At Lap {lap['LapNumber']} for {lap['Driver']} "
                    f"changed NaN to {laptime:.3f}"
                )
    return laps
