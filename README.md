# Pi Pavoni

Instrumenting a fully manual La Pavoni lever espresso machine with a Raspberry Pi Pico 2 W to capture and analyze its extraction pressure curve — and learning MicroPython along the way.

🚧 **Work in progress.** Currently on Phase 0 (toolchain) of the build. See [Build log](#build-log) below.

## TL;DR

A fully manual La Pavoni lever espresso machine has no electronics — you generate brew pressure by hand, and the only feedback is an analog gauge you can't record or replay. This project screws a pressure transducer into the group head, reads it with a Raspberry Pi Pico 2 W, and streams the pressure curve over Bluetooth to a laptop so shots can actually be logged, compared, and (eventually) used to figure out what a great pull looks like versus a bad one. Also doubling as a from-scratch MicroPython learning project — see [Why](#why) and [The idea](#the-idea) for the full story, [SHOPPING_LIST.md](SHOPPING_LIST.md) for hardware, and [Build log](#build-log) for current progress.

## Why

I'm obsessed with coffee. It started with an AeroPress and a V60, and eventually escalated into wanting an espresso machine — which led me down a very niche rabbit hole: old-school, fully manual lever machines. No pump, no electronics, just you and a spring (or not even a spring) pushing hot water through coffee by hand.

Learning to pull a decent shot on a La Pavoni took a long time. And here's the thing — even on the higher-end models, which have **two** pressure gauges (one on the boiler, one on the group head), you're still mostly operating on feel. Sometimes everything about your prep — dose, grind, tamp, timing — looks identical to the shot that tasted amazing yesterday, and today it comes out either badly over-extracted or bitter and undrinkable. It can feel like the outcome depends on the phase of the moon rather than anything you actually controlled.

The gauges tell you *a* number, but not the shape of what happened during the shot — how pressure built, held, or spiked as you pulled the lever. That curve is where the actual story of a good or bad shot lives, and no analog gauge shows it to you in a way you can review, compare, or learn from.

So: this project is an attempt to actually capture that curve — wire a pressure transducer into the group head, read it with a Raspberry Pi Pico 2 W, stream it out, and start building a real picture of what a good pull looks like versus a bad one. It's also my excuse to actually learn MicroPython properly instead of just reading about it.

## The idea

I work in data engineering, and I'm using this project to properly learn software engineering. Somewhere along the way I decided I wanted to make a fully manual, fully analog lever machine into the most precise espresso machine I possibly could — which is a bit of a contradiction, since manual lever machines exist specifically *because* there's no electronics in the loop. Part of the fun is embracing that contradiction anyway.

There are machines out there — like the Decent Espresso DE1 — that ship with their own touchscreen specifically to shape and review extraction profiles in real time, at a price that puts them well out of reach for most people learning espresso. The goal of Pi Pavoni is to bring a version of that same idea to a much cheaper, much more manual machine: instrument it, capture what's actually happening during a shot, and use the data to build a real understanding of what "good" looks like — instead of guessing based on feel.

Right now that means one variable: **pressure over time**, streamed off the machine during a pull. Later it might grow to include temperature, and maybe others — the point isn't to hit a fixed spec on day one, it's to keep expanding the picture until there's enough data across enough pulled shots to start finding real patterns: what does the pressure curve of a great shot actually look like, versus one that turns out like soy sauce? If that pattern exists and we can capture it, the plan is to turn it into concrete guidance for someone still learning to pull shots on a machine like this — not just "here's a graph," but "your pressure spiked too early, ease off the lever."

No idea yet how far this actually goes. But that's the shape of where it's headed.

## How it works

At a high level:

```
[pressure transducer] --analog--> [Pico 2 W ADC] --BLE--> [laptop client] --> logs / plots
```

The Pico samples the transducer during a shot and streams readings over Bluetooth Low Energy; a Python script on the laptop (using `bleak`) receives and records them for analysis. More detail on each piece lives in the build log below as it gets built.

## Hardware

Bill of materials, links, and open questions (thread sizes, adapters, etc.) are tracked in [SHOPPING_LIST.md](SHOPPING_LIST.md).

## Build log

Following along phase by phase — each one gets its own writeup under `docs/` once it's done.

- [x] **Phase 0** — Toolchain: flash MicroPython, REPL, blink the onboard LED ([writeup](docs/00-toolchain.md))
- [ ] **Phase 1** — Bench ADC: read the transducer's voltage on the bench, unplugged from the machine
- [ ] **Phase 2** — Calibration & sampling loop: voltage → bar, polling vs. timer-driven sampling
- [ ] **Phase 3** — BLE peripheral: advertise a GATT service, stream bench data
- [ ] **Phase 4** — Laptop client: `bleak`, buffering, live plotting
- [ ] **Phase 5** — Physical install: sensor into the machine for real
- [ ] **Phase 6** — Real shots + analysis: actual pressure curves, comparing pulls

## Getting started

_(Fills in once there's working code — for now, see the build log above for current status.)_

## Safety notes

This project involves modifying a pressurized, near-boiling-water appliance and wiring electronics near it. If you're following along: work on the machine unplugged and depressurized, mind the temperatures involved, and use your own judgment — this is a hobby project, not a certified appliance modification, and I take no responsibility for what you do to your own machine.

## Credits

- [Gaggiuino](https://github.com/Zer0-bit/gaggiuino) — the pressure/flow profiling mod for Gaggia machines that inspired this project
- The home-barista.com and La Pavoni communities for prior art on gauge threads, adapters, and lever machine mods

## License

MIT
