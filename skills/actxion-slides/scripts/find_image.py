#!/usr/bin/env python3
"""Find free-licensed photos on Wikimedia Commons for an ACTXION X post.

Usage: python3 -I find_image.py "Michael Carrick"   (full name or place)
Prints up to 8 HD images (>=2000px), newest first: licence | credit | size | year | url | file title
Every name word must appear in the file title. Still read the title before using it.
Only licences that allow reuse with credit are returned (CC0, PD, CC BY, CC BY-SA).
"""
import html
import json
import re
import sys
import unicodedata
import urllib.parse
import urllib.request

OK_LICENCES = ("cc0", "public domain", "pd", "cc by ", "cc by-sa", "cc-by", "cc by 2", "cc by 3", "cc by 4")
UA = "ACTXION-desk/1.0 (https://github.com/pvtaddyy/actxion-assets)"


def search(query, limit=40):
    params = {
        "action": "query", "format": "json", "generator": "search",
        "gsrnamespace": "6", "gsrsearch": f"{query} filetype:bitmap", "gsrlimit": str(limit),
        "prop": "imageinfo", "iiprop": "url|size|extmetadata", "iiurlwidth": "2560",
    }
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r).get("query", {}).get("pages", {}).values()


def fold(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()


def plain(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()


def main():
    query = " ".join(sys.argv[1:]).strip()
    if not query:
        sys.exit("usage: find_image.py <search terms>")
    # Every name word (3+ letters) must be in the file title, so we never attach the wrong person
    must = [w for w in re.findall(r"[a-z0-9]+", fold(query)) if len(w) >= 3]
    rows = []
    for p in search(query):
        title = fold(p["title"])
        if not all(w in title for w in must):
            continue
        ii = p["imageinfo"][0]
        m = ii.get("extmetadata", {})
        lic = plain(m.get("LicenseShortName", {}).get("value", ""))
        if not lic.lower().startswith(OK_LICENCES) and lic.lower() not in OK_LICENCES:
            continue
        w, h = ii.get("width", 0), ii.get("height", 0)
        # HD only: at least 2000px on the long side, and not a tall sliver
        if max(w, h) < 2000 or min(w, h) < 1200 or h > w * 1.6:
            continue
        url = (ii.get("thumburl") or ii["url"]).split("?")[0]
        artist = plain(m.get("Artist", {}).get("value", "")) or "Unknown"
        date = plain(m.get("DateTimeOriginal", {}).get("value", "")) or plain(m.get("DateTime", {}).get("value", ""))
        year = next((int(y) for y in re.findall(r"(?:19|20)\d\d", date)), 0)
        landscape = 1 if w >= h else 0
        # Newest first, then landscape, then resolution
        rows.append(((year, landscape, w * h), f"{lic} | 📸 {artist[:60]} / Wikimedia Commons ({lic}) | {w}x{h} | {year or '?'} | {url} | {p['title']}"))
    if not rows:
        print("NO_FREE_IMAGE")
        return
    for _, line in sorted(rows, reverse=True)[:8]:
        print(line)


if __name__ == "__main__":
    main()
