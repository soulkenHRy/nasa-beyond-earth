"""The forecasting functions over HTTP. Run:  .venv/bin/uvicorn forecast.api:app --port 8600
Then see http://localhost:8600/docs for every endpoint. Models must be trained first (forecast/train.py)."""
from __future__ import annotations

import math

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Query

from . import config as C
from . import service as S

app = FastAPI(title="NASA Beyond Earth: space-weather forecasts", version="0.1",
              description="Solar wind, magnetic field and geomagnetic forecasts from the NASA OMNI 5-minute file.")


def clean(x):
    """JSON-safe: times as text, NaN as null, numpy numbers as plain numbers."""
    if isinstance(x, pd.DataFrame):
        return [clean(r) for r in x.to_dict("records")]
    if isinstance(x, pd.Series):
        return [{"time": str(t), "value": clean(v)} for t, v in x.items()]
    if isinstance(x, dict):
        return {str(k): clean(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [clean(v) for v in x]
    if isinstance(x, (pd.Timestamp, np.datetime64)):
        return str(pd.Timestamp(x))
    if isinstance(x, (np.floating, float)):
        return None if math.isnan(float(x)) else float(x)
    if isinstance(x, np.integer):
        return int(x)
    if isinstance(x, np.bool_):
        return bool(x)
    return x


def need(data: bool = True, models: bool = False) -> None:
    if data and not S.have_data():
        raise HTTPException(503, "The data file data_cache/space_weather.parquet is not here.")
    if models and not S.models_ready():
        raise HTTPException(503, "Models are not trained yet: run  python -m forecast.train")


def check_col(col: str, forecast: bool = False) -> None:
    if col not in C.VARIABLES:
        raise HTTPException(404, f"Unknown measurement {col!r}")
    if forecast and col not in C.TARGETS:
        raise HTTPException(404, f"No forecast model for {col!r}; models exist for {C.TARGETS}")


@app.get("/api/forecast/measurements")
def measurements():
    need()
    return {"measurements": S.measurements(), "horizons": list(S.horizons()), "events": list(C.EVENTS)}


@app.get("/api/forecast/observations/latest")
def latest():
    need()
    return clean(S.latest())


@app.get("/api/forecast/observations")
def observations(variable: str, start: str, end: str, max_points: int = Query(4000, ge=10, le=20000)):
    need()
    check_col(variable)
    s = S.history(variable, start, end, max_points)
    return {"variable": variable, "unit": S.unit(variable), "points": clean(s)}


@app.get("/api/forecast/predictions")
def predictions(variable: str, horizon: str, start: str, end: str):
    need(models=True)
    check_col(variable, forecast=True)
    if horizon not in S.horizons():
        raise HTTPException(404, f"Unknown horizon {horizon!r}; use one of {list(S.horizons())}")
    if pd.Timestamp(end) - pd.Timestamp(start) > pd.Timedelta(days=62):
        raise HTTPException(400, "Ask for at most 62 days at a time.")
    bt = S.backtest(variable, horizon, start, end)
    fut = S.future(variable)
    return {"variable": variable, "unit": S.unit(variable), "horizon": horizon,
            "period": S.period_of(start), "window_scores": clean(S.window_scores(bt)),
            "backtest": clean(bt), "future": {"made_at": str(fut.attrs["origin"]), "points": clean(fut)}}


@app.get("/api/forecast/events/outlook")
def outlook():
    need(models=True)
    return clean(S.outlook())


@app.get("/api/forecast/events/history")
def events_history(min_severity: str = "Moderate"):
    order = [C.QUIET] + [n for _, n in reversed(C.SEVERITY)]
    if min_severity not in order:
        raise HTTPException(404, f"Use one of {order}")
    ev = S.storm_history()
    keep = ev["severity"].map(order.index) >= order.index(min_severity)
    return {"events": clean(ev[keep])}


@app.get("/api/forecast/events/unusual")
def unusual(days: int = Query(30, ge=1, le=365)):
    need()
    return {"days": days, "readings": clean(S.unusual(days))}


@app.get("/api/forecast/models/performance")
def performance():
    p = S.performance()
    return {"training": p["training"], "regression": clean(p["regression"]), "events": clean(p["events"]),
            "calibration": clean(p["calibration"])}


@app.get("/api/forecast/dataset")
def dataset():
    return clean(S.dataset_health())
