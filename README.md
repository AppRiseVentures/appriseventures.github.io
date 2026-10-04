# fimbl.app

Landing page for [Fimbl](https://apps.apple.com/app/id6443701726), served by GitHub Pages from `master`. Plain HTML, CSS and JS with no build step (`.nojekyll` turns off Jekyll).

| Path | Contents |
| --- | --- |
| `index.html` | Landing page |
| `privacy/`, `terms/` | Privacy policy and terms of use, linked from the app |
| `privacy_policy/`, `terms_of_use/` | Redirects from the old URLs |
| `404.html` | Not found page, also catches universal links when the app isn't installed |
| `assets/` | Styles, script, self-hosted fonts (Figtree, Geist), images and the promo film (`assets/video`) |
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
