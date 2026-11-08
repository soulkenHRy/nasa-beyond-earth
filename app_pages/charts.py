"""Charts: every picture and every animation the project made, in one place.

Simple charts are charts/K*.png (one per finding, plus a few "Meet the data" pictures). Detailed charts are the section
charts (A01 ... A16) and the first finding charts (BF07 ... BF32). Animations are animations/Fnn_*.html, one per finding,
listed in numbers/AN_index.json (notebooks/make_space_anims.py): simple space drawings on a plain 2D canvas.
"""
import json
import re
from pathlib import Path

import streamlit as st

from app_pages import ui

hp = ui.hp
st.title("Charts")
st.caption("Every chart in the `charts/` folder and every animation in `animations/`. Click a picture's corner arrows "
           "to see it full size.")

titles = {}
cards_file = hp.NUMBERS / "BF_findings.json"
if cards_file.exists():
    for c in json.loads(cards_file.read_text()):
        for ch in c["charts"] + c.get("old_charts", []):
            titles.setdefault(ch, f"Finding {c['n']}: {c['title']}")
anim_file = hp.NUMBERS / "AN_index.json"
anims = [v for _, v in sorted(json.loads(anim_file.read_text()).items(), key=lambda kv: int(kv[0]))] if anim_file.exists() else []

PART_OF = {"A": "A · Asteroids and comets", "B": "B · Close approaches", "C": "C · Fireballs", "D": "D · Space weather",
           "E": "E · Stars", "F": "F · Exoplanets", "G": "G · Moon craters"}
FINDING_PART = {**{n: "A" for n in range(1, 8)}, 8: "B", 9: "B", 10: "C", 11: "C", **{n: "D" for n in range(12, 18)},
                **{n: "E" for n in range(18, 23)}, **{n: "F" for n in range(23, 29)}, **{n: "G" for n in range(29, 33)}}


def part_of(name: str) -> str:
    m = re.match(r"K00([A-G])_", name)
    if m:
        return m.group(1)
    m = re.match(r"(?:K|BF)(\d\d)_", name)
    if m:
        return FINDING_PART.get(int(m.group(1)), "?")
    return name[0] if name[0] in PART_OF else "?"


@st.cache_data(show_spinner=False, max_entries=64)
def load_animation(path: str, mtime: float) -> str:
    return Path(path).read_text()


files = sorted(hp.CHARTS.glob("*.png"))
simple = [f for f in files if f.name.startswith("K")]
detailed = [f for f in files if not f.name.startswith("K")]

c1, c2 = st.columns([1, 1])
views = [f"Simple charts ({len(simple)})", f"Detailed charts ({len(detailed)})", f"Animations ({len(anims)})"]
start = 2 if str(st.query_params.get("view", "")).lower().startswith("anim") else 0   # ?view=animations
kind = c1.radio("Which charts", views, index=start, horizontal=True)
if kind.startswith("Animations"):
    parts_here = sorted({e["part"] for e in anims})
    pick = c2.selectbox("Part", ["All parts"] + [PART_OF[p_] for p_ in parts_here])
    pool = [e for e in anims if pick == "All parts" or PART_OF[e["part"]] == pick]
    st.caption(f"{len(pool)} animations shown. Press ▶ Play on any of them; before you press it you see the finished "
               "picture.")
    for e in pool:
        st.markdown(f"**Finding {e['n']}: {e['title']}**")
        path = hp.PROJECT / e["html"]
        if path.exists():
            st.iframe(load_animation(str(path), path.stat().st_mtime), height=e.get("height", 760))
            st.caption(f"`{e['html']}` (opens in any web browser)")
        else:
            st.warning(f"Missing animation: {e['html']}")
    st.stop()

pool = simple if kind.startswith("Simple") else detailed
parts_here = sorted({part_of(f.name) for f in pool} - {"?"})
pick = c2.selectbox("Part", ["All parts"] + [PART_OF[p_] for p_ in parts_here])
if pick != "All parts":
    pool = [f for f in pool if PART_OF.get(part_of(f.name)) == pick]
st.caption(f"{len(pool)} charts shown.")

for i in range(0, len(pool), 2):
    cols = st.columns(2, gap="large")
    for col, f in zip(cols, pool[i:i + 2]):
        with col:
            rel = f"charts/{f.name}"
            st.markdown(f"**{titles.get(rel, f.stem)}**")
            st.image(str(f), caption=rel, width="stretch")
