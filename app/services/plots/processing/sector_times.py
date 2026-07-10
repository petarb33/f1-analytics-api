from fastf1.core import Session


def get_sector_times(data: Session, entities: list[str], group_by: str) -> dict:
    sector_times = {}
    for sector in ["Sector1Time", "Sector2Time", "Sector3Time"]:
        sector_times[sector] = {}
        for entity in entities:
            laps = data.laps.loc[data.laps[group_by] == entity]
            sector_times[sector][entity] = laps[sector].min().total_seconds()
    return sector_times
