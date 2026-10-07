import pandas as pd


def pick_fast_laps(data) -> pd.DataFrame:
    laps = data.laps
    fastest = laps.groupby("Driver")["LapTime"].transform("min")
    fast_laps = laps[laps["LapTime"] <= fastest * 1.07]
    return fast_laps
