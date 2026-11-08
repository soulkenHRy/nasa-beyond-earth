"""Galaxies: upload a picture of a galaxy and the Galaxy-CLIP model ranks kinds of galaxy for it (galaxy/clip.py).

Zero-shot: the model is only used, never trained here. It is read from models/galaxy-clip-finetuned/ (not in git).
"""
from __future__ import annotations

import html

import pandas as pd
import streamlit as st

from galaxy import clip as G

st.markdown("""
<style>
.gx-card{border:1px solid #e3e1db;border-left:6px solid #2a78d6;border-radius:12px;padding:18px 22px;margin:0 0 14px;
  background:#ffffff}
.gx-head{font-size:15px;color:#55534e}
.gx-big{font-size:32px;font-weight:700;line-height:1.15;margin:4px 0 6px;color:#0b0b0b}
.gx-sub{font-size:15px;color:#2b2a27;font-variant-numeric:tabular-nums}
.gx-note{font-size:14.5px;color:#55534e;margin-top:10px;line-height:1.45}
</style>""", unsafe_allow_html=True)

st.title("Galaxy pictures")
st.markdown("Upload a picture of a galaxy. An AI model that reads pictures compares it with kinds of galaxy and "
            "ranks them by how well they match.")

problems = G.missing()
if problems:
    st.info("This page needs:\n\n" + "\n".join(f"* {p}" for p in problems))
    st.stop()


@st.cache_resource(show_spinner="Loading the galaxy model (only the first time, a few seconds) ...")
def model():
    return G.load()


@st.cache_data(show_spinner=False, max_entries=64)
def rank(data: bytes, labels: tuple[str, ...]) -> pd.DataFrame:
    return G.classify(G.open_image(data), list(labels))


@st.cache_data(show_spinner=False)
def facts() -> dict:
    """Numbers about the model: from its config file, and from numbers/GC_model.csv (python -m galaxy.check)."""
    f = {k: (f"{v:.0f}" if isinstance(v, float) else str(v)) for k, v in G.info().items()}
    saved = G.ROOT / "numbers" / "GC_model.csv"
    if saved.exists():
        f.update(pd.read_csv(saved, dtype=str).set_index("key")["shown"].to_dict())
    return f


up = st.file_uploader("Galaxy picture", type=G.PICTURE_TYPES)
with st.expander("Change the labels"):
    text = st.text_area("One kind of galaxy per line. The model ranks only these.", value="\n".join(G.DEFAULT_LABELS),
                        height=270)
    st.caption("The list to start with is the classes of Galaxy10 DECaLS, a well-known set of galaxy pictures sorted "
               "by Galaxy Zoo volunteers. Any short description works, for example \"ring galaxy\" or \"galaxy with "
               "a dark dust lane\".")
labels = G.clean_labels(text.splitlines()) or list(G.DEFAULT_LABELS)
f = facts()

if up is None:
    st.caption("No galaxy picture at hand? Open the Legacy Surveys sky viewer (legacysurvey.org/viewer), look up a "
               "galaxy such as M51 or NGC 1300 and save a cutout. A picture with one galaxy in the middle works best.")
else:
    data = up.getvalue()
    try:
        image = G.open_image(data)
    except Exception:                                   # not a picture, or a broken file
        st.error(f"Could not read {up.name} as a picture. Try a JPG or PNG file.")
        st.stop()
    model()
    table = rank(data, tuple(labels))
    top = table.iloc[0]
    notes = []
    if len(table) == 1:
        notes.append("With only one label the match is always 100%. Add more labels to compare.")
    elif top.match_pct - table.match_pct[1] < 10:
        notes.append(f"Close call: “{html.escape(table.label[1])}” is almost as good "
                     f"({table.match_pct[1]:.0f}%).")
    notes.append("The model always picks one of the labels, even for a picture that is not a galaxy.")
    left, right = st.columns([2, 3], gap="large")
    with left:
        st.image(image, caption=up.name, width="stretch")
    with right:
        st.markdown(f'<div class="gx-card"><div class="gx-head">Looks most like</div>'
                    f'<div class="gx-big">{html.escape(top.label)}</div>'
                    f'<div class="gx-sub">{top.match_pct:.0f}% match among the {len(table)} labels, '
                    f'similarity {top.similarity:.3f}</div>'
                    + "".join(f'<div class="gx-note">{n}</div>' for n in notes) + "</div>", unsafe_allow_html=True)
        st.dataframe(table, hide_index=True, column_config={
            "rank": st.column_config.NumberColumn("Rank", width="small"),
            "label": st.column_config.TextColumn("Kind of galaxy"),
            "match_pct": st.column_config.ProgressColumn("Match", format="%.0f%%", min_value=0, max_value=100),
            "similarity": st.column_config.NumberColumn("Similarity", format="%.3f")})
        usual = (f" For this model it is usually between {f['sim_lo']} and {f['sim_hi']}, so only the order matters."
                 if "sim_lo" in f else "")
        st.caption("Match: the scores add up to 100% over the labels in the list, so they change when the list "
                   f"changes. Similarity: how close the picture and the words are for the model, from -1 to 1.{usual}")

with st.expander("How it works"):
    k = f"$k$ = {f['scale']}" if "scale" in f else "$k$"
    check = (f" We tried it on {f['check_n']} well-known galaxies: its first choice fitted {f['check_right']} of "
             "them (README, section 6)." if "check_n" in f else "")
    st.markdown(f"""
**Two halves.** The model, Galaxy-CLIP, turns a picture into a list of {f['embed_dim']} numbers, and a short sentence
such as "barred spiral galaxy" into {f['embed_dim']} numbers too. The two halves were trained together, so that a
picture and a sentence about the same thing get lists that point the same way.

**Reading the picture.** It cuts the picture to a square around the middle, shrinks it to {f['image_px']} by
{f['image_px']} pixels and splits that into {f['patches_side']} by {f['patches_side']} = {f['patches']} tiles of
{f['patch_px']} by {f['patch_px']} pixels, which it reads a bit like the words of a sentence.

**Ranking the labels.** By the similarity $s$, the cosine of the angle between the picture's list $\\mathbf{{a}}$ and
a label's list $\\mathbf{{b}}$. It is 1 when they point the same way and 0 when they have nothing in common:""")
    st.latex(r"s = \frac{\mathbf{a}\cdot\mathbf{b}}{\lVert\mathbf{a}\rVert\,\lVert\mathbf{b}\rVert}")
    st.markdown(f"The match turns the similarities into shares that add up to 100%, where {k} is a number the "
                "model learned:")
    st.latex(r"p_i = \frac{e^{k s_i}}{\sum_j e^{k s_j}}")
    st.markdown(f"""
**Where the model comes from.** Galaxy-CLIP (`{G.HF_NAME}` on Hugging Face) is OpenAI's CLIP, tuned by Michael Jupp
on galaxy pictures paired with descriptions written by another AI model. It is read from
`models/galaxy-clip-finetuned/` and is not trained here. Its own page says it has not been formally tested.{check}
""")
