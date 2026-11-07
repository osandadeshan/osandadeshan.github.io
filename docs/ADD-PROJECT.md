# Adding a project or publication

1. **Images.** Put screenshots in `assets/img/publications/` (publications) or
   `assets/img/projects/` (projects). Keep them at most 1400px wide and under ~250 KB
   (`sips -s format jpeg -s formatOptions 78 -Z 1400 in.jpg --out out.jpg` on macOS).
2. **Cover image.** Add an entry to `PROJECTS` in `scripts/build-covers.py` (name, value line
   from the card text, tech chips from "Built with", a mock that shows what the project does) and
   run `python3 scripts/build-covers.py <slug>`. It writes `assets/img/covers/<slug>.jpg`
   (1280x800). Use it for the home card thumbnail, the detail page `.hero-cover`, the pager
   thumbnails that link to the page, and the `og:image` / `twitter:image` meta tags. The gallery
   keeps real screenshots; use the cover there only when there are no screenshots.
3. **Detail page.** Copy an existing page with a similar number of screenshots (e.g.
   `maxsoft-extent-reporter.html`) to `<slug>.html` and update:
   - `<title>`, meta description, `og:*` tags and the `canonical` URL
   - tag pill (Publication / Project), `h1`, hero description
   - `.hero-facts` pills (platforms, language, year) and the `.hero-cover` image + slug label
   - gallery: `.g-stage` images, `.g-thumbs` buttons and the `1 / N` counter
   - Project information `.meta-list`, Highlights `.adv-list`, Built with `.chips`
   - GitHub / publication buttons
4. **Pager.** Fix Previous/Next links (with thumbnails) on the new page and on its two
   neighbours so the chain stays continuous in the same order as the home page grid.
5. **Home page card.** Add an `<a class="card project hover spot reveal" data-cat="pub|proj">`
   in `#projects .grid-3`, in the right position, with a fitting `d1`/`d2` delay.
6. **SEO.** Add the URL to `sitemap.xml`.
7. **Verify.** `scripts/check-site.sh` must print OK; check the page at 1440px and 390px
   in both themes; click through the gallery, full-screen viewer and pager.
