"""Everything the Predictions page and the API ask for. Nothing here trains a model: models are read from
forecast/models/ (made by forecast/train.py) and test scores from numbers/FC_*."""
from __future__ import annotations

import json
import math
from functools import lru_cache

import numpy as np
import pandas as pd

from . import config as C
from . import data as D

KEY_VARIABLES = ["speed_km_s", "bt_nT", "bz_gsm_nT", "density_cm3", "temp_K", "pressure_nPa", "sym_h_nT", "ae_nT"]


# ----------------------------------------------------------------------------------------------- what is there
def have_data() -> bool:
    return D.have_data()


def models_ready() -> bool:
    return (C.MODEL_DIR / "registry.json").exists()


@lru_cache(maxsize=1)
def registry() -> dict:
    return json.loads((C.MODEL_DIR / "registry.json").read_text())


@lru_cache(maxsize=None)
def _model(kind: str, key: str):
    import xgboost as xgb
    info = registry()["regressors" if kind == "reg" else "classifiers"][key]
    m = xgb.XGBRegressor() if kind == "reg" else xgb.XGBClassifier()
    m.load_model(C.MODEL_DIR / info["file"])
    return m, info


def step() -> pd.Timedelta:
    return pd.Timedelta(minutes=D.cadence_min(D.frame()) if have_data() else 5)


def horizons() -> dict[str, int]:
    return D.horizons() if have_data() else {k: m // 5 for k, m in C.HORIZON_MIN.items()}


def measurements() -> list[dict]:
    reg = registry()["regressors"] if models_ready() else {}
    cols = list(D.frame().columns) if have_data() else list(C.VARIABLES)
    return [{"column": c, "name": C.VARIABLES.get(c, (c, ""))[0], "unit": C.VARIABLES.get(c, (c, ""))[1],
             "forecast_horizons": [h for h in horizons() if f"{c}|{h}" in reg]} for c in cols]


def unit(col: str) -> str:
    return C.VARIABLES.get(col, (col, ""))[1]


def name(col: str) -> str:
    return C.VARIABLES.get(col, (col, ""))[0]


def period_of(t) -> str:
    t = pd.Timestamp(t)
    if t < pd.Timestamp(C.TRAIN_END):
        return "train"
    return "validation" if t < pd.Timestamp(C.VAL_END) else "test"


# ----------------------------------------------------------------------------------------------- observations
def latest() -> dict:
    """The newest value of each measurement, with its change over the hour and three hours before it."""
    df = D.frame()
    out = {"time": str(df.index[-1]), "values": {}}
    for c in df.columns:
        s = df[c]
        i = s.last_valid_index()
        if i is None:
            continue
        v = float(s[i])

        def before(hours):
            prev = s.loc[: i - pd.Timedelta(hours=hours)].tail(24).dropna()
            return None if prev.empty else v - float(prev.iloc[-1])

        out["values"][c] = {"name": name(c), "unit": unit(c), "value": v, "time": str(i),
                            "change_1h": before(1), "change_3h": before(3)}
    return out


def history(col: str, start, end, max_points: int = 4000) -> pd.Series:
    """Observed values between start and end; long windows are averaged into fewer points for drawing."""
    s = D.frame().loc[pd.Timestamp(start):pd.Timestamp(end), col]
    if len(s) > max_points:
        k = math.ceil(len(s) / max_points)
        s = s.resample(step() * k).mean()
    return s


def _features_at(origins_from, origins_to) -> pd.DataFrame:
    df = D.frame()
    a = pd.Timestamp(origins_from) - step() * (D.LOOKBACK_STEPS + 12)
    return D.features(df.loc[a:pd.Timestamp(origins_to)]).loc[pd.Timestamp(origins_from):pd.Timestamp(origins_to)]


# ----------------------------------------------------------------------------------------------- forecasts
def backtest(col: str, horizon: str, start, end) -> pd.DataFrame:
    """Forecasts made `horizon` before each time in [start, end], next to what was observed then."""
    m, info = _model("reg", f"{col}|{horizon}")
    lead = step() * info["steps"]
    X = _features_at(pd.Timestamp(start) - lead, pd.Timestamp(end) - lead)
    base = D.frame()[col].reindex(X.index).to_numpy(dtype=float)
    pred = base + m.predict(X.to_numpy(), iteration_range=(0, info["best_iteration"] + 1))
    when = X.index + lead
    actual = D.frame()[col].reindex(when).to_numpy(dtype=float)
    return pd.DataFrame({"time": when, "observed": actual, "forecast": pred, "low": pred + info["lo"],
                         "high": pred + info["hi"], "persistence": base})


def window_scores(bt: pd.DataFrame) -> dict | None:
    ok = bt[["observed", "forecast", "persistence"]].notna().all(axis=1)
    if ok.sum() < 3:
        return None
    b = bt[ok]
    e, p = b["forecast"] - b["observed"], b["persistence"] - b["observed"]
    return {"n": int(ok.sum()), "mae": float(e.abs().mean()), "rmse": float(np.sqrt((e ** 2).mean())),
            "mae_persistence": float(p.abs().mean()), "rmse_persistence": float(np.sqrt((p ** 2).mean())),
            "inside_interval_pct": float(100 * ((b["observed"] >= b["low"]) & (b["observed"] <= b["high"])).mean())}


def future(col: str) -> pd.DataFrame:
    """Forecasts for every horizon, made at the last time in the file with a value for this measurement."""
    df = D.frame()
    origin = df[col].last_valid_index()
    X = _features_at(origin, origin)
    base = float(df[col][origin])
    rows = []
    for h in horizons():
        key = f"{col}|{h}"
        if key not in registry()["regressors"]:
            continue
        m, info = _model("reg", key)
        p = base + float(m.predict(X.to_numpy(), iteration_range=(0, info["best_iteration"] + 1))[0])
        rows.append({"horizon": h, "time": origin + step() * info["steps"], "forecast": p, "low": p + info["lo"],
                     "high": p + info["hi"]})
    out = pd.DataFrame(rows)
    out.attrs["origin"], out.attrs["origin_value"] = origin, base
    return out


# ----------------------------------------------------------------------------------------------- storms
def outlook() -> dict:
    """Storm chances from the classifiers and the SYM-H forecast path, all made at the last SYM-H reading."""
    df = D.frame()
    origin = df["sym_h_nT"].last_valid_index()
    X = _features_at(origin, origin).to_numpy()
    events = []
    for key in registry()["classifiers"]:
        m, info = _model("clf", key)
        p = float(m.predict_proba(X, iteration_range=(0, info["best_iteration"] + 1))[0, 1])
        events.append({"event": key, "name": info["name"], "hours": info["hours"], "threshold_nT": info["threshold"],
                       "probability": p, "decision_threshold": info["decision_threshold"],
                       "flagged": p >= info["decision_threshold"]})
    path = future("sym_h_nT")
    path["severity"] = path["forecast"].map(C.severity)
    now = float(df["sym_h_nT"][origin])
    return {"origin": str(origin), "sym_h_now": now, "severity_now": C.severity(now), "events": events,
            "sym_h_path": path}


def event_probabilities(event: str, start, end, every: int = 6) -> pd.DataFrame:
    """The classifier's storm chance every `every` time steps between start and end, with observed SYM-H."""
    m, info = _model("clf", event)
    X = _features_at(start, end).iloc[::every]
    p = m.predict_proba(X.to_numpy(), iteration_range=(0, info["best_iteration"] + 1))[:, 1]
    return pd.DataFrame({"time": X.index, "probability": p})


@lru_cache(maxsize=1)
def storm_history() -> pd.DataFrame:
    f = C.NUMBERS / "FC_storm_events.csv"
    ev = pd.read_csv(f, parse_dates=["start", "end", "time_of_min"]) if f.exists() else \
        D.storm_events(D.frame()["sym_h_nT"])
    return ev


@lru_cache(maxsize=1)
def _ranges() -> pd.DataFrame:
    df = D.frame()[KEY_VARIABLES]
    return df.quantile([0.0005, 0.9995])


def unusual(days: int = 30) -> pd.DataFrame:
    """Readings in the last `days` days outside the 0.05% to 99.95% range of the whole file (not a forecast)."""
    df = D.frame()
    recent = df.loc[df.index[-1] - pd.Timedelta(days=days):, KEY_VARIABLES]
    q = _ranges()
    rows = []
    for c in KEY_VARIABLES:
        lo, hi = float(q.loc[0.0005, c]), float(q.loc[0.9995, c])
        s = recent[c].dropna()
        for t, v in s[(s < lo) | (s > hi)].items():
            rows.append({"time": t, "column": c, "measurement": name(c), "value": float(v), "unit": unit(c),
                         "usual_low": lo, "usual_high": hi, "side": "low" if v < lo else "high"})
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------------------------- scores, health
def performance() -> dict:
    out = {}
    for k, f in [("regression", "FC_regression_scores.csv"), ("events", "FC_event_scores.csv"),
                 ("calibration", "FC_calibration.csv")]:
        p = C.NUMBERS / f
        out[k] = pd.read_csv(p) if p.exists() else pd.DataFrame()
    m = C.NUMBERS / "FC_training.json"
    out["training"] = json.loads(m.read_text()) if m.exists() else {}
    return out


@lru_cache(maxsize=1)
def dataset_health() -> dict:
    if have_data():
        return D.health(D.frame())
    f = C.NUMBERS / "FC_dataset_health.json"
    return json.loads(f.read_text()) if f.exists() else {}
