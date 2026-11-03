#!/usr/bin/env python3
"""Find a free-licence HD photo of a named football person and print {"path", "credit"} as JSON.

Each call first looks for a photo of that person the account hasn't posted before, recent
photos first (Openverse, then Wikimedia Commons, with backoff on 429s), saves it to
photos/ and returns it. Only when nothing new is available does it fall back to the saved
photos (up to 10 per person, rolling), picking the least used, so the same face isn't
repeated post after post. A file is
accepted only when its title contains every part of the person's full name, so a namesake
or someone else's photo is never used. Recent photos (2024 to 2026) rank higher.

    python3 skills/actxion-visuals/scripts/find_photo.py "Scott Parker" --club "West Ham"

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

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
LIB = os.path.join(ROOT, "photos")
INDEX = os.path.join(LIB, "index.json")
UA = "ACTXION-visuals/1.0 (https://github.com/pvtaddyy/actxion-assets)"
OK_LICENCE = re.compile(r"cc0|public ?domain|pdm|^pd|cc[ -]?by(?![ -]?nc)(?![ -]?nd)", re.I)
MIN_LONG = 800  # our photo panels are under 1000px wide; bigger files still rank higher
# A namesake from music, art or another sport is the common wrong match, so the file's
# title, categories or tags must also say football.
FOOTBALL = re.compile(r"football|soccer|futbol|fútbol|calcio|fussball|fußball|\bf\.?c\b|league|liga|serie a|"
                      r"bundesliga|uefa|fifa|cup|national team|manager|coach|united|city|stadium|stadion|estadio|"
                      r"world cup|euro 20|premier|footballer|\\b(?:cf|afc|fk|sc|ac|ssc|bv|vfb|rb)\\b|real madrid|atletico|barcelona|juventus|"
                      r"bayern|olympique|paris saint|arsenal|chelsea|liverpool|tottenham|hotspur|inter |milan|napoli|roma\\b|lazio", re.I)
MAX_VARIANTS = 10
# Whole-call budget: a desk run can't wait minutes for a busy API
DEADLINE = time.time() + 40


def norm(s):
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


def blocked(url):
    """Files we've caught as the wrong person or unlicensed: photos/blocklist.txt, one fragment per line."""
    try:
        with open(os.path.join(LIB, "blocklist.txt")) as f:
            frags = [l.strip() for l in f if l.strip() and not l.startswith("#")]
    except FileNotFoundError:
        return False
    return any(fr in url for fr in frags)


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
    args, club = sys.argv[1:], ""
    if "--club" in args:
        i = args.index("--club")
        club = " ".join(args[i + 1:i + 2])
        args = args[:i] + args[i + 2:]
    name = " ".join(a for a in args if not a.startswith("--")).strip()
    idx = load_index()
    entry = idx.get(slug(name)) or {"name": name, "variants": []}
    entry["variants"] = [v for v in entry["variants"] if os.path.exists(os.path.join(ROOT, v["file"]))]
    # Every call looks for a photo this account hasn't posted yet, newest uploads first.
    # The saved photos are only the fallback for when the APIs refuse the cloud machine.
    fresh = "--no-new" not in sys.argv and add_variant(name, entry, 3 if not entry["variants"] else 2, club)
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
