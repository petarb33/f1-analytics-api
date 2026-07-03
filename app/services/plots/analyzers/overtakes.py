import seaborn as sns
from matplotlib import pyplot as plt

from app.services.plots.plotting.plot_styles import (
    remove_spines,
    add_signature,
    set_ylabel,
    set_xlabel,
    color_ticks,
    color_axes,
    color_fig,
)
from app.services.plots.plotting.f1_colors import get_drivers_style
from app.services.plots.core.base import BaseAnalysis
from app.services.fetch import get_drivers
from app.models.image import save_image


class Overtakes(BaseAnalysis):
    def plot(self):
        fig, ax = plt.subplots()
        drivers = get_drivers(self.data)
        styles = get_drivers_style(self.data, drivers)
        self._plot_overtakes(ax, self.data, drivers, styles)
        remove_spines(ax)
        color_fig(fig)
        color_axes(ax)
        set_ylabel(ax)
        set_xlabel(ax, label="Lap Number")
        color_ticks(ax)
        add_signature(fig)
        save_image(fig, "test_2")

    def _plot_overtakes(self, ax, data, drivers, styles):
        for driver in drivers:
            driver_laps = data.laps.pick_drivers(driver)

            if driver_laps.empty:
                continue

            abb = driver_laps["Driver"].iloc[0]

            sns.lineplot(
                data=driver_laps,
                x="LapNumber",
                y="Position",
                label=abb,
                ax=ax,
                **styles[driver],
            )

        ax.invert_yaxis()
