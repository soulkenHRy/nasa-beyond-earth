"""Findings: the 32 findings in plain words (the same words as FINDINGS.md), each with its chart and an animation.

Each part starts with "Meet the data" (what one row is, what every column means), then its findings. Each finding shows
its text on the left and its chart on the right, with "How to read the chart" under the chart, and then its animation
with a ▶ Play button. Built from numbers/BF_meet_the_data.json and numbers/BF_findings.json (notebooks/make_findings.py)
and from numbers/AN_index.json and animations/ (notebooks/make_space_anims.py: simple space drawings on a plain 2D
canvas, so they work in every browser, with or without WebGL).
The page opens on all 32 findings; pick one part in the Part box, or open it directly with ?part=A (A to G).
"""
import json
import re
from pathlib import Path

import pandas as pd
import streamlit as st

from app_pages import ui

hp = ui.hp
st.title("Findings")
st.caption("32 things we found in NASA's \"Beyond Earth\" data, in plain words: the same words as `FINDINGS.md`. "
           "Every number is filled in by code from the tables in `numbers/` and checked by "
           "`notebooks/check_findings_numbers.py`.")

cards_file, meet_file, md_file = hp.NUMBERS / "BF_findings.json", hp.NUMBERS / "BF_meet_the_data.json", hp.PROJECT / "FINDINGS.md"
if not (cards_file.exists() and md_file.exists()):
    st.info("Run notebooks/make_findings.py first.")
    st.stop()
cards = json.loads(cards_file.read_text())
meets = {m["part"]: m for m in (json.loads(meet_file.read_text()) if meet_file.exists() else [])}
anim_file = hp.NUMBERS / "AN_index.json"
anims = {int(k): v for k, v in json.loads(anim_file.read_text()).items()} if anim_file.exists() else {}
md = md_file.read_text()
parts = list(dict.fromkeys(c["section"] for c in cards))            # A to G, in order
names = {c["section"]: c["section_name"] for c in cards}
names.update({p_: m["part_name"] for p_, m in meets.items()})


@st.cache_data(show_spinner=False, max_entries=64)
def load_animation(path: str, mtime: float) -> str:
    """The animation's web page (cached; mtime makes a rebuilt file load again)."""
    return Path(path).read_text()


def show_animation(n: int, key: str) -> None:
    e = anims.get(n)
    if not e or "html" not in e or not (hp.PROJECT / e["html"]).exists():
        st.info(f"The animation for finding {n} is not made yet (notebooks/make_space_anims.py).")
        return
    path = hp.PROJECT / e["html"]
    st.iframe(load_animation(str(path), path.stat().st_mtime), height=e.get("height", 760))
    st.caption(f"About {e['seconds']:.0f} seconds. Before you press ▶ Play you see the finished picture. To open it on "
               f"its own, open `{e['html']}` in any web browser.")


def show_image(path: str, caption: str | None = None) -> None:
    p = hp.PROJECT / path
    if p.exists():
        st.image(str(p), caption=caption, width="stretch")
    else:
        st.warning(f"Missing picture: {path}")


labels = {p_: f"Part {p_}: {names[p_]}" for p_ in parts}
options = ["All parts"] + list(labels.values())
want = str(st.query_params.get("part", "all")).upper()
default = options.index(labels[want]) if want in labels else 0
c1, c2 = st.columns([1, 2])
pick = c1.selectbox("Part", options, index=default, help=f"'All parts' shows all {len(cards)} findings, each with "
                    "its animation, on one long page. Pick a part to see only its findings.")
query = c2.text_input("Search", placeholder="for example: Jupiter, storm, crater, shininess").strip().lower()

how = re.search(r"## How this guide works\n(.*?)\n## Part ", md, flags=re.S)
with st.expander("How this page works, and our space rulers"):
    if how:
        st.markdown(how.group(1))
diff = hp.NUMBERS / "BF_guide_differences.csv"
if diff.exists():
    d = pd.read_csv(diff)
    with st.expander(f"Where our numbers differ from the field guide ({len(d)})"):
        for r in d.itertuples():
            st.markdown(f"- **{r.finding}. {r.title}** Note: {r.note}")

shown = 0
for part in parts:
    if pick != "All parts" and pick != labels[part]:
        continue
    m = meets.get(part)
    part_cards = [c for c in cards if c["section"] == part
                  and (not query or query in (c["title"] + c["markdown"] + c["chart_read"]).lower())]
    meet_hit = m is not None and (not query or query in (m["title"] + m["markdown"]).lower())
    if not part_cards and not meet_hit:
        continue
    st.divider()
    st.header(labels[part])
    if meet_hit:
        with st.expander(f"Meet the data: {m['title']}  (read this first)", expanded=pick != "All parts" and not query):
            if m["pictures"]:
                left, right = st.columns([3, 2], gap="large")
                with left:
                    st.markdown(m["markdown"])
                with right:
                    for pic in m["pictures"]:
                        show_image(pic)
                    if m["picture_read"]:
                        st.markdown("**How to read the picture**\n" + m["picture_read"])
            else:
                st.markdown(m["markdown"])
    for c in part_cards:
        shown += 1
        st.subheader(f"{c['n']}. {c['title']}")
        left, right = st.columns([3, 2], gap="large")
        with left:
            text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", c["markdown"])
            text = re.sub(r"(?m)^\*\*Animation:\*\*.*\n?", "", text)
            st.markdown(text)
        with right:
            for chart in c["charts"]:
                show_image(chart)
            if c.get("chart_read"):
                with st.container(border=True):
                    st.markdown("**How to read the chart**\n" + c["chart_read"])
            if c.get("old_charts"):
                with st.expander("The detailed chart"):
                    for chart in c["old_charts"]:
                        show_image(chart, caption=chart)
            st.caption(f"Numbers for this finding: `{c['facts_file']}`")
        st.markdown(f"**Animation for finding {c['n']}**")
        show_animation(c["n"], key=f"anim_{c['n']}")
st.caption(f"{shown} of {len(cards)} findings shown.")

if "## Master word list (A to Z)" in md:
    st.divider()
    with st.expander("Master word list (A to Z)"):
        st.markdown(md.split("## Master word list (A to Z)", 1)[1])
