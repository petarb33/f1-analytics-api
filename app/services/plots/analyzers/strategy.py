from matplotlib import pyplot as plt
from matplotlib.axes import Axes

from app.services.plots.core.base import BaseAnalysis
from app.services.plots.processing.strategy import get_stints
from app.services.fetch import get_drivers
from app.services.plots.plotting.plot_styles import (
    remove_spines,
    add_signature,
    set_ylabel,
    set_xlabel,
    color_ticks,
    color_axes,
    color_fig,
    add_ax_title,
    add_figure_title,
)
from app.models.image import save_image

import fastf1


class Strategy(BaseAnalysis):
    def plot(self):
        fig, ax = plt.subplots(figsize=(10, 8))
        color_fig(fig)
        color_axes(ax)
        remove_spines(ax)
        set_xlabel(ax, label="Lap Number")
        set_ylabel(ax)
        color_ticks(ax)
        self._plot_stints(ax=ax)
        add_signature(fig)
        add_figure_title(fig, self.event_info)
        add_ax_title(ax, "Race Strategy")
        _, image_bytes = save_image(fig, self.cache_key)
        return image_bytes

    def _plot_stints(self, ax: Axes):
        for driver in self._drivers:
            driver_stints = self.stints.loc[self.stints["Driver"] == driver]

            prev_stint_end = 0
            for idx, row in driver_stints.iterrows():
                compound_color = fastf1.plotting.get_compound_color(
                    row["Compound"], session=self.data
                )

                ax.barh(
                    y=driver,
                    width=row["StintLength"],
                    left=prev_stint_end,
                    color=compound_color,
                    edgecolor="black",
                    fill=True,
                )

                prev_stint_end += row["StintLength"]

        ax.invert_yaxis()

    def load(self):
        super().load()
        self._drivers = get_drivers(self.data)

    def process(self):
        self.stints = get_stints(self.data)
