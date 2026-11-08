"""Write FINDINGS.md: the 32 findings explained in plain words (plus the JSON files the app reads).

The words live in notebooks/findings_text/sec_A.py ... sec_G.py. Each part has a "Meet the data" section (what one row is,
what every column we use means) and then its findings. Every number in the words is a placeholder like {gap_count},
filled from the fact tables in numbers/ (column 'shown'), so no number is typed by hand:
  {key}      in a finding: that finding's numbers/BFnn_*.csv;  in "Meet the data": that part's numbers/BM_<part>_*.csv
  {F3_key}   finding 3's table                     {S_key}   numbers/BF00_shared_facts.csv
  {M_key}    this part's Meet-the-data table       {MA_key}  part A's Meet-the-data table
A missing placeholder stops the script with an error. The old (first) version is kept in old/.

Usage (from the project folder):
  .venv/bin/python notebooks/make_findings.py                          # everything
  .venv/bin/python notebooks/make_findings.py --parts D --out X.md     # one part only, to a test file
Then check the numbers:  .venv/bin/python notebooks/check_findings_numbers.py [--md X.md]
Each finding also links its animation (animations/Fnn_*.html), listed in numbers/AN_index.json by
notebooks/make_space_anims.py.
"""
from __future__ import annotations

import argparse
import importlib
import json
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import helpers as hp  # noqa: E402

PARTS = "ABCDEFG"
ap = argparse.ArgumentParser()
ap.add_argument("--parts", default=PARTS, help="which parts to write, e.g. D or BC (default: all)")
ap.add_argument("--out", default=None, help="write only this markdown file (a test run: no JSON for the app)")
args = ap.parse_args()
FULL = args.out is None and set(args.parts) == set(PARTS)

# ----------------------------------------------------------------------------- shared facts
AU_M = hp.AU_KM / 1e6
CAR_KMH = 100
shared = pd.DataFrame([
    {"key": "au_million_km", "value": AU_M, "shown": f"{AU_M:.1f}", "unit": "million km", "source": "known science (1 AU)"},
    {"key": "au_round", "value": round(AU_M, -1), "shown": f"{round(AU_M, -1):.0f}", "unit": "million km", "source": "1 AU rounded to the nearest 10"},
    {"key": "car_kmh", "value": CAR_KMH, "shown": f"{CAR_KMH}", "unit": "km per hour", "source": "rule we used (a highway speed)"},
    {"key": "car_years_au", "value": hp.AU_KM / CAR_KMH / 24 / 365.25, "shown": f"{hp.AU_KM / CAR_KMH / 24 / 365.25:.0f}", "unit": "years",
     "source": "1 AU divided by 100 km per hour, in years"},
    {"key": "ld_km", "value": hp.LD_KM, "shown": f"{hp.LD_KM:,}", "unit": "km", "source": "the brief (1 lunar distance)"},
    {"key": "car_days_ld", "value": hp.LD_KM / CAR_KMH / 24, "shown": f"{hp.LD_KM / CAR_KMH / 24:.0f}", "unit": "days",
     "source": "1 lunar distance divided by 100 km per hour, in days"},
    {"key": "ld_per_au", "value": hp.AU_KM / hp.LD_KM, "shown": f"{hp.AU_KM / hp.LD_KM:.0f}", "unit": "Moon distances", "source": "1 AU divided by 1 lunar distance"},
    {"key": "pc_ly", "value": 3.26, "shown": "3.26", "unit": "light-years", "source": "README (1 parsec)"},
    {"key": "kt_tonnes", "value": 1000, "shown": "1,000", "unit": "tonnes of TNT", "source": "definition of a kiloton"},
    {"key": "earth_radius", "value": hp.EARTH_RADIUS_KM, "shown": f"{hp.EARTH_RADIUS_KM:,}", "unit": "km", "source": "the brief"},
    {"key": "earth_width", "value": 2 * hp.EARTH_RADIUS_KM, "shown": f"{2 * hp.EARTH_RADIUS_KM:,}", "unit": "km", "source": "2 x Earth's radius"},
    {"key": "light_kms", "value": 299_792.458, "shown": "300,000", "unit": "km per second", "source": "known science (speed of light, rounded)"},
    {"key": "sec_per_hour", "value": 3600, "shown": "3,600", "unit": "seconds", "source": "60 x 60"},
    {"key": "full_circle", "value": 360, "shown": "360", "unit": "degrees", "source": "a full circle"},
    {"key": "hundred", "value": 100, "shown": "100", "unit": "", "source": "percent means out of 100"},
])

FACTS: dict[int, dict[str, str]] = {}
FILES: dict[int, str] = {}
for f in sorted(hp.NUMBERS.glob("BF[0-9][0-9]_*.csv")):
    t = pd.read_csv(f, dtype={"shown": str})
    if "shown" in t.columns:
        FACTS[int(f.name[2:4])] = dict(zip(t["key"], t["shown"]))
        FILES[int(f.name[2:4])] = f.name
MEET: dict[str, dict[str, str]] = {}
MEET_FILES: dict[str, str] = {}
for f in sorted(hp.NUMBERS.glob("BM_[A-G]_*.csv")):
    t = pd.read_csv(f, dtype={"shown": str})
    MEET[f.name[3]] = dict(zip(t["key"], t["shown"]))
    MEET_FILES[f.name[3]] = f.name


class Ctx(dict):
    """Placeholder lookup (see the top of this file)."""

    def __init__(self, n: int | None, part: str):
        super().__init__()
        self.n, self.part = n, part

    def __missing__(self, k: str) -> str:
        where = f"finding {self.n}" if self.n else f"part {self.part} (Meet the data)"
        try:
            m = re.fullmatch(r"F(\d+)_(.+)", k)
            if m:
                return FACTS[int(m.group(1))][m.group(2)]
            m = re.fullmatch(r"M([A-G])?_(.+)", k)
            if m:
                return MEET[m.group(1) or self.part][m.group(2)]
            if k.startswith("S_"):
                return FACTS[0][k[2:]]
            table = FACTS.get(self.n, {}) if self.n else MEET.get(self.part, {})
            return table[k]
        except KeyError:
            raise KeyError(f"{where}: no fact '{k}'") from None


def fill(text, n: int | None, part: str) -> str:
    return "" if text is None else str(text).format_map(Ctx(n, part))


# ----------------------------------------------------------------------------- words explained everywhere
# If a text uses one of these, the word goes into that text's Word box automatically. Parts add their own (GLOSSARY).
GLOSSARY = [
    ("Earth-Sun distance (AU)", r"Earth.Sun distance|\bAU\b",
     "our space ruler for the Solar System: the distance from the Sun to Earth, about {S_au_round} million km. "
     "Scientists write it as AU. A car driving at {S_car_kmh} km an hour, day and night, would need about {S_car_years_au} years to cover it."),
    ("orbit", r"\borbit", "the loop a thing travels around the Sun (or around a star), again and again."),
    ("asteroid", r"\basteroid", "a rocky lump, much smaller than a planet, that travels around the Sun."),
    ("comet", r"\bcomet", "an icy lump that travels around the Sun. Near the Sun it heats up and grows a glowing tail."),
    ("middle value (median)", r"middle value|\bmedian\b",
     "line all the values up from smallest to biggest and pick the one in the middle. Scientists call it the median. "
     "One giant value can't pull it up the way it pulls up an average."),
    ("average", r"\baverage", "add all the values up, then divide by how many there are."),
    ("percent (%)", r"%|percent", "out of every hundred. Half is the same as fifty percent."),
    ("times-ten axis (log scale)", r"times-ten|log scale",
     "a chart side where each step is ten times the step before: one, ten, a hundred, a thousand. "
     "It lets tiny numbers and huge numbers fit on the same chart."),
    ("world time (UTC)", r"\bUTC\b|world time",
     "one clock that scientists everywhere share, so readings from different countries line up. Every time in these files is in world time."),
    ("magnetic field", r"magnetic", "the invisible push and pull around a magnet. Earth and the Sun both have one."),
    ("solar wind", r"solar wind", "a wind of tiny bits of electrically charged gas that blows out from the Sun all the time."),
    ("light-year", r"light.year", "how far light travels in one year. Light is the fastest thing there is."),
    ("parsec", r"parsec", "another unit for star distances: one parsec is {S_pc_ly} light-years."),
    ("match score (correlation)", r"match score|correlation",
     "a number that says how well two lists of numbers go up and down together. One means a perfect match; zero means no match at all."),
    ("kiloton", r"kiloton", "the energy of {S_kt_tonnes} tonnes of TNT explosive going off at once."),
    ("crater", r"\bcrater", "a bowl-shaped hole made when a space rock smashes into the ground."),
    ("degree", r"degree", "a small slice of a circle. A full turn is {S_full_circle} degrees."),
    ("latitude", r"latitude", "how far north or south a place is, in degrees. The equator is zero."),
    ("longitude", r"longitude", "how far east or west a place is, in degrees."),
    ("equator", r"equator", "the imaginary line around the middle of a planet or moon, halfway between the north and south poles."),
    ("gravity", r"gravity", "the pull every object has on every other object. Bigger, heavier things pull harder."),
    ("telescope survey", r"\bsurvey", "a telescope that sweeps the sky again and again, looking for things that move or change."),
    ("decade", r"decade", "ten years in a row."),
    ("northern lights (aurora)", r"northern lights|aurora",
     "glowing curtains of green and red light in the night sky, made when a solar storm hits Earth's magnetic field."),
    ("density", r"[Dd]ensity", "how crowded something is: how many tiny bits are packed into one space."),
    ("pressure", r"[Pp]ressure", "how hard something pushes on whatever is in its way."),
    ("habitable zone", r"just.right|habitable",
     "the \"just right\" distance from a star: not too hot and not too cold, so water could be liquid."),
]

ALL_GLOSSARY = list(GLOSSARY)
SEC: dict[str, object] = {}
PENDING: list[str] = []   # parts not rewritten yet: on a full run they show their first version (old/BF_findings_v1.json)
for s in args.parts:
    try:
        SEC[s] = importlib.import_module(f"findings_text.sec_{s}")
    except ModuleNotFoundError:
        if FULL:
            PENDING.append(s)
        else:
            print(f"part {s}: notebooks/findings_text/sec_{s}.py not written yet, skipped")
        continue
    ALL_GLOSSARY += list(getattr(SEC[s], "GLOSSARY", []))
OLD = json.loads((hp.PROJECT / "old" / "BF_findings_v1.json").read_text()) if PENDING else []
_AN = hp.NUMBERS / "AN_index.json"          # the animations (notebooks/make_space_anims.py), by finding number
ANIMS: dict[str, dict] = json.loads(_AN.read_text()) if _AN.exists() else {}

# How many findings and parts: counted on a full run. A test run of a few parts keeps the saved counts (and skips the
# front page that uses them). The shared table is saved on every run, written to a temporary file first and then
# swapped in, so a checker reading it at the same moment never sees half a file.
BF00 = hp.NUMBERS / "BF00_shared_facts.csv"
saved0 = pd.read_csv(BF00, dtype={"shown": str}) if BF00.exists() else pd.DataFrame(columns=["key"])
if FULL:
    n_all = sum(len(m.FINDINGS) for m in SEC.values()) + sum(c["section"] in PENDING for c in OLD)
    counts = pd.DataFrame([
        {"key": "n_findings", "value": n_all, "shown": str(n_all), "unit": "", "source": "count of findings written"},
        {"key": "n_parts", "value": len(SEC) + len(PENDING), "shown": str(len(SEC) + len(PENDING)), "unit": "",
         "source": "count of parts written"}])
else:
    counts = saved0[saved0["key"].isin(["n_findings", "n_parts"])]
shared = pd.concat([shared, counts], ignore_index=True)
tmp = BF00.with_name(f"{BF00.name}.{Path(args.out).name if args.out else 'full'}.tmp")
shared.to_csv(tmp, index=False)
import os  # noqa: E402
os.replace(tmp, BF00)
FACTS[0] = dict(zip(shared["key"], shared["shown"]))


def word_box(text: str, own: dict, n: int | None, part: str) -> list[tuple[str, str]]:
    """Every hard word used in the text: the automatic ones first, then the ones this text adds."""
    seen, box = set(), []
    for w, pat, m in ALL_GLOSSARY:
        if re.search(pat, text) and w.lower() not in seen:
            box.append((w, fill(m, n, part))); seen.add(w.lower())
    for w, m in (own or {}).items():
        if w.lower() not in seen:
            box.append((w, fill(m, n, part))); seen.add(w.lower())
    return box


def table(header: list[str], rows: list[tuple], n: int | None, part: str) -> list[str]:
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    for r in rows:
        cells = [f"`{r[0]}`"] + [fill(c, n, part) for c in r[1:]]
        out.append("| " + " | ".join(cells) + " |")
    return out


def prose_words(md: str) -> int:
    """Words a reader reads, not counting tables, the chart box, the word box, images and the file line."""
    keep, skip = [], False
    for line in md.splitlines():
        if line.startswith("**How to read the chart") or line.startswith("**How to read the picture") or line.startswith("**Word box"):
            skip = True
        elif line.startswith("**") and skip:
            skip = False
        if (skip or line.startswith("|") or line.startswith("!") or line.startswith("- File:") or line.startswith("**Chart")
                or line.startswith("**Animation")
                or line.startswith("- Exact rule") or re.fullmatch(r"\*\*[^*]+\*\*", line.strip()) or line.strip() == "- Columns:"):
            continue
        keep.append(line)
    return len(" ".join(keep).split())


# ----------------------------------------------------------------------------- render
def render_meet(sec) -> tuple[str, dict]:
    p, M = sec.PART, sec.MEET
    f = lambda t: fill(t, None, p)  # noqa: E731
    L = [f"### Meet the data: {f(M['title'])}", "",
         f"**What is this file?** {f(M['what'])}", "",
         f"**What is one row?** {f(M['row'])}", "",
         f"**How big is it?** {f(M['size'])}", "",
         f"**What is this data trying to tell us?** {f(M['story'])}", "",
         "**The columns we use**", ""]
    L += table(["Column (name in the file)", "Nickname we use", "What it tells us", "How it's measured", f"Example ({f(M['example'])})"],
               M["columns"], None, p)
    L += ["", f"**Let's read one row together ({f(M['example'])})**"] + [f"- {f(w)}" for w in M["walk"]]
    if M.get("careful"):
        L += ["", f"**Watch out for:** {f(M['careful'])}"]
    pic_md = []
    for c in M.get("pictures", []):
        pic_md += ["", f"![Picture for part {p}]({c})", "", f"**Picture:** `{c}`"]
    read_md = []
    if M.get("picture_read"):
        read_md = ["", "**How to read the picture**"] + [f"- {f(w)}" for w in M["picture_read"]]
    body = "\n".join(L)
    wb = word_box(body + "\n".join(pic_md + read_md), M.get("words", {}), None, p)
    words_md = ["", "**Word box**"] + [f"- {w}: {m}" for w, m in wb]
    md = "\n".join(L + pic_md + read_md + words_md)
    card = {"part": p, "part_name": sec.NAME, "title": f(M["title"]), "file": sec.FILE,
            "markdown": "\n".join(L[1:] + words_md).strip(), "pictures": M.get("pictures", []),
            "picture_read": "\n".join(read_md[2:]), "facts_file": f"numbers/{MEET_FILES.get(p, '')}",
            "prose_words": prose_words(md)}
    return md, card, wb


def render_finding(sec, F: dict) -> tuple[str, dict, list]:
    n, p = F["n"], sec.PART
    f = lambda t: fill(t, n, p)  # noqa: E731
    title = f(F["title"])
    rows = f(F["rows"])
    data = ["**The data we used**",
            f"- File: `{sec.FILE}` (see \"Meet the data\" for part {p})",
            f"- Rows: {rows[0].upper() + rows[1:]}",
            f"- Exact rule, for checking: `{f(F['rule'])}`",
            "- Columns:", ""]
    data += table(["Column", "What it tells us", "Unit", f"Example value ({f(F['example'])})"], F["columns"], n, p)
    math = ["", "**The math**"] + [f"{k}. {f(s)}" for k, s in enumerate(F["math"], 1)]
    rel = ["", "**The simple relationship**", f"`{f(F['relationship'])}`"]
    pics = []
    for c in F["charts"]:
        pics += ["", f"![Chart for finding {n}]({c})"]
    read = ["", "**How to read the chart**"] + [f"- {f(s)}" for s in F["chart_read"]]
    short = ["", "**In short**", f(F["short"])]
    shows = ["", f"**Our data shows:** {f(F['data'])}"]
    if F.get("sci"):
        shows.append(f"**Scientists say (not from our data):** {f(F['sci'])}")
    careful = ["", f"**Careful:** {f(F['careful'])}"] if F.get("careful") else []
    note = ["", f"Note: {f(F['note'])}"] if F.get("note") else []
    chart_line = "**Chart:** " + ", ".join(f"`{c}`" for c in F["charts"])
    if F.get("old_charts"):
        chart_line += " (the detailed version: " + ", ".join(f"`{c}`" for c in F["old_charts"]) + ")"
    chart = ["", chart_line]
    anim = ANIMS.get(str(n))
    if anim:
        chart += ["", f"**Animation:** `{anim['html']}` (open it in a web browser and press ▶ Play. It is also on the "
                      "Findings page of the app.)"]
    head = [f"### {n}. {title}", "", f"**The question:** {f(F['question'])}", ""]
    main = head + data + math + rel + pics + read + short + shows + careful + note + chart
    wb = word_box("\n".join(main), F.get("words", {}), n, p)
    words_md = ["", "**Word box**"] + [f"- {w}: {m}" for w, m in wb]
    md = "\n".join(main + words_md)
    left = "\n".join(head[2:] + data + math + rel + short + shows + careful + note + chart + words_md).strip()
    card = {"n": n, "section": p, "section_name": sec.NAME, "title": title, "question": f(F["question"]),
            "markdown": left, "chart_read": "\n".join(read[2:]), "charts": F["charts"], "old_charts": F.get("old_charts", []),
            "facts_file": f"numbers/{FILES.get(n, '')}", "prose_words": prose_words(md)}
    return md, card, wb


front = ["# NASA Beyond Earth: what we found", "",
       fill("This guide explains {S_n_findings} things we found in NASA's \"Beyond Earth\" data files, in plain words, "
            "without leaving out anything important.", 1, "A"), "",
       "## How this guide works", "",
       fill("- There are {S_n_parts} parts, one for each data file.", 1, "A"),
       "- Each part starts with **Meet the data**. It tells you what one row of the file is and what every column we use means. Read it first!",
       "- Then come the findings. Every finding has the same boxes:",
       "  - **The question** we asked.",
       "  - **The data we used**: which rows and which columns. Column names from the files look `like this`.",
       "  - **The math**, step by step, with real numbers.",
       "  - **The simple relationship**: the whole idea in one line, with arrows.",
       "  - **How to read the chart**: what the bottom, the side, the bars, dots and colours mean, and what to look for.",
       "  - **In short**: the idea with an everyday example.",
       "  - **Our data shows** (we counted it ourselves) and **Scientists say** (known science from outside our files).",
       "  - **Careful**: a trap to watch out for.",
       "  - **Animation**: the finding as a moving picture, made from the same numbers. Open it on the Findings page of the "
       "app, or open the file in `animations/` in a web browser, and press ▶ Play. Before you press Play you see the "
       "finished picture.",
       "  - **Word box**: every hard word, explained. All the words are also in the master word list at the end.",
       "- Every number was worked out by our code and saved in the `numbers/` folder. Nobody typed a number by hand.",
       "- Where our number is different from the field guide, a line starting with \"Note:\" says so.", "",
       "**Our space rulers.** Space is so big that we use special rulers:", "",
       "| Ruler | How long it is | What we measure with it |", "|---|---|---|",
       fill("| Earth-Sun distance (AU) | about {S_au_round} million km, the distance from the Sun to Earth | how far asteroids are from the Sun |", 1, "A"),
       fill("| Moon distance | {S_ld_km} km, the distance from Earth to the Moon | how close a space rock passes by Earth |", 1, "A"),
       fill("| light-year | how far light travels in one year (light goes about {S_light_kms} km every second) | how far away stars are |", 1, "A"),
       fill("| Earth size | {S_earth_width} km, the width of Earth | how big planets around other stars are |", 1, "A"),
       ""] if FULL else [f"# Test file: part(s) {args.parts} only", ""]
if PENDING:
    front[3:3] = [f"> **Work in progress:** part {', '.join(PENDING)} still being rewritten. Until then, "
                  "those parts show the first (harder) version, with its charts.", ""]
out = list(front)

all_words: dict[str, tuple[str, str]] = {}
cards, meets, words_report = [], [], []
n_findings = 0
for s in args.parts:
    if s in PENDING:
        old = [c for c in OLD if c["section"] == s]
        out += [f"## Part {s}: {old[0]['section_name']}", "",
                "*Being rewritten right now. This is the first version, with its charts.*", ""]
        for c in old:
            pics = "\n".join(f"![Chart for finding {c['n']}]({ch})" for ch in c["charts"])
            body = c["markdown"].replace("**Chart:**", pics + "\n\n**Chart:**", 1)
            out += [f"### {c['n']}. {c['title']}", "", body, "", "---", ""]
            cards.append({**c, "markdown": body, "question": "", "chart_read": "", "old_charts": [], "first_version": True})
            n_findings += 1
        continue
    if s not in SEC:
        continue
    sec = SEC[s]
    out += [f"## Part {s}: {sec.NAME}", ""]
    md, card, wb = render_meet(sec)
    out += [md, "", "---", ""]
    meets.append(card)
    words_report.append((f"{s} meet", card["prose_words"]))
    for w, m in wb:
        all_words.setdefault(w.lower(), (w, m))
    for F in sec.FINDINGS:
        md, card, wb = render_finding(sec, F)
        out += [md, "", "---", ""]
        cards.append(card)
        n_findings += 1
        words_report.append((str(F["n"]), card["prose_words"]))
        for w, m in wb:
            all_words.setdefault(w.lower(), (w, m))
out += ["## Master word list (A to Z)", ""]
out += [f"- **{w}**: {m}" for _, (w, m) in sorted(all_words.items(), key=lambda kv: kv[0].lstrip("'\"").lower())]

if FULL:
    assert n_findings == n_all, (n_findings, n_all)
text = "\n".join(out) + "\n"
target = Path(args.out) if args.out else hp.PROJECT / "FINDINGS.md"
target.write_text(text)
if FULL:
    (hp.NUMBERS / "BF_findings.json").write_text(json.dumps(cards, indent=1, ensure_ascii=False))
    (hp.NUMBERS / "BF_meet_the_data.json").write_text(json.dumps(meets, indent=1, ensure_ascii=False))
print(f"{hp.rel(target) if target.is_relative_to(hp.PROJECT) else target}: {n_findings} findings, "
      f"{len(meets)} 'Meet the data' parts, {len(all_words)} words in the master list")
print("words to read (not counting tables, chart boxes and word boxes): " +
      ", ".join(f"{k}: {v}" for k, v in words_report))
