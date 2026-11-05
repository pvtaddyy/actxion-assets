---
name: actxion-lab
description: ACTXION LAB - the animated football series (Myth or Fact?, Race Day, Sounds Fake, Head to Head, The Table, What If?, Replay), 45-90 s of 3D + motion graphics made in code, separate from the daily actxion-video desk. Floodlit Three.js stadium, faceless stylised players in real kit colours, every number as a physical object, real club crests, word-lit captions, Kokoro voice, crisp Mixkit sound, rendered with HyperFrames; posted Mon/Wed/Sat 16:00 IST to Instagram, YouTube, TikTok and Facebook by cloud routines. Use for planning, building, rendering, posting or reviewing an ACTXION LAB episode.
---

# ACTXION LAB (cloud)

Separate from the daily video desk: never edit skills/actxion-video, its routines, or its slots (IG/YT/TikTok 19:00,
X 18:20, Facebook 21:30 IST). Owner decisions (5 Nov 2026): any look that works, real club crests OK, highly animated,
full autopilot. **House style = EP 01 v3** ("Myth or Fact? EP 01: Haaland v the Big Six", posted Sat 7 Nov 16:00 IST):
copy its look, captions and sound; don't reinvent them. Worked example: `episodes/ep01/` (script, words, facts TSV,
sources, captions) and the video at
https://raw.githubusercontent.com/pvtaddyy/actxion-assets/claude/posts/posts/2026-11-07/lab-myth-or-fact-ep01-haaland.mp4

Code lives here on `main` (skills/actxion-lab). State lives on `claude/posts`: `lab/rotation.md` (what is due),
`lab/learnings.md` (what works; read it before planning), `lab/reports/`, and the episode files in `posts/<date>/lab-<slug>.*`.

## Segments
Myth or Fact? (claim -> Round 1 -> Round 2 -> twist -> verdict) / Race Day (3D figures racing or side by side) /
Sounds Fake (one record rebuilt object by object) / Head to Head (two players, you pick) / The Table (league table race) /
What If? (one rule changed, season recomputed from real results) / Replay (a weekend moment on a 3D tactics board).
Ending: an A or B question on screen + "Which one do we test next?" + end card "<SEGMENT> / BY ACTXION /
Comment the next one we should test". Never name a weekday on screen.

## Facts (hard rule)
Every number on screen comes from a named public page (saved in sources.txt) and is computed from a table you saved (TSV).
Use WebFetch / WebSearch (Bash network may be blocked for news sites): statmuse.com/fc, premierleague.com, BBC/Sky/ESPN
reports, Wikipedia record pages, football-data.co.uk CSVs. Never get round a bot check. No source = drop the number or the topic.

## Build an episode (work dir /tmp/lab/<date>-<slug>)
0. `source skills/actxion-lab/cloud_setup.sh` (pip, ffmpeg+ffprobe, Node 22, Chrome for HyperFrames; prints timings).
1. `cp skills/actxion-lab/engine/* /tmp/lab/<dir>/`, `cd` there,
   `npx -y hyperframes@0.9.15 init hf --example blank --resolution portrait --non-interactive --skip-skills`,
   `mkdir -p hf/assets/lib hf/assets/crests assets && cp ../../<repo>/skills/actxion-lab/assets/lib/* hf/assets/lib/ && cp world.js hf/assets/`,
   crests: `skills/actxion-lab/assets/crests/<code>.png` (ars avl bou che cry liv mci mun new pl tot whu wol) into BOTH
   `hf/assets/crests/` and `assets/`. A club not there: try the repo's `photos/crests/`, else fetch its Wikipedia
   thumbnail with WebFetch-found URL via curl; if blocked, show the club name in its colours instead of a crest.
   Sound + music: `python3 lab_kit.py hf/assets` (downloads Mixkit each run; must print all ok).
2. **Hooks**: 3 of different types, score with the ig-reel hookscore (`git clone -q --depth 1 https://github.com/Jakeschincariol/instagram-agent-skill /tmp/ig`;
   `python3 /tmp/ig/skills/ig-reel/hookscore.py hooks.txt`), keep the best (aim 70+).
3. **Script**: 180-230 words (60-75 s), numbers as words, one line per beat, an early context line (player, club,
   competition, time span). `python3 /tmp/ig/skills/ig-human/detect.py script.txt` must PASS (club names flagged as slop
   are false positives). No em dashes.
4. **Voice + timings**: `python3 voice_lines.py script.txt hf/assets/voice.wav words.json --voice bm_fable --speed 1.16`
   (Kokoro, one line at a time, faster-whisper word times; numbers matched as words).
5. **Scenes**: edit build.py (beats via `at()`, EP data, cams, overlays incl. the context chip and 'Data: <source>',
   DIGITS table, HIDE windows, SFX list) and world.js scene blocks. Reuse EP 01 parts: hero figure (kit colours + number),
   ball rain/pile, glass tubes, goal grid, 3D pillars, crest sprites, mystery shield, blackout + spotlight. A new segment
   gets a new physical metaphor (Race Day: figures sprinting down lanes with a km/h readout; The Table: 3D blocks
   stacking per matchday; What If?: the table re-sorting). One idea on screen at a time; a new visual every 2-4 s.
6. `python3 build.py`; `npx -y hyperframes@0.9.15 check --json` (fix errors); `npx -y hyperframes@0.9.15 snapshot --at <every beat>`
   and LOOK at the contact sheets: no text over text, crests clear of labels, figure not behind captions, nothing
   important below y 1330. Fix and re-snapshot.
7. `npx -y hyperframes@0.9.15 render --no-browser-gpu` (software WebGL in the cloud; if it times out add
   `--workers 2 --protocol-timeout 600000`), then `python3 mix.py hf/renders/<newest>.mp4 out.mp4`: it prints the levels;
   aim -14 to -15 LUFS, peak under -1. Cover = `ffmpeg -ss 1.0 -i out.mp4 -frames:v 1 -q:v 2 cover.jpg`.
   Pull 4 frames from out.mp4 and look at them before posting.

## Sound (approved v3)
mix.py: voice levelled once to -16 LUFS; SFX crisp and untouched, one on every graphic; no music under the voice, music
only as moments (risers into rounds, 3 s over the end card); no compressor, no ducking. **Never** cinematic-cine-hit or
cinematic-film-flash (crackly static). lab_kit.py fetches only the approved kit.

## Captions (approved v3)
One centred line at y 1150, 1-3 words, never ending on a weak word, pairs kept, numbers as digits, words light grey -> white
as spoken, numbers + key words gold, Inter Black 74 px with a dark stroke, hidden while a headline says the same words.

## Publish + post (Metricool blogId "4945970", timezone Asia/Kolkata)
On the claude/posts checkout: copy out.mp4 -> `posts/<YYYY-MM-DD>/lab-<slug>.mp4`, cover -> `lab-<slug>-cover.jpg`,
script/sources -> `lab-<slug>-script.txt` / `-sources.txt`; `git add posts && git commit -qm "lab: <slug>" &&
git pull -q --rebase origin claude/posts && git push -q origin claude/posts`; poll
`https://raw.githubusercontent.com/pvtaddyy/actxion-assets/claude/posts/posts/<date>/lab-<slug>.mp4` until HTTP 200.
Then one createScheduledPost per network (autoPublish true, draft false, descendants [], shortener false,
smartLinkData {"ids": []}, hasNotReadNotes false, media [mp4 url], publicationDate {dateTime, timezone "Asia/Kolkata"}):
- **Instagram Reel**: instagramData {"type":"REEL","showReelOnFeed":true,"isAiGenerated":false}, videoThumbnailUrl = cover URL.
  Caption: first line = the question, 3-5 short lines with names and key numbers, one ask, 3 hashtags. firstCommentText =
  a second related pick-your-side question (never credits). Run ig-human detect on it.
- **YouTube Short**: youtubeData {"title": <under 60 chars, ends #shorts>, "type":"short","privacy":"public","tags":[5-12],
  "category":"SPORTS","madeForKids":false,"isAiGeneratedContent":false}; text = 2 search lines, "Pick your side in the
  comments", sources, "Crests belong to their clubs. Voice: Kokoro-82M (Apache 2.0). Music and sound: Mixkit.",
  "Vote on every big call in the ACTXION app".
- **TikTok**: hook line + the A or B ask + 3-4 hashtags; tiktokData {"privacyOption":"PUBLIC_TO_EVERYONE","isAigc":true,"autoAddMusic":false,"title":"<question>"}.
- **Facebook Reel**: providers [{"network":"facebook"}], facebookData {"type":"REEL"}; African Premier League fans: name
  players and clubs plainly; hook, 1-2 lines of context, ONE open question asking why; never "comment A or B", "tag a mate",
  "share if"; 0-2 hashtags; firstCommentText "Bonus round: <follow-up question>".
- Time 16:00 IST; check getScheduledPosts first: if a post on the same network is within 45 min (Facebook 60), use the
  nearest clear time 15:30-16:45. Never two LAB episodes in a day. UK spelling, no em dashes, nothing AI-sounding.

## Analytics (Metricool getAnalyticsDataByMetrics)
IG reels IGRE02 date, IGRE03 text, IGRE06 url, IGRE23 views, IGRE11 reach, IGRE24 avg watch, IGRE27 retention, IGRE28 3 s
view rate, IGRE21 shares, IGRE12 saves, IGRE07 comments. FB reels FBRE02, FBRE05, FBRE06, FBRE10 views, FBRE11 reach,
FBRE13 avg watched, FBRE07 actions. TikTok TKPO02, TKPO05, TKPO03, TKPO07 views, TKPO15 avg time, TKPO13 full watch,
TKPO10 shares, TKPO09 comments, TKPO16 For You. YouTube YTVP02, YTVP17, YTVP05, YTVP06 views, YTVP08 avg duration,
YTVP12 shares, YTVP11 comments. Baselines: desk reels (~19:00 IST) and combined XI reels ("player by player"); use medians.

## Never
Match footage, TV clips, other creators' videos, copyrighted music, AI images or video of real people, a cloned voice,
invented numbers, automated likes/follows/comments/DMs.
