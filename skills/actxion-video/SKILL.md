---
name: actxion-video
description: ACTXION's daily vertical video series "Pick your side in 30 seconds" - one football row told in 6-8 Still Frame cards with a narrated voiceover, rendered to a 1080x1920 MP4 and posted once to Instagram Reels, YouTube Shorts and TikTok. Use when planning, scripting, rendering, captioning or posting ACTXION short videos, or when reviewing how they perform.
---

# ACTXION video: "Pick your side in 30 seconds"

One series, three platforms, made end to end by a cloud routine. Built on actxion-growth (niche, voice), actxion-visuals (Still Frame cards) and the ig-reel rules from Jakeschincariol/instagram-agent-skill (hook in 2 seconds, one idea per beat, payoff then one ask, a loop back to the hook).

## Why this format
- The team's existing videos are re-uploads of talking points: about 200 views on Instagram, about 400 on TikTok, and YouTube has 450+ videos and about 120 subscribers. Since April 2026 Instagram stops recommending accounts that mostly repost; YouTube and TikTok reward a recognisable series.
- This series is original by construction: our own research, our own cards, our own narration, a question at the end. It is the same story as the day's best carousel, so the research is shared.
- Fans pick a side in the comments, and comments plus shares are what all three algorithms read.

## Script shape (20-35 seconds, 6-8 cards)
| Beat | Card | Narration |
|---|---|---|
| Hook, 0-2 s | `poster` with the person's face | The claim or the question, under 12 words ("Matheus Cunha did a whole season in one night. Hero, or liability?") |
| Stake | `poster` | Why it matters, one line |
| Body, 2-4 cards | `scoreboard`, `redcard` (quote), `poster` | One fact per card, the source named once ("according to Sky Sports") |
| Verdict | `ballot` with both faces | "So which is it? A, or B?" |
| Ask + loop | `poster` over the stadium or fans | "Comment A or B." Echo a word from the hook so the replay lands |

Rules: every card at least 2.2 seconds and at most about 5; numbers written as words in the narration ("two nil", "fifty four days"); never invent a quote, score or fee; real quotes only from a named source; UK times.

## Render
```bash
python3 -m pip install -q --ignore-installed pillow imageio-ffmpeg piper-tts
mkdir -p ~/voices && cd ~/voices && B=https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/northern_english_male/medium && \
  curl -sLO $B/en_GB-northern_english_male-medium.onnx && curl -sLO $B/en_GB-northern_english_male-medium.onnx.json
python3 skills/actxion-video/scripts/make_video.py spec.json posts/<date>/vid-<slug>.mp4
```
`spec.json`: `{"voice": "<path>/en_GB-northern_english_male-medium.onnx", "slides": [{"image": "<card png>", "say": "<line>"}, ...]}`. The cards come from `skills/actxion-visuals/scripts/render.py` (portrait 1080x1350); the script places each on a blurred copy of itself for 9:16, adds a slow push-in, and lines up each spoken line with its card. Voice: Piper "northern_english_male" (CC BY-SA 4.0): credit "Voice: Piper northern_english_male (CC BY-SA 4.0)" in the YouTube description. Look at a few frames (extract with the bundled ffmpeg) before posting.

## Post (Metricool createScheduledPost, one call per network so each gets its own text)
- **Instagram Reel:** providers instagram, `instagramData: {"type": "REEL", "showReelOnFeed": true, "isAiGenerated": false}`, `videoThumbnailUrl` = the cover card PNG, caption per actxion-instagram.
- **YouTube Short:** providers youtube, `youtubeData: {"type": "short", "title": "<under 70 chars, the question> #shorts", "privacy": "public", "madeForKids": false, "category": "SPORTS", "tags": [player, club, competition], "isAiGeneratedContent": false}`, text = description (2-3 lines + the photo credits + the voice credit).
- **TikTok:** providers tiktok, `tiktokData: {"privacyOption": "PUBLIC_TO_EVERYONE", "isAigc": true, "autoAddMusic": false, "title": "<the question>"}`. The narration is a synthetic voice, so it is declared.
- `media` = the MP4's raw.githubusercontent.com URL (committed to `claude/posts`, polled until 200).
- Times: 19:00 IST (UK 13:30, Lagos 14:30, Nairobi 16:30, India evening). Never within 45 minutes of a team video on the same network.

## Never
Match footage, TV clips, club or league video, copyrighted music, AI images or AI video of real people, a cloned voice of a real person.
