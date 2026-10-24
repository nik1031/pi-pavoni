from gc9a01py import GC9A01
from machine import SPI, Pin
from utime import sleep_ms

FRAME_BYTES = 240 * 240 * 2

spi = SPI(0, baudrate=20_000_000, sck=Pin(18), mosi=Pin(19))
dc = Pin(20, Pin.OUT)
# CS is needed for repeated frames: without it the display drifts out of sync
# after the first transfer and freezes
cs = Pin(21, Pin.OUT, value=1)
rst = Pin(22, Pin.OUT, value=1)

display = GC9A01(spi, dc, cs=cs, reset=rst)

# one buffer, allocated once and refilled every frame: allocating a fresh
# 115 KB block per frame runs the Pico out of contiguous memory
buffer = bytearray(FRAME_BYTES)

with open("coffee_pour.raw", "rb") as f:
    while True:
        try:
            # past the last frame, readinto() comes back short: rewind and loop
            if f.readinto(buffer) < FRAME_BYTES:
                f.seek(0)
                continue
            display.blit_buffer(buffer, 0, 0, 240, 240)
            sleep_ms(60)
        except KeyboardInterrupt:
            break

print("Stopped pouring coffee")
