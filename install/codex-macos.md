# Codex CLI install (macOS / Linux)

How to run the `system-design-tutor` skill via OpenAI's Codex CLI on macOS or Linux.

## Prerequisites

- Codex CLI installed and authenticated. See https://developers.openai.com/codex/cli for current install instructions.

## Two install patterns

Codex CLI loads agent instructions from `AGENTS.md` files. Pick whichever fits your workflow.

### Pattern A — Project-local (recommended for trying it out)

Clone this branch and run Codex from inside the repo. The repo's `AGENTS.md` is picked up automatically as project-scope guidance, which routes Codex into `SKILL.md`.

```bash
git clone -b codex-macos https://github.com/rogue-socket/system-design-tutor.git ~/system-design-tutor
cd ~/system-design-tutor
codex
```

Then say "start the course" or any trigger phrase from `SKILL.md`'s frontmatter description.

### Pattern B — Global (always-on)

If you want trigger phrases to work from any directory, link the skill's `AGENTS.md` into Codex's global config dir. Every Codex session will then have the system-design-tutor instructions loaded.

```bash
git clone -b codex-macos https://github.com/rogue-socket/system-design-tutor.git ~/system-design-tutor
mkdir -p ~/.codex
ln -sfn ~/system-design-tutor/AGENTS.md ~/.codex/AGENTS.md
```

The `-sfn` flags atomically replace any existing `~/.codex/AGENTS.md` (file or symlink). Without `-f`, `ln` would fail with `File exists` if a global `AGENTS.md` was already present.

**Caveat:** Codex's global scope reads `~/.codex/AGENTS.md` (or `AGENTS.override.md` if present). The command above **overwrites** any existing global `AGENTS.md`. If you already have one with content you care about, do this instead:
- Append the contents of this repo's `AGENTS.md` to your existing global file (skip the symlink), or
- Use `CODEX_HOME` to point Codex at a different config dir for this skill.

## Workspace location

Identical to the Claude Code distribution: `~/system-design/`. The skill creates this directory and its subfolders (`notes/`, `exercises/`, `reviews/`, `flashcards/`, `meta/`) on first invocation.

## Updating

The `codex-macos` branch is **rebased** on top of `main` whenever shared content changes upstream. Because of that, `git pull` should use rebase, not merge — set this once after cloning:

```bash
cd ~/system-design-tutor
git config pull.rebase true
```

Then update normally:

```bash
git pull
```

If you skip the `pull.rebase` config and a maintainer-side rebase has happened upstream, `git pull` will create a confusing merge commit (or refuse outright). If that happens, recover with:

```bash
git fetch origin
git reset --hard origin/codex-macos
```

(This discards any local commits on the branch — fine for a clean install with no local edits.)

## Known divergences from CC

See `AGENTS.md` for the full SKILL.md → Codex translation table. The substantive ones:
- Codex has no `/compact` or `/clear`. The skill works around this by writing state to disk first, then having you start a new Codex session.
- Codex doesn't have a "skill manifest" mechanism. `AGENTS.md` is the entry point instead.
