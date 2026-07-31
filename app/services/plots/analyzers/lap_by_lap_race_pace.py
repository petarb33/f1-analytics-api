import seaborn as sns

from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from app.services.plots.core.base import BaseAnalysis
from app.services.fetch import get_drivers
from app.services.plots.processing.race_pace import get_race_pace_boxplot
from app.services.plots.plotting.f1_colors import get_drivers_style
from app.services.plots.plotting.plot_styles import (
    remove_spines,
    add_signature,
    set_ylabel,
    set_xlabel,
    color_ticks,
    color_axes,
    color_fig,
    add_figure_title,
    move_legend,
)
from app.models.image import save_image


class LapByLapRacePace(BaseAnalysis):
    def load(self):
        super().load()
        self._drivers = get_drivers(self.data)
        self._styles = get_drivers_style(self.data, self._drivers)

    def process(self):
        self._race_pace_laps, self.order, self.mean_laptimes = get_race_pace_boxplot(
            self.data, "Driver"
        )

    def plot(self):
        fig, ax = plt.subplots(figsize=(10, 6))
        remove_spines(ax)
        color_fig(fig)
        color_axes(ax)
        self._plot_laps(ax)
        add_signature(fig)
        set_ylabel(ax)
        set_xlabel(ax, "Lap Number")
        color_ticks(ax)
        add_figure_title(fig, self.event_info, "Lap By Lap Race Pace")
        move_legend(ax, 10)
        _, image_bytes = save_image(fig, self.cache_key)
        return image_bytes

    def _plot_laps(self, ax: Axes):
        for driver in self._drivers:
            driver_laps = self._race_pace_laps.loc[
                self._race_pace_laps["Driver"] == driver
            ]
            sns.lineplot(
                data=driver_laps,
                x="LapNumber",
                y="LapTime (s)",
                label=driver,
                ax=ax,
                **self._styles[driver],
            )
