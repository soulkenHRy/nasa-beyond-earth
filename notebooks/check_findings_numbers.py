"""Check that every number in FINDINGS.md matches a file in numbers/.

The file is cut into blocks: the front page, each part's "Meet the data", each finding (### n.), and the master word
list. In every block, every number-like token must be one of:
  (a) a 'shown' text from any fact table (numbers/BFnn_*.csv or numbers/BM_<part>_*.csv), exactly as written, or
  (b) the same value as a fact in that block's own table (finding n: numbers/BFnn_*.csv; Meet the data: that part's
      numbers/BM_<part>_*.csv; both may also use numbers/BF00_shared_facts.csv), at the precision shown, or
  (c) a year (1900-2200) that appears as a cell in some numbers/*.csv file.
Skipped: list numbers ("1. "), the finding number in its heading, file paths in backticks and image links.
Exit code 1 if anything is unmatched. On the real file it also writes numbers/BF_guide_differences.csv: every
"Note: the guide said X; our data gives Y." line.

Usage (from the project folder):
  .venv/bin/python notebooks/check_findings_numbers.py              # FINDINGS.md
  .venv/bin/python notebooks/check_findings_numbers.py --md X.md    # a test file from make_findings.py --out
"""
import argparse
import csv
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import helpers as hp  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--md", default=str(hp.PROJECT / "FINDINGS.md"))
args = ap.parse_args()
md_path = Path(args.md)
REAL = md_path.resolve() == (hp.PROJECT / "FINDINGS.md").resolve()
md = md_path.read_text()

shown_all, values = set(), {}
for f in sorted(hp.NUMBERS.glob("BF[0-9][0-9]_*.csv")) + sorted(hp.NUMBERS.glob("BM_[A-G]_*.csv")):
    t = pd.read_csv(f, dtype={"shown": str})
    if "shown" not in t.columns:
        continue
    key = int(f.name[2:4]) if f.name.startswith("BF") else f"M{f.name[3]}"
    shown_all |= set(t["shown"].dropna().astype(str))
    values[key] = pd.to_numeric(t["value"], errors="coerce").dropna().tolist()
years_in_files = set()
for f in hp.NUMBERS.glob("*.csv"):
    with open(f, newline="") as fh:
        for row in csv.reader(fh):
            for cell in row:
                if re.fullmatch(r"(19|20|21)\d\d(\.0)?", cell.strip()):
                    years_in_files.add(int(float(cell)))

# shown texts that are not plain numbers (dates, times, names with digits) are hidden before the numbers are read
composite = sorted((s for s in shown_all if re.search(r"\d", s) and not re.fullmatch(r"[+\-−]?[\d,]*\.?\d*%?", s)),
                   key=len, reverse=True)
TOKEN = re.compile(r"[+\-−]?\d[\d,]*(?:\.\d+)?%?")


def value_ok(tok: str, keys: list) -> bool:
    raw = tok.replace("−", "-").replace(",", "").rstrip("%")
    try:
        v = float(raw)
    except ValueError:
        return False
    dec = len(raw.split(".")[1]) if "." in raw else 0
    for k in keys:
        for cand in values.get(k, []):
            for c in (cand, -cand):
                if round(c, dec) == v or (dec == 0 and float(round(c)) == v):
                    return True
    return False


def check(text: str, keys: list, label: str):
    bad = []
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)                       # image links
    text = re.sub(r"`[^`]*(?:\.csv|\.png|\.py|\.md|/)[^`]*`", " ", text)    # file paths
    text = re.sub(r"(?m)^(?:###\s+)?\d+\.\s", " ", text)                    # list numbers and the finding number
    for s in composite:
        text = text.replace(s, " ")
    for m in TOKEN.finditer(text):
        tok = m.group(0).rstrip(",")
        if not re.search(r"\d", tok):
            continue
        plain = tok.replace("−", "-")
        if tok in shown_all or plain in shown_all or plain.lstrip("+-") in shown_all:
            continue
        if value_ok(tok, keys):
            continue
        if re.fullmatch(r"(19|20|21)\d\d", plain) and int(plain) in years_in_files:
            continue
        ctx = text[max(0, m.start() - 50):m.end() + 25].replace("\n", " ")
        bad.append((label, tok, ctx))
    return bad


# ----------------------------------------------------------------------------- cut into blocks
blocks, part, cur = [], None, {"label": "front page", "keys": [0], "lines": [], "n": None}
for line in md.splitlines():
    m_part = re.match(r"## Part ([A-G]):", line)
    m_meet = re.match(r"### Meet the data", line)
    m_find = re.match(r"### (\d+)\. ", line)
    m_words = line.startswith("## Master word list")
    if m_part or m_meet or m_find or m_words:
        blocks.append(cur)
        if m_part:
            part = m_part.group(1)
            cur = {"label": f"part {part} heading", "keys": [0], "lines": [], "n": None}
        elif m_meet:
            cur = {"label": f"part {part}: Meet the data", "keys": [f"M{part}", 0], "lines": [], "n": None}
        elif m_find:
            n = int(m_find.group(1))
            cur = {"label": f"finding {n}", "keys": [n, 0, f"M{part}"], "lines": [], "n": n}
        else:
            cur = {"label": "master word list", "keys": [0], "lines": [], "n": None}
    cur["lines"].append(line)
blocks.append(cur)

problems, notes, n_tokens, n_findings, n_meet = [], [], 0, 0, 0
for b in blocks:
    text = "\n".join(b["lines"])
    n_tokens += len(TOKEN.findall(text))
    problems += check(text, b["keys"], b["label"])
    if b["n"] is not None:
        n_findings += 1
        title = b["lines"][0].split(". ", 1)[1]
        for line in b["lines"]:
            if line.startswith("Note:"):
                notes.append({"finding": b["n"], "title": title, "note": line[len("Note: "):]})
    elif "Meet the data" in b["label"]:
        n_meet += 1
if REAL:
    pd.DataFrame(notes, columns=["finding", "title", "note"]).to_csv(hp.NUMBERS / "BF_guide_differences.csv", index=False)

print(f"{md_path.name}: {n_findings} findings, {n_meet} 'Meet the data' parts; number tokens checked: {n_tokens}")
if problems:
    print(f"UNMATCHED numbers: {len(problems)}")
    for label, tok, ctx in problems:
        print(f"  [{label}] {tok!r}  ...{ctx}...")
    sys.exit(1)
print(f"Every number in {md_path.name} matches a file in numbers/.")
print(f"Differences from the guide: {len(notes)}" + (" (numbers/BF_guide_differences.csv)" if REAL else ""))
for x in notes:
    print(f"  {x['finding']}. {x['note']}")
