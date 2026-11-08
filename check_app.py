"""Open every page of the Streamlit app headlessly and report any error.

Usage (from the project folder):  .venv/bin/python check_app.py
Exit code 0 = every page loaded with no exception. The five pages: Home, Findings (opened once per part, each with its
animations), Charts (pictures and animations), Predictions (forecasts) and Galaxies (opened without a picture; the
upload itself can't be done here, so it is checked in a real browser). The animations are web pages shown in a frame (iframe). To check
that they really play in a browser, run notebooks/check_space_anims.py.
"""
import json
import sys
import time
from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parent
index = json.loads((ROOT / "numbers" / "AN_index.json").read_text()) if (ROOT / "numbers" / "AN_index.json").exists() else {}
parts = ["A", "B", "C", "D", "E", "F", "G"]


def count(at, kind: str) -> int:
    n, stack = 0, [at._tree]
    while stack:
        node = stack.pop()
        if getattr(node, "type", None) == kind:
            n += 1
        stack.extend(getattr(node, "children", {}).values() if isinstance(getattr(node, "children", None), dict) else [])
    return n


runs = [("app_pages/home.py", None, None), ("app_pages/findings.py", None, None)] + \
       [("app_pages/findings.py", p, None) for p in parts] + \
       [("app_pages/charts.py", None, None), ("app_pages/charts.py", None, "Animations"),
        ("app_pages/predictions.py", None, None), ("app_pages/galaxies.py", None, None)]
failed = 0
for page, part, radio in runs:
    t0 = time.time()
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=600)
    if part:
        at.query_params["part"] = part
    at.run()
    if page != "app_pages/home.py":
        at.switch_page(page)
        at.run()
    if radio:
        r = at.radio[0]
        r.set_value(next(o for o in r.options if o.startswith(radio))).run()
    errors = [str(e.value)[:500] for e in at.exception]
    n_img, n_anim = count(at, "image"), len(at.get("iframe"))
    if part:
        want = sum(1 for e in index.values() if e.get("part") == part)
    elif page == "app_pages/findings.py" or radio == "Animations":
        want = len(index)                       # these views open on every animation
    else:
        want = None
    bad_count = want is not None and n_anim != want
    status = "OK  " if not errors and not bad_count else "FAIL"
    failed += bool(errors) or bad_count
    label = page + (f" ?part={part}" if part else "") + (f" [{radio}]" if radio else "")
    print(f"{status} {label:38s} {n_img:3d} pictures, {n_anim:3d} animations"
          + (f" (expected {want})" if bad_count else "") + f", {time.time() - t0:5.1f}s")
    for err in errors:
        print("     ", err.replace("\n", "\n      "))
print(f"\n{len(runs) - failed} of {len(runs)} page views loaded with no errors.")
sys.exit(1 if failed else 0)
