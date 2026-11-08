"""Write README.md, a short note about the project, with every number filled in from numbers/.

The text below has placeholders like <<BF01_asteroid_belt_lanes.gap_count>> (file in numbers/, then key); they are
replaced by the "shown" value of that row. Numbers that only the README needs (the resonance distances, the crater
exponents, the file totals) are worked out here and saved first, in numbers/RD_readme.csv, like every other number.
At the end the README is read back and every number outside the math, code and references must be in numbers/.

    cd notebooks && ../.venv/bin/python make_readme.py
"""
from __future__ import annotations

import json
import math
import re
import sys
from datetime import date
from functools import lru_cache
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import helpers as hp  # noqa: E402

ROOT, NUM = hp.PROJECT, hp.NUMBERS
PART = {"asteroids": "A", "close_approaches": "B", "fireballs": "C", "space_weather": "D", "stars": "E",
        "planets": "F", "craters": "G"}
SOURCE = {"asteroids": "JPL Small-Body Database", "close_approaches": "JPL CNEOS close approaches",
          "fireballs": "JPL CNEOS fireballs", "space_weather": "NASA OMNIWeb, 5-minute values",
          "stars": "ESA Gaia DR3", "planets": "NASA Exoplanet Archive", "craters": "Robbins lunar crater database"}


def data_files() -> pd.DataFrame:
    """The seven data files (the Home page shows the same table). Rebuilt when the data is here, else read back."""
    out = NUM / "data_files.csv"
    if hp.HAVE_DATA and all((hp.CACHE / f"{n}.parquet").exists() for n in hp.FILES):
        import pyarrow.parquet as pq
        rows = []
        for name, path in hp.FILES.items():
            md = pq.ParquetFile(hp.CACHE / f"{name}.parquet").metadata
            rows.append({"part": PART[name], "file": path.name, "rows": md.num_rows, "columns": md.num_columns,
                         "CSV size (MB)": round(path.stat().st_size / 1e6, 1)})
        pd.DataFrame(rows).sort_values("part").to_csv(out, index=False)
    return pd.read_csv(out)


@lru_cache(None)
def table(stem: str) -> dict:
    df = pd.read_csv(NUM / f"{stem}.csv", dtype={"shown": str})
    return dict(zip(df["key"], df["shown"]))


def value(stem: str, key: str) -> float:
    df = pd.read_csv(NUM / f"{stem}.csv")
    return float(df.loc[df["key"] == key, "value"].iloc[0])


def readme_numbers(files: pd.DataFrame) -> None:
    """Numbers that only the README needs, saved like all the others."""
    rows = []

    def add(key, v, shown, unit="", source="worked out in notebooks/make_readme.py"):
        rows.append({"key": key, "value": v, "shown": shown, "unit": unit, "source": source})

    by = files.set_index("file")
    for name, path in hp.FILES.items():
        add(f"rows_{name}", int(by.loc[path.name, "rows"]), f"{int(by.loc[path.name, 'rows']):,}", "rows",
            "numbers/data_files.csv")
    mb = float(files["CSV size (MB)"].sum())
    add("raw_mb", mb, f"{mb:,.0f}", "MB", "numbers/data_files.csv (sum)")
    aj = value("AN06_trojan_swarms", "jupiter_distance")
    for n, m in [(3, 1), (5, 2), (7, 3), (2, 1)]:
        a = aj * (m / n) ** (2 / 3)
        add(f"res_{n}_{m}", a, f"{a:.2f}", "AU", "a_J (m/n)^(2/3), a_J from numbers/AN06_trojan_swarms.csv")
    an = value("BF05_neptune_rhythm", "neptune_a")
    add("neptune_a2", an, f"{an:.2f}", "AU", "numbers/BF05_neptune_rhythm.csv")
    ap = an * 1.5 ** (2 / 3)
    add("a_3_2", ap, f"{ap:.1f}", "AU", "a_N (3/2)^(2/3)")
    pairs = [("n_ge_1", "n_ge_10", "1_10"), ("n_ge_10", "n_ge_100", "10_100"), ("n_ge_100", "n_ge_1000", "100_1000")]
    for k1, k2, tag in pairs:
        b = math.log10(value("BF30_size_rule", k1) / value("BF30_size_rule", k2))
        add(f"b_{tag}", b, f"{b:.2f}", "", "log10 of the ratio, numbers/BF30_size_rule.csv")
    sw = hp.load_parquet("space_weather", columns=["datetime_utc"])["datetime_utc"] if hp.HAVE_DATA else None
    if sw is not None:
        add("sw_from", 0, str(sw.iloc[0])[:10], "date", "data_cache/space_weather.parquet")
        add("sw_to", 0, str(sw.iloc[-1])[:10], "date", "data_cache/space_weather.parquet")
    else:                                          # keep the saved dates when the data is not here
        old = table("RD_readme")
        add("sw_from", 0, old["sw_from"], "date", "data_cache/space_weather.parquet")
        add("sw_to", 0, old["sw_to"], "date", "data_cache/space_weather.parquet")
    nd = len(pd.read_csv(NUM / "BF_guide_differences.csv"))
    add("n_guide_diff", nd, str(nd), "", "numbers/BF_guide_differences.csv (rows)")
    pd.DataFrame(rows).to_csv(NUM / "RD_readme.csv", index=False)
    table.cache_clear()


TEMPLATE = r"""# NASA Beyond Earth

**Thirty-two small results from seven public NASA data sets**

Sheridan Datathon 2026, NASA track. Last revised <<DATE>>.

```
Contents
   0  Abstract
   1  The data
   2  How a number gets from a CSV file to the screen
   3  The math
   4  Results
   5  Figures
   6  Running it
   7  Caveats
   8  Files
      References
```

## 0. Abstract

We looked at seven public data files from NASA and JPL: <<RD_readme.rows_asteroids>> asteroids and comets,
<<RD_readme.rows_close_approaches>> close passes by Earth, <<RD_readme.rows_fireballs>> fireballs,
<<RD_readme.rows_space_weather>> five-minute readings of the solar wind and Earth's magnetic field
(<<RD_readme.sw_from>> to <<RD_readme.sw_to>>), <<RD_readme.rows_stars>> nearby stars from Gaia,
<<RD_readme.rows_planets>> confirmed planets around other stars, and <<RD_readme.rows_craters>> craters on the Moon.
From these we pulled out 32 results. Most of them are old physics showing up in new numbers: Kepler's third law,
Jupiter's resonances, the 27-day turn of the Sun. Some are about the data itself: where it has holes, and why a count
can say more about who was looking, and when, than about what is out there.

Every number that comes from the data, in this note, in `FINDINGS.md` and in the app, is computed by a script and
stored in `numbers/`. None of them is typed by hand.

## 1. The data

<<DATA_TABLE>>

The CSV files add up to about <<RD_readme.raw_mb>> MB, so they are not in this repository (see section 6).

## 2. How a number gets from a CSV file to the screen

```
  NASA CSV files           notebooks/BF_*.py               numbers/*.csv
  (not in git)   ------->  one script per part    ------>  key, value, shown, unit, source
                                 |                               |
                                 v                               v
                            charts/*.png            make_findings.py    -->  FINDINGS.md
                                                    make_space_anims.py -->  animations/*.html
                                                    make_readme.py      -->  README.md
                                                    app.py (Streamlit) reads all of the above
```

A number exists once, as one row of a table in `numbers/`. For example, from `numbers/BF01_asteroid_belt_lanes.csv`:

```
key,value,shown,unit,source
<<ROW_EXAMPLE>>
```

The text is written with placeholders such as `{gap_count}` and the scripts fill them in. After that,
`notebooks/check_findings_numbers.py` reads `FINDINGS.md` back and stops if it finds a number that is not in
`numbers/`. This README goes through the same check.

## 3. The math

Everything below is high-school physics or a line of statistics. Each part says which findings use it.

### 3.1 Kepler's third law and the empty lanes (findings 1 and 5)

For anything going around the Sun, the time for one trip $P$ (in years) and the average distance $a$ (in AU, the
Earth-Sun distance) obey

$$P^2 = a^3 .$$

So a rock at distance $a$ goes around $(a_J/a)^{3/2}$ times for each trip of Jupiter. When that number is a simple
fraction $n/m$, Jupiter pulls on the rock at the same point of its path again and again, and over millions of years
the rock is thrown out. Solving for the distance:

$$a_{n:m} = a_J \left(\frac{m}{n}\right)^{2/3} .$$

With $a_J$ = <<AN06_trojan_swarms.jupiter_distance>> AU (the middle distance of Jupiter's Trojans in our file):

| ratio $n:m$ | predicted $a$ (AU) | dip in the data (AU) |
|---|---|---|
| 3:1 | <<RD_readme.res_3_1>> | <<BF01_asteroid_belt_lanes.dip1_a>> |
| 5:2 | <<RD_readme.res_5_2>> | <<BF01_asteroid_belt_lanes.dip2_a>> |
| 7:3 | <<RD_readme.res_7_3>> | <<BF01_asteroid_belt_lanes.dip3_a>> |
| 2:1 | <<RD_readme.res_2_1>> | <<BF01_asteroid_belt_lanes.dip4_a>> |

The same rule works the other way past Neptune. Objects that go around twice while Neptune goes around three times
are never near Neptune when they cross its path, so they are safe there:

$$a = a_N \left(\tfrac{3}{2}\right)^{2/3} = <<RD_readme.a_3_2>>\ \text{AU},$$

with $a_N$ = <<RD_readme.neptune_a2>> AU. The crowd in the data sits at <<BF05_neptune_rhythm.band_lo>> to
<<BF05_neptune_rhythm.band_hi>> AU (<<BF05_neptune_rhythm.band_count>> objects, about
<<BF05_neptune_rhythm.band_vs_sides>> times the slices beside it).

### 3.2 Size from brightness (findings 2, 3 and 7)

Most asteroids have no measured size, only an absolute magnitude $H$ (how bright the rock would look from a fixed
standard distance; bigger $H$ means fainter). With a guess for the albedo $p_V$, the share of sunlight the surface
reflects:

$$D = \frac{1329\ \text{km}}{\sqrt{p_V}}\; 10^{-H/5} .$$

With $p_V$ = <<BF03_spin_limit.albedo_guess>> and $H$ = <<BF07_hazard_formula.H_cut>> this gives
<<BF07_hazard_formula.size_H22>> m. That is the size line in the "potentially hazardous" rule: $H \le$
<<BF07_hazard_formula.H_cut>> and a closest orbit distance (MOID) of at most <<BF07_hazard_formula.moid_cut>> AU.
Of the <<BF07_hazard_formula.pha_y>> rocks flagged hazardous, <<BF07_hazard_formula.match>>
(<<BF07_hazard_formula.match_pct>>) pass both lines exactly as written.

### 3.3 The spin barrier (finding 3)

A pile of loose rubble held together only by its own gravity comes apart when the outward pull of the spin at its
equator beats gravity, $\omega^2 R > GM/R^2$. With $M = \tfrac{4}{3}\pi R^3\rho$ and $P = 2\pi/\omega$ the size
cancels out:

$$P_{\min} = \sqrt{\frac{3\pi}{G\rho}} .$$

For rock with a density of about $2\ \text{g/cm}^3$ this is between two and three hours. We use the usual line of
<<BF03_spin_limit.limit_h>> hours (Pravec and Harris 2000). Only <<BF03_spin_limit.big_fast>> of
<<BF03_spin_limit.big_n>> asteroids wider than <<BF03_spin_limit.big_m>> m spin faster
(<<BF03_spin_limit.big_fast_pct>>). Small asteroids are often solid, and <<BF03_spin_limit.small_fast_pct>> of them do.

### 3.4 Jupiter's two swarms (finding 6)

The Trojans sit near the two points that make an equilateral triangle with the Sun and Jupiter, one ahead of Jupiter
and one behind it. The place of an asteroid along its path is its mean longitude

$$L = \Omega + \omega + M \pmod{360^\circ},$$

the sum of three angles in the file (`om`, `w`, `ma`). The two peaks in our file are
<<BF06_trojan_swarms.peaks_apart>> degrees apart: <<BF06_trojan_swarms.n_ahead>> asteroids ahead of Jupiter and
<<BF06_trojan_swarms.n_behind>> behind.

### 3.5 Fair share on a sphere (findings 10 and 32)

The part of a sphere's surface between latitudes $\varphi_1$ and $\varphi_2$ is

$$f = \frac{\sin\varphi_2 - \sin\varphi_1}{2} .$$

So the band from the equator to 30 degrees north is a quarter of Earth's surface, and if fireballs fell anywhere at
random it would get <<BF10_fireballs_anywhere.band_0_30_exp>> of the <<BF10_fireballs_anywhere.located>> with a known
place. It got <<BF10_fireballs_anywhere.band_0_30_obs>>. On the Moon the same formula turns crater counts into counts
per area: the band from the equator to 10 degrees north has <<BF32_polar_craters.area_ratio>> times the area of the
band around the north pole, and the polar band has <<BF32_polar_craters.ratio_north>> times as many craters per
square kilometre.

### 3.6 Local solar time (finding 11)

The Sun crosses 15 degrees of longitude every hour, so for a fireball at longitude $\lambda$ (east positive)

$$t_\text{local} = t_\text{UTC} + \frac{\lambda}{15^\circ}\ \text{hours}.$$

An example from the file: <<BF11_fewer_at_dawn.ex_utc_h>>:<<BF11_fewer_at_dawn.ex_utc_min>> UTC at
<<BF11_fewer_at_dawn.ex_lon>> degrees east is <<BF11_fewer_at_dawn.ex_local_clock>> local time.

### 3.7 Storms and the 27-day echo (findings 12 to 17)

The storm meter is SYM-H, in nanotesla: how far Earth's magnetic field near the equator is pushed down. Following
Gonzalez et al. (1994), a storm is SYM-H at or below <<BF12_storm_cycle.storm_cut>> nT and a strong storm at or
below <<BF12_storm_cycle.strong_cut>> nT. To see whether the Sun repeats itself, we compare the daily mean wind speed
$v$ with itself shifted by $\tau$ days:

$$r(\tau) = \frac{\sum_t (v_t - \bar v)(v_{t+\tau} - \bar v)}{\sum_t (v_t - \bar v)^2} .$$

$r$ is 1 for a perfect echo and 0 for none. We get $r$ = <<BF14_repeats_27_days.all_27>> at
<<BF14_repeats_27_days.best_lag>> days, the time the Sun takes to turn once as seen from Earth, and only
<<BF14_repeats_27_days.all_13>> at <<BF14_repeats_27_days.lag13>> days (Figure 2). The extra storms around March and
September (finding 15) are the Russell-McPherron effect (Russell and McPherron 1973).

### 3.8 Stars: true brightness, speed and groups (findings 18 to 22)

Gaia gives the apparent brightness $G$ (in magnitudes, so bigger is fainter) and the parallax $\varpi$ in
milliarcseconds. The true brightness is

$$M_G = G + 5\log_{10}\varpi - 10 .$$

We call a star a white dwarf when $M_G$ > <<BF18_star_families.wd_a>> + <<BF18_star_families.wd_b>> times its colour
(BP-RP) and the colour is below <<BF18_star_families.wd_colour>>. The sideways speed, from the proper motion $\mu$
(arcseconds per year) and the distance $d$ (parsecs), is

$$v_t = 4.74\,\mu\,d\ \ \text{km/s}.$$

The star groups of finding 21 come from DBSCAN (Ester et al. 1996) run on place and sideways speed together: a star
is in a group when at least <<BF21_star_clusters.min_samples>> stars are within <<BF21_star_clusters.eps>> of it in
that space. It finds <<BF21_star_clusters.groups>> groups. The biggest, <<BF21_star_clusters.top_stars>> stars at
<<BF21_star_clusters.top_dist>> parsecs, is the Pleiades.

### 3.9 Planets (findings 23 to 28)

A transit dims a star by the share of its disc that the planet covers:

$$\frac{\Delta F}{F} = \left(\frac{R_p}{R_\star}\right)^2 .$$

For Earth in front of the Sun that is about $8 \times 10^{-5}$, which is why the planets found this way are mostly big
or close to their star. The starlight a planet gets, compared with Earth, is $S = L/a^2$ ($L$ in Suns, $a$ in AU). We
call a planet "just right" when <<BF28_just_right_zone.insol_lo>> $\le S \le$ <<BF28_just_right_zone.insol_hi>> and it
is less than <<BF28_just_right_zone.size_cut>> Earths wide. To draw every such planet around one star, we put it
where it would get the same starlight from the Sun:

$$d = \frac{1}{\sqrt{S}}\ \text{AU}.$$

That gives <<BF28_just_right_zone.n>> planets. The closest is <<BF28_just_right_zone.top_name>>,
<<BF28_just_right_zone.top_pc>> parsecs away.

### 3.10 Crater sizes (finding 30)

If the number of craters at least $D$ wide follows a power law $N(\ge D) \propto D^{-b}$, then going ten times wider
divides the count by $10^b$, so

$$b = \log_{10} \frac{N(\ge D)}{N(\ge 10D)} .$$

From 1 to 10 km we get $b$ = <<RD_readme.b_1_10>>, from 10 to 100 km <<RD_readme.b_10_100>>, and from 100 to 1000 km
<<RD_readme.b_100_1000>> (Figure 3). A steady $b$ near 2 is all that "ten times wider, about 50 to 100 times rarer"
means.

## 4. Results

One line each. The full text, with a chart and an animation for every result, is in `FINDINGS.md` and in the app.

<<RESULTS>>

## 5. Figures

![Figure 1](charts/A05_a_histogram_1.7-5.5AU.png)

**Figure 1.** Asteroids per 0.01 AU slice of average distance from the Sun (log scale). The narrow dips are the empty
lanes of section 3.1.

![Figure 2](charts/BF14_27_day_repeat.png)

**Figure 2.** Correlation of the daily solar-wind speed with itself $N$ days earlier. The peak at 27 days is the Sun's
turn (section 3.7).

![Figure 3](charts/BF30_size_rule.png)

**Figure 3.** Moon craters at least $D$ wide, both axes on a log scale. A straight line is a power law (section 3.10).

## 6. Running it

```
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/streamlit run app.py            # then open http://localhost:8501
```

The app has three pages: Home, Findings (the 32 results with a chart and an animation each) and Charts. It only
reads `numbers/`, `charts/`, `animations/` and `FINDINGS.md`, which are all in the repository. The animations are
plain HTML files, so they also open on their own in any browser.

To redo the analysis from the raw files, put the data folder `NASA Beyond Earth/` (the seven CSV files) in the
project folder and run, from `notebooks/`:

```
../.venv/bin/python run_notebook.py BF_A_asteroids.py     # one per part: A, B_C, D, E, F, G
../.venv/bin/python make_findings.py                      # FINDINGS.md
../.venv/bin/python check_findings_numbers.py             # every number in FINDINGS.md is in numbers/
../.venv/bin/python make_space_anims.py                   # the 32 animations
../.venv/bin/python check_space_anims.py                  # plays each one in headless Chrome
../.venv/bin/python make_readme.py                        # this file
```

`check_app.py`, run from the project folder, opens every page of the app without a browser and fails on any error.

## 7. Caveats

* Most counts here are counts of what was found, not of what is there. The discovery, close-pass and planet results
  (findings 4, 8, 9, 23 and 26) say as much about telescopes as about space.
* Gaia distances toward the middle of the Milky Way are often poor (finding 20). We flag stars with RUWE above
  <<BF18_star_families.ruwe_cut>> but we do not fix them.
* Some radial speeds above <<BF22_fast_movers.escape_speed>> km/s are more likely measuring errors than real stars
  (finding 22).
* The animations are drawings. Where a drawing is not data, for example a planet's place along its path or a turning
  globe, it says so on screen.
* We compared our numbers with the datathon's field guide. In <<RD_readme.n_guide_diff>> places they differ, and
  `FINDINGS.md` says so in a line that starts with "Note".

## 8. Files

```
app.py                     the Streamlit app (Home, Findings, Charts)
app_pages/                 the three pages
check_app.py               opens every page without a browser, fails on any error
FINDINGS.md                the 32 results in plain words (notebooks/make_findings.py)
notebooks/                 one analysis script per part (BF_A ... BF_G), with the notebook next to it,
                           and the scripts that write FINDINGS.md, the animations and this file
notebooks/findings_text/   the words of FINDINGS.md, with placeholders for the numbers
numbers/                   every number, as key, value, shown, unit, source
charts/                    the charts, as PNG files
animations/                32 animations, one HTML file each (plain 2D canvas, no WebGL)
requirements.txt           the Python packages
```

## References

* Ester, M., Kriegel, H.-P., Sander, J. and Xu, X. (1996). A density-based algorithm for discovering clusters in
  large spatial databases with noise. Proceedings of KDD-96, 226-231.
* Fischer, D. A. and Valenti, J. (2005). The planet-metallicity correlation. The Astrophysical Journal 622, 1102-1117.
* Fulton, B. J. et al. (2017). The California-Kepler Survey. III. A gap in the radius distribution of small planets.
  The Astronomical Journal 154, 109.
* Gaia Collaboration, Vallenari, A. et al. (2023). Gaia Data Release 3: Summary of the content and survey
  properties. Astronomy and Astrophysics 674, A1.
* Gonzalez, W. D. et al. (1994). What is a geomagnetic storm? Journal of Geophysical Research 99, 5771-5792.
* King, J. H. and Papitashvili, N. E. (2005). Solar wind spatial scales in and comparisons of hourly Wind and ACE
  plasma and magnetic field data. Journal of Geophysical Research 110, A02104.
* Kirkwood, D. (1867). Meteoric Astronomy. J. B. Lippincott, Philadelphia.
* Mazeh, T., Holczer, T. and Faigler, S. (2016). Dearth of short-period Neptunian exoplanets: a desert in period-mass
  and period-radius planes. Astronomy and Astrophysics 589, A75.
* Pravec, P. and Harris, A. W. (2000). Fast and slow rotation of asteroids. Icarus 148, 12-20.
* Robbins, S. J. (2019). A new global database of lunar impact craters >1-2 km: 1. Crater locations and sizes,
  comparisons with published databases, and global analysis. Journal of Geophysical Research: Planets 124, 871-892.
* Russell, C. T. and McPherron, R. L. (1973). Semiannual variation of geomagnetic activity. Journal of Geophysical
  Research 78, 92-108.

Data: JPL Small-Body Database and CNEOS (asteroids, close approaches, fireballs), NASA OMNIWeb (solar wind), ESA Gaia
DR3 (stars), NASA Exoplanet Archive (planets), Robbins (2019) via the LRO mission (Moon craters).

Corrections welcome: open an issue.
"""


# which key-number lines (numbers/AN_keys.json) say the most about each result
PICK = {1: [0, 1], 3: [0, 1], 4: [0, 1], 6: [1, 2, 3], 7: [0, 2], 8: [0, 1], 9: [0, 1], 10: [1, 3], 11: [0, 1],
        12: [0, 2], 13: [1, 2], 14: [0, 1], 15: [0, 1], 16: [0, 4], 17: [0, 1], 18: [1, 2, 3], 20: [0, 2], 21: [0, 1],
        22: [0, 3], 23: [1, 2], 24: [0, 1], 25: [1, 2, 3], 26: [2, 4], 27: [1, 3], 28: [0, 1], 29: [1], 30: [0, 1],
        31: [1, 2], 32: [1]}


def results_block() -> str:
    idx = json.loads((NUM / "AN_index.json").read_text())
    keys = json.loads((NUM / "AN_keys.json").read_text())
    cards = json.loads((NUM / "BF_findings.json").read_text())
    part_name = {c["section"]: c["section_name"] for c in cards}
    out, last = [], None
    for k in sorted(idx, key=int):
        e = idx[k]
        if e["part"] != last:
            last = e["part"]
            out.append(f"\n**Part {last}: {part_name.get(last, last)}**\n")
        ks = keys[k]
        if int(k) == 17:                       # its first line was broken in two
            ks = [ks[0] + " " + ks[1]] + ks[2:]
        parts = [ks[i].rstrip(".") for i in PICK.get(int(k), [0]) if i < len(ks)]
        out.append(f"{e['n']}. {e['title']}. " + ". ".join(parts) + ".")
    return "\n".join(out).strip()


def data_block(files: pd.DataFrame) -> str:
    src = {p.name: SOURCE[n] for n, p in hp.FILES.items()}
    lines = ["| part | file | from | rows | columns | MB |", "|---|---|---|---|---|---|"]
    for r in files.itertuples(index=False):
        lines.append(f"| {r.part} | `{r.file}` | {src.get(r.file, '')} | {int(r.rows):,} | {int(r.columns)} | "
                     f"{getattr(r, '_4'):,.1f} |")
    return "\n".join(lines)


def fill(text: str) -> str:
    def one(m):
        stem, key = m.group(1), m.group(2)
        return str(table(stem)[key])
    return re.sub(r"<<([A-Za-z0-9_]+)\.([A-Za-z0-9_]+)>>", one, text)


TOKEN = re.compile(r"(?<![\w.:])[+-]?\d[\d,]*(?:\.\d+)?(?![\w:])")


def allowed() -> set:
    ok = {str(y) for y in range(1800, 2201)}
    for p in NUM.glob("*.csv"):
        if p.stat().st_size > 2_000_000:
            continue
        for col_values in pd.read_csv(p, dtype=str).fillna("").to_numpy().T:
            for v in col_values:
                ok.update(t.lstrip("+") for t in TOKEN.findall(v))
                try:
                    x = float(v.replace(",", "").replace("%", ""))
                except ValueError:
                    continue
                for k in (0, 1, 2):
                    ok.update({f"{x:,.{k}f}", f"{x:.{k}f}"})
    for lines in json.loads((NUM / "AN_keys.json").read_text()).values():
        for s in lines:
            ok.update(t.lstrip("+") for t in TOKEN.findall(s))
    return ok


def unknown_numbers(md: str) -> list[str]:
    body = md.split("## References")[0]
    body = re.sub(r"```.*?```", " ", body, flags=re.S)          # code blocks
    body = re.sub(r"\$\$.*?\$\$", " ", body, flags=re.S)        # display math
    body = re.sub(r"\$[^$\n]+\$", " ", body)                    # inline math
    body = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", body)           # pictures
    body = re.sub(r"`[^`\n]+`", " ", body)                      # file names
    body = re.sub(r"(?m)^(\s*)\d+\. ", r"\1", body)             # list numbers
    body = re.sub(r"(?m)^#{1,6}\s+[\d.]+\s", "", body)            # section numbers
    body = re.sub(r"(?m)^\s*\|.*\|\s*$", lambda m: m.group(0) if "<" not in m.group(0) else " ", body)
    ok = allowed()
    words = ("finding", "findings", "section", "Figure", "Part", "part", "between", "from", "to", "and", "Sections")
    bad = []
    for m in TOKEN.finditer(body):
        tok = m.group(0).lstrip("+").rstrip(",")
        if tok in ok:
            continue
        before = body[max(0, m.start() - 12):m.start()]
        if any(before.rstrip().endswith(w) for w in words) and len(tok) <= 2:
            continue                                            # "findings 10 and 32", "section 3.1"
        bad.append(f"{tok!r} near {body[max(0, m.start() - 40):m.end() + 20]!r}")
    return bad


def main() -> None:
    files = data_files()
    readme_numbers(files)
    row = pd.read_csv(NUM / "BF01_asteroid_belt_lanes.csv", dtype=str)
    row = row[row["key"] == "gap_count"].iloc[0]
    example = ",".join(f'"{v}"' if "," in str(v) else str(v) for v in row.fillna("").tolist())
    md = (TEMPLATE.replace("<<DATE>>", f"{date.today():%B %Y}").replace("<<DATA_TABLE>>", data_block(files))
          .replace("<<RESULTS>>", results_block()).replace("<<ROW_EXAMPLE>>", example))
    md = fill(md)
    left = re.findall(r"<<[^>]+>>", md)
    assert not left, left
    (ROOT / "README.md").write_text(md)
    bad = unknown_numbers(md)
    print(f"README.md written ({len(md.splitlines())} lines).")
    if bad:
        print("Numbers not found in numbers/:")
        for b in bad:
            print("  ", b)
        sys.exit(1)
    print("Number check: every number in the text is in numbers/ (math, code and references not counted).")


if __name__ == "__main__":
    main()
