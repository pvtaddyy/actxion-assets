#!/usr/bin/env python3
"""Find a free-licence HD photo of a named football person and print {"path", "credit"} as JSON.

Each call first looks for a photo of that person the account hasn't posted before, recent
photos first (Openverse, then Wikimedia Commons, with backoff on 429s), saves it to
photos/ and returns it. Only when nothing new is available does it fall back to the saved
photos (up to 10 per person, rolling), picking the least used, so the same face isn't
repeated post after post. A file is
accepted only when its title contains every part of the person's full name, so a namesake
or someone else's photo is never used. Recent photos (2024 to 2026) rank higher.

    python3 skills/actxion-visuals/scripts/find_photo.py "Scott Parker" --club "West Ham" --article <story URL>

--article (repeatable) takes the news article the story came from; its lead photo is used first.
Then the photo on the person's own Wikipedia page (always the right person, used once), then
recent news articles that name the person (Bing News; check these, they can show a team-mate),
then Openverse and Commons, then the saved library. Logos and title graphics are skipped. --no-search skips the news search.
To reject a photo, add its article URL or file name to photos/blocklist.txt and run again.

--club takes the club or national team in the story; "name + club" is searched first,
which finds the right person in one go.
Exit code 1 and {"path": null} when nothing qualifies.
"""
import json
import os
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request

try:
    from PIL import Image
except ImportError:  # the graphic check is skipped without Pillow
    Image = None

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
LIB = os.path.join(ROOT, "photos")
INDEX = os.path.join(LIB, "index.json")
UA = "ACTXION-visuals/1.0 (https://github.com/pvtaddyy/actxion-assets)"
# "Attribution" alone is Commons' plain credit-only licence
OK_LICENCE = re.compile(r"cc0|public ?domain|pdm|^pd|cc[ -]?by(?![ -]?nc)(?![ -]?nd)|^attribution$", re.I)
MIN_LONG = 800  # our photo panels are under 1000px wide; bigger files still rank higher
# A namesake from music, art or another sport is the common wrong match, so the file's
# title, categories or tags must also say football.
FOOTBALL = re.compile(r"football|soccer|futbol|fútbol|calcio|fussball|fußball|\bf\.?c\b|league|liga|serie a|"
                      r"bundesliga|uefa|fifa|cup|national team|manager|coach|united|city|stadium|stadion|estadio|"
                      r"world cup|euro 20|premier|footballer|\\b(?:cf|afc|fk|sc|ac|ssc|bv|vfb|rb)\\b|real madrid|atletico|barcelona|juventus|"
                      r"bayern|olympique|paris saint|arsenal|chelsea|liverpool|tottenham|hotspur|inter |milan|napoli|roma\\b|lazio", re.I)
MAX_VARIANTS = 10
SOLO_ONLY = False  # set for the small-photo pass, where a crop can land on the other person
# Whole-call budget: a desk run can't wait minutes for a busy API
DEADLINE = time.time() + 55


def norm(s):
    # Letters NFKD can't split into a base letter (Turkish ı, Nordic ø, German ß) are mapped by hand
    s = s.translate(str.maketrans({"ı": "i", "İ": "I", "ø": "o", "Ø": "O", "ß": "ss", "ł": "l", "Ł": "L", "đ": "d", "æ": "ae"}))
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9 ]+", " ", s.lower())


def name_match(name, title):
    # The full name as one phrase, in order: "Frank Thomas" is not "Thomas Frank"
    return f" {' '.join(norm(name).split())} " in f" {' '.join(norm(title).split())} "


def slug(name):
    return re.sub(r"\s+", "-", norm(name).strip())


def get(url, tries=2, binary=False):
    wait = 2
    for _ in range(tries):
        left = DEADLINE - time.time()
        if left < 3:
            return None
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=min(15, left)) as r:
                data = r.read()
                return data if binary else json.loads(data)
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503, 504):
                return None
        except Exception:
            pass
        time.sleep(min(wait, max(0, DEADLINE - time.time() - 3)))
        wait *= 2
    return None


def load_index():
    try:
        with open(INDEX) as f:
            idx = json.load(f)
    except Exception:
        return {}
    for k, e in idx.items():  # older entries held a single file
        if "variants" not in e:
            idx[k] = {"name": e["name"], "variants": [{"file": e["file"], "credit": e["credit"], "url": e.get("url", ""), "used": 0}]}
    return idx


def write_index(idx):
    os.makedirs(LIB, exist_ok=True)
    with open(INDEX, "w") as f:
        json.dump(idx, f, indent=1, ensure_ascii=False, sort_keys=True)


def score(title, w, h, name=""):
    # Close single-subject portraits and recent photos win; other people's names, "A & B" and "A v B" lose
    # "A & B" or "A and B" is a two-person shot; "France v Spain" is just the match name
    crowd = len(re.findall(r"&|,| and | with ", title))
    words = set(norm(name).split())
    extra = [x for x in re.findall(r"\b[A-Z][a-z\u00c0-\u017f]+", title) if norm(x).strip() not in words]
    bonus = 600 if re.search(r"crop|portrait|headshot", title, re.I) else 0
    year = max([int(y) for y in re.findall(r"20[12]\d", title)] or [0])
    bonus += {2026: 500, 2025: 400, 2024: 200}.get(year, 0)
    return min(w, h, 2400) - crowd * 900 - len(extra) * 120 + bonus + (300 if h >= w else 0)


def club_hit(club, text):
    """Small bonus when the photo's text names the club. Kept small: signing-day shots carry the
    club name and are often club photos re-uploaded without a real licence."""
    return 250 if club and f" {' '.join(norm(club).split())} " in f" {' '.join(norm(text).split())} " else 0


def queries(name, club):
    # "Name + club" first: it lands on the right person in one search
    return [f'intitle:"{name}" {club}', f'intitle:"{name}"'] if club else [f'intitle:"{name}"']


def from_openverse(name, tries, club=""):
    out, seen = [], set()
    for query in queries(name, club):
        q = urllib.parse.quote(query.replace("intitle:", ""))
        d = get(f"https://api.openverse.org/v1/images/?q={q}&license_type=commercial&page_size=40", tries)
        for r in (d or {}).get("results", []):
            w, h = r.get("width") or 0, r.get("height") or 0
            lic = f"{r.get('license', '')} {r.get('license_version', '')}"
            if SOLO_ONLY and re.search(r"&|,| and | with ", r.get("title", "")):
                continue
            if r["url"] in seen or max(w, h) < MIN_LONG or not name_match(name, r.get("title", "")) \
                    or not OK_LICENCE.search(lic.replace("by-sa", "by sa")):
                continue
            text = f"{r.get('title', '')} " + " ".join(t.get("name", "") for t in r.get("tags") or [])
            if not (FOOTBALL.search(text) or club_hit(club, text)):
                continue
            seen.add(r["url"])
            credit = f"Photo: {r.get('creator') or 'unknown'}, {r.get('source', 'Openverse').title()}, CC {lic.upper().strip()}"
            out.append((score(r["title"], w, h, name) + club_hit(club, text), r["url"],
                        credit.replace("CC CC0", "CC0").replace("CC PDM", "Public domain")))
        if len(out) >= 5:  # enough from "name + club"; otherwise widen to the name alone
            break
    return sorted(out, reverse=True)


def from_commons(name, tries, club=""):
    out, seen = [], set()
    for query in queries(name, club):
        q = urllib.parse.quote(query)
        d = get("https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search"
                f"&gsrnamespace=6&gsrlimit=50&gsrsearch={q}&prop=imageinfo&iiprop=url|size|extmetadata&iiurlwidth=1920", tries)
        for p in ((d or {}).get("query") or {}).get("pages", {}).values():
            i = p["imageinfo"][0]
            m = i.get("extmetadata", {})
            lic = m.get("LicenseShortName", {}).get("value", "")
            url = i.get("thumburl") or i["url"]
            if SOLO_ONLY and re.search(r"&|,| and | with ", p["title"]):
                continue
            if url in seen or max(i["width"], i["height"]) < MIN_LONG or not name_match(name, p["title"]) or not OK_LICENCE.search(lic):
                continue
            text = f"{p['title']} {m.get('Categories', {}).get('value', '')} {m.get('ImageDescription', {}).get('value', '')}"
            if not (FOOTBALL.search(text) or club_hit(club, text)):
                continue
            seen.add(url)
            art = re.sub("<[^>]+>", "", m.get("Artist", {}).get("value", "")).strip()[:40] or "unknown"
            out.append((score(p["title"], i["width"], i["height"], name) + club_hit(club, text), url,
                        f"Photo: {art}, Wikimedia Commons, {lic}"))
        if len(out) >= 5:  # enough from "name + club"; otherwise widen to the name alone
            break
    return sorted(out, reverse=True)


def face_ok(data):
    """True when the photo has a clear, close face. Rejects rooms, crowds and far-away figures.

    Used only to rank candidates. Without OpenCV installed every photo counts as fine."""
    try:
        import cv2
        cv2.CascadeClassifier  # OpenCV 5 moved it out; 4.x has it
    except (ImportError, AttributeError):
        return True
    import numpy as np
    img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_GRAYSCALE)
    if img is None:
        return False
    scale = 1000 / max(img.shape)
    img = cv2.resize(img, None, fx=scale, fy=scale)
    front = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    side = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_profileface.xml")
    sizes = [f[3] for f in front.detectMultiScale(img, 1.1, 6, minSize=(30, 30))]
    sizes += [f[3] for im in (img, cv2.flip(img, 1)) for f in side.detectMultiScale(im, 1.1, 6, minSize=(30, 30))]
    # A close face (12% of the short side) passes; three similar big faces is a group shot
    big = [s for s in sizes if s >= min(img.shape) * 0.12]
    if 1 <= len(big) <= 3 and not (len(big) == 3 and min(big) > max(big) * 0.6):
        return True
    return False


def is_graphic(im):
    """True for logos, title cards and 'Paper Talk' style graphics: few colours, big flat areas.
    A real photo of a person has thousands of colours and no one colour covering a third of it."""
    if Image is None:
        return False
    small = im.convert("RGB").resize((96, 96))
    q = small.quantize(colors=64)
    counts = sorted((c for c, _ in q.getcolors(96 * 96) or []), reverse=True)
    distinct = len(small.getcolors(96 * 96) or [])
    return bool(counts and counts[0] > 0.30 * 96 * 96) or distinct < 900


def blocked(url):
    """Files we've caught as the wrong person or unlicensed: photos/blocklist.txt, one fragment per line."""
    try:
        with open(os.path.join(LIB, "blocklist.txt")) as f:
            frags = [l.strip() for l in f if l.strip() and not l.startswith("#")]
    except FileNotFoundError:
        return False
    return any(fr in url for fr in frags)


BROWSER_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
AGENCY = re.compile(r"getty|\bpa\b|press association|reuters|\bap\b|associated press|afp|imago|offside|shutterstock|"
                    r"epa|alamy|action images|camera press|sportsfile|ansa|lapresse|dpa", re.I)


def from_article(url):
    """The lead photo of the news article the story came from: real-time and about this story.

    Returns (image bytes, credit) or None. Section pages and logos are skipped."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": BROWSER_UA, "Accept-Language": "en-GB,en"})
        with urllib.request.urlopen(req, timeout=max(3, min(15, DEADLINE - time.time()))) as r:
            html = r.read(800_000).decode("utf-8", "ignore")
    except Exception:
        return None
    def meta(*names):
        for n in names:
            m = re.search(r'<meta[^>]+(?:property|name)=["\']%s["\'][^>]*content=["\']([^"\']+)' % re.escape(n), html, re.I) \
                or re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]*(?:property|name)=["\']%s["\']' % re.escape(n), html, re.I)
            if m:
                return m.group(1).replace("&amp;", "&")
        return ""
    img = meta("og:image", "twitter:image", "twitter:image:src")
    if not img or re.search(r"logo|placeholder|default|misc_logos|favicon|paper-?talk|graphic|badge|crest", img, re.I):
        return None
    if blocked(url) or blocked(img):
        return None
    data = get(urllib.parse.urljoin(url, img), 2, binary=True)
    if not data or not (data[:3] == b"\xff\xd8\xff" or data[:8] == b"\x89PNG\r\n\x1a\n" or data[:4] == b"RIFF"):
        return None
    try:
        import io
        from PIL import Image
        im = Image.open(io.BytesIO(data))
        if max(im.size) < 800 or is_graphic(im):
            return None
        if data[:4] == b"RIFF":  # webp: store as jpeg so the renderer and Metricool both take it
            buf = io.BytesIO()
            im.convert("RGB").save(buf, "JPEG", quality=92)
            data = buf.getvalue()
    except ImportError:
        pass
    site = meta("og:site_name") or urllib.parse.urlparse(url).netloc.replace("www.", "")
    text = " ".join([meta("og:image:alt", "twitter:image:alt")] + re.findall(r"<figcaption[^>]*>(.*?)</figcaption>", html, re.I | re.S)[:3])
    agency = AGENCY.search(re.sub("<[^>]+>", " ", text))
    credit = f"Photo: {agency.group(0).title() if agency else site} via {site}" if agency else f"Photo: {site}"
    return data, credit


def from_wikipedia(name, tries=2, club=""):
    """The lead photo on the person's own Wikipedia page: always the right person.

    Returns (score, url, credit) candidates; the page whose intro names the club ranks first."""
    q = urllib.parse.quote(f"{name} footballer {club}".strip())
    d = get("https://en.wikipedia.org/w/api.php?action=query&format=json&generator=search"
            f"&gsrsearch={q}&gsrlimit=5&prop=pageimages|extracts&exintro=1&explaintext=1&exlimit=5"
            "&piprop=original|name&pilicense=free", tries)
    out = []
    for p in ((d or {}).get("query") or {}).get("pages", {}).values():
        o, intro = p.get("original"), p.get("extract", "")
        if not o or not (name_match(name, p["title"]) or name_match(name, intro[:300])):
            continue
        if not FOOTBALL.search(intro[:600]) or max(o["width"], o["height"]) < 600:
            continue
        sc = 1000 - p.get("index", 5) * 100 + club_hit(club, intro) * 4
        out.append((sc, o["source"].split("?")[0], p.get("pageimage", "")))
    out.sort(reverse=True)
    res = []
    for sc, url, fname in out[:1]:  # only the best-matching page: a second "Rodri" is someone else
        credit = "Photo: Wikimedia Commons"
        info = get("https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=imageinfo"
                   f"&iiprop=extmetadata&titles=File:{urllib.parse.quote(fname)}", 1)
        for pg in ((info or {}).get("query") or {}).get("pages", {}).values():
            m = (pg.get("imageinfo") or [{}])[0].get("extmetadata", {})
            lic = m.get("LicenseShortName", {}).get("value", "")
            art = re.sub("<[^>]+>", "", m.get("Artist", {}).get("value", "")).strip()[:40]
            if art or lic:
                credit = f"Photo: {art or 'unknown'}, Wikimedia Commons, {lic}".rstrip(", ")
        res.append((sc, url, credit))
    return res


def news_articles(name, club=""):
    """Recent news articles about the person (Bing News RSS), so a fresh lead photo can be used
    when the story's own article had none. Only articles whose headline names the person."""
    q = urllib.parse.quote(f'"{name}" {club}'.strip())
    try:
        req = urllib.request.Request(f"https://www.bing.com/news/search?q={q}&format=rss&setlang=en-gb",
                                     headers={"User-Agent": BROWSER_UA})
        with urllib.request.urlopen(req, timeout=max(3, min(10, DEADLINE - time.time()))) as r:
            xml = r.read(400_000).decode("utf-8", "ignore")
    except Exception:
        return []
    last = norm(name).split()[-1]
    out = []
    for item in re.findall(r"<item>(.*?)</item>", xml, re.S):
        t = re.search(r"<title>(.*?)</title>", item, re.S)
        l = re.search(r"<link>(.*?)</link>", item, re.S)
        if not t or not l or f" {last} " not in f" {norm(t.group(1))} ":
            continue
        link = l.group(1).replace("&amp;", "&")
        u = urllib.parse.parse_qs(urllib.parse.urlparse(link).query).get("url", [link])[0]
        if "msn.com" in u:  # MSN pages are script-only, no lead photo in the HTML
            continue
        out.append(u)
    return out[:6]


def add_variant(name, entry, tries, club=""):
    """Download the best candidate not already in the library. Returns True if one was added.

    Candidates with a clear close face go first; if none of the top ten has one, the best
    remaining photo is used rather than nothing (the desk still checks it by eye)."""
    have = {v.get("url") for v in entry["variants"]}
    for finder in (from_openverse, from_commons):
        fallback = None
        for _, url, credit in finder(name, tries, club)[:4]:
            if DEADLINE - time.time() < 5:
                break
            if url in have or blocked(url):
                continue
            data = get(url, tries, binary=True)
            if not data or not (data[:3] == b"\xff\xd8\xff" or data[:8] == b"\x89PNG\r\n\x1a\n"):
                continue
            if face_ok(data):
                return keep(name, entry, data, url, credit)
            fallback = fallback or (data, url, credit)
        if fallback:
            return keep(name, entry, *fallback)
    return False


def keep(name, entry, data, url, credit):
    n = len(entry["variants"]) + 1
    path = os.path.join(LIB, f"{slug(name)}{'' if n == 1 else '-' + str(n)}.jpg")
    while os.path.exists(path):
        n += 1
        path = os.path.join(LIB, f"{slug(name)}-{n}.jpg")
    os.makedirs(LIB, exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    entry["variants"].append({"file": os.path.relpath(path, ROOT), "credit": credit, "url": url, "used": 0})
    return True


def main():
    args, club, articles = sys.argv[1:], "", []
    for flag in ("--club", "--article"):
        while flag in args:
            i = args.index(flag)
            if flag == "--club":
                club = " ".join(args[i + 1:i + 2])
            else:
                articles += args[i + 1:i + 2]
            args = args[:i] + args[i + 2:]
    name = " ".join(a for a in args if not a.startswith("--")).strip()
    idx = load_index()
    entry = idx.get(slug(name)) or {"name": name, "variants": []}
    entry["variants"] = [v for v in entry["variants"] if os.path.exists(os.path.join(ROOT, v["file"]))]
    # The story's own article photo comes first: it is real-time and about exactly this story
    def article_photo(urls):
        for url in urls:
            if DEADLINE - time.time() < 12:
                return None
            found = from_article(url)
            if found:
                return url, found
        return None

    def done(v, source):
        idx[slug(name)] = entry
        write_index(idx)
        print(json.dumps({"path": os.path.join(ROOT, v["file"]), "credit": v["credit"], "source": source}))
        return 0

    new_ok = "--no-new" not in sys.argv
    hit = article_photo(articles)
    # No usable photo in the story's article: the person's own Wikipedia photo is next, because it is
    # always the right person. Other outlets' articles can lead with the manager or a team-mate.
    if not hit and new_ok:
        have = {v.get("url") for v in entry["variants"]}
        for _, url, credit in from_wikipedia(name, 2, club):
            if url in have or blocked(url):
                continue
            data = get(url, 2, binary=True)
            if data and (data[:3] == b"\xff\xd8\xff" or data[:8] == b"\x89PNG\r\n\x1a\n"):
                keep(name, entry, data, url, credit)
                entry["variants"][-1]["used"] = 1
                return done(entry["variants"][-1], "wikipedia")
    if not hit and new_ok and "--no-search" not in sys.argv:
        hit = article_photo([u for u in news_articles(name, club) if u not in articles])
    for url, found in [hit] if hit else []:
        if found:
            keep(name, entry, found[0], url, found[1])
            entry["variants"][-1]["source"] = "article"
            entry["variants"][-1]["article"] = url
            entry["variants"][-1]["used"] = 1
            idx[slug(name)] = entry
            write_index(idx)
            v = entry["variants"][-1]
            print(json.dumps({"path": os.path.join(ROOT, v["file"]), "credit": v["credit"], "source": "article"}))
            return 0
    # Otherwise look for a free photo this account hasn't posted yet, recent ones first.
    # The saved photos are only the fallback for when the APIs refuse the cloud machine.
    fresh = "--no-new" not in sys.argv and add_variant(name, entry, 3 if not entry["variants"] else 2, club)
    if not fresh and not entry["variants"] and "--no-new" not in sys.argv:
        # Some players have no big free photo yet; a 600px one still works on the smaller panels
        global MIN_LONG, SOLO_ONLY
        MIN_LONG, SOLO_ONLY = 600, True
        fresh = add_variant(name, entry, 2, club)
    if len(entry["variants"]) > MAX_VARIANTS:  # rolling library: drop the most-used, oldest photo
        old = max(entry["variants"][:-1], key=lambda v: (v["used"], -entry["variants"].index(v)))
        entry["variants"].remove(old)
    if not entry["variants"]:
        print(json.dumps({"path": None, "credit": None}))
        return 1
    pick = entry["variants"][-1] if fresh else min(entry["variants"], key=lambda v: (v["used"], -entry["variants"].index(v)))
    pick["used"] += 1
    idx[slug(name)] = entry
    write_index(idx)
    print(json.dumps({"path": os.path.join(ROOT, pick["file"]), "credit": pick["credit"], "variants": len(entry["variants"])}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
