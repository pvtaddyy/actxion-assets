---
name: actxion-growth
description: How ACTXION grows on X from a small account. Covers the football "fan verdict" niche, how the 2026 X ranking system actually scores posts (from xai-org/x-algorithm), which post formats and times to use, how to write copy that doesn't read as AI, the reply engine, and the weekly learning loop. Use for anything about ACTXION's X account: writing or scheduling posts, planning the day or week, reviewing what worked, fixing low reach, reply packs, or deciding what the autopilot routines should do. Pairs with actxion-visuals for the image on each post.
---

# ACTXION growth on X

ACTXION is a football fan app (500K+ downloads) with a small X account, @ACTXIONAPP. The goal is reach and followers from millions of football fans, through one niche: **football's fan verdict**. Every controversy, rumour and big moment becomes a question fans argue about.

## How X decides who sees a post (2026)

From the open-source ranking code at github.com/xai-org/x-algorithm (README updated October 2026). Base decisions on this, not on old "hacks":

- **Score = sum of predicted actions times weights.** X predicts, per viewer, the chance they'll like, reply, repost, quote, share (including by DM or copied link), click, expand the photo, watch the video, dwell, and follow the author. It also predicts the negatives: "not interested", mute, block, report, and **"not dwelled"** (scrolling straight past). Negatives carry negative weight.
- **Time spent counts more than it used to.** The October 2026 update trained ranking to predict dwell time better, and retrieval to surface posts people read all the way through. Posts worth stopping on beat posts built to be glanced at. A strong image plus a few lines of real substance is the target.
- **Author diversity decay.** Each extra post from the same author in a viewer's feed is scored lower. Twenty-five near-identical posts a day don't add up to 25 times the reach. Spacing them and varying the formats matters.
- **New-author boost.** Accounts with low impressions get lifted toward a target position. A small account is not invisible, but it has to convert that chance with engagement.
- **Out-of-network discount**, and the `OONRetweetReplyFilter`: replies and reposts from accounts a viewer doesn't follow are filtered out of For You. So replies to big accounts grow the account through the **conversation itself** (people reading the thread and tapping the profile), not through feeds.
- **48-hour age filter.** A post's feed life is two days. Old news is dead, and reacting fast is worth a lot.
- **Account reputation.** `user-cred-v2` runs PageRank over follows and engagement, and `agatha` labels accounts by how often people block or report them relative to likes. Rage-bait that earns blocks costs reputation, so argue about the football, never attack people.

What this means in practice: post varied posts at the right moments, each worth stopping on. Make every post worth stopping on. Trigger replies with real debates. Build the reply engine. Avoid anything that gets muted or reported.

## The niche and voice

The voice is a sharp, funny, fair fan who knows the game: never a press release, never a troll.

**Rhythm:** write like a person, not a template. Mix one punchy line with a two-sentence paragraph. Don't put every sentence on its own line: that "broetry" pattern is now an instant AI tell.

**Avoid these tells** (adapted from coreyhaines31/marketingskills and avoid-ai-writing):
- "It's not X, it's Y" contrasts.
- Colon reveals ("The twist:"), and self-answered questions ("The result? Chaos.").
- Stock phrases ("Say goodbye to", "Here's the thing", "Let that sink in").
- Bait endings ("Thoughts?", "Agree?").
- Em dashes, emoji used as bullets, and a hashtag pile-up.

**Ending:** a real either/or question fans can answer in one word, or a "Fan verdict:" question. Use at most one or two hashtags, and only match tags (#MUNROM) or competition tags (#UCL) on match nights.

**Times in posts and on images are UK time**, never IST. Write kick-offs as "8pm UK" (GMT in winter, BST from the last Sunday of March to the last Sunday of October; convert with `TZ=Europe/London date`). The audience is mostly UK and European fans. Scheduling in Metricool still uses Asia/Kolkata, which is only the account's clock and never appears in the copy.

**Facts:** never invent a quote, score, stat or fee. Rumours always name the source and its tier (Tier 1: BBC, Sky Sports, The Athletic, Fabrizio Romano, David Ornstein; Tier 2: national papers; Tier 3: tabloids and aggregators).

**Taste:** never mock deaths, serious injuries, racism victims or players' families. Criminal or abuse allegations go to review, never to autopost.

## Formats (each pairs with an actxion-visuals template)

| Format | When | Image template |
|---|---|---|
| Fan verdict debate | Any controversy with two clear sides | `ballot` (with both people's photos when it is person v person) |
| Full-time verdict | Within 30 min of a big final whistle | `scoreboard` with the match winner or the manager under pressure |
| Back-page story | Manager pressure, records, the big story of the day | `backpage` with a halftone photo |
| Rumour desk | Transfer or manager rumours | `rumour` with the tier stamp |
| Quote of the day | A manager or player outburst | `redcard` with the speaker's photo |
| One person, one big story | Pressure, a record, a return, a sacking watch | `poster` |
| Quote post | An official club or reporter post is the news | No image; the quoted post's media shows |
| Crossover / personality story | Celebrity, viral fan, player humour | `backpage` |

Rotate templates so no two consecutive posts use the same one.

## Volume and timing

- **Volume (owner's call, 4 Nov 2026, evening):** every news desk posts **6**. This line overrides the number in each routine's prompt. Night owl, overnight, midday, afternoon, prime-time and late: 6 each, never fewer than 5. On big match nights the afternoon, prime-time and late desks may go to 8. The full-time desk adds 3 to 6. That's about 40 a day.
- **When the news runs dry, don't stop at 3.** Use the format bank below to reach 6. A bank post is still a real post with a real fact in it, never filler:
  1. **Pick your side:** two players, managers or clubs in tonight's or the weekend's news, on a `ballot` card. Example: "Saka or Palmer: who would you rather have for the run-in?"
  2. **Prediction:** "Call the score: Porto v Napoli, 8pm UK", on a `scoreboard` with "?" scores. Use it for any big game within 12 hours.
  3. **Stat-led debate:** one hard stat from Opta, FBref or the BBC with a question. Example: "Haaland 13 goals, City's other forwards 4. Problem or fine?"
  4. **Rumour round-up:** the morning papers' best Tier 2 or Tier 3 story, on a `rumour` card with its tier.
  5. **On this day:** a famous match, goal or row from the same date in an earlier year, checked on Wikipedia or the BBC.
  6. **Pressure ranking:** "Which manager is next out?", with four names and the reason for each.
- **Watch the count:** X's author-diversity decay means each extra post in a viewer's feed scores lower, and 40 a day is the most this account should test. The daily review compares reach per post on 6-a-desk days with the earlier 3-to-5 days. If reach per post falls by more than a third and total daily impressions don't rise, recommend going back to 5.
- **Audience:** mostly UK and European fans, with big pockets in Nigeria, India and the US. In IST: UK lunchtime is 17:00 to 19:30, UK evening is 23:00 to 03:30, and Champions League full time is around 03:15 to 03:45. Weekend Premier League full times are about 21:20, 23:50 and 02:20.
- **Spacing:** at least 20 minutes between posts, except straight after full time, where 15 minutes is fine.

## Experiments running (from 5 Nov 2026)

Every desk tags each post with its variant in `posts/experiments.csv` on the claude/posts branch. The columns are `date,ist_time,desk,experiment,variant,first_line`; append a row per post and commit it with the images. The daily review reads it, waits for the stats (which lag about 3 days), and reports which variant wins on impressions, replies and follows. One winner a week becomes the default, and a new test takes its place.

1. **E1 short vs long copy.** Alternate within each desk. Variant `short` is one line of story, one line of fact and the either/or question, under 230 characters in all. Variant `long` is the current 3-to-4-paragraph style. Long reads well, but most small accounts win with short copy plus a strong image.
2. **E2 quote the source.** When a Tier 1 account (Fabrizio Romano, David Ornstein, Sky Sports News, BBC Sport, the club itself) posts the breaking news, the desk makes its post a quote of that post: our verdict line and question on top, and their x.com status URL on the last line of the text. Use no image of our own; the quoted post's media shows. Variant `quote` vs `image`, at most 2 per desk. A quote shows up in the original post's quotes list, where that account's fans are already reading.
3. **E3 video on X.** The daily "Pick your side in 30 seconds" video from actxion-video also goes to X at peak time (17:30 to 19:30 or 23:00 to 01:00 IST), uploaded as native video. So far on this account, video posts reach about three times what image posts do. The video routine (trig_01BbWXLmaTUyqeFS6SAHCc7Q) owns this. It posts the X video at 18:20 IST, or at 21:40 IST when its run starts late. **Desks never schedule an X post between 18:00 and 18:40 IST or between 21:15 and 22:00 IST**; move a post that lands there to just outside the window. The video run logs its own `video,E3,video` row in experiments.csv.

The daily review judges each test on per-post medians, not totals, and never on fewer than 10 posts per variant.

## The reply engine (the main growth lever for a small account)

Replies earn profile visits from people reading big accounts' threads. Draft replies for the owner to post by hand. Never automate likes, follows, replies or DMs: X suspends accounts for it, and the reputation models above punish it.

- **Targets:** Fabrizio Romano, David Ornstein, The Athletic, Sky Sports News, BBC Sport, Squawka, Opta, Troll Football, 433, Footy Humour, ESPN FC, and the big clubs.
- **Timing:** reply within 30 minutes of their post. A reply has to add something: a stat, a sharp take or a joke, under 200 characters, with no links.
- **Volume:** 10 to 15 replies a session, two or three sessions a day.

## Learning loop

- **Daily:** read the per-post stats in Metricool (they lag by about 3 days) and the daily follower count. Note the best and worst 3 posts and why.
- **Weekly:** compare formats, templates, hours, photo vs quote vs text-only, and hashtags vs none. Drop a format that stays below the account median for two weeks. Run two experiments a week.
- **Targets:** 150 followers by 16 Nov 2026, 750 by 2 Dec, 3,000 by 1 Jan 2027 and 8,000 by 31 Jan 2027. If the 16 Nov checkpoint misses by more than half, change the strategy, not just the volume.

## Copyright watch

Since 4 Nov 2026 the desks use the news article's own photo (often Getty, PA or club) on purpose, by the owner's decision. Watch for the cost every day:
- In Metricool, any X post that failed to publish, or whose status or media changed after publishing.
- Followers or impressions suddenly dropping to near zero, or posts not appearing in search (a sign of a restriction).
- Anything the owner reports from X notifications: "media disabled in response to a report by the copyright owner", a DMCA notice, or a strike.

On the first sign, say so at the top of the daily review and in a phone notification, list the post and the photo source, and recommend: stop article photos from that agency, keep free photos and quote posts, and review after a week. Don't change the policy alone: the owner decides.

## Off-X levers that beat any posting tactic

ACTXION's 500K app users are the fastest route to followers: an in-app banner, a push notification on match nights, and the X handle in Instagram, TikTok and Facebook bios and captions. Mention it in every review until it's done.
