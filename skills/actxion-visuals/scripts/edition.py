"""Still Frame: ACTXION's current templates (see ../DESIGN.md).

Every card is the full photo, edge to edge, with a soft vignette tinted from the photo's own
colours behind the type: no solid panels. Headlines run in caps (Instrument Sans Bold) and a
word wrapped in *asterisks* is picked out in the accent colour, which is also taken from the
photo. Datelines in Geist Mono, the human line in Instrument Serif. Club badges come from the
club's Wikipedia page. Portrait 4:5 first; wide 16:9 works too. Template names and spec fields
match the older render.py set, so callers don't change.
"""
import colorsys
import io
import json
import os
import re
import urllib.parse
import urllib.request

from PIL import Image, ImageDraw, ImageFilter, ImageFont

import render as R

SS = R.SS
FONT_FILES = {
    "sans": "InstrumentSans-Regular.ttf",
    "sans-bold": "InstrumentSans-Bold.ttf",
    "serif": "InstrumentSerif-Regular.ttf",
    "serif-it": "InstrumentSerif-Italic.ttf",
    "mono": "GeistMono-Regular.ttf",
}
WHITE = (250, 250, 248)
SOFT = (226, 226, 222)
DIM = (176, 176, 172)
FALLBACK_ACCENT = (240, 90, 60)
UA = "ACTXION-visuals/1.0 (https://github.com/pvtaddyy/actxion-assets)"
# the repo's photos/ when run from the repo (as the routines do), else beside the skill
CRESTS = (os.path.join(os.getcwd(), "photos", "crests") if os.path.isdir(os.path.join(os.getcwd(), "photos"))
          else os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "photos", "crests")))


def s(v):
    return int(round(v * SS))


def f(name, size):
    return ImageFont.truetype(str(R.FONTS / FONT_FILES[name]), s(size))


# ---------- text ----------
def tokens(text, caps=False):
    """Words with a highlight flag: *word* or *two words* marks the highlight."""
    out, hi = [], False
    for w in text.split():
        start, end = w.startswith("*"), w.rstrip("?!,.:;").endswith("*")
        word = w.replace("*", "")
        if start:
            hi = True
        out.append(((word.upper() if caps else word), hi))
        if end:
            hi = False
    return out


def wrap_tokens(d, toks, fo, max_w):
    lines, cur = [], []
    space = d.textlength(" ", font=fo)
    for t in toks:
        trial = cur + [t]
        width = sum(d.textlength(w, font=fo) for w, _ in trial) + space * (len(trial) - 1)
        if cur and width > max_w:
            lines.append(cur)
            cur = [t]
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def fit_rich(d, text, name, max_w, max_lines, start, low=28, max_h=None, lead=0.96, caps=True):
    toks = tokens(text, caps)
    size = start
    while size >= low:
        fo = f(name, size)
        lines = wrap_tokens(d, toks, fo, max_w)
        if len(lines) <= max_lines and (max_h is None or len(lines) * fo.size * lead <= max_h):
            return fo, lines
        size -= 2
    fo = f(name, low)
    return fo, wrap_tokens(d, toks, fo, max_w)[:max_lines]


def fit_plain(d, text, name, max_w, max_lines, start, low=18, lead=1.1, max_h=None):
    return fit_rich(d, text, name, max_w, max_lines, start, low, max_h, lead, caps=False)


def line_text(ln):
    return " ".join(w for w, _ in ln)


SHADOW = (0, 0, 0)
MARKER_INK = (14, 14, 16)


def draw_rich(d, xy, lines, fo, fill, accent, lead=0.96, shadow=True):
    """Rich lines on a photo; a faint offset shadow keeps them legible on any background."""
    x0, y = xy
    space = d.textlength(" ", font=fo)
    off = max(2, fo.size // 40)
    for ln in lines:
        x = x0
        i = 0
        while i < len(ln):
            w, hi = ln[i]
            if hi:
                # a highlighted run sits on a marker block in the accent, set in dark type
                run = [w]
                while i + 1 < len(ln) and ln[i + 1][1]:
                    i += 1
                    run.append(ln[i][0])
                text = " ".join(run)
                bx0, by0, bx1, by1 = d.textbbox((x, y), text, font=fo)
                pad = max(4, fo.size // 12)
                d.rectangle((bx0 - pad, by0 - pad, bx1 + pad, by1 + pad), fill=accent)
                d.text((x, y), text, font=fo, fill=MARKER_INK)
                x += d.textlength(text, font=fo) + space + pad
            else:
                if shadow:
                    d.text((x + off, y + off), w, font=fo, fill=SHADOW)
                d.text((x, y), w, font=fo, fill=fill)
                x += d.textlength(w, font=fo) + space
            i += 1
        y += int(fo.size * lead)
    return y


def rich_h(lines, fo, lead=0.96):
    return int(len(lines) * fo.size * lead)


def tracked(d, xy, text, fo, fill, track=0.08):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=fo, fill=fill)
        x += d.textlength(ch, font=fo) + fo.size * track
    return x


def tracked_len(d, text, fo, track=0.08):
    return sum(d.textlength(ch, font=fo) + fo.size * track for ch in text)


# ---------- colour from the photo ----------
def palette(photo):
    """(accent, shade): the photo's most characterful colour lifted to read on dark, and a deep
    tone of the same hue for the vignette, so every card takes its colours from its own picture."""
    acc = FALLBACK_ACCENT
    if photo is not None:
        q = photo.convert("RGB").resize((96, 96)).quantize(colors=12, method=Image.Quantize.MEDIANCUT)
        pal = q.getpalette()
        best, best_score = None, -1.0
        for n, idx in q.getcolors():
            r, g, b = pal[idx * 3: idx * 3 + 3]
            h, l, sat = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
            if l < 0.12 or l > 0.92 or sat < 0.22:
                continue
            if 0.02 < h < 0.11 and sat < 0.6:   # skin
                continue
            if 0.14 < h < 0.47:                  # pitch and floodlit grass
                continue
            score = sat * n ** 0.5
            if score > best_score:
                best, best_score = (h, l, sat), score
        if best:
            h, l, sat = best
            r, g, b = colorsys.hls_to_rgb(h, 0.6, min(1.0, max(sat, 0.7)))
            acc = (int(r * 255), int(g * 255), int(b * 255))
    h, l, sat = colorsys.rgb_to_hls(*(c / 255 for c in acc))
    r, g, b = colorsys.hls_to_rgb(h, 0.07, min(0.55, sat))
    return acc, (int(r * 255), int(g * 255), int(b * 255))


def scrim(img, box, color, alpha=230, ease=1.6, up=False):
    """Light falling off behind type, in the photo's own deep tone."""
    x0, y0, x1, y1 = box
    h = max(1, y1 - y0)
    col = Image.new("L", (1, h))
    for y in range(h):
        t = y / (h - 1 or 1)
        col.putpixel((0, y), int(alpha * ((1 - t) if up else t) ** ease))
    img.paste(color, (x0, y0, x1, y1), col.resize((x1 - x0, h)))


def vignette(img, color, strength=120):
    """Soft darkening at the edges, like a lens, so the eye goes to the face."""
    w, h = img.size
    m = Image.new("L", (64, 80), 0)
    ImageDraw.Draw(m).ellipse((-14, -10, 78, 92), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(10)).resize((w, h))
    img.paste(color, (0, 0, w, h), Image.eval(m, lambda v: int((255 - v) * strength / 255)))


def base(spec, W, H, key="photo", focus=0.18):
    """The full-bleed photo with its vignette. Returns (img, draw, accent, shade)."""
    CW, CH = s(W), s(H)
    raw = R.load_photo(spec.get(key))
    acc, shade = palette(raw)
    img = Image.new("RGB", (CW, CH), shade)
    if raw:
        img.paste(R.natural(raw, CW, CH, focus), (0, 0))
        vignette(img, shade)
    return img, ImageDraw.Draw(img), acc, shade


# ---------- furniture ----------
def meta(d, xy, parts, color, accent, size=19):
    x, y = xy
    fo = f("mono", size)
    sq = s(10)
    off = (fo.size - sq) // 2 + s(1)
    d.rectangle((x, y + off, x + sq, y + off + sq), fill=accent)
    x += sq + s(12)
    for i, p in enumerate(R.clean(p, True).upper() for p in parts if p):
        if i:
            x = tracked(d, (x, y), "  /  ", fo, color, 0.0)
        x = tracked(d, (x, y), p, fo, color)


def wordmark(img, x_right, y, color=WHITE, height=26):
    m = R.mask("wordmark", s(height))
    R.stamp_mask(img, m, (x_right - m.width, y), color)


def credit(d, x_right, y, text, color=DIM):
    if not text:
        return
    fo = f("mono", 13)
    t = R.clean(text).replace("Photo: ", "").upper()
    tracked(d, (x_right - tracked_len(d, t, fo, 0.05), y), t, fo, color, 0.05)


def top_bar(img, d, parts, acc, shade, m):
    scrim(img, (0, 0, img.width, s(240)), shade, 175, 1.2, up=True)
    meta(d, (m, m), parts, SOFT, acc)
    wordmark(img, img.width - m, m - s(3))


def margin(W, H):
    return s(56 if H > W else 64)


# ---------- club badges ----------
def crest(team):
    """The club's badge from its Wikipedia page, cached in photos/crests. None if not found."""
    if not team:
        return None
    key = re.sub(r"[^a-z0-9]+", "-", team.lower()).strip("-")
    path = os.path.join(CRESTS, key + ".png")
    if os.path.exists(path):
        return Image.open(path).convert("RGBA")
    try:
        q = urllib.parse.quote(f"{team} football club")
        url = ("https://en.wikipedia.org/w/api.php?action=query&format=json&generator=search"
               f"&gsrsearch={q}&gsrlimit=4&prop=pageimages&piprop=thumbnail&pithumbsize=400&pilicense=any")
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=8) as r:
            pages = sorted(json.load(r).get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 9))
        for p in pages:
            if re.search(r"women|femen|ladies|u-?\d\d|under-\d\d|reserve|academy|youth|season|stadium", p["title"], re.I):
                continue
            src = p.get("thumbnail", {}).get("source")
            if not src:
                continue
            with urllib.request.urlopen(urllib.request.Request(src, headers={"User-Agent": UA}), timeout=8) as r:
                im = Image.open(io.BytesIO(r.read())).convert("RGBA")
            os.makedirs(CRESTS, exist_ok=True)
            im.save(path)
            return im
    except Exception:
        return None
    return None


def paste_crest(img, im, x, y, size):
    if im is None:
        return 0
    c = im.copy()
    c.thumbnail((size, size), Image.LANCZOS)
    img.paste(c, (int(x + (size - c.width) // 2), int(y + (size - c.height) // 2)), c)
    return size


# ---------- frame: one person, one line (backpage, poster) ----------
def t_frame(spec, W, H):
    portrait = H > W
    m = margin(W, H)
    img, d, acc, shade = base(spec, W, H, focus=0.18)
    CW, CH = img.size
    scrim(img, (0, int(CH * (0.40 if portrait else 0.30)), CW, CH), shade, 248, 1.2)
    top_bar(img, d, [spec.get("label") or "Fan verdict", spec.get("date")], acc, shade, m)
    head = R.clean(spec.get("headline", ""), headline=True)
    kick = R.clean(spec.get("kicker", ""))
    max_w = CW - 2 * m if portrait else int(CW * 0.66)
    kf, kl = fit_plain(d, kick, "serif-it", max_w, 3, 40 if portrait else 36, 24) if kick else (None, [])
    hf, hl = fit_rich(d, head, "sans-bold", max_w, 4, 112 if portrait else 100, 48, max_h=CH * (0.32 if portrait else 0.40))
    k_h = rich_h(kl, kf, 1.16) + s(34) if kl else 0
    y = CH - m - s(34) - k_h - rich_h(hl, hf)
    y = draw_rich(d, (m, y), hl, hf, WHITE, acc)
    if kl:
        draw_rich(d, (m, y + s(30)), kl, kf, SOFT, acc, 1.16)
    credit(d, CW - m, CH - m + s(4), spec.get("credit"))
    return img


# ---------- quote: the speaker and their words (redcard) ----------
def t_quote(spec, W, H):
    portrait = H > W
    m = margin(W, H)
    img, d, acc, shade = base(spec, W, H, focus=0.14)
    CW, CH = img.size
    scrim(img, (0, int(CH * (0.40 if portrait else 0.22)), CW, CH), shade, 250, 0.85)
    top_bar(img, d, [spec.get("label") or "Quote of the day", spec.get("date")], acc, shade, m)
    q = R.clean(spec.get("quote", ""), headline=True)
    max_w = CW - 2 * m if portrait else int(CW * 0.70)
    qf, ql = fit_plain(d, q, "serif", max_w, 5, 108 if portrait else 92, 34, lead=1.02, max_h=CH * (0.32 if portrait else 0.42))
    qtop = CH - m - s(118) - rich_h(ql, qf, 1.02)
    d.text((m - s(4), qtop - s(124)), "“", font=f("serif", 156), fill=acc)
    draw_rich(d, (m, qtop), ql, qf, WHITE, acc, 1.02)
    fy = CH - m - s(70)
    d.rectangle((m, fy - s(22), m + s(36), fy - s(20)), fill=acc)
    tracked(d, (m, fy), R.clean(spec.get("speaker", ""), True).upper(), f("sans-bold", 26), WHITE, 0.04)
    ctx = R.clean(spec.get("context", ""))
    if ctx:
        cf, cl = fit_plain(d, ctx.upper(), "mono", max_w, 1, 16, 11)
        tracked(d, (m, fy + s(42)), line_text(cl[0]), cf, DIM, 0.06)
    credit(d, CW - m, CH - m + s(4), spec.get("credit"))
    return img


# ---------- verdict: A or B (ballot) ----------
def t_verdict(spec, W, H):
    portrait = H > W
    m = margin(W, H)
    CW, CH = s(W), s(H)
    pa, pb = R.load_photo(spec.get("photo_a")), R.load_photo(spec.get("photo_b"))
    acc, shade = palette(pa or pb)
    img = Image.new("RGB", (CW, CH), shade)
    d = ImageDraw.Draw(img)
    q = R.clean(spec.get("question", ""), headline=True)
    names = (R.clean(spec.get("option_a", ""), True), R.clean(spec.get("option_b", ""), True))
    half, gap = CW // 2, s(4)
    if pa or pb:
        for i, ph in enumerate((pa, pb)):
            x, w = (0, half - gap // 2) if i == 0 else (half + gap // 2, CW - half - gap // 2)
            if ph:
                img.paste(R.natural(ph, w, CH, 0.18), (x, 0))
        vignette(img, shade, 110)
    scrim(img, (0, 0, CW, int(CH * 0.44)), shade, 235, 1.2, up=True)
    scrim(img, (0, int(CH * 0.64), CW, CH), shade, 240, 1.4)
    meta(d, (m, m), [spec.get("label") or "Fan verdict", spec.get("date")], SOFT, acc)
    wordmark(img, CW - m, m - s(3))
    qf, ql = fit_rich(d, q, "sans-bold", CW - 2 * m, 3, 84 if portrait else 70, 36)
    draw_rich(d, (m, m + s(52)), ql, qf, WHITE, acc)
    for i, name in enumerate(names):
        x = m if i == 0 else half + gap // 2 + s(36)
        nf, nl = fit_rich(d, name, "sans-bold", half - m - s(56), 2, 54 if portrait else 46, 24)
        y = CH - m - s(40) - rich_h(nl, nf)
        tracked(d, (x, y - s(38)), "A" if i == 0 else "B", f("mono", 19), acc, 0.1)
        draw_rich(d, (x, y), nl, nf, WHITE, acc)
        credit(d, (half - gap // 2 if i == 0 else CW) - s(16), CH - s(26), spec.get("credit_a" if i == 0 else "credit_b"))
    if pa or pb:
        r = s(32)
        cx, cy = half, int(CH * (0.53 if portrait else 0.56))
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=shade)
        of = f("serif-it", 32)
        d.text((cx - d.textlength("or", font=of) / 2, cy - of.size * 0.6), "or", font=of, fill=WHITE)
    return img


# ---------- result: the score (scoreboard) ----------
def t_result(spec, W, H):
    portrait = H > W
    m = margin(W, H)
    img, d, acc, shade = base(spec, W, H, focus=0.10 if portrait else 0.16)
    CW, CH = img.size
    if portrait:
        scrim(img, (0, 0, CW, int(CH * 0.60)), shade, 240, 1.05, up=True)
        x1 = CW - m
    else:
        pw = int(CW * 0.58)
        side = Image.new("L", (pw, 1))
        for x in range(pw):
            side.putpixel((x, 0), int(235 * (1 - x / pw) ** 1.1))
        img.paste(shade, (0, 0, pw, CH), side.resize((pw, CH)))
        scrim(img, (0, 0, CW, s(240)), shade, 175, 1.2, up=True)
        x1 = int(CW * 0.52)
    meta(d, (m, m), [spec.get("status") or "Full time", spec.get("label")], SOFT, acc)
    wordmark(img, CW - m, m - s(3))
    teams = [(R.clean(spec.get("home", ""), True), str(spec.get("home_score", ""))),
             (R.clean(spec.get("away", ""), True), str(spec.get("away_score", "")))]
    sf = f("sans-bold", 156 if portrait else 140)
    row = s(168 if portrait else 150)
    cs = s(92)
    y = m + s(70)
    for i, (name, sc) in enumerate(teams):
        cw = paste_crest(img, crest(spec.get("home_crest_name" if i == 0 else "away_crest_name") or name), m, y + (row - cs) // 2 - s(6), cs)
        tx = m + (cw + s(28) if cw else 0)
        tf, tl = fit_rich(d, name, "sans-bold", int((x1 - tx) * 0.66), 1, 64, 30)
        d.text((tx, y + (row - tf.size) // 2 - s(8)), line_text(tl[0]), font=tf, fill=WHITE)
        unknown = sc.strip() in ("?", "")
        d.text((x1 - d.textlength(sc, font=sf), y - s(24)), sc, font=sf, fill=(140, 140, 138) if unknown else WHITE)
        y += row
        if i == 0:
            d.line((m, y - s(6), x1, y - s(6)), fill=(110, 110, 108), width=s(1))
    scorers = R.clean(spec.get("scorers", ""))
    if scorers:
        sf2, sl = fit_plain(d, scorers.upper(), "mono", x1 - m, 2, 19, 12)
        for ln in sl:
            tracked(d, (m, y + s(8)), line_text(ln), sf2, SOFT, 0.05)
            y += int(sf2.size * 1.6)
    scrim(img, (0, int(CH * (0.70 if portrait else 0.55)), CW, CH), shade, 235, 1.4)
    bottom = CH - m - s(30)
    lab = R.clean(spec.get("photo_label", ""), True).upper()
    if lab:
        tracked(d, (m, bottom - s(4)), lab, f("mono", 18), DIM, 0.08)
        bottom -= s(52)
    qv = R.clean(spec.get("question", ""), headline=True)
    if qv:
        qf, ql = fit_rich(d, qv, "sans-bold", CW - 2 * m if portrait else int(CW * 0.56), 3, 64 if portrait else 54, 30)
        draw_rich(d, (m, bottom - rich_h(ql, qf)), ql, qf, WHITE, acc)
    credit(d, CW - m, CH - m + s(4), spec.get("credit"))
    return img


# ---------- file: a transfer rumour (rumour) ----------
def t_file(spec, W, H):
    portrait = H > W
    m = margin(W, H)
    img, d, acc, shade = base(spec, W, H, focus=0.10)
    CW, CH = img.size
    scrim(img, (0, int(CH * (0.38 if portrait else 0.18)), CW, CH), shade, 250, 0.9)
    top_bar(img, d, ["Rumour desk", spec.get("date")], acc, shade, m)
    max_w = CW - 2 * m if portrait else int(CW * 0.62)
    tier = max(1, min(3, int(spec.get("tier") or 2)))
    words = {1: "Reliable source", 2: "Worth watching", 3: "Pinch of salt"}
    y = CH - m - s(26)
    for i in range(3):
        x = m + i * s(32)
        d.rectangle((x, y, x + s(20), y + s(20)), fill=acc if i < 4 - tier else None, outline=acc, width=s(2))
    tracked(d, (m + s(118), y - s(1)), f"TIER {tier}  /  {words[tier].upper()}", f("mono", 19), WHITE, 0.08)
    lf = f("mono", 16)
    y -= s(22)
    for label, val in (("Source", spec.get("source")), ("Fee", spec.get("fee") or "Not reported")):
        if not val:
            continue
        y -= s(76)
        d.line((m, y, m + max_w, y), fill=(120, 120, 118), width=s(1))
        tracked(d, (m, y + s(24)), label.upper(), lf, DIM, 0.1)
        vf, vl = fit_plain(d, R.clean(str(val), True), "sans", int(max_w * 0.70), 1, 34, 18)
        d.text((m + int(max_w * 0.28), y + s(15)), line_text(vl[0]), font=vf, fill=WHITE)
    # the move: badge FROM -> badge TO
    cs = s(64)
    y -= s(40) + cs
    frm, to = R.clean(spec.get("from_club", ""), True), R.clean(spec.get("to_club", ""), True)
    mf = f("sans-bold", 40)
    ty = y + (cs - mf.size) // 2 - s(4)
    x = m
    w = paste_crest(img, crest(frm), x, y, cs)
    x += w + (s(16) if w else 0)
    d.text((x, ty), frm.upper(), font=mf, fill=SOFT)
    x += d.textlength(frm.upper(), font=mf) + s(22)
    d.text((x, ty), "→", font=mf, fill=acc)
    x += d.textlength("→", font=mf) + s(22)
    w = paste_crest(img, crest(to), x, y, cs)
    x += w + (s(16) if w else 0)
    d.text((x, ty), to.upper(), font=mf, fill=WHITE)
    pf, pl = fit_rich(d, R.clean(spec.get("player", ""), True), "sans-bold", max_w, 2, 112 if portrait else 96, 44)
    draw_rich(d, (m, y - s(30) - rich_h(pl, pf)), pl, pf, WHITE, acc)
    credit(d, CW - m, CH - m + s(4), spec.get("credit"))
    return img


TEMPLATES = {"backpage": t_frame, "poster": t_frame, "redcard": t_quote, "ballot": t_verdict,
             "scoreboard": t_result, "rumour": t_file}
