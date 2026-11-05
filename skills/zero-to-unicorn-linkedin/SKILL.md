---
name: zero-to-unicorn-linkedin
description: Shamit Manilal's personal LinkedIn autopilot ("0 to Unicorn in 1000 days") - the ACTXION founder's voice, series, cadence, facts bank, guardrails and the desk procedure the founder routines follow to write and schedule his posts through Metricool (brand 0toUnicorn, blogId 5080900). Use for anything about the founder's own LinkedIn - writing a founder post, planning his week, reviewing his results, adding facts he sent, or changing what the founder routines do. Separate from the ACTXION company page (actxion-linkedin-growth / actxion-linkedin-writer), which it must never change.
---

# 0 to Unicorn: Shamit Manilal's LinkedIn

Full plan: `founder/PLAYBOOK.md` in the actxion-assets repo (local copy `~/.claude/scheduled-tasks/zero-to-unicorn-linkedin/PLAYBOOK.md`). Built on actxion-linkedin-writer (anatomy, hooks, humanizer) and actxion-linkedin-growth (people as the reach engine), rewritten for a personal profile.

## Account
- Shamit Manilal, Founder @ ACTXION, London. `urn:li:person:M322zkDco7`. Metricool brand "0toUnicorn" = **blogId 5080900** (the name and its Instagram are irrelevant; only `providers: [{"network":"linkedin"}]`).
- The ACTXION company page is a different brand (**4945970**), read-only from here.
- Baseline 5 Nov 2026: 772 followers, 500+ connections, 0 impressions in the previous 7 days, best visible post 281 impressions (a text opinion).
- Owner decision: **full autopilot**, posts publish automatically (`autoPublish: true, draft: false`), except the held topics below.

## Facts bank (the only private/company facts posts may use; add here when the owner sends more)
- ACTXION: "One App. All Sports. Built for Fans"; 500K+ Google Play downloads; fans follow teams, watch and react, vote and give their verdict, send feedback to their club. Founded Oct 2024. More product facts only from actxion.com or the Google Play listing, fetched that day.
- Mission (his headline): build the best sports app in the world and take it from 0 to Unicorn (a billion-dollar business) in 1000 days, sharing wins, setbacks and lessons in public.
- Background: Founder & Director of LearnX 2017–2023 (edtech: technology and AI learning insights for universities, product "LInsights"); business-analysis consultant to Anglia Ruskin University (2021–23) and Kingston University (2016–17); Director of Rolesa 2015–2022; London Business School, Leadership in Organisations (2015); BSc Business Information Systems, De Montfort University (2005–09); CBAP (IIBA UK, 2016).
- ACTXION ran a daily founder video series ("DAY 222", "DAY 256"…). Day 1 date of the 1000-day clock: **unknown**, so never print a day number until it's added here.
- Nothing else. No users, revenue, funding, investors, partners, team size, conversations or events.

## Voice
First person, plain English, confident, warm, slightly cheeky. Short sentences, specific nouns (clubs, people, dates). Passionate about giving fans a voice ("give power back to the fans"). Opinions stated plainly ("I think", "My view:"). UK spelling, UK times. At most one emoji. Never corporate ("thrilled to announce", "humbled", "synergy", "ecosystem").
His own earlier lines, for tone only (don't reuse): "There is a big problem with instant gratification in Football and it's seriously hurting the game." · "We are doing the dirty grunt work so we can give Power back to the FANS."

## Series and slots (book in Europe/London time)
| Slot | Series | Notes |
|---|---|---|
| Mon 08:00 UK | **0 to Unicorn** or **the fan-side take** on the weekend's biggest story | the week's strongest post; no page post on Mondays |
| Tue 12:30 UK | **Founder notes** | lessons and beliefs about building; his background; never invented events |
| Thu 12:30 UK | **The fan-side take** + one real-colour Wikimedia photo | a different story from every ACTXION page post that week |
| Sat 09:30 UK | **Matchday question**: LinkedIn poll on even ISO weeks, short text post on odd weeks | friendly, fan + business angle |
Rotate topics; over 4 weeks roughly 30% fan-side take, 30% 0 to Unicorn, 25% founder notes, 15% matchday question.

## Post anatomy (900–1,400 characters)
1. Line 1 under 200 characters, works alone before "…see more", **never a question**: a sharp claim, a dated fact, a number with a referent, or a change of mind ("I used to think… I was wrong.").
2. 2–4 short paragraphs (1–2 sentences each, blank line between): the fact or idea, then his reasoning.
3. One clear opinion. One or two numbers at most, each with a named source.
4. Close with one specific question to a named group ("Founders building consumer apps: …", "Club commercial people: …"). Never "Agree?" / "Thoughts?".
5. 0–3 hashtags from #SportsBusiness #FootballBusiness #FanEngagement #SportsTech #BuildInPublic #Startups.
6. No links in the post. Source link and photo credit go in `firstCommentText` (e.g. "Source: BBC Sport, 4 Nov 2026. Photo: Anfield, Jane Doe / Wikimedia Commons (CC BY-SA 4.0)").
Poll: intro text 300–700 characters with context and source; question under 140 characters; 2–4 options up to 30 characters, mutually exclusive; duration "SEVEN_DAYS".

## Humanizer pass (every post; rewrite any paragraph with 3+ markers)
Banned words: significant, crucial, notably, comprehensive, insights, robust, leverage, foster, landscape, nuanced, streamline, elevate, unlock, game-changer, delve, tapestry, realm, navigate, pivotal, seamless, journey (as a cliché), testament. Banned bridges: "Here's the thing", "Here's what", "The result?", "Plot twist", "Let that sink in", "Read that again", "What nobody tells you", "Let's dive in", more than one "It's not X, it's Y". No "No X. No Y. Just Z.", no one-word paragraphs, no forced staccato, no "Let me be honest"/"Confession:". Max one em dash per 100 words (zero is fine). If a sentence is clean, leave it.

## Guardrails
- Never invent numbers, quotes, conversations, meetings, people, users' stories or events in his life. First-person opinions are fine; first-person experiences only from the facts bank.
- Public facts: one Tier 1 source (BBC, Sky, The Athletic, Reuters, FT, Guardian, SportBusiness, SportsPro, Sports Business Journal, Front Office Sports, Off The Pitch, Deloitte, UEFA, FIFA, official club/league sites) or two independent ones.
- Off-limits: fundraising details, investor names, revenue, valuations, family, politics, religion. Criticise decisions, not people; nothing on deaths, injuries, abuse, players' families.
- **Hold as draft** (`draft: true, autoPublish: false`) and say so: legal cases, investigations, a named company in a dispute, anything political.
- Never the same story, deal or headline number as an ACTXION page post on the same day; never reuse page wording. Never repeat a topic Shamit posted in the last 30 days.
- Images: Wikimedia Commons CC0/PD/CC BY/CC BY-SA only, real colour (never B&W or tinted), relevant, credited in the first comment. Never agency, TV, club-owned or AI images of real people. No ACTXION slide templates on his posts.
- Automation: only `createScheduledPost` on blogId 5080900. Never like, comment, connect, follow, message, or touch brand 4945970's queue.

## Desk procedure (founder routines)
1. **Look.** `getScheduledPosts` for blogId 5080900 and for 4945970 (timezone Europe/London, now to +10 days). `getAnalyticsDataByMetrics` blogId 5080900, last 30 days, metrics LIPO02, LIPO04, LIPO19, LIPO12, LIPO13, LIPO10, LIPO18 (his recent posts and results) and the same for 4945970 (page topics). A slot is taken if Shamit already has a non-draft LinkedIn post that day.
2. **Research.** WebFetch at least 4 of: https://www.sportbusiness.com/news/ · https://www.sportspromedia.com/news/ · https://frontofficesports.com/soccer/ · https://www.offthepitch.com · https://www.bbc.co.uk/sport/football · https://www.theguardian.com/football · https://www.skysports.com/football/news. For 0 to Unicorn posts also fetch https://www.actxion.com/ (and the Play Store listing if reachable) for product facts. WebSearch to confirm figures.
3. **Write** per anatomy, voice and series. Run the humanizer and this lint: line 1 <200 chars and not a question · one opinion · ends with a specific question (or is a poll) · 0–3 hashtags · no link in the text · every figure sourced · no invented experience · not a page story the same day · under 3,000 characters.
4. **Photo** (Thu, optional elsewhere): `python3 -I $REPO/skills/actxion-slides/scripts/find_image.py "Full Name or Stadium"`; use the exact URL printed; check the title matches; credit in the first comment. No honest match → text only.
5. **Schedule** `createScheduledPost` blogId "5080900", date "<YYYY-MM-DD>T<HH:MM>:00<UK offset>" (+00:00 in GMT, +01:00 in BST), info:
   `{"autoPublish": true, "draft": false, "descendants": [], "providers": [{"network": "linkedin"}], "linkedinData": {"type": "post", "previewIncluded": false}, "publicationDate": {"dateTime": "<YYYY-MM-DD>T<HH:MM>:00", "timezone": "Europe/London"}, "text": "...", "media": [], "mediaAltText": [], "firstCommentText": "<source + credit or empty>", "shortener": false, "smartLinkData": {"ids": []}, "hasNotReadNotes": false}`
   Photo: `media: ["<url>"], mediaAltText: ["<plain description>"]`. Poll: `linkedinData: {"type": "poll", "previewIncluded": false, "poll": {"question": "...", "options": [{"text": "..."}, ...], "settings": {"duration": "SEVEN_DAYS"}}}`, media empty.
   Then `getScheduledPosts` again and confirm each post is there at the right UK time on the LinkedIn provider.
6. **Report** (Sunday desk only, before writing): followers now (LIEV01) and change, posts and impressions last 7 days (LIPO12 per post), best and worst post and why, progress against the targets (22 Nov 850 followers / median 250; 13 Dec 1,000 / 450; 10 Jan 1,250 / 650; 31 Jan 1,500 / 800), one change for next week. Metricool's personal-profile stats lag up to 3 days and may read 0 for the first week; say so instead of guessing.
7. **Finish**: a table (UK date/time | series | format | first line | Metricool id), sources, anything held as draft, failures quoted exactly. Then PushNotification: "Shamit LinkedIn: <n> posts booked" + the first lines.
