# Windows install notes (Claude Code)

Supplementary guidance for running the `system-design-tutor` skill on Windows. Everything in `SKILL.md` still applies — this file only covers the platform-specific bits.

## Install

The recommended `skills.sh` install command in the main `README.md` works unchanged on Windows (it's `npx`, which is cross-platform — requires Node.js installed):

```powershell
npx skills add rogue-socket/system-design-tutor
```

The README's *manual* install command uses `mkdir -p`, which is not a PowerShell builtin. PowerShell equivalent:

```powershell
New-Item -ItemType Directory -Force -Path "$HOME\.claude\skills" | Out-Null
git clone https://github.com/rogue-socket/system-design-tutor.git "$HOME\.claude\skills\system-design-tutor"
```

## Shell

Use **PowerShell** (Windows PowerShell 5.1 or PowerShell 7+). The skill resolves the workspace via `~`, which PowerShell expands to your home directory. `cmd.exe` does not expand `~` and will silently create a literal `~` folder — avoid it.

## Workspace location

The skill creates and reads `~/system-design/`. On Windows this resolves to:

```
C:\Users\<you>\system-design\
```

Equivalently:
- `$HOME\system-design\` (PowerShell)
- `$env:USERPROFILE\system-design\` (PowerShell, explicit)

When Claude reports paths during a session, they may appear with forward slashes (`~/system-design/notes/replication.md`). That's the same location — Claude Code on Windows accepts both separators.

## Line endings

`progress.json`, `session-state.md`, and notes files are written and re-read by Claude across sessions. **The skill creates `~/system-design/` lazily on first invocation** — the snippet below assumes that directory already exists, so run it *after* your first session, not before.

To prevent CRLF/LF churn from git, set this once in the workspace:

```powershell
cd $HOME\system-design
git init  # only if you want to version your workspace
git config core.autocrlf false
```

The skill itself doesn't require git in the workspace — this is only relevant if you choose to track your notes/progress in version control.

## Long paths

Exercise folders nest a few levels deep (`exercises/<date>-<topic>/<files>`). If you hit `Filename too long` errors, enable long path support:

```powershell
# Run as Administrator, once per machine
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" `
  -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

## Diagrams

The skill produces interactive HTML diagrams (`notes/diagrams/*.html`). Open them with your default browser:

```powershell
Start-Process notes\diagrams\<file>.html
```

## What's *not* different

- The `SKILL.md` router, references, curriculum, and exercise bank are identical to the macOS/Linux distribution. No behavioral changes.
- `progress.json` and `session-state.md` schemas are unchanged.
- Spaced repetition, mode dispatch, and session control work the same way.
