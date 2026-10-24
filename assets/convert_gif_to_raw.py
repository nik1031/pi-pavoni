"""
Converts coffee_pour.gif into a single raw binary file of RGB565-encoded
frames, back-to-back, for playback on the Pico via GC9A01.blit_buffer().

Each pixel: 2 bytes, big-endian, RGB565 (matching gc9a01py's own
_ENCODE_PIXEL format, ">H").
"""

from PIL import Image

SRC = "coffee_pour.gif"
OUT = "coffee_pour.raw"
WIDTH, HEIGHT = 240, 240


def rgb565_bytes(img):
    """Pack an RGB image's pixels into big-endian RGB565, row-major."""
    pixels = img.load()
    out = bytearray(WIDTH * HEIGHT * 2)
    i = 0
    for y in range(HEIGHT):
        for x in range(WIDTH):
            r, g, b = pixels[x, y][:3]
            value = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
            out[i] = value >> 8
            out[i + 1] = value & 0xFF
            i += 2
    return bytes(out)


def main():
    gif = Image.open(SRC)
    frame_count = gif.n_frames
    bytes_per_frame = WIDTH * HEIGHT * 2

    with open(OUT, "wb") as f:
        for i in range(frame_count):
            gif.seek(i)
            frame = gif.convert("RGB")
            f.write(rgb565_bytes(frame))

    total = frame_count * bytes_per_frame
    print(f"{frame_count} frames, {bytes_per_frame} bytes/frame, {total} bytes total ({total/1024:.1f} KB)")


if __name__ == "__main__":
    main()
