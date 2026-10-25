import os
from machine import ADC, SPI, Pin
from utime import sleep_ms, ticks_ms, ticks_diff
from gc9a01py import GC9A01, color565
import vga1_bold_16x32 as font
import vga1_8x16 as small_font   # narrow enough for a full phase name near the screen's top edge

LOG_DIR = "shots"

TARGET_BAR = 9
THRESHOLD_BAR = 6   # "meaningful extraction", same as the analysis notebook
SAMPLES = 16        # readings averaged per update, to steady the last digit

# A shot runs through phases: pre-infusion (above SHOT_ON_BAR), extraction (from the
# first reading at PULL_BAR), dripping (from the first drop below THRESHOLD_BAR once
# the press has reached it, or below PULL_BAR for a shot that never got that high).
# Each shot gets its own log file, from start to end.
SHOT_ON_BAR = 0.1    # t = 0 is the first reading above this; resting pressure reads ~0.06
CONFIRM_BAR = 0.3    # ...but it only counts as a shot once pressure also passes this. A real shot
                     # gets there within ~0.5 s; the slow drain after a shot hovers around 0.1 and
                     # never does, so it can't fake a start
CONFIRM_WINDOW = 25  # readings (~5 s) a rise has to confirm in before it's treated as noise
PULL_BAR = 1.0
END_MS = 3000       # below SHOT_ON_BAR this long ends the shot...
MAX_DRIP_MS = 60000  # ...or dripping this long, since pressure can take minutes to fully drain
PREROLL = 10         # readings from just before the start, logged as "idle" for the resting baseline

IDLE, PREINFUSION, EXTRACTION, DRIPPING = "idle", "pre-infusion", "extraction", "dripping"
LABELS = {IDLE: "Start Pulling", PREINFUSION: "Pre-infusion", EXTRACTION: "Extraction", DRIPPING: "Dripping"}
CODES = {IDLE: "i", PREINFUSION: "p", EXTRACTION: "e", DRIPPING: "d"}   # one letter per row in the log

# vertical layout, top to bottom, all sized to stay inside the round screen
PHASE_Y = 12
PRESSURE_Y = 30
ANIM_SIZE = 120
ANIM_FRAME_BYTES = ANIM_SIZE * ANIM_SIZE * 2
ANIM_X = (240 - ANIM_SIZE) // 2
ANIM_Y = 66
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
BLUE = color565(110, 170, 255)
GREY = color565(130, 130, 130)
PHASE_COLOUR = {IDLE: WHITE, PREINFUSION: BLUE, EXTRACTION: AMBER, DRIPPING: GREY}


def read_pressure():
    """Averaged reading, returned as (raw, voltage, bar)."""
    total = 0
    for _ in range(SAMPLES):
        total += pressure_pin.read_u16()
    raw = total // SAMPLES
    voltage = raw * 3.3 / 65535
    return raw, voltage, voltage / 3.3 * 16


def next_log_file():
    """shots/shot_001.csv, shot_002.csv, ...: one new file per shot.
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


def show_phase(phase):
    # names differ in length, so wipe the band before drawing the new one
    display.fill_rect(0, PHASE_Y, 240, small_font.HEIGHT, BACKGROUND)
    draw_centred(LABELS[phase], PHASE_Y, PHASE_COLOUR[phase], small_font)


def colour_for(bar):
    if bar >= TARGET_BAR:
        return GREEN
    if bar >= THRESHOLD_BAR:
        return AMBER
    return WHITE


def log_row(log, t, raw, voltage, bar, phase):
    log.write(f"{t:.2f},{raw},{voltage:.3f},{bar:.2f},{CODES[phase]}\n")


display.fill(BACKGROUND)
show_phase(IDLE)

# allocated once and refilled every frame (a fresh allocation per frame fragments memory)
anim_buffer = bytearray(ANIM_FRAME_BYTES)

phase = IDLE
recent = []          # (ticks, raw, voltage, bar) while idle: the pre-roll, plus a rise in progress
candidate = None     # ticks of the first reading above SHOT_ON_BAR in a rise not yet confirmed
armed = True         # False after a shot that ended with pressure still up: wait for it to drain
log = None
log_file = None
shot_start = 0       # ticks at t = 0, the first reading above SHOT_ON_BAR
reached_zone = False # has this shot reached THRESHOLD_BAR yet
drip_start = 0
low_since = None     # ticks pressure went below SHOT_ON_BAR, while it stays there
got_extraction = False
shot_seconds = 0.0   # the screen's timer: pre-infusion + extraction, frozen once dripping

anim = open("coffee_pour_small.raw", "rb")
try:
    while True:
        try:
            now = ticks_ms()
            raw, voltage, bar = read_pressure()

            if phase == IDLE:
                recent.append((now, raw, voltage, bar))
                if len(recent) > PREROLL + CONFIRM_WINDOW:
                    recent.pop(0)
                if bar <= SHOT_ON_BAR:
                    armed, candidate = True, None
                elif armed:
                    if candidate is None or ticks_diff(candidate, recent[0][0]) < 0:
                        candidate = now   # a new rise, or one too old to still be the same start
                    if bar >= CONFIRM_BAR:
                        # shot started: t = 0 is the first reading of this rise above SHOT_ON_BAR
                        shot_start = candidate
                        log_file = next_log_file()
                        log = open(log_file, "w")
                        log.write("t,raw,voltage,bar,phase\n")
                        for tk, r, v, b in recent:
                            row_phase = IDLE if ticks_diff(tk, shot_start) < 0 else PREINFUSION
                            log_row(log, ticks_diff(tk, shot_start) / 1000, r, v, b, row_phase)
                        log.flush()
                        phase, reached_zone, low_since, got_extraction = PREINFUSION, False, None, False
                        show_phase(phase)
                        print("Shot started, logging to", log_file)
            else:
                t = ticks_diff(now, shot_start) / 1000
                if phase == PREINFUSION and bar >= PULL_BAR:
                    phase, got_extraction = EXTRACTION, True
                    show_phase(phase)
                elif phase == EXTRACTION:
                    if bar >= THRESHOLD_BAR:
                        reached_zone = True
                    drop_line = THRESHOLD_BAR if reached_zone else PULL_BAR
                    if bar < drop_line:
                        # first drop below the line: pressing is over, freeze the timer here
                        phase, drip_start, shot_seconds = DRIPPING, now, t
                        show_phase(phase)
                        print(f"Dripping, shot time {shot_seconds:.1f} s")
                if phase != DRIPPING:
                    shot_seconds = t

                log_row(log, t, raw, voltage, bar, phase)
                # flush every line so a pulled USB cable mid-shot loses at most one reading
                log.flush()

                if bar < SHOT_ON_BAR:
                    if low_since is None:
                        low_since = now
                else:
                    low_since = None
                drained = low_since is not None and ticks_diff(now, low_since) >= END_MS
                dripped_long = phase == DRIPPING and ticks_diff(now, drip_start) >= MAX_DRIP_MS
                if drained or dripped_long:
                    log.close()
                    log = None
                    if got_extraction:
                        print(f"Shot finished: {shot_seconds:.1f} s, saved as {log_file}")
                    else:
                        # never got past pre-infusion (a knock, the boiler venting): not a shot
                        os.remove(log_file)
                        print("False start, discarded", log_file)
                    # leftover pressure (a shot cut off at MAX_DRIP_MS) mustn't start a new one
                    phase, recent, candidate, armed = IDLE, [], None, bar <= SHOT_ON_BAR
                    show_phase(phase)

            # fixed width (e.g. " 7.4 bar") so a shorter number fully overwrites a longer one
            draw_centred(f"{bar:4.1f} bar", PRESSURE_Y, colour_for(bar))
            draw_centred(f"{shot_seconds:4.1f} s", TIMER_Y,
                         WHITE if phase in (PREINFUSION, EXTRACTION) else GREY)
            print(f"{phase}: {bar:.2f} bar")

            # past the last frame, readinto() comes back short: rewind and loop
            if anim.readinto(anim_buffer) < ANIM_FRAME_BYTES:
                anim.seek(0)
                anim.readinto(anim_buffer)
            display.blit_buffer(anim_buffer, ANIM_X, ANIM_Y, ANIM_SIZE, ANIM_SIZE)

            sleep_ms(60)
        except KeyboardInterrupt:
            break
finally:
    anim.close()
    if log is not None:
        log.close()

# a Ctrl+C can land mid-transfer: raising CS tells the display that transfer is
# over, so the next commands are read cleanly instead of as leftover pixel data
cs.on()
display.fill(BACKGROUND)
draw_centred("Stopped", (240 - font.HEIGHT) // 2, GREY)
print("Stopped")
