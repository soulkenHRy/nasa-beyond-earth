"""Train and test the forecast models, then save them (forecast/models/) and their test scores (numbers/FC_*).

    .venv/bin/python -m forecast.train            # all measurements, horizons and storm events
    .venv/bin/python -m forecast.train --quick    # a fast run: speed and SYM-H at 1 h, and one storm model

Measurements: XGBoost learns the change from now to now + horizon from the last day of all solar-wind values.
The baseline is persistence (the value now). Storm events: XGBoost classifier for "SYM-H at or below the threshold at
any time in the next H hours", compared with persistence ("a storm now means a storm in the next H hours").
Years: train 2010-2021, choose settings on 2022 (validation), report on 2023 to the end of the file (test).
"""
from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import (average_precision_score, brier_score_loss, precision_recall_curve,
                             precision_recall_fscore_support, r2_score)

from . import config as C
from . import data as D

N_JOBS = max(1, (os.cpu_count() or 2) - 2)


def split_rows(index: pd.DatetimeIndex) -> dict[str, np.ndarray]:
    emb = pd.Timedelta(minutes=C.EMBARGO_MIN)
    tr_end, va_end = pd.Timestamp(C.TRAIN_END), pd.Timestamp(C.VAL_END)
    return {"train": np.flatnonzero(index < tr_end - emb)[::C.EVERY["train"]],
            "val": np.flatnonzero((index >= tr_end) & (index < va_end - emb))[::C.EVERY["val"]],
            "test": np.flatnonzero(index >= va_end)[::C.EVERY["test"]]}


def scores(y: np.ndarray, p: np.ndarray) -> dict:
    e = p - y
    return {"mae": float(np.mean(np.abs(e))), "rmse": float(np.sqrt(np.mean(e ** 2))), "r2": float(r2_score(y, p))}


def binary(y: np.ndarray, pred: np.ndarray) -> dict:
    p, r, f, _ = precision_recall_fscore_support(y, pred, average="binary", zero_division=0)
    return {"precision": float(p), "recall": float(r), "f1": float(f)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()
    t_all = time.time()
    C.MODEL_DIR.mkdir(parents=True, exist_ok=True)
    df = D.frame()
    H = D.horizons(df)
    targets, events = C.TARGETS, dict(C.EVENTS)
    if args.quick:
        targets, H, events = ["speed_km_s", "sym_h_nT"], {"1 h": H["1 h"]}, {"storm_24h": C.EVENTS["storm_24h"]}
    print(f"{len(df):,} rows, {df.index[0]} to {df.index[-1]}, step {D.cadence_min(df)} min; horizons {list(H)}")
    X = D.features(df)
    Xn, feats = X.to_numpy(), list(X.columns)
    rows = split_rows(df.index)
    print(f"{len(feats)} inputs; start times used: " + ", ".join(f"{k} {len(v):,}" for k, v in rows.items()))
    registry = {"features": feats, "regressors": {}, "classifiers": {}}

    reg_rows = []
    for target in targets:
        y = df[target].to_numpy(dtype=float)
        for hname, h in H.items():
            yf = np.r_[y[h:], np.full(h, np.nan)]          # the value h steps later
            d = yf - y                                     # what the model learns: the change
            sel = {k: r[np.isfinite(d[r])] for k, r in rows.items()}
            m = xgb.XGBRegressor(**C.XGB_REG, n_jobs=N_JOBS, random_state=0)
            t0 = time.time()
            m.fit(Xn[sel["train"]], d[sel["train"]], eval_set=[(Xn[sel["val"]], d[sel["val"]])], verbose=False)
            secs = time.time() - t0
            best = int(m.best_iteration)
            rng = (0, best + 1)
            res = yf[sel["val"]] - (y[sel["val"]] + m.predict(Xn[sel["val"]], iteration_range=rng))
            lo, hi = (float(q) for q in np.quantile(res, C.INTERVAL))
            te = sel["test"]
            pt = y[te] + m.predict(Xn[te], iteration_range=rng)
            yt = yf[te]
            sm, sp = scores(yt, pt), scores(yt, y[te])
            name = f"reg_{target}_{h}.ubj"
            m.save_model(C.MODEL_DIR / name)
            registry["regressors"][f"{target}|{hname}"] = {"file": name, "target": target, "horizon": hname,
                                                           "steps": h, "best_iteration": best, "lo": lo, "hi": hi}
            reg_rows.append({"target": target, "name": C.VARIABLES[target][0], "unit": C.VARIABLES[target][1],
                             "horizon": hname, "minutes": C.HORIZON_MIN[hname], "n_train": len(sel["train"]),
                             "n_val": len(sel["val"]), "n_test": len(te), "trees": best + 1,
                             "mae": sm["mae"], "rmse": sm["rmse"], "r2": sm["r2"],
                             "mae_persistence": sp["mae"], "rmse_persistence": sp["rmse"], "r2_persistence": sp["r2"],
                             "skill_rmse_pct": 100 * (1 - sm["rmse"] / sp["rmse"]),
                             "interval_coverage_pct": 100 * float(np.mean((yt >= pt + lo) & (yt <= pt + hi))),
                             "train_seconds": round(secs, 1)})
            r = reg_rows[-1]
            print(f"  {target:13s} {hname:>6s}: RMSE {r['rmse']:8.3f} vs persistence {r['rmse_persistence']:8.3f} "
                  f"(skill {r['skill_rmse_pct']:5.1f}%), R² {r['r2']:.3f}, 80% interval holds "
                  f"{r['interval_coverage_pct']:.0f}%, {best + 1} trees, {secs:.0f}s", flush=True)

    sym = df["sym_h_nT"]
    now = sym.to_numpy(dtype=float)
    step = D.cadence_min(df)
    ev_rows, cal_rows = [], []
    for key, ev in events.items():
        steps = ev["hours"] * 60 // step
        fut = D.future_min(sym, steps).to_numpy()
        label = np.where(np.isfinite(fut), (fut <= ev["threshold"]).astype(float), np.nan)
        sel = {k: r[np.isfinite(label[r])] for k, r in rows.items()}
        clf = xgb.XGBClassifier(**C.XGB_CLF, n_jobs=N_JOBS, random_state=0)
        t0 = time.time()
        clf.fit(Xn[sel["train"]], label[sel["train"]], eval_set=[(Xn[sel["val"]], label[sel["val"]])], verbose=False)
        secs = time.time() - t0
        best = int(clf.best_iteration)
        rng = (0, best + 1)
        pv = clf.predict_proba(Xn[sel["val"]], iteration_range=rng)[:, 1]
        prec, rec, thr = precision_recall_curve(label[sel["val"]], pv)
        f1 = 2 * prec[:-1] * rec[:-1] / np.maximum(prec[:-1] + rec[:-1], 1e-12)
        cut = float(thr[int(np.argmax(f1))])               # decision line: best F1 on the validation year
        te = sel["test"]
        yt, pt = label[te], clf.predict_proba(Xn[te], iteration_range=rng)[:, 1]
        model = binary(yt, pt >= cut)
        pers = binary(yt, np.nan_to_num(now[te], nan=0.0) <= ev["threshold"])
        quiet = np.isfinite(now[te]) & (now[te] > ev["threshold"])        # no storm at the start time
        mq = binary(yt[quiet], pt[quiet] >= cut)
        name = f"clf_{key}.ubj"
        clf.save_model(C.MODEL_DIR / name)
        registry["classifiers"][key] = {"file": name, **ev, "steps": int(steps), "best_iteration": best,
                                        "decision_threshold": cut}
        ev_rows.append({"event": key, "name": ev["name"], "hours": ev["hours"], "threshold_nT": ev["threshold"],
                        "n_train": len(sel["train"]), "n_test": len(te), "positives_test": int(yt.sum()),
                        "base_rate_pct": 100 * float(yt.mean()), "trees": best + 1, "decision_threshold": cut,
                        "precision": model["precision"], "recall": model["recall"], "f1": model["f1"],
                        "pr_auc": float(average_precision_score(yt, pt)), "brier": float(brier_score_loss(yt, pt)),
                        "precision_persistence": pers["precision"], "recall_persistence": pers["recall"],
                        "f1_persistence": pers["f1"], "n_quiet_start": int(quiet.sum()),
                        "positives_quiet_start": int(yt[quiet].sum()),
                        "pr_auc_quiet_start": float(average_precision_score(yt[quiet], pt[quiet]))
                        if yt[quiet].sum() > 0 else float("nan"),
                        "precision_quiet_start": mq["precision"], "recall_quiet_start": mq["recall"],
                        "train_seconds": round(secs, 1)})
        edges = [0, 0.02, 0.05, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0001]
        b = np.digitize(pt, edges) - 1
        for i in range(len(edges) - 1):
            k = b == i
            if k.any():
                cal_rows.append({"event": key, "bin_from": edges[i], "bin_to": min(edges[i + 1], 1.0),
                                 "n": int(k.sum()), "mean_predicted": float(pt[k].mean()),
                                 "observed_rate": float(yt[k].mean())})
        r = ev_rows[-1]
        print(f"  {key:11s}: precision {r['precision']:.2f} recall {r['recall']:.2f} F1 {r['f1']:.2f} "
              f"PR-AUC {r['pr_auc']:.3f} (base rate {r['base_rate_pct']:.1f}%); persistence F1 "
              f"{r['f1_persistence']:.2f}; {secs:.0f}s", flush=True)

    if not args.quick:
        pd.DataFrame(reg_rows).to_csv(C.NUMBERS / "FC_regression_scores.csv", index=False)
        pd.DataFrame(ev_rows).to_csv(C.NUMBERS / "FC_event_scores.csv", index=False)
        pd.DataFrame(cal_rows).to_csv(C.NUMBERS / "FC_calibration.csv", index=False)
        D.storm_events(sym).to_csv(C.NUMBERS / "FC_storm_events.csv", index=False)
        (C.NUMBERS / "FC_dataset_health.json").write_text(json.dumps(D.health(df), indent=1) + "\n")
        meta = {"trained_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
                "xgboost": xgb.__version__, "data_first": str(df.index[0]), "data_last": str(df.index[-1]),
                "train": f"{df.index[0]:%Y-%m-%d} to {pd.Timestamp(C.TRAIN_END) - pd.Timedelta(minutes=C.EMBARGO_MIN):%Y-%m-%d}",
                "validation": f"{C.TRAIN_END} to {pd.Timestamp(C.VAL_END) - pd.Timedelta(minutes=C.EMBARGO_MIN):%Y-%m-%d}",
                "test": f"{C.VAL_END} to {df.index[-1]:%Y-%m-%d}", "every": C.EVERY, "inputs": len(feats),
                "regressors": len(reg_rows), "classifiers": len(ev_rows),
                "minutes": round((time.time() - t_all) / 60, 1)}
        (C.NUMBERS / "FC_training.json").write_text(json.dumps(meta, indent=1) + "\n")
        (C.MODEL_DIR / "registry.json").write_text(json.dumps(registry, indent=1) + "\n")
    print(f"done in {(time.time() - t_all) / 60:.1f} min")


if __name__ == "__main__":
    main()
