# Codex CLI install (Windows)

How to run the `system-design-tutor` skill via OpenAI's Codex CLI on Windows.

Read `install/windows.md` first for the platform fundamentals (PowerShell vs cmd, workspace path conventions, line endings, long paths). This file only covers what's specific to running on **Codex CLI** on Windows.

## Prerequisites

- Codex CLI installed and authenticated. See https://developers.openai.com/codex/cli for current install instructions on Windows.
- PowerShell 5.1 or later (PowerShell 7+ recommended).

## Two install patterns

Codex CLI loads agent instructions from `AGENTS.md` files. Pick whichever fits your workflow.

### Pattern A — Project-local (recommended for trying it out)

Clone this branch and run Codex from inside the repo. The repo's `AGENTS.md` is picked up automatically as project-scope guidance.

```powershell
git clone -b codex-windows https://github.com/rogue-socket/system-design-tutor.git $HOME\system-design-tutor
cd $HOME\system-design-tutor
codex
```

Then say "start the course" or any trigger phrase from `SKILL.md`'s frontmatter description.

### Pattern B — Global (always-on)

Make the skill globally available across all Codex sessions by linking its `AGENTS.md` into Codex's home directory. Every Codex session will then have the system-design-tutor instructions loaded.

```powershell
git clone -b codex-windows https://github.com/rogue-socket/system-design-tutor.git $HOME\system-design-tutor
New-Item -ItemType Directory -Force -Path "$HOME\.codex" | Out-Null

# Symlink (preferred — requires Developer Mode enabled OR running PowerShell as Administrator).
# -Force overwrites any existing ~/.codex/AGENTS.md.
New-Item -ItemType SymbolicLink -Force `
  -Path "$HOME\.codex\AGENTS.md" `
  -Target "$HOME\system-design-tutor\AGENTS.md"
```

If you can't enable Developer Mode and don't want to run elevated, fall back to copying the file (you'll need to re-copy after `git pull`s):

```powershell
Copy-Item -Force "$HOME\system-design-tutor\AGENTS.md" "$HOME\.codex\AGENTS.md"
```

**Caveat:** Codex's global scope reads `~/.codex/AGENTS.md` (or `AGENTS.override.md` if present). The commands above **overwrite** any existing global `AGENTS.md`. If you already have one with content you care about, do this instead:
- Append the contents of this repo's `AGENTS.md` to your existing global file (skip the symlink/copy), or
- Use `$env:CODEX_HOME` to point Codex at a different config dir for this skill.

## Workspace location

Identical to all other distributions: `~/system-design/`, which on Windows resolves to `C:\Users\<you>\system-design\`. See `install/windows.md` for full path-convention details.

## Updating

The `codex-windows` branch is **rebased** on top of upstream branches (`codex-macos` and `cc-windows` content) when shared content changes. Because of that, `git pull` should use rebase, not merge — set this once after cloning:

```powershell
cd $HOME\system-design-tutor
git config pull.rebase true
```

Then update normally:

```powershell
git pull
```

If you skip the `pull.rebase` config and a maintainer-side rebase has happened upstream, `git pull` will create a confusing merge commit (or refuse outright). Recover with:

```powershell
git fetch origin
git reset --hard origin/codex-windows
```

(Discards any local commits — fine for a clean install with no local edits.)

If you used Pattern B with `Copy-Item` (not symlink), you'll also need to re-copy `AGENTS.md` after each pull. Symlinks pick up changes automatically.

## Known divergences

- All Windows-specific divergences from `install/windows.md` apply here.
- All Codex-specific divergences (no `/compact`, AGENTS.md as the entry point) are documented in `AGENTS.md`.
- No Windows-only Codex divergences are known beyond the symlink-permissions issue above.
