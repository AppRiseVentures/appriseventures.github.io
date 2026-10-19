#!/usr/bin/env python3
"""Tells search engines that support IndexNow (Bing, Yandex, Seznam, Naver and others) which pages exist or changed.

    python3 tools/blog/indexnow.py --dry-run     # list the URLs
    python3 tools/blog/indexnow.py               # submit every URL in sitemap.xml

Run it after the site is deployed: engines fetch https://fimbl.app/<key>.txt to check the key, and that file only exists
on the live site once the push has been published. The key is the 32-character hex file name in the repo root.
"""

from __future__ import annotations

import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = json.loads((ROOT / "tools/blog/site.json").read_text())["base"]
HOST = BASE.split("//")[1]


def key() -> str:
    found = [p.stem for p in ROOT.glob("*.txt") if re.fullmatch(r"[0-9a-f]{32}", p.stem)]
    if len(found) != 1:
        sys.exit("Expected exactly one <32-hex-key>.txt in the repo root.")
    return found[0]


def urls() -> list[str]:
    return re.findall(r"<loc>([^<]+)</loc>", (ROOT / "sitemap.xml").read_text())


def main() -> None:
    k, pages = key(), urls()
    print(f"{len(pages)} URLs, key {k[:6]}…")
    if "--dry-run" in sys.argv:
        print("\n".join(pages))
        return
    body = json.dumps({"host": HOST, "key": k, "keyLocation": f"{BASE}/{k}.txt", "urlList": pages}).encode()
    request = urllib.request.Request("https://api.indexnow.org/IndexNow", body, {"Content-Type": "application/json; charset=utf-8"})
    with urllib.request.urlopen(request, timeout=30) as response:
        print("IndexNow answered", response.status, response.reason)


if __name__ == "__main__":
    main()
