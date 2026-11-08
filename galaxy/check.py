"""Try the galaxy model on ten well-known galaxies and save what it says (numbers/GC_check.csv, numbers/GC_model.csv).

The pictures are cutouts from the DESI Legacy Imaging Surveys sky viewer (legacysurvey.org): Legacy Surveys or SDSS
images, downloaded once into data_cache/galaxy_check/ (not in git). The expected class comes from what each object
is; for three of them two Galaxy10 classes fit, and both count. This only checks that the model runs and gives
sensible answers. It is not a measure of accuracy: ten pictures are far too few, and the default labels were chosen
after trying them, and a longer wording, on these same ten.

    .venv/bin/python -m galaxy.check
"""
from __future__ import annotations

import sys
import urllib.request

import pandas as pd

from . import clip as G

CUTOUT = "https://www.legacysurvey.org/viewer/cutout.jpg?ra={ra}&dec={dec}&layer={layer}&pixscale={ps}&size=256"
OUT = G.ROOT / "data_cache" / "galaxy_check"
NUM = G.ROOT / "numbers"
CARD_PARAMS_M = 200        # the model card (README.md in the model folder) says "~200M" parameters

# name, RA and Dec (degrees), arcseconds per pixel, sky-viewer layer, what it is, the Galaxy10 class(es) that fit
GALAXIES = [
    ("M87", 187.7059, 12.3911, 1.5, "ls-dr9", "giant elliptical", ["round smooth galaxy"]),
    ("NGC 4565", 189.0866, 25.9877, 4.0, "ls-dr9", "spiral seen edge-on, with a bulge", ["edge-on galaxy with bulge"]),
    ("NGC 1300", 49.9208, -19.4111, 1.6, "ls-dr9", "barred spiral", ["barred spiral galaxy"]),
    ("NGC 4676", 191.5428, 30.7286, 0.8, "sdss", "the Mice, two galaxies merging",
     ["merging galaxies", "disturbed galaxy"]),
    ("M101", 210.8023, 54.3490, 7.0, "sdss", "spiral with open arms, seen face-on", ["unbarred loose spiral galaxy"]),
    ("M51", 202.4696, 47.1952, 3.0, "sdss", "spiral with open arms and a small companion",
     ["unbarred loose spiral galaxy", "merging galaxies"]),
    ("NGC 3115", 151.3083, -7.7186, 2.0, "ls-dr9", "lens-shaped galaxy seen edge-on",
     ["edge-on galaxy with bulge", "cigar-shaped smooth galaxy"]),
    ("NGC 4244", 184.3736, 37.8071, 4.0, "sdss", "thin spiral seen edge-on, almost no bulge",
     ["edge-on galaxy without bulge"]),
    ("NGC 4449", 187.0463, 44.0936, 1.6, "sdss", "irregular galaxy", ["disturbed galaxy"]),
    ("NGC 4414", 186.6129, 31.2235, 1.2, "sdss", "spiral with short, tightly wound arms",
     ["unbarred tight spiral galaxy"]),
]


def picture(name, ra, dec, ps, layer):
    path = OUT / f"{name.replace(' ', '')}.jpg"
    if not path.exists():
        OUT.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(CUTOUT.format(ra=ra, dec=dec, layer=layer, ps=ps),
                                     headers={"User-Agent": "nasa-beyond-earth galaxy check"})
        with urllib.request.urlopen(req, timeout=60) as r:
            path.write_bytes(r.read())
    return G.open_image(path)


def main() -> int:
    problems = G.missing()
    if problems:
        print("The galaxy model cannot run yet. Missing:\n  " + "\n  ".join(problems), file=sys.stderr)
        return 2
    rows, sims = [], []
    for name, ra, dec, ps, layer, what, fit in GALAXIES:
        try:
            img = picture(name, ra, dec, ps, layer)
        except OSError as err:
            print(f"{name}: could not get the picture ({err}); the check needs the internet once.", file=sys.stderr)
            return 1
        t = G.classify(img)
        sims += t["similarity"].tolist()
        rows.append({"galaxy": name, "what_it_is": what, "expected": " or ".join(fit),
                     "first_choice": t.label[0], "first_match_pct": round(t.match_pct[0], 1),
                     "first_similarity": round(t.similarity[0], 3), "second_choice": t.label[1],
                     "second_match_pct": round(t.match_pct[1], 1), "right": t.label[0] in fit,
                     "ra": ra, "dec": dec, "layer": layer})
        r = rows[-1]
        print(f"{'ok  ' if r['right'] else 'MISS'} {name:9s} {r['first_choice']:31s} {r['first_match_pct']:5.1f}%  "
              f"(then {r['second_choice']}, {r['second_match_pct']:.0f}%)")
    check = pd.DataFrame(rows)
    check.to_csv(NUM / "GC_check.csv", index=False)

    i, n_right = G.info(), int(check["right"].sum())
    params = G.n_params()
    src_cfg = "models/galaxy-clip-finetuned/config.json"
    facts = [
        ("params", params, f"{params:,}", "", "counted from the model weights"),
        ("params_m", params / 1e6, f"{params / 1e6:.0f}", "million", "counted from the model weights"),
        ("card_params_m", CARD_PARAMS_M, str(CARD_PARAMS_M), "million", "the model card (its README.md) says about 200M"),
        ("weights_mb", i["weights_mb"], f"{i['weights_mb']:.0f}", "MB", "size of model.safetensors"),
        ("image_px", i["image_px"], str(i["image_px"]), "pixels", src_cfg),
        ("patch_px", i["patch_px"], str(i["patch_px"]), "pixels", src_cfg),
        ("patches_side", i["patches_side"], str(i["patches_side"]), "", "image_px / patch_px"),
        ("patches", i["patches"], str(i["patches"]), "", "patches_side squared"),
        ("embed_dim", i["embed_dim"], str(i["embed_dim"]), "numbers", src_cfg),
        ("scale", G.scale(), f"{G.scale():.1f}", "", "exp(logit_scale), read from the model weights"),
        ("n_labels", len(G.DEFAULT_LABELS), str(len(G.DEFAULT_LABELS)), "", "galaxy/clip.py DEFAULT_LABELS"),
        ("check_n", len(check), str(len(check)), "", "numbers/GC_check.csv"),
        ("check_right", n_right, str(n_right), "", "numbers/GC_check.csv"),
        ("check_two_fit", int(check["expected"].str.contains(" or ").sum()),
         str(int(check["expected"].str.contains(" or ").sum())), "", "numbers/GC_check.csv"),
        ("sim_lo", min(sims), f"{min(sims):.1f}", "", "smallest similarity in the check (all labels)"),
        ("sim_hi", max(sims), f"{max(sims):.1f}", "", "largest similarity in the check (all labels)"),
    ]
    pd.DataFrame(facts, columns=["key", "value", "shown", "unit", "source"]).to_csv(NUM / "GC_model.csv", index=False)
    print(f"\n{n_right} of {len(check)} first choices fit. Saved numbers/GC_check.csv and numbers/GC_model.csv.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
