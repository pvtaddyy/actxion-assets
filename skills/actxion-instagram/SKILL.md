---
name: actxion-instagram
description: ACTXION's Instagram growth system for @actxionapp - "pick your side" niche, the 2026 Instagram signals (watch time, sends, likes per reach), the format mix (team combined XI reels plus automated carousels and portrait images), cadence in IST, captions, collabs, stories and the weekly loop. Use for anything ACTXION does on Instagram - planning, writing captions, making carousels or images, reviewing results, or deciding what the Instagram routines do. Builds on actxion-growth (niche and copy rules), actxion-visuals and actxion-slides (images), and the installed ig-* skills.
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
| Fan verdict carousel (the day's row, ends A or B) | `actxion-slides` carousel | 7 | Routine |
| Head to head / rank it | `actxion-slides` carousel (bars, versus) | 4 | Routine |
| Rumour desk | `actxion-visuals` rumour, portrait | 3 | Routine |
| Big moment back page / quote | `actxion-visuals` backpage or redcard, portrait | 3 | Routine |
| Trial reels | Trial reel | 3 | Team |
| Story polls | Story | daily | Human (poll stickers can't be automated) |

## Making the images
- **Carousels:** `actxion-slides` (`node render.mjs slides.json out`, 1080x1350). Shape: cover (photo + red card hook) → 2-4 of quote/stat/bars → versus (A or B) → outro "Pick your side". 4-7 slides, one idea a slide, about 15 words max per slide.
- **Single images:** `actxion-visuals` `render.py <template> --size portrait`. Story picks the template: backpage (big moment), ballot (A or B), rumour (with tier stamp), redcard (quote), scoreboard (full time).
- Photos: Wikimedia Commons only (CC0, PD, CC BY, CC BY-SA, 2000px+), credit on the image and in the first comment. Never agency, TV or club photos, never AI images of real people (`isAiGenerated` false).
- Look at every PNG before scheduling (nothing clipped, names spelled right, credit visible, not the same template as the last two posts).
- Hosting: commit the PNGs to the public `actxion-assets` GitHub repo and pass the `raw.githubusercontent.com` URLs to Metricool `media` (it copies them to its own storage). Never anonymous file hosts.

## Captions (run through ig-caption and ig-human)
- Line 1 is the hook and works before "... more". Short lines, one fact a line.
- End with one choice: "A or B?", "Send this to the Arsenal fan in your group".
- 3-5 hashtags, names in the text. No em dashes, no stray full stops at line ends, no "Let's dive in".
- Rumours name the source and tier. Never invent a quote, score, fee or stat.

## Scheduling (Metricool createScheduledPost)
- providers `[{"network":"instagram"}]`, `instagramData: {"type":"POST","isAiGenerated":false}`, `media` = the image URLs in slide order, `firstCommentText` = the photo credit.
- Slots: carousel 13:00 and 17:30 IST. Never within 45 minutes of a team reel; check getScheduledPosts first. Never two posts on the same story within 24 hours.

## Human-only jobs (never automate)
Likes, follows, comments, DMs, story poll stickers, collab invites. Draft them with ig-reply, ig-comment, ig-dm, ig-story; a person sends them.
- Collabs (UNITE): partner a fan page 0.5-2x our size, co-create a combined XI reel with the native Collab invite, agree the plan before creating, 1 a week.
- App loop: push the 500K app users to Instagram (in-app banner, match-night push). Biggest single lever.

## Weekly loop
Sunday report: followers, reach, non-follower share, top and bottom 5 by outlier multiple (views / account median) and sends per reach, which pillar won. Two experiments a week. A format below the account median for 2 weeks is dropped. Use ig-audit for the method and ig-viral to find outliers in the niche.
