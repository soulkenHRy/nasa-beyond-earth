"""Reading the 5-minute OMNI file, the model inputs (past values only), storm events and data health."""
from __future__ import annotations

from functools import lru_cache

import numpy as np
import pandas as pd

from . import config as C


def have_data() -> bool:
    return C.DATA_FILE.exists()


@lru_cache(maxsize=1)
def frame() -> pd.DataFrame:
    """The whole file, indexed by time (UTC), oldest first."""
    df = pd.read_parquet(C.DATA_FILE)
    df.index = pd.DatetimeIndex(pd.to_datetime(df.pop(C.TIME_COL)), name="time")
    return df.sort_index()


def cadence_min(df: pd.DataFrame) -> int:
    return int(round(pd.Series(df.index[:5000]).diff().median().total_seconds() / 60))


def horizons(df: pd.DataFrame | None = None) -> dict[str, int]:
    """Horizon name -> number of time steps, for the horizons the file's time step allows."""
    step = cadence_min(df if df is not None else frame())
    return {k: m // step for k, m in C.HORIZON_MIN.items() if m % step == 0 and m >= step}


def candidate_targets(df: pd.DataFrame, max_missing: float = 0.15) -> list[str]:
    """Numeric columns that could be forecast: mostly filled in and not constant."""
    out = []
    for c in df.columns:
        s = df[c]
        if pd.api.types.is_numeric_dtype(s) and s.isna().mean() <= max_missing and s.std(skipna=True) > 0:
            out.append(c)
    return out


def features(df: pd.DataFrame) -> pd.DataFrame:
    """Inputs at each time t, made only from values at t or before (shift(+k) and trailing windows)."""
    out = {}
    for v in C.DRIVERS:
        s = df[v]
        out[v] = s
        for k in (3, 12, 36):                         # 15 min, 1 h and 3 h ago
            out[f"{v}_lag{k}"] = s.shift(k)
        for w in (12, 36, 144):                       # mean of the last 1 h, 3 h, 12 h
            out[f"{v}_mean{w}"] = s.rolling(w, min_periods=max(1, w // 4)).mean()
        out[f"{v}_std36"] = s.rolling(36, min_periods=9).std()
    bz, sym, v = df["bz_gsm_nT"], df["sym_h_nT"], df["speed_km_s"]
    out["bz_min36"] = bz.rolling(36, min_periods=9).min()
    vbs = v * (-bz).clip(lower=0) / 1000.0            # speed x southward field: how hard the wind drives storms
    out["v_bs"] = vbs
    out["v_bs_mean12"] = vbs.rolling(12, min_periods=3).mean()
    out["v_bs_mean72"] = vbs.rolling(72, min_periods=18).mean()
    out["sym_h_min288"] = sym.rolling(288, min_periods=72).min()
    out["sym_h_change12"] = sym - sym.shift(12)
    doy = df.index.day_of_year.to_numpy()
    minute = (df.index.hour * 60 + df.index.minute).to_numpy()
    out["doy_sin"] = np.sin(2 * np.pi * doy / 365.25)
    out["doy_cos"] = np.cos(2 * np.pi * doy / 365.25)
    out["ut_sin"] = np.sin(2 * np.pi * minute / 1440)
    out["ut_cos"] = np.cos(2 * np.pi * minute / 1440)
    return pd.DataFrame(out, index=df.index).astype("float32")


LOOKBACK_STEPS = 288                                  # the longest window above (24 h)


def future_min(s: pd.Series, steps: int) -> pd.Series:
    """Lowest value in the next `steps` time steps after t (not counting t): the storm label's input."""
    return s.rolling(steps, min_periods=1).min().shift(-steps)


def storm_events(sym: pd.Series, threshold: float = -50, join_hours: float = C.STORM_JOIN_HOURS) -> pd.DataFrame:
    """Storms: runs of SYM-H at or below the threshold, joined when less than `join_hours` apart."""
    below = (sym <= threshold).to_numpy()
    t = sym.index
    if not below.any():
        return pd.DataFrame(columns=["start", "end", "time_of_min", "min_sym_h", "hours", "severity"])
    idx = np.flatnonzero(below)
    gap = np.asarray(np.diff(t[idx]) > pd.Timedelta(hours=join_hours))     # works for any time unit
    starts = np.r_[0, np.flatnonzero(gap) + 1]
    ends = np.r_[np.flatnonzero(gap), len(idx) - 1]
    rows = []
    vals = sym.to_numpy()
    for a, b in zip(starts, ends):
        i0, i1 = idx[a], idx[b]
        seg = vals[i0:i1 + 1]
        j = i0 + int(np.nanargmin(seg))
        rows.append({"start": t[i0], "end": t[i1], "time_of_min": t[j], "min_sym_h": float(vals[j]),
                     "hours": round((t[i1] - t[i0]).total_seconds() / 3600 + 5 / 60, 2)})
    ev = pd.DataFrame(rows)
    ev["severity"] = ev["min_sym_h"].map(C.severity)
    return ev


def health(df: pd.DataFrame) -> dict:
    """Coverage, time step, missing values per column and per year, longest gaps, latest values."""
    step = cadence_min(df)
    diffs = pd.Series(df.index).diff().dropna()
    expected = int((df.index[-1] - df.index[0]) / pd.Timedelta(minutes=step)) + 1
    cols = {}
    for c in df.columns:
        s = df[c]
        miss = s.isna().to_numpy()
        longest = 0
        if miss.any():
            edges = np.flatnonzero(np.diff(np.r_[0, miss.astype(np.int8), 0]))
            longest = int((edges[1::2] - edges[::2]).max())
        last = s.last_valid_index()
        cols[c] = {"name": C.VARIABLES.get(c, (c, ""))[0], "unit": C.VARIABLES.get(c, (c, ""))[1],
                   "missing_pct": round(100 * float(miss.mean()), 2), "longest_gap_hours": round(longest * step / 60, 1),
                   "min": float(s.min()), "median": float(s.median()), "max": float(s.max()),
                   "last_time": None if last is None else str(last), "last_value": None if last is None else float(s[last])}
    by_year = (df.notna().groupby(df.index.year).mean() * 100).round(1)
    return {"first": str(df.index[0]), "last": str(df.index[-1]), "rows": int(len(df)), "step_min": step,
            "regular": bool((diffs == pd.Timedelta(minutes=step)).all()), "expected_rows": expected,
            "duplicate_times": int(df.index.duplicated().sum()), "columns": cols,
            "present_pct_by_year": {str(y): by_year.loc[y].to_dict() for y in by_year.index},
            "candidate_targets": candidate_targets(df)}
