# Phase 1: Bench ADC, and an accidental first pull

This phase was supposed to be a quiet bench test: wire the transducer to the Pico, read its voltage with `machine.ADC`, done. It turned into a real debugging saga, and along the way produced the project's first actual captured espresso shot — which failed, in an interesting and useful way.

## Wiring

Per the [hardware notes](../RESOURCES.md): Red (power) β†’ **VBUS** (the transducer needs 5-16VDC, confirmed from its label; VBUS gives raw 5V straight off USB), Black (GND) β†’ **AGND** (a dedicated low-noise ground pin, physically sitting between GP27 and GP28 on the Pico 2 W), Green (signal) β†’ **GP26** (one of three ADC-capable GPIOs β€” GP26/27/28 β€” the only pins wired to the chip's analog-to-digital converter hardware).

First-ever solder job here: tinning the sensor's bare wire ends and the header pins separately, then joining them, to get something that plugs cleanly into a breadboard instead of jamming stranded wire into the holes directly.

## `machine.ADC` basics

`ADC(26)` reads GP26 in analog mode instead of digital on/off. `read_u16()` returns a value 0-65535 representing 0V to the board's 3.3V reference β€” a cross-platform MicroPython convention, regardless of the chip's actual internal resolution. Converting to volts: `voltage = raw_value / 65535 * 3.3`.

## A real unit bug

An early version computed `raw_value * (16/65535)` and printed it labeled `"Pa"`. The `16` there actually represents **16 bar**, not 16 Pascals β€” 1.6 MPa (the sensor's rated max) equals 1,600,000 Pa, but also equals 16 bar exactly (1 MPa = 10 bar). Mixing up "the M in MPa means Γ—1,000,000" with "just drop the M" is an easy trap. Fixed by relabeling to bar, which is also the standard espresso-pressure unit anyway.

## Floating pins: the recurring villain of this phase

Several separate bugs all traced back to the same underlying idea: **an analog pin with nothing solidly connected to it doesn't read 0V β€” it reads an undefined, arbitrary value**, determined by leakage current and capacitive coupling from nearby pins, not by anything meaningful. Critically, that value isn't necessarily wild and jumpy; it can be quite stable, which makes it easy to mistake for a real reading.

Symptoms chased across this phase, all eventually explained by this:
- **Wild blips** (raw values jumping to ~8500 out of nowhere, otherwise a steady 0 baseline) β€” an *intermittent* connection, snapping between solidly-connected and floating.
- **A suspiciously round baseline (~0.66-0.69V)** that matched a "live zero" design theory (many pressure transducers deliberately offset zero-pressure to ~20% of full output range, so a dead sensor reading 0V is distinguishable from a legitimate zero reading) β€” confirmed independently with a multimeter directly on the sensor's wires, so this particular reading turned out to be real.
- **A pin that read ~0.66V even with the sensor fully unplugged from the breadboard** β€” genuinely floating, coincidentally landing near the sensor's real baseline. The giveaway that it was floating rather than real: touching the hole with a finger measurably moved the reading. A solidly-driven signal (low output impedance) can't be perturbed by finger capacitance; a floating (high-impedance) node can.

**Breadboard lesson learned along the way**: the main grid is organized into isolated 5-hole clusters (a wire only connects to the *other* holes in that exact column, not to neighboring columns), while the power rails along the edges run the full length of the board as one shared connection β€” useful for VBUS/GND, but Green needs to land specifically in GP26's own cluster. A wire in the wrong cluster looks physically close but is electrically nothing.

## First real pull: a leak, and a failed hypothesis

With the transducer screwed into a freshly-bought OEM piston-shaft adapter (installed above the lever rather than fighting the machine's original, seized adapter+gauge), a real shot was pulled. The joint fizzed slightly during the pull β€” no PTFE tape had been used. The captured data showed a complete flat line for the entire ~155 second recording, no response at all.

Initial hypothesis: the leak was venting pressure before it reached the sensor. **This didn't hold up** β€” the shot still produced real puck resistance and a drinkable (if underextracted) result, meaning genuine brew-circuit pressure existed; a small leak on a side-branch shouldn't be able to reduce the reading all the way to a flat, unchanged zero. That level of pressure should have shown up as *some* visible response even with a leak present.

The real answer turned out to be electrical, not mechanical: disconnecting the sensor entirely and finding the Pico still read ~0.66V (see floating-pin section above) revealed the connection likely hadn't been solid during the pull either β€” multiple rounds of resoldering and rough handling (threading into the machine with a wrench, heat, vibration) is a much harsher environment for a first-timer's solder joints than sitting still on a desk.

## Second pull: success

After resoldering and fixing a breadboard-cluster placement issue, a second real pull produced a clean, real signal:

```
t=105-108s: baseline noise (~0.01-0.04V)
t=108-116s: clear rise
t=116.5s:   peak, 1.53V β†’ ~7.4 bar (using corrected calibration below)
t=117s+:    smooth, gradual decay over the next ~60s
```

This shape β€” flat, then a rise, a sharp peak, then a long decay β€” is exactly what a real lever-machine pressure curve should look like, anchored at a believable peak pressure. Full analysis in [`analysis/first_shot.ipynb`](../analysis/first_shot.ipynb).

## Calibration correction

The real pull data showed the resting baseline genuinely sits near **0V**, not the ~0.66V "live zero" theory from earlier in this phase (that reading turned out to be a floating-pin artifact after all, once cross-checked against a full real pull rather than a single ambiguous voltage snapshot). Calibration was corrected to the simpler assumption: **0V = 0 bar, 3.3V = 16 bar** (the sensor's rated max) β€” `pressure_bars = voltage / 3.3 * 16`.

## First result: a sour shot, explained

The pull peaked at **~7.4 bar**, short of the ~9 bar target, and spent only **~2.7 seconds** above a 6 bar "meaningfully extracting" threshold before decaying away. The shot tasted sour (underextracted) β€” which now has a measured, specific explanation instead of just a guess: insufficient pressure, held for too short a time. First real link between a felt outcome and a captured cause.

## Open items going into later phases

- Never did the originally-planned isolated bench dynamic test (blow tube / syringe) before jumping to a real machine pull β€” got lucky that the real pull data was clean enough to reason about directly.
- No PTFE tape used on the current install β€” the leak should still get fixed properly before more pulls, independent of it turning out not to be the root cause this time.
- Calibration is still a rough single-assumption line (0V/3.3V endpoints), not a real two-point calibration against a reference gauge β€” a good candidate for when Phase 2 is tackled properly.
