import pandas as pd
from fastf1.core import Session
from app.core.exceptions import AnalysisDataError


def get_qualifying_gaps(data: Session, drivers: list[str]) -> pd.DataFrame:
    """Get each driver's qualifying time and gap to the fastest time.

    Each driver is represented by their time from the last phase they
    set a time in: Q3 if they reached it, otherwise Q2, otherwise Q1.
    Drivers with no time in any phase are left out.

    Args:
        data: A loaded FastF1 qualifying session.
        drivers: Driver abbreviations to include.

    Returns:
        One row per driver, in classification order, with columns:
            - Driver: Driver abbreviation.
            - LapTime: Lap time in seconds.
            - Session: Phase the time was set in (``"Q1"``, ``"Q2"`` or
              ``"Q3"``).
            - GapToPole: Gap in seconds to the fastest ``LapTime`` among
              the included drivers, rounded to 3 decimals.

    Raises:
        AnalysisDataError: If none of the requested drivers set a time.
    """
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

    if not quali_data:
        raise AnalysisDataError(
            "No qualifying lap times recorded for the requested drivers/session."
        )

    df = pd.DataFrame(quali_data)
    pole = data.results.loc[data.results["Position"] == 1, "Q3"]
    if pole.empty or pd.isna(pole.iloc[0]):
        raise AnalysisDataError("No pole time recorded for this session.")
    df["GapToPole"] = (df["LapTime"] - pole.iloc[0].total_seconds()).round(3)
    return df
