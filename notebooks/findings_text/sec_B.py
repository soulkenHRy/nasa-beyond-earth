"""Words for part B: close approaches (put together by notebooks/make_findings.py).

Every {placeholder} is filled from numbers/: inside MEET from numbers/BM_B_meet_close_approaches.csv, inside finding n
from numbers/BFnn_*.csv. Numbers and charts: notebooks/BF_B_C_approaches_fireballs.py. Style: notebooks/findings_text/STYLE.md.
"""
PART = "B"
NAME = "Close approaches"
FILE = "extras_close_approaches_1900-2200.csv"

MEET = {
    "title": "the close-approach file",
    "what": "A list of every time a near-Earth asteroid or comet flew past Earth, or will fly past, from {y_first} to "
            "{y_last}. NASA's Jet Propulsion Laboratory (JPL) works the passes out from the paths of the rocks in part A.",
    "row": "One row is one pass: one object flying past Earth one time. A rock that passes many times has many rows.",
    "size": "{rows_total} rows and {n_columns} columns. The passes come from {objects} different objects, so each one "
            "passes about {passes_per_object} times. Over the {n_years} years in the file, that's about {per_year} passes a year.",
    "story": "How close do space rocks come to Earth, how fast are they going, and when? The file also hides a trap: it can "
             "only list passes by rocks we have already found.",
    "example": "Apophis in {apo_year}",
    "columns": [
        ("des", "name tag", "the object's short name or number. It matches the `pdes` column of the asteroid file", "a code",
         "`{apo_des}`"),
        ("fullname", "full name", "the object's whole name", "words", "{apo_name}"),
        ("cd", "pass time", "the date and time of the closest moment, in world time", "year-month-day hour:minute",
         "`{apo_cd}`"),
        ("dist", "how close", "the distance from the centre of Earth at the closest moment",
         "Earth-Sun distances (we turn them into Moon distances or km)", "{apo_dist}"),
        ("v_rel", "speed", "how fast it moves compared with Earth", "km every second", "{apo_v}"),
        ("h", "brightness number", "the same idea as `H` in part A: a bigger number means a smaller rock", "a number", "{apo_h}"),
    ],
    "walk": [
        "`fullname` is {apo_name}: Apophis, the famous asteroid from part A. `des` is `{apo_des}`, its number.",
        "`cd` is `{apo_cd}`: the moment Apophis will be closest to Earth, in world time.",
        "`dist` is {apo_dist}. Times {au_km} million km, that's {apo_km} km from Earth's centre, or about {apo_ld} of a "
        "Moon distance.",
        "Take away Earth's radius ({earth_radius} km): Apophis will pass {apo_height} km above the ground. That's lower "
        "than the TV satellites that circle Earth {geo_km} km up!",
        "`v_rel` is {apo_v}: it moves {apo_v} km every second. That's {apo_kmh} km an hour.",
        "`h` is {apo_h}. Apophis has {apo_passes} rows in this file, because it passes us many times between {y_first} "
        "and {y_last}.",
    ],
    "careful": "`dist` is measured from Earth's centre, not from the ground. Every pass in the file is closer than "
               "{range_au} Earth-Sun distances ({range_ld} Moon distances, about {range_million_km} million km): farther "
               "passes are not listed. Passes in the future are predictions. Passes from before a rock was found were "
               "worked out backwards. The brightness number `h` is blank in {h_blank} rows.",
    "pictures": [],
    "words": {
        "pass": "one time an object flies by Earth.",
        "prediction": "a careful guess about the future, worked out with math.",
        "radius": "the distance from the centre of a ball to its outside: half of its width.",
    },
}

GLOSSARY = [
    ("Moon distance", r"Moon distance", "the distance from Earth to the Moon, {S_ld_km} km. A car driving at "
     "{S_car_kmh} km an hour, day and night, would need about {S_car_days_ld} days to cover it."),
    ("km every second", r"km every second", "how many kilometres something travels in one second. Multiply by "
     "{S_sec_per_hour} to get kilometres in an hour."),
    ("near-Earth", r"[Nn]ear-Earth", "an asteroid or comet whose path around the Sun comes close to Earth's path."),
]

FINDINGS = [
    # ------------------------------------------------------------------------------------------------------------ 8
    {
        "n": 8,
        "title": "Close passes bunch up around today, because that's when we find the rocks",
        "question": "Do more space rocks fly past Earth now than in the past, or than in the future?",
        "rows": "every pass in the file (all closer than {range_ld} Moon distances): {rows} passes by {objects} different objects.",
        "rule": "all rows",
        "example": "{ex_name}",
        "columns": [
            ("cd", "pass time: date and time of the closest moment (world time)", "a date", "`{ex_cd}`"),
            ("dist", "how close: distance from Earth's centre", "Earth-Sun distances", "{ex_dist_au}"),
        ],
        "math": [
            "We count the passes in each decade. From the {dec_1900s_label}, there were about {dec_1900s_avg} per decade.",
            "The {lbl_2010}: {dec_2010}. The {lbl_2020}: {dec_2020}. The {lbl_2030}: only {dec_2030}. "
            "{dec_2020} ÷ {dec_2030} = {drop_2020s_2030s}.",
            "Passes closer than the Moon: {moon_2025} in {yr_2025} and {moon_2026} in {yr_2026}, but {moon_2027} in "
            "{yr_2027} and {moon_2028} in {yr_2028}.",
            "The closest pass of {yr_2025} was {ex_name}: {ex_dist_au} × {au_km} million km = {ex_km} km from Earth's "
            "centre. Take away Earth's radius ({earth_radius} km): only {ex_height} km above the ground, lower than the "
            "space station ({iss_km} km)!",
        ],
        "relationship": "we find most small rocks only while they pass → past and future passes look empty",
        "chart_read": [
            "**Top chart, across the bottom:** time in years, one bar for each decade. The past is on the left; the "
            "future is on the right. **Up the side:** how many passes happened (or will happen) in that decade.",
            "**The dashed line:** today. The orange bars are the {lbl_2010} and {lbl_2020}.",
            "**Bottom chart:** only the passes closer than the Moon, year by year. The orange bars are {yr_2025} and {yr_2026}.",
            "**Look for:** the tall bars right before the dashed line, and how empty it gets right after it.",
        ],
        "short": "Imagine counting cars on a dark road with a flashlight. You only see the cars in your beam. Tomorrow's cars "
               "are out there too; you just can't see them yet.",
        "data": "passes bunch up in the {lbl_2010} and {lbl_2020}, and passes closer than the Moon almost disappear after "
                "{yr_2026}.",
        "sci": "most small asteroids are found during the very pass that brings them close. Rocks that haven't been found "
               "yet can't be in the file, so the future looks quiet.",
        "careful": "passes from before a rock was found were worked out backwards with math, not seen. Future passes are "
                   "predictions.",
        "note": None,
        "charts": ["charts/K08_passes_per_decade.png"],
        "old_charts": ["charts/BF08_passes_per_decade.png"],
        "words": {
            "space station": "the International Space Station, where astronauts live as it circles Earth.",
        },
    },
    # ------------------------------------------------------------------------------------------------------------ 9
    {
        "n": 9,
        "title": "July is quiet, for the telescopes",
        "question": "Do space rocks fly past Earth more in some months than in others?",
        "rows": "passes from {y_from} to {y_to}: {rows} passes. The small rocks among them (brightness number over "
                "{h_cut}): {small_rows}.",
        "rule": "{y_from} <= year of cd <= {y_to}; small rocks: h > {h_cut}",
        "example": "{ex_name}",
        "columns": [
            ("cd", "pass time: we use its month", "a date", "`{ex_cd}`"),
            ("h", "brightness number: bigger = smaller rock", "a number", "{ex_h}"),
        ],
        "math": [
            "We count the passes in each month, adding up all the years from {y_from} to {y_to}.",
            "Small rocks (brightness number over {h_cut}, so about {size_h25} m wide or less): {small_jul} passes in "
            "July, but {small_oct} in October.",
            "{small_oct} ÷ {small_jul} = {ratio}: October has {ratio} times as many.",
            "All passes together: {all_jul} in July, {all_oct} in October.",
        ],
        "relationship": "short, stormy summer nights at northern telescopes → fewer small rocks spotted in July",
        "chart_read": [
            "**Across the bottom:** the twelve months of the year.",
            "**Up the side:** how many passes happened in that month, with all the years from {y_from} to {y_to} added up.",
            "**Gray bars:** all passes. **Blue bars:** only the small rocks.",
            "**Look for:** the blue bars dipping lowest in July and highest in {small_max_month}.",
        ],
        "short": "Imagine birdwatching only at night from your backyard. In summer the nights are short and often stormy, so "
               "you spot fewer birds. The birds didn't leave; you just looked less.",
        "data": "July is the quietest month for small rocks, and {small_max_month} is the busiest.",
        "sci": "a likely reason, which we did not test: most search telescopes are in the north, in places like Arizona "
               "and Hawaii. There, summer nights are short, summer storms close the domes, and the bright Milky Way "
               "fills the sky.",
        "careful": "this shows when we look, not when the rocks come.",
        "note": "the guide said a brightness number over {h_cut} means under about {guide_size} m; with a shininess of "
                "{albedo_guess} we get about {size_h25} m.",
        "charts": ["charts/K09_passes_by_month.png"],
        "old_charts": ["charts/BF09_passes_by_month.png"],
        "words": {
            "dome": "the round roof over a big telescope. It opens at night and closes when it rains.",
            "Milky Way": "our home galaxy. From Earth it looks like a bright, cloudy band across the night sky.",
        },
    },
]
