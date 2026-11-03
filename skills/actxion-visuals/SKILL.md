---
name: actxion-visuals
description: ACTXION's football-artifact design system and renderer for X post images. Turns a story into a branded graphic built from real football objects (tabloid back page, ballot slip, stadium scoreboard, transfer dossier, referee's red card) instead of generic AI cards. Use whenever an ACTXION X post needs an image, a Fan verdict graphic, a full-time score card, a rumour graphic or a quote card, or when someone says the visuals look AI-generated, generic or low quality. Pairs with actxion-growth (what to post) and actxion-slides (multi-slide carousels).
---

# ACTXION visuals

The account posts football controversy, rumours and debates. Its images should look like they came out of football itself: something a fan has held, read or stared at on a matchday. That is what separates them from the AI defaults everyone now recognises (purple gradients, glass cards, near-black with one neon accent, a centred hero with three icons).

## The design language

**Palette:** black, white and red, ACTXION's own colours. The red is a referee's card (`#E61E28`), so use it the way football uses red: for a decision, a warning or a stamp, not for decoration. Light templates are printed on newsprint (`#F2EEE5`) and dark ones are night at the stadium, not flat UI black.

**Type**, all open-licence and bundled in `assets/fonts`:
- **Anton** for headlines, a condensed tabloid face.
- **Barlow Condensed** for labels, stamps and scoreboards, a stadium-signage feel.
- **Source Serif 4** for kickers and context lines, newspaper body text.
- **Archivo Narrow** for typed dossier fields and photo credits.

Inter, Space Grotesk, Geist and the other "tasteful default" faces are avoided on purpose.

**Photos:** only free-licence HD photos from Wikimedia Commons, credited. They are shown **as real photos in their own colours**: cropped, levelled and sharpened, never tinted red, turned black and white or printed as dots. The owner's call: a real face next to the design's text is what makes the post feel relevant. The brand colours live in the type, panels, cards and stamps, not on the person. (`"photo_style": "print"` brings back the old halftone/duotone look for a one-off, but don't use it by default.) Never use agency or TV images, and never AI images of real people.

**Texture:** a little paper grain, hand-crooked stamps and slips. Real objects are never perfectly straight; that is part of why these read as made rather than generated.

## The six templates

Pick the object that matches the story. The story decides the template, not the other way round.

| Template | Football object | Use for | Spec fields |
|---|---|---|---|
| `backpage` | Red-top tabloid back page | Big news, manager pressure, records, viral moments | `headline`, `kicker`, `photo`, `credit`, `date` |
| `ballot` | Paper ballot slip with tick boxes | "Fan verdict" A-or-B debates | `question`, `option_a`, `option_b`, `context`; for two people add `photo_a`, `photo_b`, `credit_a`, `credit_b` |
| `scoreboard` | Stadium dot-matrix board | Full-time results, half-time, big scorelines | `home`, `away`, `home_score`, `away_score`, `scorers`, `status`, `question`; add `photo`, `photo_label`, `credit` for the player or manager of the night |
| `rumour` | Typed transfer file with a rubber stamp | Transfer and manager rumours, with the source's reliability tier | `player`, `from_club`, `to_club`, `fee`, `source`, `tier` (1-3), `photo`, `credit` |
| `redcard` | Referee's red card | A controversial quote, a manager or player outburst | `quote`, `speaker`, `context`, `label`; add `photo`, `credit` to print the speaker beside the card |
| `poster` | Full-height red-and-black print of one person | The one big story about one person: pressure, a record, a return | `headline`, `kicker`, `label`, `photo`, `credit` |

**Use a photo of the person whenever the story is about a person.** Real faces stop the scroll and make the image make sense on its own. The photo variants switch on automatically when the photo fields are filled. A ballot about two players shows both; a scoreboard shows the manager under pressure or the match winner; a red card shows whoever said it. Fall back to the text-only version only when Commons has no free HD photo of that person, and never use a photo of someone else.

## Render

```bash
python3 ~/.claude/skills/actxion-visuals/scripts/render.py ballot \
  --spec '{"question":"Should Iraola tell Isak to go down?","option_a":"Yes, refs force it","option_b":"No, stay on your feet","context":"Timber held his shirt and VAR never looked"}' \
  --out post.png --size x
```

- `--size x` gives 1600x900, the size X shows full width in the feed. `portrait` (1080x1350) and `square` (1080x1080) are for Instagram and LinkedIn.
- `--spec` takes inline JSON or a path to a JSON file.
- `photo` takes a local path or a Wikimedia `https://upload.wikimedia.org/...` URL.
- The script needs Pillow (`pip install pillow`) and nothing else. Fonts and logo masks ship in `assets/`, so it renders the same on a Mac and on a Linux cloud box.

Thumbnail URLs (`.../thumb/.../2560px-...`) also work: if Commons refuses the size, the renderer retries 3840px, 1920px and then the original file.

**Finding photos:** run `python3 skills/actxion-visuals/scripts/find_photo.py "<full name>" --club "<club or national team in the story>"`. It searches "name + club" first (one search usually lands on the right person), then the name alone, on Openverse and Wikimedia Commons with retries. It accepts a photo only when the title has the full name in order and the file is tagged as football, which rules out namesakes from music, art or other sports. Clear close faces rank first, recent (2024 to 2026) photos rank higher, and each call prefers a photo the account hasn't posted yet. Every photo is saved to `photos/` (up to 10 per person, rolling), which is the fallback when the APIs refuse the cloud machine. The finder answers within about 40 seconds, so it never holds up a run. Look at the photo before using it and drop it if it isn't clearly that person, or if it looks like a club's or agency's official shot (a signing-day backdrop, a broadcast frame), which is often a mislabelled upload. When you drop a photo for either reason, add its file name to `photos/blocklist.txt` so no run picks it again.

**Real match moments:** agency, broadcaster and club photos are never used in our own images, because X removes them on a copyright notice and strikes the account. When the actual moment matters (the goal, the red card, the celebration), quote the official club, competition or broadcaster post instead: no image of your own, with its x.com status URL on the last line of the text.

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
