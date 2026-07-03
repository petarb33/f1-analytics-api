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
    ax.set_xlabel(label, color=color)


def set_ylabel(ax: Axes, label="", color="white") -> None:
    ax.set_ylabel(label, color=color)


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


def color_axes(axs: Axes | list[Axes] | np.ndarray) -> None:
    for ax in _iter_axes(axs):
        ax.set_facecolor("#1e1c1b")


def _iter_axes(axs: Axes | list[Axes] | np.ndarray) -> Iterable[Axes]:
    return np.atleast_1d(axs).ravel()
