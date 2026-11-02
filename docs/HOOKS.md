# Claude Code hooks and settings

`docs/claude-settings.json` is the project's Claude Code configuration. Install it once:

```bash
mkdir -p .claude && cp docs/claude-settings.json .claude/settings.json
```

Then open `/hooks` in Claude Code once (or restart it) so the hook loads.

## What it does

| Setting | Effect |
|---|---|
| `hooks.PostToolUse` on `Write\|Edit` | After Claude edits any `.html`, `.css` or `.js` file, runs `scripts/check-site.sh --hook`. If it finds non-English characters or broken local links, the findings go back to Claude so it fixes them in the same turn. Other files are ignored. |
| `attribution` (all empty, `sessionUrl: false`) | No `Co-Authored-By: Claude` trailer on commits and no "Generated with Claude Code" line or session link on PRs. |
| `permissions.allow` | Running the checker, the local preview server and read-only git commands without a prompt. |

## Running the checker yourself

```bash
scripts/check-site.sh        # prints OK, or each problem with file:line; exits 1 on problems
```

To change what counts as a bad character, edit the `BAD` pattern in the script.
