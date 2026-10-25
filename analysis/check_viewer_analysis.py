"""Check the shot viewer's in-browser analysis (used for uploaded shots) agrees with shotlib.py.

Runs the page's analysis code under Node on every shot in data/ and compares each
metric and phase row with shotlib's. Re-run after changing either one:

    ../.venv/bin/python check_viewer_analysis.py
"""

import json
import math
import re
import subprocess
from pathlib import Path

from shotlib import analyse, phase_rows

HERE = Path(__file__).parent
TOLERANCE = 0.011   # times are rounded to 0.01 s on both sides; allow one rounding step

page = (HERE / "viewer" / "shot_viewer_template.html").read_text(encoding="utf-8")
js = re.search(r"// ---- ANALYSIS START.*?// ---- ANALYSIS END ----", page, re.S).group(0)

files = sorted(p for p in (HERE / "data").glob("*.csv") if p.name != "shot_notes.csv")
runner = js + """
const fs = require("fs");
const out = {};
for (const f of JSON.parse(process.argv[1])) out[f] = analyseShot(parseShotCsv(fs.readFileSync(f, "utf8")));
console.log(JSON.stringify(out));
"""
browser = json.loads(subprocess.run(["node", "-e", runner, json.dumps([str(f) for f in files])],
                                    capture_output=True, text=True, check=True).stdout)


def close(a, b):
    if isinstance(a, str) or isinstance(b, str):
        return a == b
    a, b = float(a), float(b)
    return (math.isnan(a) and math.isnan(b)) or abs(a - b) <= TOLERANCE


problems = 0
for f in files:
    df, m = analyse(f)
    got = browser[str(f)]
    for k, v in got["metrics"].items():
        if not close(m[k], v if v is not None else float("nan")):
            print(f"{f.name}: {k} python {m[k]} vs browser {v}")
            problems += 1
    rows = phase_rows(df).to_dict("records")
    if len(rows) != len(got["phases"]):
        print(f"{f.name}: {len(rows)} phases in python vs {len(got['phases'])} in browser")
        problems += 1
    for py, br in zip(rows, got["phases"]):
        for k in py:
            if not close(py[k], br[k]):
                print(f"{f.name}: {py['phase']} {k} python {py[k]} vs browser {br[k]}")
                problems += 1
    if list(df["phase"]) != got["phase"]:
        print(f"{f.name}: per-reading phases differ")
        problems += 1
    print(f"{f.name}: {len(got['metrics'])} metrics, {len(got['phases'])} phases, {len(got['phase'])} readings checked")

print("browser and python analysis agree" if problems == 0 else f"{problems} differences")
