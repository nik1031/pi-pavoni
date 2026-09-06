# Resources

Bill of materials, datasheets, docs, and prior art for this project — collected in one place instead of scattered across chat. Add to this as new things come up.

## Hardware

### Bill of materials

- [x] Pressure transducer — [G1/8 ceramic sensor, 0-1.6MPa range, 0-3.3V output variant](https://www.aliexpress.com/item/1005004559608411.html)
  - Wiring: Red = Power (label reads "SUP: 5-16VDC" — confirmed on the physical sensor, wider range than the generic listing spec suggested), Black = GND, Green = Signal
  - Comes with an attached cable already
- [ ] **Raspberry Pi Pico 2 W** — check if you already have one before buying.
  - Note: comes without header pins — either get one pre-soldered, or buy 2×20 0.1" male header pins separately if you plan to solder your own (needed for breadboard use; not needed if you wire directly).
- [ ] **Micro-USB cable** (data-capable, not charge-only) — for flashing MicroPython and for bench power via VBUS (5V). The Pico 2 W keeps the same micro-USB port as the original Pico.
- [ ] **Breadboard + jumper wire kit (M-M, M-F, F-F assortment)** — for prototyping the wiring before anything is permanent or installed in the machine.
- [ ] **Multimeter** — for verifying the transducer's pinout and output voltage ceiling before connecting it to the Pico, and general debugging. Skip if you already own one.
- [ ] **Small resistor assortment kit (or just a handful of 1kΩ)** — for a series protection resistor between the transducer's signal wire and the Pico's ADC pin.
- [ ] **PTFE (Teflon) thread seal tape** — for sealing the transducer into the group head port. Standard for espresso machine fittings.
- [x] **La Pavoni Esperto Piston Shaft Pressure Gauge Adapter** (OEM part 2124013451, confirmed for Esperto Abile/Competente/Edotto) — [The Espresso Shop](https://theespressoshop.com/products/esperto-piston-shaft-pressure-gauge-adapter-2124013451?variant=48557254017356)
  - Mounts to the piston shaft, not a simple group-head port — different mechanism than assumed, still brew-side pressure.
  - **Open question:** the gauge-facing thread size wasn't listed on the product page, so it's not yet confirmed whether it lands on G1/8 (matching the transducer) or something else. Check by measuring once it arrives, or ask the seller, before assuming no further adapter is needed.
- [ ] Small adjustable spanner/wrench sized for the fitting, to remove the old gauge and thread in the transducer.
- [ ] Soldering iron + solder — if you solder header pins to the Pico or make permanent wire connections.
- [ ] Wire strippers/small side cutters.
- [ ] Small heat-shrink tubing or electrical tape — for insulating/protecting solder joints near the machine.
- [ ] **(Later phase)** 5V power source for the sensor once off USB — e.g. a small USB power bank, or a 5V buck/boost regulator. The transducer needs ~5V; the Pico itself can run from a wider range via VSYS, but the sensor specifically wants 5V on its Red wire. Not needed until untethered/BLE operation is working.
- [ ] **(Later phase)** Small project enclosure/case for the Pico, mounted somewhere on/near the machine away from direct heat.

This list will grow as we hit each phase — add items as they come up rather than trying to buy everything upfront.

### Datasheets & reference links

- [Pico 2 W pinout diagram (PDF)](https://datasheets.raspberrypi.com/picow/pico-2-w-pinout.pdf) — physical GPIO layout, which pins are ADC-capable (GP26/27/28), VBUS/GND/3V3 locations
- [Pico 2 W datasheet (PDF)](https://datasheets.raspberrypi.com/picow/pico-2-w-datasheet.pdf)
- [Pico-series documentation (layout, wireless boards)](https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html#layout_wireless)
- [Official Pico 2 W product page](https://www.raspberrypi.com/products/raspberry-pi-pico-2/)
- [The transducer's AliExpress listing](https://www.aliexpress.com/item/1005004559608411.html)
- [La Pavoni Esperto Piston Shaft Pressure Gauge Adapter (OEM 2124013451)](https://theespressoshop.com/products/esperto-piston-shaft-pressure-gauge-adapter-2124013451?variant=48557254017356)
- [Home-Barista: La Pavoni Pro gauge thread size discussion](https://www.home-barista.com/levers/help-what-is-thread-size-la-pavoni-pro-pressure-gauge-t6171.html)
- [Coffee Sensor — La Pavoni parts](https://coffee-sensor.com/)

## Coffee & pressure profiling theory

- [Sprudge: La Marzocco pressure profiling chart, with Jimseven](https://sprudge.com/la-marzocco-pressure-profiling-chart-with-jimseven-goodness-6185.html) — real-world example of reading and shaping a pressure profile on a high-end machine
- [Daily Drink Mag: Espresso under 6 bar (Monday Espresso)](https://dailydrinkmag.com/espresso-under-6-bar-monday-espresso/) — what under-pressure/underextracted espresso looks and tastes like, directly relevant to the first captured shot's sour result
- [Prestige Coffee: Master the art of espresso with pressure profiling](https://prestige-coffee.com.au/blogs/coffee-guides-prestige-coffee/master-the-art-of-espresso-with-pressure-profiling?srsltid=AfmBOooQ6CflYXAcrq-dRP4IdDggMMwauM4thpBjAdqB6SBtbBr1ubq3) — general primer on what pressure profiling is and why it matters for extraction

## Software

### Tooling

- [MicroPython firmware download for Pico 2 W](https://micropython.org/download/RPI_PICO2_W/)
- [MicroPico VS Code extension (marketplace)](https://marketplace.visualstudio.com/items?itemName=paulober.pico-w-go) — the actual REPL/upload tooling in use, whether reached directly or via the official wizard
- [Official Raspberry Pi Pico VS Code extension](https://github.com/raspberrypi/pico-vscode) — its "New MicroPython Project" wizard scaffolds a MicroPico-based project

### Docs

- [MicroPython `machine` module docs](https://docs.micropython.org/en/latest/library/machine.html) — `Pin`, `ADC`, `Timer`, etc.
- [MicroPython `machine.ADC` docs](https://docs.micropython.org/en/latest/library/machine.ADC.html)

### Inspiration

- [Gaggiuino](https://github.com/Zer0-bit/gaggiuino) — pressure/flow profiling mod for Gaggia machines that this project is modeled on
