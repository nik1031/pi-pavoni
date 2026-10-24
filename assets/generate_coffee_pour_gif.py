"""
Generates a small pixel-art GIF of coffee being poured into a mug.
Drawn on a low-res logical grid, then upscaled with nearest-neighbor
resampling for a chunky retro pixel-art look. Target: 240x240, matching
the round GC9A01 display's framebuffer.

The mug reads as round rather than a flat box by drawing its rim and
liquid surface as ellipses (we're looking slightly down into a circular
opening), and shading the body left-to-right to fake curvature.
"""

from PIL import Image, ImageDraw
import math

GRID = 40            # logical pixel grid (40x40)
SCALE = 6             # 40 * 6 = 240, matches the display exactly
SIZE = GRID * SCALE

BG = (20, 14, 12)
MUG_SHADOW = (203, 188, 163)
MUG_BODY = (235, 222, 201)
MUG_HILITE = (250, 246, 238)
MUG_OUTLINE = (40, 28, 20)
RIM_INNER = (170, 150, 122)   # visible inside of an empty cup, through the rim opening
COFFEE = (90, 52, 28)
COFFEE_HILITE = (140, 86, 46)
COFFEE_SHADOW = (64, 36, 18)
STEAM = (210, 205, 195)

# Mug geometry (logical grid coords)
MUG_LEFT, MUG_RIGHT = 10, 28
RIM_TOP, RIM_BOTTOM = 17, 21          # top rim ellipse
BASE_TOP, BASE_BOTTOM = 31, 34        # bottom ellipse, gives a rounded base
SHADOW_EDGE = MUG_LEFT + (MUG_RIGHT - MUG_LEFT) // 3
HILITE_EDGE = MUG_RIGHT - (MUG_RIGHT - MUG_LEFT) // 4

HANDLE_COLS = (28, 32)
HANDLE_ROWS = (22, 30)

POUR_COL = (18, 20)   # stream width, columns
POUR_FRAMES = 16      # frames spent pouring
STEAM_FRAMES = 10     # frames spent steaming after the pour
TOTAL_FRAMES = POUR_FRAMES + STEAM_FRAMES


def draw_mug_handle(d):
    d.arc([HANDLE_COLS[0], HANDLE_ROWS[0], HANDLE_COLS[1] + 3, HANDLE_ROWS[1]], 270, 90, fill=MUG_OUTLINE, width=2)


def draw_body_shell(d):
    """Cylinder sides + rounded base, shaded left-to-right for curvature."""
    d.rectangle([MUG_LEFT, (RIM_TOP + RIM_BOTTOM) // 2, SHADOW_EDGE, BASE_TOP], fill=MUG_SHADOW)
    d.rectangle([SHADOW_EDGE, (RIM_TOP + RIM_BOTTOM) // 2, HILITE_EDGE, BASE_TOP], fill=MUG_BODY)
    d.rectangle([HILITE_EDGE, (RIM_TOP + RIM_BOTTOM) // 2, MUG_RIGHT, BASE_TOP], fill=MUG_HILITE)
    d.ellipse([MUG_LEFT, BASE_TOP, MUG_RIGHT, BASE_BOTTOM], fill=MUG_BODY, outline=MUG_OUTLINE)
    d.line([MUG_LEFT, (RIM_TOP + RIM_BOTTOM) // 2, MUG_LEFT, BASE_TOP], fill=MUG_OUTLINE)
    d.line([MUG_RIGHT, (RIM_TOP + RIM_BOTTOM) // 2, MUG_RIGHT, BASE_TOP], fill=MUG_OUTLINE)


def draw_rim(d, empty):
    fill = RIM_INNER if empty else None
    d.ellipse([MUG_LEFT, RIM_TOP, MUG_RIGHT, RIM_BOTTOM], fill=fill, outline=MUG_OUTLINE)


def liquid_level_row(frame):
    """Row index of the current liquid surface, interior of the mug."""
    interior_top, interior_bottom = RIM_BOTTOM, BASE_TOP - 1
    if frame >= POUR_FRAMES:
        return interior_top
    progress = frame / POUR_FRAMES
    return round(interior_bottom - progress * (interior_bottom - interior_top))


def draw_frame(frame):
    img = Image.new("RGB", (GRID, GRID), BG)
    d = ImageDraw.Draw(img)

    level = liquid_level_row(frame)
    empty = level >= BASE_TOP - 1

    # pour stream, only while actively pouring and above the rising surface
    if frame < POUR_FRAMES:
        d.rectangle([POUR_COL[0], 0, POUR_COL[1], level], fill=COFFEE)

    draw_body_shell(d)
    draw_mug_handle(d)

    # liquid fill: a filled body below the surface, capped with an elliptical surface
    if not empty:
        d.rectangle([MUG_LEFT + 1, level, MUG_RIGHT - 1, BASE_TOP - 1], fill=COFFEE)
        d.ellipse([MUG_LEFT + 1, level - 2, MUG_RIGHT - 1, level + 2], fill=COFFEE_HILITE, outline=COFFEE_SHADOW)

    draw_rim(d, empty)

    # steam, once pouring is done
    if frame >= POUR_FRAMES:
        steam_t = frame - POUR_FRAMES
        for i, base_col in enumerate((16, 20, 24)):
            phase = steam_t * 0.9 + i * 2.0
            for row_offset in range(6):
                row = RIM_TOP - 2 - row_offset - (steam_t % STEAM_FRAMES)
                if row < 0:
                    continue
                wiggle = round(math.sin(phase + row_offset * 0.6) * 1.5)
                col = base_col + wiggle
                fade = row_offset + (steam_t % STEAM_FRAMES)
                if fade < 10:
                    d.point((col, row), fill=STEAM)

    return img.resize((SIZE, SIZE), Image.NEAREST)


def main():
    frames = [draw_frame(f) for f in range(TOTAL_FRAMES)]
    out_path = "coffee_pour.gif"
    frames[0].save(
        out_path,
        save_all=True,
        append_images=frames[1:],
        duration=90,
        loop=0,
        disposal=2,
    )
    print(f"Wrote {out_path}: {len(frames)} frames at {SIZE}x{SIZE}")


if __name__ == "__main__":
    main()
