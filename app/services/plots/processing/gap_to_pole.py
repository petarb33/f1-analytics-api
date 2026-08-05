import pandas as pd
from fastf1.core import Session


def get_qualifying_gaps(data: Session, drivers: list[str]) -> pd.DataFrame:
    quali_data = []

    for row in data.results.itertuples():
        if row.Abbreviation not in drivers:
            continue

        for phase in ("Q3", "Q2", "Q1"):
            time = getattr(row, phase)
            if pd.notna(time):
                quali_data.append(
                    {
                        "Driver": row.Abbreviation,
                        "LapTime": time.total_seconds(),
                        "Session": phase,
                    }
                )
                break

    df = pd.DataFrame(quali_data)
    df["GapToPole"] = (df["LapTime"] - df["LapTime"].min()).round(3)
    return df
