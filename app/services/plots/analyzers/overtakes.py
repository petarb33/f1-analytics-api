import fastf1
import fastf1.plotting
import seaborn as sns
from matplotlib import pyplot as plt

from app.services.plots.core.base import BaseAnalysis


class Overtakes(BaseAnalysis):
    def plot(self):
        plot_overtakes(self.data)
        plt.show()


def plot_overtakes(data):
    fig, ax = plt.subplots()

    for driver in data.drivers:
        driver_laps = data.laps.pick_drivers(driver)

        if driver_laps.empty:
            continue

        abb = driver_laps["Driver"].iloc[0]

        style = fastf1.plotting.get_driver_style(
            identifier=abb, style=["color", "linestyle"], session=data
        )

        sns.lineplot(
            data=driver_laps, x="LapNumber", y="Position", label=abb, ax=ax, **style
        )

    ax.invert_yaxis()
