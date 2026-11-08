"""Words for part G: Moon craters (put together by notebooks/make_findings.py).

Every {placeholder} is filled from numbers/: inside MEET from numbers/BM_G_meet_craters.csv, inside finding n from
numbers/BFnn_*.csv. Numbers and charts: notebooks/BF_G_moon_craters.py. Style: notebooks/findings_text/STYLE.md.
"""
PART = "G"
NAME = "Moon craters"
FILE = "moon_craters_robbins_lro_1.3M.csv"

MEET = {
    "title": "the Moon crater file",
    "what": "A list of every crater on the Moon that is at least {min_km} km wide. The scientist Stuart Robbins mapped "
            "them, using pictures from NASA's Lunar Reconnaissance Orbiter, a spacecraft that circles the Moon.",
    "row": "One row is one crater.",
    "size": "{rows_total} rows and {n_columns} columns. Counting one crater every second, day and night, would take "
            "about {count_days} days. Visiting one crater a day would take about {visit_years} years!",
    "story": "Where have space rocks hit the Moon? How big are the holes, what shape are they, and what do they tell us "
             "about the Moon's past?",
    "example": "Copernicus crater",
    "columns": [
        ("crater_id", "crater ID", "the crater's ID code in the list", "a code", "`{cop_id}`"),
        ("lat", "north or south", "how far north (plus) or south (minus) of the Moon's equator the crater's centre is",
         "degrees", "{cop_lat}"),
        ("lon_east", "east", "how far east the centre is, going all the way round the Moon, from zero to {full_turn}",
         "degrees", "{cop_lon_east}"),
        ("diameter_km", "width", "how wide the crater is (the width of the circle that fits it best)", "km", "{cop_d}"),
        ("ellipse_major_km", "longest width", "the crater's longest width, if it is not a perfect circle", "km", "{cop_major}"),
        ("ellipse_minor_km", "shortest width", "the crater's shortest width", "km", "{cop_minor}"),
        ("ellipse_angle_deg", "direction", "which way the long side points, from zero to {half_turn}", "degrees",
         "{cop_angle}"),
        ("rim_arc_fraction", "rim left", "how much of the crater's rim can still be seen: one = all of it; low = old "
         "and worn away", "a number from zero to one", "{cop_rim}"),
    ],
    "walk": [
        "This is Copernicus, a big young crater on the side of the Moon that faces Earth. You can see it with a small "
        "telescope. Its `crater_id` is `{cop_id}`.",
        "`lat` is {cop_lat}: a little north of the Moon's equator.",
        "`lon_east` is {cop_lon_east}. For a map we take away {full_turn} from anything over {half_turn}: {cop_lon_east} "
        "becomes {cop_lon}, so it is a bit west of the middle of the near side.",
        "`diameter_km` is {cop_d}: wider than many cities.",
        "`ellipse_major_km` is {cop_major} and `ellipse_minor_km` is {cop_minor}. {cop_major} ÷ {cop_minor} = "
        "{cop_stretch}, so it is almost a perfect circle.",
        "`rim_arc_fraction` is {cop_rim}: almost the whole rim can still be seen, because Copernicus is young.",
    ],
    "careful": "`lon_east` goes all the way round, from zero to {full_turn}. To draw a map, we change it to go from "
               "minus {half_turn} (west) to plus {half_turn} (east). Craters narrower than {min_km} km are not in the "
               "list. The README says {dup_craters} craters appear twice under different IDs. Only {blank_cells} cells "
               "in the whole file are blank.",
    "pictures": [],
    "words": {
        "Lunar Reconnaissance Orbiter": "a NASA spacecraft that circles the Moon and photographs its whole surface.",
        "rim": "the raised edge around a crater.",
    },
}

GLOSSARY = [
    ("near side", r"near side", "the half of the Moon that always faces Earth. The Moon turns so that we always see the "
     "same side."),
    ("far side", r"far side", "the half of the Moon that always faces away from Earth. People only saw it when "
     "spacecraft flew around the Moon."),
    ("dark \"seas\"", r"\"seas\"|\bseas?\b", "the Moon's dark, smooth patches. They are not water: they are old lava "
     "that flooded low ground. Scientists call them maria."),
    ("lava", r"\blava\b", "melted rock that comes up from inside a planet or moon and then cools into hard rock."),
    ("oval", r"\boval", "a stretched circle, like an egg seen from the side. Scientists call it an ellipse."),
    ("pole", r"\bpoles?\b", "the very top (north) or very bottom (south) point of a planet or moon."),
]

FINDINGS = [
    # ----------------------------------------------------------------------------------------------------------- 29
    {
        "n": 29,
        "title": "The craters draw the Moon's dark \"seas\"",
        "question": "Are the craters spread evenly over the whole Moon?",
        "rows": "craters {d5} km and wider: {all_5}.",
        "rule": "diameter_km >= {d5}",
        "example": "one crater",
        "columns": [
            ("lat", "north or south", "degrees", "{ex_lat}"),
            ("lon_east", "east, all the way round from {lon_min} to {lon_max}", "degrees", "{ex_lon_east}"),
            ("diameter_km", "width", "km", "{ex_d}"),
        ],
        "math": [
            "We change `lon_east` to go from minus {lon_half} to {lon_half}: take away {lon_max} from anything over "
            "{lon_half} ({ex_lon_east} becomes {ex_lon}).",
            "The near side is everything within {near_cut} degrees of zero (it faces Earth). The rest is the far side.",
            "Craters {d5} km and wider: {far_5} on the far side, {near_5} on the near side. {far_5} ÷ {near_5} = {ratio_5}.",
            "Craters {d1} km and wider: {far_1} against {near_1}. Craters {d20} km and wider: {far_20} against {near_20}.",
        ],
        "relationship": "lava floods → old craters buried → fewer craters on the dark \"seas\"",
        "chart_read": [
            "**Left, the map:** the whole Moon flattened like a world map. Across the bottom is east or west; up the side "
            "is north or south.",
            "**Colours:** each little box is coloured by how many craters {d5} km and wider it has, made fair for the "
            "box's size. Darker blue = more craters.",
            "**The orange box:** the near side, which always faces Earth. **Right:** the craters on each side.",
            "**Look for:** the pale patches inside the orange box (the dark \"seas\"), and the far-side bar about twice "
            "as tall.",
        ],
        "short": "Imagine a dented car that got a thick coat of paint on one side: the dents on that side got filled in. "
               "On the Moon, lava was the paint.",
        "data": "the far side has {ratio_5} times as many big craters, and the near side has big pale patches with few "
                "craters.",
        "sci": "the dark \"seas\" (maria) are younger lava floods that buried older craters. They are the dark patches "
               "you can see on the Moon with your own eyes.",
        "careful": "the pattern is clearest for craters {d5} km and wider; tiny craters can form on top of the seas later.",
        "note": None,
        "charts": ["charts/K29_crater_map.png"],
        "old_charts": ["charts/BF29_crater_map.png"],
        "words": {},
    },
    # ----------------------------------------------------------------------------------------------------------- 30
    {
        "n": 30,
        "title": "Ten times wider, about {title_low} to {d100} times rarer",
        "question": "Are big craters as common as small ones?",
        "rows": "all the craters (each one {d1} km or wider): {n_ge_1}.",
        "rule": "all rows",
        "example": "the biggest",
        "columns": [
            ("diameter_km", "width", "km", "{max_d}"),
        ],
        "math": [
            "At least {d1} km wide: {n_ge_1}. At least {d10} km: {n_ge_10}. At least {d100} km: {n_ge_100}. At least "
            "{d1000} km: only {n_ge_1000}.",
            "{n_ge_1} ÷ {n_ge_10} = {r_1_10}.",
            "{n_ge_10} ÷ {n_ge_100} = {r_10_100}.",
            "{n_ge_100} ÷ {n_ge_1000} = {r_100_1000}.",
        ],
        "relationship": "{d10} times wider → about {r_1_10} to {r_100_1000} times rarer",
        "chart_read": [
            "**Across the bottom:** four groups: craters at least {d1}, {d10}, {d100} and {d1000} km wide.",
            "**Up the side:** how many craters are in each group. Each step up the side is {d10} times the step below "
            "it, so the huge count and the tiny count fit on one chart.",
            "**Orange labels:** how many times fewer each group has than the one before.",
            "**Look for:** the steady staircase going down.",
        ],
        "short": "Think of rain: lots of tiny drops, fewer big drops, and once in a while a giant hailstone.",
        "data": "a steady rule. The middle crater is only {median_d} km wide; the biggest is {max_d} km wide, about "
                "{M_max_share} of the Moon's whole width.",
        "sci": "this kind of steady rule is called a power law: small space rocks are far more common than big ones.",
        "careful": "below about {d2} km, craters get worn away or missed, so the count of tiny craters is too low.",
        "note": None,
        "charts": ["charts/K30_size_rule.png"],
        "old_charts": ["charts/BF30_size_rule.png"],
        "words": {
            "power law": "a rule where each step up in size makes things rarer by about the same number of times.",
        },
    },
    # ----------------------------------------------------------------------------------------------------------- 31
    {
        "n": 31,
        "title": "Most craters are nearly round, and the stretched ones lean one way",
        "question": "Are craters always round?",
        "rows": "stretched craters: longest width more than {ratio_cut} times the shortest, and at least {d_cut} km wide: "
                "{n_stretched}.",
        "rule": "ellipse_major_km / ellipse_minor_km > {ratio_cut} and diameter_km >= {d_cut}",
        "example": "a stretched crater",
        "columns": [
            ("ellipse_major_km", "longest width", "km", "{ex_major}"),
            ("ellipse_minor_km", "shortest width", "km", "{ex_minor}"),
            ("ellipse_angle_deg", "which way the long side points", "degrees", "{ex_angle}"),
        ],
        "math": [
            "Stretch = longest width ÷ shortest width. Our example: {ex_major} ÷ {ex_minor} = {ex_ratio}.",
            "The middle stretch of all craters is {median_ratio}: only {median_pct_longer} longer than wide.",
            "Stretched more than {ratio_cut}: {pct_over_1_5} of craters. More than {ratio_2}: only {pct_over_2}.",
            "Of the stretched ones, {n_60_105} point between {a60} and {a105} degrees. That's {share_60_105}, but an even "
            "spread would give {even_share}. Only {n_0_30} point between {a0} and {a30}.",
        ],
        "relationship": "rock hits at a shallow angle → stretched crater; stretched craters lean one way",
        "chart_read": [
            "**Left, across the bottom:** the stretch. One = a perfect circle. **Up the side:** how many craters.",
            "**Orange bars (left):** the stretched craters, over {ratio_cut}. **Dashed line:** the middle crater.",
            "**Right, a half compass:** each wedge counts the stretched craters whose long side points that way. Longer "
            "wedge = more craters. The dashed curve is an even spread.",
            "**Look for:** the tall pile near one on the left, and the orange wedges (between {a60} and {a105} degrees) "
            "sticking out on the right.",
        ],
        "short": "Drop a ball of clay straight down and you get a round dent. Throw it at a low angle and you get a long dent.",
        "data": "most craters are nearly round; the stretched ones lean toward {a60} to {a105} degrees.",
        "sci": "rocks that hit at a very shallow angle, and chains of rocks thrown out by a bigger impact, make stretched "
               "craters. Guess (not checked): part of the lean may come from how the ovals were fitted to the pictures.",
        "careful": "the direction is the file's angle, from zero to {M_half_turn} degrees. We did not check which "
                   "compass direction zero means.",
        "note": None,
        "charts": ["charts/K31_stretched_craters.png"],
        "old_charts": ["charts/BF31_stretched_angles.png"],
        "words": {
            "stretch (of a crater)": "how long a crater is compared with how wide: longest width ÷ shortest width. One "
                                     "is a perfect circle.",
        },
    },
    # ----------------------------------------------------------------------------------------------------------- 32
    {
        "n": 32,
        "title": "More craters per square kilometre toward the poles",
        "question": "Are there more craters near the Moon's poles or near its equator?",
        "rows": "all the craters, sorted into bands {band_w} degrees tall from the south pole to the north pole: {F30_n_ge_1}.",
        "rule": "band = floor(lat / {band_w})",
        "example": "the north pole band",
        "columns": [
            ("lat", "north (plus) or south (minus)", "degrees", "{lat_80} to {lat_90}"),
        ],
        "math": [
            "Bands of the same height are not the same size: near a pole, the band is a tiny cap. So we divide each "
            "band's count by its area.",
            "The band from {lat_80} to {lat_90} degrees north has an area of {area_80_90}, against {area_0_10} for {lat_0} "
            "to {band_w} degrees north. It is {area_ratio} times smaller.",
            "Counts: {cnt_80_90N} against {cnt_0_10N}. Per area, the north pole band has {ratio_north} times as many "
            "craters as the equator; the south pole band {ratio_south} times.",
            "Beyond {lat_80} degrees: {n_north_80} craters in the north, {n_south_80} in the south.",
        ],
        "relationship": "near the poles → low sun → long shadows → small craters easier to spot",
        "chart_read": [
            "**Left:** a globe cut into bands of the same height. The blue band near the equator is big; the orange cap "
            "at the top is tiny.",
            "**Right, up the side:** the bands, with the north pole at the top and the south pole at the bottom.",
            "**Across the bottom:** craters per area, compared with the equator. The dashed line is the equator's value, one.",
            "**Look for:** the bars getting longer toward both poles, and the orange polar bars sticking out the most.",
        ],
        "short": "Look at footprints in snow at sunset: the low sunlight makes long shadows, so every little dent shows up.",
        "data": "more craters per area toward both poles, and more in the north than in the south.",
        "sci": "part of this may come from the mapping: long shadows near the poles make small craters easier to see. "
               "The biggest crater within {sp_within} degrees of the south pole is {sp_largest} km wide; Shackleton "
               "crater ({shack_d} km here) sits right at the south pole.",
        "careful": "always divide by area when you compare bands of a globe.",
        "note": None,
        "charts": ["charts/K32_polar_craters.png"],
        "old_charts": ["charts/BF32_polar_bands.png"],
        "words": {
            "per square kilometre": "for each square of ground one kilometre long and one kilometre wide.",
            "area": "how much surface something covers.",
        },
    },
]
