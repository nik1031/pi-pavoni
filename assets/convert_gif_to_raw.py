"""
Converts a GIF into a single raw binary file of RGB565-encoded frames,
back-to-back, for playback on the Pico via GC9A01.blit_buffer().

Each pixel: 2 bytes, big-endian, RGB565 (matching gc9a01py's own
_ENCODE_PIXEL format, ">H").

Usage: python convert_gif_to_raw.py [src.gif] [out.raw]
"""

import sys
from PIL import Image


def rgb565_bytes(img):
    """Pack an RGB image's pixels into big-endian RGB565, row-major."""
    width, height = img.size
    pixels = img.load()
    out = bytearray(width * height * 2)
    i = 0
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y][:3]
            value = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
            out[i] = value >> 8
            out[i + 1] = value & 0xFF
            i += 2
    return bytes(out)


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "coffee_pour.gif"
    out = sys.argv[2] if len(sys.argv) > 2 else "coffee_pour.raw"

    gif = Image.open(src)
    width, height = gif.size
    bytes_per_frame = width * height * 2

    with open(out, "wb") as f:
        for i in range(gif.n_frames):
            gif.seek(i)
            f.write(rgb565_bytes(gif.convert("RGB")))

    total = gif.n_frames * bytes_per_frame
    print(f"{out}: {gif.n_frames} frames at {width}x{height}, {bytes_per_frame} bytes/frame, {total/1024:.1f} KB total")


if __name__ == "__main__":
    main()
