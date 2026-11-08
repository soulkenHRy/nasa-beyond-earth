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
    tr_meta = json.loads((NUM / "FC_training.json").read_text())
    add("fc_minutes", tr_meta["minutes"], f"{tr_meta['minutes']:.0f}", "minutes", "numbers/FC_training.json")
    add("fc_inputs", tr_meta["inputs"], str(tr_meta["inputs"]), "", "numbers/FC_training.json")
    for k in ("train", "val", "test"):
        txt = tr_meta["validation" if k == "val" else k]
        add(f"fc_{k}", 0, txt, "dates", "numbers/FC_training.json")
    reg = pd.read_csv(NUM / "FC_regression_scores.csv")
    bz6 = float(reg[(reg["target"] == "bz_gsm_nT") & (reg["horizon"] == "6 h")]["r2"].iloc[0])
    add("fc_bz_r2_6h", bz6, f"{bz6:.2f}", "", "numbers/FC_regression_scores.csv")
    add("fc_cov_min", reg["interval_coverage_pct"].min(), f"{reg['interval_coverage_pct'].min():.0f}", "%",
        "numbers/FC_regression_scores.csv")
    add("fc_cov_max", reg["interval_coverage_pct"].max(), f"{reg['interval_coverage_pct'].max():.0f}", "%",
        "numbers/FC_regression_scores.csv")
    dd = pd.read_csv(NUM / "FC_daily_scores.csv")
    sp = float(dd["base_rate_pct"].iloc[0])
    add("day_storm_pct", sp, f"{sp:.1f}", "%", "numbers/FC_daily_scores.csv")
    clim_to = str(pd.read_csv(NUM / "FC_daily_climatology.csv")["to"].iloc[0])
    add("day_test", 0, f"{tr_meta['test'][:10]} to {clim_to}", "dates", "numbers/FC_training.json, FC_daily_climatology.csv")
    # Section 3 (the math in simple words) shows a few small sums of its own.
    lag = value("BF06_trojan_swarms", "lagrange")
    add("trojan_apart", 2 * lag, f"{2 * lag:.0f}", "degrees", "2 x the Lagrange angle, numbers/BF06_trojan_swarms.csv")
    add("hours_per_day", 24, "24", "hours", "known science (one turn of Earth, noon to noon)")
    h, m = int(value("BF11_fewer_at_dawn", "ex_utc_h")), int(value("BF11_fewer_at_dawn", "ex_utc_min"))
    off = round(60 * value("BF11_fewer_at_dawn", "ex_lon") / value("BF11_fewer_at_dawn", "deg_per_hour"))  # minutes
    loc = h * 60 + m + off
    assert f"{loc // 60:02d}:{loc % 60:02d}" == table("BF11_fewer_at_dawn")["ex_local_clock"], "the sum must match"
    src = "longitude / 15, numbers/BF11_fewer_at_dawn.csv"
    add("ex_utc_clock", 0, f"{h:02d}:{m:02d}", "time", "numbers/BF11_fewer_at_dawn.csv")
    add("ex_off_h", off // 60, str(off // 60), "hours", src)
    add("ex_off_min", off % 60, str(off % 60), "minutes", src)
    add("ex_off_clock", 0, f"{off // 60:02d}:{off % 60:02d}", "time", src)
    add("ex_local_ampm", 0, "AM" if loc < 12 * 60 else "PM", "", "numbers/BF11_fewer_at_dawn.csv")
    sun_km = 695_700.0
    add("sun_radius", sun_km, f"{sun_km:,.0f}", "km", "known science (the Sun's radius, IAU nominal value)")
    dip = 100 * (value("BF00_shared_facts", "earth_radius") / sun_km) ** 2
    add("earth_transit_pct", dip, f"{dip:.3f}", "%", "(Earth's radius / Sun's radius)^2, numbers/BF00_shared_facts.csv")
    folds = [value("BF30_size_rule", k) for k in ("r_1_10", "r_10_100", "r_100_1000")]
    add("fold_min", min(folds), f"{min(folds):.0f}", "", "numbers/BF30_size_rule.csv (smallest of the three ratios)")
    add("fold_max", max(folds), f"{max(folds):.0f}", "", "numbers/BF30_size_rule.csv (largest of the three ratios)")
    for k, v in (("fold_min_round", min(folds)), ("fold_max_round", max(folds))):
        r1 = float(f"{v:.1g}")
        add(k, r1, f"{r1:.0f}", "", "the ratio above, to one significant figure")
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
   3  The math explained in very simple English
   4  Results
   5  Forecasts
   6  Galaxy pictures
   7  Figures
   8  Running it
   9  Caveats
  10  Files
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

The CSV files add up to about <<RD_readme.raw_mb>> MB, so they are not in this repository (see section 8).

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

## 3. The math explained in very simple English

First, don't worry about all the equations. They are just tools scientists use to understand space.

This section explains how we used math to check what is happening with asteroids, planets, stars, the Sun and
craters. Each part is explained with simple examples, and its title says which findings use it.

### 3.1 Jupiter's gravity creates empty spaces between asteroids (findings 1 and 5)

**What is this about?**

Asteroids travel around the Sun, just like Earth does. But they don't all travel at the same speed. Some take a
short time to complete one trip around the Sun. Others take much longer.

There is a rule called Kepler's third law:

$$P^2 = a^3$$

You don't need to memorize it. It simply tells us:

* $P$ = how long an object takes to go around the Sun (in years).
* $a$ = how far the object is from the Sun (in AU).
* The farther away an object is, the longer its trip takes.

Now, what does Jupiter have to do with this? Imagine an asteroid going around the Sun. Every time Jupiter and that
asteroid meet at the same positions, Jupiter's gravity can pull on the asteroid. If this keeps happening again and
again, Jupiter can slowly push the asteroid away from that area.

Think of pushing a swing at the same time during every movement. The pushes can make the swing move more and more.

This creates empty spaces where fewer asteroids are found. Scientists call this an orbital resonance.

**What did we find?**

We used Jupiter's distance from the Sun (<<AN06_trojan_swarms.jupiter_distance>> AU) to calculate where these empty
spaces should be. A 3:1 pattern means the asteroid goes around the Sun 3 times while Jupiter goes around once.

| Asteroid orbit pattern | Math prediction | Actual empty space |
|---|---|---|
| 3:1 | <<RD_readme.res_3_1>> AU | <<BF01_asteroid_belt_lanes.dip1_a>> AU |
| 5:2 | <<RD_readme.res_5_2>> AU | <<BF01_asteroid_belt_lanes.dip2_a>> AU |
| 7:3 | <<RD_readme.res_7_3>> AU | <<BF01_asteroid_belt_lanes.dip3_a>> AU |
| 2:1 | <<RD_readme.res_2_1>> AU | <<BF01_asteroid_belt_lanes.dip4_a>> AU |

AU means the average distance between Earth and the Sun. Look at the table. The predicted locations and the actual
empty spaces are almost the same.

**What about Neptune?**

Neptune is much farther away from the Sun than Jupiter. Some objects beyond Neptune move in a special pattern:

* Neptune completes 3 trips around the Sun.
* The other object completes 2 trips.

This repeating pattern helps protect those objects from getting too close to Neptune. The same math says it happens
at <<RD_readme.a_3_2>> AU from the Sun. We found <<BF05_neptune_rhythm.band_count>> objects in this area, between
<<BF05_neptune_rhythm.band_lo>> and <<BF05_neptune_rhythm.band_hi>> AU. There were about
<<BF05_neptune_rhythm.band_vs_sides>> times more objects there than in the nearby areas.

**The main idea:** Jupiter's gravity creates empty spaces between asteroids. Neptune's gravity also helps create
special areas where objects can stay safely.

### 3.2 Finding the size of asteroids using brightness (findings 2, 3 and 7)

**What is this about?**

Most asteroids are too far away for scientists to measure their actual size directly. But scientists can measure
how bright they look. This gives them a way to estimate their size.

Think about two rocks:

* A small, shiny rock can look bright.
* A large, dark rock can look equally bright.

So brightness alone cannot tell us the exact size. Scientists also need to guess how much sunlight the asteroid's
surface reflects. This is called albedo.

* High albedo = reflects lots of sunlight.
* Low albedo = reflects little sunlight.

They use this formula:

$$D = \frac{1329}{\sqrt{p_V}} \times 10^{-H/5}$$

You only need to understand these letters:

* $D$ = estimated asteroid diameter, in kilometres.
* $H$ = how bright the asteroid is. A bigger number means fainter.
* $p_V$ = how much sunlight the asteroid reflects.

**What did we find?**

We used an average reflectiveness of <<BF03_spin_limit.albedo_guess>>. For an asteroid with an $H$ value of
<<BF07_hazard_formula.H_cut>>, the estimated size is about <<BF07_hazard_formula.size_H22>> metres wide.

This is important because scientists use two rules to identify potentially hazardous asteroids:

1. The asteroid has an $H$ value of <<BF07_hazard_formula.H_cut>> or lower.
2. Its orbit comes within <<BF07_hazard_formula.moid_cut>> AU of Earth's orbit.

MOID means Minimum Orbit Intersection Distance. In simple words, it tells us how close the asteroid's path can come
to Earth's path.

Out of <<BF07_hazard_formula.pha_y>> asteroids marked as potentially hazardous, <<BF07_hazard_formula.match>> passed
both rules. That is <<BF07_hazard_formula.match_pct>>.

**The main idea:** Scientists can estimate how big an asteroid is by looking at its brightness and guessing how
reflective its surface is.

### 3.3 Why some asteroids cannot spin too fast (finding 3)

**What is this about?**

Imagine a pile of small rocks. There is no glue holding them together. Gravity is the only thing keeping them in one
pile. Now imagine spinning that pile faster and faster. At some point, the spinning becomes so fast that the rocks
start flying away.

This is similar to what can happen to asteroids. Scientists call this the spin barrier. For an asteroid made of
loose rock, there is a limit to how fast it can spin before it breaks apart. For a typical rocky asteroid, that limit
is around <<BF03_spin_limit.limit_h>> hours for one full rotation (Pravec and Harris 2000). In other words, a loose
pile of rock spinning once every <<BF03_spin_limit.limit_h>> hours is close to its breaking point.

**What did we find?**

We looked at <<BF03_spin_limit.big_n>> asteroids wider than <<BF03_spin_limit.big_m>> metres whose spin has been
measured. Only <<BF03_spin_limit.big_fast>> of them spun faster than this limit. That is just
<<BF03_spin_limit.big_fast_pct>>.

But many small asteroids spin much faster. Of the <<BF03_spin_limit.small_n>> small ones in our data (narrower than
<<BF03_spin_limit.small_m>> metres), <<BF03_spin_limit.small_fast>> spin faster than this limit. That is
<<BF03_spin_limit.small_fast_pct>>.

Why? Because small asteroids can be solid rocks. They are not always just loose piles of stones. Solid rocks can
hold together better while spinning.

**The main idea:** Big asteroids are often loose piles of rocks, so they cannot spin too fast. Small asteroids can
sometimes be solid and spin much faster.

### 3.4 Why Jupiter has two groups of asteroids (finding 6)

**What is this about?**

Jupiter has two large groups of asteroids called Trojan asteroids. One group travels ahead of Jupiter. The other
group travels behind Jupiter. They stay in special positions because of the gravity of the Sun and Jupiter.

Imagine three people standing at the corners of an equilateral triangle:

* One person represents the Sun.
* One represents Jupiter.
* The third represents an asteroid group.

The two asteroid groups sit about <<BF06_trojan_swarms.lagrange>> degrees ahead of and behind Jupiter. The angle
between the two groups is <<RD_readme.trojan_apart>> degrees.

Scientists use something called mean longitude to calculate where an asteroid is along its orbit. The formula is:

$$L = \Omega + \omega + M$$

Don't worry about the three letters. They are simply three angles that help scientists calculate an asteroid's
position.

**What did we find?**

We found two large groups, with their middles <<BF06_trojan_swarms.peaks_apart>> degrees apart:

* <<BF06_trojan_swarms.n_ahead>> asteroids ahead of Jupiter.
* <<BF06_trojan_swarms.n_behind>> asteroids behind Jupiter.

**The main idea:** Jupiter has two large groups of asteroids. One group moves ahead of it, and the other follows
behind it.

### 3.5 How to fairly compare places on a round planet (findings 10 and 32)

**What is this about?**

Imagine throwing 1,000 balls randomly across the surface of Earth. You might expect some areas to get more balls
than others. But you cannot fairly compare two areas without looking at their sizes. For example:

* Area A is very large.
* Area B is very small.

Area A might have more balls simply because it has more space.

Scientists use math to calculate how much of Earth's surface belongs to each band of latitude. A latitude is a line
that tells us how far north or south a place is from the equator. The formula is:

$$f = \frac{\sin\varphi_2 - \sin\varphi_1}{2}$$

Here $\varphi_1$ and $\varphi_2$ are the latitudes of the two edges of the band. You don't need to understand the
sine function yet. The formula simply calculates how much of the sphere's surface belongs to a particular band.

**What did we find on Earth?**

The area between the equator and <<BF10_fireballs_anywhere.band_edge>> degrees north covers
<<BF10_fireballs_anywhere.band_0_30_share>> of Earth's surface. There were <<BF10_fireballs_anywhere.located>>
fireballs with known locations. If fireballs landed randomly, we would expect about
<<BF10_fireballs_anywhere.band_0_30_exp>> to land in that area.

What actually happened? <<BF10_fireballs_anywhere.band_0_30_obs>> fireballs were found there. That is very close to
the prediction.

**What about the Moon?**

We used the same idea to study craters on the Moon. We found:

* The area between the equator and <<BF32_polar_craters.band_w>> degrees north is <<BF32_polar_craters.area_ratio>>
  times larger than the small area around the north pole (<<BF32_polar_craters.lat_80>> to
  <<BF32_polar_craters.lat_90>> degrees north).
* But the north polar area has <<BF32_polar_craters.ratio_north>> times as many craters per square kilometre.

This means the north polar area has more craters compared with its size.

**The main idea:** When comparing two areas, we must consider how big each area is. More objects do not always mean
a place is more crowded.

### 3.6 Calculating the local time of a fireball (finding 11)

**What is this about?**

Imagine a fireball falling in another country. The time in that country might be different from the time recorded
by a computer in the UK or Canada. Scientists often record events using UTC, a worldwide standard time. But they may
want to know the local time where the fireball happened.

Earth turns around once every <<RD_readme.hours_per_day>> hours. It turns <<BF00_shared_facts.full_circle>> degrees
during that time. So:

$$<<BF00_shared_facts.full_circle>> \div <<RD_readme.hours_per_day>> = <<BF11_fewer_at_dawn.deg_per_hour>>$$

Earth turns <<BF11_fewer_at_dawn.deg_per_hour>> degrees every hour. That means every
<<BF11_fewer_at_dawn.deg_per_hour>> degrees of longitude changes the local time by about one hour. The formula is:

$$t_{\text{local}} = t_{\text{UTC}} + \frac{\lambda}{15}$$

Here:

* $t_{\text{local}}$ = local time.
* $t_{\text{UTC}}$ = worldwide standard time.
* $\lambda$ = longitude, which tells us the east-west position (east counts as plus, west as minus).

This local time goes by the Sun: noon is when the Sun is highest in the sky. The clocks in that country can be set
differently.

**Example from the data**

The Chelyabinsk fireball, the biggest in the file, happened on <<BF10_fireballs_anywhere.big1_date>> at:

* UTC time: <<RD_readme.ex_utc_clock>>.
* Longitude: <<BF11_fewer_at_dawn.ex_lon>> degrees east.

<<BF11_fewer_at_dawn.ex_lon>> divided by <<BF11_fewer_at_dawn.deg_per_hour>> is about <<RD_readme.ex_off_h>> hours
and <<RD_readme.ex_off_min>> minutes. So:

<<RD_readme.ex_utc_clock>> + <<RD_readme.ex_off_clock>> = <<BF11_fewer_at_dawn.ex_local_clock>>

The local time was <<BF11_fewer_at_dawn.ex_local_clock>> <<RD_readme.ex_local_ampm>>.

**The main idea:** Scientists can calculate the local time of an event using its longitude.

### 3.7 Solar storms and the <<BF14_repeats_27_days.sun_turn>>-day repeating pattern (findings 12 to 17)

**What is this about?**

The Sun constantly sends out energy and tiny particles into space. This moving material is called the solar wind.
Sometimes the solar wind disturbs Earth's magnetic field. This can cause a solar or geomagnetic storm.

Scientists use something called SYM-H to measure how much Earth's magnetic field is disturbed. Think of it as a
storm meter. It is measured in nanotesla (nT), and we use these lines (Gonzalez et al. 1994):

* <<BF12_storm_cycle.storm_cut>> nT or lower = storm.
* <<BF12_storm_cycle.strong_cut>> nT or lower = strong storm.

The more negative the number becomes, the stronger the disturbance.

**What is the <<BF14_repeats_27_days.sun_turn>>-day pattern?**

The Sun rotates. From Earth's point of view, the Sun takes about <<BF14_repeats_27_days.sun_turn>> days to complete
one rotation. Because of this, some areas of the Sun can send fast solar wind toward Earth again after about
<<BF14_repeats_27_days.sun_turn>> days.

We wanted to see whether the solar wind speed repeats after <<BF14_repeats_27_days.sun_turn>> days. We used a math
method called correlation. Correlation simply checks whether two things move in a similar pattern. Imagine
listening to a song and hearing the same part again later. That is similar to what we are checking here.

The correlation result is:

* 1 = perfect match.
* 0 = no clear match.
* -1 = opposite pattern.

**What did we find?**

| Time difference | Correlation |
|---|---|
| <<BF14_repeats_27_days.best_lag>> days | <<BF14_repeats_27_days.all_27>> |
| <<BF14_repeats_27_days.lag13>> days | <<BF14_repeats_27_days.all_13>> |

The <<BF14_repeats_27_days.best_lag>>-day result is much stronger. This means solar wind speed shows a repeating
pattern after about <<BF14_repeats_27_days.best_lag>> days (Figure 2). The <<BF14_repeats_27_days.lag13>>-day
result is very weak.

**What about March and September?**

We also found more storms around March and September. This is called the Russell-McPherron effect (Russell and
McPherron 1973). During these times, Earth's magnetic field and the Sun's magnetic field can line up in a way that
allows more solar energy to enter Earth's magnetic space. This can make storms more likely.

**The main idea:** The Sun rotates about every <<BF14_repeats_27_days.sun_turn>> days, and this can create
repeating patterns in solar wind and Earth's magnetic storms.

### 3.8 Understanding stars: brightness, speed and groups (findings 18 to 22)

**What is this about?**

Scientists use a space telescope called Gaia to study stars. Gaia collects information about:

* How bright a star looks.
* How far away it is.
* What colour it is.
* How it moves.

Let's understand these one by one.

**1. How bright is a star?**

A star can look bright because it is close to Earth. But that does not always mean it is naturally bright. Imagine
two light bulbs: one is close to you, and one is far away. The closer bulb might look brighter, even if both bulbs
produce the same amount of light.

Scientists calculate how bright a star would look if all stars were placed at the same standard distance. This is
called absolute magnitude. The formula is:

$$M_G = G + 5\log_{10}\varpi - 10$$

You don't need to understand every part. It uses the star's observed brightness ($G$) and its distance (through the
parallax $\varpi$, in milliarcseconds) to calculate its true brightness. Remember: a bigger magnitude number means a
fainter star.

**2. What is a white dwarf?**

A white dwarf is the small, extremely dense leftover core of a star that has reached the end of its normal life.
Scientists use the star's brightness and colour to identify possible white dwarfs. The rule we used is:

$$M_G \gt <<BF18_star_families.wd_a>> + <<BF18_star_families.wd_b>>\,(BP-RP)$$

and the star's colour ($BP-RP$) must be below <<BF18_star_families.wd_colour>>. The colour measurement helps
scientists separate white dwarfs from other types of stars.

**3. How fast is a star moving?**

Stars move through space. From Earth, we can see some stars slowly changing their positions in the sky. This
movement is called proper motion. Scientists combine how quickly the star appears to move across the sky with how
far away it is. They can then estimate its sideways speed. The formula is:

$$v_t = <<BF21_star_clusters.km_s_factor>> \times \mu \times d$$

Where:

* $v_t$ = sideways speed, in km/s.
* $\mu$ = how quickly the star appears to move, in arcseconds per year.
* $d$ = distance from Earth, in parsecs.

**4. Finding groups of stars**

Imagine 100 people standing in a large park. Some people are standing close together. Others are standing far
away. A computer method called DBSCAN (Ester et al. 1996) finds groups of stars in a similar way. The computer looks
at where stars are and how fast they move. In our search, a group needs at least
<<BF21_star_clusters.min_samples>> stars close to each other according to the chosen measurements.

**What did we find?**

We found <<BF21_star_clusters.groups>> star groups. The biggest group had:

* <<BF21_star_clusters.top_stars>> stars.
* A distance of <<BF21_star_clusters.top_dist>> parsecs from Earth.
* The name Pleiades.

A parsec is a unit used to measure very large distances in space. One parsec is about
<<BF00_shared_facts.pc_ly>> light-years.

**The main idea:** Scientists can use brightness, colour, distance and movement to understand stars and discover
groups of stars.

### 3.9 Finding planets around other stars (findings 23 to 28)

**What is this about?**

Scientists want to find planets outside our solar system. These are called exoplanets. One way to find them is to
watch a star carefully.

Imagine a light bulb shining in a dark room. Now imagine a small ball passing in front of it. The light becomes
slightly weaker. The same thing happens when a planet passes in front of its star. Scientists call this a transit.

They measure how much the star's light becomes weaker. The formula is:

$$\frac{\Delta F}{F} = \left(\frac{R_p}{R_\star}\right)^2$$

In simple words: the bigger the planet is compared with its star ($R_p$ is the planet's radius and $R_\star$ the
star's), the more light it blocks.

For Earth passing in front of the Sun, the Sun's light would become weaker by only about
<<RD_readme.earth_transit_pct>>%. That is a very tiny change! This is why bigger planets are usually easier to find
using this method.

**What is the habitable zone?**

Scientists also want to find planets that receive a suitable amount of heat and light from their stars. Imagine
standing outside:

* Too little sunlight might make a place extremely cold.
* Too much sunlight might make it extremely hot.
* A suitable amount could allow liquid water to exist.

The amount of light a planet receives depends on how bright its star is and how far away the planet is. The formula
is:

$$S = \frac{L}{a^2}$$

Here:

* $S$ = amount of light the planet receives compared with Earth.
* $L$ = brightness of the star compared with the Sun.
* $a$ = distance between the planet and its star, in AU.

For this work, a planet was called suitable when:

1. It received between <<BF28_just_right_zone.insol_lo>> and <<BF28_just_right_zone.insol_hi>> times Earth's
   sunlight.
2. Its size was less than <<BF28_just_right_zone.size_cut>> times Earth's size.

This is our definition of a potentially suitable planet. It does not mean life has been found there.

**What did we find?**

We found <<BF28_just_right_zone.n>> planets that passed these rules. The closest was
<<BF28_just_right_zone.top_name>>, about <<BF28_just_right_zone.top_pc>> parsecs away.

**The main idea:** Scientists can find planets by watching stars become slightly darker. They can also estimate
whether a planet receives a suitable amount of sunlight.

### 3.10 Understanding the sizes of craters (finding 30)

**What is this about?**

The Moon has many craters. Some are small. Some are medium-sized. Some are extremely large. We wanted to understand
how often different crater sizes appear. The basic question was: are large craters as common as small craters?

The answer is no. Small craters are much more common.

We used this formula:

$$N(\geq D) \propto D^{-b}$$

Don't worry about the formula. It simply describes how the number of craters changes as crater size increases
($N(\geq D)$ is the number of craters at least $D$ wide). We calculated a number called $b$. The value of $b$ helps
describe how quickly large craters become less common.

**What did we find?**

| Crater size comparison | Result ($b$) |
|---|---|
| <<BF30_size_rule.d1>> km to <<BF30_size_rule.d10>> km | <<RD_readme.b_1_10>> |
| <<BF30_size_rule.d10>> km to <<BF30_size_rule.d100>> km | <<RD_readme.b_10_100>> |
| <<BF30_size_rule.d100>> km to <<BF30_size_rule.d1000>> km | <<RD_readme.b_100_1000>> |

All three numbers are close to 2.

What does that mean? Imagine we increase crater size by 10 times. The number of craters becomes
<<RD_readme.fold_min>> to <<RD_readme.fold_max>> times smaller (Figure 3). For example, in our file:

* <<BF30_size_rule.n_ge_1>> craters are at least <<BF30_size_rule.d1>> km wide.
* <<BF30_size_rule.n_ge_10>> are at least <<BF30_size_rule.d10>> km wide.
* <<BF30_size_rule.n_ge_100>> are at least <<BF30_size_rule.d100>> km wide.
* Only <<BF30_size_rule.n_ge_1000>> are at least <<BF30_size_rule.d1000>> km wide.

**The main idea:** Small craters are very common. Craters that are 10 times bigger are roughly
<<RD_readme.fold_min_round>> to <<RD_readme.fold_max_round>> times less common.

### Summary: what does all this math actually tell us?

Here is the whole thing in simple language:

| Section | What we learned |
|---|---|
| 3.1 Jupiter and Neptune | Gravity creates empty spaces and special safe areas for asteroids. |
| 3.2 Asteroid brightness | We can estimate an asteroid's size using its brightness. |
| 3.3 Asteroid spinning | Loose asteroids can break apart if they spin too fast. |
| 3.4 Jupiter's two groups | Jupiter has two large groups of Trojan asteroids. |
| 3.5 Earth's and Moon's surface | We must compare object counts fairly by considering area size. |
| 3.6 Local time | We can calculate when a fireball happened using its longitude. |
| 3.7 Solar storms | Solar wind can show a repeating <<BF14_repeats_27_days.sun_turn>>-day pattern. |
| 3.8 Stars | We can calculate star brightness, speed and groups. |
| 3.9 Other planets | We can find planets by watching stars become slightly darker. |
| 3.10 Moon craters | Bigger craters are much less common than smaller ones. |

### One important thing to understand

You do not need to memorize all these formulas. The important thing is to understand why each formula is being
used. For example:

* Want to know where asteroids should be? Use orbital math.
* Want to estimate an asteroid's size? Use brightness.
* Want to know how fast an asteroid can spin? Use gravity and rotation.
* Want to find groups of stars? Use a computer clustering method.
* Want to find planets? Look for tiny changes in starlight.
* Want to compare craters? Compare their sizes and how often they appear.

The math is basically helping scientists turn space observations into numbers they can test and understand.

## 4. Results

One line each. The full text, with a chart and an animation for every result, is in `FINDINGS.md` and in the app.

<<RESULTS>>

## 5. Forecasts

The fourth page of the app, Predictions, asks for one thing: a day. It answers with the chance of a geomagnetic
storm on that day (SYM-H at or below -50 nT at some time in the day), using only data from before the day.

* Next day, and any past day (to check it against what happened): the 5-minute storm model below, run at the
  last reading before midnight.
* 2 to 90 days ahead: one small XGBoost model per lead time $L$, fed daily summaries up to day $D-L$: recent
  storm counts, the share of storm days in the last year, the time of year, and the days one solar turn (27 days)
  before $D$, which is the echo of section 3.7.
* Further ahead: only the share of storm days in that calendar month over the last solar cycle. It is not a
  forecast of the day, and the page says so.

The test days are <<RD_readme.day_test>> (SYM-H stops there); <<RD_readme.day_storm_pct>>% of them had a storm.

<<FC_DAY_TABLE>>

The next-day forecast is useful. Beyond that the chances are only a little better than the usual rate (the
Brier skill compares the squared error of the chances with always giving the training years' storm rate), so the
page only says "higher" or "lower than usual" there. Storms that come from clouds thrown out by the Sun cannot be
seen in the solar wind days ahead; only the 27-day echo of fast wind gives some warning.

The engine underneath also forecasts six measurements of the solar wind and of Earth's magnetic field, 5 minutes
to 24 hours ahead. The code is in `forecast/`. The models are trained once (`python -m forecast.train`,
<<RD_readme.fc_minutes>> minutes here, then `python -m forecast.daily`) and the page and a small HTTP API
(`uvicorn forecast.api:app`) only read them.

The baseline is persistence, $\hat y_{t+h} = y_t$: tomorrow looks like today. The model learns the change instead
of the value,

$$\hat y_{t+h} = y_t + f_h(\mathbf{x}_t),$$

where $f_h$ is a gradient-boosted tree ensemble (XGBoost) and $\mathbf{x}_t$ holds <<RD_readme.fc_inputs>> numbers
built only from readings at $t$ or before: recent values, means and spreads of speed, field, density, pressure,
SYM-H and AE, and the driving term $v B_s$ with $B_s = \max(0, -B_z)$. The years are split in time: train
<<RD_readme.fc_train>>, validation <<RD_readme.fc_val>>, test <<RD_readme.fc_test>>, with one day left out at each
edge so that no answer leaks across. Every score below is from the test years. Skill is
$1 - \text{RMSE}_\text{model}/\text{RMSE}_\text{persistence}$.

<<FC_REG_TABLE>>

A storm start time is labelled 1 when $\min_{t \lt s \le t+H} \mathrm{SYMH}(s) \le \theta$, with $\theta$ = -50 nT
(storm) or -100 nT (strong storm). The classifier flags a storm when its chance passes the line with the best
$F_1$ on the validation year. Persistence here means "a storm now means a storm soon".

<<FC_EVENT_TABLE>>

Three things the scores say plainly. First, <<FC_WORSE>> Second, the field direction $B_z$ is close to unpredictable beyond a few hours
($R^2$ = <<RD_readme.fc_bz_r2_6h>> at 6 hours); the model beats persistence there mainly by predicting the
average. Third, the 80% intervals were set on 2022, a quiet year, and in the stormier test years they held
between <<RD_readme.fc_cov_min>>% and <<RD_readme.fc_cov_max>>% of the time. Not tried yet: LightGBM and recurrent
networks.

## 6. Galaxy pictures

The fifth page of the app, Galaxies, reads pictures. You upload a picture of a galaxy and an AI model says which kind
of galaxy it looks like, as a ranked list with a score for each kind. The same works from the terminal:

```
.venv/bin/python -m galaxy.classify picture.jpg
```

**What is this about?**

Galaxies come in a few main shapes: round and smooth, spiral, spiral with a bar across the middle, seen edge-on like
a plate from the side, or messy because two of them are crashing into each other. Galaxy Zoo asked volunteers to sort
pictures like these by eye. Here a computer model does it.

The model is Galaxy-CLIP (`juppy44/galaxy-clip-finetuned` on Hugging Face). Michael Jupp made it from OpenAI's CLIP
(Radford et al. 2021) by training it further on galaxy pictures paired with descriptions. We do not train it at all;
we only use it. It is "zero-shot": nobody gave it our list of kinds as fixed boxes. It compares the picture with each
description and ranks them.

**How does it work?**

The model has two halves. One turns a picture into a list of <<GC_model.embed_dim>> numbers. The other turns a short
sentence, like "barred spiral galaxy", into <<GC_model.embed_dim>> numbers too. They were trained together, so that a
picture and a sentence about the same thing get lists that point the same way.

First the picture is cut to a square around its middle, shrunk to <<GC_model.image_px>> by <<GC_model.image_px>>
pixels and split into <<GC_model.patches_side>> by <<GC_model.patches_side>> = <<GC_model.patches>> tiles of
<<GC_model.patch_px>> by <<GC_model.patch_px>> pixels, which the model reads a bit like the words of a sentence.

To compare the picture's list $\mathbf{a}$ with a label's list $\mathbf{b}$ we use the cosine similarity:

$$s = \frac{\mathbf{a}\cdot\mathbf{b}}{\lVert\mathbf{a}\rVert\,\lVert\mathbf{b}\rVert}$$

You don't need to memorize it. It is 1 when the two lists point the same way and 0 when they have nothing to do with
each other. For this model the values are small, between about <<GC_model.sim_lo>> and <<GC_model.sim_hi>>, so only
the order matters.

The match score turns the similarities into shares that add up to 100%:

$$p_i = \frac{e^{k s_i}}{\sum_j e^{k s_j}}$$

where $k$ = <<GC_model.scale>> is a number the model learned. The shares depend on the list: change the labels and
the percentages change.

The labels to start with are the <<GC_model.n_labels>> classes of Galaxy10 DECaLS (Leung and Bovy 2019), galaxy
pictures sorted by Galaxy Zoo volunteers (Walmsley et al. 2022): <<GC_LABELS>>. On the page you can type your own.

**What did we find?**

The model's own page says no formal test has been done, and our data files have no galaxy pictures with known
answers, so we cannot give an accuracy. To check that it works we tried <<GC_model.check_n>> well-known galaxies,
with pictures from the DESI Legacy Imaging Surveys sky viewer (Dey et al. 2019), using `python -m galaxy.check`:

<<GC_TABLE>>

Its first choice fitted <<GC_model.check_right>> of the <<GC_model.check_n>>. For <<GC_model.check_two_fit>> of them
two classes fit, and the table lists both. <<GC_MISSES>> We picked the Galaxy10 wording after trying it, and a longer
wording, on these same pictures, so this shows that the model runs and makes sense, not how good it is.

Note: the model's page says about <<GC_model.card_params_m>> million parameters; the file has <<GC_model.params>>,
the size of CLIP ViT-B/32.

**The main idea:** The model does not know galaxy kinds as fixed boxes. It compares the picture with each sentence
you give it and ranks the sentences by how well they match.

## 7. Figures

![Figure 1](charts/A05_a_histogram_1.7-5.5AU.png)

**Figure 1.** Asteroids per 0.01 AU slice of average distance from the Sun (log scale). The narrow dips are the empty
lanes of section 3.1.

![Figure 2](charts/BF14_27_day_repeat.png)

**Figure 2.** Correlation of the daily solar-wind speed with itself $N$ days earlier. The peak at 27 days is the Sun's
turn (section 3.7).

![Figure 3](charts/BF30_size_rule.png)

**Figure 3.** Moon craters at least $D$ wide, both axes on a log scale. A straight line is a power law (section 3.10).

## 8. Running it

```
python3 -m venv .venv
.venv/bin/pip install torch --index-url https://download.pytorch.org/whl/cpu   # the small CPU build
.venv/bin/pip install -r requirements.txt
.venv/bin/streamlit run app.py            # then open http://localhost:8501
```

The app has five pages: Home, Findings (the 32 results with a chart and an animation each), Charts, Predictions
(pick a day, get the storm chance) and Galaxies (upload a galaxy picture). For the forecasts, train the models once
with `.venv/bin/python -m forecast.train` and then `.venv/bin/python -m forecast.daily` (they are not in git). For the
galaxy pictures, download the model once (about <<GC_model.weights_mb>> MB, not in git):

```
.venv/bin/hf download juppy44/galaxy-clip-finetuned --local-dir models/galaxy-clip-finetuned
.venv/bin/python -m galaxy.classify picture.jpg     # the same as the page, in the terminal
.venv/bin/python -m galaxy.check                    # the ten-galaxy check of section 6
```

The model is read from that folder only; nothing is downloaded while the app runs. It
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

## 9. Caveats

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
* The galaxy model always picks one of the labels it is given, even for a picture that is not a galaxy. It learned
  from descriptions written by another AI model, not by astronomers, and its own page says it has not been tested.

## 10. Files

```
app.py                     the Streamlit app (Home, Findings, Charts, Predictions, Galaxies)
app_pages/                 the five pages
forecast/                  the forecasts: features, training, the service the page uses, the HTTP API
galaxy/                    the galaxy pictures: the model (clip.py), the terminal command, the ten-galaxy check
models/                    the Galaxy-CLIP model, downloaded once (not in git)
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

* Dey, A. et al. (2019). Overview of the DESI Legacy Imaging Surveys. The Astronomical Journal 157, 168.
* Ester, M., Kriegel, H.-P., Sander, J. and Xu, X. (1996). A density-based algorithm for discovering clusters in
  large spatial databases with noise. Proceedings of KDD-96, 226-231.
* Fischer, D. A. and Valenti, J. (2005). The planet-metallicity correlation. The Astrophysical Journal 622, 1102-1117.
* Fulton, B. J. et al. (2017). The California-Kepler Survey. III. A gap in the radius distribution of small planets.
  The Astronomical Journal 154, 109.
* Gaia Collaboration, Vallenari, A. et al. (2023). Gaia Data Release 3: Summary of the content and survey
  properties. Astronomy and Astrophysics 674, A1.
* Gonzalez, W. D. et al. (1994). What is a geomagnetic storm? Journal of Geophysical Research 99, 5771-5792.
* Jupp, M. (2026). Galaxy-CLIP: domain-adapted vision-language model for galaxy morphology. Hugging Face,
  juppy44/galaxy-clip-finetuned.
* King, J. H. and Papitashvili, N. E. (2005). Solar wind spatial scales in and comparisons of hourly Wind and ACE
  plasma and magnetic field data. Journal of Geophysical Research 110, A02104.
* Kirkwood, D. (1867). Meteoric Astronomy. J. B. Lippincott, Philadelphia.
* Leung, H. W. and Bovy, J. (2019). Deep learning of multi-element abundances from high-resolution spectroscopic
  data. Monthly Notices of the Royal Astronomical Society 483, 3255-3277 (astroNN, home of the Galaxy10 data sets).
* Mazeh, T., Holczer, T. and Faigler, S. (2016). Dearth of short-period Neptunian exoplanets: a desert in period-mass
  and period-radius planes. Astronomy and Astrophysics 589, A75.
* Pravec, P. and Harris, A. W. (2000). Fast and slow rotation of asteroids. Icarus 148, 12-20.
* Radford, A. et al. (2021). Learning transferable visual models from natural language supervision. Proceedings of
  the 38th International Conference on Machine Learning, PMLR 139, 8748-8763.
* Robbins, S. J. (2019). A new global database of lunar impact craters >1-2 km: 1. Crater locations and sizes,
  comparisons with published databases, and global analysis. Journal of Geophysical Research: Planets 124, 871-892.
* Russell, C. T. and McPherron, R. L. (1973). Semiannual variation of geomagnetic activity. Journal of Geophysical
  Research 78, 92-108.
* Walmsley, M. et al. (2022). Galaxy Zoo DECaLS: detailed visual morphology measurements from volunteers and deep
  learning for 314,000 galaxies. Monthly Notices of the Royal Astronomical Society 509, 3966-3988.

Data: JPL Small-Body Database and CNEOS (asteroids, close approaches, fireballs), NASA OMNIWeb (solar wind), ESA Gaia
DR3 (stars), NASA Exoplanet Archive (planets), Robbins (2019) via the LRO mission (Moon craters). The pictures for
the galaxy check are DESI Legacy Imaging Surveys and SDSS images from the Legacy Surveys sky viewer.

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


def day_table() -> str:
    d = pd.read_csv(NUM / "FC_daily_scores.csv")
    lines = ["| days ahead | model | right when it says storm | storm days caught | PR-AUC | Brier skill |",
             "|---|---|---|---|---|---|"]
    for _, r in d.iterrows():
        lines.append(f"| {int(r['lead_days'])} | {r['model']} | {100 * r['precision']:.0f}% | {100 * r['recall']:.0f}% | "
                     f"{r['pr_auc']:.2f} | {r['brier_skill_pct']:.0f}% |")
    p = d[d["lead_days"] == 1].iloc[0]
    lines.append("")
    lines.append(f"For the next day, \"a storm today if there was one yesterday\" is right {100 * p['precision_persistence']:.0f}% "
                 f"of the time and catches {100 * p['recall_persistence']:.0f}% of storm days.")
    return "\n".join(lines)


def galaxy_table() -> str:
    """The ten-galaxy check (numbers/GC_check.csv, written by python -m galaxy.check)."""
    d = pd.read_csv(NUM / "GC_check.csv")
    lines = ["| galaxy | what it is | class that fits | the model's first choice | match | fits |",
             "|---|---|---|---|---|---|"]
    for _, r in d.iterrows():
        lines.append(f"| {r['galaxy']} | {r['what_it_is']} | {r['expected']} | {r['first_choice']} | "
                     f"{r['first_match_pct']:.0f}% | {'yes' if r['right'] else 'no'} |")
    return "\n".join(lines)


def galaxy_misses() -> str:
    """One sentence on each first choice that did not fit, from numbers/GC_check.csv."""
    d = pd.read_csv(NUM / "GC_check.csv")
    miss = d[~d["right"]]
    if miss.empty:
        return ""
    parts = [f"{r['galaxy']} ({r['what_it_is']}) came out as \"{r['first_choice']}\" ({r['first_match_pct']:.0f}%), "
             f"with \"{r['second_choice']}\" next ({r['second_match_pct']:.0f}%)" for _, r in miss.iterrows()]
    return "The misses: " + "; ".join(parts) + "."


def galaxy_labels() -> str:
    sys.path.insert(0, str(ROOT))
    from galaxy.clip import DEFAULT_LABELS
    return ", ".join(f'"{lab}"' for lab in DEFAULT_LABELS)


def fc_tables() -> tuple[str, str]:
    reg = pd.read_csv(NUM / "FC_regression_scores.csv")
    names = {"speed_km_s": "wind speed", "bt_nT": "field strength", "bz_gsm_nT": "Bz", "density_cm3": "density",
             "pressure_nPa": "pressure", "sym_h_nT": "SYM-H"}
    lines = ["| measurement (unit) | RMSE 1 h (persistence) | skill 1 h | RMSE 24 h (persistence) | skill 24 h |",
             "|---|---|---|---|---|"]
    for t in reg["target"].unique():
        r1 = reg[(reg["target"] == t) & (reg["horizon"] == "1 h")].iloc[0]
        r24 = reg[(reg["target"] == t) & (reg["horizon"] == "24 h")].iloc[0]
        g = lambda v: f"{v:.3g}"  # noqa: E731
        lines.append(f"| {names.get(t, t)} ({r1['unit']}) | {g(r1['rmse'])} ({g(r1['rmse_persistence'])}) | "
                     f"{r1['skill_rmse_pct']:.0f}% | {g(r24['rmse'])} ({g(r24['rmse_persistence'])}) | "
                     f"{r24['skill_rmse_pct']:.0f}% |")
    ev = pd.read_csv(NUM / "FC_event_scores.csv")
    el = ["| event | storms in test (%) | precision | recall | F1 (persistence) | PR-AUC |", "|---|---|---|---|---|---|"]
    for _, r in ev.iterrows():
        el.append(f"| {r['name']} | {r['base_rate_pct']:.1f} | {r['precision']:.2f} | {r['recall']:.2f} | "
                  f"{r['f1']:.2f} ({r['f1_persistence']:.2f}) | {r['pr_auc']:.2f} |")
    return "\n".join(lines), "\n".join(el)


def fc_worse() -> str:
    """Where the model does not beat persistence on the test years, in words."""
    reg = pd.read_csv(NUM / "FC_regression_scores.csv")
    names = {"speed_km_s": "wind speed", "bt_nT": "field strength", "bz_gsm_nT": "Bz", "density_cm3": "density",
             "pressure_nPa": "pressure", "sym_h_nT": "SYM-H"}
    bad = reg[reg["skill_rmse_pct"] <= 0]
    if bad.empty:
        return "the model beats persistence at every horizon."
    parts = []
    for t, g in bad.groupby("target", sort=False):
        hs = " and ".join([", ".join(g["horizon"].iloc[:-1])] + [g["horizon"].iloc[-1]]) if len(g) > 1 else \
            g["horizon"].iloc[0]
        mn, mx = g["skill_rmse_pct"].min(), g["skill_rmse_pct"].max()
        rng = f"skill {mn:.1f}%" if len(g) == 1 else f"skill {mn:.1f}% to {mx:.1f}%"
        parts.append(f"{names.get(t, t)} at {hs} ({rng})")
    return ("at the shortest horizons the model is worse than persistence for " + "; ".join(parts)
            + ". Over a few minutes the value now is very hard to beat, so use persistence there.")


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
    body = re.sub(r"(?m)^\|\s*\d+\.\d+\s", "| ", body)            # section numbers in a table ("| 3.1 Jupiter")
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
    reg_t, ev_t = fc_tables()
    md = md.replace("<<FC_REG_TABLE>>", reg_t).replace("<<FC_EVENT_TABLE>>", ev_t).replace("<<FC_WORSE>>", fc_worse())
    md = md.replace("<<FC_DAY_TABLE>>", day_table())
    md = (md.replace("<<GC_TABLE>>", galaxy_table()).replace("<<GC_MISSES>>", galaxy_misses())
          .replace("<<GC_LABELS>>", galaxy_labels()))
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
