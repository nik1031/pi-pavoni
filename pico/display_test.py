"""
Screen self-test, on a loop until Ctrl+C: fills red, green, blue, then draws
"HELLO" and a border. Watch the screen and the REPL together. If the REPL
keeps counting cycles but the screen stays blank or frozen, the problem is
wiring, not code. Being on a loop, you can wiggle wires while it runs.
"""

from machine import SPI, Pin
from utime import sleep_ms
from gc9a01py import GC9A01, color565
import vga1_bold_16x32 as font

# same pins as pressure_display.py
spi = SPI(1, baudrate=10_000_000, sck=Pin(10), mosi=Pin(15))   # slower than usual, more forgiving of loose wires
dc = Pin(12, Pin.OUT)
cs = Pin(9, Pin.OUT, value=1)
rst = Pin(7, Pin.OUT, value=1)

print("SPI:", spi)
display = GC9A01(spi, dc, cs=cs, reset=rst)
print("display initialised")

BLACK = color565(0, 0, 0)
WHITE = color565(255, 255, 255)

COLOURS = (("RED", color565(255, 0, 0)),
           ("GREEN", color565(0, 255, 0)),
           ("BLUE", color565(0, 0, 255)))

cycle = 0
while True:
    try:
        cycle += 1
        for name, colour in COLOURS:
            print("cycle", cycle, "filling", name)
            display.fill(colour)
            sleep_ms(1500)

        display.fill(BLACK)
        display.rect(10, 10, 220, 220, WHITE)
        display.text(font, "HELLO", (240 - 5 * font.WIDTH) // 2, (240 - font.HEIGHT) // 2, WHITE, BLACK)
        print("cycle", cycle, "drew HELLO and a border")
        sleep_ms(1500)
    except KeyboardInterrupt:
        break

print("test stopped")
