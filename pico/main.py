# Runs automatically when the Pico powers up.
# The real code lives in pressure_display.py: live pressure on the screen,
# the coffee animation, the shot timer, and logging to shots/shot_NNN.csv.
from utime import sleep_ms

# Wait before touching the display. When plugged into a computer, MicroPico
# connects and sends Ctrl+C within the first second or so; landing in this pause
# just leaves the screen blank instead of interrupting the display's setup
# halfway and leaving it garbled. Also lets the power settle.
print("starting in 2 s (Ctrl+C now to stay in the REPL)")
sleep_ms(2000)

import pressure_display
