from fastf1.core import Session
import pandas as pd


def get_sector_times(
    data: Session, entities: list[str], group_by: str, display: str
) -> pd.DataFrame:
    rows = []
    for sector in ["Sector1Time", "Sector2Time", "Sector3Time"]:
        for entity in entities:
            laps = data.laps.loc[data.laps[group_by] == entity]
            time = laps[sector].min()
            rows.append(
                {
                    "entity": entity,
                    "sector": sector.replace("Time", "").replace("Sector", "Sector "),
                    "time": time.total_seconds(),
                }
            )

    df = pd.DataFrame(rows)

    if display == "delta":
        df["time"] = df.groupby("sector")["time"].transform(lambda x: x - x.min())

    df = df.sort_values("time").reset_index(drop=True)
    return df


def get_fastest_lap_sector_times(
    data: Session, entities: list[str], group_by: str, display: str
) -> pd.DataFrame:
    rows = []
    for entity in entities:
        laps = data.laps.loc[data.laps[group_by] == entity]
        fastest_lap = laps.pick_fastest()

        for sector in ["Sector1Time", "Sector2Time", "Sector3Time"]:
            rows.append(
                {
                    "entity": entity,
                    "sector": sector.replace("Time", "").replace("Sector", "Sector "),
                    "time": fastest_lap[sector].total_seconds(),
                }
            )

    df = pd.DataFrame(rows)
    if display == "delta":
        df["time"] = df.groupby("sector")["time"].transform(lambda x: x - x.min())

    df = df.sort_values("time").reset_index(drop=True)
    return df
