#!/usr/bin/env python3
"""Build the HyperFrames index.html for a Race Day episode from words.json + this file's EPISODE block.
   python3 build.py   ->  hf/index.html
"""
import json, re, html

ROOT = 'hf'
words = json.load(open('words.json'))
norm = [re.sub(r"[^\w']", '', w['w'].lower()) for w in words]

def at(phrase, nth=1):
    p = [re.sub(r"[^\w']", '', x.lower()) for x in phrase.split()]
    hit = 0
    for i in range(len(norm) - len(p) + 1):
        if norm[i:i + len(p)] == p:
            hit += 1
            if hit == nth: return round(words[i]['s'], 3)
    raise SystemExit(f'phrase not found: {phrase}')

END = round(words[-1]['e'] + 2.0, 2)
B = dict(hook=0.0, ctx=at('Race Day'), l1=at('Lane one'), hNum=at('Thirty six point two'), l2=at('Lane two'),
         fNum=at('Thirty six point one'), wins=at('Haaland wins'), wNum=at('nought point nought'), l3=at('Lane three'),
         mNum=at('Thirty six point seven'), quick=at('the quickest'), twist=at('But the fastest'), tch=at('Jackson Tchatchoua'),
         wolves=at('A Wolves'), tNum=at('Thirty seven point three', 1), aug=at('against Everton'), even=at('Even his'),
         since=at('Since records'), walker=at('Kyle Walker'), wkNum=at('thirty seven point three', 2), vdv=at('And Micky'),
         vdvNum=at('thirty seven point three', 3), ask=at('Tchatchoua or'), straight=at('Who wins'), oneword=at('One word'),
         nextq=at('Which race'), end=END)
import base64
CRESTS = ['mci', 'liv', 'ars', 'wol', 'tot', 'pl']
CREST_DATA = {k: 'data:image/png;base64,' + base64.b64encode(open(f'assets/{k}.png','rb').read()).decode() for k in CRESTS}
K = {  # stylised kits (no faces, no numbers except Haaland's 9)
  'haa': {'shirt': '#6CABDD', 'shorts': '#ffffff', 'socks': '#6CABDD', 'hair': '#e8cf8a', 'skin': '#e9c4a6', 'num': '9', 'bun': True},
  'fri': {'shirt': '#C8102E', 'shorts': '#C8102E', 'socks': '#C8102E', 'hair': '#1a1410', 'skin': '#7a5038', 'num': ''},
  'mar': {'shirt': '#EF0107', 'shorts': '#ffffff', 'socks': '#ffffff', 'hair': '#2a1d14', 'skin': '#d6a882', 'num': '', 'sleeves': '#ffffff'},
  'tch': {'shirt': '#FDB913', 'shorts': '#231F20', 'socks': '#FDB913', 'hair': '#141010', 'skin': '#5e3d2b', 'num': ''},
  'vdv': {'shirt': '#ffffff', 'shorts': '#132257', 'socks': '#ffffff', 'hair': '#6b4a2e', 'skin': '#ecc9ab', 'num': ''},
  'wal': {'shirt': '#6CABDD', 'shorts': '#ffffff', 'socks': '#6CABDD', 'hair': '#141010', 'skin': '#8a5f45', 'num': ''},
}
EP = {'crestData': CREST_DATA, 'beats': B, 'kits': K, 'crests': CRESTS,
      'colors': {'sky': '#070b16', 'accent': '#ffd54a'},
      'speeds': {'haa': 36.20, 'fri': 36.18, 'mar': 36.74, 'tch': 37.30, 'tch2': 36.97, 'wal': 37.31, 'vdv': 37.38}}

# ---------------- overlays ----------------
ov = []   # (id, start, end, html, kind)
def add(id, s, e, inner, kind='title'): ov.append((id, round(s, 3), round(e, 3), inner, kind))
G = lambda s: f'<b>{s}</b>'
SRC = '<div class="src">Data: Premier League</div>'
def stat(num, crest, name, extra='', dec=2):
    return (f'<div class="crow"><img src="assets/crests/{crest}.png"></div><div class="num sm" data-to="{num}" data-dec="{dec}">0</div>'
            f'<div class="lab">KM/H</div><div class="sub">{name}</div>{extra}{SRC}')
add('t-hook', 0.05, B['ctx'], f'THE LEAGUE&#39;S<br>{G("FASTEST MAN")}')
add('ctx', .3, B['l1'] + 1.5, '<span>PREMIER LEAGUE · 2025/26 · TOP SPEEDS</span>', 'chip')
add('r-0', B['ctx'], B['l1'], '<div class="rk">RACE DAY</div><div class="rt">OFFICIAL TOP SPEEDS</div><div class="rs">Premier League 2025/26</div>', 'round')
add('s-h', B['hNum'], B['l2'], stat('36.20', 'mci', 'Erling Haaland · Man City'), 'stat')
add('s-f', B['fNum'], B['wins'], stat('36.18', 'liv', 'Jeremie Frimpong · Liverpool'), 'stat')
add('s-w', B['wNum'], B['l3'], '<div class="num sm" data-to="0.02" data-dec="2">0</div><div class="lab">KM/H IN IT</div><div class="sub">Haaland 36.20 · Frimpong 36.18</div>' + SRC, 'stat')
add('s-m', B['mNum'], B['twist'], stat('36.74', 'ars', 'Gabriel Martinelli · Arsenal', '<div class="per" data-at="%s">QUICKEST FORWARD</div>' % round(B['quick'] - B['mNum'], 3)), 'stat')
add('t-twist', B['twist'], B['tch'], f'{G("THE TWIST")}<div class="gs">The fastest man<br>wasn&#39;t a forward</div>', 'glitch')
add('t-tch', B['tch'], B['tNum'], f'JACKSON<br>{G("TCHATCHOUA")}<div class="gs2">Wolves · right back</div>')
add('s-t', B['tNum'], B['even'], stat('37.30', 'wol', 'v Everton · 30 Aug 2025', '<div class="per" data-at="0.9">FASTEST OF 2025/26</div>'), 'stat')
add('s-t2', B['even'], B['since'], '<div class="crow"><img src="assets/crests/wol.png"></div><div class="num sm" data-to="36.97" data-dec="2">0</div><div class="lab">HIS 2ND BEST · KM/H</div><div class="sub">v Crystal Palace · Feb 2026</div><div class="per" data-at="1.0">NEXT BEST PLAYER: 36.74</div>' + SRC, 'stat')
add('t-since', B['since'], B['walker'], f'ONLY 2 {G("FASTER")}<br>SINCE 2020/21')
add('t-pod', B['walker'], B['ask'], '<div class="plab"><span>WALKER<br>MAN CITY<br><b>37.31</b></span><span class="late" data-at="%s">VAN DE VEN<br>SPURS<br><b>37.38</b></span><span>TCHATCHOUA<br>WOLVES<br><b>37.30</b></span></div><div class="src">km/h · Premier League, Opta tracking since 2020/21</div>' % round(B['vdv'] - B['walker'], 3), 'pl')
add('dip-1', B['twist'] - .1, B['twist'] + .12, '', 'dip')
add('flash-w', B['wins'] + 1.25, B['wins'] + 1.45, '', 'flash')
add('ask', B['ask'], END - 1.6, f'<div class="q">TCHATCHOUA</div><div class="or">or</div><div class="q b">VAN DE VEN?</div><div class="next" data-at="{round(B["nextq"] - B["ask"], 3)}">Which race do we run next? 👇</div>', 'ask')

# ---------------- captions v3: phrases of 1-3 tokens, numbers as digits, word-by-word light-up ----------------
DIGITS = [("twenty twenty five twenty six", "2025/26"), ("thirty six point one eight", "36.18"), ("thirty six point seven four", "36.74"),
          ("thirty seven point three one", "37.31"), ("thirty seven point three eight", "37.38"), ("thirty six point two", "36.2"),
          ("thirty seven point three", "37.3"), ("nought point nought two", "0.02"), ("twenty twenty", "2020"), ("one word", "1 word")]
KEYW = {'haaland', 'frimpong', 'martinelli', 'tchatchoua', 'wolves', 'walker', 'van', 'de', 'ven', 'faster', 'fastest', 'forward',
        'race', 'day', 'everton', 'nobody', 'twist', 'quickest', 'everyone', 'two'}
PAIRS = {('premier', 'league'), ('man', 'city'), ('van', 'de'), ('de', 'ven'), ('right', 'back'), ('race', 'day'), ('kyle', 'walker'),
         ('micky', 'van'), ('erling', 'haaland'), ('jeremie', 'frimpong'), ('gabriel', 'martinelli'), ('jackson', 'tchatchoua'), ('straight', 'race')}
plain = lambda w: re.sub(r"[^\w']", '', w.lower())
toks, i = [], 0
while i < len(words):
    hit = None
    for ph, dg in DIGITS:
        p = ph.split()
        if [plain(x['w']) for x in words[i:i + len(p)]] == p:
            hit = (len(p), dg); break
    if hit:
        n, dg = hit; last = words[i + n - 1]; punct = re.sub(r"^[\w']+", '', last['w'])
        if ' ' in dg: a_, b_ = dg.split(' '); toks.append({'t': a_, 's': words[i]['s'], 'e': words[i]['e'], 'num': True, 'line': words[i]['line']}); toks.append({'t': b_ + punct, 's': last['s'], 'e': last['e'], 'num': False, 'line': last['line']})
        else: toks.append({'t': dg + punct, 's': words[i]['s'], 'e': last['e'], 'num': True, 'line': words[i]['line']})
        i += n
    else:
        w = words[i]; toks.append({'t': w['w'], 's': w['s'], 'e': w['e'], 'num': False, 'line': w['line']}); i += 1
HIDE = [(B['ctx'] - .05, B['l1']), (B['wins'] - .05, B['l3']), (B['twist'] - .05, B['tch'] + 1.2), (B['since'] - .05, B['walker']), (B['ask'] - .05, END + 1)]
hidden = lambda s: any(a <= s < b for a, b in HIDE)
groups, cur = [], []
for j, tk in enumerate(toks):
    if hidden(tk['s']): 
        if cur: groups.append(cur); cur = []
        continue
    cur.append(j)
    nxt = toks[j + 1] if j + 1 < len(toks) else None
    end_p = re.search(r'[.?!,]$', tk['t']) or not nxt or nxt['line'] != tk['line'] or nxt['s'] - tk['e'] > .2
    pair = nxt and (plain(tk['t']), plain(nxt['t'])) in PAIRS
    WEAK = {'a', 'the', 'of', 'in', 'and', 'to', "it's", 'he', 'his', 'is', 'that', 'or', 'but', 'if', 'you', 'since', 'than', 'one'}
    if end_p:
        groups.append(cur); cur = []
    elif len(cur) >= 3 and not pair:
        if plain(toks[cur[-1]]['t']) in WEAK: groups.append(cur[:-1]); cur = cur[-1:]
        else: groups.append(cur); cur = []
if cur: groups.append(cur)
# merge a lonely short word into the next group of the same sentence
merged = []
for g in groups:
    if merged and len(merged[-1]) == 1 and len(toks[merged[-1][0]]['t']) <= 4 and not re.search(r'[.?!,]$', toks[merged[-1][0]]['t']) \
       and len(merged[-1]) + len(g) <= 3 and toks[g[0]]['line'] == toks[merged[-1][0]]['line']:
        merged[-1] += g
    else: merged.append(g)
groups = merged
caps = []
for gi, g in enumerate(groups):
    s = toks[g[0]]['s'] - .06; e = toks[g[-1]]['e'] + .3
    if gi + 1 < len(groups): e = min(e, toks[groups[gi + 1][0]]['s'] - .07)
    e = max(e, s + .4)
    for a, b2 in HIDE:
        if s < a < e: e = a
    spans = []
    for j in g:
        tk = toks[j]; txt = html.escape(tk['t'].strip('"'))
        cls = 'w k' if (tk['num'] or plain(tk['t']) in KEYW) else 'w'
        spans.append(f'<span class="{cls}" data-ws="{round(tk["s"] - s, 3)}">{txt}</span>')
    n_chars = sum(len(toks[j]['t']) + 1 for j in g)
    size = '' if n_chars <= 17 else (' style="font-size:62px"' if n_chars <= 23 else ' style="font-size:54px"')
    caps.append((f'c{gi}', round(max(.12, s), 3), round(e, 3), f'<span class="ln"{size}>' + ' '.join(spans) + '</span>'))

# ---------------- sound effects (crisp, on graphics) ----------------
sfx = [('impact-2', 0.0, .9), ('cinematic-deep-boom', 0.02, .5), ('whoosh-cine', .9, .45),
       ('riser-1', B['ctx'] - 1.0, .4), ('whoosh-2', B['ctx'] - .05, .7),
       ('whoosh-cine', B['l1'] + .2, .55), ('impact-2', B['hNum'], .5),
       ('whoosh-cine', B['l2'] + .2, .55), ('impact-2', B['fNum'], .5),
       ('whoosh-2', B['wins'], .5), ('pop-2', B['wins'] + 1.3, .8), ('impact-2', B['wNum'], .45),
       ('whoosh-cine', B['l3'] + .2, .55), ('impact-2', B['mNum'], .5), ('ding-1', B['quick'], .45),
       ('riser-1', B['twist'] - 1.0, .45), ('tech-glitch-1', B['twist'], .8),
       ('cinematic-deep-boom', B['tch'], .8), ('whoosh-cine', B['tch'] + .5, .6), ('impact-2', B['tNum'], .7), ('cc0-dark-sting', B['tNum'] + .1, .4),
       ('whoosh-2', B['even'], .5), ('impact-2', B['even'] + .9, .45),
       ('whoosh-2', B['since'], .45), ('wood-hit', B['walker'] + .2, .5), ('wood-hit', B['vdv'] + .2, .6), ('impact-2', B['vdvNum'], .6),
       ('whoosh-cine', B['ask'], .5), ('ding-1', B['ask'] + 1.0, .6), ('ding-1', B['nextq'], .5)]
sfx += [('tick-1', B[k] + .1 + j * .12, .28) for k in ('hNum', 'fNum', 'mNum', 'tNum') for j in range(8)]

def clip(id, s, e, cls, inner, track):
    return f'<div id="{id}" class="clip {cls}" data-start="{s}" data-duration="{round(e - s, 3)}" data-track-index="{track}"><div class="in">{inner}</div></div>'

body = '\n'.join(clip(i, s, e, f'ov {k}', h, 2) for i, s, e, h, k in ov)
capb = '\n'.join(clip(i, s, e, 'cap', h, 3) for i, s, e, h in caps)
import subprocess
import subprocess as _sp
def dur(f): return float(_sp.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f"{ROOT}/assets/sfx/{f}.wav"],capture_output=True,text=True).stdout)
aud = '\n'.join(f'<audio id="sfx{n}" class="clip" src="assets/sfx/{f}.wav" data-start="{round(s, 3)}" data-duration="{round(min(dur(f), END - s - .05), 3)}" data-volume="{v}" data-track-index="{10 + n}"></audio>' for n, (f, s, v) in enumerate(sfx))

json.dump({'sfx': sfx, 'beats': B, 'end': END}, open('mix.json', 'w'), indent=1)
page = open('template.html').read()
page = page.replace('MYTH OR FACT?', 'RACE DAY').replace('{{EP}}', json.dumps(EP)).replace('{{END}}', str(END)).replace('{{OVERLAYS}}', body).replace('{{CAPTIONS}}', capb).replace('{{SFX}}', '').replace('{{ENDCARD}}', str(round(END - 1.6, 2)))
open(f'{ROOT}/index.html', 'w').write(page)
json.dump(B, open('beats.json', 'w'), indent=1)
print('end', END, 'overlays', len(ov), 'captions', len(caps), 'sfx', len(sfx))
