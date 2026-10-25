"""Shared shot analysis: find the shot in a Pico log file and measure it.

Used by shot_analysis.ipynb (one shot in depth), compare_shots.ipynb (several
shots side by side) and build_shot_viewer.py (the shot viewer page).

Every log has a one-letter `phase` column (i, p, e, d): the current Pico script
writes it, and older recordings had it added by backfill_phases.py using the
same rules (pico_phases). A file without it still loads: its phases are worked
out on the fly.
"""

import numpy as np
import pandas as pd

TARGET_BAR = 9       # what we're aiming for
THRESHOLD_BAR = 6    # "meaningful extraction" cutoff
START_BAR = 1.0      # pre-infusion ends and extraction begins here
SHOT_ON_BAR = 0.1    # a shot starts when pressure first rises above this (as on the Pico)

PHASES = ["pre-infusion", "extraction", "dripping"]
# the Pico logs one letter per row; full names are also accepted
PHASE_CODES = {"i": "idle", "p": "pre-infusion", "e": "extraction", "d": "dripping"}


# The Pico's start and end rules (pico/pressure_display.py), for replaying them over a recording
CONFIRM_BAR = 0.3     # a rise above SHOT_ON_BAR only counts as a shot once it passes this
CONFIRM_WINDOW = 35   # readings a rise has to confirm in (the Pico's pre-roll + confirm window)
END_S = 3.0           # below SHOT_ON_BAR this long ends a shot...
MAX_DRIP_S = 60.0     # ...or dripping this long


def pico_phases(t, bar):
    """Replay the Pico's phase rules over a recording: one letter per reading.

    i idle, p pre-infusion, e extraction, d dripping. Mirrors pico/pressure_display.py:
    t = 0 is the first reading of a rise above SHOT_ON_BAR, confirmed once it passes
    CONFIRM_BAR; extraction from the first reading at START_BAR; dripping from the
    first drop below THRESHOLD_BAR once reached (below START_BAR if it never was); the
    shot ends after END_S below SHOT_ON_BAR or MAX_DRIP_S of dripping. A rise that
    never reaches extraction is a false start and stays idle, as the Pico discards it.
    """
    t, bar = list(t), list(bar)
    out = ["i"] * len(t)
    phase, armed, cand = "i", True, None
    for k, (now, b) in enumerate(zip(t, bar)):
        if phase == "i":
            if b <= SHOT_ON_BAR:
                armed, cand = True, None
            elif armed:
                if cand is None or k - cand >= CONFIRM_WINDOW:
                    cand = k
                if b >= CONFIRM_BAR:
                    first = cand
                    out[cand:k + 1] = ["p"] * (k + 1 - cand)
                    phase, reached, low_since, got_extraction = "p", False, None, False
            continue
        if phase == "p" and b >= START_BAR:
            phase, got_extraction = "e", True
        elif phase == "e":
            if b >= THRESHOLD_BAR:
                reached = True
            if b < (THRESHOLD_BAR if reached else START_BAR):
                phase, drip_start = "d", now
        out[k] = phase
        low_since = (low_since if low_since is not None else now) if b < SHOT_ON_BAR else None
        if (low_since is not None and now - low_since >= END_S) or (phase == "d" and now - drip_start >= MAX_DRIP_S):
            if not got_extraction:
                out[first:k + 1] = ["i"] * (k + 1 - first)
            phase, armed, cand = "i", b <= SHOT_ON_BAR, None
    return out


def _load(path):
    """-> (the first shot, t = 0 at its start; resting baseline; whether the file had phases)."""
    raw = pd.read_csv(path)
    logged = "phase" in raw.columns
    if logged:
        raw["phase"] = raw["phase"].replace(PHASE_CODES)
    else:
        raw["phase"] = pd.Series(pico_phases(raw["t"], raw["bar"])).replace(PHASE_CODES)

    in_shot = raw["phase"] != "idle"
    first = in_shot.idxmax()                          # first row of the first shot
    after = (~in_shot) & (raw.index > first)
    last = after.idxmax() - 1 if after.any() else raw.index[-1]
    t0 = raw.loc[first, "t"]
    before = raw[(raw.index < first) & (raw["phase"] == "idle")]
    baseline = before["bar"].mean() if len(before) else raw["bar"].min()

    df = raw.loc[first:last].reset_index(drop=True).rename(columns={"t": "t_log"})
    df.insert(0, "t", (df["t_log"] - t0).round(2))
    return df, baseline, logged


def analyse(path):
    """Find the shot in a log file and work out its key numbers.

    Times in the returned frame are seconds into the shot: t = 0 is the first
    reading above SHOT_ON_BAR (the start of pre-infusion, as on the Pico's
    screen). Every row carries its phase.
    """
    df, baseline, logged = _load(path)

    active = df[df["bar"] >= START_BAR]
    shot_start, shot_end = active["t"].min(), active["t"].max()

    peak = df.loc[df["bar"].idxmax()]
    dt = df["t"].diff()
    above = df["bar"] >= THRESHOLD_BAR
    ext_start, ext_end = df.loc[above, "t"].min(), df.loc[above, "t"].max()
    in_zone = (df["t"] >= ext_start) & (df["t"] <= ext_end)

    starts = {p: df.loc[df["phase"] == p, "t"].min() for p in PHASES}
    extraction_start, drip_start = starts["extraction"], starts["dripping"]
    end = df["t"].iloc[-1]
    pre = df[df["phase"] == "pre-infusion"]

    # area under the curve (bar*s), measured above the resting baseline so idle
    # time after the shot adds ~nothing and the padding doesn't matter
    excess = (df["bar"] - baseline).clip(lower=0)

    def area(t0, t1):
        sel = (df["t"] >= t0) & (df["t"] <= t1)
        return np.trapezoid(excess[sel], df["t"][sel])

    return df, {
        "phases_logged": logged,
        "baseline_bar": baseline,
        "sample_interval_s": df["t"].diff().median(),
        "preinfusion_s": extraction_start,
        "preinfusion_bar": pre["bar"].mean(),
        "extraction_s": (drip_start if drip_start == drip_start else end) - extraction_start,
        "dripping_s": end - drip_start if drip_start == drip_start else 0.0,
        "timer_s": drip_start if drip_start == drip_start else end,   # what the screen's timer shows
        "ramp_s": ext_start - shot_start,                                # 1 bar -> 6 bar
        "zone_mean_bar": df.loc[in_zone, "bar"].mean(),
        "fall_s": shot_end - ext_end,                                    # 6 bar -> 1 bar
        "shot_duration_s": shot_end - shot_start,
        "peak_bar": peak["bar"],
        "peak_t": peak["t"],
        "meaningful_s": dt[above].sum(),
        "at_target_s": dt[df["bar"] >= TARGET_BAR].sum(),
        "extraction_start": ext_start,
        "extraction_end": ext_end,
        "area_before": area(df["t"].iloc[0], ext_start),
        "area_extraction": area(ext_start, ext_end),
        "area_after": area(ext_end, end),
        "area_total": area(df["t"].iloc[0], end),
    }


def phase_rows(df):
    """One row per phase: when it started, how long it lasted, its pressure, and how
    much of it was meaningful (at or above THRESHOLD_BAR)."""
    rows = []
    dt = df["t"].diff()
    for p in PHASES:
        part = df[df["phase"] == p]
        if part.empty:
            continue
        later = df.loc[df["t"] > part["t"].max(), "t"]
        until = later.min() if len(later) else part["t"].max()   # next phase's start, or the end
        rows.append({
            "phase": p,
            "from_s": round(part["t"].min(), 1),
            "duration_s": round(until - part["t"].min(), 1),
            "avg_bar": round(part["bar"].mean(), 2),
            "peak_bar": round(part["bar"].max(), 2),
            # unrounded, so it rounds the same as the shot's own meaningful time wherever it's shown
            "meaningful_s": round(dt[part.index][part["bar"] >= THRESHOLD_BAR].sum(), 3),
        })
    return pd.DataFrame(rows)


# rows for comparison tables: label -> (metric key or function, format)
COMPARISON_ROWS = {
    "shot timer: pre-infusion + extraction (s)": ("timer_s", "{:.1f}"),
    "pre-infusion (s)": ("preinfusion_s", "{:.1f}"),
    "pre-infusion pressure (bar)": ("preinfusion_bar", "{:.2f}"),
    "extraction (s)": ("extraction_s", "{:.1f}"),
    "dripping (s)": ("dripping_s", "{:.1f}"),
    "ramp, 1 to 6 bar (s)": ("ramp_s", "{:.1f}"),
    "meaningful extraction, >= 6 bar (s)": ("meaningful_s", "{:.1f}"),
    "average pressure in that zone (bar)": ("zone_mean_bar", "{:.2f}"),
    "peak (bar)": ("peak_bar", "{:.2f}"),
    "peak at (s into shot)": ("peak_t", "{:.1f}"),
    "at target, >= 9 bar (s)": ("at_target_s", "{:.1f}"),
    "fall, 6 to 1 bar (s)": ("fall_s", "{:.1f}"),
    "area, highlighted zone (bar*s)": ("area_extraction", "{:.0f}"),
    "area, all other (bar*s)": (lambda r: r["area_before"] + r["area_after"], "{:.0f}"),
    "share of area in highlighted zone": (lambda r: r["area_extraction"] / r["area_total"], "{:.0%}"),
    "logging interval (s)": ("sample_interval_s", "{:.2f}"),
}


def comparison_table(results):
    """results: {column name: metrics dict from analyse()} -> formatted DataFrame."""
    def value(r, key):
        return key(r) if callable(key) else r[key]

    return pd.DataFrame(
        {name: [fmt.format(value(r, k)) for k, fmt in COMPARISON_ROWS.values()] for name, r in results.items()},
        index=list(COMPARISON_ROWS),
    )
