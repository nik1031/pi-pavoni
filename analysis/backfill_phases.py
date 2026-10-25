"""Add the Pico's one-letter phase column to shot logs recorded before it had one.

Applies the same rules as pico/pressure_display.py (shotlib.pico_phases). Rows and
times are kept exactly as recorded; only a `phase` column is added (i idle,
p pre-infusion, e extraction, d dripping). Files that already have it are left alone.

    ../.venv/bin/python backfill_phases.py
"""

from pathlib import Path

import pandas as pd

from shotlib import pico_phases

DATA = Path(__file__).parent / "data"

for path in sorted(DATA.glob("*.csv")):
    if path.name == "shot_notes.csv":
        continue
    raw = pd.read_csv(path, dtype=str)            # as text, so every value is written back unchanged
    if "phase" in raw.columns:
        print(f"{path.name}: already has phases")
        continue
    raw["phase"] = pico_phases(raw["t"].astype(float), raw["bar"].astype(float))
    raw.to_csv(path, index=False)
    counts = raw["phase"].value_counts()
    print(f"{path.name}: added phases (" + ", ".join(f"{k} {counts.get(k, 0)}" for k in "iped") + ")")
