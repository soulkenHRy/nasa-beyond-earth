"""Chart helpers for the simple charts (charts/Knn_*.png, used by FINDINGS.md).

Same colours as every other chart in the project (helpers.py), but:
  - bigger text,
  - plain numbers on the axes (1,000 not 1K, never 1e4),
  - a "1, 10, 100, 1,000" axis when a log scale can't be avoided (each step is 10 times the last),
  - arrows with short labels that point at the thing to look at.
Every number written on a chart must come from code in the notebook that draws it.

Usage in a notebook:
    import simple_charts as kc
    kc.plain_style()
    fig, ax = plt.subplots(figsize=(11, 6))
    ... draw ...
    kc.point_at(ax, (2.50, 8659), f"Empty lane: only {n0(8659)}", (2.2, 30000))
    kc.titles(fig, "The asteroid belt has empty lanes", "Each bar counts the asteroids in one thin slice of distance.",
              hp.caption(rows_used, skipped, why, "numbers/K01_empty_lanes.csv"))
    kc.save(fig, "K01_empty_lanes")
"""
from __future__ import annotations

import matplotlib as mpl
import numpy as np
from matplotlib.ticker import FixedLocator, FuncFormatter, NullFormatter, NullLocator

import helpers as hp

TITLE, SUBTITLE, CAPTION = 17, 12.5, 9.5     # text sizes for title, "how to read it" line, small caption
MAIN = hp.SERIES[0]        # blue: what we counted
HIGHLIGHT = hp.SERIES[1]   # orange: the thing to look at
OTHER = hp.GRAY            # gray: everything else


def plain_style() -> None:
    """The project's chart look, with big text."""
    hp.chart_style()
    mpl.rcParams.update({
        "font.size": 12.5, "axes.labelsize": 13, "axes.labelcolor": hp.INK,
        "xtick.labelsize": 12, "ytick.labelsize": 12, "legend.fontsize": 12, "axes.titlesize": 13.5,
    })


def plain(v, _pos=None) -> str:
    """A plain axis number: 12,000 / 2.5 / 0.25 / 0.001 (no 12K, no 1e4)."""
    v = float(v)
    if v == 0:
        return "0"
    if float(v).is_integer():
        return f"{v:,.0f}"
    if abs(v) >= 1:
        return f"{v:,.2f}".rstrip("0").rstrip(".")
    digits = max(2, -int(np.floor(np.log10(abs(v)))) + 1)
    return f"{v:.{digits}f}".rstrip("0").rstrip(".")


def plain_axis(ax, which: str = "y") -> None:
    """Use plain numbers on one axis ('x' or 'y')."""
    (ax.yaxis if which == "y" else ax.xaxis).set_major_formatter(FuncFormatter(plain))


def tens_axis(ax, which: str = "y", lo: float | None = None, hi: float | None = None) -> None:
    """A log axis labelled 1, 10, 100, 1,000 ... (each step is 10 times the last). Call after drawing."""
    (ax.set_yscale if which == "y" else ax.set_xscale)("log")
    axis = ax.yaxis if which == "y" else ax.xaxis
    lim = ax.get_ylim() if which == "y" else ax.get_xlim()
    lo, hi = lo or lim[0], hi or lim[1]
    ticks = [10.0 ** k for k in range(int(np.floor(np.log10(lo))), int(np.ceil(np.log10(hi))) + 1)]
    axis.set_major_locator(FixedLocator(ticks))
    axis.set_major_formatter(FuncFormatter(plain))
    axis.set_minor_locator(NullLocator())
    axis.set_minor_formatter(NullFormatter())
    (ax.set_ylim if which == "y" else ax.set_xlim)(lo, hi)


def point_at(ax, xy, text: str, xytext, *, coords: str = "data", ha: str = "center", va: str = "center",
             color: str | None = None, fontsize: float = 12):
    """An arrow from a short label (at xytext) to the thing to look at (at xy).
    coords='data' puts the label in data units; 'offset points' puts it that many points away from xy."""
    return ax.annotate(
        text, xy=xy, xytext=xytext, textcoords=coords, ha=ha, va=va, fontsize=fontsize,
        color=color or hp.INK, fontweight="bold", zorder=10,
        bbox=dict(boxstyle="round,pad=0.35", fc="white", ec=hp.AXIS, lw=0.8),
        arrowprops=dict(arrowstyle="-|>", color=hp.INK_2, lw=1.4, shrinkA=2, shrinkB=4, mutation_scale=14),
    )


def label(ax, x, y, text: str, *, color: str | None = None, ha: str = "left", va: str = "center",
          fontsize: float = 12, bold: bool = False, box: bool = False, transform=None):
    """A label without an arrow (for naming a line, a bar or an area directly)."""
    kw = {"bbox": dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.85)} if box else {}
    if transform is not None:
        kw["transform"] = transform
    return ax.text(x, y, text, color=color or hp.INK, ha=ha, va=va, fontsize=fontsize,
                   fontweight="bold" if bold else "normal", zorder=10, **kw)


def titles(fig, title: str, how_to_read: str, caption: str = "") -> None:
    """Big title (the finding in plain words), a 'how to read it' line, and the small caption."""
    hp.add_titles(fig, title, how_to_read, caption, sizes=(TITLE, SUBTITLE, CAPTION))


def save(fig, name: str) -> str:
    """Save as charts/<name>.png and return the project-relative path."""
    return hp.save_chart(fig, name, dpi=150)
