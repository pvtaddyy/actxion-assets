"""Still Frame: ACTXION's current templates (see ../DESIGN.md).

Portrait 4:5 first (fills a phone screen on X), wide 16:9 supported. The real photo is the
hero; one headline in Instrument Sans, a mono dateline in Geist Mono, the human line in
Instrument Serif, and a single accent colour taken from the photo itself. Template names and
spec fields match the older render.py set, so callers don't change.
"""
import colorsys

from PIL import Image, ImageDraw, ImageFont

import render as R

SS = R.SS
FONT_FILES = {
    "sans": "InstrumentSans-Regular.ttf",
    "sans-bold": "InstrumentSans-Bold.ttf",
    "serif": "InstrumentSerif-Regular.ttf",
    "serif-it": "InstrumentSerif-Italic.ttf",
    "mono": "GeistMono-Regular.ttf",
}
INK = (14, 15, 17)
PAPER = (244, 242, 237)
WHITE = (250, 250, 248)
ON_DARK = (222, 222, 219)
MUTED_DARK = (150, 152, 156)
MUTED_LIGHT = (112, 110, 106)
RULE_LIGHT = (214, 210, 202)
FALLBACK_ACCENT = (214, 74, 52)


def s(v):
    return int(round(v * SS))


def f(name, size):
    return ImageFont.truetype(str(R.FONTS / FONT_FILES[name]), s(size))


def wrap(d, text, fo, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if not cur or d.textlength(trial, font=fo) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit(d, text, name, max_w, max_lines, start, low=20, max_h=None, lead=1.04):
    """Largest size (1x units) whose wrapped lines fit max_lines, max_w and max_h (device px)."""
    size = start
    while size >= low:
        fo = f(name, size)
        lines = wrap(d, text, fo, max_w)
        if (len(lines) <= max_lines and all(d.textlength(l, font=fo) <= max_w for l in lines)
                and (max_h is None or len(lines) * fo.size * lead <= max_h)):
            return fo, lines
        size -= 2
    fo = f(name, low)
    return fo, wrap(d, text, fo, max_w)[:max_lines]


def block(d, xy, lines, fo, fill, lead=1.04):
    x, y = xy
    for ln in lines:
        d.text((x, y), ln, font=fo, fill=fill)
        y += int(fo.size * lead)
    return y


def block_h(lines, fo, lead):
    return int(len(lines) * fo.size * lead)


def tracked(d, xy, text, fo, fill, track=0.08):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=fo, fill=fill)
        x += d.textlength(ch, font=fo) + fo.size * track
    return x


def tracked_len(d, text, fo, track=0.08):
    return sum(d.textlength(ch, font=fo) + fo.size * track for ch in text)


def accent_from(photo):
    """The photo's most characterful colour (a kit, a board), lifted to read as a small mark."""
    if photo is None:
        return FALLBACK_ACCENT
    q = photo.convert("RGB").resize((96, 96)).quantize(colors=10, method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette()
    best, best_score = None, -1.0
    for n, idx in q.getcolors():
        r, g, b = pal[idx * 3: idx * 3 + 3]
        h, l, sat = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
        if l < 0.12 or l > 0.92 or sat < 0.2:
            continue
        if 0.02 < h < 0.11 and sat < 0.6:   # skin
            continue
        if 0.14 < h < 0.47:                  # pitch and floodlit grass
            continue
        score = sat * n ** 0.5
        if score > best_score:
            best, best_score = (h, l, sat), score
    if not best or best[2] < 0.3:
        return FALLBACK_ACCENT
    h, l, sat = best
    r, g, b = colorsys.hls_to_rgb(h, min(max(l, 0.50), 0.62), min(1.0, max(sat, 0.62)))
    return (int(r * 255), int(g * 255), int(b * 255))


def scrim(img, box, alpha=220, ease=1.7, up=False):
    """Tonal fall-off behind type, eased so it reads as light, not as a gradient effect."""
    x0, y0, x1, y1 = box
    h = max(1, y1 - y0)
    col = Image.new("L", (1, h))
    for y in range(h):
        t = y / (h - 1 or 1)
        col.putpixel((0, y), int(alpha * ((1 - t) if up else t) ** ease))
    img.paste(INK, (x0, y0, x1, y1), col.resize((x1 - x0, h)))


def meta(d, xy, parts, color, accent, size=19):
    """Dateline: an accent square, then letterspaced mono caps split by thin slashes."""
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


def wordmark(img, x_right, y, color, height=26):
    m = R.mask("wordmark", s(height))
    R.stamp_mask(img, m, (x_right - m.width, y), color)


def credit(d, x_right, y, text, color):
    if not text:
        return
    fo = f("mono", 13)
    t = R.clean(text).replace("Photo: ", "").upper()
    tracked(d, (x_right - tracked_len(d, t, fo, 0.05), y), t, fo, color, 0.05)


def grid(W, H):
    """Margin and type scale for the canvas: portrait and wide share one system."""
    portrait = H > W
    return portrait, s(56 if portrait else 64)


# ---------- frame: one person, one line (backpage, poster) ----------
def t_frame(spec, W, H):
    portrait, m = grid(W, H)
    CW, CH = s(W), s(H)
    img = Image.new("RGB", (CW, CH), INK)
    d = ImageDraw.Draw(img)
    raw = R.load_photo(spec.get("photo"))
    acc = accent_from(raw)
    if raw:
        img.paste(R.natural(raw, CW, CH, 0.2), (0, 0))
        scrim(img, (0, int(CH * (0.44 if portrait else 0.36)), CW, CH), 232, 1.5)
        scrim(img, (0, 0, CW, s(230)), 165, 1.2, up=True)
    meta(d, (m, m), [spec.get("label") or "Fan verdict", spec.get("date")], ON_DARK, acc)
    wordmark(img, CW - m, m - s(3), WHITE)
    head = R.clean(spec.get("headline", ""), headline=True)
    kick = R.clean(spec.get("kicker", ""))
    max_w = CW - 2 * m if portrait else int(CW * 0.62)
    kf, kl = fit(d, kick, "serif-it", max_w, 3, 36 if portrait else 34, 24) if kick else (None, [])
    hf, hl = fit(d, head, "sans-bold", max_w, 4 if portrait else 3, 104 if portrait else 96, 44,
                 max_h=CH * (0.30 if portrait else 0.36), lead=0.98)
    k_h = block_h(kl, kf, 1.2) + s(40) if kl else 0
    bottom = CH - m - s(30)
    y = block(d, (m, bottom - k_h - block_h(hl, hf, 0.98)), hl, hf, WHITE, 0.98)
    if kl:
        d.rectangle((m, y + s(18), m + s(36), y + s(20)), fill=acc)
        block(d, (m, y + s(36)), kl, kf, (234, 232, 228), 1.2)
    credit(d, CW - m, CH - m + s(4), spec.get("credit"), (160, 160, 158))
    return img


# ---------- quote: the speaker and their words (redcard) ----------
def t_quote(spec, W, H):
    portrait, m = grid(W, H)
    CW, CH = s(W), s(H)
    img = Image.new("RGB", (CW, CH), PAPER)
    d = ImageDraw.Draw(img)
    raw = R.load_photo(spec.get("photo"))
    acc = accent_from(raw)
    if raw and portrait:
        ph = int(CH * 0.50)
        img.paste(R.natural(raw, CW, ph, 0.1), (0, 0))
        scrim(img, (0, 0, CW, s(230)), 160, 1.2, up=True)
        meta(d, (m, m), [spec.get("label") or "Quote of the day", spec.get("date")], ON_DARK, acc)
        wordmark(img, CW - m, m - s(3), WHITE)
        credit(d, CW - m, ph - s(26), spec.get("credit"), (232, 232, 230))
        x0, x1, top = m, CW - m, ph + s(44)
    elif raw:
        pw = int(CW * 0.46)
        img.paste(R.natural(raw, pw, CH, 0.22), (0, 0))
        credit(d, pw - s(16), CH - s(26), spec.get("credit"), (232, 232, 230))
        x0, x1, top = pw + s(72), CW - m, m
        meta(d, (x0, top), [spec.get("label") or "Quote of the day", spec.get("date")], MUTED_LIGHT, acc)
        wordmark(img, CW - m, top - s(3), INK, 18)
        top += s(54)
    else:
        x0, x1, top = m, int(CW * (0.9 if portrait else 0.8)), m
        meta(d, (x0, top), [spec.get("label") or "Quote of the day", spec.get("date")], MUTED_LIGHT, acc)
        wordmark(img, CW - m, top - s(3), INK, 18)
        top += s(90)
    q = R.clean(spec.get("quote", ""), headline=True)
    qm = f("serif", 132)
    d.text((x0 - s(4), top - s(30)), "“", font=qm, fill=acc)
    qtop = top + s(74)
    foot = s(82)
    qf, ql = fit(d, q, "serif", x1 - x0, 6, 124 if portrait else 104, 34, max_h=CH - qtop - foot - m - s(20), lead=1.04)
    block(d, (x0, qtop), ql, qf, INK, 1.04)
    fy = CH - m - s(52)
    d.text((x0, fy - s(10)), R.clean(spec.get("speaker", ""), True), font=f("sans-bold", 32), fill=INK)
    ctx = R.clean(spec.get("context", ""))
    if ctx:
        cf, cl = fit(d, ctx.upper(), "mono", x1 - x0, 1, 17, 11)
        tracked(d, (x0, fy + s(38)), cl[0], cf, MUTED_LIGHT, 0.06)
    return img


# ---------- verdict: A or B (ballot) ----------
def t_verdict(spec, W, H):
    portrait, m = grid(W, H)
    CW, CH = s(W), s(H)
    img = Image.new("RGB", (CW, CH), INK)
    d = ImageDraw.Draw(img)
    pa, pb = R.load_photo(spec.get("photo_a")), R.load_photo(spec.get("photo_b"))
    q = R.clean(spec.get("question", ""), headline=True)
    names = (R.clean(spec.get("option_a", ""), True), R.clean(spec.get("option_b", ""), True))
    if pa or pb:
        acc = accent_from(pa or pb)
        gap = s(4)
        half = CW // 2
        for i, ph in enumerate((pa, pb)):
            x, w = (0, half - gap // 2) if i == 0 else (half + gap // 2, CW - half - gap // 2)
            if ph:
                img.paste(R.natural(ph, w, CH, 0.22), (x, 0))
            else:
                d.rectangle((x, 0, x + w, CH), fill=(32, 33, 36))
        scrim(img, (0, 0, CW, int(CH * 0.40)), 215, 1.25, up=True)
        scrim(img, (0, int(CH * 0.66), CW, CH), 225, 1.5)
        meta(d, (m, m), [spec.get("label") or "Fan verdict", spec.get("date")], ON_DARK, acc)
        wordmark(img, CW - m, m - s(3), WHITE)
        qf, ql = fit(d, q, "sans-bold", CW - 2 * m, 3 if portrait else 2, 76 if portrait else 64, 34, lead=1.0)
        block(d, (m, m + s(48)), ql, qf, WHITE, 1.0)
        for i, name in enumerate(names):
            x = m if i == 0 else half + gap // 2 + s(36)
            nf, nl = fit(d, name, "sans-bold", half - m - s(36) - s(20), 2, 52 if portrait else 44, 24, lead=1.0)
            y = CH - m - s(40) - block_h(nl, nf, 1.0)
            tracked(d, (x, y - s(36)), "A" if i == 0 else "B", f("mono", 19), acc, 0.1)
            block(d, (x, y), nl, nf, WHITE, 1.0)
            credit(d, (half - gap // 2 if i == 0 else CW) - s(16), CH - s(24),
                   spec.get("credit_a" if i == 0 else "credit_b"), (150, 150, 148))
        r = s(30)
        cx, cy = half, int(CH * (0.52 if portrait else 0.56))
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=INK)
        of = f("serif-it", 30)
        d.text((cx - d.textlength("or", font=of) / 2, cy - of.size * 0.6), "or", font=of, fill=WHITE)
        return img
    img = Image.new("RGB", (CW, CH), PAPER)
    d = ImageDraw.Draw(img)
    meta(d, (m, m), [spec.get("label") or "Fan verdict", spec.get("date")], MUTED_LIGHT, FALLBACK_ACCENT)
    wordmark(img, CW - m, m - s(3), INK, 18)
    qf, ql = fit(d, q, "sans-bold", CW - 2 * m if portrait else int(CW * 0.78), 4, 96, 40, lead=1.0)
    y = block(d, (m, m + s(84)), ql, qf, INK, 1.0)
    ctx = R.clean(spec.get("context", ""))
    if ctx:
        cf, cl = fit(d, ctx, "serif-it", CW - 2 * m if portrait else int(CW * 0.7), 3, 34, 22)
        block(d, (m, y + s(24)), cl, cf, (70, 68, 64), 1.18)
    rows = [(m, CH - m - s(150)), (m, CH - m - s(60))] if portrait else [(m, CH - m - s(50)), (m + int(CW * 0.42), CH - m - s(50))]
    for (x, y), name in zip(rows, names):
        r = s(15)
        d.ellipse((x, y + s(9), x + 2 * r, y + s(9) + 2 * r), outline=INK, width=s(2))
        nf, nl = fit(d, name, "sans-bold", int(CW * (0.8 if portrait else 0.36)), 1, 40, 22)
        d.text((x + 2 * r + s(18), y), nl[0], font=nf, fill=INK)
    return img


# ---------- result: the score (scoreboard) ----------
def t_result(spec, W, H):
    portrait, m = grid(W, H)
    CW, CH = s(W), s(H)
    img = Image.new("RGB", (CW, CH), INK)
    d = ImageDraw.Draw(img)
    raw = R.load_photo(spec.get("photo"))
    acc = accent_from(raw)
    if raw and portrait:
        py0 = int(CH * 0.54)
        img.paste(R.natural(raw, CW, CH - py0, 0.08), (0, py0))
        area = (m, m, CW - m, py0 - m)
        lab = R.clean(spec.get("photo_label", ""), True).upper()
        if lab:
            scrim(img, (0, CH - s(170), CW, CH), 200, 1.5)
            tracked(d, (m, CH - m - s(6)), lab, f("mono", 19), WHITE)
        credit(d, CW - m, CH - m + s(1), spec.get("credit"), (200, 200, 198))
    elif raw:
        pw = int(CW * 0.40)
        img.paste(R.natural(raw, pw, CH, 0.22), (CW - pw, 0))
        area = (m, m, CW - pw - m, CH - m)
        lab = R.clean(spec.get("photo_label", ""), True).upper()
        if lab:
            scrim(img, (CW - pw, int(CH * 0.74), CW, CH), 200, 1.5)
            tracked(d, (CW - pw + s(36), CH - m - s(6)), lab, f("mono", 19), WHITE)
        credit(d, CW - s(16), s(16), spec.get("credit"), (232, 232, 230))
    else:
        area = (m, m, CW - m, CH - m)
    x0, y0, x1, y1 = area
    meta(d, (x0, y0), [spec.get("status") or "Full time", spec.get("label")], MUTED_DARK, acc)
    wordmark(img, x1, y0 - s(3), WHITE, 18)
    teams = [(R.clean(spec.get("home", ""), True), str(spec.get("home_score", ""))),
             (R.clean(spec.get("away", ""), True), str(spec.get("away_score", "")))]
    sf = f("sans-bold", 150 if portrait else 160)
    row = s(150 if portrait else 160)
    y = y0 + s(70)
    for i, (name, sc) in enumerate(teams):
        tf, tl = fit(d, name, "sans-bold", int((x1 - x0) * 0.68), 1, 72, 30)
        d.text((x0, y + (row - tf.size) // 2 - s(8)), tl[0], font=tf, fill=WHITE)
        d.text((x1 - d.textlength(sc, font=sf), y - s(26)), sc, font=sf,
               fill=WHITE if sc.strip() not in ("?", "") else (88, 90, 94))
        y += row
        if i == 0:
            d.line((x0, y - s(6), x1, y - s(6)), fill=(44, 46, 50), width=s(2))
    scorers = R.clean(spec.get("scorers", ""))
    if scorers:
        sf2, sl = fit(d, scorers.upper(), "mono", x1 - x0, 2, 19, 12)
        for ln in sl:
            tracked(d, (x0, y + s(6)), ln, sf2, MUTED_DARK, 0.05)
            y += int(sf2.size * 1.6)
    qv = R.clean(spec.get("question", ""), headline=True)
    if qv:
        qf, ql = fit(d, qv, "serif-it", x1 - x0, 2, 56, 28, lead=1.1)
        qy = y1 - block_h(ql, qf, 1.1)
        qy = max(qy, y + s(40))
        d.rectangle((x0, qy - s(24), x0 + s(36), qy - s(22)), fill=acc)
        block(d, (x0, qy), ql, qf, WHITE, 1.1)
    return img


# ---------- file: a transfer rumour (rumour) ----------
def t_file(spec, W, H):
    portrait, m = grid(W, H)
    CW, CH = s(W), s(H)
    img = Image.new("RGB", (CW, CH), PAPER)
    d = ImageDraw.Draw(img)
    raw = R.load_photo(spec.get("photo"))
    acc = accent_from(raw)
    if raw and portrait:
        ph = int(CH * 0.46)
        img.paste(R.natural(raw, CW, ph, 0.06), (0, 0))
        scrim(img, (0, 0, CW, s(230)), 160, 1.2, up=True)
        meta(d, (m, m), ["Rumour desk", spec.get("date")], ON_DARK, acc)
        wordmark(img, CW - m, m - s(3), WHITE)
        credit(d, CW - m, ph - s(26), spec.get("credit"), (232, 232, 230))
        x0, x1, top = m, CW - m, ph + s(40)
    elif raw:
        pw = int(CW * 0.42)
        img.paste(R.natural(raw, pw, CH, 0.22), (CW - pw, 0))
        credit(d, CW - s(16), CH - s(26), spec.get("credit"), (232, 232, 230))
        x0, x1, top = m, CW - pw - s(72), m
        meta(d, (x0, top), ["Rumour desk", spec.get("date")], MUTED_LIGHT, acc)
        top += s(60)
    else:
        x0, x1, top = m, CW - m, m
        meta(d, (x0, top), ["Rumour desk", spec.get("date")], MUTED_LIGHT, acc)
        wordmark(img, CW - m, top - s(3), INK, 18)
        top += s(70)
    pf, pl = fit(d, R.clean(spec.get("player", ""), True), "sans-bold", x1 - x0, 2, 96 if portrait else 88, 36, lead=1.0)
    y = block(d, (x0, top), pl, pf, INK, 1.0) + s(26)
    lf = f("mono", 16)
    for label, val in (("From", spec.get("from_club")), ("To", spec.get("to_club")),
                       ("Fee", spec.get("fee") or "Not reported"), ("Source", spec.get("source"))):
        if not val:
            continue
        d.line((x0, y, x1, y), fill=RULE_LIGHT, width=s(2))
        tracked(d, (x0, y + s(30)), label.upper(), lf, MUTED_LIGHT, 0.1)
        vf, vl = fit(d, R.clean(str(val), True), "sans", int((x1 - x0) * 0.70), 1, 40, 20)
        d.text((x0 + int((x1 - x0) * 0.28), y + s(18)), vl[0], font=vf, fill=INK)
        y += s(84)
    d.line((x0, y, x1, y), fill=RULE_LIGHT, width=s(2))
    tier = max(1, min(3, int(spec.get("tier") or 2)))
    words = {1: "Reliable source", 2: "Worth watching", 3: "Pinch of salt"}
    ty = CH - m - s(22)
    for i in range(3):
        x = x0 + i * s(32)
        d.rectangle((x, ty, x + s(20), ty + s(20)), fill=acc if i < 4 - tier else None, outline=acc, width=s(2))
    tracked(d, (x0 + s(118), ty - s(1)), f"TIER {tier}  /  {words[tier].upper()}", f("mono", 19), INK, 0.08)
    if raw and not portrait:
        wordmark(img, x1, ty - s(4), INK, 16)
    return img


TEMPLATES = {"backpage": t_frame, "poster": t_frame, "redcard": t_quote, "ballot": t_verdict,
             "scoreboard": t_result, "rumour": t_file}
