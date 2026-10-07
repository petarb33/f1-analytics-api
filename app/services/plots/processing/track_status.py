from fastf1.core import Session


def get_track_status_laps_per_driver(data: Session) -> dict[str, dict[str, set[int]]]:
    """Get the laps each driver completed under neutralised track conditions.

    A lap is assigned to a condition when its ``TrackStatus`` contains
    one of that condition's status codes: ``"6"`` or ``"7"`` for Virtual
    Safety Car, ``"4"`` for Safety Car and ``"5"`` for red flag. A lap
    with several codes appears under every matching condition. Laps
    without a track status are skipped.

    Args:
        data: A loaded FastF1 session (Race or Sprint Race).

    Returns:
        A mapping of driver abbreviation to a dict with the keys
        ``"VSC"``, ``"SC"`` and ``"RF"``, each holding the set of that
        driver's lap numbers affected by the condition. Every driver has
        all three keys, with an empty set where no lap was affected.
    """
    codes = {"VSC": ("6", "7"), "SC": ("4",), "RF": ("5",)}
    result: dict[str, dict[str, set[int]]] = {}

    for driver in data.laps["Driver"].unique():
        driver_laps = data.laps.loc[data.laps["Driver"] == driver]
        driver_result = {label: set() for label in codes}

        for _, lap in driver_laps.iterrows():
            status = lap["TrackStatus"]
            if not isinstance(status, str):
                continue

            for label, lap_codes in codes.items():
                if any(code in status for code in lap_codes):
                    driver_result[label].add(int(lap["LapNumber"]))

        result[driver] = driver_result

    return result
