from matplotlib.figure import Figure
from matplotlib.axes import Axes
from collections.abc import Iterable
import pandas as pd
import numpy as np


def add_signature(fig: Figure, x: float = 0.9, y: float = 0.05) -> None:
    fig.text(
        x,
        y,
        "Petar B.",
        color="white",
        fontsize=10,
        alpha=0.7,
    )


def set_xlabel(ax: Axes, label="", color="white") -> None:
    ax.set_xlabel(label, color=color, labelpad=5)


def set_ylabel(ax: Axes, label="", color="white") -> None:
    ax.set_ylabel(label, color=color, labelpad=5)


def set_yticks(ax: Axes, ticks):
    ax.set_yticks(ticks)


def color_ticks(ax: Axes, color="white") -> None:
    ax.tick_params(color=color, axis="both", labelcolor=color)


def set_ylim(
    df: pd.DataFrame, ax: Axes, stat: str, margin_percentage: float = 0.2
) -> None:
    min_value = df[stat].min()
    max_value = df[stat].max()
    margin = (max_value - min_value) * margin_percentage
    ax.set_ylim(min_value - margin, max_value + margin)


def color_fig(fig: Figure) -> None:
    fig.patch.set_facecolor("#292625")


def remove_spines(axs: Axes | list[Axes] | np.ndarray) -> None:
    for ax in _iter_axes(axs):
        for side in ("bottom", "top", "left", "right"):
            ax.spines[side].set_visible(False)


def add_figure_title(
    fig: Figure,
    event_info: dict[str, str | int],
    desc: str | None = None,
    y: float | None = 0.96,
) -> None:
    title = (
        f'Round {event_info['round_number']} - '
        f'{event_info['grand_prix']} {event_info['year']}\n'
    )
    if desc:
        title += f"{desc}"
    fig.suptitle(title, color="white", y=y)


def add_ax_title(ax: Axes, title: str) -> None:
    ax.set_title(title, color="white")


def color_axes(axs: Axes | list[Axes] | np.ndarray) -> None:
    for ax in _iter_axes(axs):
        ax.set_facecolor("#1e1c1b")


def set_grid_lines(axs: Axes | list[Axes] | np.ndarray) -> None:
    for ax in _iter_axes(axs):
        ax.grid(visible=True, which="major", axis="y", ls="--", alpha=0.5)
        ax.set_axisbelow(True)


def _iter_axes(axs: Axes | list[Axes] | np.ndarray) -> Iterable[Axes]:
    return np.atleast_1d(axs).ravel()


def move_legend(ax: Axes, fontsize: int = 11):
    ax.legend(
        bbox_to_anchor=(1.025, 1),
        loc="upper left",
        borderaxespad=0,
        fontsize=fontsize,
    )
