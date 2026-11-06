#!/usr/bin/env python3
"""THE MIC: build hf/index.html from episode.json + timeline.json + words.json (run lines.py first).
   python3 build.py
episode.json (see episodes/ep01/episode.json for a full example):
  set: street | pub | viewing        club: {name, primary, secondary, third}
  loc: chip text                     question: {phrase, kicker, line1, line2}
  meter: {title, left, right, third}  ask: {a, b, next}    end: end-card line    keywords: [...]
  boo: true/false (crowd boo before the question)   laugh: phrase that gets a crowd laugh after it
  fans: [{who, label, sub, coat, shirt, legs, skin, hair, acc[], open, gesture, mood, laugh, pop, meter, color}]
    gesture: pockets | jab | point | handsup | crossed | shrug | facepalm ; pop = phrase that fires the gesture peak ('Lagos#2' = its 2nd time in that line)
    meter: -1 (left) .. +1 (right), or "third" (needle jumps up to the third option on its pop phrase)
script.tsv lines: who = a fan's who, or MIC (first MIC line = the question, last MIC line = the sign-off), or APP (the host's
  ACTXION feature line; the phone with that feature's app screen plays over it).
  feature: {type: fan_voice | starting_11 | fan_wall | live_subs | transfer_window, club, opponent, when, colour, text, tag,
            xi[11] + pos[11] (starting_11), off + options[{name,num,pick}] + minute (live_subs), players[{name,choice}] (transfer_window),
            comments[{user, tag, text, ago}] = the episode's own fan lines as wall/voice comments (fictional usernames),
            pick[{name,num,note,chosen}] + empty[slot indexes] (starting_11), squad[] (live_subs), banner (transfer_window).
            The screens are rebuilt in HTML to look like the real app (owner, 6 Nov 2026); never invent vote counts or %}"""
import json, re, html, math

EPI = json.load(open('episode.json'))
words = json.load(open('words.json')); TL = json.load(open('timeline.json')); LINES = TL['lines']
norm = [re.sub(r"[^\w']", '', w['w'].lower()) for w in words]
def at(phrase, nth=1, line=None):
    p = [re.sub(r"[^\w']", '', x.lower()) for x in phrase.split()]; hit = 0
    for i in range(len(norm) - len(p) + 1):
        if norm[i:i + len(p)] == p and (line is None or words[i]['line'] == line):
            hit += 1
            if hit == nth: return round(words[i]['s'], 3)
    raise SystemExit(f'phrase not found: {phrase}')
toint = lambda c: int(str(c).lstrip('#'), 16) if isinstance(c, str) else c

mic = [l for l in LINES if l['who'] == 'MIC']
assert len(mic) >= 2, 'need a MIC question line and a MIC sign-off line'
Q, CLOSE = mic[0], mic[-1]
ENDCARD = round(CLOSE['e'] + 2.6, 2); END = round(ENDCARD + 2.0, 2)
B = dict(q=at(EPI['question']['phrase'], line=Q['id']), ask=CLOSE['s'], endcard=ENDCARD, end=END)

# ---------- cast: positions alternate sides down the street / room ----------
FANS = []
for i, f in enumerate(EPI['fans']):
    f = dict(f); f['x'] = (-1.35 if i % 2 == 0 else 1.45); f['z'] = -2 - i * 5
    for k in ('coat', 'shirt', 'legs', 'skin', 'hair'): f[k] = toint(f[k])
    f.setdefault('acc', []); f.setdefault('gesture', 'shrug'); f.setdefault('mood', 0)
    fl = [l for l in LINES if l['who'] == f['who']]
    if f.get('pop') and fl:
        ph, _, nth = f['pop'].partition('#')
        f['pop'] = round(at(ph, int(nth or 1), line=fl[0]['id']) - fl[0]['s'], 2)
    else: f['pop'] = None
    FANS.append(f)
F = {f['who']: f for f in FANS}
club = {k: toint(v) for k, v in EPI['club'].items() if k != 'name'}

def shot_for(f, t, **kw):
    cx = f['x'] * .45; cz = f['z'] + 3.2
    f['face'] = math.atan2(cx - f['x'], cz - f['z'])
    return dict(t=t, p=[cx, 1.85, cz], l=[f['x'] - (cx - f['x']) * .12, 1.86, f['z']], fov=44, **kw)
SHOTS = []
for n, l in enumerate(LINES):
    t = 0 if n == 0 else l['s'] - .3
    if l is Q: SHOTS.append(dict(t=l['s'] - .15, p=[.4, 1.8, -.6], l=[0, 4.5 if EPI['set'] == 'street' else 3.0, -60], fov=52, push=.03, move=.45))
    elif l is CLOSE: SHOTS.append(dict(t=l['s'] - .35, p=[0, 1.9, 3.2], l=[0, 1.6, -14], fov=50, push=0, move=.6, crane=2.2, shake=.6))
    elif l['who'] in F: SHOTS.append(shot_for(F[l['who']], t, **({'push': .16, 'move': .1} if n == 0 else {})))
    elif l['who'] == 'APP': SHOTS.append(dict(t=l['s'] - .3, p=[0, 2.4, 1.5], l=[0, 1.7, -20], fov=52, push=.05, move=.6, shake=.4))
for f in FANS: f.setdefault('face', 0)
APPL = [l for l in LINES if l['who'] == 'APP']
PH = (round(APPL[0]['s'] - .25, 3), round(APPL[0]['e'] + .6, 3)) if APPL and EPI.get('feature') else None
EP = {'beats': B, 'lines': LINES, 'fans': FANS, 'shots': SHOTS, 'set': EPI['set'], 'club': club, 'feature': EPI.get('feature') if PH else None}

# ---------- overlays ----------
ov = []
def add(id, s, e, inner, kind): ov.append((id, round(s, 3), round(e, 3), inner, kind))
add('loc', .35, Q['e'], f'<span>{html.escape(EPI["loc"])}</span>', 'loc')
for l in LINES:
    if l['who'] in F:
        f = F[l['who']]; add(f'who-{l["id"]}', l['s'] + .1, l['e'] + .2, f'<div class="wl">{html.escape(f["label"])}</div><div class="ws">{html.escape(f["sub"])}</div>', 'who')
q = EPI['question']
add('q', B['q'] - .05, Q['e'] + .45, f'<div class="qk">{html.escape(q.get("kicker", "ONE QUESTION"))}</div><div class="qt">{html.escape(q["line1"])}<br><b>{html.escape(q["line2"])}</b></div>', 'qcard')
after = [l for l in LINES if l['s'] > Q['s'] and l['who'] in F]
m = EPI['meter']; MOVES = []
for l in after:
    v = F[l['who']].get('meter', 0)
    if v == 'third':
        t3 = l['s'] + (F[l['who']]['pop'] if F[l['who']]['pop'] is not None else .4); MOVES.append((round(t3, 3), 'third'))
    else: MOVES.append((round(l['s'] + .4, 3), float(v)))
if after:
    third = f'<div class="up">⬆ {html.escape(m["third"])}</div>' if m.get('third') else '<div class="up"></div>'
    add('meter', after[0]['s'] - .1, after[-1]['e'] + .4,
        f'<div class="mt">{html.escape(m["title"])}</div><div class="gauge"><span class="gl">{html.escape(m["left"])}</span><div class="track"><i class="needle"></i></div><span class="gr">{html.escape(m["right"])}</span></div>{third}', 'meter')
a = EPI['ask']
add('ask', B['ask'] - .05, ENDCARD, f'<div class="q a">{html.escape(a["a"])}</div><div class="or">or</div><div class="q b">{html.escape(a["b"])}</div>'
    f'<div class="next" data-at="{round(CLOSE["e"] - B["ask"] + .2, 2)}">{html.escape(a["next"])}</div>', 'ask')

# ---------- captions (word-lit, 1-3 words) ----------
KEYW = {k.lower() for k in EPI.get('keywords', [])}
plain = lambda w: re.sub(r"[^\w']", '', w.lower())
HIDE = [(B['q'] - .05, Q['e'] + .45), (B['ask'] - .05, END + 1)] + ([(PH[0], PH[1])] if PH else [])
hidden = lambda s: any(x <= s < y for x, y in HIDE)
WEAK = {'a', 'the', 'of', 'in', 'and', 'to', "it's", 'he', 'his', 'is', 'that', 'or', 'but', 'i', 'for', 'on', 'how', "i've", "he's", 'we', 'out', 'my', 'our', 'they'}
groups, cur = [], []
for j, tk in enumerate(words):
    if hidden(tk['s']):
        if cur: groups.append(cur); cur = []
        continue
    cur.append(j); nxt = words[j + 1] if j + 1 < len(words) else None
    end_p = re.search(r'[.?!,]$', tk['w']) or not nxt or nxt['line'] != tk['line'] or nxt['s'] - tk['e'] > .25
    if end_p: groups.append(cur); cur = []
    elif len(cur) >= 3:
        if plain(words[cur[-1]]['w']) in WEAK: groups.append(cur[:-1]); cur = cur[-1:]
        else: groups.append(cur); cur = []
if cur: groups.append(cur)
COL = {f['who']: f.get('color', '#ffd54a') for f in FANS}; COL['MIC'] = '#ffd54a'; COL['APP'] = '#ffd54a'
caps = []
for gi, g in enumerate(groups):
    s = words[g[0]]['s'] - .06; e = words[g[-1]]['e'] + .3
    if gi + 1 < len(groups): e = min(e, words[groups[gi + 1][0]]['s'] - .07)
    e = max(e, s + .4)
    for x, y in HIDE:
        if s < x < e: e = x
    who = words[g[0]]['who']; spans = []
    for j in g:
        tk = words[j]; cls = 'w k' if plain(tk['w']) in KEYW else 'w'
        spans.append(f'<span class="{cls}" data-ws="{round(tk["s"] - s, 3)}">{html.escape(tk["w"])}</span>')
    nch = sum(len(words[j]['w']) + 1 for j in g)
    size = '' if nch <= 17 else (' style="font-size:62px"' if nch <= 23 else ' style="font-size:54px"')
    caps.append((f'c{gi}', round(max(.12, s), 3), round(e, 3), f'<span class="ln" data-k="{COL.get(who, "#ffd54a")}"{size}>' + ' '.join(spans) + '</span>'))

# ---------- sound effects ----------
cuts = [s['t'] for s in SHOTS[1:]]
sfx = [('impact-2', 0.02, .35)] + [('whoosh-2', c - .05, .55) for c in cuts]
if EPI.get('boo', True): sfx.append(('reaction-crowd-boo', Q['s'] - .9, .55))
sfx += [('impact-2', B['q'], .7), ('cinematic-deep-boom', B['q'] + .02, .35)]
sfx += [('pop-2', l['s'] + .1, .5) for l in LINES if l['who'] in F]
sfx += [('tech-ui-confirm', t, .35) if v != 'third' else ('whoosh-3', t, .45) for t, v in MOVES]
if EPI.get('laugh'): sfx.append(('reaction-crowd-laugh', at(EPI['laugh']) + .2, .3))
if PH: sfx += [('whoosh-3', PH[0], .5), ('pop-2', PH[0] + 1.0, .45), ('tech-ui-confirm', PH[0] + max(1.6, (PH[1] - PH[0]) * .72), .55)]
sfx += [('whoosh-cine', B['ask'], .5), ('ding-1', CLOSE['e'] + .2, .55), ('whoosh-3', ENDCARD, .45), ('impact-2', ENDCARD + .15, .6)]

def clip(id, s, e, cls, inner, track):
    return f'<div id="{id}" class="clip {cls}" data-start="{s}" data-duration="{round(e - s, 3)}" data-track-index="{track}"><div class="in">{inner}</div></div>'
body = '\n'.join(clip(i, s, e, f'ov {k}', h, 2) for i, s, e, h, k in ov)
capb = '\n'.join(clip(i, s, e, 'cap', h, 3) for i, s, e, h in caps)
REC = None
if PH and EPI['feature'].get('rec'):
    r = EPI['feature']['rec']; t0, t1 = PH[0] + .35, PH[1] - .35; span = r['out'] - r['in']
    speed = min(4.0, max(1.0, span / (t1 - t0)))
    REC = {'file': r['file'], 'in': r['in'], 'out': min(r['out'], r['in'] + (t1 - t0) * speed), 'speed': round(speed, 3),
           't0': round(t0, 3), 't1': round(t1, 3), 'x': 293, 'y': 238, 'w': 511, 'h': 1111}
json.dump({'sfx': sfx, 'beats': B, 'end': END, 'set': EPI['set'], 'rec': REC}, open('mix.json', 'w'), indent=1)
page = open('template.html').read()
for k, v in {'{{EP}}': json.dumps(EP), '{{END}}': str(END), '{{OVERLAYS}}': body, '{{CAPTIONS}}': capb,
             '{{ENDCARD}}': str(ENDCARD), '{{ENDDUR}}': str(round(END - ENDCARD, 2)), '{{MOVES}}': json.dumps(MOVES),
             '{{CUTS}}': json.dumps(cuts), '{{PHONE}}': (f'<div id="phone" class="clip" data-start="{PH[0]}" data-duration="{round(PH[1] - PH[0], 3)}" data-track-index="5"></div>' if PH else ''), '{{ENDLINE}}': html.escape(EPI.get('end', 'Which fanbase do we visit next? 👇'))}.items():
    page = page.replace(k, v)
open('hf/index.html', 'w').write(page)
print('end', END, 'overlays', len(ov), 'captions', len(caps), 'sfx', len(sfx), 'shots', len(SHOTS))
