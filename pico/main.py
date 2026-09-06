from machine import ADC
from utime import sleep, ticks_ms, ticks_diff

#Initialise pressure readings on Pin 26
pressure_pin = ADC(26)

start_time = ticks_ms()

# "a" = append, so re-running this script keeps adding to the same file
# instead of overwriting whatever's already there.
with open("readings.csv", "a") as f:
    while True:
        try:
            # read_u16() returns a 16-bit integer from 0 to 65535
            raw_value = pressure_pin.read_u16()

            # Convert raw reading to actual voltage (0.0 to 3.3V)
            voltage = raw_value * (3.3 / 65535)
            # Calibration assumption: 0V = 0 bar, sensor's rated max 3.3V = 16 bar.
            # (Revised from an earlier 0.66V "live zero" assumption, which
            # didn't hold up against real captured shot data.)
            pressure_bars = voltage / 3.3 * 16
            elapsed = ticks_diff(ticks_ms(), start_time) / 1000

            print(f"t={elapsed:.2f}s | Raw: {raw_value} | Voltage: {voltage:.2f} | Pressure: {pressure_bars:.2f}bars")

            # write() doesn't add newlines itself, unlike print()
            f.write(f"{elapsed:.2f},{raw_value},{voltage:.3f},{pressure_bars:.2f}\n")
            # flush now rather than waiting for the file to close, in case
            # power gets cut mid-shot rather than a clean Ctrl+C
            f.flush()

            sleep(0.5)
        except KeyboardInterrupt:
            break

print("Finished. Readings written to readings.csv on the Pico.")
