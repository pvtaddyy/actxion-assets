---
name: actxion-slides
description: ACTXION's branded slide and image system - "the red card" design language on newsprint (shared brand with actxion-visuals), 7 templates (cover, stat, bars, quote, versus, points, outro), rendered to 1080x1350 PNGs with Playwright for LinkedIn document carousels, single-image posts, X and Instagram. Use whenever ACTXION needs a carousel, a stat card, a quote card, a poll visual or any branded social image ("make the slides", "Fan Pulse carousel", "quote card", "stat graphic").
---

# ACTXION slides: "the red card"

Built from the frontend-design skill's process (token plan, then a self-review against generic AI defaults), ui-ux-pro-max type and contrast rules, anthropics/skills `canvas-design` (one bold move, everything else quiet), and the strongest 2026 carousel skills on GitHub (dev-pf66/carousel-generator: 15 words a slide, never invent a stat; amigoscode/skills carousel: HTML, then Playwright, then 1080x1350 PNG and PDF).

## Design language (shared brand with actxion-visuals)
- **The one bold move: the red card** (`#E61E28`), used the way football uses red: for the verdict, the key number, the stamp. Never as decoration and never to highlight a single word.
- **Two grounds:** data slides are printed on **newsprint** `#F2EEE5` with ink `#0A0A0A` (a matchday programme / annual report feel). Only the cover and outro are **night at the stadium** (`#050505` with a black-and-white halftone Wikimedia photo). That mix avoids the "near-black plus one accent" AI default.
- **Type (same faces as actxion-visuals):** Anton for headlines and big numbers, Barlow Condensed for labels, bar values and the top meta, Source Serif 4 for body and context lines. Sentence case. Loaded from Google Fonts in the renderer; identical TTFs live in `~/.claude/skills/actxion-visuals/assets/fonts`.
- **Furniture:** a 3px ink rule under the top bar (logo + wordmark left, "series n/total" right), ruled rows like a printed table, ballot tick boxes for either/or, paper grain, slightly crooked cards. Source line in grey at the bottom of every data slide.
- **Layout:** 1080x1350, 88px margins, left-aligned.
- **Copy rules:** at most about 15 words of body per slide. A headline of 2–8 words. Every number gets a source. Never invent a stat, quote or poll result. `**bold**` for emphasis (weight only); `\n` for headline breaks only when needed.

## Templates (`type`)
| type | fields | use |
|---|---|---|
| `cover` | title, text?, photo?, card?{big, small}, source? | Slide 1: hook. The photo is a Wikimedia HD image URL (credit in source). The card holds the hook number. |
| `stat` | number, label, text, source | One huge number on a tilted red card. |
| `bars` | title, bars[{label, value, display?, highlight?}], text?, source | Ranked comparison (max 6 bars). Highlight the one the story is about. |
| `quote` | quote, who, role?, source? | Real, sourced quotes only. |
| `versus` | title, options[{title, text?, tick?}] (2–4), text? | Ballot slip. Used for the poll-result card (tick the winner) or an either/or debate. LinkedIn polls themselves can't carry images. |
| `points` | title, points[{head, text}] (3) | "What clubs should take from this." |
| `outro` | title?, text?, cta? | Last slide. Default: "The fan's view of the business of football." / Follow ACTXION. |

Top-level: `{"series": "Fan Pulse", "slides": [...]}`. A carousel is 6–8 slides: cover, then 3–5 of stat/bars/quote/versus, then points, then outro. A single-image post is one `stat`, `quote` or `cover` slide.

## Render
```bash
cd <dir with render.mjs>   # scripts/render.mjs in this skill
npm i playwright@1.49.1 && npx playwright install chromium   # first time only
node render.mjs slides.json out   # writes out/01.png, 02.png ...
```
The renderer downloads photos itself (with a User-Agent, as Wikimedia requires) and drops a photo that fails instead of crashing. Wikimedia thumbs only come in standard widths: use the `thumburl` from `scripts/find_image.py` (3840px) or the original `url`, never an invented `NNNNpx` size.

## Review before shipping (look at the PNGs)
- Nothing overflows, nothing is cut off, the headline doesn't wrap to one word per line.
- The text is readable on a phone at 1/3 size (body text at least 34px; already the default).
- The cover alone makes someone want to swipe.
- Sources are on every data slide.

## Publishing (Metricool)
Metricool `media` needs **public URLs** of the PNGs. Host them where ACTXION owns the account (see the LinkedIn routines for the current host). Then for a LinkedIn carousel: `linkedinData: {"type":"post","previewIncluded":true,"publishImagesAsPDF":true,"documentTitle":"<cover headline>"}` and all slide URLs in order in `media`. For a single-image post, one URL and `publishImagesAsPDF` false.

Example specs: `examples/fan-pulse-money-league.json` (6-slide carousel), `examples/poll-result.json` (single ballot card; its result is illustrative).

Cloud hosting: commit PNGs to the public GitHub repo `actxion-assets` the routine clones, push, and pass the `raw.githubusercontent.com` URLs to Metricool. Never use anonymous file hosts.
