#!/usr/bin/env python3
"""Builds the Fimbl blog in English, Finnish and German.

Writes the post pages, the three blog indexes, an RSS feed per language, sitemap.xml and llms.txt from
tools/blog/site.json (shared strings per language) and tools/blog/content/<lang>/<post>.json + .html.
The output is plain HTML that gets committed, so GitHub Pages still serves the site without a build step.

    python3 tools/blog/build.py          # pages, feeds, sitemap, llms.txt
    python3 tools/blog/build.py --og     # also renders the covers and 1200x630 share images (Google Chrome, cwebp)

Placeholders in article HTML: {img} = /assets/img/app/<lang>, {home} and {blog} = the language's home and
blog, {post:<id>} = another post in the same language, {store} = the App Store link.
"""

from __future__ import annotations

import html
import json
import re
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOL = Path(__file__).resolve().parent
SITE = json.loads((TOOL / "site.json").read_text())
BASE = SITE["base"]
LANGS = list(SITE["languages"])
STORE = SITE["store"]
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
WPM = {"en": 230, "fi": 170, "de": 200}

esc = html.escape


def attr(value: str) -> str:
    return html.escape(value, quote=True)


def strip_tags(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", value))).strip()


def load_posts() -> dict[str, dict[str, dict]]:
    """posts[id][lang] = metadata with "body" (article HTML)."""
    posts: dict[str, dict[str, dict]] = {}
    for lang in LANGS:
        for meta_path in sorted((TOOL / "content" / lang).glob("*.json")):
            body_path = meta_path.with_suffix(".html")
            if not body_path.exists():
                print(f"warning: {body_path.relative_to(ROOT)} is missing, skipping that translation", file=sys.stderr)
                continue
            meta = json.loads(meta_path.read_text())
            meta["lang"] = lang
            meta["body"] = body_path.read_text()
            meta["path"] = SITE["languages"][lang]["blog"] + meta["slug"] + "/"
            posts.setdefault(meta["id"], {})[lang] = meta
    order = SITE["order"]
    return {pid: posts[pid] for pid in sorted(posts, key=lambda p: order.index(p) if p in order else 99)}


def url(path: str) -> str:
    return BASE + path


def iso(day: str) -> str:
    return f"{day}T08:00:00+03:00"


def nice_date(day: str, lang: str) -> str:
    d = date.fromisoformat(day)
    months = SITE["languages"][lang]["months"]
    return {"en": f"{months[d.month - 1]} {d.day}, {d.year}", "fi": f"{d.day}. {months[d.month - 1]} {d.year}", "de": f"{d.day}. {months[d.month - 1]} {d.year}"}[lang]


def fill(text: str, lang: str, posts: dict) -> str:
    L = SITE["languages"][lang]
    text = text.replace("{img}", f"/assets/img/app/{lang}").replace("{home}", L["home"]).replace("{blog}", L["blog"]).replace("{store}", STORE)

    def post_link(match: re.Match) -> str:
        return posts[match.group(1)][lang]["path"]

    return re.sub(r"\{post:([a-z0-9-]+)\}", post_link, text)


def reading_minutes(meta: dict) -> int:
    words = len(strip_tags(meta["body"]).split()) + sum(len(strip_tags(f["q"] + " " + f["a"]).split()) for f in meta.get("faq", []))
    meta["word_count"] = words
    return max(3, round(words / WPM[meta["lang"]]))


# ---------- Shared chrome ----------

SPRITE = """<svg width="0" height="0" style="position:absolute" aria-hidden="true">
    <symbol id="i-mark" viewBox="100 96 360 391"><path fill="currentColor" d="M100 254.874C100 167.13 171.13 96 258.874 96C259.752 96 260.463 96.7113 260.463 97.5887V426.199C260.463 454.484 260.463 468.626 251.676 477.412C242.889 486.199 228.747 486.199 200.463 486.199H111.365C105.088 486.199 100 481.111 100 474.834V254.874Z"/><path fill="currentColor" d="M303.114 96C389.76 96 460 166.24 460 252.886C460 255.486 457.893 257.593 455.293 257.593L346.477 257.593C318.192 257.593 304.05 257.593 295.263 248.806C286.477 240.019 286.477 225.877 286.477 197.593L286.477 97.718C286.477 96.7692 287.246 96 288.195 96L303.114 96Z"/><circle fill="currentColor" cx="373.2" cy="371.9" r="79.4"/></symbol>
    <symbol id="i-apple" viewBox="0 0 24 24"><path fill="currentColor" d="M12.152 6.896c-.948 0-2.415-1.078-3.96-1.04-2.04.027-3.91 1.183-4.961 3.014-2.117 3.675-.546 9.103 1.519 12.09 1.013 1.454 2.208 3.09 3.792 3.039 1.52-.065 2.09-.987 3.935-.987 1.831 0 2.35.987 3.96.948 1.637-.026 2.676-1.48 3.676-2.948 1.156-1.688 1.636-3.325 1.662-3.415-.039-.013-3.182-1.221-3.22-4.857-.026-3.04 2.48-4.494 2.597-4.559-1.429-2.09-3.623-2.324-4.39-2.376-2-.156-3.675 1.09-4.61 1.09zM15.53 3.83c.843-1.012 1.4-2.427 1.245-3.83-1.207.052-2.662.805-3.532 1.818-.78.896-1.454 2.338-1.273 3.714 1.338.104 2.715-.688 3.559-1.701"/></symbol>
    <symbol id="i-check" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" d="m5 12.5 4.5 4.5L19 7.5"/></symbol>
    <symbol id="i-x" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" d="M7 7l10 10M17 7 7 17"/></symbol>
    <symbol id="i-minus" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" d="M6.5 12h11"/></symbol>
    <symbol id="i-info" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 11v5.5M12 7.6v.01" stroke-width="2.2"/></g></symbol>
    <symbol id="i-utensils" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M6 3v6a2 2 0 0 0 4 0V3M8 11v10"/><path d="M18 21V3c-2.2 1.4-3.5 4-3.5 7.2V13H18"/></g></symbol>
    <symbol id="i-smile" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M8.5 14.2s1.3 1.8 3.5 1.8 3.5-1.8 3.5-1.8M9 9.5h.01M15 9.5h.01" stroke-width="2"/></g></symbol>
    <symbol id="i-leaf" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M5 19.5C4.5 10.5 10 4.5 20 4.5c0 9.5-5.5 15-14.5 15H5Z"/><path d="M5 19.5 13 11.5"/></g></symbol>
    <symbol id="i-sparkle" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"><path d="m11 3 1.9 5.1L18 10l-5.1 1.9L11 17l-1.9-5.1L4 10l5.1-1.9L11 3Z"/><path d="m18.5 15 .9 2.1 2.1.9-2.1.9-.9 2.1-.9-2.1-2.1-.9 2.1-.9.9-2.1Z"/></g></symbol>
    <symbol id="i-search" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.8-3.8"/></g></symbol>
    <symbol id="i-barcode" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M3 7.5V6a3 3 0 0 1 3-3h1.5M16.5 3H18a3 3 0 0 1 3 3v1.5M21 16.5V18a3 3 0 0 1-3 3h-1.5M7.5 21H6a3 3 0 0 1-3-3v-1.5M7.5 8v8M10.5 8v8M13.5 8v8M16.5 8v8"/></g></symbol>
    <symbol id="i-camera" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"><path d="M4.5 8H7l1.8-2.6c.2-.3.5-.4.8-.4h4.8c.3 0 .6.1.8.4L17 8h2.5A1.5 1.5 0 0 1 21 9.5v8a1.5 1.5 0 0 1-1.5 1.5h-15A1.5 1.5 0 0 1 3 17.5v-8A1.5 1.5 0 0 1 4.5 8Z"/><circle cx="12" cy="13.2" r="3.4"/></g></symbol>
    <symbol id="i-mic" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5.5 11a6.5 6.5 0 0 0 13 0M12 17.5V21"/></g></symbol>
    <symbol id="i-heart" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" d="M12 20s-7.5-4.6-7.5-10.3A4.2 4.2 0 0 1 12 7.2a4.2 4.2 0 0 1 7.5 2.5C19.5 15.4 12 20 12 20Z"/></symbol>
    <symbol id="i-widgets" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3.5" y="3.5" width="7.5" height="7.5" rx="2.2"/><rect x="13" y="3.5" width="7.5" height="7.5" rx="3.75"/><rect x="3.5" y="13" width="17" height="7.5" rx="2.2"/></g></symbol>
    <symbol id="i-link" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 0 0-5.7 0l-3 3A4 4 0 0 0 11 18.7l1-1"/></g></symbol>
    <symbol id="i-chat" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" d="M20 12a8 8 0 0 1-11.6 7.1L4 20l1-4A8 8 0 1 1 20 12Z"/></symbol>
    <symbol id="i-lock" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><rect x="5" y="10.5" width="14" height="10" rx="3"/><path d="M8.5 10.5V8a3.5 3.5 0 0 1 7 0v2.5"/></g></symbol>
    <symbol id="i-globe" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.6 3.8 5.6 3.8 9S14.5 18.4 12 21c-2.5-2.6-3.8-5.6-3.8-9S9.5 5.6 12 3Z"/></g></symbol>
    <symbol id="i-swap" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" d="M4 8h13l-3-3M20 16H7l3 3"/></symbol>
    <symbol id="i-bookmark" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" d="M7 4h10a1 1 0 0 1 1 1v15l-6-4-6 4V5a1 1 0 0 1 1-1Z"/></symbol>
    <symbol id="i-wave" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" d="M4 11v2M7.5 8v8M11 5v14M14.5 9v6M18 7v10M21 11v2"/></symbol>
    <symbol id="i-eye" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"><path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12Z"/><circle cx="12" cy="12" r="3"/></g></symbol>
    <symbol id="i-shield" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3.5 5 6v5.5c0 4.2 2.9 7.6 7 9 4.1-1.4 7-4.8 7-9V6l-7-2.5Z"/><path d="m9 12 2.2 2.2L15.2 10"/></g></symbol>
    <symbol id="i-pause" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M10 9v6M14 9v6" stroke-width="2.2"/></g></symbol>
    <symbol id="i-moon" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" d="M19.5 14.5A8 8 0 0 1 9.5 4.5a8 8 0 1 0 10 10Z"/></symbol>
    <symbol id="i-clock" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/></g></symbol>
    <symbol id="i-chart" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" d="M4 19h16M6.5 15l4-4.5 3 3L19 7"/></symbol>
  </svg>"""


def head(L: dict, *, title: str, description: str, path: str, alternates: dict[str, str], og: dict, extra: str = "", feed: str | None = None) -> str:
    lang = L["code"]
    alt_links = "\n".join(f'  <link rel="alternate" hreflang="{code}" href="{url(p)}">' for code, p in alternates.items())
    alt_links += f'\n  <link rel="alternate" hreflang="x-default" href="{url(alternates["en"])}">'
    og_alt = "\n".join(f'  <meta property="og:locale:alternate" content="{SITE["languages"][c]["locale"]}">' for c in alternates if c != lang)
    feed_link = f'\n  <link rel="alternate" type="application/rss+xml" title="{attr(L["feed_title"])}" href="{feed}">' if feed else ""
    og_extra = "".join(f'\n  <meta property="{k}" content="{attr(v)}">' for k, v in og.get("extra", []))
    return f"""<!doctype html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{esc(title)}</title>
  <meta name="description" content="{attr(description)}">
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
  <link rel="canonical" href="{url(path)}">
{alt_links}{feed_link}
  <meta name="theme-color" content="#f7f5fd">
  <meta name="apple-itunes-app" content="app-id=6443701726">

  <meta property="og:type" content="{og['type']}">
  <meta property="og:site_name" content="Fimbl">
  <meta property="og:locale" content="{L['locale']}">
{og_alt}
  <meta property="og:url" content="{url(path)}">
  <meta property="og:title" content="{attr(og['title'])}">
  <meta property="og:description" content="{attr(og.get('description', description))}">
  <meta property="og:image" content="{url(og['image'])}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="{attr(og['image_alt'])}">{og_extra}
  <meta name="twitter:card" content="summary_large_image">

  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="icon" href="/favicon.png" type="image/png" sizes="48x48">
  <link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">

  <link rel="preload" href="/assets/fonts/figtree-extrabold.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="/assets/fonts/geist-regular.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="/assets/css/styles.css">
  <script>document.documentElement.classList.add("js")</script>
  <script src="/assets/js/main.js" defer></script>
{extra}</head>"""


def lang_menu(L: dict, alternates: dict[str, str]) -> str:
    items = []
    for code in LANGS:
        other = SITE["languages"][code]
        current = ' aria-current="page"' if code == L["code"] else ""
        items.append(f'          <li><a href="{alternates.get(code, other["blog"])}" hreflang="{code}" lang="{code}"{current}>{other["name"]} <small>{code.upper()}</small></a></li>')
    return f"""<details class="lang" data-lang>
          <summary aria-label="{attr(L['language_label'])}: {L['name']}"><svg aria-hidden="true"><use href="#i-globe"/></svg>{L['code'].upper()}</summary>
          <ul class="lang-menu">
{chr(10).join(items)}
          </ul>
        </details>"""


def nav(L: dict, alternates: dict[str, str], current: str | None = None) -> str:
    links = []
    for item in L["nav"]:
        cls = ' class="nav-opt"' if item.get("optional") else ""
        cur = ' aria-current="page"' if current and item["href"] == current else ""
        links.append(f'        <li{cls}><a href="{item["href"]}"{cur}>{esc(item["label"])}</a></li>')
    return f"""  <a class="skip-link" href="#main">{esc(L['skip'])}</a>

  <header class="nav" data-nav>
    <div class="container nav-inner">
      <a class="brand" href="{L['home']}" aria-label="{attr(L['home_label'])}">fimbl</a>
      <ul class="nav-links">
{chr(10).join(links)}
      </ul>
      <div class="nav-end">
        {lang_menu(L, alternates)}
        <a class="btn btn-primary btn-sm" href="{STORE}" data-store>
          <svg aria-hidden="true"><use href="#i-apple"/></svg>{esc(L['get_app'])}
        </a>
      </div>
    </div>
  </header>"""


def store_button(L: dict) -> str:
    return f"""<a class="btn btn-primary btn-store" href="{STORE}" data-store>
              <svg aria-hidden="true"><use href="#i-apple"/></svg>
              <span class="btn-label"><small>{esc(L['store_small'])}</small><strong>{esc(L['store_big'])}</strong></span>
            </a>"""


def cta(L: dict) -> str:
    return f"""    <section class="section cta" style="padding-top:0">
      <div class="container">
        <div class="cta-card cta-contained">
          <div class="cta-copy">
            <img class="cta-icon" src="/assets/img/app-icon.webp" width="256" height="256" alt="" loading="lazy">
            <h2>{esc(L['cta_title'])}</h2>
            <p>{esc(L['cta_text'])}</p>
            {store_button(L)}
          </div>
          <div class="cta-phone" aria-hidden="true">
            <div class="phone"><img src="/assets/img/app/{L['code']}/welcome.webp" width="720" height="1564" alt="" loading="lazy"></div>
          </div>
        </div>
      </div>
    </section>"""


def footer(L: dict, alternates: dict[str, str]) -> str:
    links = "\n".join(f'          <li><a href="{l["href"]}"{" hreflang=" + chr(34) + l["hreflang"] + chr(34) if l.get("hreflang") else ""}>{esc(l["label"])}</a></li>' for l in L["footer_links"])
    langs = "\n".join(
        f'          <li><a href="{alternates.get(c, SITE["languages"][c]["blog"])}" hreflang="{c}" lang="{c}"{" aria-current=" + chr(34) + "page" + chr(34) if c == L["code"] else ""}>{SITE["languages"][c]["name"]}</a></li>'
        for c in LANGS
    )
    return f"""  <footer class="footer">
    <div class="container">
      <div class="footer-top">
        <div>
          <a class="brand" href="{L['home']}" aria-label="{attr(L['home_label'])}">fimbl</a>
          <p class="footer-tagline">{esc(L['tagline'])}</p>
        </div>
        <ul class="footer-links">
{links}
        </ul>
      </div>
      <div class="footer-bottom">
        <span>© <span data-year>2026</span> AppRise Ventures Oy · {esc(L['city'])}</span>
        <ul class="footer-langs" data-lang aria-label="{attr(L['language_label'])}">
{langs}
        </ul>
        <span>{esc(L['business_id'])}</span>
      </div>
    </div>
  </footer>"""


def ld(data: object) -> str:
    body = json.dumps(data, ensure_ascii=False, indent=2).replace("</", "<\\/")
    return f'  <script type="application/ld+json">\n{body}\n  </script>\n'


def publisher() -> dict:
    return {
        "@type": "Organization",
        "@id": BASE + "/#organization",
        "name": "AppRise Ventures Oy",
        "url": BASE + "/",
        "logo": {"@type": "ImageObject", "url": BASE + "/assets/img/icon-512.png", "width": 512, "height": 512},
        "address": {"@type": "PostalAddress", "streetAddress": "Sokerilinnantie 1 A", "postalCode": "02600", "addressLocality": "Espoo", "addressCountry": "FI"},
        "sameAs": [STORE],
    }


def author(L: dict) -> dict:
    return {"@type": "Person", "@id": BASE + "/#author", "name": SITE["author"]["name"], "jobTitle": L["author_role"], "worksFor": {"@id": BASE + "/#organization"}, "url": BASE + L["home"]}


def phone(src: str, alt: str, *, eager: bool = False) -> str:
    loading = "" if eager else ' loading="lazy"'
    alt_attr = f' alt="{attr(alt)}"' if alt else ' alt=""'
    return f'<div class="phone"><img src="{src}" width="720" height="1564"{alt_attr}{loading}></div>'


def initials(name: str) -> str:
    return "".join(part[0] for part in name.split()[:2]).upper()


def cover_img(meta: dict, *, alt: str = "", eager: bool = False, sizes: str = "(min-width: 1200px) 560px, (min-width: 960px) 45vw, 100vw") -> str:
    base = f"/assets/img/covers/{meta['lang']}-{meta['id']}"
    loading = ' fetchpriority="high"' if eager else ' loading="lazy" decoding="async"'
    return f'<img src="{base}-1200.webp" srcset="{base}-1200.webp 1200w, {base}-2400.webp 2400w" sizes="{sizes}" width="2400" height="1200" alt="{attr(alt)}"{loading}>'


# ---------- Post page ----------


def toc(body: str, L: dict, faq: bool, sources: bool) -> str:
    items = [(m.group(1), strip_tags(m.group(2))) for m in re.finditer(r'<h2[^>]*\bid="([^"]+)"[^>]*>(.*?)</h2>', body, re.S)]
    if faq:
        items.append(("faq", L["faq_title"]))
    links = "\n".join(f'            <li><a href="#{i}">{esc(t)}</a></li>' for i, t in items)
    return f"""        <details class="post-toc" data-toc open>
          <summary>{esc(L['toc_title'])}</summary>
          <ol>
{links}
          </ol>
        </details>"""


def faq_html(meta: dict, L: dict) -> str:
    if not meta.get("faq"):
        return ""
    items = "\n".join(f"""          <details>
            <summary>{esc(f['q'])}</summary>
            <p>{f['a']}</p>
          </details>""" for f in meta["faq"])
    return f"""
        <h2 id="faq">{esc(L['faq_title'])}</h2>
        <div class="faq">
{items}
        </div>"""


def sources_html(meta: dict, L: dict) -> str:
    if not meta.get("sources"):
        return ""
    items = "\n".join(
        f'            <li id="source-{i}">{s["text"]}{" " + chr(60) + "a href=" + chr(34) + attr(s["url"]) + chr(34) + " rel=" + chr(34) + "noopener" + chr(34) + ">" + esc(re.sub(r"^https?://(www[.])?", "", s["url"]).split("/")[0]) + "</a>" if s.get("url") else ""}</li>'
        for i, s in enumerate(meta["sources"], 1)
    )
    return f"""
        <section class="sources" aria-labelledby="sources">
          <h2 id="sources">{esc(L['sources_title'])}</h2>
          <ol>
{items}
          </ol>
        </section>"""


def post_card(meta: dict, L: dict, *, featured: bool = False, heading: str = "h3") -> str:
    cls = "post-card is-featured" if featured else "post-card"
    sizes = "(min-width: 960px) 640px, 100vw" if featured else "(min-width: 960px) 560px, 100vw"
    return f"""        <li class="{cls}">
          <div class="post-card-media">{cover_img(meta, sizes=sizes)}</div>
          <div class="post-card-body">
            <p class="post-card-meta"><span class="kicker">{esc(meta['tag'])}</span><span>{L['minutes'].format(n=meta['minutes'])}</span></p>
            <{heading}><a href="{meta['path']}">{esc(meta['headline'])}</a></{heading}>
            <p class="post-card-text">{esc(meta['description'])}</p>
            <p class="post-card-foot"><time datetime="{meta['published']}">{nice_date(meta['published'], meta['lang'])}</time><span class="read-more" aria-hidden="true">{esc(L['read_more'])}</span></p>
          </div>
        </li>"""


def render_post(meta: dict, siblings: dict[str, dict], posts: dict) -> str:
    lang = meta["lang"]
    L = SITE["languages"][lang]
    alternates = {c: siblings[c]["path"] for c in LANGS if c in siblings}
    body = fill(meta["body"], lang, posts)
    og_image = f"/assets/img/og/{lang}-{meta['id']}.jpg"
    path = meta["path"]
    faq_items = meta.get("faq", [])

    graph = [
        {
            "@type": "BlogPosting",
            "@id": url(path) + "#article",
            "headline": meta["headline"],
            "description": meta["description"],
            "image": [url(og_image)],
            "datePublished": iso(meta["published"]),
            "dateModified": iso(meta["modified"]),
            "inLanguage": L["locale"].replace("_", "-"),
            "author": author(L),
            "publisher": publisher(),
            "mainEntityOfPage": {"@type": "WebPage", "@id": url(path)},
            "isPartOf": {"@type": "Blog", "@id": url(L["blog"]) + "#blog", "name": L["feed_title"]},
            "articleSection": meta["tag"],
            "keywords": ", ".join(meta.get("keywords", [])),
            "wordCount": meta["word_count"],
            "about": [{"@type": "Thing", "name": a} for a in meta.get("about", [])],
        },
        {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": L["crumb_home"], "item": url(L["home"])},
                {"@type": "ListItem", "position": 2, "name": L["blog_name"], "item": url(L["blog"])},
                {"@type": "ListItem", "position": 3, "name": meta["headline"], "item": url(path)},
            ],
        },
    ]
    if meta.get("mentions"):
        graph[0]["mentions"] = [{"@type": "SoftwareApplication", "name": m, "applicationCategory": "HealthApplication"} for m in meta["mentions"]]
    if meta.get("sources"):
        graph[0]["citation"] = [s["url"] for s in meta["sources"] if s.get("url")]
    if faq_items:
        graph.append(
            {
                "@type": "FAQPage",
                "@id": url(path) + "#faq",
                "inLanguage": L["locale"].replace("_", "-"),
                "mainEntity": [{"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": strip_tags(fill(f["a"], lang, posts))}} for f in faq_items],
            }
        )
    extra = ld({"@context": "https://schema.org", "@graph": graph})

    og = {
        "type": "article",
        "title": meta.get("og_title", meta["headline"]),
        "image": og_image,
        "image_alt": meta.get("og_alt", meta["headline"]),
        "extra": [
            ("article:published_time", iso(meta["published"])),
            ("article:modified_time", iso(meta["modified"])),
            ("article:section", meta["tag"]),
        ]
        + [("article:tag", k) for k in meta.get("keywords", [])[:5]],
    }
    meta_head = head(L, title=meta["title"], description=meta["description"], path=path, alternates=alternates, og=og, extra=extra, feed=L["blog"] + "feed.xml")

    hero_image = cover_img(meta, alt=L["cover_alt"], eager=True, sizes="(min-width: 1200px) 1120px, calc(100vw - 40px)")
    avatar = initials(SITE["author"]["name"])
    updated = ""
    if meta["modified"] != meta["published"]:
        updated = f' · {esc(L["updated"])} <time datetime="{meta["modified"]}">{nice_date(meta["modified"], lang)}</time>'

    related = [posts[pid][lang] for pid in posts if pid != meta["id"] and lang in posts[pid]]
    related_cards = "\n".join(post_card(r, L) for r in related[:2])
    faq_part = fill(faq_html(meta, L), lang, posts)

    return f"""{meta_head}
<body>
  {SPRITE}

{nav(L, alternates, L['blog'])}

  <main id="main">
    <article>
      <header class="post-hero">
        <span class="nav-sentinel" data-nav-sentinel aria-hidden="true"></span>
        <div class="container post-head">
          <nav class="crumbs" aria-label="{attr(L['crumbs_label'])}">
            <ol>
              <li><a href="{L['home']}">{esc(L['crumb_home'])}</a></li>
              <li><a href="{L['blog']}">{esc(L['blog_name'])}</a></li>
              <li aria-current="page">{esc(meta['headline'])}</li>
            </ol>
          </nav>
          <p class="post-kicker"><span class="kicker">{esc(meta['tag'])}</span><span>{L['minutes'].format(n=meta['minutes'])}</span></p>
          <h1>{meta['h1']}</h1>
          <p class="post-dek">{esc(meta['dek'])}</p>
          <div class="byline">
            <span class="avatar" aria-hidden="true">{avatar}</span>
            <p class="byline-text"><strong>{esc(SITE['author']['name'])}</strong><span>{esc(L['author_role'])} · {esc(L['published'])} <time datetime="{meta['published']}">{nice_date(meta['published'], lang)}</time>{updated}</span></p>
          </div>
        </div>
        <figure class="container post-figure">{hero_image}</figure>
      </header>

      <div class="container post-wrap">
{toc(body, L, bool(faq_items), bool(meta.get('sources')))}
        <div class="article">
{body.rstrip()}
{faq_part}
{sources_html(meta, L)}
        <aside class="author-card">
          <span class="avatar avatar-lg" aria-hidden="true">{avatar}</span>
          <div>
            <p class="author-name">{esc(SITE['author']['name'])}</p>
            <p class="author-role">{esc(L['author_role'])}</p>
            <p>{L['author_bio']}</p>
          </div>
        </aside>
        </div>
      </div>
    </article>

    <section class="related" aria-labelledby="related-title">
      <div class="container">
        <h2 id="related-title">{esc(L['related_title'])}</h2>
        <ul class="post-cards post-cards-related">
{related_cards}
        </ul>
      </div>
    </section>

{cta(L)}
  </main>

{footer(L, alternates)}
</body>
</html>
"""


# ---------- Blog index ----------


def render_index(lang: str, posts: dict) -> str:
    L = SITE["languages"][lang]
    alternates = {c: SITE["languages"][c]["blog"] for c in LANGS}
    items = [posts[pid][lang] for pid in posts if lang in posts[pid]]
    cards = "\n".join(post_card(m, L, featured=(i == 0), heading="h2") for i, m in enumerate(items))
    og_image = f"/assets/img/og/{lang}-blog.jpg"
    graph = [
        {
            "@type": "Blog",
            "@id": url(L["blog"]) + "#blog",
            "name": L["feed_title"],
            "description": L["blog_description"],
            "url": url(L["blog"]),
            "inLanguage": L["locale"].replace("_", "-"),
            "publisher": publisher(),
            "blogPost": [{"@type": "BlogPosting", "headline": m["headline"], "url": url(m["path"]), "datePublished": iso(m["published"]), "dateModified": iso(m["modified"]), "image": url(f"/assets/img/og/{lang}-{m['id']}.jpg"), "author": {"@id": BASE + "/#author"}} for m in items],
        },
        {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": L["crumb_home"], "item": url(L["home"])},
                {"@type": "ListItem", "position": 2, "name": L["blog_name"], "item": url(L["blog"])},
            ],
        },
    ]
    og = {"type": "website", "title": L["blog_og_title"], "image": og_image, "image_alt": L["blog_og_title"]}
    return f"""{head(L, title=L['blog_title'], description=L['blog_description'], path=L['blog'], alternates=alternates, og=og, extra=ld({'@context': 'https://schema.org', '@graph': graph}), feed=L['blog'] + 'feed.xml')}
<body>
  {SPRITE}

{nav(L, alternates, L['blog'])}

  <main id="main">
    <section class="blog-hero">
      <span class="nav-sentinel" data-nav-sentinel aria-hidden="true"></span>
      <div class="container">
        <nav class="crumbs" aria-label="{attr(L['crumbs_label'])}">
          <ol>
            <li><a href="{L['home']}">{esc(L['crumb_home'])}</a></li>
            <li aria-current="page">{esc(L['blog_name'])}</li>
          </ol>
        </nav>
        <p class="kicker">{esc(L['blog_eyebrow'])}</p>
        <h1>{L['blog_h1']}</h1>
        <p class="lead">{esc(L['blog_lead'])}</p>
      </div>
    </section>

    <section class="post-list">
      <div class="container">
        <ul class="post-cards">
{cards}
        </ul>
      </div>
    </section>

{cta(L)}
  </main>

{footer(L, alternates)}
</body>
</html>
"""


# ---------- Feeds, sitemap, llms.txt ----------


def render_feed(lang: str, posts: dict) -> str:
    L = SITE["languages"][lang]
    items = [posts[pid][lang] for pid in posts if lang in posts[pid]]
    entries = "\n".join(
        f"""    <item>
      <title>{esc(m['headline'])}</title>
      <link>{url(m['path'])}</link>
      <guid isPermaLink="true">{url(m['path'])}</guid>
      <pubDate>{date.fromisoformat(m['published']).strftime('%a, %d %b %Y')} 08:00:00 +0300</pubDate>
      <description>{esc(m['description'])}</description>
    </item>"""
        for m in items
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{esc(L['feed_title'])}</title>
    <link>{url(L['blog'])}</link>
    <atom:link href="{url(L['blog'] + 'feed.xml')}" rel="self" type="application/rss+xml"/>
    <description>{esc(L['blog_description'])}</description>
    <language>{L['locale'].replace('_', '-').lower()}</language>
{entries}
  </channel>
</rss>
"""


def render_sitemap(posts: dict) -> str:
    groups: list[tuple[dict[str, str], str]] = []
    today = SITE["site_modified"]
    groups.append(({c: SITE["languages"][c]["home"] for c in LANGS}, today))
    newest = max(m["modified"] for p in posts.values() for m in p.values())
    groups.append(({c: SITE["languages"][c]["blog"] for c in LANGS}, newest))
    for pid, langs in posts.items():
        groups.append(({c: langs[c]["path"] for c in LANGS if c in langs}, max(m["modified"] for m in langs.values())))
    rows = []
    for alts, mod in groups:
        links = "".join(f'\n    <xhtml:link rel="alternate" hreflang="{c}" href="{url(p)}"/>' for c, p in alts.items())
        links += f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{url(alts["en"])}"/>'
        for p in alts.values():
            rows.append(f"  <url>\n    <loc>{url(p)}</loc>\n    <lastmod>{mod}</lastmod>{links}\n  </url>")
    for path, mod in SITE["single_pages"].items():
        rows.append(f"  <url>\n    <loc>{url(path)}</loc>\n    <lastmod>{mod}</lastmod>\n  </url>")
    return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(rows) + "\n</urlset>\n"


def render_llms(posts: dict) -> str:
    lines = [SITE["llms"]["intro"].rstrip(), "", "## Articles", ""]
    for pid, langs in posts.items():
        en = langs["en"]
        lines.append(f"- [{en['headline']}]({url(en['path'])}): {en['description']}")
        for c in LANGS:
            if c != "en" and c in langs:
                lines.append(f"  - {SITE['languages'][c]['name']}: [{langs[c]['headline']}]({url(langs[c]['path'])})")
    lines += ["", SITE["llms"]["outro"].rstrip(), ""]
    return "\n".join(lines)


# ---------- Share images ----------


def render_og(posts: dict) -> None:
    if not Path(CHROME).exists():
        sys.exit("Google Chrome not found; share images need it.")
    template = (TOOL / "og.html").read_text()
    jobs = []
    for pid, langs in posts.items():
        for lang, m in langs.items():
            jobs.append((f"{lang}-{pid}", m["og_kicker"], m["og_heading"], m["cover"][:2], lang))
    for lang in LANGS:
        L = SITE["languages"][lang]
        jobs.append((f"{lang}-blog", L["blog_og_kicker"], L["blog_og_heading"], L["blog_og_shots"], lang))
    for extra in SITE.get("og_pages", []):
        jobs.append((extra["name"], extra["kicker"], extra["heading"], extra["shots"], extra["lang"]))
    render_covers(posts)
    out_dir = ROOT / "assets/img/og"
    out_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        for name, kicker, heading, shots, lang in jobs:
            page = (
                template.replace("{root}", ROOT.as_uri())
                .replace("{lang}", lang)
                .replace("{kicker}", esc(kicker))
                .replace("{heading}", heading)
                .replace("{shot1}", f"{ROOT.as_uri()}/assets/img/app/{lang}/{shots[0]}.webp")
                .replace("{shot2}", f"{ROOT.as_uri()}/assets/img/app/{lang}/{shots[1]}.webp")
            )
            src = Path(tmp) / f"{name}.html"
            src.write_text(page)
            png = Path(tmp) / f"{name}.png"
            jpg = out_dir / f"{name}.jpg"
            subprocess.run(
                [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1", "--window-size=1200,630", "--virtual-time-budget=3000", f"--screenshot={png}", src.as_uri()],
                check=True,
                capture_output=True,
            )
            # JPEG keeps each share image around 100 KB instead of 400 KB.
            subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "85", str(png), "--out", str(jpg)], check=True, capture_output=True)
            print("og", jpg.relative_to(ROOT))


def render_covers(posts: dict) -> None:
    """Cover art for each post: three whole devices on a themed backdrop, at 1200 and 2400 px wide."""
    template = (TOOL / "cover.html").read_text()
    out_dir = ROOT / "assets/img/covers"
    out_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        for pid, langs in posts.items():
            spec = SITE["covers"][pid]
            for lang in langs:
                shots = [f"{ROOT.as_uri()}/assets/img/app/{lang}/{s}.webp" for s in spec["screens"]]
                page = template.replace("{theme}", spec["theme"]).replace("{left}", shots[0]).replace("{center}", shots[1]).replace("{right}", shots[2])
                src = Path(tmp) / f"{lang}-{pid}.html"
                src.write_text(page)
                png = Path(tmp) / f"{lang}-{pid}.png"
                subprocess.run(
                    [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files", "--force-device-scale-factor=1", "--window-size=2400,1200", "--virtual-time-budget=3000", f"--screenshot={png}", src.as_uri()],
                    check=True,
                    capture_output=True,
                )
                for width in (2400, 1200):
                    out = out_dir / f"{lang}-{pid}-{width}.webp"
                    subprocess.run(["cwebp", "-quiet", "-q", "82", "-resize", str(width), "0", str(png), "-o", str(out)], check=True)
                print("cover", f"assets/img/covers/{lang}-{pid}")


# ---------- Main ----------


def write(path: str, text: str) -> None:
    target = ROOT / path.lstrip("/")
    if path.endswith("/"):
        target = target / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text)
    print("wrote", target.relative_to(ROOT))


def main() -> None:
    for lang in LANGS:
        SITE["languages"][lang]["code"] = lang
    posts = load_posts()
    for langs in posts.values():
        for m in langs.values():
            m["minutes"] = reading_minutes(m)
    for pid, langs in posts.items():
        missing = [c for c in LANGS if c not in langs and c not in SITE.get("untranslated", {}).get(pid, [])]
        if missing:
            print(f"warning: {pid} has no {', '.join(missing)} version", file=sys.stderr)
        for m in langs.values():
            write(m["path"], render_post(m, langs, posts))
    for lang in LANGS:
        L = SITE["languages"][lang]
        write(L["blog"], render_index(lang, posts))
        (ROOT / L["blog"].lstrip("/") / "feed.xml").write_text(render_feed(lang, posts))
        print("wrote", L["blog"].lstrip("/") + "feed.xml")
    (ROOT / "sitemap.xml").write_text(render_sitemap(posts))
    print("wrote sitemap.xml")
    (ROOT / "llms.txt").write_text(render_llms(posts))
    print("wrote llms.txt")
    if "--og" in sys.argv:
        render_og(posts)


if __name__ == "__main__":
    main()
