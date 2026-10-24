import os
from machine import ADC, SPI, Pin
from utime import sleep_ms, ticks_ms, ticks_diff
from gc9a01py import GC9A01, color565
import vga1_bold_16x32 as font
import vga1_8x16 as small_font   # narrow enough for a full message at the screen's bottom edge

PROMPT = "Start Pulling"   # shown where the timer goes, until the first shot starts

LOG_DIR = "shots"

TARGET_BAR = 9
THRESHOLD_BAR = 6   # "meaningful extraction", same as the analysis notebook
SAMPLES = 16        # readings averaged per update, to steady the last digit

# shot timer: starts above START_BAR, stops below STOP_BAR. The gap between the two
# stops sensor noise hovering around one number from flicking it on and off.
START_BAR = 1.0
STOP_BAR = 0.5

# vertical layout, top to bottom, all sized to stay inside the round screen
PRESSURE_Y = 28
ANIM_SIZE = 120
ANIM_FRAME_BYTES = ANIM_SIZE * ANIM_SIZE * 2
ANIM_X = (240 - ANIM_SIZE) // 2
ANIM_Y = 64
TIMER_Y = 190

pressure_pin = ADC(26)

spi = SPI(1, baudrate=20_000_000, sck=Pin(10), mosi=Pin(15))
dc = Pin(12, Pin.OUT)
cs = Pin(9, Pin.OUT, value=1)
rst = Pin(7, Pin.OUT, value=1)
display = GC9A01(spi, dc, cs=cs, reset=rst)

# same dark brown as the animation's own background, so the two blend together
BACKGROUND = color565(20, 14, 12)
WHITE = color565(255, 255, 255)
AMBER = color565(255, 150, 0)
GREEN = color565(0, 220, 90)
GREY = color565(130, 130, 130)   # timer once a shot has finished


def read_pressure():
    """Averaged reading, returned as (raw, voltage, bar)."""
    total = 0
    for _ in range(SAMPLES):
        total += pressure_pin.read_u16()
    raw = total // SAMPLES
    voltage = raw * 3.3 / 65535
    return raw, voltage, voltage / 3.3 * 16


def next_log_file():
    """shots/shot_001.csv, shot_002.csv, ...: one new file per power-up.
    Numbered rather than dated: the Pico's clock resets whenever it loses power."""
    try:
        os.mkdir(LOG_DIR)
    except OSError:
        pass   # already exists
    numbers = [int(name[5:8]) for name in os.listdir(LOG_DIR)
               if name.startswith("shot_") and name.endswith(".csv")]
    last = max(numbers) if numbers else 0
    return f"{LOG_DIR}/shot_{last + 1:03d}.csv"


def draw_centred(text, y, colour, f=font):
    x = (240 - len(text) * f.WIDTH) // 2
    display.text(f, text, x, y, colour, BACKGROUND)


def colour_for(bar):
    if bar >= TARGET_BAR:
        return GREEN
    if bar >= THRESHOLD_BAR:
        return AMBER
    return WHITE


display.fill(BACKGROUND)

# allocated once and refilled every frame (a fresh allocation per frame fragments memory)
anim_buffer = bytearray(ANIM_FRAME_BYTES)

log_file = next_log_file()
print("Logging to", log_file)
start_time = ticks_ms()

shot_start = None    # ticks_ms when the current shot began; None between shots
shot_seconds = 0.0   # last shot's duration, held on screen until the next one starts
any_shot_yet = False # until the first shot, show PROMPT instead of the timer
draw_centred(PROMPT, TIMER_Y + (font.HEIGHT - small_font.HEIGHT) // 2, WHITE, small_font)

with open("coffee_pour_small.raw", "rb") as anim, open(log_file, "w") as log:
    log.write("t,raw,voltage,bar\n")
    while True:
        try:
            raw, voltage, bar = read_pressure()
            elapsed = ticks_diff(ticks_ms(), start_time) / 1000
            log.write(f"{elapsed:.2f},{raw},{voltage:.3f},{bar:.2f}\n")
            # flush every line so a pulled USB cable mid-shot loses at most one reading
            log.flush()

            # fixed width (e.g. " 7.4 bar") so a shorter number fully overwrites a longer one
            draw_centred(f"{bar:4.1f} bar", PRESSURE_Y, colour_for(bar))
            print(f"Pressure: {bar:.2f} bar")

            now = ticks_ms()
            if shot_start is None and bar >= START_BAR:
                shot_start = now
                print("Shot started")
                if not any_shot_yet:
                    any_shot_yet = True
                    # the prompt is wider than the timer text, so wipe its whole band first
                    display.fill_rect(0, TIMER_Y, 240, font.HEIGHT, BACKGROUND)
            elif shot_start is not None and bar < STOP_BAR:
                shot_start = None
                print(f"Shot finished: {shot_seconds:.1f} s")
            if shot_start is not None:
                shot_seconds = ticks_diff(now, shot_start) / 1000
            if any_shot_yet:
                draw_centred(f"{shot_seconds:4.1f} s", TIMER_Y,
                             WHITE if shot_start is not None else GREY)

            # past the last frame, readinto() comes back short: rewind and loop
            if anim.readinto(anim_buffer) < ANIM_FRAME_BYTES:
                anim.seek(0)
                anim.readinto(anim_buffer)
            display.blit_buffer(anim_buffer, ANIM_X, ANIM_Y, ANIM_SIZE, ANIM_SIZE)

            sleep_ms(60)
        except KeyboardInterrupt:
            break

# a Ctrl+C can land mid-transfer: raising CS tells the display that transfer is
# over, so the next commands are read cleanly instead of as leftover pixel data
cs.on()
display.fill(BACKGROUND)
draw_centred("Stopped", (240 - font.HEIGHT) // 2, GREY)
print("Stopped")
