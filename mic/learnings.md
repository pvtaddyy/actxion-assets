# THE MIC learnings (read before every episode; the Monday review rewrites this)

Last updated: 9 Nov 2026 (Monday review 1: 2 episodes posted, both too early for firm conclusions).

## Baselines to beat (Instagram, early Nov 2026)
- Daily desk news reel ~330 views, ~8 s average watch. Team combined XI reels 1.4-1.8K views, 18-22 s watch.

## Current rules
- Approved style = EP 01 (street set, 5 fans, blame meter, mic in frame, ElevenLabs voices, rain + crowd bed).
- Cold open is the most emotional line, not context. The question card lands by ~10 s.
- One fan is funny (a crowd laugh after the joke). One fan picks a third option (meter jumps up).
- 40-50 s. Never sell the app in the episode.
- NEW 9 Nov (change of the week): HARD CAP 50 s, aim for 45 s. Cut fan lines before going over; the mic sign-off stays.
  Why: EP 1 (47 s) holds IG average watch at 14.0 s (~30 % of the video) on 1,632 views; EP 2 (57.6 s) is at 2.5 s
  average watch on 114 views after 12.5 h. Only 2 episodes and EP 2 also changed slot, set, club, cold open and added an
  app line, so this is a guard-rail back to the approved length, not a proven effect. Re-check Mon 16 Nov.
- Budget (9 Nov): THE MIC used 2,847 ElevenLabs credits by 9 Nov (about 760 per episode incl. tests) and is on course
  to pass 8,000 in November. For the rest of November use eleven_flash_v2_5 for the fans (keep the MIC host on the
  usual model only if it fits; no test renders on eleven_v4). Back to normal on 1 Dec.

## Posting time (E4-time, owner-approved 5 Nov 2026; shared with ACTXION LAB)
- Current best slot: A = 16:00 IST (default until the decision on Mon 30 Nov).
- Test 7-28 Nov: A 16:00 IST, B 23:30 IST, C 01:30 IST next day; schedule in mic/rotation.md; every post logged in
  posts/experiments.csv as date,ist_time,mic,E4-time,<A|B|C>,first_line. Extra point: EP 1 at 00:30 IST (variant 0030).
- Measure per network: views 48 h after posting (+ IG average watch, comments, shares), divided by the series median.
  "Too early" until each slot has 3 episodes.
- Results: the Monday review writes desk=mic rows (episode x network) to posts/e4-time-results.csv (shared with the LAB:
  date,desk,variant,ist_time,network,views_48h,norm_views,ig_avg_watch_s,comments,shares). Variant is A/B/C; EP 1's 00:30
  post is the extra point 0030 and is left out of the pooling.
- Decision: the LAB's Sunday review on 29 Nov pools lab + mic (about 6 per slot) and writes posts/e4-decision.md (best median
  norm_views; within 10 % -> better IG average watch; a network gets its own slot only if its gap is over 20 %). THE MIC's
  Monday review on 30 Nov follows it unless MIC's own data clearly disagrees (another slot >20 % better on 3+ episodes each),
  writes the winner here and into mic/rotation.md, then re-tests once a month against one challenger slot.
- Table 9 Nov (median norm_views; MIC series median = EP 1 only so far):
  | slot | MIC episodes with 48 h data | IG | TikTok | FB | IG avg watch |
  | A 16:00 | 0 | too early | too early | too early | too early |
  | B 23:30 | 0 (EP 2 is 12.5 h old) | too early | too early | too early | too early |
  | C 01:30 | 0 | too early | too early | too early | too early |
  | 0030 extra (EP 1) | 1 | 1.00 (1,629) | 1.00 (602) | 1.00 (218) | 14.1 s |

## Open tests (one at a time)
1. Set: street v pub v viewing centre.
2. Club: United / Arsenal / Chelsea v Real / Barca.
3. Cold open: sad line v angry line v funny line.
Scoreboard 9 Nov (too early everywhere, under 3 episodes per variant):
  | variant | episodes | IG views / avg watch | TikTok | FB |
  | viewing (Lagos) / Liverpool / angry / 47 s / 00:30 | 1 | 1,632 / 14.0 s (84 h) | 602 | 219 |
  | pub (Manchester) / Man City / sad / 57.6 s / B 23:30 | 1 | 114 / 2.5 s (12.5 h) | 14 | 1 |
  YouTube: Metricool has no YouTube rows after 3 Nov, so no MIC YouTube numbers yet.
