"""Shared helpers for the NASA Beyond Earth notebooks and the Streamlit app.

- Where the data files are (found automatically, even inside the unzipped folder).
- How to read each file safely (the known traps are handled once, here): `read_csv`.
- A fast Parquet copy of each file in data_cache/ for the app: `load_parquet`.
- Saving charts to charts/ and the numbers behind them to numbers/.
- The running LOG: every chart's entry, a progress table, and parked edge cases. Stored in
  numbers/_log.json and drawn as LOG.md. Re-running a cell replaces its entry instead of adding a copy.
  A file lock makes this safe when several notebooks run at the same time.
"""
from __future__ import annotations

import fcntl
import json
import os
import re
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
CHARTS = PROJECT / "charts"
NUMBERS = PROJECT / "numbers"
CACHE = PROJECT / "data_cache"
LOG = PROJECT / "LOG.md"
LOG_JSON = NUMBERS / "_log.json"


def _find_data_dir() -> Path:
    """Find the 'NASA Beyond Earth' folder: directly in the project, or one folder down (unzipped)."""
    candidates = [PROJECT / "NASA Beyond Earth", *sorted(PROJECT.glob("*/NASA Beyond Earth"))]
    for p in candidates:
        if (p / "1_Asteroids_and_Comets").is_dir():
            return p
    # Not found: the paths below still point where the folder should go, and reading a file says what is missing.
    # The app runs without it (it reads numbers/, charts/ and animations/).
    return PROJECT / "NASA Beyond Earth"


DATA = _find_data_dir()
HAVE_DATA = (DATA / "1_Asteroids_and_Comets").is_dir()
README = DATA / "README.md"
FILES = {
    "asteroids": DATA / "1_Asteroids_and_Comets" / "jpl_small_bodies_asteroids_comets.csv",
    "close_approaches": DATA / "1_Asteroids_and_Comets" / "extras_close_approaches_1900-2200.csv",
    "fireballs": DATA / "1_Asteroids_and_Comets" / "extras_fireballs.csv",
    "space_weather": DATA / "2_Space_Weather" / "nasa_omni_solar_wind_storms_5min_2010-2026.csv",
    "stars": DATA / "3_Stars_and_Exoplanets" / "gaia_dr3_stars_within_500_light_years.csv",
    "planets": DATA / "3_Stars_and_Exoplanets" / "nasa_exoplanet_archive_confirmed_planets.csv",
    "craters": DATA / "4_Moon_Craters" / "moon_craters_robbins_lro_1.3M.csv",
}

for _d in (CHARTS, NUMBERS, CACHE):
    _d.mkdir(exist_ok=True)

# ----------------------------------------------------------------------------- reading the files

# Which columns are text, and which must be whole numbers with no blanks. Every other column is read
# as a decimal number, so a cell that is not a number makes reading stop with an error (nothing silent).
# Text stays text: designations like "1" vs "2017 U1", and 19-digit IDs such as gaia_source_id
# (as a float it would be rounded and the join to Gaia would silently fail).
READ_RULES = {
    "asteroids": {"text": ["full_name", "pdes", "name", "kind", "neo", "pha", "class", "first_obs", "last_obs"],
                  "int": ["spkid"]},
    "close_approaches": {"text": ["des", "orbit_id", "cd", "t_sigma_f", "fullname"]},
    "fireballs": {"text": ["date", "lat-dir", "lon-dir"]},
    "space_weather": {"text": ["datetime_utc"]},
    "stars": {"text": ["phot_variable_flag"], "int": ["source_id"]},
    "planets": {"text": ["pl_name", "hostname", "gaia_dr3_id", "discoverymethod", "disc_facility", "gaia_source_id"]},
    "craters": {"text": ["crater_id"]},
}


def columns(name: str) -> list[str]:
    """Column names of one file, read from its header line."""
    with open(FILES[name]) as fh:
        return fh.readline().rstrip("\n").split(",")


def read_csv(name: str, usecols=None, dtype_override: dict | None = None, **kw):
    """Read one file (only the columns asked for) with the safe reading rules.

    - quotechar '"' (names such as 'Oumuamua start with an apostrophe)
    - only empty cells are blank (keep_default_na=False), so text like "NA" stays text
    - text columns as text, ID columns as whole numbers, everything else as decimal numbers
    """
    import pandas as pd

    rules = READ_RULES[name]
    header = columns(name)
    cols = header if usecols is None else list(usecols)
    missing = [c for c in cols if c not in header]
    if missing:
        raise KeyError(f"{name}: no such column(s) {missing}")
    dtype = {}
    for c in cols:
        if c in rules["text"]:
            dtype[c] = "str"
        elif c in rules.get("int", []):
            dtype[c] = "int64"
        else:
            dtype[c] = "float64"
    dtype |= dtype_override or {}
    df = pd.read_csv(FILES[name], usecols=cols, quotechar='"', keep_default_na=False, na_values=[""],
                     dtype=dtype, **kw)
    return df[cols]


def load_parquet(name: str, columns=None):
    """Whole file as a cached Parquet copy (data_cache/<name>.parquet), built with read_csv the first time."""
    import pandas as pd

    path = CACHE / f"{name}.parquet"
    if not path.exists():
        with _lock(CACHE / f".{name}.lock"):
            if not path.exists():
                df = read_csv(name)
                tmp = path.with_name(path.name + ".tmp")
                df.to_parquet(tmp, index=False)
                os.replace(tmp, path)
    return pd.read_parquet(path, columns=columns)


# ----------------------------------------------------------------------------- shared science helpers

AU_KM = 149_597_870.7      # 1 AU in km
LD_AU = 0.00257            # 1 lunar distance in AU (as given in the brief)
LD_KM = 384_400            # 1 lunar distance in km
EARTH_RADIUS_KM = 6_371


def size_from_H(H, albedo=0.14):
    """Diameter in km from brightness H: D = 1329 / sqrt(albedo) * 10**(-H/5)."""
    import numpy as np

    return 1329 / np.sqrt(albedo) * 10 ** (-np.asarray(H, dtype=float) / 5)


def year_from_text(s):
    """Year from date text like '1999-??-??', '240-11-10' or '-146-08-06' (text before the first dash,
    keeping a leading minus sign)."""
    import pandas as pd

    return pd.to_numeric(s.str.extract(r"^(-?\d+)-", expand=False), errors="coerce")


# ----------------------------------------------------------------------------- saving files


def rel(path: Path) -> str:
    """Path relative to the project folder, for printing and for LOG.md."""
    return str(Path(path).resolve().relative_to(PROJECT))


def save_numbers(df, name: str, index: bool = False) -> str:
    """Save a table as numbers/<name>.csv and return its project-relative path."""
    path = NUMBERS / f"{name}.csv"
    df.to_csv(path, index=index)
    return rel(path)


def numbers(name: str):
    """Read a table saved with save_numbers (used by the app, so it shows the same numbers)."""
    import pandas as pd

    return pd.read_csv(NUMBERS / f"{name}.csv")


def save_chart(fig, name: str, dpi: int = 150) -> str:
    """Save a matplotlib figure as charts/<name>.png and return its project-relative path."""
    path = CHARTS / f"{name}.png"
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    return rel(path)


# ----------------------------------------------------------------------------- chart style

# Colours (light chart surface). One hue per job:
#   SERIES   = categories, used in this fixed order (never cycled)
#   SEQ_BLUE = one-hue ramp, light -> dark, for "more" (heatmaps)
SURFACE = "#fcfcfb"
INK = "#0b0b0b"         # titles, values
INK_2 = "#52514e"       # subtitles, axis labels
INK_MUTED = "#898781"   # captions, tick marks
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
GRAY = "#b4b2a9"        # de-emphasis colour for "everything else"
SEQ_BLUE = ["#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7", "#3987e5",
            "#2a78d6", "#256abf", "#1c5cab", "#184f95", "#104281", "#0d366b"]


def chart_style() -> None:
    """Quiet, consistent matplotlib look for every chart in the project."""
    import matplotlib as mpl

    mpl.rcParams.update({
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
        "axes.edgecolor": AXIS, "axes.linewidth": 0.8,
        "axes.labelcolor": INK_2, "axes.labelsize": 10,
        "axes.titlecolor": INK, "axes.titlesize": 11, "axes.titlelocation": "left",
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "axes.axisbelow": True,
        "grid.color": GRID, "grid.linewidth": 0.8, "grid.linestyle": "-",
        "xtick.color": AXIS, "ytick.color": AXIS, "xtick.labelcolor": INK_2, "ytick.labelcolor": INK_2,
        "xtick.labelsize": 9, "ytick.labelsize": 9,
        "font.family": "sans-serif", "font.size": 10,
        "legend.frameon": False, "legend.fontsize": 9,
        "lines.linewidth": 2, "lines.solid_capstyle": "round", "lines.solid_joinstyle": "round",
        "patch.edgecolor": "none",
    })


def compact(v, _pos=None) -> str:
    """Axis tick text: 950 / 1K / 25K / 1.5M."""
    v = float(v)
    for div, unit in ((1e9, "B"), (1e6, "M"), (1e3, "K")):
        if abs(v) >= div:
            s = f"{v / div:.1f}".rstrip("0").rstrip(".")
            return f"{s}{unit}"
    return f"{v:g}"


def caption(used, skipped=0, why: str = "", numbers_file: str = "", extra: str = "") -> str:
    """Standard chart caption: rows used, rows skipped (and why), where the numbers are."""
    s = f"Rows used: {used:,}. Skipped: {skipped:,}" + (f" ({why})" if why and skipped else "") + "."
    if extra:
        s += " " + extra
    if numbers_file:
        s += f" Numbers: {numbers_file}"
    return s


def draw_hist(ax, counts, edges, color=None, label=None, dense_at: int = 70):
    """Histogram from pre-computed counts. Few bins: bars with a thin surface gap. Many bins: a step
    line with a light wash under it (bars would be thinner than their gaps)."""
    import numpy as np

    color = color or SERIES[0]
    counts, edges = np.asarray(counts), np.asarray(edges)
    if len(counts) <= dense_at:
        ax.bar(edges[:-1], counts, width=np.diff(edges), align="edge", color=color,
               edgecolor=SURFACE, linewidth=0.6, label=label)
    else:
        ax.stairs(counts, edges, fill=True, color=color, alpha=0.18, linewidth=0)
        ax.stairs(counts, edges, color=color, linewidth=1.1, label=label)


def seq_cmap(start_at_surface: bool = True):
    """One-hue blue colour map, light -> dark (optionally starting from the chart surface for zero)."""
    from matplotlib.colors import LinearSegmentedColormap

    colors = ([SURFACE] if start_at_surface else []) + SEQ_BLUE
    return LinearSegmentedColormap.from_list("seq_blue", colors)


def add_titles(fig, title: str, subtitle: str = "", caption: str = "", width_chars: int | None = None,
               sizes: tuple[float, float, float] = (13.5, 10, 8.5)) -> None:
    """Title + subtitle stacked above all the axes, caption below, all left-aligned.

    Placed after drawing, from the real size of the axes and their labels, so nothing overlaps.
    Saved with bbox_inches='tight', so text outside the figure box is kept.
    """
    import textwrap

    width_chars = width_chars or int(fig.get_figwidth() * 12)
    wrap = lambda s, size: "\n".join(  # noqa: E731
        textwrap.fill(p, int(width_chars * 10 / size)) for p in s.split("\n")
    )
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    boxes = [a.get_tightbbox(r) for a in fig.axes if a.get_visible()]
    x0, y0, y1 = min(b.x0 for b in boxes), min(b.y0 for b in boxes), max(b.y1 for b in boxes)
    to_fig = fig.transFigure.inverted()
    fx = to_fig.transform((x0, 0))[0]
    pt = fig.dpi / 72
    y = y1 + 10 * pt
    if subtitle:
        t = fig.text(fx, to_fig.transform((0, y))[1], wrap(subtitle, sizes[1]), ha="left", va="bottom",
                     fontsize=sizes[1], color=INK_2, linespacing=1.4)
        fig.canvas.draw()
        y = t.get_window_extent(r).y1 + 6 * pt
    fig.text(fx, to_fig.transform((0, y))[1], wrap(title, sizes[0]), ha="left", va="bottom",
             fontsize=sizes[0], fontweight="bold", color=INK, linespacing=1.3)
    if caption:
        fig.text(fx, to_fig.transform((0, y0 - 8 * pt))[1], wrap(caption, sizes[2]), ha="left", va="top",
                 fontsize=sizes[2], color=INK_MUTED, linespacing=1.4)



# ----------------------------------------------------------------------------- timing


_T0 = [None]


def tick(label: str = "") -> str:
    """Print seconds since the last tick and this process's memory (to spot slow or heavy cells)."""
    import time

    now = time.time()
    dt = 0.0 if _T0[0] is None else now - _T0[0]
    _T0[0] = now
    rss = 0
    try:
        for line in open("/proc/self/status"):
            if line.startswith("VmRSS:"):
                rss = int(line.split()[1]) // 1024
    except OSError:
        pass
    msg = f"[{label}] +{dt:.1f}s, memory {rss:,} MB"
    print(msg)
    return msg


# ----------------------------------------------------------------------------- LOG (json store -> LOG.md)

SECTION_TITLES = {
    "A": "Section A: Asteroids and comets",
    "B": "Section B: Close approaches",
    "C": "Section C: Fireballs",
    "D": "Section D: Space weather",
    "E": "Section E: Stars",
    "F": "Section F: Exoplanets",
    "G": "Section G: Moon craters",
}
STEPS = ["1", "2", "3", "4", "5", "6", "app"]
STEP_NAMES = {"1": "Scan", "2": "One label", "3": "Two labels", "4": "Odd things", "5": "Checks",
              "6": "Explain", "app": "App page"}

LOG_HEADER = """# LOG

Running log of every chart and table, in the order of the brief's chart list.
Written by code (`notebooks/helpers.py`, functions `log_entry`, `progress`, `edge_case`), so every number
in it comes from code that ran. The same content is stored as data in `numbers/_log.json` (the app reads it).
Re-running a notebook replaces its entries instead of adding copies.

Each entry: chart file, numbers file, rows used, rows skipped (blanks), key numbers, what it shows.
"""


@contextmanager
def _lock(path: Path):
    path.parent.mkdir(exist_ok=True)
    with open(path, "w") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


def _write_atomic(path: Path, text: str) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text)
    os.replace(tmp, path)


def log_store() -> dict:
    """The whole log as data: {'entries': {...}, 'progress': {...}, 'edge_cases': {...}}."""
    if LOG_JSON.exists():
        store = json.loads(LOG_JSON.read_text())
    else:
        store = {}
    for k in ("entries", "progress", "edge_cases"):
        store.setdefault(k, {})
    return store


def entry(key: str) -> dict | None:
    """One log entry (title, chart, numbers, key_numbers, what_it_shows, ...)."""
    return log_store()["entries"].get(key)


def _update(fn) -> None:
    with _lock(NUMBERS / ".log.lock"):
        store = log_store()
        fn(store)
        _write_atomic(LOG_JSON, json.dumps(store, indent=1, ensure_ascii=False))
        _write_atomic(LOG, _render(store))


def fmt(x) -> str:
    """Plain number formatting with thousands separators."""
    if isinstance(x, bool):
        return str(x)
    if isinstance(x, int):
        return f"{x:,}"
    try:
        xf = float(x)
    except (TypeError, ValueError):
        return str(x)
    if xf.is_integer() and abs(xf) < 1e15:
        return f"{int(xf):,}"
    return f"{xf:,.4g}"


def log_entry(
    key: str,
    title: str,
    *,
    chart: str | list[str] | None = None,
    numbers: str | list[str] | None = None,
    rows_used=None,
    rows_skipped=None,
    key_numbers: list[str] | tuple[str, ...] = (),
    what_it_shows: str = "",
    step: int | str | None = None,
) -> None:
    """Insert or replace one entry, keyed by e.g. 'A05'. Numbers should be formatted from variables."""
    as_list = lambda v: [] if v is None else ([v] if isinstance(v, str) else list(v))  # noqa: E731
    rec = {
        "key": key,
        "section": key[0],
        "step": None if step is None else str(step),
        "title": title,
        "chart": as_list(chart),
        "numbers": as_list(numbers),
        "rows_used": rows_used if isinstance(rows_used, str) else fmt(rows_used),
        "rows_skipped": rows_skipped if isinstance(rows_skipped, str) else fmt(rows_skipped),
        "key_numbers": list(key_numbers),
        "what_it_shows": what_it_shows,
        "updated": datetime.now().isoformat(timespec="seconds"),
    }
    _update(lambda s: s["entries"].__setitem__(key, rec))


def progress(section: str, step, note: str = "") -> None:
    """Mark one step of a section as done (step = 1..6 or 'app'). Shown in the table at the top of LOG.md."""
    def fn(s):
        s["progress"].setdefault(section, {})[str(step)] = {
            "done": datetime.now().isoformat(timespec="minutes"), "note": note}
    _update(fn)


def edge_case(section: str, text: str) -> None:
    """Park a small edge case in LOG.md instead of spending long on it."""
    def fn(s):
        lst = s["edge_cases"].setdefault(section, [])
        if text not in lst:
            lst.append(text)
    _update(fn)


def _next_step(store) -> str:
    for sec in SECTION_TITLES:
        for st in STEPS:
            if st not in store["progress"].get(sec, {}):
                return f"Section {sec}, {'step ' + st if st != 'app' else 'app page'} ({STEP_NAMES[st]})"
    return "All sections done: write FINDINGS.md, compare with the answer key, test the app."


def _render(store) -> str:
    out = [LOG_HEADER, "## Progress\n"]
    out.append("| Section | " + " | ".join(f"{s} {STEP_NAMES[s]}" if s != "app" else "App page" for s in STEPS) + " |")
    out.append("|---" * (len(STEPS) + 1) + "|")
    for sec in SECTION_TITLES:
        p = store["progress"].get(sec, {})
        out.append(f"| {sec} | " + " | ".join("done" if s in p else "" for s in STEPS) + " |")
    out.append(f"\n**Next:** {_next_step(store)}\n")
    notes = [(sec, st, v["note"]) for sec, d in store["progress"].items() for st, v in d.items() if v.get("note")]
    if notes:
        out.append("Notes: " + "; ".join(f"{sec}{st}: {n}" for sec, st, n in notes) + "\n")

    entries = store["entries"]
    for sec, title in SECTION_TITLES.items():
        keys = sorted(k for k in entries if k[0] == sec)
        cases = store["edge_cases"].get(sec, [])
        if not keys and not cases:
            continue
        out.append(f"## {title}\n")
        for k in keys:
            e = entries[k]
            join = lambda v: ", ".join(f"`{x}`" for x in v) if v else "none"  # noqa: E731
            out.append(f"### {k} {e['title']}\n")
            out.append(f"- **Chart file:** {join(e['chart'])}")
            out.append(f"- **Numbers file:** {join(e['numbers'])}")
            out.append(f"- **Rows used:** {e['rows_used']}")
            out.append(f"- **Rows skipped (blanks):** {e['rows_skipped']}")
            out.append("- **Key numbers:**")
            out.extend(f"  - {x}" for x in e["key_numbers"])
            out.append(f"- **What it shows:** {e['what_it_shows']}\n")
        if cases:
            out.append(f"### Edge cases parked ({sec})\n")
            out.extend(f"- {c}" for c in cases)
            out.append("")
    return "\n".join(out) + "\n"
