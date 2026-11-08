"""What is forecast, how far ahead, and how the years are split. Change things here, then run forecast/train.py."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data_cache" / "space_weather.parquet"
MODEL_DIR = ROOT / "forecast" / "models"            # trained models (not in git: rebuild with forecast/train.py)
NUMBERS = ROOT / "numbers"                          # the test scores, like every other number in the project
TIME_COL = "datetime_utc"

# column: (name, unit). Units as in the OMNI file.
VARIABLES = {
    "speed_km_s": ("Solar wind speed", "km/s"),
    "bt_nT": ("Magnetic field strength |B|", "nT"),
    "bz_gsm_nT": ("Bz, north-south field (GSM)", "nT"),
    "by_gsm_nT": ("By, east-west field (GSM)", "nT"),
    "density_cm3": ("Proton density", "per cm³"),
    "temp_K": ("Proton temperature", "K"),
    "pressure_nPa": ("Flow pressure", "nPa"),
    "efield_mV_m": ("Electric field", "mV/m"),
    "ae_nT": ("AE index (auroral activity)", "nT"),
    "al_nT": ("AL index", "nT"),
    "sym_h_nT": ("SYM-H (geomagnetic storm meter)", "nT"),
    "pcn": ("PCN index (polar cap)", ""),
    "proton_flux_10mev": ("Proton flux above 10 MeV", "pfu"),
}

# Measurements with a forecast model. Any column that data.candidate_targets() accepts can be added.
TARGETS = ["speed_km_s", "bt_nT", "bz_gsm_nT", "density_cm3", "pressure_nPa", "sym_h_nT"]
# Measurements used as inputs (their recent past) for every model.
DRIVERS = ["speed_km_s", "bt_nT", "bz_gsm_nT", "by_gsm_nT", "density_cm3", "pressure_nPa", "sym_h_nT", "ae_nT"]

# Forecast horizons in minutes. A horizon is used only if it is a whole number of time steps of the file.
HORIZON_MIN = {"5 min": 5, "15 min": 15, "30 min": 30, "1 h": 60, "3 h": 180, "6 h": 360, "12 h": 720, "24 h": 1440}

# Storm events (SYM-H thresholds as for Dst in Gonzalez et al. 1994: -50 nT moderate, -100 nT intense).
EVENTS = {
    "storm_6h": {"threshold": -50, "hours": 6, "name": "Storm (SYM-H ≤ -50 nT) within 6 h"},
    "storm_24h": {"threshold": -50, "hours": 24, "name": "Storm (SYM-H ≤ -50 nT) within 24 h"},
    "strong_6h": {"threshold": -100, "hours": 6, "name": "Strong storm (SYM-H ≤ -100 nT) within 6 h"},
    "strong_24h": {"threshold": -100, "hours": 24, "name": "Strong storm (SYM-H ≤ -100 nT) within 24 h"},
}
# Severity of a SYM-H value (upper edges, nT).
SEVERITY = [(-250, "Extreme"), (-100, "Intense"), (-50, "Moderate"), (-30, "Weak")]
QUIET = "Quiet"
STORM_JOIN_HOURS = 12                               # storms closer than this are one event (as in finding 13)

# Chronological split by forecast start time. A gap of one day (the longest horizon) at each edge keeps the
# answers of one part out of the next part.
TRAIN_END = "2022-01-01"
VAL_END = "2023-01-01"
EMBARGO_MIN = 1440
# Use every k-th start time (neighbouring 5-minute rows are nearly the same, so this loses little).
EVERY = {"train": 12, "val": 6, "test": 3}
INTERVAL = (0.10, 0.90)                             # 80% interval, from validation errors

XGB_REG = dict(n_estimators=600, learning_rate=0.1, max_depth=6, min_child_weight=5, subsample=0.8,
               colsample_bytree=0.8, tree_method="hist", early_stopping_rounds=40, eval_metric="rmse")
XGB_CLF = dict(n_estimators=700, learning_rate=0.05, max_depth=5, min_child_weight=10, subsample=0.8,
               colsample_bytree=0.8, tree_method="hist", early_stopping_rounds=50, eval_metric="aucpr")


def severity(sym_h: float) -> str:
    for edge, name in SEVERITY:
        if sym_h <= edge:
            return name
    return QUIET
