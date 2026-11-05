---
name: actxion-mic
description: THE MIC by ACTXION - an animated street-interview series. A branded ACTXION microphone (the camera) pushes into a crowd after a big game and five stylised, fictional fans answer one sharp question, voiced in ElevenLabs with accents that fit the fanbase, over a 3D street / pub / viewing-centre set made in Three.js and rendered with HyperFrames. 40-50 s, posted Tue/Thu/Sun 16:00 IST to Instagram, YouTube, TikTok and Facebook by a cloud routine. Use for planning, writing, voicing, building, rendering, posting or reviewing a THE MIC episode.
---

# THE MIC (cloud)

Separate from the daily video desk (skills/actxion-video) and ACTXION LAB (skills/actxion-lab): never edit those
skills, their routines or their slots. Approved by the owner on 5 Nov 2026 ("Build it": Tue/Thu/Sun at 16:00 IST,
full autopilot, never ask; retry busy tools on your own). The approved look and sound = `episodes/ep01`
("Carrick or the players?", street set). Copy that style; don't reinvent it.

## What an episode is
- 40-50 s, 1080x1920, 30 fps. The ACTXION mic is the camera's point of view, always in frame bottom right.
- Shape: cold open (a fan's best line) -> the MIC voice asks ONE question (question card) -> four more fans answer,
  whip-cut between them, a blame meter swings with each answer -> the MIC voice signs off with the A-or-B question ->
  end card "THE MIC / BY ACTXION / <which fanbase next>".
- The cast is 5 fictional characters from ONE fanbase: the angry one, the loyal one, the old head, the funny one, the
  one against everyone (the "third" option on the meter). Mix ages, genders, skin tones, and where they're from
  (locals + fans from Lagos, Nairobi, Accra, Mumbai, Jakarta: our audience). New clothes and accessories every time.
- Sets (`set` in episode.json): `street` (rainy terraces outside the ground, after a home game), `pub` (watch-party
  bar), `viewing` (viewing centre with benches and a big screen: Lagos / Nairobi style, after an away game or a game
  watched abroad). Pick the one that fits the story; don't use the same set three episodes running.

## Honesty rules (hard)
- The fans are fictional and clearly animated. Their OPINIONS must match what real fans said about this game this
  week (match reports, fan reaction pieces, club fan channels' public posts, read only). Paraphrase into the
  character's own words; never quote or name a real fan; never attribute words to a real player, manager or pundit.
- Any FACT a fan says (score, opponent, date, minute, a red card) must be true and in sources.txt. No invented stats.
- No real people's faces, no crests drawn on the characters (plain kit colours only), no match footage, no copyrighted
  music. Never sell the app in the episode: ACTXION is the name on the mic and the end card only.
- AI labels ON every post (the voices are synthetic): TikTok isAigc true, Instagram isAiGenerated true, YouTube
  isAiGeneratedContent true. YouTube description: "Characters are fictional; opinions reflect fan reaction reported
  this week. Voices: ElevenLabs."

## Build an episode (work dir /tmp/mic/<date>-<slug>)
0. `source skills/actxion-lab/cloud_setup.sh` (pip incl. faster-whisper, ffmpeg+ffprobe, Node 22, Chrome for HyperFrames).
1. Copy `skills/actxion-mic/engine/*` into the work dir.
   `npx -y hyperframes@0.9.15 init hf --example blank --resolution portrait --non-interactive --skip-skills`
   `mkdir -p hf/assets/lib && cp skills/actxion-lab/assets/lib/three.*.js hf/assets/lib/ && cp world.js hf/assets/`
   `python3 mic_kit.py hf/assets` (downloads the Mixkit effects; must print all ok).
2. **Story**: the biggest fan argument of the last 48 h (see the routine prompt). One question that splits a fanbase,
   two clear sides (meter left/right) and a third option the contrarian picks.
3. **Script** `script.tsv` (tab-separated: id, who, voice, text), 7 lines, 95-125 words in all:
   l1 = a fan's cold-open line (the hook: emotional, under 14 words, no context needed), l2 = MIC question (UK host,
   names the result in a few words, then "One question. <question>?"), l3-l6 = the other four fans (6-20 words each,
   one with a joke, one with "Neither..." style third option), l7 = MIC sign-off ("<A>, or <B>? You tell us.").
   ElevenLabs v4 direction tags in [brackets] at the start of a fan line ([angry, fast], [laughing], [tired, quiet]).
   Spoken English, contractions, numbers as words, UK spelling, no em dashes. Run
   `python3 /tmp/ig/skills/ig-human/detect.py` on the text without tags (short dialogue lines score low on
   "burstiness": that one flag is fine; fix anything else it flags).
4. **episode.json**: copy `episodes/ep01/episode.json` and change everything: set, club colours (hex), loc chip,
   question card, meter labels, ask card, keywords, and the 5 fans (label, sub, colours, acc, gesture, mood, pop,
   meter, caption colour). Kit: acc = cap, scarf, ponytail, hood, bucket, beanie, glasses (combine freely);
   gesture = pockets, jab, point, handsup, crossed, shrug, facepalm; mood = brows (-0.3 sad .. +0.45 angry);
   pop = the phrase where the gesture peaks ('Lagos#2' = 2nd time); meter = -1..1 or "third".
5. **Voice** (ElevenLabs; owner on a paid plan since 5 Nov 2026; credits shared with the desk and LAB):
   a. Budget: sum this calendar month's rows in `posts/elevenlabs-ledger.csv` on claude/posts (the one shared ledger;
      THE MIC rows have slugs starting `mic-`). THE MIC cap = 8,000 credits/month (~610 an episode; agreed split 5 Nov:
      LAB 14,000, LinkedIn 1,300, daily reel now Kokoro-only). If THE MIC month total + 700 would pass 8,000, OR the
      whole file's month total + 700 would pass 28,500 (95 % of the 30k plan), use `eleven_flash_v2_5` for the fans
      (about half the cost); if even that would pass 28,500, Kokoro for every line. Say which in the report.
   b. For each line: `creative_generate_speech` (model eleven_v4, the line's voice_id, generations_count 1, prompt = the
      text with its tags). Then `creative_get_generations` and curl `full_res_url` to voice/<id>.mp3. ONE call per line:
      never re-call a line that started (each call charges). If it says "busy" (nothing charged), wait 60-90 s
      (`sleep 75`) and try that line again, up to 6 times. If a line still fails, Kokoro for that line only:
      `python3 skills/actxion-lab/engine/voice.py voice/<id>.txt voice/<id>-kokoro.wav --voice <bm_george|bf_emma|...>`.
   c. Append one row per generation to posts/elevenlabs-ledger.csv: `<date>,mic-<slug>-<id>,<model>,<credits>`
      (credits = the `credit_costs` value the tool returned).
   d. `python3 lines.py` (trims, levels each line to -16 LUFS, word times via faster-whisper, script spelling laid over).
6. `python3 build.py`, `npx -y hyperframes@0.9.15 check --json` (fix errors), then
   `npx -y hyperframes@0.9.15 snapshot --at <one time inside every line + the question card + the ask>` and LOOK at every
   frame: each fan's face visible and not under the meter or a label, caption on the chest not the face, the mic in the
   corner, the gesture firing on its word, no crowd figure blocking the speaker. Fix and re-snapshot.
7. Render: `npx -y hyperframes@0.9.15 render --no-browser-gpu --workers 3 --protocol-timeout 600000` (re-run with
   `--workers 1` if it fails), then `python3 mix.py hf/renders/<newest>.mp4 out.mp4` (aim -14 to -15 LUFS, peak under
   -1 dB). Cover = frame at 1.0 s. Look at 4 frames of the final file.

## Voices (ElevenLabs voice_ids; the MIC host is fixed, fans change)
| Role | Voice | id |
|---|---|---|
| THE MIC host (every episode) | Mia Moore, young British female | ZtcPZrt9K4w8e1OB9M6w |
| Manchester / Northern woman | Maria | RU8huomG1ebFQW6nNko3 |
| Older English man | Peter Alec Underwood | ItluBpGWT7OvTHpsgTJY |
| Deep middle-aged English man | Narrator Rob | N3KdYXuAuQCEeNRC4lXJ |
| Young London man (cockney) | Harry | kOVqQImaJYcrUxZmjqgl |
| Young Black London man | Prince | nstAjY74EkciBLEg9uvD |
| London bloke | Vinnie | TjO2L33VfWYPVuCxsbC4 |
| Young Nigerian man (storyteller) | Terna Gabriel | bHclEKSjOa1XXz9wbyW6 |
| Young Nigerian man (calm) | Oluwadamilare | VzScgb5Pi0A6lafMNQpm |
| Mature Nigerian man | RemJac | uJr8JoCxdxv815lCABau |
| Kenyan man | Keith | uLfPT2jUO3X81OwnftBP |
| Posh young English woman | Alexandra | m0MqfGOWTAfVVEaz4KxX |
Need another accent (Indian English, Ghanaian, Indonesian English, a Scouse or Geordie fan, an African woman)?
`creative_list_voices` with languages ["en"] + accent/gender/age filters, pick one, add it to this table. Never use
Petros (the desk's voice), Daniel (the LAB's voice) or any voice cloned from a real person.

## Post (4 networks, Metricool blogId "4945970", timezone Asia/Kolkata)
Publish: copy out.mp4 + cover + script.tsv + episode.json + sources.txt to `posts/<date>/mic-<slug>.*` on claude/posts,
commit, push, then check `https://raw.githubusercontent.com/pvtaddyy/actxion-assets/claude/posts/posts/<date>/mic-<slug>.mp4`
returns 200. One createScheduledPost per network (autoPublish true, draft false, descendants [], shortener false,
smartLinkData {"ids": []}, hasNotReadNotes false, media [mp4 url]):
- **Instagram Reel**: instagramData {"type":"REEL","showReelOnFeed":true,"isAiGenerated":true}, videoThumbnailUrl = cover.
  Caption (actxion-instagram rules): first line = the question; 2-4 short lines naming the club, the result and the
  sides; "Comment A or B"-style single ask; 3 hashtags. firstCommentText = a second, related question (never credits).
- **YouTube Short**: title under 60 chars, the question + club name, ends #shorts. Description: 2 lines on the game,
  "Pick your side in the comments", the honesty line above, sources, "Sound: Mixkit", "Vote on every big call in the
  ACTXION app". 5-12 tags. youtubeData {"type":"short","privacy":"public","madeForKids":false,"category":"SPORTS","isAiGeneratedContent":true}.
- **TikTok**: hook line + the A-or-B ask + 3-4 hashtags. tiktokData {"privacyOption":"PUBLIC_TO_EVERYONE","isAigc":true,"autoAddMusic":false,"title":"<question>"}.
- **Facebook Reel**: providers [{"network":"facebook"}], facebookData {"type":"REEL"}. African Premier League fans: name
  clubs and players plainly. Hook line, 1-2 lines of context, ONE open question asking for a reason ("...and why?").
  Never "comment A or B", "tag a mate", "share if". 0-2 hashtags. firstCommentText "Bonus round: <follow-up question>".
- Time: 16:00 IST. Look at getScheduledPosts first; if the same network has a post within 45 min (Facebook 60), use the
  nearest clear time 15:30-16:45. Never two MIC episodes in a day. All copy: UK spelling, no em dashes, nothing that
  reads AI-written (ig-human detect on the IG caption).

## Learn (weekly)
State on claude/posts: `mic/rotation.md` (next episodes + results log), `mic/learnings.md` (rules that numbers proved),
`mic/episodes/<date>-<slug>/`. Monday review: per episode Instagram views + average watch, YouTube views, TikTok views,
Facebook views, comments; compare sets, clubs, cold-open types and length; change ONE thing a week; write it down.

## Never
Match footage, TV clips, other creators' videos, copyrighted music, AI images or video of real people, a cloned real
voice, invented facts, quotes put in real people's mouths, selling the app inside the episode, automated likes, follows,
comments or DMs, the sounds cinematic-cine-hit / cinematic-film-flash, any API key written anywhere.
