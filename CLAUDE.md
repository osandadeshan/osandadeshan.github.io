# Osanda Nimalarathna — portfolio site

Personal portfolio of a Lead Software Engineer (test automation, performance testing,
quality governance, AI-driven engineering) based in Singapore. Hosted on **GitHub Pages**
at https://osandadeshan.github.io from the `master` branch. The primary audience is
**recruiters and hiring managers**; every change should make the profile easier to pick
for an opening.

Read these before content or design work:
- @docs/CONTENT-GUIDE.md — facts sheet (source of truth), voice, recruiter personas, open items
- @docs/DESIGN-SYSTEM.md — colour tokens, components and CSS class conventions

## Stack and layout

Plain static HTML/CSS/JS. **No build step, no framework, no npm dependencies.**

| Path | What it is |
|---|---|
| `index.html` | Single-page home: hero, stats, recruiter snapshot, about, skills & journey, services, projects, credentials, testimonials, contact |
| `<project>.html` (12 files) | One detail page per project/publication; all share one template |
| `404.html` | Themed not-found page |
| `assets/css/site.css` | All styles (one file). Dark theme default, light theme via `[data-theme="light"]`; print stylesheet at the end turns the home page into a resume |
| `assets/js/site.js` | All behaviour (one IIFE): theme toggle, menu, typewriter, reveal-on-scroll, tabs, project filter, testimonial slider, detail gallery + lightbox, print, contact form |
| `assets/img/` | Images. `publications/` and `projects/` hold card and gallery screenshots |
| `sitemap.xml`, `robots.txt` | SEO. Add every new page to `sitemap.xml` |
| `scripts/check-site.sh` | Content + link checker (also runs as a Claude Code hook) |
| `resume/resume.html` | Source of the ATS-friendly resume PDF (not published as a page) |
| `scripts/build-covers.py` | Generates the project cover images in `assets/img/covers/` (sources in `covers/`, not published) |
| `scripts/build-resume.sh` | Builds `assets/Osanda-Nimalarathna-Resume.pdf` from `resume/resume.html` with headless Chromium |

External resources: Google Fonts (Inter, Space Grotesk, JetBrains Mono), Bootstrap Icons
1.11.3 from jsDelivr, FormSubmit for the contact form (`osanda.deshan@gmail.com`).

## Hard rules

1. **English only.** No accented letters (write "resume", never "résumé"), no arrows (`→`),
   no curly quotes or ellipsis characters in site text. **No em or en dashes (`—`, `–`) in site prose:**
   they read as AI-written. Use a comma, colon, full stop or "to" instead; date ranges use a
   spaced hyphen ("Feb 2025 - Present"). Only verbatim testimonials keep their dashes.
   Allowed: middle dot `·`, `©`, `®`. Run `scripts/check-site.sh` before finishing.
2. **Never invent facts.** No made-up metrics, employers, dates, tools, star counts or
   testimonials. Use only what is in `docs/CONTENT-GUIDE.md`, the existing site, or what
   Osanda states. If a claim needs a number you do not have, ask or flag it.
3. **Verify live numbers** (GitHub stars/forks/repo count, Medium followers) against the
   source before changing or repeating them: `curl -s https://api.github.com/users/osandadeshan`.
4. **Keep the existing template, colours and styling.** Extend `site.css` with new rules;
   reuse `.card`, `.chip`, `.btn`, `.eyebrow`, `.grad-text`, `.reveal` etc.
5. **Detail pages are templated.** A structural change to one detail page must be applied
   to all 12 (script it with Python and assert each replacement matched).
6. **Git:** never commit to `master` directly; branch, commit, push, open a PR.
   **Do not add Claude as co-author or committer** — no `Co-Authored-By: Claude` trailer and
   no "Generated with Claude Code" line in PR bodies.
7. Mobile must not scroll horizontally at 390px wide.

## Verify a change

```bash
scripts/check-site.sh                 # characters + broken local links; must print OK
python3 -m http.server 8765           # then open http://localhost:8765
```

Check desktop (1440px) and mobile (390px), dark and light theme, and the browser print view
if the home page content changed. Reveal animations
hide content until scrolled into view — when screenshotting headlessly, add class `in`
to every `.reveal` element first.

**Resume PDF:** the "Resume (PDF)" buttons download `assets/Osanda-Nimalarathna-Resume.pdf`.
When career facts, skills, projects or credentials change, update `resume/resume.html` too,
then run `scripts/build-resume.sh` and commit the regenerated PDF. Keep it ATS-friendly (online ATS checkers mark down anything else): **one column**, no
grids/columns, tables, images, icons or positioned elements; Arial; plain ASCII punctuation;
standard headings (Summary, Skills, Work Experience, Projects, Certifications, Awards,
Education); each job as a title/dates row, a company/location row, context, outcome-first bullets
and a Tools line; at most 3 pages; every project, publication, certification and award linked to its page. After
building, check the text order with
`python3 -c "import pypdf;print(pypdf.PdfReader('assets/Osanda-Nimalarathna-Resume.pdf').pages[0].extract_text()[:300])"`.

`gh` is not installed on this machine; after pushing a branch give the user the compare
link: `https://github.com/osandadeshan/osandadeshan.github.io/compare/master...<branch>?expand=1`

## Common tasks

- **Add a project/publication:** follow `docs/ADD-PROJECT.md`.
- **Add a job:** copy a `<details class="card t-item spot">` block in `#pane-exp`. Several
  roles at one company go in one entry with an `<ol class="ladder">` and a green
  `<span class="promo-badge">` starting with "Promoted" (see Wiley and Mitra entries).
  Move the `now` class and `open` attribute to the current role.
- **Add a certification:** add a `.card.cred` in `#pane-certs`, ordered by relevance to QE
  leadership (ISTQB/SAFe/Chaos first, basic courses last), and update the count in the tab
  label and the stats tile.
- **Update skills:** keep the "AI & intelligent automation" group first in Skills & journey
  and AI-assisted engineering first in the snapshot's Core stack.
