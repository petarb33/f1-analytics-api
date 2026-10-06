from fastf1.core import Session
import pandas as pd


def get_sector_times(
    data: Session, entities: list[str], group_by: str, display: str
) -> pd.DataFrame:
    """Get each entity's best time in each sector, across all laps.

    Each sector is taken independently, so an entity's three best
    sectors may come from different laps (their "theoretical" best lap).
    Entities with no recorded time in a sector are left out of that
    sector.

    Args:
        data: A loaded FastF1 session.
        entities: Drivers or teams to include.
        group_by: Laps column the entities belong to, either ``"Driver"``
            or ``"Team"``.
        display: ``"absolute"`` for sector times in seconds, or
            ``"delta"`` for the gap in seconds to the fastest entity in
            each sector.

    Returns:
        One row per entity per sector, sorted by time, with columns:
            - entity: Driver or team name.
            - sector: ``"Sector 1"``, ``"Sector 2"`` or ``"Sector 3"``.
            - time: Sector time or delta, in seconds.
            - tyre: Compound used on the lap where the best sector was set.
    """
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
    """Get the sector times from each entity's fastest lap.

    Unlike ``get_sector_times``, all three sectors come from the same
    lap, so they add up to the entity's fastest lap time. For teams,
    this is the fastest lap set by either driver. Entities without a
    valid fastest lap are left out.

    Args:
        data: A loaded FastF1 session.
        entities: Drivers or teams to include.
        group_by: Laps column the entities belong to, either ``"Driver"``
            or ``"Team"``.
        display: ``"absolute"`` for sector times in seconds, or
            ``"delta"`` for the gap in seconds to the fastest entity in
            each sector.

    Returns:
        One row per entity per sector, sorted by time, with columns:
            - entity: Driver or team name.
            - sector: ``"Sector 1"``, ``"Sector 2"`` or ``"Sector 3"``.
            - time: Sector time or delta, in seconds.
            - tyre: Compound used on the fastest lap.
    """
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
