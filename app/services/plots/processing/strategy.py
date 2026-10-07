from fastf1.core import Session

import pandas as pd


def get_stints(data: Session) -> pd.DataFrame:
    """Get the length of every tyre stint for each driver.

    Args:
        data: A loaded FastF1 session.

    Returns:
        One row per driver per stint per compound, with columns:
            - Driver: Driver abbreviation.
            - Stint: Stint number.
            - Compound: Tyre compound used in the stint.
            - StintLength: Number of laps completed in the stint.
    """
    stints = data.laps[["Driver", "Stint", "Compound", "LapNumber"]]

    stints = (
        stints.groupby(["Driver", "Stint", "Compound"])
        .count()
        .reset_index()
        .rename(columns={"LapNumber": "StintLength"})
    )

    return stints
