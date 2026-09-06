# Phase 0: Toolchain

Getting from "Pico 2 W in a box" to "I can write MicroPython and run it on the board from VS Code."

## Editor setup

Using VS Code (not Thonny, though Thonny works fine too) via the official **Raspberry Pi Pico** extension ([raspberrypi/pico-vscode](https://github.com/raspberrypi/pico-vscode)). Its "New MicroPython Project" wizard (Command Palette → search "Raspberry Pi Pico Project") scaffolds a project that, under the hood, is actually built on the community **MicroPico** extension ([paulober.pico-w-go](https://marketplace.visualstudio.com/items?itemName=paulober.pico-w-go)) — you can tell because it generates a `.micropico` marker file and MicroPico-specific settings. So either extension gets you to the same place; the official wizard is just a friendlier on-ramp.

What the wizard generates:
- `.vscode/settings.json` — MicroPico config (`micropico.openOnStart: true` auto-connects the REPL when the folder opens), plus Pylance settings pointed at the MicroPython stub files for autocomplete.
- `.micropico` — an empty marker file; its only purpose is telling the extension "this folder is a MicroPico project."
- A starter script (originally named `blink.py`).

**Project layout:** both `.vscode/` and `.micropico` need to live in whatever folder VS Code opens as its workspace root — that's why they ended up at the repo root here (`pi-pavoni/`) rather than nested under `pico/`. The actual on-device MicroPython code lives in [`pico/`](../pico/).

## Firmware

Board: Raspberry Pi Pico 2 W (RP2350). Confirmed running **MicroPython v1.28.0** via the REPL banner:

```
MicroPython v1.28.0 on 2026-04-06; Raspberry Pi Pico 2 W with RP2350
```

If a board doesn't already have MicroPython on it, the manual flashing path is: hold the **BOOTSEL** button, plug in USB, release once it mounts as a drive (usually `RPI-RP2`), then drag the correct UF2 for your board onto it — for Pico 2 W specifically, from [micropython.org/download/RPI_PICO2_W](https://micropython.org/download/RPI_PICO2_W/). Get the **W** variant specifically (not plain Pico 2), since that's the one with WiFi/Bluetooth support needed for later phases.

## Running code on the board

Two different ways to "run" a `.py` file, and they are not interchangeable:

1. **MicroPico: Run current file on Pico** — Command Palette (`Cmd+Shift+P`) → search `micropico` → **"Run current file on Pico"**. This streams the file to the board over the REPL and executes it live on the actual hardware. Nothing is saved to the board's flash — it's for quick iteration. This is what you want almost all the time during development.
2. **Upload / sync to the board** — copies a file onto the Pico's own filesystem so it persists across power cycles. A file specifically named `main.py` auto-runs on every boot, no computer attached. Not used yet — everything so far runs ephemerally via option 1.

**Gotcha:** VS Code's built-in Python extension also adds its own generic "Run" button/command to `.py` files. That runs the file with your *computer's* local Python, not the Pico's — and since MicroPython-only modules like `machine` don't exist on a desktop, it fails immediately with `ModuleNotFoundError: No module named 'machine'`. The tell is in the traceback: if the file path shown is your computer's local path (e.g. `/Users/.../pico/blink.py`) rather than something on the board, it ran locally, not on the device. Always use the MicroPico-specific run command instead.

Once a script is running via option 1, the REPL panel stays live — `Ctrl+C` in that panel sends a `KeyboardInterrupt` into the running script, which is how you stop something like `blink.py`'s infinite loop cleanly.
