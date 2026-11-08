"""Will there be a geomagnetic storm on a given day? A storm day is a day when SYM-H reaches -50 nT or lower.

Only data from before the day is used:
  1 day ahead      the 5-minute storm model (forecast/train.py), run at the last reading before the day starts
  2 to 90 days     one small XGBoost model per lead time, on daily summaries (this file)
  further ahead    the usual share of storm days in that month over the last solar cycle (not a forecast of the day)

    .venv/bin/python -m forecast.daily        # train and test the daily models (about a minute)
"""
from __future__ import annotations

import json
import time
from functools import lru_cache

import numpy as np
import pandas as pd

from . import config as C
from . import data as D

LEADS = [2, 3, 5, 7, 10, 14, 21, 27, 35, 45, 60, 75, 90]      # day 1 uses the 5-minute model
MAX_LEAD = LEADS[-1]
REPORT_LEADS = [1, 2, 3, 7, 14, 27, 60, 90]
STORM, STRONG = -50, -100
MIN_COVER = 0.5                     # a day counts only if at least half of its SYM-H readings are there
CLIMATE_YEARS = 11                  # one solar cycle, for the long-range answer
TRAIN_END = "2021-01-01"            # daily models: train 2010-2020, choose flag lines on 2021-2022, test 2023 on
XGB = dict(n_estimators=300, learning_rate=0.03, max_depth=3, min_child_weight=10, subsample=0.8,
           colsample_bytree=0.8, tree_method="hist")               # chosen on 2021-2022, not on the test years


@lru_cache(maxsize=1)
def days() -> pd.DataFrame:
    """One row per UTC day: the day's summaries and whether it had a storm."""
    df = D.frame()
    per_day = 1440 // D.cadence_min(df)
    g = df.groupby(df.index.floor("D"))
    t = pd.DataFrame({"sym_min": g["sym_h_nT"].min(), "sym_mean": g["sym_h_nT"].mean(),
                      "sym_cover": g["sym_h_nT"].count() / per_day, "v_mean": g["speed_km_s"].mean(),
                      "v_max": g["speed_km_s"].max(), "bz_min": g["bz_gsm_nT"].min(), "bt_max": g["bt_nT"].max(),
                      "n_mean": g["density_cm3"].mean(), "p_max": g["pressure_nPa"].max(), "ae_max": g["ae_nT"].max()})
    t.index = pd.DatetimeIndex(t.index, name="day")
    t = t.asfreq("D")
    known = t["sym_cover"] >= MIN_COVER
    t.loc[~known, ["sym_min", "sym_mean"]] = np.nan
    t["storm"] = np.where(known, (t["sym_min"] <= STORM).astype(float), np.nan)
    return t


def last_day() -> pd.Timestamp:
    """The last day with storm-meter (SYM-H) readings: forecasts start from here."""
    return days()["sym_min"].last_valid_index()


def lead_features(t: pd.DataFrame, lead: int) -> pd.DataFrame:
    """Inputs for every day D of `t`, using only the days up to D - lead."""
    f = {}
    for c in ["sym_min", "sym_mean", "v_mean", "v_max", "bz_min", "bt_max", "n_mean", "p_max", "ae_max"]:
        f[f"{c}_last"] = t[c].shift(lead)
    f["sym_min_2nd_last"] = t["sym_min"].shift(lead + 1)
    f["sym_min_3rd_last"] = t["sym_min"].shift(lead + 2)
    f["v_mean_3d"] = t["v_mean"].rolling(3, min_periods=1).mean().shift(lead)
    f["storms_7d"] = t["storm"].rolling(7, min_periods=3).sum().shift(lead)
    f["storms_27d"] = t["storm"].rolling(27, min_periods=10).sum().shift(lead)
    f["storm_rate_365d"] = t["storm"].rolling(365, min_periods=180).mean().shift(lead)
    f["v_mean_27d"] = t["v_mean"].rolling(27, min_periods=10).mean().shift(lead)
    for k in (27, 54):                                   # one and two turns of the Sun before D (finding 14)
        known = k - 1 >= lead                            # the days D-k-1 .. D-k+1 are all before D - lead
        for c, how in [("sym_min", "min"), ("v_mean", "max"), ("storm", "max")]:
            w = getattr(t[c].rolling(3, center=True, min_periods=1), how)().shift(k)
            f[f"{c}_{k}d_before"] = w if known else pd.Series(np.nan, index=t.index)
    doy = t.index.day_of_year.to_numpy()
    f["doy_sin"] = np.sin(2 * np.pi * doy / 365.25)
    f["doy_cos"] = np.cos(2 * np.pi * doy / 365.25)
    return pd.DataFrame(f, index=t.index).astype("float32")


def _flag_line(y, p) -> float:
    from sklearn.metrics import precision_recall_curve
    pr, rc, th = precision_recall_curve(y, p)
    f1 = 2 * pr[:-1] * rc[:-1] / np.maximum(pr[:-1] + rc[:-1], 1e-12)
    return float(th[int(np.argmax(f1))]) if len(th) else 0.5


def _row(lead, model, y, p, line, base_train) -> dict:
    from sklearn.metrics import average_precision_score, brier_score_loss, precision_recall_fscore_support
    pr, rc, f1, _ = precision_recall_fscore_support(y, p >= line, average="binary", zero_division=0)
    brier, clim = float(brier_score_loss(y, p)), float(brier_score_loss(y, np.full(len(y), base_train)))
    return {"lead_days": lead, "model": model, "test_days": int(len(y)), "storm_days": int(y.sum()),
            "base_rate_pct": 100 * float(y.mean()), "precision": float(pr), "recall": float(rc), "f1": float(f1),
            "pr_auc": float(average_precision_score(y, p)), "brier": brier, "brier_usual_rate": clim,
            "brier_skill_pct": 100 * (1 - brier / clim), "flag_line": float(line)}


# ----------------------------------------------------------------------------------------------- training
def train() -> None:
    import xgboost as xgb
    from sklearn.metrics import precision_recall_fscore_support

    from . import service as S
    t0 = time.time()
    t = days()
    y_all = t["storm"]
    when = t.index
    is_train, is_val = when < pd.Timestamp(TRAIN_END), (when >= pd.Timestamp(TRAIN_END)) & (when < pd.Timestamp(C.VAL_END))
    is_test = when >= pd.Timestamp(C.VAL_END)
    known = y_all.notna().to_numpy()
    base_train = float(y_all[is_train & known].mean())
    reg = {"last_day": str(last_day().date()), "base_rate_train": base_train, "models": {}}
    rows = []

    # 1 day ahead: the 5-minute model, run at the last reading before each test day
    m5, info5 = S._model("clf", "storm_24h")
    test_days = when[is_test & known]
    origins = [d - S.step() for d in test_days]
    X5 = S._features_at(origins[0], origins[-1])
    X5 = X5.reindex(pd.DatetimeIndex(origins))
    p1 = m5.predict_proba(X5.to_numpy(), iteration_range=(0, info5["best_iteration"] + 1))[:, 1]
    y1 = y_all[test_days].to_numpy()
    r = _row(1, "5-minute model", y1, p1, info5["decision_threshold"], base_train)
    yest = (np.nan_to_num(y_all.shift(1)[test_days].to_numpy(), nan=0.0) > 0.5)
    p0, r0, f0, _ = precision_recall_fscore_support(y1, yest, average="binary", zero_division=0)
    r.update(precision_persistence=float(p0), recall_persistence=float(r0), f1_persistence=float(f0))
    rows.append(r)
    reg["models"]["1"] = {"kind": "5-minute model", "event": "storm_24h", "line": info5["decision_threshold"]}

    # 2 to 90 days ahead: one daily model per lead
    for L in LEADS:
        X = lead_features(t, L)
        feats = list(X.columns)
        m = xgb.XGBClassifier(**XGB, n_jobs=4, random_state=0)
        m.fit(X[is_train & known], y_all[is_train & known], verbose=False)
        line = _flag_line(y_all[is_val & known], m.predict_proba(X[is_val & known])[:, 1])
        name = f"daily_storm_{L}.ubj"
        m.save_model(C.MODEL_DIR / name)
        reg["models"][str(L)] = {"kind": "daily model", "file": name, "line": line, "features": feats}
        if L in REPORT_LEADS:
            rows.append(_row(L, "daily model", y_all[is_test & known].to_numpy(),
                             m.predict_proba(X[is_test & known])[:, 1], line, base_train))
    for r in rows:
        print(f"  {r['lead_days']:3d} days ahead ({r['model']}): precision {r['precision']:.2f} recall {r['recall']:.2f} "
              f"F1 {r['f1']:.2f} PR-AUC {r['pr_auc']:.2f} (storm days {r['base_rate_pct']:.1f}%), "
              f"Brier skill {r['brier_skill_pct']:.0f}%" + (f"; persistence F1 {r['f1_persistence']:.2f}"
                                                            if 'f1_persistence' in r else ""), flush=True)
    pd.DataFrame(rows).to_csv(C.NUMBERS / "FC_daily_scores.csv", index=False)
    climate(t).to_csv(C.NUMBERS / "FC_daily_climatology.csv", index=False)
    reg["trained_seconds"] = round(time.time() - t0, 1)
    (C.MODEL_DIR / "daily_registry.json").write_text(json.dumps(reg, indent=1) + "\n")
    print(f"done in {time.time() - t0:.0f} s")


def climate(t: pd.DataFrame) -> pd.DataFrame:
    """Share of storm days in each calendar month over the last CLIMATE_YEARS years of data."""
    end = last_day()
    w = t.loc[end - pd.DateOffset(years=CLIMATE_YEARS) + pd.Timedelta(days=1):end]
    w = w[w["storm"].notna()]
    g = w.groupby(w.index.month)
    return pd.DataFrame({"month": g.size().index, "days": g.size().to_numpy(),
                         "storm_days": g["storm"].sum().astype(int).to_numpy(),
                         "from": str(w.index[0].date()), "to": str(w.index[-1].date())})


# ----------------------------------------------------------------------------------------------- one date
def ready() -> bool:
    return (C.MODEL_DIR / "daily_registry.json").exists()


@lru_cache(maxsize=1)
def registry() -> dict:
    return json.loads((C.MODEL_DIR / "daily_registry.json").read_text())


@lru_cache(maxsize=None)
def _daily_model(lead: int):
    import xgboost as xgb
    m = xgb.XGBClassifier()
    m.load_model(C.MODEL_DIR / registry()["models"][str(lead)]["file"])
    return m


def usual_rate() -> float:
    """Share of storm days in the last 365 days of data: how stormy an ordinary day has been lately."""
    t = days()
    w = t.loc[last_day() - pd.Timedelta(days=364):last_day(), "storm"].dropna()
    return float(w.mean())


def scores() -> pd.DataFrame:
    f = C.NUMBERS / "FC_daily_scores.csv"
    return pd.read_csv(f) if f.exists() else pd.DataFrame()


def first_day() -> pd.Timestamp:
    return days().index[0] + pd.Timedelta(days=28)


def quality(lead: int) -> dict | None:
    """Test scores for the reported lead nearest to this one."""
    s = scores()
    if s.empty:
        return None
    r = s.iloc[(s["lead_days"] - lead).abs().argsort()].iloc[0]
    return r.to_dict()


def forecast_day(date) -> dict:
    """The answer for one date (see the top of this file)."""
    from . import service as S
    day = pd.Timestamp(date).normalize()
    t, end = days(), last_day()
    out = {"date": str(day.date()), "data_until": str(end.date())}
    if day < first_day():
        return {**out, "mode": "too early",
                "message": f"Pick a day from {first_day().date()} on: earlier days have no data before them."}
    lead = 1 if day <= end else int((day - end).days)
    out["lead_days"] = lead
    if lead > MAX_LEAD:
        cl = pd.read_csv(C.NUMBERS / "FC_daily_climatology.csv").set_index("month").loc[day.month]
        return {**out, "mode": "long range", "p_storm": float(cl["storm_days"] / cl["days"]),
                "climate_days": int(cl["days"]), "climate_storm_days": int(cl["storm_days"]),
                "climate_from": cl["from"], "climate_to": cl["to"]}
    res = {**out, "mode": "check" if day <= end else "forecast"}
    if lead == 1:
        origin = day - S.step() if day <= end else S.D.frame()["sym_h_nT"].last_valid_index()
        m5, info5 = S._model("clf", "storm_24h")
        x = S._features_at(origin, origin)
        p = float(m5.predict_proba(x.to_numpy(), iteration_range=(0, info5["best_iteration"] + 1))[0, 1])
        res.update(model="5-minute model", made_from=str(origin)[:16], line=info5["decision_threshold"])
    else:
        use = min(L for L in LEADS if L >= lead)        # the nearest model whose data is all available
        tt = t.reindex(pd.date_range(t.index[0], day, freq="D"))
        x = lead_features(tt, use).loc[[day]]
        p = float(_daily_model(use).predict_proba(x)[0, 1])
        res.update(model="daily model", made_from=str((day - pd.Timedelta(days=use)).date()),
                   line=registry()["models"][str(use)]["line"], model_lead=use)
    res.update(p_storm=p, flag=p >= res["line"])
    if day <= end and pd.notna(t.loc[day, "sym_min"]):
        sm = float(t.loc[day, "sym_min"])
        res.update(actual_sym_min=sm, actual_severity=C.severity(sm), actual_storm=bool(sm <= STORM))
    return res


def around(date, half: int = 10) -> pd.DataFrame:
    """The same forecast for each day around a date, with what happened (for a small chart)."""
    c = pd.Timestamp(date).normalize()
    rows = []
    for d in pd.date_range(c - pd.Timedelta(days=half), c + pd.Timedelta(days=half), freq="D"):
        r = forecast_day(d)
        if r["mode"] in ("check", "forecast"):
            rows.append({"day": d, "chance": r["p_storm"], "line": r["line"], "actual_sym_min": r.get("actual_sym_min")})
    return pd.DataFrame(rows)


if __name__ == "__main__":
    C.MODEL_DIR.mkdir(parents=True, exist_ok=True)
    train()
