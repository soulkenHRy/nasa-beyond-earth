"""Words for part D: space weather (put together by notebooks/make_findings.py).

Every {placeholder} is filled from numbers/: inside MEET from numbers/BM_D_meet_space_weather.csv, inside finding n from
numbers/BFnn_*.csv. Numbers and charts: notebooks/BF_D_space_weather.py. Style: notebooks/findings_text/STYLE.md.
"""
PART = "D"
NAME = "Space weather"
FILE = "nasa_omni_solar_wind_storms_5min_2010-2026.csv"

MEET = {
    "title": "the space weather file",
    "what": "Readings of the solar wind and of Earth's storm meter, taken every {step_min} minutes from {first} to {last}. "
            "NASA's OMNI service puts them together from spacecraft that sit between the Sun and Earth, and from "
            "magnetic sensors on the ground.",
    "row": "One row is one {step_min}-minute reading: what the solar wind and Earth's magnetic field were doing in those "
           "{step_min} minutes.",
    "size": "{rows_total} rows and {n_columns} columns. That's {per_day} readings every day and about {per_year} a year, "
            "for about {years_span} years.",
    "story": "Space has weather too! The Sun blows a wind at Earth all the time. Sometimes it sends a gust or a giant "
             "cloud, and Earth's magnetic field shakes: that is a magnetic storm, and it can make northern lights. The "
             "file shows when storms happen, how strong they are, and what the wind was doing just before.",
    "example": "a calm reading",
    "columns": [
        ("datetime_utc", "time", "when the {step_min}-minute reading starts, in world time", "year-month-day hour:minute",
         "`{ex_time}`"),
        ("sym_h_nT", "storm meter", "how hard a storm is shaking Earth's magnetic field. Near zero = calm. {storm_cut} "
         "or lower = a storm; {strong_cut} = a strong storm; {extreme_cut} = an extreme one", "nanotesla", "{ex_symh}"),
        ("speed_km_s", "wind speed", "how fast the solar wind is blowing", "km every second", "{ex_speed}"),
        ("density_cm3", "how crowded", "how many tiny bits of wind are packed into one cubic centimetre (a cube one "
         "centimetre on each side, smaller than a sugar cube)", "bits per cubic centimetre", "{ex_den}"),
        ("pressure_nPa", "push", "how hard the wind pushes on Earth's magnetic bubble", "nanopascals", "{ex_pre}"),
        ("bz_gsm_nT", "Bz (north or south)", "which way the magnetic field inside the wind points: plus = north, "
         "minus = south. South is the way that lets storm energy in", "nanotesla", "{ex_bz}"),
    ],
    "walk": [
        "`datetime_utc` is `{ex_time}`, in world time, during a calm year.",
        "`sym_h_nT` is {ex_symh}: close to zero, so there's no storm. The middle reading of the whole file is {symh_median}.",
        "`speed_km_s` is {ex_speed}: the wind blew {ex_speed} km every second. That's {ex_kmh} km an hour! At its "
        "middle speed, the wind takes about {sun_days} days to travel from the Sun to Earth.",
        "`density_cm3` is {ex_den}: about {ex_den} tiny bits in each cubic centimetre. Space is very empty: the air "
        "around you is packed far, far tighter.",
        "`pressure_nPa` is {ex_pre}: a very gentle push.",
        "`bz_gsm_nT` is {ex_bz}: almost zero, so the door for storm energy is nearly shut.",
        "Compare the strongest storm in the file: at `{file_low_time}` the storm meter read {file_low}.",
    ],
    "careful": "A blank cell means no measurement in those minutes: {bz_blank_pct} of the Bz readings and "
               "{speed_blank_pct} of the speed readings are blank. The storm meter stops on {symh_last}, even though the "
               "wind readings go on. Even on calm days the storm meter sits a little below zero. The other {n_other} "
               "columns (like temperature and aurora meters) are not used here.",
    "pictures": [],
    "words": {
        "spacecraft": "a machine that travels or works in space.",
        "magnetic storm": "a storm in Earth's magnetic field, set off by the Sun. Scientists call it a geomagnetic storm.",
        "sugar cube": "a small cube of sugar; a cubic centimetre is a bit smaller than one.",
    },
}

GLOSSARY = [
    ("storm meter", r"storm meter|sym_h", "a number that shows how hard a solar storm is shaking Earth's magnetic field. "
     "Near zero is calm; the more negative, the bigger the storm. Scientists call it SYM-H."),
    ("Bz", r"\bBz\b|bz_gsm", "the north-south direction of the magnetic field carried by the solar wind. When it points "
     "south (a minus number), it links up with Earth's field and lets storm energy in, like opening a door."),
    ("nanotesla", r"nanotesla", "a very tiny unit for how strong a magnetic field is."),
    ("nanopascal", r"nanopascal", "a very tiny unit for how hard something pushes."),
    ("magnetic bubble", r"magnetic bubble", "the space around Earth that Earth's magnetic field controls. It shields us "
     "from most of the solar wind. Scientists call it the magnetosphere."),
    ("equinox", r"equinox", "one of the two days each year, in late March and late September, when day and night are "
     "about the same length everywhere on Earth."),
    ("cycle", r"\bcycle\b", "something that repeats over and over, like the seasons."),
    ("Toronto time", r"Toronto", "the clock time in Toronto, Ontario. It is {F17_utc_offset_winter} hours behind world "
     "time in winter and {F17_utc_offset_summer} hours behind in summer."),
]

FINDINGS = [
    # ----------------------------------------------------------------------------------------------------------- 12
    {
        "n": 12,
        "title": "Storms rise and fall with the Sun's {cycle_years}-year cycle",
        "question": "Does the Sun make the same number of storms every year?",
        "rows": "the readings grouped into world-time days. For each day we keep its lowest storm-meter reading: {days} days.",
        "rule": "sym_h_nT is not blank; one row per day = that day's lowest sym_h_nT",
        "example": "{ex_day}",
        "columns": [
            ("sym_h_nT", "storm meter: we keep each day's lowest reading", "nanotesla", "{ex_day_min}"),
            ("speed_km_s", "wind speed: we average it for each day and each year", "km every second", "{ex_speed}"),
        ],
        "math": [
            "A storm day is a day when the storm meter reached {storm_cut} or lower. A strong-storm day reached "
            "{strong_cut} or lower.",
            "Storm days: {storm_2019} in {y_2019} and only {storm_2020} in {y_2020}, the fewest. Then {storm_2024} in "
            "{y_2024} and {storm_2025} in {y_2025}, the most.",
            "Strong-storm days were highest in {strong_max_year}: {strong_max} of them.",
            "The wind was fastest on average in {speed_max_year} ({speed_max} km every second) and slowest in "
            "{speed_min_year} ({speed_min}).",
        ],
        "relationship": "busy Sun → more storms; it rises and falls about every {cycle_years} years",
        "chart_read": [
            "**Top chart, across the bottom:** the years. **Up the side:** how many days that year had a storm.",
            "**Blue bars:** storm days. **Orange bars:** strong-storm days.",
            "**Bottom chart:** the average speed of the solar wind each year.",
            "**Look for:** the short bars in {y_2019} and {y_2020}, and the tall ones in {y_2024} and {y_2025}.",
        ],
        "short": "The Sun has moods that last for years, like very slow seasons. {y_2019} to {y_2020} was its calm winter. "
               "{y_2024} to {y_2025} was its stormy summer.",
        "data": "few storm days in {y_2019} and {y_2020}, and many in {y_2024} and {y_2025}.",
        "sci": "the Sun's activity goes up and down about every {cycle_years} years (the sunspot cycle). This cycle turned "
               "out stronger than many forecasts.",
        "careful": "the storm meter stops on {last_day}, so {y_2026} is not a full year.",
        "note": None,
        "charts": ["charts/K12_storm_days_per_year.png"],
        "old_charts": ["charts/BF12_storm_days_per_year.png"],
        "words": {
            "sunspot": "a dark, cooler patch on the Sun. More sunspots mean a busier, stormier Sun.",
            "forecast": "a prediction, like a weather forecast.",
        },
    },
    # ----------------------------------------------------------------------------------------------------------- 13
    {
        "n": 13,
        "title": "What the solar wind does in the hours before a big storm",
        "question": "Does the solar wind change before a big storm, like a warning sign?",
        "rows": "storms: runs of readings at {storm_cut} or lower, joined together when they are less than {join_gap_h} "
                "hours apart. That makes {events_all} storms, and {events_strong} of them are strong ({strong_cut} or lower).",
        "rule": "storm = sym_h_nT <= {storm_cut}, runs joined if less than {join_gap_h} hours apart; strong = lowest <= {strong_cut}",
        "example": "the middle strong storm, {h24} hours before its lowest point",
        "columns": [
            ("density_cm3", "how crowded the wind is", "bits per cubic centimetre", "{den_m24}"),
            ("pressure_nPa", "how hard the wind pushes", "nanopascals", "{pre_m24}"),
            ("bz_gsm_nT", "Bz: plus = north, minus = south", "nanotesla", "{bz_24}"),
            ("sym_h_nT", "storm meter", "nanotesla", "{symh_24}"),
        ],
        "math": [
            "We line up the {events_strong} strong storms so that their lowest points match. Then, every {step_min} "
            "minutes, we take the middle value of all of them.",
            "Crowding: {den_base} bits per cubic centimetre two days before, but {den_m20} at {h20} hours before. Twice "
            "as crowded!",
            "Push: {pre_base} two days before, {pre_m8} at {h8} hours before. {pre_m8} ÷ {pre_base} = {pre_ratio_m8} "
            "times harder.",
            "Bz turns south: {bz_6} at {h6} hours before, and {bz_2} at {h2} hours before.",
            "Storm by storm, the lowest point comes about {lead_median} hours (the middle value) after Bz first reaches "
            "{bz_cut}.",
        ],
        "relationship": "crowded, pushy wind + Bz turns south → a storm a few hours later",
        "chart_read": [
            "**Across the bottom:** time, counted from each storm's lowest point (the dashed line). Left = before, "
            "right = after.",
            "**Four charts, top to bottom:** how crowded the wind is, how hard it pushes, Bz (north or south), and the "
            "storm meter. Each has its own numbers up the side.",
            "**The orange area:** the hours when Bz points south, so the door is open.",
            "**Look for:** the top two lines climbing first, then the orange area, then the storm meter diving down.",
        ],
        "short": "Think of a traffic jam before a crash. First the cars bunch up. Then they push harder. Then the road tilts "
               "the wrong way, and the crash happens.",
        "data": "crowding and pushing rise first, then Bz turns south, and then the storm meter drops.",
        "sci": "when Bz points south, the Sun's magnetic field links up with Earth's and lets energy in, like opening a door.",
        "careful": "the readings are already moved to the time the wind reaches Earth, so these hours are not real "
                   "warning time.",
        "note": None,
        "charts": ["charts/K13_before_a_storm.png"],
        "old_charts": ["charts/BF13_before_a_storm.png"],
        "words": {
            "lined up": "moved in time so that every storm's lowest point sits at the same spot on the chart.",
        },
    },
    # ----------------------------------------------------------------------------------------------------------- 14
    {
        "n": 14,
        "title": "The Sun repeats itself every {sun_turn} days",
        "question": "Does the solar wind follow a pattern?",
        "rows": "the average wind speed of each day: {days} days.",
        "rule": "speed_km_s is not blank, averaged over each world-time day",
        "example": "{ex_day1}",
        "columns": [
            ("speed_km_s", "wind speed, averaged over the day", "km every second", "{ex_speed1}"),
        ],
        "math": [
            "An example: on {ex_day1} the wind blew {ex_speed1} km every second. {sun_turn} days later, on {ex_day2}, "
            "it blew {ex_speed2}.",
            "We compare the whole list of daily speeds with the same list shifted by some days. Then we give it a match "
            "score: one = a perfect match, zero = no match.",
            "Shifted by {sun_turn} days: {all_27} for all the years, and {sub_27} for the quiet years {y_2016} to {y_2018}.",
            "Shifted by {lag13} days: only {all_13}. By {lag20} days: {all_20}. Almost no match at all.",
        ],
        "relationship": "the Sun turns about once every {sun_turn} days → the same fast wind comes back",
        "chart_read": [
            "**Top chart:** the daily wind speed through part of {y_2017}. Across the bottom is the date; up the side "
            "is the speed.",
            "**Orange dashed lines:** {sun_turn} days apart. The peaks of fast wind keep coming back near them.",
            "**Bottom chart:** the match score (up the side) for each number of days apart (across the bottom), up to "
            "{lag60}. Blue = all years; orange = the quiet years.",
            "**Look for:** the big bump at {sun_turn} days.",
        ],
        "short": "Think of a lighthouse: its beam sweeps past you once every turn. The Sun has \"holes\" that blow fast wind, "
               "and the same hole faces Earth again every {sun_turn} days.",
        "data": "between {lag20} and {lag35} days apart, the best match is at exactly {best_lag} days.",
        "sci": "seen from Earth, the Sun turns once about every {sun_turn} days. Holes in the Sun's outer layer, called "
               "coronal holes, send out fast wind on each turn.",
        "careful": "busy years blur the pattern; quiet years show it best.",
        "note": None,
        "charts": ["charts/K14_27_day_repeat.png"],
        "old_charts": ["charts/BF14_27_day_repeat.png"],
        "words": {
            "coronal hole": "a darker, cooler patch in the Sun's outer layer, where fast wind escapes.",
            "shifted": "slid along, so each day lines up with a later day.",
        },
    },
    # ----------------------------------------------------------------------------------------------------------- 15
    {
        "n": 15,
        "title": "Storms like the months around the equinoxes",
        "question": "Do magnetic storms happen more in some months than in others?",
        "rows": "every reading that has a storm-meter value: {readings}.",
        "rule": "sym_h_nT is not blank",
        "example": "a calm reading",
        "columns": [
            ("datetime_utc", "time: we use its month", "a date and time", "`{M_ex_time}`"),
            ("sym_h_nT", "storm meter: stormy = {storm_cut} or lower", "nanotesla", "{M_ex_symh}"),
        ],
        "math": [
            "For each month, we find the percent of readings that are stormy ({storm_cut} or lower).",
            "Highest: March {share_3} and April {share_4}. High again in September {share_9} and October {share_10}.",
            "Lowest: December {share_12} and July {share_7}. {share_3} ÷ {share_12} = {max_vs_min}.",
            "Strong storms: {strong_3} in March, {strong_10} in October and {strong_11} in November, but only "
            "{strong_7} in July and {strong_12} in December.",
        ],
        "relationship": "near the equinoxes → Earth's magnetic field lines up best with the Sun's → more storms",
        "chart_read": [
            "**Both charts, across the bottom:** the twelve months.",
            "**Left, up the side:** the percent of time that month was stormy. **Right, up the side:** how many strong "
            "storms had their lowest point in that month.",
            "**Orange bars:** the months around the equinoxes (March, April, September, October).",
            "**Look for:** two humps (spring and autumn) and two dips (summer and winter).",
        ],
        "short": "A key only opens a lock when you hold it at the right angle. Around late March and late September, Earth "
               "is tilted at just the right angle for the Sun's magnetic key.",
        "data": "two peaks (spring and autumn) and two dips (summer and winter).",
        "sci": "this pattern has a name: the Russell-McPherron effect, after the two scientists who explained it.",
        "careful": "a few huge storms can tip a month, so we added all the years together.",
        "note": "the guide said {guide_sep_oct} for September and October; our data gives {share_9} and {share_10}.",
        "charts": ["charts/K15_storms_by_month.png"],
        "old_charts": ["charts/BF15_storms_by_month.png"],
        "words": {},
    },
    # ----------------------------------------------------------------------------------------------------------- 16
    {
        "n": 16,
        "title": "The May {y_2024} superstorm, hour by hour",
        "question": "What happened, step by step, during the biggest storm in the file?",
        "rows": "the readings from {win_from} to {win_to}, world time: {win_rows} readings.",
        "rule": "{win_from_code} <= datetime_utc <= {win_to_code}",
        "example": "right after the cloud hit",
        "columns": [
            ("speed_km_s", "wind speed", "km every second", "{speed_after}"),
            ("density_cm3", "how crowded the wind is", "bits per cubic centimetre", "{den_after}"),
            ("bz_gsm_nT", "Bz: minus = south", "nanotesla", "{bz1}"),
            ("sym_h_nT", "storm meter", "nanotesla", "{symh_up}"),
        ],
        "math": [
            "At {shock_utc} world time ({shock_tor} in Toronto), a giant cloud from the Sun hit. The wind speed jumped "
            "from {speed_before} to {speed_after} km every second in one {step_min}-minute step.",
            "The wind got {den_ratio} times as crowded ({den_before} → {den_after}). The storm meter first jumped UP to "
            "{symh_up}, because the cloud squeezed Earth's magnetic bubble.",
            "Then Bz turned south: {bz1} at {bz1_utc}, and {bz2} at {bz2_utc}.",
            "The lowest point: {low} at {low_utc} world time, which was {low_tor} in Toronto. That's {hours_shock_to_low} "
            "hours after the cloud hit.",
        ],
        "relationship": "cloud hits → magnetic bubble squeezed → Bz turns south → huge storm",
        "chart_read": [
            "**Across the bottom:** time, in world time, over two days.",
            "**Three charts:** wind speed (top), Bz (middle) and the storm meter (bottom).",
            "**The orange line:** the moment the cloud hit.",
            "**Look for:** the jump in speed at the orange line, Bz plunging below zero, and the storm meter falling to "
            "its lowest point hours later.",
        ],
        "short": "Think of a big wave hitting a sandcastle. First the splash pushes it (the storm meter goes up). Then the "
               "water pulls everything down (the storm meter dives).",
        "data": "the lowest storm-meter reading in the whole file, {low}. The October {y_2024} storm reached {oct_low}, "
                "on {oct_tor} Toronto time.",
        "sci": "this was the Gannon superstorm. It painted northern lights across Ontario and much of the world.",
        "careful": "{bz_blank_pct} of the Bz readings in these two days are blank; they show as gaps in the line.",
        "note": "the guide said the cloud hit at about {guide_shock} with the speed jumping to {guide_speed_after}; our "
                "readings show the jump at {shock_utc} to {speed_after}, then {speed_plus10} at {plus10_utc}.",
        "charts": ["charts/K16_may_2024.png"],
        "old_charts": ["charts/BF16_may_2024.png"],
        "words": {
            "superstorm": "an extremely strong magnetic storm, the kind that happens only every few decades.",
        },
    },
    # ----------------------------------------------------------------------------------------------------------- 17
    {
        "n": 17,
        "title": "Big storms that happened during an Ontario night",
        "question": "How often could people in Ontario have seen northern lights from a strong storm?",
        "rows": "storm-meter readings up to {F12_last_day}, changed to Toronto time, dark hours only: {nights_all} nights.",
        "rule": "Toronto time from {from_h} to {to_h} (the hours after midnight count for the night before)",
        "example": "January {y_2026}",
        "columns": [
            ("datetime_utc", "time, which we change to Toronto time", "a date and time", "{jan_utc}"),
            ("sym_h_nT", "storm meter", "nanotesla", "{jan_low}"),
        ],
        "math": [
            "Toronto clocks are {utc_offset_winter} hours behind world time in winter and {utc_offset_summer} hours "
            "behind in summer.",
            "For each night, from {from_h} to {to_h}, we keep the lowest storm-meter reading.",
            "Nights at {cut} or lower: {nights_total}. There were {n_2023} each in {y_2023}, {y_2024} and {y_2025}, but "
            "{n_2019} in {y_2019}, {y_2020} and {y_2022}.",
            "In January {y_2026} the storm meter hit {jan_low}, but at {jan_tor_ampm} in Toronto, when the dark hours "
            "were over. The nights around it reached {jan_dark_before} (before) and {jan_dark_after} (after).",
        ],
        "relationship": "strong storm + dark sky in Toronto → a chance of northern lights",
        "chart_read": [
            "**Across the bottom:** the years.",
            "**Up the side:** how many nights that year had a strong storm while it was dark in Toronto.",
            "**Orange bars:** the years with the most.",
            "**Look for:** the empty years around {y_2019} to {y_2022}, and the busy years {y_2023} to {y_2025}.",
        ],
        "short": "It's like a shooting star: the show has to happen while it's dark where you are. Part of it is luck.",
        "data": "{nights_total} good nights since {y_2010}.",
        "sci": "the storm meter is only a rough guide: clouds, moonlight and city lights matter too.",
        "careful": "the storm meter stops on {F12_last_day}, so {y_2026} is not complete.",
        "note": "the guide said the dark-hours value was {guide_jan_dark}; our data gives {jan_dark_before} the night "
                "before and {jan_dark_after} the night after.",
        "charts": ["charts/K17_ontario_nights.png"],
        "old_charts": ["charts/BF17_ontario_nights.png"],
        "words": {
            "dark hours": "here, {from_h} to {to_h} Toronto time, when the sky is dark enough to see northern lights.",
        },
    },
]
