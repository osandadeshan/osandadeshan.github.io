# Adding a project or publication

1. **Images.** Put screenshots in `assets/img/publications/` (publications) or
   `assets/img/projects/` (projects). Keep them at most 1400px wide and under ~250 KB
   (`sips -s format jpeg -s formatOptions 78 -Z 1400 in.jpg --out out.jpg` on macOS).
2. **Detail page.** Copy an existing page with a similar number of screenshots (e.g.
   `maxsoft-extent-reporter.html`) to `<slug>.html` and update:
   - `<title>`, meta description, `og:*` tags and the `canonical` URL
   - tag pill (Publication / Project), `h1`, hero description
   - `.hero-facts` pills (platforms, language, year) and the `.hero-cover` image + slug label
   - gallery: `.g-stage` images, `.g-thumbs` buttons and the `1 / N` counter
   - Project information `.meta-list`, Highlights `.adv-list`, Built with `.chips`
   - GitHub / publication buttons
3. **Pager.** Fix Previous/Next links (with thumbnails) on the new page and on its two
   neighbours so the chain stays continuous in the same order as the home page grid.
4. **Home page card.** Add an `<a class="card project hover spot reveal" data-cat="pub|proj">`
   in `#projects .grid-3`, in the right position, with a fitting `d1`/`d2` delay.
5. **SEO.** Add the URL to `sitemap.xml`.
6. **Verify.** `scripts/check-site.sh` must print OK; check the page at 1440px and 390px
   in both themes; click through the gallery, full-screen viewer and pager.
