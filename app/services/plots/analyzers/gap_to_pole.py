import matplotlib.patches as mpatches

from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from app.services.plots.core.base import BaseAnalysis
from app.services.fetch import get_drivers
from app.services.constants import SESSION_COLORS
from app.services.plots.processing.gap_to_pole import get_qualifying_gaps
from app.services.plots.plotting.plot_styles import (
    remove_spines,
    add_signature,
    set_ylabel,
    set_xlabel,
    color_ticks,
    color_axes,
    color_fig,
    add_figure_title,
    convert_time,
)
from app.models.image import save_image


class GapToPole(BaseAnalysis):
    def load(self):
        super().load()
        self._drivers = get_drivers(self.data)

    def process(self):
        self._quali_laps = get_qualifying_gaps(self.data, self._drivers)

    def plot(self):
        fig, ax = plt.subplots(figsize=(10, 8))
        remove_spines(ax)
        color_fig(fig)
        color_axes(ax)
        color_ticks(ax)
        set_xlabel(ax, "Time (s)")
        self._plot_gap_to_pole(ax)
        self._add_legend(ax)
        set_ylabel(ax)
        add_signature(fig)
        add_figure_title(
            fig, self.event_info, f"{self.event_info["session"]} - Gap To Pole"
        )
        _, image_bytes = save_image(fig, self.cache_key)

        return image_bytes

    def _plot_gap_to_pole(self, ax: Axes) -> None:
        """Draw each driver's gap-to-pole as a horizontal bar; pole gets its absolute lap time, others get +gap."""
        max_width = 0

        for row in self._quali_laps.itertuples():
            color = SESSION_COLORS.get(row.Session, "#888888")
            bar = ax.barh(row.Driver, row.GapToPole, color=color)
            max_width = max(bar[0].get_width(), max_width)

            if row.GapToPole == 0:
                ax.bar_label(
                    bar, labels=[convert_time(row.LapTime)], padding=3, color="white"
                )
            else:
                ax.bar_label(
                    bar, labels=[f"+{row.GapToPole:.3f}"], padding=3, color="white"
                )

        ax.invert_yaxis()
        ax.set_xlim(0, max_width * 1.1)

    def _add_legend(self, ax: Axes):
        legend_patches = [
            mpatches.Patch(color=SESSION_COLORS["Q1"], label="Q1 Lap"),
            mpatches.Patch(color=SESSION_COLORS["Q2"], label="Q2 Lap"),
            mpatches.Patch(color=SESSION_COLORS["Q3"], label="Q3 Lap"),
        ]

        ax.legend(
            handles=legend_patches,
            loc="upper right",
            labelcolor="white",
            facecolor="#292625",
        )
