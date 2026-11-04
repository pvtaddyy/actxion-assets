---
name: actxion-instagram
description: ACTXION's Instagram growth system for @actxionapp - "pick your side" niche, the 2026 Instagram signals (watch time, sends, likes per reach), the format mix (team combined XI reels plus automated carousels and portrait images), cadence in IST, captions, collabs, stories and the weekly loop. Use for anything ACTXION does on Instagram - planning, writing captions, making carousels or images, reviewing results, or deciding what the Instagram routines do. Builds on actxion-growth (niche and copy rules), actxion-visuals (Still Frame cards, the same as X), and the installed ig-* skills (Jakeschincariol/instagram-agent-skill).
---

# ACTXION on Instagram

The Instagram layer of `actxion-growth`. Read that skill first for the niche ("football's fan verdict") and the no-AI-tells copy rules; this file adds what is different on Instagram. The full playbook is `~/.claude/scheduled-tasks/actxion-ig/INSTAGRAM-PLAYBOOK.md`.

Curated from: social-media-skills/skills (`instagram-growth`, `carousel-writer`, `collabs-and-cross-promotion`, `trend-jacking`, `meme-and-culture`, `quote-cards-and-text-graphics`), coreyhaines31/marketingskills (`social`, `referrals`, `marketing-psychology`), Nutlope/hallmark (never invent a number, quote or logo), ScrapeCreators/social-media-research-skills (outlier finding, comment mining) and our own Metricool data.

## Facts
- Account: @actxionapp, Metricool brand/blogId **4945970**, timezone **Asia/Kolkata**.
- Baseline (3 Nov 2026): 4,120 followers and falling since the ads stopped. Organic reach 1-3K a day. Followers: India 24%, Kenya 11%, Indonesia 9%, Nigeria 8%, Brazil 5%, UK 2%.
- Proven winner: the team's combined XI / player by player reels (1,300-2,100 views every time, breakouts of 11-13K). News reels with X captions get about 200 views. Single images and Fan Wall carousels got no follows.
- Best hours (Metricool, our followers): 18:00-21:30 IST.

## How Instagram ranks in 2026
1. **Watch time** (reels: the first 3 seconds decide it) and **dwell** (carousels: every swipe counts).
2. **Sends per reach** (shares into DMs) are the strongest signal for reaching non-followers. Make posts people send to a mate who's wrong.
3. **Likes per reach** matter most with existing followers.
4. **Originality.** Since April 2026 accounts that mostly re-upload others' content lose recommendations. Every post must add something of ours.
5. Max 5 hashtags. Instagram search reads captions, so the player, club and competition names go in the caption text.

Diagnose before prescribing (instagram-growth loop): no views = hook problem; views but no follows = profile problem; follows but no repeat views = retention (stories, replies).

## Format mix (per week)
| Pillar | Format | Per week | Made by |
|---|---|---|---|
| Combined XI / player by player | Reel | 7 | Team |
| Star moment (one moment, text hook in the first second) | Reel | 5-7 | Team |
| Fan verdict carousel (the day's row, ends A or B) | Still Frame carousel | 7 | Routine |
| Head to head / rank it | Still Frame carousel (poster, scoreboard, ballot) | 4 | Routine |
| Rumour desk | `actxion-visuals` rumour, portrait | 3 | Routine |
| Big moment back page / quote | `actxion-visuals` backpage or redcard, portrait | 3 | Routine |
| Trial reels | Trial reel | 3 | Team |
| Story polls | Story | daily | Human (poll stickers can't be automated) |

## Making the images (same method as the X desks)
Source of truth: `github.com/pvtaddyy/actxion-assets` (`main`). Read `skills/actxion-visuals/DESIGN.md` ("Still Frame") and its SKILL.md first. Owner rules: real-colour photos only, UK times in copy and on images, no blank cards.

- **Every Instagram image is a Still Frame card** from `skills/actxion-visuals/scripts/render.py` (portrait 1080x1350 by default): `poster`, `redcard`, `ballot`, `scoreboard`, `rumour`. Headlines in caps with one or two `*words*` marked.
- **Carousels are a run of Still Frame cards**, one render per slide, so Instagram looks exactly like X. Don't use actxion-slides for Instagram (it's the older look). Put the slide number in `label` ("Fan verdict 1/6"). Structure (ig-carousel from Jakeschincariol/instagram-agent-skill): 1 cover `poster` (6 words or fewer) → 2 the stake `poster` → 3-4 one idea a slide (`redcard` for a quote, `poster` for the other side, `scoreboard` for a result) → 5 verdict `ballot` with both faces → 6 the ask `poster` over a stadium or fans photo ("Comment *A* or *B*"). 6-8 slides. Alt text on the cover.
- **Photos:** `python3 skills/actxion-visuals/scripts/find_photo.py "<full name>" --club "<club or national team>" --article "<story URL>"` → JSON {path, credit, source}. Order: the article's own photo (credited to the outlet), the person's Wikipedia photo, Bing News photos, Openverse/Commons, the shared `photos/` library (least-used first, `photos/index.json`).
- **Identity check (no face recognition, so you do it):** Read every photo. It must clearly be that person (face, kit, crest, number). If it's someone else, add the file name or article URL to `photos/blocklist.txt`, delete it and rerun. If the person is in the frame but off-centre, crop to them before rendering (the renderer centres horizontally).
- **No repeats:** never the same photo twice in one carousel, and not a photo X used in the last 24 hours if another exists (the `used` counts in `photos/index.json` spread this). Wikimedia Commons search by full name finds extra angles.
- `render.py` refuses a card without a photo (exit 3). Fix the photo; `--text-ok` only for a deliberate text card, with the reason in the run report.
- Look at every PNG before scheduling: nothing clipped, names right, credit visible, not the same template as the last two posts.

## Hosting (cloud routines, identical to X)
1. `python3 -m pip install -q --ignore-installed pillow`
2. `git fetch -q origin main claude/posts && git checkout -q -B claude/posts origin/claude/posts && git merge -q --no-edit -X theirs origin/main`
3. Render to `posts/<YYYY-MM-DD>/ig-<HHMM>-<slug>-<NN>.png`, then `git add posts photos && git commit -m "ig <slug>" && git pull --rebase origin claude/posts && git push origin claude/posts`
4. URL: `https://raw.githubusercontent.com/pvtaddyy/actxion-assets/claude/posts/<path>`. Poll until HTTP 200, then pass the URLs in slide order in Metricool `media`.
Cloud runs push only to `claude/*`. The repo is public: nothing private in it. Never anonymous file hosts.

## Avoiding repeats across platforms
Before choosing stories, read the Metricool queue with getScheduledPosts for the last 24h and the next 24h, all networks. Don't post a story X or Facebook already covered in that window unless Instagram adds a new angle (a carousel that explains it, a verdict). A shared story log for X, Instagram and Facebook doesn't exist yet; it is proposed to the owner in the playbook.

## Captions (run through ig-caption and ig-human)
- Line 1 is the hook and works before "... more". Short lines, one fact a line.
- End with one choice: "A or B?", "Send this to the Arsenal fan in your group".
- 3-5 hashtags, names in the text. No em dashes, no stray full stops at line ends, no "Let's dive in".
- Rumours name the source and tier. Never invent a quote, score, fee or stat. Times in UK time.

## Scheduling (Metricool createScheduledPost)
- providers `[{"network":"instagram"}]`, `instagramData: {"type":"POST","isAiGenerated":false}`, `media` = the image URLs in slide order, `firstCommentText` = the photo credit.
- Slots: carousel 13:00 and 17:30 IST. Never within 45 minutes of a team reel; check getScheduledPosts first. Never two posts on the same story within 24 hours.

## Human-only jobs (never automate)
Likes, follows, comments, DMs, story poll stickers, collab invites. Draft them with ig-reply, ig-comment, ig-dm, ig-story; a person sends them.
- Collabs (UNITE): partner a fan page 0.5-2x our size, co-create a combined XI reel with the native Collab invite, agree the plan before creating, 1 a week.
- App loop: push the 500K app users to Instagram (in-app banner, match-night push). Biggest single lever.

## Weekly loop
Sunday report: followers, reach, non-follower share, top and bottom 5 by outlier multiple (views / account median) and sends per reach, which pillar won. Two experiments a week. A format below the account median for 2 weeks is dropped. Use ig-audit for the method and ig-viral to find outliers in the niche.
