"""Home: what this is, the seven data files, and where to look."""
import json

import pandas as pd
import pyarrow.parquet as pq
import streamlit as st

from app_pages import ui

hp = ui.hp

st.title("NASA Beyond Earth: what we found")
cards_file, anim_file = hp.NUMBERS / "BF_findings.json", hp.NUMBERS / "AN_index.json"
n_find = len(json.loads(cards_file.read_text())) if cards_file.exists() else 0
n_anim = len(json.loads(anim_file.read_text())) if anim_file.exists() else 0
n_png = len(list(hp.CHARTS.glob("*.png")))
st.markdown(
    "Sheridan Datathon 2026, NASA track. We explored seven NASA data files about space: asteroids, close passes by "
    "Earth, fireballs, space weather, stars, planets around other stars and Moon craters. Every number on these pages "
    "was worked out by code and saved in the `numbers/` folder; nobody typed a number by hand.")

c1, c2, c3 = st.columns(3, gap="large")
with c1:
    with st.container(border=True):
        st.markdown(f"### 📋 Findings\n{n_find} things we found, in plain words. Each part starts with **Meet the data** "
                    "(what one row is and what each column means). Each finding has the question, the data and the "
                    "math, a chart with **How to read the chart**, and an **animation** with a ▶ Play button.")
        st.page_link("app_pages/findings.py", label="Open the Findings", icon="📋")
with c2:
    with st.container(border=True):
        st.markdown(f"### 🖼️ Charts\nAll {n_png} charts and all {n_anim} animations in one place, by part.")
        st.page_link("app_pages/charts.py", label="Open the Charts", icon="🖼️")
with c3:
    with st.container(border=True):
        st.markdown("### 🛰️ Predictions\nForecasts of the solar wind, the magnetic field and geomagnetic storms from "
                    "the 5-minute space-weather file, made by models tested on 2023 onward, with their scores.")
        st.page_link("app_pages/predictions.py", label="Open the Predictions", icon="🛰️")

st.divider()
SECTION_OF = {"asteroids": "A", "close_approaches": "B", "fireballs": "C", "space_weather": "D", "stars": "E",
              "planets": "F", "craters": "G"}


SAVED = hp.NUMBERS / "data_files.csv"       # the same table, saved, for a copy of the project without the data


@st.cache_data(show_spinner="Building the Parquet cache (first run only) ...")
def file_table() -> pd.DataFrame:
    if not all((hp.CACHE / f"{n}.parquet").exists() and p_.exists() for n, p_ in hp.FILES.items()):
        return pd.read_csv(SAVED)
    rows = []
    for name, path in hp.FILES.items():
        pqf = hp.CACHE / f"{name}.parquet"
        if not pqf.exists():
            hp.load_parquet(name, columns=[hp.columns(name)[0]])
        md = pq.ParquetFile(pqf).metadata
        rows.append({"part": SECTION_OF[name], "file": path.name, "rows": md.num_rows, "columns": md.num_columns,
                     "CSV size (MB)": round(path.stat().st_size / 1e6, 1)})
    out = pd.DataFrame(rows).sort_values("part")
    out.to_csv(SAVED, index=False)
    return out


st.subheader("The seven data files")
ft = file_table()
st.dataframe(ft, hide_index=True)
st.caption(f"{int(ft['rows'].sum()):,} rows in total. Row counts are read from the Parquet copies in data_cache/, which "
           "are built from the CSVs with the same reading rules as the notebooks (notebooks/helpers.py). The earlier "
           "step-by-step pages are kept in old/app_pages/.")
