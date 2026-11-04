#!/usr/bin/env python3
"""Full-screen Instagram Story frames (1080x1920) in the Still Frame design language.

Usage: python3 story_frame.py <template> --spec '<json or path>' --out frame.png
Templates:
  verdict     one person full-bleed: headline, kicker, then the two sides as A / B and the ask
              spec: headline, kicker?, option_a, option_b, photo, credit?, label?, date?, ask?
  thisorthat  two people stacked, one per half, the question on the seam
              spec: question, option_a, option_b, photo_a, photo_b, credit_a?, credit_b?, label?, ask?
  quote       the speaker full-bleed, their words in serif, then the ask
              spec: quote, speaker, context?, photo, credit?, label?, ask?
  result      full time: one person full-bleed, the score line, a question
              spec: home, away, home_score, away_score, question, photo, credit?, label?, ask?
Everything readable sits between y=270 and y=1580: Instagram's progress bar and profile row
cover the top, the reply box covers the bottom. Stories made through the API can't carry
stickers, so the ask is a reply ("Reply A or B"), which lands in DMs.
"""
import argparse
import json
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
VIS = os.path.join(HERE, "..", "..", "actxion-visuals", "scripts")
sys.path.insert(0, os.path.abspath(VIS))
import edition as E  # noqa: E402
import render as R  # noqa: E402

W, H = 1080, 1920
TOP, BOTTOM = 270, 1580  # safe zone, in final pixels
M = 64


def s(v):
    return E.s(v)


def header(img, d, spec, acc, shade, default):
    E.scrim(img, (0, 0, img.width, s(TOP + 150)), shade, 200, 1.1, up=True)
    E.meta(d, (s(M), s(TOP)), [spec.get("label") or default, spec.get("date")], E.SOFT, acc, size=20)
    E.wordmark(img, img.width - s(M), s(TOP) - s(3), height=28)


def ask_pill(d, y_bottom, text, acc):
    """A solid pill in the accent with dark type, its bottom edge on y_bottom. Returns its top."""
    fo = E.f("sans-bold", 34)
    t = R.clean(text, True).upper()
    tw = E.tracked_len(d, t, fo, 0.06)
    ph, pw = s(84), tw + s(72)
    x0, y0 = s(M), y_bottom - ph
    d.rounded_rectangle((x0, y0, x0 + pw, y_bottom), radius=ph // 2, fill=acc)
    E.tracked(d, (x0 + s(36), y0 + (ph - fo.size) // 2 - s(3)), t, fo, E.MARKER_INK, 0.06)
    return y0


def options(d, y_bottom, a, b, acc):
    """Two ruled rows, A and B, stacked upwards from y_bottom. Returns the top of the block."""
    fo, lf = E.f("sans-bold", 46), E.f("mono", 22)
    row = s(96)
    y = y_bottom - 2 * row
    for letter, text in (("A", a), ("B", b)):
        d.rectangle((s(M), y, W * E.SS - s(M), y + s(2)), fill=(255, 255, 255, 60) if False else E.DIM)
        d.text((s(M), y + s(34)), letter, font=lf, fill=acc)
        t = R.clean(text, True).upper()
        ff, fl = E.fit_plain(d, t, "sans-bold", W * E.SS - s(2 * M + 70), 1, 46, 28)
        d.text((s(M + 60), y + s(22)), E.line_text(fl[0]), font=ff, fill=E.WHITE)
        y += row
    return y_bottom - 2 * row


def finish(img):
    return img.resize((W, H), Image.LANCZOS)


def t_verdict(spec):
    img, d, acc, shade = E.base(spec, W, H, focus=0.16)
    CW, CH = img.size
    E.scrim(img, (0, int(CH * 0.36), CW, CH), shade, 250, 1.15)
    header(img, d, spec, acc, shade, "Fan verdict")
    yb = s(BOTTOM)
    yb = ask_pill(d, yb, spec.get("ask") or "Reply A or B", acc) - s(44)
    yb = options(d, yb, spec.get("option_a", ""), spec.get("option_b", ""), acc) - s(40)
    max_w = CW - s(2 * M)
    kick = R.clean(spec.get("kicker", ""))
    kf, kl = E.fit_plain(d, kick, "serif-it", max_w, 2, 40, 26) if kick else (None, [])
    if kl:
        yb -= E.rich_h(kl, kf, 1.16)
        E.draw_rich(d, (s(M), yb), kl, kf, E.SOFT, acc, 1.16)
        yb -= s(30)
    hf, hl = E.fit_rich(d, R.clean(spec.get("headline", ""), headline=True), "sans-bold", max_w, 4, 120, 56,
                        max_h=CH * 0.24)
    E.draw_rich(d, (s(M), yb - E.rich_h(hl, hf)), hl, hf, E.WHITE, acc)
    E.credit(d, CW - s(M), s(BOTTOM) + s(30), spec.get("credit"))
    return finish(img)


def t_thisorthat(spec):
    CW, CH = s(W), s(H)
    pa, pb = R.load_photo(spec.get("photo_a")), R.load_photo(spec.get("photo_b"))
    acc, shade = E.palette(pa or pb)
    acc = E.spec_accent(spec, acc)
    img = Image.new("RGB", (CW, CH), shade)
    half = CH // 2
    for raw, y in ((pa, 0), (pb, half)):
        if raw:
            img.paste(R.natural(raw, CW, half, 0.2), (0, y))
    d = E.ImageDraw.Draw(img)
    E.scrim(img, (0, half - s(300), CW, half), shade, 235, 1.0)
    E.scrim(img, (0, half, CW, half + s(260)), shade, 235, 1.0, up=True)
    E.scrim(img, (0, CH - s(520), CW, CH), shade, 240, 1.1)
    header(img, d, spec, acc, shade, "This or that")
    # the question sits on the seam; A's name just above it, B's just below it, faces stay clear
    qf, ql = E.fit_rich(d, R.clean(spec.get("question", ""), headline=True), "sans-bold", CW - s(2 * M), 2, 76, 40)
    qh = E.rich_h(ql, qf)
    qy = half - qh // 2
    E.scrim(img, (0, qy - s(260), CW, qy + qh + s(260)), shade, 210, 1.0)
    E.draw_rich(d, (s(M), qy), ql, qf, E.WHITE, acc)
    lf = E.f("mono", 22)
    for letter, text, y in (("A", spec.get("option_a", ""), qy - s(120)), ("B", spec.get("option_b", ""), qy + qh + s(70))):
        ff, fl = E.fit_plain(d, R.clean(text, True).upper(), "sans-bold", CW - s(2 * M + 60), 1, 56, 32)
        d.text((s(M), y + s(18)), letter, font=lf, fill=acc)
        d.text((s(M + 48), y), E.line_text(fl[0]), font=ff, fill=E.WHITE)
    ask_pill(d, s(BOTTOM), spec.get("ask") or "Reply A or B", acc)
    if spec.get("credit_a"):
        E.credit(d, CW - s(M), qy - s(170), spec.get("credit_a"))
    if spec.get("credit_b"):
        E.credit(d, CW - s(M), s(BOTTOM) + s(30), spec.get("credit_b"))
    return finish(img)


def t_quote(spec):
    img, d, acc, shade = E.base(spec, W, H, focus=0.14)
    CW, CH = img.size
    E.scrim(img, (0, int(CH * 0.38), CW, CH), shade, 250, 0.9)
    header(img, d, spec, acc, shade, "Said today")
    yb = ask_pill(d, s(BOTTOM), spec.get("ask") or "Agree or disagree? Reply", acc) - s(56)
    ctx = R.clean(spec.get("context", ""))
    if ctx:
        cf, cl = E.fit_plain(d, ctx.upper(), "mono", CW - s(2 * M), 1, 18, 12)
        E.tracked(d, (s(M), yb - cf.size), E.line_text(cl[0]), cf, E.DIM, 0.06)
        yb -= cf.size + s(20)
    E.tracked(d, (s(M), yb - s(34)), R.clean(spec.get("speaker", ""), True).upper(), E.f("sans-bold", 30), E.WHITE, 0.04)
    d.rectangle((s(M), yb - s(60), s(M + 40), yb - s(57)), fill=acc)
    yb -= s(100)
    qf, ql = E.fit_plain(d, R.clean(spec.get("quote", ""), headline=True), "serif", CW - s(2 * M), 6, 96, 40, lead=1.04,
                         max_h=CH * 0.30)
    qtop = yb - E.rich_h(ql, qf, 1.04)
    d.text((s(M - 4), qtop - s(140)), "“", font=E.f("serif", 170), fill=acc)
    E.draw_rich(d, (s(M), qtop), ql, qf, E.WHITE, acc, 1.04)
    E.credit(d, CW - s(M), s(BOTTOM) + s(30), spec.get("credit"))
    return finish(img)


def t_result(spec):
    img, d, acc, shade = E.base(spec, W, H, focus=0.16)
    CW, CH = img.size
    E.scrim(img, (0, int(CH * 0.38), CW, CH), shade, 250, 1.1)
    header(img, d, spec, acc, shade, "Full time")
    yb = ask_pill(d, s(BOTTOM), spec.get("ask") or "Rate the winner out of 10", acc) - s(48)
    qf, ql = E.fit_plain(d, R.clean(spec.get("question", "")), "serif-it", CW - s(2 * M), 2, 44, 28)
    if ql:
        yb -= E.rich_h(ql, qf, 1.14)
        E.draw_rich(d, (s(M), yb), ql, qf, E.SOFT, acc, 1.14)
        yb -= s(48)
    sf, nf = E.f("sans-bold", 72), E.f("sans-bold", 120)
    for team, score in ((spec.get("away"), spec.get("away_score")), (spec.get("home"), spec.get("home_score"))):
        yb -= s(132)
        d.text((s(M), yb + s(30)), R.clean(str(team), True).upper(), font=sf, fill=E.WHITE)
        sc = str(score)
        d.text((CW - s(M) - d.textlength(sc, font=nf), yb), sc, font=nf, fill=E.WHITE)
        d.rectangle((s(M), yb + s(128), CW - s(M), yb + s(130)), fill=E.DIM)
    E.credit(d, CW - s(M), s(BOTTOM) + s(30), spec.get("credit"))
    return finish(img)


TEMPLATES = {"verdict": t_verdict, "thisorthat": t_thisorthat, "quote": t_quote, "result": t_result}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("template", choices=sorted(TEMPLATES))
    ap.add_argument("--spec", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    spec = json.load(open(a.spec)) if os.path.exists(a.spec) else json.loads(a.spec)
    img = TEMPLATES[a.template](spec)
    if spec.get("photo") is None and spec.get("photo_a") is None:
        sys.exit("NO PHOTO: a story frame needs a real photo")
    img.convert("RGB").save(a.out, quality=94)
    print(a.out, img.size)


if __name__ == "__main__":
    main()
