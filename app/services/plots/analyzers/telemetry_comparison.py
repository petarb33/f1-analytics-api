from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.ticker import MaxNLocator
from app.services.plots.core.base import BaseAnalysis
from app.services.plots.processing.telemetry_comparison import (
    parse_lap_picks,
    resolve_lap,
    compute_delta,
)
from app.services.plots.processing.validation import validate_drivers
from app.services.plots.plotting.f1_colors import get_drivers_style
from app.services.plots.plotting.plot_styles import (
    remove_spines,
    add_signature,
    set_ylabel,
    set_xlabel,
    color_ticks,
    color_axes,
    color_fig,
    set_grid_lines,
    add_figure_title,
    move_legend,
)
from app.models.image import save_image
from functools import partial

_LINESTYLES = ("solid", "dashed", "dotted", "dashdot")

_PANEL_HEIGHTS = {
    "speed": 1.0,
    "delta": 0.8,
    "throttle": 0.6,
    "brake": 0.2,
    "gear": 0.4,
}


class TelemetryComparison(BaseAnalysis):
    def __init__(self, year, round_number, session, picks: list[str]):
        super().__init__(year, round_number, session)
        self.raw_picks = picks

    def load(self):
        super().load()
        parsed = parse_lap_picks(self.raw_picks)
        validate_drivers(self.data, [driver for driver, _ in parsed])
        self._picks = [
            (driver, ident, resolve_lap(self.data, self.session, driver, ident))
            for driver, ident in parsed
        ]

    def process(self):
        self._telemetry = [
            (driver, ident, lap.get_car_data().add_distance())
            for driver, ident, lap in self._picks
        ]

        self._show_delta = len(self._picks) == 2
        if self._show_delta:
            self._process_delta()

    def _process_delta(self):
        (driver_a, ident_a, lap_a), (driver_b, ident_b, lap_b) = self._picks
        if lap_a["LapTime"] <= lap_b["LapTime"]:
            faster, slower = (driver_a, ident_a, lap_a), (driver_b, ident_b, lap_b)
        else:
            faster, slower = (driver_b, ident_b, lap_b), (driver_a, ident_a, lap_a)

        self._faster_pick = faster
        self._slower_pick = slower
        self._delta, self._delta_ref_tel = compute_delta(faster[2], slower[2])

    @property
    def cache_key(self) -> str:
        picks_key = "_".join(sorted(self.raw_picks))
        return f"{super().cache_key}_{picks_key}"

    def plot(self):
        panels = ["speed"]
        if self._show_delta:
            panels.append("delta")
        panels += ["throttle", "brake", "gear"]

        height_ratios = [_PANEL_HEIGHTS[p] for p in panels]

        fig, axes = plt.subplots(
            nrows=len(panels),
            ncols=1,
            sharex=True,
            figsize=(12, 3 * sum(height_ratios)),
            gridspec_kw={"height_ratios": height_ratios},
        )

        remove_spines(axes)
        color_fig(fig)
        color_axes(axes)
        set_grid_lines(axes)
        for ax in axes:
            color_ticks(ax)

        drivers = dict.fromkeys(driver for driver, _, _ in self._telemetry)
        self._driver_styles = get_drivers_style(self.data, list(drivers))
        self._pick_linestyles = self._assign_linestyles()

        panel_plotters = {
            "speed": (
                lambda ax: self._plot_channel(ax, "Speed", "line", label=True),
                "Speed (km/h)",
            ),
            "delta": (self._plot_delta, "Time Delta (s)"),
            "throttle": (
                lambda ax: self._plot_channel(ax, "Throttle", "line"),
                "Throttle (%)",
            ),
            "brake": (
                lambda ax: self._plot_channel(ax, "Brake", "step", cast=int),
                "Brake",
            ),
            "gear": (lambda ax: self._plot_channel(ax, "nGear", "step"), "Gear"),
        }

        for ax, panel in zip(axes, panels):
            plotter, ylabel = panel_plotters[panel]
            plotter(ax)
            set_ylabel(ax, ylabel)
            if panel == "brake":
                ax.set_yticks([0, 1])
                ax.set_yticklabels(["OFF", "ON"])
            elif panel == "gear":
                ax.yaxis.set_major_locator(MaxNLocator(integer=True))
                ax.tick_params(axis="y", labelsize=6)

        set_xlabel(axes[-1], "Distance (m)")
        move_legend(axes[0], 10)
        add_signature(fig)
        add_figure_title(fig, self.event_info, "Telemetry Comparison")
        _, image_bytes = save_image(fig, self.cache_key)
        return image_bytes

    def _assign_linestyles(self) -> list[str]:
        seen_per_driver: dict[str, int] = {}
        styles = []
        for driver, _, _ in self._telemetry:
            base = self._driver_styles[driver]["linestyle"]
            offset = seen_per_driver.get(driver, 0)
            seen_per_driver[driver] = offset + 1
            base_index = _LINESTYLES.index(base)
            styles.append(_LINESTYLES[(base_index + offset) % len(_LINESTYLES)])
        return styles

    def _plot_channel(self, ax: Axes, col: str, kind: str, cast=None, label=False):
        for (driver, ident, telemetry), linestyle in zip(
            self._telemetry, self._pick_linestyles
        ):
            y = telemetry[col]
            if cast is not None:
                y = y.astype(cast)
            draw = ax.plot if kind == "line" else partial(ax.step, where="post")
            draw(
                telemetry["Distance"],
                y,
                color=self._driver_styles[driver]["color"],
                linestyle=linestyle,
                **({"label": f"{driver} ({ident})"} if label else {}),
            )

    def _plot_delta(self, ax: Axes):
        faster_driver, faster_ident, _ = self._faster_pick
        slower_driver, slower_ident, _ = self._slower_pick
        ax.axhline(0, color="white", linestyle="dashed", alpha=0.6)
        ax.plot(
            self._delta_ref_tel["Distance"],
            self._delta,
            color=self._driver_styles[slower_driver]["color"],
            label=(
                f"{slower_driver} ({slower_ident}) vs "
                f"{faster_driver} ({faster_ident})"
            ),
        )
