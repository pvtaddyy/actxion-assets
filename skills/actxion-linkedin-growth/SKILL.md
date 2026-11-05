---
name: actxion-linkedin-growth
description: ACTXION's LinkedIn growth system - company page as credibility hub, founder and team profiles as the reach engine, weekly cadence, pillars, targets and guardrails. Use when planning, reviewing or running anything for ACTXION on LinkedIn ("plan the LinkedIn week", "why is LinkedIn dead", "LinkedIn report", "what should the founder post"). Builds on actxion-growth (cross-platform niche and copy rules). Pairs with actxion-linkedin-writer (the words) and actxion-slides (the visuals, same brand as actxion-visuals).
---

# ACTXION LinkedIn growth

Curated from the best 2026 open-source LinkedIn skills (social-media-skills/skills `linkedin-company-pages` and `linkedin-growth`, sergebulaev/linkedin-skills `content-planner` / `employee-advocacy` / `engager-analytics`, espindolavinicius/linkedin-growth-skill), then fitted to ACTXION's data. The full playbook is `~/.claude/scheduled-tasks/actxion-linkedin/PLAYBOOK.md`.

## Facts to work from
- Page: ACTXION company page, `urn:li:organization:101149376`, Metricool brand/blogId **4945970**, timezone **Asia/Kolkata**.
- Baseline (3 Nov 2026): 57 followers, median 6 impressions/post, 0 shares in 90 days. Followers: 44% UK, business development and professional services.
- ACTXION facts allowed in copy: "500K+ Google Play downloads", "One App. All Sports. Built for Fans", fans vote and give their verdict in the app. Nothing else unless the team supplied it (never invent users, partners, funding, revenue).

## The model: HUB + PEOPLE
1. **The page is the hub, not the megaphone.** Pages get a small slice of feed reach in 2026 (people beat logos by roughly 4–6x on reach and about 63% on engagement). The page's jobs: credibility for clubs, sponsors, investors and press; the official record; a library of saveable carousels.
2. **People are the engine.** The founder posts 2x a week from their own profile; the team reshares each page post with their own line in the first hour; the founder leaves 5 thoughtful comments a day on sports-business posts. All of this is human, done by hand. Automation only drafts.
3. **Saves and real comments beat likes.** Optimise for dwell time: carousels (documents), polls, data, clear opinions. No engagement bait.

## Positioning
"ACTXION: the voice of the fan, for the people who run the game." Every post answers: *what do fans really think, and why should the business of football care?* On X, ACTXION is the fan arguing in the pub; on LinkedIn it explains fans to the industry.

## Pillars (share of page posts)
| Pillar | Share | What |
|---|---|---|
| Fan Pulse (insight carousel) | 35% | Public data (Deloitte, UEFA, league and club reports, attendance, prices, TV deals) + the fan angle + 3 takeaways for clubs/sponsors |
| The fan-side read | 35% | A sports-business story this week (ownership, sackings, ticket prices, broadcast, sponsorship, VAR rules, fan protests) with one clear opinion |
| Building ACTXION | 20% | Milestones, features, lessons from 500K fans; only with facts the team sent |
| People and culture | 10% | Team, hiring, events; only from the team |

## Weekly cadence (IST; 13:30 IST = 08:00 UK, the page's top audience)
| Slot | Post | Format |
|---|---|---|
| Tue 13:30 | Fan-side read #1 | Text + 1 branded image (stat or quote card from actxion-slides) |
| Wed 13:30 | **Fan Pulse** | Document carousel, 6–8 slides from actxion-slides, `publishImagesAsPDF` |
| Thu 13:30 | Industry poll | LinkedIn poll, 7 days, 2–4 options |
| Fri 13:30 | Fan-side read #2 (or a milestone/culture post when the team has sent facts) | Text + 1 branded image |
| Mon 08:00 | Team reshare pack (drafts only) | team reshare lines; everything for the founder (posts, comments, his reshare lines) is in `zero-to-unicorn-linkedin` |
| Sun 19:00 | Weekly report | Metrics vs targets, best/worst, one change |

### Voice: "Fan Pulse in 60 seconds" (ElevenLabs, paid plan from 5 Nov 2026)
- **What:** every other Friday, the Friday slot becomes a 45–60 s narrated video of that week's Wednesday carousel instead of the image post (still 4 page posts a week). 1080x1350 (4:5, fills the LinkedIn feed), the carousel slides with gentle Ken Burns motion and slide-to-slide cuts, word-by-word burned-in captions (most LinkedIn video is watched muted), the ACTXION lockup throughout, ending on the outro slide.
- **Voice:** the house voice of the video desks, so the brand sounds the same everywhere: ElevenLabs `creative_generate_speech`, eleven_v4, voice Petros `vr54y8Xovf4AEnfNrGqH`, `generations_count: 1` (settings and fallbacks live in actxion-video, which owns them). Script: 110–150 words, the cover hook, the 2–3 key numbers with their source said aloud, the 3 takeaways, "Follow ACTXION for the fan's view of the business of football." No music bed, or a quiet one from actxion-video's licensed list.
- **Credits are shared with the video desks.** Plan: Starter, 30,000 credits a month; the daily reel is capped at 12,500, leaving about 17,500 for LAB, THE MIC and LinkedIn combined. LinkedIn's budget is about 1,300 credits a month (2 videos). Before generating, sum this month's rows in `posts/elevenlabs-ledger.csv` on the `claude/posts` branch of actxion-assets; after generating, append `date,slug,model,credits` (e.g. `2026-11-13,linkedin-fan-pulse-60s,eleven_v4,620`) and push. If ElevenLabs says busy or the monthly credits are low, use Kokoro `bm_fable`; if neither is available, post the normal Friday image post. Never retry in a loop.
- **Caption:** like a carousel caption (writer skill), first line "60 seconds on …". Metricool LinkedIn video post with `linkedinData {"type":"post","previewIncluded":true}`.
- **Not cross-posted:** football clips and Reels from the video desks stay off the page (max 1 a week with a business caption, per the rule below).
- **Judge it after 4 videos** (the Sunday report): keep it only if its median impressions beat the median of the image posts it replaced.

Metricool does not report LinkedIn poll votes, so poll results are never automated or guessed; if the founder shares the real split, a ballot card (actxion-slides `versus` with `tick`) can report it. Never more than 1 page post a day. Weekends off. Football clips are not cross-posted to LinkedIn (max 1/week with a business caption).

## Automate vs human
- **Automated (cloud routines via Metricool, the official partner API):** research, writing, slide rendering, scheduling page posts, drafting founder/team material, reporting.
- **Human only (LinkedIn bans bots on personal accounts):** founder posting, all comments, likes, reshares, connection requests, invites, DMs, page settings. Never automate these, never script a browser to do them.

## Targets (deadline 31 Jan 2027)
| Date | Followers | Median impressions per page post | Also |
|---|---|---|---|
| 16 Nov | 75 | 50 | page fixes done; founder posted 4x |
| 2 Dec | 120 | 100 | a carousel over 500 impressions |
| 1 Jan | 250 | 175 | 1 inbound conversation |
| 31 Jan | 500 | 250 | a post over 2,000; 3 inbound conversations |
If a checkpoint misses by more than half, first check whether the human part happened, then change formats.

## Metrics (Metricool getAnalyticsDataByMetrics, brandId 4945970)
Account: LIEV01 followers, LIEV08 new followers, LIEV18 post impressions, LIEV05 reactions, LIEV06 comments, LIEV19 shares, LIEV07 clicks, LIEV31 page views. Posts: LIPO02 date, LIPO04 text, LIPO19 type, LIPO12 impressions, LIPO13 reactions, LIPO10 comments, LIPO18 shares, LIPO09 clicks. Per-post stats lag up to 3 days.

## Guardrails
- Facts: one Tier 1 source (Deloitte, UEFA, FIFA, league or club official sites, BBC, Sky, The Athletic, Reuters, FT, SportBusiness, SportsPro, Sports Business Journal, Front Office Sports, Off The Pitch) or two independent ones. Cite on the slide or in the post.
- Criticise decisions, not people. Nothing on deaths, injuries, abuse, families. Legal cases, investigations, named-company disputes: `createScheduledPostForReview`, never auto-post.
- Images: actxion-slides output, or Wikimedia Commons free licences (CC0, PD, CC BY, CC BY-SA) with credit. Never agency photos, TV grabs, club/player-owned images, AI images of real people.
- No "comment YES", pods, bought followers, or identical team reshares.

## Desk rules (for the scheduling routines)
- **No repeat stories.** Before choosing a topic, read the text of every LinkedIn post in Metricool for the next 10 days (including drafts) and the last 30 days of published posts. Never pick a story, deal or headline number that is already queued or was posted in that window, even with a different angle.
- **Drafts don't block a slot.** A day whose only LinkedIn post is a draft counts as empty: schedule a fresh post and leave the draft alone.
- **Wikimedia rate limits (HTTP 429):** wait about 15 seconds and retry up to 3 times; search one name at a time.
- **Never commit `node_modules/` or `package-lock.json`.** They're in `.gitignore`.

