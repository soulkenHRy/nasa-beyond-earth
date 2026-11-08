"""Rank kinds of galaxy for one or more pictures, from the terminal.

    .venv/bin/python -m galaxy.classify picture.jpg [more.png ...]
    .venv/bin/python -m galaxy.classify picture.jpg --labels "spiral galaxy" "elliptical galaxy" "irregular galaxy"
    .venv/bin/python -m galaxy.classify picture.jpg --top 3

Without --labels it ranks the ten Galaxy10 classes (galaxy/clip.py, DEFAULT_LABELS).
"""
from __future__ import annotations

import argparse
import sys

from . import clip as G


def show(table) -> str:
    lines = ["  rank  match  similarity  label"]
    lines += [f"  {r.rank:4d}  {r.match_pct:4.0f}%  {r.similarity:10.3f}  {r.label}" for r in table.itertuples()]
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m galaxy.classify", description=__doc__.split("\n")[0])
    ap.add_argument("pictures", nargs="+", help="picture files (jpg, png, webp, gif, bmp, tif)")
    ap.add_argument("--labels", nargs="+", metavar="LABEL", help="kinds of galaxy to rank (default: the ten Galaxy10 classes)")
    ap.add_argument("--top", type=int, default=0, help="show only the best N (default: all)")
    args = ap.parse_args(argv)
    problems = G.missing()
    if problems:
        print("The galaxy model cannot run yet. Missing:\n  " + "\n  ".join(problems), file=sys.stderr)
        return 2
    bad = 0
    for path in args.pictures:
        try:
            image = G.open_image(path)
        except (OSError, ValueError) as err:
            print(f"\n{path}: could not read it as a picture ({err})", file=sys.stderr)
            bad += 1
            continue
        table = G.classify(image, args.labels)
        print(f"\n{path}\n{show(table.head(args.top) if args.top > 0 else table)}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
