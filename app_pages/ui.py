"""Shared pieces for every app page.

- Data access goes through notebooks/helpers.py:
  `numbers(name)` = the exact table behind a notebook chart (numbers/<name>.csv),
  `data(name, columns)` = the raw file from the Parquet cache in data_cache/.
- `chart(key, fig)` = one chart block: title, Plotly chart (hover, zoom), "What I see" box, numbers, static PNG.
- `steps_4_to_6(section)` = odd things, checks, explanations and the answer key of one section.
- `explore(...)` = a small "make your own histogram" tool on the Parquet data.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
_NB = str(ROOT / "notebooks")
if _NB not in sys.path:
    sys.path.insert(0, _NB)
import helpers as hp  # noqa: E402

SERIES = hp.SERIES
BLUE, ORANGE, AQUA, YELLOW = SERIES[:4]
GRAY = hp.GRAY
BLUES = [[0, "#eaf2fd"]] + [[(k + 1) / len(hp.SEQ_BLUE), c] for k, c in enumerate(hp.SEQ_BLUE)]


# ----------------------------------------------------------------------------- data


@st.cache_data(show_spinner=False)
def numbers(name: str) -> pd.DataFrame:
    """A table a notebook saved in numbers/ (the exact numbers behind one of its charts)."""
    return hp.numbers(name)


def has_numbers(name: str) -> bool:
    return (hp.NUMBERS / f"{name}.csv").exists()


@st.cache_data(show_spinner="Reading the Parquet cache in data_cache/ ...")
def data(name: str, columns: tuple[str, ...] | None = None) -> pd.DataFrame:
    """Raw data from the Parquet cache (built from the CSV on first use)."""
    return hp.load_parquet(name, list(columns) if columns else None)


def entry(key: str) -> dict:
    return hp.entry(key) or {}


def fmt(x) -> str:
    return hp.fmt(x)


# ----------------------------------------------------------------------------- plotly helpers


def style(fig, height: int = 420, xlog=False, ylog=False, xtitle=None, ytitle=None, legend=None):
    """Same quiet look on every chart; hover and zoom come from Plotly."""
    fig.update_layout(height=height, margin=dict(l=8, r=8, t=36, b=8), bargap=0.06, hovermode="closest",
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0))
    if legend is not None:
        fig.update_layout(showlegend=legend)
    if xlog:
        fig.update_xaxes(type="log")
    if ylog:
        fig.update_yaxes(type="log")
    if xtitle:
        fig.update_xaxes(title_text=xtitle)
    if ytitle:
        fig.update_yaxes(title_text=ytitle)
    return fig


def hist(df: pd.DataFrame, lo: str, hi: str, count: str, name: str = "", color: str = BLUE, step: bool = False,
         unit: str = ""):
    """A histogram trace from a numbers table with 'from' and 'to' columns.
    step=True draws a stair line (use it for log-x axes or very many bins)."""
    if step:
        x = np.r_[df[lo].to_numpy(), df[hi].to_numpy()[-1]]
        y = np.r_[df[count].to_numpy(), df[count].to_numpy()[-1]]
        return go.Scatter(x=x, y=y, mode="lines", line=dict(shape="hv", color=color, width=1.6), fill="tozeroy",
                          fillcolor="rgba(42,120,214,0.15)", name=name,
                          hovertemplate=f"from %{{x:.4g}}{unit}: %{{y:,}}<extra></extra>")
    mid = (df[lo] + df[hi]) / 2
    return go.Bar(x=mid, y=df[count], width=(df[hi] - df[lo]) * 0.94, marker_color=color, name=name,
                  customdata=np.stack([df[lo], df[hi]], axis=1),
                  hovertemplate=f"%{{customdata[0]:.4g}} to %{{customdata[1]:.4g}}{unit}: %{{y:,}}<extra></extra>")


def log_toggle(key: str, default: bool = False, label: str = "Log scale") -> bool:
    return st.toggle(label, value=default, key=f"log_{key}")


# ----------------------------------------------------------------------------- blocks


def what_i_see(key: str) -> None:
    """The short 'What I see' box: facts and numbers from the log entry the notebook wrote."""
    e = entry(key)
    if not e:
        st.warning(f"No log entry {key} yet.")
        return
    with st.container(border=True):
        st.markdown("**What I see**")
        st.markdown("\n".join(f"- {k}" for k in e["key_numbers"]))
        if e.get("what_it_shows"):
            st.markdown(e["what_it_shows"])
        st.caption(f"Rows used: {e['rows_used']} · Rows skipped: {e['rows_skipped']}")


def chart(key: str, fig=None, tables: list[str] | None = None, show_tables: bool = False, note: str = "",
          controls=None) -> None:
    """One chart block: title, optional controls, Plotly chart, 'What I see', numbers and the static PNG."""
    e = entry(key)
    st.subheader(f"{key} · {e.get('title', '')}")
    if note:
        st.caption(note)
    if fig is not None:
        st.plotly_chart(fig, key=f"fig_{key}", config={"displaylogo": False})
    what_i_see(key)
    files = tables if tables is not None else [Path(p).stem for p in e.get("numbers", [])]
    files = [f for f in files if has_numbers(f)]
    if show_tables:
        for f in files:
            st.caption(f"numbers/{f}.csv")
            st.dataframe(numbers(f), hide_index=True)
    elif files:
        with st.expander("Numbers behind this chart"):
            for f in files:
                st.caption(f"numbers/{f}.csv")
                st.dataframe(numbers(f), hide_index=True)
    pngs = [p for p in e.get("chart", []) if (ROOT / p).exists()]
    if pngs:
        with st.expander("Static chart from the notebook (PNG)"):
            for p in pngs:
                st.image(str(ROOT / p), width="stretch")
    st.divider()


_LABELS = ["Data proves:", "Known science (outside the data):", "Known science:", "Guess:", "Caution (data proves):"]


def _split_reasons(text: str) -> list[str]:
    pat = "(" + "|".join(re.escape(lab) for lab in _LABELS) + ")"
    parts = re.split(pat, text)
    out, cur = [], ""
    for p in parts:
        if p in _LABELS:
            if cur.strip():
                out.append(cur.strip())
            cur = f"**{p}**"
        else:
            cur += " " + p.strip() if cur else p.strip()
    if cur.strip():
        out.append(cur.strip())
    return out


VERDICT_ICON = {"real": "✅", "maybe": "🟡", "probably a bias": "⚠️"}


def steps_4_to_6(section: str) -> None:
    """Step 4 odd things, Step 5 checks, Step 6 explanations and the answer key, for one section."""
    S = section.upper()
    t4, t5, t6, tk = st.tabs(["4 · Odd things", "5 · Checks", "6 · Explanations and tips", "Answer key"])
    with t4:
        if has_numbers(f"{S}90_odd_things"):
            st.caption("Facts only, no reasons. Each item points to the chart it comes from.")
            for r in numbers(f"{S}90_odd_things").itertuples():
                st.markdown(f"- **{r.id}** ({r.chart}): {r.what_stands_out}")
        else:
            st.info("Not done yet.")
    with t5:
        if has_numbers(f"{S}91_checks"):
            st.caption("Each odd thing checked at least two ways. Verdict: real, maybe, or probably a bias.")
            for r in numbers(f"{S}91_checks").fillna("").itertuples():
                icon = next((v for k, v in VERDICT_ICON.items() if str(r.verdict).startswith(k)), "•")
                with st.container(border=True):
                    st.markdown(f"**{r.id} · {r.odd_thing}** → {icon} **{r.verdict}**")
                    for c in (r.check_1, r.check_2, r.check_3):
                        if c:
                            st.markdown(f"- {c}")
        else:
            st.info("Not done yet.")
    with t6:
        if has_numbers(f"{S}92_findings"):
            st.caption("Reasons are labelled: Data proves / Known science (outside the data) / Guess.")
            for r in numbers(f"{S}92_findings").fillna("").itertuples():
                with st.container(border=True):
                    st.markdown(f"**{r.id} · {r.finding}**")
                    st.caption(f"Confidence: {r.confidence} · Reason type: {r.reason_type} · Chart: {r.chart_file}")
                    st.markdown(f"**Key numbers:** {r.key_numbers}")
                    st.markdown(f"**How I checked it:** {r.how_checked}")
                    for part in _split_reasons(r.reasons):
                        st.markdown(f"- {part}")
                    if r.tip:
                        st.success(f"**Tip:** {r.tip}")
        else:
            st.info("Not done yet.")
    with tk:
        if has_numbers(f"{S}99_answer_key"):
            st.caption("Compared only after all numbers were computed.")
            st.dataframe(numbers(f"{S}99_answer_key"), hide_index=True)
        else:
            st.info("Not done yet.")


def explore(dataset: str, numeric: list[str], category: str | None = None, note: str = "") -> None:
    """Make your own histogram from the Parquet copy of the data (counts are computed here, then drawn)."""
    st.caption(note or f"Reads data_cache/{dataset}.parquet. Pick a column, filter, and zoom.")
    c1, c2, c3 = st.columns([2, 2, 1])
    col = c1.selectbox("Column", numeric, key=f"exp_col_{dataset}")
    cols = (col,) + ((category,) if category else ())
    df = data(dataset, cols)
    if category:
        cats = sorted(df[category].dropna().astype(str).unique().tolist())
        pick = c2.multiselect(f"Filter by {category}", cats, default=cats if len(cats) <= 12 else cats[:12],
                              key=f"exp_cat_{dataset}")
        df = df[df[category].astype(str).isin(pick)]
    logx = c3.toggle("Log x", key=f"exp_lx_{dataset}")
    logy = c3.toggle("Log y", key=f"exp_ly_{dataset}")
    s = pd.to_numeric(df[col], errors="coerce").dropna()
    if logx:
        s = s[s > 0]
    if s.empty:
        st.info("No values to show.")
        return
    lo_q, hi_q = float(s.quantile(0.001)), float(s.quantile(0.999))
    lo, hi = st.slider("Range (starts at the 0.1% and 99.9% points)", float(s.min()), float(s.max()),
                       (lo_q, hi_q), key=f"exp_rng_{dataset}_{col}")
    bins = st.slider("Bins", 10, 400, 100, key=f"exp_bins_{dataset}")
    s = s[(s >= lo) & (s <= hi)]
    edges = np.geomspace(max(lo, s.min()), hi, bins + 1) if logx and lo > 0 else np.linspace(lo, hi, bins + 1)
    cnt, edges = np.histogram(s, bins=edges)
    t = pd.DataFrame({"from": edges[:-1], "to": edges[1:], "count": cnt})
    fig = go.Figure(hist(t, "from", "to", "count", step=logx))
    style(fig, height=380, xlog=logx, ylog=logy, xtitle=col, ytitle="rows", legend=False)
    st.plotly_chart(fig, key=f"exp_fig_{dataset}", config={"displaylogo": False})
    st.caption(f"{len(s):,} rows shown · median {s.median():.4g} · min {s.min():.4g} · max {s.max():.4g}")
