---
name: actxion-video
description: ACTXION's short-video engine for Instagram Reels, YouTube Shorts, TikTok and X - football "pick your side" debates told with a narrated voice (Kokoro, or ElevenLabs on a paid plan), word-by-word captions, real player cut-outs with text behind them, animated scoreboards, stat counters, head-to-head bars and 3D pitches, rendered frame by frame to a 1080x1920 MP4. Covers the series, hooks (Hook Code), the 5-pass edit (reel-edit), sound, packaging per platform and posting through Metricool. Use when planning, scripting, voicing, editing, rendering, captioning, posting or reviewing any ACTXION video.
---

# ACTXION video engine

One vertical master file (1080x1920, 30 fps, H.264, AAC, -14 LUFS) goes to Instagram Reels, YouTube
Shorts, TikTok and X, each with its own text. Everything is made in code from scratch: our research,
our script, our voice, our graphics. No match footage, no TV clips, no copyrighted music, no AI
images or AI video of real people, no cloned real voice.

Built from: the Hook Code and the 5-pass reel edit (upscalecreativeclub.com/hook-code, /reel-edit),
the ig-reel / ig-caption / ig-human pack (Jakeschincariol/instagram-agent-skill, MIT), the yt-script /
yt-package / yt-seo / yt-shorts / yt-retention pack (Jakeschincariol/youtube-agent-skill, MIT),
actxion-growth (voice, niche, banned AI tells) and actxion-visuals (brand, fonts, photo method).
Reference account: @thefinalthird.pro (26.9K followers from 11 reels, 2.4M on one) proved that
football debates and myth-busting built entirely in code, with a voiceover and data graphics, travel.

## 1. What we make (series)
Every video ends in an A or B choice. Rotate these; the weekly review keeps what works.

| Series | Length | Shape | Scenes |
|---|---|---|---|
| **Pick your side** (daily) | 20-35 s | today's biggest row: hook, 3-5 facts, A or B | player, score, stat, card, versus, ask |
| **Fans say...** (myth test) | 45-75 s | "X fans say Y. Is it true?" then 3-4 numbers that test it, verdict left to the viewer | player, compare, stat, list, versus, ask |
| **Head to head** | 30-45 s | two players, 4-5 stats, bars grow on the word | compare, player, versus, ask |
| **Combined XI** (big games) | 40-60 s | position by position pick, then the XI on a 3D pitch | versus (per position), pitch, ask |
| **Then and now** | 25-40 s | a club or player now vs a past season | score, stat, compare, ask |

Facts come from named, reachable sources (Sky Sports, BBC Sport, ESPN, the club, Opta via a
publication, FBref / Transfermarkt pages). Every number on screen must be traceable to a URL saved in
the spec's `sources`. Never invent a quote, score, fee, stat or record. If a number can't be checked,
the video doesn't use it.

## 2. Hook (Hook Code)
The first line must do three things: **stop the thumb, make a promise, open a loop.** Under 12
words, spoken and on screen from frame one, with a hit sound on frame one. Write **three** hooks of
**different** types, score them, use the best:
```bash
python3 /tmp/ig/skills/ig-reel/hookscore.py hooks.txt    # under 50 = no hook yet, write again
```
The seven types (examples are ours):
1. **Name the person** - "If you're a United fan, you need to see this."
2. **The mistake** - "Everyone says Haaland goes missing in big games. Check this."
3. **Result first** - "Two nil down after eighteen minutes. Three two at full time."
4. **Curiosity gap** - "There's one stat nobody mentions about Salah's season."
5. **Number list** - "Three numbers that end the Saka v Foden debate."
6. **Before / after** - "Same club. Same manager. Two completely different teams."
7. **Give them a job** - "Pick one before the clock hits zero. Messi or Ronaldo?"
"Fans say..." videos open with the claim both fanbases make ("Messi fans say Ronaldo stat-pads.
Ronaldo fans say Messi stat-pads.") because the comments do the rest. For each hook, write what the
first frame shows (`player` with the big word, `score`, `stat`).

## 3. Script
Shape (ig-reel): hook 0-2 s; stake 2-7 s, one line on why it matters; body, one idea per beat with
the frame changing every beat (no beat over 4 s); payoff; one ask ("Comment A or B"); the last line
echoes a word from the hook so the replay loops. Spoken English, contractions, numbers written as
words ("two nil", "fifty four days"), source named once ("according to Sky Sports"). UK times.
Run the script through ig-human (`python3 /tmp/ig/skills/ig-human/detect.py script.txt`) and fix
everything it flags (no em dashes, no AI slop words). Read it aloud in your head: nothing that
sounds written.

## 4. Voice
**Default: Kokoro-82M** (Apache-2.0 weights, MIT runtime, free for commercial use), runs in the
cloud box in seconds, no credits:
```bash
python3 skills/actxion-video/scripts/voice.py script.txt voice.wav --voice bm_george --speed 1.08
```
British male voices: `bm_george` (house voice), `bm_fable`, `bm_lewis`, `bm_daniel`. Credit in the
YouTube description: "Voice: Kokoro-82M (Apache 2.0)". Write for the ear: short sentences, "..." for
a pause; direction tags are stripped.

**ElevenLabs: only on a paid plan.** The owner's account is on the free plan (4 Nov 2026), whose
terms don't allow commercial use, and ACTXION posts are commercial. So ElevenLabs is OFF for
anything that gets posted until the owner upgrades (Starter or higher includes a commercial
licence). When it is on: `creative_generate_speech`, eleven_v4, voice Petros `vr54y8Xovf4AEnfNrGqH`,
`generations_count: 1`, then `creative_get_generations` and curl `full_res_url`. About 340-390
credits per 30 s on eleven_v4, 170 on flash. If it says "busy", use Kokoro; never retry in a loop.

**Fallback:** Piper `en_GB-northern_english_male-medium` (CC BY-SA 4.0, credit it).

## 5. Edit: the five passes
Working folder `work/<date>-<slug>/`. Everything is code; every pass writes a file the next reads.
```bash
S=skills/actxion-video/scripts
python3 $S/words.py voice.mp3 words.json --script script.txt         # 01 transcribe: every word timed, script spelling kept
python3 $S/tighten.py voice.mp3 words.json voice-tight.wav words-tight.json   # 01b cut dead air, keep breath
python3 $S/cutout.py photo.jpg photo-cut.png [--at 0.4,0.35]          # 02 cut-out (one per photo; LOOK at it)
python3 $S/build.py spec.json out.mp4 --plan                          # 03+04 plan: motion table + key words
python3 $S/build.py spec.json out.mp4 --stills 0.5,4,9,14             # check stills before the full render
python3 $S/build.py spec.json out.mp4                                 # render + 05 sound + mux + cover
```
- **01 Transcribe.** faster-whisper base.en gives word times; the script's spelling is laid on top.
  Pauses over 0.4 s are cut by tighten.py (0.28 s left inside a sentence, 0.45 s at a full stop).
- **02 Cut-out.** rembg keeps only the main person (or the one nearest `--at`), fills holes, soft
  edge, no outline, no glow. If the cut keeps a logo, a team-mate or loses an arm, try `--at`, then
  another photo. Photos come from actxion-visuals `find_photo.py` (article lead photo, credited).
- **03 Captions.** 1-3 words at a time, each on the word it is spoken, held at least 0.4 s. One key
  word per sentence in `keywords` goes big in Instrument Serif Italic (prefix `!` = red). Captions
  live at y 1200-1430, never over a face.
- **04 Motion.** One scene per idea, fired on its trigger word (`at`). Fast in (0.2-0.35 s,
  ease-out), hold, clean out. Push-ins at most 6%. One idea on screen at a time.
- **05 Sound.** mix.py: hit on frame one, whoosh on every scene change, tap on list items / goals /
  stat rows, ticks on counters, buzz on a red card, chime on the ask. All synthesised in code. Voice
  cleaned and always on top; anything else ducked under it. Master -14 LUFS, true peak under -1 dB.

### spec.json
```json
{
 "voice": "voice-tight.wav", "words": "words-tight.json", "mark": "<repo>/logo/mark-white.png",
 "accent": "#E61E28", "credit": "Photos: Sky Sports, CBS Sports", "tail": 1.2,
 "header": {"text": "Cunha: hero or liability?", "key": ["hero or liability?"]},
 "keywords": ["!off", "eighteen", "penalty", "equaliser", "!winner", "fifty", "!red", "liability"],
 "sources": ["https://www.skysports.com/..."],
 "scenes": [
  {"type": "player", "at": 0, "photo": "cunha-cut.png", "bgPhoto": "cunha.jpg", "word": "HERO", "label": "Man Utd 3-2 Roma", "wordY": -20, "wordSize": 400},
  {"type": "card", "at": "sent", "colour": "red", "text": "Sent off"},
  {"type": "score", "at": "Two", "label": "Champions League", "home": "Man Utd", "away": "Roma", "homeCrest": "...png", "awayCrest": "...png",
   "states": [{"at": "Two", "h": 0, "a": 2, "foot": "18 minutes in"}, {"at": "penalty", "h": 1, "a": 2, "foot": "Bruno scores"}]},
  {"type": "stat", "at": "first", "value": 54, "unit": "days", "label": "without a win", "source": "Yahoo Sports"},
  {"type": "list", "at": "three", "title": "His night", "items": [{"at": "penalty", "text": "Won the penalty"}]},
  {"type": "compare", "at": "goals", "aName": "Saka", "bName": "Foden", "aPhoto": "a-cut.png", "bPhoto": "b-cut.png",
   "rows": [{"label": "Goals", "a": "12", "b": "9", "at": "goals"}]},
  {"type": "pitch", "at": "eleven", "title": "Combined XI", "players": [{"n": "Raya", "x": 50, "y": 90}]},
  {"type": "versus", "at": "So", "a": {"photo": "a-cut.png", "label": "Hero"}, "b": {"photo": "b-cut.png", "label": "Liability"}},
  {"type": "ask", "at": "Comment", "html": "Hero or <span class=\"k\">liability?</span>", "sub": "Send this to a United fan"}
 ]
}
```
`at` is a spoken word (`"two#2"` = its second time) or seconds. Scenes run until the next one starts.
Fonts: Instrument Sans (support, labels) and Instrument Serif Italic (key words); never a third on
screen. Colours: background #09090A with a soft red glow, text #F5F5F4, muted #A3A3AB, accent #E61E28.

### Safe area (strictest of reel-edit and ig-reel)
Nothing important above y=230, below y=1440, or in the right 230 px. The header sits at y 250-420,
the stage at y 430-1190, captions at y 1200-1430.

## 6. Review before anything posts (direct, don't settle)
Look at the stills from `--stills`, then 4 frames pulled from the final MP4. Fix and re-render if:
a cut-out has an outline, a logo or a stray limb; anything covers a face; two ideas are on screen at
once; a graphic lands late (fire 3 frames earlier by moving `at` to the word before); a caption
flashes under 0.4 s; the hook frame has no big word; text breaks the safe area; a scene is under
0.8 s. Check the mix line: LUFS -13.5 to -14.5 and true peak under -1. The video must make sense
with the sound off (captions + graphics) and with it on.

## 7. Package per platform (one call per network in Metricool)
- **Cover:** the frame with the big word (`<out>-cover.jpg`); never a frame with captions half in.
- **Instagram Reel:** caption per ig-caption rules: the first line survives "... more" and is the
  question, 3-5 short lines with player and club names (search), one ask, 3 hashtags. First comment
  = a second, related pick-your-side question (never credits). `instagramData {"type": "REEL",
  "showReelOnFeed": true, "isAiGenerated": false}`, `videoThumbnailUrl` = cover.
- **YouTube Short:** title per yt-package: under 60 characters (40 for mobile), the question with a
  name or a number, no more than 2 capitalised words, ends `#shorts`. Description per yt-seo: the
  first two lines answer the query people type ("Cunha red card Roma"), then "Pick your side in the
  comments", sources, photo credits, the voice credit ("Voice: Kokoro-82M (Apache 2.0)"), "Vote on every big
  call in the ACTXION app". 5-12 tags (names, club, competition). `youtubeData {"type": "short",
  "privacy": "public", "madeForKids": false, "category": "SPORTS", "isAiGeneratedContent": false}`.
- **TikTok:** one hook line + the A or B ask + 3-4 hashtags. `tiktokData {"privacyOption":
  "PUBLIC_TO_EVERYONE", "isAigc": true, "autoAddMusic": false, "title": "<question>"}` (synthetic voice is declared).
- **X (experiment E3):** native video, 1-2 lines in the actxion-growth voice ending in an either/or,
  at most one match or competition hashtag, photo credits in `firstCommentText`. Time it 17:30-19:30
  IST (not on the dot of the other networks) or 23:00-01:00 IST, at least 20 minutes from any queued X
  post. Append `date,ist_time,desk,experiment,variant,first_line` = `...,video,E3,video,...` to
  posts/experiments.csv on claude/posts. If X rejects the file, report it; don't retry in a loop.
- **Timing:** main post 19:00 IST (UK 13:30, Lagos 14:30, Nairobi 16:30, India evening). Never within
  45 minutes of a team video on the same network.

## 8. Publish
Commit the MP4, cover and spec to `claude/posts` at `posts/<date>/vid-<slug>.mp4`, push, poll the
raw.githubusercontent.com URL until HTTP 200, then schedule. Keep each MP4 under 50 MB.

## 9. Learn (weekly)
From Metricool, per video and per platform: views, average watch time, full-watch rate (TikTok),
shares, comments, follows. Judge series against each other, not against last week's luck. Keep the
two best series, change one variable at a time (hook type, length, voice, first scene), and write the
result into this file's series table.

## Cloud setup (once per run)
```bash
python3 -m pip install -q --ignore-installed pillow numpy scipy imageio-ffmpeg "rembg[cpu]" faster-whisper kokoro-onnx soundfile
(cd skills/actxion-video/engine && npm i --silent)      # playwright 1.49.1; falls back to /opt/pw-browsers/chromium
git clone -q --depth 1 https://github.com/Jakeschincariol/instagram-agent-skill /tmp/ig
git clone -q --depth 1 https://github.com/Jakeschincariol/youtube-agent-skill /tmp/yt
```
First runs download the cut-out model (~180 MB), the whisper model (~140 MB) and Kokoro (~350 MB).
Kokoro needs Python 3.10+.

## Never
Match footage, TV clips, club or league video, copyrighted music, AI images or AI video of real
people, a cloned voice of a real person, invented numbers or quotes, automated likes, follows,
comments or DMs.
