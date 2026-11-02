# AGENTS.md

Instructions for AI coding agents (Codex, Cursor, GitHub Copilot, Gemini and others)
working in this repository. Claude Code reads `CLAUDE.md`; the rules are the same.

Read first:
- `CLAUDE.md` — project overview, stack, hard rules, verification, common tasks
- `docs/CONTENT-GUIDE.md` — facts sheet (source of truth), voice, recruiter personas, open items
- `docs/DESIGN-SYSTEM.md` — tokens, components, responsive and accessibility rules
- `docs/ADD-PROJECT.md` — checklist for a new project/publication page

## The short version

- Static GitHub Pages site: plain HTML, one CSS file, one JS file. No build step.
- Audience is recruiters and hiring managers; optimise for a 30-second scan.
- English only: no accented letters, arrows, curly quotes or ellipsis characters.
- Never invent facts, metrics, dates, tools or testimonials.
- Keep the existing dark violet/cyan design; extend `assets/css/site.css`, do not restyle.
- Changes to one project detail page apply to all 12.
- Before finishing: `scripts/check-site.sh` must print OK, and check 1440px and 390px.
- Work on a branch and open a PR. Do not add AI tools as commit co-authors.
