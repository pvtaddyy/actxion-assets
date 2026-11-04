#!/usr/bin/env python3
"""Turn a 1080x1350 Still Frame card into a 1080x1920 Instagram Story frame.

Usage: python3 story.py card.png out.png [--top "New post"] [--ask "Reply A or B"]
The card sits in Instagram's safe zone (nothing above y=250 or below y=1600, where the profile
row and the reply bar sit) on a blurred, darkened copy of itself. --top is a short line above the
card, --ask a red pill under it: stories made through the API can't carry poll stickers, so the
ask is a reply ("Reply A or B"), which lands in DMs, the strongest signal a story can earn.
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

W, H = 1080, 1920
RED = (230, 30, 40)
INK = (250, 249, 246)
FONTS = Path(__file__).resolve().parents[2] / "actxion-visuals" / "assets" / "fonts"


def font(size):
    return ImageFont.truetype(str(FONTS / "InstrumentSans-Bold.ttf"), size)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("card")
    ap.add_argument("out")
    ap.add_argument("--top", default="")
    ap.add_argument("--ask", default="")
    a = ap.parse_args()

    card = Image.open(a.card).convert("RGB")
    scale = max(W / card.width, H / card.height)
    bg = card.resize((int(card.width * scale) + 1, int(card.height * scale) + 1))
    bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
    bg = ImageEnhance.Brightness(bg.filter(ImageFilter.GaussianBlur(45))).enhance(0.4)

    cw = 930
    fg = card.resize((cw, round(card.height * cw / card.width)), Image.LANCZOS)
    top = 330
    shadow = Image.new("RGBA", (fg.width + 40, fg.height + 40), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((20, 20, fg.width + 20, fg.height + 20), 28, fill=(0, 0, 0, 150))
    bg.paste(shadow.filter(ImageFilter.GaussianBlur(18)), ((W - cw) // 2 - 20, top - 6), shadow.filter(ImageFilter.GaussianBlur(18)))
    m = Image.new("L", fg.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, fg.width, fg.height), 26, fill=255)
    bg.paste(fg, ((W - cw) // 2, top), m)

    d = ImageDraw.Draw(bg)
    if a.top:
        d.text((W // 2, 285), a.top, font=font(44), fill=INK, anchor="ms")
    if a.ask:
        f = font(46)
        tw = d.textlength(a.ask, font=f)
        y = top + fg.height + 30
        d.rounded_rectangle(((W - tw) // 2 - 40, y, (W + tw) // 2 + 40, y + 84), 42, fill=RED)
        d.text((W // 2, y + 42), a.ask, font=f, fill=INK, anchor="mm")
    bg.save(a.out, quality=94)
    print(a.out, bg.size)


if __name__ == "__main__":
    main()
