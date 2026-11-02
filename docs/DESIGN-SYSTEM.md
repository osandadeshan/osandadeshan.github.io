# Design system

Dark-first, glassy cards on a faint grid, violet-to-cyan gradient accents. Keep it;
extend rather than restyle.

## Tokens (`assets/css/site.css`)

| Token | Dark | Light | Use |
|---|---|---|---|
| `--accent-1` | `#8B5CF6` | `#7C3AED` | Violet; gradient start, borders, markers |
| `--accent-2` | `#22D3EE` | `#0E7490` | Cyan; eyebrows, icons, links |
| `--grad` | accent-1 → accent-2 | same | Buttons, `.grad-text`, top accent bars |
| `--bg` / `--bg-alt` | `#07080F` / `#0C0E1A` | `#F7F7FB` / `#EEEFF6` | Page / alternate sections |
| `--surface`, `--surface-strong` | translucent white | white | Card fills |
| `--text`, `--muted`, `--heading` | | | Body, secondary, headings |
| `--radius` | 18px | | Card corners |
| Success green | `#22C55E` | | "CURRENT" tag, `.promo-badge`, check icons |

Fonts: **Space Grotesk** (headings), **Inter** (body), **JetBrains Mono** (eyebrows,
dates, labels, counters). Icons: Bootstrap Icons (`<i class="bi bi-…">`).

Always define colours through tokens so both themes work. Test both themes.

## Building blocks

| Class | What it is |
|---|---|
| `.container` | 1180px max width, 92% on small screens |
| `section` (`.alt`, `.pt-sm`, `.pt-0`, `.pb-0`) | 110px vertical rhythm, with modifiers |
| `.eyebrow` + `.section-title` + `.section-lead` | Standard section header (mono label, big title, muted lead) |
| `.grad-text` | Gradient text for the emphasised words in a title |
| `.card` (+ `.hover`, `.spot`, `.pad`) | Glass card; `.hover` lifts, `.spot` adds cursor spotlight (JS), `.pad` adds padding |
| `.btn.btn-primary` / `.btn.btn-ghost` | Gradient / outline buttons |
| `.chip`, `.chip-sm`, `.chips` | Pills for skills and tools |
| `.reveal` + `.d1`–`.d3` | Fade-up on scroll with stagger delays |
| `.tabs` / `.tab` / `.pane` | Tabbed panes (`data-pane="x"` ↔ `id="pane-x"`) |
| `.t-item` (`details`) | Timeline entry; `.now` marks current; `.ladder` + `.promo-badge` for promotions |
| `.snapshot`, `.snap-grid` | Recruiter "short version" card |
| `.project` | Project card (`data-cat="pub"` or `"proj"` for the filter) |
| `.repo` | Open-source starter kit card |
| `.impact-card`, `.impact-kicker`, `.principles`, `.principles-list` | Selected impact cards and the "How I lead quality" principles row |
| `[data-print]` | Any button with this attribute prints the resume |
| `.cred` (`.award`) | Certification / award card with optional `.verify` icon |
| `.quote` + `.q-hl` | Testimonial with bold pull-quote headline |
| Detail page: `.detail-hero-grid`, `.hero-cover`, `.browser`, `.browser-bar`, `.hero-facts`, `.gallery`, `.g-count`, `.g-zoom`, `.lightbox`, `.adv-list`, `.side-stack`, `.cta-card`, `.pager` | Project page layout |

## Responsive and accessibility

- Breakpoints: 1040px (3→2 columns), 900px (single column layouts), 600px (mobile).
- No horizontal scroll at 390px.
- `prefers-reduced-motion` disables animations; keep it that way for new effects.
- Every icon-only button needs `aria-label`; decorative icons get `aria-hidden="true"`.
- Images need `width`/`height` and `loading="lazy"` below the fold.
- Print (`@media print`) renders the home page as a light, single-column resume; hide new
  decorative sections there.
