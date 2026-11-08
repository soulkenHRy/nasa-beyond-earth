"""Make the 32 finding animations: simple space sketches on a plain 2D canvas (no WebGL, no chart library).

Each finding gets animations/Fnn_<slug>.html: one page with a Play button. Before Play it shows the finished
picture; Play runs the story and stops on the finished picture again. The numbers on screen come from numbers/
(the key numbers are the checked lines kept in numbers/AN_keys.json) or straight from the data files in
data_cache/. Anything drawn that is not data says "Illustration, not to scale". The drawing code is
notebooks/space_engine.js. The earlier chart animations are kept in old/animations_plotly/.

    cd notebooks && ../.venv/bin/python make_space_anims.py              # all 32
    cd notebooks && ../.venv/bin/python make_space_anims.py --only 1 7   # some of them
"""
from __future__ import annotations

import argparse
import json
import re
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
NUM, DATA, OUT = ROOT / "numbers", ROOT / "data_cache", ROOT / "animations"
ENGINE = Path(__file__).with_name("space_engine.js")
ILL = "Illustration, not to scale"
# titles, short names and parts of the 32 findings (kept in the animation index itself)
OLD_INDEX = {int(v["n"]): v for v in json.loads((NUM / "AN_index.json").read_text()).values()}
KEYS = json.loads((NUM / "AN_keys.json").read_text())
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]
MOON_KM = 1737.4          # known science: the Moon's radius in km (used only to draw craters at true size)
PC_PER_MYR = 1.0227       # known science: 1 km per second is about 1.02 parsecs per million years (drawing only)
USED: dict[int, set] = {}  # numbers files used by each finding


class Facts:
    """One numbers/ table of key, value, shown."""

    def __init__(self, name: str, n: int | None = None):
        df = pd.read_csv(NUM / f"{name}.csv", dtype={"shown": str})
        self._s = dict(zip(df["key"], df["shown"]))
        self._v = {}
        for k, v in zip(df["key"], df["value"]):
            try:
                self._v[k] = float(v)
            except (TypeError, ValueError):
                pass
        if n is not None:
            USED.setdefault(n, set()).add(f"numbers/{name}.csv")

    def s(self, k: str) -> str:
        return str(self._s[k])

    def v(self, k: str) -> float:
        return self._v[k]


def K(name: str, n: int) -> pd.DataFrame:
    USED.setdefault(n, set()).add(f"numbers/{name}.csv")
    return pd.read_csv(NUM / f"{name}.csv")


@lru_cache(None)
def pq(name: str, cols: tuple) -> pd.DataFrame:
    return pd.read_parquet(DATA / f"{name}.parquet", columns=list(cols))


def data(name: str, cols: tuple, n: int) -> pd.DataFrame:
    USED.setdefault(n, set()).add(f"data_cache/{name}.parquet")
    return pq(name, cols)


def n0(v) -> str:
    return f"{int(round(float(v))):,}"


def rl(a, k: int = 2) -> list:
    return [round(float(x), k) for x in np.asarray(a, dtype=float)]


def il(a) -> list:
    return [int(x) for x in np.asarray(a)]


def ro(at: float, *lines: str) -> dict:
    return {"at": at, "lines": list(lines)}


def planet(name, a, P, lon0, color, rad, **kw) -> dict:
    return dict(name=name, a=float(a), P=float(P), lon0=lon0, color=color, r=rad, **kw)


def pick(n_rows: int, k: int, seed: int) -> np.ndarray:
    rs = np.random.default_rng(seed)
    return np.sort(rs.choice(n_rows, min(k, n_rows), replace=False))


@lru_cache(None)
def land(step_deg: float = 2.0) -> tuple:
    from global_land_mask import globe
    st = int(round(step_deg / abs(globe._lat[1] - globe._lat[0])))
    la, lo = globe._lat[st // 2::st], globe._lon[st // 2::st]
    m = ~globe._mask[st // 2::st, st // 2::st]          # the package's mask marks water; land is the rest
    ii, jj = np.nonzero(m)
    return la[ii], lo[jj]


def land_pts(step_deg: float = 2.0, north_only: bool = False) -> dict:
    la, lo = land(step_deg)
    keep = la > 0 if north_only else np.ones(len(la), bool)
    return dict(lat=rl(la[keep], 1), lon=rl(lo[keep], 1))


def wrap180(x):
    return (np.asarray(x) + 180.0) % 360.0 - 180.0


def destination(lat, lon, dist_deg, bearing_deg):
    """Point reached from (lat, lon) after dist_deg of arc along bearing_deg (from north, clockwise)."""
    p1, l1, d, b = (np.radians(np.asarray(x, dtype=float)) for x in (lat, lon, dist_deg, bearing_deg))
    p2 = np.arcsin(np.sin(p1) * np.cos(d) + np.cos(p1) * np.sin(d) * np.cos(b))
    l2 = l1 + np.arctan2(np.sin(b) * np.sin(d) * np.cos(p1), np.cos(d) - np.sin(p1) * np.sin(p2))
    return np.degrees(p2), wrap180(np.degrees(l2))


def circle_on_sphere(lat, lon, rad_deg, k: int = 24):
    b = np.linspace(0, 360, k + 1)
    la, lo = destination(np.full(k + 1, lat), np.full(k + 1, lon), np.full(k + 1, rad_deg), b)
    return rl(la, 2), rl(lo, 2)


def asteroids(cols, n):
    return data("asteroids", tuple(cols), n)


# ======================================================================================================= Part A
def s01():
    n = 1
    f, z = Facts("BF01_asteroid_belt_lanes", n), Facts("AN01_empty_lanes", n)
    jA = Facts("AN06_trojan_swarms", n).v("jupiter_distance")
    lo, hi, jP = z.v("zoom_lo"), z.v("zoom_hi"), f.v("jupiter_period")
    a = asteroids(["a"], n)["a"].to_numpy()
    a = a[(a >= lo) & (a <= hi)]
    a = a[pick(len(a), 7000, 1)]
    ang = np.random.default_rng(2).uniform(0, 360, len(a))
    dips = [(f.v(f"dip{k}_a"), f.s(f"dip{k}_a"), f.s(f"dip{k}_ratio")) for k in range(1, 5)]
    mars = lo * 0.85
    belt = dict(
        tilt=0.56, rmap=[[0, 0], [lo, 0.3], [hi, 0.86], [jA, 0.98]], yps=0.75, sunR=11,
        planets=[planet("Earth", 1, 1, 40, "#4f8cff", 4.5), planet("Mars", mars, mars ** 1.5, 200, "#d0573a", 4),
                 planet("Jupiter", jA, jP, 120, "#d9b38c", 8, glow=True)],
        dots=dict(a=rl(a, 4), ang=rl(ang, 1), colors=["#cfd6e6"], size=1.5, alpha=0.8),
        marks=[dict(a=d[0], text=d[1], at=3.5 + i, ang=25 if i % 2 == 0 else -25) for i, d in enumerate(dips)],
        readout=[ro(0, "The asteroid belt", f"Each dot is a real asteroid (a sample of the {f.s('rows_kept')} counted)"),
                 ro(3.5, "Empty lanes (dashed rings)", f"at {dips[0][1]}, {dips[1][1]}, {dips[2][1]} and {dips[3][1]} "
                    "Earth-Sun distances from the Sun"),
                 ro(8, "Jupiter's rhythm: trips for each trip of Jupiter",
                    *[f"lane {d[1]}: {d[2]} trips" for d in dips]),
                 ro(12.5, f"The closest lane, {f.s('gap_lo')} to {f.s('gap_hi')}", f"only {f.s('gap_count')} asteroids",
                    f"just inside it, {f.s('inside_lo')} to {f.s('inside_hi')}: {f.s('inside_count')}")])
    return dict(type="belt", dur=16, belt=belt,
                tag=f"{ILL}: each dot sits at its real distance from the Sun, but where it is around its path is made up, "
                    "and the Sun and planets are drawn far too big.",
                how="Press ▶ Play: real asteroids go around the Sun, and the empty lanes in the belt light up.",
                steps=[[0, "Thousands of real asteroids go around the Sun, between Mars and Jupiter. Each dot sits at "
                            "its real distance from the Sun."],
                       [3.5, "Look for thin, dark rings in the belt: the empty lanes (dashed)."],
                       [8, f"A rock in the {dips[0][1]} lane goes around {dips[0][2]} times for each trip of Jupiter. "
                           "Jupiter pulls it at the same spot again and again, like pushing a swing, until the rock "
                           "is thrown out of its path."],
                       [12.5, "That is why the lanes stay empty."]])


def s02():
    n = 2
    f, z = Facts("BF02_darker_farther_out", n), Facts("AN01_empty_lanes", n)
    jA = Facts("AN06_trojan_swarms", n).v("jupiter_distance")
    jP = Facts("BF01_asteroid_belt_lanes", n).v("jupiter_period")
    zones = K("K02_darker_farther_out", n)
    lo, hi, cut = float(zones["zone_from"].min()), float(zones["zone_to"].max()), f.v("bright_cut")
    t = asteroids(["a", "albedo", "kind"], n).dropna()
    t = t[(t["a"] >= lo) & (t["a"] < hi) & t["kind"].str.startswith("a")]
    assert len(t) == int(f.v("zone_rows")), len(t)
    t = t.iloc[pick(len(t), 6500, 3)]
    ang = np.random.default_rng(4).uniform(0, 360, len(t))
    t0, t1 = 3.0, 11.0
    zl, ztext = [], []
    for k in range(1, 5):
        a0, a1 = f.v(f"z{k}_lo"), f.v(f"z{k}_hi")
        at = round(t0 + (t1 - t0) * ((a0 + a1) / 2 - lo) / (hi - lo), 2)
        zl.append(dict(a0=a0, a1=a1, at=at, color="#7fe3ff", alpha=0.08))
        ztext.append(dict(a=(a0 + a1) / 2, ang=0, at=at, text=f.s(f"z{k}_pct"), bold=True, color="#ffffff", size=12.5))
    mars = lo * 0.85
    belt = dict(
        tilt=0.56, rmap=[[0, 0], [lo, 0.3], [hi, 0.86], [jA, 0.98]], yps=0.5, sunR=11,
        planets=[planet("Mars", mars, mars ** 1.5, 200, "#d0573a", 4), planet("Jupiter", jA, jP, 120, "#d9b38c", 8)],
        dots=dict(a=rl(t["a"], 4), ang=rl(ang, 1), c=il(t["albedo"].to_numpy() >= cut),
                  colors=["#6b5444", "#fff3d6"], size=1.9, alpha=0.95),
        zones=zl, labels=ztext, sweep=dict(a0=lo, a1=hi, t0=t0, t1=t1),
        readout=[ro(0, "Shiny or dark?", f"Light dots: shiny rock (shininess {f.s('bright_cut')} or more)",
                    "Dark dots: dark rock, like charcoal", f"{f.s('zone_rows')} asteroids with a measured shininess")]
        + [ro(zl[k - 1]["at"], f"Zone {k}: {f.s(f'z{k}_lo')} to {f.s(f'z{k}_hi')} from the Sun",
              f"{f.s(f'z{k}_pct')} of the asteroids here are shiny",
              f"middle shininess: {f.s(f'z{k}_median')}") for k in range(1, 5)]
        + [ro(12, "Shiny ones, out of every 100:", f"{f.s('z1_pct')}, then {f.s('z2_pct')}, then {f.s('z3_pct')}, "
              f"then only {f.s('z4_pct')}")])
    return dict(type="belt", dur=15, belt=belt,
                tag=f"{ILL}: each dot is a real asteroid at its real distance from the Sun; where it sits around "
                    "its path is made up.",
                how="Press ▶ Play: a probe flies out through the belt and counts the shiny rocks in each zone.",
                steps=[[0, "Each dot is a real asteroid with a measured shininess. Light dots are shiny stone; dark "
                           "dots are dark rock."],
                       [t0, "A probe flies out from the Sun and checks each zone of the belt."],
                       [12, "Near the Sun, most rocks are light-coloured stone. Far away, almost all are as dark as "
                            "charcoal."]])


def s03():
    n = 3
    f = Facts("BF03_spin_limit", n)
    t = asteroids(["diameter", "rot_per", "H", "kind"], n)
    t = t[t["kind"].isin(["an", "au"]) & t["rot_per"].notna()].copy()
    guess = 1329 / np.sqrt(f.v("albedo_guess")) * 10 ** (-t["H"] / 5)       # size from brightness (BF_A rule)
    t["diameter"] = t["diameter"].fillna(guess)
    t = t.dropna(subset=["diameter"])
    lim = f.v("limit_h")
    big = t[t["diameter"] > f.v("big_km")]["rot_per"].to_numpy()
    small = t[t["diameter"] < f.v("small_km")]["rot_per"].to_numpy()
    assert (len(big), int((big < lim).sum()), len(small), int((small < lim).sum())) == tuple(
        int(f.v(k)) for k in ("big_n", "big_fast", "small_n", "small_fast")), (len(big), len(small))
    rs = np.random.default_rng(5)

    def strat(vals, k, share):
        nf = int(round(k * share))
        fast, slow = vals[vals < lim], vals[vals >= lim]
        out = np.concatenate([rs.choice(fast, nf, replace=False), rs.choice(slow, k - nf, replace=False)])
        rs.shuffle(out)
        return out

    bigs = strat(big, 30, f.v("big_fast") / f.v("big_n"))
    smalls = strat(small, 30, f.v("small_fast") / f.v("small_n"))
    spin = dict(big=rl(bigs, 3), small=rl(smalls, 4), limit=lim, hps=1, blurBelow=lim / 7, tSmall=4.5, tRecord=10.5,
                bigTitle=f"Big asteroids (wider than {f.s('big_m')} m)",
                smallTitle=f"Small asteroids (narrower than {f.s('small_m')} m)",
                legend=f"Orange: spins faster than once every {f.s('limit_h')} hours",
                recordName=f.s("record_name"),
                readout=[ro(0, "Every rock is spinning, at its real speed (sped up)"),
                         ro(4.5, f"Speed limit: once every {f.s('limit_h')} hours",
                            f"Big: only {f.s('big_fast')} of {f.s('big_n')} spin faster ({f.s('big_fast_pct')})"),
                         ro(7.5, f"Big: only {f.s('big_fast')} of {f.s('big_n')} spin faster ({f.s('big_fast_pct')})",
                            f"Small: {f.s('small_fast')} of {f.s('small_n')} do ({f.s('small_fast_pct')})"),
                         ro(10.5, f"Record: {f.s('record_name')}, one spin every {f.s('record_seconds')} seconds",
                            f"Big: only {f.s('big_fast_pct')} spin faster than the limit; small: {f.s('small_fast_pct')}")])
    return dict(type="spin", dur=14, spin=spin,
                tag=f"{ILL}: the spin times are real (sped up); the rock shapes are made up.",
                how="Press ▶ Play: big and small asteroids spin at their real speeds, sped up.",
                steps=[[0, "Each rock spins at the real speed of a real asteroid, sped up so that one second here is "
                           "one hour in space."],
                       [4.5, f"Big asteroids are piles of loose rubble. Almost none turn faster than once every "
                             f"{f.s('limit_h')} hours, or they would fly apart, like sand from a fast-spinning bucket."],
                       [7.5, "Small asteroids are often solid rock, so many of them spin much faster."],
                       [10.5, f"The record: {f.s('record_name')}, one spin every {f.s('record_seconds')} seconds."]])


def s04():
    n = 4
    f = Facts("BF04_discovery_chart_2025", n)
    k4 = K("K04_discoveries_per_year", n).set_index("year")["first_sightings"]
    jA = Facts("AN06_trojan_swarms", n).v("jupiter_distance")
    jP = Facts("BF01_asteroid_belt_lanes", n).v("jupiter_period")
    y0, y1 = int(f.v("y_2018")), int(f.v("y_2025"))
    t = asteroids(["first_obs", "a"], n).copy()
    t["d"] = pd.to_datetime(t["first_obs"], errors="coerce")
    t = t[(t["d"].dt.year >= y0) & (t["d"].dt.year <= y1) & (t["a"] > 0) & (t["a"] < jA * 1.05)].dropna()
    t = t.iloc[pick(len(t), len(t) // 40, 6)]
    yr = t["d"].dt.year + (t["d"].dt.day_of_year - 1) / 366.0
    tY, start = 1.55, 0.6
    t0 = start + (yr - y0) * tY
    ang = np.random.default_rng(7).uniform(0, 360, len(t))
    belt = dict(
        tilt=0.56, rmap=[[0, 0], [1, 0.18], [1.8, 0.3], [3.6, 0.84], [jA, 0.98]], yps=0.6, sunR=11,
        planets=[planet("Earth", 1, 1, 40, "#4f8cff", 4.5), planet("Jupiter", jA, jP, 120, "#d9b38c", 8)],
        dots=dict(a=rl(t["a"], 3), ang=rl(ang, 1), t0=rl(t0, 2), c=il(t["d"].dt.year == y1),
                  colors=["#9fb3d8", "#ffd166"], size=1.9, alpha=0.9),
        readout=[ro(start + (y - y0) * tY, f"{y}", f"{n0(k4[y])} objects seen for the first time")
                 for y in range(y0, y1)]
        + [ro(start + (y1 - y0) * tY, f"{y1}: a big new telescope starts work",
              f"{f.s('y2025')} objects seen for the first time", f"July {y1} alone: {f.s('july_2025')}"),
           ro(start + (y1 - y0 + 1) * tY, f"{y1}: {f.s('y2025')} seen for the first time",
              f"{f.s('ratio_2025_avg')} times the {f.s('y_2018')} to {f.s('y_2024')} average of {f.s('y2018_24_avg')}")])
    return dict(type="belt", dur=start + (y1 - y0 + 1) * tY + 2.2, belt=belt,
                tag=f"{ILL}: each dot is a real object at its real distance from the Sun, appearing when it was first "
                    "seen; only some of them are drawn.",
                how="Press ▶ Play: year by year, new space rocks light up when they are first seen.",
                steps=[[0, "Each dot is a real object, lighting up in the year it was first seen. Blue: 2018 to 2024."],
                       [start + (y1 - y0) * tY, f"In {y1} (yellow) a big new telescope started work and spotted rocks "
                                                "nobody could see before, like new glasses for tiny print."],
                       [start + (y1 - y0 + 1) * tY, f"{y1}: about {f.s('ratio_2025_avg')} times as many as in a normal "
                                                    "recent year."]])


def s05():
    n = 5
    f, z = Facts("BF05_neptune_rhythm", n), Facts("AN05_neptune_rhythm", n)
    lo, hi = f.v("lo"), f.v("hi")
    t = asteroids(["a", "e", "kind"], n)
    a = t.loc[t["kind"].isin(["an", "au"]) & (t["e"] < 1) & (t["a"] > lo) & (t["a"] < hi), "a"].to_numpy()
    assert len(a) == int(f.v("rows_kept")), len(a)
    a = a[pick(len(a), 4500, 26)]
    band = (a > f.v("band_lo")) & (a < f.v("band_hi"))
    ang = np.random.default_rng(8).uniform(0, 360, len(a))
    pN = f.v("neptune_period")
    pP = pN * f.v("period_ratio")
    dur = 16
    belt = dict(
        tilt=0.56, rmap=[[0, 0], [hi, 0.97]], yps=z.v("neptune_trips") * pN / dur, sunR=7,
        planets=[planet("Neptune", f.v("neptune_a"), pN, 90, "#5b8cff", 6.5, glow=True),
                 planet("Pluto", f.v("pluto_a"), pP, 0, "#e0b48a", 4, e=f.v("pluto_e"), peri=0, M0=0)],
        dots=dict(a=rl(a, 3), ang=rl(ang, 1), c=il(band), colors=["#9fb0cc", "#ffb347"], size=1.7, alpha=0.85),
        labels=[dict(a=(f.v("band_lo") + f.v("band_hi")) / 2, ang=205, at=9.5, color="#ffcf8a", bold=True,
                     text=f"Pluto's crowd: {f.s('band_count')}"),
                dict(a=(f.v("kb_lo") + f.v("kb_hi")) / 2, ang=-62, at=11, color="#dfe6f5",
                     text=f"main crowd, {f.s('kb_lo')} to {f.s('kb_hi')}: {f.s('kb_count')}")],
        trips=[dict(p=0, name="Neptune"), dict(p=1, name="Pluto")],
        readout=[ro(0, "Past Neptune", f"{f.s('rows_kept')} icy objects between {f.s('lo')} and {f.s('hi')} Earth-Sun "
                    "distances"),
                 ro(4, f"The rhythm: {z.s('neptune_trips')} : {z.s('pluto_trips')}",
                    f"Neptune goes around {z.s('neptune_trips')} times while Pluto goes around {z.s('pluto_trips')} times"),
                 ro(9.5, f"Pluto's crowd, {f.s('band_lo')} to {f.s('band_hi')}: {f.s('band_count')} objects",
                    f"about {f.s('band_vs_sides')} times the same-size slices beside it")])
    return dict(type="belt", dur=dur, belt=belt,
                tag=f"{ILL}: Neptune and Pluto's paths and the dots' distances are real; the speed is sped up and "
                    "where each dot sits around its path is made up.",
                how="Press ▶ Play: Neptune goes around the Sun 3 times while Pluto goes around 2 times.",
                steps=[[0, "Past Neptune, thousands of icy objects go around the Sun. Each dot sits at its real "
                           "distance."],
                       [4, f"Pluto's path crosses Neptune's. But Neptune goes around {z.s('neptune_trips')} times "
                           f"while Pluto goes around {z.s('pluto_trips')} times, so Neptune is always far away when "
                           "Pluto crosses its path."],
                       [9.5, "Like two runners timed never to bump: objects at Pluto's distance are safe, so they "
                             "crowd there (orange)."]])


def s06():
    n = 6
    f, z = Facts("BF06_trojan_swarms", n), Facts("AN06_trojan_swarms", n)
    jP = Facts("BF01_asteroid_belt_lanes", n).v("jupiter_period")
    t = K("AN06_trojan_places", n)
    t = t.iloc[pick(len(t), 6000, 9)]
    jA, J = z.v("jupiter_distance"), f.v("jupiter_est")
    dur = 16
    belt = dict(
        tilt=0.56, rmap=[[0, 0], [jA * 1.25, 0.97]], yps=jP / dur, sunR=10,
        planets=[planet("Earth", 1, 1, 30, "#4f8cff", 4), planet("Jupiter", jA, jP, J, "#d9b38c", 9, glow=True)],
        dots=dict(a=rl(t["distance_from_sun"], 3), ang=rl(t["place_deg"], 2), lockP=jP, colors=["#b9d3ff"],
                  size=1.6, alpha=0.75),
        labels=[dict(a=jA, ang=f.v("ahead_peak"), lockP=jP, at=9.5, bold=True, color="#ffd166", border="#ffd166",
                     text=f"Ahead of Jupiter: {f.s('n_ahead')}", dy=-26),
                dict(a=jA, ang=f.v("behind_peak"), lockP=jP, at=10.5, bold=True, color="#ffffff",
                     text=f"Behind Jupiter: {f.s('n_behind')}", dy=-26)],
        readout=[ro(0, "Jupiter's two swarms", f"{f.s('trojans')} asteroids share Jupiter's path"),
                 ro(4, f"One trip around the Sun takes Jupiter {Facts('BF01_asteroid_belt_lanes').s('jupiter_period')} "
                    "years", "the swarms travel with it"),
                 ro(9.5, f"Ahead: {f.s('n_ahead')}   Behind: {f.s('n_behind')}",
                    f"{f.s('n_ahead')} ÷ {f.s('n_behind')} = {f.s('ratio')}: the front swarm is bigger")])
    return dict(type="belt", dur=dur, belt=belt,
                tag=f"{ILL}: the dots are the Trojans' real places; the turning is sped up and the Sun and planets "
                    "are drawn far too big.",
                how="Press ▶ Play: Jupiter goes once around the Sun, with one swarm ahead of it and one behind.",
                steps=[[0, "Each dot is a real Trojan asteroid, at its real place. They share Jupiter's path around "
                           "the Sun."],
                       [4, "As Jupiter goes around, the two swarms go with it: one stays ahead, one stays behind, "
                           "like joggers with a big runner."],
                       [9.5, f"The swarm in front is bigger: {f.s('n_ahead')} against {f.s('n_behind')}."]])


def s07():
    n = 7
    f = Facts("BF07_hazard_formula", n)
    t = asteroids(["pdes", "neo", "pha", "H", "moid", "a", "e", "om", "w", "ma"], n).dropna(subset=["a", "e", "moid", "H"])
    t = t[(t["neo"] == "Y") & (t["a"] * (1 + t["e"]) < 2.45) & (t["e"] < 0.85)]
    cut, hcut = f.v("moid_cut"), f.v("H_cut")
    rs = np.random.default_rng(10)
    g2 = t[(t["pha"] == "Y")]
    g1 = t[(t["moid"] <= cut) & (t["H"] > hcut) & (t["pha"] == "N")]
    g0 = t[(t["moid"] > cut)]
    every = asteroids(["pdes", "neo", "pha", "H", "moid", "a", "e", "om", "w", "ma"], n)
    yr4 = every[every["pdes"] == f.s("yr4_name")].copy()
    assert len(yr4) == 1
    yr4["ma"] = (-360 * 0.3 * 14 / yr4["a"] ** 1.5) % 360        # at the Sun end of its path when it is shown
    parts = [g2.iloc[rs.choice(len(g2), 22, replace=False)], g1.iloc[rs.choice(len(g1), 15, replace=False)],
             g0.iloc[rs.choice(len(g0), 22, replace=False)], yr4]
    kinds = [2] * 22 + [1] * 15 + [0] * 22 + [1] * len(yr4)
    s = pd.concat(parts)
    rocks = dict(a=rl(s["a"], 4), e=rl(s["e"], 4), w=rl((s["om"] + s["w"]) % 360, 1), M0=rl(s["ma"], 1),
                 H=rl(s["H"], 2), kind=kinds, yr4=[0] * (len(s) - len(yr4)) + [1] * len(yr4))
    nea = dict(rocks=rocks, rmax=2.45, yps=0.3, band=cut, tBand=4, tSize=8, tYr4=12, earthLon0=0,
               yr4Name=f.s("yr4_name"),
               readout=[ro(0, "Near-Earth rocks", "Each line is a real rock's path around the Sun"),
                        ro(4, "Line 1: distance", f"its path comes within {f.s('moid_cut')} Earth-Sun distances of "
                           f"Earth's path ({f.s('moid_km')} million km): yellow"),
                        ro(8, "Line 2: size", f"brightness number {f.s('H_cut')} or less (about {f.s('size_H22')} m "
                           "or wider)", "past both lines: red, \"potentially hazardous\""),
                        ro(12, f.s("yr4_name"), f"its path comes very close ({f.s('yr4_moid')}), but its brightness "
                           f"number is {f.s('yr4_H')}: too small for line 2", f"so its label is {f.s('yr4_pha')}")])
    return dict(type="nea", dur=16, nea=nea,
                tag=f"{ILL}: the paths are real; the speed is sped up and the Sun, Earth and rocks are drawn far too "
                    "big. Only some of the rocks are drawn.",
                how="Press ▶ Play: real near-Earth rocks go around the Sun, and the two measuring lines are checked.",
                steps=[[0, "Real near-Earth rocks go around the Sun on their real paths. Earth's path is the blue ring."],
                       [4, "Line 1: the rock's path must come close to Earth's path (inside the yellow band)."],
                       [8, "Line 2: the rock must be big enough. Rocks past both lines turn red: \"potentially "
                           "hazardous\"."],
                       [12, "Like the height line at a theme-park ride: the label only means a rock passed two "
                            "measuring lines. It does not mean the rock is coming."]])


# ======================================================================================================= Parts B and C
def s08():
    n = 8
    f = Facts("BF08_passes_bunch_today", n)
    k8 = K("K08_passes_per_decade", n)
    c = data("close_approaches", ("cd", "dist"), n)
    yr = c["cd"].str[:4].astype(int)
    dec = (yr // 10) * 10
    ld = f.v("ld_au")
    rs = np.random.default_rng(11)
    decades, tDec = [], 0.42
    for d, p in zip(k8["decade"], k8["passes"]):
        dist = c.loc[dec == d, "dist"].to_numpy() / ld
        k = max(1, int(round(p / 100)))
        dd = rs.choice(dist, min(k, len(dist)), replace=False) if len(dist) else np.array([])
        decades.append(dict(d=rl(dd, 3), lines=[f"{d}s", f"{n0(p)} close passes"]))
    edge = f"as far as the file goes: {f.s('range_ld')} Moon distances"
    flyby = dict(decades=decades, tDec=tDec, cross=1.25, rmax=f.v("range_ld"), edgeText=edge,
                 final=["Close passes per decade", f"{f.s('dec_1900s_label')}: about {f.s('dec_1900s_avg')}",
                        f"2010s: {f.s('dec_2010')}   2020s: {f.s('dec_2020')}", f"2030s: only {f.s('dec_2030')}",
                        "Red: closer than the Moon"])
    i2010 = list(k8["decade"]).index(int(f.s("lbl_2010")[:4]))
    i2030 = list(k8["decade"]).index(int(f.s("lbl_2030")[:4]))
    dur = round(len(decades) * tDec + 2.6, 2)
    return dict(type="flyby", dur=dur, flyby=flyby,
                tag=f"{ILL}: each streak is a real pass at its real closest distance (on a squeezed scale); the "
                    "direction is made up. One streak for about every 100 passes.",
                how="Press ▶ Play: decade by decade, real space rocks fly past Earth.",
                steps=[[0, "Each streak is a real space rock passing Earth, at its real closest distance. The grey "
                           "ring is the Moon's path."],
                       [i2010 * tDec, "Around today the passes bunch up: we find far more rocks now, with better "
                                      "telescopes."],
                       [i2030 * tDec, "After the 2020s they drop: we only know the future passes of rocks already "
                                      "found."],
                       [len(decades) * tDec, "Like counting cars with a flashlight: you only see the cars in your "
                                             "beam."]])


def s09():
    n = 9
    f = Facts("BF09_july_quiet", n)
    k9 = K("K09_passes_by_month", n)
    vals = k9["small_rocks_h_over_25"].to_numpy()
    hi = [MONTHS.index(f.s("small_min_month")), MONTHS.index(f.s("small_max_month"))]
    months = dict(names=list(k9["month"]), texts=[n0(v) for v in vals], hi=hi, t0=0.6, t1=12.6,
                  flashes=[int(round(v / 45)) for v in vals], flashColour="#e6ecff",
                  title=f"Small rocks found passing Earth, {f.s('y_from')} to {f.s('y_to')}",
                  lines=[f"{MONTHS[i]}: {n0(v)} passes" for i, v in enumerate(vals)],
                  final=[f"Small rocks, {f.s('y_from')} to {f.s('y_to')}",
                         f"July: {f.s('small_jul')} passes. October: {f.s('small_oct')}",
                         f"{f.s('small_oct')} ÷ {f.s('small_jul')} = {f.s('ratio')}"])
    return dict(type="months", dur=15, months=months,
                tag=f"{ILL}: Earth's trip and the flashes are drawn; the counts per month are real.",
                how="Press ▶ Play: Earth goes once around the Sun, and each month the rocks found that month flash.",
                steps=[[0, "Earth goes around the Sun once a year. Each flash is a small rock found passing Earth "
                           "in that month."],
                       [6.6, "July: short, stormy summer nights where most telescopes are, so fewer rocks are found."],
                       [9.6, "October: long, dark nights, and the telescopes find far more."],
                       [12.6, "The rocks didn't leave in July. Like birdwatching on short summer nights, we just "
                              "looked less."]])


def s10():
    n = 10
    f = Facts("BF10_fireballs_anywhere", n)
    t = data("fireballs", ("date", "impact-e", "lat", "lat-dir", "lon", "lon-dir"), n).dropna(subset=["lat", "lon"]).copy()
    assert len(t) == int(f.v("located")), len(t)
    t["la"] = np.where(t["lat-dir"] == "S", -t["lat"], t["lat"])
    t["lo"] = np.where(t["lon-dir"] == "W", -t["lon"], t["lon"])
    t["d"] = pd.to_datetime(t["date"])
    t = t.sort_values("d")
    span = (t["d"] - t["d"].min()) / (t["d"].max() - t["d"].min())
    t0 = 0.8 + 11.5 * span.to_numpy()
    e = t["impact-e"].fillna(t["impact-e"].median()).to_numpy()
    size = np.clip(2.2 + 1.5 * np.log10(np.maximum(e, 0.01) / 0.05), 2.2, 9)
    big = int(np.argmax(e))
    cls = np.zeros(len(t), int)
    cls[big] = 1
    tb = round(float(t0[big]), 2)
    years = sorted(set(t["d"].dt.year))
    globe = dict(
        body="earth", land=land_pts(1.5),
        pts=dict(lat=rl(t["la"], 1), lon=rl(t["lo"], 1), t0=rl(t0, 2), s=rl(size, 1), c=il(cls),
                 colors=["#ffb347", "#ff3b3b"], pop=True, popColour="#ffd27a"),
        globes=[dict(cx=0.27, cy=0.56, wf=0.23, hf=0.36, rot=[[0, -130, 12], [16, -75, 12]],
                     title="The Americas side"),
                dict(cx=0.71, cy=0.56, wf=0.23, hf=0.36, rot=[[0, 30, 12], [16, 85, 12]],
                     title="Europe, Africa and Asia side")],
        labels=[dict(text=f"Biggest: {f.s('big1_kt')} kilotons ({f.s('big1_date')[:4]})", lat=f.v("big1_lat"),
                     lon=f.v("big1_lon"), at=tb, g=1, color="#ff6b6b", r=11)],
        readout=[ro(0.8 + 11.5 * (pd.Timestamp(f"{y}-01-01") - t["d"].min()) / (t["d"].max() - t["d"].min()),
                    "Fireballs with a known place", f"Year: {y}") for y in years if y > years[0]]
        + [ro(0, "Fireballs with a known place", f"Year: {years[0]}"),
           ro(12.6, f"{f.s('located')} of the {f.s('rows')} fireballs have a known place",
              f"Over the ocean: {f.s('over_ocean')} ({f.s('ocean_pct')}); the ocean covers about "
              f"{f.s('earth_ocean_pct')} of Earth", f"Biggest: {f.s('big1_kt')} kilotons, {f.s('big1_date')}")],
        roW=0.42)
    globe["readout"].sort(key=lambda r: r["at"])
    return dict(type="globe", dur=16, globe=globe,
                tag=f"{ILL}: the places and dates are real; the dot sizes and the turning are not.",
                how="Press ▶ Play: real fireballs flash on Earth at their real places, in time order.",
                steps=[[0, f"Each flash is a real fireball, a space rock burning up in the sky, at its real place, in "
                           f"time order ({f.s('first')[:4]} to {f.s('last')[:4]})."],
                       [5.5, "They happen everywhere. Most are over the ocean, because the ocean covers most of Earth."],
                       [tb, "One was far bigger than all the others (red)."],
                       [12.6, "Like rice thrown at a spinning beach ball: it lands everywhere."]])


def s11():
    n = 11
    f = Facts("BF11_fewer_at_dawn", n)
    slots = [dict(h0=h, h1=h + 2, n=int(f.v(f"slot_{h}")),
                  hi=h in (int(f.v("min_slot_from")), int(f.v("max_slot_from")))) for h in range(0, 24, 2)]
    pole = dict(slots=slots, land=land_pts(3.0, north_only=True), tR0=1.0, tR1=12.5, hps=2, ut0=0,
                readout=[ro(0, "Fireballs by the local clock (Sun time)",
                            f"Fewest: {f.s('min_slot_from')} to {f.s('min_slot_to')} am (dawn), {f.s('min_count')}",
                            f"Most: the two hours before midnight, {f.s('max_count')}",
                            f"Even spread: {f.s('avg_slot')} per 2-hour slot")])
    return dict(type="pole", dur=15, pole=pole,
                tag=f"{ILL}: the counts are real; the rocks' paths and Earth's turning are drawn.",
                how="Press ▶ Play: real fireballs hit Earth at their real local time; watch the evening side.",
                steps=[[0, "Earth seen from above the North Pole. Sunlight comes from the left: the left half is day, "
                           "the right half is night."],
                       [3, "Each streak is a real fireball, placed at its local time. The ring counts them in 2-hour "
                           "slots."],
                       [7.5, "Many space rocks go around the Sun the same way as Earth, a bit faster. They catch Earth "
                             "from behind, on the evening side."],
                       [12.5, f"The dawn side faces forward, so fewer hit it: only {f.s('min_count')} at "
                              f"{f.s('min_slot_from')} to {f.s('min_slot_to')} am, against {f.s('max_count')} before "
                              "midnight."]])


# ======================================================================================================= Part D
def s12():
    n = 12
    f = Facts("BF12_storm_cycle", n)
    k = K("K12_storm_days_per_year", n)
    mx = float(k["storm_days"].max())
    tY = 0.85
    years = []
    for _, r in k.iterrows():
        y = int(r["year"])
        lvl = float(r["storm_days"]) / mx
        last = f" (to {f.s('last_day')})" if y == int(k["year"].max()) else ""
        years.append(dict(speed=float(r["average_speed_km_s"]), level=lvl, dens=0.3 + 0.7 * lvl,
                          spots=int(round(1 + 9 * lvl)),
                          lines=[f"{y}{last}", f"Storm days: {n0(r['storm_days'])}",
                                 f"Strong-storm days: {n0(r['strong_storm_days'])}",
                                 f"Wind: {n0(r['average_speed_km_s'])} km every second"]))
    ys = list(k["year"].astype(int))
    wind = dict(years=years, tYear=tY, pRef=1, symScale=1, pxPerKm=0.45,
                notes=[ro(0, f"The Sun's cycle: about {f.s('cycle_years')} years from one stormy time to the next")])
    return dict(type="wind", dur=round(len(years) * tY + 1.5, 2), wind=wind,
                tag=f"{ILL}: the yearly numbers are real; the Sun, its spots, Earth and the wind are drawn.",
                how="Press ▶ Play: year by year, the solar wind blows and Earth's space storms rise and fall.",
                steps=[[0, "The Sun blows a wind of tiny particles at Earth. When it blows hard, Earth gets storms in "
                           "space (green lights at the poles)."],
                       [ys.index(int(f.v("y_2019"))) * tY, f"{f.s('y_2019')} and {f.s('y_2020')}: the Sun's calm winter, only "
                                             f"{f.s('storm_2019')} and {f.s('storm_2020')} storm days."],
                       [ys.index(int(f.v("y_2024"))) * tY, f"{f.s('y_2024')} and {f.s('y_2025')}: its stormy summer, "
                                             f"{f.s('storm_2024')} and {f.s('storm_2025')} storm days."]])


def s13():
    n = 13
    f = Facts("BF13_before_a_storm", n)
    m = K("BF13_median_curves", n)
    m = m[(m["hours_from_lowest"] >= -48) & (m["hours_from_lowest"] <= 6)].iloc[::3]
    h = m["hours_from_lowest"].to_numpy()
    tt = 0.5 + (h + 48) / 54 * 14.5

    def when(x):
        if abs(x) < 0.05:
            return "The lowest point of the storm"
        return f"{abs(x):.1f} hours {'before' if x < 0 else 'after'} the lowest point".replace(".0 hours", " hours")

    s = dict(t=rl(tt, 3), speed=rl(m["speed_km_s"], 1), dens=rl(m["density_cm3"], 2), bz=rl(m["bz_gsm_nT"], 2),
             sym=rl(m["sym_h_nT"], 1), press=rl(m["pressure_nPa"], 2), when=[when(x) for x in h])
    wind = dict(series=s, pRef=float(np.median(m["pressure_nPa"])), densMax=float(m["density_cm3"].max()),
                symScale=150, pxPerKm=0.45, redBelow=f.v("storm_cut"),
                notes=[ro(0, f"{f.s('events_strong')} strong storms, lined up on their lowest points: these are the "
                          "middle values")])
    at = lambda hours: round(0.5 + (hours + 48) / 54 * 14.5, 2)  # noqa: E731
    return dict(type="wind", dur=16, wind=wind,
                tag=f"{ILL}: the numbers are the real middle values of {f.s('events_strong')} storms; the Sun, the "
                    "bubble and the particles are drawn.",
                how="Press ▶ Play: the two days before a big storm, as the solar wind changes hour by hour.",
                steps=[[0, "The solar wind blows from the Sun to Earth's magnetic bubble. These are the middle values "
                           f"of {f.s('events_strong')} big storms, lined up on their worst moment."],
                       [at(-f.v("h20")), f"About {f.s('h20')} hours before: the wind gets crowded ({f.s('den_m20')} "
                                         f"instead of {f.s('den_base')})."],
                       [at(-f.v("h8")), f"About {f.s('h8')} hours before: it pushes harder ({f.s('pre_m8')} instead of "
                                        f"{f.s('pre_base')}) and squeezes the bubble."],
                       [at(-f.v("h6")), "Then the wind's magnet turns south (red arrow). The door opens and the "
                                        "storm meter dives."],
                       [at(0), "The storm. Like a traffic jam: first the cars bunch up, then they push, then the road "
                               "tilts the wrong way."]])


def s14():
    n = 14
    f = Facts("BF14_repeats_27_days", n)
    per = f.v("best_lag")
    spiral = dict(period=per, dps=3 * per / 15, travel=4, a0=0,
                  hitText="The same hole has faced Earth {n} times",
                  waitText="Waiting for the hole to face Earth",
                  final=[f"The Sun turns once every {f.s('sun_turn')} days (seen from Earth)",
                         f"Slid by {f.s('best_lag')} days, the wind matches itself: {f.s('all_27')} (all years)",
                         f"{f.s('sub_27')} in the quiet years {f.s('y_2016')} to {f.s('y_2018')}",
                         f"Slid by {f.s('lag13')} days: only {f.s('all_13')}"])
    return dict(type="spiral", dur=15, spiral=spiral,
                tag=f"{ILL}: the {f.s('best_lag')}-day turn is from our data; the Sun, the hole and the beam are drawn.",
                how="Press ▶ Play: the Sun turns, and its fast-wind beam sweeps over Earth every 27 days.",
                steps=[[0, "Seen from above: the Sun turns. A dark \"hole\" on it blows a beam of fast wind, like a "
                           "lighthouse."],
                       [1, "When the beam sweeps over Earth (green flash), a storm can start."],
                       [6, f"One turn later, {f.s('best_lag')} days on, the same hole faces Earth again, and the storm "
                           "comes back."]])


def s15():
    n = 15
    f = Facts("BF15_equinox_storms", n)
    k = K("K15_storms_by_month", n)
    pct = k["percent_of_time_in_storm"].to_numpy()
    months = dict(names=list(k["month"]), texts=[f.s(f"share_{i}") for i in range(1, 13)], hi=[2, 3, 8, 9],
                  t0=0.6, t1=12.6, flashes=[int(round(p * 7)) for p in pct], flashColour="#4dff9a", aurora=True,
                  level=rl(pct / pct.max(), 3), title="Share of the time with a storm in space",
                  lines=[f"{MONTHS[i - 1]}: storms {f.s(f'share_{i}')} of the time, {f.s(f'strong_{i}')} strong ones"
                         for i in range(1, 13)],
                  final=[f"Most stormy: March {f.s('share_3')}, April {f.s('share_4')}",
                         f"September {f.s('share_9')}, October {f.s('share_10')}",
                         f"Least: December {f.s('share_12')}, July {f.s('share_7')}",
                         f"{f.s('share_3')} ÷ {f.s('share_12')} = {f.s('max_vs_min')}"])
    return dict(type="months", dur=15, months=months,
                tag=f"{ILL}: Earth's trip and the flashes are drawn; the share of storm time in each month is real.",
                how="Press ▶ Play: Earth goes once around the Sun; storms flash more around March and October.",
                steps=[[0, "Earth goes around the Sun. Each green flash is a storm in space; more flashes means more "
                           "storm time that month."],
                       [2.6, "Around late March, Earth is tilted at just the right angle for the Sun's magnetic "
                             "\"key\": more storms."],
                       [8.6, "Around late September and October it happens again."],
                       [12.6, "In the months between, the key doesn't fit as well."]])


def s16():
    n = 16
    f = Facts("BF16_may_2024_superstorm", n)
    off = Facts("BF17_ontario_nights", n).v("utc_offset_summer")
    m = K("BF16_may_2024_window", n)
    m["d"] = pd.to_datetime(m["time_utc"])
    tt = 0.5 + np.arange(len(m)) / (len(m) - 1) * 14.5
    tor = m["d"] - pd.to_timedelta(off, unit="h")
    when = [f"{a:%d %b %H:%M} world time ({b:%H:%M} in Toronto)" for a, b in zip(m["d"], tor)]
    s = dict(t=rl(tt, 3), speed=rl(m["speed_km_s"].interpolate().bfill(), 1),
             dens=rl(m["density_cm3"].interpolate().bfill(), 2), bz=rl(m["bz_gsm_nT"].interpolate().bfill(), 2),
             sym=rl(m["sym_h_nT"].interpolate().bfill(), 1), press=rl(m["pressure_nPa"].interpolate().bfill(), 2),
             when=when)
    hit = float(tt[int(np.argmin(np.abs(m["d"] - pd.Timestamp(f"{f.s('win_from_code')[:10]} {f.s('shock_utc')}"))))])
    low = float(tt[int(np.argmin(m["sym_h_nT"].to_numpy()))])
    wind = dict(series=s, pRef=float(np.nanmedian(m["pressure_nPa"])), densMax=float(np.nanmax(m["density_cm3"])),
                symScale=220, pxPerKm=0.4, cme=dict(t0=max(0.2, hit - 2.6), t1=hit,
                                                                    text="a giant cloud from the Sun"),
                notes=[ro(0, f"From {f.s('win_from')} to {f.s('win_to')} (world time)")])
    wind["redBelow"] = Facts("BF12_storm_cycle", n).v("strong_cut")
    return dict(type="wind", dur=16, wind=wind,
                tag=f"{ILL}: the wind, magnet and storm numbers are the real 5-minute readings; the Sun, the cloud and "
                    "the bubble are drawn.",
                how="Press ▶ Play: the May 2024 superstorm, hour by hour, as a giant cloud from the Sun hits Earth.",
                steps=[[0, "10 May 2024, noon world time. The solar wind blows as usual."],
                       [max(0.2, hit - 2.6), "A giant cloud of particles from the Sun is on its way."],
                       [hit, f"{f.s('shock_utc')} world time ({f.s('shock_tor')} in Toronto): it hits. The wind jumps "
                             f"from {f.s('speed_before')} to {f.s('speed_after')} km every second, and the storm meter "
                             f"first goes UP to {f.s('symh_up')}."],
                       [hit + 1.2, "Then the cloud's magnet points south (red arrow) and the storm meter dives."],
                       [low, f"Lowest: {f.s('low')} at {f.s('low_utc')} world time ({f.s('low_tor')} in Toronto). "
                             "Like a wave hitting a sandcastle: first a push up, then everything pulled down."]])


def s17():
    n = 17
    f = Facts("BF17_ontario_nights", n)
    k = K("K17_ontario_nights", n)
    j = K("AN17_january_2026_storm", n)
    j["d"] = pd.to_datetime(j["toronto_time"])
    j = j.iloc[::3]
    tY, tS0, tS1 = 0.7, None, None
    years = [dict(n=int(r["nights"]), lines=[f"{int(r['year'])}", f"{n0(r['nights'])} strong-storm nights in "
                                             "Toronto"]) for _, r in k.iterrows()]
    tS0 = round(len(years) * tY + 0.4, 2)
    tS1 = tS0 + 5.5
    hh = (j["d"].dt.hour + j["d"].dt.minute / 60).to_numpy()
    dark = (hh >= int(f.s("from_h")[:2])) | (hh < int(f.s("to_h")[:2]))
    lines = [[f"January {f.s('y_2026')} storm", f"{d:%d %b %H:%M} Toronto time", f"Storm meter: {n0(v)}",
              "dark in Toronto" if dk else "daytime in Toronto"] for d, v, dk in zip(j["d"], j["sym_h_nT"], dark)]
    pole = dict(years=years, tYear=tY, tS0=tS0, tS1=tS1, land=land_pts(3.0, north_only=True), hps=1, ut0=0,
                toronto=dict(lat=43.7, lon=-79.4), ovalQuiet=67, ovalStorm=44,
                series=dict(h=rl(hh, 3), v=rl(j["sym_h_nT"], 1), lines=lines, scale=-f.v("jan_low")),
                readout=[ro(0, f"{f.s('nights_total')} nights with a strong storm",
                            f"(storm meter {f.s('cut')} or lower) between {f.s('from_h')} and {f.s('to_h')} Toronto time",
                            f"{f.s('n_2023')} each in {f.s('y_2023')}, {f.s('y_2024')} and {f.s('y_2025')}; "
                            f"{f.s('n_2019')} in {f.s('y_2019')}, {f.s('y_2020')} and {f.s('y_2022')}")])
    return dict(type="pole", dur=round(tS1 + 1.8, 2), pole=pole,
                tag=f"{ILL}: the nights and the storm meter are real; Earth, the northern-lights ring and Toronto's "
                    "place are drawn.",
                how="Press ▶ Play: year by year, every strong storm that happened while it was dark in Toronto.",
                steps=[[0, "Earth from above the North Pole; the right half is night. The green ring is where the "
                           "northern lights are."],
                       [0.7, f"Each flash is one night with a strong storm while it was dark in Toronto "
                             f"({f.s('from_h')} to {f.s('to_h')})."],
                       [tS0, f"January {f.s('y_2026')}: a strong storm, hour by hour, in Toronto time."],
                       [tS1, "Like a shooting star: the show has to happen while it's dark where you are."]])


# ======================================================================================================= Part E
def s18():
    n = 18
    f = Facts("BF18_star_families", n)
    st = data("stars", ("bp_rp", "abs_g_mag"), n).dropna()
    wd = (st["abs_g_mag"] > f.v("wd_a") + f.v("wd_b") * st["bp_rp"]) & (st["bp_rp"] < f.v("wd_colour"))
    gi = (st["abs_g_mag"] < f.v("giant_mag")) & (st["bp_rp"] > f.v("giant_colour"))
    assert (int(wd.sum()), int(gi.sum())) == (int(f.v("wd")), int(f.v("giants")))
    fam = np.where(wd, 1, np.where(gi, 2, 0))
    idx = pick(len(st), 2600, 12)
    s = st.iloc[idx]
    fm = fam[idx]
    size = np.where(fm == 2, 6.5, np.where(fm == 1, 1.7, np.clip(3.9 - 0.2 * s["abs_g_mag"], 1.3, 3.4)))
    sort = dict(bp=rl(s["bp_rp"], 2), fam=il(fm), size=rl(size, 2), tMove0=3, tMove1=7.5,
                groups=[dict(x=0.33, y=0.54, spread=1.0, ly=0.42, color="#9fd0ff", at=8,
                             text=f"Main band, like the Sun: {f.s('main_seq')}"),
                        dict(x=0.78, y=0.74, spread=1.1, ly=0.14, color="#dfe6ff", at=9,
                             text=f"White dwarfs: {f.s('wd')}"),
                        dict(x=0.78, y=0.33, spread=2.6, ly=-0.13, color="#ffab5e", at=10,
                             text=f"Giants: {f.s('giants')}")],
                readout=[ro(0, f"Stars with a colour: {f.s('with_colour')}", "each dot is a real star, in its real colour")])
    return dict(type="sort", dur=13.5, sort=sort,
                tag=f"{ILL}: the stars' colours and families are real; their places in the sky here are made up.",
                how="Press ▶ Play: real stars, all mixed up, sort themselves into families.",
                steps=[[0, "Each dot is a real star near the Sun, in its real colour. In the sky they are all mixed up."],
                       [3, "Sort them by colour and true brightness, and they fall into families."],
                       [8, "Most are in the main band, like the Sun. A few are giants: huge and bright. Some are white "
                           "dwarfs: tiny, hot and faint."]])


def _hundred(shares) -> list:
    raw = np.asarray(shares, dtype=float)
    raw = raw / raw.sum() * 100
    out = np.floor(raw).astype(int)
    for i in np.argsort(-(raw - out))[: 100 - out.sum()]:
        out[i] += 1
    return [int(x) for x in out]


STAR_TYPES = {"M": ("red dwarfs", "#ff7b4a", 3.0), "K": ("orange", "#ffab5e", 4.0), "G": ("like the Sun", "#ffe9a0", 5.0),
              "F": ("yellow-white", "#fff7e0", 5.6), "A": ("white", "#e8eeff", 6.0), "O/B": ("blue-white", "#9db4ff", 6.5)}


def s19():
    n = 19
    f = Facts("BF19_red_dwarfs", n)
    k = K("K19_star_types", n)
    groups = []
    for _, r in k.iterrows():
        if int(r["out_of_100"]) == 0:
            continue
        name, col, size = STAR_TYPES[r["type"]]
        groups.append(dict(n=int(r["out_of_100"]), color=col, size=size, hide=r["type"] == "M",
                           text=f"{int(r['out_of_100'])} {name}\n(type {r['type']})"))
    crowd = dict(crowds=[dict(x0=0.04, w=0.62, title="100 main-band stars near the Sun", groups=groups, sun=True)],
                 tSort=9, hideUntil=4.5,
                 readout=[ro(0, "What your eyes see", "the bright stars stand out"),
                          ro(4.5, "With a telescope", "lots of faint red stars appear: the red dwarfs"),
                          ro(9, f"Out of 100: about {f.s('w_M')} red dwarfs", f"{f.s('w_K')} orange, {f.s('w_G')} like "
                             f"the Sun, {f.s('w_F')} yellow-white", "white and blue-white: less than 1 in 100")])
    return dict(type="crowd", dur=13.5, crowd=crowd,
                tag=f"{ILL}: the share of each kind is real (out of 100); the stars' places and sizes are drawn.",
                how="Press ▶ Play: 100 stars near the Sun, first the bright ones, then the faint red dwarfs.",
                steps=[[0, "100 stars near the Sun, drawn by kind. With your eyes you notice only the bright ones."],
                       [4.5, "With a telescope, the faint red dwarfs appear. They are everywhere."],
                       [9, f"Sorted into groups: about {f.s('w_M')} out of 100 are red dwarfs. In a noisy crowd you "
                           "only hear the few loud people."]])


def s20():
    n = 20
    f, z = Facts("BF20_galactic_centre_excess", n), Facts("AN20_sky_map", n)
    st = data("stars", ("l", "b", "ruwe"), n)
    rad = f.v("radius")
    ruwe_cut = Facts("BF18_star_families", n).v("ruwe_cut")
    lr, br = np.radians(st["l"].to_numpy()), np.radians(st["b"].to_numpy())

    def circle(l0):
        l0r = np.radians(l0)
        cosd = np.cos(br) * np.cos(lr - l0r)
        d = np.degrees(np.arccos(np.clip(cosd, -1, 1)))
        return d

    views = []
    for l0, key, col, title, bad in [(0, "gc", "#ff9f43", "Toward the middle", f.s("gc_ruwe_bad")),
                                     (180, "ac", "#46e0ff", "The opposite way", z.s("ac_ruwe_bad"))]:
        d = circle(l0)
        r_used = rad / 2 if abs((d <= rad / 2).sum() - f.v(key)) < abs((d <= rad).sum() - f.v(key)) else rad
        m = d <= r_used
        assert int(m.sum()) == int(f.v(key)), (key, int(m.sum()))
        dl = wrap180(st["l"].to_numpy()[m] - l0)
        db = st["b"].to_numpy()[m]
        order = np.random.default_rng(13).permutation(int(m.sum()))[: int(m.sum()) // 3]
        views.append(dict(dl=rl(dl[order], 2), db=rl(db[order], 2), bad=il((st["ruwe"].to_numpy()[m] > ruwe_cut)[order]),
                          count=int(m.sum()), colour=col, title=title, badText=f"badly measured: {bad}"))
    gal = dict(views=views, radius=r_used, tFill0=2.5, tFill1=9, tBad=11,
               readout=[ro(0, "Same-size circles on the sky", "pointing toward the middle of the Milky Way, and the "
                           "opposite way"),
                        ro(9.5, f"Toward the middle: {f.s('gc')}", f"The opposite way: {f.s('ac')}",
                           f"{f.s('gc')} ÷ {f.s('ac')} = {f.s('ratio')} times as many"),
                        ro(11, f"Badly measured (orange): {f.s('gc_ruwe_bad')} toward the middle",
                           f"(all stars: {f.s('all_ruwe_bad')})")])
    return dict(type="galaxy", dur=15, gal=gal,
                tag=f"{ILL}: the Milky Way drawing is not to scale; the stars in the two circles are real.",
                how="Press ▶ Play: two same-size circles on the sky fill up with the stars the file calls nearby.",
                steps=[[0, "We live inside the Milky Way, far from its middle. Point two same-size circles at the sky: "
                           "one toward the middle, one the opposite way."],
                       [2.5, "Each dot is a real star the file calls \"nearby\" (a third of them are drawn)."],
                       [9.5, f"Toward the middle: {f.s('gc')}. The opposite way: {f.s('ac')}. That's "
                             f"{f.s('ratio')} times as many."],
                       [11, f"But toward the middle, {f.s('gc_ruwe_bad')} are badly measured (orange): in a packed crowd "
                            "it's hard to judge distance, so far stars can look near."]])


def s21():
    n = 21
    f = Facts("BF21_star_clusters", n)
    lab = K("BF21_dbscan_labels", n)
    grp = K("BF21_groups", n)
    st = data("stars", ("source_id", "ra", "dec", "distance_pc", "pmra", "pmdec"), n)
    t = lab.merge(st, on="source_id", how="left")
    mem = t[t["label"] >= 0]
    assert len(mem) == int(f.v("in_groups")), len(mem)
    top = int(grp.sort_values("stars", ascending=False)["grp"].iloc[0])
    field = t[t["label"] < 0]
    field = field.iloc[pick(len(field), 2600, 14)]
    s = pd.concat([mem, field]).dropna(subset=["ra", "dec", "distance_pc", "pmra", "pmdec"])
    ra, de, d = np.radians(s["ra"].to_numpy()), np.radians(s["dec"].to_numpy()), s["distance_pc"].to_numpy()
    x0 = np.stack([d * np.cos(de) * np.cos(ra), d * np.cos(de) * np.sin(ra), d * np.sin(de)])
    east = np.stack([-np.sin(ra), np.cos(ra), np.zeros_like(ra)])
    north = np.stack([-np.sin(de) * np.cos(ra), -np.sin(de) * np.sin(ra), np.cos(de)])
    k = f.v("km_s_factor") / f.v("mas_per_arcsec") * PC_PER_MYR
    tau = 2.0  # million years of drifting (illustration)
    v = (s["pmra"].to_numpy() * k * d) * east + (s["pmdec"].to_numpy() * k * d) * north
    x1 = x0 + tau * v
    L = float(np.percentile(np.abs(x0), 98))
    g = np.where(s["label"] == top, 1, np.where(s["label"] >= 0, 2, 0))
    pm = g == 1
    pc = [float(x0[i][pm].mean() / L) for i in range(3)] + [float(x1[i][pm].mean() / L) for i in range(3)]
    cloud = dict(x0=rl(x0[0] / L, 3), y0=rl(x0[1] / L, 3), z0=rl(x0[2] / L, 3), x1=rl(x1[0] / L, 3),
                 y1=rl(x1[1] / L, 3), z1=rl(x1[2] / L, 3), g=il(g), pleiades=[round(p, 3) for p in pc],
                 az0=30, azSpeed=9, el=18, tGroups=4.5, tDrift0=9, tDrift1=14.5,
                 pleiadesText=f"Pleiades: {f.s('top_stars')} stars, {f.s('top_dist')} parsecs ({f.s('top_ly')} "
                              "light-years)",
                 readout=[ro(0, f"{f.s('sample')} nearby stars", "a sample is drawn, in 3D around the Sun"),
                          ro(4.5, f"{f.s('groups')} groups found by the computer", f"Orange: the Pleiades, "
                             f"{f.s('top_stars')} stars", "Blue: the other groups"),
                          ro(9, "Now let them drift (sped up)", "each group's stars travel together")])
    return dict(type="cloud", dur=16, cloud=cloud,
                tag=f"{ILL}: the stars' places and sideways speeds are real; the drift is sped up and the turning "
                    "view is drawn.",
                how="Press ▶ Play: real stars in 3D; the star groups light up and drift together.",
                steps=[[0, "Each dot is a real star near the Sun, in 3D, at its real place. The view turns slowly."],
                       [4.5, f"The computer found {f.s('groups')} groups whose stars are close together AND drift the "
                             "same way."],
                       [9, "Let time run forward: each group's stars stay together, like a school class walking "
                           "through a busy museum."]])


def s22():
    n = 22
    f = Facts("BF22_fast_movers", n)
    st = data("stars", ("radial_velocity",), n)["radial_velocity"].dropna().to_numpy()
    cut, esc = f.v("rv_cut"), f.v("escape_speed")
    fast = st[np.abs(st) > cut]
    assert len(fast) == int(f.v("rv_over_300")), len(fast)
    slow = st[np.abs(st) <= cut]
    slow = slow[pick(len(slow), 520, 15)]
    rv = np.concatenate([slow, fast])
    radial = dict(rv=rl(rv, 0), flag=il(np.abs(rv) > esc), cut=cut, vRef=esc, reach=0.55, tFast=4, tFlag=9,
                  readout=[ro(0, "Speeds toward or away from us", "each dot is a real star with a measured speed"),
                           ro(4, f"Faster than {f.s('rv_cut')} km every second: {f.s('rv_over_300')} stars",
                              f"{f.s('rv_over_300_pos')} of them moving away"),
                           ro(9, f"Faster than {f.s('escape_speed')} km every second (\"?\")",
                              "fast enough to leave the Milky Way: check the measurement first",
                              f"They look fainter: middle brightness number {f.s('rv_fast_g')}, against "
                              f"{f.s('rv_all_g')} for all")])
    return dict(type="radial", dur=14, radial=radial,
                tag=f"{ILL}: the speeds are real (sped up); the directions and distances in the drawing are made up.",
                how="Press ▶ Play: real stars rush toward us or away from us at their measured speeds.",
                steps=[[0, "We are in the middle. Each dot is a real star moving toward us (blue) or away (red), at "
                           "its real measured speed, sped up."],
                       [4, f"A few are really fast: more than {f.s('rv_cut')} km every second."],
                       [9, f"Some seem faster than {f.s('escape_speed')} km every second, fast enough to leave the "
                           "Milky Way. If a speed camera says a bicycle went as fast as a race car, you check the "
                           "camera first."]])


# ======================================================================================================= Part F
def s23():
    n = 23
    f = Facts("BF23_planet_batches", n)
    k = K("K23_planets_per_year", n)
    p = data("planets", ("ra", "dec", "disc_year", "discoverymethod", "disc_facility"), n).dropna(
        subset=["ra", "dec", "disc_year"])
    m = np.where(p["discoverymethod"] == "Transit", 0, np.where(p["discoverymethod"] == "Radial Velocity", 1, 2))
    y0, y1, tY, t0 = int(k["disc_year"].min()), int(k["disc_year"].max()), 0.36, 0.6
    u = np.random.default_rng(16).uniform(0, 0.9, len(p))
    kp = p[(p["disc_facility"] == "Kepler") & (p["discoverymethod"] == "Transit")]
    lines = [[f"{int(r['disc_year'])}", f"by transit: {n0(r['Transit'])}", f"by radial velocity: "
              f"{n0(r['Radial Velocity'])}", f"other ways: {n0(r['Other'])}"] for _, r in k.iterrows()]
    sky = dict(ra=rl(p["ra"], 2), dec=rl(p["dec"], 2), yr=il(p["disc_year"]), m=il(m), u=rl(u, 3), y0=y0, y1=y1,
               tYear=tY, t0=t0, years=il(k["disc_year"]), lines=lines,
               colors=["#46e0ff", "#ff7bd5", "#c9d3ea"], legend=["● found by transit", "● by radial velocity",
                                                                 "● other ways"],
               kepler=[float(kp["ra"].median()), float(kp["dec"].median())],
               keplerText="one telescope's patch of sky (Kepler)", tKepler=t0 + (int(f.v("y_2014")) - y0) * tY,
               final=[f"{f.s('rows')} planets; {f.s('transit_all')} found by transit",
                      f"By transit: {f.s('tr_2013')} in {f.s('y_2013')}, {f.s('tr_2014')} in {f.s('y_2014')}, "
                      f"{f.s('tr_2015')} in {f.s('y_2015')}, {f.s('tr_2016')} in {f.s('y_2016')}",
                      f"Busiest: {f.s('busiest_year')}, {f.s('busiest_n')} planets"])
    end = t0 + (y1 - y0 + 1) * tY
    return dict(type="sky", dur=round(end + 2.2, 2), sky=sky,
                tag=f"{ILL}: the whole sky is flattened like a world map; each dot is a real planet's star at its real "
                    "place.",
                how="Press ▶ Play: year by year, planets light up on the sky in the year they were announced.",
                steps=[[0, "The whole sky, flattened like a world map. Each dot is a planet's star, lighting up in the "
                           "year the planet was announced."],
                       [t0 + (int(f.v("y_2014")) - y0) * tY, f"{f.s('y_2014')} and {f.s('y_2016')}: huge batches at once, mostly "
                                               "from one patch of sky watched by one telescope (Kepler)."],
                       [end, "Like a teacher handing back all the tests on one day: the work was spread out, but the "
                             "news came at once."]])


def s24():
    n = 24
    f = Facts("BF24_hot_neptune_desert", n)
    p = data("planets", ("pl_orbper", "pl_rade"), n).dropna()
    p = p[(p["pl_orbper"] > 0) & (p["pl_orbper"] <= f.v("p2"))]
    lo, hi, jup = f.v("nep_lo"), f.v("nep_hi"), f.v("jup_size")
    c = np.select([p["pl_rade"] < lo, p["pl_rade"] <= hi, p["pl_rade"] <= jup], [0, 1, 2], 3)
    rs = np.random.default_rng(17)
    keep = []
    for cls, k in [(0, 380), (1, 10 ** 6), (2, 90), (3, 380)]:
        ii = np.flatnonzero(c == cls)
        keep.append(rs.choice(ii, min(k, len(ii)), replace=False))
    ii = np.sort(np.concatenate(keep))
    p, c = p.iloc[ii], c[ii]
    sys = dict(v=rl(p["pl_orbper"], 3), rade=rl(p["pl_rade"], 2), c=il(c), vmax=f.v("p2"), pow=2 / 3, speed=0.5,
               sizeK=1.1, starColour="#ffd27d", starR=9,
               classes=[dict(name=f"small (under {f.s('nep_lo')} Earths wide)", color="#a7b0c0"),
                        dict(name=f"Neptune-size ({f.s('nep_lo')} to {f.s('nep_hi')} Earths)", color="#46e0ff"),
                        dict(name="in between", color="#d8cfc0"),
                        dict(name=f"hot Jupiters (over {f.s('jup_size')} Earths)", color="#ff9f43")],
               rings=[dict(v=f.v("p1"), text=f"{f.s('p1')}-day year", ang=62, color="#ffd166", at=0),
                      dict(v=f.v("p2"), text=f"{f.s('p2')}-day year", ang=62, color="#9fb3d8", at=0)],
               zones=[dict(v0=0.05, v1=f.v("p1"), color="#ff9f43", alpha=0.1, at=6)],
               focus=[dict(at=6, cls=[1]), dict(at=11, cls=[0, 1, 2, 3])],
               readout=[ro(0, f"Planets with a year shorter than {f.s('p2')} days",
                           "all drawn around one star; far = longer year"),
                        ro(6, f"Only the Neptune-size planets ({f.s('nep_lo')} to {f.s('nep_hi')} Earths)",
                           f"{f.s('nep_3_10')} with a year of {f.s('p1')} to {f.s('p2')} days",
                           f"only {f.s('nep_lt3')} with a year shorter than {f.s('p1')} days"),
                        ro(11, f"Hot Jupiters (over {f.s('jup_size')} Earths): {f.s('jup8_lt10')}",
                           "close to the star the giants survive; Neptunes are rare")])
    return dict(type="system", dur=14, sys=sys,
                tag=f"{ILL}: every planet is drawn around one shared star; each distance comes from the planet's real "
                    "year and each size from its real width (enlarged).",
                how="Press ▶ Play: real short-year planets circle a star; then only the Neptune-size ones are shown.",
                steps=[[0, "Real planets with very short years, all drawn around one star. A shorter year means closer "
                           "to the star."],
                       [6, f"Now only the Neptune-size planets: inside the {f.s('p1')}-day ring there are hardly any. "
                           "That's the \"desert\"."],
                       [11, "Hot Jupiters are common there. Like snowballs near a campfire: the medium ones melt away, "
                            "big blocks of ice last."]])


def s25():
    n = 25
    f = Facts("BF25_radius_valley", n)
    p = data("planets", ("pl_orbper", "pl_rade"), n).dropna()
    p = p[(p["pl_orbper"] < f.v("p_cut")) & (p["pl_rade"] >= f.v("size_lo")) & (p["pl_rade"] <= f.v("size_hi"))]
    assert len(p) == int(f.v("rows")), len(p)
    p = p.iloc[pick(len(p), 1500, 18)]
    vlo, vhi = f.v("valley_lo"), f.v("valley_hi")
    c = np.select([p["pl_rade"] < vlo, p["pl_rade"] <= vhi], [0, 1], 2)
    sys = dict(v=rl(p["pl_orbper"], 2), rade=rl(p["pl_rade"], 2), c=il(c), vmax=f.v("p_cut"), pow=1 / 3, speed=1.6,
               sizeK=1.5, starColour="#ffd27d", starR=9,
               classes=[dict(name=f"rocky size (under {f.s('valley_lo')} Earths)", color="#d0a37a"),
                        dict(name=f"in the gap ({f.s('valley_lo')} to {f.s('valley_hi')})", color="#ffffff"),
                        dict(name=f"gassy size (over {f.s('valley_hi')} Earths)", color="#5b9cff")],
               focus=[dict(at=6, cls=[1]), dict(at=10, cls=[0, 1, 2])],
               inset=dict(at=10, left="rocky: gas blown away", right="gassy: kept its gas", note=ILL),
               readout=[ro(0, f"Planets with a year shorter than {f.s('p_cut')} days",
                           f"{f.s('size_lo')} to {f.s('size_hi')} Earths wide: {f.s('rows')}"),
                        ro(6, f"The dip: {f.s('valley_lo')} to {f.s('valley_hi')} Earths, only {f.s('valley_n')}",
                           f"Smaller hump: {f.s('peak1_lo')} to {f.s('peak1_hi')} Earths, {f.s('peak1_n')}",
                           f"Bigger hump: {f.s('peak2_lo')} to {f.s('peak2_hi')} Earths, {f.s('peak2_n')}")])
    return dict(type="system", dur=14, sys=sys,
                tag=f"{ILL}: every planet is drawn around one shared star, at a distance from its real year and a size "
                    "from its real width (enlarged).",
                how="Press ▶ Play: small real planets circle a star; then only the ones in the size gap are shown.",
                steps=[[0, "Real small planets, all drawn around one star. Brown: rocky size. Blue: gassy size."],
                       [6, f"Show only the in-between ones, {f.s('valley_lo')} to {f.s('valley_hi')} Earths wide: "
                           "there are fewer."],
                       [10, "Near their star, small planets lose their gas and end up rocky; bigger ones keep it. Like "
                            "a slide: you are at the bottom or still at the top."]])


def s26():
    n = 26
    f = Facts("BF26_sun_like_hosts", n)
    k = K("K26_host_stars", n)
    keys = {"O/B": "OB", "A": "A", "F": "F", "G": "G", "K": "K", "M": "M"}
    order = ["M", "K", "G", "F", "A", "O/B"]
    k = k.set_index("type").loc[order]
    all100, host100 = _hundred(k["pct_all_nearby_stars"]), _hundred(k["pct_planet_hosts"])

    def groups(counts, prefix):
        out = []
        for ty, c in zip(order, counts):
            if c == 0:
                continue
            name, col, size = STAR_TYPES[ty]
            out.append(dict(n=c, color=col, size=size, text=f"{f.s(prefix + keys[ty])}\n{name}"))
        return out

    crowd = dict(crowds=[dict(x0=0.03, w=0.45, title="100 ordinary stars near the Sun",
                              groups=groups(all100, "gaia_"), stagger=True),
                         dict(x0=0.52, w=0.45, title="100 stars with planets found", groups=groups(host100, "host_"),
                              planets=True, stagger=True)],
                 tSort=4,
                 readout=[ro(0, "Two crowds of 100 stars", "left: ordinary stars; right: planet hosts")])
    return dict(type="crowd", dur=13, crowd=crowd,
                tag=f"{ILL}: the share of each star type is real (out of 100); places and sizes are drawn.",
                how="Press ▶ Play: 100 ordinary stars and 100 planet hosts sort themselves by type.",
                steps=[[0, "Left: 100 ordinary stars near the Sun. Right: 100 stars where planets were found (each "
                           "with a tiny planet)."],
                       [4, "Sort them by type."],
                       [7.5, f"Sun-like stars (yellow) are only {f.s('gaia_G')} of ordinary stars, but {f.s('host_G')} of "
                             "planet hosts. Like looking for your keys only under the streetlight."]])


def s27():
    n = 27
    f = Facts("BF27_metal_rich_giants", n)
    k = K("K27_giant_share", n)
    lst = []
    for i, (_, r) in enumerate(k.iterrows(), start=1):
        g = int(round(r["pct_giants"] / 10))
        gi = sorted({int(round(x)) for x in np.linspace(1, 9, g)}) if g > 1 else ([5] if g == 1 else [])
        lst.append(dict(at=0.5 + 1.6 * (i - 1), metal=[4, 10, 18, 30][i - 1], giants=gi, top=r["label"],
                        mid=f"{f.s(f'b{i}_pct')} giants",
                        bottom=f"{f.s(f'b{i}_giants')} of {f.s(f'b{i}_n')} planets"))
    systems = dict(list=lst, arrow="less metal in the star   →   more metal",
                   readout=[ro(0, f"Giant planet: heavier than {f.s('mass_cut')} Earths or wider than "
                               f"{f.s('size_cut')} Earths"),
                            ro(7, f"Most metal: {f.s('b4_giants')} of {f.s('b4_n')} = {f.s('b4_pct')} giants",
                               f"Least metal: {f.s('b1_giants')} of {f.s('b1_n')} = {f.s('b1_pct')}")])
    return dict(type="systems", dur=12.5, systems=systems,
                tag=f"{ILL}: each drawing shows the real share of giants, rounded to tenths; the planets themselves "
                    "are drawn.",
                how="Press ▶ Play: four kinds of stars, from little metal to lots, with their share of giant planets.",
                steps=[[0, "Four groups of stars, from little metal (left) to lots of metal (right). In each drawing, "
                           "the big striped planets are giants, in the real share."],
                       [5.3, f"Stars with the most metal: {f.s('b4_pct')} of their planets are giants."],
                       [8, "Like Lego: more pieces in the box, bigger towers."]])


def s28():
    n = 28
    f = Facts("BF28_just_right_zone", n)
    p = K("BF28_planet_list", n).sort_values("sy_dist").reset_index(drop=True)
    assert len(p) == int(f.v("n"))
    d = 1 / np.sqrt(p["pl_insol"].to_numpy())
    c = np.where(p["discoverymethod"] == "Radial Velocity", 0, np.where(p["discoverymethod"] == "Transit", 1, 2))
    lo, hi = 1 / np.sqrt(f.v("insol_hi")), 1 / np.sqrt(f.v("insol_lo"))
    top = int(np.flatnonzero(p["pl_name"] == f.s("top_name"))[0])
    sys = dict(v=rl(d, 3), rade=rl(p["pl_rade"], 2), c=il(c), vmax=hi * 1.15, pow=1, speed=0.35, periodOf="d",
               sizeK=3.0, starColour="#ffd27d", starR=10, t0=rl(1.5 + 0.2 * np.arange(len(p)), 2),
               classes=[dict(name="found by radial velocity", color="#ff7bd5"),
                        dict(name="found by transit", color="#46e0ff"), dict(name="other", color="#c9d3ea")],
               zones=[dict(v0=0.05, v1=lo, color="#ff6a3d", alpha=0.13, at=0),
                      dict(v0=lo, v1=hi, color="#4dff9a", alpha=0.2, at=0),
                      dict(v0=hi, v1=hi * 1.15, color="#5b9cff", alpha=0.12, at=0)],
               labels=[dict(i=top, at=10.6, text=f"{f.s('top_name')}: {f.s('top_ly')} light-years away")],
               earth="Earth's spot (for comparison)",
               readout=[ro(0, "Starlight on each planet, compared with Earth's",
                           f"green zone, just right: {f.s('insol_lo')} to {f.s('insol_hi')} times Earth's"),
                        ro(10.6, f"{f.s('n')} Earth-size planets in the zone",
                           f"{f.s('n_rv')} found by radial velocity, {f.s('n_transit')} by transit",
                           f"closest: {f.s('top_name')}, {f.s('top_pc')} parsecs ({f.s('top_ly')} light-years)")])
    return dict(type="system", dur=14, sys=sys,
                tag=f"{ILL}: every planet is drawn around one shared star, where it would get its real starlight; "
                    "sizes are enlarged.",
                how="Press ▶ Play: Earth-size planets appear in the just-right zone, from the closest to us to the "
                    "farthest.",
                steps=[[0, "Each planet sits where it would get its real starlight. Green ring: not too hot, not too "
                           "cold."],
                       [1.5, "The planets appear from the closest to us to the farthest."],
                       [10.6, f"The closest: {f.s('top_name')}, only {f.s('top_ly')} light-years away. Like Goldilocks' "
                              "porridge: not too hot, not too cold, just right."]])


# ======================================================================================================= Part G
def craters(cols, n):
    return data("craters", tuple(cols), n)


def moon_globes(lon_a, lon_b, dur, lat=0.0):
    return [dict(cx=0.27, cy=0.58, wf=0.21, hf=0.33, rot=[[0, lon_a - 22, lat], [dur, lon_a + 22, lat]]),
            dict(cx=0.71, cy=0.58, wf=0.21, hf=0.33, rot=[[0, lon_b - 22, lat], [dur, lon_b + 22, lat]])]


def s29():
    n = 29
    f = Facts("BF29_craters_draw_seas", n)
    c = craters(["lat", "lon_east", "diameter_km"], n)
    c = c[c["diameter_km"] >= f.v("d5")]
    assert len(c) == int(f.v("all_5")), len(c)
    c = c.iloc[pick(len(c), 14000, 19)]
    t0 = np.random.default_rng(20).uniform(0.8, 8.5, len(c))
    g = moon_globes(0, 180, 14)
    g[0].update(title="Near side (always faces Earth)", under=[dict(at=9, text=f"Near side: {f.s('near_5')}")])
    g[1].update(title="Far side", under=[dict(at=9, text=f"Far side: {f.s('far_5')}")])
    globe = dict(body="moon", globes=g,
                 pts=dict(lat=rl(c["lat"], 2), lon=rl(wrap180(c["lon_east"]), 2), t0=rl(t0, 2),
                          colors=["#ece6d6"], size=1.4),
                 readout=[ro(0, f"Moon craters {f.s('d5')} km and wider", "each dot is a real crater"),
                          ro(9, f"Far side {f.s('far_5')}, near side {f.s('near_5')}",
                             f"{f.s('far_5')} ÷ {f.s('near_5')} = {f.s('ratio_5')} times as many")])
    return dict(type="globe", dur=14, globe=globe,
                tag=f"{ILL}: the craters' places are real; the turning is drawn.",
                how="Press ▶ Play: real craters appear on both sides of the Moon, and the dark seas show up.",
                steps=[[0, f"Two views of the Moon: the side that always faces Earth, and the far side. Each dot is a "
                           f"real crater {f.s('d5')} km or wider."],
                       [9, "The near side has big dark patches with few craters: the Moon's \"seas\"."],
                       [11.5, "Long ago, lava flooded the near side and filled in its old craters, like a thick coat of "
                              "paint over the dents of a car."]])


def s30():
    n = 30
    f = Facts("BF30_size_rule", n)
    c = craters(["lat", "lon_east", "diameter_km"], n)
    d10 = c[c["diameter_km"] >= f.v("d10")]
    assert len(d10) == int(f.v("n_ge_10"))
    dots = d10.iloc[pick(len(d10), 8000, 21)]
    t0 = np.random.default_rng(22).uniform(0.5, 4, len(dots))
    rings = []
    r100 = c[c["diameter_km"] >= f.v("d100")].sort_values("diameter_km")
    assert len(r100) == int(f.v("n_ge_100"))
    for i, (_, r) in enumerate(r100.iterrows()):
        giant = r["diameter_km"] >= f.v("d1000")
        la, lo = circle_on_sphere(r["lat"], float(wrap180(r["lon_east"])),
                                  np.degrees(r["diameter_km"] / 2 / MOON_KM), 72 if giant else 24)
        rings.append(dict(lat=la, lon=lo, at=(8.5 if giant else 4.5 + 2.5 * i / len(r100)),
                          color="#ffd166" if giant else "#7fe3ff", w=2.6 if giant else 1.2))
    big = r100.iloc[-1]
    blon, blat = float(wrap180(big["lon_east"])), float(big["lat"])
    globe = dict(body="moon", globes=[dict(cx=0.38, cy=0.55, wf=0.3, hf=0.41,
                                           rot=[[0, 0, 0], [8, 140, -15], [12.5, blon, max(-45.0, blat)],
                                                [15, blon + 15, max(-45.0, blat)]])],
                 pts=dict(lat=rl(dots["lat"], 2), lon=rl(wrap180(dots["lon_east"]), 2), t0=rl(t0, 2),
                          colors=["#cfc9bb"], size=1.3),
                 rings=rings,
                 readout=[ro(0, f"At least {f.s('d10')} km wide: {f.s('n_ge_10')} craters (dots)"),
                          ro(4.5, f"At least {f.s('d100')} km wide: {f.s('n_ge_100')} (blue rings)"),
                          ro(8.5, f"At least {f.s('d1000')} km wide: only {f.s('n_ge_1000')} (yellow)",
                             f"Biggest: {f.s('max_d')} km"),
                          ro(11.5, "Ten times wider, about 50 to 100 times rarer",
                             f"{f.s('n_ge_1')} ÷ {f.s('n_ge_10')} = {f.s('r_1_10')}; {f.s('n_ge_10')} ÷ "
                             f"{f.s('n_ge_100')} = {f.s('r_10_100')}; {f.s('n_ge_100')} ÷ {f.s('n_ge_1000')} = "
                             f"{f.s('r_100_1000')}")],
                 roW=0.4)
    return dict(type="globe", dur=15, globe=globe,
                tag=f"{ILL}: the turning is drawn; the craters' places and sizes are real.",
                how="Press ▶ Play: the Moon turns, showing many small craters, fewer big ones, and three giants.",
                steps=[[0, f"Each dot is a real crater at least {f.s('d10')} km wide: there are lots."],
                       [4.5, f"Blue rings: craters at least {f.s('d100')} km wide, drawn at their true size. Far fewer."],
                       [8.5, f"Yellow: at least {f.s('d1000')} km wide. Only {f.s('n_ge_1000')}."],
                       [11.5, "Like rain: lots of tiny drops, fewer big drops, and once in a while a giant hailstone."]])


def s31():
    n = 31
    f = Facts("BF31_stretched_craters", n)
    c = craters(["lat", "lon_east", "diameter_km", "ellipse_major_km", "ellipse_minor_km", "ellipse_angle_deg"], n)
    c = c[c["diameter_km"] >= f.v("d_cut")].dropna()
    ratio = c["ellipse_major_km"] / c["ellipse_minor_km"]
    s = c[ratio > f.v("ratio_cut")]
    assert len(s) == int(f.v("n_stretched")), len(s)
    ang = s["ellipse_angle_deg"].to_numpy() % 180
    main = (ang >= f.v("a60")) & (ang < f.v("a105"))
    bearing = 90 - ang
    lon = wrap180(s["lon_east"].to_numpy())
    la1, lo1 = destination(s["lat"], lon, np.full(len(s), 1.1), bearing)
    la0, lo0 = destination(s["lat"], lon, np.full(len(s), 1.1), bearing + 180)
    dots = c.iloc[pick(len(c), 7000, 23)]
    globe = dict(body="moon", globes=[dict(cx=0.36, cy=0.55, wf=0.3, hf=0.41, rot=[[0, -40, 10], [15, 40, 10]])],
                 pts=dict(lat=rl(dots["lat"], 2), lon=rl(wrap180(dots["lon_east"]), 2), colors=["#8d8a83"], size=1.2),
                 segs=dict(lat0=rl(la0, 2), lon0=rl(lo0, 2), lat1=rl(la1, 2), lon1=rl(lo1, 2), c=il(main),
                           t0=rl(np.random.default_rng(24).uniform(4.5, 8, len(s)), 2),
                           colors=["#7fe3ff", "#ffb347"], colAt=[4.5, 4.5], w=1.6),
                 compass=dict(at=9, x=0.83, y=0.6, a0=f.v("a60"), a1=f.v("a105"),
                              text=f"{f.s('share_60_105')} lean this way"),
                 readout=[ro(0, "Most craters are nearly round",
                             f"middle stretch: {f.s('median_ratio')}, only {f.s('median_pct_longer')} longer than wide"),
                          ro(4.5, f"Stretched (more than {f.s('ratio_cut')}): {f.s('n_stretched')} craters",
                             f"{f.s('pct_over_1_5')} of craters; lines point along the long side"),
                          ro(9, f"{f.s('share_60_105')} lean between {f.s('a60')} and {f.s('a105')} degrees (orange)",
                             f"with no favourite direction it would be {f.s('even_share')}")],
                 roW=0.4)
    return dict(type="globe", dur=15, globe=globe,
                tag=f"{ILL}: the craters' places and directions are real; the line lengths and the turning are drawn.",
                how="Press ▶ Play: the stretched craters appear as lines; many lean the same way.",
                steps=[[0, f"Each grey dot is a real crater {f.s('d_cut')} km or wider. Almost all are nearly round."],
                       [4.5, f"Lines show the {f.s('n_stretched')} stretched craters, pointing along their long side."],
                       [9, f"Many lean the same way (orange): {f.s('share_60_105')}, where an even spread would give "
                           f"{f.s('even_share')}."],
                       [12, "Drop a ball of clay straight down: a round dent. Throw it at a low angle: a long dent."]])


def s32():
    n = 32
    f = Facts("BF32_polar_craters", n)
    b = K("BF32_bands", n)
    c = craters(["lat", "lon_east"], n)
    c = c.iloc[pick(len(c), 15000, 25)]
    dens = b["density_vs_equator"].to_numpy()
    edges = np.linspace(dens.min(), dens.max() + 1e-9, 6)
    lvl = np.clip(np.digitize(dens, edges) - 1, 0, 4)
    band_of = np.clip(np.searchsorted(b["lat_from"].to_numpy(), c["lat"].to_numpy(), side="right") - 1, 0, len(b) - 1)
    ramp = ["#5d6b8a", "#8c95a8", "#c6b98f", "#f2c55c", "#ffd166"]
    globe = dict(body="moon", globes=[dict(cx=0.37, cy=0.56, wf=0.3, hf=0.41,
                                           rot=[[0, 0, 0], [5, 0, 0], [8.5, 30, 55], [15, 75, 55]])],
                 pts=dict(lat=rl(c["lat"], 2), lon=rl(wrap180(c["lon_east"]), 2), c=il(lvl[band_of]), colors=ramp,
                          size=1.3),
                 circles=[dict(lat=f.v("lat_80"), color="#ffd166", at=5)],
                 readout=[ro(0, "Moon craters, coloured by how crowded their band is",
                             "grey: fewer per square km; yellow: more"),
                          ro(5, f"North pole band ({f.s('lat_80')} to {f.s('lat_90')} N): {f.s('ratio_north')} times "
                             "as many per square km as the equator", f"south pole band: {f.s('ratio_south')} times"),
                          ro(10, f"{f.s('cnt_80_90N')} craters at {f.s('lat_80')} to {f.s('lat_90')} N",
                             f"{f.s('cnt_0_10N')} at {f.s('lat_0')} to {f.s('band_w')} N, a band {f.s('area_ratio')} times bigger")],
                 roW=0.4)
    return dict(type="globe", dur=15, globe=globe,
                tag=f"{ILL}: the craters are real (a sample); the turning is drawn.",
                how="Press ▶ Play: the Moon tips to show its north pole, where craters are the most crowded.",
                steps=[[0, "Each dot is a real crater. Its colour shows how crowded its band of latitude is."],
                       [5, "Tip the Moon to see the north pole: the polar band (dashed ring) is the most crowded."],
                       [10, "Near the poles the sunlight is always low, so long shadows show every dent, like "
                            "footprints in snow at sunset."]])


SCENES = {i: globals()[f"s{i:02d}"] for i in range(1, 33)}
KIND_3D = {21, 29, 30, 31, 32}

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>__TITLE__</title>
<style>
  :root { color-scheme: dark; }
  html, body { margin: 0; background: #0b1020; color: #e8ecf5;
    font-family: system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
  .wrap { max-width: 1180px; margin: 0 auto; padding: 10px 12px 14px; }
  .bar { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; margin: 0 0 8px; }
  .bar h1 { font-size: 16.5px; line-height: 1.3; margin: 0 6px 0 0; font-weight: 600; flex: 1 1 260px; }
  button { font: inherit; font-size: 15px; padding: 7px 16px; border-radius: 9px; border: 1px solid #3a4770;
    background: #1d2747; color: #fff; cursor: pointer; }
  button:disabled { opacity: .5; cursor: default; }
  #play { background: #2f6fed; border-color: #2f6fed; font-weight: 600; min-width: 132px; }
  canvas { width: 100%; height: 440px; display: block; border-radius: 12px; background: #03050d; }
  #live { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; min-height: 56px; }
  #live .blk { background: #141b30; border: 1px solid #2a3452; border-radius: 9px; padding: 6px 12px;
    font-size: 14px; line-height: 1.4; max-width: 100%; }
  #live .hd { font-weight: 600; color: #ffffff; }
  #live .ln { color: #d5dcec; }
  #note { margin: 6px 2px 0; font-size: 13px; font-style: italic; color: #f0c674; }
  #step { margin: 8px 2px 0; font-size: 15px; line-height: 1.45; min-height: 2.9em; color: #f3f5fb; }
  .keys { margin-top: 6px; background: #141b30; border: 1px solid #2a3452; border-radius: 10px;
    padding: 8px 14px 6px; font-size: 14.5px; line-height: 1.45; }
  .keys b { color: #ffd166; }
  .keys ul { margin: 4px 0; padding-left: 20px; }
  .keys li { transition: opacity .35s; }
  .keys li.hide { opacity: 0; }
</style>
</head>
<body>
<div class="wrap">
  <div class="bar"><h1>__TITLE__</h1>
    <button id="play" type="button">▶ Play</button><button id="pause" type="button">⏸ Pause</button></div>
  <canvas id="sky" role="img" aria-label="__ARIA__"></canvas>
  <div id="note"></div>
  <div id="live" aria-live="polite"></div>
  <div id="step"></div>
  <div class="keys"><b>Key numbers</b><ul id="keys"></ul></div>
</div>
<script>window.SCENE = __SCENE__;</script>
<script>
__ENGINE__
</script>
</body>
</html>
"""


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def build(n: int) -> dict:
    sc = SCENES[n]()
    meta = OLD_INDEX[n]
    title = f"Finding {n}: {meta['title']}"
    keys = KEYS[str(n)]
    d = float(sc["dur"])
    sc.update(n=n, keys=keys, keyAt=[round(d * (0.45 + 0.5 * i / max(1, len(keys) - 1)), 2) for i in range(len(keys))],
              intro="This is the finished picture. Press ▶ Play to watch it happen, step by step.")
    sc.setdefault("tag", ILL)
    if sc["tag"].startswith(ILL + ": "):                 # short label on the picture, the details under it
        rest = sc["tag"][len(ILL) + 2:]
        sc["tag"], sc["tagNote"] = ILL, rest[:1].upper() + rest[1:]
    blob = json.dumps(sc, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = (TEMPLATE.replace("__TITLE__", esc(title)).replace("__ARIA__", esc(sc["how"]))
            .replace("__SCENE__", blob).replace("__ENGINE__", ENGINE.read_text()))
    path = OUT / f"F{n:02d}_{meta['slug']}.html"
    path.write_text(html)
    return dict(n=n, slug=meta["slug"], title=meta["title"], part=meta["part"],
                kind="3D" if n in KIND_3D else "2D", style="space sketch (2D canvas, no WebGL)",
                html=str(path.relative_to(ROOT)), seconds=round(d, 1), how=sc["how"],
                illustration=True, numbers=sorted(USED.get(n, set())) + ["numbers/AN_keys.json"],
                height=int(735 + sum(23 * (1 + len(k) // 100) for k in keys)),
                kb=round(path.stat().st_size / 1024))


TOKEN = re.compile(r"(?<![\w.:])[+-]?\d[\d,]*(?:\.\d+)?(?![\w:])")


@lru_cache(None)
def allowed() -> frozenset:
    """Every number written in numbers/ (as shown, or rounded), the key-number lines, and years."""
    ok = set(str(y) for y in range(1900, 2201))
    for p in NUM.glob("*.csv"):
        if p.stat().st_size > 2_000_000:
            continue
        df = pd.read_csv(p, dtype=str)
        for col in df.columns:
            for v in df[col].dropna().astype(str):
                ok.update(t.lstrip("+") for t in TOKEN.findall(v))
                try:
                    x = float(v.replace(",", "").replace("%", ""))
                except ValueError:
                    continue
                for k in (0, 1, 2):
                    ok.add(f"{x:,.{k}f}")
                    ok.add(f"{x:.{k}f}")
    for lines in KEYS.values():
        for s in lines:
            ok.update(t.lstrip("+") for t in TOKEN.findall(s))
    return frozenset(ok)


def unknown_numbers(n: int) -> list[str]:
    """Number tokens in finding n's words that are not in numbers/ (data-row text such as times is skipped)."""
    meta = OLD_INDEX[n]
    html = (OUT / f"F{n:02d}_{meta['slug']}.html").read_text()
    sc = json.loads(re.search(r"window\.SCENE = (.*?);</script>", html, re.S).group(1).replace("<\\/", "</"))
    bad = []

    def walk(x, key=""):
        if key in ("when", "keys") or (key == "lines" and isinstance(x, list) and x and isinstance(x[0], list)
                                       and n == 17):
            return
        if isinstance(x, dict):
            for k, v in x.items():
                walk(v, k)
        elif isinstance(x, list):
            for v in x:
                walk(v, key)
        elif isinstance(x, str):
            for tok in TOKEN.findall(x):
                if tok.lstrip("+") not in allowed():
                    bad.append(f"{tok} in {x[:70]!r}")

    walk(sc)
    return bad


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", type=int, nargs="*")
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    idx_path = NUM / "AN_index.json"
    index = json.loads(idx_path.read_text()) if idx_path.exists() else {}
    if any("json" in v for v in index.values()):
        index = {}                     # the old chart-animation index is kept in old/animations_plotly/
    for n in args.only or range(1, 33):
        e = build(n)
        index[str(n)] = e
        print(f"F{n:02d} {e['kind']} {e['seconds']:5.1f}s {e['kb']:5d} KB  {e['html']}")
    index = {k: index[k] for k in sorted(index, key=int)}
    tmp = idx_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(index, indent=1, ensure_ascii=False) + "\n")
    tmp.replace(idx_path)
    print(f"{len(index)} animations in {idx_path.relative_to(ROOT)}")
    problems = {n: unknown_numbers(n) for n in (args.only or range(1, 33))}
    problems = {n: p for n, p in problems.items() if p}
    if problems:
        for n, p in problems.items():
            print(f"F{n:02d} numbers not found in numbers/: {p}")
    else:
        print("Number check: every number in the words is in numbers/ (or is a year).")


if __name__ == "__main__":
    main()
