import numpy as np
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from app.services.fetch import get_drivers
from app.services.plots.core.base import BaseAnalysis
from app.models.image import save_image
from app.services.plots.plotting.plot_styles import (
    remove_spines,
    add_signature,
    set_ylabel,
    set_xlabel,
    color_axes,
    color_fig,
    add_figure_title,
    color_ticks,
)
from app.services.plots.processing.lap_time_heatmap import (
    get_lap_time_consistency,
    order_by_finishing_position,
    validate_drivers,
)


class LapTimeHeatmap(BaseAnalysis):
    def __init__(self, year, round_number, session, drivers=None, mode="race"):
        super().__init__(year, round_number, session)
        self.drivers_to_analyze = drivers
        self.mode = mode

    def load(self):
        super().load()
        if self.drivers_to_analyze:
            validate_drivers(self.data, self.drivers_to_analyze)
        else:
            self.drivers_to_analyze = get_drivers(self.data)
        self.drivers_to_analyze = order_by_finishing_position(
            self.data, self.drivers_to_analyze
        )

    def process(self):
        self._lap_time_matrix = get_lap_time_consistency(
            self.data, self.drivers_to_analyze, self.mode
        )

    @property
    def cache_key(self) -> str:
        drivers_key = (
            "_".join(sorted(self.drivers_to_analyze))
            if self.drivers_to_analyze
            else "all"
        )
        return f"{super().cache_key}_{self.mode}_{drivers_key}"

    def plot(self):
        fig, ax = plt.subplots(figsize=(16, 10))
        remove_spines(ax)
        color_fig(fig)
        color_axes(ax)
        color_ticks(ax)
        self._create_heatmap(ax)
        set_xlabel(ax, "Lap Number")
        set_ylabel(ax)
        add_signature(fig, x=0.8)
        add_figure_title(
            fig,
            self.event_info,
            f"Lap Time Consistency - {'All Laps' if self.mode == 'all' else 'Race Laps Only'}",
        )
        _, image_bytes = save_image(fig, self.cache_key)
        return image_bytes

    def _create_heatmap(self, ax: Axes):
        max_laps = self.data.total_laps
        im = ax.imshow(self._lap_time_matrix, cmap="RdYlGn_r", aspect="auto")
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label("Lap Time (s)", rotation=270, labelpad=15, color="white")
        color_ticks(cbar.ax)
        tick_labels = [1] + list(range(5, max_laps + 1, 5))
        tick_positions = [label - 1 for label in tick_labels]
        ax.set_xticks(tick_positions)
        ax.set_xticklabels(tick_labels)
        ax.set_yticks(np.arange(len(self.drivers_to_analyze)))
        ax.set_yticklabels(self.drivers_to_analyze)
