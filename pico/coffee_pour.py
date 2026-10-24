from gc9a01py import GC9A01
from machine import SPI, Pin
from utime import sleep_ms

ANIM_SIZE = 120
FRAME_BYTES = ANIM_SIZE * ANIM_SIZE * 2
ANIM_POS = (240 - ANIM_SIZE) // 2   # centred

spi = SPI(1, baudrate=20_000_000, sck=Pin(10), mosi=Pin(15))
dc = Pin(12, Pin.OUT)
# CS is needed for repeated frames: without it the display drifts out of sync
# after the first transfer and freezes
cs = Pin(9, Pin.OUT, value=1)
rst = Pin(7, Pin.OUT, value=1)

display = GC9A01(spi, dc, cs=cs, reset=rst)

# one buffer, allocated once and refilled every frame: allocating a fresh
# block per frame runs the Pico out of contiguous memory
buffer = bytearray(FRAME_BYTES)

with open("coffee_pour_small.raw", "rb") as f:
    while True:
        try:
            # past the last frame, readinto() comes back short: rewind and loop
            if f.readinto(buffer) < FRAME_BYTES:
                f.seek(0)
                continue
            display.blit_buffer(buffer, ANIM_POS, ANIM_POS, ANIM_SIZE, ANIM_SIZE)
            sleep_ms(60)
        except KeyboardInterrupt:
            break

print("Stopped pouring coffee")
