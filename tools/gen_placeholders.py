#!/usr/bin/env python3
"""Generate placeholder art + audio for the Ren'Py prototype.

Pure stdlib — no Pillow, no numpy. Everything stays under E:/aiproject/new.
"""
import array
import math
import os
import random
import struct
import time
import wave
import zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "game", "images", "placeholder")
AUD = os.path.join(ROOT, "game", "audio")
os.makedirs(IMG, exist_ok=True)
os.makedirs(AUD, exist_ok=True)

RATE = 44100


def clamp8(v):
    return 0 if v < 0 else (255 if v > 255 else int(v))


def write_png(path, width, height, rows):
    raw = bytearray()
    for row in rows:
        raw.append(0)
        raw.extend(row)

    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", zlib.compress(bytes(raw), 6))
           + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)


def smoothstep(a, b, x):
    if x <= a:
        return 0.0
    if x >= b:
        return 1.0
    t = (x - a) / (b - a)
    return t * t * (3.0 - 2.0 * t)


def make_bg(path, w=1280, h=720):
    random.seed(7)
    rows = []
    for y in range(h):
        v = y / (h - 1)
        row = bytearray()
        for x in range(w):
            u = x / (w - 1)
            r = g = b = 6.0 + 7.0 * v

            # warm pool of candlelight, low centre
            dx = (u - 0.50) / 0.55
            dy = (v - 0.78) / 0.30
            glow = max(0.0, 1.0 - math.sqrt(dx * dx + dy * dy)) ** 2 * 0.62
            r += 232.0 * glow
            g += 162.0 * glow
            b += 74.0 * glow

            # cold shaft from the hole above
            dx2 = (u - 0.48) / 0.22
            dy2 = (v - 0.06) / 0.42
            cool = max(0.0, 1.0 - math.sqrt(dx2 * dx2 + dy2 * dy2)) ** 3 * 0.16
            r += 110.0 * cool
            g += 130.0 * cool
            b += 165.0 * cool

            vx = (u - 0.5) * 1.45
            vy = (v - 0.5) * 1.25
            vig = 1.0 - min(1.0, vx * vx + vy * vy) * 0.55
            r *= vig
            g *= vig
            b *= vig

            n = random.randint(-4, 4)
            row += bytes((clamp8(r + n), clamp8(g + n), clamp8(b + n), 255))
        rows.append(row)
    write_png(path, w, h, rows)


def make_glow(path, size=512):
    rows = []
    c = (size - 1) / 2.0
    rad = size * 0.5
    for y in range(size):
        row = bytearray()
        for x in range(size):
            d = math.sqrt((x - c) ** 2 + (y - c) ** 2) / rad
            a = int(255 * max(0.0, 1.0 - d) ** 2 * 0.85)
            row += bytes((232, 162, 74, a))
        rows.append(row)
    write_png(path, size, size, rows)


def make_vignette(path, w=1280, h=720):
    rows = []
    for y in range(h):
        v = y / (h - 1)
        row = bytearray()
        for x in range(w):
            u = x / (w - 1)
            d = math.sqrt(((u - 0.5) * 1.35) ** 2 + ((v - 0.5) * 1.15) ** 2)
            a = int(255 * smoothstep(0.30, 0.95, d) * 0.9)
            row += bytes((0, 0, 0, a))
        rows.append(row)
    write_png(path, w, h, rows)


def make_grain(path, w=1280, h=720):
    random.seed(99)
    rows = []
    for _y in range(h):
        row = bytearray()
        for _x in range(w):
            n = random.randint(0, 255)
            a = random.randint(10, 26)
            row += bytes((n, n, n, a))
        rows.append(row)
    write_png(path, w, h, rows)


def write_wav(path, samples, rate=RATE):
    data = array.array("h")
    for s in samples:
        if s > 1.0:
            s = 1.0
        elif s < -1.0:
            s = -1.0
        data.append(int(s * 32767))
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(rate)
        f.writeframes(data.tobytes())


def make_wind(path, seconds=8.0):
    random.seed(11)
    n = int(seconds * RATE)
    lp = 0.0
    out = []
    for i in range(n):
        x = random.uniform(-1.0, 1.0)
        lp += 0.02 * (x - lp)
        env = min(1.0, i / (RATE * 1.5), (n - i) / (RATE * 1.5))
        mod = 0.6 + 0.4 * math.sin(2.0 * math.pi * 0.11 * i / RATE)
        out.append(lp * 3.0 * env * mod)
    write_wav(path, out)


def make_impact(path):
    random.seed(12)
    n = int(2.0 * RATE)
    out = []
    for i in range(n):
        t = i / RATE
        thump = math.sin(2.0 * math.pi * 45.0 * t) * math.exp(-t * 3.0)
        noise = random.uniform(-1.0, 1.0) * math.exp(-t * 18.0)
        click = random.uniform(-1.0, 1.0) * math.exp(-t * 80.0) * 0.5
        out.append((thump * 0.9 + noise * 0.5 + click) * 0.9)
    write_wav(path, out)


def make_heartbeat(path, seconds=4.8):
    n = int(seconds * RATE)
    out = []
    for i in range(n):
        t = i / RATE
        bt = t % 1.2

        def thump(tt, freq=55.0, decay=8.0):
            if tt < 0:
                return 0.0
            return math.sin(2.0 * math.pi * freq * tt) * math.exp(-tt * decay)

        out.append((thump(bt) * 0.9 + thump(bt - 0.28) * 0.6) * 0.8)
    write_wav(path, out)


def make_drone(path, seconds=20.0):
    random.seed(13)
    n = int(seconds * RATE)
    out = []
    for i in range(n):
        t = i / RATE
        lfo1 = 0.5 + 0.5 * math.sin(2.0 * math.pi * 0.050 * t)
        lfo2 = 0.5 + 0.5 * math.sin(2.0 * math.pi * 0.037 * t + 1.3)
        s = 0.20 * math.sin(2.0 * math.pi * 55.0 * t)
        s += 0.12 * math.sin(2.0 * math.pi * 82.5 * t) * lfo1
        s += 0.08 * math.sin(2.0 * math.pi * 110.0 * t) * lfo2
        s += 0.04 * math.sin(2.0 * math.pi * 164.8 * t)
        s += 0.02 * random.uniform(-1.0, 1.0)
        env = min(1.0, t / 1.0, (seconds - t) / 1.0)
        out.append(s * env)
    write_wav(path, out)


def make_candle(path, seconds=6.0):
    random.seed(14)
    n = int(seconds * RATE)
    out = [0.0] * n
    for _ in range(18):
        start = random.randint(0, n - RATE // 4)
        amp = random.uniform(0.05, 0.16)
        for k in range(RATE // 12):
            if start + k < n:
                out[start + k] += (random.uniform(-1.0, 1.0)
                                   * math.exp(-k / (RATE * 0.008)) * amp)
    write_wav(path, out)


def main():
    t0 = time.time()
    steps = [
        ("bg_hall.png", lambda: make_bg(os.path.join(IMG, "bg_hall.png"))),
        ("glow_warm.png", lambda: make_glow(os.path.join(IMG, "glow_warm.png"))),
        ("vignette.png", lambda: make_vignette(os.path.join(IMG, "vignette.png"))),
        ("grain.png", lambda: make_grain(os.path.join(IMG, "grain.png"))),
        ("wind.wav", lambda: make_wind(os.path.join(AUD, "wind.wav"))),
        ("impact.wav", lambda: make_impact(os.path.join(AUD, "impact.wav"))),
        ("heartbeat.wav", lambda: make_heartbeat(os.path.join(AUD, "heartbeat.wav"))),
        ("drone.wav", lambda: make_drone(os.path.join(AUD, "drone.wav"))),
        ("candle.wav", lambda: make_candle(os.path.join(AUD, "candle.wav"))),
    ]
    for name, fn in steps:
        t = time.time()
        fn()
        print("  %-14s %5.1fs" % (name, time.time() - t))
    print("done in %.1fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
