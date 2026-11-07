#!/usr/bin/env bash
# Build the ATS-friendly resume PDF from resume/resume.html.
#
# Usage: scripts/build-resume.sh
# Output: assets/Osanda-Nimalarathna-Resume.pdf (linked from the home page)
#
# Uses any installed Chromium-based browser in headless mode; links stay clickable
# and all text stays selectable, which is what applicant tracking systems need.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/resume/resume.html"
OUT="$ROOT/assets/Osanda-Nimalarathna-Resume.pdf"

BROWSER="${CHROME:-}"
if [ -z "$BROWSER" ]; then
  # Brave is listed last: its headless mode can hang on macOS.
  for c in \
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
    "/Applications/Chromium.app/Contents/MacOS/Chromium" \
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge" \
    $(ls -d "$HOME"/Library/Caches/ms-playwright/chromium_headless_shell-*/*/chrome-headless-shell 2>/dev/null | sort -r) \
    "$(command -v google-chrome || true)" "$(command -v chromium || true)" "$(command -v chromium-browser || true)" \
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"; do
    [ -n "$c" ] && [ -x "$c" ] && { BROWSER="$c"; break; }
  done
fi
[ -n "$BROWSER" ] || { echo "No Chromium-based browser found; set CHROME=/path/to/chrome" >&2; exit 1; }

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
"$BROWSER" --headless --disable-gpu --no-first-run --user-data-dir="$TMP" \
  --no-pdf-header-footer --virtual-time-budget=10000 --run-all-compositor-stages-before-draw --print-to-pdf="$OUT" "file://$SRC" >/dev/null 2>&1
echo "Built $OUT ($(du -h "$OUT" | cut -f1))"
