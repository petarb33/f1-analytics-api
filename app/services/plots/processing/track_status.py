from fastf1.core import Session


def get_track_status_laps_per_driver(data: Session) -> dict[str, dict[str, set[int]]]:
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
