from fastf1.core import Session
import pandas as pd


def get_sector_times(
    data: Session, entities: list[str], group_by: str, display: str
) -> pd.DataFrame:
    rows = []
    for sector in ["Sector1Time", "Sector2Time", "Sector3Time"]:
        for entity in entities:
            laps = data.laps.loc[data.laps[group_by] == entity]
            sector_times = laps[sector].dropna()
            if sector_times.empty:
                continue

            time = laps[sector].min()
            index = laps[sector].idxmin()
            rows.append(
                {
                    "entity": entity,
                    "sector": sector.replace("Time", "").replace("Sector", "Sector "),
                    "time": time.total_seconds(),
                    "tyre": laps.loc[index]["Compound"],
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

        if fastest_lap is None:
            continue

        for sector in ["Sector1Time", "Sector2Time", "Sector3Time"]:
            rows.append(
                {
                    "entity": entity,
                    "sector": sector.replace("Time", "").replace("Sector", "Sector "),
                    "time": fastest_lap[sector].total_seconds(),
                    "tyre": fastest_lap["Compound"],
                }
            )

    df = pd.DataFrame(rows)
    if display == "delta":
        df["time"] = df.groupby("sector")["time"].transform(lambda x: x - x.min())

    df = df.sort_values("time").reset_index(drop=True)
    return df
