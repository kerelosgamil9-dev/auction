# -*- coding: utf-8 -*-
"""Generates assets/icons/*.png, icon.png, presplash.png and assets/sounds/*.wav.
Run once:  python gen_assets.py   (needs Pillow; the generated files are already in the repo)."""
import math
import os
import struct
import wave

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
S = 256
W = (255, 255, 255, 255)


def tile(color):
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = tuple(int(v * 255) for v in color[:3])
    d.rounded_rectangle((0, 0, S - 1, S - 1), 44, fill=c + (255,))
    d.rounded_rectangle((0, S // 2, S - 1, S - 1), 44, fill=tuple(int(v * .82) for v in c) + (255,))
    d.rectangle((0, S // 2, S - 1, S // 2 + 40), fill=c + (255,))
    d.rounded_rectangle((0, 0, S - 1, S - 1), 44, outline=(255, 255, 255, 90), width=4)
    return img, d


def star(d, cx, cy, r, fill):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=fill)


def draw_palace(d):
    d.rectangle((70, 120, 186, 205), fill=W)
    for x in (48, 168):
        d.rectangle((x, 90, x + 40, 205), fill=W)
        d.polygon([(x - 6, 92), (x + 20, 52), (x + 46, 92)], fill=(255, 215, 80, 255))
    d.polygon([(100, 122), (128, 78), (156, 122)], fill=(255, 215, 80, 255))
    d.pieslice((108, 150, 148, 230), 180, 360, fill=(90, 60, 120, 255))
    d.rectangle((108, 190, 148, 205), fill=(90, 60, 120, 255))


def draw_house(d):
    d.polygon([(36, 128), (128, 48), (220, 128)], fill=(255, 215, 80, 255))
    d.rectangle((60, 124, 196, 208), fill=W)
    d.rectangle((112, 156, 144, 208), fill=(70, 110, 160, 255))
    d.rectangle((72, 140, 100, 166), fill=(140, 200, 240, 255))
    d.rectangle((156, 140, 184, 166), fill=(140, 200, 240, 255))
    d.rectangle((160, 62, 178, 100), fill=W)


def draw_restaurant(d):
    d.ellipse((58, 70, 198, 210), fill=W)
    d.ellipse((82, 94, 174, 186), outline=(220, 190, 160, 255), width=6)
    d.rectangle((24, 60, 32, 130), fill=W)
    for x in (24, 32, 40):
        d.rectangle((x - 2, 56, x + 2, 100), fill=W)
    d.rectangle((24, 100, 44, 120), fill=W)
    d.rectangle((26, 120, 38, 200), fill=W)
    d.polygon([(214, 58), (232, 58), (232, 130), (214, 130)], fill=W)
    d.rectangle((216, 130, 230, 200), fill=W)


def draw_beach(d):
    d.ellipse((170, 36, 226, 92), fill=(255, 225, 90, 255))
    d.pieslice((40, 70, 170, 170), 180, 360, fill=(255, 90, 90, 255))
    d.pieslice((40, 70, 105, 170), 180, 360, fill=W)
    d.line((105, 120, 105, 190), fill=W, width=8)
    for i, y in enumerate((196, 220)):
        for x in range(28, 200, 60):
            d.arc((x, y - 14, x + 60, y + 14), 0, 180, fill=W, width=7)


def draw_park(d):
    cx, cy, r = 128, 118, 70
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=W, width=8)
    for i in range(8):
        a = i * math.pi / 4
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        d.line((cx, cy, x, y), fill=W, width=5)
        d.ellipse((x - 11, y - 11, x + 11, y + 11), fill=(255, 215, 80, 255))
    d.ellipse((cx - 10, cy - 10, cx + 10, cy + 10), fill=W)
    d.line((cx, cy, 82, 224), fill=W, width=9)
    d.line((cx, cy, 174, 224), fill=W, width=9)


def draw_football(d):
    cx, cy, r = 128, 128, 84
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=W, outline=(30, 30, 30, 255), width=5)
    pts = [(cx + 32 * math.cos(-math.pi / 2 + i * 2 * math.pi / 5),
            cy + 32 * math.sin(-math.pi / 2 + i * 2 * math.pi / 5)) for i in range(5)]
    d.polygon(pts, fill=(30, 30, 30, 255))
    for i, p in enumerate(pts):
        a = -math.pi / 2 + i * 2 * math.pi / 5
        d.line((p[0], p[1], cx + 78 * math.cos(a), cy + 78 * math.sin(a)), fill=(30, 30, 30, 255), width=5)


def draw_heroes(d):
    d.polygon([(50, 50), (206, 50), (206, 130), (128, 222), (50, 130)], fill=W)
    d.polygon([(64, 62), (192, 62), (192, 128), (128, 204), (64, 128)], fill=(40, 80, 200, 255))
    star(d, 128, 120, 52, (255, 215, 80, 255))


def draw_marvel(d):
    d.ellipse((38, 38, 218, 218), fill=W)
    d.ellipse((54, 54, 202, 202), fill=(200, 30, 40, 255))
    d.polygon([(142, 52), (86, 138), (122, 138), (106, 206), (172, 112), (134, 112)], fill=(255, 225, 90, 255))


def draw_zoo(d):
    d.ellipse((78, 130, 178, 214), fill=W)
    for x, y, w in ((40, 100, 40), (88, 52, 42), (130, 52, 42), (176, 100, 40)):
        d.ellipse((x, y, x + w, y + int(w * 1.15)), fill=W)


def draw_space(d):
    for x, y in ((40, 50), (210, 70), (60, 205), (205, 190), (120, 40)):
        d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=W)
    d.arc((24, 96, 232, 170), 200, 340, fill=(255, 215, 80, 255), width=10)
    d.ellipse((82, 82, 174, 174), fill=(255, 160, 80, 255))
    d.arc((24, 96, 232, 170), 20, 160, fill=(255, 215, 80, 255), width=10)
    d.ellipse((98, 98, 128, 128), fill=(255, 200, 130, 255))


def draw_pirate(d):
    d.line((50, 190, 206, 60), fill=W, width=14)
    d.line((50, 60, 206, 190), fill=W, width=14)
    d.ellipse((84, 56, 172, 144), fill=W)
    d.rectangle((102, 130, 154, 164), fill=W)
    k = (60, 40, 30, 255)
    d.ellipse((98, 86, 120, 112), fill=k)
    d.ellipse((136, 86, 158, 112), fill=k)
    d.polygon([(128, 112), (118, 130), (138, 130)], fill=k)
    for x in (112, 124, 136):
        d.line((x, 140, x, 164), fill=k, width=3)


DRAW = dict(palace=draw_palace, house=draw_house, restaurant=draw_restaurant, beach=draw_beach,
            park=draw_park, football=draw_football, heroes=draw_heroes, marvel=draw_marvel,
            zoo=draw_zoo, space=draw_space, pirate=draw_pirate)


def font(size):
    return ImageFont.truetype(os.path.join(HERE, "assets", "fonts", "DejaVuSans-Bold.ttf"), size)


def make_logo(size=512):
    img = Image.new("RGBA", (size, size), (28, 24, 58, 255))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, size - 1, size - 1), size // 6, fill=(28, 24, 58, 255))
    c = size // 2
    d.ellipse((c - 190, c - 150, c + 90, c + 130), fill=(255, 196, 40, 255), outline=(255, 235, 150, 255), width=10)
    d.ellipse((c - 160, c - 120, c + 60, c + 100), outline=(200, 140, 20, 255), width=8)
    f = font(190)
    d.text((c - 50, c - 10), "$", font=f, anchor="mm", fill=(150, 95, 10, 255))
    g = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    gd = ImageDraw.Draw(g)
    gd.rounded_rectangle((300, 90, 460, 170), 18, fill=(230, 230, 245, 255))
    gd.rounded_rectangle((365, 150, 395, 400), 14, fill=(170, 110, 60, 255))
    g = g.rotate(35, center=(380, 250), resample=Image.BICUBIC)
    img.alpha_composite(g)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((90, 410, 420, 438), 12, fill=(120, 90, 50, 255))
    return img


# ------------------------------------------------------------------ sounds
RATE = 22050


def tone(freq, dur, vol=0.5, kind="sine", slide=0.0):
    n = int(RATE * dur)
    out, ph = [], 0.0
    for i in range(n):
        t = i / n
        f = freq + slide * t
        ph += 2 * math.pi * f / RATE
        v = math.sin(ph) if kind == "sine" else (1.0 if math.sin(ph) > 0 else -1.0) * 0.6
        env = min(1.0, i / (RATE * 0.01)) * (1 - t) ** 0.7
        out.append(v * env * vol)
    return out


def write_wav(name, samples):
    path = os.path.join(HERE, "assets", "sounds", name + ".wav")
    with wave.open(path, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, s)) * 32000)) for s in samples))


def build_sounds():
    write_wav("click", tone(1100, 0.04, 0.4))
    write_wav("bid", tone(660, 0.09) + tone(880, 0.14))
    write_wav("pass", tone(440, 0.08, 0.4) + tone(330, 0.12, 0.4))
    write_wav("win", sum([tone(f, 0.13) for f in (523, 659, 784)], []) + tone(1046, 0.35))
    write_wav("prank", tone(300, 0.35, 0.5, "square", slide=-220) + tone(110, 0.25, 0.5, "square"))
    write_wav("lucky", tone(880, 0.07) + tone(1175, 0.07) + tone(1568, 0.18))
    write_wav("end", sum([tone(f, 0.16, 0.5) for f in (392, 523, 659, 784)], []) + tone(1046, 0.5, 0.6))


def main():
    from gamedata import CATEGORIES
    os.makedirs(os.path.join(HERE, "assets", "icons"), exist_ok=True)
    os.makedirs(os.path.join(HERE, "assets", "sounds"), exist_ok=True)
    for c in CATEGORIES:
        img, d = tile(c["color"])
        DRAW[c["id"]](d)
        img.save(os.path.join(HERE, "assets", "icons", c["id"] + ".png"))
    logo = make_logo()
    logo.save(os.path.join(HERE, "assets", "icon.png"))
    pre = Image.new("RGBA", (768, 768), (28, 24, 58, 255))
    pre.alpha_composite(logo.resize((420, 420)), (174, 174))
    pre.save(os.path.join(HERE, "assets", "presplash.png"))
    build_sounds()
    print("assets generated")


if __name__ == "__main__":
    main()
