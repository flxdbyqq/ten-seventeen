#!/usr/bin/env python3
"""Visual-novel staging test: NPC on the left, protagonist on the right."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cutout_sprite import read_png, write_png

HALL = r"E:/aiproject/new/风格/殡仪馆大厅.png"
DIRECTOR = r"E:/aiproject/new/风格/司仪立绘_cutout.png"
MILES = r"E:/aiproject/new/game/images/characters/miles/miles_default.png"
OUT_DIR = r"E:/aiproject/new/风格"


def scale_rgba(src, sw, sh, dw, dh):
    dst = bytearray(dw * dh * 4)
    for y in range(dh):
        sy = (y + 0.5) * sh / dh - 0.5
        y0 = int(math.floor(sy))
        y1 = min(sh - 1, y0 + 1)
        fy = sy - y0
        if y0 < 0:
            y0 = y1 = 0
            fy = 0.0
        for x in range(dw):
            sx = (x + 0.5) * sw / dw - 0.5
            x0 = int(math.floor(sx))
            x1 = min(sw - 1, x0 + 1)
            fx = sx - x0
            if x0 < 0:
                x0 = x1 = 0
                fx = 0.0
            i00 = (y0 * sw + x0) * 4
            i10 = (y0 * sw + x1) * 4
            i01 = (y1 * sw + x0) * 4
            i11 = (y1 * sw + x1) * 4
            o = (y * dw + x) * 4
            for c in range(4):
                v = (src[i00 + c] * (1 - fx) * (1 - fy)
                     + src[i10 + c] * fx * (1 - fy)
                     + src[i01 + c] * (1 - fx) * fy
                     + src[i11 + c] * fx * fy)
                dst[o + c] = int(v)
    return dst


def place(canvas, w, h, sprite, sw, sh, target_h, ox, oy):
    tw = int(sw * target_h / sh)
    scaled = scale_rgba(sprite, sw, sh, tw, target_h)
    for y in range(target_h):
        cy = oy + y
        if cy < 0 or cy >= h:
            continue
        for x in range(tw):
            cx = ox + x
            if cx < 0 or cx >= w:
                continue
            si = (y * tw + x) * 4
            a = scaled[si + 3]
            if a == 0:
                continue
            ci = (cy * w + cx) * 3
            for c in range(3):
                canvas[ci + c] = (scaled[si + c] * a + canvas[ci + c] * (255 - a)) // 255


def grade(hall, w, h):
    for y in range(h):
        for x in range(w):
            i = (y * w + x) * 3
            r, g, b = hall[i], hall[i + 1], hall[i + 2]
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            warm = max(0.0, r - b)
            keep = min(1.0, warm / 70.0) * 0.75
            nr = lum + (r - lum) * keep
            ng = lum + (g - lum) * keep
            nb = lum + (b - lum) * keep
            nr = (nr - 128) * 1.06 + 128
            ng = (ng - 128) * 1.06 + 128
            nb = (nb - 128) * 1.06 + 128
            dx = (x / w - 0.5) * 1.15
            dy = (y / h - 0.5) * 1.05
            vig = 1.0 - min(1.0, dx * dx + dy * dy) * 0.30
            hall[i] = max(0, min(255, int(nr * vig)))
            hall[i + 1] = max(0, min(255, int(ng * vig)))
            hall[i + 2] = max(0, min(255, int(nb * vig)))


def add_textbox(hall, w, h):
    band = 220
    top = h - band
    for y in range(top, h):
        for x in range(w):
            i = (y * w + x) * 3
            hall[i] = int(hall[i] * 0.28)
            hall[i + 1] = int(hall[i + 1] * 0.28)
            hall[i + 2] = int(hall[i + 2] * 0.28)
    for x in range(w):
        i = (top * w + x) * 3
        hall[i] = (hall[i] + 232) // 2
        hall[i + 1] = (hall[i + 1] + 162) // 2
        hall[i + 2] = (hall[i + 2] + 74) // 2


def save_half(canvas, w, h, path):
    pw, ph = w // 2, h // 2
    prev = bytearray(pw * ph * 3)
    for y in range(ph):
        for x in range(pw):
            r = g = b = 0
            for dy in (0, 1):
                for dx in (0, 1):
                    i = ((y * 2 + dy) * w + (x * 2 + dx)) * 3
                    r += canvas[i]
                    g += canvas[i + 1]
                    b += canvas[i + 2]
            j = (y * pw + x) * 3
            prev[j] = r // 4
            prev[j + 1] = g // 4
            prev[j + 2] = b // 4
    write_png(path, pw, ph, prev, 3)
    print("saved:", path)


def main():
    w, h, bpp, hall = read_png(HALL)
    dw, dh, dbpp, director = read_png(DIRECTOR)
    mw, mh, mbpp, miles = read_png(MILES)
    print("hall:", w, h, "director:", dw, dh, "miles:", mw, mh)

    grade(hall, w, h)

    # 1) Director on the left, first-person shot.
    solo = bytearray(hall)
    place(solo, w, h, director, dw, dh, 1150, 250, 1550 - 1150)
    add_textbox(solo, w, h)
    save_half(solo, w, h, os.path.join(OUT_DIR, "合成测试_大厅_司仪_左.png"))

    # 2) Two-shot: NPC left, protagonist right.
    duo = bytearray(hall)
    place(duo, w, h, director, dw, dh, 1150, 250, 1550 - 1150)
    place(duo, w, h, miles, mw, mh, 950, 1850, 1500 - 950)
    add_textbox(duo, w, h)
    save_half(duo, w, h, os.path.join(OUT_DIR, "合成测试_双人.png"))


if __name__ == "__main__":
    main()
