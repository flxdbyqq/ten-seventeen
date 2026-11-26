#!/usr/bin/env python3
"""Cut the protagonist sprite out of its light background.

Pure stdlib: PNG decode -> ink barrier -> flood fill -> RGBA cutout.
Outputs:
  E:/aiproject/new/风格/主人公立绘_cutout.png   (full canvas, transparent)
  E:/aiproject/new/风格/主人公立绘_preview.png  (half-size, over dark bg)
  E:/aiproject/new/game/images/characters/miles/miles_default.png (cropped)
"""
import os
import struct
import zlib

SRC = r"E:/aiproject/new/主人公立绘.png"
OUT_DIR = r"E:/aiproject/new/风格"
GAME_DIR = r"E:/aiproject/new/game/images/characters/miles"
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(GAME_DIR, exist_ok=True)


def read_png(path):
    data = open(path, "rb").read()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "not a png"
    pos = 8
    idat = bytearray()
    w = h = bd = ct = None
    while pos < len(data):
        ln = struct.unpack(">I", data[pos:pos + 4])[0]
        tag = data[pos + 4:pos + 8]
        chunk = data[pos + 8:pos + 8 + ln]
        pos += 12 + ln
        if tag == b"IHDR":
            w, h, bd, ct, _comp, _filt, _inter = struct.unpack(">IIBBBBB", chunk)
        elif tag == b"IDAT":
            idat.extend(chunk)
        elif tag == b"IEND":
            break
    assert bd == 8 and ct in (2, 6), ("expected 8-bit RGB/RGBA, got", bd, ct)
    raw = zlib.decompress(bytes(idat))
    bpp = 3 if ct == 2 else 4
    stride = w * bpp
    out = bytearray(w * h * bpp)
    prev = bytearray(stride)
    p = 0
    for y in range(h):
        f = raw[p]
        p += 1
        line = bytearray(raw[p:p + stride])
        p += stride
        if f == 1:
            for i in range(bpp, stride):
                line[i] = (line[i] + line[i - bpp]) & 255
        elif f == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 255
        elif f == 3:
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 255
        elif f == 4:
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0
                b = prev[i]
                c = prev[i - bpp] if i >= bpp else 0
                pp = a + b - c
                pa = abs(pp - a)
                pb = abs(pp - b)
                pc = abs(pp - c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 255
        out[y * stride:(y + 1) * stride] = line
        prev = line
    return w, h, bpp, out


def write_png(path, w, h, data, bpp):
    stride = w * bpp
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        raw.extend(data[y * stride:(y + 1) * stride])

    def chunk(tag, payload):
        return (struct.pack(">I", len(payload)) + tag + payload
                + struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF))

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 6 if bpp == 4 else 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", zlib.compress(bytes(raw), 6))
           + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)


def main():
    w, h, bpp, px = read_png(SRC)
    n = w * h
    print("size:", w, "x", h)

    def rgb(x, y):
        i = (y * w + x) * bpp
        return px[i], px[i + 1], px[i + 2]

    print("corners:", rgb(0, 0), rgb(w - 1, 0), rgb(0, h - 1), rgb(w - 1, h - 1))
    print("edges:", rgb(w // 2, 0), rgb(0, h // 2), rgb(w - 1, h // 2), rgb(w // 2, h - 1))

    # 1. Ink mask: anything clearly darker than paper.
    ink = bytearray(n)
    for i in range(n):
        j = i * 3
        if (px[j] + px[j + 1] + px[j + 2]) // 3 < 150:
            ink[i] = 1

    # 2. Dilate ink by 1px, closing small gaps in the outline.
    dil = bytearray(n)
    for y in range(h):
        for x in range(w):
            idx = y * w + x
            if ink[idx]:
                dil[idx] = 1
                continue
            found = False
            for dy in (-1, 0, 1):
                yy = y + dy
                if yy < 0 or yy >= h:
                    continue
                for dx in (-1, 0, 1):
                    xx = x + dx
                    if 0 <= xx < w and ink[yy * w + xx]:
                        found = True
                        break
                if found:
                    break
            if found:
                dil[idx] = 1

    # 3. The bust is cut off at the bottom edge, so block the bottom under it.
    # Keep this separate: it stops the flood fill, but must not become part
    # of the character silhouette.
    BARRIER_X = 1000
    bbar = bytearray(n)
    for x in range(BARRIER_X, w):
        bbar[(h - 1) * w + x] = 1

    # 4. Flood fill the paper from the borders.
    bg = bytearray(n)
    stack = []

    def push(x, y):
        if x < 0 or y < 0 or x >= w or y >= h:
            return
        idx = y * w + x
        if bg[idx] or dil[idx] or bbar[idx]:
            return
        j = idx * 3
        if (px[j] + px[j + 1] + px[j + 2]) // 3 >= 200:
            bg[idx] = 1
            stack.append(idx)

    for x in range(w):
        push(x, 0)
        if x < BARRIER_X:
            push(x, h - 1)
    for y in range(h):
        push(0, y)
        push(w - 1, y)
    for sx, sy in [(50, 50), (50, h // 2), (50, h - 50),
                   (w // 4, h // 2), (w // 2, h // 2)]:
        push(sx, sy)

    while stack:
        idx = stack.pop()
        x = idx % w
        y = idx // w
        push(x + 1, y)
        push(x - 1, y)
        push(x, y + 1)
        push(x, y - 1)

    # The artificial bottom barrier is not part of the character.
    for x in range(BARRIER_X, w):
        idx = (h - 1) * w + x
        j = idx * 3
        if (px[j] + px[j + 1] + px[j + 2]) // 3 >= 200:
            bg[idx] = 1

    # 5. Character = not background.
    minx, miny, maxx, maxy = w, h, -1, -1
    count = 0
    for y in range(h):
        row = y * w
        for x in range(w):
            if not bg[row + x]:
                count += 1
                if x < minx:
                    minx = x
                if x > maxx:
                    maxx = x
                if y < miny:
                    miny = y
                if y > maxy:
                    maxy = y
    print("character pixels:", count, "bbox:", (minx, miny, maxx, maxy))

    # 6. Full RGBA cutout.
    rgba = bytearray(n * 4)
    for i in range(n):
        j = i * 3
        k = i * 4
        rgba[k] = px[j]
        rgba[k + 1] = px[j + 1]
        rgba[k + 2] = px[j + 2]
        rgba[k + 3] = 0 if bg[i] else 255

    write_png(os.path.join(OUT_DIR, "主人公立绘_cutout.png"), w, h, rgba, 4)

    # 7. Cropped sprite for the game.
    cw = maxx - minx + 1
    ch = maxy - miny + 1
    crop = bytearray(cw * ch * 4)
    for y in range(ch):
        srow = (miny + y) * w
        drow = y * cw
        for x in range(cw):
            si = (srow + minx + x) * 4
            di = (drow + x) * 4
            crop[di:di + 4] = rgba[si:si + 4]
    write_png(os.path.join(GAME_DIR, "miles_default.png"), cw, ch, crop, 4)

    # 8. Half-size preview over dark background.
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
    write_png(os.path.join(OUT_DIR, "主人公立绘_preview.png"), pw, ph, prev, 3)
    print("saved cutout + cropped sprite + preview")


if __name__ == "__main__":
    main()
