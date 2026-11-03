#!/usr/bin/env python3
"""ACTXION post renderer: football-artifact templates, not generic AI cards.

Usage:
  python3 render.py <template> --spec spec.json --out post.png [--size x|portrait|square]

Templates (see SKILL.md for the spec fields of each):
  backpage    red-top tabloid back page, halftone photo, giant headline
  ballot      a paper ballot slip for a Fan verdict A-or-B question
  scoreboard  stadium dot-matrix scoreboard for a full-time result
  rumour      a typed transfer dossier with a reliability-tier rubber stamp
  redcard     a quote printed on a referee's red card

Needs Pillow. Fonts and logo masks ship in ../assets, so it runs the same on a Mac or a
Linux cloud box. Photos can be a local path or an https URL (Wikimedia Commons).
"""
import argparse
import io
import json
import math
import random
import re
import sys
import urllib.request
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets"
FONTS = ASSETS / "fonts"

# Brand: black, white, red. The red is a referee's card, not a UI accent.
RED = (230, 30, 40)
INK = (17, 16, 15)            # printer's black, slightly warm
PAPER = (242, 238, 229)       # newsprint
PAPER_SHADE = (226, 220, 208)
WHITE = (250, 249, 246)
PITCH_NIGHT = (16, 18, 17)
LED_OFF = (40, 22, 22)

SIZES = {"x": (1600, 900), "portrait": (1080, 1350), "square": (1080, 1080)}
SS = 2  # supersample factor


# ---------- copy hygiene: keep the tells out of the text ----------
def clean(text, headline=False):
    """Remove the punctuation habits that make copy read machine-written."""
    t = (text or "").strip()
    t = t.replace("—", ",").replace("–", "-").replace("_", " ")
    t = re.sub(r"\s{2,}", " ", t)
    if headline:
        t = t.rstrip(".")  # a headline never ends in a full stop; ? and ! are fine
    return t


# ---------- primitives ----------
def font(name, size):
    files = {
        "anton": "Anton-Regular.ttf",
        "barlow": "BarlowCondensed-SemiBold.ttf",
        "barlow-bold": "BarlowCondensed-Bold.ttf",
        "barlow-xb": "BarlowCondensed-ExtraBold.ttf",
        "barlow-med": "BarlowCondensed-Medium.ttf",
        "serif": "SourceSerif4[opsz,wght].ttf",
        "narrow": "ArchivoNarrow[wght].ttf",
    }
    f = ImageFont.truetype(str(FONTS / files[name]), int(size * SS))
    if name == "serif":
        try:
            f.set_variation_by_axes([24, 520])
        except Exception:
            pass
    return f


def mask(name, height):
    m = Image.open(ASSETS / "logo" / f"{name}-mask.png").convert("L")
    w = round(m.width * height / m.height)
    return m.resize((w, int(height)), Image.LANCZOS)


def stamp_mask(img, m, xy, color):
    img.paste(Image.new("RGB", m.size, color), xy, m)


def fit(draw, text, fname, max_w, max_lines, start, min_size=20, upper=False, max_h=None, lead=1.05):
    """Largest size where text wraps into max_lines inside max_w (and max_h). Returns (font, lines)."""
    if upper:
        text = text.upper()
    size = start
    while size >= min_size:
        f = font(fname, size)
        lines, cur = [], ""
        for word in text.split():
            trial = (cur + " " + word).strip()
            if draw.textlength(trial, font=f) <= max_w * SS:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        tall_ok = max_h is None or len(lines) * f.size * lead <= max_h * SS
        if len(lines) <= max_lines and tall_ok and all(draw.textlength(l, font=f) <= max_w * SS for l in lines):
            return f, lines
        size -= 2
    return font(fname, min_size), [text]


def grain(img, amount=18):
    n = Image.effect_noise(img.size, amount).convert("L")
    n = n.point(lambda v: 128 + (v - 128) // 3)
    return ImageChops.overlay(img, Image.merge("RGB", (n, n, n)))


def load_photo(src):
    if not src:
        return None
    if re.match(r"^https?://", src):
        # Wikimedia only serves standard thumbnail widths; fall back to ones it accepts, then the original
        tries = [src]
        m = re.match(r"(https://[^/]*wikimedia\.org/wikipedia/commons)/thumb/(.+?)/\d+px-[^/]+$", src)
        if m:
            tries += [re.sub(r"/\d+px-", "/3840px-", src), re.sub(r"/\d+px-", "/1920px-", src),
                      f"{m.group(1).replace('thumb.wikimedia.org', 'upload.wikimedia.org')}/{m.group(2)}"]
        last = None
        for u in dict.fromkeys(tries):
            try:
                req = urllib.request.Request(u, headers={"User-Agent": "ACTXION-visuals/1.0 (https://github.com/pvtaddyy/actxion-assets)"})
                data = urllib.request.urlopen(req, timeout=30).read()
                return Image.open(io.BytesIO(data)).convert("RGB")
            except Exception as e:  # try the next size
                last = e
        raise last
    return Image.open(src).convert("RGB")


def cover(im, w, h, focus_y=0.35):
    """Crop-to-fill, biased upward so faces stay in frame."""
    scale = max(w / im.width, h / im.height)
    im = im.resize((math.ceil(im.width * scale), math.ceil(im.height * scale)), Image.LANCZOS)
    x = (im.width - w) // 2
    y = int((im.height - h) * focus_y)
    return im.crop((x, y, x + w, y + h))


def halftone(photo, w, h, cell=9, ink=INK, paper=PAPER, angle=45):
    """Newspaper halftone: a file photo printed, not filtered. Hides age and noise."""
    g = ImageOps.autocontrast(cover(photo, w, h).convert("L"), cutoff=2)
    g = ImageOps.equalize(g).filter(ImageFilter.GaussianBlur(0.6))
    big = int(math.hypot(w, h)) + cell * 2
    rot = g.rotate(angle, expand=True, fillcolor=255).resize((big, big))
    dots = Image.new("L", (big, big), 0)
    dd = ImageDraw.Draw(dots)
    for y in range(0, big, cell):
        for x in range(0, big, cell):
            v = rot.getpixel((min(x + cell // 2, big - 1), min(y + cell // 2, big - 1)))
            r = (1 - v / 255) * cell * 0.72
            if r > 0.4:
                dd.ellipse((x + cell / 2 - r, y + cell / 2 - r, x + cell / 2 + r, y + cell / 2 + r), fill=255)
    dots = dots.rotate(-angle)
    ox, oy = (dots.width - w) // 2, (dots.height - h) // 2
    dots = dots.crop((ox, oy, ox + w, oy + h))
    out = Image.new("RGB", (w, h), paper)
    out.paste(Image.new("RGB", (w, h), ink), (0, 0), dots)
    return out


def credit_line(draw, xy, text, fill, size=17):
    if text:
        draw.text(xy, clean(text), font=font("narrow", size), fill=fill)


# ---------- templates ----------
def t_backpage(spec, W, H):
    """Red-top tabloid back page. Spec: headline, kicker, photo, credit, date."""
    img = Image.new("RGB", (W * SS, H * SS), PAPER)
    d = ImageDraw.Draw(img)
    portrait = H > W
    # Masthead: the red top
    mh = int((150 if portrait else 120) * SS)
    d.rectangle((0, 0, W * SS, mh), fill=RED)
    wm = mask("wordmark", (52 if portrait else 46) * SS)
    stamp_mask(img, wm, (int(56 * SS), (mh - wm.height) // 2), WHITE)
    tag = clean(spec.get("date") or "THE FAN VERDICT")
    tf = font("barlow-bold", 30)
    d.text((W * SS - int(56 * SS) - d.textlength(tag, font=tf), (mh - 34 * SS) // 2), tag.upper(), font=tf, fill=WHITE)
    d.rectangle((0, mh, W * SS, mh + int(6 * SS)), fill=INK)

    photo = load_photo(spec.get("photo"))
    m = int(56 * SS)
    if portrait:
        ph_h = int(H * SS * 0.42)
        head_box = (m, mh + int(40 * SS), W * SS - m, mh + int(40 * SS) + int(H * SS * 0.26))
        ph_box = (0, H * SS - ph_h - int(150 * SS), W * SS, H * SS - int(150 * SS))
    else:
        ph_w = int(W * SS * 0.40)
        ph_box = (W * SS - ph_w, mh + int(6 * SS), W * SS, H * SS)
        head_box = (m, mh + int(50 * SS), W * SS - ph_w - m, H * SS - int(170 * SS))
    if photo:
        bw, bh = ph_box[2] - ph_box[0], ph_box[3] - ph_box[1]
        img.paste(treat(photo, bw, bh, spec, lambda: halftone(photo, bw, bh, cell=int(8 * SS))), ph_box[:2])
        if spec.get("credit"):  # credit on a paper tab, like a picture desk caption
            cf = font("narrow", 17)
            ct = clean(spec["credit"])
            tw = d.textlength(ct, font=cf)
            d.rectangle((ph_box[0], ph_box[3] - int(34 * SS), ph_box[0] + tw + int(28 * SS), ph_box[3]), fill=PAPER)
            d.text((ph_box[0] + int(14 * SS), ph_box[3] - int(28 * SS)), ct, font=cf, fill=INK)

    head = clean(spec.get("headline", ""), headline=True).upper()
    max_w = (head_box[2] - head_box[0]) / SS
    kick_room = 120 if spec.get("kicker") else 0
    max_h = (head_box[3] - head_box[1]) / SS - kick_room
    hf, lines = fit(d, head, "anton", max_w, 4 if not portrait else 3, 150 if not portrait else 120, max_h=max_h, lead=1.02)
    y = head_box[1]
    lh = int(hf.size * 1.02)
    for ln in lines:
        d.text((head_box[0], y), ln, font=hf, fill=INK)
        y += lh
    kick = clean(spec.get("kicker", ""))
    if kick:
        kf, klines = fit(d, kick, "serif", max_w, 2, 38)
        y += int(34 * SS)
        d.rectangle((head_box[0], y + int(8 * SS), head_box[0] + int(10 * SS), y + int(8 * SS) + len(klines) * int(kf.size * 1.25) - int(14 * SS)), fill=RED)
        for ln in klines:
            d.text((head_box[0] + int(28 * SS), y), ln, font=kf, fill=INK)
            y += int(kf.size * 1.25)
    footer(d, W, H, dark=False)
    return img


def t_ballot(spec, W, H):
    """A paper ballot slip. Spec: question, option_a, option_b, context."""
    img = Image.new("RGB", (W * SS, H * SS), PITCH_NIGHT)
    d = ImageDraw.Draw(img)
    pitch_lines(d, W, H, (34, 38, 36))
    sw, sh = int(W * SS * (0.86 if H > W else 0.64)), int(H * SS * (0.80 if H > W else 0.80))
    slip = Image.new("RGB", (sw, sh), PAPER)
    sd = ImageDraw.Draw(slip)
    pad = int(52 * SS)
    sd.rectangle((0, 0, sw, int(84 * SS)), fill=INK)
    wm = mask("wordmark", 34 * SS)
    stamp_mask(slip, wm, (pad, (int(84 * SS) - wm.height) // 2), PAPER)
    lab = "FAN VERDICT"
    lf = font("barlow-xb", 30)
    sd.text((sw - pad - sd.textlength(lab, font=lf), int(22 * SS)), lab, font=lf, fill=RED)
    for x in range(0, sw, int(18 * SS)):  # perforation along the top tear line
        sd.ellipse((x, int(96 * SS), x + int(6 * SS), int(102 * SS)), fill=PAPER_SHADE)
    q = clean(spec.get("question", ""), headline=True)
    qf, ql = fit(sd, q, "anton", (sw - 2 * pad) / SS, 3, 92, upper=True)
    y = int(130 * SS)
    for ln in ql:
        sd.text((pad, y), ln.upper(), font=qf, fill=INK)
        y += int(qf.size * 1.04)
    y += int(44 * SS)
    of = font("barlow-bold", 52)
    box = int(62 * SS)
    for i, opt in enumerate([spec.get("option_a", ""), spec.get("option_b", "")]):
        oy = y + i * int(box * 1.45)
        sd.rectangle((pad, oy, pad + box, oy + box), outline=INK, width=int(4 * SS))
        sd.text((pad + box + int(26 * SS), oy + int(2 * SS)), clean(opt, headline=True).upper(), font=of, fill=INK)
    ctx = clean(spec.get("context", ""))
    if ctx:
        cf, cl = fit(sd, ctx, "serif", (sw - 2 * pad) / SS - 360, 3, 28)
        cy = sh - pad - len(cl) * int(cf.size * 1.3)
        for ln in cl:
            sd.text((pad, cy), ln, font=cf, fill=(70, 66, 60))
            cy += int(cf.size * 1.3)
    slip = grain(slip, 14)
    # Red rubber stamp, slightly crooked
    st = rubber_stamp("VOTE IN THE REPLIES", 30, RED)
    slip.paste(st, (sw - st.width - int(40 * SS), sh - st.height - int(36 * SS)), st.split()[3])
    rot = slip.rotate(-1.6, expand=True, resample=Image.BICUBIC, fillcolor=PITCH_NIGHT)
    shadow = Image.new("L", rot.size, 0)
    shadow.paste(255, (0, 0, rot.width, rot.height))
    img.paste((8, 8, 8), ((W * SS - rot.width) // 2 + int(10 * SS), (H * SS - rot.height) // 2 + int(14 * SS)), shadow.filter(ImageFilter.GaussianBlur(18 * SS)).point(lambda v: v // 2))
    img.paste(rot, ((W * SS - rot.width) // 2, (H * SS - rot.height) // 2))
    return img


def t_scoreboard_core(spec, W, H):
    """Stadium dot-matrix scoreboard. Spec: home, away, home_score, away_score, scorers, status, question."""
    img = Image.new("RGB", (W * SS, H * SS), (8, 8, 9))
    d = ImageDraw.Draw(img)
    m = int(60 * SS)
    board = (m, m, W * SS - m, int(H * SS * (0.70 if H <= W else 0.62)))
    d.rectangle(board, fill=(14, 12, 12), outline=(50, 50, 52), width=int(6 * SS))
    for bx in (board[0] + int(30 * SS), board[2] - int(42 * SS)):  # bolts
        for by in (board[1] + int(26 * SS), board[3] - int(38 * SS)):
            d.ellipse((bx, by, bx + int(12 * SS), by + int(12 * SS)), fill=(60, 60, 62))
    bw, bh = board[2] - board[0], board[3] - board[1]
    status = clean(spec.get("status") or "FULL TIME", headline=True).upper()
    led_text(img, status, (board[0] + bw // 2, board[1] + int(bh * 0.16)), int(bh * 0.10), RED, center=True)
    home, away = clean(spec.get("home", ""), True).upper(), clean(spec.get("away", ""), True).upper()
    hs, as_ = str(spec.get("home_score", "")), str(spec.get("away_score", ""))
    row_y = board[1] + int(bh * 0.50)
    cell_h = int(bh * 0.26)
    led_text(img, home, (board[0] + int(bw * 0.06), row_y), int(cell_h * 0.62), WHITE)
    led_text(img, away, (board[0] + int(bw * 0.06), row_y + int(cell_h * 0.95)), int(cell_h * 0.62), WHITE)
    led_text(img, hs, (board[2] - int(bw * 0.10), row_y), int(cell_h * 0.62), WHITE, right=True)
    led_text(img, as_, (board[2] - int(bw * 0.10), row_y + int(cell_h * 0.95)), int(cell_h * 0.62), WHITE, right=True)
    d = ImageDraw.Draw(img)
    y = board[3] + int(34 * SS)
    sc = clean(spec.get("scorers", ""))
    if sc:
        sf, sl = fit(d, sc, "barlow-med", (W * SS - 2 * m) / SS, 2, 34)
        for ln in sl:
            d.text((m, y), ln, font=sf, fill=(170, 168, 162))
            y += int(sf.size * 1.2)
    q = clean(spec.get("question", ""), headline=True)
    if q:
        qf, ql = fit(d, q, "anton", (W * SS - 2 * m) / SS, 2, 64, upper=True)
        y += int(14 * SS)
        for ln in ql:
            d.text((m, y), ln.upper(), font=qf, fill=WHITE)
            y += int(qf.size * 1.05)
    footer(d, W, H, dark=True)
    return grain(img, 10)


def t_rumour(spec, W, H):
    """Typed transfer dossier. Spec: player, from_club, to_club, fee, source, tier (1-3), photo, credit, note."""
    img = Image.new("RGB", (W * SS, H * SS), (196, 176, 138))  # manila folder
    d = ImageDraw.Draw(img)
    m = int(56 * SS)
    sheet = (m, m, W * SS - m, H * SS - m)
    d.rectangle((sheet[0] + int(8 * SS), sheet[1] + int(10 * SS), sheet[2] + int(8 * SS), sheet[3] + int(10 * SS)), fill=(150, 130, 98))
    d.rectangle(sheet, fill=PAPER)
    pad = int(54 * SS)
    x0, y0 = sheet[0] + pad, sheet[1] + pad
    wm = mask("wordmark", 34 * SS)
    stamp_mask(img, wm, (x0, y0), INK)
    d.text((x0 + wm.width + int(24 * SS), y0 + int(2 * SS)), "RUMOUR DESK  /  TRANSFER FILE", font=font("barlow-bold", 28), fill=RED)
    d.line((x0, y0 + int(62 * SS), sheet[2] - pad, y0 + int(62 * SS)), fill=INK, width=int(3 * SS))
    photo = load_photo(spec.get("photo"))
    portrait = H > W
    text_right = sheet[2] - pad
    if photo:
        pw = int((sheet[2] - sheet[0]) * (0.34 if not portrait else 0.42))
        ph = int(pw * 1.22)
        px, py = sheet[2] - pad - pw, y0 + int(96 * SS)
        img.paste(treat(photo, pw, ph, spec, lambda: halftone(photo, pw, ph, cell=int(7 * SS))), (px, py))
        d.rectangle((px, py, px + pw, py + ph), outline=INK, width=int(3 * SS))
        credit_line(d, (px, py + ph + int(10 * SS)), spec.get("credit"), (90, 86, 78), 16)
        text_right = px - int(40 * SS)
    lf, vf = font("barlow-bold", 26), font("narrow", 46)
    y = y0 + int(100 * SS)
    for label, key in (("PLAYER", "player"), ("FROM", "from_club"), ("TO", "to_club"), ("FEE", "fee"), ("SOURCE", "source")):
        val = clean(str(spec.get(key, "") or ""), headline=True)
        if not val:
            continue
        d.text((x0, y), label, font=lf, fill=(120, 114, 104))
        vff, vl = fit(d, val, "narrow", (text_right - x0) / SS, 1, 46 if key != "player" else 70)
        d.text((x0, y + int(30 * SS)), vl[0], font=vff, fill=INK)
        y += int(30 * SS) + int(vff.size * 1.15) + int(10 * SS)
        d.line((x0, y - int(6 * SS), text_right, y - int(6 * SS)), fill=PAPER_SHADE, width=int(2 * SS))
    tier = int(spec.get("tier", 2))
    words = {1: "TIER 1  CREDIBLE", 2: "TIER 2  UNCONFIRMED", 3: "TIER 3  PINCH OF SALT"}[max(1, min(3, tier))]
    st = rubber_stamp(words, 44, RED, rot=-8)
    img.paste(st, (sheet[2] - pad - st.width, sheet[3] - pad - st.height), st.split()[3])
    note = clean(spec.get("note", ""))
    if note:
        nf, nl = fit(d, note, "serif", (text_right - x0 - st.width / SS * 0 - 40) / SS, 2, 26)
    return grain(img, 14)


def t_redcard(spec, W, H):
    """Quote on a referee's red card. Spec: quote, speaker, context."""
    img = Image.new("RGB", (W * SS, H * SS), PITCH_NIGHT)
    d = ImageDraw.Draw(img)
    pitch_lines(d, W, H, (32, 36, 34))
    portrait = H > W
    cw = int(W * SS * (0.80 if portrait else 0.50))
    ch = int(cw * 1.40)
    if ch > H * SS * 0.86:
        ch = int(H * SS * 0.86)
        cw = int(ch / 1.40)
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    cd = ImageDraw.Draw(card)
    cd.rounded_rectangle((0, 0, cw, ch), radius=int(22 * SS), fill=RED)
    pad = int(48 * SS)
    qmark = font("anton", 150)
    cd.text((pad, pad - int(40 * SS)), "“", font=qmark, fill=(150, 12, 20, 255))
    q = clean(spec.get("quote", ""), headline=True)
    qf, ql = fit(cd, q, "anton", (cw - 2 * pad) / SS, 7, 74, 30, upper=True)
    y = pad + int(100 * SS)
    for ln in ql:
        cd.text((pad, y), ln.upper(), font=qf, fill=WHITE)
        y += int(qf.size * 1.06)
    sp = clean(spec.get("speaker", ""), headline=True)
    cd.text((pad, ch - pad - int(70 * SS)), sp.upper(), font=font("barlow-xb", 34), fill=INK)
    ctx = clean(spec.get("context", ""))
    if ctx:
        cf, cl = fit(cd, ctx, "barlow-med", (cw - 2 * pad) / SS, 1, 26)
        cd.text((pad, ch - pad - int(30 * SS)), cl[0], font=cf, fill=(60, 10, 12))
    card = card.rotate(4.5, expand=True, resample=Image.BICUBIC)
    sh = Image.new("L", card.size, 0)
    sh.paste(card.split()[3])
    cx = (W * SS - card.width) // 2 if portrait else int(W * SS * 0.40)
    cy = (H * SS - card.height) // 2
    img.paste((0, 0, 0), (cx + int(16 * SS), cy + int(22 * SS)), sh.filter(ImageFilter.GaussianBlur(20 * SS)).point(lambda v: int(v * 0.6)))
    img.paste(card, (cx, cy), card)
    if not portrait:
        wm = mask("wordmark", 40 * SS)
        stamp_mask(img, wm, (int(70 * SS), int(70 * SS)), WHITE)
        side = clean(spec.get("label") or "STRAIGHT RED", True).upper()
        sf, sl = fit(d, side, "anton", (cx / SS) - 120, 3, 110, upper=True)
        d = ImageDraw.Draw(img)
        yy = int(H * SS * 0.38)
        for ln in sl:
            d.text((int(70 * SS), yy), ln, font=sf, fill=WHITE)
            yy += int(sf.size * 1.02)
    footer(ImageDraw.Draw(img), W, H, dark=True)
    return grain(img, 10)


# ---------- shared pieces ----------
def pitch_lines(d, W, H, color):
    w = int(3 * SS)
    cx, cy = int(W * SS * 0.5), int(H * SS * 0.5)
    r = int(min(W, H) * SS * 0.22)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=color, width=w)
    d.line((cx, 0, cx, H * SS), fill=color, width=w)
    d.rectangle((-w, int(H * SS * 0.22), int(W * SS * 0.12), int(H * SS * 0.78)), outline=color, width=w)
    d.rectangle((int(W * SS * 0.88), int(H * SS * 0.22), W * SS + w, int(H * SS * 0.78)), outline=color, width=w)


def rubber_stamp(text, size, color, rot=-6):
    f = font("barlow-xb", size)
    tmp = ImageDraw.Draw(Image.new("L", (1, 1)))
    tw = int(tmp.textlength(text, font=f))
    pad = int(18 * SS)
    w, h = tw + 2 * pad, int(f.size * 1.3) + pad
    m = Image.new("L", (w, h), 0)
    md = ImageDraw.Draw(m)
    md.rectangle((int(3 * SS), int(3 * SS), w - int(3 * SS), h - int(3 * SS)), outline=255, width=int(5 * SS))
    md.text((pad, pad // 2 + int(4 * SS)), text, font=f, fill=255)
    rnd = random.Random(len(text))
    worn = Image.new("L", (w, h), 255)
    wd = ImageDraw.Draw(worn)
    for _ in range(w * h // (220 * SS * SS)):  # ink skips, like a real stamp
        x, y = rnd.randint(0, w), rnd.randint(0, h)
        s = rnd.randint(1, 4) * SS
        wd.ellipse((x, y, x + s, y + s), fill=0)
    m = ImageChops.multiply(m, worn)
    out = Image.new("RGBA", (w, h), color + (0,))
    out.putalpha(m.point(lambda v: int(v * 0.88)))
    return out.rotate(rot, expand=True, resample=Image.BICUBIC)


def led_text(img, text, xy, height, color, center=False, right=False):
    """Draw text as lit LED dots on a matrix, like a stadium board."""
    f = font("barlow-xb", height / SS * 1.25)
    tmp = ImageDraw.Draw(Image.new("L", (1, 1)))
    tw = int(tmp.textlength(text, font=f)) + 4
    th = int(f.size * 1.2)
    m = Image.new("L", (tw, th), 0)
    ImageDraw.Draw(m).text((2, 0), text, font=f, fill=255)
    m = m.crop(m.getbbox() or (0, 0, tw, th))
    pitch = max(4, height // 14)
    cols, rows = max(1, m.width // pitch), max(1, m.height // pitch)
    small = m.resize((cols, rows), Image.BOX)
    x0, y0 = xy
    if center:
        x0 -= cols * pitch // 2
    if right:
        x0 -= cols * pitch
    d = ImageDraw.Draw(img)
    r = pitch * 0.42
    for j in range(rows):
        for i in range(cols):
            on = small.getpixel((i, j)) > 110
            cx, cy = x0 + i * pitch + pitch / 2, y0 + j * pitch + pitch / 2
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=color if on else LED_OFF)


def footer(d, W, H, dark=True):
    f = font("barlow-bold", 24)
    col = (150, 148, 142) if dark else (110, 104, 94)
    h = "@ACTXIONAPP"
    d.text((W * SS - int(56 * SS) - d.textlength(h, font=f), H * SS - int(52 * SS)), h, font=f, fill=RED if dark else INK)




# ---------- photo-led variants ----------
def duotone(photo, w, h, dark=INK, light=PAPER, focus_y=0.30, contrast=1.15):
    """Print a file photo in two inks. Faces stay readable, age and colour casts disappear."""
    g = ImageOps.autocontrast(cover(photo, w, h, focus_y).convert("L"), cutoff=1)
    g = g.point(lambda v: max(0, min(255, int((v - 128) * contrast + 128))))
    return ImageOps.colorize(g, black=dark, white=light)


def natural(photo, w, h, focus_y=0.30):
    """The photo as it was taken, in full colour: just cropped, levelled and sharpened."""
    im = ImageOps.autocontrast(cover(photo.convert("RGB"), w, h, focus_y), cutoff=0.5)
    im = ImageEnhance.Color(im).enhance(1.05)
    return im.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=3))


def treat(photo, w, h, spec, printed):
    """Real colour by default. spec photo_style "print" keeps the old halftone/duotone look."""
    if (spec or {}).get("photo_style") == "print":
        return printed()
    return natural(photo, w, h)


def photo_card(photo, w, h, credit=None, dark=INK, light=PAPER, label=None, label_bg=RED, spec=None):
    """A photo with a thin keyline, an optional label tab and a credit line."""
    card = treat(photo, w, h, spec, lambda: grain(duotone(photo, w, h, dark, light), 12))
    d = ImageDraw.Draw(card)
    d.rectangle((0, 0, w - 1, h - 1), outline=INK, width=int(3 * SS))
    if label:
        lf = font("barlow-xb", 30)
        tw = d.textlength(label, font=lf)
        d.rectangle((0, h - int(56 * SS), tw + int(36 * SS), h), fill=label_bg)
        d.text((int(18 * SS), h - int(50 * SS)), label, font=lf, fill=WHITE)
    if credit:
        cf = font("narrow", 15)
        ct = clean(credit)
        cw = d.textlength(ct, font=cf)
        d.rectangle((w - cw - int(22 * SS), 0, w, int(28 * SS)), fill=PAPER)
        d.text((w - cw - int(11 * SS), int(4 * SS)), ct, font=cf, fill=INK)
    return card


def t_ballot_photos(spec, W, H):
    """Ballot slip with a photo above each tick box: a straight A-or-B choice between two people."""
    img = Image.new("RGB", (W * SS, H * SS), PITCH_NIGHT)
    d = ImageDraw.Draw(img)
    pitch_lines(d, W, H, (34, 38, 36))
    sw, sh = int(W * SS * 0.90), int(H * SS * 0.90)
    slip = Image.new("RGB", (sw, sh), PAPER)
    sd = ImageDraw.Draw(slip)
    pad = int(44 * SS)
    sd.rectangle((0, 0, sw, int(78 * SS)), fill=INK)
    wm = mask("wordmark", 32 * SS)
    stamp_mask(slip, wm, (pad, (int(78 * SS) - wm.height) // 2), PAPER)
    lf = font("barlow-xb", 30)
    sd.text((sw - pad - sd.textlength("FAN VERDICT", font=lf), int(20 * SS)), "FAN VERDICT", font=lf, fill=RED)
    # Question on the left, two photo ballots on the right
    qw = int(sw * 0.40)
    q = clean(spec.get("question", ""), headline=True)
    qf, ql = fit(sd, q, "anton", (qw - pad) / SS, 5, 80, upper=True, max_h=(sh - int(260 * SS)) / SS)
    y = int(120 * SS)
    for ln in ql:
        sd.text((pad, y), ln, font=qf, fill=INK)
        y += int(qf.size * 1.04)
    ctx = clean(spec.get("context", ""))
    if ctx:
        # Context sits under the question so the stamp at the foot never covers it
        cf, cl = fit(sd, ctx, "serif", (qw - pad) / SS, 3, 26)
        cy = y + int(26 * SS)
        for ln in cl:
            sd.text((pad, cy), ln, font=cf, fill=(70, 66, 60))
            cy += int(cf.size * 1.3)
    gap = int(28 * SS)
    cw = (sw - qw - pad - gap) // 2
    ch = sh - int(78 * SS) - int(40 * SS) - int(120 * SS)
    for i, key in enumerate(("a", "b")):
        x = qw + i * (cw + gap)
        ph = load_photo(spec.get(f"photo_{key}"))
        top = int(78 * SS) + int(36 * SS)
        if ph:
            slip.paste(photo_card(ph, cw, ch, spec.get(f"credit_{key}"), spec=spec), (x, top))
        else:
            sd.rectangle((x, top, x + cw, top + ch), fill=PAPER_SHADE)
        box = int(50 * SS)
        by = top + ch + int(22 * SS)
        sd.rectangle((x, by, x + box, by + box), outline=INK, width=int(4 * SS))
        of, ol = fit(sd, clean(spec.get(f"option_{key}", ""), headline=True), "barlow-xb", (cw - box - 20 * SS) / SS, 1, 46, upper=True)
        sd.text((x + box + int(18 * SS), by - int(2 * SS)), ol[0], font=of, fill=INK)
    slip = grain(slip, 10)
    rot = slip.rotate(-1.2, expand=True, resample=Image.BICUBIC, fillcolor=PITCH_NIGHT)
    img.paste(rot, ((W * SS - rot.width) // 2, (H * SS - rot.height) // 2))
    st = rubber_stamp("VOTE IN THE REPLIES", 28, RED, rot=-8)
    img.paste(st, (int(W * SS * 0.05) + int(30 * SS), int(H * SS * 0.86) - st.height), st.split()[3])
    return img


def t_redcard_photo(spec, W, H):
    """The speaker's printed photo on the left, their words on the red card on the right."""
    img = Image.new("RGB", (W * SS, H * SS), PITCH_NIGHT)
    d = ImageDraw.Draw(img)
    pw = int(W * SS * 0.46)
    ph = load_photo(spec["photo"])
    img.paste(treat(ph, pw, H * SS, spec, lambda: grain(duotone(ph, pw, H * SS, dark=(10, 10, 12), light=(205, 200, 190)), 12)), (0, 0))
    wm = mask("wordmark", 38 * SS)
    d.rectangle((0, 0, wm.width + int(80 * SS), int(98 * SS)), fill=PITCH_NIGHT)
    stamp_mask(img, wm, (int(40 * SS), int(30 * SS)), WHITE)
    if spec.get("credit"):
        cf = font("narrow", 15)
        ct = clean(spec["credit"])
        d.rectangle((0, H * SS - int(30 * SS), d.textlength(ct, font=cf) + int(30 * SS), H * SS), fill=PITCH_NIGHT)
        d.text((int(16 * SS), H * SS - int(26 * SS)), ct, font=cf, fill=(160, 158, 152))
    cw = int(W * SS * 0.44)
    ch = min(int(cw * 1.38), int(H * SS * 0.84))
    cw = int(ch / 1.38)
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    cd = ImageDraw.Draw(card)
    cd.rounded_rectangle((0, 0, cw, ch), radius=int(22 * SS), fill=RED)
    pad = int(44 * SS)
    cd.text((pad, pad - int(40 * SS)), "“", font=font("anton", 140), fill=(150, 12, 20, 255))
    q = clean(spec.get("quote", ""), headline=True)
    qf, ql = fit(cd, q, "anton", (cw - 2 * pad) / SS, 7, 70, 28, upper=True, max_h=(ch - 260 * SS) / SS)
    y = pad + int(92 * SS)
    for ln in ql:
        cd.text((pad, y), ln, font=qf, fill=WHITE)
        y += int(qf.size * 1.06)
    cd.text((pad, ch - pad - int(70 * SS)), clean(spec.get("speaker", ""), True).upper(), font=font("barlow-xb", 32), fill=INK)
    ctx = clean(spec.get("context", ""))
    if ctx:
        cf2, cl2 = fit(cd, ctx, "barlow-med", (cw - 2 * pad) / SS, 1, 24)
        cd.text((pad, ch - pad - int(30 * SS)), cl2[0], font=cf2, fill=(60, 10, 12))
    card = card.rotate(4, expand=True, resample=Image.BICUBIC)
    sh = Image.new("L", card.size, 0)
    sh.paste(card.split()[3])
    cx, cy = pw + int((W * SS - pw - card.width) * 0.45), (H * SS - card.height) // 2
    img.paste((0, 0, 0), (cx + int(16 * SS), cy + int(20 * SS)), sh.filter(ImageFilter.GaussianBlur(20 * SS)).point(lambda v: int(v * 0.6)))
    img.paste(card, (cx, cy), card)
    footer(ImageDraw.Draw(img), W, H, dark=True)
    return img


def t_scoreboard_photo(spec, W, H):
    """Scoreboard on the left, the player or manager of the night printed on the right."""
    pw = int(W * SS * 0.36)
    img = Image.new("RGB", (W * SS, H * SS), (8, 8, 9))
    ph = load_photo(spec["photo"])
    img.paste(treat(ph, pw, H * SS, spec, lambda: grain(duotone(ph, pw, H * SS, dark=(12, 8, 8), light=RED), 12)), (W * SS - pw, 0))
    sub = t_scoreboard_core(spec, W - pw // SS, H)
    img.paste(sub, (0, 0))
    d = ImageDraw.Draw(img)
    lab = clean(spec.get("photo_label", ""), True).upper()
    if lab:
        lf = font("barlow-xb", 30)
        tw = d.textlength(lab, font=lf)
        d.rectangle((W * SS - pw, H * SS - int(70 * SS), W * SS - pw + tw + int(40 * SS), H * SS - int(14 * SS)), fill=INK)
        d.text((W * SS - pw + int(20 * SS), H * SS - int(64 * SS)), lab, font=lf, fill=WHITE)
    if spec.get("credit"):
        cf = font("narrow", 15)
        ct = clean(spec["credit"])
        cw = d.textlength(ct, font=cf)
        d.rectangle((W * SS - cw - int(24 * SS), 0, W * SS, int(28 * SS)), fill=(8, 8, 9))
        d.text((W * SS - cw - int(12 * SS), int(4 * SS)), ct, font=cf, fill=(170, 168, 162))
    return img


def t_poster(spec, W, H):
    """One big story: the person printed full height in red and black, one line of headline beside them."""
    img = Image.new("RGB", (W * SS, H * SS), INK)
    d = ImageDraw.Draw(img)
    portrait = H > W
    ph = load_photo(spec.get("photo"))
    if portrait:
        box = (0, 0, W * SS, int(H * SS * 0.60))
    else:
        box = (int(W * SS * 0.42), 0, W * SS, H * SS)
    bw, bh = box[2] - box[0], box[3] - box[1]
    if ph:
        img.paste(treat(ph, bw, bh, spec, lambda: grain(duotone(ph, bw, bh, dark=(14, 6, 7), light=RED, contrast=1.25), 14)), box[:2])
    m = int(60 * SS)
    wm = mask("wordmark", 40 * SS)
    stamp_mask(img, wm, (m, m), WHITE)
    lab = clean(spec.get("label", ""), True).upper()
    if lab:
        st = rubber_stamp(lab, 30, WHITE, rot=-5)
        img.paste(st, (m - int(8 * SS), m + wm.height + int(34 * SS)), st.split()[3])
    tx0 = m
    tx1 = (box[0] - int(40 * SS)) if not portrait else W * SS - m
    ty0 = int(H * SS * 0.30) if not portrait else box[3] + int(40 * SS)
    ty1 = H * SS - int(150 * SS)
    head = clean(spec.get("headline", ""), headline=True)
    hf, hl = fit(d, head, "anton", (tx1 - tx0) / SS, 4, 140, upper=True, max_h=(ty1 - ty0) / SS - 90, lead=1.02)
    y = ty0
    for ln in hl:
        d.text((tx0, y), ln, font=hf, fill=WHITE)
        y += int(hf.size * 1.02)
    kick = clean(spec.get("kicker", ""))
    if kick:
        kf, kl = fit(d, kick, "barlow-med", (tx1 - tx0) / SS, 3, 34)
        y += int(44 * SS)
        for ln in kl:
            d.text((tx0, y), ln, font=kf, fill=(236, 232, 224))
            y += int(kf.size * 1.25)
    if spec.get("credit"):
        cf = font("narrow", 15)
        ct = clean(spec["credit"])
        cw = d.textlength(ct, font=cf)
        # Bottom-left of the photo on a dark tab, clear of the handle in the bottom-right corner
        d.rectangle((box[0], box[3] - int(30 * SS), box[0] + cw + int(28 * SS), box[3]), fill=INK)
        d.text((box[0] + int(14 * SS), box[3] - int(26 * SS)), ct, font=cf, fill=(200, 196, 188))
    footer(d, W, H, dark=True)
    return img


def t_scoreboard(spec, W, H):
    return t_scoreboard_photo(spec, W, H) if spec.get("photo") else t_scoreboard_core(spec, W, H)


_ballot_plain = t_ballot
_redcard_plain = t_redcard


def t_ballot_any(spec, W, H):
    return t_ballot_photos(spec, W, H) if (spec.get("photo_a") or spec.get("photo_b")) else _ballot_plain(spec, W, H)


def t_redcard_any(spec, W, H):
    return t_redcard_photo(spec, W, H) if spec.get("photo") else _redcard_plain(spec, W, H)


TEMPLATES = {"backpage": t_backpage, "ballot": t_ballot_any, "scoreboard": t_scoreboard, "rumour": t_rumour, "redcard": t_redcard_any, "poster": t_poster}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("template", choices=sorted(TEMPLATES))
    ap.add_argument("--spec", required=True, help="JSON file or inline JSON")
    ap.add_argument("--out", required=True)
    ap.add_argument("--size", default="x", choices=sorted(SIZES))
    a = ap.parse_args()
    spec = json.loads(a.spec) if a.spec.strip().startswith("{") else json.loads(Path(a.spec).read_text())
    W, H = SIZES[a.size]
    img = TEMPLATES[a.template](spec, W, H)
    img = img.resize((W, H), Image.LANCZOS)
    img.save(a.out, quality=92, optimize=True)
    print(a.out, img.size)


if __name__ == "__main__":
    sys.exit(main())
