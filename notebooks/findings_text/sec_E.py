"""Words for part E: stars (put together by notebooks/make_findings.py).

Every {placeholder} is filled from numbers/: inside MEET from numbers/BM_E_meet_stars.csv, inside finding n from
numbers/BFnn_*.csv. Numbers and charts: notebooks/BF_E_stars.py. Style: notebooks/findings_text/STYLE.md.
"""
PART = "E"
NAME = "Stars"
FILE = "gaia_dr3_stars_within_500_light_years.csv"

MEET = {
    "title": "the star file (Gaia)",
    "what": "The European Space Agency's Gaia spacecraft measured the position, distance, brightness, colour and movement "
            "of stars all over the sky. This file keeps only the stars within about {max_ly} light-years of the Sun "
            "({max_pc} parsecs).",
    "row": "One row is one star.",
    "size": "{rows_total} rows and {n_columns} columns. Counting one star every second, day and night, would take about "
            "{count_days} days. Only {eye_visible} of them are bright enough to see with your eyes on a dark night.",
    "story": "What kinds of stars live near the Sun? How hot and how bright are they? How fast do they move? Which ones "
             "travel together in families?",
    "example": "Proxima Centauri",
    "columns": [
        ("source_id", "star ID", "Gaia's ID number for the star", "a long number", "{prox_id}"),
        ("ra, dec", "sky position", "where the star is on the sky, like longitude and latitude on a map of the sky",
         "degrees", "{prox_ra}, {prox_dec}"),
        ("l, b", "Milky Way position", "the same position, measured from the middle of the Milky Way: `l` goes around "
         "the sky, `b` is above or below the Milky Way's flat disc", "degrees", "{prox_l}, {prox_b}"),
        ("distance_pc", "distance", "how far away the star is, worked out from its tiny yearly wobble (the `parallax` "
         "column)", "parsecs (one parsec = {pc_ly} light-years)", "{prox_dist}"),
        ("pmra, pmdec", "sideways drift", "how fast the star slides across the sky each year, east-west and north-south",
         "thousandths of an arcsecond per year", "{prox_pmra}, {prox_pmdec}"),
        ("radial_velocity", "toward-or-away speed", "how fast it moves straight toward us (minus) or away from us (plus)",
         "km every second", "{prox_rv}"),
        ("phot_g_mean_mag", "brightness as we see it", "how bright the star looks from Earth. Like the asteroid "
         "brightness number: smaller = brighter", "a number", "{prox_g}"),
        ("bp_rp", "colour number", "the star's colour: small = blue and hot, big = red and cool", "a number", "{prox_bp_rp}"),
        ("abs_g_mag", "true brightness", "how bright the star would look if every star were the same distance away. "
         "Smaller = brighter", "a number", "{prox_absg}"),
        ("ruwe", "wobble score", "how well Gaia's measurement fits one simple star. Over {ruwe_cut} = suspicious (maybe "
         "a hidden partner star, or a bad measurement)", "a number", "{prox_ruwe}"),
    ],
    "walk": [
        "This is Proxima Centauri, the closest star to the Sun. Its `source_id` is `{prox_id}`.",
        "`distance_pc` is {prox_dist} parsecs. Times {pc_ly}, that's {prox_ly} light-years: its light takes {prox_ly} "
        "years to reach us!",
        "`ra` is {prox_ra} and `dec` is {prox_dec}: far down in the southern sky, so it never rises over Ontario.",
        "`phot_g_mean_mag` is {prox_g}. Eyes can only see stars down to about {eye_limit}, so even the closest star is "
        "too faint to see without a telescope.",
        "`bp_rp` is {prox_bp_rp}: very red and cool. `abs_g_mag` is {prox_absg}: a very dim star. It is a red dwarf.",
        "`pmra` is {prox_pmra} and `pmdec` is {prox_pmdec}: together, it slides {prox_pm_arcsec} arcseconds across the "
        "sky each year. That's fast for a star.",
        "`radial_velocity` is {prox_rv}: the minus sign means it is coming toward us. `ruwe` is {prox_ruwe}, under "
        "{ruwe_cut}, so the measurement looks fine.",
    ],
    "careful": "Blank cells are common: only {rv_have_pct} of the stars have a toward-or-away speed, and {colour_blank_pct} "
               "have no colour. This file has no quality filter: {ruwe_bad_pct} of the stars have a wobble score over "
               "{ruwe_cut}. The very brightest stars, like Sirius, are too bright for Gaia, so they're missing.",
    "pictures": [],
    "words": {
        "Gaia": "a European space telescope that measures the positions and movements of stars very precisely.",
        "parallax": "the tiny shift in a star's position as Earth goes around the Sun. Hold up a finger and close one eye, "
                    "then the other: the finger jumps. Closer stars jump more, so the jump tells us the distance.",
        "red dwarf": "a small, cool, dim, red star. The most common kind of star.",
    },
}

GLOSSARY = [
    ("colour number", r"colour number|\bbp_rp\b", "a star's colour (column `bp_rp`): a small number means blue and hot; "
     "a big number means red and cool."),
    ("true brightness", r"true brightness", "how bright a star would look if all stars were the same distance away "
     "(column `abs_g_mag`). Smaller means brighter."),
    ("wobble score", r"wobble score|\bruwe\b", "how well Gaia's measurement fits one simple star (column `ruwe`). Over "
     "{F18_ruwe_cut} means the measurement is suspicious."),
    ("arcsecond", r"arcsecond", "a tiny angle: about the width of a coin seen from {ME_coin_km} km away. There are "
     "{S_sec_per_hour} arcseconds in one degree."),
    ("white dwarf", r"white dwarf", "the small, hot leftover core of a dead star, about as big as Earth."),
    ("giant star", r"\bgiants?\b", "a big, bright star near the end of its life."),
    ("main band", r"main band", "the long band on the colour-brightness chart where most stars, like the Sun, spend most "
     "of their lives. Scientists call it the main sequence."),
    ("Milky Way", r"Milky Way", "our home galaxy. From Earth it looks like a cloudy band of light across the night sky."),
    ("galaxy", r"galax", "a giant family of stars held together by gravity. Ours is the Milky Way."),
]

FINDINGS = [
    # ----------------------------------------------------------------------------------------------------------- 18
    {
        "n": 18,
        "title": "A star's colour and true brightness sort it into a family",
        "question": "If we put every star on one chart, by colour and true brightness, do they spread out evenly?",
        "rows": "stars with a colour and a true brightness: {with_colour} of the {rows}.",
        "rule": "bp_rp and abs_g_mag are not blank",
        "example": "Proxima Centauri",
        "columns": [
            ("bp_rp", "colour number: small = blue and hot, big = red and cool", "a number", "{prox_bp_rp}"),
            ("abs_g_mag", "true brightness: smaller = brighter", "a number", "{prox_absg}"),
            ("ruwe", "wobble score: over {ruwe_cut} = suspicious", "a number", "{ME_prox_ruwe}"),
        ],
        "math": [
            "We put colour across the bottom and true brightness up the side. Then we count the stars in each little square.",
            "White-dwarf test: true brightness more than {wd_a} + {wd_b} × colour, and colour under {wd_colour}. That "
            "finds {wd} stars ({wd_clean} with a good wobble score).",
            "Giant test: true brightness under {giant_mag} and colour over {giant_colour}: {giants} stars.",
            "All the rest make the main band: {main_seq} stars. The Sun would sit at colour {sun_bp_rp}, true "
            "brightness {sun_absg}.",
        ],
        "relationship": "colour + true brightness → star family",
        "chart_read": [
            "**Across the bottom:** the colour number. Left = blue and hot; right = red and cool.",
            "**Up the side:** true brightness. Brighter stars are at the top.",
            "**Colours:** each little square is coloured by how many stars are in it: darker blue = more. Each step on "
            "the colour key is 10 times more.",
            "**Look for:** the long main band with the Sun on it, the white-dwarf band below it, and the giants at the top.",
        ],
        "short": "Sort all the people in your town by height and weight. Most fall along one line. A few are giants. And "
               "some are tiny but very heavy, like the white dwarfs.",
        "data": "a main band, a white-dwarf band below it, and a small group of giants above.",
        "sci": "this chart is called the Hertzsprung-Russell diagram, after two astronomers. White dwarfs are the cooling "
               "cores of dead stars.",
        "careful": "dots scattered between the bands are often bad measurements (wobble score over {ruwe_cut}).",
        "note": None,
        "charts": ["charts/K18_colour_brightness.png"],
        "old_charts": ["charts/BF18_colour_brightness.png"],
        "words": {},
    },
    # ----------------------------------------------------------------------------------------------------------- 19
    {
        "n": 19,
        "title": "Three out of four nearby stars are red dwarfs",
        "question": "What kind of star is the most common near the Sun?",
        "rows": "main-band stars (the white dwarfs and giants from finding 18 are taken out): {ms_rows}.",
        "rule": "has a colour, and is not white dwarf-like and not giant-like",
        "example": "Proxima Centauri",
        "columns": [
            ("bp_rp", "colour number, used to sort the stars into types", "a number", "{F18_prox_bp_rp}"),
        ],
        "math": [
            "We cut the colour number at {c1}, {c2}, {c3}, {c4} and {c5}. That makes six types, from blue-white to red.",
            "The reddest type (M, the red dwarfs): {n_M}. {n_M} ÷ {ms_rows} = {pct_M}.",
            "The others: orange (K) {pct_K}, yellow like the Sun (G) {pct_G}, yellow-white (F) {pct_F}, white (A) "
            "{pct_A}, blue-white (O and B) {pct_OB}.",
            "Out of {hundred} stars, that's about {w_M} red dwarfs and only {w_G} like the Sun.",
        ],
        "relationship": "small, cool, red stars → the most common, but too dim to see",
        "chart_read": [
            "**Left:** {hundred} little squares, one for each star if you picked {hundred} at random. The colour shows "
            "the star's type.",
            "**Right:** the exact percent for each type. A longer bar means a bigger percent.",
            "**Look for:** how much of the square is red, and how tiny the white and blue-white bars are: less than one "
            "star in {hundred}.",
        ],
        "short": "In a noisy crowd you only hear the few loud people. Most stars are quiet red dwarfs that you can't see "
               "without a telescope.",
        "data": "{pct_M} red dwarfs, but only {pct_G} Sun-like stars.",
        "sci": "no red dwarf is bright enough to see with your eyes, so the night sky looks nothing like this list.",
        "careful": "the types come from colour only. Guess (not checked): Gaia misses the dimmest far-away red dwarfs, so "
                   "the real share may be even higher.",
        "note": None,
        "charts": ["charts/K19_star_types.png"],
        "old_charts": ["charts/BF19_colour_classes.png"],
        "words": {},
    },
    # ----------------------------------------------------------------------------------------------------------- 20
    {
        "n": 20,
        "title": "Eight times too many \"nearby\" stars toward the middle of the Milky Way",
        "question": "Are the nearby stars spread evenly around the sky?",
        "rows": "all the stars, counted inside two circles on the sky, each reaching {radius} degrees from its centre.",
        "rule": "angle from the middle of the Milky Way < {radius}, against angle from the opposite direction < {radius}",
        "example": "Proxima Centauri",
        "columns": [
            ("l, b", "position measured from the middle of the Milky Way", "degrees", "{ME_prox_l}, {ME_prox_b}"),
            ("ruwe", "wobble score", "a number", "{ME_prox_ruwe}"),
            ("bp_rp", "colour number (blank = no colour measured)", "a number", "{ME_prox_bp_rp}"),
        ],
        "math": [
            "Toward the middle of the Milky Way: {gc} stars. In the opposite direction: {ac}. {gc} ÷ {ac} = {ratio}.",
            "Wobble score: the middle value is {gc_ruwe} toward the middle, against {all_ruwe} for all stars. Badly "
            "measured (over {F18_ruwe_cut}): {gc_ruwe_bad} against {all_ruwe_bad}.",
            "No colour: {gc_nocolour} against {all_nocolour}.",
            "A check: the Large Magellanic Cloud, a small galaxy next to ours, gives {lmc} against {lmc_mirror} in a "
            "mirror patch. No extra stars there.",
        ],
        "relationship": "very crowded, far-away stars → wrong distance → they look nearby",
        "chart_read": [
            "**Left, across the bottom:** around the sky, measured from the middle of the Milky Way. **Up the side:** "
            "above or below the Milky Way's flat disc.",
            "**Colours:** darker blue = more stars on that part of the sky. Each step on the colour key is 10 times more.",
            "**Orange circles:** the two circles we compare. **Right:** the stars inside each circle.",
            "**Look for:** the dark knot in the middle of the map, and the orange bar about eight times taller than the "
            "blue one.",
        ],
        "short": "In a packed concert crowd, it's hard to judge how far away people are, so some faraway people seem close.",
        "data": "about {ratio} times too many \"nearby\" stars toward the middle, and most of them are badly measured.",
        "sci": "the galaxy's crowded middle confuses Gaia's distance measurements: stars that are really far away get "
               "counted as nearby.",
        "careful": "this file has no quality filter, so always check the wobble score.",
        "note": "the guide said {guide_gc} against {guide_ac} (wobble score {guide_ruwe}, {guide_nocolour} with no colour) "
                "and {guide_lmc} against {guide_lmc_mirror}; our circles give {gc} against {ac} ({gc_ruwe}, "
                "{gc_nocolour}) and {lmc} against {lmc_mirror}.",
        "charts": ["charts/K20_sky_map.png"],
        "old_charts": ["charts/BF20_sky_map.png"],
        "words": {
            "Large Magellanic Cloud": "a small galaxy that circles our Milky Way. You can see it from the southern half "
                                      "of Earth.",
        },
    },
    # ----------------------------------------------------------------------------------------------------------- 21
    {
        "n": 21,
        "title": "Stars that were born together still travel together",
        "question": "Can a computer find star families using only where stars are and how they move?",
        "rows": "well-measured stars brighter than {g_cut} (brightness as we see it) that have a measured drift: {sample}.",
        "rule": "ruwe < {F18_ruwe_cut} and phot_g_mean_mag < {g_cut} and pmra, pmdec are not blank",
        "example": "the biggest group, middle values",
        "columns": [
            ("ra, dec", "sky position", "degrees", "{top_ra}, {top_dec}"),
            ("distance_pc", "distance", "parsecs", "{top_dist}"),
            ("pmra, pmdec", "sideways drift", "thousandths of an arcsecond per year", "{top_pmra}, {top_pmdec}"),
        ],
        "math": [
            "For each star we make five numbers. Three say where it is in space, in parsecs. Two say how fast it drifts "
            "sideways, in km every second (drift × distance × {km_s_factor} ÷ {mas_per_arcsec}).",
            "We multiply the speeds by {vel_weight}, so moving together counts as much as sitting together.",
            "The computer (a method called DBSCAN) calls stars a group when {min_samples} or more of them are within "
            "{eps} steps of each other.",
            "Result: {groups} groups. The biggest has {top_stars} stars, about {top_dist} parsecs ({top_ly} light-years) "
            "away. The next two have {second_stars} and {third_stars}.",
        ],
        "relationship": "born together → same place + same motion → one group",
        "chart_read": [
            "**Left:** a map of the sky. Across the bottom is `ra`; up the side is `dec`. Each dot is a star in a group; "
            "orange = the biggest group.",
            "**Right:** a close-up of the biggest group. Each arrow shows which way a star drifts across the sky.",
            "**Orange arrows:** the group's stars. **Gray arrows:** other stars in the same patch of sky (long arrows "
            "are cut short).",
            "**Look for:** the orange arrows all pointing the same way, while the gray ones point every which way.",
        ],
        "short": "It's like spotting a school class on a trip to a busy museum: the students stay close together and walk the "
               "same way.",
        "data": "{groups} groups. The biggest sits at the same place in the sky as the Pleiades.",
        "sci": "the biggest group is the Pleiades, also called the Seven Sisters (`ra` {pleiades_ra}, `dec` "
               "{pleiades_dec}). Its stars were born from the same cloud of gas.",
        "careful": "the computer's settings ({eps} steps, {min_samples} stars) change how many groups it finds.",
        "note": None,
        "charts": ["charts/K21_star_groups.png"],
        "old_charts": ["charts/BF21_star_groups.png"],
        "words": {
            "DBSCAN": "a computer method that finds crowded spots: points with many close neighbours become a group.",
            "Pleiades": "a famous little cluster of stars in the winter sky, also called the Seven Sisters.",
        },
    },
    # ----------------------------------------------------------------------------------------------------------- 22
    {
        "n": 22,
        "title": "Some stars are really fast, and some speeds can't be right",
        "question": "How fast do stars move, and can we trust every speed in the file?",
        "rows": "all stars for the sideways drift. For the speed toward or away from us, only the stars where it was "
                "measured: {rv_n}.",
        "rule": "radial_velocity is not blank",
        "example": "{groom_name}",
        "columns": [
            ("pmra, pmdec", "sideways drift", "thousandths of an arcsecond per year", "{groom_pmra}, {groom_pmdec}"),
            ("distance_pc", "distance", "parsecs", "{groom_dist}"),
            ("radial_velocity", "speed toward (minus) or away (plus)", "km every second", "{groom_rv}"),
        ],
        "math": [
            "The fastest sideways drift: {pm_max} arcseconds a year, at {pm_max_dist} parsecs. Its position matches "
            "Barnard's Star.",
            "Sideways speed = {F21_km_s_factor} × drift × distance. Groombridge 1830: {F21_km_s_factor} × {groom_pm} × "
            "{groom_dist} = {groom_vt} km every second.",
            "Faster than {vt_cut} km every second sideways: {vt_over_200} stars.",
            "Faster than {rv_cut} toward or away: {rv_over_300}. They look fainter (middle brightness number "
            "{rv_fast_g}, against {rv_all_g} for all). The wildest: {rv_min} km every second, at {rv_min_dist} parsecs. "
            "That's faster than a star needs to escape our galaxy (about {escape_speed}).",
        ],
        "relationship": "faint star + extreme speed → probably a measuring mistake",
        "chart_read": [
            "**Left, across the bottom:** speed toward or away from us, in groups (km every second). **Up the side:** "
            "how many stars.",
            "**The orange bar:** the {rv_over_300} stars faster than {rv_cut}.",
            "**Right:** the middle brightness number as we see it (bigger = fainter), for all stars and for the "
            "fastest ones.",
            "**Look for:** almost all stars in the slow groups, and the fastest ones looking fainter.",
        ],
        "short": "If a speed camera says a bicycle went as fast as a race car, you check the camera first.",
        "data": "a few truly fast stars, and {rv_over_300} speeds that look suspicious.",
        "sci": "Barnard's Star, Groombridge 1830 and Kapteyn's Star are old stars from the galaxy's halo, just passing "
               "through our neighbourhood. Kapteyn's Star moves away from us at {kapteyn_rv} km every second.",
        "careful": "a speed this big is possible but rare; for a faint star, a measuring mistake is more likely.",
        "note": "the guide said {guide_vt} stars beat {vt_cut} km every second sideways; our data gives {vt_over_200}.",
        "charts": ["charts/K22_fast_movers.png"],
        "old_charts": ["charts/BF22_radial_velocity.png"],
        "words": {
            "halo": "the thin cloud of old stars around our galaxy's flat disc.",
            "escape": "to move so fast that gravity can't pull you back.",
        },
    },
]
