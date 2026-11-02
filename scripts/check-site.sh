#!/usr/bin/env bash
# Content and link checks for the portfolio site.
#
# Usage:
#   scripts/check-site.sh            # check every site file, exit 1 on problems
#   scripts/check-site.sh --hook     # Claude Code PostToolUse hook mode (reads hook JSON on stdin)
#
# Checks:
#   1. Non-English characters in site files (accented letters such as "é",
#      arrows, curly quotes, ellipsis). Standard punctuation used on purpose
#      across the site is allowed: em/en dash, middle dot, (c), (R).
#   2. Broken local links: every href/src in the HTML pages that points at a
#      local file must exist.

set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 0

HOOK=0
[ "${1:-}" = "--hook" ] && HOOK=1

if [ "$HOOK" = 1 ]; then
  # Only react to edits of site files; stay silent for everything else.
  FILE="$(jq -r '.tool_input.file_path // .tool_response.filePath // empty' 2>/dev/null)"
  case "$FILE" in
    *.html|*.css|*.js) ;;
    *) exit 0 ;;
  esac
fi

REPORT="$(python3 -I - "$ROOT" <<'PY'
import os, re, sys, glob
root = sys.argv[1]
os.chdir(root)
problems = []

# 1. Characters a recruiter-facing English page should not contain.
BAD = re.compile(r"[À-ÿĀ-ɏ←-⇿‘’“”…]")
files = sorted(glob.glob("*.html")) + ["assets/css/site.css", "assets/js/site.js"]
for f in files:
    if not os.path.exists(f):
        continue
    for n, line in enumerate(open(f, encoding="utf-8"), 1):
        for m in BAD.finditer(line):
            ctx = line[max(0, m.start() - 30): m.end() + 30].strip()
            problems.append(f"{f}:{n}: non-English character '{m.group()}' in: ...{ctx}...")

# 2. Local links and images that do not resolve.
REF = re.compile(r'(?:href|src)="([^"]+)"')
for f in sorted(glob.glob("*.html")):
    text = open(f, encoding="utf-8").read()
    for ref in set(REF.findall(text)):
        if re.match(r"^(https?:|mailto:|tel:|#|data:|javascript:)", ref):
            continue
        path = ref.split("#")[0].split("?")[0]
        if path and not os.path.exists(path):
            problems.append(f"{f}: broken local link -> {ref}")

print("\n".join(problems))
PY
)"

if [ -z "$REPORT" ]; then
  [ "$HOOK" = 0 ] && echo "check-site: OK (no non-English characters, no broken local links)"
  exit 0
fi

if [ "$HOOK" = 1 ]; then
  # Feed the findings back to Claude so it fixes them in the same turn.
  jq -n --arg r "$REPORT" '{
    systemMessage: "check-site found content issues",
    hookSpecificOutput: {
      hookEventName: "PostToolUse",
      additionalContext: ("scripts/check-site.sh found problems. Fix them before finishing (see CLAUDE.md content rules):\n" + $r)
    }
  }'
  exit 0
fi

echo "$REPORT"
exit 1
