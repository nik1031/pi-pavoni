# Analysis

Laptop-side analysis of the shot logs the Pico writes (`shots/shot_NNN.csv` on the Pico).

## Layout

| Path | What it is |
| --- | --- |
| `data/` | Shot logs copied off the Pico, plus `shot_notes.csv` (beans, grind, dose, yield, comments per shot) |
| `shotlib.py` | The shared analysis: finds the shot in a log, works out phases, meaningful extraction (time at or above 6 bar), areas and the rest |
| `first_shot.ipynb` | Phase 1: the first captured pull, analysed on its own |
| `shot_analysis.ipynb` | One shot in depth (shot_010), compared with the first |
| `compare_shots.ipynb` | Several shots side by side, with their notes |
| `figures/` | Charts the notebooks save |
| `viewer/` | The shot viewer page: `shot_viewer_template.html` is the source, `shot_viewer.html` is built from it with the data embedded |
| `build_shot_viewer.py` | Builds `viewer/shot_viewer.html` from the template, `data/` and `shotlib.py` |
| `check_viewer_analysis.py` | Checks the viewer's in-browser analysis (used for uploaded shots) gives the same numbers as `shotlib.py` |
| `backfill_phases.py` | Adds the one-letter `phase` column to logs recorded before the Pico wrote it |

## Log format

One file per shot, one row per reading:

```
t,raw,voltage,bar,phase
```

`phase` is `i` idle, `p` pre-infusion, `e` extraction or `d` dripping. A few idle rows before the shot starts are kept as a resting baseline.

## Adding a shot

1. Copy the new CSV from the Pico's `shots/` folder into `data/`.
2. Add a row for it to `data/shot_notes.csv` (optional).
3. Rebuild the viewer, and re-run the comparison notebook if you want it updated:

```
../.venv/bin/python build_shot_viewer.py
../.venv/bin/jupyter nbconvert --to notebook --execute --inplace compare_shots.ipynb
```

The published viewer also has an **Add shot** button that takes a CSV directly, without any of this.

If you change the rules in `shotlib.py`, make the same change in the analysis block of `viewer/shot_viewer_template.html` and run `check_viewer_analysis.py`.
