# Video plan: Carrick sacked: Neville says it won't fix United (Fans say..., Thu 12 Nov 2026)

## 1. Freshness (checked 16:10 IST / 10:40 UK)
| # | Story | Published | URL |
|---|---|---|---|
| 1 | **Man Utd sack Michael Carrick, Pochettino set to replace him** | Thu 12 Nov 10:27 UK | https://www.skysports.com/football/news/13606106/man-utd-sack-michael-carrick-with-mauricio-pochettino-set-to-be-appointed-after-worst-start-to-premier-league-season |
| 2 | Man Utd strike Pochettino agreement (£7m release clause with USA) | Thu 12 Nov 10:31 UK | https://www.skysports.com/football/news/13610949/mauricio-pochettino-man-utd-strike-agreement-with-michael-carricks-potential-successor |
| 3 | Josh King: rising star after England call-up | Thu 12 Nov (Sky analysis) | https://www.skysports.com/football/news/13611079/josh-king-the-making-of-the-rising-star-tipped-to-become-one-of-worlds-best-players-after-england-call-up |
| 4 | England v Croatia tonight, 7.45pm UK | live blog, today | https://www.skysports.com/football/live-blog/13427059/england-football-news-live-updates-schedule-and-analysis-of-thomas-tuchels-three-lions |
| 5 | Italy v France tonight, Mbappé out | today | covered by the 11 Nov video (France nine out) |

Winner: #1. It broke this morning (UK), it is the biggest row in the Premier League today, and it has a clean two-sided
question (Carrick or the club?) with Gary Neville's "rinse and repeat" on record. No ACTXION video in 48 h covered it:
video desk did Wenger/Infantino (10 Nov) and France nine out (11 Nov); the "mic" desk's 16:00 IST reel is Chelsea/Xabi,
the lab reel is Leicester 5000-1. #2 is the same story, folded in. #5 was covered yesterday.

## 2. Fact sheet (all from Sky Sports, 12 Nov 2026, URL 1 unless marked)
- Man Utd have sacked Michael Carrick; Pochettino set to be appointed (headline, URL 1).
- "United are in the relegation zone after 10 league games" (URL 1).
- "the club's worst-ever start to a Premier League season" (URL 1).
- "just three wins in 15 matches this term have cost him his job" (URL 1).
- "winning 12 of 17 matches to earn a third-place finish in the Premier League and a return to the Champions League" (URL 1, last season).
- "United are now looking for an eighth permanent head coach since Sir Alex Ferguson left in 2013" (URL 1; URL 2 says Pochettino would be the eighth).
- Gary Neville: "this has been proven now over 12 years, that's not the answer." / "It's rinse and repeat." (URL 1)
- Spoken paraphrase "Gary Neville says sacking Carrick won't fix United" = Neville's "that's not the answer" about a new-manager bounce, URL 1. On screen we show only his exact words "rinse and repeat".

## 3. Angle, series, A or B
- Angle: test Neville's claim that sacking the manager won't fix United with the numbers on both sides.
- Series: **Fans say...** (Thursday in rotation.md), myth-test shape, claim from a named pundit. Music mood from series.
- A or B: **A = Carrick's fault** (worst ever start, relegation zone) / **B = the club's fault** (8th permanent head coach since 2013, Carrick finished third last season). Both defensible.
- Current test (9-15 Nov): fact-first opener, the A/B question only in the last line. Followed.

## 4. Hooks (hookscore.py)
| Hook | Type | Score |
|---|---|---|
| **Gary Neville says sacking Carrick won't fix United. Check the numbers.** | The mistake / claim (fact-first: a name and a claim) | **57.6** |
| Relegation zone after ten games. Michael Carrick is gone. | Result first | 50.6 |
| Three wins in fifteen. United just sacked Michael Carrick. | Number | 50.6 |
Winner: Neville hook. Frame one: `player` Carrick cut-out over his own photo, big word SACKED.

## 5. Beat sheet (times approximate, set to word triggers after voicing)
| t | Line | Scene | On screen | Motion | Sound | Why |
|---|---|---|---|---|---|---|
| 0-3 | Gary Neville says sacking Carrick won't fix United. Check the numbers. | player | Carrick cut-out, word SACKED | push-in | kick + boom | the news + the claim to test |
| 3-7 | Manchester United have sacked Michael Carrick, and Sky Sports says Mauricio Pochettino is set to replace him. | player | Pochettino cut-out, word NEXT? -> label "Set to replace Carrick (Sky Sports)" | fast in | whoosh | stake: who comes next |
| 7-10 | First, the case against Carrick. United are in the relegation zone after ten league games. | stat | 10 games, "in the relegation zone" | counter | ticks + impact | A side, fact 1 |
| 10-13 | It's the club's worst ever start to a Premier League season. | player | Carrick2 cut-out, word WORST EVER | fast in | whoosh | A side, fact 2 |
| 13-16 | Just three wins in fifteen matches this term. | stat | 3 wins / "in 15 matches this term" | counter | impact | A side, fact 3 |
| 16-20 | Now Neville's side. Last season Carrick won twelve of seventeen and finished third. | list | "Last season": Won 12 of 17 / Finished 3rd | taps | taps | B side, fact 1 |
| 20-25 | Pochettino would be United's eighth permanent head coach since Sir Alex Ferguson left in twenty thirteen. | stat | 8th permanent head coach since 2013 | counter | impact | B side, fact 2 |
| 25-27 | Neville calls it rinse and repeat. | player | Neville cut-out, word RINSE & REPEAT | fast in | whoosh | the claim in his words |
| 27-30 | So who's really to blame for this? Carrick, or the club? | versus | Carrick v club (Carrick / Pochettino... see note) | split | riser | the choice |
| 30-33 | Comment A or B. | ask | "Carrick or the club?" | pop | chant + ding | ask; "Carrick" echoes the hook |
Versus note: A = Carrick cut-out "Carrick's fault", B = Neville cut-out? No: B uses Pochettino "The club's fault (8th boss)"? Final: B = United crest is not ours to use, so B shows Pochettino labelled "The club: 8 bosses since 2013".

## 6. Photos (find_photo.py)
- Carrick: Sky Sports article lead (Photo: Sky Sports); the photo has a "CARRICK SACKED" graphic, so only the cut-out is used, the bg is the second photo.
- Carrick 2: Getty via Yahoo Sports (find_photo returned it for Pochettino from URL 2's search; it is Carrick at Old Trafford).
- Pochettino: FOX Sports (USA press conference).
- Neville: University of Salford Press Office, Wikimedia Commons, CC BY 2.0.
- The finder's first Neville and Pochettino results were Carrick photos: discarded.
- Cut-out check: see section 8.

## 7. Packaging
- Cover: frame one (Carrick, SACKED).
- YouTube title: "Carrick sacked: is Neville right about United? #shorts"
- IG first line: "Carrick's gone. Gary Neville says that won't fix United."
- YT first line: "Michael Carrick sacked by Manchester United, Pochettino set to replace him."
- TikTok: "Carrick sacked. Neville says it won't fix United."
- X: "Manchester United have sacked Michael Carrick after three wins in 15. Gary Neville calls it rinse and repeat."
- Facebook: "Manchester United have sacked Michael Carrick."

## 8. Checklist
- [x] story <24 h old (10:27 UK today)
- [x] every fact sourced (section 2)
- [x] one idea per beat (check after --plan)
- [x] no face covered (check stills)
- [x] safe area respected (check stills)
- [x] no photo credits on screen
- [x] music under the voice (check SOUND PLAN, LUFS)
- [x] the ask is a real two-sided question

## Build notes
- Voice: Kokoro bm_fable, speed 1.1 (34.6 s raw, 32.9 s tightened). Video 33.6 s. Music bed: tense (series Fans say...).
- Beat changes after --plan: added a red card "Gone" at 3.6 s and moved Neville to "twenty" so no beat runs over 4 s; the
  "case against" list now carries the relegation-zone fact (stat scene dropped, it repeated it); "8th" became "8 bosses";
  versus B shows Neville (the club side is his argument), not Pochettino.
- Cut-outs looked at: Carrick (Sky) clean, Carrick 2 clean, Pochettino clean, Neville cropped to drop a painted Subbuteo figure.
- Mix: LUFS -14.00, true peak -3.48.
