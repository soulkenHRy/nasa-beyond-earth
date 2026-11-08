"""Words for part A: asteroids and comets (put together by notebooks/make_findings.py).

Every {placeholder} is filled from numbers/: inside MEET from numbers/BM_A_meet_asteroids.csv, inside finding n from
numbers/BFnn_*.csv ({M_key} = this part's MEET table, {F3_key} = finding 3's table, {S_key} = shared table).
The numbers and charts are made by notebooks/BF_A_asteroids.py. Style rules: notebooks/findings_text/STYLE.md.
"""
PART = "A"
NAME = "Asteroids and comets"
FILE = "jpl_small_bodies_asteroids_comets.csv"

MEET = {
    "title": "the asteroid and comet file",
    "what": "A giant list of every asteroid and comet whose path around the Sun is known. NASA's Jet Propulsion Laboratory "
            "(JPL) keeps it up to date.",
    "row": "One row is one object: one asteroid or one comet. Each column is one fact about it, like its name, its size, "
           "or how it travels around the Sun.",
    "size": "{rows_total} rows and {n_columns} columns. Reading one row every second, day and night, would take you about "
            "{read_days} days! Almost all of them ({asteroid_pct}) are asteroids: {asteroids} asteroids and only {comets} comets.",
    "story": "Where do the rocks of the Solar System live? How big are they? How fast do they spin? Could any of them come near "
             "Earth? One row tells you about one rock. Thousands of rows together show patterns that no single rock can show.",
    "example": "{ceres_name}",
    "columns": [
        ("name", "name", "the object's name, if it has one (most don't)", "words", "{ceres_name}"),
        ("kind", "kind", "`an` = asteroid with a number, `au` = asteroid without a number yet, `cn` or `cu` = comet",
         "a short code", "`{ceres_kind}`"),
        ("class", "neighbourhood", "the group its path belongs to: `MBA` = main asteroid belt, `TJN` = shares Jupiter's path, "
         "`TNO` = beyond Neptune, `APO`, `ATE` or `AMO` = comes near Earth", "a short code", "`{ceres_class}`"),
        ("a", "distance from the Sun", "its average distance from the Sun: halfway between its closest and farthest points",
         "Earth-Sun distances (one = as far as Earth)", "{ceres_a}"),
        ("q", "closest point", "the closest it ever gets to the Sun", "Earth-Sun distances", "{ceres_q}"),
        ("e", "stretch number", "how stretched its path is: zero = a circle, near one = a long, thin oval, one or more = not a "
         "closed loop at all", "a number", "{ceres_e}"),
        ("per_y", "year length", "how long one trip around the Sun takes", "Earth years", "{ceres_per}"),
        ("om, w, ma", "the three angles", "which way its path is turned, and where along the path it is right now", "degrees",
         "{ceres_om}, {ceres_w}, {ceres_ma}"),
        ("H", "brightness number", "how bright it would look from a set distance. Like a golf score, smaller wins: a smaller "
         "number means a bigger rock", "a number", "{ceres_H}"),
        ("diameter", "width", "how wide it is, where someone measured it", "km", "{ceres_d}"),
        ("albedo", "shininess", "how much sunlight its surface bounces back: zero = pitch black, one = all of it",
         "a number from zero to one", "{ceres_albedo}"),
        ("rot_per", "spin time", "how long one full spin takes", "hours", "{ceres_rot}"),
        ("neo", "near-Earth flag", "`Y` (yes) if its path comes near Earth's path, `N` (no) if not", "`Y` or `N`", "`{ceres_neo}`"),
        ("pha", "hazard flag", "`Y` (yes) if it is called \"potentially hazardous\": its path comes very close to Earth's path "
         "and it is big", "`Y` or `N`", "`{ceres_pha}`"),
        ("moid", "closest the paths get", "the smallest gap between its path and Earth's path (it's about the paths, not "
         "where the rock is today)", "Earth-Sun distances", "{ceres_moid}"),
        ("first_obs", "first sighting", "the date of the earliest sighting used to work out its path",
         "a date: year-month-day", "{ceres_first_obs}"),
    ],
    "walk": [
        "`name` is {ceres_name} and `kind` is `{ceres_kind}`: an asteroid with a number. Its number is {ceres_number}, "
        "because it was the first asteroid ever found.",
        "`a` is {ceres_a}: on average, Ceres is {ceres_a} times as far from the Sun as Earth is. Its closest point (`q`) is {ceres_q}.",
        "`e` is {ceres_e}. That's close to zero, so its path is almost a circle. `per_y` is {ceres_per}: one trip around the "
        "Sun takes {ceres_per} of our years.",
        "`diameter` is {ceres_d} km, and `H` is {ceres_H}: a very small brightness number, because Ceres is huge.",
        "`albedo` is {ceres_albedo}, so Ceres is dark, like a road. `rot_per` is {ceres_rot} hours, so it spins about "
        "{ceres_day_vs_earth} times in one of our {hours_per_day}-hour days.",
        "`neo` and `pha` are both `{ceres_neo}` (no). The closest its path gets to Earth's path (`moid`) is {ceres_moid} "
        "Earth-Sun distances: far away.",
        "`first_obs` is {ceres_first_obs}. Ceres was really found in {F4_ceres_found}, but the file lists the earliest "
        "sighting used for today's path, not the discovery day.",
        "Compare Apophis, a famous near-Earth asteroid: its `neo` is `{apophis_neo}` and its `pha` is `{apophis_pha}`. "
        "Its path comes within {apophis_moid_km} km of Earth's path.",
    ],
    "careful": "A blank cell means nobody has measured that fact yet. It does not mean zero! Only {diam_share} of the "
               "asteroids have a measured width, {albedo_share} a measured shininess, and {rot_share} a measured spin time. "
               "Some first-sighting dates are only partly known, like `{partial_example}` ({partial_dates} rows). "
               "Most findings leave comets out, because many comet paths are not closed loops.",
    "pictures": ["charts/K00A_paths_around_the_sun.png"],
    "picture_read": [
        "**Left picture:** we are looking down on the Solar System from above. The yellow dot is the Sun. The blue circle "
        "is Earth's path. The orange oval is a made-up asteroid's path.",
        "**Closest point (`q`):** {demo_q} Earth-Sun distances. **Farthest point:** {demo_Q}. **Distance from the Sun "
        "(`a`):** halfway between them, ({demo_q} + {demo_Q}) ÷ {demo_two} = {demo_a}.",
        "**moid:** the short orange bar is the smallest gap between the two paths: {demo_moid} here.",
        "**Right picture:** three paths with different stretch numbers (`e`). {e_demo1} is a circle, {e_demo2} is an egg "
        "shape, {e_demo3} is a long, thin oval.",
    ],
    "words": {
        "row": "one line across a table. Here, one row is one asteroid or comet.",
        "column": "one list going down a table. Each column holds one kind of fact, like the width.",
        "Y and N": "the file's short way of writing yes and no.",
        "JPL": "NASA's Jet Propulsion Laboratory in California. It keeps track of asteroids and comets.",
        "code": "a few letters that stand for something longer, like `MBA` for main belt asteroid.",
    },
}

GLOSSARY = [
    ("stretch number (e)", r"stretch number",
     "how stretched a path around the Sun is. Zero is a perfect circle; close to one is a long, thin oval; one or more "
     "means the path is not a closed loop, so the object flies off and never comes back. Scientists call it eccentricity."),
    ("brightness number (H)", r"brightness number",
     "how bright an asteroid would look from a set distance. Smaller means brighter, and brighter means bigger. "
     "Scientists call it absolute magnitude."),
    ("shininess (albedo)", r"shininess|shiny",
     "how much sunlight a surface bounces back, from zero (pitch black) to one (all of it). Coal is close to zero; fresh "
     "snow is close to one. Scientists call it albedo."),
    ("spin time", r"spin time", "how long one full turn takes (column `rot_per`), like Earth's day."),
    ("near-Earth", r"[Nn]ear-Earth", "an asteroid or comet whose path around the Sun comes close to Earth's path."),
    ("moid", r"\bmoid\b|closest the paths get|smallest gap",
     "the smallest gap between an asteroid's path and Earth's path. It is about the paths, not about where the rock is "
     "today. The letters stand for \"minimum orbit intersection distance\"."),
]

FINDINGS = [
    # ------------------------------------------------------------------------------------------------------------ 1
    {
        "n": 1,
        "title": "The asteroid belt has empty lanes",
        "question": "Are the rocks in the asteroid belt spread out evenly, or are there empty places?",
        "rows": "asteroids only (no comets), on closed loops, between {a_low} and {a_high} Earth-Sun distances from the "
                "Sun. That keeps {rows_kept} of the {rows_total} rows.",
        "rule": "kind in [an, au] and e < {e_cut} and {a_low} < a < {a_high}",
        "example": "Ceres",
        "columns": [
            ("kind", "asteroid or comet: we keep `an` and `au` (asteroids)", "a code", "`{M_ceres_kind}`"),
            ("e", "stretch number: we keep paths under {e_cut} (closed loops)", "a number", "{ceres_e}"),
            ("a", "distance from the Sun", "Earth-Sun distances", "{ceres_a}"),
            ("per_y", "year length: how long one trip around the Sun takes", "years", "{M_ceres_per}"),
        ],
        "math": [
            "We cut the distances into thin slices, each {slice_width} wide, and count the asteroids in every slice.",
            "We add up three boxes of four slices each. From {inside_lo} to {inside_hi}: {inside_count} asteroids. "
            "From {outside_lo} to {outside_hi}: {outside_count}.",
            "In between, more than {gap_lo} and less than {gap_hi}: only {gap_count}. {inside_count} ÷ {gap_count} = "
            "{ratio_inside}: the box just inside has about {ratio_inside} times as many rocks as the lane.",
            "A rock in the lane takes {file_per_y_at_2_5} years to go around the Sun (column `per_y`). Jupiter takes "
            "{jupiter_period} years. {jupiter_period} ÷ {file_per_y_at_2_5} = {period_ratio}: three rock trips for "
            "every one Jupiter trip.",
        ],
        "relationship": "rock goes around {period_ratio} times while Jupiter goes around once → Jupiter pulls at the same "
                        "spot again and again → rock pushed out → empty lane",
        "chart_read": [
            "**Across the bottom:** distance from the Sun, in Earth-Sun distances (column `a`). Left is closer to the Sun.",
            "**Up the side:** how many asteroids are in each thin slice.",
            "**The blue shape:** the tops of many thin bars, one bar for each slice.",
            "**The shaded boxes:** the three boxes from the math. The orange one is the lane.",
            "**Look for:** the deep, narrow dips. They are the empty lanes, and the arrows point at them.",
        ],
        "short": "Think of pushing a friend on a swing. If you push at the same moment every time, the swing goes higher and "
               "higher. Jupiter does that to a rock in the lane. It pulls at the same spot over and over, until the rock "
               "is pushed out of its path.",
        "data": "empty lanes at {dip1_a}, {dip2_a}, {dip3_a} and {dip4_a} Earth-Sun distances. Our code found them by "
                "looking for the emptiest slices.",
        "sci": "Jupiter's repeated pulls cleared these lanes. They are called Kirkwood gaps, after Daniel Kirkwood, the "
               "astronomer who noticed them.",
        "careful": "the file rounds distances to the nearest thousandth, so {on_edge_2_48} asteroids sit exactly on "
                   "{gap_lo}. Counting \"from {gap_lo}\" gives {gap_count_ge}, not {gap_count}. Open paths (stretch "
                   "number {e_cut} or more) are left out: their distance in the file is negative, which makes no sense.",
        "note": "the guide said the last lane is at {guide_dip4}; our data gives {dip4_a}.",
        "charts": ["charts/K01_empty_lanes.png"],
        "old_charts": ["charts/A05_a_histogram_1.7-5.5AU.png"],
        "words": {
            "asteroid belt": "the ring of rocks between Mars and Jupiter.",
            "Kirkwood gap": "an empty lane in the asteroid belt, cleared by Jupiter's pulls.",
            "closed loop": "a path that goes round and round the Sun. An open path swings past the Sun once and never "
                           "comes back.",
        },
    },
    # ------------------------------------------------------------------------------------------------------------ 2
    {
        "n": 2,
        "title": "Asteroids get darker the farther they are from the Sun",
        "question": "Are asteroids near the Sun the same colour as asteroids far away?",
        "rows": "asteroids on closed loops with a measured shininess, between {z1_lo} and {z4_hi} Earth-Sun distances "
                "from the Sun: {zone_rows} rows.",
        "rule": "kind in [an, au] and e < {F1_e_cut} and albedo is not blank and {z1_lo} <= a < {z4_hi}",
        "example": "Vesta",
        "columns": [
            ("a", "distance from the Sun", "Earth-Sun distances", "{vesta_a}"),
            ("albedo", "shininess: zero = pitch black, one = bounces back all the light", "a number", "{vesta_albedo}"),
        ],
        "math": [
            "We call an asteroid \"shiny\" if its shininess is more than {bright_cut}.",
            "Closest zone, {z1_lo} to {z1_hi}: {z1_bright} shiny out of {z1_n}. That is {z1_pct}, more than half.",
            "Next zones out: {z2_pct} ({z2_lo} to {z2_hi}), then {z3_pct} ({z3_lo} to {z3_hi}).",
            "Farthest zone, {z4_lo} to {z4_hi}: only {z4_bright} shiny out of {z4_n}, just {z4_pct}.",
            "Two examples: Vesta, at {vesta_a}, has a shininess of {vesta_albedo}. Hygiea, at {hygiea_a}, has only "
            "{hygiea_albedo}.",
        ],
        "relationship": "farther from the Sun → fewer shiny asteroids → darker rocks",
        "chart_read": [
            "**Left chart, across the bottom:** four zones of distance from the Sun. The closest zone is on the left.",
            "**Left chart, up the side:** out of every hundred asteroids in that zone, how many are shiny.",
            "**Right chart:** each dot is one slice of distance. It shows the middle shininess of the asteroids in that "
            "slice. Across the bottom is the distance from the Sun again.",
            "**Look for:** the bars getting shorter from left to right, and the very shiny bump near {spike_lo} on the "
            "right chart.",
        ],
        "short": "Picture a class photo where the front rows wear white shirts and the back rows wear black ones. Near the "
               "Sun, most rocks are light-coloured stone. Far away, most are as dark as charcoal.",
        "data": "the share of shiny asteroids drops from {z1_pct} to {z2_pct} to {z3_pct} to {z4_pct}. There is a very "
                "shiny bump at {spike_lo} to {spike_hi}.",
        "sci": "near the Sun, most asteroids are stony. Farther out, most are made of dark rock full of carbon, as dark "
               "as charcoal. The shiny bump is a family of rocks called the Hungarias.",
        "careful": "only {measured_share} of asteroids have a measured shininess, and they are mostly big ones. Small "
                   "asteroids might not follow the same pattern.",
        "note": "the guide said the bump's middle shininess is {guide_spike_median}; our data gives {spike_median} "
                "({spike_lo} to {spike_hi}, {spike_n} asteroids).",
        "charts": ["charts/K02_darker_farther_out.png"],
        "old_charts": ["charts/A10_albedo_by_distance.png"],
        "words": {
            "zone": "a range of distances that we compare with the other ranges.",
            "Hungaria family": "a group of very shiny asteroids at the inner edge of the asteroid belt.",
            "carbon": "the stuff that coal, charcoal and pencil lead are made of.",
        },
    },
    # ------------------------------------------------------------------------------------------------------------ 3
    {
        "n": 3,
        "title": "Big asteroids almost never spin faster than once every {limit_h} hours",
        "question": "How fast can an asteroid spin before it falls apart?",
        "rows": "asteroids with a measured spin time and a size: {rows_kept} rows. For {estimated} of them the size is a "
                "guess, worked out from the brightness number.",
        "rule": "kind in [an, au] and rot_per is not blank and (diameter or H is not blank)",
        "example": "Ceres",
        "columns": [
            ("rot_per", "spin time: how long one full spin takes", "hours", "{ceres_rot}"),
            ("diameter", "width, where someone measured it", "km", "{ceres_d}"),
            ("H", "brightness number: smaller = bigger. Used to guess the width when nobody measured it", "a number",
             "{ceres_H}"),
        ],
        "math": [
            "The speed limit: one spin every {limit_h} hours. That's {limit_min} minutes.",
            "Big asteroids (wider than {big_m} m): {big_n}. Only {big_fast} of them spin faster than the limit. "
            "{big_fast} ÷ {big_n} = {big_fast_pct}. So about {big_ok_pct} obey the limit.",
            "Small asteroids (narrower than {small_m} m): {small_n}. Of these, {small_fast} spin faster than the limit: "
            "{small_fast_pct}.",
            "The record holder, {record_name}, spins once every {record_hours} hours. {record_hours} × {S_sec_per_hour} "
            "= {record_seconds} seconds for one whole spin!",
        ],
        "relationship": "big rock → loose rubble held by weak gravity → can't spin faster than once every {limit_h} hours",
        "chart_read": [
            "**Top chart:** big asteroids (wider than {big_m} m). **Bottom chart:** small asteroids (narrower than {small_m} m).",
            "**Across the bottom:** spin time in hours (column `rot_per`). Left = fast spinners.",
            "**Up the side:** how many asteroids have that spin time.",
            "**The orange line:** the speed limit, one spin every {limit_h} hours.",
            "**Look for:** in the top chart, the bars jump up just right of the line, with only a few to its left. In "
            "the bottom chart, most small rocks are to its left.",
        ],
        "short": "Swing a bucket of sand around very fast, and the sand flies out. Big asteroids are piles of loose rubble, "
               "held together only by their own weak gravity. Spin one too fast and it would fly apart.",
        "data": "a sharp edge at {limit_h} hours for big asteroids. Small asteroids break it all the time.",
        "sci": "big asteroids are \"rubble piles\". Small ones can be single solid rocks, which can spin much faster "
               "without breaking.",
        "careful": "for {big_fast_est} of the {big_fast} big fast spinners, the width is only a guess from the brightness "
                   "number. We assumed a shininess of {albedo_guess}, so some may really be small. Guess (not checked): "
                   "some of the other {big_fast_meas} may have a wrongly measured spin time.",
        "note": None,
        "charts": ["charts/K03_spin_speed_limit.png"],
        "old_charts": ["charts/A11_size_vs_spin.png"],
        "words": {
            "rubble pile": "a loose heap of rocks held together only by gravity.",
        },
    },
    # ------------------------------------------------------------------------------------------------------------ 4
    {
        "n": 4,
        "title": "In {y_2025}, three times as many objects were seen for the first time as in a normal recent year",
        "question": "Do we find more space rocks every year? Did anything special happen in {y_2025}?",
        "rows": "every object in the file, sorted by the year of its first sighting. From {y_lo} to {y_hi}: "
                "{rows_1980_2026} rows.",
        "rule": "year = the part of first_obs before the first dash, and {y_lo} <= year <= {y_hi}",
        "example": "Ceres",
        "columns": [
            ("first_obs", "first sighting: the earliest sighting used to work out the path", "a date", "{ceres_first_obs}"),
            ("neo", "near-Earth flag: `Y` (yes) if its path comes near Earth's path", "`Y` or `N`", "`{M_ceres_neo}`"),
            ("H", "brightness number, used to guess how wide new near-Earth rocks are", "a number", "{F3_ceres_H}"),
        ],
        "math": [
            "From {y_2018} to {y_2024}, between {y2018_24_min} and {y2018_24_max} objects were seen for the first time "
            "each year. The average was {y2018_24_avg}.",
            "In {y_2025}: {y2025}. {y2025} ÷ {y2018_24_avg} = {ratio_2025_avg}, so three times a normal recent year.",
            "July {y_2025} alone had {july_2025}: that's {july_share} of the whole year.",
            "New near-Earth rocks: {neo_1995} in {y_1995}, but between {neo_2022_25_min} and {neo_2022_25_max} a year "
            "since {y_2022}.",
            "They got smaller, too. The middle width of new near-Earth rocks was about {neo_size_1995} m in {y_1995}, "
            "and about {neo_size_2026} m in {y_2026}.",
        ],
        "relationship": "better telescopes → more rocks found each year, and smaller ones",
        "chart_read": [
            "**Top chart, across the bottom:** the year of the first sighting (column `first_obs`). **Up the side:** how "
            "many objects were seen for the first time that year.",
            "**The orange bar:** {y_2025}. It is about three times as tall as the bars from {y_2018} to {y_2024}.",
            "**Bottom chart:** each dot is the middle width (in metres) of the near-Earth rocks first seen that year.",
            "**Look for:** the jump in {y_2025} on top, and the line sliding down on the bottom: we now find much "
            "smaller rocks.",
        ],
        "short": "It's like getting new glasses: suddenly you can read the tiny print. A big new telescope started work in "
               "{y_2025} and spotted rocks nobody could see before.",
        "data": "a big jump in {y_2025}, with {july_share} of it in July alone. It was the most first sightings in one "
                "year since {prev_bigger_year}.",
        "sci": "the Vera C. Rubin Observatory in Chile ran its first test sweeps of the sky in the summer of {y_2025}. It "
               "found more than {rubin_new} new asteroids in about {rubin_weeks} weeks.",
        "careful": "`first_obs` is not always the day a rock was discovered: old photos are sometimes matched to a rock "
                   "years later. Ceres was found in {ceres_found}, but its first sighting in the file is "
                   "{ceres_first_obs}. The busiest year in the file is {busiest_year}, with {busiest_count}.",
        "note": None,
        "charts": ["charts/K04_discoveries_per_year.png"],
        "old_charts": ["charts/A12_first_obs_per_year.png", "charts/A13_nea_size_per_year.png"],
        "words": {
            "first sighting": "the earliest photo of an object that was used to work out its path (column `first_obs`).",
            "Vera C. Rubin Observatory": "a new, very big telescope in Chile that photographs the whole southern sky "
                                         "every few nights.",
        },
    },
    # ------------------------------------------------------------------------------------------------------------ 5
    {
        "n": 5,
        "title": "Past Neptune, icy objects crowd into the spot where Neptune's rhythm keeps them safe",
        "question": "Far beyond Neptune, are the icy objects spread out evenly?",
        "rows": "asteroids on closed loops between {lo} and {hi} Earth-Sun distances from the Sun: {rows_kept} rows.",
        "rule": "kind in [an, au] and e < {F1_e_cut} and {lo} < a < {hi}",
        "example": "Pluto",
        "columns": [
            ("a", "distance from the Sun", "Earth-Sun distances", "{pluto_a}"),
            ("per_y", "year length: how long one trip around the Sun takes", "years", "{pluto_per}"),
        ],
        "math": [
            "In the narrow band from {band_lo} to {band_hi}: {band_count} objects.",
            "In the same-size boxes on each side: {left_count} and {right_count}. The band has about {band_vs_sides} "
            "times more.",
            "Objects in the band take about {band_period} years to go around the Sun. Neptune takes {neptune_period} "
            "years. {band_period} ÷ {neptune_period} = {period_ratio}. So while they go around twice, Neptune goes "
            "around three times.",
            "The main crowd, from {kb_lo} to {kb_hi}, has {kb_count}. Beyond {far_lo}: only {far_count}.",
        ],
        "relationship": "two of their trips = three of Neptune's → never close to Neptune → safe spot → crowd",
        "chart_read": [
            "**Across the bottom:** distance from the Sun, in Earth-Sun distances (column `a`). Neptune is at about "
            "{neptune_a}, on the far left.",
            "**Up the side:** how many objects are in each slice.",
            "**Each bar:** one slice of distance. The orange bars are the band from {band_lo} to {band_hi}, where Pluto lives.",
            "**Look for:** the tall orange spike, the wide main crowd to its right, and almost nothing past {far_lo}.",
        ],
        "short": "Two runners on a track are timed so the slow one is always on the far side when the fast one comes round. "
               "They never bump into each other. Neptune is the fast runner, and these icy objects are the slow ones.",
        "data": "a crowd at {band_lo} to {band_hi}, a bigger crowd from {kb_lo} to {kb_hi}, and a big drop after {far_lo}.",
        "sci": "objects with Pluto's rhythm (two trips for every three of Neptune's) are called Plutinos, which means "
               "\"little Plutos\". Neptune's timing keeps them safe.",
        "careful": "comets are left out. With them, and counting from {band_lo} itself, the band holds "
                   "{all_objects_count}.",
        "note": None,
        "charts": ["charts/K05_neptune_rhythm.png"],
        "old_charts": ["charts/A06_a_histogram_30-60AU.png"],
        "words": {
            "Kuiper belt": "a ring of icy objects beyond Neptune. Pluto lives there.",
            "Plutino": "\"little Pluto\": an object with Pluto's rhythm, two trips around the Sun for every three of "
                       "Neptune's.",
            "rhythm": "a pattern that repeats in time, like the beat in a song.",
        },
    },
    # ------------------------------------------------------------------------------------------------------------ 6
    {
        "n": 6,
        "title": "Jupiter has two swarms of asteroids, and the one in front is bigger",
        "question": "Do any asteroids share Jupiter's path around the Sun?",
        "rows": "Jupiter's Trojan asteroids only: {trojans} rows.",
        "rule": "class == \"TJN\"",
        "example": "Achilles",
        "columns": [
            ("class", "neighbourhood: `TJN` = shares Jupiter's path", "a code", "`TJN`"),
            ("om", "angle: which way the path is turned", "degrees", "{achilles_om}"),
            ("w", "angle: where the closest point to the Sun is on the path", "degrees", "{achilles_w}"),
            ("ma", "angle: how far the rock has moved along its path since its closest point", "degrees",
             "{achilles_ma}"),
        ],
        "math": [
            "Add the three angles to find where each rock is around the Sun. If the total is more than {full_circle}, "
            "take away {full_circle} (one full turn).",
            "Achilles: {achilles_om} + {achilles_w} + {achilles_ma} = {achilles_sum}. Take away {full_circle}: "
            "{achilles_L} degrees.",
            "Counting the rocks in slices of {bin} degrees shows two clumps, {peaks_apart} degrees apart.",
            "Jupiter sits halfway between them. In front of Jupiter: {n_ahead}. Behind it: {n_behind}. "
            "{n_ahead} ÷ {n_behind} = {ratio}.",
        ],
        "relationship": "balance points {lagrange} degrees ahead of and behind Jupiter → two swarms → the front one is bigger",
        "chart_read": [
            "**This chart is a map, seen from above the Solar System.** The Sun is in the middle. The small circle is "
            "Earth's path; the dashed circle is Jupiter's path.",
            "**Each blue dot:** one Trojan asteroid, placed where it is around the Sun.",
            "**The orange dot:** about where Jupiter is. Everything goes around the Sun the way the arrow points.",
            "**Look for:** two clouds of dots, one ahead of Jupiter and one behind it. The one ahead has more dots.",
        ],
        "short": "Imagine two groups of joggers running laps with one big runner. One group stays just ahead of the big "
                 "runner, and one stays just behind. Nobody ever catches up. The group in front is bigger.",
        "data": "two swarms, and the one in front is {ratio} times as big as the one behind.",
        "sci": "Trojans gather around two balance points, {lagrange} degrees ahead of and behind Jupiter. There, the pulls "
               "of the Sun and Jupiter work together. Scientists still argue about why the front swarm is bigger.",
        "careful": "which swarm is \"in front\" comes from the picture: Jupiter must sit halfway between the two clumps, "
                   "about {jupiter_est} degrees here.",
        "note": "the guide estimated Jupiter at about {guide_jupiter} degrees; our halfway point is {jupiter_est} degrees.",
        "charts": ["charts/K06_trojan_swarms.png"],
        "old_charts": ["charts/A14_trojan_longitude.png"],
        "words": {
            "Trojan asteroid": "a rock that shares Jupiter's path, ahead of it or behind it.",
            "balance point": "a spot where a small object can ride along with a planet without being pulled away. "
                             "Scientists call it a Lagrange point.",
            "swarm": "a big crowd of things moving together, like bees.",
        },
    },
    # ------------------------------------------------------------------------------------------------------------ 7
    {
        "n": 7,
        "title": "\"Potentially hazardous\" is a rule, not a warning",
        "question": "When an asteroid is called \"potentially hazardous\", does that mean it's coming for us?",
        "rows": "asteroids whose hazard flag is filled in: {pha_filled} rows.",
        "rule": "kind in [an, au] and pha is not blank",
        "example": "{yr4_name}",
        "columns": [
            ("pha", "hazard flag: `Y` (yes) = called \"potentially hazardous\"", "`Y` or `N`", "`{yr4_pha}`"),
            ("moid", "the closest its path ever gets to Earth's path", "Earth-Sun distances", "{yr4_moid}"),
            ("H", "brightness number: smaller = bigger", "a number", "{yr4_H}"),
            ("q", "closest point to the Sun", "Earth-Sun distances", "{yr4_q}"),
        ],
        "math": [
            "NASA's rule has two parts. One: the paths come within {moid_cut} Earth-Sun distances. Two: the brightness "
            "number is {H_cut} or less.",
            "{moid_cut} Earth-Sun distances is {moid_km} million km, or about {moid_ld} Moon distances. A brightness "
            "number of {H_cut} means about {size_H22} m wide.",
            "Flagged `Y`: {pha_y}. Of those, {match} pass both parts of the rule. That's {match_pct}.",
            "{yr4_name} has a brightness number of {yr4_H}: only about {yr4_size} m wide. Too small, so its flag is "
            "`{yr4_pha}`, even though in early {F4_y_2025} it had about a {yr4_chance} chance of hitting Earth.",
        ],
        "relationship": "paths come close + rock is big enough → \"potentially hazardous\" flag",
        "chart_read": [
            "**Across the bottom:** the closest the asteroid's path gets to Earth's path, in Moon distances (column "
            "`moid`).",
            "**Up the side:** the brightness number (column `H`). Smaller numbers are higher up, so the big rocks are "
            "at the top.",
            "**Each dot:** one near-Earth asteroid. Orange = flag `Y`; blue = flag `N`.",
            "**The shaded box:** the rule: paths closer than {moid_ld} Moon distances, and wider than about {size_H22} m.",
            "**Look for:** the orange dots fill the box, and almost all blue dots stay outside it.",
        ],
        "short": "It's like the height line at a theme-park ride: if you're tall enough, you can ride. The label just "
               "means a rock passed two measuring lines. It does not mean the rock is coming.",
        "data": "{match} of the {pha_y} `Y` flags follow the rule exactly. The other {exceptions} have brightness "
                "numbers from {exc_H_min} to {exc_H_max}, just past the line. Only {pha_n_rule_yes} `N` asteroids sit "
                "inside the box. The near-Earth flag is a rule too: closest point to the Sun less than {q_cut} "
                "Earth-Sun distances. That is true for {neo_rule} of the {neo_y} asteroids flagged near-Earth.",
        "sci": "NASA defines \"potentially hazardous\" with exactly these two lines. It is a watch list, not a forecast.",
        "careful": "a computer model that \"predicts\" the hazard flag from `moid` and `H` only learns the rule again. "
                   "It learns nothing about danger.",
        "note": None,
        "charts": ["charts/K07_hazard_box.png"],
        "old_charts": ["charts/BF07_hazard_box.png"],
        "words": {
            "potentially hazardous": "could possibly be dangerous one day, so it is worth watching.",
            "Moon distance": "the distance from Earth to the Moon, {S_ld_km} km.",
        },
    },
]
