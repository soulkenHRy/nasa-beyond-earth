"""Words for part C: fireballs (put together by notebooks/make_findings.py).

Every {placeholder} is filled from numbers/: inside MEET from numbers/BM_C_meet_fireballs.csv, inside finding n from
numbers/BFnn_*.csv. Numbers and charts: notebooks/BF_B_C_approaches_fireballs.py. Style: notebooks/findings_text/STYLE.md.
"""
PART = "C"
NAME = "Fireballs"
FILE = "extras_fireballs.csv"

MEET = {
    "title": "the fireball file",
    "what": "A list of fireballs: space rocks that blew up high in our air. Government sensors on satellites, built to "
            "watch for big flashes, spotted them. NASA keeps the list.",
    "row": "One row is one fireball.",
    "size": "{rows_total} rows and {n_columns} columns, from {first} to {last}. That's about {years_span} years, or "
            "about {per_year} fireballs a year.",
    "story": "Where and when do space rocks blow up in our sky, and how much energy do they let out?",
    "example": "the Chelyabinsk fireball",
    "columns": [
        ("date", "when", "the date and time of the fireball, in world time", "year-month-day hour:minute:second",
         "`{ex_date}`"),
        ("energy", "light energy", "how much light it gave off, counted in units of {energy_unit} joules", "a number",
         "{ex_energy}"),
        ("impact-e", "total energy", "all the energy it let out. One kiloton is the energy of {S_kt_tonnes} tonnes of TNT",
         "kilotons", "{ex_kt}"),
        ("lat, lat-dir", "north or south", "how far from the equator, and which way: `N` = north, `S` = south",
         "degrees, then a letter", "{ex_lat}, `{ex_latdir}`"),
        ("lon, lon-dir", "east or west", "how far east or west, and which way: `E` = east, `W` = west",
         "degrees, then a letter", "{ex_lon}, `{ex_londir}`"),
        ("alt", "height", "how high up it was when it shone brightest", "km above the ground", "{ex_alt}"),
        ("vel", "speed", "how fast it was going", "km every second", "{ex_vel}"),
    ],
    "walk": [
        "This is the biggest fireball in the file. It blew up over the city of Chelyabinsk, in Russia.",
        "`date` is `{ex_date}`, in world time.",
        "`impact-e` is {ex_kt} kilotons: the same energy as {ex_tonnes} tonnes of TNT going off at once.",
        "`lat` is {ex_lat} and `lat-dir` is `{ex_latdir}`: {ex_lat} degrees north. `lon` is {ex_lon} and `lon-dir` is "
        "`{ex_londir}`: {ex_lon} degrees east.",
        "`alt` is {ex_alt}: it blew up {ex_alt} km above the ground, about {ex_alt_vs_plane} times as high as a passenger "
        "plane flies ({plane_km} km).",
        "`vel` is {ex_vel}: {ex_vel} km every second. That's {ex_kmh} km an hour!",
    ],
    "careful": "A blank cell means the sensors didn't report it: {no_place} fireballs have no place, {no_alt} have no "
               "height, and {no_vel} have no speed. Each place is split into two columns, a number and a direction "
               "letter. To put fireballs on a map, we turn south and west into negative numbers. Most fireballs are "
               "small: the middle one is only {kt_median} kilotons.",
    "pictures": [],
    "words": {
        "sensor": "a machine that notices things, like a flash of light.",
        "satellite": "a machine that circles Earth in space.",
    },
}

GLOSSARY = [
    ("fireball", r"[Ff]ireball", "a very bright shooting star: a space rock that burns and explodes high in the air."),
    ("TNT", r"\bTNT\b", "a strong explosive. Scientists use it as a ruler for the size of explosions."),
    ("joule", r"joule", "the scientists' unit for energy."),
    ("km every second", r"km every second", "how many kilometres something travels in one second. Multiply by "
     "{S_sec_per_hour} to get kilometres in an hour."),
]

FINDINGS = [
    # ----------------------------------------------------------------------------------------------------------- 10
    {
        "n": 10,
        "title": "Fireballs happen everywhere, and one was far bigger than all the others",
        "question": "Do fireballs like some places on Earth better than others? How big do they get?",
        "rows": "fireballs with a known place: {located} of the {rows}.",
        "rule": "lat and lon are not blank",
        "example": "Chelyabinsk",
        "columns": [
            ("lat, lat-dir", "north or south of the equator", "degrees, `N` or `S`", "{big1_lat}, `{M_ex_latdir}`"),
            ("lon, lon-dir", "east or west", "degrees, `E` or `W`", "{big1_lon}, `{M_ex_londir}`"),
            ("impact-e", "total energy", "kilotons", "{big1_kt}"),
        ],
        "math": [
            "We turn south and west into negative numbers, so every place becomes one pair of numbers on a map.",
            "If fireballs fell at random, each band of the globe would get its fair share of the area. From the equator "
            "to {band_edge} degrees north is {band_0_30_share} of Earth's surface, so we expect {band_0_30_exp} of the "
            "{located}. We see {band_0_30_obs}.",
            "Over the ocean: {over_ocean} of {located}, which is {ocean_pct}. The ocean covers about {earth_ocean_pct} "
            "of Earth.",
            "The biggest: {big1_kt} kilotons on {big1_date}. The next biggest: {big2_kt} kilotons on {big2_date}. "
            "{big1_kt} ÷ {big2_kt} = {big_ratio}.",
        ],
        "relationship": "random hits → each part of the globe gets its fair share of the area",
        "chart_read": [
            "**Left, the map:** across the bottom is east or west; up the side is north or south. Gray is land, white is "
            "ocean.",
            "**Each blue circle:** one fireball. A bigger circle means more energy. The orange circle is the biggest one.",
            "**Right, the bars:** each pair is one band of the globe. Blue = fireballs seen. Gray = the band's fair "
            "share if fireballs fell at random.",
            "**Look for:** circles spread all over the map, and each blue bar close to its gray bar.",
        ],
        "short": "Throw a handful of rice at a spinning beach ball. The grains land everywhere, with more on the wide middle "
               "of the ball, because there's more room there. Space rocks do the same to Earth.",
        "data": "every band gets about its fair share of the area, and the biggest fireball was {big_ratio} times the next "
                "biggest.",
        "sci": "the biggest is the Chelyabinsk fireball over Russia. Its energy was about {big1_hiroshimas} times that of "
               "the Hiroshima bomb ({hiroshima_kt} kilotons).",
        "careful": "{no_place} fireballs have no place, so they are not on the map. Early years have fewer fireballs with "
                   "a known place.",
        "note": "the guide said {guide_land} were over land; our land map gives {over_land}.",
        "charts": ["charts/K10_fireball_map.png"],
        "old_charts": ["charts/BF10_fireball_map.png"],
        "words": {
            "fair share": "what each part would get if things were shared out evenly by size.",
            "Hiroshima bomb": "the atomic bomb dropped on the city of Hiroshima, Japan, near the end of World War Two.",
        },
    },
    # ----------------------------------------------------------------------------------------------------------- 11
    {
        "n": 11,
        "title": "Fewer fireballs at dawn",
        "question": "Do fireballs happen at every time of day equally?",
        "rows": "fireballs with a known place: {located}.",
        "rule": "lat and lon are not blank; Sun time = world-time hour + longitude ÷ {deg_per_hour}, wrapped around to stay within one day",
        "example": "Chelyabinsk",
        "columns": [
            ("date", "when, in world time", "a date and time", "`{M_ex_date}`"),
            ("lon, lon-dir", "east or west (east counts as plus, west as minus)", "degrees", "{ex_lon}"),
        ],
        "math": [
            "The file uses world time. To get the time where the fireball happened, we use the Sun: every "
            "{deg_per_hour} degrees east is one hour later.",
            "Chelyabinsk: world time {ex_utc_dec} hours + {ex_lon} ÷ {deg_per_hour} = {ex_utc_dec} + {ex_lon_h} = "
            "{ex_local}. That's about {ex_local_clock} in the morning.",
            "We count the fireballs in {slot_hours}-hour slots. Fewest: {min_slot_from} to {min_slot_to} am "
            "({min_count}). Most: the slot before midnight ({max_count}). An even spread would be {avg_slot} per slot.",
            "Months are flat: every month has between {month_min} and {month_max} fireballs.",
        ],
        "relationship": "slow rocks catch up with Earth from behind → they hit the evening side → fewer fireballs at dawn",
        "chart_read": [
            "**Across the bottom:** the time of day where the fireball happened, in {slot_hours}-hour slots. Midnight is "
            "at both ends.",
            "**Up the side:** how many fireballs happened in that slot.",
            "**The dashed line:** an even spread, {avg_slot} in every slot. **The orange bar:** the slot with the fewest.",
            "**Look for:** the dip around dawn and the tallest bar just before midnight.",
        ],
        "short": "Ride your bike slowly, and faster bikes going the same way bump into your back. Many space rocks travel "
               "around the Sun the same way Earth does, but a bit faster. They catch Earth from behind, on the side "
               "where it's evening.",
        "data": "dawn has the fewest fireballs in both halves of the data. Before {split_year}: {before2010_dawn} at dawn "
                "against {before2010_night} late in the evening. Since then: {from2010_dawn} against {from2010_night}.",
        "sci": "meteorites have long been found to fall more often in the afternoon and evening than in the morning. "
               "Slow rocks on paths like Earth's catch up from behind.",
        "careful": "the sensors might not watch every hour equally. We did not test that.",
        "note": None,
        "charts": ["charts/K11_local_time.png"],
        "old_charts": ["charts/BF11_local_time.png"],
        "words": {
            "Sun time": "the time of day set by the Sun: noon is when the Sun is highest. It changes as you go east or west.",
            "dawn": "early morning, when the Sun comes up.",
            "meteorite": "a space rock that reaches the ground.",
        },
    },
]
