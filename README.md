# fimbl.app

Landing page for [Fimbl](https://apps.apple.com/app/id6443701726), served by GitHub Pages from `master`. Plain HTML, CSS and JS with no build step (`.nojekyll` turns off Jekyll).

| Path | Contents |
| --- | --- |
| `index.html` | Landing page (English, also `x-default`) |
| `fi/`, `de/` | Finnish and German landing pages |
| `blog/`, `fi/blogi/`, `de/blog/` | Blog indexes, posts and RSS feeds per language (generated, see below) |
| `tools/blog/` | Blog generator and its content (not linked, disallowed in `robots.txt`) |
| `sitemap.xml`, `llms.txt`, `llms-full.txt` | Generated with the blog: every page with its `hreflang` alternates, a plain summary for AI assistants, and the full text of every English article in one file |
| `index.md` next to every page | Generated with the blog: the page's `<main>` as Markdown, served to agents that send `Accept: text/markdown` (see Cloudflare below) |
| `auth.md` | Tells AI agents that reading the site needs no credentials and that there is no agent registration or public API |
| `<key>.txt` | The IndexNow key (a 32-character hex file name, its content is the same key). `tools/blog/indexnow.py` submits the sitemap's URLs to Bing and other IndexNow engines |
| `privacy/`, `terms/` | Privacy policy and terms of use, linked from the app |
| `privacy_policy/`, `terms_of_use/` | Redirects from the old URLs |
| `404.html` | Not found page, also catches universal links when the app isn't installed |
| `assets/` | Styles, script, self-hosted fonts (Figtree, Geist), images, share images (`assets/img/og`), localized app screens (`assets/img/app/{en,fi,de}`) and the promo film's poster (`assets/video`) |
| `.well-known/apple-app-site-association` | Universal links and web credentials |
| `CNAME`, `googledfd3fa1b8efcd494.html` | Custom domain and Google Search Console verification |

`robots.txt` is hand-written. Its `Content-Signal` lines (https://contentsignals.org) allow search, AI answers and AI training, to match the crawlers it welcomes.

`screen-07-goals` and `screen-08-meal` come from `SwiftUI-Rewrite/verification_screenshots/iphone` (`tab-goals.png`, `meals/05-meal-detail.png`). The other screenshots in `assets/img` come from `fimbl-app/SwiftUI-Rewrite/appstore/screenshots/iphone/en-US`, resized to 720 px wide WebP:

```bash
cwebp -resize 720 0 -q 84 -sharp_yuv 02-diary.png -o assets/img/screen-02-diary.webp
```

Preview locally with `python3 -m http.server` and open http://localhost:8000.

The promo film is the v2 horizontal cut from `fimbl-app/SwiftUI-Rewrite/appstore/marketing/promo-video` (48 MB), compressed to about 9 MB and given a poster frame:

```bash
ffmpeg -i out/fimbl-promo-v2-1920x1080-60fps.mp4 -c:v libx264 -preset slower -crf 28 -profile:v high -level 4.2 \
  -x264-params aq-mode=3 -c:a aac -b:a 96k -ac 2 -movflags +faststart -pix_fmt yuv420p assets/video/fimbl-promo-v2.mp4
ffmpeg -ss 11.6 -i out/fimbl-promo-v2-1920x1080-60fps.mp4 -frames:v 1 -vf scale=1280:-2 poster.png
cwebp -q 82 -sharp_yuv poster.png -o assets/video/fimbl-promo-v2-poster.webp
```

The mp4 is too big for this repo, so it's hosted on Cloudflare Pages and the page loads `https://video.fimbl.app/fimbl-promo-v2.mp4`. Setup, the DNS record and how to replace the film are in `fimbl-video-host/` (next to this repo). Only the 37 KB poster stays in `assets/video`. The video loads only when played (`preload="none"`), so it doesn't affect page speed.

## Cloudflare

fimbl.app is proxied through Cloudflare in front of GitHub Pages. GitHub Pages can't set response headers or look at the `Accept` header, so three rules in the Cloudflare dashboard (fimbl.app zone, Rules > Overview) do it. They aren't in this repo, so keep this list in step with the dashboard.

1. **URL Rewrite Rule** "Markdown for agents". Custom filter expression:

   ```
   (http.host eq "fimbl.app" and any(http.request.headers["accept"][*] contains "text/markdown") and ends_with(http.request.uri.path, "/") and not starts_with(http.request.uri.path, "/tools/"))
   ```

   Path: Rewrite to, Dynamic, `concat(http.request.uri.path, "index.md")`. Query: Preserve. GitHub Pages serves `.md` files as `text/markdown; charset=utf-8`, so agents get Markdown and browsers still get HTML.

2. **Response Header Transform Rule** "Agent discovery links". Expression `(http.host eq "fimbl.app" and http.request.uri.path in {"/" "/index.md"})`. Set static, header `Link`:

   ```
   </llms.txt>; rel="describedby"; type="text/plain", </llms-full.txt>; rel="describedby"; type="text/plain", </index.md>; rel="alternate"; type="text/markdown"
   ```

3. **Response Header Transform Rule** "Vary on Accept". Expression `(http.host eq "fimbl.app" and (ends_with(http.request.uri.path, "/") or ends_with(http.request.uri.path, "/index.md")))`. Add, header `Vary`, value `Accept`, so caches keep the HTML and Markdown versions apart.

Check with `curl -sI https://fimbl.app | grep -i link` and `curl -s -H 'Accept: text/markdown' https://fimbl.app | head`, or scan the site at https://isitagentready.com.

## Languages

English is the default and lives at the root. Finnish is under `/fi/` and German under `/de/`, with localized blog paths and slugs (`/fi/blogi/paras-kalorilaskuri-sovellus/`, `/de/blog/beste-kalorienzaehler-app/`). The privacy policy, terms and 404 page are English only and shared by all three.

- Every localized page has a self-referencing canonical and `hreflang` links to its translations plus `x-default` (English). `sitemap.xml` repeats them.
- The language menu in the header and the footer links go to the same page in the other language, not to its home page.
- A language picked in the menu is remembered in `localStorage` (`fimbl-lang`, disclosed in the privacy policy, section 13). Then `/` opens the saved language, and the English-only pages (`<body data-shared>`) point their home, section and blog links at it. The 404 page also follows the `/fi/` or `/de/` prefix of the missing address.
- Visitors whose browser prefers another available language see a small hint to switch, never a redirect, so search engines always get the page they asked for.

The Finnish and German landing pages are hand-written HTML like `index.html`. Keep their structure in step when the English page changes. The one exception is the "From the blog" cards between the `blog-cards` comments: the blog build rewrites them with the newest six posts, so don't edit them by hand.

## Blog

Posts are written once per language and built into static pages by `tools/blog/build.py` (Python 3, no dependencies). The generated HTML is committed, so GitHub Pages still has no build step.

```bash
python3 tools/blog/build.py        # posts, blog indexes, feeds, sitemap.xml, llms.txt, llms-full.txt, home page blog cards, index.md per page
python3 tools/blog/build.py --og   # also renders the covers and 1200×630 share images (Google Chrome, cwebp)
python3 tools/blog/indexnow.py     # after publishing: tell Bing and other IndexNow engines about every URL
```

| File | Contents |
| --- | --- |
| `tools/blog/site.json` | Shared strings per language (nav, footer, labels, dates, author), post order, `llms.txt` text, extra share images |
| `tools/blog/content/<lang>/<post>.json` | Slug, title tag, headline, description, cover screens, FAQ, sources, keywords |
| `tools/blog/content/<lang>/<post>.html` | The article body. `{img}` is the language's screenshot folder, `{post:<id>}` links another post in the same language, `{store}` is the App Store link |
| `tools/blog/og.html` | Template for the share images |
| `tools/blog/cover.html` | Template for the article covers (three whole devices on a themed backdrop). Screens and theme per post are under `covers` in `site.json`; output is `assets/img/covers/<lang>-<post>-{1200,2400}.webp` |

Each post page gets `BlogPosting`, `BreadcrumbList` and `FAQPage` structured data, a table of contents built from the `<h2 id>` headings, related posts and the localized call to action. To add a post, add the same `id` in all three content folders (the build warns about a missing translation), add the id to `order` in `site.json`, run both commands and check the pages locally. Claims about other apps need a source in the post's `sources` list and a check date; prices change too often to quote.

The screens in `assets/img/app/<lang>` are the App Store captures from `ventures-apps/fimbl/appstore/screenshots/iphone/<locale>` plus extra demo captures (activity, goals, food, meal, progress photo compare, gallery and camera, welcome) from the `Fimbl App Store iPhone 6.9` simulator, all at 720 × 1564 WebP:

```bash
xcrun simctl launch --terminate-running-process <udid> com.kkoskenvirta.myFitnessBroApp \
  -AppleLanguages "(fi)" -AppleLocale fi_FI -demo YES -demoTab progress -demoProgressPhotos YES -demoSheet progressCompare \
  -demoLongJourney YES -demoProgressPhotoDir "<path>/ventures-apps/fimbl/appstore/demo-progress-photos"
xcrun simctl io <udid> screenshot fi-photos-compare.png
cwebp -resize 720 1564 -q 82 -sharp_yuv fi-photos-compare.png -o assets/img/app/fi/photos-compare.webp
```

The progress photos in those screens show a fictional woman generated with Nano Banana by `ventures-apps/fimbl/scripts/generate_demo_progress_photos.py`, so wherever they appear the caption says they're AI-generated demo photos. `-demoLongJourney YES` is the version on the site: 195 days from 78.8 kg to her 65 kg goal, using the `*-65kg.jpg` photos for today. Leave it out for the default nine weeks, 78.8 to 74.2 kg. Gallery and camera use `-demoSheet progressPhotos` and `-demoSheet logWeight -demoPhotoStep camera -demoCamera live -demoPhotoPoses front,side`. The status bar shows 9:41 only when the simulator's region uses a colon for time (en_US); en_FI turns it into 9.41.

Other apps are only ever described in text, never shown.

The German site never names other apps. Comparative advertising follows the same EU rules everywhere, but in Germany (UWG §6) competitors and associations enforce them with costly cease-and-desist letters, so the comparison post has no German version (`untranslated` in `site.json`) and German posts don't link to it. Keep competitor names out of `tools/blog/content/de/` and `de/`.
