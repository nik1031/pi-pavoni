# Shopping List

Materials for the La Pavoni pressure-profiling project (Pico 2 W + pressure transducer, streamed over BLE to a laptop).

## Already have

- [x] Pressure transducer — [G1/8 ceramic sensor, 0-1.6MPa range, 0-3.3V output variant](https://www.aliexpress.com/item/1005004559608411.html)
  - Wiring: Red = Power (needs 5V, see hardware notes), Black = GND, Green = Signal
  - Comes with an attached cable already

## Core electronics

- [ ] **Raspberry Pi Pico 2 W** — check if you already have one before buying.
  - [Official Raspberry Pi product page](https://www.raspberrypi.com/products/raspberry-pi-pico-2/)
  - [Pimoroni](https://shop.pimoroni.com/en-us/products/raspberry-pi-pico-2-w)
  - [PiShop US](https://www.pishop.us/product/raspberry-pi-pico-2-w/)
  - [Micro Center](https://www.microcenter.com/product/687384/raspberry-pi-pico-2-w)
  - Note: comes without header pins — either get one pre-soldered, or buy 2×20 0.1" male header pins separately if you plan to solder your own (needed for breadboard use; not needed if you wire directly).
- [ ] **Micro-USB cable** (data-capable, not charge-only) — for flashing MicroPython and for bench power via VBUS (5V). The Pico 2 W keeps the same micro-USB port as the original Pico.
- [ ] **Breadboard + jumper wire kit (M-M, M-F, F-F assortment)** — for prototyping the wiring before anything is permanent or installed in the machine.
- [ ] **Multimeter** — for verifying the transducer's pinout and output voltage ceiling before connecting it to the Pico, and general debugging. Skip if you already own one.
- [ ] **Small resistor assortment kit (or just a handful of 1kΩ)** — for a series protection resistor between the transducer's signal wire and the Pico's ADC pin.

## Plumbing / mechanical

- [ ] **PTFE (Teflon) thread seal tape** — for sealing the transducer into the group head port. Standard for espresso machine fittings.
- [x] **La Pavoni Esperto Piston Shaft Pressure Gauge Adapter** (OEM part 2124013451, confirmed for Esperto Abile/Competente/Edotto) — [The Espresso Shop](https://theespressoshop.com/products/esperto-piston-shaft-pressure-gauge-adapter-2124013451?variant=48557254017356)
  - Mounts to the piston shaft, not a simple group-head port — different mechanism than assumed, still brew-side pressure.
  - **Open question:** the gauge-facing thread size wasn't listed on the product page, so it's not yet confirmed whether it lands on G1/8 (matching the transducer) or something else. Check by measuring once it arrives, or ask the seller, before assuming no further adapter is needed.
- [ ] Small adjustable spanner/wrench sized for the fitting, to remove the old gauge and thread in the transducer.

## Tools (skip anything you already own)

- [ ] Soldering iron + solder — if you solder header pins to the Pico or make permanent wire connections.
- [ ] Wire strippers/small side cutters.
- [ ] Small heat-shrink tubing or electrical tape — for insulating/protecting solder joints near the machine.

## Later phases (not needed yet — for untethered/BLE operation once bench testing works)

- [ ] **5V power source for the sensor once off USB** — e.g. a small USB power bank, or a 5V buck/boost regulator if powering from another supply. The transducer needs ~5V; the Pico itself can run from a wider range via VSYS, but the sensor specifically wants 5V on its Red wire.
- [ ] Small project enclosure/case for the Pico, mounted somewhere on/near the machine away from direct heat.

## Notes

- Don't buy the group-head adapter yet — confirm the thread match first (measure the existing gauge's fitting, or check what comes off when you remove it).
- This list will grow as we hit each phase — add items as they come up rather than trying to buy everything upfront.
