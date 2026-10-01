# fimbl.app

Landing page for [Fimbl](https://apps.apple.com/app/id6443701726), served by GitHub Pages from `master`. Plain HTML, CSS and JS with no build step (`.nojekyll` turns off Jekyll).

| Path | Contents |
| --- | --- |
| `index.html` | Landing page |
| `privacy/`, `terms/` | Privacy policy and terms of use, linked from the app |
| `privacy_policy/`, `terms_of_use/` | Redirects from the old URLs |
| `404.html` | Not found page, also catches universal links when the app isn't installed |
| `assets/` | Styles, script, self-hosted fonts (Figtree, Geist) and images |
| `.well-known/apple-app-site-association` | Universal links and web credentials |
| `CNAME`, `googledfd3fa1b8efcd494.html` | Custom domain and Google Search Console verification |

Screenshots in `assets/img` come from `fimbl-app/SwiftUI-Rewrite/appstore/screenshots/iphone/en-US`, resized to 720 px wide WebP:

```bash
cwebp -resize 720 0 -q 84 -sharp_yuv 02-diary.png -o assets/img/screen-02-diary.webp
```

Preview locally with `python3 -m http.server` and open http://localhost:8000.
