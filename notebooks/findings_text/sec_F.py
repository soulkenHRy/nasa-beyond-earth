"""Words for part F: planets around other stars (put together by notebooks/make_findings.py).

Every {placeholder} is filled from numbers/: inside MEET from numbers/BM_F_meet_planets.csv, inside finding n from
numbers/BFnn_*.csv. Numbers and charts: notebooks/BF_F_exoplanets.py. Style: notebooks/findings_text/STYLE.md.
"""
PART = "F"
NAME = "Planets around other stars"
FILE = "nasa_exoplanet_archive_confirmed_planets.csv"

MEET = {
    "title": "the planet file",
    "what": "NASA's Exoplanet Archive: the official list of confirmed planets that go around other stars. Planets "
            "outside our Solar System are called exoplanets.",
    "row": "One row is one planet.",
    "size": "{rows_total} rows and {n_columns} columns. The planets go around {n_hosts} different stars, and "
            "{multi_hosts} of those stars have more than one planet. The first one in the list was found in "
            "{first_year}; the newest in {last_year}.",
    "story": "What kinds of planets are out there? How big are they, how close to their star, how were they found, and "
             "could any of them be a bit like Earth?",
    "example": "{ex_name}",
    "columns": [
        ("pl_name, hostname", "planet name, star name", "the planet's name and its star's name. The planet is the star's "
         "name plus a small letter", "words", "{ex_name}, {ex_host}"),
        ("disc_year", "year found", "the year the planet was announced", "a year", "{ex_year}"),
        ("discoverymethod", "how it was found", "`Transit` = it passed in front of its star and made it a tiny bit "
         "dimmer; `Radial Velocity` = its pull made the star wobble toward and away from us", "words", "{ex_method}"),
        ("disc_facility", "who found it", "the telescope or team that found it", "words", "{ex_facility}"),
        ("pl_orbper", "year length", "how many Earth days one trip around its star takes", "days", "{ex_orbper}"),
        ("pl_rade", "size", "how wide the planet is, compared with Earth", "Earths (one = as wide as Earth)", "{ex_rade}"),
        ("pl_bmasse", "mass", "how heavy the planet is, compared with Earth", "Earths (one = as heavy as Earth)", "{ex_mass}"),
        ("pl_insol", "starlight", "how much starlight the planet gets, compared with Earth", "Earths (one = the same as "
         "Earth)", "{ex_insol}"),
        ("st_met", "metal score", "how much metal the star has: zero = like the Sun, plus = more, minus = less", "a number",
         "{ex_met}"),
        ("sy_dist", "distance", "how far the planet's star is from us", "parsecs (one parsec = {pc_ly} light-years)",
         "{ex_dist}"),
        ("gaia_source_id", "Gaia ID", "the star's ID in the Gaia star file of part E, so the two files can be joined",
         "a long number, kept as text", "{ex_gaia}"),
    ],
    "walk": [
        "{ex_name} goes around {ex_host} (Proxima Centauri), the closest star to the Sun.",
        "`disc_year` is {ex_year} and `discoverymethod` is {ex_method}: astronomers saw the star wobble. "
        "`disc_facility` is the {ex_facility}.",
        "`pl_orbper` is {ex_orbper}: one year there lasts only {ex_orbper} days, so it has about "
        "{ex_years_per_earth_year} birthdays in one of our years!",
        "`pl_rade` is {ex_rade} and `pl_bmasse` is {ex_mass}: about the size and weight of Earth.",
        "`pl_insol` is {ex_insol}: it gets a bit less starlight than Earth does.",
        "`st_met` is {ex_met}: nobody has measured the star's metal score yet.",
        "`sy_dist` is {ex_dist} parsecs, about {ex_ly} light-years. Its `gaia_source_id` is `{ex_gaia}`, the same ID "
        "Proxima Centauri has in the Gaia file of part E.",
    ],
    "careful": "A blank cell means nobody has measured it yet: {rade_blank} planets have no size, {insol_blank} no "
               "starlight value, and {met_blank} no metal score. Planets found by radial velocity ({rv_pct} of the list) "
               "never crossed their star. So their size is worked out from their mass: it's a careful guess. Most planets "
               "({transit_pct}) were found by transit. `gaia_source_id` must be read as text: long ID numbers get rounded "
               "if a computer treats them as decimals.",
    "pictures": [],
    "words": {
        "exoplanet": "a planet that goes around a star other than our Sun.",
        "confirmed": "checked carefully, so scientists are sure the planet is really there.",
        "mass": "how much stuff something is made of. On Earth, more mass means heavier.",
    },
}

GLOSSARY = [
    ("transit", r"[Tt]ransit", "when a planet passes in front of its star and makes the star a tiny bit dimmer, like a "
     "moth flying past a lamp."),
    ("radial velocity", r"[Rr]adial [Vv]elocity", "a way to find planets: the planet's pull makes its star wobble toward "
     "and away from us, and telescopes can measure that wobble."),
    ("Earths (planet size)", r"in Earths|Earth-size|Earths\b", "planet sizes are measured against Earth: two means twice as "
     "wide as Earth."),
    ("metal score", r"metal score|\bmetal\b", "how much metal a star has (column `st_met`). To astronomers, \"metal\" means "
     "any element heavier than helium, like iron or oxygen."),
    ("Kepler", r"Kepler", "a NASA space telescope that stared at one patch of sky and found thousands of planets by transit."),
    ("Neptune-size", r"Neptune", "about as big as Neptune, which is {F24_neptune_re} times as wide as Earth."),
    ("hot Jupiter", r"hot Jupiter", "a giant planet like Jupiter that goes around its star very closely, so it is very hot."),
    ("habitable zone", r"just.right|habitable", "the \"just right\" distance from a star: not too hot and not too cold, so "
     "water could be liquid."),
]

FINDINGS = [
    # ----------------------------------------------------------------------------------------------------------- 23
    {
        "n": 23,
        "title": "Planet discoveries arrive in batches",
        "question": "Do astronomers find about the same number of planets every year?",
        "rows": "all the confirmed planets: {rows}. Of these, {transit_all} were found by transit.",
        "rule": "all rows",
        "example": "{M_ex_name}",
        "columns": [
            ("disc_year", "year the planet was announced", "a year", "{M_ex_year}"),
            ("discoverymethod", "how it was found", "words", "{M_ex_method}"),
            ("disc_facility", "who found it", "words", "{M_ex_facility}"),
        ],
        "math": [
            "We count the planets in each year, split by how they were found.",
            "Found by transit: {tr_2013} in {y_2013}, then {tr_2014} in {y_2014}, {tr_2015} in {y_2015}, and {tr_2016} in {y_2016}.",
            "The Kepler telescope alone: {kepler_2014} in {y_2014} and {kepler_2016} in {y_2016}.",
            "The busiest year is {busiest_year}, with {busiest_n} planets. All of {y_2025} had {tot_2025}; {y_2026} so far has {tot_2026}.",
        ],
        "relationship": "a team checks many planets, then announces them all at once → one very tall bar",
        "chart_read": [
            "**Across the bottom:** the year the planet was announced.",
            "**Up the side:** how many planets were announced that year.",
            "**Colours:** blue = found by transit, orange = found by radial velocity, gray = other ways.",
            "**Look for:** the two very tall, mostly blue bars in {y_2014} and {y_2016}.",
        ],
        "short": "A teacher marks everyone's tests over many weeks, then hands them all back on the same day. That one day "
               "looks huge, even though the work was spread out.",
        "data": "two very tall years, {y_2014} and {y_2016}, mostly planets found by transit.",
        "sci": "the Kepler team confirmed big batches of planets at once in {y_2014} and {y_2016}.",
        "careful": "the year is when a planet was announced, not when its star was first watched.",
        "note": None,
        "charts": ["charts/K23_planets_per_year.png"],
        "old_charts": ["charts/BF23_planets_per_year.png"],
        "words": {
            "batch": "a big group of things that arrive at the same time.",
        },
    },
    # ----------------------------------------------------------------------------------------------------------- 24
    {
        "n": 24,
        "title": "Hot Jupiters are common in the list, but hot Neptunes are rare",
        "question": "Can a planet of any size live very close to its star?",
        "rows": "planets with a year length and a size: {rows}.",
        "rule": "pl_orbper and pl_rade are not blank",
        "example": "{ex_name}",
        "columns": [
            ("pl_orbper", "year length", "days", "{ex_orbper}"),
            ("pl_rade", "size", "Earths", "{ex_rade}"),
            ("discoverymethod", "how it was found", "words", "Transit"),
        ],
        "math": [
            "Neptune-size means more than {nep_lo} and up to {nep_hi} Earths wide.",
            "Neptune-size planets with a year shorter than {p1} days: {nep_lt3}. With a year of {p1} to {p2} days: "
            "{nep_3_10}. {nep_3_10} ÷ {nep_lt3} = {nep_ratio}.",
            "Jupiter-size planets (over {jup_size} Earths) with a year shorter than {p2} days: {jup8_lt10}.",
            "A strange flat line: {rv_flat} planets found by radial velocity have sizes from {flat_lo} to {flat_hi} "
            "Earths. Their sizes were worked out from their mass.",
        ],
        "relationship": "very close to the star + middle size → rare",
        "chart_read": [
            "**Across the bottom:** year length in days. Left = a very short year, so very close to the star.",
            "**Up the side:** planet size, in Earths.",
            "**Each dot:** one planet. Blue = found by transit, orange = found by radial velocity.",
            "**The shaded box:** Neptune-size planets with years shorter than {p1} days. **The dashed box:** the same "
            "sizes with years of {p1} to {p2} days.",
            "**Look for:** few dots in the shaded box, many in the dashed box, and a big cloud of hot Jupiters at the top left.",
        ],
        "short": "Put snowballs near a campfire: the medium ones melt away, but big blocks of ice last much longer.",
        "data": "Neptune-size planets almost disappear on the shortest years; Jupiter-size planets don't.",
        "sci": "this is called the hot Neptune desert: strong starlight may strip away a middle-size planet's gas. Hot "
               "Jupiters are the easiest planets to find, so there are extra of them in the list.",
        "careful": "the chart only shows planets with years up to {zoom_days} days and sizes up to {zoom_size} Earths, so it zooms in on "
                   "the planets closest to their stars.",
        "note": None,
        "charts": ["charts/K24_orbit_vs_size.png"],
        "old_charts": ["charts/BF24_orbit_vs_size.png"],
        "words": {
            "desert": "here, an empty part of the chart where few planets are found.",
        },
    },
    # ----------------------------------------------------------------------------------------------------------- 25
    {
        "n": 25,
        "title": "A gap between rocky planets and gassy planets",
        "question": "Are planets of every size equally common, or are some sizes missing?",
        "rows": "planets with a year shorter than {p_cut} days and a size from {size_lo} to {size_hi} Earths: {rows}.",
        "rule": "pl_orbper < {p_cut} and {size_lo} <= pl_rade <= {size_hi}",
        "example": "{M_ex_name}",
        "columns": [
            ("pl_rade", "size", "Earths", "{M_ex_rade}"),
            ("pl_orbper", "year length", "days", "{M_ex_orbper}"),
        ],
        "math": [
            "We cut the sizes into {bins} slices. Each slice is a little wider than the one before it, so small planets "
            "get a fair look.",
            "Hump of smaller planets: {peak1_lo} to {peak1_hi} Earths, {peak1_n} planets.",
            "The dip: {valley_lo} to {valley_hi} Earths, only {valley_n}.",
            "Hump of bigger planets: {peak2_lo} to {peak2_hi} Earths, {peak2_n} planets.",
        ],
        "relationship": "small planets lose their gas → rocky; bigger ones keep it → gassy; few stay in between",
        "chart_read": [
            "**Across the bottom:** planet size, in Earths. The slices get wider to the right.",
            "**Up the side:** how many planets are in each size slice.",
            "**Colours:** blue = smaller (rocky) planets, green = bigger (gassy) ones, orange = the slice in the dip.",
            "**Look for:** two humps with a small dip between them.",
        ],
        "short": "People on a slide end up either at the bottom or still sitting at the top. Hardly anyone stays stuck "
               "halfway down.",
        "data": "two humps with a shallow dip between them.",
        "sci": "this is called the radius valley. Planets smaller than the gap are bare rock; bigger ones have thick "
               "layers of gas.",
        "careful": "many sizes are worked out from mass, which blurs the dip.",
        "note": None,
        "charts": ["charts/K25_radius_gap.png"],
        "old_charts": ["charts/BF25_radius_valley.png"],
        "words": {
            "radius valley": "the dip in planet sizes between rocky planets and gassy planets.",
        },
    },
    # ----------------------------------------------------------------------------------------------------------- 26
    {
        "n": 26,
        "title": "Planet hunters mostly look at Sun-like stars",
        "question": "Do planets turn up around every kind of star?",
        "rows": "planets whose star is also in the Gaia star file, matched by ID: {matched_planets} planets around "
                "{matched_hosts} stars.",
        "rule": "gaia_source_id (read as text) == source_id in the Gaia file (read as text)",
        "example": "{M_ex_name}",
        "columns": [
            ("gaia_source_id", "the star's Gaia ID (planet file)", "text", "{M_ex_gaia}"),
            ("source_id", "the star's Gaia ID (star file of part E)", "text", "{M_ex_gaia}"),
            ("bp_rp", "colour number (star file), used to sort stars into types", "a number", "{F18_prox_bp_rp}"),
        ],
        "math": [
            "Matching the IDs as text: {matched_planets} planets.",
            "If the IDs are turned into decimal numbers first, {float_changed_pct} of them change, and only {float_join} "
            "still match.",
            "Stars with planets: yellow like the Sun (G) {host_G}, orange (K) {host_K}, red dwarfs (M) {host_M}.",
            "All nearby stars: G {gaia_G}, K {gaia_K}, M {gaia_M}.",
        ],
        "relationship": "planet searches aim at Sun-like stars → planets are found there",
        "chart_read": [
            "**Across the bottom:** six types of stars, from blue-white to red.",
            "**Up the side:** the percent of stars of that type.",
            "**Gray bars:** all nearby stars. **Blue bars:** stars where planets were found.",
            "**Look for:** the blue bars taller than the gray ones for Sun-like stars, and much shorter for red dwarfs.",
        ],
        "short": "If you only look for your lost keys under the streetlight, every key you find will be under the streetlight.",
        "data": "red dwarfs are {gaia_M} of the stars but only {host_M} of the stars with planets.",
        "sci": "planet searches often pick bright, Sun-like stars on purpose.",
        "careful": "a computer model that learns \"which stars have planets\" also learns where people looked.",
        "note": "the guide said decimals change {guide_changed} of the IDs, leaving {guide_float_join}; our test gives "
                "{float_changed_pct} and {float_join} (it depends on how the IDs are turned into numbers).",
        "charts": ["charts/K26_host_stars.png"],
        "old_charts": ["charts/BF26_host_classes.png"],
        "words": {
            "join": "matching the rows of two files by a value they share, like an ID number.",
            "decimal number": "a number a computer stores with limited precision, so very long IDs can get rounded.",
        },
    },
    # ----------------------------------------------------------------------------------------------------------- 27
    {
        "n": 27,
        "title": "Stars with more metal have more giant planets",
        "question": "Does the star's metal have anything to do with the planets it makes?",
        "rows": "planets whose star has a metal score from just above {b1_lo} up to {b4_hi}: {met_rows}.",
        "rule": "{b1_lo} < st_met <= {b4_hi}",
        "example": "the most metal-rich group",
        "columns": [
            ("st_met", "metal score of the star: zero = like the Sun", "a number", "{b4_lo} to {b4_hi}"),
            ("pl_bmasse", "planet mass, in Earths", "Earths", "over {mass_cut} = a giant"),
            ("pl_rade", "planet size, in Earths", "Earths", "over {size_cut} = a giant"),
        ],
        "math": [
            "A giant planet is heavier than {mass_cut} Earths or wider than {size_cut} Earths.",
            "Least metal ({b1_lo} to {b1_hi}): {b1_giants} giants out of {b1_n} planets = {b1_pct}.",
            "The middle groups: {b2_pct} and {b3_pct}.",
            "Most metal ({b4_lo} to {b4_hi}): {b4_giants} giants out of {b4_n} = {b4_pct}.",
        ],
        "relationship": "more metal in the star → more giant planets",
        "chart_read": [
            "**Across the bottom:** four groups of stars, from the least metal (left) to the most (right).",
            "**Up the side:** out of every hundred planets of those stars, how many are giants.",
            "**The orange bar:** the most metal-rich stars.",
            "**Look for:** the orange bar, about twice as tall as the others.",
        ],
        "short": "More Lego in the box means you can build bigger towers. Stars born with more heavy stuff had more "
               "planet-building material.",
        "data": "the giant share jumps to {b4_pct} for the most metal-rich stars.",
        "sci": "this link between metal-rich stars and giant planets is well known.",
        "careful": "{met_blank} planets have no metal score for their star, so they are left out.",
        "note": "the guide said {guide_b3} for the third group; ours is {b3_pct} ({b3_pct1} before rounding).",
        "charts": ["charts/K27_giant_share.png"],
        "old_charts": ["charts/BF27_giant_share.png"],
        "words": {
            "giant planet": "a very big planet, like Jupiter or Saturn, made mostly of gas.",
        },
    },
    # ----------------------------------------------------------------------------------------------------------- 28
    {
        "n": 28,
        "title": "Earth-size planets in the \"just right\" zone",
        "question": "Are there planets like Earth: about Earth's size and getting about Earth's starlight?",
        "rows": "Earth-size planets that get Earth-like starlight: {n}.",
        "rule": "pl_rade <= {size_cut} and {insol_lo} <= pl_insol <= {insol_hi}",
        "example": "{top_name}",
        "columns": [
            ("pl_rade", "size, in Earths", "Earths", "{top_rade}"),
            ("pl_insol", "starlight, compared with Earth (Earth = {earth_insol})", "Earths", "{top_insol}"),
            ("sy_dist", "distance", "parsecs", "{top_pc}"),
        ],
        "math": [
            "Up to {size_cut} Earths wide, and getting {insol_lo} to {insol_hi} times Earth's starlight: {n} planets.",
            "The nearest: {top_name}, at {top_pc} parsecs × {pc_ly} = {top_ly} light-years.",
            "Travelling at the speed of the {voyager_name} spacecraft ({voyager_kms} km every second), the trip would "
            "take about {voyager_years} years.",
        ],
        "relationship": "Earth-size + Earth-like warmth → maybe \"just right\" for liquid water",
        "chart_read": [
            "**Across the bottom:** how much starlight the planet gets. One = the same as Earth; left = colder, right = hotter.",
            "**Up the side:** planet size, in Earths.",
            "**The green box:** our \"just right\" rule. **Blue dots:** the {n} planets inside it. **The orange star:** "
            "where Earth would sit.",
            "**Look for:** the blue dots crowded around Earth's star, and the closest one, {top_name}.",
        ],
        "short": "Like Goldilocks' porridge: not too hot, not too cold, just right.",
        "data": "{n} planets, and {n_within_10pc} of them are within {near_pc} parsecs of us.",
        "sci": "\"just right\" (the habitable zone) means water could be liquid there. It does not mean anything lives there.",
        "careful": "{n_rv} of the {n} were found by radial velocity, so their sizes are guesses worked out from their mass.",
        "note": None,
        "charts": ["charts/K28_just_right.png"],
        "old_charts": ["charts/BF28_just_right.png"],
        "words": {
            "Voyager 1": "a NASA spacecraft that is now the farthest human-made object from Earth.",
        },
    },
]
