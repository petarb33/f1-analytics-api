from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.patches import Rectangle

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
from app.services.constants import CONDITION_COLORS
from app.services.plots.processing.track_status import get_track_status_laps_per_driver

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
        self._mark_track_status(ax=ax)
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
                try:
                    compound_color = fastf1.plotting.get_compound_color(
                        row["Compound"], session=self.data
                    )
                except ValueError:
                    compound_color = "grey"

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

    def _mark_track_status(self, ax):
        laps_by_driver = get_track_status_laps_per_driver(
            self.data
        )  # {driver: {label: set(laps)}}

        for i, driver in enumerate(self._drivers):
            for label, lap_numbers in laps_by_driver.get(driver, {}).items():
                for lap in lap_numbers:
                    ax.add_patch(
                        Rectangle(
                            (lap - 0.5, i - 0.4),
                            width=1,
                            height=0.8,
                            color=CONDITION_COLORS[label],
                            alpha=0.7,
                            zorder=2,
                        )
                    )

    def load(self):
        super().load()
        self._drivers = get_drivers(self.data)

    def process(self):
        self.stints = get_stints(self.data)
