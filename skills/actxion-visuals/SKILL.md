---
name: actxion-visuals
description: ACTXION's football-artifact design system and renderer for X post images. Turns a story into a branded graphic built from real football objects (tabloid back page, ballot slip, stadium scoreboard, transfer dossier, referee's red card) instead of generic AI cards. Use whenever an ACTXION X post needs an image, a Fan verdict graphic, a full-time score card, a rumour graphic or a quote card, or when someone says the visuals look AI-generated, generic or low quality. Pairs with actxion-growth (what to post) and actxion-slides (multi-slide carousels).
---

# ACTXION visuals

The account posts football controversy, rumours and debates. Its images should look like they came out of football itself: something a fan has held, read or stared at on a matchday. That is what separates them from the AI defaults everyone now recognises (purple gradients, glass cards, near-black with one neon accent, a centred hero with three icons).

## The design language: Still Frame

Read `DESIGN.md` before designing anything. In short: every card is the real photo, full-bleed, in its own colours, with a soft vignette tinted from the photo's own tones behind the type. Headlines run in caps (Instrument Sans Bold). Wrap the one or two words that carry the story in asterisks, like `"Carrick leaves *Lisandro* on the bench"`; they get a marker block in the accent colour. The accent is taken from the photo itself (the kit, a board). Mono datelines (Geist Mono), the human line in Instrument Serif. The older newsprint and red-card look is retired; `--style classic` still renders it if ever needed.

**Size: portrait 4:5 (1080x1350) by default.** On the X phone app a single 4:5 image shows uncropped and fills about twice the screen of a 16:9 one, which is what X's dwell-time ranking rewards. Use `--size x` (1600x900) only for a deliberate test; the weekly report compares the two.

## The templates

Pick the object that matches the story. The story decides the template, not the other way round.

| Template | Look | Use for | Spec fields |
|---|---|---|---|
| `poster` / `backpage` | Full photo, caps headline and italic kicker on the lower third | The big story about one person: pressure, records, sackings, viral moments | `headline`, `kicker`, `label`, `date`, `photo`, `credit` |
| `ballot` | Two full-height photos side by side, "or" on the seam, question on top | Fan verdict A-or-B debates | `question`, `option_a`, `option_b`, `photo_a`, `photo_b`, `credit_a`, `credit_b`, `label` |
| `scoreboard` | Full photo with the score table and club badges over the top | Full time, half time, kick-off previews | `home`, `away`, `home_score`, `away_score`, `scorers`, `status`, `label`, `question`, `photo`, `photo_label`, `credit`; optional `home_crest_name` / `away_crest_name` when the short name is ambiguous (e.g. "Man Utd" -> "Manchester United") |
| `rumour` | Full photo, player name, badge FROM -> badge TO, fee, source, reliability squares | Transfer and manager rumours with the source tier | `player`, `from_club`, `to_club`, `fee`, `source`, `tier` (1-3), `photo`, `credit` |
| `redcard` | Full photo, the quote large in serif over the lower half | A quote, an outburst, a press-conference line | `quote`, `speaker`, `context`, `label`, `photo`, `credit` |

Club badges are looked up automatically from each club's Wikipedia page and cached in `photos/crests/`. Use full club names (or the `*_crest_name` fields) so the lookup finds the right club. Highlighting with `*asterisks*` works in `headline`, `question`, `quote`, `player` and `option_a`/`option_b`; use it on at most two words.

**Use a photo of the person whenever the story is about a person.** Real faces stop the scroll and make the image make sense on its own. The photo variants switch on automatically when the photo fields are filled. A ballot about two players shows both; a scoreboard shows the manager under pressure or the match winner; a red card shows whoever said it. Never use a photo of someone else.

**No photo, no image.** The renderer refuses a card without a photo (exit code 3, "NO PHOTO") because a blank dark card is what went out on 4 Nov when the finder missed. When that happens, in this order:
1. Run `find_photo.py` again without `--article`: it now tries the person's Wikipedia photo, then recent news articles about them, then Commons.
2. Still nothing: use the other person in the story (the manager who spoke, the player it's about, the rival), or the story article's own match photo, and say so in the alt text.
3. A ballot with one photo is fine: it runs that photo full-bleed.
4. `--text-ok` exists for a deliberate text card only. If you use it, say why in the run report.

## Render

```bash
python3 ~/.claude/skills/actxion-visuals/scripts/render.py ballot \
  --spec '{"question":"Should Iraola tell Isak to go down?","option_a":"Yes, refs force it","option_b":"No, stay on your feet","context":"Timber held his shirt and VAR never looked"}' \
  --out post.png
```

- Default size is portrait 1080x1350. `--size x` is 1600x900, `square` is 1080x1080.
- `--spec` takes inline JSON or a path to a JSON file.
- `photo` takes a local path or a Wikimedia `https://upload.wikimedia.org/...` URL.
- The script needs Pillow (`pip install pillow`) and nothing else. Fonts and logo masks ship in `assets/`, so it renders the same on a Mac and on a Linux cloud box.

Thumbnail URLs (`.../thumb/.../2560px-...`) also work: if Commons refuses the size, the renderer retries 3840px, 1920px and then the original file.

**Finding photos:** run `python3 skills/actxion-visuals/scripts/find_photo.py "<full name>" --club "<club or national team>" --article "<the article URL you took the story from>"`. Pass `--article` every time (repeat it for a second source). The order it tries, stopping at the first that works (about a minute at most):
1. **The story article's lead photo:** real-time and about exactly this story, credited "Photo: <agency> via <outlet>" when the caption names one, otherwise "Photo: <outlet>". Logos and title graphics such as Sky's "Paper Talk" card are skipped automatically.
2. **The person's own Wikipedia photo:** always the right person, free licence. Used once, then the next options take over.
3. **Recent news articles that name the person** (Bing News) and their lead photos. These can show a team-mate or the manager, so check them.
4. **Openverse and Wikimedia Commons:** "name + club" title search, football-tagged, recent first.
5. **The saved library** in `photos/`.

The JSON's `source` says which one won. Look at the photo before using it. If it isn't clearly that person, add the file name, or the article URL for an article photo, to `photos/blocklist.txt`, delete the file and run again: the next source is used. `--no-search` skips step 3.

For a stadium, search Commons for the stadium name. Keep only CC0, public domain, CC BY or CC BY-SA files at least 2000px on the long side, and put the credit in the post's first comment as well as on the image.

## Copy on images

The renderer already strips em dashes and underscores, and drops full stops from the ends of headlines. Still write it right the first time:
- Headlines are what a back-page sub-editor would write. Short, one idea, no full stop at the end, and a question mark only when it is a real question.
- A full stop in the middle of a headline ("NINE WITHOUT A WIN. IS TONIGHT CARRICK'S LAST?") is fine when it is two beats. Avoid it otherwise.
- No hashtags on images, no "BREAKING" unless a Tier 1 source confirmed it, no emoji on images.
- Kick-off and other times on images are UK time, e.g. `"status": "Kick-off 8pm UK"`. Never IST.
- Never invent a score, quote or fee. If the fee is unknown, write "Not reported".

## Check before posting

Look at the PNG, because a render can hide problems the spec can't. Check:
1. Nothing is clipped or overlapping.
2. Every name is spelled the way the source spells it.
3. The photo credit is visible.
4. It would still make sense if someone only saw the image, not the text.
5. It doesn't look like the last three images posted. Rotate templates so the feed doesn't turn into one repeated card.

## Getting images to X from a cloud routine

This is tested and working (3 Nov 2026):

1. **Install Pillow** with `python3 -m pip install -q --ignore-installed pillow`. Plain `pip` installs for a different Python on the cloud box, and the system copy of Pillow there is broken.
2. **Check out the posts branch:** `git fetch -q origin claude/posts && git checkout -q -B claude/posts origin/claude/posts`. Cloud runs can push to `claude/` branches; `main` holds the skills.
3. **Render** to `posts/<YYYY-MM-DD>/<HHMM>-<slug>.png`.
4. **Commit and push:** `git pull -q --rebase origin claude/posts; git push -q origin claude/posts`.
5. **Get the image URL:** `https://raw.githubusercontent.com/pvtaddyy/actxion-assets/claude/posts/<path>`. It returns 200 within seconds.
6. **Schedule:** pass that URL in Metricool's `media`. Metricool copies the file to static.metricool.com when the post is scheduled.

Never upload brand files to anonymous public file-sharing hosts.
