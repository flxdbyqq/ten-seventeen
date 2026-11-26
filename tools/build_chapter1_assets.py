#!/usr/bin/env python3
"""Build Chapter 1 assets: graded backgrounds, UI textures, face crop, SFX."""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cutout_sprite import read_png, write_png
from gen_placeholders import write_wav

ROOT = r"E:/aiproject/new"
BG_DIR = os.path.join(ROOT, "game", "images", "bg")
UI_DIR = os.path.join(ROOT, "game", "images", "ui")
CH_DIR = os.path.join(ROOT, "game", "images", "characters")
AUD = os.path.join(ROOT, "game", "audio")
for d in (BG_DIR, UI_DIR, AUD):
    os.makedirs(d, exist_ok=True)

HALL = os.path.join(ROOT, "风格", "殡仪馆大厅.png")
COFFIN = os.path.join(ROOT, "风格", "棺材近景.png")
MILES = os.path.join(ROOT, "game", "images", "characters", "miles", "miles_default.png")

RATE = 44100


def clamp(v):
    return 0 if v < 0 else (255 if v > 255 else int(v))


def write_png_rows(path, w, h, rows, bpp):
    flat = bytearray()
    for row in rows:
        flat.extend(row)
    write_png(path, w, h, flat, bpp)


def grade(src, dst, lift=0.0, contrast=1.06, vig=0.30, warm_keep=0.75):
    w, h, bpp, px = read_png(src)
    out = bytearray(len(px))
    for y in range(h):
        for x in range(w):
            i = (y * w + x) * 3
            r, g, b = px[i], px[i + 1], px[i + 2]
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            warm = max(0.0, r - b)
            keep = min(1.0, warm / 70.0) * warm_keep
            nr = lum + (r - lum) * keep
            ng = lum + (g - lum) * keep
            nb = lum + (b - lum) * keep
            nr = (nr - 128) * contrast + 128 + lift
            ng = (ng - 128) * contrast + 128 + lift
            nb = (nb - 128) * contrast + 128 + lift
            dx = (x / w - 0.5) * 1.15
            dy = (y / h - 0.5) * 1.05
            v = 1.0 - min(1.0, dx * dx + dy * dy) * vig
            out[i] = clamp(nr * v)
            out[i + 1] = clamp(ng * v)
            out[i + 2] = clamp(nb * v)
    write_png(dst, w, h, out, 3)
    print("graded:", os.path.basename(dst), w, h)


def crop_face():
    w, h, bpp, px = read_png(MILES)
    x0, y0, cw, ch = 190, 70, 520, 560
    cw = min(cw, w - x0)
    ch = min(ch, h - y0)
    out = bytearray(cw * ch * bpp)
    for y in range(ch):
        srow = (y0 + y) * w
        for x in range(cw):
            si = (srow + x0 + x) * bpp
            di = (y * cw + x) * bpp
            out[di:di + bpp] = px[si:si + bpp]
    dst = os.path.join(CH_DIR, "miles", "miles_face.png")
    write_png(dst, cw, ch, out, bpp)
    print("face crop:", cw, ch, dst)


def make_paper(w=1280, h=720):
    random.seed(21)
    rows = []
    fold = h // 2
    for y in range(h):
        row = bytearray()
        for x in range(w):
            base = 206 + random.randint(-7, 7)
            # horizontal fibres
            if random.random() < 0.0015:
                base -= random.randint(6, 20)
            # a few soft stains
            for sx, sy, sr, sa in ((260, 190, 120, 10), (980, 540, 150, 8), (640, 90, 90, 6)):
                d2 = (x - sx) ** 2 + (y - sy) ** 2
                if d2 < sr * sr:
                    base -= int(sa * (1 - d2 / (sr * sr)))
            # fold shadow
            if abs(y - fold) < 3:
                base -= 5
            dx = (x / w - 0.5) * 1.2
            dy = (y / h - 0.5) * 1.1
            v = 1.0 - min(1.0, dx * dx + dy * dy) * 0.16
            c = clamp(base * v)
            row += bytes((c, max(0, c - 2), max(0, c - 8), 255))
        rows.append(row)
    write_png_rows(os.path.join(UI_DIR, "paper.png"), w, h, rows, 3)
    print("paper.png")


def make_textbox(w=1280, h=240):
    rows = []
    for y in range(h):
        a = int(195 * (y / (h - 1)) ** 1.25)
        row = bytearray()
        for _x in range(w):
            row += bytes((8, 7, 10, a))
        rows.append(row)
    write_png_rows(os.path.join(UI_DIR, "textbox.png"), w, h, rows, 4)
    print("textbox.png", w, h)


def make_choice_bars(w=900, h=42):
    def bar(path, color, alpha_center):
        rows = []
        for y in range(h):
            row = bytearray()
            for x in range(w):
                edge = min(1.0, x / 120.0, (w - 1 - x) / 120.0)
                a = int(alpha_center * (edge ** 0.8))
                row += bytes((color[0], color[1], color[2], a))
            rows.append(row)
        write_png_rows(path, w, h, rows, 4)

    bar(os.path.join(UI_DIR, "choice_idle.png"), (5, 5, 8), 175)
    bar(os.path.join(UI_DIR, "choice_hover.png"), (139, 46, 42), 225)
    print("choice bars")


def make_stamp(size=300):
    random.seed(22)
    rows = []
    c = (size - 1) / 2.0
    for y in range(size):
        row = bytearray()
        for x in range(size):
            dx = x - c
            dy = y - c
            d = math.hypot(dx, dy)
            ang = math.atan2(dy, dx)
            r_out = 122 + 4 * math.sin(ang * 7) + random.uniform(-1.5, 1.5)
            r_in = 106 + 3 * math.sin(ang * 5 + 1)
            a = 0
            if r_in <= d <= r_out:
                a = 185
            if 76 <= d <= 80:
                a = 120
            row += bytes((139, 46, 42, a))
        rows.append(row)
    write_png_rows(os.path.join(UI_DIR, "stamp_ring.png"), size, size, rows, 4)
    print("stamp_ring.png")


def sfx_rain(path, seconds=8.0):
    random.seed(31)
    n = int(seconds * RATE)
    lp = 0.0
    out = []
    for i in range(n):
        x = random.uniform(-1.0, 1.0)
        lp += 0.05 * (x - lp)
        bed = lp * 0.8 + random.uniform(-1.0, 1.0) * 0.04
        drop = 0.0
        if random.random() < 0.0009:
            drop = random.uniform(-0.5, 0.5)
        env = min(1.0, i / (RATE * 0.2), (n - i) / (RATE * 0.2))
        out.append((bed + drop) * env * 0.6)
    write_wav(path, out)


def sfx_clock(path, seconds=8.0):
    n = int(seconds * RATE)
    out = [0.0] * n
    for tick in range(int(seconds)):
        start = tick * RATE
        for k in range(int(0.04 * RATE)):
            if start + k < n:
                t = k / RATE
                out[start + k] += ((random.uniform(-1, 1) * 0.3
                                    + math.sin(2 * math.pi * 1800 * t) * 0.4)
                                   * math.exp(-t * 120))
    write_wav(path, out)


def sfx_door(path):
    n = int(1.4 * RATE)
    out = []
    for i in range(n):
        t = i / RATE
        thud = math.sin(2 * math.pi * 60 * t) * math.exp(-t * 8)
        creak = math.sin(2 * math.pi * (300 - 120 * t) * t) * 0.15 * math.exp(-t * 2)
        noise = random.uniform(-1, 1) * math.exp(-t * 20) * 0.3
        out.append((thud + creak + noise) * 0.8)
    write_wav(path, out)


def sfx_steps(path):
    n = int(3.6 * RATE)
    out = [0.0] * n
    for step in range(4):
        start = int((0.2 + step * 0.8) * RATE)
        for k in range(int(0.25 * RATE)):
            if start + k < n:
                t = k / RATE
                out[start + k] += (math.sin(2 * math.pi * 70 * t) * math.exp(-t * 18) * 0.4
                                   + random.uniform(-1, 1) * math.exp(-t * 30) * 0.15)
    write_wav(path, out)


def sfx_match(path):
    n = int(1.4 * RATE)
    out = []
    for i in range(n):
        t = i / RATE
        scratch = random.uniform(-1, 1) * math.exp(-t * 12) * 0.5 if t < 0.25 else 0.0
        whoosh = random.uniform(-1, 1) * min(1.0, t / 0.3) * math.exp(-t * 2.5) * 0.25
        out.append(scratch + whoosh)
    write_wav(path, out)


def sfx_exhale(path):
    n = int(1.6 * RATE)
    lp = 0.0
    out = []
    for i in range(n):
        t = i / RATE
        x = random.uniform(-1, 1)
        lp += 0.08 * (x - lp)
        env = math.sin(math.pi * min(1.0, t / 1.6)) ** 2
        out.append(lp * env * 1.5)
    write_wav(path, out)


def sfx_pen(path):
    n = int(1.6 * RATE)
    out = []
    for i in range(n):
        t = i / RATE
        mod = 0.5 + 0.5 * math.sin(2 * math.pi * 7 * t)
        scratch = random.uniform(-1, 1) * 0.2 * mod
        env = min(1.0, t / 0.1, (1.6 - t) / 0.2)
        out.append(scratch * env)
    write_wav(path, out)


def sfx_paper(path):
    n = int(1.2 * RATE)
    out = []
    for i in range(n):
        t = i / RATE
        env = min(1.0, t / 0.05, (1.2 - t) / 0.3)
        crinkle = random.uniform(-1, 1) * (0.5 + 0.5 * math.sin(2 * math.pi * 13 * t)) * 0.25
        out.append(crinkle * env)
    write_wav(path, out)


def sfx_stamp(path):
    n = int(0.9 * RATE)
    out = []
    for i in range(n):
        t = i / RATE
        thud = math.sin(2 * math.pi * 55 * t) * math.exp(-t * 10)
        slap = random.uniform(-1, 1) * math.exp(-t * 25) * 0.4
        out.append((thud + slap) * 0.9)
    write_wav(path, out)


def make_title_bg():
    w, h, bpp, px = read_png(os.path.join(BG_DIR, "bg_hall_wide.png"))
    tw, th = 1280, 720
    out = bytearray(tw * th * 3)
    for y in range(th):
        sy = int(y * h / th)
        for x in range(tw):
            sx = int(x * w / tw)
            i = (sy * w + sx) * 3
            d = 0.30 + 0.30 * (x / tw)
            dx = (x / tw - 0.5) * 1.2
            dy = (y / th - 0.5) * 1.1
            v = 1.0 - min(1.0, dx * dx + dy * dy) * 0.25
            k = d * v
            o = (y * tw + x) * 3
            out[o] = clamp(px[i] * k)
            out[o + 1] = clamp(px[i + 1] * k)
            out[o + 2] = clamp(px[i + 2] * k)
    write_png(os.path.join(UI_DIR, "title_bg.png"), tw, th, out, 3)
    print("title_bg.png")


def main():
    grade(HALL, os.path.join(BG_DIR, "bg_hall_wide.png"))
    grade(COFFIN, os.path.join(BG_DIR, "bg_coffin_close.png"),
          lift=8.0, contrast=1.03, vig=0.22, warm_keep=0.85)
    make_title_bg()
    crop_face()
    make_paper()
    make_textbox()
    make_stamp()
    sfx_rain(os.path.join(AUD, "rain.wav"))
    sfx_clock(os.path.join(AUD, "clock.wav"))
    sfx_door(os.path.join(AUD, "door.wav"))
    sfx_steps(os.path.join(AUD, "footsteps.wav"))
    sfx_match(os.path.join(AUD, "match.wav"))
    sfx_exhale(os.path.join(AUD, "exhale.wav"))
    sfx_pen(os.path.join(AUD, "pen.wav"))
    sfx_paper(os.path.join(AUD, "paper.wav"))
    sfx_stamp(os.path.join(AUD, "stamp.wav"))
    print("chapter 1 assets done")


if __name__ == "__main__":
    main()
