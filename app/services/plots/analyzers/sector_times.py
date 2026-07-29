from abc import abstractmethod

from matplotlib import pyplot as plt
import seaborn as sns

from app.services.plots.core.base import BaseAnalysis
from app.services.fetch import get_drivers, get_teams
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
    set_ylim,
    set_grid_lines,
)
from app.services.plots.plotting.f1_colors import (
    get_drivers_colors,
    get_teams_colors,
    get_compound_colors,
)
from app.models.image import save_image
from app.services.plots.processing.sector_times import get_sector_times
from app.services.plots.processing.sector_times import get_fastest_lap_sector_times


class SectorTimes(BaseAnalysis):
    def __init__(
        self,
        year: int,
        round_number: int,
        session: str,
        display: str = "absolute",
        basis: str = "theoretical",
    ):
        super().__init__(year, round_number, session)
        self.display = display
        self.basis = basis

    @property
    @abstractmethod
    def entities(self) -> list[str]:
        """Drivers or teams to analyze."""
        pass

    @property
    @abstractmethod
    def colors(self) -> dict[str, str]:
        """Map of entity name -> hex color."""
        pass

    @property
    @abstractmethod
    def group_by(self) -> str:
        """FastF1 laps column to filter on: 'Driver' or 'Team'."""
        pass

    @property
    def cache_key(self) -> str:
        return f"{super().cache_key}_{self.display}_{self.basis}"

    def process(self):
        if self.basis == "theoretical":
            self.sector_times = get_sector_times(
                self.data, self.entities, self.group_by, self.display
            )
        else:
            self.sector_times = get_fastest_lap_sector_times(
                self.data, self.entities, self.group_by, self.display
            )

    def plot(self):
        fig, axs = plt.subplots(nrows=3, ncols=1, figsize=(10, 10))
        fig.subplots_adjust(hspace=0.5)
        compound_colors = get_compound_colors(self.data)

        remove_spines(axs)
        color_fig(fig)
        color_axes(axs)
        set_grid_lines(axs)
        add_signature(fig)

        for ax, (sector, group) in zip(
            axs, self.sector_times.groupby("sector", sort=False)
        ):
            sns.barplot(
                data=group,
                x="entity",
                y="time",
                hue="entity",
                legend=False,
                palette=self.colors,
                ax=ax,
            )

            for container in ax.containers:
                ax.bar_label(container, fontsize=7, color="white")

            for bar, tyre in zip(ax.patches, group["tyre"]):
                bar.set_edgecolor(compound_colors.get(tyre, "white"))
                bar.set_linewidth(1)

            set_ylim(group, ax, "time")
            add_ax_title(ax, title=sector)
            color_ticks(ax)
            set_xlabel(ax)
            set_ylabel(ax, label="Time (s)")

        title = (
            "Fastest Lap Sector Times"
            if self.basis == "fastest_lap"
            else "Fastest Sectors Comparison"
        )
        add_figure_title(fig, self.event_info, title, 0.95)
        _, image_bytes = save_image(fig, self.cache_key)
        return image_bytes


class DriverSectorTimes(SectorTimes):
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


class TeamSectorTimes(SectorTimes):
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
