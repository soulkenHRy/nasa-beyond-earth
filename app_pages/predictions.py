"""Predictions: pick a day and get the chance of a geomagnetic storm on it, from data before that day only.

The answer comes from forecast/daily.py: the 5-minute storm model for the next day, small daily models for 2 to 90
days ahead, and the usual share of storm days further ahead. The earlier six-tab page is in old/app_pages/.
"""
from __future__ import annotations

import datetime as dt
import html

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from forecast import config as C
from forecast import daily as F
from forecast import service as S

st.markdown("""
<style>
.fc-card{border:1px solid #e3e1db;border-left:6px solid #8a96b2;border-radius:12px;padding:18px 22px;margin:10px 0 14px;
  background:#ffffff;max-width:760px}
.fc-card.storm{border-left-color:#e8590c}.fc-card.calm{border-left-color:#2f9e44}.fc-card.info{border-left-color:#2a78d6}
.fc-head{font-size:24px;font-weight:700;color:#0b0b0b}
.fc-big{font-size:44px;font-weight:700;line-height:1.1;margin-top:6px;font-variant-numeric:tabular-nums}
.fc-sub{font-size:15px;color:#55534e}
.fc-note{font-size:15px;color:#2b2a27;margin-top:12px;line-height:1.5}
.fc-small{font-size:13.5px;color:#6b6963;margin-top:10px;line-height:1.45}
</style>""", unsafe_allow_html=True)

st.title("Storm forecast")
st.markdown("Pick a day. You get the chance of a **geomagnetic storm** on that day, worked out only from data from "
            "before the day. A storm day is a day when the storm meter SYM-H drops to -50 nT or lower.")

if not (S.have_data() and S.models_ready() and F.ready()):
    st.info("The forecast needs the data file and the trained models. Run `.venv/bin/python -m forecast.train` and "
            "then `.venv/bin/python -m forecast.daily` from the project folder.")
    st.stop()


@st.cache_data(show_spinner=False, max_entries=500)
def answer(day: str) -> dict:
    return F.forecast_day(day)


@st.cache_data(show_spinner=False, max_entries=100)
def nearby(day: str) -> pd.DataFrame:
    return F.around(day)


end = F.last_day().date()
usual = F.usual_rate()
day = st.date_input("Day (UTC)", value=min(dt.date.today(), dt.date(2035, 12, 31)), min_value=F.first_day().date(),
                    max_value=dt.date(2035, 12, 31), format="YYYY-MM-DD")
r = answer(str(day))
when = pd.Timestamp(day).strftime("%-d %B %Y")


def card(kind: str, head: str, big: str, sub: str, notes: list[str], small: str = "") -> None:
    st.markdown(f'<div class="fc-card {kind}"><div class="fc-head">{html.escape(head)}</div>'
                f'<div class="fc-big">{html.escape(big)}</div><div class="fc-sub">{html.escape(sub)}</div>'
                + "".join(f'<div class="fc-note">{n}</div>' for n in notes)
                + (f'<div class="fc-small">{small}</div>' if small else "") + "</div>", unsafe_allow_html=True)


q = F.quality(r.get("model_lead", r.get("lead_days", 1))) if r["mode"] in ("check", "forecast") else None
if r["mode"] == "too early":
    st.info(r["message"])
elif r["mode"] == "long range":
    month = pd.Timestamp(day).strftime("%B")
    card("info", "Too far ahead to forecast this day", f"{100 * r['p_storm']:.0f}%",
         f"the usual chance of a storm on a day in {month}",
         [f"The data ends on {end}, {r['lead_days']} days before {when}. Nothing measured that early says anything "
          f"about one single day so far away, so this is only the usual rate: over the last solar cycle "
          f"({r['climate_from']} to {r['climate_to']}), {r['climate_storm_days']} of {r['climate_days']} days in "
          f"{month} had a storm."])
else:
    p = r["p_storm"]
    notes = []
    if r["lead_days"] == 1:
        kind, head = ("storm", "Storm expected") if r["flag"] else ("calm", "No storm expected")
        notes.append(f"Made from the data up to {r['made_from']} UTC, just before the day started.")
    else:
        ratio = p / usual if usual else 1
        kind, head = ("storm", "Higher chance than usual") if ratio >= 1.5 else \
            ("calm", "Lower chance than usual") if ratio <= 2 / 3 else ("info", "About the usual chance")
        notes.append(f"The data ends on {end}, {r['lead_days']} days before this day, so this is a rough forecast. "
                     f"It mostly knows how stormy the Sun has been lately, the time of year, and what happened one turn "
                     f"of the Sun (27 days) earlier. Lately, {100 * usual:.0f}% of days had a storm.")
    if r["mode"] == "check" and "actual_sym_min" in r:
        happened = r["actual_storm"]
        if r["lead_days"] == 1:
            verdict = ("The forecast was right." if happened == r["flag"] else
                       "The forecast missed this storm." if happened else "False alarm: no storm came.")
        else:
            verdict = ""
        what = (f"a storm ({r['actual_severity'].lower()})" if happened else "no storm")
        notes.append(f"<b>What really happened:</b> the storm meter went down to {r['actual_sym_min']:.0f} nT, "
                     f"{what}. {verdict}")
    elif r["mode"] == "check":
        notes.append("The storm meter has no readings for this day, so we can't say what happened.")
    small = ""
    if q:
        if q["lead_days"] == 1:
            small = (f"How good is it? On the test days (2023 to {end.year}), when it said \"storm\" a storm came "
                     f"{100 * q['precision']:.0f}% of the time, and it caught {100 * q['recall']:.0f}% of the storm days. "
                     f"Just saying \"a storm today if there was one yesterday\" catches {100 * q['recall_persistence']:.0f}%.")
        else:
            small = (f"How good is it? About {int(q['lead_days'])} days ahead, on the test days (2023 to {end.year}), "
                     f"its chances were only {q['brier_skill_pct']:.0f}% better than always giving the usual rate. "
                     "Storms are hard to see coming this early.")
    card(kind, head, f"{100 * p:.0f}%", f"chance of a storm on {when}", notes, small)

    with st.expander("The days around it"):
        w = nearby(str(day))
        if not w.empty:
            fig = go.Figure(go.Bar(x=w["day"], y=100 * w["chance"], name="chance of a storm",
                                   marker=dict(color=["#e8590c" if d.date() == day else "#9db9e8" for d in w["day"]]),
                                   hovertemplate="%{x|%d %b %Y}: %{y:.0f}%<extra></extra>"))
            seen = w.dropna(subset=["actual_sym_min"])
            storms = seen[seen["actual_sym_min"] <= F.STORM]
            if not storms.empty:
                fig.add_trace(go.Scatter(x=storms["day"], y=[102] * len(storms), mode="markers", name="storm happened",
                                         marker=dict(symbol="triangle-down", size=12, color="#c92a2a"),
                                         hovertemplate="%{x|%d %b %Y}: storm happened<extra></extra>"))
            fig.update_layout(height=300, margin=dict(l=50, r=10, t=10, b=40), plot_bgcolor="#ffffff",
                              paper_bgcolor="#ffffff", yaxis=dict(title="chance (%)", range=[0, 108], gridcolor="#eceae4"),
                              xaxis=dict(gridcolor="#eceae4"), legend=dict(orientation="h", y=1.1), hovermode="closest")
            st.plotly_chart(fig, theme=None, config={"displaylogo": False}, width="stretch")
            st.caption("Each bar is the forecast for that day, made the same way as above.")

with st.expander("How it works"):
    st.markdown(f"""
* **Next day** (and any past day, to check it): the 5-minute storm model looks at the last 24 hours of solar wind and
  magnetic field before the day starts and gives the chance that SYM-H reaches -50 nT during the day.
* **2 to {F.MAX_LEAD} days ahead:** a small model for each lead time uses daily summaries up to the last day of data:
  how stormy the last week, month and year were, the time of year, and the day one solar turn (27 days) before.
* **Further ahead:** only the usual share of storm days in that month.
* Trained on 2010 to 2020, tuned on 2021 to 2022, and tested on 2023 onward, which the models never saw.
  The data ends on {end}, so "now" here means that day, not today.

The chance is a number $p$ between 0 and 1; "storm expected" means $p$ is above the line that gave the best balance
of right calls and caught storms on 2021 to 2022.
""")
