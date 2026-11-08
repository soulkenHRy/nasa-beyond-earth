"""Check that every space-sketch animation really plays in a browser (headless Chrome, plain 2D canvas, no WebGL).

For each animations/Fnn_*.html: the page opens with the finished picture and no errors, a real mouse click on
▶ Play starts it, it runs to the end, and it stops on the finished picture again.

    cd notebooks && ../.venv/bin/python check_space_anims.py                 # all 32
    cd notebooks && ../.venv/bin/python check_space_anims.py --only 1 2 --shots /tmp/shots
"""
from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from browser import Browser

ROOT = Path(__file__).resolve().parent.parent


async def check_one(b: Browser, e: dict, shots: Path | None) -> tuple[bool, str]:
    n = int(e["n"])
    b.console.clear()
    await b.open((ROOT / e["html"]).as_uri(), ready="window.__anim && document.readyState === 'complete'")
    s0 = await b.js("JSON.stringify({T: __anim.T, started: __anim.started, errors: __anim.errors, "
                    "webgl: !!document.querySelector('canvas') && typeof Plotly === 'undefined', "
                    "keys: document.querySelectorAll('#keys li').length, "
                    "hidden: document.querySelectorAll('#keys li.hide').length})")
    s0 = json.loads(s0)
    if shots:
        await b.screenshot(str(shots / f"F{n:02d}_a_before.png"))
    r = json.loads(await b.js("JSON.stringify(document.getElementById('play').getBoundingClientRect())"))
    await b.click(r["x"] + r["width"] / 2, r["y"] + r["height"] / 2)
    T = s0["T"]
    started = await b.wait_for("__anim.started && __anim.playing", timeout=5, every=0.1)
    await b.wait_for(f"__anim.t >= {T * 0.5}", timeout=T + 20, every=0.2)
    if shots:
        await b.screenshot(str(shots / f"F{n:02d}_b_middle.png"))
    done = await b.wait_for("!__anim.playing && __anim.t >= __anim.T", timeout=T + 30, every=0.25)
    s1 = json.loads(await b.js("JSON.stringify({t: __anim.t, frames: __anim.frames, errors: __anim.errors, "
                               "hidden: document.querySelectorAll('#keys li.hide').length, "
                               "button: document.getElementById('play').textContent})"))
    if shots:
        await b.screenshot(str(shots / f"F{n:02d}_c_end.png"))
    errs = s0["errors"] + s1["errors"] + [c for c in b.console if "EXCEPTION" in c or "rror" in c]
    ok = (not s0["started"] and s0["hidden"] == 0 and s0["keys"] > 0 and started and done and s1["frames"] > 30
          and s1["hidden"] == 0 and not errs)
    msg = (f"F{n:02d} {'OK ' if ok else 'BAD'} {s1['frames']:4d} frames in {T:4.1f}s, {s0['keys']} key lines, "
           f"ends on the full picture: {s1['hidden'] == 0}, button now '{s1['button']}'"
           + (f"  ERRORS: {errs[:3]}" if errs else ""))
    return ok, msg


async def worker(items: list, shots: Path | None, out: list) -> None:
    async with Browser(1280, 900) as b:
        for e in items:
            try:
                out.append(await check_one(b, e, shots))
            except Exception as ex:  # noqa: BLE001
                out.append((False, f"F{int(e['n']):02d} BAD {type(ex).__name__}: {ex}"))
            print(out[-1][1], flush=True)


async def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", type=int, nargs="*")
    ap.add_argument("--shots", type=Path)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    idx = json.loads((ROOT / "numbers" / "AN_index.json").read_text())
    items = [e for e in idx.values() if not a.only or int(e["n"]) in a.only]
    if a.shots:
        a.shots.mkdir(parents=True, exist_ok=True)
    out: list = []
    k = max(1, min(a.workers, len(items)))
    await asyncio.gather(*(worker(items[i::k], a.shots, out) for i in range(k)))
    good = sum(ok for ok, _ in out)
    print(f"{good} of {len(items)} animations played to the end with no errors."
          + (" All checks passed." if good == len(items) else " SOME FAILED."))


if __name__ == "__main__":
    asyncio.run(main())
