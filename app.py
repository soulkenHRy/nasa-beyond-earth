"""NASA Beyond Earth: what we found in seven NASA data files (Sheridan Datathon 2026, NASA track).

Run from the project folder:
    .venv/bin/streamlit run app.py

Five pages:
  Home         what this is and the seven data files
  Findings     the 32 findings (same words as FINDINGS.md), each with its chart and an animation with a Play button
  Charts       every chart and every animation in one place
  Predictions  pick a day, get the chance of a geomagnetic storm on it (forecast/)
  Galaxies     upload a galaxy picture, get the kinds of galaxy it looks like, ranked (galaxy/, Galaxy-CLIP model)
Every number comes from code in the notebooks (numbers/*.csv). The earlier pages are kept in old/app_pages/.
"""
import streamlit as st

st.set_page_config(page_title="NASA Beyond Earth", page_icon="🔭", layout="wide")
pages = [st.Page("app_pages/home.py", title="Home", icon="🏠", default=True),
         st.Page("app_pages/findings.py", title="Findings", icon="📋"),
         st.Page("app_pages/charts.py", title="Charts", icon="🖼️"),
         st.Page("app_pages/predictions.py", title="Predictions", icon="🛰️"),
         st.Page("app_pages/galaxies.py", title="Galaxies", icon="🌌")]
st.navigation(pages, position="sidebar").run()
