#!/usr/bin/env python3
"""Chroma-key the director sprite (magenta background) to RGBA grayscale."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cutout_sprite import read_png, write_png

SRC = r"E:/aiproject/new/风格/司仪立绘.png"
OUT_DIR = r"E:/aiproject/new/风格"
GAME_DIR = r"E:/aiproject/new/game/images/characters/director"
os.makedirs(GAME_DIR, exist_ok=True)


def main():
    w, h, bpp, px = read_png(SRC)
    n = w * h
    print("size:", w, "x", h)

    def rgb(x, y):
        i = (y * w + x) * bpp
        return px[i], px[i + 1], px[i + 2]

    print("corners:", rgb(0, 0), rgb(w - 1, 0), rgb(0, h - 1), rgb(w - 1, h - 1))

    rgba = bytearray(n * 4)
    for i in range(n):
        j = i * 3
        k = i * 4
        r, g, b = px[j], px[j + 1], px[j + 2]

        # Magenta score: high for (r high, b high, g low).
        score = (r + b) / 2.0 - g
        if score <= 30:
            a = 255
        elif score >= 90:
            a = 0
        else:
            a = int(255 * (1.0 - (score - 30) / 60.0))

        # Main tone: black / white / gray.
        lum = int(0.299 * r + 0.587 * g + 0.114 * b)
        rgba[k] = lum
        rgba[k + 1] = lum
        rgba[k + 2] = lum
        rgba[k + 3] = a

    minx, miny, maxx, maxy = w, h, -1, -1
    for y in range(h):
        row = y * w
        for x in range(w):
            if rgba[(row + x) * 4 + 3] > 8:
                if x < minx:
                    minx = x
                if x > maxx:
                    maxx = x
                if y < miny:
                    miny = y
                if y > maxy:
                    maxy = y
    print("bbox:", (minx, miny, maxx, maxy))

    write_png(os.path.join(OUT_DIR, "司仪立绘_cutout.png"), w, h, rgba, 4)

    cw = maxx - minx + 1
    ch = maxy - miny + 1
    crop = bytearray(cw * ch * 4)
    for y in range(ch):
        srow = (miny + y) * w
        for x in range(cw):
            si = (srow + minx + x) * 4
            di = (y * cw + x) * 4
            crop[di:di + 4] = rgba[si:si + 4]
    write_png(os.path.join(GAME_DIR, "director_default.png"), cw, ch, crop, 4)

    # Preview over dark, half size.
    pw, ph = w // 2, h // 2
    prev = bytearray(pw * ph * 3)
    for y in range(ph):
        for x in range(pw):
            r = g = b = 0
            for dy in (0, 1):
                for dx in (0, 1):
                    sx = x * 2 + dx
                    sy = y * 2 + dy
                    i = (sy * w + sx) * 4
                    a = rgba[i + 3] / 255.0
                    r += rgba[i] * a + 18 * (1 - a)
                    g += rgba[i + 1] * a + 16 * (1 - a)
                    b += rgba[i + 2] * a + 24 * (1 - a)
            j = (y * pw + x) * 3
            prev[j] = int(r / 4)
            prev[j + 1] = int(g / 4)
            prev[j + 2] = int(b / 4)
    write_png(os.path.join(OUT_DIR, "司仪立绘_preview.png"), pw, ph, prev, 3)
    print("saved:", os.path.join(OUT_DIR, "司仪立绘_preview.png"))


if __name__ == "__main__":
    main()
