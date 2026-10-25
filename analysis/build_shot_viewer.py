"""Build viewer/shot_viewer.html: pick any shot in data/ and see its analysis.

The numbers come from shotlib.analyse(), the same code the notebooks use, so
the page always agrees with them. Re-run after adding shots to data/:

    ../.venv/bin/python build_shot_viewer.py
"""

import json
from pathlib import Path

import pandas as pd

from shotlib import analyse, phase_rows, TARGET_BAR, THRESHOLD_BAR, START_BAR

HERE = Path(__file__).parent
DATA = HERE / "data"


def main():
    notes = pd.read_csv(DATA / "shot_notes.csv", dtype=str).fillna("").set_index("shot")

    shots = []
    for path in sorted(DATA.glob("*.csv")):
        if path.name == "shot_notes.csv":
            continue
        try:
            df, m = analyse(path)
        except Exception as e:   # a file with no shot in it, a partial download, ...
            print(f"skipped {path.name}: {e}")
            continue
        name = path.stem
        shots.append({
            "name": name,
            "t": df["t"].round(2).tolist(),
            "bar": df["bar"].round(2).tolist(),
            "phase": df["phase"].tolist(),
            "phases": phase_rows(df).to_dict("records"),
            "metrics": {k: round(float(v), 3) for k, v in m.items()},
            "notes": notes.loc[name].to_dict() if name in notes.index else {},
        })
        print(f"{name}: peak {m['peak_bar']:.2f} bar, {m['meaningful_s']:.1f}s above {THRESHOLD_BAR} bar")

    payload = {"target": TARGET_BAR, "threshold": THRESHOLD_BAR, "start": START_BAR, "shots": shots}
    template = (HERE / "viewer" / "shot_viewer_template.html").read_text(encoding="utf-8")
    page = template.replace("/*SHOT_DATA*/null", json.dumps(payload, ensure_ascii=False))
    (HERE / "viewer" / "shot_viewer.html").write_text(page, encoding="utf-8")
    print(f"wrote viewer/shot_viewer.html with {len(shots)} shots")


if __name__ == "__main__":
    main()
