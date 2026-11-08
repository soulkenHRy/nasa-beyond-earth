# NASA Beyond Earth

**Thirty-two small results from seven public NASA data sets**

Sheridan Datathon 2026, NASA track. Last revised November 2026.

```
Contents
   0  Abstract
   1  The data
   2  How a number gets from a CSV file to the screen
   3  The math
   4  Results
   5  Forecasts
   6  Figures
   7  Running it
   8  Caveats
   9  Files
      References
```

## 0. Abstract

We looked at seven public data files from NASA and JPL: 1,582,869 asteroids and comets,
120,071 close passes by Earth, 1,074 fireballs,
1,766,880 five-minute readings of the solar wind and Earth's magnetic field
(2010-01-01 to 2026-10-18), 1,165,165 nearby stars from Gaia,
6,451 confirmed planets around other stars, and 1,296,796 craters on the Moon.
From these we pulled out 32 results. Most of them are old physics showing up in new numbers: Kepler's third law,
Jupiter's resonances, the 27-day turn of the Sun. Some are about the data itself: where it has holes, and why a count
can say more about who was looking, and when, than about what is out there.

Every number that comes from the data, in this note, in `FINDINGS.md` and in the app, is computed by a script and
stored in `numbers/`. None of them is typed by hand.

## 1. The data

| part | file | from | rows | columns | MB |
|---|---|---|---|---|---|
| A | `jpl_small_bodies_asteroids_comets.csv` | JPL Small-Body Database | 1,582,869 | 29 | 256.8 |
| B | `extras_close_approaches_1900-2200.csv` | JPL CNEOS close approaches | 120,071 | 14 | 19.8 |
| C | `extras_fireballs.csv` | JPL CNEOS fireballs | 1,074 | 9 | 0.1 |
| D | `nasa_omni_solar_wind_storms_5min_2010-2026.csv` | NASA OMNIWeb, 5-minute values | 1,766,880 | 14 | 138.7 |
| E | `gaia_dr3_stars_within_500_light_years.csv` | ESA Gaia DR3 | 1,165,165 | 21 | 314.4 |
| F | `nasa_exoplanet_archive_confirmed_planets.csv` | NASA Exoplanet Archive | 6,451 | 25 | 1.4 |
| G | `moon_craters_robbins_lro_1.3M.csv` | Robbins lunar crater database | 1,296,796 | 10 | 102.0 |

The CSV files add up to about 833 MB, so they are not in this repository (see section 6).

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
gap_count,8659.0,"8,659",,our data
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

With $a_J$ = 5.20 AU (the middle distance of Jupiter's Trojans in our file):

| ratio $n:m$ | predicted $a$ (AU) | dip in the data (AU) |
|---|---|---|
| 3:1 | 2.50 | 2.50 |
| 5:2 | 2.83 | 2.82 |
| 7:3 | 2.96 | 2.95 |
| 2:1 | 3.28 | 3.29 |

The same rule works the other way past Neptune. Objects that go around twice while Neptune goes around three times
are never near Neptune when they cross its path, so they are safe there:

$$a = a_N \left(\tfrac{3}{2}\right)^{2/3} = 39.4\ \text{AU},$$

with $a_N$ = 30.07 AU. The crowd in the data sits at 39.2 to
39.7 AU (586 objects, about
3.6 times the slices beside it).

### 3.2 Size from brightness (findings 2, 3 and 7)

Most asteroids have no measured size, only an absolute magnitude $H$ (how bright the rock would look from a fixed
standard distance; bigger $H$ means fainter). With a guess for the albedo $p_V$, the share of sunlight the surface
reflects:

$$D = \frac{1329\ \text{km}}{\sqrt{p_V}}\; 10^{-H/5} .$$

With $p_V$ = 0.14 and $H$ = 22 this gives
141 m. That is the size line in the "potentially hazardous" rule: $H \le$
22 and a closest orbit distance (MOID) of at most 0.05 AU.
Of the 2,550 rocks flagged hazardous, 2,517
(98.7%) pass both lines exactly as written.

### 3.3 The spin barrier (finding 3)

A pile of loose rubble held together only by its own gravity comes apart when the outward pull of the spin at its
equator beats gravity, $\omega^2 R > GM/R^2$. With $M = \tfrac{4}{3}\pi R^3\rho$ and $P = 2\pi/\omega$ the size
cancels out:

$$P_{\min} = \sqrt{\frac{3\pi}{G\rho}} .$$

For rock with a density of about $2\ \text{g/cm}^3$ this is between two and three hours. We use the usual line of
2.2 hours (Pravec and Harris 2000). Only 1,236 of
33,616 asteroids wider than 300 m spin faster
(3.7%). Small asteroids are often solid, and 80% of them do.

### 3.4 Jupiter's two swarms (finding 6)

The Trojans sit near the two points that make an equilateral triangle with the Sun and Jupiter, one ahead of Jupiter
and one behind it. The place of an asteroid along its path is its mean longitude

$$L = \Omega + \omega + M \pmod{360^\circ},$$

the sum of three angles in the file (`om`, `w`, `ma`). The two peaks in our file are
120 degrees apart: 10,494 asteroids ahead of Jupiter and
5,951 behind.

### 3.5 Fair share on a sphere (findings 10 and 32)

The part of a sphere's surface between latitudes $\varphi_1$ and $\varphi_2$ is

$$f = \frac{\sin\varphi_2 - \sin\varphi_1}{2} .$$

So the band from the equator to 30 degrees north is a quarter of Earth's surface, and if fireballs fell anywhere at
random it would get 222 of the 888 with a known
place. It got 227. On the Moon the same formula turns crater counts into counts
per area: the band from the equator to 10 degrees north has 11.4 times the area of the
band around the north pole, and the polar band has 3.0 times as many craters per
square kilometre.

### 3.6 Local solar time (finding 11)

The Sun crosses 15 degrees of longitude every hour, so for a fireball at longitude $\lambda$ (east positive)

$$t_\text{local} = t_\text{UTC} + \frac{\lambda}{15^\circ}\ \text{hours}.$$

An example from the file: 3:20 UTC at
61.1 degrees east is 07:24 local time.

### 3.7 Storms and the 27-day echo (findings 12 to 17)

The storm meter is SYM-H, in nanotesla: how far Earth's magnetic field near the equator is pushed down. Following
Gonzalez et al. (1994), a storm is SYM-H at or below -50 nT and a strong storm at or
below -100 nT. To see whether the Sun repeats itself, we compare the daily mean wind speed
$v$ with itself shifted by $\tau$ days:

$$r(\tau) = \frac{\sum_t (v_t - \bar v)(v_{t+\tau} - \bar v)}{\sum_t (v_t - \bar v)^2} .$$

$r$ is 1 for a perfect echo and 0 for none. We get $r$ = 0.46 at
27 days, the time the Sun takes to turn once as seen from Earth, and only
0.08 at 13 days (Figure 2). The extra storms around March and
September (finding 15) are the Russell-McPherron effect (Russell and McPherron 1973).

### 3.8 Stars: true brightness, speed and groups (findings 18 to 22)

Gaia gives the apparent brightness $G$ (in magnitudes, so bigger is fainter) and the parallax $\varpi$ in
milliarcseconds. The true brightness is

$$M_G = G + 5\log_{10}\varpi - 10 .$$

We call a star a white dwarf when $M_G$ > 10 + 2.6 times its colour
(BP-RP) and the colour is below 1.7. The sideways speed, from the proper motion $\mu$
(arcseconds per year) and the distance $d$ (parsecs), is

$$v_t = 4.74\,\mu\,d\ \ \text{km/s}.$$

The star groups of finding 21 come from DBSCAN (Ester et al. 1996) run on place and sideways speed together: a star
is in a group when at least 12 stars are within 3 of it in
that space. It finds 24 groups. The biggest, 768 stars at
136 parsecs, is the Pleiades.

### 3.9 Planets (findings 23 to 28)

A transit dims a star by the share of its disc that the planet covers:

$$\frac{\Delta F}{F} = \left(\frac{R_p}{R_\star}\right)^2 .$$

For Earth in front of the Sun that is about $8 \times 10^{-5}$, which is why the planets found this way are mostly big
or close to their star. The starlight a planet gets, compared with Earth, is $S = L/a^2$ ($L$ in Suns, $a$ in AU). We
call a planet "just right" when 0.25 $\le S \le$ 1.5 and it
is less than 1.8 Earths wide. To draw every such planet around one star, we put it
where it would get the same starlight from the Sun:

$$d = \frac{1}{\sqrt{S}}\ \text{AU}.$$

That gives 43 planets. The closest is Proxima Cen b,
1.30 parsecs away.

### 3.10 Crater sizes (finding 30)

If the number of craters at least $D$ wide follows a power law $N(\ge D) \propto D^{-b}$, then going ten times wider
divides the count by $10^b$, so

$$b = \log_{10} \frac{N(\ge D)}{N(\ge 10D)} .$$

From 1 to 10 km we get $b$ = 1.73, from 10 to 100 km 1.89, and from 100 to 1000 km
2.02 (Figure 3). A steady $b$ near 2 is all that "ten times wider, about 50 to 100 times rarer"
means.

## 4. Results

One line each. The full text, with a chart and an animation for every result, is in `FINDINGS.md` and in the app.

**Part A: Asteroids and comets**

1. The asteroid belt has empty lanes. Empty lane 2.48 to 2.52: only 8,659 asteroids. Just inside it, 2.40 to 2.44: 54,292 (6.3 times as many).
2. Asteroids get darker the farther they are from the Sun. Out of every 100 asteroids in each zone, the shiny ones: 57%, then 37%, then 15%, then only 3%.
3. Big asteroids almost never spin faster than once every 2.2 hours. Big asteroids: only 1,236 of 33,616 spin faster than once every 2.2 hours (3.7%). Small asteroids: 524 of 655 do (80%).
4. In 2025, three times as many objects were seen for the first time as in a normal recent year. 2025: 56,928 objects seen for the first time, 3.0 times the 2018 to 2024 average of 19,089. July 2025 alone: 25,523 (45% of the year).
5. Past Neptune, icy objects crowd into the spot where Neptune's rhythm keeps them safe. Pluto's crowd, 39.2 to 39.7: 586 objects, about 3.6 times the same-size slices beside it.
6. Jupiter has two swarms of asteroids, and the one in front is bigger. Ahead of Jupiter: 10,494. Behind Jupiter: 5,951. 10,494 ÷ 5,951 = 1.76: the front swarm is bigger.
7. "Potentially hazardous" is a rule, not a warning. Flagged Y: 2,550. Inside the box: 2,517 (98.7%). Flagged N but inside the box: only 17.

**Part B: Close approaches**

8. Close passes bunch up around today, because that's when we find the rocks. 1900s to 1990s: about 3,323 passes per decade. 2010s: 12,237. 2020s: 18,757. 2030s: only 3,805.
9. July is quiet, for the telescopes. Small rocks: 691 passes in July, 2,555 in October. 2,555 ÷ 691 = 3.7: October has 3.7 times as many.

**Part C: Fireballs**

10. Fireballs happen everywhere, and one was far bigger than all the others. Over the ocean: 647 (73%); the ocean covers about 71% of Earth. Biggest: 441 kilotons; next biggest: 49 kilotons. 441 ÷ 49 = 9.
11. Fewer fireballs at dawn. Fewest: 4 to 6 am (dawn), 49 fireballs. Most: the two hours before midnight, 111.

**Part D: Space weather**

12. Storms rise and fall with the Sun's 11-year cycle. Storm days: 11 in 2019, 9 in 2020 then 66 in 2024, 97 in 2025. Wind: 378 km every second in 2020, 490 in 2025.
13. What the solar wind does in the hours before a big storm. Crowding: 5.1 two days before, 10.0 at 20 hours before. Push: 1.6, then 5.2 at 8 hours before (3.2 times as hard).
14. The Sun repeats itself every 27 days. Slid by 27 days: match 0.46 (all years), 0.60 in the quiet years 2016 to 2018. Slid by 13 days: 0.08; by 20 days: 0.04.
15. Storms like the months around the equinoxes. Most stormy: March 4.5%, April 4.2%; September 3.7%, October 4.0%. Least: December 1.5%, July 2.0%.
16. The May 2024 superstorm, hour by hour. 17:05 world time (13:05 in Toronto): a giant cloud from the Sun hits. Lowest: -497 at 11 May 02:15 (10 May 22:15 in Toronto).
17. Big storms that happened during an Ontario night. 58 nights with a strong storm (storm meter -100 or lower) between 21:00 and 04:00 Toronto time. 9 each in 2023, 2024 and 2025; 0 in 2019, 2020 and 2022.

**Part E: Stars**

18. A star's colour and true brightness sort it into a family. Main band: 1,024,913. White dwarfs: 84,595 (55,995 well measured). Giants: 5,058.
19. Three out of four nearby stars are red dwarfs. Out of 100 main-band stars near the Sun: about 78 red dwarfs, 14 orange stars, 5 like the Sun and 3 yellow-white stars.
20. Eight times too many "nearby" stars toward the middle of the Milky Way. Circles 5 degrees across, same size: toward the middle 15,901, opposite way 2,041. Badly measured: 66% toward the middle (all stars: 22%); no colour: 33%.
21. Stars that were born together still travel together. 24 groups found by the computer (DBSCAN) using where 700,570 stars are and how they drift. Biggest: 768 stars, about 136 parsecs (442 light-years) away: the Pleiades.
22. Some stars are really fast, and some speeds can't be right. Faster than 300 km every second toward or away: 201 stars. Sideways faster than 200: 2,278 stars.

**Part F: Planets around other stars**

23. Planet discoveries arrive in batches. By transit: 79 in 2013, 810 in 2014, 99 in 2015, 1,432 in 2016. Busiest: 2016, 1,504 planets.
24. Hot Jupiters are common in the list, but hot Neptunes are rare. Neptune-size planets (2.5 to 6 Earths): 449 with a year of 3 to 10 days, only 70 with a year shorter than 3 days. Hot Jupiters: 764.
25. A gap between rocky planets and gassy planets. Smaller hump: 1.47 to 1.59 Earths, 233. The dip: 1.73 to 1.88 Earths, only 199. Bigger hump: 2.22 to 2.41 Earths, 347.
26. Planet hunters mostly look at Sun-like stars. Sun-like (G): 28% of hosts, 6% of stars. Red dwarfs (M): 27% of hosts, 71% of stars.
27. Stars with more metal have more giant planets. Least metal: 196 giants of 689 planets = 28%. Most metal: 510 of 842 = 61%.
28. Earth-size planets in the "just right" zone. 43 planets in the box: 18 found by radial velocity, 24 by transit. Closest: Proxima Cen b, 1.30 parsecs (4.2 light-years); 1.02 Earths wide, starlight 0.64 of Earth's.

**Part G: Moon craters**

29. The craters draw the Moon's dark "seas". Far side 55,586, near side 27,475: 55,586 ÷ 27,475 = 2.0 times as many.
30. Ten times wider, about 50 to 100 times rarer. At least 1 km: 1,296,796; at least 10 km: 24,412. At least 100 km: 314; at least 1,000 km: only 3.
31. Most craters are nearly round, and the stretched ones lean one way. Middle stretch: 1.12, only 12% longer than wide. More than 1.5: 2.1% of craters; more than 2: 0.22%.
32. More craters per square kilometre toward the poles. Per area: the north pole band has 3.0 times as many as the equator; the south pole band 1.8 times.

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

The test days are 2023-01-01 to 2026-09-30 (SYM-H stops there); 20.4% of them had a storm.

| days ahead | model | right when it says storm | storm days caught | PR-AUC | Brier skill |
|---|---|---|---|---|---|
| 1 | 5-minute model | 75% | 63% | 0.79 | 48% |
| 2 | daily model | 30% | 73% | 0.42 | 15% |
| 3 | daily model | 23% | 86% | 0.31 | 9% |
| 7 | daily model | 26% | 58% | 0.29 | 7% |
| 14 | daily model | 22% | 94% | 0.25 | 4% |
| 27 | daily model | 35% | 34% | 0.31 | 8% |
| 60 | daily model | 22% | 66% | 0.24 | 4% |
| 90 | daily model | 22% | 89% | 0.23 | 4% |

For the next day, "a storm today if there was one yesterday" is right 59% of the time and catches 59% of storm days.

The next-day forecast is useful. Beyond that the chances are only a little better than the usual rate (the
Brier skill compares the squared error of the chances with always giving the training years' storm rate), so the
page only says "higher" or "lower than usual" there. Storms that come from clouds thrown out by the Sun cannot be
seen in the solar wind days ahead; only the 27-day echo of fast wind gives some warning.

The engine underneath also forecasts six measurements of the solar wind and of Earth's magnetic field, 5 minutes
to 24 hours ahead. The code is in `forecast/`. The models are trained once (`python -m forecast.train`,
8 minutes here, then `python -m forecast.daily`) and the page and a small HTTP API
(`uvicorn forecast.api:app`) only read them.

The baseline is persistence, $\hat y_{t+h} = y_t$: tomorrow looks like today. The model learns the change instead
of the value,

$$\hat y_{t+h} = y_t + f_h(\mathbf{x}_t),$$

where $f_h$ is a gradient-boosted tree ensemble (XGBoost) and $\mathbf{x}_t$ holds 74 numbers
built only from readings at $t$ or before: recent values, means and spreads of speed, field, density, pressure,
SYM-H and AE, and the driving term $v B_s$ with $B_s = \max(0, -B_z)$. The years are split in time: train
2010-01-01 to 2021-12-31, validation 2022-01-01 to 2022-12-31, test 2023-01-01 to 2026-10-18, with one day left out at each
edge so that no answer leaks across. Every score below is from the test years. Skill is
$1 - \text{RMSE}_\text{model}/\text{RMSE}_\text{persistence}$.

| measurement (unit) | RMSE 1 h (persistence) | skill 1 h | RMSE 24 h (persistence) | skill 24 h |
|---|---|---|---|---|
| wind speed (km/s) | 19.1 (19.8) | 3% | 69.9 (82.2) | 15% |
| field strength (nT) | 1.32 (1.29) | -3% | 3.71 (4.51) | 18% |
| Bz (nT) | 3.23 (3.68) | 12% | 4.19 (5.74) | 27% |
| density (per cm³) | 2.56 (2.72) | 6% | 4.85 (6.76) | 28% |
| pressure (nPa) | 1.23 (1.29) | 5% | 2.17 (2.85) | 24% |
| SYM-H (nT) | 5.71 (6.77) | 16% | 21.9 (26.9) | 19% |

A storm start time is labelled 1 when $\min_{t \lt s \le t+H} \mathrm{SYMH}(s) \le \theta$, with $\theta$ = -50 nT
(storm) or -100 nT (strong storm). The classifier flags a storm when its chance passes the line with the best
$F_1$ on the validation year. Persistence here means "a storm now means a storm soon".

| event | storms in test (%) | precision | recall | F1 (persistence) | PR-AUC |
|---|---|---|---|---|---|
| Storm (SYM-H ≤ -50 nT) within 6 h | 12.2 | 0.86 | 0.75 | 0.80 (0.72) | 0.90 |
| Storm (SYM-H ≤ -50 nT) within 24 h | 20.4 | 0.72 | 0.63 | 0.67 (0.51) | 0.78 |
| Strong storm (SYM-H ≤ -100 nT) within 6 h | 2.1 | 0.84 | 0.56 | 0.67 (0.68) | 0.77 |
| Strong storm (SYM-H ≤ -100 nT) within 24 h | 4.4 | 0.50 | 0.47 | 0.49 (0.41) | 0.51 |

Three things the scores say plainly. First, at the shortest horizons the model is worse than persistence for field strength at 5 min, 15 min, 30 min and 1 h (skill -17.6% to -2.6%); density at 5 min and 15 min (skill -5.3% to -1.4%); pressure at 5 min and 30 min (skill -2.9% to -0.5%). Over a few minutes the value now is very hard to beat, so use persistence there. Second, the field direction $B_z$ is close to unpredictable beyond a few hours
($R^2$ = 0.01 at 6 hours); the model beats persistence there mainly by predicting the
average. Third, the 80% intervals were set on 2022, a quiet year, and in the stormier test years they held
between 74% and 80% of the time. Not tried yet: LightGBM and recurrent
networks.

## 6. Figures

![Figure 1](charts/A05_a_histogram_1.7-5.5AU.png)

**Figure 1.** Asteroids per 0.01 AU slice of average distance from the Sun (log scale). The narrow dips are the empty
lanes of section 3.1.

![Figure 2](charts/BF14_27_day_repeat.png)

**Figure 2.** Correlation of the daily solar-wind speed with itself $N$ days earlier. The peak at 27 days is the Sun's
turn (section 3.7).

![Figure 3](charts/BF30_size_rule.png)

**Figure 3.** Moon craters at least $D$ wide, both axes on a log scale. A straight line is a power law (section 3.10).

## 7. Running it

```
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/streamlit run app.py            # then open http://localhost:8501
```

The app has four pages: Home, Findings (the 32 results with a chart and an animation each), Charts and
Predictions (pick a day, get the storm chance). For the forecasts, train the models once with
`.venv/bin/python -m forecast.train` and then `.venv/bin/python -m forecast.daily` (they are not in git). It only
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

## 8. Caveats

* Most counts here are counts of what was found, not of what is there. The discovery, close-pass and planet results
  (findings 4, 8, 9, 23 and 26) say as much about telescopes as about space.
* Gaia distances toward the middle of the Milky Way are often poor (finding 20). We flag stars with RUWE above
  1.4 but we do not fix them.
* Some radial speeds above 550 km/s are more likely measuring errors than real stars
  (finding 22).
* The animations are drawings. Where a drawing is not data, for example a planet's place along its path or a turning
  globe, it says so on screen.
* We compared our numbers with the datathon's field guide. In 12 places they differ, and
  `FINDINGS.md` says so in a line that starts with "Note".

## 9. Files

```
app.py                     the Streamlit app (Home, Findings, Charts, Predictions)
app_pages/                 the four pages
forecast/                  the forecasts: features, training, the service the page uses, the HTTP API
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
