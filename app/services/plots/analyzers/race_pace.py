import matplotlib.pyplot as plt
from abc import abstractmethod

from matplotlib.axes import Axes
from app.services.plots.core.base import BaseAnalysis
from app.services.plots.plotting.f1_colors import get_teams_colors, get_drivers_colors
from app.services.plots.processing.race_pace import get_race_pace_boxplot
from app.services.fetch import get_teams, get_drivers
from app.services.plots.plotting.plot_styles import (
    remove_spines,
    add_signature,
    set_ylabel,
    set_xlabel,
    color_ticks,
    color_axes,
    color_fig,
    add_figure_title,
)
from app.models.image import save_image


class RacePace(BaseAnalysis):
    @property
    @abstractmethod
    def entities(self) -> list[str]:
        """Drivers or teams to analyze."""
        pass

    @property
    @abstractmethod
    def group_by(self) -> str:
        """FastF1 laps column to filter on: 'Driver' or 'Team'."""
        pass

    @property
    @abstractmethod
    def colors(self) -> dict[str, str]:
        """Map of entity name -> hex color."""
        pass

    def process(self):
        self.race_pace_laps, self.order, self.mean_laptimes = get_race_pace_boxplot(
            self.data, self.group_by
        )

    def plot(self):
        fig, ax = plt.subplots(figsize=(10, 6))

        remove_spines(ax)
        color_fig(fig)
        color_axes(ax)
        color_ticks(ax)
        self._plot_pace(ax)
        set_ylabel(ax, "LapTime (s)")
        set_xlabel(ax)
        add_figure_title(fig, self.event_info, "Race Pace")
        add_signature(fig)
        _, image_bytes = save_image(fig, self.cache_key)
        return image_bytes

    def _plot_pace(self, ax: Axes):
        race_pace_data = [
            self.race_pace_laps.loc[
                self.race_pace_laps[self.group_by] == entity, "LapTime (s)"
            ].values
            for entity in self.order
        ]
        colors_in_order = [self.colors[entity] for entity in self.order]

        boxplot = ax.boxplot(
            x=race_pace_data,
            tick_labels=self.order,
            patch_artist=True,
            meanline=True,
            showmeans=True,
            meanprops={"color": "black", "linestyle": "--", "linewidth": 1},
            medianprops={"color": "black", "linestyle": "-", "linewidth": 1},
            boxprops={"color": "white", "linewidth": 1},
            whiskerprops={"color": "white", "linewidth": 1},
            capprops={"color": "white"},
            showfliers=False,
        )

        for patch, color in zip(boxplot["boxes"], colors_in_order):
            patch.set_facecolor(color)


class TeamsRacePace(RacePace):
    def load(self):
        super().load()
        self._teams = get_teams(self.data)
        self._colors = get_teams_colors(self.data)

    @property
    def entities(self) -> list[str]:
        return self._teams

    @property
    def colors(self) -> dict[str, str]:
        return self._colors

    @property
    def group_by(self) -> str:
        return "Team"


class DriversRacePace(RacePace):
    def load(self):
        super().load()
        self._drivers = get_drivers(self.data)
        self._colors = get_drivers_colors(self.data)

    @property
    def entities(self) -> list[str]:
        return self._drivers

    @property
    def colors(self) -> dict[str, str]:
        return self._colors

    @property
    def group_by(self) -> str:
        return "Driver"
