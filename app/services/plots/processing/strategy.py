from fastf1.core import Session

import pandas as pd


def get_stints(data: Session) -> pd.DataFrame:
    stints = data.laps[["Driver", "Stint", "Compound", "LapNumber"]]

    stints = (
        stints.groupby(["Driver", "Stint", "Compound"])
        .count()
        .reset_index()
        .rename(columns={"LapNumber": "StintLength"})
    )

    return stints
