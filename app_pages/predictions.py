"""Predictions: space-weather forecasts from the NASA OMNI 5-minute file.

Six tabs: Overview, Forecast explorer, Storm outlook, Model performance, Dataset health, Method. The models are
trained once by forecast/train.py (XGBoost, tested against persistence) and only read here. "Now" on this page is
the last reading in the file. Charts are plain SVG Plotly (no WebGL), so they work in any browser.
"""
from __future__ import annotations

import html
from datetime import timedelta

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from forecast import config as C
from forecast import service as S

# ---------------------------------------------------------------------------------------------- look
NAVY, GRID, INK, MUTED = "#0b1222", "#1f2b47", "#e6ecf8", "#9aa8c7"
OBS, FC, PERS, ALERT = "#3fd0ff", "#ffb547", "#8a96b2", "#ff5a5f"
SEV_COL = {"Quiet": "#3ecf8e", "Weak": "#c9d36a", "Moderate": "#ffb547", "Intense": "#ff7a45", "Extreme": "#ff4d6d"}
DIGITS = {"speed_km_s": 0, "bt_nT": 1, "bz_gsm_nT": 1, "by_gsm_nT": 1, "density_cm3": 2, "temp_K": 0,
          "pressure_nPa": 2, "efield_mV_m": 2, "ae_nT": 0, "al_nT": 0, "sym_h_nT": 0, "pcn": 2, "proton_flux_10mev": 2}
PLOT_CFG = {"displaylogo": False, "scrollZoom": False, "modeBarButtonsToRemove": ["lasso2d", "select2d"]}

st.markdown("""
<style>
.sw-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:6px 0 16px}
.sw-card{background:#0b1222;border:1px solid #1f2b47;border-radius:10px;padding:12px 14px;color:#e6ecf8;
  animation:swfade .5s ease both}
.sw-label{font-size:12px;color:#9aa8c7;letter-spacing:.04em;text-transform:uppercase}
.sw-value{font-size:26px;font-weight:600;font-variant-numeric:tabular-nums;margin-top:4px;color:#ffffff}
.sw-unit{font-size:13px;color:#9aa8c7;font-weight:400;margin-left:5px}
.sw-trend{font-size:12.5px;margin-top:3px;color:#9aa8c7;font-variant-numeric:tabular-nums}
.sw-time{font-size:11.5px;color:#6f7c9c;margin-top:2px}
.sw-band{background:#0b1222;border:1px solid #1f2b47;border-left:4px solid #3fd0ff;border-radius:8px;
  padding:10px 14px;color:#e6ecf8;margin:6px 0 10px;animation:swfade .5s ease both}
.sw-band b{color:#ffffff}
.sw-band.warn{border-left-color:#ffb547}.sw-band.alert{border-left-color:#ff5a5f}
.sw-pill{display:inline-block;padding:1px 9px;border-radius:999px;font-size:12px;font-weight:600;color:#0b1222;
  margin-left:6px}
.sw-small{font-size:12.5px;color:#9aa8c7}
@keyframes swfade{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}
</style>""", unsafe_allow_html=True)


def fmt(col: str, v, signed: bool = False) -> str:
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "–"
    d = DIGITS.get(col, 2)
    return f"{v:+,.{d}f}" if signed else f"{v:,.{d}f}"


def pill(sev: str) -> str:
    return f'<span class="sw-pill" style="background:{SEV_COL.get(sev, "#9aa8c7")}">{html.escape(sev)}</span>'


def band(text: str, kind: str = "") -> None:
    st.markdown(f'<div class="sw-band {kind}">{text}</div>', unsafe_allow_html=True)


def dark(fig: go.Figure, height: int = 420, ytitle: str | None = None, legend: bool = True) -> go.Figure:
    fig.update_layout(template="plotly_dark", paper_bgcolor=NAVY, plot_bgcolor=NAVY, height=height,
                      font=dict(color=INK, size=13), margin=dict(l=64, r=18, t=36 if legend else 16, b=44),
                      hovermode="x unified", showlegend=legend,
                      legend=dict(orientation="h", y=1.04, x=0, yanchor="bottom", bgcolor="rgba(0,0,0,0)"),
                      hoverlabel=dict(bgcolor="#14203a", font=dict(color=INK)))
    fig.update_xaxes(gridcolor=GRID, zeroline=False, linecolor=GRID)
    fig.update_yaxes(gridcolor=GRID, zeroline=False, linecolor=GRID)
    if ytitle:
        fig.update_yaxes(title_text=ytitle)
    return fig


def show(fig: go.Figure, key: str) -> None:
    st.plotly_chart(fig, theme=None, key=key, config=PLOT_CFG, width="stretch")


def band_shape(b: pd.DataFrame) -> tuple[list, list]:
    """The interval as closed shapes, one per stretch of time with no missing forecast, so gaps stay empty."""
    ok = b["low"].notna().to_numpy() & b["high"].notna().to_numpy()
    xs, ys = [], []
    i, n = 0, len(b)
    while i < n:
        if not ok[i]:
            i += 1
            continue
        j = i
        while j < n and ok[j]:
            j += 1
        t = list(b["time"].iloc[i:j])
        xs += t + t[::-1] + [None]
        ys += list(b["high"].iloc[i:j]) + list(b["low"].iloc[i:j])[::-1] + [None]
        i = j
    return xs, ys


def label_of(col: str) -> str:
    u = S.unit(col)
    return f"{S.name(col)} ({u})" if u else S.name(col)


# ---------------------------------------------------------------------------------------------- page
st.title("Predictions")
have_data, ready = S.have_data(), S.models_ready()
perf = S.performance()
health = S.dataset_health()
if have_data:
    last_time = pd.Timestamp(health["last"])
    st.caption(f"Space-weather forecasts from the NASA OMNI file of 5-minute readings, {health['first'][:10]} to "
               f"{health['last'][:16]} UTC. The file stops there, so on this page \"now\" means the last reading "
               "in the file, not today. Forecasts come from XGBoost models trained on 2010 to 2021 and tested on "
               "2023 onward; every score shown was measured on those test years.")
else:
    st.warning("The data file `data_cache/space_weather.parquet` is not in this copy of the project, so live "
               "forecasts are off. The test scores and the data summary below were saved when the models were trained.")
if have_data and not ready:
    st.info("The forecast models are not trained yet. Run `.venv/bin/python -m forecast.train` from the project "
            "folder (about 15 minutes); observations and data health work without them.")

tabs = st.tabs(["Overview", "Forecast explorer", "Storm outlook", "Model performance", "Dataset health", "Method"])

# ============================================================================================== Overview
with tabs[0]:
    if not have_data:
        st.info("Needs the data file.")
    else:
        lat = S.latest()
        out = S.outlook() if ready else None
        sym = lat["values"]["sym_h_nT"]
        sev_now = C.severity(sym["value"])
        band(f"<b>Last reading in the file:</b> {lat['time'][:16]} UTC (solar wind). &nbsp;Geomagnetic activity: "
             f"SYM-H {fmt('sym_h_nT', sym['value'])} nT {pill(sev_now)} at {sym['time'][:16]} UTC, its last reading "
             "(the SYM-H column stops earlier than the solar-wind columns).")
        if out:
            flagged = [e for e in out["events"] if e["flagged"]]
            if flagged:
                strong = any(e["threshold_nT"] <= -100 for e in flagged)
                items = "; ".join(f"{html.escape(e['name'])}: {100 * e['probability']:.0f}%" for e in flagged)
                band(f"<b>Storm alert from the models</b> (made at {out['origin'][:16]} UTC): {items}. A model "
                     "flags an event when its chance passes the line chosen on the validation year; see Model "
                     "performance for how often such flags were right.", "alert" if strong else "warn")
            else:
                worst = max(out["events"], key=lambda e: e["probability"])
                band(f"<b>No storm flagged</b> for the next 6 or 24 hours (models run at {out['origin'][:16]} UTC). "
                     f"Highest chance: {html.escape(worst['name'])}, {100 * worst['probability']:.0f}%.")
        cards = []
        for c in S.KEY_VARIABLES:
            v = lat["values"].get(c)
            if not v:
                continue
            ch = v["change_1h"]
            arrow = "–" if ch is None else ("▲" if ch > 0 else "▼" if ch < 0 else "•")
            trend = "no reading an hour before" if ch is None else f"{arrow} {fmt(c, ch, signed=True)} in 1 h"
            cards.append(f'<div class="sw-card"><div class="sw-label">{html.escape(v["name"])}</div>'
                         f'<div class="sw-value">{fmt(c, v["value"])}<span class="sw-unit">{html.escape(v["unit"])}'
                         f'</span></div><div class="sw-trend">{trend}</div>'
                         f'<div class="sw-time">{v["time"][:16]} UTC</div></div>')
        st.markdown(f'<div class="sw-grid">{"".join(cards)}</div>', unsafe_allow_html=True)

        cols = ["speed_km_s", "bz_gsm_nT", "density_cm3", "sym_h_nT"]
        end = min(pd.Timestamp(lat["values"][c]["time"]) for c in cols)
        st.subheader(f"The last three days with all four readings (to {end:%Y-%m-%d %H:%M} UTC)")
        fig = make_subplots(rows=len(cols), cols=1, shared_xaxes=True, vertical_spacing=0.04,
                            subplot_titles=[label_of(c) for c in cols])
        for i, c in enumerate(cols, start=1):
            s = S.history(c, end - timedelta(days=3), end)
            fig.add_trace(go.Scatter(x=s.index, y=s.values, mode="lines", line=dict(color=OBS, width=1.6),
                                     name=S.name(c), hovertemplate=f"%{{y:.{DIGITS[c]}f}} {S.unit(c)}<extra></extra>"),
                          row=i, col=1)
        for y0, col in [(-50, FC), (-100, ALERT)]:
            fig.add_hline(y=y0, line=dict(color=col, width=1, dash="dot"), row=4, col=1)
        fig.add_hline(y=0, line=dict(color=MUTED, width=1, dash="dot"), row=2, col=1)
        dark(fig, height=640, legend=False)
        fig.update_annotations(font=dict(size=12.5, color=MUTED), x=0, xanchor="left")
        show(fig, "overview_72h")

        st.subheader("What can be forecast")
        reg, ev = perf["regression"], perf["events"]
        if ready and not reg.empty:
            hz = list(S.horizons())
            st.markdown(
                f"* **{reg['target'].nunique()} measurements** forecast {hz[0]} to {hz[-1]} ahead "
                f"({len(hz)} horizons, {len(reg)} models): "
                + ", ".join(S.name(t) for t in reg["target"].unique()) + ".\n"
                f"* **{len(ev)} storm models:** " + "; ".join(ev["name"]) + ".\n"
                f"* Trained {perf['training'].get('trained_at', '?')} on {perf['training'].get('train', '?')}; "
                f"tested on {perf['training'].get('test', '?')}.")
        else:
            st.info("No models yet.")

# ============================================================================================== Explorer
with tabs[1]:
    if not (have_data and ready):
        st.info("Needs the data file and trained models.")
    else:
        targets = [c for c in C.TARGETS if any(m["column"] == c and m["forecast_horizons"] for m in S.measurements())]
        c1, c2, c3 = st.columns([1.3, 0.8, 1.4])
        col = c1.selectbox("Measurement", targets, format_func=label_of, key="fx_col")
        hz = c2.selectbox("Forecast horizon", list(S.horizons()), index=3, key="fx_h")
        first, last = pd.Timestamp(health["first"]).date(), pd.Timestamp(health["last"]).date()
        col_last = pd.Timestamp(health["columns"][col]["last_time"]).date()
        rng = c3.date_input("Dates (UTC)", value=(col_last - timedelta(days=6), col_last), min_value=first,
                            max_value=last, key=f"fx_dates_{col}",
                            help=f"Up to 31 days at a time. {S.name(col)} has readings up to {col_last}.")
        t1, t2, _ = st.columns([1, 1, 2])
        show_pers = t1.toggle("Show persistence", value=True, help="The simplest forecast: the value stays as it is now.")
        show_band = t2.toggle("Show 80% interval", value=True)
        if not isinstance(rng, (list, tuple)) or len(rng) != 2:
            st.info("Pick an end date too.")
        else:
            d0, d1 = rng
            if (d1 - d0).days > 31:
                d1 = d0 + timedelta(days=31)
                st.warning(f"Showing 31 days, {d0} to {d1}.")
            start, end = pd.Timestamp(d0), min(pd.Timestamp(d1) + timedelta(days=1) - S.step(), last_time)
            period = S.period_of(start)
            with st.spinner("Running the model over these dates ..."):
                bt = S.backtest(col, hz, start, end)
                fut = S.future(col) if end >= last_time else None
            note = {"train": "inside the training years (2010 to 2021): the model has seen these answers, so this "
                             "looks better than it really is",
                    "validation": "inside the validation year (2022), used to tune the models",
                    "test": "inside the test years (2023 onward): the model never saw these answers"}[period]
            band(f"<b>{html.escape(S.name(col))}, {hz} ahead.</b> Each forecast point was made {hz} before its time, "
                 f"from readings up to then only. These dates are {note}.", "warn" if period == "train" else "")
            u = S.unit(col)
            d = DIGITS[col]
            k = max(1, len(bt) // 3000)
            b = bt.iloc[::k]
            fig = go.Figure()
            if show_band:
                bx, by = band_shape(b)
                fig.add_trace(go.Scatter(x=bx, y=by, mode="lines", line=dict(width=0), fill="toself",
                                         fillcolor="rgba(255,181,71,0.18)", name="80% interval", hoverinfo="skip"))
            fig.add_trace(go.Scatter(x=b["time"], y=b["observed"], mode="lines", name="observed",
                                     line=dict(color=OBS, width=1.8),
                                     hovertemplate=f"observed %{{y:.{d}f}} {u}<extra></extra>"))
            if show_pers:
                fig.add_trace(go.Scatter(x=b["time"], y=b["persistence"], mode="lines", name=f"persistence ({hz} before)",
                                         line=dict(color=PERS, width=1.2, dash="dot"),
                                         hovertemplate=f"persistence %{{y:.{d}f}} {u}<extra></extra>"))
            fig.add_trace(go.Scatter(x=b["time"], y=b["forecast"], mode="lines", name=f"XGBoost ({hz} before)",
                                     line=dict(color=FC, width=1.6, dash="dash"),
                                     hovertemplate=f"forecast %{{y:.{d}f}} {u}<extra></extra>"))
            if fut is not None and not fut.empty:
                origin = fut.attrs["origin"]
                fig.add_trace(go.Scatter(
                    x=[origin, *fut["time"]], y=[fut.attrs["origin_value"], *fut["forecast"]], mode="lines+markers",
                    name="forecast past the end of the file", line=dict(color=FC, width=2),
                    marker=dict(size=7, color=FC, line=dict(color=NAVY, width=1)),
                    error_y=dict(type="data", symmetric=False, color=FC, thickness=1.2, width=4,
                                 array=[0, *(fut["high"] - fut["forecast"])],
                                 arrayminus=[0, *(fut["forecast"] - fut["low"])]),
                    customdata=["now", *fut["horizon"]],
                    hovertemplate=f"%{{customdata}} ahead: %{{y:.{d}f}} {u}<extra></extra>"))
                fig.add_vline(x=origin, line=dict(color=MUTED, width=1, dash="dash"))
                fig.add_annotation(x=origin, y=1, yref="paper", text="last reading", showarrow=False, xanchor="right",
                                   yanchor="bottom", font=dict(color=MUTED, size=12))
            dark(fig, height=470, ytitle=u)
            fig.update_xaxes(rangeselector=dict(
                buttons=[dict(count=1, label="1 d", step="day", stepmode="backward"),
                         dict(count=3, label="3 d", step="day", stepmode="backward"), dict(step="all", label="all")],
                x=1, xanchor="right", y=1.0, yanchor="bottom", bgcolor="#14203a", activecolor="#2a3b63",
                font=dict(color=INK)))
            fig.update_layout(margin=dict(t=64), legend=dict(y=1.0, yanchor="bottom", x=0))
            show(fig, "explorer")
            ws = S.window_scores(bt)
            reg = perf["regression"]
            row = reg[(reg["target"] == col) & (reg["horizon"] == hz)]
            m1, m2, m3, m4 = st.columns(4)
            if ws:
                m1.metric(f"Error on these dates (MAE, {u})", fmt(col, ws["mae"]),
                          delta=f"{fmt(col, ws['mae'] - ws['mae_persistence'], signed=True)} vs persistence",
                          delta_color="inverse")
                m2.metric(f"RMSE on these dates ({u})", fmt(col, ws["rmse"]),
                          delta=f"{fmt(col, ws['rmse'] - ws['rmse_persistence'], signed=True)} vs persistence",
                          delta_color="inverse")
                m3.metric("Inside the 80% interval", f"{ws['inside_interval_pct']:.0f}%")
            if not row.empty:
                r = row.iloc[0]
                m4.metric("Test years: R² (persistence)", f"{r['r2']:.3f}", delta=f"{r['r2_persistence']:.3f}",
                          delta_color="off")
                st.caption(f"Test years 2023 onward, {int(r['n_test']):,} forecasts: RMSE {r['rmse']:.3g} {u} against "
                           f"{r['rmse_persistence']:.3g} for persistence ({r['skill_rmse_pct']:.1f}% better); the 80% "
                           f"interval held {r['interval_coverage_pct']:.0f}% of the time.")
            if fut is not None and not fut.empty:
                st.caption(f"Forecast past the end of the file: made at {str(fut.attrs['origin'])[:16]} UTC, the last "
                           f"reading of this measurement. The bars are 80% intervals.")
            with st.expander("The numbers behind the chart"):
                st.dataframe(bt.round({c_: 3 for c_ in bt.columns if c_ != "time"}), hide_index=True, width="stretch")
                st.download_button("Download as CSV", bt.to_csv(index=False).encode(), file_name=f"forecast_{col}_{hz}.csv",
                                   mime="text/csv")

# ============================================================================================== Storms
with tabs[2]:
    hist = S.storm_history()
    if have_data and ready:
        out = S.outlook()
        st.subheader("Storm chances for the next hours")
        st.caption(f"Made at the last SYM-H reading in the file, {out['origin'][:16]} UTC, when SYM-H was "
                   f"{out['sym_h_now']:.0f} nT ({out['severity_now']}). Each bar is a model's chance; the white tick is "
                   "where that model starts flagging (the line with the best F1 on the validation year).")
        ev = pd.DataFrame(out["events"])
        scores = perf["events"].set_index("event") if not perf["events"].empty else None
        fig = go.Figure(go.Bar(
            y=ev["name"], x=100 * ev["probability"], orientation="h",
            marker=dict(color=[ALERT if f else OBS for f in ev["flagged"]]),
            text=[f"{100 * p:.0f}%" for p in ev["probability"]], textposition="outside",
            hovertemplate="%{y}: %{x:.1f}%<extra></extra>"))
        for i, r in ev.iterrows():
            fig.add_shape(type="line", x0=100 * r["decision_threshold"], x1=100 * r["decision_threshold"],
                          y0=i - 0.42, y1=i + 0.42, line=dict(color="#ffffff", width=2))
        dark(fig, height=300, legend=False)
        fig.update_xaxes(range=[0, 105], title_text="chance (%)")
        fig.update_layout(hovermode="closest")
        show(fig, "storm_bars")
        if scores is not None:
            st.caption("On the test years, when these models flagged a storm they were right "
                       + ", ".join(f"{100 * scores.loc[e, 'precision']:.0f}% of the time ({scores.loc[e, 'name']})"
                                   for e in ev["event"] if e in scores.index) + ".")

        st.subheader("Forecast storm meter (SYM-H) and severity")
        path = out["sym_h_path"]
        end = pd.Timestamp(out["origin"])
        s = S.history("sym_h_nT", end - timedelta(days=2), end)
        fig = go.Figure()
        for lo, hi, name_ in [(-30, 60, "Quiet"), (-50, -30, "Weak"), (-100, -50, "Moderate"), (-250, -100, "Intense")]:
            fig.add_hrect(y0=lo, y1=hi, fillcolor=SEV_COL[name_], opacity=0.07, line_width=0,
                          annotation_text=name_, annotation_position="right",
                          annotation=dict(font=dict(color=SEV_COL[name_], size=11)))
        fig.add_trace(go.Scatter(x=s.index, y=s.values, mode="lines", name="observed SYM-H",
                                 line=dict(color=OBS, width=1.8), hovertemplate="%{y:.0f} nT<extra></extra>"))
        fig.add_trace(go.Scatter(
            x=[end, *path["time"]], y=[out["sym_h_now"], *path["forecast"]], mode="lines+markers", name="forecast",
            line=dict(color=FC, width=2), marker=dict(size=7, color=FC),
            error_y=dict(type="data", symmetric=False, color=FC, array=[0, *(path["high"] - path["forecast"])],
                         arrayminus=[0, *(path["forecast"] - path["low"])], thickness=1.2, width=4),
            customdata=[["now", out["severity_now"]], *path[["horizon", "severity"]].to_numpy().tolist()],
            hovertemplate="%{customdata[0]}: %{y:.0f} nT (%{customdata[1]})<extra></extra>"))
        lo_y = min(-60.0, float(np.nanmin(path["low"])) - 10, float(np.nanmin(s.values)) - 10)
        dark(fig, height=380, ytitle="nT")
        fig.update_yaxes(range=[lo_y, max(30.0, float(np.nanmax(s.values)) + 10)])
        show(fig, "sym_path")
        worst = path.loc[path["forecast"].idxmin()]
        st.caption(f"Lowest forecast value: {worst['forecast']:.0f} nT at {worst['horizon']} ahead "
                   f"({worst['severity']}); the bars are 80% intervals from the validation year.")

        st.subheader("The last 30 days: storm meter and the 24-hour storm model")
        days_from = end - timedelta(days=30)
        sym30 = S.history("sym_h_nT", days_from, end)
        pr = S.event_probabilities("storm_24h", days_from, end)
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08, row_heights=[0.6, 0.4],
                            subplot_titles=["SYM-H (nT)", "Chance of a storm (SYM-H ≤ -50 nT) within 24 h, %"])
        fig.add_trace(go.Scatter(x=sym30.index, y=sym30.values, mode="lines", line=dict(color=OBS, width=1.4),
                                 name="SYM-H", hovertemplate="%{y:.0f} nT<extra></extra>"), row=1, col=1)
        for y0, colr in [(-50, FC), (-100, ALERT)]:
            fig.add_hline(y=y0, line=dict(color=colr, width=1, dash="dot"), row=1, col=1)
        fig.add_trace(go.Scatter(x=pr["time"], y=100 * pr["probability"], mode="lines", line=dict(color=FC, width=1.4),
                                 fill="tozeroy", fillcolor="rgba(255,181,71,0.15)", name="storm chance",
                                 hovertemplate="%{y:.0f}%<extra></extra>"), row=2, col=1)
        cut = S.registry()["classifiers"]["storm_24h"]["decision_threshold"]
        fig.add_hline(y=100 * cut, line=dict(color="#ffffff", width=1, dash="dash"), row=2, col=1)
        dark(fig, height=470, legend=False)
        fig.update_annotations(font=dict(size=12.5, color=MUTED), x=0, xanchor="left")
        fig.update_yaxes(range=[0, 100], row=2, col=1)
        show(fig, "timeline30")
    elif not have_data:
        st.info("Live storm chances need the data file; the storm list below is saved.")
    else:
        st.info("Storm chances need trained models; the storm list below comes from the data.")

    st.subheader("Storms in the file, 2010 to now")
    if hist.empty:
        st.info("No storm list.")
    else:
        hist = hist.copy()
        hist["year"] = pd.to_datetime(hist["time_of_min"]).dt.year
        order = ["Moderate", "Intense", "Extreme"]
        f1, f2 = st.columns([2, 1])
        y0, y1 = int(hist["year"].min()), int(hist["year"].max())
        yr = f1.slider("Years", y0, y1, (y0, y1), key="storm_years") if y1 > y0 else (y0, y1)
        sev_min = f2.selectbox("At least", order, key="storm_sev")
        keep = hist["year"].between(*yr) & hist["severity"].map(lambda v: order.index(v) if v in order else -1).ge(
            order.index(sev_min))
        h = hist[keep]
        fig = go.Figure()
        for sev in order:
            part = h[h["severity"] == sev]
            if part.empty:
                continue
            fig.add_trace(go.Scatter(
                x=part["time_of_min"], y=part["min_sym_h"], mode="markers", name=sev,
                marker=dict(color=SEV_COL[sev], size=np.clip(4 + part["hours"] ** 0.5 * 1.6, 5, 22),
                            line=dict(color=NAVY, width=1), opacity=0.9),
                customdata=part[["hours"]].to_numpy(),
                hovertemplate="%{x|%Y-%m-%d %H:%M}: lowest %{y:.0f} nT, %{customdata[0]:.0f} h below -50<extra></extra>"))
        dark(fig, height=380, ytitle="lowest SYM-H (nT)")
        fig.update_layout(hovermode="closest")
        show(fig, "storm_history")
        counts = h["severity"].value_counts()
        st.caption(f"{len(h):,} storms shown (" + ", ".join(f"{counts.get(s_, 0):,} {s_.lower()}" for s_ in order)
                   + f"). A storm is SYM-H at or below -50 nT; storms less than {C.STORM_JOIN_HOURS} hours apart count "
                   "as one. Dot size: hours below -50 nT.")
        with st.expander("Storm list"):
            st.dataframe(h.sort_values("time_of_min", ascending=False)[
                ["time_of_min", "min_sym_h", "severity", "hours", "start", "end"]], hide_index=True, width="stretch")

    if have_data:
        st.subheader("Unusual readings in the last 30 days")
        un = S.unusual(30)
        if un.empty:
            st.success("No reading in the last 30 days of the file is outside the 0.05% to 99.95% range of 2010 to now.")
        else:
            cnt = un.groupby("measurement").size().sort_values(ascending=False)
            st.markdown(" · ".join(f"**{m}**: {n:,}" for m, n in cnt.items()))
            st.caption("Readings outside the range that holds 99.9% of all readings since 2010. This is a statistical "
                       "flag, not a forecast; big storms and data glitches both show up here.")
            st.dataframe(un.sort_values("time", ascending=False).head(200)[
                ["time", "measurement", "value", "unit", "side", "usual_low", "usual_high"]].round(
                {"value": 2, "usual_low": 2, "usual_high": 2}),
                hide_index=True, width="stretch")

# ============================================================================================== Performance
with tabs[3]:
    reg, ev, cal, tr = perf["regression"], perf["events"], perf["calibration"], perf["training"]
    if reg.empty:
        st.info("No test scores yet: train the models with `.venv/bin/python -m forecast.train`.")
    else:
        status = "trained" if ready else "scores saved, model files not in this copy"
        band(f"<b>Status:</b> {status}. XGBoost {html.escape(str(tr.get('xgboost', '?')))}, trained "
             f"{html.escape(str(tr.get('trained_at', '?')))} in {tr.get('minutes', '?')} minutes. "
             f"Train {html.escape(str(tr.get('train', '?')))}, validation {html.escape(str(tr.get('validation', '?')))}, "
             f"test {html.escape(str(tr.get('test', '?')))}. {tr.get('inputs', '?')} inputs per forecast. "
             "All scores below are from the test years only.")
        pick = st.selectbox("Measurement", list(reg["target"].unique()), format_func=label_of, key="perf_col")
        r = reg[reg["target"] == pick].sort_values("minutes")
        u = S.unit(pick)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Error by horizon** (lower is better)")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=r["horizon"], y=r["rmse_persistence"], mode="lines+markers", name="persistence",
                                     line=dict(color=PERS, width=2, dash="dot"), marker=dict(size=8)))
            fig.add_trace(go.Scatter(x=r["horizon"], y=r["rmse"], mode="lines+markers", name="XGBoost",
                                     line=dict(color=FC, width=2.4), marker=dict(size=8)))
            dark(fig, height=360, ytitle=f"RMSE ({u})")
            show(fig, "perf_rmse")
        with c2:
            st.markdown("**Skill:** how much lower the error is than persistence's")
            fig = go.Figure(go.Bar(x=r["horizon"], y=r["skill_rmse_pct"],
                                   marker=dict(color=[OBS if v >= 0 else ALERT for v in r["skill_rmse_pct"]]),
                                   text=[f"{v:.1f}%" for v in r["skill_rmse_pct"]], textposition="outside",
                                   hovertemplate="%{x}: %{y:.1f}% lower RMSE than persistence<extra></extra>"))
            dark(fig, height=360, ytitle="% better than persistence", legend=False)
            fig.update_layout(hovermode="closest")
            show(fig, "perf_skill")
        worse = r[r["skill_rmse_pct"] <= 0]
        if not worse.empty:
            band(f"<b>Worse than persistence</b> for {html.escape(S.name(pick))} at " + ", ".join(worse["horizon"])
                 + " on the test years. Over such short times the value now is very hard to beat; use persistence "
                 "there.", "warn")
        table = reg.assign(measurement=reg["target"].map(S.name))[
            ["measurement", "unit", "horizon", "n_test", "mae", "rmse", "r2", "mae_persistence", "rmse_persistence",
             "r2_persistence", "skill_rmse_pct", "interval_coverage_pct", "trees"]]
        st.dataframe(table.round(3), hide_index=True, width="stretch")

    if not ev.empty:
        st.subheader("Storm models")
        t = ev[["name", "n_test", "base_rate_pct", "precision", "recall", "f1", "pr_auc", "brier",
                "precision_persistence", "recall_persistence", "f1_persistence", "precision_quiet_start",
                "recall_quiet_start", "pr_auc_quiet_start", "decision_threshold"]]
        st.dataframe(t.round(3), hide_index=True, width="stretch")
        st.caption("Precision: of the times a model flagged a storm, the share that had one. Recall: of the storms, the "
                   "share flagged. PR-AUC: precision and recall over every line, 1 is perfect and the base rate is "
                   "chance. Persistence: \"a storm now means a storm soon\". Quiet start: only start times with no "
                   "storm yet, the hard case.")
        if not cal.empty:
            ek = st.selectbox("Calibration of", list(ev["event"]), format_func=lambda k: ev.set_index("event").loc[k, "name"],
                              key="cal_ev")
            cc = cal[cal["event"] == ek]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", line=dict(color=PERS, dash="dot"),
                                     name="perfect", hoverinfo="skip"))
            fig.add_trace(go.Scatter(x=cc["mean_predicted"], y=cc["observed_rate"], mode="lines+markers",
                                     name="model", line=dict(color=FC, width=2.4),
                                     marker=dict(size=np.clip(np.sqrt(cc["n"]) / 4, 6, 18)),
                                     customdata=cc[["n"]].to_numpy(),
                                     hovertemplate="said %{x:.2f}, happened %{y:.2f} (%{customdata[0]:,} cases)"
                                                   "<extra></extra>"))
            dark(fig, height=360)
            fig.update_xaxes(title_text="chance the model gave", range=[0, 1])
            fig.update_yaxes(title_text="share that had a storm", range=[0, 1])
            fig.update_layout(hovermode="closest")
            show(fig, "calibration")
    st.caption("Not tried yet: LightGBM and recurrent networks (LSTM/GRU). Only XGBoost and persistence are scored here.")

# ============================================================================================== Health
with tabs[4]:
    if not health:
        st.info("No data summary.")
    else:
        cols = health["columns"]
        cards = [("First reading", health["first"][:16]), ("Last reading", health["last"][:16]),
                 ("Readings", f"{health['rows']:,}"), ("Time step", f"{health['step_min']} min"),
                 ("Regular time step", "yes" if health["regular"] else "no"),
                 ("Duplicate times", f"{health['duplicate_times']:,}")]
        st.markdown('<div class="sw-grid">' + "".join(
            f'<div class="sw-card"><div class="sw-label">{a}</div><div class="sw-value" style="font-size:20px">{b}'
            f'</div></div>' for a, b in cards) + "</div>", unsafe_allow_html=True)
        miss = pd.DataFrame([{"column": c, "measurement": v["name"], "missing_pct": v["missing_pct"]}
                             for c, v in cols.items()]).sort_values("missing_pct")
        fig = go.Figure(go.Bar(y=miss["measurement"], x=miss["missing_pct"], orientation="h",
                               marker=dict(color=[ALERT if v > 15 else OBS for v in miss["missing_pct"]]),
                               text=[f"{v:.1f}%" for v in miss["missing_pct"]], textposition="outside",
                               hovertemplate="%{y}: %{x:.1f}% missing<extra></extra>"))
        dark(fig, height=430, legend=False)
        fig.update_xaxes(title_text="readings missing (%)", range=[0, max(5.0, float(miss["missing_pct"].max())) * 1.15])
        fig.update_layout(hovermode="closest")
        st.markdown("**Missing readings by measurement**")
        show(fig, "missing")
        yrs = health["present_pct_by_year"]
        order_cols = list(miss["column"])
        z = [[yrs[y].get(c, np.nan) for y in yrs] for c in order_cols]
        fig = go.Figure(go.Heatmap(z=z, x=list(yrs), y=[S.name(c) for c in order_cols], zmin=0, zmax=100,
                                   colorscale=[[0, "#3a0d1a"], [0.6, "#7a5a12"], [0.9, "#1f6f8b"], [1, OBS]],
                                   colorbar=dict(title="% present"),
                                   hovertemplate="%{y}, %{x}: %{z:.1f}% present<extra></extra>"))
        dark(fig, height=470, legend=False)
        fig.update_layout(hovermode="closest")
        st.markdown("**Readings present, by year** (% of the 5-minute slots with a value)")
        show(fig, "present_by_year")
        tab = pd.DataFrame([{"measurement": v["name"], "column": c, "unit": v["unit"], "missing %": v["missing_pct"],
                             "longest gap (h)": v["longest_gap_hours"], "min": v["min"], "median": v["median"],
                             "max": v["max"], "last reading": (v["last_time"] or "")[:16]} for c, v in cols.items()])
        st.dataframe(tab.round(2), hide_index=True, width="stretch")
        st.caption("Columns that could be forecast (at most 15% missing, not constant): "
                   + ", ".join(S.name(c) for c in health.get("candidate_targets", []))
                   + f". Models exist for {len(C.TARGETS)} of them; the rest can be added in forecast/config.py.")

# ============================================================================================== Method
with tabs[5]:
    st.markdown(r"""
**Data.** NASA OMNI, 5-minute values of the solar wind at Earth and of the geomagnetic indices, 2010 to 2026.
Every forecast below starts at a time $t$ and may use readings at $t$ or before, never after.

**Persistence**, the baseline: the value stays as it is,

$$\hat y_{t+h} = y_t$$


**XGBoost** learns the change instead of the value,

$$\hat y_{t+h} = y_t + f_h(\mathbf{x}_t)$$

where $\mathbf{x}_t$ holds, for speed, $|B|$, $B_z$, $B_y$, density, pressure, SYM-H and AE: the value now, 15 minutes,
1 hour and 3 hours ago, the mean over the last 1, 3 and 12 hours and the spread over the last 3 hours; plus the
southward driving $v\,B_s$ with $B_s=\max(0,-B_z)$, the lowest SYM-H of the last day, and the time of day and year.
One model per measurement and horizon $h$.

**Split by time.** Train on 2010 to 2021, tune on 2022 (validation), report on 2023 to the end (test). One day is left
out at each edge so that no answer leaks across. Neighbouring 5-minute start times are almost the same, so only every
12th (train), 6th (validation) and 3rd (test) start time is used.

**Scores** on the $n$ test forecasts:

$$\mathrm{MAE}=\frac{1}{n}\sum_i \lvert \hat y_i-y_i \rvert$$

$$\mathrm{RMSE}=\sqrt{\frac{1}{n}\sum_i (\hat y_i-y_i)^2}$$

$$R^2 = 1-\frac{\sum_i(\hat y_i-y_i)^2}{\sum_i(y_i-\bar y)^2}$$

and the skill against persistence, $1-\mathrm{RMSE}_{\mathrm{model}}\,/\,\mathrm{RMSE}_{\mathrm{persistence}}$.

**80% interval.** The 10th and 90th percentiles $q_{10},q_{90}$ of the errors on the validation year are added to each
forecast: $[\hat y+q_{10},\ \hat y+q_{90}]$. The test scores show how often it really held.

**Storms.** SYM-H is the storm meter. A start time is labelled 1 when

$$\min_{t \lt s \le t+H}\ \mathrm{SYMH}(s) \le \theta$$

with $\theta=-50$ nT (storm) or $-100$ nT (strong storm), as for Dst in Gonzalez et al. (1994), and $H$ = 6 or 24 hours.
An XGBoost classifier gives the chance $p$. It flags a storm when $p$ is above the line with the best
$F_1=2PR/(P+R)$ on the validation year. Storms are rare, so the scores are precision, recall, $F_1$ and the area under
the precision-recall curve, next to persistence ("a storm now means a storm soon").

**What this is not.** The file ends in October 2026; these are not live forecasts. The models only know what the
solar wind did near Earth, so they cannot see a storm leaving the Sun days ahead.
""")
