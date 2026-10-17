# fimbl.app

Landing page for [Fimbl](https://apps.apple.com/app/id6443701726), served by GitHub Pages from `master`. Plain HTML, CSS and JS with no build step (`.nojekyll` turns off Jekyll).

| Path | Contents |
| --- | --- |
| `index.html` | Landing page (English, also `x-default`) |
| `fi/`, `de/` | Finnish and German landing pages |
| `blog/`, `fi/blogi/`, `de/blog/` | Blog indexes, posts and RSS feeds per language (generated, see below) |
| `tools/blog/` | Blog generator and its content (not linked, disallowed in `robots.txt`) |
| `sitemap.xml`, `llms.txt` | Generated with the blog: every page with its `hreflang` alternates, and a plain summary for AI assistants |
| `privacy/`, `terms/` | Privacy policy and terms of use, linked from the app |
| `privacy_policy/`, `terms_of_use/` | Redirects from the old URLs |
| `404.html` | Not found page, also catches universal links when the app isn't installed |
| `assets/` | Styles, script, self-hosted fonts (Figtree, Geist), images, share images (`assets/img/og`), localized app screens (`assets/img/app/{en,fi,de}`) and the promo film (`assets/video`) |
| `.well-known/apple-app-site-association` | Universal links and web credentials |
| `CNAME`, `googledfd3fa1b8efcd494.html` | Custom domain and Google Search Console verification |

`screen-07-goals` and `screen-08-meal` come from `SwiftUI-Rewrite/verification_screenshots/iphone` (`tab-goals.png`, `meals/05-meal-detail.png`). The other screenshots in `assets/img` come from `fimbl-app/SwiftUI-Rewrite/appstore/screenshots/iphone/en-US`, resized to 720 px wide WebP:

```bash
cwebp -resize 720 0 -q 84 -sharp_yuv 02-diary.png -o assets/img/screen-02-diary.webp
```

Preview locally with `python3 -m http.server` and open http://localhost:8000.

The promo film in `assets/video` is the v2 horizontal cut from `fimbl-app/SwiftUI-Rewrite/appstore/marketing/promo-video` (48 MB), compressed to about 9 MB and given a poster frame:

```bash
ffmpeg -i out/fimbl-promo-v2-1920x1080-60fps.mp4 -c:v libx264 -preset slower -crf 28 -profile:v high -level 4.2 \
  -x264-params aq-mode=3 -c:a aac -b:a 96k -ac 2 -movflags +faststart -pix_fmt yuv420p assets/video/fimbl-promo-v2.mp4
ffmpeg -ss 11.6 -i out/fimbl-promo-v2-1920x1080-60fps.mp4 -frames:v 1 -vf scale=1280:-2 poster.png
cwebp -q 82 -sharp_yuv poster.png -o assets/video/fimbl-promo-v2-poster.webp
```

The video loads only when played (`preload="none"`), so it doesn't affect page speed.

## Languages

English is the default and lives at the root. Finnish is under `/fi/` and German under `/de/`, with localized blog paths and slugs (`/fi/blogi/paras-kalorilaskuri-sovellus/`, `/de/blog/beste-kalorienzaehler-app/`). The privacy policy, terms and 404 page are English only and shared by all three.

- Every localized page has a self-referencing canonical and `hreflang` links to its translations plus `x-default` (English). `sitemap.xml` repeats them.
- The language menu in the header and the footer links go to the same page in the other language, not to its home page.
- A language picked in the menu is remembered in `localStorage` (`fimbl-lang`, disclosed in the privacy policy, section 13). Then `/` opens the saved language, and the English-only pages (`<body data-shared>`) point their home, section and blog links at it. The 404 page also follows the `/fi/` or `/de/` prefix of the missing address.
- Visitors whose browser prefers another available language see a small hint to switch, never a redirect, so search engines always get the page they asked for.

The Finnish and German landing pages are hand-written HTML like `index.html`. Keep their structure in step when the English page changes.

## Blog

Posts are written once per language and built into static pages by `tools/blog/build.py` (Python 3, no dependencies). The generated HTML is committed, so GitHub Pages still has no build step.

```bash
python3 tools/blog/build.py        # posts, blog indexes, feeds, sitemap.xml, llms.txt
python3 tools/blog/build.py --og   # also renders the 1200×630 share images with Google Chrome
```

| File | Contents |
| --- | --- |
| `tools/blog/site.json` | Shared strings per language (nav, footer, labels, dates, author), post order, `llms.txt` text, extra share images |
| `tools/blog/content/<lang>/<post>.json` | Slug, title tag, headline, description, cover screens, FAQ, sources, keywords |
| `tools/blog/content/<lang>/<post>.html` | The article body. `{img}` is the language's screenshot folder, `{post:<id>}` links another post in the same language, `{store}` is the App Store link |
| `tools/blog/og.html` | Template for the share images |

Each post page gets `BlogPosting`, `BreadcrumbList` and `FAQPage` structured data, a table of contents built from the `<h2 id>` headings, related posts and the localized call to action. To add a post, add the same `id` in all three content folders (the build warns about a missing translation), add the id to `order` in `site.json`, run both commands and check the pages locally. Claims about other apps need a source in the post's `sources` list and a check date; prices change too often to quote.

The screens in `assets/img/app/<lang>` are the App Store captures from `ventures-apps/fimbl/appstore/screenshots/iphone/<locale>` plus extra demo captures (activity, goals, food, meal, progress photo compare, welcome) from the `Fimbl App Store iPhone 6.9` simulator, all at 720 px wide WebP:

```bash
xcrun simctl launch --terminate-running-process <udid> com.kkoskenvirta.myFitnessBroApp \
  -AppleLanguages "(fi)" -AppleLocale fi_FI -demo YES -demoTab progress -demoProgressPhotos YES -demoSheet progressCompare
xcrun simctl io <udid> screenshot fi-photos-compare.png
cwebp -resize 720 0 -q 82 -sharp_yuv fi-photos-compare.png -o assets/img/app/fi/photos-compare.webp
```

Other apps are only ever described in text, never shown.

The German site never names other apps. Comparative advertising follows the same EU rules everywhere, but in Germany (UWG §6) competitors and associations enforce them with costly cease-and-desist letters, so the comparison post has no German version (`untranslated` in `site.json`) and German posts don't link to it. Keep competitor names out of `tools/blog/content/de/` and `de/`.
